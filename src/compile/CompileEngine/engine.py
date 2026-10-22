"""
Compile Engine Maestro para Escritorio / Scrivener 3.
Orquestador integral de compilación editorial:
- Resolución de Front Matter y Back Matter.
- Mapeo semántico de Section Types a Section Layouts.
- Inyección de Separadores configurables.
- Evaluación de variables y comodines dinámicos (Placeholders).
- Transformaciones tipográficas (comillas curvas, guiones largos, elipsis).
- Reemplazos de texto y expresiones regulares (Regex).
- Exportación multiformato (DOCX, PDF, EPUB, RTF, FDX, Markdown, HTML).
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Set

from ...core.project import EscritorioProject, BinderItem
from ...core.rtf_engine import RTFEngine
from .models import (
    CompileFormat, SectionLayout, BookMetadata, CompileFilterConfig,
    CompileReplacementRule, create_builtin_formats
)
from .placeholders import PlaceholderResolver
from .separators import SectionSeparators, SeparatorType, SeparatorsManager
from .section_layouts import SectionLayoutEngine, SectionLayoutType
from ..exporters import UnifiedExporter, ExportFormat


@dataclass
class CompileConfig:
    """Configuración básica de compilación para compatibilidad previa."""
    author_name: str = "Autor"
    include_cover: bool = True
    scene_separator: str = "* * *"
    strip_comments: bool = True
    target_format: str = "docx"


class CompileEngine:
    """Motor central de compilación editorial de Scrivener 3."""

    def __init__(
        self,
        project: EscritorioProject,
        config_or_format: Optional[Union[CompileConfig, CompileFormat, str]] = None
    ):
        self.project: EscritorioProject = project
        self.builtin_formats = create_builtin_formats()

        # Configuración / Formato activo
        if isinstance(config_or_format, CompileFormat):
            self.format: CompileFormat = config_or_format
            self.config = CompileConfig(
                author_name=project.project_data.get("author", "Autor"),
                scene_separator="* * *",
                strip_comments=self.format.strip_comments,
                target_format=self.format.target_format
            )
        elif isinstance(config_or_format, str) and config_or_format in self.builtin_formats:
            self.format = self.builtin_formats[config_or_format]
            self.config = CompileConfig(
                author_name=project.project_data.get("author", "Autor"),
                scene_separator="* * *",
                strip_comments=self.format.strip_comments,
                target_format=self.format.target_format
            )
        elif isinstance(config_or_format, CompileConfig):
            self.config = config_or_format
            self.format = self.builtin_formats["manuscript_standard"]
            self.format.strip_comments = self.config.strip_comments
            self.format.target_format = self.config.target_format
        else:
            self.format = self.builtin_formats["manuscript_standard"]
            self.config = CompileConfig()

        # Metadatos del libro
        proj_title = project.project_data.get("title", "Manuscrito")
        proj_author = project.project_data.get("author", self.config.author_name)
        self.metadata = BookMetadata(
            title=proj_title,
            author=proj_author
        )

        # Filtros de selección
        self.filter_config = CompileFilterConfig()

        # Mapeo semántico de Section Type -> Layout ID
        self.section_mappings: Dict[str, str] = {}
        self.assign_default_mappings()

        # Evaluador de variables
        self.placeholder_resolver = PlaceholderResolver({
            "title": self.metadata.title,
            "author": self.metadata.author
        })

    def assign_default_mappings(self):
        """Asigna automáticamente los mejores layouts del formato activo a cada Section Type."""
        available_layouts = self.format.layouts
        if not available_layouts:
            return

        for st in ("Part", "Chapter", "Scene", "Heading", "Text", "Folder"):
            st_lower = st.lower()
            matched_id = None
            for lid, lay in available_layouts.items():
                if st_lower in lid.lower() or st_lower in lay.name.lower():
                    matched_id = lid
                    break
            if not matched_id and st in ("Scene", "Text"):
                for lid in available_layouts:
                    if any(k in lid.lower() for k in ("text", "scene", "body")):
                        matched_id = lid
                        break
            if not matched_id and st in ("Chapter", "Folder", "Heading"):
                for lid in available_layouts:
                    if any(k in lid.lower() for k in ("chapter", "heading", "title")):
                        matched_id = lid
                        break
            if matched_id:
                self.section_mappings[st] = matched_id
            elif available_layouts:
                self.section_mappings[st] = next(iter(available_layouts.keys()))

    def assign_section_layout(self, section_type: str, layout_id: str):
        """Asigna un diseño de sección (Section Layout) a un tipo de documento (Section Type)."""
        self.section_mappings[section_type] = layout_id

    def set_format(self, format_or_key: Union[CompileFormat, str]):
        """Cambia el formato de compilación activo."""
        if isinstance(format_or_key, str):
            if format_or_key in self.builtin_formats:
                self.format = self.builtin_formats[format_or_key]
        elif isinstance(format_or_key, CompileFormat):
            self.format = format_or_key
        self.assign_default_mappings()

    # =========================================================================
    # Ensamblaje del Manuscrito
    # =========================================================================

    def _collect_compilable_nodes(self) -> List[BinderItem]:
        """Recopila en orden editorial: Front Matter -> Borrador -> Back Matter."""
        nodes: List[BinderItem] = []

        def traverse(item: BinderItem):
            # Filtro por inclusión explícita
            if not item.data.include_in_compile:
                return

            # Filtro por UUIDs específicos si están configurados
            if self.filter_config.included_uuids is not None:
                if item.uuid not in self.filter_config.included_uuids:
                    return

            # Filtro por etiqueta
            if self.filter_config.filter_label_id is not None:
                if item.data.label_id != self.filter_config.filter_label_id:
                    return

            # Filtro por estado
            if self.filter_config.filter_status_id is not None:
                if item.data.status_id != self.filter_config.filter_status_id:
                    return

            nodes.append(item)
            for child in item.children:
                traverse(child)

        # 1. Front Matter (si está activo)
        if self.filter_config.include_front_matter and self.filter_config.front_matter_uuid:
            fm_item = self.project.get_item(self.filter_config.front_matter_uuid)
            if fm_item:
                for child in fm_item.children:
                    traverse(child)

        # 2. Borrador principal (DraftFolder)
        draft = self.project.get_draft_folder()
        if not draft and self.project.root_items:
            draft = self.project.root_items[0]

        if draft:
            for child in draft.children:
                traverse(child)

        # 3. Back Matter (si está activo)
        if self.filter_config.include_back_matter and self.filter_config.back_matter_uuid:
            bm_item = self.project.get_item(self.filter_config.back_matter_uuid)
            if bm_item:
                for child in bm_item.children:
                    traverse(child)

        return nodes

    def assemble_manuscript(self) -> str:
        """
        Ensambla y compila el manuscrito unificado aplicando maquetación,
        separadores, resolución de variables y transformaciones léxicas.
        """
        self.placeholder_resolver.reset_counters()
        nodes = self._collect_compilable_nodes()

        if not nodes:
            return ""

        assembled_parts: List[str] = []
        prev_type: Optional[str] = None
        chapter_counter = 1

        for idx, item in enumerate(nodes):
            sec_type = item.data.section_type or item.item_type
            raw_rtf = item.read_content_rtf()
            plain_body = RTFEngine.rtf_to_plain_text(raw_rtf) if raw_rtf else ""
            synopsis = item.read_synopsis() or ""
            notes_rtf = item.read_notes_rtf()
            notes = RTFEngine.rtf_to_plain_text(notes_rtf) if notes_rtf else ""

            # Determinar Layout asignado
            layout_id = self.section_mappings.get(sec_type)
            layout: Optional[SectionLayout] = None
            if layout_id and layout_id in self.format.layouts:
                layout = self.format.layouts[layout_id]
            else:
                # Fallback al primer layout disponible o crear uno ad-hoc
                if self.format.layouts:
                    layout = next(iter(self.format.layouts.values()))

            # Separadores antes / entre secciones
            if layout:
                sep = SeparatorsManager.format_boundary(
                    prev_type=prev_type,
                    current_type=sec_type,
                    current_separators=layout.separators,
                    is_first_section=(idx == 0)
                )
                if sep:
                    assembled_parts.append(sep)

            # Formatear la sección
            if layout:
                formatted = SectionLayoutEngine.format_with_layout(
                    layout=layout,
                    title=item.title,
                    body=plain_body,
                    synopsis=synopsis,
                    notes=notes,
                    chapter_index=chapter_counter
                )
            else:
                # Modo de compatibilidad clásica
                if sec_type == "Chapter":
                    formatted = SectionLayoutEngine.format_section(
                        SectionLayoutType.NUMBERED_CHAPTER,
                        item.title,
                        plain_body,
                        chapter_index=chapter_counter,
                        scene_separator=self.config.scene_separator
                    )
                elif sec_type == "Scene":
                    formatted = SectionLayoutEngine.format_section(
                        SectionLayoutType.SCENE_SEPARATOR,
                        item.title,
                        plain_body,
                        scene_separator=self.config.scene_separator
                    )
                else:
                    formatted = SectionLayoutEngine.format_section(
                        SectionLayoutType.TITLE_AND_TEXT,
                        item.title,
                        plain_body
                    )

            if sec_type == "Chapter":
                chapter_counter += 1

            # Resolver comodines (Placeholders)
            words = len(plain_body.split())
            resolved_chunk = self.placeholder_resolver.resolve(
                text=formatted,
                item_title=item.title,
                item_synopsis=synopsis,
                item_notes=notes,
                word_count=words
            )

            assembled_parts.append(resolved_chunk)
            prev_type = sec_type

        full_text = "".join(assembled_parts)

        # Transformaciones tipográficas
        full_text = self._apply_transformations(full_text)

        # Reglas de reemplazo personalizadas
        full_text = self._apply_replacements(full_text)

        return full_text.strip()

    def _apply_transformations(self, text: str) -> str:
        """Aplica transformaciones de comillas curvas, guiones y comentarios."""
        res = text

        # Eliminar comentarios editoriales si está habilitado
        if self.format.strip_comments:
            res = re.sub(r"<!--.*?-->", "", res, flags=re.DOTALL)
            res = re.sub(r"\[\[.*?\]\]", "", res)

        # Guiones largos tipográficos (em-dashes)
        if self.format.em_dashes:
            res = res.replace(" -- ", " — ")
            res = res.replace("--", "—")

        # Puntos suspensivos (elipsis)
        if self.format.ellipses:
            res = res.replace("...", "…")

        # Comillas curvas tipográficas (smart quotes)
        if self.format.smart_quotes:
            # Comillas dobles
            res = re.sub(r'(^|[\s\(\[\{])"([^\s"])', r'\1“\2', res)
            res = re.sub(r'"', '”', res)
            # Comillas simples
            res = re.sub(r"(^|[\s\(\[\{])'([^\s'])", r'\1‘\2', res)
            res = re.sub(r"'", '’', res)

        return res

    def _apply_replacements(self, text: str) -> str:
        """Aplica las reglas de búsqueda y reemplazo configuradas en el formato."""
        res = text
        for rule in self.format.replacements:
            if not rule.pattern:
                continue
            if rule.is_regex:
                flags = 0 if rule.case_sensitive else re.IGNORECASE
                try:
                    res = re.sub(rule.pattern, rule.replacement, res, flags=flags)
                except re.error:
                    pass
            else:
                if rule.whole_word:
                    pattern = rf"\b{re.escape(rule.pattern)}\b"
                    flags = 0 if rule.case_sensitive else re.IGNORECASE
                    res = re.sub(pattern, rule.replacement, res, flags=flags)
                else:
                    if rule.case_sensitive:
                        res = res.replace(rule.pattern, rule.replacement)
                    else:
                        pattern = re.compile(re.escape(rule.pattern), re.IGNORECASE)
                        res = pattern.sub(rule.replacement, res)
        return res

    def compile_and_export(
        self,
        destination_path: Union[str, Path],
        format_type: Optional[ExportFormat] = None
    ) -> Path:
        """Ensambla el manuscrito y lo exporta al formato solicitado."""
        compiled_text = self.assemble_manuscript()

        # Determinar formato de exportación
        if format_type is None:
            ext_map = {
                "docx": ExportFormat.DOCX,
                "pdf": ExportFormat.PDF,
                "epub": ExportFormat.EPUB,
                "rtf": ExportFormat.RTF,
                "fdx": ExportFormat.FDX,
                "md": ExportFormat.MARKDOWN,
                "html": ExportFormat.HTML,
                "txt": ExportFormat.MARKDOWN
            }
            target_ext = self.format.target_format.lower()
            format_type = ext_map.get(target_ext, ExportFormat.DOCX)

        return UnifiedExporter.export(
            text_content=compiled_text,
            destination_path=destination_path,
            format_type=format_type
        )
