"""
Theme, styling tokens, and palette configurations for other_tools CustomTkinter UI.
"""
import customtkinter as ctk

# Color Palette (Dark Mode Primary with Light Mode support)
COLORS = {
    "bg_dark": "#121316",
    "bg_sidebar": "#18191E",
    "bg_card": "#1E2026",
    "bg_card_hover": "#252830",
    "bg_terminal": "#0D0E11",
    "accent_primary": "#3B82F6",       # Modern vibrant blue
    "accent_primary_hover": "#2563EB",
    "accent_success": "#10B981",       # Emerald green
    "accent_success_hover": "#059669",
    "accent_warning": "#F59E0B",       # Amber
    "accent_danger": "#EF4444",        # Rose red
    "accent_danger_hover": "#DC2626",
    "accent_purple": "#8B5CF6",
    "border": "#2A2D35",
    "text_primary": "#F3F4F6",
    "text_secondary": "#9CA3AF",
    "text_muted": "#6B7280",
}

# Typography helper
def get_font(size=13, weight="normal"):
    return ctk.CTkFont(family="Segoe UI", size=size, weight=weight)

def get_mono_font(size=12, weight="normal"):
    return ctk.CTkFont(family="Consolas", size=size, weight=weight)
