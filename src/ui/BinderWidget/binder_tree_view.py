"""
BinderTreeView para Escritorio
Árbol jerárquico multinivel con carpetas raíz especiales (Manuscrito, Investigación, Papelera, Plantillas),
capacidad dual de nodos (carpetas con texto propio y documentos con hijos),
modos de visualización de color de etiqueta y biblioteca de micro-iconos vectoriales.
"""

from enum import Enum
from typing import Optional, Callable, Dict, Any, List, Set, Union
from ...core.project import EscritorioProject, BinderItem
from .icon_library import IconLibrary

class LabelColorMode(Enum):
    """Modos de visualización del color de etiqueta en el Binder."""
    NONE = "none"
    DOT_RIGHT = "dot_right"        # Punto cromático circular a la derecha de la fila
    ICON_TINT = "icon_tint"        # Tinte de color sobre el icono del nodo
    ROW_HIGHLIGHT = "row_highlight"# Resaltado suave de fondo en toda la fila


class BinderTreeView:
    """
    Vista y controlador del árbol jerárquico del Binder.
    Gestiona la estructura arbórea, selección simple y múltiple, estados de expansión,
    y opciones cromáticas de visualización.
    """

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.project = project
        self.selected_uuids: List[str] = []
        self.expanded_nodes: Set[str] = set()
        self.label_color_mode: LabelColorMode = LabelColorMode.DOT_RIGHT

        # Callbacks para notificación a la UI
        self.on_selection_changed: Optional[Callable[[List[str]], None]] = None
        self.on_item_activated: Optional[Callable[[str], None]] = None

        if project:
            self.set_project(project)

    def set_project(self, project: EscritorioProject):
        self.project = project
        self.selected_uuids.clear()
        self.expanded_nodes.clear()

        if project and project.root_items:
            # Expandir por defecto el Manuscrito y la Investigación
            for root in project.root_items:
                if root.item_type in ("DraftFolder", "ResearchFolder"):
                    self.expanded_nodes.add(root.uuid)

            # Seleccionar por defecto el primer elemento del borrador
            draft = project.get_draft_folder()
            if draft:
                if draft.children:
                    self.select_item(draft.children[0].uuid)
                else:
                    self.select_item(draft.uuid)

    @property
    def selected_uuid(self) -> Optional[str]:
        """Devuelve el primer ítem seleccionado para compatibilidad con vistas de un solo documento."""
        return self.selected_uuids[0] if self.selected_uuids else None

    def select_item(self, uuid: str, extend: bool = False):
        """Selecciona un elemento (soporta selección múltiple con extend=True)."""
        if extend:
            if uuid not in self.selected_uuids:
                self.selected_uuids.append(uuid)
        else:
            self.selected_uuids = [uuid]

        if self.on_selection_changed:
            self.on_selection_changed(self.selected_uuids)

    def select_multiple(self, uuids: List[str]):
        """Establece una selección múltiple de elementos."""
        self.selected_uuids = list(uuids)
        if self.on_selection_changed:
            self.on_selection_changed(self.selected_uuids)

    def toggle_expand(self, uuid: str):
        """Alterna el estado expandido/colapsado de un nodo contenedor."""
        if uuid in self.expanded_nodes:
            self.expanded_nodes.remove(uuid)
        else:
            self.expanded_nodes.add(uuid)

    def expand_all(self):
        """Expande todos los nodos contenedores del proyecto."""
        if not self.project:
            return
        for item in self.project.items_by_uuid.values():
            if item.data.children:
                self.expanded_nodes.add(item.uuid)

    def collapse_all(self):
        """Colapsa todos los nodos excepto las raíces principales."""
        self.expanded_nodes.clear()
        if self.project:
            for root in self.project.root_items:
                self.expanded_nodes.add(root.uuid)

    def set_label_color_mode(self, mode: Union[LabelColorMode, str]):
        """Configura cómo se renderiza el color de etiqueta en las filas del Binder."""
        if isinstance(mode, str):
            self.label_color_mode = LabelColorMode(mode.lower())
        else:
            self.label_color_mode = mode

    def get_node_icon_svg(self, item: BinderItem) -> str:
        """Determina y resuelve el icono vectorial SVG para un nodo del Binder."""
        icon_name = item.data.icon_file_name or ""

        # Si tiene icono personalizado asignado
        if icon_name and icon_name in IconLibrary.ICONS:
            return IconLibrary.get_icon(icon_name)

        # Si es un emoji o texto corto
        if icon_name.startswith("emoji:"):
            return IconLibrary.generate_emoji_svg(icon_name[6:])

        # Iconos por defecto según tipo de elemento
        t = item.item_type
        if t == "DraftFolder":
            return IconLibrary.get_icon("folder_draft")
        elif t == "ResearchFolder":
            return IconLibrary.get_icon("folder_research")
        elif t == "TrashFolder":
            return IconLibrary.get_icon("folder_trash")
        elif t == "TemplatesFolder":
            return IconLibrary.get_icon("folder_templates")
        elif t == "Folder":
            return IconLibrary.get_icon("folder_standard")
        elif t == "Text":
            if item.data.children:
                # Documento dual con subdocumentos hijos
                return IconLibrary.get_icon("doc_chapter")
            return IconLibrary.get_icon("doc_text")
        elif t == "PDF":
            return IconLibrary.get_icon("doc_sheet")
        elif t == "Image":
            return IconLibrary.get_icon("obj_camera")
        elif t == "Media":
            return IconLibrary.get_icon("folder_audio")
        elif t == "WebArchive":
            return IconLibrary.get_icon("folder_web")
        else:
            return IconLibrary.get_icon("doc_text")

    def get_render_tree(self) -> List[Dict[str, Any]]:
        """
        Genera la estructura de datos jerárquica lista para el renderizado visual
        en la interfaz (con profundidad, micro-iconos, capacidad dual y opciones de color).
        """
        if not self.project:
            return []

        def build_node_dict(item: BinderItem, depth: int) -> Dict[str, Any]:
            # Resolver color de etiqueta
            label_rgba = "transparent"
            label_hex = ""
            if item.data.label_id != -1 and self.project:
                lbl = self.project.project_data.get("labels", {}).get(item.data.label_id)
                if lbl:
                    label_rgba = lbl.color_rgba
                    # Convertir 'r g b a' a hex si es posible
                    try:
                        parts = [float(x) for x in lbl.color_rgba.split()]
                        if len(parts) >= 3:
                            r, g, b = int(parts[0] * 255), int(parts[1] * 255), int(parts[2] * 255)
                            label_hex = f"#{r:02x}{g:02x}{b:02x}"
                    except Exception:
                        pass

            # Resolver texto de estado
            status_name = ""
            if item.data.status_id != -1 and self.project:
                st = self.project.project_data.get("statuses", {}).get(item.data.status_id)
                if st:
                    status_name = st.name

            # Capacidad dual: texto propio y recuento de palabras en cualquier nodo
            has_text_content = bool(item.read_content_rtf().strip())
            word_count = item.get_word_count()

            # Renderizado de color según el modo activo
            row_bg_tint = "transparent"
            icon_tint = "none"
            show_dot = False

            if label_hex:
                if self.label_color_mode == LabelColorMode.DOT_RIGHT:
                    show_dot = True
                elif self.label_color_mode == LabelColorMode.ICON_TINT:
                    icon_tint = label_hex
                elif self.label_color_mode == LabelColorMode.ROW_HIGHLIGHT:
                    row_bg_tint = f"{label_hex}22"  # 13% opacidad

            return {
                "uuid": item.uuid,
                "title": item.title,
                "type": item.item_type,
                "depth": depth,
                "is_selected": (item.uuid in self.selected_uuids),
                "is_expanded": (item.uuid in self.expanded_nodes),
                "has_children": len(item.data.children) > 0,
                "has_text": has_text_content,
                "word_count": word_count,
                "label_id": item.data.label_id,
                "label_rgba": label_rgba,
                "label_hex": label_hex,
                "status_id": item.data.status_id,
                "status_name": status_name,
                "include_in_compile": item.data.include_in_compile,
                "section_type": item.data.section_type,
                "icon_svg": self.get_node_icon_svg(item),
                "show_label_dot": show_dot,
                "icon_tint": icon_tint,
                "row_bg_tint": row_bg_tint,
                "children": [build_node_dict(child, depth + 1) for child in item.children]
            }

        return [build_node_dict(root, 0) for root in self.project.root_items]
