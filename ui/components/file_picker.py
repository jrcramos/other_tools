"""
Reusable file and folder picker input component with browse dialogs and path helpers.
"""
import os
import customtkinter as ctk
from tkinter import filedialog
from ui.theme import COLORS, get_font

class FilePicker(ctk.CTkFrame):
    def __init__(
        self,
        master,
        label_text: str = "Input File / Folder:",
        placeholder: str = "Select or paste file/folder path...",
        file_types: list = None,
        allow_folder: bool = True,
        allow_multiple: bool = False,
        on_change=None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.file_types = file_types or [("All files", "*.*")]
        self.allow_folder = allow_folder
        self.allow_multiple = allow_multiple
        self.on_change = on_change

        self._build_ui(label_text, placeholder)

    def _build_ui(self, label_text, placeholder):
        # Label
        self.label = ctk.CTkLabel(
            self,
            text=label_text,
            font=get_font(13, "bold"),
            text_color=COLORS["text_primary"]
        )
        self.label.pack(anchor="w", pady=(0, 4))

        # Input Row
        self.row_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.row_frame.pack(fill="x")

        self.entry = ctk.CTkEntry(
            self.row_frame,
            placeholder_text=placeholder,
            font=get_font(12),
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"],
            height=34
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        # Browse File button
        self.browse_file_btn = ctk.CTkButton(
            self.row_frame,
            text="📄 File",
            font=get_font(12),
            width=70,
            height=34,
            fg_color=COLORS["border"],
            hover_color=COLORS["bg_card_hover"],
            command=self._browse_file
        )
        self.browse_file_btn.pack(side="left", padx=2)

        # Browse Folder button
        if self.allow_folder:
            self.browse_folder_btn = ctk.CTkButton(
                self.row_frame,
                text="📁 Folder",
                font=get_font(12),
                width=75,
                height=34,
                fg_color=COLORS["border"],
                hover_color=COLORS["bg_card_hover"],
                command=self._browse_folder
            )
            self.browse_folder_btn.pack(side="left", padx=2)

        # Clear Button
        self.clear_btn = ctk.CTkButton(
            self.row_frame,
            text="✕",
            font=get_font(12),
            width=34,
            height=34,
            fg_color=COLORS["border"],
            hover_color=COLORS["accent_danger"],
            command=self.clear
        )
        self.clear_btn.pack(side="left", padx=(2, 0))

    def _browse_file(self):
        if self.allow_multiple:
            paths = filedialog.askopenfilenames(filetypes=self.file_types)
            if paths:
                formatted = "; ".join(f'"{p}"' for p in paths)
                self.set_path(formatted)
        else:
            path = filedialog.askopenfilename(filetypes=self.file_types)
            if path:
                self.set_path(path)

    def _browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.set_path(folder)

    def get_path(self) -> str:
        raw = self.entry.get().strip()
        # Clean enclosing quotes if single path
        if raw.startswith('"') and raw.endswith('"') and raw.count('"') == 2:
            raw = raw[1:-1]
        return raw

    def set_path(self, path: str):
        self.entry.delete(0, "end")
        self.entry.insert(0, path)
        if self.on_change:
            self.on_change(path)

    def clear(self):
        self.entry.delete(0, "end")
        if self.on_change:
            self.on_change("")
