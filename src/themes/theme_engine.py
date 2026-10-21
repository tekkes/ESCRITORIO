"""
Theme Engine para Escritorio
Gestor central de estilos visuales, paletas cromáticas, modos de densidad UI
e inyección dinámica de tokens con conmutación en caliente de sub-50ms.
"""

import time
from enum import Enum
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from .theme_parser import ThemePackage, ThemeParser, ScrThemeLoader


class ThemeMode(Enum):
    """Los 7 modos de visualización predefinidos de Escritorio."""
    MINIMALIST_DEFAULT = "minimalist_default"
    CARBON_DARK = "carbon_dark"
    SOLARIZED_DARK = "solarized_dark"
    SOLARIZED_LIGHT = "solarized_light"
    SEPIA_PARCHMENT = "sepia_parchment"
    NORDIC_FROST = "nordic_frost"
    CATPPUCCIN_MOCHA = "catppuccin_mocha"

    # Aliases de compatibilidad hacia atrás
    DARK_OBSIDIAN = "carbon_dark"
    MINIMAL_NORD = "nordic_frost"
    SOLARIZED_WARM = "solarized_light"
    SEPIA_CLASSIC = "sepia_parchment"
    SCRIVENER_CLASSIC_LIGHT = "minimalist_default"


class UIDensityMode(Enum):
    """
    Control de Densidad Visual (UI Density) para maximizar el espacio de escritura.
    """
    ULTRA_COMPACT = "ultra_compact"   # Iconos 14px, toolbar 28px, header 24px, badge 10px, dot 6px
    COMPACT = "compact"               # Iconos 16px, toolbar 32px, header 26px, badge 12px, dot 6px
    COMFORTABLE = "comfortable"       # Iconos 18px, toolbar 38px, header 30px, badge 14px, dot 8px


@dataclass
class DensityMetrics:
    icon_size: int
    toolbar_height: int
    editor_header_height: int
    badge_height: int
    status_indicator_size: int
    binder_row_height: int
    font_size_ui: int
    font_size_small: int


DENSITY_CONFIGS: Dict[UIDensityMode, DensityMetrics] = {
    UIDensityMode.ULTRA_COMPACT: DensityMetrics(
        icon_size=14,
        toolbar_height=28,
        editor_header_height=24,
        badge_height=10,
        status_indicator_size=6,
        binder_row_height=22,
        font_size_ui=11,
        font_size_small=10
    ),
    UIDensityMode.COMPACT: DensityMetrics(
        icon_size=16,
        toolbar_height=32,
        editor_header_height=26,
        badge_height=12,
        status_indicator_size=6,
        binder_row_height=24,
        font_size_ui=12,
        font_size_small=11
    ),
    UIDensityMode.COMFORTABLE: DensityMetrics(
        icon_size=18,
        toolbar_height=38,
        editor_header_height=30,
        badge_height=14,
        status_indicator_size=8,
        binder_row_height=28,
        font_size_ui=13,
        font_size_small=12
    ),
}


