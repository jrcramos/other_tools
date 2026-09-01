"""
Modern Splash Screen for Power Tools.
Displays a centered glowing splash screen with progress animation on startup.
"""
import os
import sys
import customtkinter as ctk
from PIL import Image
from ui.theme import COLORS, get_font

ROOT_DIR = os.path.dirname(os.path.abspath(__file__ + "/.."))
ICON_PATH = os.path.join(ROOT_DIR, "assets", "icon.png")

class SplashScreen(ctk.CTkToplevel):
    def __init__(self, parent, on_complete, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_complete = on_complete

        # Window styling
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color=COLORS["bg_dark"])

        # Center on screen
        w, h = 460, 260
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui()
        self._animate_progress(0)

    def _build_ui(self):
        # Container with subtle blue border
        self.container = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_sidebar"],
            corner_radius=12,
            border_width=2,
            border_color=COLORS["accent_primary"]
        )
        self.container.pack(fill="both", expand=True, padx=2, pady=2)

        # Header area
        self.center_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.center_frame.pack(expand=True, pady=(20, 10))

        # Icon image
        if os.path.exists(ICON_PATH):
            try:
                pil_img = Image.open(ICON_PATH).resize((64, 64), Image.Resampling.LANCZOS)
                self.icon_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(64, 64))
                self.icon_lbl = ctk.CTkLabel(self.center_frame, image=self.icon_img, text="")
                self.icon_lbl.pack(pady=(0, 8))
            except Exception:
                pass

        # Title
        self.title_lbl = ctk.CTkLabel(
            self.center_frame,
            text="⚡ Power Tools",
            font=get_font(20, "bold"),
            text_color=COLORS["text_primary"]
        )
        self.title_lbl.pack()

        # Subtitle
        self.sub_lbl = ctk.CTkLabel(
            self.center_frame,
            text="media and other automation v1.0",
            font=get_font(12),
            text_color=COLORS["text_muted"]
        )
        self.sub_lbl.pack(pady=(2, 0))

        # Progress bar
        self.progress = ctk.CTkProgressBar(
            self.container,
            width=360,
            height=6,
            progress_color=COLORS["accent_primary"],
            fg_color=COLORS["bg_terminal"]
        )
        self.progress.pack(pady=(0, 8))
        self.progress.set(0)

        # Status text
        self.status_lbl = ctk.CTkLabel(
            self.container,
            text="Initializing modules & binary engines...",
            font=get_font(10),
            text_color=COLORS["text_muted"]
        )
        self.status_lbl.pack(pady=(0, 16))

    def _animate_progress(self, val: float):
        if val < 1.0:
            self.progress.set(val)
            next_val = val + 0.08
            self.after(35, lambda: self._animate_progress(next_val))
        else:
            self.progress.set(1.0)
            self.after(150, self._finish)

    def _finish(self):
        self.destroy()
        if self.on_complete:
            self.on_complete()
