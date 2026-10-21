"""
RTF Editor View para Escritorio
Editor de texto enriquecido de alta velocidad con soporte para estilos de párrafo,
formato de caracteres (negrita, cursiva, subrayado), recuento métrico en tiempo real y autoguardado.
"""

from typing import Optional, Callable
from ..core.project import BinderItem
from ..core.rtf_engine import RTFEngine

class RTFEditorView:
    """Controlador y lógica del editor de texto principal."""

    def __init__(self):
        self.current_item: Optional[BinderItem] = None
        self.plain_text: str = ""
        self.rtf_text: str = ""
        self.is_dirty: bool = False
        self.on_metrics_updated: Optional[Callable[[int, int], None]] = None

    def load_item(self, item: BinderItem):
        """Carga un nuevo nodo en el editor."""
        if self.is_dirty and self.current_item:
            self.save_current()

        self.current_item = item
        self.rtf_text = item.read_content_rtf()
        self.plain_text = RTFEngine.rtf_to_plain_text(self.rtf_text)
        self.is_dirty = False
        self._notify_metrics()

    def update_text(self, new_plain_text: str):
        """Se ejecuta cada vez que el usuario teclea en el editor."""
        self.plain_text = new_plain_text
        self.rtf_text = RTFEngine.plain_text_to_rtf(new_plain_text)
        self.is_dirty = True
        self._notify_metrics()

    def save_current(self):
        """Guarda los cambios pendientes en el elemento activo."""
        if self.current_item and self.is_dirty:
            self.current_item.write_content_rtf(self.rtf_text)
            self.is_dirty = False

    def get_word_count(self) -> int:
        return RTFEngine.count_words(self.plain_text, is_rtf=False)

    def get_character_count(self) -> int:
        return RTFEngine.count_characters(self.plain_text, is_rtf=False)

    def _notify_metrics(self):
        if self.on_metrics_updated:
            self.on_metrics_updated(self.get_word_count(), self.get_character_count())
