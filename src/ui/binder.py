"""
Binder View para Escritorio
Compatibilidad e integración del Cuaderno con BinderWidget, árbol jerárquico multinivel,
capacidades duales de nodos, colecciones y personalización cromática.
"""

from typing import Optional, Callable, Dict, Any, List
from ..core.project import BinderItem, EscritorioProject
from .BinderWidget.binder_widget import BinderWidget
from .BinderWidget.binder_tree_view import BinderTreeView, LabelColorMode
from .BinderWidget.icon_library import IconLibrary
from .BinderWidget.collections_bar import CollectionsManager

class BinderView(BinderWidget):
    """
    Controlador y lógica del árbol del Binder (panel lateral izquierdo).
    Hereda todas las capacidades estructurales, narrativas y de colecciones de BinderWidget.
    """

    def __init__(self, project: Optional[EscritorioProject] = None):
        super().__init__(project)
        self.on_selection_changed: Optional[Callable[[str], None]] = None

    def _on_tree_selection_changed(self, uuids: List[str]):
        super()._on_tree_selection_changed(uuids)
        if uuids and self.on_selection_changed:
            self.on_selection_changed(uuids[0])

    def select_item(self, uuid: str):
        self.tree_view.select_item(uuid)

    def toggle_expand(self, uuid: str):
        self.tree_view.toggle_expand(uuid)

    @property
    def expanded_nodes(self) -> set:
        return self.tree_view.expanded_nodes

    def get_render_tree(self) -> List[Dict[str, Any]]:
        return self.tree_view.get_render_tree()
