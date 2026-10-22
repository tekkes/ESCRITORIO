"""
Pestaña 5 del Inspector: Comentarios y Notas al Pie (Comments & Footnotes)
- Lista interactiva de comentarios enlazados a selecciones de texto (con color, autor y marca de tiempo)
- Notas al pie del Inspector (Footnotes)
- Interactividad bidireccional: clic en comentario navega al editor y viceversa
- Persistencia transparente en Files/Data/<UUID>/content.comments (XML Scrivener)
"""

import xml.etree.ElementTree as ET
import datetime
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from ...core.project import BinderItem, EscritorioProject


@dataclass
class CommentItem:
    id: str
    item_type: str = "Comment"  # "Comment" o "Footnote"
    color_hex: str = "#FBBF24"  # Amarillo cálido por defecto
    author: str = "Escritor"
    date: str = ""
    text: str = ""
    start_offset: int = 0
    length: int = 0
    quote: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "item_type": self.item_type,
            "color_hex": self.color_hex,
            "author": self.author,
            "date": self.date,
            "text": self.text,
            "start_offset": self.start_offset,
            "length": self.length,
            "quote": self.quote
        }


class TabCommentsFootnotes:
    """Controlador de la Pestaña 5: Comentarios interactivos y Notas al pie."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.project: Optional[EscritorioProject] = project
        self.active_item: Optional[BinderItem] = None

        self.comments: List[CommentItem] = []
        self.selected_item_id: Optional[str] = None

    def set_item(self, item: Optional[BinderItem]):
        self.active_item = item
        if not self.project and item and getattr(item, "project", None):
            self.project = item.project
        self.selected_item_id = None
        self.load_comments_from_xml()

    # =========================================================================
    # Carga y Serialización en content.comments
    # =========================================================================

    def load_comments_from_xml(self):
        """Carga y parsea el archivo XML content.comments del documento activo."""
        self.comments.clear()
        if not self.active_item or not getattr(self.active_item, "project", None):
            return

        xml_content = self.active_item.read_comments_xml()
        if not xml_content or not xml_content.strip():
            return

        try:
            root = ET.fromstring(xml_content)
            for node in root.findall("Comment"):
                cid = node.get("ID", f"c_{len(self.comments)+1}")
                ctype = node.get("Type", "Comment")
                col = node.get("Color", "#FBBF24")
                author = node.get("Author", "Escritor")
                date = node.get("Date", "")
                text_elem = node.find("Text")
                text = text_elem.text if text_elem is not None and text_elem.text else ""

                rng = node.find("Range")
                start = int(rng.get("Start", 0)) if rng is not None else 0
                length = int(rng.get("Length", 0)) if rng is not None else 0
                quote = rng.get("Quote", "") if rng is not None else ""

                c = CommentItem(
                    id=cid,
                    item_type=ctype,
                    color_hex=col,
                    author=author,
                    date=date,
                    text=text,
                    start_offset=start,
                    length=length,
                    quote=quote
                )
                self.comments.append(c)
        except Exception:
            pass

    def save_comments_to_xml(self):
        """Genera el XML Scrivener compatible y lo persiste de forma atómica."""
        if not self.active_item or not getattr(self.active_item, "project", None):
            return

        root = ET.Element("Comments", {"Version": "1.0"})
        for c in self.comments:
            c_elem = ET.SubElement(root, "Comment", {
                "ID": c.id,
                "Type": c.item_type,
                "Color": c.color_hex,
                "Author": c.author,
                "Date": c.date
            })
            t_elem = ET.SubElement(c_elem, "Text")
            t_elem.text = c.text

            ET.SubElement(c_elem, "Range", {
                "Start": str(c.start_offset),
                "Length": str(c.length),
                "Quote": c.quote
            })

        xml_str = ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
        self.active_item.write_comments_xml(xml_str)
        self.active_item.save_if_dirty()

    # =========================================================================
    # Adición, Edición y Eliminación de Comentarios
    # =========================================================================

    def add_comment(
        self,
        text: str,
        start_offset: int = 0,
        length: int = 0,
        quote: str = "",
        author: str = "Escritor",
        color_hex: str = "#FBBF24"
    ) -> CommentItem:
        """Añade un comentario enlazado a un fragmento del texto."""
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cid = f"comm_{int(datetime.datetime.now().timestamp()*1000)}"

        c = CommentItem(
            id=cid,
            item_type="Comment",
            color_hex=color_hex,
            author=author,
            date=now_str,
            text=text,
            start_offset=start_offset,
            length=length,
            quote=quote
        )
        self.comments.append(c)
        self.selected_item_id = cid
        self.save_comments_to_xml()
        return c

    def add_footnote(
        self,
        text: str,
        start_offset: int = 0,
        length: int = 0,
        quote: str = "",
        author: str = "Escritor"
    ) -> CommentItem:
        """Añade una nota al pie del Inspector."""
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fid = f"fn_{int(datetime.datetime.now().timestamp()*1000)}"

        fn = CommentItem(
            id=fid,
            item_type="Footnote",
            color_hex="#94A3B8",
            author=author,
            date=now_str,
            text=text,
            start_offset=start_offset,
            length=length,
            quote=quote
        )
        self.comments.append(fn)
        self.selected_item_id = fid
        self.save_comments_to_xml()
        return fn

    def update_comment_text(self, item_id: str, new_text: str) -> bool:
        c = next((x for x in self.comments if x.id == item_id), None)
        if c:
            c.text = new_text
            self.save_comments_to_xml()
            return True
        return False

    def remove_item(self, item_id: str):
        self.comments = [x for x in self.comments if x.id != item_id]
        if self.selected_item_id == item_id:
            self.selected_item_id = None
        self.save_comments_to_xml()

    # =========================================================================
    # Navegación e Interactividad Bidireccional
    # =========================================================================

    def select_comment(self, item_id: str) -> Optional[Tuple[int, int]]:
        """
        Al hacer clic en un comentario en el Inspector,
        devuelve el rango (start_offset, length) para que el editor se desplace y resalte el texto.
        """
        self.selected_item_id = item_id
        c = next((x for x in self.comments if x.id == item_id), None)
        if c:
            return (c.start_offset, c.length)
        return None

    def find_comment_at_offset(self, cursor_offset: int) -> Optional[CommentItem]:
        """
        Cuando el cursor se mueve en el editor,
        localiza si coincide con un comentario o nota al pie existente para resaltarlo.
        """
        for c in self.comments:
            if c.start_offset <= cursor_offset <= (c.start_offset + c.length):
                self.selected_item_id = c.id
                return c
        return None

    def get_comments_only(self) -> List[CommentItem]:
        return [c for c in self.comments if c.item_type == "Comment"]

    def get_footnotes_only(self) -> List[CommentItem]:
        return [c for c in self.comments if c.item_type == "Footnote"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_count": len(self.comments),
            "selected_id": self.selected_item_id,
            "comments": [c.to_dict() for c in self.comments]
        }
