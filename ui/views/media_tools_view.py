"""
Media Utilities View - Tabbed workspace for GIF/WebP creation, Trimming, Joining, Snapshots, and Audio Extraction.
"""
import os
import shutil
import subprocess
import customtkinter as ctk
from ui.theme import COLORS, get_font
from ui.views.base_view import BaseToolView
from ui.components.file_picker import FilePicker

ROOT_DIR = os.path.dirname(os.path.abspath(__file__ + "/../.."))

def get_ffmpeg_path():
    candidates = [
        os.path.join(ROOT_DIR, "bin", "ffmpeg.exe"),
        os.path.join(ROOT_DIR, "bin", "ffmpeg", "bin", "ffmpeg.exe"),
        os.path.join(ROOT_DIR, "ffmpeg.exe"),
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        os.path.expanduser(r"~\ffmpeg\bin\ffmpeg.exe")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return shutil.which("ffmpeg") or "ffmpeg"

def get_ffprobe_path():
    candidates = [
        os.path.join(ROOT_DIR, "bin", "ffprobe.exe"),
        os.path.join(ROOT_DIR, "bin", "ffmpeg", "bin", "ffprobe.exe"),
        os.path.join(ROOT_DIR, "ffprobe.exe"),
        r"C:\ffmpeg\bin\ffprobe.exe",
        r"C:\Program Files\ffmpeg\bin\ffprobe.exe",
        os.path.expanduser(r"~\ffmpeg\bin\ffprobe.exe")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return shutil.which("ffprobe") or "ffprobe"


class MediaToolsView(BaseToolView):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            title="✂️ Media Utilities & Video Toolkit",
            description="Fast FFmpeg tools for Target Size Compression, GIF/WebP conversion, lossless cutting, joining, contact sheets, and audio extraction.",
            **kwargs
        )

    def build_options(self, container: ctk.CTkFrame):
        self.tabview = ctk.CTkTabview(container, fg_color="transparent")
        self.tabview.pack(fill="both", expand=True)

        self.tab_target = self.tabview.add("🎯 Target Size")
        self.tab_gif = self.tabview.add("🎞️ GIF / WebP")
        self.tab_cut = self.tabview.add("✂️ Cut / Trim")
        self.tab_join = self.tabview.add("🔗 Join Videos")
        self.tab_snap = self.tabview.add("📸 Snapshots & Grid")
        self.tab_audio = self.tabview.add("🎵 Extract Audio")

        self._build_target_tab(self.tab_target)
        self._build_gif_tab(self.tab_gif)
        self._build_cut_tab(self.tab_cut)
        self._build_join_tab(self.tab_join)
        self._build_snap_tab(self.tab_snap)
        self._build_audio_tab(self.tab_audio)

    # -------------------------------------------------------------------------
    # TAB 0: Target Size / Social Media Compressor
    # -------------------------------------------------------------------------
    def _build_target_tab(self, tab):
        self.target_picker = FilePicker(tab, label_text="Input Video File:", placeholder="Select video to compress to target size...")
        self.target_picker.pack(fill="x", pady=(0, 8))

        row1 = ctk.CTkFrame(tab, fg_color="transparent")
        row1.pack(fill="x", pady=4)
        row1.columnconfigure((0, 1, 2), weight=1)

        # Preset
        f1 = ctk.CTkFrame(row1, fg_color="transparent")
        f1.grid(row=0, column=0, sticky="ew", padx=4)
        ctk.CTkLabel(f1, text="Platform / Size Preset:", font=get_font(12, "bold")).pack(anchor="w")
        self.target_preset = ctk.CTkComboBox(
            f1,
            values=[
                "Discord Free (25 MB)",
                "Discord Nitro (50 MB)",
                "Discord Nitro (100 MB)",
                "WhatsApp Video (16 MB)",
                "WhatsApp Large (64 MB)",
                "Telegram (50 MB)",
                "Email Attachment (10 MB)",
                "Custom Size (MB)"
            ],
            font=get_font(11),
            command=self._on_target_preset_changed
        )
        self.target_preset.set("Discord Free (25 MB)")
        self.target_preset.pack(fill="x", pady=2)

        # Custom MB
        f2 = ctk.CTkFrame(row1, fg_color="transparent")
        f2.grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkLabel(f2, text="Target File Size (MB):", font=get_font(12, "bold")).pack(anchor="w")
        self.target_size_entry = ctk.CTkEntry(f2, font=get_font(12), height=28)
        self.target_size_entry.insert(0, "24.5")
        self.target_size_entry.pack(fill="x", pady=2)

        # Codec
        f3 = ctk.CTkFrame(row1, fg_color="transparent")
        f3.grid(row=0, column=2, sticky="ew", padx=4)
        ctk.CTkLabel(f3, text="Target Codec:", font=get_font(12, "bold")).pack(anchor="w")
        self.target_codec = ctk.CTkComboBox(
            f3,
            values=["H.264 / MP4 (Universal)", "H.265 / HEVC (High Quality)", "AV1 (Maximum Quality/Size)"],
            font=get_font(11)
        )
        self.target_codec.set("H.264 / MP4 (Universal)")
        self.target_codec.pack(fill="x", pady=2)

        row2 = ctk.CTkFrame(tab, fg_color="transparent")
        row2.pack(fill="x", pady=4)
        row2.columnconfigure((0, 1), weight=1)

        # Audio Budget
        c1 = ctk.CTkFrame(row2, fg_color="transparent")
        c1.grid(row=0, column=0, sticky="ew", padx=4)
        ctk.CTkLabel(c1, text="Audio Quality / Budget:", font=get_font(12, "bold")).pack(anchor="w")
        self.target_audio_budget = ctk.CTkComboBox(
            c1,
            values=["Auto-Balance (Recommended)", "128 kbps (Music / Rich)", "96 kbps (Standard)", "64 kbps (Compact Voice)", "Mute (Video Only)"],
            font=get_font(11)
        )
        self.target_audio_budget.set("Auto-Balance (Recommended)")
        self.target_audio_budget.pack(fill="x", pady=2)

        # Options Checkboxes
        c2 = ctk.CTkFrame(row2, fg_color="transparent")
        c2.grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkLabel(c2, text="Smart Optimizations:", font=get_font(12, "bold")).pack(anchor="w")

        c2_inner = ctk.CTkFrame(c2, fg_color="transparent")
        c2_inner.pack(fill="x", pady=2)

        self.target_autores = ctk.CTkCheckBox(c2_inner, text="Smart Auto-Downscale (Preserves clarity on small sizes)", font=get_font(11))
        self.target_autores.select()
        self.target_autores.pack(anchor="w")

    def _on_target_preset_changed(self, choice):
        if "25 MB" in choice:
            self.target_size_entry.delete(0, "end")
            self.target_size_entry.insert(0, "24.5")
        elif "50 MB" in choice:
            self.target_size_entry.delete(0, "end")
            self.target_size_entry.insert(0, "49.0")
        elif "100 MB" in choice:
            self.target_size_entry.delete(0, "end")
            self.target_size_entry.insert(0, "98.0")
        elif "16 MB" in choice:
            self.target_size_entry.delete(0, "end")
            self.target_size_entry.insert(0, "15.5")
        elif "64 MB" in choice:
            self.target_size_entry.delete(0, "end")
            self.target_size_entry.insert(0, "62.0")
        elif "10 MB" in choice:
            self.target_size_entry.delete(0, "end")
            self.target_size_entry.insert(0, "9.5")

    # -------------------------------------------------------------------------
    # TAB 1: GIF / WebP
    # -------------------------------------------------------------------------
    def _build_gif_tab(self, tab):
        self.gif_picker = FilePicker(tab, label_text="Input Video File:", placeholder="Select video to convert to animated GIF or WebP...")
        self.gif_picker.pack(fill="x", pady=(0, 10))

        row1 = ctk.CTkFrame(tab, fg_color="transparent")
        row1.pack(fill="x", pady=4)
        row1.columnconfigure((0, 1, 2), weight=1)

        # Format
        f1 = ctk.CTkFrame(row1, fg_color="transparent")
        f1.grid(row=0, column=0, sticky="ew", padx=4)
        ctk.CTkLabel(f1, text="Format:", font=get_font(12, "bold")).pack(anchor="w")
        self.gif_format = ctk.CTkSegmentedButton(f1, values=["GIF", "Animated WebP", "Both"], font=get_font(12))
        self.gif_format.set("GIF")
        self.gif_format.pack(fill="x", pady=2)

        # Width
        f2 = ctk.CTkFrame(row1, fg_color="transparent")
        f2.grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkLabel(f2, text="Width (Aspect Preserved):", font=get_font(12, "bold")).pack(anchor="w")
        self.gif_width = ctk.CTkComboBox(f2, values=["480px (Standard)", "720px (HD)", "360px (Compact)", "Original"], font=get_font(12))
        self.gif_width.set("480px (Standard)")
        self.gif_width.pack(fill="x", pady=2)

        # FPS
        f3 = ctk.CTkFrame(row1, fg_color="transparent")
        f3.grid(row=0, column=2, sticky="ew", padx=4)
        ctk.CTkLabel(f3, text="Framerate:", font=get_font(12, "bold")).pack(anchor="w")
        self.gif_fps = ctk.CTkComboBox(f3, values=["15 FPS (Balanced)", "24 FPS (Smooth)", "30 FPS (Fluid)", "10 FPS (Compact)"], font=get_font(12))
        self.gif_fps.set("15 FPS (Balanced)")
        self.gif_fps.pack(fill="x", pady=2)

        # Time range
        row2 = ctk.CTkFrame(tab, fg_color="transparent")
        row2.pack(fill="x", pady=6)
        row2.columnconfigure((0, 1), weight=1)

        c1 = ctk.CTkFrame(row2, fg_color="transparent")
        c1.grid(row=0, column=0, sticky="ew", padx=4)
        ctk.CTkLabel(c1, text="Start Time (e.g. 00:00:05 or 10):", font=get_font(11)).pack(anchor="w")
        self.gif_start = ctk.CTkEntry(c1, placeholder_text="00:00:00 (Start of video)", height=32)
        self.gif_start.pack(fill="x")

        c2 = ctk.CTkFrame(row2, fg_color="transparent")
        c2.grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkLabel(c2, text="Duration in seconds (e.g. 5, 10):", font=get_font(11)).pack(anchor="w")
        self.gif_dur = ctk.CTkEntry(c2, placeholder_text="Full video or 5", height=32)
        self.gif_dur.pack(fill="x")

    # -------------------------------------------------------------------------
    # TAB 2: Cut / Trim
    # -------------------------------------------------------------------------
    def _build_cut_tab(self, tab):
        self.cut_picker = FilePicker(tab, label_text="Input Video File:", placeholder="Select video to trim/cut...")
        self.cut_picker.pack(fill="x", pady=(0, 10))

        row1 = ctk.CTkFrame(tab, fg_color="transparent")
        row1.pack(fill="x", pady=4)
        row1.columnconfigure((0, 1, 2), weight=1)

        c1 = ctk.CTkFrame(row1, fg_color="transparent")
        c1.grid(row=0, column=0, sticky="ew", padx=4)
        ctk.CTkLabel(c1, text="Start Timestamp (HH:MM:SS or SS):", font=get_font(11, "bold")).pack(anchor="w")
        self.cut_start = ctk.CTkEntry(c1, placeholder_text="00:00:00", height=32)
        self.cut_start.pack(fill="x")

        c2 = ctk.CTkFrame(row1, fg_color="transparent")
        c2.grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkLabel(c2, text="End Timestamp / Duration:", font=get_font(11, "bold")).pack(anchor="w")
        self.cut_end = ctk.CTkEntry(c2, placeholder_text="00:01:30 or +45s", height=32)
        self.cut_end.pack(fill="x")

        c3 = ctk.CTkFrame(row1, fg_color="transparent")
        c3.grid(row=0, column=2, sticky="ew", padx=4)
        ctk.CTkLabel(c3, text="Cut Mode:", font=get_font(11, "bold")).pack(anchor="w")
        self.cut_mode = ctk.CTkSegmentedButton(c3, values=["Lossless (Fast)", "Accurate (Re-encode)"], font=get_font(11))
        self.cut_mode.set("Lossless (Fast)")
        self.cut_mode.pack(fill="x", pady=2)

    # -------------------------------------------------------------------------
    # TAB 3: Join Videos
    # -------------------------------------------------------------------------
    def _build_join_tab(self, tab):
        self.join_picker = FilePicker(tab, label_text="Select Multiple Videos to Concatenate:", placeholder="Select video files...", allow_multiple=True)
        self.join_picker.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(tab, text="Joining Mode:", font=get_font(12, "bold")).pack(anchor="w", pady=(4, 2))
        self.join_mode = ctk.CTkSegmentedButton(
            tab,
            values=["Lossless Stream Copy (Same Codec/Res)", "Re-encode & Unify Formats"],
            font=get_font(12)
        )
        self.join_mode.set("Lossless Stream Copy (Same Codec/Res)")
        self.join_mode.pack(fill="x", pady=(0, 6))

    # -------------------------------------------------------------------------
    # TAB 4: Snapshots & Grid
    # -------------------------------------------------------------------------
    def _build_snap_tab(self, tab):
        self.snap_picker = FilePicker(tab, label_text="Input Video File:", placeholder="Select video to generate contact sheet or stills...")
        self.snap_picker.pack(fill="x", pady=(0, 10))

        row1 = ctk.CTkFrame(tab, fg_color="transparent")
        row1.pack(fill="x", pady=4)
        row1.columnconfigure((0, 1), weight=1)

        f1 = ctk.CTkFrame(row1, fg_color="transparent")
        f1.grid(row=0, column=0, sticky="ew", padx=4)
        ctk.CTkLabel(f1, text="Snapshot Mode:", font=get_font(12, "bold")).pack(anchor="w")
        self.snap_mode = ctk.CTkSegmentedButton(
            f1,
            values=["Contact Sheet / Grid", "Interval Extraction", "Single Still"],
            font=get_font(11)
        )
        self.snap_mode.set("Contact Sheet / Grid")
        self.snap_mode.pack(fill="x", pady=2)

        f2 = ctk.CTkFrame(row1, fg_color="transparent")
        f2.grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkLabel(f2, text="Grid Layout / Interval:", font=get_font(12, "bold")).pack(anchor="w")
        self.snap_grid = ctk.CTkComboBox(f2, values=["4x4 Grid (16 Tiles)", "3x3 Grid (9 Tiles)", "Every 5 Seconds", "Every 10 Seconds", "Single Timestamp (00:01:00)"], font=get_font(12))
        self.snap_grid.set("4x4 Grid (16 Tiles)")
        self.snap_grid.pack(fill="x", pady=2)

    # -------------------------------------------------------------------------
    # TAB 5: Extract Audio
    # -------------------------------------------------------------------------
    def _build_audio_tab(self, tab):
        self.audio_picker = FilePicker(tab, label_text="Input Video or Audio File:", placeholder="Select video to extract audio track...")
        self.audio_picker.pack(fill="x", pady=(0, 10))

        row1 = ctk.CTkFrame(tab, fg_color="transparent")
        row1.pack(fill="x", pady=4)
        row1.columnconfigure((0, 1), weight=1)

        f1 = ctk.CTkFrame(row1, fg_color="transparent")
        f1.grid(row=0, column=0, sticky="ew", padx=4)
        ctk.CTkLabel(f1, text="Audio Target Format:", font=get_font(12, "bold")).pack(anchor="w")
        self.audio_fmt = ctk.CTkSegmentedButton(
            f1,
            values=["MP3 (320 kbps)", "M4A / AAC", "FLAC (Lossless)", "WAV (Uncompressed)", "Original Track"],
            font=get_font(11)
        )
        self.audio_fmt.set("MP3 (320 kbps)")
        self.audio_fmt.pack(fill="x", pady=2)

        f2 = ctk.CTkFrame(row1, fg_color="transparent")
        f2.grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkLabel(f2, text="Bitrate / Quality:", font=get_font(12, "bold")).pack(anchor="w")
        self.audio_quality = ctk.CTkComboBox(f2, values=["320 kbps (High Fidelity)", "256 kbps", "192 kbps", "128 kbps"], font=get_font(12))
        self.audio_quality.set("320 kbps (High Fidelity)")
        self.audio_quality.pack(fill="x", pady=2)

    # -------------------------------------------------------------------------
    # Execution Dispatcher
    # -------------------------------------------------------------------------
    def on_start_clicked(self):
        active_tab = self.tabview.get()
        ffmpeg = get_ffmpeg_path()

        if "Target" in active_tab:
            self._run_target(ffmpeg)
        elif "GIF" in active_tab:
            self._run_gif(ffmpeg)
        elif "Cut" in active_tab:
            self._run_cut(ffmpeg)
        elif "Join" in active_tab:
            self._run_join(ffmpeg)
        elif "Snapshots" in active_tab:
            self._run_snap(ffmpeg)
        elif "Audio" in active_tab:
            self._run_audio(ffmpeg)

    def _get_video_duration(self, filepath):
        ffprobe = get_ffprobe_path()
        try:
            cmd = [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filepath]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            if res.returncode == 0 and res.stdout.strip():
                return float(res.stdout.strip())
        except Exception:
            pass
        return 0.0

    def _run_target(self, ffmpeg):
        inp = self.target_picker.get_path()
        if not inp or not os.path.exists(inp):
            self.terminal.clear()
            self.terminal.append_log("⚠️ Error: Please select a valid video file to compress.\n")
            return

        try:
            target_mb = float(self.target_size_entry.get().strip())
        except ValueError:
            self.terminal.clear()
            self.terminal.append_log("⚠️ Error: Target size must be a valid number in MB (e.g. 24.5 or 50).\n")
            return

        duration = self._get_video_duration(inp)
        if duration <= 0:
            self.terminal.clear()
            self.terminal.append_log("⚠️ Warning: Could not detect video duration via ffprobe. Defaulting to 60s baseline.\n")
            duration = 60.0

        # Target total kilobits with 5% safety margin for MP4 container / moov atom
        target_total_kbits = (target_mb * 8192) * 0.95
        total_bitrate_kbps = target_total_kbits / duration

        # Audio allocation
        audio_choice = self.target_audio_budget.get()
        if "Mute" in audio_choice:
            audio_kbps = 0
        elif "128" in audio_choice:
            audio_kbps = 128
        elif "96" in audio_choice:
            audio_kbps = 96
        elif "64" in audio_choice:
            audio_kbps = 64
        else: # Auto-Balance
            if total_bitrate_kbps > 2000:
                audio_kbps = 128
            elif total_bitrate_kbps > 800:
                audio_kbps = 96
            elif total_bitrate_kbps > 300:
                audio_kbps = 64
            else:
                audio_kbps = 48

        video_kbps = max(40, int(total_bitrate_kbps - audio_kbps))
        
        # Codec selection
        codec_choice = self.target_codec.get()
        if "AV1" in codec_choice:
            vcodec = "libsvtav1"
            preset_arg = ["-preset", "6"]
        elif "HEVC" in codec_choice or "H.265" in codec_choice:
            vcodec = "libx265"
            preset_arg = ["-preset", "fast"]
        else:
            vcodec = "libx264"
            preset_arg = ["-preset", "medium"]

        # Smart Auto-Downscale if video bitrate is tight
        vf_args = []
        if self.target_autores.get():
            if video_kbps < 350:
                vf_args = ["-vf", "scale=-2:480"]
            elif video_kbps < 850:
                vf_args = ["-vf", "scale=-2:720"]

        base, ext = os.path.splitext(inp)
        out_file = f"{base}_target_{int(target_mb)}MB.mp4"

        cmd = [ffmpeg, "-hide_banner", "-y", "-i", inp]
        if vf_args:
            cmd.extend(vf_args)

        cmd.extend([
            "-c:v", vcodec,
            "-b:v", f"{video_kbps}k",
            "-maxrate", f"{int(video_kbps * 1.35)}k",
            "-bufsize", f"{int(video_kbps * 2)}k",
        ] + preset_arg)

        if audio_kbps == 0:
            cmd.append("-an")
        else:
            cmd.extend(["-c:a", "aac", "-b:a", f"{audio_kbps}k"])

        cmd.extend(["-movflags", "+faststart", out_file])

        self.terminal.clear()
        self.terminal.append_log(f"🎯 Target File Size: {target_mb:.1f} MB (Duration: {duration:.1f}s)\n")
        self.terminal.append_log(f"📊 Allocated Bitrates: Video {video_kbps} kbps | Audio {audio_kbps} kbps\n")
        self.terminal.append_log(f"🚀 Starting Compression -> {out_file}\n\n")

        self.execute_command(cmd)

    def _run_gif(self, ffmpeg):
        inp = self.gif_picker.get_path()
        if not inp or not os.path.exists(inp):
            self.terminal.clear()
            self.terminal.append_log("⚠️ Error: Please select a valid video file first.\n")
            return

        base, _ = os.path.splitext(inp)
        fmt = self.gif_format.get()
        width_str = self.gif_width.get()
        fps_str = self.gif_fps.get()

        fps_val = "15"
        if "24" in fps_str: fps_val = "24"
        elif "30" in fps_str: fps_val = "30"
        elif "10" in fps_str: fps_val = "10"

        scale_filter = ""
        if "480" in width_str: scale_filter = "scale=480:-1:flags=lanczos"
        elif "720" in width_str: scale_filter = "scale=720:-1:flags=lanczos"
        elif "360" in width_str: scale_filter = "scale=360:-1:flags=lanczos"

        filter_base = f"fps={fps_val}"
        if scale_filter:
            filter_base += f",{scale_filter}"

        start = self.gif_start.get().strip()
        dur = self.gif_dur.get().strip()
        time_args = []
        if start and start != "00:00:00":
            time_args.extend(["-ss", start])
        if dur:
            time_args.extend(["-t", dur])

        out_gif = f"{base}.gif"
        gif_filter = f"{filter_base},split[s0][s1];[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5"

        cmd = [ffmpeg, "-hide_banner", "-v", "error", "-stats"] + time_args + ["-i", inp, "-filter_complex", gif_filter, "-loop", "0", "-y", out_gif]
        self.execute_command(cmd)

    def _run_cut(self, ffmpeg):
        inp = self.cut_picker.get_path()
        if not inp or not os.path.exists(inp):
            self.terminal.clear()
            self.terminal.append_log("⚠️ Error: Please select a valid video file to trim.\n")
            return

        base, ext = os.path.splitext(inp)
        start = self.cut_start.get().strip() or "00:00:00"
        end = self.cut_end.get().strip()
        mode = self.cut_mode.get()

        out_file = f"{base}_cut{ext}"
        if "Lossless" in mode:
            cmd = [ffmpeg, "-hide_banner", "-ss", start]
            if end:
                cmd.extend(["-to", end] if ":" in end else ["-t", end.replace("+", "").replace("s", "")])
            cmd.extend(["-i", inp, "-c", "copy", "-avoid_negative_ts", "make_zero", "-y", out_file])
        else:
            cmd = [ffmpeg, "-hide_banner", "-ss", start]
            if end:
                cmd.extend(["-to", end] if ":" in end else ["-t", end.replace("+", "").replace("s", "")])
            cmd.extend(["-i", inp, "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-c:a", "aac", "-b:a", "192k", "-y", out_file])

        self.execute_command(cmd)

    def _run_join(self, ffmpeg):
        inp = self.join_picker.get_path()
        if not inp:
            self.terminal.clear()
            self.terminal.append_log("⚠️ Error: Please select multiple video files to join.\n")
            return

        files = [p.strip().strip('"') for p in inp.split(";") if p.strip()]
        if len(files) < 2:
            self.terminal.clear()
            self.terminal.append_log("⚠️ Error: At least 2 video files are required to join.\n")
            return

        base_dir = os.path.dirname(files[0])
        list_file = os.path.join(base_dir, "join_list.txt")
        with open(list_file, "w", encoding="utf-8") as f:
            for filepath in files:
                f.write(f"file '{filepath}'\n")

        _, ext = os.path.splitext(files[0])
        out_file = os.path.join(base_dir, f"joined_video{ext}")
        cmd = [ffmpeg, "-hide_banner", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", "-y", out_file]
        self.execute_command(cmd)

    def _run_snap(self, ffmpeg):
        inp = self.snap_picker.get_path()
        if not inp or not os.path.exists(inp):
            self.terminal.clear()
            self.terminal.append_log("⚠️ Error: Please select a valid video file.\n")
            return

        base, _ = os.path.splitext(inp)
        out_img = f"{base}_contact_sheet.jpg"
        cmd = [ffmpeg, "-hide_banner", "-i", inp, "-vf", "fps=1/10,scale=320:-1,tile=4x4", "-frames:v", "1", "-q:v", "2", "-y", out_img]
        self.execute_command(cmd)

    def _run_audio(self, ffmpeg):
        inp = self.audio_picker.get_path()
        if not inp or not os.path.exists(inp):
            self.terminal.clear()
            self.terminal.append_log("⚠️ Error: Please select a valid video file.\n")
            return

        base, _ = os.path.splitext(inp)
        fmt_choice = self.audio_fmt.get()

        if "MP3" in fmt_choice:
            out_file = f"{base}.mp3"
            cmd = [ffmpeg, "-hide_banner", "-i", inp, "-vn", "-c:a", "libmp3lame", "-q:a", "0", "-y", out_file]
        elif "M4A" in fmt_choice:
            out_file = f"{base}.m4a"
            cmd = [ffmpeg, "-hide_banner", "-i", inp, "-vn", "-c:a", "aac", "-b:a", "256k", "-y", out_file]
        elif "FLAC" in fmt_choice:
            out_file = f"{base}.flac"
            cmd = [ffmpeg, "-hide_banner", "-i", inp, "-vn", "-c:a", "flac", "-y", out_file]
        elif "WAV" in fmt_choice:
            out_file = f"{base}.wav"
            cmd = [ffmpeg, "-hide_banner", "-i", inp, "-vn", "-c:a", "pcm_s16le", "-y", out_file]
        else:
            out_file = f"{base}_extracted.aac"
            cmd = [ffmpeg, "-hide_banner", "-i", inp, "-vn", "-c:a", "copy", "-y", out_file]

        self.execute_command(cmd)
