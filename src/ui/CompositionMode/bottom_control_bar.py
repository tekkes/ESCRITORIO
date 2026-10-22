"""
Bottom Control Bar para el Modo Composición de Escritorio.
Barra de control auto-ocultable que emerge al acercar el cursor al borde inferior de la pantalla.
Contiene controles ergonómicos de ancho de papel, posición, zoom, fundido, Go To, Inspector y métricas en vivo.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class GoToItem:
    uuid: str
    title: str
    item_type: str = "Text"
    level: int = 0
    word_count: int = 0


class BottomControlBar:
    """Controlador y estado de la barra flotante inferior auto-ocultable."""

    def __init__(self, height_px: int = 48, trigger_zone_px: int = 56):
        self.height_px = height_px
        self.trigger_zone_px = trigger_zone_px

        # Visibilidad automática (auto-hide)
        self.is_visible: bool = False
        self.is_pinned: bool = False

        # Estado del Inspector flotante
        self.is_inspector_hud_open: bool = False

        # Menú Go To
        self.is_goto_menu_open: bool = False
        self.goto_items: List[GoToItem] = []

        # Métricas en vivo
        self.current_words: int = 0
        self.current_characters: int = 0
        self.session_words: int = 0
        self.session_target: int = 1500

    def update_cursor_position(self, cursor_y: int, screen_height: int) -> bool:
        """
        Determina si la barra debe mostrarse u ocultarse según la posición Y del ratón.
        Retorna True si cambió el estado de visibilidad.
        """
        if self.is_pinned:
            if not self.is_visible:
                self.is_visible = True
                return True
            return False

        should_show = cursor_y >= (screen_height - self.trigger_zone_px)
        if should_show != self.is_visible:
            self.is_visible = should_show
            if not should_show:
                self.is_goto_menu_open = False
            return True
        return False

    def toggle_pin(self) -> bool:
        """Fija la barra para que no se oculte automáticamente."""
        self.is_pinned = not self.is_pinned
        if self.is_pinned:
            self.is_visible = True
        return self.is_pinned

    def toggle_inspector_hud(self) -> bool:
        """Abre o cierra el panel flotante translúcido del Inspector en modo composición."""
        self.is_inspector_hud_open = not self.is_inspector_hud_open
        return self.is_inspector_hud_open

    def toggle_goto_menu(self) -> bool:
        """Abre o cierra el menú emergente Go To para saltar a cualquier escena."""
        self.is_goto_menu_open = not self.is_goto_menu_open
        return self.is_goto_menu_open

    def set_goto_items(self, items: List[GoToItem]):
        self.goto_items = items

    @property
    def goto_tree(self) -> List[GoToItem]:
        return self.goto_items

    def update_live_metrics(self, doc_words: int, doc_chars: int, session_words: int = 0, session_target: int = 1500):
        self.current_words = doc_words
        self.current_characters = doc_chars
        self.session_words = session_words
        self.session_target = session_target

    def to_dict(self) -> Dict[str, Any]:
        return {
            "height_px": self.height_px,
            "trigger_zone_px": self.trigger_zone_px,
            "is_visible": self.is_visible,
            "is_pinned": self.is_pinned,
            "is_inspector_hud_open": self.is_inspector_hud_open,
            "is_goto_menu_open": self.is_goto_menu_open,
            "goto_count": len(self.goto_items),
            "current_words": self.current_words,
            "current_characters": self.current_characters,
            "session_words": self.session_words,
            "session_target": self.session_target
        }
