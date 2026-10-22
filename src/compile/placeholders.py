"""
Placeholder Resolver para Escritorio
Sustitución de etiquetas dinámicas y comodines editoriales estándar de Scrivener 3:
<$projecttitle>, <$title>, <$author>, <$p> (numeración de páginas),
<$n>, <$r>, <$R>, <$t>, <$T>, <$w>, <$W>, <$hn>, <$wc>, <$date>, <$time>, <$rst_n>.
"""

from .CompileEngine.placeholders import (
    PlaceholderResolver,
    int_to_roman,
    int_to_words_es
)

__all__ = ["PlaceholderResolver", "int_to_roman", "int_to_words_es"]
