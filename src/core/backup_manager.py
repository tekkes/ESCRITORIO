"""
Backup Manager para Escritorio
Gestión automatizada de copias de seguridad en segundo plano, compresión ZIP,
sellado de tiempo y política de rotación de copias conservadas.
"""

import os
import zipfile
import datetime
from pathlib import Path
from typing import Union, Optional, List

class BackupManager:
    """Gestiona la compresión y rotación de copias de seguridad del proyecto."""

    def __init__(self, backup_dir: Union[str, Path], max_backups: int = 5):
        self.backup_dir = Path(backup_dir).resolve()
        self.max_backups = max_backups
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_project_backup(self, project_path: Union[str, Path], project_title: Optional[str] = None) -> Path:
        """
        Empaqueta el directorio del proyecto (.scriv o .escr) en un archivo ZIP con marca temporal.
        Aplica la política de rotación eliminando las copias más antiguas si se supera max_backups.
        """
        proj = Path(project_path).resolve()
        if not proj.exists() or not proj.is_dir():
            raise FileNotFoundError(f"El proyecto '{project_path}' no existe o no es un directorio.")

        title = project_title or proj.stem
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{title}_backup_{timestamp}.zip"
        backup_file_path = self.backup_dir / backup_filename

        temp_zip = self.backup_dir / f"{backup_filename}.tmp"

        with zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for root, dirs, files in os.walk(proj):
                for file in files:
                    # Omitir archivos temporales de bloqueo o swap
                    if file.endswith((".tmp", ".lock", "~")):
                        continue
                    file_full_path = Path(root) / file
                    rel_path = file_full_path.relative_to(proj)
                    zipf.write(file_full_path, arcname=str(rel_path))

        # Reemplazo seguro
        if backup_file_path.exists():
            backup_file_path.unlink()
        temp_zip.rename(backup_file_path)

        # Aplicar rotación
        self.rotate_backups(title)

        return backup_file_path

    def rotate_backups(self, prefix: str) -> List[Path]:
        """Elimina copias antiguas si superan el límite establecido."""
        pattern = f"{prefix}_backup_*.zip"
        backups = sorted(self.backup_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)

        removed = []
        if len(backups) > self.max_backups:
            for extra in backups[self.max_backups:]:
                try:
                    extra.unlink()
                    removed.append(extra)
                except OSError:
                    pass
        return removed

    def list_backups(self, prefix: Optional[str] = None) -> List[Path]:
        """Devuelve la lista de copias disponibles ordenadas por fecha más reciente."""
        pattern = f"{prefix}_backup_*.zip" if prefix else "*_backup_*.zip"
        return sorted(self.backup_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
