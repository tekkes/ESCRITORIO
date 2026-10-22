"""
CorkboardWidget para Escritorio
Componente principal de la Pizarra de Corcho (Ctrl+2) con paridad funcional total respecto a Scrivener 3.
Coordina:
- Diseño de fichas de índice (IndexCard) con títulos in-situ, sinopsis, sellos y etiquetas
- 3 Submodos: Modo Rejilla (Grid), Modo Forma Libre (Freeform) y Modo Apilado por Etiqueta (Swimlanes)
- Barra inferior ultra-compacta (CorkboardFooterBar) con ajustes en vivo
- Sincronización directa y bidireccional con el árbol del Binder
"""

from enum import Enum
from typing import Optional, List, Dict, Any, Callable

from ...core.project import BinderItem, EscritorioProject
from .index_card import IndexCard, CardAspectRatio, LabelColorStyle
from .corkboard_grid import CorkboardGrid
from .corkboard_freeform import CorkboardFreeform
from .corkboard_swimlanes import CorkboardSwimlanes
from .corkboard_footer import CorkboardFooterBar


class CorkboardMode(Enum):
    GRID = "grid"                # Rejilla (Arrange by Order)
    FREEFORM = "freeform"        # Forma Libre 2D (Lienzo libre con Zoom y Paneo)
    SWIMLANES = "swimlanes"      # Apilado por Etiqueta (Columnas / Carriles temáticos)


