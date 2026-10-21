"""
Live Theme Studio para Escritorio
Estudio en tiempo real para personalizar colores, tipografía, texturas de fondo,
tamaño de iconos y densidad visual con vista previa instantánea y exportación
a paquetes compatibles .scrtheme y paquetes nativos .escrtheme.
"""

import io
import json
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List, Union
from .theme_engine import ThemeEngine, ThemeMode, UIDensityMode
from .theme_parser import ThemePackage, ScrThemeLoader, ThemeParser


class LiveThemeStudio:
    """
    Configurador y editor de temas visuales en tiempo real.
    Permite modificar tokens cromáticos, fuentes, texturas y densidad visual
    con propagación en caliente y exportación a .scrtheme (Scrivener 3) y .escrtheme.
    """

    # Texturas de fondo predefinidas para el corcho y paneles
    TEXTURE_PRESETS = {
        "plain": "none",
        "cork_grain": "radial-gradient(#b89778 15%, transparent 16%) 0 0, radial-gradient(#a07855 15%, transparent 16%) 8px 8px",
        "subtle_grid": "linear-gradient(to right, rgba(0,0,0,0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(0,0,0,0.05) 1px, transparent 1px)",
        "classic_parchment": "linear-gradient(135deg, rgba(230,218,190,0.2) 25%, transparent 25%)",
        "linen": "repeating-linear-gradient(45deg, rgba(0,0,0,0.02) 0px, rgba(0,0,0,0.02) 2px, transparent 2px, transparent 4px)"
    }

    def __init__(self, theme_engine: ThemeEngine):
        self.theme_engine = theme_engine
        self.working_palette: Dict[str, str] = dict(theme_engine.current_palette)
        self.working_density: UIDensityMode = theme_engine.density_mode
        self.working_typography: Dict[str, Any] = {
            "font_family_ui": "Segoe UI Variable Display",
            "font_family_editor": "Georgia",
            "font_size_ui": theme_engine.density_metrics.font_size_ui,
            "font_size_editor": 15,
            "font_size_small": theme_engine.density_metrics.font_size_small
        }
        self.working_texture: str = "plain"
        self.custom_metrics: Dict[str, int] = {
            "icon_size": theme_engine.density_metrics.icon_size,
            "toolbar_height": theme_engine.density_metrics.toolbar_height,
            "editor_header_height": theme_engine.density_metrics.editor_header_height,
            "badge_height": theme_engine.density_metrics.badge_height,
            "status_indicator_size": theme_engine.density_metrics.status_indicator_size
        }

        # Callbacks para vista previa reactiva
        self.on_preview_update: Optional[Callable[[Dict[str, Any]], None]] = None

    def update_color_token(self, token_name: str, hex_color: str):
        """Actualiza un color específico y notifica a la vista previa en vivo."""
        self.working_palette[token_name] = hex_color
        self._notify_preview()

    def update_typography(self, key: str, value: Any):
        """Modifica parámetros de tipografía (familia, tamaño)."""
        self.working_typography[key] = value
        self._notify_preview()

    def set_texture(self, texture_key: str):
        """Configura la textura de fondo para corcho/paneles."""
        if texture_key in self.TEXTURE_PRESETS:
            self.working_texture = texture_key
            self._notify_preview()

    def set_density(self, density_mode: UIDensityMode):
        """Ajusta la densidad visual y sincroniza métricas por defecto."""
        self.working_density = density_mode
        m = self.theme_engine.DENSITY_CONFIGS if hasattr(self.theme_engine, 'DENSITY_CONFIGS') else None
        if not m:
            from .theme_engine import DENSITY_CONFIGS
            m = DENSITY_CONFIGS
        metrics = m[density_mode]
        self.custom_metrics["icon_size"] = metrics.icon_size
        self.custom_metrics["toolbar_height"] = metrics.toolbar_height
        self.custom_metrics["editor_header_height"] = metrics.editor_header_height
        self.custom_metrics["badge_height"] = metrics.badge_height
        self.custom_metrics["status_indicator_size"] = metrics.status_indicator_size
        self.working_typography["font_size_ui"] = metrics.font_size_ui
        self.working_typography["font_size_small"] = metrics.font_size_small
        self._notify_preview()

    def set_custom_metric(self, key: str, value: int):
        """Ajusta una dimensión específica de control UI (altura de barra, cabecera, icono)."""
        self.custom_metrics[key] = value
        self._notify_preview()

    def _notify_preview(self):
        if self.on_preview_update:
            try:
                self.on_preview_update(self.get_preview_state())
            except Exception:
                pass

    def get_preview_state(self) -> Dict[str, Any]:
        """Devuelve el estado completo actual para renderizado instantáneo."""
        return {
            "palette": dict(self.working_palette),
            "density": self.working_density.value,
            "metrics": dict(self.custom_metrics),
            "typography": dict(self.working_typography),
            "texture": self.working_texture,
            "texture_css": self.TEXTURE_PRESETS.get(self.working_texture, "none")
        }

    def reset_to_current(self):
        """Restaura los valores al tema actualmente activo en el motor."""
        self.working_palette = dict(self.theme_engine.current_palette)
        self.working_density = self.theme_engine.density_mode
        m = self.theme_engine.density_metrics
        self.custom_metrics = {
            "icon_size": m.icon_size,
            "toolbar_height": m.toolbar_height,
            "editor_header_height": m.editor_header_height,
            "badge_height": m.badge_height,
            "status_indicator_size": m.status_indicator_size
        }
        self._notify_preview()

    def commit_changes(self):
        """Aplica definitivamente la configuración editada al ThemeEngine activo."""
        self.theme_engine.current_palette.update(self.working_palette)
        self.theme_engine.set_density_mode(self.working_density)
        # Inyectar métricas personalizadas si difieren
        for k, v in self.custom_metrics.items():
            if hasattr(self.theme_engine.density_metrics, k):
                setattr(self.theme_engine.density_metrics, k, v)
        self.theme_engine._notify_listeners()

    def export_as_escrtheme(self, name: str, author: str = "Escritorio User", file_path: Optional[Union[str, Path]] = None) -> str:
        """Serializa y opcionalmente guarda el tema en formato nativo .escrtheme (JSON)."""
        pkg = ThemePackage(
            name=name,
            author=author,
            version="1.0.0",
            base_theme="Custom",
            target_platform="Windows",
            palette=dict(self.working_palette),
            preferences={
                "density": self.working_density.value,
                "metrics": dict(self.custom_metrics),
                "typography": dict(self.working_typography),
                "texture": self.working_texture
            },
            qss_stylesheet=self.theme_engine.generate_qss()
        )
        if file_path:
            return ThemeParser.save_escrtheme(pkg, file_path)
        else:
            return json.dumps({
                "name": pkg.name,
                "author": pkg.author,
                "version": pkg.version,
                "base_theme": pkg.base_theme,
                "target_platform": pkg.target_platform,
                "palette": pkg.palette,
                "preferences": pkg.preferences,
                "stylesheet": pkg.qss_stylesheet
            }, indent=4, ensure_ascii=False)

    def export_as_scrtheme(self, name: str, author: str = "Scrivener User", file_path: Optional[Union[str, Path]] = None) -> bytes:
        """
        Exporta y opcionalmente guarda un paquete .scrtheme (contenedor ZIP válido para Scrivener 3)
        con manifest.xml, palette.pal, preferences.prefs y stylesheet.qss.
        """
        pkg = ThemePackage(
            name=name,
            author=author,
            version="1.0.0",
            base_theme="Dark" if "dark" in name.lower() else "Light",
            target_platform="Windows",
            palette=dict(self.working_palette),
            preferences={
                "Editor.DefaultFont": self.working_typography.get("font_family_editor", "Georgia"),
                "Editor.FontSize": self.working_typography.get("font_size_editor", 15),
                "Corkboard.CardWidth": 180,
                "Corkboard.CardHeight": 120,
                "UI.Density": self.working_density.value,
                "UI.ToolbarHeight": self.custom_metrics.get("toolbar_height", 28),
                "UI.Texture": self.working_texture
            },
            qss_stylesheet=self.theme_engine.generate_qss()
        )
        return ScrThemeLoader.export_to_scrtheme(pkg, file_path)

    @staticmethod
    def get_editable_token_groups() -> Dict[str, List[Dict[str, str]]]:
        """
        Devuelve el catálogo estructurado de tokens editables para renderizar
        los controles de la ventana Live Theme Studio por pestañas / secciones.
        """
        return {
            "Ventana y Barras": [
                {"token": "window.background", "label": "Fondo de Ventana"},
                {"token": "window.foreground", "label": "Texto Principal"},
                {"token": "toolbar.background", "label": "Fondo Barra de Herramientas"},
                {"token": "toolbar.foreground", "label": "Texto Barra de Herramientas"},
                {"token": "statusbar.background", "label": "Fondo Barra de Estado"},
                {"token": "statusbar.foreground", "label": "Texto Barra de Estado"}
            ],
            "Binder / Cuaderno": [
                {"token": "binder.background", "label": "Fondo del Binder"},
                {"token": "binder.foreground", "label": "Texto de Documentos"},
                {"token": "binder.secondary_text", "label": "Texto Secundario"},
                {"token": "binder.selected_bg", "label": "Fondo de Selección"},
                {"token": "binder.selected_fg", "label": "Texto de Selección"}
            ],
            "Editor de Manuscrito": [
                {"token": "editor.background", "label": "Fondo del Papel"},
                {"token": "editor.foreground", "label": "Tinta del Texto"},
                {"token": "editor.caret", "label": "Cursor de Inserción"},
                {"token": "editor.selection", "label": "Resaltado de Selección"},
                {"token": "editor.header_bg", "label": "Cabecera del Editor"},
                {"token": "editor.header_fg", "label": "Texto de Cabecera"}
            ],
            "Pizarra de Corcho": [
                {"token": "corkboard.background", "label": "Fondo del Corcho"},
                {"token": "corkboard.card_bg", "label": "Fondo de Tarjeta"},
                {"token": "corkboard.card_fg", "label": "Texto de Tarjeta"},
                {"token": "corkboard.card_border", "label": "Borde de Tarjeta"},
                {"token": "corkboard.pin_color", "label": "Color del Alfiler"}
            ],
            "Esquematizador": [
                {"token": "outliner.background", "label": "Fondo de la Tabla"},
                {"token": "outliner.foreground", "label": "Texto de Filas"},
                {"token": "outliner.row_alternate", "label": "Fila Alterna"},
                {"token": "outliner.grid", "label": "Líneas de Cuadrícula"}
            ],
            "Inspector y Micro-Badges": [
                {"token": "inspector.background", "label": "Fondo del Inspector"},
                {"token": "inspector.foreground", "label": "Texto del Inspector"},
                {"token": "accent.primary", "label": "Acento Primario"},
                {"token": "badge.label_bg", "label": "Fondo de Micro-Etiqueta"},
                {"token": "badge.label_fg", "label": "Texto de Micro-Etiqueta"}
            ]
        }
