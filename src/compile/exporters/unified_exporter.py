"""
Exportador Unificado para Escritorio.
Punto de entrada único que orquesta todos los exportadores nativos:
DOCX, PDF, EPUB3, FDX, FOUNTAIN, LaTeX, Markdown, RTF y HTML.
"""

from enum import Enum
from pathlib import Path
from typing import Union, Optional, Any, Dict

from .docx_exporter import DOCXExporter
from .pdf_exporter import PDFExporter
from .epub3_exporter import EPUB3Exporter
from .screenplay_exporter import ScreenplayExporter
from .text_exporters import LaTeXExporter, MarkdownExporter, RTFExporter, HTMLExporter


class ExportFormat(Enum):
    MARKDOWN = "md"
    HTML = "html"
    RTF = "rtf"
    DOCX = "docx"
    PDF = "pdf"
    EPUB = "epub"
    EPUB3 = "epub3"
    FDX = "fdx"
    FOUNTAIN = "fountain"
    LATEX = "tex"


class UnifiedExporter:
    """Exportador centralizado con despacho dinámico a generadores nativos."""

    @classmethod
    def export(
        cls,
        text_content: str,
        destination_path: Union[str, Path],
        format_type: Union[ExportFormat, str],
        title: str = "Manuscrito",
        author: str = "Autor",
        **kwargs: Any
    ) -> Path:
        """
        Exporta el texto al formato solicitado con sus opciones específicas.
        """
        out_path = Path(destination_path)

        # Normalizar format_type si viene como string
        if isinstance(format_type, str):
            clean_str = format_type.lower().lstrip(".")
            for fmt in ExportFormat:
                if fmt.value == clean_str or fmt.name.lower() == clean_str:
                    format_type = fmt
                    break
            else:
                format_type = ExportFormat.MARKDOWN

        if format_type == ExportFormat.DOCX:
            return DOCXExporter.export(
                text_content=text_content,
                destination_path=out_path,
                title=title,
                author=author,
                font_family=kwargs.get("font_family", "Times New Roman"),
                font_size_pt=kwargs.get("font_size_pt", 12),
                line_spacing=kwargs.get("line_spacing", 2.0),
                margin_inches=kwargs.get("margin_inches", 1.0),
                page_size=kwargs.get("page_size", "letter")
            )

        elif format_type == ExportFormat.PDF:
            return PDFExporter.export(
                text_content=text_content,
                destination_path=out_path,
                title=title,
                author=author,
                font_family=kwargs.get("font_family", "Times"),
                font_size_pt=kwargs.get("font_size_pt", 11.0),
                line_height_pt=kwargs.get("line_height_pt", 16.0),
                page_size=kwargs.get("page_size", "letter"),
                margin_inches=kwargs.get("margin_inches", 1.0)
            )

        elif format_type in (ExportFormat.EPUB, ExportFormat.EPUB3):
            return EPUB3Exporter.export(
                text_content=text_content,
                destination_path=out_path,
                title=title,
                author=author,
                language=kwargs.get("language", "es"),
                publisher=kwargs.get("publisher", "Escritorio Publishing"),
                cover_subtitle=kwargs.get("cover_subtitle", None)
            )

        elif format_type == ExportFormat.FDX:
            return ScreenplayExporter.export_fdx(
                text_content=text_content,
                destination_path=out_path,
                title=title,
                author=author
            )

        elif format_type == ExportFormat.FOUNTAIN:
            return ScreenplayExporter.export_fountain(
                text_content=text_content,
                destination_path=out_path,
                title=title,
                author=author
            )

        elif format_type == ExportFormat.LATEX:
            return LaTeXExporter.export(
                text_content=text_content,
                destination_path=out_path,
                title=title,
                author=author,
                doc_class=kwargs.get("doc_class", "book"),
                paper_size=kwargs.get("paper_size", "a4paper"),
                font_size=kwargs.get("font_size", "11pt")
            )

        elif format_type == ExportFormat.MARKDOWN:
            return MarkdownExporter.export(
                text_content=text_content,
                destination_path=out_path,
                title=title,
                author=author
            )

        elif format_type == ExportFormat.RTF:
            return RTFExporter.export(
                text_content=text_content,
                destination_path=out_path,
                font_family=kwargs.get("font_family", "Times New Roman"),
                font_size_pt=kwargs.get("font_size_pt", 12)
            )

        elif format_type == ExportFormat.HTML:
            return HTMLExporter.export(
                text_content=text_content,
                destination_path=out_path,
                title=title,
                author=author
            )

        else:
            # Fallback seguro a Markdown
            return MarkdownExporter.export(
                text_content=text_content,
                destination_path=out_path,
                title=title,
                author=author
            )
