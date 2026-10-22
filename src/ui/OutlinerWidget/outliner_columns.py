"""
Outliner Columns Selector and Definitions para Escritorio
Gestor compacto y dinámico de columnas del Esquematizador jerárquico:
- Title & Synopsis (combinado) o separados Title y Synopsis
- Label, Status, Section Type, Include in Compile
- Words, Total Words, Characters, Total Characters
- Target, Total Target, Progress (con gradiente dinámico de color)
- Keywords, Created Date, Modified Date
- Metadatos Personalizados (Custom Metadata) dinámicos del proyecto
"""

from enum import Enum
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field


class ColumnType(Enum):
    TEXT = "text"
    NUMERIC = "numeric"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    PROGRESS_BAR = "progress_bar"
    CHIPS = "chips"
    DATE = "date"


class StandardColumnId(Enum):
    TITLE_AND_SYNOPSIS = "title_synopsis"
    TITLE = "title"
    SYNOPSIS = "synopsis"
    LABEL = "label"
    STATUS = "status"
    SECTION_TYPE = "section_type"
    INCLUDE_IN_COMPILE = "include_in_compile"
    WORDS = "words"
    TOTAL_WORDS = "total_words"
    CHARACTERS = "characters"
    TOTAL_CHARACTERS = "total_characters"
    TARGET = "target"
    TOTAL_TARGET = "total_target"
    PROGRESS = "progress"
    KEYWORDS = "keywords"
    CREATED_DATE = "created_date"
    MODIFIED_DATE = "modified_date"


@dataclass
class OutlinerColumn:
    """Definición y estado de visualización de una columna del Esquema."""
    col_id: str
    title: str
    column_type: ColumnType = ColumnType.TEXT
    visible: bool = True
    width: int = 120
    min_width: int = 40
    is_custom_metadata: bool = False
    editable: bool = False
    tooltip: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "col_id": self.col_id,
            "title": self.title,
            "column_type": self.column_type.value,
            "visible": self.visible,
            "width": self.width,
            "min_width": self.min_width,
            "is_custom_metadata": self.is_custom_metadata,
            "editable": self.editable,
            "tooltip": self.tooltip
        }


def calculate_progress_color(percent: float) -> str:
    """
    Calcula gradualmente el color de la barra de progreso:
    - 0%: Rojo (#EF4444)
    - 50%: Ámbar (#F59E0B)
    - 100%: Verde (#10B981) o Azul (#3B82F6) para sobrecumplimiento
    """
    p = max(0.0, min(100.0, percent))

    if p <= 50.0:
        # Interpolar entre Rojo (239, 68, 68) y Ámbar (245, 158, 11)
        factor = p / 50.0
        r = int(239 + (245 - 239) * factor)
        g = int(68 + (158 - 68) * factor)
        b = int(68 + (11 - 68) * factor)
    else:
        # Interpolar entre Ámbar (245, 158, 11) y Verde (16, 185, 129)
        factor = (p - 50.0) / 50.0
        r = int(245 + (16 - 245) * factor)
        g = int(158 + (185 - 158) * factor)
        b = int(11 + (129 - 11) * factor)

    return f"#{r:02X}{g:02X}{b:02X}"