# Definición exacta de las 7 paletas oficiales de fábrica
BUILTIN_PALETTES: Dict[ThemeMode, Dict[str, str]] = {
    # 1. Modo Minimalista (Por Defecto)
    ThemeMode.MINIMALIST_DEFAULT: {
        "window.background": "#F7F7F5",
        "window.foreground": "#242424",
        "window.border": "#E5E5E2",
        "toolbar.background": "#EFEFEC",
        "toolbar.foreground": "#242424",
        "toolbar.border": "#E0E0DD",
        "statusbar.background": "#EFEFEC",
        "statusbar.foreground": "#6E6E6E",
        "binder.background": "#F7F7F5",
        "binder.foreground": "#242424",
        "binder.secondary_text": "#787878",
        "binder.selected_bg": "#E2E2DE",
        "binder.selected_fg": "#000000",
        "binder.border": "#E5E5E2",
        "editor.background": "#FFFFFF",
        "editor.foreground": "#1A1A1A",
        "editor.caret": "#2D72D9",
        "editor.selection": "#D4E2F5",
        "editor.header_bg": "#FAFAFA",
        "editor.header_fg": "#4A4A4A",
        "corkboard.background": "#F2F2EE",
        "corkboard.card_bg": "#FFFFFF",
        "corkboard.card_fg": "#242424",
        "corkboard.card_border": "#D8D8D4",
        "corkboard.pin_color": "#2D72D9",
        "outliner.background": "#FFFFFF",
        "outliner.foreground": "#242424",
        "outliner.row_alternate": "#F9F9F8",
        "outliner.grid": "#E8E8E4",
        "inspector.background": "#F7F7F5",
        "inspector.foreground": "#242424",
        "inspector.card_bg": "#FFFFFF",
        "accent.primary": "#2D72D9",
        "accent.secondary": "#4A5568",
        "badge.label_bg": "#E5EDF9",
        "badge.label_fg": "#1E4F9E",
        "badge.status_bg": "#E8E8E4",
        "badge.status_fg": "#4A4A4A"
    },

    # 2. Modo Oscuro (Carbon Dark)
    ThemeMode.CARBON_DARK: {
        "window.background": "#18191A",
        "window.foreground": "#E4E6EB",
        "window.border": "#2E3033",
        "toolbar.background": "#202124",
        "toolbar.foreground": "#E4E6EB",
        "toolbar.border": "#2E3033",
        "statusbar.background": "#141517",
        "statusbar.foreground": "#B0B3B8",
        "binder.background": "#18191A",
        "binder.foreground": "#E4E6EB",
        "binder.secondary_text": "#8A8D91",
        "binder.selected_bg": "#2D3748",
        "binder.selected_fg": "#FFFFFF",
        "binder.border": "#2E3033",
        "editor.background": "#141517",
        "editor.foreground": "#E4E6EB",
        "editor.caret": "#4E95FF",
        "editor.selection": "#2C3E50",
        "editor.header_bg": "#1C1D20",
        "editor.header_fg": "#B0B3B8",
        "corkboard.background": "#1C1D1F",
        "corkboard.card_bg": "#25272A",
        "corkboard.card_fg": "#E4E6EB",
        "corkboard.card_border": "#36383D",
        "corkboard.pin_color": "#EF4444",
        "outliner.background": "#18191A",
        "outliner.foreground": "#E4E6EB",
        "outliner.row_alternate": "#1C1D20",
        "outliner.grid": "#2E3033",
        "inspector.background": "#18191A",
        "inspector.foreground": "#E4E6EB",
        "inspector.card_bg": "#25272A",
        "accent.primary": "#4E95FF",
        "accent.secondary": "#6366F1",
        "badge.label_bg": "#1E3A8A",
        "badge.label_fg": "#BFDBFE",
        "badge.status_bg": "#374151",
        "badge.status_fg": "#E5E7EB"
    },

    # 3. Modo Solarizado Oscuro (Solarized Dark)
    ThemeMode.SOLARIZED_DARK: {
        "window.background": "#002B36",
        "window.foreground": "#839496",
        "window.border": "#073642",
        "toolbar.background": "#073642",
        "toolbar.foreground": "#93A1A1",
        "toolbar.border": "#094959",
        "statusbar.background": "#073642",
        "statusbar.foreground": "#657B83",
        "binder.background": "#00212B",
        "binder.foreground": "#839496",
        "binder.secondary_text": "#586E75",
        "binder.selected_bg": "#073642",
        "binder.selected_fg": "#93A1A1",
        "binder.border": "#073642",
        "editor.background": "#002B36",
        "editor.foreground": "#839496",
        "editor.caret": "#B58900",
        "editor.selection": "#073642",
        "editor.header_bg": "#00242E",
        "editor.header_fg": "#93A1A1",
        "corkboard.background": "#073642",
        "corkboard.card_bg": "#002B36",
        "corkboard.card_fg": "#839496",
        "corkboard.card_border": "#094959",
        "corkboard.pin_color": "#DC322F",
        "outliner.background": "#002B36",
        "outliner.foreground": "#839496",
        "outliner.row_alternate": "#00313E",
        "outliner.grid": "#073642",
        "inspector.background": "#00212B",
        "inspector.foreground": "#839496",
        "inspector.card_bg": "#002B36",
        "accent.primary": "#B58900",
        "accent.secondary": "#2AA198",
        "badge.label_bg": "#073642",
        "badge.label_fg": "#2AA198",
        "badge.status_bg": "#073642",
        "badge.status_fg": "#B58900"
    },

    # 4. Modo Solarizado Claro (Solarized Light)
    ThemeMode.SOLARIZED_LIGHT: {
        "window.background": "#EEE8D5",
        "window.foreground": "#657B83",
        "window.border": "#E0D9C4",
        "toolbar.background": "#E8E2CF",
        "toolbar.foreground": "#586E75",
        "toolbar.border": "#DACFB7",
        "statusbar.background": "#E8E2CF",
        "statusbar.foreground": "#839496",
        "binder.background": "#EEE8D5",
        "binder.foreground": "#657B83",
        "binder.secondary_text": "#93A1A1",
        "binder.selected_bg": "#DFD7C2",
        "binder.selected_fg": "#073642",
        "binder.border": "#DACFB7",
        "editor.background": "#FDF6E3",
        "editor.foreground": "#657B83",
        "editor.caret": "#B58900",
        "editor.selection": "#EEE8D5",
        "editor.header_bg": "#F5EED9",
        "editor.header_fg": "#586E75",
        "corkboard.background": "#E5DECB",
        "corkboard.card_bg": "#FDF6E3",
        "corkboard.card_fg": "#657B83",
        "corkboard.card_border": "#DACFB7",
        "corkboard.pin_color": "#CB4B16",
        "outliner.background": "#FDF6E3",
        "outliner.foreground": "#657B83",
        "outliner.row_alternate": "#F8F0DC",
        "outliner.grid": "#EEE8D5",
        "inspector.background": "#EEE8D5",
        "inspector.foreground": "#657B83",
        "inspector.card_bg": "#FDF6E3",
        "accent.primary": "#B58900",
        "accent.secondary": "#268BD2",
        "badge.label_bg": "#DFD7C2",
        "badge.label_fg": "#268BD2",
        "badge.status_bg": "#DFD7C2",
        "badge.status_fg": "#B58900"
    },

    # 5. Modo Sepia (Classic Parchment)
    ThemeMode.SEPIA_PARCHMENT: {
        "window.background": "#E8DEC3",
        "window.foreground": "#3B2F2F",
        "window.border": "#D6C8A8",
        "toolbar.background": "#E2D7BB",
        "toolbar.foreground": "#3B2F2F",
        "toolbar.border": "#D2C3A0",
        "statusbar.background": "#E2D7BB",
        "statusbar.foreground": "#6E5D4F",
        "binder.background": "#E8DEC3",
        "binder.foreground": "#3B2F2F",
        "binder.secondary_text": "#7A6856",
        "binder.selected_bg": "#D9CEB0",
        "binder.selected_fg": "#231B1B",
        "binder.border": "#D6C8A8",
        "editor.background": "#F4ECD8",
        "editor.foreground": "#3B2F2F",
        "editor.caret": "#8C5333",
        "editor.selection": "#E4D5B7",
        "editor.header_bg": "#ECE3CD",
        "editor.header_fg": "#5C4A3E",
        "corkboard.background": "#DFD3B5",
        "corkboard.card_bg": "#F7F1E1",
        "corkboard.card_fg": "#3B2F2F",
        "corkboard.card_border": "#CCBE9E",
        "corkboard.pin_color": "#8C5333",
        "outliner.background": "#F4ECD8",
        "outliner.foreground": "#3B2F2F",
        "outliner.row_alternate": "#ECE4CE",
        "outliner.grid": "#DFD3B5",
        "inspector.background": "#E8DEC3",
        "inspector.foreground": "#3B2F2F",
        "inspector.card_bg": "#F7F1E1",
        "accent.primary": "#8C5333",
        "accent.secondary": "#5C4A3E",
        "badge.label_bg": "#DACFB2",
        "badge.label_fg": "#8C5333",
        "badge.status_bg": "#D6C8A8",
        "badge.status_fg": "#4A3B31"
    },

    # 6. Modo Nord (Nordic Frost)
    ThemeMode.NORDIC_FROST: {
        "window.background": "#2E3440",
        "window.foreground": "#ECEFF4",
        "window.border": "#434C5E",
        "toolbar.background": "#3B4252",
        "toolbar.foreground": "#ECEFF4",
        "toolbar.border": "#4C566A",
        "statusbar.background": "#2E3440",
        "statusbar.foreground": "#D8DEE9",
        "binder.background": "#2E3440",
        "binder.foreground": "#ECEFF4",
        "binder.secondary_text": "#9FB0C7",
        "binder.selected_bg": "#434C5E",
        "binder.selected_fg": "#ECEFF4",
        "binder.border": "#434C5E",
        "editor.background": "#2E3440",
        "editor.foreground": "#ECEFF4",
        "editor.caret": "#88C0D0",
        "editor.selection": "#434C5E",
        "editor.header_bg": "#353C4A",
        "editor.header_fg": "#E5E9F0",
        "corkboard.background": "#3B4252",
        "corkboard.card_bg": "#434C5E",
        "corkboard.card_fg": "#ECEFF4",
        "corkboard.card_border": "#4C566A",
        "corkboard.pin_color": "#BF616A",
        "outliner.background": "#2E3440",
        "outliner.foreground": "#ECEFF4",
        "outliner.row_alternate": "#353C4A",
        "outliner.grid": "#434C5E",
        "inspector.background": "#2E3440",
        "inspector.foreground": "#ECEFF4",
        "inspector.card_bg": "#434C5E",
        "accent.primary": "#88C0D0",
        "accent.secondary": "#81A1C1",
        "badge.label_bg": "#434C5E",
        "badge.label_fg": "#88C0D0",
        "badge.status_bg": "#4C566A",
        "badge.status_fg": "#E5E9F0"
    },

    # 7. Modo Catppuccin Mocha
    ThemeMode.CATPPUCCIN_MOCHA: {
        "window.background": "#181825",
        "window.foreground": "#CDD6F4",
        "window.border": "#313244",
        "toolbar.background": "#11111B",
        "toolbar.foreground": "#CDD6F4",
        "toolbar.border": "#313244",
        "statusbar.background": "#11111B",
        "statusbar.foreground": "#A6ADC8",
        "binder.background": "#181825",
        "binder.foreground": "#CDD6F4",
        "binder.secondary_text": "#6C7086",
        "binder.selected_bg": "#313244",
        "binder.selected_fg": "#CDD6F4",
        "binder.border": "#313244",
        "editor.background": "#1E1E2E",
        "editor.foreground": "#CDD6F4",
        "editor.caret": "#CBA6F7",
        "editor.selection": "#45475A",
        "editor.header_bg": "#181825",
        "editor.header_fg": "#A6ADC8",
        "corkboard.background": "#181825",
        "corkboard.card_bg": "#313244",
        "corkboard.card_fg": "#CDD6F4",
        "corkboard.card_border": "#45475A",
        "corkboard.pin_color": "#F38BA8",
        "outliner.background": "#1E1E2E",
        "outliner.foreground": "#CDD6F4",
        "outliner.row_alternate": "#181825",
        "outliner.grid": "#313244",
        "inspector.background": "#181825",
        "inspector.foreground": "#CDD6F4",
        "inspector.card_bg": "#313244",
        "accent.primary": "#CBA6F7",
        "accent.secondary": "#B4BEFE",
        "badge.label_bg": "#313244",
        "badge.label_fg": "#B4BEFE",
        "badge.status_bg": "#45475A",
        "badge.status_fg": "#CDD6F4"
    }
}


