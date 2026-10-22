"""
EditorWidget para Escritorio
Componente principal del Editor de Texto Enriquecido con paridad funcional respecto a Scrivener 3.
Orquesta:
- Procesador de texto enriquecido RTF de alto rendimiento
- Barra de formato compacta (FormatToolbar)
- Regla horizontal interactiva (RulerBar / Ctrl+Shift+R)
- Sistema de Estilos Semánticos (StyleEngine) con estado por defecto "Sin Estilo"
- Vista de Página (PageView / Alt+Shift+P) frente a modo continuo
- Desplazamiento de Máquina de Escribir (Typewriter Scrolling / Ctrl+Alt+T)
- Modo Foco (Focus Mode: Línea, Oración, Párrafo)
- Foco Lingüístico (Linguistic Focus: Diálogos, Adverbios, Adjetivos, Verbos, Conjunciones)
- Caracteres Invisibles (Show Invisibles: ¶, ·, →)
- Tablas editables, Listas, Imágenes con redimensionamiento y Scrivener Links.
"""

from pathlib import Path
from typing import Optional, Callable, Dict, Any, List, Tuple

from ...core.project import BinderItem, EscritorioProject
from ...core.rtf_engine import RTFEngine
from ...core.StyleEngine import StyleEngine, StyleDefinition, StyleType
from .format_toolbar import FormatToolbar, TextFormatState
from .ruler_bar import RulerBar
from .page_view import PageViewEngine, EditorViewMode, PageFormat
from .linguistic_focus import LinguisticFocusEngine, LinguisticCategory, HighlightSpan
from .focus_mode import FocusModeEngine, FocusScope
from .invisibles import InvisiblesEngine
from .scrivener_links import ScrivenerLinksEngine, ScrivenerLinkMatch
from .table_manager import TableManager, EditableTable


