"""
Music & Audio Downloader View - Powered by yt-dlp and FFmpeg.
Extracts high-bitrate audio with ID3 metadata, cover art, chapter splitting, and batch downloads.
"""
import os
import shutil
import customtkinter as ctk
from tkinter import filedialog
from ui.theme import COLORS, get_font
from ui.views.base_view import BaseToolView
from config_manager import get_download_dir, set_download_dir

ROOT_DIR = os.path.dirname(os.path.abspath(__file__ + "/../.."))

def get_ytdlp_path():
    candidates = [
        os.path.join(ROOT_DIR, "bin", "yt-dlp.exe"),
        os.path.join(ROOT_DIR, "yt-dlp.exe"),
        r"C:\Users\joao3\Videos\yt-dlp-master\yt-dlp.exe",
        os.path.expanduser(r"~\yt-dlp.exe"),
        os.path.expanduser(r"~\Videos\yt-dlp-master\yt-dlp.exe")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return shutil.which("yt-dlp") or "yt-dlp"

def get_ffmpeg_dir():
    candidates = [
        os.path.join(ROOT_DIR, "bin"),
        os.path.join(ROOT_DIR, "bin", "ffmpeg"),
        r"C:\ffmpeg\bin",
        r"C:\Program Files\ffmpeg\bin",
        os.path.expanduser(r"~\ffmpeg\bin")
    ]
    for c in candidates:
        if os.path.exists(os.path.join(c, "ffmpeg.exe")):
            return c
        elif os.path.exists(os.path.join(c, "bin", "ffmpeg.exe")):
            return os.path.join(c, "bin")
    return ""

def get_cookies_path():
    candidates = [
        os.path.join(ROOT_DIR, "cookies", "chrome"),
        os.path.join(ROOT_DIR, "cookies.txt"),
        r"C:\Users\joao3\Videos\yt-dlp-master\chrome",
        r"C:\Users\joao3\Videos\yt-dlp-master\cookies.txt",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


class AudioDownloaderView(BaseToolView):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            title="🎵 Music & Audio Downloader",
            description="Extract high-fidelity audio from YouTube, SoundCloud, Bandcamp, and 1000+ sites with ID3 tags, cover art, and chapter splitting.",
            **kwargs
        )

    def build_options(self, container: ctk.CTkFrame):
        # 1. Global Persistent Download Directory Config Bar
        self.config_card = ctk.CTkFrame(container, fg_color=COLORS["bg_terminal"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        self.config_card.pack(fill="x", pady=(0, 10), padx=2)

        config_inner = ctk.CTkFrame(self.config_card, fg_color="transparent")
        config_inner.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(
            config_inner,
            text="💾 Persistent Download Folder:",
            font=get_font(12, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(0, 8))

        self.global_save_entry = ctk.CTkEntry(
            config_inner,
            font=get_font(12),
            height=30
        )
        self.global_save_entry.insert(0, get_download_dir())
        self.global_save_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.browse_save_btn = ctk.CTkButton(
            config_inner,
            text="📁 Change & Save",
            font=get_font(12),
            width=120,
            height=30,
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_primary_hover"],
            command=self._change_global_download_dir
        )
        self.browse_save_btn.pack(side="right")

        # 2. Main Input Card
        self.input_card = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        self.input_card.pack(fill="x", pady=4, padx=2)

        inner = ctk.CTkFrame(self.input_card, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=12)

        # URL or Batch list
        ctk.CTkLabel(inner, text="Media URL, piped 'URL|Referer', or path to .txt batch list:", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 2))
        
        url_row = ctk.CTkFrame(inner, fg_color="transparent")
        url_row.pack(fill="x", pady=(0, 6))

        self.url_entry = ctk.CTkEntry(url_row, placeholder_text="https://www.youtube.com/watch?v=... or SoundCloud / Bandcamp / Playlist URL", height=34)
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

        # Referer & Custom filename row
        row_ref = ctk.CTkFrame(inner, fg_color="transparent")
        row_ref.pack(fill="x", pady=2)
        row_ref.columnconfigure((0, 1), weight=1)

        c1 = ctk.CTkFrame(row_ref, fg_color="transparent")
        c1.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(c1, text="Referer URL (Auto-detected from pipe or optional):", font=get_font(11)).pack(anchor="w")
        self.ref_entry = ctk.CTkEntry(c1, placeholder_text="https://example.com/...", height=32)
        self.ref_entry.pack(fill="x")

        c2 = ctk.CTkFrame(row_ref, fg_color="transparent")
        c2.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(c2, text="Custom Output File Name (Optional):", font=get_font(11)).pack(anchor="w")
        self.name_entry = ctk.CTkEntry(c2, placeholder_text="Leave blank to use track/video title", height=32)
        self.name_entry.pack(fill="x")

        self.url_entry.bind("<KeyRelease>", self._auto_split_piped_url)

        # Audio Format Selection Row
        ctk.CTkLabel(inner, text="Audio Format & Fidelity:", font=get_font(12, "bold")).pack(anchor="w", pady=(8, 2))
        
        self.fmt_segment = ctk.CTkSegmentedButton(
            inner,
            values=["MP3 (320k)", "MP3 (192k)", "M4A / AAC", "FLAC (Lossless)", "OPUS (160k)", "WAV"],
            font=get_font(11)
        )
        self.fmt_segment.set("MP3 (320k)")
        self.fmt_segment.pack(fill="x", pady=(0, 8))

        # Checkbox Options Row
        row_opts = ctk.CTkFrame(inner, fg_color="transparent")
        row_opts.pack(fill="x", pady=4)

        self.meta_chk = ctk.CTkCheckBox(row_opts, text="Embed Cover Art & ID3 Metadata", font=get_font(12))
        self.meta_chk.select()
        self.meta_chk.pack(side="left", padx=(0, 16))

        self.split_chk = ctk.CTkCheckBox(row_opts, text="Split into individual tracks by chapters", font=get_font(12))
        self.split_chk.pack(side="left", padx=(0, 16))

        self.playlist_chk = ctk.CTkCheckBox(row_opts, text="Number tracks if downloading playlist (01 - Title)", font=get_font(12))
        self.playlist_chk.select()
        self.playlist_chk.pack(side="left")

    def _change_global_download_dir(self):
        folder = filedialog.askdirectory(initialdir=get_download_dir())
        if folder:
            set_download_dir(folder)
            self.global_save_entry.delete(0, "end")
            self.global_save_entry.insert(0, folder)
            self.terminal.append_log(f"[*] Default download folder saved: {folder}\n")

    def get_effective_save_dir(self) -> str:
        custom = self.global_save_entry.get().strip()
        if custom and os.path.exists(custom):
            set_download_dir(custom)
            return custom
        return get_download_dir()

    def _browse_batch_txt(self):
        file_path = filedialog.askopenfilename(
            title="Select Text File with URLs",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, file_path)

    def _auto_split_piped_url(self, event=None):
        val = self.url_entry.get()
        if "|" in val:
            parts = val.split("|", 1)
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, parts[0].strip())
            self.ref_entry.delete(0, "end")
            self.ref_entry.insert(0, parts[1].strip())

    def on_start_clicked(self):
        raw_input = self.url_entry.get().strip()
        if not raw_input:
            self.terminal.clear()
            self.terminal.append_log("⚠️ Error: Please enter a media URL or select a .txt batch list file.\n")
            return

        ytdlp = get_ytdlp_path()
        ffmpeg_dir = get_ffmpeg_dir()
        save_dir = self.get_effective_save_dir()
        ref_url = self.ref_entry.get().strip()
        custom_name = self.name_entry.get().strip()
        fmt_choice = self.fmt_segment.get()

        is_batch = os.path.isfile(raw_input) and raw_input.lower().endswith(".txt")

        # Output filename template
        if is_batch:
            out_template = os.path.join(save_dir, "%(title)s.%(ext)s")
        elif custom_name:
            out_template = os.path.join(save_dir, f"{custom_name}.%(ext)s")
        elif self.playlist_chk.get():
            out_template = os.path.join(save_dir, "%(playlist_index&{:02d} - |)s%(title)s.%(ext)s")
        else:
            out_template = os.path.join(save_dir, "%(title)s.%(ext)s")

        cmd = [ytdlp]

        if is_batch:
            cmd.extend(["--batch-file", raw_input])
        else:
            cmd.append(raw_input)

        cmd.extend([
            "--newline",
            "-i",
            "-o", out_template,
            "--ignore-config",
            "--buffer-size", "16k",
            "--no-warning"
        ])

        # Format mappings
        if "192k" in fmt_choice:
            cmd.extend(["--extract-audio", "--audio-format", "mp3", "--audio-quality", "192K"])
        elif "M4A" in fmt_choice:
            cmd.extend(["--extract-audio", "--audio-format", "m4a", "--audio-quality", "0"])
        elif "FLAC" in fmt_choice:
            cmd.extend(["--extract-audio", "--audio-format", "flac", "--audio-quality", "0"])
        elif "OPUS" in fmt_choice:
            cmd.extend(["--extract-audio", "--audio-format", "opus", "--audio-quality", "0"])
        elif "WAV" in fmt_choice:
            cmd.extend(["--extract-audio", "--audio-format", "wav"])
        else:  # Default MP3 (320k)
            cmd.extend(["--extract-audio", "--audio-format", "mp3", "--audio-quality", "0"])

        # Metadata & thumbnail embedding
        if self.meta_chk.get():
            cmd.extend(["--embed-thumbnail", "--embed-metadata", "--embed-chapters", "--convert-thumbnails", "jpg"])
        else:
            cmd.extend(["--embed-metadata", "--embed-chapters"])

        # Chapter splitting
        if self.split_chk.get() and not is_batch:
            cmd.append("--split-chapters")

        # Cookies
        cookies = get_cookies_path()
        if cookies:
            cmd.extend(["--cookies", cookies])

        # FFmpeg location
        if ffmpeg_dir:
            cmd.extend(["--ffmpeg-location", ffmpeg_dir])

        # Referer & User-Agent
        if ref_url:
            cmd.extend([
                "--add-header", f"Referer: {ref_url}",
                "--add-header", f"Origin: {ref_url}",
                "--add-header", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ])

        self.execute_command(cmd)
