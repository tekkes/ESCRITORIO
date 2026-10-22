"""
Corkboard Grid Mode para Escritorio
Modo Rejilla (Arrange by Order):
- Disposición regular de tarjetas por orden secuencial de manuscrito
- Arrastrar y soltar (Drag & Drop) que reordena automáticamente en el Binder
- Soporte para columnas fijas (1 a 10) o 'Auto' según ancho de ventana
- Ajuste dinámico de ratio de aspecto (3x5, 4x6, 1x1) y espaciado
"""

from typing import List, Optional, Tuple, Dict, Any, Callable
from .index_card import IndexCard, CardAspectRatio
from ...core.project import BinderItem


class CorkboardGrid:
    """Gestor del Modo Rejilla del Tablero de Corcho."""

    def __init__(self):
        self.cards: List[IndexCard] = []
        self.parent_item: Optional[BinderItem] = None

        # Parámetros de cuadrícula
        self.cards_per_row: int = 0      # 0 = 'Auto'
        self.card_base_width: float = 220.0
        self.aspect_ratio: CardAspectRatio = CardAspectRatio.RATIO_3x5
        self.spacing_px: float = 16.0

        # Callback cuando se reordena
        self.on_order_changed: Optional[Callable[[List[str]], None]] = None

    def set_cards(self, cards: List[IndexCard], parent_item: Optional[BinderItem] = None):
        self.cards = list(cards)
        self.parent_item = parent_item
        self._update_card_numbers()

    def _update_card_numbers(self):
        for idx, card in enumerate(self.cards):
            card.card_number = idx + 1

    @property
    def card_width(self) -> float:
        return self.card_base_width

    @property
    def card_height(self) -> float:
        return self.card_base_width / self.aspect_ratio.ratio_float

    def calculate_columns(self, available_width: float) -> int:
        """Determina el número de columnas a renderizar."""
        if self.cards_per_row > 0:
            return min(10, max(1, self.cards_per_row))

        # Modo Auto: calcular según el ancho de la ventana
        col_width = self.card_width + self.spacing_px
        cols = int(max(1.0, (available_width - self.spacing_px) // col_width))
        return min(10, max(1, cols))

    def get_card_bounds(self, index: int, available_width: float) -> Tuple[float, float, float, float]:
        """Calcula el rectángulo (x, y, w, h) para la tarjeta en la posición dada."""
        cols = self.calculate_columns(available_width)
        row = index // cols
        col = index % cols

        x = self.spacing_px + col * (self.card_width + self.spacing_px)
        y = self.spacing_px + row * (self.card_height + self.spacing_px)
        return x, y, self.card_width, self.card_height

    def reorder_cards(self, from_index: int, to_index: int) -> bool:
        """
        Reordena una tarjeta de la posición from_index a to_index
        y sincroniza la nueva ordenación en el BinderItem contenedor.
        """
        if not (0 <= from_index < len(self.cards)) or not (0 <= to_index < len(self.cards)):
            return False

        card = self.cards.pop(from_index)
        self.cards.insert(to_index, card)
        self._update_card_numbers()

        # Sincronizar orden en el BinderItem padre
        if self.parent_item and hasattr(self.parent_item, "children"):
            child_map = {c.uuid: c for c in self.parent_item.children}
            new_children = []
            for c in self.cards:
                if c.uuid in child_map:
                    new_children.append(child_map[c.uuid])
            # Añadir cualquier hijo que no esté en la rejilla
            for c in self.parent_item.children:
                if c not in new_children:
                    new_children.append(c)
            self.parent_item.children = new_children
            self.parent_item.mark_dirty()

            # Guardar estructura en el proyecto
            if hasattr(self.parent_item, "project") and self.parent_item.project:
                self.parent_item.project.save_structure()

        if self.on_order_changed:
            self.on_order_changed([c.uuid for c in self.cards])

        return True

    def get_layout_data(self, available_width: float = 1000.0) -> Dict[str, Any]:
        """Calcula las posiciones absolutas de todas las tarjetas para renderizar."""
        cols = self.calculate_columns(available_width)
        layout_cards = []

        for idx, card in enumerate(self.cards):
            x, y, w, h = self.get_card_bounds(idx, available_width)
            layout_cards.append({
                "index": idx,
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "card": card.get_render_data()
            })

        total_rows = (len(self.cards) + cols - 1) // cols if cols else 0
        total_height = self.spacing_px + total_rows * (self.card_height + self.spacing_px)

        return {
            "mode": "grid",
            "columns": cols,
            "cards_per_row": self.cards_per_row,
            "aspect_ratio": self.aspect_ratio.value,
            "card_width": self.card_width,
            "card_height": self.card_height,
            "spacing": self.spacing_px,
            "total_height": total_height,
            "cards": layout_cards
        }
