"""
General File Downloader View - Powered by aria2c multi-connection acceleration.
Splits direct downloads into parallel 16-32 chunks with auto-resume, piped URL|Referer, and batch list support.
"""
import os
import shutil
import customtkinter as ctk
from tkinter import filedialog
from ui.theme import COLORS, get_font
from ui.views.base_view import BaseToolView
from config_manager import get_download_dir, set_download_dir

ROOT_DIR = os.path.dirname(os.path.abspath(__file__ + "/../.."))

def get_aria2_path():
    candidates = [
        os.path.join(ROOT_DIR, "bin", "aria2c.exe"),
        os.path.join(ROOT_DIR, "aria2c.exe"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return shutil.which("aria2c") or "aria2c"


class FileDownloaderView(BaseToolView):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            title="🚀 General File Downloader (aria2c)",
            description="Multi-connection turbo file accelerator. Splits any direct file download into 16–32 parallel streams with auto-resume.",
            **kwargs
        )

    def build_options(self, container: ctk.CTkFrame):
        # 1. Persistent Download Folder Card
        self.config_card = ctk.CTkFrame(container, fg_color=COLORS["bg_terminal"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        self.config_card.pack(fill="x", pady=(0, 10), padx=2)

        config_inner = ctk.CTkFrame(self.config_card, fg_color="transparent")
        config_inner.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(
            config_inner,
            text="💾 Save Destination:",
            font=get_font(12, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(0, 8))

        self.save_dir_entry = ctk.CTkEntry(
            config_inner,
            font=get_font(12),
            height=30
        )
        self.save_dir_entry.insert(0, get_download_dir())
        self.save_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.browse_save_btn = ctk.CTkButton(
            config_inner,
            text="📁 Change & Save",
            font=get_font(12),
            width=120,
            height=30,
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_primary_hover"],
            command=self._change_save_dir
        )
        self.browse_save_btn.pack(side="right")

        # 2. Main Input Card
        self.input_card = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        self.input_card.pack(fill="x", pady=4, padx=2)

        inner = ctk.CTkFrame(self.input_card, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=12)

        # URL Input
        ctk.CTkLabel(inner, text="Download Link (Direct URL, piped 'URL|Referer', or path to .txt batch list):", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 2))
        
        url_row = ctk.CTkFrame(inner, fg_color="transparent")
        url_row.pack(fill="x", pady=(0, 8))
        
        self.url_entry = ctk.CTkEntry(url_row, placeholder_text="https://example.com/file.zip, .iso, .tar.gz, Google Drive direct link...", height=34)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.browse_txt_btn = ctk.CTkButton(
            url_row,
            text="📄 Batch .txt",
            width=100,
            height=34,
            fg_color=COLORS["bg_terminal"],
            hover_color=COLORS["border"],
            command=self._browse_batch_txt
        )
        self.browse_txt_btn.pack(side="right")

        # Referer & Custom Filename Row
        row_ref = ctk.CTkFrame(inner, fg_color="transparent")
        row_ref.pack(fill="x", pady=2)
        row_ref.columnconfigure((0, 1), weight=1)

        c1 = ctk.CTkFrame(row_ref, fg_color="transparent")
        c1.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(c1, text="Referer URL (Auto-filled from pipe or optional):", font=get_font(11)).pack(anchor="w")
        self.ref_entry = ctk.CTkEntry(c1, placeholder_text="https://example.com/download-page", height=32)
        self.ref_entry.pack(fill="x")

        c2 = ctk.CTkFrame(row_ref, fg_color="transparent")
        c2.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(c2, text="Custom Output File Name (Optional):", font=get_font(11)).pack(anchor="w")
        self.name_entry = ctk.CTkEntry(c2, placeholder_text="Leave blank to auto-detect from server", height=32)
        self.name_entry.pack(fill="x")

        # Auto-split hook
        self.url_entry.bind("<KeyRelease>", lambda e: self._auto_split_piped_url())

        # 3. Connection & Performance Parameters Card
        self.params_card = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        self.params_card.pack(fill="x", pady=6, padx=2)

        p_inner = ctk.CTkFrame(self.params_card, fg_color="transparent")
        p_inner.pack(fill="x", padx=12, pady=10)

        row_ctrl = ctk.CTkFrame(p_inner, fg_color="transparent")
        row_ctrl.pack(fill="x", pady=2)
        row_ctrl.columnconfigure((0, 1), weight=1)

        f1 = ctk.CTkFrame(row_ctrl, fg_color="transparent")
        f1.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(f1, text="Parallel Connection Streams:", font=get_font(11, "bold")).pack(anchor="w")
        self.chunks_segment = ctk.CTkSegmentedButton(
            f1,
            values=["16 Streams (Turbo)", "32 Streams (Ultra)", "8 Streams (Safe)", "64 Streams (Max)"],
            font=get_font(11)
        )
        self.chunks_segment.set("16 Streams (Turbo)")
        self.chunks_segment.pack(fill="x", pady=2)

        f2 = ctk.CTkFrame(row_ctrl, fg_color="transparent")
        f2.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(f2, text="Parallel Batch Tasks:", font=get_font(11, "bold")).pack(anchor="w")
        self.batch_tasks_segment = ctk.CTkSegmentedButton(
            f2,
            values=["4 Parallel Files", "8 Parallel Files", "1 Sequential"],
            font=get_font(11)
        )
        self.batch_tasks_segment.set("4 Parallel Files")
        self.batch_tasks_segment.pack(fill="x", pady=2)

        # Advanced Checkboxes
        row_chk = ctk.CTkFrame(p_inner, fg_color="transparent")
        row_chk.pack(fill="x", pady=(8, 0))

        self.resume_chk = ctk.CTkCheckBox(row_chk, text="Auto-Resume Broken Downloads (-c)", font=get_font(12))
        self.resume_chk.select()
        self.resume_chk.pack(side="left", padx=(0, 16))

        self.alloc_chk = ctk.CTkCheckBox(row_chk, text="Fast Pre-Allocation (falloc)", font=get_font(12))
        self.alloc_chk.select()
        self.alloc_chk.pack(side="left", padx=(0, 16))

        self.ua_chk = ctk.CTkCheckBox(row_chk, text="Spoof Desktop Chrome User-Agent", font=get_font(12))
        self.ua_chk.select()
        self.ua_chk.pack(side="left")

    def _change_save_dir(self):
        folder = filedialog.askdirectory(initialdir=get_download_dir())
        if folder:
            set_download_dir(folder)
            self.save_dir_entry.delete(0, "end")
            self.save_dir_entry.insert(0, folder)
            self.terminal.append_log(f"[*] Save folder saved: {folder}\n")

    def _browse_batch_txt(self):
        txt_path = filedialog.askopenfilename(
            title="Select Text File with URLs",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if txt_path:
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, txt_path)

    def _auto_split_piped_url(self):
        val = self.url_entry.get()
        if "|" in val:
            parts = val.split("|", 1)
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, parts[0].strip())
            self.ref_entry.delete(0, "end")
            self.ref_entry.insert(0, parts[1].strip())

    def get_effective_save_dir(self) -> str:
        custom = self.save_dir_entry.get().strip()
        if custom and os.path.exists(custom):
            set_download_dir(custom)
            return custom
        return get_download_dir()

    def on_start_clicked(self):
        raw_url = self.url_entry.get().strip()
        if not raw_url:
            self.terminal.clear()
            self.terminal.append_log("⚠️ Error: Please enter a download link or select a .txt batch file.\n")
            return

        aria2_bin = get_aria2_path()
        ref_url = self.ref_entry.get().strip()
        custom_name = self.name_entry.get().strip()
        save_dir = self.get_effective_save_dir()

        chunks_choice = self.chunks_segment.get()
        split_count = "16"
        split_size = "1M"
        if "32" in chunks_choice:
            split_count = "32"
            split_size = "512K"
        elif "8" in chunks_choice:
            split_count = "8"
            split_size = "2M"
        elif "64" in chunks_choice:
            split_count = "64"
            split_size = "256K"

        batch_choice = self.batch_tasks_segment.get()
        max_concurrent = "4"
        if "8" in batch_choice:
            max_concurrent = "8"
        elif "1" in batch_choice:
            max_concurrent = "1"

        is_batch = os.path.isfile(raw_url) and raw_url.lower().endswith(".txt")

        cmd = [aria2_bin]
        if is_batch:
            cmd.extend(["-i", raw_url])
        else:
            cmd.append(raw_url)

        cmd.extend([
            "-d", save_dir,
            "-s", split_count,
            "-x", split_count,
            "-k", split_size,
            "-j", max_concurrent,
            "--summary-interval=1",
            "--console-log-level=warn"
        ])

        if self.ua_chk.get():
            cmd.append("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

        if self.resume_chk.get():
            cmd.append("-c")

        if self.alloc_chk.get():
            cmd.append("--file-allocation=falloc")

        if custom_name and not is_batch:
            cmd.extend(["--out", custom_name])

        if ref_url and not is_batch:
            cmd.extend(["--referer", ref_url, "--header", f"Origin: {ref_url}"])

        self.execute_command(cmd, cwd=save_dir)
