"""
Corkboard View para Escritorio
Tablero de corcho virtual con tarjetas de indexación, alfileres cromáticos,
sinopsis resumida, metadatos y reordenación visual mediante drag-and-drop.
Retrocompatible con CorkboardWidget.
"""

from typing import List, Dict, Any, Optional
from ..core.project import BinderItem, EscritorioProject
from .CorkboardWidget import (
    CorkboardWidget,
    CorkboardMode,
    IndexCard,
    CardAspectRatio,
    LabelColorStyle
)


class CorkboardCard(IndexCard):
    """Ficha de índice retrocompatible con CorkboardCard original."""

    def __init__(
        self,
        item: Optional[BinderItem] = None,
        item_id: Optional[str] = None,
        title: str = "",
        synopsis: str = "",
        label_color: str = "",
        status: str = ""
    ):
        if item is None:
            from ..core.xml_parser import BinderItemData
            data = BinderItemData(uuid=item_id or "dummy-uuid", title=title or "Card", item_type="Text")
            item = BinderItem(data, None)
        super().__init__(item)
        if title:
            self.title = title
        if synopsis:
            self.synopsis = synopsis
        if label_color:
            self.label_color = label_color
        if status:
            self.status_name = status
            self.status_stamp_text = status.upper()
        self.section_type = getattr(item.data, "section_type", "Structure Based") if hasattr(item, "data") else "Structure Based"

    def update_synopsis(self, new_text: str):
        self.set_synopsis(new_text)


class CorkboardView(CorkboardWidget):
    """Controlador y lógica del tablero de corcho para contenedores de documentos."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        super().__init__(project)

    @property
    def columns(self) -> int:
        return self.grid.calculate_columns(1200.0)

    @columns.setter
    def columns(self, val: int):
        self.footer.set_cards_per_row(val)

    @property
    def card_size(self) -> str:
        s = self.footer.card_size_px
        if s <= 160:
            return "small"
        elif s >= 280:
            return "large"
        return "medium"

    @card_size.setter
    def card_size(self, val: str):
        if val == "small":
            self.footer.set_card_size(160.0)
        elif val == "large":
            self.footer.set_card_size(300.0)
        else:
            self.footer.set_card_size(220.0)

    def add_card(self, card: IndexCard):
        self.cards.append(card)
        card.card_number = len(self.cards)
        self.grid.set_cards(self.cards, self.parent_item)

    def get_cards_data(self) -> List[Dict[str, Any]]:
        return [
            {
                "uuid": card.uuid,
                "title": card.title,
                "synopsis": card.synopsis,
                "label_id": card.label_id,
                "status_id": card.status_id,
                "section_type": getattr(card, "section_type", "Structure Based"),
            }
            for card in self.cards
        ]
