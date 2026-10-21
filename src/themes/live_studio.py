"""
Live Theme Studio para Escritorio
Estudio en tiempo real para modificar colores, tipografía y márgenes visuales,
con vista previa instantánea y exportación a paquetes .scrtheme y .escrtheme.
"""

import json
from typing import Dict, Callable, Optional
from .theme_engine import ThemeEngine
from .theme_parser import ThemePackage

class LiveThemeStudio:
    """Controlador del editor de temas en vivo."""

    def __init__(self, theme_engine: ThemeEngine):
        self.theme_engine = theme_engine
        self.working_palette: Dict[str, str] = dict(theme_engine.current_palette)
        self.on_preview_update: Optional[Callable[[Dict[str, str]], None]] = None

    def update_token(self, token_name: str, hex_color: str):
        """Actualiza un color y notifica a la interfaz para refresco en caliente."""
        self.working_palette[token_name] = hex_color
        if self.on_preview_update:
            self.on_preview_update(self.working_palette)

    def commit_changes(self):
        """Aplica definitivamente los cambios al motor de temas activo."""
        self.theme_engine.current_palette.update(self.working_palette)

    def export_as_escrtheme_json(self, name: str, author: str = "Autor") -> str:
        """Serializa la paleta en formato JSON nativo .escrtheme."""
        package = {
            "name": name,
            "author": author,
            "version": "1.0.0",
            "base_theme": "Custom",
            "palette": self.working_palette,
            "stylesheet": self.theme_engine.generate_qss()
        }
        return json.dumps(package, indent=4)
