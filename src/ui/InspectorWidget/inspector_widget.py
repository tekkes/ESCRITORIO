"""
InspectorWidget para Escritorio
Panel lateral derecho multifunción (Ctrl+Shift+I) con paridad funcional total respecto a Scrivener 3:
Coordina las 6 pestañas especializadas con cabecera de iconos compactos de 16px:
1. Pestaña 1: Sinopsis y Notas (Notes & Synopsis) con soporte de imagen y pie persistente
2. Pestaña 2: Marcadores (Bookmarks) con visor de lectura/edición integrado
3. Pestaña 3: Metadatos (Metadata), Custom Metadata configurable y Keywords HUD
4. Pestaña 4: Instantáneas (Snapshots / Ctrl+5 / Ctrl+Shift+5) con Myers Diff y Rollback
5. Pestaña 5: Comentarios y Notas al Pie (Comments & Footnotes) bidireccionales
"""

from typing import Optional, Dict, Any, List, Callable
from pathlib import Path

from ...core.project import BinderItem, EscritorioProject
from .inspector_tabs import InspectorTabId, TAB_METADATA
from .tab_notes_synopsis import TabNotesSynopsis
from .tab_bookmarks import TabBookmarks, BookmarkScope
from .tab_metadata import TabMetadata, CustomFieldType
from .tab_snapshots import TabSnapshots
from .tab_comments_footnotes import TabCommentsFootnotes
from .myers_diff import DiffGranularity


