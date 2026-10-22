"""
Index Card Widget para Corkboard de Escritorio
Diseño visual y lógica de la Ficha de Índice con paridad funcional respecto a Scrivener 3:
- Cabecera con icono, numeración opcional y título editable con doble clic
- Cuerpo con sinopsis editable (synopsis.txt) sobre líneas de libreta o visualización de imagen
- Color de Etiqueta (Label) como alfiler (Pin), franja lateral (Stripe) o tintado de fondo
- Sello de Estado (Status Stamp) diagonal semitransparente personalizable
- Chips de palabras clave (Keywords) con bloques cromáticos
"""

from enum import Enum
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path

from ...core.project import BinderItem


class LabelColorStyle(Enum):
    PIN = "pin"                  # Alfiler cromático en la parte superior
    STRIPE = "stripe"            # Franja de color en el lateral izquierdo
    FULL_BACKGROUND = "full"     # Tintado suave de todo el fondo de la ficha


class CardAspectRatio(Enum):
    RATIO_3x5 = "3x5"            # 3 x 5 pulgadas (1.67)
    RATIO_4x6 = "4x6"            # 4 x 6 pulgadas (1.50)
    RATIO_1x1 = "1x1"            # Cuadrado 1:1 (1.00)

    @property
    def ratio_float(self) -> float:
        if self == CardAspectRatio.RATIO_3x5:
            return 5.0 / 3.0     # ~1.666
        elif self == CardAspectRatio.RATIO_4x6:
            return 6.0 / 4.0     # 1.5
        elif self == CardAspectRatio.RATIO_1x1:
            return 1.0
        return 1.666


class IndexCard:
    """Modelo y controlador de una Ficha de Índice individual."""

    def __init__(self, item: BinderItem, card_number: Optional[int] = None):
        self.item = item
        self.uuid: str = item.uuid
        self.title: str = item.title
        self.synopsis: str = item.read_synopsis() if getattr(item, "project", None) else ""
        self.card_number: Optional[int] = card_number
        self.show_number: bool = True

        # Opciones visuales del cuerpo
        self.notebook_lines: bool = True
        self.image_path: Optional[str] = None

        # Etiqueta (Label)
        self.label_id: int = item.data.label_id if hasattr(item, "data") else -1
        self.label_name: str = "Sin Etiqueta"
        self.label_color: str = "#2D72D9"  # Color hex o rgba
        self.label_style: LabelColorStyle = LabelColorStyle.PIN

        # Estado y Sello diagonal (Status Stamp)
        self.status_id: int = item.data.status_id if hasattr(item, "data") else -1
        self.status_name: str = "Borrador"
        self.show_status_stamp: bool = True
        self.status_stamp_text: str = "BORRADOR"

        # Palabras clave (Keywords)
        self.keywords: List[str] = list(item.data.keywords) if hasattr(item, "data") and item.data.keywords else []
        self.keyword_colors: Dict[str, str] = {}
        for kw in self.keywords:
            self.keyword_colors[kw] = self._generate_keyword_color(kw)

        # Posición espacial para el Modo Forma Libre (Freeform)
        self.freeform_x: float = 0.0
        self.freeform_y: float = 0.0

        # Metadatos del nodo
        self.icon_name: str = getattr(item.data, "icon_file_name", "document.svg") or "document.svg"

    @classmethod
    def from_binder_item(cls, item: BinderItem, card_number: Optional[int] = None) -> 'IndexCard':
        return cls(item, card_number=card_number)

    def _generate_keyword_color(self, keyword: str) -> str:
        """Genera un color cromático determinista y agradable para cada palabra clave."""
        h = sum(ord(c) for c in keyword) % 360
        palette = ["#EF4444", "#F59E0B", "#10B981", "#3B82F6", "#8B5CF6", "#EC4899", "#14B8A6"]
        return palette[h % len(palette)]

    # =========================================================================
    # Edición In-Situ de Título y Sinopsis
    # =========================================================================

    def set_title(self, new_title: str) -> str:
        """Edita directamente el título con actualización inmediata en el BinderItem."""
        clean_title = new_title.strip()
        if clean_title:
            self.title = clean_title
            self.item.title = clean_title
            if hasattr(self.item, "data"):
                self.item.data.title = clean_title
            self.item.mark_dirty()
        return self.title

    def set_synopsis(self, new_text: str) -> str:
        """Edita la sinopsis con persistencia atómica en synopsis.txt del nodo."""
        self.synopsis = new_text
        if getattr(self.item, "project", None):
            self.item.write_synopsis(new_text)
            self.item.save_if_dirty()
        return self.synopsis

    # =========================================================================
    # Metadatos: Etiqueta, Estado, Imagen y Keywords
    # =========================================================================

    def set_label(self, label_id: int, label_name: str, color_hex: str):
        self.label_id = label_id
        self.label_name = label_name
        self.label_color = color_hex
        if hasattr(self.item, "data"):
            self.item.data.label_id = label_id
            self.item.mark_dirty()

    def set_status(self, status_id: int, status_name: str):
        self.status_id = status_id
        self.status_name = status_name
        self.status_stamp_text = status_name.upper()
        if hasattr(self.item, "data"):
            self.item.data.status_id = status_id
            self.item.mark_dirty()

    def set_image(self, image_path: Optional[str]):
        """Asocia o elimina una imagen en lugar de texto en el cuerpo de la tarjeta."""
        self.image_path = image_path

    def add_keyword(self, keyword: str, color: Optional[str] = None):
        kw_clean = keyword.strip()
        if kw_clean and kw_clean not in self.keywords:
            self.keywords.append(kw_clean)
            self.keyword_colors[kw_clean] = color or self._generate_keyword_color(kw_clean)
            if hasattr(self.item, "data"):
                self.item.data.keywords = self.keywords
                self.item.mark_dirty()

    def remove_keyword(self, keyword: str):
        if keyword in self.keywords:
            self.keywords.remove(keyword)
            self.keyword_colors.pop(keyword, None)
            if hasattr(self.item, "data"):
                self.item.data.keywords = self.keywords
                self.item.mark_dirty()

    def set_freeform_position(self, x: float, y: float):
        self.freeform_x = x
        self.freeform_y = y

    # =========================================================================
    # Exportación de Datos para la Capa de Presentación
    # =========================================================================

    def get_render_data(self) -> Dict[str, Any]:
        return {
            "uuid": self.uuid,
            "title": self.title,
            "card_number": self.card_number,
            "show_number": self.show_number,
            "icon": self.icon_name,
            "synopsis": self.synopsis,
            "has_image": self.image_path is not None,
            "image_path": self.image_path,
            "notebook_lines": self.notebook_lines,
            "label": {
                "id": self.label_id,
                "name": self.label_name,
                "color": self.label_color,
                "style": self.label_style.value
            },
            "status": {
                "id": self.status_id,
                "name": self.status_name,
                "show_stamp": self.show_status_stamp,
                "stamp_text": self.status_stamp_text
            },
            "keywords": [
                {"name": kw, "color": self.keyword_colors.get(kw, "#3B82F6")}
                for kw in self.keywords
            ],
            "freeform_pos": (self.freeform_x, self.freeform_y)
        }