class ColumnSelector:
    """Selector compacto y gestor de visibilidad y anchos de columnas."""

    def __init__(self, combined_title_synopsis: bool = True):
        self.combined_title_synopsis: bool = combined_title_synopsis
        self.columns: Dict[str, OutlinerColumn] = {}
        self.on_columns_changed: Optional[Callable[[], None]] = None

        self._init_standard_columns()

    def _init_standard_columns(self):
        """Inicializa las columnas predeterminadas con sus tipos y anchos ergonomicos."""
        defs = [
            OutlinerColumn(
                col_id=StandardColumnId.TITLE_AND_SYNOPSIS.value,
                title="Título y Sinopsis",
                column_type=ColumnType.TEXT,
                visible=self.combined_title_synopsis,
                width=320,
                min_width=160,
                editable=True,
                tooltip="Título y resumen sinóptico combinado en la misma celda"
            ),
            OutlinerColumn(
                col_id=StandardColumnId.TITLE.value,
                title="Título",
                column_type=ColumnType.TEXT,
                visible=not self.combined_title_synopsis,
                width=220,
                min_width=120,
                editable=True,
                tooltip="Título del documento o carpeta"
            ),
            OutlinerColumn(
                col_id=StandardColumnId.SYNOPSIS.value,
                title="Sinopsis",
                column_type=ColumnType.TEXT,
                visible=not self.combined_title_synopsis,
                width=240,
                min_width=120,
                editable=True,
                tooltip="Sinopsis del documento (synopsis.txt)"
            ),
            OutlinerColumn(
                col_id=StandardColumnId.LABEL.value,
                title="Etiqueta",
                column_type=ColumnType.DROPDOWN,
                visible=True,
                width=110,
                min_width=80,
                editable=True,
                tooltip="Etiqueta cromática del proyecto"
            ),
            OutlinerColumn(
                col_id=StandardColumnId.STATUS.value,
                title="Estado",
                column_type=ColumnType.DROPDOWN,
                visible=True,
                width=100,
                min_width=70,
                editable=True,
                tooltip="Estado de avance del documento"
            ),
            OutlinerColumn(
                col_id=StandardColumnId.SECTION_TYPE.value,
                title="Tipo Sección",
                column_type=ColumnType.DROPDOWN,
                visible=True,
                width=120,
                min_width=80,
                editable=True,
                tooltip="Tipo de sección estructural para la compilación"
            ),
            OutlinerColumn(
                col_id=StandardColumnId.INCLUDE_IN_COMPILE.value,
                title="Compilar",
                column_type=ColumnType.CHECKBOX,
                visible=True,
                width=75,
                min_width=60,
                editable=True,
                tooltip="Incluir o excluir en la compilación"
            ),
            OutlinerColumn(
                col_id=StandardColumnId.WORDS.value,
                title="Palabras",
                column_type=ColumnType.NUMERIC,
                visible=True,
                width=80,
                min_width=60,
                tooltip="Palabras directas del documento"
            ),
            OutlinerColumn(
                col_id=StandardColumnId.TOTAL_WORDS.value,
                title="Total Palabras",
                column_type=ColumnType.NUMERIC,
                visible=True,
                width=100,
                min_width=70,
                tooltip="Palabras recursivas sumando todos los descendientes"
            ),
            OutlinerColumn(
                col_id=StandardColumnId.CHARACTERS.value,
                title="Caracteres",
                column_type=ColumnType.NUMERIC,
                visible=False,
                width=85,
                min_width=60,
                tooltip="Caracteres directos del documento"
            ),
            OutlinerColumn(
                col_id=StandardColumnId.TOTAL_CHARACTERS.value,
                title="Total Caracteres",
                column_type=ColumnType.NUMERIC,
                visible=False,
                width=110,
                min_width=75,
                tooltip="Caracteres recursivos sumando todos los descendientes"
            ),
            OutlinerColumn(
                col_id=StandardColumnId.TARGET.value,
                title="Objetivo",
                column_type=ColumnType.NUMERIC,
                visible=True,
                width=80,
                min_width=60,
                editable=True,
                tooltip="Objetivo de palabras asignado a este ítem"
            ),
            OutlinerColumn(
                col_id=StandardColumnId.TOTAL_TARGET.value,
                title="Total Objetivo",
                column_type=ColumnType.NUMERIC,
                visible=True,
                width=105,
                min_width=75,
                tooltip="Suma recursiva de objetivos de toda la rama"
            ),
            OutlinerColumn(
                col_id=StandardColumnId.PROGRESS.value,
                title="Progreso",
                column_type=ColumnType.PROGRESS_BAR,
                visible=True,
                width=120,
                min_width=90,
                tooltip="Barra de avance hacia el objetivo (Rojo -> Ámbar -> Verde)"
            ),
            OutlinerColumn(
                col_id=StandardColumnId.KEYWORDS.value,
                title="Palabras Clave",
                column_type=ColumnType.CHIPS,
                visible=False,
                width=140,
                min_width=90,
                tooltip="Etiquetas temáticas del documento"
            ),
            OutlinerColumn(
                col_id=StandardColumnId.CREATED_DATE.value,
                title="Fecha Creación",
                column_type=ColumnType.DATE,
                visible=False,
                width=125,
                min_width=90,
                tooltip="Fecha y hora de creación"
            ),
            OutlinerColumn(
                col_id=StandardColumnId.MODIFIED_DATE.value,
                title="Fecha Modificación",
                column_type=ColumnType.DATE,
                visible=True,
                width=135,
                min_width=90,
                tooltip="Última fecha y hora de modificación"
            ),
        ]

        for col in defs:
            self.columns[col.col_id] = col

    def set_combined_title_synopsis(self, combined: bool):
        """Alterna entre celda única 'Título y Sinopsis' o columnas separadas 'Título' y 'Sinopsis'."""
        self.combined_title_synopsis = combined
        if combined:
            self.set_visible(StandardColumnId.TITLE_AND_SYNOPSIS.value, True)
            self.set_visible(StandardColumnId.TITLE.value, False)
            self.set_visible(StandardColumnId.SYNOPSIS.value, False)
        else:
            self.set_visible(StandardColumnId.TITLE_AND_SYNOPSIS.value, False)
            self.set_visible(StandardColumnId.TITLE.value, True)
            self.set_visible(StandardColumnId.SYNOPSIS.value, True)
        self._notify()

    def set_visible(self, col_id: str, visible: bool):
        if col_id in self.columns:
            self.columns[col_id].visible = visible
            self._notify()

    def toggle_column(self, col_id: str) -> bool:
        if col_id in self.columns:
            self.columns[col_id].visible = not self.columns[col_id].visible
            self._notify()
            return self.columns[col_id].visible
        return False

    def is_visible(self, col_id: str) -> bool:
        return self.columns.get(col_id, OutlinerColumn(col_id, "", visible=False)).visible

    def get_visible_columns(self) -> List[OutlinerColumn]:
        return [col for col in self.columns.values() if col.visible]

    def get_all_columns(self) -> List[OutlinerColumn]:
        return list(self.columns.values())

    def add_custom_metadata_column(self, field_id: str, title: Optional[str] = None, column_type: ColumnType = ColumnType.TEXT) -> OutlinerColumn:
        """Añade o activa dinámicamente una columna de metadatos personalizados."""
        key = f"custom:{field_id}" if not field_id.startswith("custom:") else field_id
        display_title = title or field_id.replace("custom:", "").replace("_", " ").title()

        col = OutlinerColumn(
            col_id=key,
            title=display_title,
            column_type=column_type,
            visible=True,
            width=120,
            min_width=60,
            is_custom_metadata=True,
            editable=True,
            tooltip=f"Metadato personalizado: {display_title}"
        )
        self.columns[key] = col
        self._notify()
        return col

    def set_column_width(self, col_id: str, width: int):
        if col_id in self.columns:
            col = self.columns[col_id]
            col.width = max(col.min_width, width)
            self._notify()

    def _notify(self):
        if self.on_columns_changed:
            self.on_columns_changed()
