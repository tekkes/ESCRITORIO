"""
Escritorio UI Module
Componentes de presentación visual: Ventana principal, BinderWidget, BinderView, Editor RTF, Split View,
Corcho (Corkboard), Esquematizador (Outliner), Inspector, Modo Composición y Colecciones.
"""

from .main_window import MainWindow
from .binder import BinderView
from .BinderWidget import (
    BinderWidget,
    BinderTreeView,
    LabelColorMode,
    CollectionsManager,
    IconLibrary,
    UndoStack
)
from .EditorWidget import (
    EditorWidget,
    FormatToolbar,
    TextFormatState,
    RulerBar,
    PageViewEngine,
    EditorViewMode,
    LinguisticFocusEngine,
    LinguisticCategory,
    FocusModeEngine,
    FocusScope,
    InvisiblesEngine,
    ScrivenerLinksEngine,
    TableManager
)
from .editor_rtf import RTFEditorView
from .split_view import SplitContainer
from .corkboard import CorkboardView
from .outliner import OutlinerView
from .inspector import InspectorView
from .composition_mode import CompositionMode

__all__ = [
    "MainWindow",
    "BinderView",
    "BinderWidget",
    "BinderTreeView",
    "LabelColorMode",
    "CollectionsManager",
    "IconLibrary",
    "UndoStack",
    "EditorWidget",
    "FormatToolbar",
    "TextFormatState",
    "RulerBar",
    "PageViewEngine",
    "EditorViewMode",
    "LinguisticFocusEngine",
    "LinguisticCategory",
    "FocusModeEngine",
    "FocusScope",
    "InvisiblesEngine",
    "ScrivenerLinksEngine",
    "TableManager",
    "RTFEditorView",
    "SplitContainer",
    "CorkboardView",
    "OutlinerView",
    "InspectorView",
    "CompositionMode",
]
