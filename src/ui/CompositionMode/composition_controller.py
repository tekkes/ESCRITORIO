"""
Composition Mode Controller para Escritorio.
Orquestador maestro del modo de redacción libre de distracciones a pantalla completa (F11):
- Pantalla completa sin bordes en Windows 11.
- Hoja de papel central de ancho, posición y zoom ajustables.
- Textura / imagen de fondo personalizada con atenuación continua (Background Fade).
- Barra de control inferior auto-ocultable al acercar el ratón.
- Selector rápido 'Go To' para saltar a cualquier escena del Binder sin salir del modo inmersivo.
- Inspector flotante translúcido HUD y contador de palabras en vivo.
"""

from typing import Optional, Dict, Any, List, Callable
from pathlib import Path

from ...core.project import BinderItem, EscritorioProject
from ...core.rtf_engine import RTFEngine
from .paper_settings import CompositionPaperSettings, PaperPosition
from .bottom_control_bar import BottomControlBar, GoToItem


class CompositionMode:
    """Controlador del Modo Composición libre de distracciones."""

    def __init__(
        self,
        project_or_editor: Optional[Any] = None,
        active_item: Optional[BinderItem] = None,
        editor: Optional[Any] = None
    ):
        if hasattr(project_or_editor, "get_draft_folder") or hasattr(project_or_editor, "project_dir"):
            self.project: Optional[EscritorioProject] = project_or_editor
            self.editor: Optional[Any] = editor
        else:
            self.editor: Optional[Any] = project_or_editor
            self.project: Optional[EscritorioProject] = getattr(project_or_editor, "project", None) if project_or_editor else None

        self.active_item: Optional[BinderItem] = active_item

        # Estado del modo inmersivo
        self.is_active: bool = False

        # Configuración de hoja y fondo
        self.paper_settings = CompositionPaperSettings()

        # Barra de control inferior
        self.control_bar = BottomControlBar()

        # Callbacks de navegación y guardado
        self.on_scene_changed: Optional[Callable[[BinderItem], None]] = None
        self.on_exit: Optional[Callable[[], None]] = None

        if self.project and hasattr(self.project, "get_draft_folder"):
            self._sync_goto_tree()

    @property
    def backdrop_opacity(self) -> float:
        return self.paper_settings.background_fade

    @backdrop_opacity.setter
    def backdrop_opacity(self, val: float):
        self.paper_settings.background_fade = max(0.0, min(1.0, float(val)))

    @property
    def paper_width_percent(self) -> int:
        return self.paper_settings.paper_width_percent

    @paper_width_percent.setter
    def paper_width_percent(self, val: int):
        self.paper_settings.paper_width_percent = max(30, min(100, int(val)))

    @property
    def typewriter_scrolling(self) -> bool:
        return self.paper_settings.typewriter_scrolling

    @typewriter_scrolling.setter
    def typewriter_scrolling(self, val: bool):
        self.paper_settings.typewriter_scrolling = bool(val)

    @property
    def paper_color(self) -> str:
        return self.paper_settings.paper_color

    @paper_color.setter
    def paper_color(self, val: str):
        self.paper_settings.paper_color = val

    @property
    def text_color(self) -> str:
        return self.paper_settings.text_color

    @text_color.setter
    def text_color(self, val: str):
        self.paper_settings.text_color = val

    def set_backdrop_opacity(self, opacity: float):
        self.backdrop_opacity = opacity

    def set_paper_width(self, width_percent: int):
        self.paper_width_percent = width_percent

    # =========================================================================
    # Ciclo de Vida (F11)
    # =========================================================================

    def enter(self):
        """Activa el modo a pantalla completa sin distracciones."""
        self.is_active = True
        self._sync_goto_tree()
        self.refresh_metrics()

    def exit(self):
        """Sale del modo a pantalla completa y regresa a la ventana tripartita."""
        self.is_active = False
        self.control_bar.is_visible = False
        self.control_bar.is_goto_menu_open = False
        if self.on_exit:
            self.on_exit()

    def toggle(self) -> bool:
        """Atajo F11 para conmutar el Modo Composición."""
        if self.is_active:
            self.exit()
        else:
            self.enter()
        return self.is_active

    # =========================================================================
    # Sincronización del Documento y Binder
    # =========================================================================

    def set_item(self, item: Optional[BinderItem]):
        self.active_item = item
        if not self.project and item and getattr(item, "project", None):
            self.project = item.project
        self._sync_goto_tree()
        self.refresh_metrics()

    def set_project(self, project: EscritorioProject):
        self.project = project
        self._sync_goto_tree()

    def _sync_goto_tree(self):
        """Puebla la lista de escenas del Binder para el menú emergente Go To."""
        if not self.project or not hasattr(self.project, "get_draft_folder"):
            return

        items: List[GoToItem] = []

        def traverse(node: BinderItem, depth: int):
            # Obtener conteo aproximado de palabras si es texto
            words = 0
            if node.item_type.lower() == "text":
                content = node.read_content_rtf()
                words = len(RTFEngine.rtf_to_plain_text(content).split())

            items.append(GoToItem(
                uuid=node.uuid,
                title=node.title,
                item_type=node.item_type,
                level=depth,
                word_count=words
            ))
            for child in node.children:
                traverse(child, depth + 1)

        draft = self.project.get_draft_folder()
        if draft:
            for child in draft.children:
                traverse(child, 0)

        self.control_bar.set_goto_items(items)

    def go_to_scene(self, scene_uuid: str) -> Optional[BinderItem]:
        """Salta a cualquier escena del proyecto directamente desde el modo composición."""
        if not self.project or not hasattr(self.project, "get_item"):
            return None

        target = self.project.get_item(scene_uuid)
        if target:
            self.active_item = target
            self.refresh_metrics()
            self.control_bar.is_goto_menu_open = False
            if self.on_scene_changed:
                self.on_scene_changed(target)
            return target
        return None

    # =========================================================================
    # Métricas y Typewriter Scrolling
    # =========================================================================

    def refresh_metrics(self):
        """Calcula palabras y caracteres del documento activo y actualiza la barra."""
        if not self.active_item:
            self.control_bar.update_live_metrics(0, 0)
            return

        rtf = self.active_item.read_content_rtf()
        text = RTFEngine.rtf_to_plain_text(rtf)
        words = len(text.split())
        chars = len(text)
        self.control_bar.update_live_metrics(words, chars)

    def calculate_typewriter_scroll_offset(
        self,
        caret_line_index: int,
        total_lines: int,
        line_height_px: int,
        viewport_height_px: int
    ) -> int:
        """
        Calcula el desplazamiento vertical para mantener la línea activa
        exactamente en el centro vertical de la pantalla (50% de la altura).
        """
        if not self.paper_settings.typewriter_scrolling:
            return 0

        caret_y = caret_line_index * line_height_px
        half_screen = viewport_height_px // 2
        # Queremos que caret_y quede en half_screen -> scroll = caret_y - half_screen
        return max(0, caret_y - half_screen)

    # =========================================================================
    # Métodos de Acceso Rápido y Compatibilidad
    # =========================================================================

    def set_paper_width(self, width_percent: int):
        self.paper_settings.set_paper_width(width_percent)

    def set_paper_position(self, pos: PaperPosition):
        self.paper_settings.set_position(pos)

    def set_background_fade(self, fade: float):
        self.paper_settings.set_background_fade(fade)

    def set_background_image(self, path: Optional[str]):
        self.paper_settings.set_background_image(path)

    def set_text_zoom(self, zoom: int):
        self.paper_settings.set_text_zoom(zoom)

    def toggle_typewriter_scrolling(self) -> bool:
        self.paper_settings.typewriter_scrolling = not self.paper_settings.typewriter_scrolling
        return self.paper_settings.typewriter_scrolling

    def toggle_inspector_hud(self) -> bool:
        return self.control_bar.toggle_inspector_hud()

    def on_mouse_move(self, cursor_y: int, screen_height: int) -> bool:
        """Notificación de movimiento de ratón para mostrar/ocultar la barra inferior."""
        return self.control_bar.update_cursor_position(cursor_y, screen_height)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_active": self.is_active,
            "document_uuid": self.active_item.uuid if self.active_item else None,
            "document_title": self.active_item.title if self.active_item else "Sin selección",
            "paper": self.paper_settings.to_dict(),
            "control_bar": self.control_bar.to_dict()
        }