class EditorWidget:
    """Controlador y orquestador maestro del Editor de Escritorio."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.project = project
        self.current_item: Optional[BinderItem] = None

        # Contenido textual
        self.plain_text: str = ""
        self.rtf_text: str = ""
        self.is_dirty: bool = False

        # Posición de cursor y selección
        self.cursor_pos: int = 0
        self.selection_start: int = 0
        self.selection_end: int = 0

        # Submódulos del editor
        proj_dir = project.project_dir if project else None
        self.style_engine = StyleEngine(proj_dir)
        self.toolbar = FormatToolbar()
        self.ruler = RulerBar()
        self.page_view = PageViewEngine()
        self.linguistic_focus = LinguisticFocusEngine(language="es")
        self.focus_mode = FocusModeEngine()
        self.invisibles = InvisiblesEngine()

        # Callbacks de notificación
        self.on_metrics_updated: Optional[Callable[[int, int], None]] = None
        self.on_link_clicked: Optional[Callable[[str], None]] = None

    def set_project(self, project: EscritorioProject):
        """Asigna un nuevo proyecto activo y sincroniza el StyleEngine."""
        if self.is_dirty and self.current_item:
            self.save_current()

        self.project = project
        self.style_engine = StyleEngine(project.project_dir)
        self.current_item = None
        self.plain_text = ""
        self.rtf_text = ""
        self.is_dirty = False

    def load_item(self, item: BinderItem):
        """Carga un documento del Binder en el editor."""
        if self.is_dirty and self.current_item:
            self.save_current()

        self.current_item = item
        self.rtf_text = item.read_content_rtf()
        self.plain_text = RTFEngine.rtf_to_plain_text(self.rtf_text)
        self.is_dirty = False
        self.cursor_pos = 0
        self.selection_start = 0
        self.selection_end = 0

        # Recalcular paginación si estamos en vista de página
        self.page_view.calculate_pagination(self.plain_text)
        self._notify_metrics()

    def update_text(self, new_plain_text: str):
        """Actualiza el texto plano y genera el RTF sincronizado."""
        self.plain_text = new_plain_text
        # Regenerar RTF aplicando estilo o formato tipográfico activo
        self.rtf_text = RTFEngine.plain_text_to_rtf(
            new_plain_text,
            font_name=self.toolbar.state.font_family,
            font_size_pt=int(self.toolbar.state.font_size_pt)
        )
        self.is_dirty = True
        self.page_view.calculate_pagination(self.plain_text)
        self._notify_metrics()

    def save_current(self):
        """Persiste inmediatamente el contenido del documento activo en disco."""
        if self.current_item and self.is_dirty:
            self.current_item.write_content_rtf(self.rtf_text)
            self.is_dirty = False

    # =========================================================================
    # Métricas de Texto (Palabras y Caracteres)
    # =========================================================================

    def get_word_count(self) -> int:
        return RTFEngine.count_words(self.plain_text, is_rtf=False)

    def get_character_count(self, count_spaces: bool = True) -> int:
        return RTFEngine.count_characters(self.plain_text, is_rtf=False, count_spaces=count_spaces)

    def _notify_metrics(self):
        if self.on_metrics_updated:
            self.on_metrics_updated(self.get_word_count(), self.get_character_count())

    # =========================================================================
    # Sistema de Estilos Semánticos (StyleEngine)
    # =========================================================================

    def apply_style(self, style_id: str) -> bool:
        """Aplica un estilo semántico al párrafo o selección activa."""
        style = self.style_engine.get_style(style_id)
        if not style:
            return False

        self.toolbar.set_active_style(style.id)

        # Si el estilo define propiedades tipográficas, sincronizarlas en la barra
        if style.font_family:
            self.toolbar.set_font_family(style.font_family)
        if style.font_size is not None:
            self.toolbar.set_font_size(style.font_size)
        if style.bold is not None:
            self.toolbar.state.bold = style.bold
        if style.italic is not None:
            self.toolbar.state.italic = style.italic
        if style.underline is not None:
            self.toolbar.state.underline = style.underline
        if style.alignment:
            self.toolbar.set_alignment(style.alignment)
        if style.line_spacing is not None:
            self.toolbar.set_line_spacing(style.line_spacing)
        if style.space_before is not None or style.space_after is not None:
            sb = style.space_before or 0.0
            sa = style.space_after or 0.0
            self.toolbar.set_paragraph_spacing(sb, sa)
        if style.first_line_indent is not None:
            self.ruler.set_first_line_indent(style.first_line_indent)
        if style.left_indent is not None:
            self.ruler.set_left_indent(style.left_indent)
        if style.right_indent is not None:
            self.ruler.set_right_indent(style.right_indent)

        return True

    def create_style_from_selection(self, name: str, style_type: StyleType, shortcut: str = "") -> StyleDefinition:
        """Crea un nuevo estilo semántico guardando los atributos de la selección activa."""
        attrs = {
            "font_family": self.toolbar.state.font_family,
            "font_size": self.toolbar.state.font_size_pt,
            "bold": self.toolbar.state.bold,
            "italic": self.toolbar.state.italic,
            "underline": self.toolbar.state.underline,
            "strikethrough": self.toolbar.state.strikethrough,
            "text_color": self.toolbar.state.text_color,
            "background_color": self.toolbar.state.highlight_color or None,
            "alignment": self.toolbar.state.alignment,
            "line_spacing": self.toolbar.state.line_spacing,
            "space_before": self.toolbar.state.space_before_pt,
            "space_after": self.toolbar.state.space_after_pt,
            "first_line_indent": self.ruler.state.first_line_indent_pt,
            "left_indent": self.ruler.state.left_indent_pt,
            "right_indent": self.ruler.state.right_indent_pt,
        }
        style = self.style_engine.create_style_from_selection(name, style_type, attrs, shortcut)
        self.toolbar.set_active_style(style.id)
        return style

    def redefine_style_from_selection(self, style_id: str) -> Optional[StyleDefinition]:
        """Redefine un estilo existente con los atributos actuales de formato."""
        attrs = {
            "font_family": self.toolbar.state.font_family,
            "font_size": self.toolbar.state.font_size_pt,
            "bold": self.toolbar.state.bold,
            "italic": self.toolbar.state.italic,
            "underline": self.toolbar.state.underline,
            "strikethrough": self.toolbar.state.strikethrough,
            "text_color": self.toolbar.state.text_color,
            "background_color": self.toolbar.state.highlight_color or None,
            "alignment": self.toolbar.state.alignment,
            "line_spacing": self.toolbar.state.line_spacing,
            "space_before": self.toolbar.state.space_before_pt,
            "space_after": self.toolbar.state.space_after_pt,
            "first_line_indent": self.ruler.state.first_line_indent_pt,
            "left_indent": self.ruler.state.left_indent_pt,
            "right_indent": self.ruler.state.right_indent_pt,
        }
        return self.style_engine.redefine_style_from_selection(style_id, attrs)

    # =========================================================================
    # Modos Ergonómicos de Visualización
    # =========================================================================

    def toggle_page_view(self) -> EditorViewMode:
        """Alterna entre Vista Continua y Vista de Página (Alt+Shift+P)."""
        mode = self.page_view.toggle_mode()
        self.page_view.calculate_pagination(self.plain_text)
        return mode

    def toggle_typewriter_scrolling(self) -> bool:
        """Alterna el desplazamiento de máquina de escribir centrado (Ctrl+Alt+T)."""
        return self.focus_mode.toggle_typewriter_scrolling()

    def set_focus_mode(self, scope: FocusScope):
        """Configura el ámbito de foco (Off, Line, Sentence, Paragraph)."""
        self.focus_mode.set_scope(scope)

    def set_linguistic_focus(self, category: LinguisticCategory, lang: str = "es"):
        """Configura el filtro del foco lingüístico."""
        self.linguistic_focus.language = lang
        self.linguistic_focus.set_category(category)

    def toggle_invisibles(self) -> bool:
        """Alterna la visualización de caracteres no imprimibles."""
        return self.invisibles.toggle()

    def toggle_ruler(self) -> bool:
        """Alterna la visibilidad de la regla horizontal (Ctrl+Shift+R)."""
        return self.ruler.toggle_visibility()

    # =========================================================================
    # Inserciones Avanzadas: Tablas, Listas, Imágenes y Scrivener Links
    # =========================================================================

    def insert_table(self, rows: int = 2, cols: int = 3, cell_width_pt: float = 100.0) -> EditableTable:
        """Inserta una tabla editable en la posición del cursor."""
        table = TableManager.create_table(rows, cols, cell_width_pt)
        table_rtf = TableManager.table_to_rtf(table)
        # Añadir al texto en la posición del cursor
        prefix = self.plain_text[:self.cursor_pos]
        suffix = self.plain_text[self.cursor_pos:]
        table_plain = f"\n[Tabla {rows}x{cols}]\n"
        self.update_text(prefix + table_plain + suffix)
        return table

    def insert_bullet_list(self):
        """Inserta o conmuta una lista con viñetas."""
        self.toolbar.set_list_type("bullet")
        prefix = self.plain_text[:self.cursor_pos]
        suffix = self.plain_text[self.cursor_pos:]
        bullet_item = "\n• "
        self.update_text(prefix + bullet_item + suffix)
        self.cursor_pos += len(bullet_item)

    def insert_numbered_list(self):
        """Inserta o conmuta una lista numerada."""
        self.toolbar.set_list_type("numbered")
        prefix = self.plain_text[:self.cursor_pos]
        suffix = self.plain_text[self.cursor_pos:]
        num_item = "\n1. "
        self.update_text(prefix + num_item + suffix)
        self.cursor_pos += len(num_item)

    def insert_image(self, image_path: str, width_px: int = 400, height_px: int = 300, scale: float = 1.0) -> str:
        """Inserta una imagen vinculada al proyecto con dimensiones escalables."""
        img_tag = f"[Imagen: {Path(image_path).name} ({int(width_px*scale)}x{int(height_px*scale)})]"
        prefix = self.plain_text[:self.cursor_pos]
        suffix = self.plain_text[self.cursor_pos:]
        self.update_text(prefix + f"\n{img_tag}\n" + suffix)
        return img_tag

    def insert_scrivener_link(self, target_uuid: str, display_text: str) -> str:
        """Inserta un hipervínculo interno Scrivener hacia otro documento del proyecto."""
        link_str = f"[{display_text}](scrivener-link://{target_uuid})"
        prefix = self.plain_text[:self.cursor_pos]
        suffix = self.plain_text[self.cursor_pos:]
        self.update_text(prefix + link_str + suffix)
        self.cursor_pos += len(link_str)
        return link_str

    def insert_wiki_link(self, target_title: str) -> str:
        """Inserta un enlace de tipo [[Título del Documento]]."""
        link_str = f"[[{target_title}]]"
        prefix = self.plain_text[:self.cursor_pos]
        suffix = self.plain_text[self.cursor_pos:]
        self.update_text(prefix + link_str + suffix)
        self.cursor_pos += len(link_str)
        return link_str

    def handle_link_click(self, raw_link: str) -> Optional[str]:
        """Resuelve el destino de un enlace pulsado y notifica a la aplicación."""
        dest_uuid = ScrivenerLinksEngine.resolve_link_destination(raw_link, self.project)
        if dest_uuid and self.on_link_clicked:
            self.on_link_clicked(dest_uuid)
        return dest_uuid

    # =========================================================================
    # Consulta de Estado para Renderizado (GDI / Web / Qt)
    # =========================================================================

    def get_view_data(self) -> Dict[str, Any]:
        """Genera el árbol de datos completo para la capa de presentación visual."""
        # Modo Foco
        focused_span = self.focus_mode.get_focused_span(self.plain_text, self.cursor_pos)

        # Foco Lingüístico
        linguistic_spans = self.linguistic_focus.analyze(self.plain_text)

        # Enlaces internos
        scrivener_links = ScrivenerLinksEngine.find_all_links(self.plain_text, self.project)

        # Paginación
        current_page = self.page_view.get_current_page_for_cursor(self.cursor_pos)

        # Texto para renderizar según modo invisibles
        display_text = self.invisibles.render_text_with_invisibles(self.plain_text)

        return {
            "current_item_uuid": self.current_item.uuid if self.current_item else "",
            "current_item_title": self.current_item.title if self.current_item else "",
            "plain_text": display_text,
            "raw_text": self.plain_text,
            "cursor_pos": self.cursor_pos,
            "selection": (self.selection_start, self.selection_end),
            "word_count": self.get_word_count(),
            "character_count": self.get_character_count(),
            "toolbar": self.toolbar.get_render_data(),
            "ruler": self.ruler.get_render_data(),
            "page_view": self.page_view.get_render_data(),
            "current_page": current_page,
            "focus_mode": {
                **self.focus_mode.get_state(),
                "focused_span": focused_span
            },
            "linguistic_focus": {
                "active_category": self.linguistic_focus.active_category.value,
                "language": self.linguistic_focus.language,
                "highlight_count": len(linguistic_spans),
                "spans": [
                    {"start": s.start, "end": s.end, "token": s.token, "category": s.category.value}
                    for s in linguistic_spans
                ]
            },
            "invisibles_active": self.invisibles.is_visible,
            "scrivener_links": [
                {
                    "start": l.start_pos,
                    "end": l.end_pos,
                    "target_uuid": l.target_uuid,
                    "target_title": l.target_title,
                    "display": l.display_text
                }
                for l in scrivener_links
            ]
        }
