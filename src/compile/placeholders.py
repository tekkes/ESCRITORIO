"""
Placeholder Resolver para Escritorio
Sustitución de etiquetas dinámicas y comodines editoriales estándar de Scrivener 3:
<$projecttitle>, <$title>, <$author>, <$p> (numeración de páginas),
<$n> (numeradores secuenciales automáticos), <$wc> (recuento de palabras), <$date>.
"""

import re
import datetime
from typing import Dict, Any

class PlaceholderResolver:
    """Resuelve etiquetas dinámicas en el texto o encabezados durante la compilación."""

    def __init__(self, project_metadata: Dict[str, Any]):
        self.meta = project_metadata
        self.counters: Dict[str, int] = {"n": 0, "ch": 0, "sc": 0}

    def reset_counters(self):
        self.counters = {"n": 0, "ch": 0, "sc": 0}

    def resolve(self, text: str, item_title: str = "", current_page: int = 1) -> str:
        if not text:
            return ""

        result = text
        now = datetime.datetime.now()

        # Metadatos del proyecto
        result = result.replace("<$projecttitle>", self.meta.get("title", "Sin Título"))
        result = result.replace("<$author>", self.meta.get("author", "Autor"))
        result = result.replace("<$title>", item_title)
        result = result.replace("<$p>", str(current_page))
        result = result.replace("<$date>", now.strftime("%Y-%m-%d"))
        result = result.replace("<$time>", now.strftime("%H:%M"))

        # Contadores secuenciales
        def increment_counter(match):
            tag = match.group(1).lower()
            val = self.counters.get(tag, 0) + 1
            self.counters[tag] = val
            return str(val)

        result = re.sub(r"<\$(n|ch|sc)>", increment_counter, result)

        return result
