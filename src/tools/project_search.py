"""
Project Search & Replace Engine para Escritorio.
Búsqueda y reemplazo global en todo el proyecto:
- Ámbitos de búsqueda: Todo el Proyecto (ALL), solo Texto (TEXT), Sinopsis (SYNOPSIS),
  Notas del Documento (NOTES) o Títulos (TITLES).
- Soporte de Expresiones Regulares (Regex / sintaxis PCRE2).
- Distinción de mayúsculas/minúsculas y palabras completas.
- Extracción de snippets con contexto circundante.
- Función de Reemplazo individual y Reemplazo masivo en todo el manuscrito.
- Opción de guardar los resultados encontrados como Colección dinámica en el Binder.
"""

import re
from enum import Enum
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from ..core.project import EscritorioProject, BinderItem
from ..core.rtf_engine import RTFEngine


class SearchScope(Enum):
    ALL = "all"            # Todo el proyecto (Texto, Sinopsis, Notas y Título)
    TEXT = "text"          # Solo contenido principal (content.rtf)
    SYNOPSIS = "synopsis"  # Solo sinopsis de tarjeta (synopsis.txt)
    NOTES = "notes"        # Solo notas del inspector (notes.rtf)
    TITLES = "titles"      # Solo títulos de documentos y carpetas


@dataclass
class SearchMatch:
    item_uuid: str
    item_title: str
    field_name: str       # "text", "synopsis", "notes", "title"
    match_text: str
    start_offset: int
    end_offset: int
    line_number: int
    context_snippet: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_uuid": self.item_uuid,
            "item_title": self.item_title,
            "field_name": self.field_name,
            "match_text": self.match_text,
            "start_offset": self.start_offset,
            "end_offset": self.end_offset,
            "line_number": self.line_number,
            "context_snippet": self.context_snippet
        }


