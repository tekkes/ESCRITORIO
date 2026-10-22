"""
Diálogo Maestro de Compilación (Compile Dialog - Ctrl+Shift+E) para Escritorio / Scrivener 3.
Interfaz estructurada en 3 columnas independientes:
- Columna 1: Formatos predefinidos y personalizados con diseñador integrado.
- Columna 2: Mapeo y vista previa visual de Section Layouts.
- Columna 3: Pestañas de Contenidos (árbol, filtros, Front/Back Matter), Metadatos y Reemplazos.
"""

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from ...core.project import EscritorioProject
from ...compile.CompileEngine.models import CompileFormat
from ...compile.CompileEngine.engine import CompileEngine
from ...compile.exporters import ExportFormat
from .formats_column import FormatsColumn
from .section_layouts_column import SectionLayoutsColumn
from .contents_tab import ContentsTab
from .metadata_tab import MetadataTab
from .replacements_tab import ReplacementsTab


class RightPanelTab(Enum):
    CONTENTS = "contents"
    METADATA = "metadata"
    REPLACEMENTS = "replacements"


class CompileDialog:
    """Controlador principal de la ventana de Compilación de 3 Columnas."""

    SUPPORTED_TARGET_FORMATS = [
        "DOCX",
        "PDF",
        "EPUB",
        "RTF",
        "FDX",
        "MARKDOWN",
        "HTML",
        "TXT"
    ]

    def __init__(self, project: EscritorioProject):
        self.project: EscritorioProject = project
        self.is_open: bool = False

        # Columna 1: Formatos
        self.formats_column = FormatsColumn(on_format_changed=self._on_format_changed)

        # Columna 2: Diseños de Sección
        self.section_layouts_column = SectionLayoutsColumn(self.formats_column.current_format)

        # Columna 3: Pestañas de la derecha
        self.contents_tab = ContentsTab(project)
        self.metadata_tab = MetadataTab(project)
        self.replacements_tab = ReplacementsTab(self.formats_column.current_format)

        self.active_tab: RightPanelTab = RightPanelTab.CONTENTS
        self.selected_target_format: str = self.formats_column.current_format.target_format.upper()

    def _on_format_changed(self, new_format: CompileFormat):
        """Callback invocado cuando el usuario cambia el formato en la Columna 1."""
        self.section_layouts_column.update_format(new_format)
        self.replacements_tab.update_format(new_format)
        self.selected_target_format = new_format.target_format.upper()

    # =========================================================================
    # Ciclo de Vida (Ctrl+Shift+E)
    # =========================================================================

    def open(self):
        """Abre el diálogo de compilación."""
        self.is_open = True

    def close(self):
        """Cierra el diálogo."""
        self.is_open = False
        self.formats_column.close_designer()
        self.section_layouts_column.close_assign_modal()

    def toggle(self) -> bool:
        """Atajo Ctrl+Shift+E para alternar visibilidad."""
        if self.is_open:
            self.close()
        else:
            self.open()
        return self.is_open

    def switch_tab(self, tab: Union[RightPanelTab, str]):
        """Cambia la pestaña activa en la Columna 3."""
        if isinstance(tab, str):
            self.active_tab = RightPanelTab(tab.lower())
        else:
            self.active_tab = tab

    def set_target_format(self, target_format: str):
        """Modifica el formato de salida seleccionado en la barra inferior."""
        norm = target_format.upper().strip()
        if norm in self.SUPPORTED_TARGET_FORMATS:
            self.selected_target_format = norm
            self.formats_column.current_format.target_format = norm.lower()

    # =========================================================================
    # Ejecución de la Compilación
    # =========================================================================

    def compile(self, destination_path: Optional[Union[str, Path]] = None) -> Union[str, Path]:
        """
        Ejecuta la compilación con la configuración activa.
        Si se pasa una ruta de destino, exporta el archivo en disco.
        Si no, devuelve la cadena de texto compilada en memoria.
        """
        fmt = self.formats_column.current_format
        fmt.target_format = self.selected_target_format.lower()

        # Configurar motor maestro
        engine = CompileEngine(self.project, fmt)
        engine.metadata = self.metadata_tab.metadata
        engine.filter_config.included_uuids = set(self.contents_tab.included_uuids)
        engine.filter_config.filter_label_id = self.contents_tab.filter_label_id
        engine.filter_config.filter_status_id = self.contents_tab.filter_status_id
        engine.filter_config.include_front_matter = self.contents_tab.include_front_matter
        engine.filter_config.front_matter_uuid = self.contents_tab.front_matter_uuid
        engine.filter_config.include_back_matter = self.contents_tab.include_back_matter
        engine.filter_config.back_matter_uuid = self.contents_tab.back_matter_uuid
        engine.section_mappings = dict(self.section_layouts_column.section_mappings)

        if destination_path:
            return engine.compile_and_export(destination_path)
        else:
            return engine.assemble_manuscript()

    # =========================================================================
    # Estado Integral para Renderizado
    # =========================================================================

    def get_state(self) -> Dict[str, Any]:
        """Devuelve una instantánea completa del estado de la ventana para renderizado."""
        return {
            "is_open": self.is_open,
            "selected_target_format": self.selected_target_format,
            "active_tab": self.active_tab.value,
            "formats_column": {
                "selected_id": self.formats_column.selected_format_id,
                "current_name": self.formats_column.current_format.name,
                "formats": self.formats_column.get_formats_list(),
                "is_designer_open": self.formats_column.is_designer_open
            },
            "section_layouts_column": {
                "mappings": self.section_layouts_column.get_mapping_items(),
                "is_assign_modal_open": self.section_layouts_column.is_assign_modal_open,
                "available_layouts": self.section_layouts_column.get_available_layouts_list()
            },
            "contents_tab": {
                "tree": self.contents_tab.get_compilation_tree(),
                "selected_count": len(self.contents_tab.included_uuids),
                "include_front_matter": self.contents_tab.include_front_matter,
                "include_back_matter": self.contents_tab.include_back_matter
            },
            "metadata_tab": self.metadata_tab.get_data(),
            "replacements_tab": {
                "rules": self.replacements_tab.get_rules_list(),
                "strip_comments": self.replacements_tab.strip_comments,
                "strip_footnotes": self.replacements_tab.strip_footnotes,
                "footnotes_as_endnotes": self.replacements_tab.footnotes_as_endnotes
            }
        }
