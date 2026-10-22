"""
Inspector Tabs Definitions para Escritorio
Definición de las pestañas especializadas del panel lateral derecho con iconos compactos de 16px.
"""

from enum import Enum
from typing import List, Dict, Any


class InspectorTabId(Enum):
    NOTES_SYNOPSIS = "notes_synopsis"    # 1. Sinopsis y Notas
    BOOKMARKS = "bookmarks"              # 2. Marcadores (Doc y Proyecto)
    METADATA = "metadata"                # 3. Metadatos (Config, Custom y Keywords HUD)
    SNAPSHOTS = "snapshots"              # 4. Instantáneas con Myers Diff y Rollback
    COMMENTS_FOOTNOTES = "comments"      # 5. Comentarios interactivos y Notas al pie

    # Alias de retrocompatibilidad
    SYNOPSIS = "notes_synopsis"
    NOTES = "notes_synopsis"
    COMMENTS = "comments"


TAB_METADATA = [
    {
        "id": InspectorTabId.NOTES_SYNOPSIS.value,
        "title": "Sinopsis y Notas",
        "short_title": "Notas",
        "icon": "icon_notes.png",
        "icon_glyph": "📝",
        "tooltip": "Sinopsis de tarjeta y notas del documento (notes.rtf)"
    },
    {
        "id": InspectorTabId.BOOKMARKS.value,
        "title": "Marcadores",
        "short_title": "Marcadores",
        "icon": "icon_bookmark.png",
        "icon_glyph": "🔖",
        "tooltip": "Marcadores del documento y del proyecto con visor integrado"
    },
    {
        "id": InspectorTabId.METADATA.value,
        "title": "Metadatos",
        "short_title": "Metadatos",
        "icon": "icon_metadata.png",
        "icon_glyph": "⚙",
        "tooltip": "Compilación, Tipo de sección, Custom Metadata y Keywords HUD"
    },
    {
        "id": InspectorTabId.SNAPSHOTS.value,
        "title": "Instantáneas",
        "short_title": "Instantáneas",
        "icon": "icon_snapshots.png",
        "icon_glyph": "📷",
        "tooltip": "Toma de instantáneas (Ctrl+5), comparación Myers Diff y Rollback"
    },
    {
        "id": InspectorTabId.COMMENTS_FOOTNOTES.value,
        "title": "Comentarios y Notas al Pie",
        "short_title": "Comentarios",
        "icon": "icon_comments.png",
        "icon_glyph": "💬",
        "tooltip": "Comentarios enlazados bidireccionalmente y notas al pie"
    }
]
