"""
Pestaña de Metadatos (Metadata Tab) de la Columna 3 para Escritorio / Scrivener 3.
Gestión de metadatos editoriales del libro para exportación:
Título, Subtítulo, Autor, Editor, ISBN, Sello/Editorial, Copyright, Idioma y Portada.
"""

from typing import Dict, Any, Optional
from ...core.project import EscritorioProject
from ...compile.CompileEngine.models import BookMetadata


class MetadataTab:
    """Controlador de la pestaña de Metadatos del Libro."""

    def __init__(self, project: EscritorioProject):
        self.project: EscritorioProject = project
        self.metadata = BookMetadata(
            title=project.project_data.get("title", "Manuscrito"),
            author=project.project_data.get("author", "Autor")
        )

    def update_field(self, field_name: str, value: Any):
        """Actualiza un campo específico de metadatos."""
        if hasattr(self.metadata, field_name):
            setattr(self.metadata, field_name, value)

    def get_data(self) -> Dict[str, Any]:
        """Devuelve los metadatos en formato de diccionario para la UI."""
        return {
            "title": self.metadata.title,
            "subtitle": self.metadata.subtitle,
            "author": self.metadata.author,
            "editor": self.metadata.editor,
            "isbn": self.metadata.isbn,
            "publisher": self.metadata.publisher,
            "copyright_notice": self.metadata.copyright_notice,
            "language": self.metadata.language,
            "cover_image_path": self.metadata.cover_image_path
        }
