"""
Corkboard Footer Bar para Escritorio
Barra inferior ultra-compacta de control del Corcho para ajuste en vivo:
- Tamaño de tarjeta (Card Size: Small, Medium, Large o píxeles directos)
- Ratio de aspecto (3x5, 4x6, 1:1)
- Espaciado entre fichas (Spacing)
- Tarjetas por fila (Auto o 1 a 10)
- Conmutadores de sellos, pines, líneas de libreta y chips de palabras clave
"""

from typing import Dict, Any, Callable, Optional
from .index_card import CardAspectRatio, LabelColorStyle


class CorkboardFooterBar:
    """Controlador y estado de la barra de herramientas inferior del Corcho."""

    def __init__(self):
        # Dimensiones y disposición
        self.card_size_px: float = 220.0
        self.aspect_ratio: CardAspectRatio = CardAspectRatio.RATIO_3x5
        self.spacing_px: float = 16.0
        self.cards_per_row: int = 0  # 0 = 'Auto'

        # Conmutadores visuales
        self.show_status_stamps: bool = True
        self.show_pins: bool = True
        self.show_notebook_lines: bool = True
        self.show_keyword_chips: bool = True
        self.show_card_numbers: bool = True
        self.label_style: LabelColorStyle = LabelColorStyle.PIN

        # Callback cuando se modifica un parámetro
        self.on_settings_changed: Optional[Callable[[], None]] = None

    def set_card_size(self, size_px: float):
        self.card_size_px = max(120.0, min(500.0, size_px))
        self._notify()

    def set_aspect_ratio(self, ratio: CardAspectRatio):
        self.aspect_ratio = ratio
        self._notify()

    def set_spacing(self, spacing_px: float):
        self.spacing_px = max(4.0, min(48.0, spacing_px))
        self._notify()

    def set_cards_per_row(self, count: int):
        """0 para Auto, o entre 1 y 10."""
        self.cards_per_row = max(0, min(10, count))
        self._notify()

    def toggle_status_stamps(self) -> bool:
        self.show_status_stamps = not self.show_status_stamps
        self._notify()
        return self.show_status_stamps

    def toggle_pins(self) -> bool:
        self.show_pins = not self.show_pins
        self._notify()
        return self.show_pins

    def toggle_notebook_lines(self) -> bool:
        self.show_notebook_lines = not self.show_notebook_lines
        self._notify()
        return self.show_notebook_lines

    def toggle_keyword_chips(self) -> bool:
        self.show_keyword_chips = not self.show_keyword_chips
        self._notify()
        return self.show_keyword_chips

    def toggle_card_numbers(self) -> bool:
        self.show_card_numbers = not self.show_card_numbers
        self._notify()
        return self.show_card_numbers

    def set_label_style(self, style: LabelColorStyle):
        self.label_style = style
        self._notify()

    def _notify(self):
        if self.on_settings_changed:
            self.on_settings_changed()

    def get_state(self) -> Dict[str, Any]:
        return {
            "card_size_px": self.card_size_px,
            "aspect_ratio": self.aspect_ratio.value,
            "spacing_px": self.spacing_px,
            "cards_per_row": "Auto" if self.cards_per_row == 0 else self.cards_per_row,
            "show_status_stamps": self.show_status_stamps,
            "show_pins": self.show_pins,
            "show_notebook_lines": self.show_notebook_lines,
            "show_keyword_chips": self.show_keyword_chips,
            "show_card_numbers": self.show_card_numbers,
            "label_style": self.label_style.value
        }
