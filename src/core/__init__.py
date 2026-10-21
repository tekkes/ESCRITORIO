"""
Escritorio Core Module
Motor central para gestión de proyectos, almacenamiento atómico y parseo de formatos Scrivener 3 y nativos.
"""

from .uuid_manager import UUIDManager
from .storage_atomic import AtomicStorage
from .backup_manager import BackupManager
from .rtf_engine import RTFEngine
from .xml_parser import ScrivenerXMLParser
from .project import EscritorioProject, BinderItem

__all__ = [
    "UUIDManager",
    "AtomicStorage",
    "BackupManager",
    "RTFEngine",
    "ScrivenerXMLParser",
    "EscritorioProject",
    "BinderItem",
]
