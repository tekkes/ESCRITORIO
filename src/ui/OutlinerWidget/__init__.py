"""
Paquete OutlinerWidget de Escritorio
Vista matricial jerárquica de alto rendimiento para la planificación estructural de obras complejas (Ctrl+3).
"""

from .outliner_columns import (
    OutlinerColumn,
    ColumnSelector,
    ColumnType,
    StandardColumnId,
    calculate_progress_color
)
from .outliner_row import OutlinerRow
from .outliner_exporter import OutlinerExporter
from .outliner_widget import OutlinerWidget

__all__ = [
    "OutlinerColumn",
    "ColumnSelector",
    "ColumnType",
    "StandardColumnId",
    "calculate_progress_color",
    "OutlinerRow",
    "OutlinerExporter",
    "OutlinerWidget"
]
