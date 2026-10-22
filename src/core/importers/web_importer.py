"""
Importador de Páginas Web y Documentos HTML para Escritorio.
Permite descargar e importar artículos y páginas web desde una URL o archivo HTML local
directamente a la carpeta de Investigación (Research) del Binder sin dependencias externas:
- Extracción de título (<title>, <h1> o metadatos OpenGraph).
- Limpieza de scripts, anuncios, hojas de estilo y menús de navegación.
- Conversión a texto enriquecido editorial estructurado con párrafos y subtítulos.
- Registro de URL de procedencia y fecha de captura en las notas de investigación.
"""

import re
import html
import urllib.request
import urllib.error
import datetime
from pathlib import Path
from html.parser import HTMLParser
from typing import Union, Dict, Any, Optional, List, Tuple

from ..project import EscritorioProject, BinderItem
from ..rtf_engine import RTFEngine


class _HTMLContentExtractor(HTMLParser):
    """Parser SAX ligero de HTML para extraer texto estructurado y título."""

    def __init__(self):
        super().__init__()
        self.title: str = ""
        self.in_title: bool = False
        self.in_ignored_tag: bool = False
        self.ignored_tags = {"script", "style", "noscript", "svg", "nav", "footer", "header"}
        self.current_tag_stack: List[str] = []

        self.paragraphs: List[str] = []
        self.current_p: List[str] = []
        self.current_is_heading: bool = False

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        tag_lower = tag.lower()
        self.current_tag_stack.append(tag_lower)

        if tag_lower in self.ignored_tags:
            self.in_ignored_tag = True
            return

        if tag_lower == "title":
            self.in_title = True
        elif tag_lower in ("p", "div", "article", "section", "blockquote"):
            self._flush_paragraph()
        elif tag_lower in ("h1", "h2", "h3", "h4"):
            self._flush_paragraph()
            self.current_is_heading = True
        elif tag_lower in ("br", "hr"):
            self._flush_paragraph()

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        if self.current_tag_stack and self.current_tag_stack[-1] == tag_lower:
            self.current_tag_stack.pop()

        if tag_lower in self.ignored_tags:
            self.in_ignored_tag = any(t in self.ignored_tags for t in self.current_tag_stack)
            return

        if tag_lower == "title":
            self.in_title = False
        elif tag_lower in ("p", "div", "article", "section", "blockquote", "h1", "h2", "h3", "h4"):
            self._flush_paragraph()
            self.current_is_heading = False

    def handle_data(self, data: str):
        if self.in_ignored_tag:
            return

        text = data.strip()
        if not text:
            return

        if self.in_title:
            self.title = (self.title + " " + text).strip()
        else:
            self.current_p.append(text)

    def _flush_paragraph(self):
        if self.current_p:
            p_text = " ".join(self.current_p).strip()
            if p_text:
                if self.current_is_heading:
                    self.paragraphs.append(f"\n### {p_text}\n")
                else:
                    self.paragraphs.append(p_text)
            self.current_p = []


class WebImporter:
    """Importador de páginas web y artículos de investigación para el Binder."""

    @classmethod
    def import_from_url_or_file(
        cls,
        source: Union[str, Path],
        project: EscritorioProject,
        parent_uuid: Optional[str] = None,
        custom_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Descarga o lee un documento HTML y lo añade a la carpeta de investigación del Binder.
        """
        source_str = str(source).strip()
        is_url = bool(re.match(r"^https?://", source_str, re.IGNORECASE))

        if is_url:
            html_text, original_url = cls._fetch_url(source_str)
        else:
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"Archivo HTML no encontrado: {path}")
            html_text = path.read_text(encoding="utf-8", errors="ignore")
            original_url = str(path.resolve())

        # Parsear HTML
        extractor = _HTMLContentExtractor()
        extractor.feed(html_text)

        title = custom_title or extractor.title or (Path(source_str).stem if not is_url else "Página Web")
        title = html.unescape(title)
        body_text = "\n\n".join(extractor.paragraphs).strip()

        if not body_text:
            body_text = "No se pudo extraer contenido textual principal de la página."

        # Destino: Research Folder o parent especificado
        if not parent_uuid:
            research_folder = project.get_research_folder()
            target_uuid = research_folder.uuid if research_folder else (
                project.root_items[0].uuid if project.root_items else ""
            )
        else:
            target_uuid = parent_uuid

        # Crear ítem en el Binder
        new_item = project.add_item(
            parent_uuid=target_uuid,
            title=title[:80],
            item_type="Text"
        )

        # Generar contenido RTF
        rtf_content = RTFEngine.plain_text_to_rtf(body_text)
        new_item.write_content_rtf(rtf_content)

        # Guardar URL y metadatos en notas del documento
        capture_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notes_text = (
            f"--- Fuente Web / Referencia ---\n"
            f"URL Original: {original_url}\n"
            f"Fecha de Captura: {capture_date}\n"
            f"Título Original: {title}\n"
        )
        new_item.write_notes_rtf(RTFEngine.plain_text_to_rtf(notes_text))
        new_item.write_synopsis(f"Página web importada: {title}\nOrigen: {original_url}")

        project.save_all()

        return {
            "success": True,
            "title": title,
            "url": original_url,
            "item_uuid": new_item.uuid,
            "item": new_item,
            "words_imported": RTFEngine.count_words(body_text)
        }

    @staticmethod
    def _fetch_url(url: str, timeout: int = 10) -> Tuple[str, str]:
        """Descarga el HTML usando cabecera User-Agent estándar para evitar bloqueos 403."""
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36 Escritorio/1.0"
                )
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            raw_bytes = response.read()
            html_text = raw_bytes.decode(charset, errors="ignore")
            final_url = response.geturl()
            return html_text, final_url
