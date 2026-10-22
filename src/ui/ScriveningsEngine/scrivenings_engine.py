"""
ScriveningsEngine para Escritorio
Motor de edición continua de manuscritos compuestos con paridad funcional respecto a Scrivener 3.
Permite:
- Concatenar virtualmente múltiples documentos seleccionados o carpetas enteras en una sola vista continua.
- Encabezados de sección editables in-situ con sincronización al título del nodo.
- Separadores configurables (línea sutil, esquinas recortadas o salto de página).
- Mapeo bidireccional de rangos y sincronización transparente e individual en content.rtf de cada ítem.
"""

from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass
from pathlib import Path

from ...core.project import BinderItem, EscritorioProject
from ...core.rtf_engine import RTFEngine
from .scrivenings_divider import DividerStyle, ScriveningsDivider


@dataclass
class ScriveningsSection:
    item: BinderItem
    uuid: str
    title: str
    raw_content: str
    header_start: int = 0
    header_end: int = 0
    content_start: int = 0
    content_end: int = 0
    divider_start: int = 0
    divider_end: int = 0
    is_dirty: bool = False

    @property
    def word_count(self) -> int:
        return RTFEngine.count_words(self.raw_content, is_rtf=False)

    @property
    def character_count(self) -> int:
        return RTFEngine.count_characters(self.raw_content, is_rtf=False)


