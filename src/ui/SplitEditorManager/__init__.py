"""
Paquete SplitEditorManager de Escritorio.
"""

from .editor_pane import EditorPane, PaneContentType
from .split_editor_manager import SplitEditorManager, SplitLayoutMode
from .quick_reference import QuickReferenceWindow, QuickReferenceManager

__all__ = [
    "EditorPane",
    "PaneContentType",
    "SplitEditorManager",
    "SplitLayoutMode",
    "QuickReferenceWindow",
    "QuickReferenceManager"
]
