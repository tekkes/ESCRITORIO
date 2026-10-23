"""
ESCRITORIO v2.0 - Theme Engine & Visual Styling
Motor de diseño y estilos inspirado en la estética limpia y profesional de Scrivener 3 para macOS,
adaptado a Windows 11 con High DPI y soporte para 8 temas completos en caliente.
"""

from typing import Dict, Any

V2_THEMES = {
    "obsidian_dark": {
        "name": "Oscuro Obsidiana",
        "bg_app": "#1e1e24",
        "bg_sidebar": "#16161a",
        "bg_editor": "#24242e",
        "bg_card": "#2a2a36",
        "text_main": "#e1e1e6",
        "text_secondary": "#a0a0b2",
        "border": "#323242",
        "accent": "#7c5cbf",
        "accent_hover": "#9370db",
        "corkboard_bg": "#201c18",
        "toolbar_bg": "#1a1a20",
        "highlight": "#4a3b69"
    },
    "macos_light": {
        "name": "macOS Claro Minimalista",
        "bg_app": "#f5f5f7",
        "bg_sidebar": "#ececf0",
        "bg_editor": "#ffffff",
        "bg_card": "#ffffff",
        "text_main": "#1d1d1f",
        "text_secondary": "#6e6e73",
        "border": "#d2d2d7",
        "accent": "#0071e3",
        "accent_hover": "#0077ed",
        "corkboard_bg": "#d9cfbe",
        "toolbar_bg": "#f0f0f2",
        "highlight": "#b3d7ff"
    },
    "nordic_frost": {
        "name": "Nordic Frost (Azul Ártico)",
        "bg_app": "#2e3440",
        "bg_sidebar": "#242933",
        "bg_editor": "#3b4252",
        "bg_card": "#3b4252",
        "text_main": "#eceff4",
        "text_secondary": "#d8dee9",
        "border": "#4c566a",
        "accent": "#88c0d0",
        "accent_hover": "#81a1c1",
        "corkboard_bg": "#212630",
        "toolbar_bg": "#272c36",
        "highlight": "#434c5e"
    },
    "catppuccin_mocha": {
        "name": "Catppuccin Mocha",
        "bg_app": "#1e1e2e",
        "bg_sidebar": "#181825",
        "bg_editor": "#24273a",
        "bg_card": "#24273a",
        "text_main": "#cdd6f4",
        "text_secondary": "#a6adc8",
        "border": "#45475a",
        "accent": "#cba6f7",
        "accent_hover": "#b4befe",
        "corkboard_bg": "#14141e",
        "toolbar_bg": "#181825",
        "highlight": "#585b70"
    },
    "sepia_classic": {
        "name": "Sepia Pergamino",
        "bg_app": "#f4ecd8",
        "bg_sidebar": "#eadeca",
        "bg_editor": "#fdf6e2",
        "bg_card": "#fbf0d9",
        "text_main": "#433422",
        "text_secondary": "#7f6a52",
        "border": "#d8c7ad",
        "accent": "#b5651d",
        "accent_hover": "#c97525",
        "corkboard_bg": "#c8b496",
        "toolbar_bg": "#eee2cc",
        "highlight": "#e2cca6"
    },
    "solarized_dark": {
        "name": "Solarizado Oscuro",
        "bg_app": "#002b36",
        "bg_sidebar": "#00212b",
        "bg_editor": "#073642",
        "bg_card": "#073642",
        "text_main": "#839496",
        "text_secondary": "#586e75",
        "border": "#0e4a59",
        "accent": "#268bd2",
        "accent_hover": "#2aa198",
        "corkboard_bg": "#021c22",
        "toolbar_bg": "#00212b",
        "highlight": "#0a4554"
    },
    "solarized_light": {
        "name": "Solarizado Claro",
        "bg_app": "#fdf6e3",
        "bg_sidebar": "#eee8d5",
        "bg_editor": "#ffffff",
        "bg_card": "#fdf6e3",
        "text_main": "#657b83",
        "text_secondary": "#93a1a1",
        "border": "#d5cbb6",
        "accent": "#268bd2",
        "accent_hover": "#2aa198",
        "corkboard_bg": "#dfd6bf",
        "toolbar_bg": "#eee8d5",
        "highlight": "#eee8d5"
    },
    "high_contrast_dark": {
        "name": "Alto Contraste Accesibilidad",
        "bg_app": "#000000",
        "bg_sidebar": "#0a0a0a",
        "bg_editor": "#121212",
        "bg_card": "#1a1a1a",
        "text_main": "#ffffff",
        "text_secondary": "#cccccc",
        "border": "#00ffff",
        "accent": "#00ffff",
        "accent_hover": "#33ffff",
        "corkboard_bg": "#050505",
        "toolbar_bg": "#000000",
        "highlight": "#005577"
    },
    "carbon_dark": {
        "name": "Carbon Dark (Grafito)",
        "bg_app": "#18191a",
        "bg_sidebar": "#1f2022",
        "bg_editor": "#141517",
        "bg_card": "#25272a",
        "text_main": "#e4e6eb",
        "text_secondary": "#b0b3b8",
        "border": "#2e3033",
        "accent": "#3b82f6",
        "accent_hover": "#60a5fa",
        "corkboard_bg": "#1c1d1f",
        "toolbar_bg": "#202124",
        "highlight": "#2d3748"
    },
    "scrivener_classic": {
        "name": "Scrivener 3 Clásico",
        "bg_app": "#eae8e1",
        "bg_sidebar": "#ded9cd",
        "bg_editor": "#fbfbf9",
        "bg_card": "#ffffff",
        "text_main": "#2b2b2b",
        "text_secondary": "#656565",
        "border": "#c5bfae",
        "accent": "#526f84",
        "accent_hover": "#658ba6",
        "corkboard_bg": "#c9bea9",
        "toolbar_bg": "#e2ded5",
        "highlight": "#d0dbe5"
    }
}


