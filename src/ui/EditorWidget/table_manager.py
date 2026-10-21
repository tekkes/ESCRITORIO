"""
TableManager para Escritorio
Gestión e inserción de tablas editables compatibles con Scrivener 3 y RTF 1.5 - 1.9:
- Generación de tablas con sintaxis RTF: \\trowd \\cellx... \\cell \\row
- Inserción de filas y columnas dinámicas
- Modificación de ancho de celdas y bordes.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class TableCell:
    content: str = ""
    width_pt: float = 120.0
    align: str = "left"


@dataclass
class TableRow:
    cells: List[TableCell] = field(default_factory=list)


@dataclass
class EditableTable:
    rows: List[TableRow] = field(default_factory=list)

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def col_count(self) -> int:
        return len(self.rows[0].cells) if self.rows else 0


class TableManager:
    """Motor de creación y edición de tablas RTF."""

    @classmethod
    def create_table(cls, num_rows: int, num_cols: int, default_cell_width_pt: float = 100.0) -> EditableTable:
        """Crea una nueva tabla vacía con las dimensiones indicadas."""
        rows = []
        for _ in range(max(1, num_rows)):
            cells = [TableCell(content="", width_pt=default_cell_width_pt) for _ in range(max(1, num_cols))]
            rows.append(TableRow(cells=cells))
        return EditableTable(rows=rows)

    @classmethod
    def add_row(cls, table: EditableTable, at_index: Optional[int] = None) -> TableRow:
        col_c = table.col_count or 1
        width = table.rows[0].cells[0].width_pt if table.rows else 100.0
        new_row = TableRow(cells=[TableCell(content="", width_pt=width) for _ in range(col_c)])
        if at_index is None or at_index >= len(table.rows):
            table.rows.append(new_row)
        else:
            table.rows.insert(max(0, at_index), new_row)
        return new_row

    @classmethod
    def delete_row(cls, table: EditableTable, index: int) -> bool:
        if 0 <= index < len(table.rows) and len(table.rows) > 1:
            table.rows.pop(index)
            return True
        return False

    @classmethod
    def add_column(cls, table: EditableTable, width_pt: float = 100.0) -> int:
        for r in table.rows:
            r.cells.append(TableCell(content="", width_pt=width_pt))
        return table.col_count

    @classmethod
    def delete_column(cls, table: EditableTable, col_index: int) -> bool:
        if table.col_count > 1 and 0 <= col_index < table.col_count:
            for r in table.rows:
                r.cells.pop(col_index)
            return True
        return False

    @classmethod
    def table_to_rtf(cls, table: EditableTable) -> str:
        """Serializa la tabla a sintaxis canónica RTF compatible con Scrivener y Microsoft Word."""
        rtf_parts = [r"\par "]
        for row in table.rows:
            # Encabezado de fila
            rtf_parts.append(r"\trowd\trgaph108\trleft0")
            # Definir límites derechos acumulativos de cada celda (en twips: 1 pt = 20 twips)
            accum_twips = 0
            for cell in row.cells:
                accum_twips += int(cell.width_pt * 20)
                rtf_parts.append(rf"\cellx{accum_twips}")

            # Contenido de cada celda
            for cell in row.cells:
                content_escaped = cell.content.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
                rtf_parts.append(rf"\pard\intbl {content_escaped}\cell ")

            rtf_parts.append(r"\row ")

        rtf_parts.append(r"\pard\par ")
        return "".join(rtf_parts)
