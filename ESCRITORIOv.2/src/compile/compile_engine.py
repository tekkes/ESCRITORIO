"""
ESCRITORIO v2.0 - Scrivener 3 Compile Engine
Pipeline semántico de compilación editorial: resolución de Section Layouts,
reemplazo de placeholders (<$p>, <$t>, <$author>) y exportación multiformato.
"""

import os
import re
import time
from pathlib import Path
from typing import List, Dict, Optional, Any
from ..core.project_v2 import BinderNode, EscritorioProjectV2


class CompileEngineV2:
    """Motor de compilación determinista multiformato."""

    def __init__(self, project: EscritorioProjectV2):
        self.project = project

    def compile_project(
        self,
        output_path: Path,
        format_type: str = "DOCX",
        format_preset: str = "Standard Manuscript",
        include_front_matter: bool = False,
        author: str = "Autor",
        title: str = "Mi Obra"
    ) -> bool:
        """Ejecuta el pipeline completo de compilación."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Recolectar documentos marcados para compilación
        nodes_to_compile: List[BinderNode] = []
        if self.project.draft_node:
            self._collect_compilable_nodes(self.project.draft_node, nodes_to_compile)

        # 2. Generar texto ensamblado resolviendo Section Layouts y Placeholders
        compiled_sections = []
        chapter_counter = 1

        for node in nodes_to_compile:
            self.project.load_node_content(node)
            raw_text = node.get_plain_text()

            # Resolver Section Layout según Section Type
            if node.section_type in ("Chapter", "Folder") or node.is_folder():
                header = f"\n\nCAPÍTULO {chapter_counter}: {node.title.upper()}\n\n"
                chapter_counter += 1
                compiled_sections.append(header)
                if raw_text.strip():
                    compiled_sections.append(raw_text + "\n\n")
            elif node.section_type == "Part":
                compiled_sections.append(f"\n\nPARTE: {node.title.upper()}\n\n")
            else:
                # Scene normal
                compiled_sections.append(f"\n* * *\n\n{raw_text}\n\n")

        full_content = "".join(compiled_sections)

        # 3. Reemplazar placeholders
        full_content = full_content.replace("<$projecttitle>", title or self.project.name)
        full_content = full_content.replace("<$author>", author)
        full_content = full_content.replace("<$date>", time.strftime("%d/%m/%Y"))

        # 4. Exportar según formato
        fmt = format_type.upper()
        if fmt == "DOCX":
            return self._export_docx(output_path, title, author, full_content)
        elif fmt == "PDF":
            return self._export_pdf(output_path, title, author, full_content)
        elif fmt == "EPUB":
            return self._export_epub(output_path, title, author, full_content)
        elif fmt == "RTF":
            return self._export_rtf(output_path, title, full_content)
        elif fmt == "MARKDOWN" or fmt == "MD":
            output_path.write_text(full_content, encoding="utf-8")
            return True
        else:  # TXT
            output_path.write_text(full_content, encoding="utf-8")
            return True

    def _collect_compilable_nodes(self, node: BinderNode, result: List[BinderNode]):
        if node.type == "TrashFolder":
            return
        if node.include_in_compile and node.type != "DraftFolder":
            result.append(node)
        for child in node.children:
            self._collect_compilable_nodes(child, result)

    def _export_docx(self, path: Path, title: str, author: str, content: str) -> bool:
        """Exporta a archivo DOCX profesional."""
        try:
            import docx
            doc = docx.Document()
            doc.add_heading(title, level=0)
            p_author = doc.add_paragraph(f"Por {author}")
            p_author.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
            doc.add_page_break()

            for paragraph in content.split("\n\n"):
                p_clean = paragraph.strip()
                if p_clean:
                    if p_clean.startswith("CAPÍTULO") or p_clean.startswith("PARTE"):
                        doc.add_heading(p_clean, level=1)
                    elif p_clean == "* * *":
                        p_sep = doc.add_paragraph("* * *")
                        p_sep.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
                    else:
                        doc.add_paragraph(p_clean)

            doc.save(str(path))
            return True
        except Exception:
            # Fallback a texto si docx falla
            path.with_suffix(".txt").write_text(content, encoding="utf-8")
            return False

    def _export_pdf(self, path: Path, title: str, author: str, content: str) -> bool:
        """Exporta a PDF con portadas y márgenes estándar."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

            doc = SimpleDocTemplate(str(path), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
            styles = getSampleStyleSheet()

            story = []
            title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], alignment=1, fontSize=24, spaceAfter=20)
            story.append(Paragraph(title, title_style))
            story.append(Paragraph(f"Por {author}", styles['Normal']))
            story.append(PageBreak())

            body_style = ParagraphStyle('DocBody', parent=styles['Normal'], fontSize=11, leading=16, spaceAfter=8)

            for p in content.split("\n\n"):
                p_clean = p.strip()
                if p_clean:
                    if p_clean.startswith("CAPÍTULO") or p_clean.startswith("PARTE"):
                        story.append(Spacer(1, 20))
                        story.append(Paragraph(p_clean, styles['Heading2']))
                        story.append(Spacer(1, 10))
                    elif p_clean == "* * *":
                        story.append(Paragraph("<para align=center>* * *</para>", body_style))
                    else:
                        safe_text = p_clean.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        story.append(Paragraph(safe_text, body_style))

            doc.build(story)
            return True
        except Exception:
            return False

    def _export_epub(self, path: Path, title: str, author: str, content: str) -> bool:
        """Exporta a EPUB 3 estándar."""
        try:
            from ebooklib import epub
            book = epub.EpubBook()
            book.set_identifier(f"escr-{int(time.time())}")
            book.set_title(title)
            book.set_language('es')
            book.add_author(author)

            # Capítulos
            chapters = []
            parts = content.split("CAPÍTULO ")
            for idx, part in enumerate(parts):
                if not part.strip():
                    continue
                c_title = f"Capítulo {idx}" if idx > 0 else "Introducción"
                c_item = epub.EpubHtml(title=c_title, file_name=f"chap_{idx}.xhtml", lang='es')
                c_item.content = f"<h1>{c_title}</h1><p>{part.replace(chr(10), '</p><p>')}</p>"
                book.add_item(c_item)
                chapters.append(c_item)

            book.toc = tuple(chapters)
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())

            book.spine = ['nav'] + chapters
            epub.write_epub(str(path), book)
            return True
        except Exception:
            return False

    def _export_rtf(self, path: Path, title: str, content: str) -> bool:
        """Exporta a archivo RTF nativo."""
        rtf_header = r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Georgia;}} \viewkind4\uc1\pard\f0\fs24 "
        rtf_body = content.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}").replace("\n", r"\par ")
        full_rtf = rtf_header + rtf_body + r"}"
        path.write_text(full_rtf, encoding="utf-8")
        return True
