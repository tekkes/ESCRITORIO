"""
Main Window para Escritorio
Ventana principal y orquestador maestro de la interfaz: barra de menú, barra de herramientas,
alternancia entre vistas (Editor, Corcho, Esquematizador), paneles acoplables, motor de temas,
control de densidad UI (Ultra-compacto) y Live Theme Studio.
"""

from enum import Enum
from typing import Optional, Dict, Any, List, Union

from ..core.project import EscritorioProject, BinderItem
from ..themes.theme_engine import ThemeEngine, ThemeMode, UIDensityMode
from ..themes.live_studio import LiveThemeStudio
from .binder import BinderView
from .editor_rtf import RTFEditorView
from .split_view import SplitContainer, SplitOrientation
from .corkboard import CorkboardView
from .outliner import OutlinerView
from .inspector import InspectorView
from .composition_mode import CompositionMode

class CentralViewMode(Enum):
    EDITOR = "editor"
    CORKBOARD = "corkboard"
    OUTLINER = "outliner"

class MainWindow:
    """Ventana principal de la aplicación Escritorio."""

    def __init__(
        self,
        project: Optional[EscritorioProject] = None,
        theme_mode: ThemeMode = ThemeMode.MINIMALIST_DEFAULT,
        density_mode: UIDensityMode = UIDensityMode.ULTRA_COMPACT
    ):
        self.project = project
        self.theme_engine = ThemeEngine(initial_mode=theme_mode, initial_density=density_mode)
        self.live_studio = LiveThemeStudio(self.theme_engine)

        self.binder = BinderView(project)
        self.split_container = SplitContainer()
        self.corkboard = CorkboardView()
        self.outliner = OutlinerView()
        self.inspector = InspectorView()
        self.composition_mode = CompositionMode(self.split_container.primary_editor)

        self.current_view_mode = CentralViewMode.EDITOR
        self.inspector_visible: bool = True
        self.binder_visible: bool = True
        self.last_theme_switch_latency_ms: float = 0.0

        # Conectar selección del binder con las vistas
        self.binder.on_selection_changed = self._on_binder_selection_changed

        if project:
            self.load_project(project)

    def load_project(self, project: EscritorioProject):
        self.project = project
        self.binder.set_project(project)
        if self.binder.selected_uuid:
            self._on_binder_selection_changed(self.binder.selected_uuid)

    def _on_binder_selection_changed(self, uuid: str):
        if not self.project:
            return
        item = self.project.get_item(uuid)
        if not item:
            return

        # Actualizar editor primario
        self.split_container.primary_editor.load_item(item)
        # Actualizar inspector
        self.inspector.set_item(item)

        # Si el elemento tiene hijos o es contenedor, actualizar corcho y esquematizador
        if item.children:
            self.corkboard.load_container(item)
            self.outliner.load_container(item)

    def set_view_mode(self, mode: CentralViewMode):
        self.current_view_mode = mode

    def toggle_binder(self):
        self.binder_visible = not self.binder_visible

    def toggle_inspector(self):
        self.inspector_visible = not self.inspector_visible

    def toggle_composition_mode(self):
        self.composition_mode.toggle()

    def set_theme(self, mode: Union[ThemeMode, str]) -> float:
        """
        Cambia el modo visual instantáneamente (<50ms).
        Acepta una instancia de ThemeMode o el nombre en string.
        """
        if isinstance(mode, str):
            try:
                mode_enum = ThemeMode(mode.lower())
            except ValueError:
                # Buscar por nombre del enum
                mode_enum = getattr(ThemeMode, mode.upper(), ThemeMode.MINIMALIST_DEFAULT)
        else:
            mode_enum = mode

        elapsed = self.theme_engine.set_builtin_mode(mode_enum)
        self.last_theme_switch_latency_ms = elapsed
        return elapsed

    def set_ui_density(self, density: Union[UIDensityMode, str]):
        """Ajusta la densidad visual de los controles e iconos."""
        if isinstance(density, str):
            density_enum = UIDensityMode(density.lower())
        else:
            density_enum = density
        self.theme_engine.set_density_mode(density_enum)

    def get_available_themes(self) -> List[Dict[str, str]]:
        """Lista los 7 modos visuales predefinidos para selectores de interfaz y menús."""
        return [
            {"id": ThemeMode.MINIMALIST_DEFAULT.value, "name": "Modo Minimalista (Por Defecto)", "base": "Light"},
            {"id": ThemeMode.CARBON_DARK.value, "name": "Modo Oscuro (Carbon Dark)", "base": "Dark"},
            {"id": ThemeMode.SOLARIZED_DARK.value, "name": "Modo Solarizado Oscuro (Solarized Dark)", "base": "Dark"},
            {"id": ThemeMode.SOLARIZED_LIGHT.value, "name": "Modo Solarizado Claro (Solarized Light)", "base": "Light"},
            {"id": ThemeMode.SEPIA_PARCHMENT.value, "name": "Modo Sepia (Classic Parchment)", "base": "Sepia"},
            {"id": ThemeMode.NORDIC_FROST.value, "name": "Modo Nord (Nordic Frost)", "base": "Dark"},
            {"id": ThemeMode.CATPPUCCIN_MOCHA.value, "name": "Modo Catppuccin Mocha", "base": "Dark"}
        ]

    def get_status_info(self) -> Dict[str, Any]:
        """Obtiene la telemetría de la barra de estado inferior."""
        active_editor = self.split_container.get_active_editor()
        words = active_editor.get_word_count()
        chars = active_editor.get_character_count()
        title = active_editor.current_item.title if active_editor.current_item else "Ningún documento seleccionado"

        return {
            "document_title": title,
            "words": words,
            "characters": chars,
            "view_mode": self.current_view_mode.value,
            "is_dirty": active_editor.is_dirty,
            "project_title": self.project.project_data.get("title", "") if self.project else "",
            "active_theme": self.theme_engine.current_mode.value,
            "ui_density": self.theme_engine.density_mode.value,
            "theme_switch_latency_ms": self.last_theme_switch_latency_ms
        }
