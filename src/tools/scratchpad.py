"""
Global Scratchpad Manager para Escritorio.
Bloc de notas flotante global e independiente para capturar ideas repentinas,
citas y fragmentos desde cualquier aplicación (accesible con Ctrl+Alt+Shift+S),
con capacidad de enviar notas directamente al documento activo o al Binder del proyecto.
"""

import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass, field
from ..core.storage_atomic import AtomicStorage
from ..core.project import EscritorioProject, BinderItem
from ..core.rtf_engine import RTFEngine


@dataclass
class ScratchpadNote:
    id: str
    title: str
    content: str
    created: str
    modified: str
    file_path: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created": self.created,
            "modified": self.modified,
            "file_path": self.file_path
        }


class ScratchpadManager:
    """Gestiona el Bloc de Notas Flotante Global (Ctrl+Alt+Shift+S)."""

    def __init__(self, storage_dir: Union[str, Path]):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.is_visible: bool = False
        self.active_note_id: Optional[str] = None

    def toggle_visibility(self) -> bool:
        """Atajo global de Windows Ctrl+Alt+Shift+S para mostrar/ocultar el Scratchpad."""
        self.is_visible = not self.is_visible
        return self.is_visible

    # =========================================================================
    # Operaciones con Notas
    # =========================================================================

    def create_note(self, title: str, content: str = "") -> ScratchpadNote:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).strip()
        if not safe_title:
            safe_title = f"Nota_{int(datetime.datetime.now().timestamp())}"

        fpath = self.storage_dir / f"{safe_title}.txt"
        AtomicStorage.write_atomic_text(fpath, content, encoding="utf-8")

        note = ScratchpadNote(
            id=safe_title,
            title=title,
            content=content,
            created=now_str,
            modified=now_str,
            file_path=str(fpath)
        )
        self.active_note_id = safe_title
        return note

    def get_note(self, note_id: str) -> Optional[ScratchpadNote]:
        fpath = self.storage_dir / f"{note_id}.txt"
        if not fpath.exists():
            return None

        content = AtomicStorage.read_text(fpath, encoding="utf-8")
        stat = fpath.stat()
        mod_str = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        cre_str = datetime.datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")

        return ScratchpadNote(
            id=note_id,
            title=fpath.stem,
            content=content,
            created=cre_str,
            modified=mod_str,
            file_path=str(fpath)
        )

    def update_note(self, note_id: str, new_content: str, new_title: Optional[str] = None) -> Optional[ScratchpadNote]:
        old_note = self.get_note(note_id)
        if not old_note:
            return None

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        target_path = Path(old_note.file_path)

        if new_title and new_title != old_note.title:
            safe_title = "".join(c for c in new_title if c.isalnum() or c in (' ', '_', '-')).strip()
            if safe_title:
                new_fpath = self.storage_dir / f"{safe_title}.txt"
                if target_path.exists() and new_fpath != target_path:
                    target_path.unlink()
                target_path = new_fpath
                note_id = safe_title

        AtomicStorage.write_atomic_text(target_path, new_content, encoding="utf-8")

        note = ScratchpadNote(
            id=note_id,
            title=new_title or old_note.title,
            content=new_content,
            created=old_note.created,
            modified=now_str,
            file_path=str(target_path)
        )
        self.active_note_id = note_id
        return note

    def delete_note(self, note_id: str) -> bool:
        fpath = self.storage_dir / f"{note_id}.txt"
        if fpath.exists():
            fpath.unlink()
            if self.active_note_id == note_id:
                self.active_note_id = None
            return True
        return False

    def list_notes(self) -> List[ScratchpadNote]:
        notes = []
        for p in self.storage_dir.glob("*.txt"):
            try:
                content = AtomicStorage.read_text(p, encoding="utf-8")
                stat = p.stat()
                mod_str = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                cre_str = datetime.datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                notes.append(ScratchpadNote(
                    id=p.stem,
                    title=p.stem,
                    content=content,
                    created=cre_str,
                    modified=mod_str,
                    file_path=str(p)
                ))
            except Exception:
                pass
        return sorted(notes, key=lambda n: n.modified, reverse=True)

    # =========================================================================
    # Enviar al Proyecto Activo (Send to Active Project)
    # =========================================================================

    def send_to_active_document(
        self,
        note_id: str,
        project: EscritorioProject,
        target_item_uuid: Optional[str] = None,
        destination: str = "text"
    ) -> bool:
        """
        Envía el contenido de la nota al proyecto:
        - destination="text": Anexa al texto principal (content.rtf) del documento.
        - destination="notes": Anexa a las notas del inspector (notes.rtf).
        - destination="new_document": Crea un nuevo documento en el Borrador con el título y contenido de la nota.
        """
        note = self.get_note(note_id)
        if not note:
            return False

        if destination == "new_document":
            draft = project.get_draft_folder()
            if not draft:
                return False
            new_item = project.add_item(draft.uuid, note.title, item_type="Text")
            rtf_content = RTFEngine.plain_text_to_rtf(note.content)
            new_item.write_content_rtf(rtf_content)
            new_item.save_if_dirty()
            project.save_structure()
            return True

        # Destino text o notes en documento existente
        target_item = None
        if target_item_uuid:
            target_item = project.get_item(target_item_uuid)
        else:
            # Primer documento de texto en el draft si no se especificó UUID
            draft = project.get_draft_folder()
            if draft and draft.children:
                target_item = draft.children[0]

        if not target_item:
            return False

        if destination == "notes":
            existing_notes_rtf = target_item.read_notes_rtf()
            existing_plain = RTFEngine.rtf_to_plain_text(existing_notes_rtf) if existing_notes_rtf else ""
            combined = f"{existing_plain}\n\n[Scratchpad: {note.title}]\n{note.content}".strip()
            target_item.write_notes_rtf(RTFEngine.plain_text_to_rtf(combined))
            target_item.save_if_dirty()
            return True
        else:
            # destination == "text"
            existing_rtf = target_item.read_content_rtf()
            existing_plain = RTFEngine.rtf_to_plain_text(existing_rtf) if existing_rtf else ""
            combined = f"{existing_plain}\n\n{note.content}".strip()
            target_item.write_content_rtf(RTFEngine.plain_text_to_rtf(combined))
            target_item.save_if_dirty()
            return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_visible": self.is_visible,
            "active_note_id": self.active_note_id,
            "notes_count": len(self.list_notes()),
            "storage_dir": str(self.storage_dir)
        }
