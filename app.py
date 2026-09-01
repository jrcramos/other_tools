"""
Main Application Entry Point for Power Tools — Media and other tools for optimizations v1.
"""
import sys
import os
import customtkinter as ctk

# Ensure workspace root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ui.theme import COLORS
from ui.components.sidebar import Sidebar
from ui.components.status_bar import StatusBar
from ui.splash import SplashScreen
from ui.views.compressor_view import CompressorView
from ui.views.media_tools_view import MediaToolsView
from ui.views.subtitle_view import SubtitleView
from ui.views.downloader_view import DownloaderView
from ui.views.live_stream_view import LiveStreamView
from ui.views.audio_downloader_view import AudioDownloaderView
from ui.views.file_downloader_view import FileDownloaderView
from ui.views.system_tools_view import SystemToolsView

class PowerToolsApp(ctk.CTk):
    def __init__(self, show_splash=True):
        super().__init__()

        # Hide window initially if showing splash screen
        if show_splash:
            self.withdraw()

        # Window configuration
        self.title("⚡ Power Tools — media and other automation v1.0")
        self.geometry("1100x760")
        self.minsize(940, 620)
        self.configure(fg_color=COLORS["bg_dark"])

        # Set default appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Set application icon (ICO & PNG)
        self._set_app_icon()

        # Intercept window close to clean up background processes
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self._build_layout()
        self._init_views()

        # Select initial view (Video & Stream Downloaders)
        self.navigate_to("downloaders")

        # Show splash screen or reveal window
        if show_splash:
            self.splash = SplashScreen(self, on_complete=self._on_splash_done)
        else:
            self.deiconify()

    def _set_app_icon(self):
        ico_path = os.path.join(BASE_DIR, "assets", "icon.ico")
        png_path = os.path.join(BASE_DIR, "assets", "icon.png")

        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass

        if os.path.exists(png_path):
            try:
                from PIL import ImageTk
                img = ImageTk.PhotoImage(file=png_path)
                self.iconphoto(True, img)
            except Exception:
                pass

    def _on_splash_done(self):
        # Center main window on screen
        self.update_idletasks()
        w, h = 1100, 760
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.deiconify()

    def _build_layout(self):
        # 1. Status Bar at the bottom
        self.status_bar = StatusBar(self)
        self.status_bar.pack(side="bottom", fill="x")

        # 2. Main horizontal container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(side="top", fill="both", expand=True)

        # 3. Left Navigation Sidebar
        self.sidebar = Sidebar(self.main_container, on_navigate=self.navigate_to)
        self.sidebar.pack(side="left", fill="y")

        # 4. Right View Container
        self.view_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.view_container.pack(side="right", fill="both", expand=True)

    def _init_views(self):
        self.views = {
            "downloaders": DownloaderView(self.view_container),
            "live_stream": LiveStreamView(self.view_container),
            "audio_downloader": AudioDownloaderView(self.view_container),
            "file_downloader": FileDownloaderView(self.view_container),
            "compressor": CompressorView(self.view_container),
            "media_tools": MediaToolsView(self.view_container),
            "subtitles": SubtitleView(self.view_container),
            "system": SystemToolsView(self.view_container),
        }
        self.current_view_key = None

    def navigate_to(self, view_key: str):
        if view_key == self.current_view_key or view_key not in self.views:
            return

        # Hide current view
        if self.current_view_key and self.current_view_key in self.views:
            self.views[self.current_view_key].pack_forget()

        # Show selected view
        self.current_view_key = view_key
        self.sidebar.set_active(view_key)
        target_view = self.views[view_key]
        target_view.pack(fill="both", expand=True)

    def on_close(self):
        # Terminate any active background subprocesses cleanly
        for view in self.views.values():
            if hasattr(view, "runner") and view.runner and view.runner.is_running:
                view.runner.terminate()
        self.destroy()

# Backwards compatibility alias
OtherToolsApp = PowerToolsApp

def main():
    app = PowerToolsApp(show_splash=True)
    app.mainloop()

if __name__ == "__main__":
    main()
