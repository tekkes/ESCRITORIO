"""
Binder View para Escritorio
Visualización jerárquica del árbol de documentos, carpetas del sistema (Manuscrito, Investigación, Papelera)
y gestión de estados, etiquetas de color e iconos vectoriales.
"""

from typing import Optional, Callable, Dict, Any, List
from ..core.project import BinderItem, EscritorioProject

class BinderView:
    """Controlador y lógica del árbol del Binder (panel lateral izquierdo)."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.project = project
        self.selected_uuid: Optional[str] = None
        self.on_selection_changed: Optional[Callable[[str], None]] = None
        self.expanded_nodes: set = set()

    def set_project(self, project: EscritorioProject):
        self.project = project
        self.selected_uuid = None
        if project and project.root_items:
            # Seleccionar por defecto el primer elemento del borrador
            draft = project.root_items[0]
            if draft.children:
                self.selected_uuid = draft.children[0].uuid
            else:
                self.selected_uuid = draft.uuid

    def select_item(self, uuid: str):
        """Selecciona un nodo del binder y notifica a las vistas conectadas."""
        self.selected_uuid = uuid
        if self.on_selection_changed:
            self.on_selection_changed(uuid)

    def toggle_expand(self, uuid: str):
        """Alterna el estado expandido/colapsado de una carpeta."""
        if uuid in self.expanded_nodes:
            self.expanded_nodes.remove(uuid)
        else:
            self.expanded_nodes.add(uuid)

    def get_render_tree(self) -> List[Dict[str, Any]]:
        """Genera la estructura procesada para el renderizado del árbol en la interfaz."""
        if not self.project:
            return []

        def build_node(item: BinderItem, depth: int) -> Dict[str, Any]:
            label_color = "transparent"
            if item.data.label_id != -1 and self.project:
                lbl = self.project.project_data.get("labels", {}).get(item.data.label_id)
                if lbl:
                    label_color = lbl.color_rgba

            status_text = ""
            if item.data.status_id != -1 and self.project:
                st = self.project.project_data.get("statuses", {}).get(item.data.status_id)
                if st:
                    status_text = st.name

            return {
                "uuid": item.uuid,
                "title": item.title,
                "type": item.item_type,
                "depth": depth,
                "is_selected": (item.uuid == self.selected_uuid),
                "is_expanded": (item.uuid in self.expanded_nodes),
                "has_children": len(item.data.children) > 0,
                "word_count": item.get_word_count() if item.item_type == "Text" else 0,
                "label_color": label_color,
                "status": status_text,
                "children": [build_node(child, depth + 1) for child in item.children]
            }

        return [build_node(root, 0) for root in self.project.root_items]
