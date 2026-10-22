"""
Motor de Estilos QSS para Escritorio en PyQt6.
Genera hojas de estilo nativas de Windows 11 Fluent para todos los modos visuales:
Minimalista, Oscuro Obsidiana, Solarizado Claro/Oscuro, Sepia Pergamino, Nordic Frost y Catppuccin Mocha.
"""

from typing import Dict, Any

THEME_PALETTES: Dict[str, Dict[str, str]] = {
    "dark_obsidian": {
        "bg_main": "#1e1e24",
        "bg_surface": "#25252d",
        "bg_elevated": "#2d2d38",
        "bg_input": "#1a1a20",
        "fg_main": "#f0f0f5",
        "fg_muted": "#a0a0b0",
        "accent": "#7c5cbf",
        "accent_hover": "#9370db",
        "border": "#3a3a48",
        "header_bg": "#18181e",
        "card_bg": "#2b2b36",
        "selection_bg": "#4a3b68",
        "selection_fg": "#ffffff",
    },
    "minimalist_default": {
        "bg_main": "#f8f9fa",
        "bg_surface": "#ffffff",
        "bg_elevated": "#f0f2f5",
        "bg_input": "#ffffff",
        "fg_main": "#1c1e21",
        "fg_muted": "#65676b",
        "accent": "#0d6efd",
        "accent_hover": "#0b5ed7",
        "border": "#dee2e6",
        "header_bg": "#eaedf1",
        "card_bg": "#ffffff",
        "selection_bg": "#cfe2ff",
        "selection_fg": "#084298",
    },
    "solarized_dark": {
        "bg_main": "#002b36",
        "bg_surface": "#073642",
        "bg_elevated": "#0a4554",
        "bg_input": "#00212b",
        "fg_main": "#839496",
        "fg_muted": "#586e75",
        "accent": "#268bd2",
        "accent_hover": "#2aa198",
        "border": "#0e5a6e",
        "header_bg": "#001e26",
        "card_bg": "#073642",
        "selection_bg": "#0d5c75",
        "selection_fg": "#fdf6e3",
    },
    "solarized_light": {
        "bg_main": "#fdf6e3",
        "bg_surface": "#eee8d5",
        "bg_elevated": "#e4decb",
        "bg_input": "#ffffff",
        "fg_main": "#657b83",
        "fg_muted": "#93a1a1",
        "accent": "#268bd2",
        "accent_hover": "#2aa198",
        "border": "#d33682",
        "header_bg": "#e6e0cc",
        "card_bg": "#eee8d5",
        "selection_bg": "#d8d1bc",
        "selection_fg": "#073642",
    },
    "sepia_parchment": {
        "bg_main": "#f4ecd8",
        "bg_surface": "#faf4e6",
        "bg_elevated": "#e8dfc8",
        "bg_input": "#fffdf7",
        "fg_main": "#433422",
        "fg_muted": "#826d57",
        "accent": "#8b5a2b",
        "accent_hover": "#a76d34",
        "border": "#d2c4aa",
        "header_bg": "#ded3b8",
        "card_bg": "#fcf8ee",
        "selection_bg": "#d9cbaf",
        "selection_fg": "#2c1f10",
    },
    "nordic_frost": {
        "bg_main": "#2e3440",
        "bg_surface": "#3b4252",
        "bg_elevated": "#434c5e",
        "bg_input": "#242933",
        "fg_main": "#eceff4",
        "fg_muted": "#d8dee9",
        "accent": "#88c0d0",
        "accent_hover": "#81a1c1",
        "border": "#4c566a",
        "header_bg": "#272c36",
        "card_bg": "#3b4252",
        "selection_bg": "#434c5e",
        "selection_fg": "#eceff4",
    },
    "catppuccin_mocha": {
        "bg_main": "#1e1e2e",
        "bg_surface": "#24273a",
        "bg_elevated": "#313244",
        "bg_input": "#181825",
        "fg_main": "#cdd6f4",
        "fg_muted": "#a6adc8",
        "accent": "#cba6f7",
        "accent_hover": "#b4befe",
        "border": "#45475a",
        "header_bg": "#181825",
        "card_bg": "#24273a",
        "selection_bg": "#45475a",
        "selection_fg": "#f5e0dc",
    }
}