class CorkboardWidget:
    """Controlador y orquestador maestro de la Pizarra de Corcho."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.project = project
        self.parent_item: Optional[BinderItem] = None
        self.cards: List[IndexCard] = []
        self.current_mode: CorkboardMode = CorkboardMode.GRID

        # Gestores de los 3 submodos
        self.grid = CorkboardGrid()
        self.freeform = CorkboardFreeform()
        self.swimlanes = CorkboardSwimlanes(project)
        self.footer = CorkboardFooterBar()

        # Conectar cambios de configuración de la barra inferior con la rejilla
        self.footer.on_settings_changed = self._apply_footer_settings

        # Callbacks hacia MainWindow / Binder
        self.on_selection_requested: Optional[Callable[[str], None]] = None

    def set_project(self, project: EscritorioProject):
        self.project = project
        self.swimlanes.project = project
        if self.parent_item:
            self.load_container(self.parent_item)

    def load_container(self, item: BinderItem):
        """Carga las fichas de índice de todos los descendientes directos del contenedor."""
        self.parent_item = item
        self.cards.clear()

        # Recopilar etiquetas y estados del proyecto
        labels_map = getattr(self.project, "labels", {}) if self.project else {}
        statuses_map = getattr(self.project, "statuses", {}) if self.project else {}

        children = getattr(item, "children", []) or []
        for idx, child in enumerate(children):
            card = IndexCard(child, card_number=idx + 1)

            # Sincronizar etiqueta
            lid = card.label_id
            if lid in labels_map:
                ldef = labels_map[lid]
                card.label_name = ldef.name
                card.label_color = getattr(ldef, "color_hex", "#3B82F6") or "#3B82F6"

            # Sincronizar estado
            sid = card.status_id
            if sid in statuses_map:
                sdef = statuses_map[sid]
                card.status_name = sdef.name
                card.status_stamp_text = sdef.name.upper()

            # Aplicar opciones activas del pie
            card.label_style = self.footer.label_style
            card.show_status_stamp = self.footer.show_status_stamps
            card.notebook_lines = self.footer.show_notebook_lines

            self.cards.append(card)

        # Distribuir a los 3 gestores
        self.grid.set_cards(self.cards, item)
        self.freeform.set_cards(self.cards, item)
        self.swimlanes.initialize_lanes(self.cards, item)
        self._apply_footer_settings()

    def _apply_footer_settings(self):
        """Transfiere los ajustes de la barra inferior a los gestores y tarjetas."""
        self.grid.card_base_width = self.footer.card_size_px
        self.grid.aspect_ratio = self.footer.aspect_ratio
        self.grid.spacing_px = self.footer.spacing_px
        self.grid.cards_per_row = self.footer.cards_per_row

        self.freeform.card_width = self.footer.card_size_px
        self.freeform.card_height = self.footer.card_size_px / self.footer.aspect_ratio.ratio_float

        for card in self.cards:
            card.label_style = self.footer.label_style
            card.show_status_stamp = self.footer.show_status_stamps
            card.notebook_lines = self.footer.show_notebook_lines
            card.show_number = self.footer.show_card_numbers

    # =========================================================================
    # Conmutación de Modos (Grid, Freeform, Swimlanes)
    # =========================================================================

    def set_mode(self, mode: CorkboardMode):
        self.current_mode = mode
        if mode == CorkboardMode.GRID:
            self.grid.set_cards(self.cards, self.parent_item)
        elif mode == CorkboardMode.FREEFORM:
            self.freeform.set_cards(self.cards, self.parent_item)
        elif mode == CorkboardMode.SWIMLANES:
            self.swimlanes.initialize_lanes(self.cards, self.parent_item)

    def cycle_mode(self) -> CorkboardMode:
        """Cicla entre los 3 submodos."""
        if self.current_mode == CorkboardMode.GRID:
            self.set_mode(CorkboardMode.FREEFORM)
        elif self.current_mode == CorkboardMode.FREEFORM:
            self.set_mode(CorkboardMode.SWIMLANES)
        else:
            self.set_mode(CorkboardMode.GRID)
        return self.current_mode

    # =========================================================================
    # Operaciones del Modo Rejilla (Grid)
    # =========================================================================

    def reorder_grid_cards(self, from_idx: int, to_idx: int) -> bool:
        """Reordena tarjetas en el modo Rejilla y sincroniza en el Binder."""
        ok = self.grid.reorder_cards(from_idx, to_idx)
        if ok:
            self.cards = list(self.grid.cards)
        return ok

    # =========================================================================
    # Operaciones del Modo Forma Libre (Freeform)
    # =========================================================================

    def set_freeform_card_position(self, card_uuid: str, x: float, y: float):
        """Mueve una tarjeta en el lienzo libre 2D."""
        self.freeform.set_card_position(card_uuid, x, y)

    def commit_freeform_order_to_binder(self) -> List[str]:
        """Aplica la disposición libre 2D como nuevo orden en el Binder."""
        ordered = self.freeform.commit_order_to_binder()
        self.cards = list(self.freeform.cards)
        self.grid.set_cards(self.cards, self.parent_item)
        return ordered

    # =========================================================================
    # Operaciones del Modo Apilado por Etiqueta (Swimlanes)
    # =========================================================================

    def move_card_to_swimlane(self, card_uuid: str, target_label_id: int, new_index: int = -1) -> bool:
        """Mueve una tarjeta a otro carril de etiqueta."""
        return self.swimlanes.move_card_to_lane(card_uuid, target_label_id, new_index)

    # =========================================================================
    # Búsqueda y Modificación de Fichas
    # =========================================================================

    def get_card(self, uuid: str) -> Optional[IndexCard]:
        for c in self.cards:
            if c.uuid == uuid:
                return c
        return None

    def update_card_title(self, uuid: str, new_title: str) -> bool:
        card = self.get_card(uuid)
        if card:
            card.set_title(new_title)
            return True
        return False

    def update_card_synopsis(self, uuid: str, new_synopsis: str) -> bool:
        card = self.get_card(uuid)
        if card:
            card.set_synopsis(new_synopsis)
            return True
        return False

    # =========================================================================
    # Datos para Renderizado
    # =========================================================================

    def get_view_data(self, available_width: float = 1200.0) -> Dict[str, Any]:
        """Genera el árbol completo de telemetría y geometría para la capa gráfica."""
        if self.current_mode == CorkboardMode.GRID:
            mode_data = self.grid.get_layout_data(available_width)
        elif self.current_mode == CorkboardMode.FREEFORM:
            mode_data = self.freeform.get_layout_data()
        else:
            mode_data = self.swimlanes.get_layout_data()

        return {
            "mode": self.current_mode.value,
            "parent_uuid": self.parent_item.uuid if self.parent_item else "",
            "parent_title": self.parent_item.title if self.parent_item else "Pizarra Vacía",
            "card_count": len(self.cards),
            "footer": self.footer.get_state(),
            "layout": mode_data
        }
