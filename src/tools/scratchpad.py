"""
Scratchpad Manager para Escritorio
Bloc de notas rápido global e independiente para capturar ideas repentinas,
citas y fragmentos, con capacidad de enviarlos directamente al Binder del proyecto.
"""

from pathlib import Path
from typing import List, Dict, Optional, Union
from ..core.storage_atomic import AtomicStorage

class ScratchpadManager:
    """Gestiona notas efímeras de escritura rápida."""

    def __init__(self, storage_dir: Union[str, Path]):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_scratch_note(self, title: str, text_content: str) -> Path:
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).rstrip()
        fpath = self.storage_dir / f"{safe_title}.txt"
        AtomicStorage.write_atomic_text(fpath, text_content, encoding="utf-8")
        return fpath

    def list_notes(self) -> List[Dict[str, str]]:
        notes = []
        for p in self.storage_dir.glob("*.txt"):
            notes.append({
                "title": p.stem,
                "content": AtomicStorage.read_text(p, encoding="utf-8"),
                "path": str(p)
            })
        return notes
