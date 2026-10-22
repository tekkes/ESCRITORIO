"""
Backup Manager para Escritorio
Gestión automatizada de copias de seguridad en segundo plano, compresión ZIP,
sellado de tiempo, verificación de integridad criptográfica SHA-256 y política de rotación.
"""

import os
import zipfile
import datetime
import hashlib
from pathlib import Path
from typing import Union, Optional, List, Dict, Any

class BackupManager:
    """Gestiona la compresión, verificación SHA-256 y rotación de copias de seguridad del proyecto."""

    def __init__(self, backup_dir: Union[str, Path], max_backups: int = 5):
        self.backup_dir = Path(backup_dir).resolve()
        self.max_backups = max_backups
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def compute_file_sha256(file_path: Union[str, Path]) -> str:
        """Calcula el hash SHA-256 de un archivo en disco."""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    @classmethod
    def create_backup_zip(
        cls,
        project_path: Union[str, Path],
        backup_dir: Union[str, Path],
        project_title: Optional[str] = None
    ):
        """Método de clase de conveniencia para empaquetar un backup ZIP y retornar (path, sha256)."""
        mgr = cls(backup_dir)
        res = mgr.create_project_backup(project_path, project_title)
        return str(res["path"]), res["sha256"]

    def create_project_backup(self, project_path: Union[str, Path], project_title: Optional[str] = None) -> Dict[str, Any]:
        """
        Empaqueta el directorio del proyecto (.scriv o .escr) en un archivo ZIP con marca temporal.
        Verifica su integridad comprobando el archivo ZIP y calculando su hash SHA-256.
        Aplica la política de rotación eliminando las copias más antiguas si se supera max_backups.
        """
        proj = Path(project_path).resolve()
        if not proj.exists() or not proj.is_dir():
            raise FileNotFoundError(f"El proyecto '{project_path}' no existe o no es un directorio.")

        title = project_title or proj.stem
        # Limpieza de caracteres no permitidos en nombres de archivo
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).strip()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{safe_title}_backup_{timestamp}.zip"
        backup_file_path = self.backup_dir / backup_filename

        temp_zip = self.backup_dir / f"{backup_filename}.tmp"

        with zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for root, dirs, files in os.walk(proj):
                for file in files:
                    # Omitir archivos temporales de bloqueo, swap o temporales
                    if file.endswith((".tmp", ".lock", "~")) or file == "project.lock":
                        continue
                    file_full_path = Path(root) / file
                    rel_path = file_full_path.relative_to(proj)
                    zipf.write(file_full_path, arcname=str(rel_path))

        # 1. Validación de integridad de la estructura ZIP
        with zipfile.ZipFile(temp_zip, "r") as test_zip:
            bad_file = test_zip.testzip()
            if bad_file is not None:
                temp_zip.unlink(missing_ok=True)
                raise IOError(f"El archivo ZIP generado contiene un archivo corrupto: {bad_file}")

        # 2. Reemplazo seguro
        if backup_file_path.exists():
            backup_file_path.unlink()
        temp_zip.rename(backup_file_path)

        # 3. Cálculo de SHA-256
        sha256_hash = self.compute_file_sha256(backup_file_path)

        # 4. Aplicar política de rotación
        removed = self.rotate_backups(safe_title)

        return {
            "path": backup_file_path,
            "filename": backup_filename,
            "sha256": sha256_hash,
            "size_bytes": backup_file_path.stat().st_size,
            "rotated_count": len(removed)
        }

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