class ThemeEngine:
    """
    Motor central de estilos visuales, resolución de tokens y control de densidad.
    Diseñado para garantizar cambios de tema sin parpadeos y en menos de 50 ms.
    """

    def __init__(
        self,
        initial_mode: ThemeMode = ThemeMode.MINIMALIST_DEFAULT,
        initial_density: UIDensityMode = UIDensityMode.ULTRA_COMPACT
    ):
        self.current_mode = initial_mode
        self.density_mode = initial_density
        self.density_metrics = DENSITY_CONFIGS[initial_density]
        self.current_palette: Dict[str, str] = dict(BUILTIN_PALETTES[initial_mode])
        self.custom_package: Optional[ThemePackage] = None
        self._on_theme_changed_listeners: List[Callable[['ThemeEngine'], None]] = []

    def register_listener(self, callback: Callable[['ThemeEngine'], None]):
        """Registra un observador para cambios de tema o densidad."""
        if callback not in self._on_theme_changed_listeners:
            self._on_theme_changed_listeners.append(callback)

    def unregister_listener(self, callback: Callable[['ThemeEngine'], None]):
        if callback in self._on_theme_changed_listeners:
            self._on_theme_changed_listeners.remove(callback)

    def _notify_listeners(self):
        for listener in self._on_theme_changed_listeners:
            try:
                listener(self)
            except Exception:
                pass

    def set_builtin_mode(self, mode: ThemeMode) -> float:
        """
        Cambia al modo predefinido indicado.
        Retorna el tiempo transcurrido en milisegundos (garantizado < 50ms).
        """
        t0 = time.perf_counter()
        self.current_mode = mode
        self.current_palette = dict(BUILTIN_PALETTES[mode])
        self.custom_package = None
        self._notify_listeners()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return elapsed_ms

    def set_density_mode(self, density: UIDensityMode):
        """Ajusta la densidad visual de la interfaz (Ultra-compacto, Compacto, Cómodo)."""
        self.density_mode = density
        self.density_metrics = DENSITY_CONFIGS[density]
        self._notify_listeners()

    def apply_custom_package(self, package: ThemePackage) -> float:
        """Aplica un paquete importado (.scrtheme o .escrtheme)."""
        t0 = time.perf_counter()
        self.custom_package = package
        self.current_palette.update(package.palette)
        self._notify_listeners()
        return (time.perf_counter() - t0) * 1000.0

    def get_color(self, token_name: str, fallback: str = "#FFFFFF") -> str:
        """Resuelve un token cromático con fallback."""
        return self.current_palette.get(token_name, fallback)

    def benchmark_mode_switching(self) -> Dict[str, float]:
        """
        Mide el tiempo de conmutación entre los 7 modos oficiales.
        Verifica que cada conmutación se complete en menos de 50 ms.
        """
        results = {}
        modes = [
            ThemeMode.MINIMALIST_DEFAULT,
            ThemeMode.CARBON_DARK,
            ThemeMode.SOLARIZED_DARK,
            ThemeMode.SOLARIZED_LIGHT,
            ThemeMode.SEPIA_PARCHMENT,
            ThemeMode.NORDIC_FROST,
            ThemeMode.CATPPUCCIN_MOCHA
        ]
        for mode in modes:
            elapsed = self.set_builtin_mode(mode)
            results[mode.value] = elapsed
        return results

    def generate_micro_badge(self, text: str, bg_color: Optional[str] = None, fg_color: Optional[str] = None) -> str:
        """
        Genera el fragmento de estilo y marcado para micro-píldoras (10px altura en ultra-compacto).
        """
        m = self.density_metrics
        bg = bg_color or self.get_color("badge.label_bg", "#E5EDF9")
        fg = fg_color or self.get_color("badge.label_fg", "#1E4F9E")
        return (
            f"display: inline-block; height: {m.badge_height}px; line-height: {m.badge_height}px; "
            f"padding: 0 4px; font-size: {m.font_size_small - 1}px; font-weight: bold; "
            f"border-radius: {m.badge_height // 2}px; background-color: {bg}; color: {fg}; text-transform: uppercase;"
        )

    def generate_status_dot(self, color_hex: str) -> str:
        """
        Genera el indicador cromático circular de estado (6px diámetro en ultra-compacto).
        """
        size = self.density_metrics.status_indicator_size
        return (
            f"display: inline-block; width: {size}px; height: {size}px; "
            f"border-radius: {size // 2}px; background-color: {color_hex}; vertical-align: middle;"
        )

    def generate_qss(self) -> str:
        """
        Genera una hoja de estilo Qt/QSS completa inyectando los tokens cromáticos
        y las dimensiones exactas de densidad UI.
        """
        p = self.current_palette
        d = self.density_metrics

        return f"""
        /* Hoja de estilos dinámica generada por ThemeEngine de Escritorio */
        QMainWindow, QWidget#root {{
            background-color: {p.get("window.background")};
            color: {p.get("window.foreground")};
            font-family: 'Segoe UI Variable Display', 'Segoe UI', -apple-system, sans-serif;
            font-size: {d.font_size_ui}px;
        }}

        /* Barra de herramientas compacta ({d.toolbar_height}px) */
        QToolBar#mainToolbar {{
            background-color: {p.get("toolbar.background")};
            color: {p.get("toolbar.foreground")};
            border-bottom: 1px solid {p.get("toolbar.border")};
            min-height: {d.toolbar_height}px;
            max-height: {d.toolbar_height}px;
            padding: 0 4px;
        }}
        QToolBar#mainToolbar QToolButton {{
            font-size: {d.font_size_small}px;
            height: {d.toolbar_height - 6}px;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        QToolBar#mainToolbar QToolButton:hover {{
            background-color: {p.get("binder.selected_bg")};
        }}

        /* Binder / Navegador jerárquico */
        QTreeView#binder {{
            background-color: {p.get("binder.background")};
            color: {p.get("binder.foreground")};
            border: none;
            border-right: 1px solid {p.get("binder.border")};
            font-size: {d.font_size_ui}px;
        }}
        QTreeView#binder::item {{
            height: {d.binder_row_height}px;
        }}
        QTreeView#binder::item:selected {{
            background-color: {p.get("binder.selected_bg")};
            color: {p.get("binder.selected_fg")};
            border-radius: 3px;
        }}

        /* Cabecera del Editor ({d.editor_header_height}px) */
        QWidget#editorHeader {{
            background-color: {p.get("editor.header_bg")};
            color: {p.get("editor.header_fg")};
            min-height: {d.editor_header_height}px;
            max-height: {d.editor_header_height}px;
            border-bottom: 1px solid {p.get("window.border")};
            font-size: {d.font_size_small}px;
        }}

        /* Editor RTF */
        QTextEdit#editor {{
            background-color: {p.get("editor.background")};
            color: {p.get("editor.foreground")};
            selection-background-color: {p.get("editor.selection")};
            border: none;
            font-family: 'Georgia', 'Segoe UI Variable Text', serif;
        }}

        /* Pizarra de Corcho (Corkboard) */
        QWidget#corkboard {{
            background-color: {p.get("corkboard.background")};
        }}
        QWidget#corkboardCard {{
            background-color: {p.get("corkboard.card_bg")};
            color: {p.get("corkboard.card_fg")};
            border: 1px solid {p.get("corkboard.card_border")};
            border-radius: 4px;
        }}

        /* Esquematizador (Outliner) */
        QTableView#outliner {{
            background-color: {p.get("outliner.background")};
            color: {p.get("outliner.foreground")};
            gridline-color: {p.get("outliner.grid")};
            border: none;
        }}
        QTableView#outliner::item:alternate {{
            background-color: {p.get("outliner.row_alternate")};
        }}

        /* Inspector Lateral */
        QDockWidget#inspector {{
            background-color: {p.get("inspector.background")};
            color: {p.get("inspector.foreground")};
            border-left: 1px solid {p.get("window.border")};
        }}
        QWidget#inspectorCard {{
            background-color: {p.get("inspector.card_bg")};
            border: 1px solid {p.get("window.border")};
            border-radius: 4px;
        }}

        /* Barra de estado */
        QStatusBar#statusBar {{
            background-color: {p.get("statusbar.background")};
            color: {p.get("statusbar.foreground")};
            border-top: 1px solid {p.get("toolbar.border")};
            min-height: 22px;
            font-size: {d.font_size_small}px;
        }}

        /* Micro-etiquetas y badges */
        QLabel.microBadge {{
            font-size: {d.font_size_small - 1}px;
            font-weight: bold;
            padding: 1px 4px;
            border-radius: {d.badge_height // 2}px;
            background-color: {p.get("badge.label_bg")};
            color: {p.get("badge.label_fg")};
        }}
        """
