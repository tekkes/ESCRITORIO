"""
Outliner View para Escritorio
Esquematizador tabular jerárquico con columnas configurables (Título, Sinopsis,
Recuento de palabras, Objetivo, Tipo de Sección, Estado, Etiqueta y Modificación).
"""

from typing import List, Dict, Any, Optional
from ..core.project import BinderItem

class OutlinerView:
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

    def __init__(self):
        self.parent_item: Optional[BinderItem] = None
        self.visible_columns = list(self.DEFAULT_COLUMNS)
        self.sort_by: Optional[str] = None
        self.sort_ascending: bool = True

    def load_container(self, item: BinderItem):
        self.parent_item = item

    def get_rows_data(self) -> List[Dict[str, Any]]:
        if not self.parent_item:
            return []

        rows = []
        for child in self.parent_item.children:
            rows.append({
                "uuid": child.uuid,
                "title": child.title,
                "synopsis": child.read_synopsis(),
                "word_count": child.get_word_count(),
                "target": child.data.target_words,
                "section_type": child.data.section_type,
                "label_id": child.data.label_id,
                "status_id": child.data.status_id,
                "created": child.data.created,
                "modified": child.data.modified
            })

        if self.sort_by:
            rows.sort(key=lambda r: r.get(self.sort_by, ""), reverse=not self.sort_ascending)

        return rows
