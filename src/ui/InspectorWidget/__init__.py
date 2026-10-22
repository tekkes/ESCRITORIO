"""
Paquete InspectorWidget de Escritorio
Panel lateral derecho multifunción (Ctrl+Shift+I) con paridad funcional total respecto a Scrivener 3.
"""

from .inspector_tabs import InspectorTabId, TAB_METADATA
from .tab_notes_synopsis import TabNotesSynopsis
from .tab_bookmarks import TabBookmarks, BookmarkScope, BookmarkItem
from .tab_metadata import TabMetadata, CustomFieldType, CustomFieldDefinition, ProjectKeywordsHUD, KeywordDefinition
from .myers_diff import MyersDiffEngine, DiffOp, DiffGranularity, DiffChunk
MyersDiff = MyersDiffEngine
from .tab_snapshots import TabSnapshots, SnapshotItem
from .tab_comments_footnotes import TabCommentsFootnotes, CommentItem
from .inspector_widget import InspectorWidget

__all__ = [
    "InspectorTabId",
    "TAB_METADATA",
    "TabNotesSynopsis",
    "TabBookmarks",
    "BookmarkScope",
    "BookmarkItem",
    "TabMetadata",
    "CustomFieldType",
    "CustomFieldDefinition",
    "ProjectKeywordsHUD",
    "KeywordDefinition",
    "MyersDiffEngine",
    "DiffOp",
    "DiffGranularity",
    "DiffChunk",
    "TabSnapshots",
    "SnapshotItem",
    "TabCommentsFootnotes",
    "CommentItem",
    "InspectorWidget"
]
