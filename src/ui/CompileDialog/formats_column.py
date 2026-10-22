"""
Columna 1: Formatos de Compilación (Formats Column) para Escritorio / Scrivener 3.
Lista de formatos integrados y personalizados del proyecto, con soporte
para selección, duplicación y apertura del diseñador con doble clic.
"""

from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from ...compile.CompileEngine.models import CompileFormat, create_builtin_formats
from ...compile.CompileEngine.format_designer import CompileFormatDesigner


class FormatCategory(Enum):
    PROJECT = "project"
    BUILTIN = "builtin"


class FormatsColumn:
    """Controlador de la Columna 1 del Diálogo de Compilación."""

    def __init__(self, on_format_changed: Optional[Callable[[CompileFormat], None]] = None):
        self.builtin_formats: Dict[str, CompileFormat] = create_builtin_formats()
        self.project_formats: Dict[str, CompileFormat] = {}
        self.selected_format_id: str = "manuscript_standard"
        self.on_format_changed = on_format_changed
        self.is_designer_open: bool = False
        self.designer_instance: Optional[CompileFormatDesigner] = None

    @property
    def current_format(self) -> CompileFormat:
        if self.selected_format_id in self.project_formats:
            return self.project_formats[self.selected_format_id]
        return self.builtin_formats.get(self.selected_format_id, self.builtin_formats["manuscript_standard"])

    def select_format(self, format_id: str) -> bool:
        """Selecciona un formato por su ID."""
        if format_id in self.project_formats or format_id in self.builtin_formats:
            self.selected_format_id = format_id
            if self.on_format_changed:
                self.on_format_changed(self.current_format)
            return True
        return False

    def duplicate_current_format(self, new_name: Optional[str] = None) -> CompileFormat:
        """Duplica el formato seleccionado como formato personalizado del proyecto."""
        source = self.current_format
        designer = CompileFormatDesigner.duplicate_format(source, new_name=new_name, is_project=True)
        duplicated = designer.current_format
        self.project_formats[duplicated.id] = duplicated
        self.selected_format_id = duplicated.id
        if self.on_format_changed:
            self.on_format_changed(duplicated)
        return duplicated

    def open_format_designer(self, format_id: Optional[str] = None) -> CompileFormatDesigner:
        """Abre el Diseñador Completo de Formatos (doble clic o botón Editar)."""
        target_id = format_id or self.selected_format_id
        fmt = self.project_formats.get(target_id) or self.builtin_formats.get(target_id)
        if not fmt:
            fmt = self.current_format

        # Si es un formato integrado, se duplica automáticamente para editarlo
        if fmt.is_builtin:
            designer = CompileFormatDesigner.duplicate_format(fmt, is_project=True)
            self.project_formats[designer.current_format.id] = designer.current_format
            self.selected_format_id = designer.current_format.id
        else:
            designer = CompileFormatDesigner(fmt)

        self.designer_instance = designer
        self.is_designer_open = True
        return designer

    def save_designer_changes(self) -> Optional[CompileFormat]:
        """Aplica y guarda los cambios realizados en el diseñador."""
        if self.designer_instance:
            updated = self.designer_instance.current_format
            self.project_formats[updated.id] = updated
            self.selected_format_id = updated.id
            self.is_designer_open = False
            if self.on_format_changed:
                self.on_format_changed(updated)
            return updated
        return None

    def close_designer(self):
        self.is_designer_open = False
        self.designer_instance = None

    def delete_project_format(self, format_id: str) -> bool:
        """Elimina un formato personalizado del proyecto."""
        if format_id in self.project_formats:
            del self.project_formats[format_id]
            if self.selected_format_id == format_id:
                self.selected_format_id = "manuscript_standard"
                if self.on_format_changed:
                    self.on_format_changed(self.current_format)
            return True
        return False

    def get_formats_list(self) -> List[Dict[str, Any]]:
        """Devuelve la lista estructurada de formatos clasificados para la interfaz."""
        items = []

        # 1. Formatos del Proyecto
        for fmt in self.project_formats.values():
            items.append({
                "id": fmt.id,
                "name": fmt.name,
                "description": fmt.description,
                "category": FormatCategory.PROJECT.value,
                "category_label": "Formatos del Proyecto",
                "target_format": fmt.target_format.upper(),
                "is_builtin": False,
                "is_selected": (fmt.id == self.selected_format_id)
            })

        # 2. Formatos Integrados
        for fmt in self.builtin_formats.values():
            items.append({
                "id": fmt.id,
                "name": fmt.name,
                "description": fmt.description,
                "category": FormatCategory.BUILTIN.value,
                "category_label": "Formatos Integrados",
                "target_format": fmt.target_format.upper(),
                "is_builtin": True,
                "is_selected": (fmt.id == self.selected_format_id)
            })

        return items
