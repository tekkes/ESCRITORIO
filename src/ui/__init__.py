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

from .corkboard import CorkboardView, CorkboardCard
from .CorkboardWidget import (
    CorkboardWidget,
    CorkboardMode,
    IndexCard,
    CardAspectRatio,
    LabelColorStyle,
    CorkboardGrid,
    CorkboardFreeform,
    CorkboardSwimlanes,
    SwimlaneColumn,
    CorkboardFooterBar
)
from .outliner import OutlinerView
from .OutlinerWidget import (
    OutlinerWidget,
    OutlinerColumn,
    ColumnSelector,
    ColumnType,
    StandardColumnId,
    calculate_progress_color,
    OutlinerRow,
    OutlinerExporter
)
from .inspector import InspectorView
from .InspectorWidget import (
    InspectorWidget,
    InspectorTabId,
    TabNotesSynopsis,
    TabBookmarks,
    BookmarkScope,
    BookmarkItem,
    TabMetadata,
    CustomFieldType,
    CustomFieldDefinition,
    ProjectKeywordsHUD,
    KeywordDefinition,
    MyersDiffEngine,
    DiffOp,
    DiffGranularity,
    DiffChunk,
    TabSnapshots,
    SnapshotItem,
    TabCommentsFootnotes,
    CommentItem
)
from .CompositionMode import (
    CompositionMode,
    CompositionPaperSettings,
    PaperPosition,
    BottomControlBar,
    GoToItem
)

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
    "CorkboardCard",
    "CorkboardWidget",
    "CorkboardMode",
    "IndexCard",
    "CardAspectRatio",
    "LabelColorStyle",
    "CorkboardGrid",
    "CorkboardFreeform",
    "CorkboardSwimlanes",
    "SwimlaneColumn",
    "CorkboardFooterBar",
    "OutlinerView",
    "OutlinerWidget",
    "OutlinerColumn",
    "ColumnSelector",
    "ColumnType",
    "StandardColumnId",
    "calculate_progress_color",
    "OutlinerRow",
    "OutlinerExporter",
    "InspectorView",
    "InspectorWidget",
    "InspectorTabId",
    "TabNotesSynopsis",
    "TabBookmarks",
    "BookmarkScope",
    "BookmarkItem",
    "TabMetadata",
    "CustomFieldType",
    "CustomFieldDefinition",
    "ProjectKeywordsHUD",
    "KeywordDefinition",
    "MyersDiffEngine",
    "DiffOp",
    "DiffGranularity",
    "DiffChunk",
    "TabSnapshots",
    "SnapshotItem",
    "TabCommentsFootnotes",
    "CommentItem",
    "CompositionMode",
]
