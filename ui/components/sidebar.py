"""
Sidebar navigation menu component with category buttons and theme toggle.
"""
import customtkinter as ctk
from ui.theme import COLORS, get_font

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate, **kwargs):
        super().__init__(
            master,
            width=220,
            fg_color=COLORS["bg_sidebar"],
            corner_radius=0,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs
        )
        self.on_navigate = on_navigate
        self.buttons = {}
        self.active_tab = None

        self._build_ui()

    def _build_ui(self):
        # App Branding Header
        self.brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.brand_frame.pack(fill="x", padx=16, pady=(20, 16))

        self.brand_title = ctk.CTkLabel(
            self.brand_frame,
            text="⚡ Power Tools",
            font=get_font(18, "bold"),
            text_color=COLORS["text_primary"]
        )
        self.brand_title.pack(anchor="w")

        self.brand_subtitle = ctk.CTkLabel(
            self.brand_frame,
            text="media and other automation v1.0",
            font=get_font(10),
            text_color=COLORS["text_muted"],
            wraplength=180,
            justify="left"
        )
        self.brand_subtitle.pack(anchor="w", pady=(2, 0))

        # Nav Items
        self.nav_items = [
            ("downloaders", "🌐 Video Downloader", "yt-dlp, Playlists, M3U8/DASH"),
            ("live_stream", "📡 Live Stream Recorder", "Twitch, Kick, Live Auto-Monitor"),
            ("audio_downloader", "🎵 Music & Audio Downloader", "MP3 320k, FLAC, Chapters & Metadata"),
            ("file_downloader", "🚀 General File Downloader", "aria2c 16-Connection Accelerator"),
            ("compressor", "🎬 Video Compressor", "AV1/HEVC Smart Compression"),
            ("media_tools", "✂️ Media Utilities", "Target Size, GIF, Cut, Join, Audio"),
            ("subtitles", "📝 Subtitle Generator", "faster-whisper GPU Transcribe"),
            ("system", "🛠️ System & Updaters", "One-Click Updates, Docker, Display"),
        ]

        self.nav_container = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_container.pack(fill="both", expand=True, padx=10, pady=10)

        for key, title, desc in self.nav_items:
            btn = ctk.CTkButton(
                self.nav_container,
                text=f"  {title}",
                font=get_font(13, "bold"),
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["bg_card"],
                command=lambda k=key: self._on_btn_click(k)
            )
            btn.pack(fill="x", pady=4)
            self.buttons[key] = btn

        # Bottom section: Theme toggle
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="x", padx=14, pady=16)

        self.theme_switch = ctk.CTkSwitch(
            self.bottom_frame,
            text="Dark Theme",
            font=get_font(11),
            command=self._toggle_theme,
            width=36,
            height=18
        )
        self.theme_switch.select()
        self.theme_switch.pack(anchor="w")

    def _on_btn_click(self, tab_key: str):
        self.set_active(tab_key)
        if self.on_navigate:
            self.on_navigate(tab_key)

    def set_active(self, tab_key: str):
        self.active_tab = tab_key
        for key, btn in self.buttons.items():
            if key == tab_key:
                btn.configure(
                    fg_color=COLORS["accent_primary"],
                    text_color="#FFFFFF"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"]
                )

    def _toggle_theme(self):
        if self.theme_switch.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
