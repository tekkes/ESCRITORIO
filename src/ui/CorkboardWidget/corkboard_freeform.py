"""
Corkboard Freeform Mode para Escritorio
Modo Forma Libre (Freeform Corkboard):
- Lienzo libre 2D infinito con soporte de Zoom y Paneo
- Colocación de tarjetas en coordenadas (x, y) arbitrarias sin alterar el Binder
- Botón y motor para 'Confirmar orden libre al Binder' (Commit freeform order to Binder)
"""

from typing import List, Dict, Tuple, Optional, Any, Callable
from .index_card import IndexCard
from ...core.project import BinderItem


class CorkboardFreeform:
    """Gestor del Modo Forma Libre 2D."""

    def __init__(self):
        self.cards: List[IndexCard] = []
        self.parent_item: Optional[BinderItem] = None

        # Posiciones libres: uuid -> (x, y)
        self.positions: Dict[str, Tuple[float, float]] = {}

        # Transformaciones de vista (Zoom y Paneo)
        self.zoom: float = 1.0       # 0.25 a 2.5
        self.pan_x: float = 0.0
        self.pan_y: float = 0.0

        # Dimensiones de tarjeta en lienzo libre
        self.card_width: float = 220.0
        self.card_height: float = 132.0

        self.on_order_committed: Optional[Callable[[List[str]], None]] = None

    def set_cards(self, cards: List[IndexCard], parent_item: Optional[BinderItem] = None):
        self.cards = list(cards)
        self.parent_item = parent_item

        # Inicializar posiciones dispersas si no existían
        for idx, card in enumerate(self.cards):
            if card.uuid not in self.positions:
                col = idx % 4
                row = idx // 4
                px = 40.0 + col * (self.card_width + 40.0)
                py = 40.0 + row * (self.card_height + 40.0)
                self.positions[card.uuid] = (px, py)
                card.set_freeform_position(px, py)
            else:
                pos = self.positions[card.uuid]
                card.set_freeform_position(pos[0], pos[1])

    def set_card_position(self, uuid: str, x: float, y: float):
        """Mueve una tarjeta a una coordenada libre sin alterar el Binder."""
        self.positions[uuid] = (x, y)
        for c in self.cards:
            if c.uuid == uuid:
                c.set_freeform_position(x, y)
                break

    # =========================================================================
    # Control de Zoom y Paneo en el Lienzo 2D
    # =========================================================================

    def set_zoom(self, zoom_factor: float):
        self.zoom = max(0.25, min(2.5, round(zoom_factor, 2)))

    def zoom_in(self, delta: float = 0.15):
        self.set_zoom(self.zoom + delta)

    def zoom_out(self, delta: float = 0.15):
        self.set_zoom(self.zoom - delta)

    def reset_view(self):
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0

    def pan(self, dx: float, dy: float):
        self.pan_x += dx
        self.pan_y += dy

    # =========================================================================
    # Confirmar Orden Libre al Binder (Commit to Binder)
    # =========================================================================

    def commit_order_to_binder(self, row_threshold_y: float = 80.0) -> List[str]:
        """
        Calcula el orden narrativo natural a partir de la disposición espacial
        (ordenando principalmente por filas en Y, y de izquierda a derecha en X)
        y actualiza la jerarquía de hijos en el Binder.
        """
        if not self.cards:
            return []

        # Ordenar espacialmente: agrupar por franja vertical (Y) y ordenar por X
        def sort_key(card: IndexCard):
            pos = self.positions.get(card.uuid, (0.0, 0.0))
            # Cuantizar Y según row_threshold_y para agrupar tarjetas en la misma 'línea'
            row_bucket = int(pos[1] // row_threshold_y)
            return (row_bucket, pos[0])

        sorted_cards = sorted(self.cards, key=sort_key)
        self.cards = sorted_cards

        # Actualizar numeración
        for idx, card in enumerate(self.cards):
            card.card_number = idx + 1

        ordered_uuids = [c.uuid for c in self.cards]

        # Sincronizar en el BinderItem
        if self.parent_item and hasattr(self.parent_item, "children"):
            child_map = {c.uuid: c for c in self.parent_item.children}
            new_children = []
            for uid in ordered_uuids:
                if uid in child_map:
                    new_children.append(child_map[uid])
            for c in self.parent_item.children:
                if c not in new_children:
                    new_children.append(c)

            self.parent_item.children = new_children
            self.parent_item.mark_dirty()

            if hasattr(self.parent_item, "project") and self.parent_item.project:
                self.parent_item.project.save_structure()

        if self.on_order_committed:
            self.on_order_committed(ordered_uuids)

        return ordered_uuids

    def get_layout_data(self) -> Dict[str, Any]:
        """Exporta las tarjetas con coordenadas de pantalla transformadas por Zoom y Paneo."""
        layout_cards = []
        for idx, card in enumerate(self.cards):
            base_pos = self.positions.get(card.uuid, (0.0, 0.0))
            # Proyección según Zoom y Paneo
            screen_x = (base_pos[0] + self.pan_x) * self.zoom
            screen_y = (base_pos[1] + self.pan_y) * self.zoom
            w = self.card_width * self.zoom
            h = self.card_height * self.zoom

            layout_cards.append({
                "index": idx,
                "world_x": base_pos[0],
                "world_y": base_pos[1],
                "screen_x": screen_x,
                "screen_y": screen_y,
                "width": w,
                "height": h,
                "card": card.get_render_data()
            })

        return {
            "mode": "freeform",
            "zoom": self.zoom,
            "pan": (self.pan_x, self.pan_y),
            "cards": layout_cards
        }