def get_qss(theme_name: str = "dark_obsidian") -> str:
    """Genera la hoja de estilos QSS completa para el tema indicado."""
    p = THEME_PALETTES.get(theme_name, THEME_PALETTES["dark_obsidian"])

    qss = f"""
    /* Ventana principal y widgets base */
    QMainWindow, QDialog, QWidget {{
        background-color: {p["bg_main"]};
        color: {p["fg_main"]};
        font-family: "Segoe UI Variable Display", "Segoe UI", sans-serif;
        font-size: 10pt;
    }}

    /* Barra de menús */
    QMenuBar {{
        background-color: {p["header_bg"]};
        color: {p["fg_main"]};
        border-bottom: 1px solid {p["border"]};
        padding: 4px;
    }}
    QMenuBar::item {{
        background: transparent;
        padding: 4px 10px;
        border-radius: 4px;
    }}
    QMenuBar::item:selected {{
        background-color: {p["bg_elevated"]};
        color: {p["accent"]};
    }}
    QMenu {{
        background-color: {p["bg_surface"]};
        color: {p["fg_main"]};
        border: 1px solid {p["border"]};
        border-radius: 6px;
        padding: 4px;
    }}
    QMenu::item {{
        padding: 6px 24px;
        border-radius: 4px;
    }}
    QMenu::item:selected {{
        background-color: {p["accent"]};
        color: #ffffff;
    }}
    QMenu::separator {{
        height: 1px;
        background-color: {p["border"]};
        margin: 4px 8px;
    }}

    /* Barra de herramientas */
    QToolBar {{
        background-color: {p["header_bg"]};
        border-bottom: 1px solid {p["border"]};
        spacing: 6px;
        padding: 4px 8px;
    }}
    QToolButton {{
        background: transparent;
        color: {p["fg_main"]};
        border: 1px solid transparent;
        border-radius: 4px;
        padding: 4px 8px;
        font-weight: 500;
    }}
    QToolButton:hover {{
        background-color: {p["bg_elevated"]};
        border: 1px solid {p["border"]};
        color: {p["accent"]};
    }}
    QToolButton:pressed {{
        background-color: {p["accent"]};
        color: #ffffff;
    }}

    /* Barra de estado */
    QStatusBar {{
        background-color: {p["header_bg"]};
        color: {p["fg_muted"]};
        border-top: 1px solid {p["border"]};
        font-size: 9pt;
        padding: 2px 8px;
    }}

    /* Divisores (QSplitter) */
    QSplitter::handle {{
        background-color: {p["border"]};
    }}
    QSplitter::handle:horizontal {{
        width: 3px;
    }}
    QSplitter::handle:vertical {{
        height: 3px;
    }}

    /* Árbol del Binder (QTreeWidget) */
    QTreeWidget {{
        background-color: {p["bg_surface"]};
        color: {p["fg_main"]};
        border: 1px solid {p["border"]};
        border-radius: 6px;
        padding: 4px;
    }}
    QTreeWidget::item {{
        padding: 5px 6px;
        border-radius: 4px;
    }}
    QTreeWidget::item:hover {{
        background-color: {p["bg_elevated"]};
    }}
    QTreeWidget::item:selected {{
        background-color: {p["selection_bg"]};
        color: {p["selection_fg"]};
    }}
    QHeaderView::section {{
        background-color: {p["header_bg"]};
        color: {p["fg_muted"]};
        padding: 4px 8px;
        border: none;
        border-right: 1px solid {p["border"]};
        border-bottom: 1px solid {p["border"]};
        font-weight: 600;
    }}

    /* Editor de texto RTF (QTextEdit) */
    QTextEdit, QPlainTextEdit {{
        background-color: {p["bg_input"]};
        color: {p["fg_main"]};
        border: 1px solid {p["border"]};
        border-radius: 6px;
        padding: 12px;
        selection-background-color: {p["selection_bg"]};
        selection-color: {p["selection_fg"]};
    }}

    /* Tablas (QTableWidget) para el Outliner */
    QTableWidget {{
        background-color: {p["bg_surface"]};
        color: {p["fg_main"]};
        gridline-color: {p["border"]};
        border: 1px solid {p["border"]};
        border-radius: 6px;
        selection-background-color: {p["selection_bg"]};
        selection-color: {p["selection_fg"]};
    }}
    QTableWidget::item {{
        padding: 4px 8px;
    }}

    /* Pestañas (QTabWidget) para el Inspector */
    QTabWidget::pane {{
        border: 1px solid {p["border"]};
        border-radius: 6px;
        background-color: {p["bg_surface"]};
        top: -1px;
    }}
    QTabBar::tab {{
        background-color: {p["header_bg"]};
        color: {p["fg_muted"]};
        border: 1px solid {p["border"]};
        border-bottom: none;
        padding: 6px 12px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background-color: {p["bg_surface"]};
        color: {p["accent"]};
        font-weight: 600;
    }}
    QTabBar::tab:hover:!selected {{
        background-color: {p["bg_elevated"]};
    }}

    /* Botones generales (QPushButton) */
    QPushButton {{
        background-color: {p["bg_elevated"]};
        color: {p["fg_main"]};
        border: 1px solid {p["border"]};
        border-radius: 5px;
        padding: 6px 14px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: {p["accent"]};
        color: #ffffff;
        border-color: {p["accent_hover"]};
    }}
    QPushButton:pressed {{
        background-color: {p["accent_hover"]};
    }}
    QPushButton:disabled {{
        background-color: {p["bg_surface"]};
        color: {p["fg_muted"]};
        border-color: {p["border"]};
    }}

    /* Campos de entrada (QLineEdit, QComboBox, QSpinBox) */
    QLineEdit, QComboBox, QSpinBox {{
        background-color: {p["bg_input"]};
        color: {p["fg_main"]};
        border: 1px solid {p["border"]};
        border-radius: 5px;
        padding: 4px 8px;
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 1px solid {p["accent"]};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {p["bg_surface"]};
        color: {p["fg_main"]};
        border: 1px solid {p["border"]};
        selection-background-color: {p["accent"]};
        selection-color: #ffffff;
    }}

    /* Barras de progreso */
    QProgressBar {{
        background-color: {p["bg_elevated"]};
        border: 1px solid {p["border"]};
        border-radius: 4px;
        text-align: center;
        color: {p["fg_main"]};
        font-size: 8pt;
    }}
    QProgressBar::chunk {{
        background-color: {p["accent"]};
        border-radius: 3px;
    }}

    /* Barras de desplazamiento (QScrollBar) */
    QScrollBar:vertical {{
        background: {p["bg_main"]};
        width: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {p["border"]};
        min-height: 20px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {p["accent"]};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background: {p["bg_main"]};
        height: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: {p["border"]};
        min-width: 20px;
        border-radius: 5px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {p["accent"]};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    """
    return qss
