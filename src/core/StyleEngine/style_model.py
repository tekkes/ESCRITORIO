"""
Style Model para Escritorio StyleEngine
Define la estructura semántica de estilos de Scrivener 3:
- Estado por defecto "Sin Estilo" (No Style)
- Estilos de Párrafo, de Carácter y Mixtos (Combined)
- Serialización y deserialización a XML y atributos RTF.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List
import xml.etree.ElementTree as ET


class StyleType(str, Enum):
    NONE = "None"             # Sin Estilo (No Style)
    PARAGRAPH = "Paragraph"   # Afecta al bloque de párrafo
    CHARACTER = "Character"   # Afecta al tramo de caracteres
    COMBINED = "Combined"     # Afecta a párrafo y carácter simultáneamente


@dataclass
class StyleDefinition:
    """Definición semántica de un estilo de texto en Scrivener / Escritorio."""
    id: str
    name: str
    style_type: StyleType = StyleType.NONE
    shortcut: str = ""
    is_builtin: bool = False
    is_default: bool = False  # True para "Sin Estilo"

    # Tipografía y formato de carácter
    font_family: Optional[str] = None
    font_size: Optional[float] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    strikethrough: Optional[bool] = None
    superscript: Optional[bool] = None
    subscript: Optional[bool] = None
    text_color: Optional[str] = None         # Hex ej. #000000 o RGBA
    background_color: Optional[str] = None   # Color de resaltado / fondo

    # Geometría y formato de párrafo
    alignment: Optional[str] = None          # "left", "center", "right", "justify"
    line_spacing: Optional[float] = None     # 1.0, 1.15, 1.5, 2.0, etc.
    space_before: Optional[float] = None     # Puntos tipográficos
    space_after: Optional[float] = None      # Puntos tipográficos
    first_line_indent: Optional[float] = None # Sangría primera línea (pt)
    left_indent: Optional[float] = None      # Sangría izquierda (pt)
    right_indent: Optional[float] = None     # Sangría derecha (pt)

    # Metadatos adicionales
    custom_attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "style_type": self.style_type.value,
            "shortcut": self.shortcut,
            "is_builtin": self.is_builtin,
            "is_default": self.is_default,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "bold": self.bold,
            "italic": self.italic,
            "underline": self.underline,
            "strikethrough": self.strikethrough,
            "superscript": self.superscript,
            "subscript": self.subscript,
            "text_color": self.text_color,
            "background_color": self.background_color,
            "alignment": self.alignment,
            "line_spacing": self.line_spacing,
            "space_before": self.space_before,
            "space_after": self.space_after,
            "first_line_indent": self.first_line_indent,
            "left_indent": self.left_indent,
            "right_indent": self.right_indent,
            "custom_attributes": dict(self.custom_attributes)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StyleDefinition":
        st_val = data.get("style_type", "None")
        try:
            st = StyleType(st_val)
        except ValueError:
            st = StyleType.NONE

        return cls(
            id=data.get("id", ""),
            name=data.get("name", "Sin Estilo"),
            style_type=st,
            shortcut=data.get("shortcut", ""),
            is_builtin=data.get("is_builtin", False),
            is_default=data.get("is_default", False),
            font_family=data.get("font_family"),
            font_size=data.get("font_size"),
            bold=data.get("bold"),
            italic=data.get("italic"),
            underline=data.get("underline"),
            strikethrough=data.get("strikethrough"),
            superscript=data.get("superscript"),
            subscript=data.get("subscript"),
            text_color=data.get("text_color"),
            background_color=data.get("background_color"),
            alignment=data.get("alignment"),
            line_spacing=data.get("line_spacing"),
            space_before=data.get("space_before"),
            space_after=data.get("space_after"),
            first_line_indent=data.get("first_line_indent"),
            left_indent=data.get("left_indent"),
            right_indent=data.get("right_indent"),
            custom_attributes=data.get("custom_attributes", {})
        )

    def to_xml_element(self) -> ET.Element:
        elem = ET.Element("Style")
        elem.set("ID", self.id)
        elem.set("Name", self.name)
        elem.set("Type", self.style_type.value)
        if self.shortcut:
            elem.set("Shortcut", self.shortcut)
        if self.is_builtin:
            elem.set("BuiltIn", "Yes")
        if self.is_default:
            elem.set("IsDefault", "Yes")

        if self.font_family:
            ET.SubElement(elem, "FontFamily").text = self.font_family
        if self.font_size is not None:
            ET.SubElement(elem, "FontSize").text = str(self.font_size)
        if self.bold is not None:
            ET.SubElement(elem, "Bold").text = "Yes" if self.bold else "No"
        if self.italic is not None:
            ET.SubElement(elem, "Italic").text = "Yes" if self.italic else "No"
        if self.underline is not None:
            ET.SubElement(elem, "Underline").text = "Yes" if self.underline else "No"
        if self.strikethrough is not None:
            ET.SubElement(elem, "Strikethrough").text = "Yes" if self.strikethrough else "No"
        if self.superscript is not None:
            ET.SubElement(elem, "Superscript").text = "Yes" if self.superscript else "No"
        if self.subscript is not None:
            ET.SubElement(elem, "Subscript").text = "Yes" if self.subscript else "No"
        if self.text_color:
            ET.SubElement(elem, "TextColor").text = self.text_color
        if self.background_color:
            ET.SubElement(elem, "BackgroundColor").text = self.background_color
        if self.alignment:
            ET.SubElement(elem, "Alignment").text = self.alignment
        if self.line_spacing is not None:
            ET.SubElement(elem, "LineSpacing").text = str(self.line_spacing)
        if self.space_before is not None:
            ET.SubElement(elem, "SpaceBefore").text = str(self.space_before)
        if self.space_after is not None:
            ET.SubElement(elem, "SpaceAfter").text = str(self.space_after)
        if self.first_line_indent is not None:
            ET.SubElement(elem, "FirstLineIndent").text = str(self.first_line_indent)
        if self.left_indent is not None:
            ET.SubElement(elem, "LeftIndent").text = str(self.left_indent)
        if self.right_indent is not None:
            ET.SubElement(elem, "RightIndent").text = str(self.right_indent)

        return elem

    @classmethod
    def from_xml_element(cls, elem: ET.Element) -> "StyleDefinition":
        st_id = elem.get("ID", "")
        name = elem.get("Name", "Sin Estilo")
        st_type_str = elem.get("Type", "None")
        try:
            st_type = StyleType(st_type_str)
        except ValueError:
            st_type = StyleType.NONE

        shortcut = elem.get("Shortcut", "")
        is_builtin = elem.get("BuiltIn", "No").lower() in ("yes", "true", "1")
        is_default = elem.get("IsDefault", "No").lower() in ("yes", "true", "1") or (st_type == StyleType.NONE)

        def get_text(tag: str) -> Optional[str]:
            sub = elem.find(tag)
            return sub.text.strip() if (sub is not None and sub.text) else None

        def get_bool(tag: str) -> Optional[bool]:
            val = get_text(tag)
            if val is None:
                return None
            return val.lower() in ("yes", "true", "1")

        def get_float(tag: str) -> Optional[float]:
            val = get_text(tag)
            if val is None:
                return None
            try:
                return float(val)
            except ValueError:
                return None

        return cls(
            id=st_id,
            name=name,
            style_type=st_type,
            shortcut=shortcut,
            is_builtin=is_builtin,
            is_default=is_default,
            font_family=get_text("FontFamily"),
            font_size=get_float("FontSize"),
            bold=get_bool("Bold"),
            italic=get_bool("Italic"),
            underline=get_bool("Underline"),
            strikethrough=get_bool("Strikethrough"),
            superscript=get_bool("Superscript"),
            subscript=get_bool("Subscript"),
            text_color=get_text("TextColor"),
            background_color=get_text("BackgroundColor"),
            alignment=get_text("Alignment"),
            line_spacing=get_float("LineSpacing"),
            space_before=get_float("SpaceBefore"),
            space_after=get_float("SpaceAfter"),
            first_line_indent=get_float("FirstLineIndent"),
            left_indent=get_float("LeftIndent"),
            right_indent=get_float("RightIndent")
        )

    def to_rtf_tags(self) -> str:
        """Genera la secuencia de tokens de formato RTF asociados a este estilo."""
        if self.style_type == StyleType.NONE:
            return ""

        tags = []
        # Párrafo
        if self.style_type in (StyleType.PARAGRAPH, StyleType.COMBINED):
            if self.alignment == "center":
                tags.append(r"\qc")
            elif self.alignment == "right":
                tags.append(r"\qr")
            elif self.alignment == "justify":
                tags.append(r"\qj")
            elif self.alignment == "left":
                tags.append(r"\ql")

            if self.left_indent is not None:
                # 1 pt = 20 twips
                tags.append(rf"\li{int(self.left_indent * 20)}")
            if self.right_indent is not None:
                tags.append(rf"\ri{int(self.right_indent * 20)}")
            if self.first_line_indent is not None:
                tags.append(rf"\fi{int(self.first_line_indent * 20)}")
            if self.space_before is not None:
                tags.append(rf"\sb{int(self.space_before * 20)}")
            if self.space_after is not None:
                tags.append(rf"\sa{int(self.space_after * 20)}")
            if self.line_spacing is not None:
                # \sl240\slmult1 = 1.0 (240 twips = 12pt line)
                twips = int(self.line_spacing * 240)
                tags.append(rf"\sl{twips}\slmult1")

        # Carácter
        if self.style_type in (StyleType.CHARACTER, StyleType.COMBINED):
            if self.bold is True:
                tags.append(r"\b")
            elif self.bold is False:
                tags.append(r"\b0")

            if self.italic is True:
                tags.append(r"\i")
            elif self.italic is False:
                tags.append(r"\i0")

            if self.underline is True:
                tags.append(r"\ul")
            elif self.underline is False:
                tags.append(r"\ulnone")

            if self.strikethrough is True:
                tags.append(r"\strike")
            elif self.strikethrough is False:
                tags.append(r"\strike0")

            if self.superscript is True:
                tags.append(r"\super")
            elif self.subscript is True:
                tags.append(r"\sub")

            if self.font_size is not None:
                half_pts = int(self.font_size * 2)
                tags.append(rf"\fs{half_pts}")

        return "".join(tags)
