"""
Linguistic Focus para Escritorio
Modo de enfoque lingüístico que atenúa el texto general y resalta elementos clave:
Diálogos (entre comillas o rayas de diálogo —), adverbios, verbos o sustantivos.
"""

import re
from enum import Enum
from typing import List, Tuple

class FocusCategory(Enum):
    ALL = "all"
    DIALOGUE = "dialogue"
    ADVERBS = "adverbs"

class LinguisticFocus:
    """Procesador para enfoque estilístico del texto."""

    # Regex para diálogos en español e inglés: rayas («...», "...", — ... —)
    DIALOGUE_REGEX = re.compile(r'(«[^»]+»|"[^"]+"|[—–][^—–\n]+[—–]?)')
    ADVERB_ES_REGEX = re.compile(r'\b\w+mente\b', re.IGNORECASE)

    @classmethod
    def extract_dialogue_ranges(cls, text: str) -> List[Tuple[int, int]]:
        """Devuelve los rangos (inicio, fin) correspondientes a líneas de diálogo."""
        ranges = []
        for match in cls.DIALOGUE_REGEX.finditer(text):
            ranges.append((match.start(), match.end()))
        return ranges

    @classmethod
    def extract_adverb_ranges(cls, text: str) -> List[Tuple[int, int]]:
        """Devuelve los rangos de adverbios (terminados en -mente)."""
        ranges = []
        for match in cls.ADVERB_ES_REGEX.finditer(text):
            ranges.append((match.start(), match.end()))
        return ranges
