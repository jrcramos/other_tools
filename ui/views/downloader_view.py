"""
Stream, Video & Turbo Media Downloader View - Clearly separated tabs for:
1. 🎬 General Video Downloader (downloader.bat)
2. 🛡️ Proxy Video Downloader (downloader_proxy.bat)
3. 📚 Channel & Playlist Archiver (download_channel_playlist.cmd)
4. 📡 HLS / DASH / Live Streams (stream_downloader.py / stream_downloader.cmd)
5. 🎵 Audio & Music Downloader (download_audio.cmd)
6. 🚀 Turbo File Accelerator (aria2_downloader.cmd)
"""
import os
import shutil
import sys
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

def get_aria2_path():
    candidates = [
        os.path.join(ROOT_DIR, "bin", "aria2c.exe"),
        os.path.join(ROOT_DIR, "aria2c.exe"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return shutil.which("aria2c") or "aria2c"

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


class DownloaderView(BaseToolView):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            title="🌐 Video & Stream Downloader",
            description="Dedicated tool tabs for General Video, Proxy Downloads, Channel & Playlist Archiving, and M3U8/DASH Streams.",
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

        # 2. Distinct Tool Tabs
        self.tabview = ctk.CTkTabview(container, fg_color="transparent")
        self.tabview.pack(fill="both", expand=True)

        self.tab_general = self.tabview.add("🎬 General Video")
        self.tab_proxy = self.tabview.add("🛡️ Proxy Downloader")
        self.tab_playlist = self.tabview.add("📚 Channel / Playlist")
        self.tab_stream = self.tabview.add("📡 M3U8 / Live Streams")

        self._build_general_tab(self.tab_general)
        self._build_proxy_tab(self.tab_proxy)
        self._build_playlist_tab(self.tab_playlist)
        self._build_stream_tab(self.tab_stream)

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

    def _auto_split_piped_url(self, url_entry: ctk.CTkEntry, ref_entry: ctk.CTkEntry):
        """Auto-detects URL|Referer piped format and populates both fields automatically."""
        val = url_entry.get()
        if "|" in val:
            parts = val.split("|", 1)
            url_entry.delete(0, "end")
            url_entry.insert(0, parts[0].strip())
            ref_entry.delete(0, "end")
            ref_entry.insert(0, parts[1].strip())

    # -------------------------------------------------------------------------
    # TAB 1: General Video Downloader (downloader.bat)
    # -------------------------------------------------------------------------
    def _build_general_tab(self, tab):
        ctk.CTkLabel(tab, text="Video URL (Supports direct URL or pasted 'URL|Referer'):", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 2))
        self.gen_url_entry = ctk.CTkEntry(tab, placeholder_text="Paste video URL or piped URL|Referer...", height=34)
        self.gen_url_entry.pack(fill="x", pady=(0, 6))

        row_ref = ctk.CTkFrame(tab, fg_color="transparent")
        row_ref.pack(fill="x", pady=2)
        row_ref.columnconfigure((0, 1), weight=1)

        c1 = ctk.CTkFrame(row_ref, fg_color="transparent")
        c1.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(c1, text="Referer URL (Auto-detected from pipe or optional):", font=get_font(11)).pack(anchor="w")
        self.gen_ref_entry = ctk.CTkEntry(c1, placeholder_text="https://example.com/embed/...", height=32)
        self.gen_ref_entry.pack(fill="x")

        c2 = ctk.CTkFrame(row_ref, fg_color="transparent")
        c2.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(c2, text="Custom Output File Name (Optional):", font=get_font(11)).pack(anchor="w")
        self.gen_name_entry = ctk.CTkEntry(c2, placeholder_text="Leave blank to use video title", height=32)
        self.gen_name_entry.pack(fill="x")

        self.gen_url_entry.bind("<KeyRelease>", lambda e: self._auto_split_piped_url(self.gen_url_entry, self.gen_ref_entry))

        row_ctrl = ctk.CTkFrame(tab, fg_color="transparent")
        row_ctrl.pack(fill="x", pady=6)
        row_ctrl.columnconfigure((0, 1), weight=1)

        f1 = ctk.CTkFrame(row_ctrl, fg_color="transparent")
        f1.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(f1, text="Quality / Resolution:", font=get_font(11, "bold")).pack(anchor="w")
        self.gen_quality = ctk.CTkSegmentedButton(f1, values=["Best (4K/1080p)", "Max 1080p", "Max 720p"], font=get_font(11))
        self.gen_quality.set("Best (4K/1080p)")
        self.gen_quality.pack(fill="x", pady=2)

        f2 = ctk.CTkFrame(row_ctrl, fg_color="transparent")
        f2.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(f2, text="Subtitles & Streams:", font=get_font(11, "bold")).pack(anchor="w")
        self.gen_subs = ctk.CTkSegmentedButton(f2, values=["All Subtitles", "Auto/EN", "No Subs"], font=get_font(11))
        self.gen_subs.set("All Subtitles")
        self.gen_subs.pack(fill="x", pady=2)

    # -------------------------------------------------------------------------
    # TAB 2: Proxy Video Downloader (downloader_proxy.bat)
    # -------------------------------------------------------------------------
    def _build_proxy_tab(self, tab):
        ctk.CTkLabel(tab, text="Video URL (Supports piped URL|Referer):", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 2))
        self.proxy_url_entry = ctk.CTkEntry(tab, placeholder_text="Paste video URL or piped URL|Referer...", height=34)
        self.proxy_url_entry.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(tab, text="SOCKS5 / HTTP Proxy URL:", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 2))
        self.proxy_addr_entry = ctk.CTkEntry(tab, font=get_font(11), height=32)
        self.proxy_addr_entry.insert(0, "socks5://pvetbwz00882:lsp3hmupkzzu@lis.socks.privado.io:1080")
        self.proxy_addr_entry.pack(fill="x", pady=(0, 6))

        row_p = ctk.CTkFrame(tab, fg_color="transparent")
        row_p.pack(fill="x", pady=2)
        row_p.columnconfigure((0, 1), weight=1)

        c1 = ctk.CTkFrame(row_p, fg_color="transparent")
        c1.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(c1, text="Referer URL (Optional):", font=get_font(11)).pack(anchor="w")
        self.proxy_ref_entry = ctk.CTkEntry(c1, placeholder_text="https://example.com/...", height=32)
        self.proxy_ref_entry.pack(fill="x")

        c2 = ctk.CTkFrame(row_p, fg_color="transparent")
        c2.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(c2, text="Custom Output File Name (Optional):", font=get_font(11)).pack(anchor="w")
        self.proxy_name_entry = ctk.CTkEntry(c2, placeholder_text="Leave blank to use video title", height=32)
        self.proxy_name_entry.pack(fill="x")

        self.proxy_url_entry.bind("<KeyRelease>", lambda e: self._auto_split_piped_url(self.proxy_url_entry, self.proxy_ref_entry))

        row_q = ctk.CTkFrame(tab, fg_color="transparent")
        row_q.pack(fill="x", pady=6)
        ctk.CTkLabel(row_q, text="Quality:", font=get_font(11, "bold")).pack(side="left", padx=(0, 10))
        self.proxy_quality = ctk.CTkSegmentedButton(row_q, values=["Best (4K/1080p)", "Max 1080p", "Max 720p"], font=get_font(11))
        self.proxy_quality.set("Best (4K/1080p)")
        self.proxy_quality.pack(side="left", fill="x", expand=True)

    # -------------------------------------------------------------------------
    # TAB 3: Channel & Playlist Archiver (download_channel_playlist.cmd)
    # -------------------------------------------------------------------------
    def _build_playlist_tab(self, tab):
        ctk.CTkLabel(tab, text="Channel or Playlist URL:", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 2))
        self.pl_url_entry = ctk.CTkEntry(tab, placeholder_text="https://www.youtube.com/playlist?list=... or @Channel/videos", height=34)
        self.pl_url_entry.pack(fill="x", pady=(0, 8))

        row1 = ctk.CTkFrame(tab, fg_color="transparent")
        row1.pack(fill="x", pady=4)
        row1.columnconfigure((0, 1), weight=1)

        f1 = ctk.CTkFrame(row1, fg_color="transparent")
        f1.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(f1, text="Download Quality:", font=get_font(12, "bold")).pack(anchor="w")
        self.pl_quality_combo = ctk.CTkComboBox(
            f1,
            values=["Best Video + Audio (Up to 4K/1080p, MP4)", "Max 1080p Full HD (MP4)", "Max 720p HD (Compact MP4)", "Audio Only (MP3 320k)", "Audio Only (M4A)"],
            font=get_font(12),
            height=32
        )
        self.pl_quality_combo.set("Best Video + Audio (Up to 4K/1080p, MP4)")
        self.pl_quality_combo.pack(fill="x", pady=2)

        f2 = ctk.CTkFrame(row1, fg_color="transparent")
        f2.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(f2, text="Naming Scheme:", font=get_font(12, "bold")).pack(anchor="w")
        self.pl_naming_combo = ctk.CTkComboBox(
            f2,
            values=["Numbered Index (01 - Title.mp4) [Best for Courses]", "Upload Date ([YYYY-MM-DD] Title.mp4)", "Simple (Title.mp4)"],
            font=get_font(12),
            height=32
        )
        self.pl_naming_combo.set("Numbered Index (01 - Title.mp4) [Best for Courses]")
        self.pl_naming_combo.pack(fill="x", pady=2)

        row_range = ctk.CTkFrame(tab, fg_color="transparent")
        row_range.pack(fill="x", pady=4)
        row_range.columnconfigure((0, 1), weight=1)

        r1 = ctk.CTkFrame(row_range, fg_color="transparent")
        r1.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(r1, text="Item Range (e.g. 1:20, or leave blank for All):", font=get_font(11)).pack(anchor="w")
        self.pl_range_entry = ctk.CTkEntry(r1, placeholder_text="All items (or e.g. 1:15)", height=32)
        self.pl_range_entry.pack(fill="x")

        r2 = ctk.CTkFrame(row_range, fg_color="transparent")
        r2.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(r2, text="Max Latest Items (Optional):", font=get_font(11)).pack(anchor="w")
        self.pl_max_entry = ctk.CTkEntry(r2, placeholder_text="e.g. 5 or 10", height=32)
        self.pl_max_entry.pack(fill="x")

        row2 = ctk.CTkFrame(tab, fg_color="transparent")
        row2.pack(fill="x", pady=6)

        self.pl_archive_chk = ctk.CTkCheckBox(row2, text="Archive Sync (Skip already downloaded videos on re-run)", font=get_font(12))
        self.pl_archive_chk.select()
        self.pl_archive_chk.pack(side="left", padx=(0, 14))

        self.pl_subs_chk = ctk.CTkCheckBox(row2, text="Embed Subtitles (EN/PT/Auto)", font=get_font(12))
        self.pl_subs_chk.select()
        self.pl_subs_chk.pack(side="left")

    # -------------------------------------------------------------------------
    # TAB 4: M3U8 / DASH Live Streams (stream_downloader.py / .cmd)
    # -------------------------------------------------------------------------
    def _build_stream_tab(self, tab):
        ctk.CTkLabel(tab, text="Stream URL (.m3u8, .mpd, or live web stream):", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 2))
        self.stream_url_entry = ctk.CTkEntry(tab, placeholder_text="https://.../manifest.m3u8 or https://.../manifest.mpd", height=34)
        self.stream_url_entry.pack(fill="x", pady=(0, 6))

        row1 = ctk.CTkFrame(tab, fg_color="transparent")
        row1.pack(fill="x", pady=2)
        row1.columnconfigure((0, 1), weight=1)

        c1 = ctk.CTkFrame(row1, fg_color="transparent")
        c1.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(c1, text="Referer URL (Optional):", font=get_font(11)).pack(anchor="w")
        self.stream_ref_entry = ctk.CTkEntry(c1, placeholder_text="https://example.com/player", height=32)
        self.stream_ref_entry.pack(fill="x")

        c2 = ctk.CTkFrame(row1, fg_color="transparent")
        c2.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(c2, text="Custom Output File Name (Optional):", font=get_font(11)).pack(anchor="w")
        self.stream_name_entry = ctk.CTkEntry(c2, placeholder_text="my_downloaded_stream", height=32)
        self.stream_name_entry.pack(fill="x")

        self.stream_url_entry.bind("<KeyRelease>", lambda e: self._auto_split_piped_url(self.stream_url_entry, self.stream_ref_entry))

        row_eng = ctk.CTkFrame(tab, fg_color="transparent")
        row_eng.pack(fill="x", pady=6)
        ctk.CTkLabel(row_eng, text="Engine:", font=get_font(11, "bold")).pack(side="left", padx=(0, 10))
        self.stream_engine = ctk.CTkSegmentedButton(
            row_eng,
            values=["Auto-Detect Best Engine", "N_m3u8DL-RE (16-Thread Fast)", "Streamlink (Live Recording)", "yt-dlp Native"],
            font=get_font(11)
        )
        self.stream_engine.set("Auto-Detect Best Engine")
        self.stream_engine.pack(side="left", fill="x", expand=True)

    # -------------------------------------------------------------------------
    # Execution Dispatcher
    # -------------------------------------------------------------------------
    def on_start_clicked(self):
        active_tab = self.tabview.get()
        ytdlp = get_ytdlp_path()
        ffmpeg_dir = get_ffmpeg_dir()

        if "General Video" in active_tab:
            self._run_general(ytdlp, ffmpeg_dir)
        elif "Proxy" in active_tab:
            self._run_proxy(ytdlp, ffmpeg_dir)
        elif "Playlist" in active_tab:
            self._run_playlist(ytdlp, ffmpeg_dir)
        elif "Stream" in active_tab:
            self._run_stream(ytdlp, ffmpeg_dir)

    def _run_general(self, ytdlp, ffmpeg_dir):
        raw_url = self.gen_url_entry.get().strip()
        if not raw_url:
            self.terminal.clear()
            self.terminal.append_log("⚠️ Error: Please enter a video URL.\n")
            return

        ref_url = self.gen_ref_entry.get().strip()
        custom_name = self.gen_name_entry.get().strip()
        save_dir = self.get_effective_save_dir()
        out_template = os.path.join(save_dir, f"{custom_name}.%(ext)s" if custom_name else "%(title)s.%(ext)s")

        cmd = [
            ytdlp,
            raw_url,
            "--newline",
            "-i",
            "-o", out_template,
            "--ignore-config",
            "--hls-prefer-native",
            "--buffer-size", "16k",
            "--no-warning",
            "--remux-video", "mp4",
            "--audio-multistreams"
        ]

        q = self.gen_quality.get()
        if "720p" in q:
            cmd.extend(["-f", "bestvideo[height<=?720]+bestaudio/best[height<=?720]/bestvideo+bestaudio/best/b"])
        elif "Max 1080p" in q:
            cmd.extend(["-f", "bestvideo[height<=?1080]+bestaudio/best[height<=?1080]/bestvideo+bestaudio/best/b"])
        else:
            cmd.extend(["-f", "bestvideo+bestaudio/best/b"])

        subs = self.gen_subs.get()
        if "All" in subs:
            cmd.extend(["--all-subs", "--sub-langs", "all"])
        elif "Auto" in subs:
            cmd.extend(["--write-subs", "--write-auto-subs", "--sub-langs", "en.*,pt.*", "--embed-subs"])

        cookies = get_cookies_path()
        if cookies:
            cmd.extend(["--cookies", cookies])

        if ffmpeg_dir:
            cmd.extend(["--ffmpeg-location", ffmpeg_dir])
        if ref_url:
            cmd.extend(["--add-header", f"Referer: {ref_url}", "--add-header", f"Origin: {ref_url}", "--add-header", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"])

        self.execute_command(cmd)

    def _run_proxy(self, ytdlp, ffmpeg_dir):
        raw_url = self.proxy_url_entry.get().strip()
        if not raw_url:
            self.terminal.clear()
            self.terminal.append_log("⚠️ Error: Please enter a video URL.\n")
            return

        proxy_addr = self.proxy_addr_entry.get().strip()
        ref_url = self.proxy_ref_entry.get().strip()
        custom_name = self.proxy_name_entry.get().strip()
        save_dir = self.get_effective_save_dir()
        out_template = os.path.join(save_dir, f"{custom_name}.%(ext)s" if custom_name else "%(title)s.%(ext)s")

        cmd = [
            ytdlp,
            raw_url,
            "--newline",
            "-i",
            "--all-subs",
            "-o", out_template,
            "--ignore-config",
            "--hls-prefer-native",
            "--buffer-size", "16k",
            "--no-warning",
            "--remux-video", "mp4",
            "--audio-multistreams",
            "--sub-langs", "all"
        ]

        if proxy_addr:
            cmd.extend(["--proxy", proxy_addr])

        q = self.proxy_quality.get()
        if "720p" in q:
            cmd.extend(["-f", "bestvideo[height<=?720]+bestaudio/best[height<=?720]/bestvideo+bestaudio/best/b"])
        elif "Max 1080p" in q:
            cmd.extend(["-f", "bestvideo[height<=?1080]+bestaudio/best[height<=?1080]/bestvideo+bestaudio/best/b"])
        else:
            cmd.extend(["-f", "bestvideo+bestaudio/best/b"])

        cookies = get_cookies_path()
        if cookies:
            cmd.extend(["--cookies", cookies])

        if ffmpeg_dir:
            cmd.extend(["--ffmpeg-location", ffmpeg_dir])
        if ref_url:
            cmd.extend(["--add-header", f"Referer: {ref_url}", "--add-header", f"Origin: {ref_url}", "--add-header", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"])

        self.execute_command(cmd)

    def _run_playlist(self, ytdlp, ffmpeg_dir):
        raw_url = self.pl_url_entry.get().strip()
        if not raw_url:
            self.terminal.clear()
            self.terminal.append_log("⚠️ Error: Please enter a channel or playlist URL.\n")
            return

        save_dir = self.get_effective_save_dir()
        naming = self.pl_naming_combo.get()
        if "Numbered" in naming:
            out_template = os.path.join(save_dir, "%(uploader,playlist_uploader,playlist_title)s/%(playlist_index&{:02d} - |)s%(title)s.%(ext)s")
        elif "Upload Date" in naming:
            out_template = os.path.join(save_dir, "%(uploader,playlist_uploader,channel)s/[%(upload_date)s] %(title)s.%(ext)s")
        else:
            out_template = os.path.join(save_dir, "%(uploader,playlist_uploader,channel)s/%(title)s.%(ext)s")

        quality = self.pl_quality_combo.get()
        cmd = [ytdlp, raw_url, "--newline", "-i", "-o", out_template]

        if "Audio Only" in quality:
            if "MP3" in quality:
                cmd.extend(["--extract-audio", "--audio-format", "mp3", "--audio-quality", "0", "--embed-thumbnail", "--convert-thumbnails", "jpg"])
            else:
                cmd.extend(["--extract-audio", "--audio-format", "m4a", "--audio-quality", "0", "--embed-thumbnail", "--convert-thumbnails", "jpg"])
        elif "720p" in quality:
            cmd.extend(["-f", "bestvideo[height<=?720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=?720]+bestaudio/best[height<=?720]/bestvideo+bestaudio/best/b", "--remux-video", "mp4"])
        elif "1080p" in quality and "Up to" not in quality:
            cmd.extend(["-f", "bestvideo[height<=?1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=?1080]+bestaudio/best[height<=?1080]/bestvideo+bestaudio/best/b", "--remux-video", "mp4"])
        else:
            cmd.extend(["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best/b", "--remux-video", "mp4"])

        range_val = self.pl_range_entry.get().strip()
        if range_val and ":" in range_val:
            cmd.extend(["--playlist-items", range_val])
        elif range_val:
            cmd.extend(["--playlist-start", range_val])

        max_val = self.pl_max_entry.get().strip()
        if max_val:
            cmd.extend(["--max-downloads", max_val])

        if self.pl_archive_chk.get():
            archive_file = os.path.join(save_dir, "download_archive.txt")
            cmd.extend(["--download-archive", archive_file])

        if self.pl_subs_chk.get() and "Audio" not in quality:
            cmd.extend(["--write-subs", "--write-auto-subs", "--sub-langs", "en.*,pt.*", "--embed-subs"])

        cmd.extend(["--embed-metadata", "--embed-chapters"])
        if ffmpeg_dir:
            cmd.extend(["--ffmpeg-location", ffmpeg_dir])

        self.execute_command(cmd)

    def _run_stream(self, ytdlp, ffmpeg_dir):
        raw_url = self.stream_url_entry.get().strip()
        if not raw_url:
            self.terminal.clear()
            self.terminal.append_log("⚠️ Error: Please enter a stream manifest URL.\n")
            return

        ref_url = self.stream_ref_entry.get().strip()
        name = self.stream_name_entry.get().strip()
        save_dir = self.get_effective_save_dir()
        out_template = os.path.join(save_dir, f"{name}.%(ext)s" if name else "%(title)s.%(ext)s")

        stream_py = os.path.join(ROOT_DIR, "stream_downloader.py")
        engine_choice = self.stream_engine.get()

        if "N_m3u8" in engine_choice:
            nm3u8_bin = os.path.join(ROOT_DIR, "bin", "N_m3u8DL-RE.exe")
            if not os.path.exists(nm3u8_bin):
                nm3u8_bin = shutil.which("N_m3u8DL-RE") or "N_m3u8DL-RE"
            cmd = [nm3u8_bin, raw_url, "--save-dir", save_dir, "--auto-select", "--thread-count", "16", "--check-segments-count", "false"]
            if name:
                cmd.extend(["--save-name", name])
            if ref_url:
                cmd.extend(["--header", f"Referer:{ref_url}", "--header", f"Origin:{ref_url}"])
            self.execute_command(cmd, cwd=save_dir)
        elif "Streamlink" in engine_choice:
            cmd = ["streamlink", "--output", os.path.join(save_dir, f"{name or 'livestream'}.mp4"), raw_url, "best"]
            if ref_url:
                cmd.extend(["--http-header", f"Referer={ref_url}"])
            self.execute_command(cmd, cwd=save_dir)
        elif os.path.exists(stream_py) and "Auto" in engine_choice:
            cmd = [sys.executable, stream_py, raw_url]
            if ref_url:
                cmd.extend(["--referer", ref_url])
            if name:
                cmd.extend(["--output", name])
            self.execute_command(cmd, cwd=ROOT_DIR)
        else:
            cmd = [ytdlp, raw_url, "--newline", "-i", "-o", out_template, "--hls-prefer-native", "--remux-video", "mp4"]
            if ref_url:
                cmd.extend(["--add-header", f"Referer: {ref_url}", "--add-header", f"Origin: {ref_url}"])
            if ffmpeg_dir:
                cmd.extend(["--ffmpeg-location", ffmpeg_dir])
            self.execute_command(cmd)
