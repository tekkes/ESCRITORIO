"""
Main Window para Escritorio
Ventana principal y orquestador maestro de la interfaz: barra de menú, barra de herramientas,
alternancia entre vistas (Editor, Corcho, Esquematizador), paneles acoplables, motor de temas,
control de densidad UI (Ultra-compacto), Live Theme Studio, Modo Scrivenings (Ctrl+1),
Pantalla Dividida (Ctrl+', Ctrl+\", Grid 4), Modo Guion (Ctrl+8) y Visores de Investigación.
"""

from enum import Enum
from typing import Optional, Dict, Any, List, Union
from pathlib import Path

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

from .ScriveningsEngine import ScriveningsEngine, DividerStyle
from .SplitEditorManager import SplitEditorManager, SplitLayoutMode, QuickReferenceManager, QuickReferenceWindow
from .ScriptwritingMode import ScriptwritingEngine, ScriptFormat, ScriptElementType
from .ResearchViewers import ResearchViewerRouter, PDFViewer, ImageViewer, TranscriptionPlayer, WebArchiveViewer


class CentralViewMode(Enum):
    EDITOR = "editor"
    CORKBOARD = "corkboard"
    OUTLINER = "outliner"
    SCRIVENINGS = "scrivenings"


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
        self.split_container = SplitContainer(project)
        self.split_manager: SplitEditorManager = self.split_container.manager
        self.quick_ref_manager: QuickReferenceManager = self.split_manager.quick_ref_manager

        self.scrivenings_engine = ScriveningsEngine(project)
        self.scriptwriting_engine = ScriptwritingEngine()

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
        self.split_container.manager.set_project(project)
        self.scrivenings_engine.project = project
        if self.binder.selected_uuid:
            self._on_binder_selection_changed(self.binder.selected_uuid)

    def _on_binder_selection_changed(self, uuid: str):
        if not self.project:
            return
        item = self.project.get_item(uuid)
        if not item:
            return

        # Si estamos en modo Scrivenings y se selecciona una carpeta o contenedor,
        # cargarlo en la vista compuesta continua
        if self.current_view_mode == CentralViewMode.SCRIVENINGS or self.scrivenings_engine.is_active:
            target_items = [item] if not item.children else [item] + item.children
            self.scrivenings_engine.load_from_binder_items(target_items)
            active_ed = self.split_container.get_active_editor()
            active_ed.plain_text = self.scrivenings_engine.composite_text

        # Cargar a través del SplitEditorManager respetando Lock in Place y navegación cruzada
        loaded_pane = self.split_container.load_item_to_active(item)

        # Actualizar inspector
        self.inspector.set_item(item)

        # Si el elemento tiene hijos o es contenedor, actualizar corcho y esquematizador
        if item.children:
            self.corkboard.load_container(item)
            self.outliner.load_container(item)

    # =========================================================================
    # Modo Scrivenings (Ctrl+1)
    # =========================================================================

    def toggle_scrivenings_mode(self) -> bool:
        """Alterna el modo Scrivenings continuo (Ctrl+1)."""
        if self.current_view_mode == CentralViewMode.SCRIVENINGS:
            self.current_view_mode = CentralViewMode.EDITOR
            self.scrivenings_engine.deactivate()
            # Restaurar documento simple
            if self.binder.selected_uuid:
                it = self.project.get_item(self.binder.selected_uuid)
                if it:
                    self.split_container.get_active_editor().load_item(it)
            return False
        else:
            self.current_view_mode = CentralViewMode.SCRIVENINGS
            self.scrivenings_engine.activate()
            # Cargar elementos seleccionados o activos
            if self.binder.selected_uuid:
                it = self.project.get_item(self.binder.selected_uuid)
                if it:
                    items = [it] if not it.children else [it] + it.children
                    self.scrivenings_engine.load_from_binder_items(items)
                    self.split_container.get_active_editor().plain_text = self.scrivenings_engine.composite_text
            return True

    def set_scrivenings_divider(self, style: DividerStyle):
        self.scrivenings_engine.set_divider_style(style)
        if self.current_view_mode == CentralViewMode.SCRIVENINGS:
            self.split_container.get_active_editor().plain_text = self.scrivenings_engine.composite_text

    # =========================================================================
    # Pantalla Dividida y Bloqueo (Ctrl+', Ctrl+\", Ctrl+Shift+L)
    # =========================================================================

    def split_vertical(self):
        """Divide verticalmente en 2 paneles (Ctrl+')."""
        self.split_container.split_vertical()

    def split_horizontal(self):
        """Divide horizontalmente en 2 paneles (Ctrl+\")."""
        self.split_container.split_horizontal()

    def split_grid(self):
        """Divide en cuadrícula de 4 paneles (2x2)."""
        self.split_container.split_grid()

    def close_split(self):
        self.split_container.close_split()

    def toggle_lock_editor(self) -> bool:
        """Bloquea el editor activo frente a selecciones del Binder (Ctrl+Shift+L)."""
        return self.split_container.toggle_lock_active_pane()

    def toggle_navigate_affects_other(self) -> bool:
        """Alterna la navegación cruzada hacia el otro editor."""
        return self.split_container.toggle_navigate_affects_other()

    def open_quick_reference(self, item: BinderItem) -> QuickReferenceWindow:
        """Abre un documento en ventana flotante independiente multi-monitor."""
        return self.quick_ref_manager.open_document(item)

    # =========================================================================
    # Modo Escritura de Guiones (Ctrl+8)
    # =========================================================================

    def toggle_scriptwriting_mode(self) -> bool:
        """Alterna el modo de escritura de guiones (Ctrl+8)."""
        return self.scriptwriting_engine.toggle_mode()

    def set_script_format(self, script_format: ScriptFormat):
        self.scriptwriting_engine.set_format(script_format)

    # =========================================================================
    # Visores de Investigación
    # =========================================================================

    def open_research_file(self, file_path: str, pane_id: Optional[str] = None):
        """Carga un archivo de investigación en el panel especificado o activo."""
        target_pane = self.split_manager.panes.get(pane_id or self.split_manager.active_pane_id)
        if not target_pane:
            return

        v_type, viewer = ResearchViewerRouter.create_and_load_viewer(file_path)
        if viewer:
            target_pane.load_research_media(file_path, viewer, v_type)

    # =========================================================================
    # Vistas y Temas
    # =========================================================================

    def set_view_mode(self, mode: CentralViewMode):
        self.current_view_mode = mode

    def toggle_binder(self):
        self.binder_visible = not self.binder_visible

    def toggle_inspector(self):
        self.inspector_visible = not self.inspector_visible

    def toggle_composition_mode(self):
        self.composition_mode.toggle()

    def set_theme(self, mode: Union[ThemeMode, str]) -> float:
        if isinstance(mode, str):
            try:
                mode_enum = ThemeMode(mode.lower())
            except ValueError:
                mode_enum = getattr(ThemeMode, mode.upper(), ThemeMode.MINIMALIST_DEFAULT)
        else:
            mode_enum = mode

        elapsed = self.theme_engine.set_builtin_mode(mode_enum)
        self.last_theme_switch_latency_ms = elapsed
        return elapsed

    def set_ui_density(self, density: Union[UIDensityMode, str]):
        if isinstance(density, str):
            density_enum = UIDensityMode(density.lower())
        else:
            density_enum = density
        self.theme_engine.set_density_mode(density_enum)

    def get_available_themes(self) -> List[Dict[str, str]]:
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
        words = self.scrivenings_engine.get_total_word_count() if self.current_view_mode == CentralViewMode.SCRIVENINGS else active_editor.get_word_count()
        chars = self.scrivenings_engine.get_total_character_count() if self.current_view_mode == CentralViewMode.SCRIVENINGS else active_editor.get_character_count()
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
            "theme_switch_latency_ms": self.last_theme_switch_latency_ms,
            "split_layout": self.split_manager.layout_mode.value,
            "is_locked": self.split_container.is_active_locked(),
            "scriptwriting_active": self.scriptwriting_engine.is_active,
            "scriptwriting_status": self.scriptwriting_engine.get_status_label() if self.scriptwriting_engine.is_active else ""
        }