def get_v2_stylesheet(theme_key: str = "obsidian_dark") -> str:
    """Genera la hoja de estilos QSS completa para ESCRITORIO v2.0."""
    t = V2_THEMES.get(theme_key, V2_THEMES["obsidian_dark"])

    return f"""
    /* Ventana Principal y Elementos Globales */
    QMainWindow, QDialog {{
        background-color: {t['bg_app']};
        color: {t['text_main']};
        font-family: 'Segoe UI Variable Display', 'Segoe UI', sans-serif;
        font-size: 13px;
    }}

    QWidget {{
        color: {t['text_main']};
    }}

    /* Barra de Menú Estilo macOS / Win11 */
    QMenuBar {{
        background-color: {t['toolbar_bg']};
        color: {t['text_main']};
        border-bottom: 1px solid {t['border']};
        padding: 4px 6px;
        font-weight: 500;
    }}
    QMenuBar::item {{
        background: transparent;
        padding: 4px 10px;
        border-radius: 4px;
    }}
    QMenuBar::item:selected {{
        background-color: {t['border']};
    }}

    QMenu {{
        background-color: {t['bg_card']};
        color: {t['text_main']};
        border: 1px solid {t['border']};
        border-radius: 6px;
        padding: 4px;
    }}
    QMenu::item {{
        padding: 6px 24px;
        border-radius: 4px;
    }}
    QMenu::item:selected {{
        background-color: {t['accent']};
        color: #ffffff;
    }}
    QMenu::separator {{
        height: 1px;
        background-color: {t['border']};
        margin: 4px 8px;
    }}

    /* Barra de Herramientas Premium */
    QToolBar {{
        background-color: {t['toolbar_bg']};
        border-bottom: 1px solid {t['border']};
        spacing: 6px;
        padding: 4px 8px;
    }}
    QToolButton {{
        background-color: transparent;
        color: {t['text_main']};
        border: 1px solid transparent;
        border-radius: 5px;
        padding: 4px 8px;
        font-weight: 500;
    }}
    QToolButton:hover {{
        background-color: {t['border']};
        border: 1px solid {t['border']};
    }}
    QToolButton:pressed, QToolButton:checked {{
        background-color: {t['accent']};
        color: #ffffff;
    }}

    /* Archivador (Binder) y Árboles */
    QTreeWidget, QTreeView {{
        background-color: {t['bg_sidebar']};
        color: {t['text_main']};
        border: none;
        border-right: 1px solid {t['border']};
        padding: 6px;
    }}
    QTreeWidget::item {{
        height: 28px;
        border-radius: 4px;
        padding-left: 4px;
    }}
    QTreeWidget::item:hover {{
        background-color: {t['border']};
    }}
    QTreeWidget::item:selected {{
        background-color: {t['accent']};
        color: #ffffff;
    }}

    /* Editor de Texto */
    QTextEdit, QPlainTextEdit {{
        background-color: {t['bg_editor']};
        color: {t['text_main']};
        border: none;
        selection-background-color: {t['highlight']};
        line-height: 1.6;
    }}

    /* Pizarra de Corcho */
    QScrollArea#CorkboardScrollArea {{
        background-color: {t['corkboard_bg']};
        border: none;
    }}
    QWidget#CorkboardCanvas {{
        background-color: {t['corkboard_bg']};
    }}

    /* Tarjetas de Índice (Index Cards) */
    QFrame.IndexCard {{
        background-color: {t['bg_card']};
        border: 1px solid {t['border']};
        border-radius: 8px;
    }}
    QFrame.IndexCard:hover {{
        border: 1px solid {t['accent']};
    }}

    /* Botones y Controles */
    QPushButton {{
        background-color: {t['bg_card']};
        color: {t['text_main']};
        border: 1px solid {t['border']};
        border-radius: 6px;
        padding: 5px 12px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: {t['border']};
        border-color: {t['accent']};
    }}
    QPushButton:pressed {{
        background-color: {t['accent']};
        color: #ffffff;
    }}
    QPushButton#PrimaryButton {{
        background-color: {t['accent']};
        color: #ffffff;
        border: 1px solid {t['accent']};
    }}
    QPushButton#PrimaryButton:hover {{
        background-color: {t['accent_hover']};
    }}

    /* Control Segmentado (Segmented Button Group) */
    QFrame#SegmentedControl {{
        background-color: {t['border']};
        border-radius: 6px;
        padding: 2px;
    }}
    QPushButton.SegmentBtn {{
        background-color: transparent;
        border: none;
        border-radius: 4px;
        padding: 4px 10px;
        font-size: 12px;
        font-weight: bold;
    }}
    QPushButton.SegmentBtn:checked {{
        background-color: {t['bg_card']};
        color: {t['accent']};
    }}

    /* Desplegables QComboBox */
    QComboBox {{
        background-color: {t['bg_card']};
        color: {t['text_main']};
        border: 1px solid {t['border']};
        border-radius: 5px;
        padding: 3px 10px;
        min-height: 24px;
        font-weight: 500;
    }}
    QComboBox:hover {{
        border-color: {t['accent']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 18px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {t['bg_card']};
        color: {t['text_main']};
        border: 1px solid {t['border']};
        selection-background-color: {t['accent']};
        selection-color: #ffffff;
        padding: 4px;
    }}

    /* Entradas de Texto y Buscadores */
    QLineEdit {{
        background-color: {t['bg_editor']};
        color: {t['text_main']};
        border: 1px solid {t['border']};
        border-radius: 6px;
        padding: 4px 8px;
    }}
    QLineEdit:focus {{
        border: 1px solid {t['accent']};
    }}

    /* Listas y Tablas */
    QListWidget, QTableWidget {{
        background-color: {t['bg_sidebar']};
        color: {t['text_main']};
        border: 1px solid {t['border']};
        border-radius: 5px;
    }}
    QListWidget::item:selected, QTableWidget::item:selected {{
        background-color: {t['accent']};
        color: #ffffff;
    }}
    QHeaderView::section {{
        background-color: {t['toolbar_bg']};
        color: {t['text_secondary']};
        border: none;
        border-bottom: 1px solid {t['border']};
        border-right: 1px solid {t['border']};
        padding: 4px 8px;
        font-weight: bold;
    }}

    /* Pestañas */
    QTabWidget::pane {{
        border: 1px solid {t['border']};
        background-color: {t['bg_card']};
    }}
    QTabBar::tab {{
        background-color: {t['bg_app']};
        color: {t['text_secondary']};
        border: 1px solid {t['border']};
        border-bottom: none;
        padding: 6px 14px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }}
    QTabBar::tab:selected {{
        background-color: {t['bg_card']};
        color: {t['text_main']};
        font-weight: bold;
    }}

    /* Barra de Estado */
    QStatusBar {{
        background-color: {t['toolbar_bg']};
        color: {t['text_secondary']};
        border-top: 1px solid {t['border']};
    }}

    /* Divisores (QSplitter) */
    QSplitter::handle {{
        background-color: {t['border']};
    }}
    QSplitter::handle:horizontal {{
        width: 1px;
    }}
    QSplitter::handle:vertical {{
        height: 1px;
    }}

    /* Barras del Editor de Texto (Header, Formato y Footer) */
    QFrame#EditorHeaderBar {{
        background-color: {t['toolbar_bg']};
        border-bottom: 1px solid {t['border']};
        padding: 2px 8px;
    }}
    QToolBar#EditorFormatBar {{
        background-color: {t['toolbar_bg']};
        border-bottom: 1px solid {t['border']};
        padding: 3px 6px;
        spacing: 4px;
    }}
    QFrame#EditorFooterBar {{
        background-color: {t['toolbar_bg']};
        border-top: 1px solid {t['border']};
        padding: 2px 10px;
    }}

    /* Botones de acción del Editor y Formato */
    QToolButton.EditorActionBtn, QToolButton.FormatToolButton {{
        background-color: transparent;
        color: {t['text_main']};
        border: 1px solid transparent;
        border-radius: 4px;
        padding: 1px;
        min-width: 28px;
        min-height: 28px;
        font-size: 12px;
        font-weight: bold;
    }}
    QToolButton.EditorActionBtn:hover, QToolButton.FormatToolButton:hover {{
        background-color: {t['border']};
        border: 1px solid {t['border']};
    }}
    QToolButton.EditorActionBtn:checked, QToolButton.FormatToolButton:checked,
    QToolButton.EditorActionBtn:pressed, QToolButton.FormatToolButton:pressed {{
        background-color: {t['accent']};
        color: #ffffff;
        border: 1px solid {t['accent']};
    }}

    /* Tarjetas y Paneles de Estadísticas */
    QFrame.StatCard {{
        background-color: {t['bg_card']};
        border: 1px solid {t['border']};
        border-radius: 8px;
        padding: 12px;
    }}
    QLabel.StatValue {{
        font-size: 18px;
        font-weight: bold;
        color: {t['accent']};
    }}
    QLabel.StatLabel {{
        font-size: 11px;
        color: {t['text_secondary']};
    }}
    """
