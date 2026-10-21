"""
Escritorio UI Module
Componentes de presentación visual: Ventana principal, Binder, Editor RTF, Split View,
Corcho (Corkboard), Esquematizador (Outliner), Inspector y Modo Composición.
"""

from .main_window import MainWindow
from .binder import BinderView
from .editor_rtf import RTFEditorView
from .split_view import SplitContainer
from .corkboard import CorkboardView
from .outliner import OutlinerView
from .inspector import InspectorView
from .composition_mode import CompositionMode

__all__ = [
    "MainWindow",
    "BinderView",
    "RTFEditorView",
    "SplitContainer",
    "CorkboardView",
    "OutlinerView",
    "InspectorView",
    "CompositionMode",
]
