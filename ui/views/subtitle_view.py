"""
Subtitle Generator View - Graphical frontend for subtitle_generator.py.
"""
import os
import sys
import customtkinter as ctk
from ui.theme import COLORS, get_font
from ui.views.base_view import BaseToolView
from ui.components.file_picker import FilePicker

LANGUAGE_OPTIONS = [
    ("auto", "🌐 Auto-detect Language"),
    ("en", "English"),
    ("pt", "Portuguese"),
    ("es", "Spanish"),
    ("fr", "French"),
    ("de", "German"),
    ("it", "Italian"),
    ("ja", "Japanese"),
    ("zh", "Chinese"),
    ("ko", "Korean"),
    ("ru", "Russian"),
    ("nl", "Dutch"),
    ("pl", "Polish"),
    ("tr", "Turkish"),
    ("ar", "Arabic"),
    ("hi", "Hindi"),
]

class SubtitleView(BaseToolView):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            title="📝 faster-whisper GPU Subtitle Generator",
            description="Automatic speech recognition, subtitle (.SRT) generation, and multi-language translation powered by faster-whisper & CTranslate2.",
            **kwargs
        )

    def build_options(self, container: ctk.CTkFrame):
        # 1. File / Folder Picker
        self.file_picker = FilePicker(
            container,
            label_text="Select Video/Audio File or Folder:",
            placeholder="Select video(s) or folder to generate subtitles...",
            file_types=[("Media files", "*.mp4 *.mkv *.avi *.mov *.webm *.mp3 *.m4a *.wav *.flac"), ("All files", "*.*")],
            allow_folder=True,
            allow_multiple=True
        )
        self.file_picker.pack(fill="x", pady=(0, 14))

        # 2. Grid options
        grid = ctk.CTkFrame(container, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 10))
        grid.columnconfigure((0, 1), weight=1)

        # Left Column: Whisper Model & Track
        left = ctk.CTkFrame(grid, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(left, text="Whisper AI Model:", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 4))
        self.model_segment = ctk.CTkSegmentedButton(
            left,
            values=["tiny", "base", "small", "medium", "large-v3"],
            font=get_font(12)
        )
        self.model_segment.set("base")
        self.model_segment.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(left, text="Audio Track Index:", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 4))
        self.track_combo = ctk.CTkComboBox(
            left,
            values=["Track 0 (Default / Primary)", "Track 1 (Second Audio Track)", "Track 2", "Track 3"],
            font=get_font(12),
            height=32
        )
        self.track_combo.set("Track 0 (Default / Primary)")
        self.track_combo.pack(fill="x")

        # Right Column: Source & Target Language
        right = ctk.CTkFrame(grid, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        lang_display_names = [name for _, name in LANGUAGE_OPTIONS]

        ctk.CTkLabel(right, text="Spoken Audio Language (Source):", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 4))
        self.source_lang_combo = ctk.CTkComboBox(
            right,
            values=lang_display_names,
            font=get_font(12),
            height=32
        )
        self.source_lang_combo.set("🌐 Auto-detect Language")
        self.source_lang_combo.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(right, text="Subtitle Output Language (Target):", font=get_font(12, "bold")).pack(anchor="w", pady=(0, 4))
        self.target_lang_combo = ctk.CTkComboBox(
            right,
            values=["Original Spoken Language (No translation)"] + [name for code, name in LANGUAGE_OPTIONS if code != "auto"],
            font=get_font(12),
            height=32
        )
        self.target_lang_combo.set("Original Spoken Language (No translation)")
        self.target_lang_combo.pack(fill="x")

    def _get_lang_code(self, display_text: str) -> str:
        for code, name in LANGUAGE_OPTIONS:
            if name == display_text:
                return code
        return "auto"

    def on_start_clicked(self):
        raw_path = self.file_picker.get_path()
        if not raw_path:
            self.terminal.clear()
            self.terminal.append_log("⚠️ Error: Please select an input media file or folder first.\n")
            return

        model = self.model_segment.get()
        source_lang = self._get_lang_code(self.source_lang_combo.get())

        target_display = self.target_lang_combo.get()
        target_lang = "auto"
        if "Original" not in target_display:
            target_lang = self._get_lang_code(target_display)

        track_str = self.track_combo.get()
        track_num = "0"
        if "Track 1" in track_str: track_num = "1"
        elif "Track 2" in track_str: track_num = "2"
        elif "Track 3" in track_str: track_num = "3"

        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__ + "/../..")), "subtitle_generator.py")
        cmd = [
            sys.executable,
            script_path,
            raw_path,
            "--model", model,
            "--source-lang", source_lang,
            "--target-lang", target_lang,
            "--track", track_num
        ]

        self.execute_command(cmd, cwd=os.path.dirname(script_path))
