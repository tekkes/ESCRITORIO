"""
ESCRITORIO v2.0 - Theme Engine & Visual Styling
Motor de diseño y estilos inspirado en la estética limpia y profesional de Scrivener 3 para macOS,
adaptado a Windows 11 con High DPI y soporte para temas en caliente.
"""

from typing import Dict, Any

V2_THEMES = {
    "macos_light": {
        "name": "macOS Claro",
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
    "sepia_classic": {
        "name": "Sepia Clásico",
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
        "bg_sidebar": "#073642",
        "bg_editor": "#00212b",
        "bg_card": "#073642",
        "text_main": "#839496",
        "text_secondary": "#586e75",
        "border": "#0e4a59",
        "accent": "#268bd2",
        "accent_hover": "#2aa198",
        "corkboard_bg": "#021c22",
        "toolbar_bg": "#073642",
        "highlight": "#073642"
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
    QToolButton:pressed {{
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
    """
