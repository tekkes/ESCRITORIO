"""
Atomic Storage Manager para Escritorio
Garantiza persistencia segura contra cortes de energía mediante escritura en staging (.tmp),
verificación de integridad de checksum SHA-256 y sustitución atómica mediante Windows ReplaceFileW.
"""

import os
import sys
import hashlib
import ctypes
from pathlib import Path
from typing import Union, Optional

class AtomicStorage:
    """Manejador de operaciones de I/O atómicas sobre el sistema de archivos."""

    @staticmethod
    def _calculate_sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @classmethod
    def write_atomic_bytes(cls, target_path: Union[str, Path], data: bytes, backup_extension: Optional[str] = None) -> bool:
        """
        Escribe 'data' de forma transaccional en 'target_path'.
        1. Escribe en {target_path}.tmp_{pid}
        2. Vuelca a disco con flush y fsync
        3. Realiza sustitución atómica usando ReplaceFileW en Windows o atomic rename
        """
        target = Path(target_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)

        temp_path = target.with_name(f"{target.name}.tmp_{os.getpid()}")
        expected_hash = cls._calculate_sha256(data)

        # 1. Escritura inicial en archivo temporal
        with open(temp_path, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())

        # 2. Verificación de integridad post-escritura
        with open(temp_path, "rb") as f:
            written_data = f.read()
            if cls._calculate_sha256(written_data) != expected_hash:
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
                raise IOError(f"Falla de integridad SHA-256 al escribir en {temp_path}")

        # 3. Reemplazo atómico
        if not target.exists():
            # Si el destino no existe, un renombramiento simple es atómico a nivel de directorio
            try:
                os.replace(temp_path, target)
                return True
            except Exception as e:
                if temp_path.exists():
                    os.remove(temp_path)
                raise e

        # Si el destino ya existe en Windows, usamos ReplaceFileW para atomicidad garantizada
        if sys.platform == "win32":
            kernel32 = ctypes.windll.kernel32
            REPLACEFILE_WRITE_THROUGH = 0x00000001
            REPLACEFILE_IGNORE_MERGE_ERRORS = 0x00000002

            lp_target = str(target)
            lp_temp = str(temp_path)
            lp_backup = str(target.with_suffix(backup_extension)) if backup_extension else None

            success = kernel32.ReplaceFileW(
                ctypes.c_wchar_p(lp_target),
                ctypes.c_wchar_p(lp_temp),
                ctypes.c_wchar_p(lp_backup),
                ctypes.c_uint(REPLACEFILE_WRITE_THROUGH | REPLACEFILE_IGNORE_MERGE_ERRORS),
                None,
                None
            )
            if success:
                return True
            else:
                # Fallback a os.replace si ReplaceFileW falla por permisos o filesystem exFAT/FAT32
                os.replace(temp_path, target)
                return True
        else:
            os.replace(temp_path, target)
            return True

    @classmethod
    def write_atomic_text(cls, target_path: Union[str, Path], content: str, encoding: str = "utf-8") -> bool:
        """Escribe texto de forma atómica codificado en la codificación especificada (por defecto UTF-8)."""
        data = content.encode(encoding)
        return cls.write_atomic_bytes(target_path, data)

    @classmethod
    def read_text(cls, file_path: Union[str, Path], encoding: str = "utf-8") -> str:
        """Lee texto garantizando el cierre inmediato del descriptor de archivo."""
        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            return f.read()

    @classmethod
    def read_bytes(cls, file_path: Union[str, Path]) -> bytes:
        """Lee bytes garantizando el cierre inmediato del descriptor de archivo."""
        with open(file_path, "rb") as f:
            return f.read()
