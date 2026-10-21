"""
Escritorio Tools Module
Herramientas avanzadas para el escritor: Project Targets (metas), Linguistic Focus (enfoque lingüístico),
Estadísticas de legibilidad, Generador de nombres de personajes y Scratchpad flotante.
"""

from .project_targets import ProjectTargetsTracker
from .linguistic_focus import LinguisticFocus, FocusCategory
from .statistics import WritingStatistics
from .name_generator import CharacterNameGenerator
from .scratchpad import ScratchpadManager

__all__ = [
    "ProjectTargetsTracker",
    "LinguisticFocus",
    "FocusCategory",
    "WritingStatistics",
    "CharacterNameGenerator",
    "ScratchpadManager",
]
