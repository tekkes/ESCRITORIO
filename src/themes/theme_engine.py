"""
Theme Engine para Escritorio
Gestor central de estilos visuales, paletas cromáticas e inyección dinámica
de tokens en tiempo de ejecución.
"""

from enum import Enum
from typing import Dict, Any, Optional
from .theme_parser import ThemePackage

class ThemeMode(Enum):
    DARK_OBSIDIAN = "dark_obsidian"
    MINIMAL_NORD = "minimal_nord"
    SOLARIZED_WARM = "solarized_warm"
    SEPIA_CLASSIC = "sepia_classic"
    SCRIVENER_CLASSIC_LIGHT = "scrivener_classic_light"

# Paletas base integradas
BUILTIN_PALETTES: Dict[ThemeMode, Dict[str, str]] = {
    ThemeMode.DARK_OBSIDIAN: {
        "window.background": "#1e1e24",
        "window.foreground": "#e0e0e6",
        "binder.background": "#18181c",
        "binder.foreground": "#c8c8d0",
        "binder.selected_bg": "#2d3748",
        "binder.selected_fg": "#ffffff",
        "editor.background": "#141416",
        "editor.foreground": "#d4d4d8",
        "editor.caret": "#6366f1",
        "editor.selection": "#3b4252",
        "corkboard.background": "#23232a",
        "corkboard.card_bg": "#2a2b36",
        "corkboard.card_fg": "#e2e8f0",
        "outliner.grid": "#2e2e38",
        "inspector.background": "#18181c"
    },
    ThemeMode.MINIMAL_NORD: {
        "window.background": "#2e3440",
        "window.foreground": "#d8dee9",
        "binder.background": "#242933",
        "binder.foreground": "#e5e9f0",
        "binder.selected_bg": "#434c5e",
        "binder.selected_fg": "#eceff4",
        "editor.background": "#2e3440",
        "editor.foreground": "#eceff4",
        "editor.caret": "#88c0d0",
        "editor.selection": "#4c566a",
        "corkboard.background": "#3b4252",
        "corkboard.card_bg": "#434c5e",
        "corkboard.card_fg": "#eceff4",
        "outliner.grid": "#434c5e",
        "inspector.background": "#242933"
    },
    ThemeMode.SOLARIZED_WARM: {
        "window.background": "#fdf6e3",
        "window.foreground": "#657b83",
        "binder.background": "#eee8d5",
        "binder.foreground": "#586e75",
        "binder.selected_bg": "#e0d9c4",
        "binder.selected_fg": "#073642",
        "editor.background": "#fdf6e3",
        "editor.foreground": "#073642",
        "editor.caret": "#b58900",
        "editor.selection": "#eee8d5",
        "corkboard.background": "#e8e0cc",
        "corkboard.card_bg": "#fffbf0",
        "corkboard.card_fg": "#586e75",
        "outliner.grid": "#e0d9c4",
        "inspector.background": "#eee8d5"
    },
    ThemeMode.SEPIA_CLASSIC: {
        "window.background": "#fbf0d9",
        "window.foreground": "#5f4b32",
        "binder.background": "#f4e4c1",
        "binder.foreground": "#493824",
        "binder.selected_bg": "#e6d2a7",
        "binder.selected_fg": "#2c2013",
        "editor.background": "#fef7e9",
        "editor.foreground": "#3b2d1d",
        "editor.caret": "#8b5a2b",
        "editor.selection": "#e6d2a7",
        "corkboard.background": "#edd8b1",
        "corkboard.card_bg": "#fff9eb",
        "corkboard.card_fg": "#493824",
        "outliner.grid": "#e0caa0",
        "inspector.background": "#f4e4c1"
    },
    ThemeMode.SCRIVENER_CLASSIC_LIGHT: {
        "window.background": "#f3f3f3",
        "window.foreground": "#111111",
        "binder.background": "#e8ebed",
        "binder.foreground": "#222222",
        "binder.selected_bg": "#c8d4df",
        "binder.selected_fg": "#000000",
        "editor.background": "#ffffff",
        "editor.foreground": "#111111",
        "editor.caret": "#0066cc",
        "editor.selection": "#b4d5fe",
        "corkboard.background": "#d8cfbe",
        "corkboard.card_bg": "#fffffc",
        "corkboard.card_fg": "#222222",
        "outliner.grid": "#e0e0e0",
        "inspector.background": "#edf0f2"
    }
}

class ThemeEngine:
    """Motor de gestión de temas activos y resolución de tokens."""

    def __init__(self, initial_mode: ThemeMode = ThemeMode.DARK_OBSIDIAN):
        self.current_mode = initial_mode
        self.current_palette = dict(BUILTIN_PALETTES[initial_mode])
        self.custom_package: Optional[ThemePackage] = None

    def set_builtin_mode(self, mode: ThemeMode):
        self.current_mode = mode
        self.current_palette = dict(BUILTIN_PALETTES[mode])
        self.custom_package = None

    def apply_custom_package(self, package: ThemePackage):
        self.custom_package = package
        self.current_palette.update(package.palette)

    def get_color(self, token_name: str, fallback: str = "#ffffff") -> str:
        return self.current_palette.get(token_name, fallback)

    def generate_qss(self) -> str:
        """Genera una hoja de estilo QSS completa inyectando los tokens activos."""
        p = self.current_palette
        return f"""
        QMainWindow, QWidget#root {{
            background-color: {p.get("window.background")};
            color: {p.get("window.foreground")};
            font-family: 'Segoe UI Variable Display', 'Segoe UI', sans-serif;
        }}
        QTreeView#binder {{
            background-color: {p.get("binder.background")};
            color: {p.get("binder.foreground")};
            border: none;
        }}
        QTreeView#binder::item:selected {{
            background-color: {p.get("binder.selected_bg")};
            color: {p.get("binder.selected_fg")};
        }}
        QTextEdit#editor {{
            background-color: {p.get("editor.background")};
            color: {p.get("editor.foreground")};
            selection-background-color: {p.get("editor.selection")};
        }}
        QWidget#corkboard {{
            background-color: {p.get("corkboard.background")};
        }}
        QWidget#corkboardCard {{
            background-color: {p.get("corkboard.card_bg")};
            color: {p.get("corkboard.card_fg")};
            border-radius: 6px;
        }}
        QTableView#outliner {{
            gridline-color: {p.get("outliner.grid")};
        }}
        QDockWidget#inspector {{
            background-color: {p.get("inspector.background")};
        }}
        """