class ProjectSearchEngine:
    """Motor de búsqueda y reemplazo a nivel de proyecto."""

    @classmethod
    def _compile_pattern(
        cls,
        query: str,
        use_regex: bool = False,
        case_sensitive: bool = False,
        whole_words: bool = False
    ) -> Tuple[Optional[re.Pattern], Optional[str]]:
        if not query:
            return None, "Consulta vacía"

        flags = re.UNICODE
        if not case_sensitive:
            flags |= re.IGNORECASE

        pattern_str = query
        if not use_regex:
            pattern_str = re.escape(query)

        if whole_words:
            pattern_str = rf"\b{pattern_str}\b"

        try:
            compiled = re.compile(pattern_str, flags)
            return compiled, None
        except re.error as err:
            return None, f"Error en expresión regular: {err}"

    @classmethod
    def _create_snippet(cls, text: str, start: int, end: int, context_chars: int = 40) -> str:
        snippet_start = max(0, start - context_chars)
        snippet_end = min(len(text), end + context_chars)

        prefix = "..." if snippet_start > 0 else ""
        suffix = "..." if snippet_end < len(text) else ""

        lead = text[snippet_start:start]
        matched = text[start:end]
        trail = text[end:snippet_end]

        return f"{prefix}{lead}[{matched}]{trail}{suffix}".replace("\n", " ").replace("\r", "")

    @classmethod
    def search_project(
        cls,
        project: EscritorioProject,
        query: str,
        scope: SearchScope = SearchScope.ALL,
        use_regex: bool = False,
        case_sensitive: bool = False,
        whole_words: bool = False
    ) -> Tuple[List[SearchMatch], Optional[str]]:
        """
        Ejecuta la búsqueda en el proyecto según el alcance y filtros seleccionados.
        Retorna (lista_de_coincidencias, mensaje_de_error).
        """
        pattern, err = cls._compile_pattern(query, use_regex, case_sensitive, whole_words)
        if err or not pattern:
            return [], err

        results: List[SearchMatch] = []

        def search_in_text(raw_text: str, item: BinderItem, field_name: str):
            for m in pattern.finditer(raw_text):
                start, end = m.span()
                line_no = raw_text[:start].count("\n") + 1
                snippet = cls._create_snippet(raw_text, start, end)
                results.append(SearchMatch(
                    item_uuid=item.uuid,
                    item_title=item.title,
                    field_name=field_name,
                    match_text=m.group(0),
                    start_offset=start,
                    end_offset=end,
                    line_number=line_no,
                    context_snippet=snippet
                ))

        # Recorrer todos los elementos del proyecto
        items = project.get_all_items() if hasattr(project, "get_all_items") else list(getattr(project, "items_by_uuid", {}).values())
        for item in items:
            # 1. Títulos
            if scope in (SearchScope.ALL, SearchScope.TITLES):
                search_in_text(item.title, item, "title")

            # 2. Texto principal
            if scope in (SearchScope.ALL, SearchScope.TEXT) and item.item_type.lower() == "text":
                rtf_content = item.read_content_rtf()
                plain_text = RTFEngine.rtf_to_plain_text(rtf_content)
                search_in_text(plain_text, item, "text")

            # 3. Sinopsis
            if scope in (SearchScope.ALL, SearchScope.SYNOPSIS):
                synopsis = item.read_synopsis()
                if synopsis:
                    search_in_text(synopsis, item, "synopsis")

            # 4. Notas
            if scope in (SearchScope.ALL, SearchScope.NOTES) and item.item_type.lower() == "text":
                notes_rtf = item.read_notes_rtf()
                notes_plain = RTFEngine.rtf_to_plain_text(notes_rtf) if notes_rtf else ""
                if notes_plain:
                    search_in_text(notes_plain, item, "notes")

        return results, None

    @classmethod
    def replace_all(
        cls,
        project: EscritorioProject,
        query: str,
        replacement: str,
        scope: SearchScope = SearchScope.ALL,
        use_regex: bool = False,
        case_sensitive: bool = False,
        whole_words: bool = False
    ) -> Tuple[int, Optional[str]]:
        """
        Reemplaza todas las coincidencias en los documentos del proyecto.
        Retorna (total_reemplazos, mensaje_de_error).
        """
        pattern, err = cls._compile_pattern(query, use_regex, case_sensitive, whole_words)
        if err or not pattern:
            return 0, err

        total_replacements = 0
        items = project.get_all_items() if hasattr(project, "get_all_items") else list(getattr(project, "items_by_uuid", {}).values())
        for item in items:
            modified = False

            # 1. Título
            if scope in (SearchScope.ALL, SearchScope.TITLES):
                new_title, count = pattern.subn(replacement, item.title)
                if count > 0:
                    item.title = new_title
                    total_replacements += count
                    modified = True

            # 2. Texto principal
            if scope in (SearchScope.ALL, SearchScope.TEXT) and item.item_type.lower() == "text":
                rtf_content = item.read_content_rtf()
                plain = RTFEngine.rtf_to_plain_text(rtf_content)
                new_plain, count = pattern.subn(replacement, plain)
                if count > 0:
                    new_rtf = RTFEngine.plain_text_to_rtf(new_plain)
                    item.write_content_rtf(new_rtf)
                    total_replacements += count
                    modified = True

            # 3. Sinopsis
            if scope in (SearchScope.ALL, SearchScope.SYNOPSIS):
                syn = item.read_synopsis()
                if syn:
                    new_syn, count = pattern.subn(replacement, syn)
                    if count > 0:
                        item.write_synopsis(new_syn)
                        total_replacements += count
                        modified = True

            # 4. Notas
            if scope in (SearchScope.ALL, SearchScope.NOTES) and item.item_type.lower() == "text":
                notes_rtf = item.read_notes_rtf()
                notes_plain = RTFEngine.rtf_to_plain_text(notes_rtf) if notes_rtf else ""
                if notes_plain:
                    new_notes, count = pattern.subn(replacement, notes_plain)
                    if count > 0:
                        new_notes_rtf = RTFEngine.plain_text_to_rtf(new_notes)
                        item.write_notes_rtf(new_notes_rtf)
                        total_replacements += count
                        modified = True

            if modified:
                item.save_if_dirty()

        project.save_structure()
        return total_replacements, None

    @classmethod
    def save_as_collection(
        cls,
        project: EscritorioProject,
        collection_name: str,
        matches: List[SearchMatch],
        color_hex: str = "#3B82F6"
    ) -> bool:
        """
        Guarda los documentos coincidentes como una Colección en el proyecto.
        """
        # Extraer lista de UUIDs únicos conservando el orden de aparición
        seen_uuids = set()
        matched_uuids = []
        for m in matches:
            if m.item_uuid not in seen_uuids:
                seen_uuids.add(m.item_uuid)
                matched_uuids.append(m.item_uuid)

        # Si el proyecto tiene gestor de colecciones o método directo
        if hasattr(project, "add_collection"):
            project.add_collection(name=collection_name, item_uuids=matched_uuids, color_hex=color_hex)
            return True
        elif hasattr(project, "collections_manager"):
            project.collections_manager.create_collection(name=collection_name, item_uuids=matched_uuids, color_hex=color_hex)
            return True

        # Almacenar en metadatos del proyecto
        if not hasattr(project, "saved_collections"):
            project.saved_collections = {}
        project.saved_collections[collection_name] = {
            "name": collection_name,
            "uuids": matched_uuids,
            "color": color_hex,
            "count": len(matched_uuids)
        }
        return True
