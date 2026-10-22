"""
Outliner CSV Exporter para Escritorio
Exportación directa y configurable de la tabla del Esquema a formato CSV:
- Preserva cabeceras, indentación jerárquica opcional, metadatos y comillas multilínea
- Soporte para columnas estándar y de metadatos personalizados
"""

import csv
import io
from typing import List, Dict, Optional, Any, Union
from pathlib import Path

from .outliner_row import OutlinerRow
from .outliner_columns import OutlinerColumn, StandardColumnId


class OutlinerExporter:
    """Motor de exportación tabular a archivo .csv."""

    @classmethod
    def export_to_csv(
        cls,
        rows: List[OutlinerRow],
        columns: List[OutlinerColumn],
        output_file_or_path: Optional[Union[str, Path]] = None,
        include_hierarchy_indent: bool = True
    ) -> str:
        """
        Exporta las filas dadas al formato CSV.
        Si se especifica output_file_or_path, escribe el archivo en disco.
        Retorna siempre la cadena de texto con el contenido CSV generado.
        """
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")

        # 1. Cabeceras
        headers = [col.title for col in columns]
        writer.writerow(headers)

        # 2. Filas de datos
        for row in rows:
            line = []
            for col in columns:
                val = cls._format_cell_for_csv(row, col, include_hierarchy_indent)
                line.append(val)
            writer.writerow(line)

        csv_text = output.getvalue()
        output.close()

        if output_file_or_path:
            p = Path(output_file_or_path).resolve()
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(csv_text, encoding="utf-8")

        return csv_text

    @classmethod
    def _format_cell_for_csv(cls, row: OutlinerRow, col: OutlinerColumn, include_hierarchy_indent: bool) -> str:
        """Formatea el valor de una celda para salida textual en CSV."""
        col_id = col.col_id

        if col_id == StandardColumnId.TITLE_AND_SYNOPSIS.value:
            indent = "  " * row.level if include_hierarchy_indent else ""
            t = f"{indent}{row.title}"
            s = row.synopsis.strip()
            return f"{t}\n{s}" if s else t

        elif col_id == StandardColumnId.TITLE.value:
            indent = "  " * row.level if include_hierarchy_indent else ""
            return f"{indent}{row.title}"

        elif col_id == StandardColumnId.SYNOPSIS.value:
            return row.synopsis

        elif col_id == StandardColumnId.INCLUDE_IN_COMPILE.value:
            return "Yes" if row.include_in_compile else "No"

        elif col_id == StandardColumnId.PROGRESS.value:
            return f"{row.progress_percent:.1f}%"

        elif col_id == StandardColumnId.KEYWORDS.value:
            return ", ".join(row.keywords)

        elif col_id == StandardColumnId.WORDS.value:
            return str(row.words)

        elif col_id == StandardColumnId.TOTAL_WORDS.value:
            return str(row.total_words)

        elif col_id == StandardColumnId.CHARACTERS.value:
            return str(row.characters)

        elif col_id == StandardColumnId.TOTAL_CHARACTERS.value:
            return str(row.total_characters)

        elif col_id == StandardColumnId.TARGET.value:
            return str(row.target)

        elif col_id == StandardColumnId.TOTAL_TARGET.value:
            return str(row.total_target)

        elif col_id == StandardColumnId.SECTION_TYPE.value:
            return row.section_type

        elif col_id == StandardColumnId.LABEL.value:
            return str(row.label_id)

        elif col_id == StandardColumnId.STATUS.value:
            return str(row.status_id)

        elif col_id == StandardColumnId.CREATED_DATE.value:
            return row.created_date

        elif col_id == StandardColumnId.MODIFIED_DATE.value:
            return row.modified_date

        elif col_id.startswith("custom:"):
            key = col_id.replace("custom:", "")
            return row.custom_metadata.get(key, "")

        return str(row.get_cell_value(col_id))
