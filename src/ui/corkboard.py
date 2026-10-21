"""
Corkboard View para Escritorio
Tablero de corcho virtual con tarjetas de indexación, alfileres cromáticos,
sinopsis resumida, metadatos y reordenación visual mediante drag-and-drop.
"""

from typing import List, Dict, Any, Optional
from ..core.project import BinderItem

class CorkboardCard:
    def __init__(self, item: BinderItem):
        self.item = item
        self.uuid = item.uuid
        self.title = item.title
        self.synopsis = item.read_synopsis()
        self.label_id = item.data.label_id
        self.status_id = item.data.status_id
        self.section_type = item.data.section_type

    def update_synopsis(self, new_text: str):
        self.synopsis = new_text
        self.item.write_synopsis(new_text)

class CorkboardView:
    """Controlador y lógica del tablero de corcho para contenedores de documentos."""

    def __init__(self):
        self.parent_item: Optional[BinderItem] = None
        self.cards: List[CorkboardCard] = []
        self.columns: int = 4
        self.card_size: str = "medium"  # small, medium, large

    def load_container(self, item: BinderItem):
        """Carga las tarjetas de los hijos del elemento seleccionado."""
        self.parent_item = item
        self.cards = [CorkboardCard(child) for child in item.children]

    def get_cards_data(self) -> List[Dict[str, Any]]:
        return [
            {
                "uuid": card.uuid,
                "title": card.title,
                "synopsis": card.synopsis,
                "label_id": card.label_id,
                "status_id": card.status_id,
                "section_type": card.section_type,
            }
            for card in self.cards
        ]
