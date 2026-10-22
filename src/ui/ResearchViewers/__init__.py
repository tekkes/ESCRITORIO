"""
Paquete ResearchViewers de Escritorio.
"""

from .pdf_viewer import PDFViewer, PDFSearchResult
from .image_viewer import ImageViewer
from .media_player import TranscriptionPlayer
from .web_viewer import WebArchiveViewer
from .research_router import ResearchViewerRouter

__all__ = [
    "PDFViewer",
    "PDFSearchResult",
    "ImageViewer",
    "TranscriptionPlayer",
    "WebArchiveViewer",
    "ResearchViewerRouter"
]
