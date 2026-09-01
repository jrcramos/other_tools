"""
Embedded live streaming terminal output component with copy, clear, and abort controls.
"""
import customtkinter as ctk
import tkinter as tk
from ui.theme import COLORS, get_font, get_mono_font

class TerminalView(ctk.CTkFrame):
    def __init__(self, master, on_abort_requested=None, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_card"], corner_radius=10, border_width=1, border_color=COLORS["border"], **kwargs)
        self.on_abort_requested = on_abort_requested
        self.auto_scroll = True

        self._build_ui()

    def _build_ui(self):
        # Header toolbar
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", height=36)
        self.header_frame.pack(fill="x", padx=12, pady=(8, 4))

        # Title & Status badge
        self.title_lbl = ctk.CTkLabel(
            self.header_frame,
            text="🖥️ Console Output",
            font=get_font(13, "bold"),
            text_color=COLORS["text_primary"]
        )
        self.title_lbl.pack(side="left")

        self.status_badge = ctk.CTkLabel(
            self.header_frame,
            text="IDLE",
            font=get_mono_font(11, "bold"),
            text_color=COLORS["text_muted"],
            fg_color=COLORS["bg_terminal"],
            corner_radius=6,
            padx=8,
            pady=2
        )
        self.status_badge.pack(side="left", padx=10)

        # Abort Button (disabled by default)
        self.abort_btn = ctk.CTkButton(
            self.header_frame,
            text="⏹️ Stop",
            font=get_font(12, "bold"),
            width=70,
            height=28,
            fg_color=COLORS["accent_danger"],
            hover_color=COLORS["accent_danger_hover"],
            state="disabled",
            command=self._on_abort
        )
        self.abort_btn.pack(side="right", padx=(6, 0))

        # Clear Button
        self.clear_btn = ctk.CTkButton(
            self.header_frame,
            text="🧹 Clear",
            font=get_font(12),
            width=65,
            height=28,
            fg_color=COLORS["border"],
            hover_color=COLORS["bg_card_hover"],
            command=self.clear
        )
        self.clear_btn.pack(side="right", padx=6)

        # Copy Output Button
        self.copy_btn = ctk.CTkButton(
            self.header_frame,
            text="📋 Copy",
            font=get_font(12),
            width=65,
            height=28,
            fg_color=COLORS["border"],
            hover_color=COLORS["bg_card_hover"],
            command=self.copy_to_clipboard
        )
        self.copy_btn.pack(side="right", padx=6)

        # Auto-scroll Switch
        self.scroll_switch = ctk.CTkSwitch(
            self.header_frame,
            text="Auto-scroll",
            font=get_font(11),
            command=self._toggle_autoscroll,
            width=36,
            height=18
        )
        self.scroll_switch.select()
        self.scroll_switch.pack(side="right", padx=10)

        # Terminal text display
        self.textbox = ctk.CTkTextbox(
            self,
            font=get_mono_font(12),
            fg_color=COLORS["bg_terminal"],
            text_color="#E0E6ED",
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
            wrap="char"
        )
        self.textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _toggle_autoscroll(self):
        self.auto_scroll = bool(self.scroll_switch.get())

    def append_log(self, text: str):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", text)
        if self.auto_scroll:
            self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def clear(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")

    def copy_to_clipboard(self):
        content = self.textbox.get("1.0", "end-1c")
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)

    def set_running_state(self, is_running: bool):
        if is_running:
            self.status_badge.configure(text="RUNNING", text_color=COLORS["accent_warning"])
            self.abort_btn.configure(state="normal")
        else:
            self.status_badge.configure(text="IDLE", text_color=COLORS["text_muted"])
            self.abort_btn.configure(state="disabled")

    def set_status(self, text: str, color: str = None):
        self.status_badge.configure(
            text=text.upper(),
            text_color=color if color else COLORS["text_primary"]
        )

    def _on_abort(self):
        if self.on_abort_requested:
            self.on_abort_requested()
