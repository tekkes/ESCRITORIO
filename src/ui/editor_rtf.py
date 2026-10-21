"""
RTF Editor View para Escritorio
Editor de texto enriquecido principal compatible con EditorWidget.
Hereda todas las capacidades ergonómicas, formato, estilos, folios y foco.
"""

from typing import Optional, Callable
from ..core.project import BinderItem, EscritorioProject
from .EditorWidget import EditorWidget


class RTFEditorView(EditorWidget):
    """Controlador y lógica del editor de texto principal, retrocompatible con RTFEditorView."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        super().__init__(project)
