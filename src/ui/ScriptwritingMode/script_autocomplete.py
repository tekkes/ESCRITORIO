"""
Script Autocomplete para Escritorio
Motor de autocompletado inteligente contextual para guiones de cine, teatro y cómic.
Aprende nombres de personajes, locaciones y momentos directamente del manuscrito.
"""

from typing import List, Set, Dict, Optional
import re
from .script_elements import ScriptElementType, ScriptFormat


class ScriptAutocomplete:
    """Motor de sugerencias contextuales para guiones."""

    DEFAULT_PREFIXES = ["INT.", "EXT.", "INT./EXT.", "I/E."]
    DEFAULT_TIMES = ["DÍA", "NOCHE", "TARDE", "AMANECER", "CONTINUO", "MOMENTOS DESPUÉS", "DAY", "NIGHT", "CONTINUOUS"]
    DEFAULT_TRANSITIONS = ["CORTE A:", "FUNDIDO A NEGRO:", "DISOLVENCIA A:", "CORTE RÁPIDO A:", "FUNDIDO DE SALIDA.", "FADE OUT.", "FADE IN:"]
    DEFAULT_PARENTHETICALS = ["(susurrando)", "(pausa)", "(riendo)", "(al teléfono)", "(gritando)", "(con ironía)", "(beat)"]
    DEFAULT_SFX = ["¡BANG!", "¡CRASH!", "¡BOOM!", "¡WHAM!", "¡ZAP!", "¡CLIC!"]

    def __init__(self):
        self.characters: Set[str] = set()
        self.locations: Set[str] = set()

    def register_character(self, name: str):
        clean = name.strip().upper()
        if clean:
            self.characters.add(clean)

    def register_location(self, location: str):
        clean = location.strip().upper()
        if clean:
            self.locations.add(clean)

    def learn_from_text(self, text: str):
        """Analiza el texto existente para extraer automáticamente personajes y encabezados."""
        for line in text.splitlines():
            line_s = line.strip()
            if not line_s:
                continue

            # Encabezados de escena
            for pfx in self.DEFAULT_PREFIXES:
                if line_s.upper().startswith(pfx):
                    # Extraer locación: ej "INT. CAFETERIA - DIA" -> "CAFETERIA"
                    rem = line_s[len(pfx):].strip()
                    if "-" in rem:
                        loc = rem.split("-")[0].strip().upper()
                        self.register_location(loc)
                    else:
                        self.register_location(rem.upper())
                    break

            # Personajes (línea corta en mayúsculas, sin puntuación de fin de frase)
            if line_s.isupper() and 2 <= len(line_s) <= 30 and not line_s.endswith((".", ":", "!", "?")):
                # Si no es un prefijo de escena ni una transición
                if not any(line_s.startswith(pfx) for pfx in self.DEFAULT_PREFIXES):
                    if not line_s.endswith(":") and line_s not in self.DEFAULT_TIMES:
                        clean_char = re.sub(r"\(.*?\)", "", line_s).strip()
                        if clean_char:
                            self.register_character(clean_char)

    def get_suggestions(self, element: ScriptElementType, current_prefix: str = "") -> List[str]:
        """Obtiene una lista de autocompletado según el elemento dramático activo."""
        prefix_upper = current_prefix.upper().strip()

        if element == ScriptElementType.SCENE_HEADING:
            if not prefix_upper:
                return list(self.DEFAULT_PREFIXES)

            # Si ya empieza por un prefijo, sugerir locaciones
            for pfx in self.DEFAULT_PREFIXES:
                if prefix_upper.startswith(pfx):
                    after_pfx = prefix_upper[len(pfx):].strip()
                    if "-" in after_pfx:
                        # Sugerir momentos del día
                        after_dash = after_pfx.split("-")[-1].strip()
                        return [f"{current_prefix} - {t}" for t in self.DEFAULT_TIMES if t.startswith(after_dash)]
                    else:
                        # Sugerir locaciones
                        matching_locs = [loc for loc in self.locations if loc.startswith(after_pfx)]
                        if matching_locs:
                            return [f"{pfx} {loc}" for loc in matching_locs]
                        return [f"{pfx} {loc}" for loc in self.locations]

            return [pfx for pfx in self.DEFAULT_PREFIXES if pfx.startswith(prefix_upper)]

        elif element == ScriptElementType.CHARACTER:
            candidates = sorted(list(self.characters))
            if not prefix_upper:
                return candidates
            return [c for c in candidates if c.startswith(prefix_upper)]

        elif element == ScriptElementType.TRANSITION:
            if not prefix_upper:
                return list(self.DEFAULT_TRANSITIONS)
            return [t for t in self.DEFAULT_TRANSITIONS if t.startswith(prefix_upper)]

        elif element == ScriptElementType.PARENTHETICAL:
            if not prefix_upper:
                return list(self.DEFAULT_PARENTHETICALS)
            return [p for p in self.DEFAULT_PARENTHETICALS if p.upper().startswith(prefix_upper)]

        elif element == ScriptElementType.SFX:
            return list(self.DEFAULT_SFX)

        return []
