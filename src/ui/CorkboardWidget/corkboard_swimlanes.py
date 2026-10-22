"""
Corkboard Swimlanes Mode para Escritorio
Modo Apilado por Etiqueta (Arrange by Label / Swimlanes):
- Organiza las tarjetas en columnas (o filas) según su Etiqueta (Label)
- Ideal para el seguimiento visual de arcos dramáticos de personajes o líneas temporales
- Arrastrar una tarjeta de un carril a otro actualiza instantáneamente su Etiqueta y orden
"""

from typing import List, Dict, Optional, Any, Callable
from .index_card import IndexCard
from ...core.project import BinderItem, EscritorioProject


class SwimlaneColumn:
    """Columna o carril temático que agrupa tarjetas por una Etiqueta específica."""

    def __init__(self, label_id: int, label_name: str, color_hex: str):
        self.label_id = label_id
        self.label_name = label_name
        self.color_hex = color_hex
        self.cards: List[IndexCard] = []

    def add_card(self, card: IndexCard, position: int = -1):
        if position < 0 or position >= len(self.cards):
            self.cards.append(card)
        else:
            self.cards.insert(position, card)

    def remove_card(self, card_uuid: str) -> Optional[IndexCard]:
        for idx, c in enumerate(self.cards):
            if c.uuid == card_uuid:
                return self.cards.pop(idx)
        return None


class CorkboardSwimlanes:
    """Gestor del Modo Apilado por Etiqueta (Swimlanes)."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.project = project
        self.parent_item: Optional[BinderItem] = None
        self.columns: Dict[int, SwimlaneColumn] = {}
        self.is_horizontal: bool = False  # False = Columnas verticales, True = Filas horizontales

        # Callbacks
        self.on_card_label_changed: Optional[Callable[[str, int], None]] = None

    def initialize_lanes(self, cards: List[IndexCard], parent_item: Optional[BinderItem] = None):
        """Construye los carriles a partir de las etiquetas del proyecto y clasifica las tarjetas."""
        self.parent_item = parent_item
        self.columns.clear()

        # 1. Carril por defecto para elementos sin etiqueta
        self.columns[-1] = SwimlaneColumn(-1, "Sin Etiqueta", "#94A3B8")

        # 2. Carriles para las etiquetas definidas en el proyecto
        if self.project and hasattr(self.project, "labels"):
            for lid, ldef in self.project.labels.items():
                col_hex = getattr(ldef, "color_hex", "#3B82F6") or "#3B82F6"
                self.columns[lid] = SwimlaneColumn(lid, ldef.name, col_hex)

        # 3. Clasificar cada tarjeta en su carril
        for card in cards:
            lid = card.label_id
            if lid not in self.columns:
                # Si la etiqueta no existe explícitamente, añadirla dinámicamente
                self.columns[lid] = SwimlaneColumn(lid, card.label_name or f"Etiqueta {lid}", card.label_color or "#3B82F6")

            # Asignar atributos de color a la tarjeta
            lane = self.columns[lid]
            card.label_name = lane.label_name
            card.label_color = lane.color_hex
            lane.add_card(card)

    def move_card_to_lane(self, card_uuid: str, target_label_id: int, new_index: int = -1) -> bool:
        """
        Mueve una tarjeta de su carril actual a target_label_id.
        Actualiza el label_id del BinderItem y sincroniza.
        """
        # 1. Encontrar y extraer la tarjeta de su carril de origen
        found_card: Optional[IndexCard] = None
        for col in self.columns.values():
            found_card = col.remove_card(card_uuid)
            if found_card:
                break

        if not found_card:
            return False

        # 2. Asegurar que existe el carril destino
        if target_label_id not in self.columns:
            self.columns[target_label_id] = SwimlaneColumn(target_label_id, f"Etiqueta {target_label_id}", "#3B82F6")

        target_lane = self.columns[target_label_id]

        # 3. Actualizar la tarjeta y su BinderItem con la nueva etiqueta
        found_card.set_label(target_lane.label_id, target_lane.label_name, target_lane.color_hex)
        target_lane.add_card(found_card, new_index)

        # 4. Notificar
        if self.on_card_label_changed:
            self.on_card_label_changed(card_uuid, target_label_id)

        # 5. Persistir si procede
        if self.project:
            self.project.save_structure()

        return True

    def toggle_orientation(self) -> bool:
        """Alterna entre columnas verticales y filas horizontales."""
        self.is_horizontal = not self.is_horizontal
        return self.is_horizontal

    def get_layout_data(self) -> Dict[str, Any]:
        """Exporta los carriles y sus tarjetas agrupadas para la presentación."""
        lanes_data = []
        for lid, col in self.columns.items():
            # Solo incluir carriles que tengan tarjetas o sean etiquetas válidas
            lanes_data.append({
                "label_id": col.label_id,
                "label_name": col.label_name,
                "color_hex": col.color_hex,
                "card_count": len(col.cards),
                "cards": [c.get_render_data() for c in col.cards]
            })

        return {
            "mode": "swimlanes",
            "is_horizontal": self.is_horizontal,
            "lane_count": len(lanes_data),
            "lanes": lanes_data
        }
