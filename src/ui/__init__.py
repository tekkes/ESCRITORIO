"""
Escritorio UI Module
Componentes de presentación visual: Ventana principal, BinderWidget, Editor RTF,
ScriveningsEngine, SplitEditorManager, ScriptwritingMode, ResearchViewers,
Corcho (Corkboard), Esquematizador (Outliner), Inspector, Modo Composición y Colecciones.
"""

from .main_window import MainWindow, CentralViewMode
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
from .split_view import SplitContainer, SplitOrientation

from .ScriveningsEngine import (
    ScriveningsEngine,
    ScriveningsSection,
    DividerStyle,
    ScriveningsDivider
)
from .SplitEditorManager import (
    SplitEditorManager,
    SplitLayoutMode,
    EditorPane,
    PaneContentType,
    QuickReferenceManager,
    QuickReferenceWindow
)
from .ScriptwritingMode import (
    ScriptwritingEngine,
    ScriptFormat,
    ScriptElementType,
    ElementStyleRule,
    SCREENPLAY_RULES,
    ScriptAutocomplete
)
from .ResearchViewers import (
    PDFViewer,
    PDFSearchResult,
    ImageViewer,
    TranscriptionPlayer,
    WebArchiveViewer,
    ResearchViewerRouter
)

from .corkboard import CorkboardView
from .outliner import OutlinerView
from .inspector import InspectorView
from .composition_mode import CompositionMode

__all__ = [
    "MainWindow",
    "CentralViewMode",
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
    "SplitOrientation",
    "ScriveningsEngine",
    "ScriveningsSection",
    "DividerStyle",
    "ScriveningsDivider",
    "SplitEditorManager",
    "SplitLayoutMode",
    "EditorPane",
    "PaneContentType",
    "QuickReferenceManager",
    "QuickReferenceWindow",
    "ScriptwritingEngine",
    "ScriptFormat",
    "ScriptElementType",
    "ElementStyleRule",
    "SCREENPLAY_RULES",
    "ScriptAutocomplete",
    "PDFViewer",
    "PDFSearchResult",
    "ImageViewer",
    "TranscriptionPlayer",
    "WebArchiveViewer",
    "ResearchViewerRouter",
    "CorkboardView",
    "OutlinerView",
    "InspectorView",
    "CompositionMode",
]
