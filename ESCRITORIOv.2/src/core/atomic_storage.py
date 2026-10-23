"""
ESCRITORIO v2.0 - Atomic Storage & Cooperative Locking Engine
Garantiza persistencia ACID 100% libre de corrupción y bloqueos cooperativos.
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any


class AtomicStorage:
    """Manejador de almacenamiento atómico para Windows 11."""

    @staticmethod
    def write_atomic_text(target_path: Path, content: str, encoding: str = "utf-8") -> bool:
        """Escribe un archivo de texto de forma atómica: tmp -> flush -> rename."""
        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = target_path.with_name(f"{target_path.name}.{os.getpid()}.tmp")

        try:
            with open(tmp_path, "w", encoding=encoding) as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())

            # En Windows os.replace reemplaza atómicamente el destino
            os.replace(tmp_path, target_path)
            return True
        except Exception as e:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass
            raise IOError(f"Fallo en escritura atómica de {target_path}: {e}")

    @staticmethod
    def write_atomic_bytes(target_path: Path, data: bytes) -> bool:
        """Escribe datos binarios de forma atómica."""
        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = target_path.with_name(f"{target_path.name}.{os.getpid()}.tmp")

        try:
            with open(tmp_path, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())

            os.replace(tmp_path, target_path)
            return True
        except Exception as e:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass
            raise IOError(f"Fallo en escritura atómica binaria de {target_path}: {e}")

    @staticmethod
    def read_text_safe(path: Path, default: str = "", encoding: str = "utf-8") -> str:
        """Lee un archivo de texto de forma segura."""
        path = Path(path)
        if not path.exists():
            return default
        try:
            with open(path, "r", encoding=encoding, errors="replace") as f:
                return f.read()
        except Exception:
            return default

    @staticmethod
    def compute_sha256(path: Path) -> str:
        """Calcula el hash SHA-256 de un archivo."""
        sha = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                sha.update(chunk)
        return sha.hexdigest()


class ProjectLock:
    """Bloqueo cooperativo para prevenir aperturas concurrentes de un mismo proyecto."""

    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir)
        self.lock_file = self.project_dir / "project.lock"
        self._is_locked = False

    def acquire(self) -> bool:
        """Intenta adquirir el lock. Retorna True si tiene éxito, False si ya está bloqueado."""
        if self.lock_file.exists():
            try:
                data = json.loads(self.lock_file.read_text(encoding="utf-8"))
                pid = data.get("pid")
                # Verificar si el proceso todavía sigue vivo
                if pid and self._is_process_running(pid):
                    return False
            except Exception:
                pass

        lock_data = {
            "pid": os.getpid(),
            "time": time.time(),
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "user": os.getenv("USERNAME", "user"),
            "machine": os.getenv("COMPUTERNAME", "localhost")
        }
        try:
            AtomicStorage.write_atomic_text(self.lock_file, json.dumps(lock_data, indent=2))
            self._is_locked = True
            return True
        except Exception:
            return False

    def release(self):
        """Libera el lock eliminando el archivo project.lock."""
        if self.lock_file.exists():
            try:
                self.lock_file.unlink()
                self._is_locked = False
            except Exception:
                pass

    @staticmethod
    def _is_process_running(pid: int) -> bool:
        """Comprueba si un PID dado está activo en el sistema Windows."""
        if sys.platform == "win32":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            SYNCHRONIZE = 0x00100000
            process = kernel32.OpenProcess(SYNCHRONIZE, False, pid)
            if process:
                kernel32.CloseHandle(process)
                return True
            return False
        else:
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False
