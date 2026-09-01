"""
Live Stream Recorder & Monitor View - Powered by Streamlink, yt-dlp, and FFmpeg.
Captures live broadcasts from Twitch, Kick, YouTube Live, TikTok, and direct M3U8/HLS streams with auto-monitor mode.
"""
import os
import shutil
import datetime
import re
import customtkinter as ctk
from tkinter import filedialog
from ui.theme import COLORS, get_font
from ui.views.base_view import BaseToolView
from config_manager import get_download_dir, set_download_dir

ROOT_DIR = os.path.dirname(os.path.abspath(__file__ + "/../.."))

def find_binary(name):
    search_dirs = [
        os.path.join(ROOT_DIR, "bin"),
        os.path.join(ROOT_DIR, "bin", "ffmpeg", "bin"),
        ROOT_DIR,
        r"C:\ffmpeg\bin",
        r"C:\Program Files\ffmpeg\bin",
        os.path.expanduser(r"~\ffmpeg\bin"),
        os.path.expanduser(r"~\Videos\yt-dlp-master"),
    ]
    for d in search_dirs:
        candidate = os.path.join(d, f"{name}.exe")
        if os.path.isfile(candidate):
            return candidate
    return shutil.which(name) or name


class LiveStreamView(BaseToolView):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            title="📡 Live Stream Recorder & Monitor",
            description="Record live broadcasts from Twitch, Kick, YouTube Live, and HLS streams. Includes Auto-Monitor mode to start recording the moment a streamer goes live.",
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
            text="💾 Persistent Stream Recordings Folder:",
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

        # 2. Main Stream Input Card
        self.input_card = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        self.input_card.pack(fill="x", pady=4, padx=2)

        inner = ctk.CTkFrame(self.input_card, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=12)

        # Stream URL
        ctk.CTkLabel(inner, text="Stream or Channel URL (Twitch, Kick, YouTube Live, TikTok, or direct .m3u8 / .mpd):", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 2))
        
        self.url_entry = ctk.CTkEntry(inner, placeholder_text="https://twitch.tv/streamer, https://kick.com/streamer, or https://.../playlist.m3u8", height=34)
        self.url_entry.pack(fill="x", pady=(0, 6))

        # Referer & Custom File Name
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
        ctk.CTkLabel(c2, text="Streamer / File Name (Optional):", font=get_font(11)).pack(anchor="w")
        self.name_entry = ctk.CTkEntry(c2, placeholder_text="Leave blank to use StreamerName_Timestamp", height=32)
        self.name_entry.pack(fill="x")

        self.url_entry.bind("<KeyRelease>", self._auto_split_piped_url)

        # Mode Selection
        row_mode = ctk.CTkFrame(inner, fg_color="transparent")
        row_mode.pack(fill="x", pady=(8, 4))
        ctk.CTkLabel(row_mode, text="Recording Mode:", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 2))

        self.mode_segment = ctk.CTkSegmentedButton(
            row_mode,
            values=["🔴 Record Live Stream Now", "⏱️ Auto-Monitor & Record When Live"],
            font=get_font(11)
        )
        self.mode_segment.set("🔴 Record Live Stream Now")
        self.mode_segment.pack(fill="x")

        # Controls Row (Quality, Engine, Duration Limit)
        row_ctrl = ctk.CTkFrame(inner, fg_color="transparent")
        row_ctrl.pack(fill="x", pady=6)
        row_ctrl.columnconfigure((0, 1, 2), weight=1)

        # Quality
        f1 = ctk.CTkFrame(row_ctrl, fg_color="transparent")
        f1.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ctk.CTkLabel(f1, text="Quality Preset:", font=get_font(11, "bold")).pack(anchor="w")
        self.quality_combo = ctk.CTkComboBox(
            f1,
            values=["Best (Source Quality)", "1080p60", "720p60", "480p", "Audio Only"],
            font=get_font(11),
            height=30
        )
        self.quality_combo.set("Best (Source Quality)")
        self.quality_combo.pack(fill="x", pady=2)

        # Engine
        f2 = ctk.CTkFrame(row_ctrl, fg_color="transparent")
        f2.grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkLabel(f2, text="Recording Engine:", font=get_font(11, "bold")).pack(anchor="w")
        self.engine_combo = ctk.CTkComboBox(
            f2,
            values=["Auto-Detect Best Engine", "Streamlink (Twitch/Kick/Live)", "yt-dlp Native", "FFmpeg HLS Capture"],
            font=get_font(11),
            height=30
        )
        self.engine_combo.set("Auto-Detect Best Engine")
        self.engine_combo.pack(fill="x", pady=2)

        # Duration Limit
        f3 = ctk.CTkFrame(row_ctrl, fg_color="transparent")
        f3.grid(row=0, column=2, sticky="ew", padx=(4, 0))
        ctk.CTkLabel(f3, text="Max Recording Duration:", font=get_font(11, "bold")).pack(anchor="w")
        self.duration_combo = ctk.CTkComboBox(
            f3,
            values=["Continuous (Stop manually)", "Limit: 30 Minutes", "Limit: 1 Hour", "Limit: 2 Hours", "Limit: 4 Hours", "Limit: 8 Hours"],
            font=get_font(11),
            height=30
        )
        self.duration_combo.set("Continuous (Stop manually)")
        self.duration_combo.pack(fill="x", pady=2)

    def _change_global_download_dir(self):
        folder = filedialog.askdirectory(initialdir=get_download_dir())
        if folder:
            set_download_dir(folder)
            self.global_save_entry.delete(0, "end")
            self.global_save_entry.insert(0, folder)
            self.terminal.append_log(f"[*] Default recordings folder saved: {folder}\n")

    def get_effective_save_dir(self) -> str:
        custom = self.global_save_entry.get().strip()
        if custom and os.path.exists(custom):
            set_download_dir(custom)
            return custom
        return get_download_dir()

    def _auto_split_piped_url(self, event=None):
        val = self.url_entry.get()
        if "|" in val:
            parts = val.split("|", 1)
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, parts[0].strip())
            self.ref_entry.delete(0, "end")
            self.ref_entry.insert(0, parts[1].strip())

    def on_start_clicked(self):
        raw_url = self.url_entry.get().strip()
        if not raw_url:
            self.terminal.clear()
            self.terminal.append_log("⚠️ Error: Please enter a stream or channel URL.\n")
            return

        ref_url = self.ref_entry.get().strip()
        custom_name = self.name_entry.get().strip()
        save_dir = self.get_effective_save_dir()
        mode = self.mode_segment.get()
        quality_choice = self.quality_combo.get()
        engine_choice = self.engine_combo.get()
        duration_choice = self.duration_combo.get()

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if custom_name:
            out_base = custom_name
        else:
            # Extract streamer name from URL if possible
            match = re.search(r'(?:twitch\.tv|kick\.com)/([a-zA-Z0-9_-]+)', raw_url, re.IGNORECASE)
            streamer = match.group(1) if match else "Stream"
            out_base = f"{streamer}_{timestamp}"

        out_file = os.path.join(save_dir, f"{out_base}.mp4")

        streamlink = find_binary("streamlink")
        ytdlp = find_binary("yt-dlp")
        ffmpeg = find_binary("ffmpeg")

        has_streamlink = streamlink and (os.path.isfile(streamlink) or shutil.which(streamlink))
        is_twitch_kick = any(k in raw_url.lower() for k in ["twitch.tv", "kick.com", "tiktok.com"])

        # Decide Engine
        chosen_engine = "streamlink" if ("Streamlink" in engine_choice or ("Auto" in engine_choice and has_streamlink and is_twitch_kick)) else "ytdlp"
        if "FFmpeg" in engine_choice:
            chosen_engine = "ffmpeg"

        is_monitor = "Auto-Monitor" in mode

        self.terminal.clear()
        self.terminal.append_log("=" * 68 + "\n")
        self.terminal.append_log(f"📡 Live Stream Recording: {raw_url}\n")
        self.terminal.append_log(f"📁 Destination File:    {out_file}\n")
        self.terminal.append_log(f"⚙️  Engine / Mode:       {chosen_engine.upper()} | {'Auto-Monitor Mode' if is_monitor else 'Direct Capture'}\n")
        self.terminal.append_log("💡 Click the Red Stop Button anytime to gracefully stop and finalize the MP4 video.\n")
        self.terminal.append_log("=" * 68 + "\n\n")

        # Map Quality
        streamlink_q = "best"
        ytdlp_q = "bestvideo+bestaudio/best/b"
        if "1080p" in quality_choice:
            streamlink_q = "1080p60,1080p,best"
            ytdlp_q = "bestvideo[height<=?1080]+bestaudio/best[height<=?1080]/bestvideo+bestaudio/best/b"
        elif "720p" in quality_choice:
            streamlink_q = "720p60,720p,best"
            ytdlp_q = "bestvideo[height<=?720]+bestaudio/best[height<=?720]/bestvideo+bestaudio/best/b"
        elif "480p" in quality_choice:
            streamlink_q = "480p,best"
            ytdlp_q = "bestvideo[height<=?480]+bestaudio/best[height<=?480]/bestvideo+bestaudio/best/b"
        elif "Audio" in quality_choice:
            streamlink_q = "audio_only,best"
            ytdlp_q = "bestaudio/best"

        if chosen_engine == "streamlink" and has_streamlink:
            cmd = [streamlink, raw_url, streamlink_q, "-o", out_file, "--force"]
            if is_monitor:
                cmd.extend(["--retry-streams", "15", "--retry-open", "3"])
            if ref_url:
                cmd.extend(["--http-header", f"Referer={ref_url}"])
            if ffmpeg and (os.path.isfile(ffmpeg) or shutil.which(ffmpeg)):
                cmd.extend(["--ffmpeg-ffmpeg", ffmpeg])
            self.execute_command(cmd)

        elif chosen_engine == "ffmpeg" and ffmpeg:
            cmd = [ffmpeg, "-hide_banner", "-y"]
            if ref_url:
                cmd.extend(["-headers", f"Referer: {ref_url}\r\nOrigin: {ref_url}\r\n"])
            cmd.extend(["-i", raw_url, "-c", "copy", out_file])
            self.execute_command(cmd)

        else: # Default yt-dlp
            cmd = [
                ytdlp,
                raw_url,
                "--newline",
                "-i",
                "-o", out_file,
                "--hls-prefer-native",
                "-f", ytdlp_q,
                "--remux-video", "mp4",
                "--no-part"
            ]
            if is_monitor:
                cmd.extend(["--wait-for-video", "15"])
            if ref_url:
                cmd.extend([
                    "--add-header", f"Referer: {ref_url}",
                    "--add-header", f"Origin: {ref_url}",
                    "--add-header", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                ])
            if ffmpeg:
                ffmpeg_dir = os.path.dirname(ffmpeg) if os.path.isfile(ffmpeg) else ""
                if ffmpeg_dir:
                    cmd.extend(["--ffmpeg-location", ffmpeg_dir])
            self.execute_command(cmd)
