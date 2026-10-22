"""
Outliner View para Escritorio
Esquematizador tabular jerárquico con columnas configurables (Título, Sinopsis,
Recuento de palabras, Objetivo, Tipo de Sección, Estado, Etiqueta y Modificación).
Retrocompatible con OutlinerWidget.
"""

from typing import List, Dict, Any, Optional
from ..core.project import BinderItem, EscritorioProject
from .OutlinerWidget import (
    OutlinerWidget,
    OutlinerColumn,
    ColumnSelector,
    StandardColumnId,
    OutlinerRow,
    OutlinerExporter
)


class OutlinerView(OutlinerWidget):
    """Controlador y lógica del esquematizador tipo hoja de cálculo jerárquica."""

    DEFAULT_COLUMNS = [
        "title",
        "synopsis",
        "word_count",
        "target",
        "section_type",
        "label",
        "status",
        "modified"
    ]

    def __init__(self, project: Optional[EscritorioProject] = None):
        super().__init__(project=project, combined_title_synopsis=True)
        self.visible_columns = list(self.DEFAULT_COLUMNS)

    @property
    def sort_by(self) -> Optional[str]:
        return self.sort_column

    @sort_by.setter
    def sort_by(self, val: Optional[str]):
        self.sort_column = val

    def get_rows_data(self) -> List[Dict[str, Any]]:
        """Devuelve los datos de las filas para retrocompatibilidad."""
        if not self.parent_item:
            return []

        rows = []
        for child in self.parent_item.children:
            rows.append({
                "uuid": child.uuid,
                "title": child.title,
                "synopsis": child.read_synopsis() if getattr(child, "project", None) else "",
                "word_count": child.get_word_count() if hasattr(child, "get_word_count") else 0,
                "target": getattr(child.data, "target_words", 0),
                "section_type": getattr(child.data, "section_type", "Structure Based"),
                "label_id": getattr(child.data, "label_id", -1),
                "status_id": getattr(child.data, "status_id", -1),
                "created": getattr(child.data, "created", ""),
                "modified": getattr(child.data, "modified", "")
            })

        if self.sort_by:
            rows.sort(key=lambda r: r.get(self.sort_by, ""), reverse=not self.sort_ascending)

        return rows
