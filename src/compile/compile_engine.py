"""
Compile Engine para Escritorio
Orquestador de compilación editorial: recorre el árbol de borrador, filtra nodos excluidos,
resuelve marcadores y aplica la plantilla de maquetación en una sola pasada eficiente.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from ..core.project import EscritorioProject, BinderItem
from ..core.rtf_engine import RTFEngine
from .placeholders import PlaceholderResolver
from .section_layouts import SectionLayoutEngine, SectionLayoutType

@dataclass
class CompileConfig:
    author_name: str = "Autor"
    include_cover: bool = True
    scene_separator: str = "* * *"
    strip_comments: bool = True
    target_format: str = "docx"

class CompileEngine:
    """Motor de compilación principal."""

    def __init__(self, project: EscritorioProject, config: Optional[CompileConfig] = None):
        self.project = project
        self.config = config or CompileConfig()
        self.placeholder_resolver = PlaceholderResolver({
            "title": project.project_data.get("title", "Manuscrito"),
            "author": self.config.author_name
        })

    def assemble_manuscript(self) -> str:
        """Recorre la carpeta de borrador (Draft) y ensambla el documento unificado."""
        self.placeholder_resolver.reset_counters()
        assembled_chunks: List[str] = []

        if not self.project.root_items:
            return ""

        # El primer elemento raíz suele ser el borrador (DraftFolder)
        draft_root = self.project.root_items[0]
        chapter_counter = 1

        def process_node(item: BinderItem):
            nonlocal chapter_counter

            # Verificar si está marcado para incluirse en la compilación
            if not item.data.include_in_compile:
                return

            raw_rtf = item.read_content_rtf()
            plain_body = RTFEngine.rtf_to_plain_text(raw_rtf)

            # Resolver tipo de sección
            sec_type = item.data.section_type
            if sec_type == "Chapter":
                formatted = SectionLayoutEngine.format_section(
                    SectionLayoutType.NUMBERED_CHAPTER,
                    item.title,
                    plain_body,
                    chapter_index=chapter_counter,
                    scene_separator=self.config.scene_separator
                )
                chapter_counter += 1
            elif sec_type == "Scene":
                formatted = SectionLayoutEngine.format_section(
                    SectionLayoutType.SCENE_SEPARATOR,
                    item.title,
                    plain_body,
                    scene_separator=self.config.scene_separator
                )
            elif item.item_type == "Folder":
                formatted = SectionLayoutEngine.format_section(
                    SectionLayoutType.TITLE_ONLY,
                    item.title,
                    ""
                )
            else:
                formatted = SectionLayoutEngine.format_section(
                    SectionLayoutType.TITLE_AND_TEXT,
                    item.title,
                    plain_body
                )

            # Resolver placeholders
            final_chunk = self.placeholder_resolver.resolve(formatted, item_title=item.title)
            assembled_chunks.append(final_chunk)

            # Procesar hijos
            for child in item.children:
                process_node(child)

        for top_child in draft_root.children:
            process_node(top_child)

        return "\n".join(assembled_chunks)
