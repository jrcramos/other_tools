"""
System & Updaters View - One-click tool updaters, Display Brightness reset, and Docker WSL2 compaction.
"""
import os
import sys
import customtkinter as ctk
from ui.theme import COLORS, get_font
from ui.views.base_view import BaseToolView

class SystemToolsView(BaseToolView):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            title="🛠️ System Utilities & Tool Updaters",
            description="One-click Git/binary updaters for FFmpeg, yt-dlp, and Streamlink, plus Windows hardware and Docker maintenance.",
            **kwargs
        )

    def build_options(self, container: ctk.CTkFrame):
        # We replace standard single start button with dedicated action cards
        self.action_bar.pack_forget()

        # Grid of tool cards
        grid = ctk.CTkFrame(container, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.columnconfigure((0, 1), weight=1)

        # Card 1: Master Updaters
        self._build_card(
            grid,
            row=0, col=0,
            title="🔄 1-Click Update All Tools",
            desc="Downloads and updates latest Git builds for FFmpeg, yt-dlp, N_m3u8DL-RE, and Streamlink.",
            btn_text="Run Full Updater",
            btn_color=COLORS["accent_primary"],
            command=self.run_update_all
        )

        # Card 2: yt-dlp Updater
        self._build_card(
            grid,
            row=0, col=1,
            title="📥 Update yt-dlp Only",
            desc="Runs self-updater for yt-dlp to get the latest YouTube / streaming extractor fixes.",
            btn_text="Update yt-dlp",
            btn_color=COLORS["accent_success"],
            command=self.run_update_ytdlp
        )

        # Card 3: Display Brightness Reset
        self._build_card(
            grid,
            row=1, col=0,
            title="☀️ Fix Display Brightness",
            desc="Resets Windows display driver instances via pnputil to restore broken brightness slider controls.",
            btn_text="Reset Display Driver",
            btn_color=COLORS["accent_warning"],
            command=self.run_fix_brightness
        )

        # Card 4: Docker & WSL2 Compactor
        self._build_card(
            grid,
            row=1, col=1,
            title="🐳 Docker & WSL2 Cleaner",
            desc="Prunes unused Docker images/volumes and compacts docker_data.vhdx disk space.",
            btn_text="Prune Docker Cache",
            btn_color=COLORS["accent_purple"],
            command=self.run_clean_docker
        )

    def _build_card(self, parent, row, col, title, desc, btn_text, btn_color, command):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_terminal"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"]
        )
        card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)

        ctk.CTkLabel(card, text=title, font=get_font(13, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(card, text=desc, font=get_font(11), text_color=COLORS["text_secondary"], wraplength=260, justify="left").pack(anchor="w", padx=12, pady=(0, 10))

        btn = ctk.CTkButton(
            card,
            text=btn_text,
            font=get_font(12, "bold"),
            height=32,
            fg_color=btn_color,
            command=command
        )
        btn.pack(anchor="w", padx=12, pady=(0, 12))

    def run_update_all(self):
        script_dir = os.path.dirname(os.path.abspath(__file__ + "/../.."))
        cmd_chain = f'cd /d "{script_dir}" && call update_yt-dlp.bat && call update_ffmpeg.bat && call update_stream_tools.bat && call update_aria2.bat'
        self.execute_command(f'cmd /c "{cmd_chain}"', cwd=script_dir)

    def run_update_ytdlp(self):
        script_dir = os.path.dirname(os.path.abspath(__file__ + "/../.."))
        self.execute_command(f'cmd /c "update_yt-dlp.bat"', cwd=script_dir)

    def run_fix_brightness(self):
        script_dir = os.path.dirname(os.path.abspath(__file__ + "/../.."))
        self.execute_command(f'cmd /c "FixBrightness.bat"', cwd=script_dir)

    def run_clean_docker(self):
        cmd = 'cmd /c "docker system prune -a --volumes -f"'
        self.execute_command(cmd)
