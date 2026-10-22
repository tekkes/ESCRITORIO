"""
OutlinerWidget para Escritorio
Componente principal del Esquematizador jerárquico tipo hoja de cálculo (Ctrl+3)
con paridad funcional total respecto a Scrivener 3:
1. Árbol tabular multinivel con soporte de celda combinada 'Title & Synopsis' o separada
2. Selector compacto de columnas visibles (estándar y Custom Metadata)
3. Métricas de palabras, caracteres, objetivos y barras de progreso con gradiente
4. Ordenación multi-criterio en cabeceras (Asc, Desc, Orden del Binder)
5. Filtrado rápido de texto con preservación de jerarquía
6. Exportación directa a archivo .csv
"""

from typing import List, Dict, Optional, Any, Callable, Union
from pathlib import Path

from ...core.project import BinderItem, EscritorioProject
from .outliner_columns import ColumnSelector, OutlinerColumn, StandardColumnId, ColumnType
from .outliner_row import OutlinerRow
from .outliner_exporter import OutlinerExporter


class OutlinerWidget:
    """Controlador y orquestador maestro del Esquematizador."""

    def __init__(self, project: Optional[EscritorioProject] = None, combined_title_synopsis: bool = True):
        self.project: Optional[EscritorioProject] = project
        self.parent_item: Optional[BinderItem] = None
        self.root_rows: List[OutlinerRow] = []

        # Selector de columnas
        self.column_selector = ColumnSelector(combined_title_synopsis=combined_title_synopsis)

        # Estado de ordenación: (col_id, ascending) o None (orden original del Binder)
        self.sort_column: Optional[str] = None
        self.sort_ascending: bool = True

        # Filtro de búsqueda rápida
        self.filter_text: str = ""

        # Callbacks
        self.on_selection_requested: Optional[Callable[[str], None]] = None
        self.on_data_modified: Optional[Callable[[], None]] = None

    @property
    def combined_title_synopsis(self) -> bool:
        return self.column_selector.combined_title_synopsis

    @combined_title_synopsis.setter
    def combined_title_synopsis(self, val: bool):
        self.column_selector.set_combined_title_synopsis(val)

    # =========================================================================
    # Carga de Contenedores y Construcción del Árbol Multinivel
    # =========================================================================

    def load_container(self, item: BinderItem, recursive: bool = True):
        """Carga el contenedor dado y construye la jerarquía de filas del esquema."""
        self.parent_item = item
        if not self.project and getattr(item, "project", None):
            self.project = item.project

        self.root_rows.clear()
        children = getattr(item, "children", []) or []

        for child in children:
            row = self._build_row_recursive(child, level=0, recursive=recursive)
            self.root_rows.append(row)

        # Descubrir y registrar columnas de metadatos personalizados si existen
        self._discover_custom_metadata()

    def _build_row_recursive(self, item: BinderItem, level: int, recursive: bool) -> OutlinerRow:
        row = OutlinerRow(item, level=level, project=self.project)
        if recursive:
            children = getattr(item, "children", []) or []
            for child in children:
                child_row = self._build_row_recursive(child, level=level + 1, recursive=True)
                row.children.append(child_row)
        return row

    def _discover_custom_metadata(self):
        """Detecta las claves de Custom Metadata presentes en los elementos y añade sus columnas."""
        discovered_keys = set()

        def scan(row: OutlinerRow):
            for k in row.custom_metadata.keys():
                if not k.startswith("_"):
                    discovered_keys.add(k)
            for c in row.children:
                scan(c)

        for r in self.root_rows:
            scan(r)

        for key in sorted(discovered_keys):
            col_id = f"custom:{key}"
            if col_id not in self.column_selector.columns:
                self.column_selector.add_custom_metadata_column(key)

    # =========================================================================
    # Aplanado de Filas (Flattening) con Filtro y Expansión
    # =========================================================================

    def get_flattened_rows(self) -> List[OutlinerRow]:
        """
        Retorna la lista secuencial de filas aplanadas visibles,
        respetando el estado de expansión de nodos, ordenación y filtrado.
        """
        # 1. Copiar y ordenar jerárquicamente las filas
        ordered_roots = self._sort_rows_hierarchical(self.root_rows)

        # 2. Filtrar si hay texto de búsqueda
        if self.filter_text.strip():
            ordered_roots = self._filter_rows_hierarchical(ordered_roots, self.filter_text.strip())

        # 3. Aplanar respetando nodos colapsados
        flattened: List[OutlinerRow] = []
        for root in ordered_roots:
            self._flatten_recursive(root, flattened)

        return flattened

    def _flatten_recursive(self, row: OutlinerRow, result: List[OutlinerRow]):
        result.append(row)
        if row.expanded and row.children:
            for child in row.children:
                self._flatten_recursive(child, result)

    # =========================================================================
    # Ordenación Multi-criterio (Asc, Desc, Restaurar Orden del Binder)
    # =========================================================================

    def click_header_sort(self, col_id: str) -> Optional[bool]:
        """
        Cicla el criterio de ordenación al hacer clic en un encabezado de columna:
        - Si no estaba seleccionada: ordena Ascendente (True)
        - Si estaba Ascendente: pasa a Descendente (False)
        - Si estaba Descendente: restaura el orden del Binder (None)
        """
        if self.sort_column != col_id:
            self.sort_column = col_id
            self.sort_ascending = True
            return True
        else:
            if self.sort_ascending:
                self.sort_ascending = False
                return False
            else:
                self.sort_column = None
                self.sort_ascending = True
                return None

    def _sort_rows_hierarchical(self, rows: List[OutlinerRow]) -> List[OutlinerRow]:
        """Ordena las filas dentro de cada nivel conservando la jerarquía arbórea."""
        if not self.sort_column:
            # Restaurar orden original de Binder
            result = []
            for r in rows:
                sorted_r = OutlinerRow(r.item, level=r.level, project=self.project)
                sorted_r.expanded = r.expanded
                sorted_r.children = self._sort_rows_hierarchical(r.children)
                result.append(sorted_r)
            return result

        col_id = self.sort_column
        reverse = not self.sort_ascending

        def key_func(row: OutlinerRow):
            val = row.get_cell_value(col_id)
            if isinstance(val, dict):
                # Para Title & Synopsis o Progress
                return val.get("title", "") or val.get("percent", 0.0)
            if isinstance(val, (int, float)):
                return val
            return str(val).lower()

        sorted_rows = sorted(rows, key=key_func, reverse=reverse)
        result = []
        for r in sorted_rows:
            sorted_r = OutlinerRow(r.item, level=r.level, project=self.project)
            sorted_r.expanded = r.expanded
            sorted_r.children = self._sort_rows_hierarchical(r.children)
            result.append(sorted_r)
        return result

    # =========================================================================
    # Filtrado Rápido por Texto
    # =========================================================================

    def set_filter_text(self, text: str):
        self.filter_text = text.strip()

    def _filter_rows_hierarchical(self, rows: List[OutlinerRow], query: str) -> List[OutlinerRow]:
        """Conserva los nodos que coinciden o aquellos cuyos descendientes coinciden."""
        matching_rows = []
        for r in rows:
            # Filtrar hijos primero
            filtered_children = self._filter_rows_hierarchical(r.children, query)
            self_matches = r.matches_query(query)

            if self_matches or filtered_children:
                copied_row = OutlinerRow(r.item, level=r.level, project=self.project)
                copied_row.expanded = True  # Auto-expandir cuando hay coincidencia en hijos
                copied_row.children = filtered_children
                matching_rows.append(copied_row)

        return matching_rows

    # =========================================================================
    # Expansión y Contracción de Nodos
    # =========================================================================

    def toggle_expand(self, uuid: str) -> bool:
        row = self.find_row_by_uuid(uuid)
        if row and row.children:
            row.expanded = not row.expanded
            return row.expanded
        return False

    def expand_all(self):
        def _expand(row: OutlinerRow):
            row.expanded = True
            for c in row.children:
                _expand(c)
        for r in self.root_rows:
            _expand(r)

    def collapse_all(self):
        def _collapse(row: OutlinerRow):
            row.expanded = False
            for c in row.children:
                _collapse(c)
        for r in self.root_rows:
            _collapse(r)

    def find_row_by_uuid(self, uuid: str) -> Optional[OutlinerRow]:
        def _find(row: OutlinerRow) -> Optional[OutlinerRow]:
            if row.uuid == uuid:
                return row
            for c in row.children:
                res = _find(c)
                if res:
                    return res
            return None

        for r in self.root_rows:
            found = _find(r)
            if found:
                return found
        return None

    # =========================================================================
    # Edición In-Situ
    # =========================================================================

    def update_cell(self, uuid: str, col_id: str, new_value: Any) -> bool:
        """Modifica in-situ el valor de una celda y sincroniza con el proyecto."""
        row = self.find_row_by_uuid(uuid)
        if not row:
            return False

        if col_id in (StandardColumnId.TITLE.value, StandardColumnId.TITLE_AND_SYNOPSIS.value):
            if isinstance(new_value, dict):
                row.set_title(new_value.get("title", row.title))
                if "synopsis" in new_value:
                    row.set_synopsis(new_value["synopsis"])
            else:
                row.set_title(str(new_value))
        elif col_id == StandardColumnId.SYNOPSIS.value:
            row.set_synopsis(str(new_value))
        elif col_id == StandardColumnId.TARGET.value:
            row.set_target(int(new_value))
        elif col_id == StandardColumnId.LABEL.value:
            row.set_label(int(new_value))
        elif col_id == StandardColumnId.STATUS.value:
            row.set_status(int(new_value))
        elif col_id == StandardColumnId.SECTION_TYPE.value:
            row.set_section_type(str(new_value))
        elif col_id == StandardColumnId.INCLUDE_IN_COMPILE.value:
            row.set_include_in_compile(bool(new_value))
        elif col_id.startswith("custom:"):
            row.set_custom_metadata(col_id, str(new_value))
        else:
            row.set_custom_metadata(col_id, str(new_value))

        row.invalidate_metrics()

        # Guardar cambios estructurales si el proyecto está disponible
        if self.project:
            self.project.save_structure()

        if self.on_data_modified:
            self.on_data_modified()

        return True

    # =========================================================================
    # Exportación a Archivo .csv
    # =========================================================================

    def export_csv(self, output_file_or_path: Optional[Union[str, Path]] = None, only_visible_columns: bool = True) -> str:
        """Exporta la vista actual del Esquema a formato .csv."""
        rows = self.get_flattened_rows()
        cols = self.column_selector.get_visible_columns() if only_visible_columns else self.column_selector.get_all_columns()
        return OutlinerExporter.export_to_csv(rows, cols, output_file_or_path=output_file_or_path)

    # =========================================================================
    # Telemetría y Geometría para UI
    # =========================================================================

    def get_view_data(self) -> Dict[str, Any]:
        """Genera el árbol estructurado de datos de renderizado."""
        flat_rows = self.get_flattened_rows()
        visible_cols = self.column_selector.get_visible_columns()

        return {
            "parent_uuid": self.parent_item.uuid if self.parent_item else "",
            "parent_title": self.parent_item.title if self.parent_item else "Esquema",
            "sort": {
                "column": self.sort_column,
                "ascending": self.sort_ascending
            },
            "filter": self.filter_text,
            "columns": [c.to_dict() for c in visible_cols],
            "total_rows": len(flat_rows),
            "rows": [
                {
                    "uuid": r.uuid,
                    "level": r.level,
                    "expanded": r.expanded,
                    "is_folder": r.is_folder,
                    "cells": {c.col_id: r.get_cell_value(c.col_id) for c in visible_cols}
                }
                for r in flat_rows
            ]
        }
