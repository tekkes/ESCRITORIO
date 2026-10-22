"""
EditorWidget Module
Editor principal de texto enriquecido, reglas, formato, folios físicos, foco y estilos semánticos.
"""

from .editor_widget import EditorWidget
from .format_toolbar import FormatToolbar, TextFormatState
from .ruler_bar import RulerBar, RulerState, TabStop
from .page_view import PageViewEngine, EditorViewMode, PageFormat, PageDimensions, FolioPage
from .linguistic_focus import LinguisticFocusEngine, LinguisticCategory, HighlightSpan
from .focus_mode import FocusModeEngine, FocusScope
from .invisibles import InvisiblesEngine
from .scrivener_links import ScrivenerLinksEngine, ScrivenerLinkMatch
from .table_manager import TableManager, EditableTable, TableRow, TableCell

__all__ = [
    "EditorWidget",
    "FormatToolbar",
    "TextFormatState",
    "RulerBar",
    "RulerState",
    "TabStop",
    "PageViewEngine",
    "EditorViewMode",
    "PageFormat",
    "PageDimensions",
    "FolioPage",
    "LinguisticFocusEngine",
    "LinguisticCategory",
    "HighlightSpan",
    "FocusModeEngine",
    "FocusScope",
    "InvisiblesEngine",
    "ScrivenerLinksEngine",
    "ScrivenerLinkMatch",
    "TableManager",
    "EditableTable",
    "TableRow",
    "TableCell",
]
