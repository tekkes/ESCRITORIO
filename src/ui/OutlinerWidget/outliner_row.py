"""
Outliner Row Node para Escritorio
Representación jerárquica de cada fila en el Esquema con:
- Cálculos recursivos de palabras, caracteres y objetivos totales
- Barra de progreso con gradiente cromático
- Edición directa in-situ de todas las propiedades
- Sincronización transparente con el BinderItem del proyecto
"""

from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path

from ...core.project import BinderItem, EscritorioProject
from ...core.rtf_engine import RTFEngine
from .outliner_columns import StandardColumnId, calculate_progress_color


class OutlinerRow:
    """Nodo jerárquico del Esquematizador."""

    def __init__(self, item: BinderItem, level: int = 0, project: Optional[EscritorioProject] = None):
        self.item: BinderItem = item
        self.uuid: str = item.uuid
        self.level: int = level
        self.project: Optional[EscritorioProject] = project or getattr(item, "project", None)
        self.expanded: bool = True
        self.children: List['OutlinerRow'] = []

        # Cachés de métricas calculadas
        self._cached_direct_words: Optional[int] = None
        self._cached_direct_chars: Optional[int] = None

    def invalidate_metrics(self):
        """Invalida las cachés tras ediciones directas."""
        self._cached_direct_words = None
        self._cached_direct_chars = None

    # =========================================================================
    # Propiedades Básicas del Documento
    # =========================================================================

    @property
    def title(self) -> str:
        return self.item.title

    @property
    def synopsis(self) -> str:
        if getattr(self.item, "project", None):
            return self.item.read_synopsis()
        return getattr(self.item, "_dummy_synopsis", "")

    @property
    def item_type(self) -> str:
        return self.item.item_type

    @property
    def is_folder(self) -> bool:
        return self.item.item_type == "Folder" or bool(self.children)

    @property
    def include_in_compile(self) -> bool:
        return getattr(self.item.data, "include_in_compile", True)

    @property
    def section_type(self) -> str:
        return getattr(self.item.data, "section_type", "Structure Based")

    @property
    def label_id(self) -> int:
        return getattr(self.item.data, "label_id", -1)

    @property
    def status_id(self) -> int:
        return getattr(self.item.data, "status_id", -1)

    @property
    def target(self) -> int:
        return getattr(self.item.data, "target_words", 0)

    @property
    def keywords(self) -> List[str]:
        return list(getattr(self.item.data, "keywords", []))

    @property
    def created_date(self) -> str:
        return getattr(self.item.data, "created", "")

    @property
    def modified_date(self) -> str:
        return getattr(self.item.data, "modified", "")

    @property
    def custom_metadata(self) -> Dict[str, str]:
        return dict(getattr(self.item.data, "custom_metadata", {}))

    # =========================================================================
    # Cálculos Recursivos de Palabras, Caracteres y Objetivos
    # =========================================================================

    @property
    def words(self) -> int:
        """Palabras del texto propio del documento."""
        if self._cached_direct_words is None:
            if getattr(self.item, "project", None):
                rtf = self.item.read_content_rtf()
                self._cached_direct_words = RTFEngine.count_words(rtf, is_rtf=True)
            else:
                self._cached_direct_words = 0
        return self._cached_direct_words

    @property
    def characters(self) -> int:
        """Caracteres del texto propio del documento."""
        if self._cached_direct_chars is None:
            if getattr(self.item, "project", None):
                rtf = self.item.read_content_rtf()
                self._cached_direct_chars = RTFEngine.count_characters(rtf, is_rtf=True)
            else:
                self._cached_direct_chars = 0
        return self._cached_direct_chars

    @property
    def total_words(self) -> int:
        """Suma recursiva de palabras del nodo y todos sus descendientes."""
        child_sum = sum(child.total_words for child in self.children)
        return self.words + child_sum

    @property
    def total_characters(self) -> int:
        """Suma recursiva de caracteres del nodo y todos sus descendientes."""
        child_sum = sum(child.total_characters for child in self.children)
        return self.characters + child_sum

    @property
    def total_target(self) -> int:
        """Suma recursiva del objetivo de palabras del nodo y sus descendientes."""
        child_sum = sum(child.total_target for child in self.children)
        return self.target + child_sum

    @property
    def progress_percent(self) -> float:
        """
        Porcentaje de progreso hacia el objetivo:
        - Si el ítem tiene un target directo > 0, calcula (words / target * 100).
        - Si es carpeta/contenedor sin target directo pero con total_target > 0, calcula (total_words / total_target * 100).
        """
        tgt = self.target
        curr = self.words
        if tgt <= 0 and self.total_target > 0:
            tgt = self.total_target
            curr = self.total_words

        if tgt <= 0:
            return 0.0
        return min(100.0, round((curr / tgt) * 100.0, 1))

    @property
    def progress_color(self) -> str:
        """Color interpolado según el avance hacia la meta."""
        return calculate_progress_color(self.progress_percent)

    # =========================================================================
    # Edición In-Situ de Propiedades
    # =========================================================================

    def set_title(self, new_title: str) -> str:
        clean = new_title.strip()
        if clean:
            self.item.title = clean
            if hasattr(self.item, "data"):
                self.item.data.title = clean
            self.item.mark_dirty()
        return self.item.title

    def set_synopsis(self, new_synopsis: str) -> str:
        if getattr(self.item, "project", None):
            self.item.write_synopsis(new_synopsis)
            self.item.save_if_dirty()
        else:
            setattr(self.item, "_dummy_synopsis", new_synopsis)
        return new_synopsis

    def set_target(self, new_target: int) -> int:
        val = max(0, int(new_target))
        if hasattr(self.item, "data"):
            self.item.data.target_words = val
            self.item.mark_dirty()
        return val

    def set_label(self, label_id: int):
        if hasattr(self.item, "data"):
            self.item.data.label_id = label_id
            self.item.mark_dirty()

    def set_status(self, status_id: int):
        if hasattr(self.item, "data"):
            self.item.data.status_id = status_id
            self.item.mark_dirty()

    def set_section_type(self, section_type: str):
        if hasattr(self.item, "data"):
            self.item.data.section_type = section_type
            self.item.mark_dirty()

    def set_include_in_compile(self, include: bool):
        if hasattr(self.item, "data"):
            self.item.data.include_in_compile = bool(include)
            self.item.mark_dirty()

    def set_custom_metadata(self, key: str, value: str):
        if hasattr(self.item, "data"):
            if not hasattr(self.item.data, "custom_metadata") or self.item.data.custom_metadata is None:
                self.item.data.custom_metadata = {}
            clean_key = key.replace("custom:", "")
            self.item.data.custom_metadata[clean_key] = str(value)
            self.item.mark_dirty()

    def remove_custom_metadata(self, key: str):
        if hasattr(self.item, "data") and self.item.data.custom_metadata:
            clean_key = key.replace("custom:", "")
            self.item.data.custom_metadata.pop(clean_key, None)
            self.item.mark_dirty()

    # =========================================================================
    # Consulta de Valores por Columna
    # =========================================================================

    def get_cell_value(self, col_id: str) -> Any:
        """Obtiene el valor formateado para una columna específica."""
        if col_id == StandardColumnId.TITLE_AND_SYNOPSIS.value:
            return {
                "title": self.title,
                "synopsis": self.synopsis
            }
        elif col_id == StandardColumnId.TITLE.value:
            return self.title
        elif col_id == StandardColumnId.SYNOPSIS.value:
            return self.synopsis
        elif col_id == StandardColumnId.LABEL.value:
            return self.label_id
        elif col_id == StandardColumnId.STATUS.value:
            return self.status_id
        elif col_id == StandardColumnId.SECTION_TYPE.value:
            return self.section_type
        elif col_id == StandardColumnId.INCLUDE_IN_COMPILE.value:
            return self.include_in_compile
        elif col_id == StandardColumnId.WORDS.value:
            return self.words
        elif col_id == StandardColumnId.TOTAL_WORDS.value:
            return self.total_words
        elif col_id == StandardColumnId.CHARACTERS.value:
            return self.characters
        elif col_id == StandardColumnId.TOTAL_CHARACTERS.value:
            return self.total_characters
        elif col_id == StandardColumnId.TARGET.value:
            return self.target
        elif col_id == StandardColumnId.TOTAL_TARGET.value:
            return self.total_target
        elif col_id == StandardColumnId.PROGRESS.value:
            return {
                "percent": self.progress_percent,
                "color": self.progress_color
            }
        elif col_id == StandardColumnId.KEYWORDS.value:
            return self.keywords
        elif col_id == StandardColumnId.CREATED_DATE.value:
            return self.created_date
        elif col_id == StandardColumnId.MODIFIED_DATE.value:
            return self.modified_date
        elif col_id.startswith("custom:"):
            key = col_id.replace("custom:", "")
            return self.custom_metadata.get(key, "")

        return self.custom_metadata.get(col_id, "")

    def matches_query(self, query: str) -> bool:
        """Verifica si la fila coincide con una búsqueda de texto."""
        q = query.lower().strip()
        if not q:
            return True

        if q in self.title.lower():
            return True
        if q in self.synopsis.lower():
            return True
        if any(q in kw.lower() for kw in self.keywords):
            return True
        if any(q in str(v).lower() for v in self.custom_metadata.values()):
            return True
        if getattr(self.item, "project", None):
            body_rtf = self.item.read_content_rtf()
            if body_rtf and q in RTFEngine.rtf_to_plain_text(body_rtf).lower():
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Exporta el estado completo de la fila a un diccionario."""
        return {
            "uuid": self.uuid,
            "level": self.level,
            "expanded": self.expanded,
            "is_folder": self.is_folder,
            "title": self.title,
            "synopsis": self.synopsis,
            "words": self.words,
            "total_words": self.total_words,
            "characters": self.characters,
            "total_characters": self.total_characters,
            "target": self.target,
            "total_target": self.total_target,
            "progress_percent": self.progress_percent,
            "progress_color": self.progress_color,
            "include_in_compile": self.include_in_compile,
            "section_type": self.section_type,
            "label_id": self.label_id,
            "status_id": self.status_id,
            "keywords": self.keywords,
            "created": self.created_date,
            "modified": self.modified_date,
            "custom_metadata": self.custom_metadata,
            "children_count": len(self.children)
        }
