"""
ImageViewer para Escritorio
Visor de imágenes de investigación con soporte de zoom, rotación y ajuste.
Formatos: PNG, JPG, JPEG, SVG, BMP, GIF, WEBP.
"""

from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import struct


class ImageViewer:
    """Visor ergonómico de imágenes de investigación."""

    SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".bmp", ".gif", ".webp"}

    def __init__(self):
        self.file_path: Optional[str] = None
        self.zoom: float = 1.0  # 1.0 = 100%
        self.rotation_degrees: int = 0  # 0, 90, 180, 270
        self.flip_h: bool = False
        self.flip_v: bool = False
        self.fit_to_window: bool = True
        self.width_px: int = 0
        self.height_px: int = 0
        self.metadata: Dict[str, Any] = {}

    def load_file(self, file_path: str) -> bool:
        """Carga una imagen y extrae sus dimensiones y metadatos básicos."""
        p = Path(file_path)
        if not p.exists() or p.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return False

        self.file_path = str(p.resolve())
        self.zoom = 1.0
        self.rotation_degrees = 0
        self.flip_h = False
        self.flip_v = False
        self.fit_to_window = True

        data = p.read_bytes()
        self.width_px, self.height_px = self._extract_dimensions(data, p.suffix.lower())
        self.metadata = {
            "file_name": p.name,
            "format": p.suffix.lower().lstrip("."),
            "file_size_kb": round(len(data) / 1024, 2),
            "dimensions": f"{self.width_px}x{self.height_px}" if self.width_px else "Vectorial"
        }
        return True

    def _extract_dimensions(self, data: bytes, ext: str) -> Tuple[int, int]:
        """Extrae el tamaño en píxeles inspeccionando las cabeceras de imagen estándar."""
        try:
            if ext == ".png" and len(data) >= 24:
                # Cabecera IHDR de PNG: offset 16 -> width (4 bytes), height (4 bytes)
                w, h = struct.unpack(">II", data[16:24])
                return w, h
            elif ext in (".jpg", ".jpeg") and len(data) >= 10:
                # Parse básico de JPEG SOF0 / SOF2
                idx = 2
                while idx < len(data) - 9:
                    marker, length = struct.unpack(">2sH", data[idx:idx+4])
                    if marker in (b"\xff\xc0", b"\xff\xc2"):
                        h, w = struct.unpack(">HH", data[idx+5:idx+9])
                        return w, h
                    idx += 2 + length
            elif ext == ".bmp" and len(data) >= 26:
                w, h = struct.unpack("<II", data[18:26])
                return w, h
            elif ext == ".gif" and len(data) >= 10:
                w, h = struct.unpack("<HH", data[6:10])
                return w, h
        except Exception:
            pass
        return 800, 600  # Dimensiones por defecto si no se pueden extraer

    # =========================================================================
    # Control de Zoom
    # =========================================================================

    def zoom_in(self, step: float = 0.15):
        self.zoom = min(5.0, round(self.zoom + step, 2))
        self.fit_to_window = False

    def zoom_out(self, step: float = 0.15):
        self.zoom = max(0.1, round(self.zoom - step, 2))
        self.fit_to_window = False

    def reset_zoom(self):
        self.zoom = 1.0
        self.fit_to_window = False

    def toggle_fit_to_window(self) -> bool:
        self.fit_to_window = not self.fit_to_window
        if self.fit_to_window:
            self.zoom = 1.0
        return self.fit_to_window

    # =========================================================================
    # Rotación y Espejado
    # =========================================================================

    def rotate_clockwise(self):
        """Rota 90 grados en sentido horario."""
        self.rotation_degrees = (self.rotation_degrees + 90) % 360

    def rotate_counter_clockwise(self):
        """Rota 90 grados en sentido antihorario."""
        self.rotation_degrees = (self.rotation_degrees - 90) % 360

    def rotate_180(self):
        self.rotation_degrees = (self.rotation_degrees + 180) % 360

    def toggle_flip_horizontal(self) -> bool:
        self.flip_h = not self.flip_h
        return self.flip_h

    def toggle_flip_vertical(self) -> bool:
        self.flip_v = not self.flip_v
        return self.flip_v

    def get_state(self) -> dict:
        return {
            "file_path": self.file_path,
            "zoom": self.zoom,
            "rotation_degrees": self.rotation_degrees,
            "flip_h": self.flip_h,
            "flip_v": self.flip_v,
            "fit_to_window": self.fit_to_window,
            "dimensions": (self.width_px, self.height_px),
            "metadata": self.metadata
        }
