"""
Project Manager para Escritorio
Gestión unificada de ciclo de vida de proyectos (.scriv y .escr), árbol de Binder,
lectura y escritura atómica de archivos de datos (Files/Data/<UUID>/),
carga diferida (Lazy Loading), concurrencia con project.lock y autoguardado atómico.
"""

import os
import sys
import time
import socket
import getpass
import json
import datetime
import ctypes
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from .uuid_manager import UUIDManager
from .storage_atomic import AtomicStorage
from .backup_manager import BackupManager
from .rtf_engine import RTFEngine
from .xml_parser import (
    ScrivenerXMLParser,
    BinderItemData,
    LabelDefinition,
    StatusDefinition,
    CollectionDefinition
)

class ProjectLockedError(Exception):
    """Excepción lanzada cuando un proyecto ya está abierto por otra instancia o proceso activo."""
    def __init__(self, message: str, lock_info: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.lock_info = lock_info or {}

class BinderItem:
    """
    Nodo en memoria del árbol del Binder con carga diferida (Lazy Loading),
    marcado de estado sucio (dirty flag) y persistencia física atómica en Files/Data/<UUID>/.
    """

    def __init__(self, data: BinderItemData, project: 'EscritorioProject'):
        self.data = data
        self.project = project

        # Cachés de carga diferida
        self._cached_content_rtf: Optional[str] = None
        self._content_loaded: bool = False

        self._cached_notes_rtf: Optional[str] = None
        self._notes_loaded: bool = False

        self._cached_synopsis: Optional[str] = None
        self._synopsis_loaded: bool = False

        self._cached_comments_xml: Optional[str] = None
        self._comments_loaded: bool = False

        # Estado sucio y temporizador para autoguardado tras 2s de inactividad
        self.is_dirty: bool = False
        self.last_modified_timestamp: float = 0.0

    @property
    def uuid(self) -> str:
        return self.data.uuid

    @property
    def title(self) -> str:
        return self.data.title

    @title.setter
    def title(self, val: str):
        self.data.title = val
        self.mark_dirty()

    @property
    def item_type(self) -> str:
        return self.data.item_type

    @item_type.setter
    def item_type(self, val: str):
        self.data.item_type = val
        self.mark_dirty()

    @property
    def children(self) -> List['BinderItem']:
        return [self.project.get_item(c.uuid) for c in self.data.children if self.project.get_item(c.uuid)]

    def mark_dirty(self):
        """Marca el documento como modificado y actualiza el reloj de inactividad."""
        self.is_dirty = True
        self.last_modified_timestamp = time.time()
        self.data.modified = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_data_dir(self) -> Path:
        """Ruta física del directorio de datos del nodo: Files/Data/<UUID>/"""
        d = self.project.project_dir / "Files" / "Data" / self.uuid
        d.mkdir(parents=True, exist_ok=True)
        return d

    # =========================================================================
    # Carga Diferida (Lazy Loading) de Recursos de Archivo
    # =========================================================================

    def read_content_rtf(self) -> str:
        """Carga el texto enriquecido principal (content.rtf) solo cuando se solicita."""
        if not self._content_loaded:
            fpath = self.get_data_dir() / "content.rtf"
            if fpath.exists():
                self._cached_content_rtf = AtomicStorage.read_text(fpath, encoding="utf-8")
            else:
                self._cached_content_rtf = RTFEngine.plain_text_to_rtf("")
            self._content_loaded = True
        return self._cached_content_rtf

    def write_content_rtf(self, rtf_text: str):
        """Actualiza el texto en memoria y marca para autoguardado atómico."""
        self._cached_content_rtf = rtf_text
        self._content_loaded = True
        self.mark_dirty()

    def read_synopsis(self) -> str:
        """Carga la sinopsis para tarjetas del corcho (synopsis.txt) de forma diferida."""
        if not self._synopsis_loaded:
            fpath = self.get_data_dir() / "synopsis.txt"
            if fpath.exists():
                self._cached_synopsis = AtomicStorage.read_text(fpath, encoding="utf-8")
            else:
                self._cached_synopsis = ""
            self._synopsis_loaded = True
        return self._cached_synopsis

    def write_synopsis(self, text: str):
        """Actualiza la sinopsis de la tarjeta de corcho."""
        self._cached_synopsis = text
        self._synopsis_loaded = True
        self.mark_dirty()

    def read_notes_rtf(self) -> str:
        """Carga las notas del inspector (notes.rtf) de forma diferida."""
        if not self._notes_loaded:
            fpath = self.get_data_dir() / "notes.rtf"
            if fpath.exists():
                self._cached_notes_rtf = AtomicStorage.read_text(fpath, encoding="utf-8")
            else:
                self._cached_notes_rtf = ""
            self._notes_loaded = True
        return self._cached_notes_rtf

    def write_notes_rtf(self, rtf_text: str):
        """Actualiza las notas del inspector."""
        self._cached_notes_rtf = rtf_text
        self._notes_loaded = True
        self.mark_dirty()

    def read_comments_xml(self) -> str:
        """Carga el XML de comentarios y notas al pie (content.comments)."""
        if not self._comments_loaded:
            fpath = self.get_data_dir() / "content.comments"
            if fpath.exists():
                self._cached_comments_xml = AtomicStorage.read_text(fpath, encoding="utf-8")
            else:
                self._cached_comments_xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<Comments Version=\"1.0\"/>"
            self._comments_loaded = True
        return self._cached_comments_xml

    def write_comments_xml(self, xml_text: str):
        """Actualiza comentarios y notas al pie."""
        self._cached_comments_xml = xml_text
        self._comments_loaded = True
        self.mark_dirty()

    def save_if_dirty(self) -> bool:
        """
        Persiste los datos pendientes en disco mediante escritura atómica
        (staging en .tmp, flush de buffers físicos y reemplazo atómico).
        """
        if not self.is_dirty:
            return False

        data_dir = self.get_data_dir()
        if self._content_loaded and self._cached_content_rtf is not None:
            AtomicStorage.write_atomic_text(data_dir / "content.rtf", self._cached_content_rtf)

        if self._synopsis_loaded and self._cached_synopsis is not None:
            AtomicStorage.write_atomic_text(data_dir / "synopsis.txt", self._cached_synopsis)

        if self._notes_loaded and self._cached_notes_rtf is not None:
            AtomicStorage.write_atomic_text(data_dir / "notes.rtf", self._cached_notes_rtf)

        if self._comments_loaded and self._cached_comments_xml is not None:
            AtomicStorage.write_atomic_text(data_dir / "content.comments", self._cached_comments_xml)

        self.is_dirty = False
        return True

    def get_word_count(self) -> int:
        """Devuelve el recuento de palabras en el texto del nodo."""
        rtf = self.read_content_rtf()
        return RTFEngine.count_words(rtf, is_rtf=True)

class EscritorioProject:
    """
    Gestor principal de proyecto Escritorio (.escr) y Scrivener 3 (.scriv).
    Soporta cerrojo de concurrencia project.lock, autoguardado atómico y copias ZIP de respaldo.
    """

    _ACTIVE_PROJECT_INSTANCES: Dict[str, Any] = {}

    def __init__(self, project_dir: Union[str, Path]):
        self.project_dir = Path(project_dir).resolve()
        self.is_native = (self.project_dir.suffix.lower() == ".escr")
        self.project_file = self._find_project_file()
        self.project_data: Dict[str, Any] = {}
        self.items_by_uuid: Dict[str, BinderItem] = {}
        self.root_items: List[BinderItem] = []
        self.backup_manager: Optional[BackupManager] = None
        self._has_lock: bool = False

    def _find_project_file(self) -> Path:
        """Localiza el archivo XML maestro (.scrivx o .escrx)."""
        ext = ".escrx" if self.is_native else ".scrivx"
        candidates = list(self.project_dir.glob(f"*{ext}"))
        if candidates:
            return candidates[0]
        return self.project_dir / f"{self.project_dir.stem}{ext}"

    # =========================================================================
    # Sistema de Bloqueo Concurrente (project.lock)
    # =========================================================================

    def get_lock_file(self) -> Path:
        return self.project_dir / "project.lock"

    def is_locked(self) -> Optional[Dict[str, Any]]:
        """
        Verifica si el proyecto está bloqueado activamente por otra instancia.
        Si el proceso que creó el cerrojo ya murió, se detecta cerrojo obsoleto (stale lock).
        """
        canon = str(self.project_dir.resolve()).lower()
        if canon in self._ACTIVE_PROJECT_INSTANCES and self._ACTIVE_PROJECT_INSTANCES[canon] is not self:
            return {
                "pid": os.getpid(),
                "host": socket.gethostname(),
                "user": getpass.getuser(),
                "opened_at": "Instancia activa en este proceso",
                "status": "same_process_active"
            }

        lock_file = self.get_lock_file()
        if not lock_file.exists():
            return None

        try:
            with open(lock_file, "r", encoding="utf-8") as f:
                lock_data = json.load(f)
        except Exception:
            return {"pid": 0, "status": "corrupt"}

        pid = lock_data.get("pid", 0)
        if pid == os.getpid():
            # Si el archivo tiene nuestro propio PID y NO estamos registrados en _ACTIVE_PROJECT_INSTANCES,
            # significa que es un cerrojo residual de una ejecución previa
            if canon not in self._ACTIVE_PROJECT_INSTANCES:
                return None
            return None

        # Comprobar si el proceso con 'pid' sigue vivo
        if sys.platform == "win32":
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            STILL_ACTIVE = 259
            kernel32 = ctypes.windll.kernel32
            h_proc = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if h_proc:
                exit_code = ctypes.c_ulong()
                if kernel32.GetExitCodeProcess(h_proc, ctypes.byref(exit_code)):
                    kernel32.CloseHandle(h_proc)
                    if exit_code.value == STILL_ACTIVE:
                        return lock_data  # Bloqueo real activo
                else:
                    kernel32.CloseHandle(h_proc)
        else:
            try:
                os.kill(pid, 0)
                return lock_data
            except OSError:
                pass

        # Cerrojo obsoleto
        return None

    def acquire_lock(self, force: bool = False):
        """Adquiere el cerrojo exclusivo project.lock."""
        active_lock = self.is_locked()
        if active_lock and not force:
            raise ProjectLockedError(
                f"El proyecto ya está abierto por el proceso {active_lock.get('pid')} "
                f"en el equipo '{active_lock.get('host')}' desde {active_lock.get('opened_at')}.",
                lock_info=active_lock
            )

        canon = str(self.project_dir.resolve()).lower()
        self._ACTIVE_PROJECT_INSTANCES[canon] = self

        lock_data = {
            "pid": os.getpid(),
            "host": socket.gethostname(),
            "user": getpass.getuser(),
            "opened_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        lock_file = self.get_lock_file()
        with open(lock_file, "w", encoding="utf-8") as f:
            json.dump(lock_data, f, indent=2)
        self._has_lock = True

    def release_lock(self):
        """Libera el cerrojo project.lock si nos pertenece."""
        canon = str(self.project_dir.resolve()).lower()
        if self._ACTIVE_PROJECT_INSTANCES.get(canon) is self:
            self._ACTIVE_PROJECT_INSTANCES.pop(canon, None)

        if self._has_lock:
            lock_file = self.get_lock_file()
            try:
                if lock_file.exists():
                    lock_file.unlink()
            except OSError:
                pass
            self._has_lock = False

    # =========================================================================
    # Creación y Carga de Proyectos
    # =========================================================================

    @classmethod
    def create_new(cls, destination_path: Union[str, Path], title: str = "Nuevo Proyecto", native: bool = False) -> 'EscritorioProject':
        """Crea un nuevo proyecto con la estructura estándar de Scrivener 3 / Escritorio."""
        path = Path(destination_path)
        ext = ".escr" if native else ".scriv"
        if path.suffix.lower() != ext:
            path = path.with_suffix(ext)

        path.mkdir(parents=True, exist_ok=True)
        (path / "Files" / "Data").mkdir(parents=True, exist_ok=True)
        (path / "Files" / "Snapshots").mkdir(parents=True, exist_ok=True)
        (path / "Settings").mkdir(parents=True, exist_ok=True)

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Elementos raíz estándar
        draft_item = BinderItemData(
            uuid=UUIDManager.generate_uuid(),
            item_type="DraftFolder",
            title="Manuscrito",
            created=now_str,
            modified=now_str,
            icon_file_name="DraftFolder.png"
        )
        research_item = BinderItemData(
            uuid=UUIDManager.generate_uuid(),
            item_type="ResearchFolder",
            title="Investigación",
            created=now_str,
            modified=now_str,
            include_in_compile=False,
            icon_file_name="ResearchFolder.png"
        )
        trash_item = BinderItemData(
            uuid=UUIDManager.generate_uuid(),
            item_type="TrashFolder",
            title="Papelera",
            created=now_str,
            modified=now_str,
            include_in_compile=False,
            icon_file_name="TrashFolder.png"
        )

        project_data = {
            "version": "3.0",
            "creator": "Escritorio-1.0",
            "identifier": UUIDManager.generate_uuid(),
            "title": title,
            "binder": [draft_item, research_item, trash_item],
            "labels": {
                -1: LabelDefinition(-1, "Ninguna", "1.0 1.0 1.0 0.0"),
                1: LabelDefinition(1, "Concepto", "0.95 0.26 0.21 1.0"),
                2: LabelDefinition(2, "Capítulo", "0.13 0.59 0.95 1.0"),
                3: LabelDefinition(3, "Escena", "0.30 0.69 0.31 1.0")
            },
            "statuses": {
                -1: StatusDefinition(-1, "Ninguno"),
                1: StatusDefinition(1, "Por hacer"),
                2: StatusDefinition(2, "Primer borrador"),
                3: StatusDefinition(3, "Borrador revisado"),
                4: StatusDefinition(4, "Completado")
            },
            "section_types": {
                "Structure Based": "Según estructura",
                "Heading": "Encabezado",
                "Chapter": "Capítulo",
                "Scene": "Escena"
            },
            "targets": {
                "draft_words": 50000,
                "session_words": 1500
            },
            "collections": []
        }

        proj_file = path / f"{path.stem}{'.escrx' if native else '.scrivx'}"
        xml_content = ScrivenerXMLParser.generate_xml_string(project_data)
        AtomicStorage.write_atomic_text(proj_file, xml_content, encoding="utf-8")

        proj_instance = cls(path)
        proj_instance.acquire_lock()
        proj_instance.load()
        return proj_instance

    def load(self, force_unlock: bool = False):
        """Carga el proyecto completo desde el archivo maestro y mapea el Binder."""
        if not self.project_file.exists():
            raise FileNotFoundError(f"No se encontró el archivo maestro del proyecto: {self.project_file}")

        if not self._has_lock:
            self.acquire_lock(force=force_unlock)

        self.project_data = ScrivenerXMLParser.parse_xml_file(str(self.project_file))
        self.items_by_uuid.clear()
        self.root_items.clear()

        for item_data in self.project_data.get("binder", []):
            item = self._register_item_tree(item_data)
            self.root_items.append(item)

        # Configurar gestor de backups en ./portable_config/backups/ o ./config/backups/
        backups_dir = self.project_dir.parent / "config" / "backups"
        if not backups_dir.exists():
            backups_dir = self.project_dir.parent / "portable_config" / "backups"
        self.backup_manager = BackupManager(backups_dir)

    def _register_item_tree(self, item_data: BinderItemData) -> BinderItem:
        item = BinderItem(item_data, self)
        self.items_by_uuid[item.uuid] = item
        for child_data in item_data.children:
            self._register_item_tree(child_data)
        return item

    def get_item(self, uuid: str) -> Optional[BinderItem]:
        """Obtiene un nodo del Binder por su UUID."""
        return self.items_by_uuid.get(uuid)

    def add_item(self, parent_uuid: str, title: str, item_type: str = "Text") -> BinderItem:
        """Añade un nuevo nodo al árbol del Binder."""
        parent = self.get_item(parent_uuid)
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_data = BinderItemData(
            uuid=UUIDManager.generate_uuid(),
            item_type=item_type,
            title=title,
            created=now_str,
            modified=now_str
        )
        if parent:
            parent.data.children.append(new_data)
        else:
            self.project_data["binder"].append(new_data)

        new_item = self._register_item_tree(new_data)
        self.save_structure()
        return new_item

    # =========================================================================
    # Autoguardado Atómico y Persistencia
    # =========================================================================

    def autosave_pending_changes(self, inactivity_seconds: float = 2.0) -> int:
        """
        Recorre todos los documentos modificados; si han transcurrido más de
        'inactivity_seconds' (por defecto 2s) desde su última modificación,
        los persiste atómicamente a disco.
        """
        now = time.time()
        saved_count = 0
        for item in self.items_by_uuid.values():
            if item.is_dirty:
                if (now - item.last_modified_timestamp) >= inactivity_seconds:
                    if item.save_if_dirty():
                        saved_count += 1

        if saved_count > 0:
            self.save_structure()

        return saved_count

    def save_all(self):
        """Guarda forzosamente todos los documentos modificados y el índice maestro."""
        for item in self.items_by_uuid.values():
            item.save_if_dirty()
        self.save_structure()

    def save_structure(self):
        """Guarda de forma atómica el archivo maestro XML del proyecto."""
        xml_content = ScrivenerXMLParser.generate_xml_string(self.project_data)
        AtomicStorage.write_atomic_text(self.project_file, xml_content, encoding="utf-8")

    def perform_backup(self) -> Optional[Dict[str, Any]]:
        """Ejecuta una copia de seguridad empaquetada en ZIP verificando SHA-256."""
        if self.backup_manager:
            return self.backup_manager.create_project_backup(self.project_dir, self.project_data.get("title"))
        return None

    def close(self):
        """Cierra el proyecto, guardando cambios pendientes y liberando el cerrojo."""
        self.save_all()
        self.release_lock()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.release_lock()
