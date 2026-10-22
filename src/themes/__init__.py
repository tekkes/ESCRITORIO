"""
Escritorio Themes Module
Motor dinámico de temas, soporte de paquetes .scrtheme y .escrtheme,
7 modos visuales predefinidos, control de densidad UI (Ultra-compacto/Compacto)
y Live Theme Studio.
"""

from .theme_parser import (
    ThemeParser,
    ThemePackage,
    ScrThemeLoader,
    SCRIVENER_TO_ESCRITORIO_TOKENS,
    ESCRITORIO_TO_SCRIVENER_TOKENS
)
from .theme_engine import (
    ThemeEngine,
    ThemeMode,
    UIDensityMode,
    DensityMetrics,
    DENSITY_CONFIGS,
    BUILTIN_PALETTES
)
from .live_studio import LiveThemeStudio

__all__ = [
    "ThemeParser",
    "ThemePackage",
    "ScrThemeLoader",
    "SCRIVENER_TO_ESCRITORIO_TOKENS",
    "ESCRITORIO_TO_SCRIVENER_TOKENS",
    "ThemeEngine",
    "ThemeMode",
    "UIDensityMode",
    "DensityMetrics",
    "DENSITY_CONFIGS",
    "BUILTIN_PALETTES",
    "LiveThemeStudio",
]