class ScriveningsEngine:
    """Motor central para la gestión del Modo Scrivenings (Ctrl+1)."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.project = project
        self.sections: List[ScriveningsSection] = []
        self.composite_text: str = ""
        self.divider_style: DividerStyle = DividerStyle.SUBTLE_LINE
        self.show_section_titles: bool = True
        self.show_section_numbers: bool = True
        self.is_active: bool = False

        # Callbacks
        self.on_title_changed: Optional[Callable[[str, str], None]] = None
        self.on_content_saved: Optional[Callable[[str], None]] = None

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def load_from_binder_items(self, items: List[BinderItem]):
        """
        Carga una lista de BinderItems en el modo Scrivenings.
        Si algún ítem es una carpeta o tiene hijos, recopila todos los documentos
        descendientes en orden narrativo.
        """
        flattened_items: List[BinderItem] = []
        for item in items:
            flattened_items.extend(self._flatten_item(item))

        # Evitar duplicados manteniendo orden
        seen_uuids = set()
        unique_items = []
        for it in flattened_items:
            if it.uuid not in seen_uuids:
                seen_uuids.add(it.uuid)
                unique_items.append(it)

        self.sections.clear()
        for it in unique_items:
            rtf = it.read_content_rtf()
            plain = RTFEngine.rtf_to_plain_text(rtf)
            sec = ScriveningsSection(
                item=it,
                uuid=it.uuid,
                title=it.title,
                raw_content=plain
            )
            self.sections.append(sec)

        self.rebuild_composite_text()
        self.is_active = len(self.sections) > 0

    load_items = load_from_binder_items

    @property
    def segments(self) -> List[ScriveningsSection]:
        return self.sections

    def get_composite_text(self) -> str:
        return self.composite_text

    def update_segment_text(self, index: int, new_text: str) -> bool:
        if 0 <= index < len(self.sections):
            return self.edit_section_content(self.sections[index].uuid, new_text)
        return False

    def _flatten_item(self, item: BinderItem) -> List[BinderItem]:
        """Extrae recursivamente el nodo y sus hijos si corresponden al manuscrito."""
        result = [item]
        for child in item.children:
            result.extend(self._flatten_item(child))
        return result

    def set_divider_style(self, style: DividerStyle):
        """Configura el estilo del separador visual."""
        self.divider_style = style
        self.rebuild_composite_text()

    def set_show_titles(self, show: bool, show_numbers: bool = True):
        """Configura la visibilidad de los encabezados de sección."""
        self.show_section_titles = show
        self.show_section_numbers = show_numbers
        self.rebuild_composite_text()

    def rebuild_composite_text(self):
        """Reconstruye el buffer unificado continuo calculando los offsets exactos."""
        parts: List[str] = []
        current_offset = 0

        divider_text = ScriveningsDivider.get_divider_text(self.divider_style)

        for i, sec in enumerate(self.sections):
            # 1. Encabezado de sección
            if self.show_section_titles:
                header = ScriveningsDivider.format_section_header(
                    sec.title,
                    section_number=i + 1,
                    show_number=self.show_section_numbers
                )
                sec.header_start = current_offset
                sec.header_end = current_offset + len(header)
                current_offset += len(header)
                parts.append(header)
            else:
                sec.header_start = current_offset
                sec.header_end = current_offset

            # 2. Contenido de la sección
            sec.content_start = current_offset
            sec.content_end = current_offset + len(sec.raw_content)
            current_offset += len(sec.raw_content)
            parts.append(sec.raw_content)

            # 3. Separador (si no es la última sección)
            if i < len(self.sections) - 1:
                sec.divider_start = current_offset
                sec.divider_end = current_offset + len(divider_text)
                current_offset += len(divider_text)
                parts.append(divider_text)
            else:
                sec.divider_start = current_offset
                sec.divider_end = current_offset

        self.composite_text = "".join(parts)

    def get_section_at_offset(self, offset: int) -> Optional[ScriveningsSection]:
        """Devuelve la sección a la que pertenece un offset del flujo continuo."""
        for sec in self.sections:
            if sec.header_start <= offset <= sec.divider_end:
                return sec
        return self.sections[-1] if self.sections else None

    def get_section_by_uuid(self, uuid: str) -> Optional[ScriveningsSection]:
        """Busca una sección por su identificador UUID."""
        for sec in self.sections:
            if sec.uuid == uuid:
                return sec
        return None

    def edit_section_title(self, uuid: str, new_title: str) -> bool:
        """
        Modifica el título de una sección in-situ.
        Actualiza el BinderItem y notifica al resto del sistema.
        """
        sec = self.get_section_by_uuid(uuid)
        if not sec:
            return False

        sec.title = new_title
        sec.item.title = new_title
        if hasattr(sec.item, "data"):
            sec.item.data.title = new_title
        sec.item.mark_dirty()
        if self.project:
            self.project.save_structure()
        self.rebuild_composite_text()

        if self.on_title_changed:
            self.on_title_changed(uuid, new_title)
        return True

    def edit_section_content(self, uuid: str, new_content: str, auto_save: bool = True) -> bool:
        """
        Actualiza el contenido individual de una sección y sincroniza
        inmediatamente con su archivo content.rtf.
        """
        sec = self.get_section_by_uuid(uuid)
        if not sec:
            return False

        sec.raw_content = new_content
        sec.is_dirty = True

        if auto_save:
            self.save_section(sec)

        self.rebuild_composite_text()
        return True

    def save_section(self, section: ScriveningsSection):
        """Guarda de forma atómica y transparente en el content.rtf del ítem."""
        rtf_content = RTFEngine.plain_text_to_rtf(section.raw_content)
        section.item.write_content_rtf(rtf_content)
        section.item.save_if_dirty()
        section.is_dirty = False

        if self.on_content_saved:
            self.on_content_saved(section.uuid)

    def save_all_dirty(self):
        """Guarda todas las secciones con modificaciones pendientes."""
        for sec in self.sections:
            if sec.is_dirty:
                self.save_section(sec)

    def update_from_composite_edit(self, start_offset: int, end_offset: int, replacement: str):
        """
        Aplica una edición realizada directamente sobre el texto continuo compuesto,
        traduciendo el rango al documento individual correspondiente.
        """
        target_sec = self.get_section_at_offset(start_offset)
        if not target_sec:
            return

        # Comprobar si la edición cae dentro del contenido
        if target_sec.content_start <= start_offset <= target_sec.content_end:
            local_start = start_offset - target_sec.content_start
            local_end = min(end_offset, target_sec.content_end) - target_sec.content_start

            old_text = target_sec.raw_content
            new_text = old_text[:local_start] + replacement + old_text[local_end:]
            self.edit_section_content(target_sec.uuid, new_text, auto_save=True)

    def get_total_word_count(self) -> int:
        """Calcula el conteo de palabras global del manuscrito compuesto."""
        return sum(sec.word_count for sec in self.sections)

    def get_total_character_count(self) -> int:
        """Calcula el conteo de caracteres global."""
        return sum(sec.character_count for sec in self.sections)

    def get_summary(self) -> Dict:
        """Devuelve un resumen de telemetría de las secciones compuestas."""
        return {
            "is_active": self.is_active,
            "section_count": len(self.sections),
            "total_words": self.get_total_word_count(),
            "total_characters": self.get_total_character_count(),
            "divider_style": self.divider_style.value,
            "sections": [
                {
                    "uuid": s.uuid,
                    "title": s.title,
                    "words": s.word_count,
                    "chars": s.character_count,
                    "offsets": {
                        "header": (s.header_start, s.header_end),
                        "content": (s.content_start, s.content_end),
                        "divider": (s.divider_start, s.divider_end)
                    }
                }
                for s in self.sections
            ]
        }
