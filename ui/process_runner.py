"""
Thread-safe background process execution engine with live streaming logs and clean process-tree termination.
"""
import os
import sys
import time
import queue
import threading
import subprocess
import re

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def strip_ansi(text: str) -> str:
    """Removes ANSI color/formatting escape codes."""
    return ANSI_ESCAPE.sub('', text)


class ProcessRunner:
    """
    Executes CLI commands / scripts asynchronously and pipes stdout/stderr
    to a thread-safe callback without freezing the GUI.
    """

    def __init__(self, on_log=None, on_finish=None):
        self.on_log = on_log
        self.on_finish = on_finish
        self.process: subprocess.Popen = None
        self.thread: threading.Thread = None
        self.log_queue = queue.Queue()
        self.is_running = False
        self.start_time = 0.0

    def run_command(self, cmd_args, cwd=None, env=None):
        """Starts a background process given a command list or string."""
        if self.is_running:
            raise RuntimeError("A process is already actively running.")

        self.is_running = True
        self.start_time = time.time()

        # Merge environment
        proc_env = os.environ.copy()
        proc_env["PYTHONUNBUFFERED"] = "1"
        proc_env["PYTHONIOENCODING"] = "utf-8"
        if env:
            proc_env.update(env)

        # Launch worker thread
        self.thread = threading.Thread(
            target=self._worker,
            args=(cmd_args, cwd, proc_env),
            daemon=True
        )
        self.thread.start()

    def _worker(self, cmd_args, cwd, env):
        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NO_WINDOW

        returncode = -1
        try:
            # If string command on Windows, run through cmd /c if needed or directly
            shell = isinstance(cmd_args, str)
            
            self.process = subprocess.Popen(
                cmd_args,
                cwd=cwd,
                env=env,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                creationflags=creation_flags
            )

            # Read output line by line
            for line in iter(self.process.stdout.readline, ''):
                clean_line = strip_ansi(line)
                if self.on_log:
                    self.on_log(clean_line)

            self.process.stdout.close()
            returncode = self.process.wait()

        except Exception as e:
            if self.on_log:
                self.on_log(f"\n[EXECUTION ERROR]: {e}\n")
            returncode = -1
        finally:
            duration = time.time() - self.start_time
            self.is_running = False
            self.process = None
            if self.on_finish:
                self.on_finish(returncode, duration)

    def terminate(self):
        """Force-kills the running process and all child processes."""
        if not self.is_running or not self.process:
            return False

        try:
            pid = self.process.pid
            if sys.platform == "win32":
                # Terminate entire process tree forcibly
                subprocess.run(
                    f"taskkill /F /T /PID {pid}",
                    shell=True,
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                self.process.terminate()
            if self.on_log:
                self.on_log("\n[ABORTED]: Process terminated by user.\n")
            return True
        except Exception as e:
            if self.on_log:
                self.on_log(f"\n[TERMINATE ERROR]: Failed to kill PID {self.process.pid}: {e}\n")
            return False
