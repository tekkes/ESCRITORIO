"""
SplitEditorManager para Escritorio
Gestor central de pantalla dividida con soporte de hasta 4 paneles,
bloqueo en el lugar (Lock in Place / Ctrl+Shift+L), navegación cruzada
y ventanas flotantes Quick Reference (QR).
"""

from typing import Dict, List, Optional, Any
from enum import Enum

from ...core.project import BinderItem, EscritorioProject
from .editor_pane import EditorPane, PaneContentType
from .quick_reference import QuickReferenceManager, QuickReferenceWindow


class SplitLayoutMode(Enum):
    SINGLE = "single"
    VERTICAL = "vertical"        # Ctrl+'
    HORIZONTAL = "horizontal"    # Ctrl+"
    GRID_4 = "grid_4"            # Cuadrícula 2x2 (hasta 4 paneles)


class SplitEditorManager:
    """Controlador maestro del editor central con soporte de división multinivel."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.project = project
        self.layout_mode: SplitLayoutMode = SplitLayoutMode.SINGLE
        self.active_pane_id: str = "pane_0"

        # Inicialización de hasta 4 paneles
        self.panes: Dict[str, EditorPane] = {
            "pane_0": EditorPane("pane_0", project),
            "pane_1": EditorPane("pane_1", project),
            "pane_2": EditorPane("pane_2", project),
            "pane_3": EditorPane("pane_3", project),
        }

        # Gestor de ventanas flotantes Quick Reference
        self.quick_ref_manager = QuickReferenceManager(project)

    def set_project(self, project: EscritorioProject):
        self.project = project
        for pane in self.panes.values():
            pane.project = project
            pane.editor.set_project(project)
        self.quick_ref_manager.set_project(project)

    # =========================================================================
    # Modos de División de Pantalla (Ctrl+', Ctrl+", Grid)
    # =========================================================================

    def split_vertical(self):
        """Divide el editor verticalmente en 2 paneles (Ctrl+')."""
        self.layout_mode = SplitLayoutMode.VERTICAL

    def split_horizontal(self):
        """Divide el editor horizontalmente en 2 paneles (Ctrl+\")."""
        self.layout_mode = SplitLayoutMode.HORIZONTAL

    def split_grid(self):
        """Divide el editor en una cuadrícula de 4 paneles (2x2)."""
        self.layout_mode = SplitLayoutMode.GRID_4

    def close_split(self):
        """Cierra los paneles secundarios y vuelve al panel principal único."""
        # Guardar cambios pendientes en paneles secundarios
        for pid in ("pane_1", "pane_2", "pane_3"):
            self.panes[pid].save_if_dirty()

        self.layout_mode = SplitLayoutMode.SINGLE
        self.active_pane_id = "pane_0"

    # =========================================================================
    # Gestión de Panel Activo y Visibilidad
    # =========================================================================

    @property
    def active_pane(self) -> EditorPane:
        return self.panes.get(self.active_pane_id, self.panes["pane_0"])

    def set_active_pane(self, pane_id: str):
        if pane_id in self.panes:
            self.active_pane_id = pane_id

    def get_visible_pane_ids(self) -> List[str]:
        """Devuelve los IDs de los paneles activos según el modo de división actual."""
        if self.layout_mode == SplitLayoutMode.SINGLE:
            return ["pane_0"]
        elif self.layout_mode in (SplitLayoutMode.VERTICAL, SplitLayoutMode.HORIZONTAL):
            return ["pane_0", "pane_1"]
        elif self.layout_mode == SplitLayoutMode.GRID_4:
            return ["pane_0", "pane_1", "pane_2", "pane_3"]
        return ["pane_0"]

    def get_visible_panes(self) -> List[EditorPane]:
        return [self.panes[pid] for pid in self.get_visible_pane_ids()]

    # =========================================================================
    # Bloqueo en el Lugar (Lock in Place / Ctrl+Shift+L)
    # =========================================================================

    def toggle_lock_active_pane(self) -> bool:
        """Alterna el bloqueo del panel activo (Ctrl+Shift+L)."""
        return self.active_pane.toggle_lock()

    def is_active_locked(self) -> bool:
        return self.active_pane.is_locked

    def set_lock(self, pane_id: str, locked: bool):
        if pane_id in self.panes:
            self.panes[pane_id].set_lock(locked)

    # =========================================================================
    # Navegación Afecta al Otro Editor
    # =========================================================================

    def toggle_navigate_affects_other(self, pane_id: Optional[str] = None) -> bool:
        """Alterna el comportamiento de navegación cruzada en el panel."""
        pid = pane_id or self.active_pane_id
        if pid in self.panes:
            return self.panes[pid].toggle_navigate_affects_other()
        return False

    def get_other_pane(self, source_pane_id: Optional[str] = None) -> Optional[EditorPane]:
        """Calcula el panel objetivo 'otro' para operaciones cruzadas."""
        src_id = source_pane_id or self.active_pane_id
        visible_ids = self.get_visible_pane_ids()

        if len(visible_ids) <= 1:
            return None

        # Si hay 2 paneles
        if len(visible_ids) == 2:
            other_id = "pane_1" if src_id == "pane_0" else "pane_0"
            return self.panes[other_id]

        # Si estamos en cuadrícula de 4
        other_candidates = [pid for pid in visible_ids if pid != src_id and not self.panes[pid].is_locked]
        if other_candidates:
            return self.panes[other_candidates[0]]

        # Si todos los demás están bloqueados, devuelve el primero diferente
        other_fallback = [pid for pid in visible_ids if pid != src_id]
        return self.panes[other_fallback[0]] if other_fallback else None

    # =========================================================================
    # Despacho de Documentos desde el Binder
    # =========================================================================

    def load_item_from_binder(self, item: BinderItem) -> Optional[EditorPane]:
        """
        Carga un ítem seleccionado en el Binder respetando las reglas de:
        1. 'Navegación afecta al otro editor': Si el panel activo lo tiene activo,
           se desvía al otro editor.
        2. 'Lock in Place' (Bloqueo): Si el panel destino está bloqueado,
           se desvía a un panel no bloqueado.
        """
        active = self.active_pane

        # 1. Comprobar si la navegación debe afectar al otro editor
        if active.navigate_affects_other:
            other = self.get_other_pane(self.active_pane_id)
            if other and not other.is_locked:
                other.load_item(item)
                return other
            elif other and other.is_locked:
                # Si el otro también está bloqueado, buscar cualquier otro visible no bloqueado
                for p in self.get_visible_panes():
                    if not p.is_locked:
                        p.load_item(item)
                        return p
                return None

        # 2. Si el panel activo no está bloqueado, cargar normalmente
        if not active.is_locked:
            active.load_item(item)
            return active

        # 3. El panel activo ESTÁ BLOQUEADO: Buscar el primer panel visible no bloqueado
        for pane in self.get_visible_panes():
            if not pane.is_locked:
                pane.load_item(item)
                self.set_active_pane(pane.pane_id)
                return pane

        # 4. Todos los paneles visibles están bloqueados: no sobreescribir ninguno
        return None

    def save_all_dirty(self):
        """Guarda todos los paneles visibles que tengan modificaciones pendientes."""
        for pane in self.get_visible_panes():
            pane.save_if_dirty()

    def get_summary(self) -> dict:
        """Devuelve el estado de todos los paneles para la barra superior y de estado."""
        return {
            "layout_mode": self.layout_mode.value,
            "active_pane_id": self.active_pane_id,
            "visible_panes_count": len(self.get_visible_pane_ids()),
            "panes": {
                pid: self.panes[pid].get_header_state()
                for pid in self.get_visible_pane_ids()
            },
            "qr_open_count": len(self.quick_ref_manager.get_open_windows())
        }
