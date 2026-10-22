"""
Escritorio Tools Module
Herramientas avanzadas para el escritor:
- Project Targets (metas de manuscrito, sesión y calculadora de fecha límite / cuota diaria).
- Linguistic Focus (enfoque lingüístico por categorías gramaticales).
- Writing Statistics (métricas editoriales, páginas estimadas y tabla de frecuencia de palabras).
- Project Search & Replace (buscador global con soporte Regex y guardado como colección).
- Character Name Generator (generador con 8 culturas y filtros de inicial / aliteración).
- Scratchpad (bloc de notas flotante global con atajo Ctrl+Alt+Shift+S y envío al proyecto).
"""

from .project_targets import ProjectTargetsTracker
from .linguistic_focus import LinguisticFocus, FocusCategory
from .statistics import WritingStatistics, ALL_STOP_WORDS, SPANISH_STOP_WORDS, ENGLISH_STOP_WORDS
from .project_search import ProjectSearchEngine, SearchScope, SearchMatch
from .name_generator import CharacterNameGenerator, NAMES_DATABASE
from .scratchpad import ScratchpadManager, ScratchpadNote

__all__ = [
    "ProjectTargetsTracker",
    "LinguisticFocus",
    "FocusCategory",
    "WritingStatistics",
    "ALL_STOP_WORDS",
    "SPANISH_STOP_WORDS",
    "ENGLISH_STOP_WORDS",
    "ProjectSearchEngine",
    "SearchScope",
    "SearchMatch",
    "CharacterNameGenerator",
    "NAMES_DATABASE",
    "ScratchpadManager",
    "ScratchpadNote",
]
