"""
Video Compressor View - Graphical frontend for video_compressor.py.
"""
import os
import sys
import customtkinter as ctk
from ui.theme import COLORS, get_font
from ui.views.base_view import BaseToolView
from ui.components.file_picker import FilePicker

class CompressorView(BaseToolView):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            title="🎬 AV1 / HEVC Smart Video Compressor",
            description="High-efficiency video compression powered by SVT-AV1, x265, and NVIDIA NVENC GPU acceleration.",
            **kwargs
        )

    def build_options(self, container: ctk.CTkFrame):
        # 1. File / Folder Picker
        self.file_picker = FilePicker(
            container,
            label_text="Select Video File or Folder:",
            placeholder="Select a video file or folder to batch compress...",
            file_types=[("Video files", "*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.ts"), ("All files", "*.*")],
            allow_folder=True
        )
        self.file_picker.pack(fill="x", pady=(0, 14))

        # 2. Settings Grid (2 Columns)
        self.grid_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.grid_frame.pack(fill="x", pady=(0, 10))
        self.grid_frame.columnconfigure((0, 1), weight=1)

        # Left Column: Codec & Quality Profile
        self.left_col = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Codec selector
        ctk.CTkLabel(self.left_col, text="Target Video Codec:", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 4))
        self.codec_segment = ctk.CTkSegmentedButton(
            self.left_col,
            values=["AV1 (Best Efficiency)", "HEVC / H.265", "H.264 (Universal)"],
            font=get_font(12),
            selected_color=COLORS["accent_primary"]
        )
        self.codec_segment.set("AV1 (Best Efficiency)")
        self.codec_segment.pack(fill="x", pady=(0, 12))

        # Quality Preset
        ctk.CTkLabel(self.left_col, text="Quality Profile:", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 4))
        self.preset_segment = ctk.CTkSegmentedButton(
            self.left_col,
            values=["Archival (CRF 22)", "High (CRF 26)", "Balanced (CRF 28)", "Compact (CRF 32)"],
            font=get_font(11),
            selected_color=COLORS["accent_primary"]
        )
        self.preset_segment.set("Balanced (CRF 28)")
        self.preset_segment.pack(fill="x", pady=(0, 12))

        # Target Size in MB (optional)
        ctk.CTkLabel(self.left_col, text="Or Target File Size (MB) [Optional]:", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 4))
        self.target_mb_entry = ctk.CTkEntry(
            self.left_col,
            placeholder_text="e.g. 25, 50, 100 (Overrides preset if filled)",
            font=get_font(12),
            height=32
        )
        self.target_mb_entry.pack(fill="x")

        # Right Column: Hardware GPU, Audio, Resolution
        self.right_col = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # GPU Acceleration Checkbox
        self.gpu_check = ctk.CTkCheckBox(
            self.right_col,
            text="Enable NVIDIA NVENC Hardware Acceleration (GPU)",
            font=get_font(12, "bold"),
            checkmark_color=COLORS["accent_success"]
        )
        self.gpu_check.select()
        self.gpu_check.pack(anchor="w", pady=(0, 12))

        # Audio handling dropdown
        ctk.CTkLabel(self.right_col, text="Audio Track Processing:", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 4))
        self.audio_combo = ctk.CTkComboBox(
            self.right_col,
            values=["Copy (Lossless Passthrough)", "Compress to OPUS (Ultra Efficient ~96k)", "Compress to AAC (Compatible ~128k)"],
            font=get_font(12),
            height=32
        )
        self.audio_combo.set("Copy (Lossless Passthrough)")
        self.audio_combo.pack(fill="x", pady=(0, 12))

        # Resolution Downscaling
        ctk.CTkLabel(self.right_col, text="Resolution Downscaling:", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 4))
        self.scale_combo = ctk.CTkComboBox(
            self.right_col,
            values=["Original Resolution (No Scaling)", "1080p (1920x1080)", "720p (1280x720)", "480p (854x480)"],
            font=get_font(12),
            height=32
        )
        self.scale_combo.set("Original Resolution (No Scaling)")
        self.scale_combo.pack(fill="x")

        # Benchmark button beside run button
        self.test_btn = ctk.CTkButton(
            self.action_bar,
            text="🧪 Run VMAF / CRF Sample Test",
            font=get_font(13),
            height=38,
            fg_color=COLORS["accent_purple"],
            hover_color="#7C3AED",
            command=self.on_benchmark_clicked
        )
        self.test_btn.pack(side="left", padx=10)

    def _build_command(self, is_benchmark=False):
        raw_path = self.file_picker.get_path()
        if not raw_path:
            self.terminal.clear()
            self.terminal.append_log("⚠️ Error: Please select an input video file or directory first.\n")
            return None

        # Codec map
        codec_val = self.codec_segment.get()
        codec = "av1"
        if "HEVC" in codec_val:
            codec = "hevc"
        elif "H.264" in codec_val:
            codec = "h264"

        # Preset map
        preset_val = self.preset_segment.get()
        preset = "balanced"
        if "Archival" in preset_val:
            preset = "archival"
        elif "High" in preset_val:
            preset = "high"
        elif "Compact" in preset_val:
            preset = "compact"

        # Audio map
        audio_val = self.audio_combo.get()
        audio = "copy"
        if "OPUS" in audio_val:
            audio = "opus"
        elif "AAC" in audio_val:
            audio = "aac"

        # Scale map
        scale_val = self.scale_combo.get()
        scale = None
        if "1080p" in scale_val:
            scale = "1080"
        elif "720p" in scale_val:
            scale = "720"
        elif "480p" in scale_val:
            scale = "480"

        # GPU
        use_gpu = bool(self.gpu_check.get())

        # Target MB
        target_mb = self.target_mb_entry.get().strip()

        # Build python invocation
        cmd = [sys.executable, "video_compressor.py", raw_path, "-c", codec, "-p", preset, "--audio", audio]

        if use_gpu:
            cmd.append("--gpu")

        if scale:
            cmd.extend(["--scale", scale])

        if target_mb:
            try:
                val = float(target_mb)
                cmd.extend(["--target-mb", str(val)])
            except ValueError:
                pass

        if is_benchmark:
            cmd.append("--sample-test")

        if os.path.isdir(raw_path):
            cmd.append("--batch")

        return cmd

    def on_start_clicked(self):
        cmd = self._build_command(is_benchmark=False)
        if cmd:
            self.execute_command(cmd, cwd=os.path.dirname(os.path.abspath(__file__ + "/../..")))

    def on_benchmark_clicked(self):
        cmd = self._build_command(is_benchmark=True)
        if cmd:
            self.execute_command(cmd, cwd=os.path.dirname(os.path.abspath(__file__ + "/../..")))
