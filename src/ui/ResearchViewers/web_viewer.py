"""
WebArchiveViewer para Escritorio
Visor de páginas web archivadas (.html, .htm, .mhtml, .webarchive) para investigación.
Incluye:
- Modo Lectura (Reader Mode) con extracción limpia de contenido textual
- Búsqueda de texto dentro del documento web archivado
- Extracción de metadatos (título, autor, enlaces)
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
import re


class WebArchiveViewer:
    """Visor y analizador de páginas web archivadas."""

    SUPPORTED_EXTS = {".html", ".htm", ".mhtml", ".webarchive"}

    def __init__(self):
        self.file_path: Optional[str] = None
        self.raw_html: str = ""
        self.reader_mode_text: str = ""
        self.page_title: str = ""
        self.links: List[str] = []
        self.reader_mode: bool = True

    def load_file(self, file_path: str) -> bool:
        """Carga y procesa un archivo web archivado."""
        p = Path(file_path)
        if not p.exists() or p.suffix.lower() not in self.SUPPORTED_EXTS:
            return False

        self.file_path = str(p.resolve())
        try:
            self.raw_html = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return False

        self._parse_content()
        return True

    def load_html(self, html_string: str, title: str = "Página Web"):
        """Carga directamente una cadena HTML."""
        self.file_path = None
        self.raw_html = html_string
        self._parse_content()
        if not self.page_title:
            self.page_title = title

    def _parse_content(self):
        # 1. Extraer título
        title_match = re.search(r"<title>(.*?)</title>", self.raw_html, re.IGNORECASE | re.DOTALL)
        self.page_title = title_match.group(1).strip() if title_match else "Sin Título"

        # 2. Extraer enlaces
        self.links = re.findall(r'href=[\'"](https?://[^\'"]+)[\'"]', self.raw_html, re.IGNORECASE)

        # 3. Generar Modo Lectura (eliminar scripts, styles, comentarios y tags)
        clean = re.sub(r"<script.*?>.*?</script>", "", self.raw_html, flags=re.IGNORECASE | re.DOTALL)
        clean = re.sub(r"<style.*?>.*?</style>", "", clean, flags=re.IGNORECASE | re.DOTALL)
        clean = re.sub(r"<!--.*?-->", "", clean, flags=re.DOTALL)
        # Reemplazar saltos de bloque
        clean = re.sub(r"<(p|div|h[1-6]|li|br)[^>]*>", "\n", clean, flags=re.IGNORECASE)
        # Eliminar cualquier tag restante
        clean = re.sub(r"<[^>]+>", "", clean)
        # Normalizar espacios y saltos de línea repetidos
        clean = re.sub(r"\n\s*\n+", "\n\n", clean)
        self.reader_mode_text = clean.strip()

    def toggle_reader_mode(self) -> bool:
        self.reader_mode = not self.reader_mode
        return self.reader_mode

    def get_display_content(self) -> str:
        return self.reader_mode_text if self.reader_mode else self.raw_html

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Busca coincidencias en el texto extraído."""
        results = []
        if not query:
            return results

        text = self.reader_mode_text
        q_lower = query.lower()
        text_lower = text.lower()
        start = 0

        while True:
            idx = text_lower.find(q_lower, start)
            if idx == -1:
                break
            snippet_start = max(0, idx - 40)
            snippet_end = min(len(text), idx + len(query) + 40)
            results.append({
                "index": idx,
                "matched": text[idx:idx+len(query)],
                "snippet": "..." + text[snippet_start:snippet_end].replace("\n", " ") + "..."
            })
            start = idx + len(query)

        return results

    def get_state(self) -> dict:
        return {
            "file_path": self.file_path,
            "title": self.page_title,
            "reader_mode": self.reader_mode,
            "links_count": len(self.links),
            "text_length": len(self.reader_mode_text)
        }
