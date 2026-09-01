"""
Status bar showing tool health, binary discovery status (FFmpeg, yt-dlp, N_m3u8DL-RE), and hardware info.
"""
import os
import shutil
import subprocess
import customtkinter as ctk
from ui.theme import COLORS, get_font

ROOT_DIR = os.path.dirname(os.path.abspath(__file__ + "/../.."))

class StatusBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            height=28,
            fg_color=COLORS["bg_sidebar"],
            corner_radius=0,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs
        )
        self._build_ui()
        self.refresh_status()

    def _build_ui(self):
        # Left status indicators
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.pack(side="left", padx=12)

        self.ffmpeg_lbl = ctk.CTkLabel(
            self.left_frame,
            text="FFmpeg: Checking...",
            font=get_font(11),
            text_color=COLORS["text_muted"]
        )
        self.ffmpeg_lbl.pack(side="left", padx=(0, 12))

        self.ytdlp_lbl = ctk.CTkLabel(
            self.left_frame,
            text="yt-dlp: Checking...",
            font=get_font(11),
            text_color=COLORS["text_muted"]
        )
        self.ytdlp_lbl.pack(side="left", padx=(0, 12))

        self.nm3u8_lbl = ctk.CTkLabel(
            self.left_frame,
            text="N_m3u8: Checking...",
            font=get_font(11),
            text_color=COLORS["text_muted"]
        )
        self.nm3u8_lbl.pack(side="left", padx=(0, 12))

        self.aria2_lbl = ctk.CTkLabel(
            self.left_frame,
            text="aria2: Checking...",
            font=get_font(11),
            text_color=COLORS["text_muted"]
        )
        self.aria2_lbl.pack(side="left", padx=(0, 12))

        # Right status indicator (ready)
        self.ready_lbl = ctk.CTkLabel(
            self,
            text="🟢 Ready",
            font=get_font(11),
            text_color=COLORS["accent_success"]
        )
        self.ready_lbl.pack(side="right", padx=12)

    def refresh_status(self):
        # Check FFmpeg
        local_ffmpeg = os.path.exists(os.path.join(ROOT_DIR, "bin", "ffmpeg.exe")) or os.path.exists(os.path.join(ROOT_DIR, "bin", "ffmpeg", "bin", "ffmpeg.exe"))
        ffmpeg_found = local_ffmpeg or bool(shutil.which("ffmpeg")) or os.path.exists(r"C:\ffmpeg\bin\ffmpeg.exe")
        if local_ffmpeg:
            self.ffmpeg_lbl.configure(text="⚡ FFmpeg: OK (Portable)", text_color=COLORS["accent_success"])
        elif ffmpeg_found:
            self.ffmpeg_lbl.configure(text="⚡ FFmpeg: OK (System)", text_color=COLORS["accent_success"])
        else:
            self.ffmpeg_lbl.configure(text="⚠️ FFmpeg: Missing", text_color=COLORS["accent_warning"])

        # Check yt-dlp
        local_ytdlp = os.path.exists(os.path.join(ROOT_DIR, "bin", "yt-dlp.exe")) or os.path.exists(os.path.join(ROOT_DIR, "yt-dlp.exe"))
        ytdlp_found = local_ytdlp or bool(shutil.which("yt-dlp")) or os.path.exists(r"C:\Users\joao3\Videos\yt-dlp-master\yt-dlp.exe")
        if local_ytdlp:
            self.ytdlp_lbl.configure(text="📥 yt-dlp: OK (Portable)", text_color=COLORS["accent_success"])
        elif ytdlp_found:
            self.ytdlp_lbl.configure(text="📥 yt-dlp: OK (System)", text_color=COLORS["accent_success"])
        else:
            self.ytdlp_lbl.configure(text="⚠️ yt-dlp: Missing", text_color=COLORS["accent_warning"])

        # Check N_m3u8DL-RE
        local_nm3u8 = os.path.exists(os.path.join(ROOT_DIR, "bin", "N_m3u8DL-RE.exe"))
        nm3u8_found = local_nm3u8 or bool(shutil.which("N_m3u8DL-RE")) or os.path.exists(r"C:\ffmpeg\bin\N_m3u8DL-RE.exe")
        if local_nm3u8:
            self.nm3u8_lbl.configure(text="📡 N_m3u8: OK (Portable)", text_color=COLORS["accent_success"])
        elif nm3u8_found:
            self.nm3u8_lbl.configure(text="📡 N_m3u8: OK (System)", text_color=COLORS["accent_success"])
        else:
            self.nm3u8_lbl.configure(text="⚠️ N_m3u8: Missing", text_color=COLORS["text_muted"])

        # Check aria2c
        local_aria2 = os.path.exists(os.path.join(ROOT_DIR, "bin", "aria2c.exe")) or os.path.exists(os.path.join(ROOT_DIR, "aria2c.exe"))
        aria2_found = local_aria2 or bool(shutil.which("aria2c"))
        if local_aria2:
            self.aria2_lbl.configure(text="🚀 aria2: OK (Portable)", text_color=COLORS["accent_success"])
        elif aria2_found:
            self.aria2_lbl.configure(text="🚀 aria2: OK (System)", text_color=COLORS["accent_success"])
        else:
            self.aria2_lbl.configure(text="⚠️ aria2: Missing", text_color=COLORS["text_muted"])
