"""
Sistema de Comandos de Estructura Narrativa con Deshacer / Rehacer (Undo / Redo)
Implementa el patrón Command para todas las transformaciones estructurales del Binder:
Agrupar (Ctrl+G), Desagrupar (Ctrl+Shift+G), Dividir (Ctrl+K), Dividir con Título (Ctrl+Shift+K),
Fusionar (Ctrl+Shift+M), Duplicar (Ctrl+D), Papelera y Drag & Drop.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from ...core.project import EscritorioProject, BinderItem
from ...core.rtf_engine import RTFEngine

class BinderCommand(ABC):
    """Clase base abstracta para operaciones reversibles sobre el árbol del Binder."""

    def __init__(self, project: EscritorioProject, description: str):
        self.project = project
        self.description = description
        self.executed: bool = False

    @abstractmethod
    def execute(self) -> bool:
        pass

    @abstractmethod
    def undo(self) -> bool:
        pass

    def redo(self) -> bool:
        return self.execute()


class UndoStack:
    """Pila de Deshacer / Rehacer (Ctrl+Z / Ctrl+Y) para el Binder."""

    def __init__(self, max_depth: int = 50):
        self.max_depth = max_depth
        self._undo_stack: List[BinderCommand] = []
        self._redo_stack: List[BinderCommand] = []

    @property
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def push_and_execute(self, command: BinderCommand) -> bool:
        success = command.execute()
        if success:
            self._undo_stack.append(command)
            if len(self._undo_stack) > self.max_depth:
                self._undo_stack.pop(0)
            self._redo_stack.clear()
        return success

    def undo(self) -> bool:
        if not self.can_undo:
            return False
        cmd = self._undo_stack.pop()
        success = cmd.undo()
        if success:
            self._redo_stack.append(cmd)
        return success

    def redo(self) -> bool:
        if not self.can_redo:
            return False
        cmd = self._redo_stack.pop()
        success = cmd.redo()
        if success:
            self._undo_stack.append(cmd)
        return success

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()

    def get_undo_description(self) -> str:
        return self._undo_stack[-1].description if self._undo_stack else ""

    def get_redo_description(self) -> str:
        return self._redo_stack[-1].description if self._redo_stack else ""


# =========================================================================
# Comandos Concretos de Narrativa
# =========================================================================

class MoveItemsCommand(BinderCommand):
    """Mueve una selección de elementos a un nuevo padre y posición (Drag & Drop)."""

    def __init__(self, project: EscritorioProject, item_uuids: List[str], target_parent_uuid: str, target_index: Optional[int] = None):
        super().__init__(project, f"Mover {len(item_uuids)} elemento(s)")
        self.item_uuids = item_uuids
        self.target_parent_uuid = target_parent_uuid
        self.target_index = target_index
        self._original_locations: List[Tuple[str, str, int]] = []

    def execute(self) -> bool:
        self._original_locations.clear()
        for u in self.item_uuids:
            loc = self.project.find_parent_data_and_index(u)
            if loc:
                parent_data, _, idx = loc
                parent_uuid = parent_data.uuid if parent_data else ""
                self._original_locations.append((u, parent_uuid, idx))

        success = True
        for offset, u in enumerate(self.item_uuids):
            idx = (self.target_index + offset) if self.target_index is not None else None
            ok = self.project.move_item(u, self.target_parent_uuid, idx)
            if not ok:
                success = False
        return success

    def undo(self) -> bool:
        success = True
        for u, orig_parent_uuid, orig_idx in reversed(self._original_locations):
            ok = self.project.move_item(u, orig_parent_uuid, orig_idx)
            if not ok:
                success = False
        return success


class GroupItemsCommand(BinderCommand):
    """Agrupa los ítems seleccionados dentro de una nueva carpeta (Ctrl+G)."""

    def __init__(self, project: EscritorioProject, item_uuids: List[str], folder_title: str = "Nueva Carpeta"):
        super().__init__(project, f"Agrupar en '{folder_title}'")
        self.item_uuids = item_uuids
        self.folder_title = folder_title
        self.created_folder_uuid: Optional[str] = None
        self._original_locations: List[Tuple[str, str, int]] = []

    def execute(self) -> bool:
        self._original_locations.clear()
        for u in self.item_uuids:
            loc = self.project.find_parent_data_and_index(u)
            if loc:
                parent_data, _, idx = loc
                parent_uuid = parent_data.uuid if parent_data else ""
                self._original_locations.append((u, parent_uuid, idx))

        folder = self.project.group_items(self.item_uuids, self.folder_title, self.created_folder_uuid)
        if folder:
            self.created_folder_uuid = folder.uuid
            return True
        return False

    def undo(self) -> bool:
        if not self.created_folder_uuid:
            return False

        # Mover cada ítem de vuelta a su ubicación original
        for u, parent_uuid, idx in self._original_locations:
            self.project.move_item(u, parent_uuid, idx)

        # Eliminar la carpeta creada
        self.project.move_to_trash(self.created_folder_uuid)
        trash = self.project.get_trash_folder()
        if trash:
            loc = self.project.find_parent_data_and_index(self.created_folder_uuid)
            if loc:
                _, p_list, i = loc
                p_list.pop(i)
                self.project.items_by_uuid.pop(self.created_folder_uuid, None)
        self.project.save_structure()
        return True


class UngroupFolderCommand(BinderCommand):
    """Desagrupa una carpeta extrayendo sus hijos al nivel superior (Ctrl+Shift+G)."""

    def __init__(self, project: EscritorioProject, folder_uuid: str):
        super().__init__(project, "Desagrupar carpeta")
        self.folder_uuid = folder_uuid
        self._folder_data_backup: Optional[Dict[str, Any]] = None
        self._children_uuids: List[str] = []
        self._original_parent_uuid: str = ""
        self._original_index: int = 0

    def execute(self) -> bool:
        folder = self.project.get_item(self.folder_uuid)
        if not folder:
            return False

        parent = self.project.find_parent(self.folder_uuid)
        self._original_parent_uuid = parent.uuid if parent else ""

        loc = self.project.find_parent_data_and_index(self.folder_uuid)
        self._original_index = loc[2] if loc else 0

        self._children_uuids = [c.uuid for c in folder.children]
        self._folder_data_backup = {
            "title": folder.title,
            "type": folder.item_type,
            "icon": folder.data.icon_file_name,
            "content": folder.read_content_rtf(),
            "synopsis": folder.read_synopsis(),
            "notes": folder.read_notes_rtf()
        }

        extracted = self.project.ungroup_folder(self.folder_uuid)
        return len(extracted) >= 0

    def undo(self) -> bool:
        if not self._folder_data_backup:
            return False

        # Re-crear la carpeta original
        folder = self.project.add_item(
            self._original_parent_uuid,
            title=self._folder_data_backup["title"],
            item_type=self._folder_data_backup["type"]
        )
        self.folder_uuid = folder.uuid
        folder.data.icon_file_name = self._folder_data_backup["icon"]
        folder.write_content_rtf(self._folder_data_backup["content"])
        folder.write_synopsis(self._folder_data_backup["synopsis"])
        folder.write_notes_rtf(self._folder_data_backup["notes"])

        # Mover los hijos extraídos de vuelta a la carpeta
        for u in self._children_uuids:
            self.project.move_item(u, folder.uuid)

        self.project.save_structure()
        return True


class SplitDocumentCommand(BinderCommand):
    """Divide un documento en la posición de caracteres indicada (Ctrl+K)."""

    def __init__(self, project: EscritorioProject, item_uuid: str, split_pos: int, new_title: str = "Continuación"):
        super().__init__(project, f"Dividir documento en '{new_title}'")
        self.item_uuid = item_uuid
        self.split_pos = split_pos
        self.new_title = new_title
        self.created_item_uuid: Optional[str] = None
        self._original_content_rtf: str = ""

    def execute(self) -> bool:
        item = self.project.get_item(self.item_uuid)
        if not item:
            return False
        self._original_content_rtf = item.read_content_rtf()

        new_item = self.project.split_item(self.item_uuid, self.split_pos, self.new_title, self.created_item_uuid)
        if new_item:
            self.created_item_uuid = new_item.uuid
            return True
        return False

    def undo(self) -> bool:
        item = self.project.get_item(self.item_uuid)
        if not item:
            return False

        item.write_content_rtf(self._original_content_rtf)

        if self.created_item_uuid:
            # Eliminar documento generado
            loc = self.project.find_parent_data_and_index(self.created_item_uuid)
            if loc:
                _, p_list, idx = loc
                p_list.pop(idx)
                self.project.items_by_uuid.pop(self.created_item_uuid, None)

        self.project.save_structure()
        return True


class SplitDocumentWithTitleCommand(BinderCommand):
    """Divide usando el texto seleccionado como título del segundo documento (Ctrl+Shift+K)."""

    def __init__(self, project: EscritorioProject, item_uuid: str, start_pos: int, end_pos: int):
        super().__init__(project, "Dividir usando selección como título")
        self.item_uuid = item_uuid
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.created_item_uuid: Optional[str] = None
        self._original_content_rtf: str = ""

    def execute(self) -> bool:
        item = self.project.get_item(self.item_uuid)
        if not item:
            return False
        self._original_content_rtf = item.read_content_rtf()

        new_item = self.project.split_item_with_selection_as_title(self.item_uuid, self.start_pos, self.end_pos, self.created_item_uuid)
        if new_item:
            self.created_item_uuid = new_item.uuid
            return True
        return False

    def undo(self) -> bool:
        item = self.project.get_item(self.item_uuid)
        if not item:
            return False

        item.write_content_rtf(self._original_content_rtf)

        if self.created_item_uuid:
            loc = self.project.find_parent_data_and_index(self.created_item_uuid)
            if loc:
                _, p_list, idx = loc
                p_list.pop(idx)
                self.project.items_by_uuid.pop(self.created_item_uuid, None)

        self.project.save_structure()
        return True


class MergeDocumentsCommand(BinderCommand):
    """Fusiona múltiples documentos en el primero (Ctrl+Shift+M)."""

    def __init__(self, project: EscritorioProject, item_uuids: List[str]):
        super().__init__(project, f"Fusionar {len(item_uuids)} documentos")
        self.item_uuids = item_uuids
        self._backups: Dict[str, Dict[str, Any]] = {}

    def execute(self) -> bool:
        self._backups.clear()
        for u in self.item_uuids:
            it = self.project.get_item(u)
            if it:
                parent = self.project.find_parent(u)
                self._backups[u] = {
                    "content": it.read_content_rtf(),
                    "synopsis": it.read_synopsis(),
                    "notes": it.read_notes_rtf(),
                    "parent_uuid": parent.uuid if parent else ""
                }

        merged = self.project.merge_items(self.item_uuids)
        return merged is not None

    def undo(self) -> bool:
        # Restaurar documento primario
        prim_uuid = self.item_uuids[0]
        prim_item = self.project.get_item(prim_uuid)
        if prim_item and prim_uuid in self._backups:
            b = self._backups[prim_uuid]
            prim_item.write_content_rtf(b["content"])
            prim_item.write_synopsis(b["synopsis"])
            prim_item.write_notes_rtf(b["notes"])

        # Restaurar documentos absorbidos desde la papelera
        for u in self.item_uuids[1:]:
            if u in self._backups:
                b = self._backups[u]
                self.project.restore_from_trash(u, b["parent_uuid"])
                other = self.project.get_item(u)
                if other:
                    other.write_content_rtf(b["content"])
                    other.write_synopsis(b["synopsis"])
                    other.write_notes_rtf(b["notes"])

        self.project.save_structure()
        return True


class DuplicateItemCommand(BinderCommand):
    """Duplica profundamente un ítem (Ctrl+D)."""

    def __init__(self, project: EscritorioProject, item_uuid: str):
        super().__init__(project, "Duplicar documento o carpeta")
        self.item_uuid = item_uuid
        self.created_duplicate_uuid: Optional[str] = None

    def execute(self) -> bool:
        clone = self.project.duplicate_item(self.item_uuid, dest_uuid=self.created_duplicate_uuid)
        if clone:
            self.created_duplicate_uuid = clone.uuid
            return True
        return False

    def undo(self) -> bool:
        if not self.created_duplicate_uuid:
            return False

        loc = self.project.find_parent_data_and_index(self.created_duplicate_uuid)
        if loc:
            _, p_list, idx = loc
            p_list.pop(idx)
            self.project.items_by_uuid.pop(self.created_duplicate_uuid, None)
            self.project.save_structure()
            return True
        return False


class TrashItemCommand(BinderCommand):
    """Mueve ítems a la papelera (Supr)."""

    def __init__(self, project: EscritorioProject, item_uuids: List[str]):
        super().__init__(project, f"Enviar a la Papelera {len(item_uuids)} elemento(s)")
        self.item_uuids = item_uuids
        self._orig_locations: List[Tuple[str, str, int]] = []

    def execute(self) -> bool:
        self._orig_locations.clear()
        for u in self.item_uuids:
            loc = self.project.find_parent_data_and_index(u)
            if loc:
                p_data, _, idx = loc
                p_uuid = p_data.uuid if p_data else ""
                self._orig_locations.append((u, p_uuid, idx))

        success = True
        for u in self.item_uuids:
            if not self.project.move_to_trash(u):
                success = False
        return success

    def undo(self) -> bool:
        success = True
        for u, parent_uuid, idx in self._orig_locations:
            ok = self.project.restore_from_trash(u, parent_uuid)
            if not ok:
                success = False
        return success


class ChangeIconCommand(BinderCommand):
    """Cambia el icono de un nodo en el Binder."""

    def __init__(self, project: EscritorioProject, item_uuid: str, new_icon: str):
        super().__init__(project, f"Cambiar icono a '{new_icon}'")
        self.item_uuid = item_uuid
        self.new_icon = new_icon
        self.previous_icon: Optional[str] = None

    def execute(self) -> bool:
        item = self.project.get_item(self.item_uuid)
        if not item:
            return False
        self.previous_icon = item.data.icon_file_name
        item.data.icon_file_name = self.new_icon
        item.mark_dirty()
        self.project.save_structure()
        return True

    def undo(self) -> bool:
        item = self.project.get_item(self.item_uuid)
        if not item:
            return False
        item.data.icon_file_name = self.previous_icon
        item.mark_dirty()
        self.project.save_structure()
        return True
