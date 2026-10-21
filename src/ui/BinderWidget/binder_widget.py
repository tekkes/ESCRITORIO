"""
BinderWidget para Escritorio
Componente integral del Cuaderno de Scrivener que combina:
- Pestañas compactas de Colecciones (Estándar y Búsqueda en tiempo real).
- Árbol jerárquico multinivel (BinderTreeView) con soporte dual de nodos.
- Comandos estructurales de narrativa con pila Deshacer/Rehacer (Ctrl+Z / Ctrl+Y).
- Catálogo visual de más de 80 micro-iconos vectoriales y emojis.
"""

from typing import Optional, List, Dict, Any, Callable, Union
from ...core.project import EscritorioProject, BinderItem
from .binder_tree_view import BinderTreeView, LabelColorMode
from .collections_bar import CollectionsManager
from .narrative_commands import (
    UndoStack,
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
from .icon_library import IconLibrary

class BinderWidget:
    """
    Controlador maestro del Cuaderno (Binder).
    Orquesta la vista en árbol, colecciones, operaciones de narrativa y comandos undo/redo.
    """

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.project = project
        self.tree_view = BinderTreeView(project)
        self.collections_mgr = CollectionsManager(project)
        self.undo_stack = UndoStack(max_depth=50)

        # Conectar cambios de colección con la vista
        self.collections_mgr.on_collection_changed = self._on_collection_tab_changed

        # Callback externo para selección de documentos
        self.on_document_selected: Optional[Callable[[str], None]] = None
        self.tree_view.on_selection_changed = self._on_tree_selection_changed

    def set_project(self, project: EscritorioProject):
        self.project = project
        self.tree_view.set_project(project)
        self.collections_mgr.set_project(project)
        self.undo_stack.clear()

    def _on_tree_selection_changed(self, uuids: List[str]):
        if uuids and self.on_document_selected:
            self.on_document_selected(uuids[0])

    def _on_collection_tab_changed(self, col):
        # Si se selecciona una colección, se notifica la selección del primer ítem
        if col:
            items = self.collections_mgr.get_items_for_collection(col)
            if items:
                self.tree_view.select_item(items[0].uuid)

    @property
    def selected_uuid(self) -> Optional[str]:
        return self.tree_view.selected_uuid

    @property
    def selected_uuids(self) -> List[str]:
        return self.tree_view.selected_uuids

    # =========================================================================
    # Operaciones Estructurales con Soporte Undo / Redo
    # =========================================================================

    def group_selection(self, folder_title: str = "Nueva Carpeta") -> bool:
        """Agrupa los ítems seleccionados en una nueva carpeta (Ctrl+G)."""
        if not self.project or not self.selected_uuids:
            return False
        cmd = GroupItemsCommand(self.project, self.selected_uuids, folder_title)
        ok = self.undo_stack.push_and_execute(cmd)
        if ok and cmd.created_folder_uuid:
            self.tree_view.expanded_nodes.add(cmd.created_folder_uuid)
            self.tree_view.select_item(cmd.created_folder_uuid)
        return ok

    def ungroup_selection(self) -> bool:
        """Desagrupa la carpeta seleccionada extrayendo sus hijos (Ctrl+Shift+G)."""
        if not self.project or not self.selected_uuid:
            return False
        item = self.project.get_item(self.selected_uuid)
        if not item or item.item_type in ("DraftFolder", "ResearchFolder", "TrashFolder"):
            return False
        cmd = UngroupFolderCommand(self.project, self.selected_uuid)
        return self.undo_stack.push_and_execute(cmd)

    def split_document(self, split_char_pos: int, new_title: str = "Continuación") -> bool:
        """Divide el documento seleccionado en dos (Ctrl+K)."""
        if not self.project or not self.selected_uuid:
            return False
        cmd = SplitDocumentCommand(self.project, self.selected_uuid, split_char_pos, new_title)
        ok = self.undo_stack.push_and_execute(cmd)
        if ok and cmd.created_item_uuid:
            self.tree_view.select_item(cmd.created_item_uuid)
        return ok

    def split_document_with_title(self, start_pos: int, end_pos: int) -> bool:
        """Divide usando la selección como título (Ctrl+Shift+K)."""
        if not self.project or not self.selected_uuid:
            return False
        cmd = SplitDocumentWithTitleCommand(self.project, self.selected_uuid, start_pos, end_pos)
        ok = self.undo_stack.push_and_execute(cmd)
        if ok and cmd.created_item_uuid:
            self.tree_view.select_item(cmd.created_item_uuid)
        return ok

    def merge_selection(self) -> bool:
        """Fusiona los documentos seleccionados en el primero (Ctrl+Shift+M)."""
        if not self.project or len(self.selected_uuids) < 2:
            return False
        cmd = MergeDocumentsCommand(self.project, self.selected_uuids)
        ok = self.undo_stack.push_and_execute(cmd)
        if ok:
            self.tree_view.select_item(self.selected_uuids[0])
        return ok

    def duplicate_selection(self) -> bool:
        """Duplica los documentos o carpetas seleccionados (Ctrl+D)."""
        if not self.project or not self.selected_uuid:
            return False
        cmd = DuplicateItemCommand(self.project, self.selected_uuid)
        ok = self.undo_stack.push_and_execute(cmd)
        if ok and cmd.created_duplicate_uuid:
            self.tree_view.select_item(cmd.created_duplicate_uuid)
        return ok

    def trash_selection(self) -> bool:
        """Envía los ítems seleccionados a la Papelera (Supr)."""
        if not self.project or not self.selected_uuids:
            return False
        cmd = TrashItemCommand(self.project, self.selected_uuids)
        ok = self.undo_stack.push_and_execute(cmd)
        if ok:
            # Seleccionar el borrador
            draft = self.project.get_draft_folder()
            if draft:
                self.tree_view.select_item(draft.uuid)
        return ok

    def change_icon(self, item_uuid: str, icon_id_or_emoji: str) -> bool:
        """Asigna un nuevo icono vectorial o emoji a un nodo."""
        if not self.project:
            return False
        cmd = ChangeIconCommand(self.project, item_uuid, icon_id_or_emoji)
        return self.undo_stack.push_and_execute(cmd)

    def move_selection_drag_and_drop(self, target_parent_uuid: str, target_index: Optional[int] = None) -> bool:
        """Ejecuta el reordenamiento o anidamiento por Drag & Drop."""
        if not self.project or not self.selected_uuids:
            return False
        cmd = MoveItemsCommand(self.project, self.selected_uuids, target_parent_uuid, target_index)
        return self.undo_stack.push_and_execute(cmd)

    # =========================================================================
    # Deshacer y Rehacer (Undo / Redo)
    # =========================================================================

    def undo(self) -> bool:
        """Deshace la última operación estructural (Ctrl+Z)."""
        return self.undo_stack.undo()

    def redo(self) -> bool:
        """Rehace la última operación deshecha (Ctrl+Y)."""
        return self.undo_stack.redo()

    @property
    def can_undo(self) -> bool:
        return self.undo_stack.can_undo

    @property
    def can_redo(self) -> bool:
        return self.undo_stack.can_redo

    # =========================================================================
    # Consulta y Renderizado de la Interfaz
    # =========================================================================

    def get_view_data(self) -> Dict[str, Any]:
        """
        Devuelve el estado completo del Binder para renderizado:
        pestañas de colecciones, árbol o lista de colección activa, y estado de deshacer.
        """
        active_col = self.collections_mgr.get_active_collection()
        tabs = self.collections_mgr.get_tabs_render_data()

        if active_col is None:
            # Pestaña Cuaderno: Árbol completo multinivel
            items_tree = self.tree_view.get_render_tree()
            is_collection_mode = False
        else:
            # Pestaña Colección: Lista plana filtrada/arbitraria
            collection_items = self.collections_mgr.get_items_for_collection(active_col)
            items_tree = [
                {
                    "uuid": it.uuid,
                    "title": it.title,
                    "type": it.item_type,
                    "depth": 0,
                    "is_selected": (it.uuid in self.selected_uuids),
                    "is_expanded": False,
                    "has_children": len(it.data.children) > 0,
                    "has_text": True,
                    "word_count": it.get_word_count(),
                    "icon_svg": self.tree_view.get_node_icon_svg(it),
                    "show_label_dot": True,
                    "children": []
                }
                for it in collection_items
            ]
            is_collection_mode = True

        return {
            "tabs": tabs,
            "active_tab_index": self.collections_mgr.active_tab_index,
            "is_collection_mode": is_collection_mode,
            "items": items_tree,
            "can_undo": self.can_undo,
            "can_redo": self.can_redo,
            "undo_text": self.undo_stack.get_undo_description(),
            "redo_text": self.undo_stack.get_redo_description(),
            "label_color_mode": self.tree_view.label_color_mode.value
        }
