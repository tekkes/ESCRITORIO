"""
PageViewEngine para Escritorio
Gestión del modo de visualización paginada (Page View / Alt+Shift+P):
- Modo Continuo (Continuous Flow) con ancho adaptable o fijo centrado
- Modo Vista de Página (Physical Folio Paginated View)
- Cálculo de folios físicos (A4, US Letter, Formato Editorial 6x9 in)
- Cálculo de márgenes reales, saltos de página e indexación de páginas por cursor.
"""

from enum import Enum
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass


class EditorViewMode(str, Enum):
    CONTINUOUS = "Continuous"  # Flujo continuo vertical centrado
    PAGE_VIEW = "PageView"    # Folios físicos paginados con márgenes


class PageFormat(str, Enum):
    A4 = "A4"                  # 210 x 297 mm = 595.28 x 841.89 pt
    US_LETTER = "US_Letter"    # 8.5 x 11 in = 612 x 792 pt
    TRADE_PB = "Trade_Paperback" # 6 x 9 in = 432 x 648 pt (Novela estándar)
    CUSTOM = "Custom"


@dataclass
class PageDimensions:
    width_pt: float
    height_pt: float
    margin_top_pt: float = 72.0     # 1 pulgada
    margin_bottom_pt: float = 72.0
    margin_left_pt: float = 85.0    # Margen interior más amplio
    margin_right_pt: float = 72.0

    @property
    def content_width_pt(self) -> float:
        return max(50.0, self.width_pt - self.margin_left_pt - self.margin_right_pt)

    @property
    def content_height_pt(self) -> float:
        return max(50.0, self.height_pt - self.margin_top_pt - self.margin_bottom_pt)


@dataclass
class FolioPage:
    page_number: int
    start_char_index: int
    end_char_index: int
    text_content: str
    is_explicit_break: bool = False


class PageViewEngine:
    """Motor de cálculo y maquetación de folios físicos paginados."""

    FORMAT_MAP = {
        PageFormat.A4: PageDimensions(595.28, 841.89, 70.87, 70.87, 85.04, 70.87),      # ~25mm márgenes
        PageFormat.US_LETTER: PageDimensions(612.0, 792.0, 72.0, 72.0, 72.0, 72.0),      # 1 pulgada
        PageFormat.TRADE_PB: PageDimensions(432.0, 648.0, 54.0, 54.0, 54.0, 45.0),      # Formato editorial 6x9"
    }

    # Capacidad aproximada de caracteres por línea y líneas por página en fuente estándar 12pt
    CHARS_PER_LINE_AVG = 65
    LINES_PER_PAGE_AVG = 32

    def __init__(self, mode: EditorViewMode = EditorViewMode.CONTINUOUS, page_format: PageFormat = PageFormat.A4):
        self.mode = mode
        self.page_format = page_format
        self.dimensions = self.FORMAT_MAP.get(page_format, self.FORMAT_MAP[PageFormat.A4])
        self.pages: List[FolioPage] = []

    def toggle_mode(self) -> EditorViewMode:
        """Alterna entre Vista Continua y Vista de Página (Alt+Shift+P)."""
        if self.mode == EditorViewMode.CONTINUOUS:
            self.mode = EditorViewMode.PAGE_VIEW
        else:
            self.mode = EditorViewMode.CONTINUOUS
        return self.mode

    def set_page_format(self, fmt: PageFormat, custom_dims: Optional[PageDimensions] = None):
        self.page_format = fmt
        if fmt == PageFormat.CUSTOM and custom_dims:
            self.dimensions = custom_dims
        else:
            self.dimensions = self.FORMAT_MAP.get(fmt, self.FORMAT_MAP[PageFormat.A4])

    def calculate_pagination(self, plain_text: str, line_height_pt: float = 14.4) -> List[FolioPage]:
        """
        Divide el texto en folios virtuales respetando saltos explícitos (\\page)
        y dimensiones físicas de la página.
        """
        self.pages.clear()
        if not plain_text:
            p = FolioPage(1, 0, 0, "")
            self.pages.append(p)
            return self.pages

        # Capacidad de líneas por página física
        max_lines_per_page = max(10, int(self.dimensions.content_height_pt / max(10.0, line_height_pt)))
        max_chars_per_page = max(200, max_lines_per_page * self.CHARS_PER_LINE_AVG)

        # Detectar saltos explícitos de página
        explicit_parts = plain_text.split("--- Salto de Página ---")
        current_char = 0
        page_num = 1

        for part_idx, part in enumerate(explicit_parts):
            paragraphs = part.split("\n")
            current_page_text: List[str] = []
            current_line_count = 0
            page_start_char = current_char

            for para in paragraphs:
                para_len = len(para)
                # Estimar líneas que ocupa este párrafo
                para_lines = max(1, (para_len + self.CHARS_PER_LINE_AVG - 1) // self.CHARS_PER_LINE_AVG)

                if current_line_count + para_lines > max_lines_per_page and current_page_text:
                    # Cerrar página actual y comenzar nueva
                    page_str = "\n".join(current_page_text)
                    page_end_char = page_start_char + len(page_str)
                    self.pages.append(FolioPage(
                        page_number=page_num,
                        start_char_index=page_start_char,
                        end_char_index=page_end_char,
                        text_content=page_str,
                        is_explicit_break=False
                    ))
                    page_num += 1
                    page_start_char = page_end_char + 1
                    current_page_text = [para]
                    current_line_count = para_lines
                else:
                    current_page_text.append(para)
                    current_line_count += para_lines

            # Añadir lo restante del fragmento
            page_str = "\n".join(current_page_text)
            page_end_char = page_start_char + len(page_str)
            is_break = (part_idx < len(explicit_parts) - 1)
            self.pages.append(FolioPage(
                page_number=page_num,
                start_char_index=page_start_char,
                end_char_index=page_end_char,
                text_content=page_str,
                is_explicit_break=is_break
            ))
            page_num += 1
            current_char = page_end_char + (len("--- Salto de Página ---") if is_break else 0)

        return self.pages

    def get_current_page_for_cursor(self, cursor_char_pos: int) -> int:
        """Determina en qué página física se encuentra el cursor del escritor."""
        if not self.pages:
            return 1
        for page in self.pages:
            if page.start_char_index <= cursor_char_pos <= page.end_char_index:
                return page.page_number
        return self.pages[-1].page_number

    def get_render_data(self) -> Dict[str, Any]:
        """Devuelve los parámetros de renderizado de la vista de página."""
        return {
            "mode": self.mode.value,
            "is_page_view": (self.mode == EditorViewMode.PAGE_VIEW),
            "format": self.page_format.value,
            "dimensions": {
                "width_pt": self.dimensions.width_pt,
                "height_pt": self.dimensions.height_pt,
                "margin_top_pt": self.dimensions.margin_top_pt,
                "margin_bottom_pt": self.dimensions.margin_bottom_pt,
                "margin_left_pt": self.dimensions.margin_left_pt,
                "margin_right_pt": self.dimensions.margin_right_pt,
                "content_width_pt": self.dimensions.content_width_pt,
                "content_height_pt": self.dimensions.content_height_pt,
            },
            "total_pages": len(self.pages),
            "pages": [
                {
                    "number": p.page_number,
                    "start": p.start_char_index,
                    "end": p.end_char_index,
                    "is_break": p.is_explicit_break
                }
                for p in self.pages
            ]
        }
