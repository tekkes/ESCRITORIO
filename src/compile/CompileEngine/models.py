"""
Modelos de Datos para el Motor de Compilación de Escritorio / Scrivener 3.
Definiciones de Formatos de Compilación, Diseños de Sección (Section Layouts),
Metadatos del Libro, Reglas de Reemplazo y Filtros de Contenido.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Any
from .separators import SectionSeparators, SeparatorType


class PageSize(Enum):
    LETTER = "letter"          # 8.5 x 11 in
    A4 = "a4"                  # 210 x 297 mm
    PAPERBACK_6X9 = "6x9"      # 6 x 9 in (estándar imprenta KDP/Ingram)
    DIGEST_5_5X8_5 = "5.5x8.5" # 5.5 x 8.5 in
    CUSTOM = "custom"


class PageOrientation(Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


@dataclass
class PageMargins:
    top_in: float = 1.0
    bottom_in: float = 1.0
    left_in: float = 1.0
    right_in: float = 1.0


@dataclass
class SectionLayout:
    """
    Diseño de Maquetación de Sección (Section Layout) en Scrivener 3.
    Determina cómo se procesa y maqueta un tipo de sección específico.
    """
    id: str
    name: str
    description: str = ""
    # Prefijo y sufijo de título
    title_prefix: str = ""            # Ej. "CAPÍTULO <$n>\n\n" o "PARTE <$R>: "
    title_suffix: str = "\n\n"
    # Elementos incluidos
    include_title: bool = True
    include_body: bool = True
    include_synopsis: bool = False
    include_notes: bool = False
    # Tipografía
    title_uppercase: bool = False
    title_bold: bool = True
    title_centered: bool = False
    body_indent_first_paragraph: bool = False
    # Separadores
    separators: SectionSeparators = field(default_factory=SectionSeparators)


@dataclass
class BookMetadata:
    """Metadatos editoriales del libro / manuscrito para publicación."""
    title: str = "Manuscrito Sin Título"
    subtitle: str = ""
    author: str = "Autor"
    editor: str = ""
    isbn: str = ""
    publisher: str = "Editorial Independiente"
    copyright_notice: str = "Todos los derechos reservados"
    language: str = "es"
    cover_image_path: Optional[str] = None


@dataclass
class CompileReplacementRule:
    """Regla de sustitución automática de texto o Regex previa a la compilación."""
    pattern: str
    replacement: str
    is_regex: bool = False
    case_sensitive: bool = True
    whole_word: bool = False


@dataclass
class CompileFilterConfig:
    """Configuración de selección y filtrado de qué documentos se compilan."""
    included_uuids: Optional[Set[str]] = None
    filter_label_id: Optional[int] = None
    filter_status_id: Optional[int] = None
    filter_collection: Optional[str] = None
    include_front_matter: bool = False
    front_matter_uuid: Optional[str] = None
    include_back_matter: bool = False
    back_matter_uuid: Optional[str] = None


@dataclass
class CompileFormat:
    """
    Formato de Compilación completo de Scrivener 3.
    Contiene tipografía, página, diseños de sección, separadores y transformaciones.
    """
    id: str
    name: str
    description: str = ""
    is_builtin: bool = True
    is_project_format: bool = False
    target_format: str = "docx"  # docx, pdf, epub, rtf, fdx, md, html, txt
    # Página
    page_size: PageSize = PageSize.LETTER
    orientation: PageOrientation = PageOrientation.PORTRAIT
    margins: PageMargins = field(default_factory=PageMargins)
    # Tipografía
    font_family: str = "Times New Roman"
    font_size_pt: int = 12
    line_spacing: float = 2.0
    first_line_indent_pt: float = 24.0
    # Diseños de sección
    layouts: Dict[str, SectionLayout] = field(default_factory=dict)
    # Transformaciones de texto
    smart_quotes: bool = True
    em_dashes: bool = True
    ellipses: bool = True
    strip_comments: bool = True
    strip_footnotes: bool = False
    footnotes_as_endnotes: bool = False
    # Reemplazos específicos del formato
    replacements: List[CompileReplacementRule] = field(default_factory=list)


def create_builtin_formats() -> Dict[str, CompileFormat]:
    """Genera el catálogo de los 7 formatos predefinidos estándar de Scrivener 3."""
    formats: Dict[str, CompileFormat] = {}

    # 1. Manuscrito Estándar (Courier / Times)
    manuscript_layouts = {
        "part_title": SectionLayout(
            id="part_title",
            name="Título de Parte",
            title_prefix="PARTE <$R>\n\n",
            include_title=True,
            include_body=False,
            title_uppercase=True,
            title_centered=True,
            separators=SectionSeparators(
                before_section=SeparatorType.PAGE_BREAK,
                between_sections=SeparatorType.PAGE_BREAK
            )
        ),
        "chapter_heading": SectionLayout(
            id="chapter_heading",
            name="Encabezado de Capítulo",
            title_prefix="# Capítulo <$n>: ",
            include_title=True,
            include_body=True,
            title_centered=False,
            separators=SectionSeparators(
                before_section=SeparatorType.PAGE_BREAK,
                between_sections=SeparatorType.PAGE_BREAK
            )
        ),
        "scene_text": SectionLayout(
            id="scene_text",
            name="Texto de Escena",
            include_title=False,
            include_body=True,
            separators=SectionSeparators(
                before_section=SeparatorType.CUSTOM_SYMBOL,
                custom_before="#",
                between_sections=SeparatorType.CUSTOM_SYMBOL,
                custom_between="#"
            )
        )
    }
    formats["manuscript_standard"] = CompileFormat(
        id="manuscript_standard",
        name="Manuscrito Estándar (Courier / Times)",
        description="Formato estándar para envío a editoriales y agentes. Doble espacio, márgenes de 1 pulgada y numeración clásica.",
        is_builtin=True,
        target_format="docx",
        font_family="Courier New",
        font_size_pt=12,
        line_spacing=2.0,
        first_line_indent_pt=36.0,
        layouts=manuscript_layouts
    )

    # 2. Novela Moderna
    modern_layouts = {
        "part_modern": SectionLayout(
            id="part_modern",
            name="Parte Moderna",
            title_prefix="PARTE <$R>\n",
            include_title=True,
            include_body=False,
            title_uppercase=True,
            title_centered=True,
            separators=SectionSeparators(before_section=SeparatorType.PAGE_BREAK)
        ),
        "chapter_modern": SectionLayout(
            id="chapter_modern",
            name="Capítulo Numerado",
            title_prefix="<$T>\n\n",
            include_title=True,
            include_body=True,
            title_centered=True,
            separators=SectionSeparators(before_section=SeparatorType.PAGE_BREAK)
        ),
        "scene_modern": SectionLayout(
            id="scene_modern",
            name="Escena Continua",
            include_title=False,
            include_body=True,
            separators=SectionSeparators(
                between_sections=SeparatorType.CUSTOM_SYMBOL,
                custom_between="* * *"
            )
        )
    }
    formats["modern_novel"] = CompileFormat(
        id="modern_novel",
        name="Novela Moderna",
        description="Tipografía elegante con números de capítulo en palabras, versalitas y separadores ornamentados.",
        is_builtin=True,
        target_format="pdf",
        font_family="Palatino",
        font_size_pt=11,
        line_spacing=1.3,
        first_line_indent_pt=18.0,
        layouts=modern_layouts
    )

    # 3. Libro de Bolsillo 6x9 (Paperback)
    paperback_layouts = {
        "chapter_pb": SectionLayout(
            id="chapter_pb",
            name="Capítulo 6x9",
            title_prefix="<$n>\n",
            include_title=True,
            include_body=True,
            title_centered=True,
            separators=SectionSeparators(before_section=SeparatorType.PAGE_BREAK)
        ),
        "scene_pb": SectionLayout(
            id="scene_pb",
            name="Escena de Bolsillo",
            include_title=False,
            include_body=True,
            separators=SectionSeparators(
                between_sections=SeparatorType.CUSTOM_SYMBOL,
                custom_between="~ ~ ~"
            )
        )
    }
    formats["paperback_6x9"] = CompileFormat(
        id="paperback_6x9",
        name="Libro de Bolsillo 6x9",
        description="Maquetado ajustado a tamaño de imprenta 6x9 pulgadas con márgenes para encuadernación.",
        is_builtin=True,
        target_format="pdf",
        page_size=PageSize.PAPERBACK_6X9,
        font_family="Garamond",
        font_size_pt=10,
        line_spacing=1.2,
        first_line_indent_pt=14.0,
        layouts=paperback_layouts
    )

    # 4. Ebook Estándar (EPUB 3)
    epub_layouts = {
        "chapter_epub": SectionLayout(
            id="chapter_epub",
            name="Capítulo Digital",
            title_prefix="Capítulo <$n>: ",
            include_title=True,
            include_body=True,
            separators=SectionSeparators(before_section=SeparatorType.PAGE_BREAK)
        ),
        "scene_epub": SectionLayout(
            id="scene_epub",
            name="Escena Digital",
            include_title=False,
            include_body=True,
            separators=SectionSeparators(
                between_sections=SeparatorType.CUSTOM_SYMBOL,
                custom_between="* * *"
            )
        )
    }
    formats["standard_epub"] = CompileFormat(
        id="standard_epub",
        name="Ebook Estándar",
        description="Optimizado para lectores electrónicos ePub 3, Kindle y Apple Books con maquetación fluida.",
        is_builtin=True,
        target_format="epub",
        font_family="Georgia",
        font_size_pt=12,
        line_spacing=1.4,
        first_line_indent_pt=20.0,
        layouts=epub_layouts
    )

    # 5. Guion Hollywood
    script_layouts = {
        "script_scene": SectionLayout(
            id="script_scene",
            name="Escena de Guion",
            include_title=True,
            include_body=True,
            title_uppercase=True,
            separators=SectionSeparators(before_section=SeparatorType.EMPTY_LINE)
        )
    }
    formats["hollywood_script"] = CompileFormat(
        id="hollywood_script",
        name="Guion Hollywood",
        description="Formato profesional de la industria según especificaciones de la Academia y Final Draft.",
        is_builtin=True,
        target_format="fdx",
        font_family="Courier Prime",
        font_size_pt=12,
        line_spacing=1.0,
        first_line_indent_pt=0.0,
        layouts=script_layouts
    )

    # 6. Ensayo Académico APA / MLA
    academic_layouts = {
        "academic_heading": SectionLayout(
            id="academic_heading",
            name="Encabezado Jerárquico",
            title_prefix="<$hn> ",
            include_title=True,
            include_body=True,
            separators=SectionSeparators(before_section=SeparatorType.EMPTY_LINE)
        ),
        "academic_text": SectionLayout(
            id="academic_text",
            name="Párrafo Académico",
            include_title=False,
            include_body=True,
            separators=SectionSeparators(before_section=SeparatorType.SINGLE_RETURN)
        )
    }
    formats["academic_paper"] = CompileFormat(
        id="academic_paper",
        name="Ensayo Académico APA/MLA",
        description="Estructura formal con numeración jerárquica <$hn>, notas a pie de página y portada académica.",
        is_builtin=True,
        target_format="docx",
        font_family="Times New Roman",
        font_size_pt=12,
        line_spacing=2.0,
        first_line_indent_pt=36.0,
        layouts=academic_layouts
    )

    # 7. Esquema de Sinopsis
    synopsis_layouts = {
        "synopsis_folder": SectionLayout(
            id="synopsis_folder",
            name="Carpeta con Sinopsis",
            title_prefix="[CARPETA] ",
            include_title=True,
            include_body=False,
            include_synopsis=True,
            separators=SectionSeparators(before_section=SeparatorType.EMPTY_LINE)
        ),
        "synopsis_text": SectionLayout(
            id="synopsis_text",
            name="Documento con Sinopsis",
            title_prefix="  - ",
            include_title=True,
            include_body=False,
            include_synopsis=True,
            include_notes=True,
            separators=SectionSeparators(before_section=SeparatorType.SINGLE_RETURN)
        )
    }
    formats["synopsis_outline"] = CompileFormat(
        id="synopsis_outline",
        name="Esquema de Sinopsis",
        description="Exporta el árbol estructural mostrando títulos, sinopsis y notas para revisión editorial.",
        is_builtin=True,
        target_format="md",
        font_family="Calibri",
        font_size_pt=11,
        line_spacing=1.15,
        first_line_indent_pt=0.0,
        layouts=synopsis_layouts
    )

    return formats