class InspectorWidget:
    """Controlador y orquestador maestro del panel Inspector (6 en 1)."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.project: Optional[EscritorioProject] = project
        self.active_item: Optional[BinderItem] = None
        self.active_tab: str = InspectorTabId.NOTES_SYNOPSIS.value
        self.is_visible: bool = True

        # Gestores de cada pestaña especializada
        self.tab_notes_synopsis = TabNotesSynopsis(project)
        self.tab_bookmarks = TabBookmarks(project)
        self.tab_metadata = TabMetadata(project)
        self.tab_snapshots = TabSnapshots(project)
        self.tab_comments_footnotes = TabCommentsFootnotes(project)

        # Callbacks hacia el Editor principal
        self.on_navigate_to_offset: Optional[Callable[[int, int], None]] = None
        self.on_item_updated: Optional[Callable[[], None]] = None

    # =========================================================================
    # Sincronización del Documento Activo
    # =========================================================================

    def set_item(self, item: Optional[BinderItem]):
        """Carga el nodo seleccionado del Binder en todas las pestañas del inspector."""
        self.active_item = item
        if not self.project and item and getattr(item, "project", None):
            self.project = item.project

        self.tab_notes_synopsis.set_item(item)
        self.tab_bookmarks.set_item(item)
        self.tab_metadata.set_item(item)
        self.tab_snapshots.set_item(item)
        self.tab_comments_footnotes.set_item(item)

    def set_project(self, project: EscritorioProject):
        self.project = project
        self.tab_notes_synopsis.project = project
        self.tab_bookmarks.project = project
        self.tab_metadata.project = project
        self.tab_snapshots.project = project
        self.tab_comments_footnotes.project = project

    # =========================================================================
    # Cambio y Gestión de Pestañas
    # =========================================================================

    def set_tab(self, tab_id: str):
        # Resolver alias de retrocompatibilidad
        if tab_id == "synopsis" or tab_id == "notes":
            self.active_tab = InspectorTabId.NOTES_SYNOPSIS.value
        elif tab_id == "comments":
            self.active_tab = InspectorTabId.COMMENTS_FOOTNOTES.value
        else:
            self.active_tab = tab_id

    def get_tabs_metadata(self) -> List[Dict[str, Any]]:
        return TAB_METADATA

    def toggle_visibility(self) -> bool:
        """Atajo Ctrl+Shift+I para conmutar el panel Inspector."""
        self.is_visible = not self.is_visible
        return self.is_visible

    # =========================================================================
    # Accesos Rápidos de la Pestaña 1 (Sinopsis, Imagen, Notas, Label/Status)
    # =========================================================================

    def get_synopsis(self) -> str:
        return self.tab_notes_synopsis.get_synopsis()

    def update_synopsis(self, text: str):
        self.tab_notes_synopsis.set_synopsis(text)
        if self.on_item_updated:
            self.on_item_updated()

    def toggle_synopsis_image_mode(self) -> bool:
        return self.tab_notes_synopsis.toggle_image_mode()

    def set_scene_image(self, file_path: str):
        return self.tab_notes_synopsis.set_scene_image(file_path)

    def get_notes_rtf(self) -> str:
        return self.tab_notes_synopsis.get_notes_rtf()

    def update_notes_rtf(self, rtf: str):
        self.tab_notes_synopsis.set_notes_rtf(rtf)
        if self.on_item_updated:
            self.on_item_updated()

    def set_label(self, label_id: int):
        self.tab_notes_synopsis.set_label(label_id)

    def set_status(self, status_id: int):
        self.tab_notes_synopsis.set_status(status_id)

    # =========================================================================
    # Accesos Rápidos de la Pestaña 2 (Marcadores)
    # =========================================================================

    def add_bookmark(self, target_uuid: str, title: Optional[str] = None, is_project: bool = False):
        scope = BookmarkScope.PROJECT if is_project else BookmarkScope.DOCUMENT
        return self.tab_bookmarks.add_bookmark(target_uuid, title=title, scope=scope)

    def get_preview_bookmark_content(self) -> str:
        return self.tab_bookmarks.get_preview_content()

    def update_preview_bookmark_content(self, text: str) -> bool:
        return self.tab_bookmarks.update_preview_content(text)

    # =========================================================================
    # Accesos Rápidos de la Pestaña 3 (Metadatos)
    # =========================================================================

    def set_include_in_compile(self, include: bool):
        self.tab_metadata.set_include_in_compile(include)

    def set_section_type(self, section_type: str):
        self.tab_metadata.set_section_type(section_type)

    def add_custom_metadata_field(self, field_id: str, name: str, field_type: str = "text"):
        ft = CustomFieldType.TEXT
        try:
            ft = CustomFieldType(field_type)
        except ValueError:
            pass
        return self.tab_metadata.add_custom_field(field_id, name, field_type=ft)

    def set_custom_metadata_value(self, field_id: str, value: Any):
        self.tab_metadata.set_custom_value(field_id, value)

    def get_custom_metadata_value(self, field_id: str) -> str:
        return self.tab_metadata.get_custom_value(field_id)

    def toggle_keywords_hud(self) -> bool:
        return self.tab_metadata.toggle_keywords_hud()

    # =========================================================================
    # Accesos Rápidos de la Pestaña 4 (Instantáneas / Snapshots)
    # =========================================================================

    def take_snapshot(self, title: Optional[str] = None):
        """Atajo Ctrl+5: Toma rápida de instantánea."""
        return self.tab_snapshots.take_snapshot(title=title)

    def take_snapshot_with_title(self, title: str):
        """Atajo Ctrl+Shift+5: Toma con título personalizado."""
        return self.tab_snapshots.take_snapshot_with_title(title=title)

    def compare_snapshot(self, snap_id: str, granularity: str = "word") -> str:
        gr = DiffGranularity.WORD
        try:
            gr = DiffGranularity(granularity)
        except ValueError:
            pass
        self.tab_snapshots.set_diff_granularity(gr)
        self.tab_snapshots.select_snapshot(snap_id)
        return self.tab_snapshots.get_diff_html()

    def rollback_snapshot(self, snap_id: str, create_safety_snapshot: bool = True) -> bool:
        ok = self.tab_snapshots.rollback(snap_id, create_safety_snapshot=create_safety_snapshot)
        if ok and self.on_item_updated:
            self.on_item_updated()
        return ok

    # =========================================================================
    # Accesos Rápidos de la Pestaña 5 (Comentarios y Notas al Pie)
    # =========================================================================

    def add_comment(self, text: str, start_offset: int = 0, length: int = 0, quote: str = "", author: str = "Escritor", color_hex: str = "#FBBF24"):
        return self.tab_comments_footnotes.add_comment(text, start_offset, length, quote, author, color_hex)

    def add_footnote(self, text: str, start_offset: int = 0, length: int = 0, quote: str = "", author: str = "Escritor"):
        return self.tab_comments_footnotes.add_footnote(text, start_offset, length, quote, author)

    def select_comment(self, item_id: str) -> Optional[tuple]:
        rng = self.tab_comments_footnotes.select_comment(item_id)
        if rng and self.on_navigate_to_offset:
            self.on_navigate_to_offset(rng[0], rng[1])
        return rng

    def highlight_comment_at_cursor(self, cursor_offset: int):
        return self.tab_comments_footnotes.find_comment_at_offset(cursor_offset)

    # =========================================================================
    # Datos de Vista / Telemetría
    # =========================================================================

    def get_view_data(self) -> Dict[str, Any]:
        return {
            "visible": self.is_visible,
            "active_tab": self.active_tab,
            "item_uuid": self.active_item.uuid if self.active_item else "",
            "item_title": self.active_item.title if self.active_item else "Sin selección",
            "tabs_header": self.get_tabs_metadata(),
            "notes_synopsis": self.tab_notes_synopsis.to_dict(),
            "bookmarks": self.tab_bookmarks.to_dict(),
            "metadata": self.tab_metadata.to_dict(),
            "snapshots": self.tab_snapshots.to_dict(),
            "comments": self.tab_comments_footnotes.to_dict(),
            "footer": self.tab_notes_synopsis.get_footer_state()
        }

    to_dict = get_view_data
