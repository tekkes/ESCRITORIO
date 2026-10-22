"""
BinderWidget Package para Escritorio
Componente completo del Cuaderno (Binder) con árbol multinivel,
capacidades duales de nodos, comandos narrativos con Undo/Redo,
biblioteca de más de 80 micro-iconos vectoriales y Colecciones.
"""

from .binder_widget import BinderWidget
from .binder_tree_view import BinderTreeView, LabelColorMode
from .collections_bar import CollectionsManager
from .icon_library import IconLibrary
from .narrative_commands import (
    UndoStack,
    BinderCommand,
    MoveItemsCommand,
    GroupItemsCommand,
    UngroupFolderCommand,
    SplitDocumentCommand,
    SplitDocumentWithTitleCommand,
    MergeDocumentsCommand,
    DuplicateItemCommand,
    TrashItemCommand,
    ChangeIconCommand
)

__all__ = [
    "BinderWidget",
    "BinderTreeView",
    "LabelColorMode",
    "CollectionsManager",
    "IconLibrary",
    "UndoStack",
    "BinderCommand",
    "MoveItemsCommand",
    "GroupItemsCommand",
    "UngroupFolderCommand",
    "SplitDocumentCommand",
    "SplitDocumentWithTitleCommand",
    "MergeDocumentsCommand",
    "DuplicateItemCommand",
    "TrashItemCommand",
    "ChangeIconCommand",
]
