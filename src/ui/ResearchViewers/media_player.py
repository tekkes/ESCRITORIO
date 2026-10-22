"""
MediaPlayerViewer / TranscriptionPlayer para Escritorio
Reproductor integrado de audio y vídeo optimizado para la transcripción de entrevistas.
Soporta:
- Archivos de audio (MP3, WAV, OGG, M4A, FLAC, AAC) y vídeo (MP4, MKV, AVI, MOV, WEBM)
- Control de reproducción: Play, Pause, Toggle (F5 / Ctrl+Shift+Space)
- Retroceso de 5 segundos para transcripción continua (F6 / Ctrl+Alt+Left)
- Avance de 5 segundos (F7 / Ctrl+Alt+Right)
- Generación de marcas de tiempo automáticas para inserción en el editor ([00:04:12]) (F8)
- Control de velocidad de reproducción (0.5x .. 2.0x)
"""

from typing import Optional, Dict, Any
from pathlib import Path
import math


class TranscriptionPlayer:
    """Reproductor multimedia de investigación con foco en transcripción ágil."""

    AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac", ".wma"}
    VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm"}

    def __init__(self):
        self.file_path: Optional[str] = None
        self.is_video: bool = False
        self.is_playing: bool = False
        self.current_position: float = 0.0  # en segundos
        self.duration: float = 0.0          # en segundos
        self.playback_speed: float = 1.0     # 0.5x, 0.75x, 1.0x, 1.25x, 1.5x, 2.0x
        self.volume: float = 1.0            # 0.0 a 1.0

    def load_media(self, file_path: str, simulated_duration: float = 300.0) -> bool:
        """Carga un archivo de audio o vídeo para transcripción."""
        p = Path(file_path)
        ext = p.suffix.lower()
        if ext not in self.AUDIO_EXTS and ext not in self.VIDEO_EXTS:
            return False

        self.file_path = str(p.resolve())
        self.is_video = ext in self.VIDEO_EXTS
        self.is_playing = False
        self.current_position = 0.0
        self.playback_speed = 1.0
        self.duration = simulated_duration
        return True

    # =========================================================================
    # Controles de Reproducción y Atajos de Transcripción
    # =========================================================================

    def play(self):
        self.is_playing = True

    def pause(self):
        self.is_playing = False

    def toggle_play_pause(self) -> bool:
        """Alterna reproducción / pausa (Atajo: F5 / Ctrl+Shift+Space)."""
        self.is_playing = not self.is_playing
        return self.is_playing

    def rewind_seconds(self, seconds: float = 5.0) -> float:
        """
        Retrocede X segundos sin quitar las manos del teclado (Atajo: F6 / Ctrl+Alt+Left).
        Permite reescuchar una frase inmediatamente mientras se teclea.
        """
        self.current_position = max(0.0, self.current_position - seconds)
        return self.current_position

    def forward_seconds(self, seconds: float = 5.0) -> float:
        """Avanza X segundos (Atajo: F7 / Ctrl+Alt+Right)."""
        self.current_position = min(self.duration, self.current_position + seconds)
        return self.current_position

    def seek(self, target_seconds: float) -> float:
        """Salta a un instante determinado."""
        self.current_position = max(0.0, min(self.duration, target_seconds))
        return self.current_position

    def set_speed(self, speed: float):
        """Ajusta la velocidad de reproducción para mecanografía cómoda (0.5x a 2.0x)."""
        if 0.25 <= speed <= 3.0:
            self.playback_speed = speed

    def set_volume(self, vol: float):
        self.volume = max(0.0, min(1.0, vol))

    # =========================================================================
    # Marcas de Tiempo para Transcripción (F8)
    # =========================================================================

    def get_timestamp_string(self) -> str:
        """
        Genera la marca de tiempo formateada para incrustar en el texto:
        Ejemplo: '[00:04:12]' o '[01:23:45]' (Atajo: F8).
        """
        total_sec = int(self.current_position)
        hours = total_sec // 3600
        minutes = (total_sec % 3600) // 60
        seconds = total_sec % 60

        if hours > 0:
            return f"[{hours:02d}:{minutes:02d}:{seconds:02d}]"
        return f"[{minutes:02d}:{seconds:02d}]"

    def get_state(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "is_video": self.is_video,
            "is_playing": self.is_playing,
            "position": round(self.current_position, 2),
            "duration": round(self.duration, 2),
            "playback_speed": self.playback_speed,
            "timestamp": self.get_timestamp_string(),
            "volume": self.volume
        }
