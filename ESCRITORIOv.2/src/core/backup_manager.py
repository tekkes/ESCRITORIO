"""
ESCRITORIO v2.0 - Backup Manager
Motor de copias de seguridad automáticas en formato ZIP con hash SHA-256 y retención configurable.
"""

import os
import json
import time
import zipfile
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from .atomic_storage import AtomicStorage


class BackupManager:
    """Gestiona copias de seguridad comprimidas en ZIP para proyectos de Escritorio."""

    def __init__(self, backup_dir: Path, max_backups: int = 5):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.max_backups = max_backups
        self.manifest_file = self.backup_dir / "backups_manifest.json"

    def create_backup(self, project_dir: Path, prefix: str = "backup") -> Optional[Path]:
        """Comprime el proyecto en un archivo ZIP con timestamp y calcula su SHA-256."""
        project_dir = Path(project_dir)
        if not project_dir.exists():
            return None

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        proj_name = project_dir.name
        zip_filename = f"{proj_name}_{prefix}_{timestamp}.zip"
        zip_path = self.backup_dir / zip_filename

        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
                for root, _, files in os.walk(project_dir):
                    for file in files:
                        # Excluir locks temporales
                        if file.endswith(".tmp") or file == "project.lock":
                            continue
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(project_dir)
                        zf.write(file_path, arcname)

            sha256 = AtomicStorage.compute_sha256(zip_path)
            self._record_manifest(zip_filename, proj_name, sha256, os.path.getsize(zip_path))
            self._rotate_backups(proj_name)
            return zip_path
        except Exception as e:
            if zip_path.exists():
                zip_path.unlink()
            raise IOError(f"Error al generar copia de seguridad ZIP: {e}")

    def list_backups(self, project_name: Optional[str] = None) -> List[Dict]:
        """Devuelve el historial de copias registradas."""
        manifest = self._load_manifest()
        if project_name:
            return [b for b in manifest if b.get("project") == project_name]
        return manifest

    def restore_backup(self, zip_filename: str, target_dir: Path) -> bool:
        """Restaura una copia de seguridad verificando previamente su integridad SHA-256."""
        zip_path = self.backup_dir / zip_filename
        if not zip_path.exists():
            raise FileNotFoundError(f"Copia no encontrada: {zip_filename}")

        manifest = self._load_manifest()
        recorded = next((b for b in manifest if b["filename"] == zip_filename), None)
        if recorded:
            current_hash = AtomicStorage.compute_sha256(zip_path)
            if current_hash != recorded["sha256"]:
                raise ValueError("La firma SHA-256 de la copia de seguridad no coincide (archivo corrupto)")

        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(target_dir)
        return True

    def _load_manifest(self) -> List[Dict]:
        if not self.manifest_file.exists():
            return []
        try:
            return json.loads(self.manifest_file.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _record_manifest(self, filename: str, project_name: str, sha256: str, size: int):
        manifest = self._load_manifest()
        manifest.insert(0, {
            "filename": filename,
            "project": project_name,
            "sha256": sha256,
            "size_bytes": size,
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": time.time()
        })
        AtomicStorage.write_atomic_text(self.manifest_file, json.dumps(manifest, indent=2))

    def _rotate_backups(self, project_name: str):
        """Mantiene únicamente las últimas N copias de un proyecto."""
        manifest = self._load_manifest()
        proj_backups = [b for b in manifest if b.get("project") == project_name]

        if len(proj_backups) > self.max_backups:
            to_remove = proj_backups[self.max_backups:]
            for item in to_remove:
                file_path = self.backup_dir / item["filename"]
                if file_path.exists():
                    try:
                        file_path.unlink()
                    except Exception:
                        pass
                manifest = [b for b in manifest if b["filename"] != item["filename"]]

            AtomicStorage.write_atomic_text(self.manifest_file, json.dumps(manifest, indent=2))
