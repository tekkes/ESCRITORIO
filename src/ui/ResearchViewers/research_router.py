"""
ResearchViewerRouter para Escritorio
Enrutador unificado para identificar el tipo de archivo de investigación
y despachar la instancia del visor adecuado: PDF, Imagen, Reproductor de Transcripción o Web.
"""

from pathlib import Path
from typing import Tuple, Any, Optional

from .pdf_viewer import PDFViewer
from .image_viewer import ImageViewer
from .media_player import TranscriptionPlayer
from .web_viewer import WebArchiveViewer


class ResearchViewerRouter:
    """Enrutador automático de visores de investigación."""

    @staticmethod
    def identify_type(file_path: str) -> str:
        """Determina el tipo de visor necesario ('pdf', 'image', 'media', 'web', 'unknown')."""
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            return "pdf"
        elif ext in ImageViewer.SUPPORTED_EXTENSIONS:
            return "image"
        elif ext in TranscriptionPlayer.AUDIO_EXTS or ext in TranscriptionPlayer.VIDEO_EXTS:
            return "media"
        elif ext in WebArchiveViewer.SUPPORTED_EXTS:
            return "web"
        return "unknown"

    @staticmethod
    def create_and_load_viewer(file_path: str) -> Tuple[str, Optional[Any]]:
        """Crea el visor correspondiente y carga el archivo."""
        v_type = ResearchViewerRouter.identify_type(file_path)

        if v_type == "pdf":
            v = PDFViewer()
            v.load_file(file_path)
            return "pdf", v
        elif v_type == "image":
            v = ImageViewer()
            v.load_file(file_path)
            return "image", v
        elif v_type == "media":
            v = TranscriptionPlayer()
            v.load_media(file_path)
            return "media", v
        elif v_type == "web":
            v = WebArchiveViewer()
            v.load_file(file_path)
            return "web", v

        return "unknown", None
