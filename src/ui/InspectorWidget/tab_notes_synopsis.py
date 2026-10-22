"""
Pestaña 1 del Inspector: Sinopsis y Notas (Notes & Synopsis)
- Parte superior: Tarjeta de sinopsis con botón para alternar entre Sinopsis de texto
  e Imagen de escena (con soporte drag-and-drop de imágenes)
- Parte inferior: Editor RTF de Notas del Documento (notes.rtf)
- Pie fijo del Inspector: Selectores rápidos de Label y Status
"""

from typing import Optional, Dict, Any
from pathlib import Path
from ...core.project import BinderItem, EscritorioProject


class TabNotesSynopsis:
    """Controlador de la Pestaña 1: Sinopsis, Imagen de Escena y Notas RTF."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.project: Optional[EscritorioProject] = project
        self.active_item: Optional[BinderItem] = None

        # Estado del modo imagen vs texto
        self.is_image_mode: bool = False
        self.image_path: Optional[str] = None

    def set_item(self, item: Optional[BinderItem]):
        self.active_item = item
        if not self.project and item and getattr(item, "project", None):
            self.project = item.project

        # Verificar si hay imagen asociada en el directorio del nodo
        if item and getattr(item, "project", None):
            data_dir = item.get_data_dir()
            img_candidates = list(data_dir.glob("synopsis_image.*"))
            if img_candidates:
                self.image_path = str(img_candidates[0])
                self.is_image_mode = True
            else:
                self.image_path = None
                self.is_image_mode = False
        else:
            self.image_path = None
            self.is_image_mode = False

    # =========================================================================
    # Sinopsis de Texto
    # =========================================================================

    def get_synopsis(self) -> str:
        if not self.active_item:
            return ""
        if getattr(self.active_item, "project", None):
            return self.active_item.read_synopsis()
        return getattr(self.active_item, "_dummy_synopsis", "")

    def set_synopsis(self, text: str) -> str:
        if not self.active_item:
            return ""
        if getattr(self.active_item, "project", None):
            self.active_item.write_synopsis(text)
            self.active_item.save_if_dirty()
        else:
            setattr(self.active_item, "_dummy_synopsis", text)
        return text

    # =========================================================================
    # Imagen de Escena (Soporte Drag-and-Drop)
    # =========================================================================

    def toggle_image_mode(self) -> bool:
        """Alterna entre vista de texto e imagen de escena."""
        self.is_image_mode = not self.is_image_mode
        return self.is_image_mode

    def set_scene_image(self, file_path: str) -> Optional[str]:
        """Asigna una imagen de escena a la tarjeta de sinopsis."""
        if not self.active_item or not getattr(self.active_item, "project", None):
            self.image_path = file_path
            self.is_image_mode = True
            return file_path

        p = Path(file_path)
        if not p.exists():
            return None

        # Guardar / enlazar en el directorio del nodo
        data_dir = self.active_item.get_data_dir()
        target_ext = p.suffix.lower() if p.suffix else ".png"
        target_img = data_dir / f"synopsis_image{target_ext}"

        # Eliminar imágenes previas
        for old_img in data_dir.glob("synopsis_image.*"):
            try:
                old_img.unlink()
            except OSError:
                pass

        try:
            target_img.write_bytes(p.read_bytes())
            self.image_path = str(target_img)
            self.is_image_mode = True
            return self.image_path
        except Exception:
            self.image_path = file_path
            self.is_image_mode = True
            return file_path

    def remove_scene_image(self):
        """Elimina la imagen asociada y regresa a sinopsis de texto."""
        if self.active_item and getattr(self.active_item, "project", None):
            data_dir = self.active_item.get_data_dir()
            for old_img in data_dir.glob("synopsis_image.*"):
                try:
                    old_img.unlink()
                except OSError:
                    pass
        self.image_path = None
        self.is_image_mode = False

    # =========================================================================
    # Editor RTF de Notas del Documento (notes.rtf)
    # =========================================================================

    def get_notes_rtf(self) -> str:
        if not self.active_item:
            return ""
        if getattr(self.active_item, "project", None):
            return self.active_item.read_notes_rtf()
        return getattr(self.active_item, "_dummy_notes", "")

    def set_notes_rtf(self, rtf_text: str) -> str:
        if not self.active_item:
            return ""
        if getattr(self.active_item, "project", None):
            self.active_item.write_notes_rtf(rtf_text)
            self.active_item.save_if_dirty()
        else:
            setattr(self.active_item, "_dummy_notes", rtf_text)
        return rtf_text

    # =========================================================================
    # Pie Fijo del Inspector: Selectores Rápidos de Label y Status
    # =========================================================================

    def set_label(self, label_id: int):
        if self.active_item and hasattr(self.active_item, "data"):
            self.active_item.data.label_id = label_id
            self.active_item.mark_dirty()
            if self.project:
                self.project.save_structure()

    def set_status(self, status_id: int):
        if self.active_item and hasattr(self.active_item, "data"):
            self.active_item.data.status_id = status_id
            self.active_item.mark_dirty()
            if self.project:
                self.project.save_structure()

    def get_footer_state(self) -> Dict[str, Any]:
        """Devuelve el estado de etiqueta y avance para el pie persistente."""
        lid = getattr(self.active_item.data, "label_id", -1) if self.active_item else -1
        sid = getattr(self.active_item.data, "status_id", -1) if self.active_item else -1
        return {
            "label_id": lid,
            "status_id": sid
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_image_mode": self.is_image_mode,
            "image_path": self.image_path,
            "synopsis": self.get_synopsis(),
            "notes_rtf": self.get_notes_rtf(),
            "footer": self.get_footer_state()
        }
