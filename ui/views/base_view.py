"""
Base View class providing standard layout, execution lifecycle, and streaming terminal integration.
"""
import queue
import customtkinter as ctk
from ui.theme import COLORS, get_font
from ui.process_runner import ProcessRunner
from ui.components.terminal_view import TerminalView

class BaseToolView(ctk.CTkFrame):
    """
    Abstract Base Class for all tool views in other_tools.
    """

    def __init__(self, master, title: str, description: str, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.title_text = title
        self.description_text = description

        self.runner = ProcessRunner(
            on_log=self._handle_log_threadsafe,
            on_finish=self._handle_finish_threadsafe
        )
        self.log_queue = queue.Queue()
        self._polling_active = False

        self._build_base_layout()
        self.build_options(self.options_container)

    def _build_base_layout(self):
        # 1. Header Frame
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(16, 12))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=self.title_text,
            font=get_font(20, "bold"),
            text_color=COLORS["text_primary"]
        )
        self.title_label.pack(anchor="w")

        self.desc_label = ctk.CTkLabel(
            self.header_frame,
            text=self.description_text,
            font=get_font(12),
            text_color=COLORS["text_secondary"]
        )
        self.desc_label.pack(anchor="w", pady=(2, 0))

        # 2. Main Content Split: Options on Top, Terminal on Bottom
        self.content_panes = ctk.CTkFrame(self, fg_color="transparent")
        self.content_panes.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # Options Container (Card style)
        self.options_card = ctk.CTkFrame(
            self.content_panes,
            fg_color=COLORS["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )
        self.options_card.pack(fill="x", pady=(0, 12))

        self.options_container = ctk.CTkFrame(self.options_card, fg_color="transparent")
        self.options_container.pack(fill="both", expand=True, padx=16, pady=16)

        # Action Bar (Execute Button Row)
        self.action_bar = ctk.CTkFrame(self.options_card, fg_color="transparent")
        self.action_bar.pack(fill="x", padx=16, pady=(0, 16))

        self.run_btn = ctk.CTkButton(
            self.action_bar,
            text="▶ Start Process",
            font=get_font(13, "bold"),
            height=38,
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_primary_hover"],
            command=self.on_start_clicked
        )
        self.run_btn.pack(side="left", padx=(0, 10))

        # Terminal Output View
        self.terminal = TerminalView(
            self.content_panes,
            on_abort_requested=self.on_abort_clicked
        )
        self.terminal.pack(fill="both", expand=True)

    def build_options(self, container: ctk.CTkFrame):
        """Override in subclass to build custom tool input controls."""
        pass

    def on_start_clicked(self):
        """Override in subclass to validate inputs and invoke self.execute_command(...)."""
        pass

    def on_abort_clicked(self):
        """Invoked when user clicks Stop in terminal view."""
        self.runner.terminate()
        self.terminal.set_status("ABORTED", COLORS["accent_danger"])

    def execute_command(self, cmd_args, cwd=None, env=None):
        """Executes command asynchronously through ProcessRunner."""
        if self.runner.is_running:
            return

        self.terminal.clear()
        cmd_str = cmd_args if isinstance(cmd_args, str) else " ".join(f'"{a}"' if " " in a else a for a in cmd_args)
        self.terminal.append_log(f"========================================================================\n")
        self.terminal.append_log(f"⚡ EXECUTING: {cmd_str}\n")
        self.terminal.append_log(f"========================================================================\n\n")

        self.terminal.set_running_state(True)
        self.run_btn.configure(state="disabled")

        self._polling_active = True
        self._poll_logs()

        self.runner.run_command(cmd_args, cwd=cwd, env=env)

    def _handle_log_threadsafe(self, line: str):
        self.log_queue.put(("log", line))

    def _handle_finish_threadsafe(self, returncode: int, duration: float):
        self.log_queue.put(("finish", (returncode, duration)))

    def _poll_logs(self):
        if not self._polling_active:
            return

        try:
            while True:
                msg_type, data = self.log_queue.get_nowait()
                if msg_type == "log":
                    self.terminal.append_log(data)
                elif msg_type == "finish":
                    returncode, duration = data
                    self.terminal.set_running_state(False)
                    self.run_btn.configure(state="normal")
                    self._polling_active = False

                    if returncode == 0:
                        self.terminal.append_log(f"\n✨ [COMPLETED SUCCESSFULLY] in {duration:.2f}s\n")
                        self.terminal.set_status("SUCCESS", COLORS["accent_success"])
                    else:
                        self.terminal.append_log(f"\n❌ [PROCESS EXITED WITH CODE {returncode}] after {duration:.2f}s\n")
                        self.terminal.set_status(f"FAILED ({returncode})", COLORS["accent_danger"])
                    return
        except queue.Empty:
            pass

        if self._polling_active:
            self.after(50, self._poll_logs)
