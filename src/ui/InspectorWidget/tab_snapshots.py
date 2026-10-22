"""
Pestaña 4 del Inspector: Instantáneas (Snapshots)
- Toma de instantáneas rápidas (Ctrl+5) o con título (Ctrl+Shift+5) en Snapshots/<UUID>/
- Motor de Comparación Diferencial (Compare) con algoritmo de Myers Diff
  (palabras eliminadas tachadas en rojo, palabras añadidas subrayadas en azul/verde)
- Botón Rollback con opción de instantánea de seguridad previa
"""

import json
import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass, field

from ...core.project import BinderItem, EscritorioProject
from ...core.rtf_engine import RTFEngine
from .myers_diff import MyersDiffEngine, DiffChunk, DiffGranularity


@dataclass
class SnapshotItem:
    id: str
    uuid_doc: str
    title: str
    date: str
    word_count: int
    file_path: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "uuid_doc": self.uuid_doc,
            "title": self.title,
            "date": self.date,
            "word_count": self.word_count,
            "file_path": self.file_path
        }


class TabSnapshots:
    """Controlador de la Pestaña 4: Instantáneas, Comparador Myers Diff y Rollback."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.project: Optional[EscritorioProject] = project
        self.active_item: Optional[BinderItem] = None

        # Caché de instantáneas en memoria
        self.snapshots: List[SnapshotItem] = []
        self.selected_snapshot_id: Optional[str] = None

        # Granularidad activa para el diff
        self.diff_granularity: DiffGranularity = DiffGranularity.WORD
        self.current_diff_chunks: List[DiffChunk] = []

    def set_item(self, item: Optional[BinderItem]):
        self.active_item = item
        if not self.project and item and getattr(item, "project", None):
            self.project = item.project
        self.selected_snapshot_id = None
        self.current_diff_chunks.clear()
        self.refresh_snapshots()

    def _get_snapshots_dir(self) -> Optional[Path]:
        """Directorio físico: <project_dir>/Files/Snapshots/<UUID>/"""
        if not self.active_item or not getattr(self.active_item, "project", None):
            return None
        proj_dir = self.active_item.project.project_dir
        snap_dir = proj_dir / "Files" / "Snapshots" / self.active_item.uuid
        snap_dir.mkdir(parents=True, exist_ok=True)
        return snap_dir

    def _get_index_file(self) -> Optional[Path]:
        d = self._get_snapshots_dir()
        return d / "snapshots.json" if d else None

    def refresh_snapshots(self):
        """Carga el listado histórico de instantáneas desde disco."""
        self.snapshots.clear()
        idx_file = self._get_index_file()

        if idx_file and idx_file.exists():
            try:
                data = json.loads(idx_file.read_text(encoding="utf-8"))
                for item in data.get("snapshots", []):
                    snap = SnapshotItem(
                        id=item["id"],
                        uuid_doc=item["uuid_doc"],
                        title=item["title"],
                        date=item["date"],
                        word_count=item.get("word_count", 0),
                        file_path=item["file_path"]
                    )
                    self.snapshots.append(snap)
            except Exception:
                pass

    def _save_index(self):
        idx_file = self._get_index_file()
        if idx_file:
            payload = {
                "snapshots": [s.to_dict() for s in self.snapshots]
            }
            idx_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # =========================================================================
    # Toma de Instantáneas (Ctrl+5 / Ctrl+Shift+5)
    # =========================================================================

    def take_snapshot(self, title: Optional[str] = None) -> Optional[SnapshotItem]:
        """Toma una instantánea de la versión actual del documento."""
        if not self.active_item:
            return None

        now = datetime.datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
        snap_id = f"snap_{now.strftime('%Y%m%d_%H%M%S')}_{len(self.snapshots)+1}"
        snap_title = title.strip() if title and title.strip() else f"Instantánea {timestamp_str}"

        # Obtener contenido actual
        current_rtf = self.active_item.read_content_rtf() if getattr(self.active_item, "project", None) else ""
        current_words = RTFEngine.count_words(current_rtf, is_rtf=True)

        snap_dir = self._get_snapshots_dir()
        if snap_dir:
            file_name = f"{snap_id}.rtf"
            file_path = snap_dir / file_name
            file_path.write_text(current_rtf, encoding="utf-8")
            saved_rel_path = str(file_path)
        else:
            saved_rel_path = ""

        snap = SnapshotItem(
            id=snap_id,
            uuid_doc=self.active_item.uuid,
            title=snap_title,
            date=timestamp_str,
            word_count=current_words,
            file_path=saved_rel_path
        )

        self.snapshots.insert(0, snap)
        self.selected_snapshot_id = snap.id
        self._save_index()
        return snap

    def take_snapshot_with_title(self, title: str) -> Optional[SnapshotItem]:
        """Atajo Ctrl+Shift+5: Toma de instantánea con diálogo de título."""
        return self.take_snapshot(title=title)

    def delete_snapshot(self, snap_id: str):
        snap = next((s for s in self.snapshots if s.id == snap_id), None)
        if snap:
            if snap.file_path and Path(snap.file_path).exists():
                try:
                    Path(snap.file_path).unlink()
                except OSError:
                    pass
            self.snapshots.remove(snap)
            self._save_index()
            if self.selected_snapshot_id == snap_id:
                self.selected_snapshot_id = None
                self.current_diff_chunks.clear()

    # =========================================================================
    # Comparador Diferencial Myers Diff (Compare)
    # =========================================================================

    def select_snapshot(self, snap_id: str):
        self.selected_snapshot_id = snap_id
        self.compute_comparison()

    def set_diff_granularity(self, granularity: DiffGranularity):
        self.diff_granularity = granularity
        self.compute_comparison()

    def compute_comparison(self) -> List[DiffChunk]:
        """Calcula las diferencias entre la versión actual y la instantánea seleccionada."""
        self.current_diff_chunks.clear()
        if not self.active_item or not self.selected_snapshot_id:
            return []

        snap = next((s for s in self.snapshots if s.id == self.selected_snapshot_id), None)
        if not snap or not snap.file_path or not Path(snap.file_path).exists():
            return []

        snap_rtf = Path(snap.file_path).read_text(encoding="utf-8")
        snap_plain = RTFEngine.rtf_to_plain_text(snap_rtf)

        current_rtf = self.active_item.read_content_rtf() if getattr(self.active_item, "project", None) else ""
        current_plain = RTFEngine.rtf_to_plain_text(current_rtf)

        # Original = Instantánea antigua, Revisado = Documento actual
        self.current_diff_chunks = MyersDiffEngine.compute_diff(
            original_text=snap_plain,
            revised_text=current_plain,
            granularity=self.diff_granularity
        )
        return self.current_diff_chunks

    def get_diff_html(self) -> str:
        """Devuelve el HTML enriquecido con tachados en rojo y subrayados en verde/azul."""
        if not self.current_diff_chunks:
            self.compute_comparison()
        return MyersDiffEngine.format_diff_html(self.current_diff_chunks)

    def get_diff_plain(self) -> str:
        if not self.current_diff_chunks:
            self.compute_comparison()
        return MyersDiffEngine.format_diff_plain(self.current_diff_chunks)

    # =========================================================================
    # Rollback a Versión Antigua
    # =========================================================================

    def rollback(self, snap_id: Optional[str] = None, create_safety_snapshot: bool = True) -> bool:
        """
        Restaura el contenido de la instantánea seleccionada como el content.rtf actual.
        Si create_safety_snapshot es True, toma antes una instantánea de seguridad.
        """
        target_id = snap_id or self.selected_snapshot_id
        if not self.active_item or not target_id:
            return False

        snap = next((s for s in self.snapshots if s.id == target_id), None)
        if not snap or not snap.file_path or not Path(snap.file_path).exists():
            return False

        if create_safety_snapshot:
            self.take_snapshot(title=f"Seguridad antes de Rollback a '{snap.title}'")

        snap_rtf = Path(snap.file_path).read_text(encoding="utf-8")
        if getattr(self.active_item, "project", None):
            self.active_item.write_content_rtf(snap_rtf)
            self.active_item.save_if_dirty()

        self.compute_comparison()
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_count": len(self.snapshots),
            "selected_snapshot_id": self.selected_snapshot_id,
            "snapshots": [s.to_dict() for s in self.snapshots],
            "granularity": self.diff_granularity.value,
            "diff_plain": self.get_diff_plain() if self.selected_snapshot_id else "",
            "diff_html": self.get_diff_html() if self.selected_snapshot_id else ""
        }
