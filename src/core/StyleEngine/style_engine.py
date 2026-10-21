"""
StyleEngine para Escritorio
Gestor central del sistema de estilos semánticos de Scrivener 3.
- Estado por defecto "Sin Estilo" (No Style)
- Presets canónicos (Título 1, Título 2, Cita en bloque, Epígrafe, Código, Verso)
- Creación y redefinición interactiva desde selecciones de texto
- Persistencia atómica en Settings/styles.xml del paquete de proyecto.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import xml.etree.ElementTree as ET
import xml.dom.minidom

from .style_model import StyleDefinition, StyleType
from ..storage_atomic import AtomicStorage


class StyleEngine:
    """Motor de gestión de estilos semánticos."""

    DEFAULT_STYLE_ID = "style-no-style"

    def __init__(self, project_dir: Optional[Path] = None):
        self.project_dir = Path(project_dir).resolve() if project_dir else None
        self._styles: Dict[str, StyleDefinition] = {}
        self._initialize_builtin_styles()
        if self.project_dir:
            self.load()

    def _initialize_builtin_styles(self):
        """Inicializa los estilos predefinidos estándar de Scrivener."""
        # 1. Sin Estilo (No Style) - Default absoluto
        no_style = StyleDefinition(
            id=self.DEFAULT_STYLE_ID,
            name="Sin Estilo",
            style_type=StyleType.NONE,
            shortcut="Ctrl+0",
            is_builtin=True,
            is_default=True
        )
        self._styles[no_style.id] = no_style

        # 2. Título 1 (Heading 1)
        h1 = StyleDefinition(
            id="style-heading-1",
            name="Título 1",
            style_type=StyleType.PARAGRAPH,
            shortcut="Ctrl+Alt+1",
            is_builtin=True,
            font_size=18.0,
            bold=True,
            alignment="left",
            space_before=14.0,
            space_after=6.0,
            line_spacing=1.15
        )
        self._styles[h1.id] = h1

        # 3. Título 2 (Heading 2)
        h2 = StyleDefinition(
            id="style-heading-2",
            name="Título 2",
            style_type=StyleType.PARAGRAPH,
            shortcut="Ctrl+Alt+2",
            is_builtin=True,
            font_size=14.0,
            bold=True,
            alignment="left",
            space_before=10.0,
            space_after=4.0,
            line_spacing=1.15
        )
        self._styles[h2.id] = h2

        # 4. Cita en bloque (Block Quote)
        blockquote = StyleDefinition(
            id="style-block-quote",
            name="Cita en bloque",
            style_type=StyleType.COMBINED,
            shortcut="Ctrl+Alt+Q",
            is_builtin=True,
            italic=True,
            left_indent=36.0,
            right_indent=36.0,
            space_before=6.0,
            space_after=6.0,
            line_spacing=1.15
        )
        self._styles[blockquote.id] = blockquote

        # 5. Epígrafe (Epigraph)
        epigraph = StyleDefinition(
            id="style-epigraph",
            name="Epígrafe",
            style_type=StyleType.COMBINED,
            shortcut="Ctrl+Alt+E",
            is_builtin=True,
            italic=True,
            left_indent=72.0,
            right_indent=20.0,
            alignment="right",
            space_before=4.0,
            space_after=12.0,
            line_spacing=1.15
        )
        self._styles[epigraph.id] = epigraph

        # 6. Código (Code)
        code = StyleDefinition(
            id="style-code",
            name="Código",
            style_type=StyleType.CHARACTER,
            shortcut="Ctrl+Alt+C",
            is_builtin=True,
            font_family="Consolas",
            font_size=10.0,
            background_color="#F2F2F2"
        )
        self._styles[code.id] = code

        # 7. Verso (Verse)
        verse = StyleDefinition(
            id="style-verse",
            name="Verso",
            style_type=StyleType.PARAGRAPH,
            shortcut="Ctrl+Alt+V",
            is_builtin=True,
            italic=True,
            left_indent=24.0,
            space_before=2.0,
            space_after=2.0,
            line_spacing=1.0
        )
        self._styles[verse.id] = verse

    def get_styles_file(self) -> Optional[Path]:
        if not self.project_dir:
            return None
        return self.project_dir / "Settings" / "styles.xml"

    def get_default_style(self) -> StyleDefinition:
        """Devuelve el estilo por defecto 'Sin Estilo'."""
        return self._styles.get(self.DEFAULT_STYLE_ID, list(self._styles.values())[0])

    def get_style(self, style_id: str) -> Optional[StyleDefinition]:
        return self._styles.get(style_id)

    def get_style_by_name(self, name: str) -> Optional[StyleDefinition]:
        name_clean = name.strip().lower()
        for s in self._styles.values():
            if s.name.strip().lower() == name_clean:
                return s
        return None

    def list_styles(self) -> List[StyleDefinition]:
        """Devuelve la lista ordenada de estilos con 'Sin Estilo' siempre al principio."""
        default = self.get_default_style()
        others = [s for s in self._styles.values() if s.id != default.id]
        others.sort(key=lambda x: (not x.is_builtin, x.name.lower()))
        return [default] + others

    def create_style_from_selection(
        self,
        name: str,
        style_type: StyleType,
        attributes: Dict[str, Any],
        shortcut: str = ""
    ) -> StyleDefinition:
        """
        Crea un nuevo estilo semántico a partir del formato extraído de la selección activa.
        """
        import uuid
        style_id = f"style-{uuid.uuid4().hex[:8]}"
        new_style = StyleDefinition(
            id=style_id,
            name=name.strip(),
            style_type=style_type,
            shortcut=shortcut.strip(),
            is_builtin=False,
            is_default=False,
            font_family=attributes.get("font_family"),
            font_size=attributes.get("font_size"),
            bold=attributes.get("bold"),
            italic=attributes.get("italic"),
            underline=attributes.get("underline"),
            strikethrough=attributes.get("strikethrough"),
            superscript=attributes.get("superscript"),
            subscript=attributes.get("subscript"),
            text_color=attributes.get("text_color"),
            background_color=attributes.get("background_color"),
            alignment=attributes.get("alignment"),
            line_spacing=attributes.get("line_spacing"),
            space_before=attributes.get("space_before"),
            space_after=attributes.get("space_after"),
            first_line_indent=attributes.get("first_line_indent"),
            left_indent=attributes.get("left_indent"),
            right_indent=attributes.get("right_indent"),
            custom_attributes=attributes.get("custom_attributes", {})
        )

        self._styles[new_style.id] = new_style
        self.save()
        return new_style

    def redefine_style_from_selection(
        self,
        style_id: str,
        new_attributes: Dict[str, Any]
    ) -> Optional[StyleDefinition]:
        """
        Redefine los parámetros de un estilo existente manteniendo su ID y semántica.
        """
        target = self.get_style(style_id)
        if not target or target.style_type == StyleType.NONE:
            return None

        # Actualizar campos no nulos de new_attributes
        for attr, val in new_attributes.items():
            if hasattr(target, attr) and attr not in ("id", "is_builtin", "is_default"):
                setattr(target, attr, val)

        self.save()
        return target

    def delete_style(self, style_id: str) -> bool:
        """Elimina un estilo de usuario. 'Sin Estilo' nunca puede ser eliminado."""
        if style_id == self.DEFAULT_STYLE_ID:
            return False
        style = self._styles.get(style_id)
        if not style or style.is_builtin:
            return False
        del self._styles[style_id]
        self.save()
        return True

    # =========================================================================
    # Persistencia XML (Settings/styles.xml)
    # =========================================================================

    def load(self):
        """Carga los estilos guardados desde Settings/styles.xml si existe."""
        sfile = self.get_styles_file()
        if not sfile or not sfile.exists():
            return

        try:
            tree = ET.parse(sfile)
            root = tree.getroot()
            for child in root.findall("Style"):
                style = StyleDefinition.from_xml_element(child)
                self._styles[style.id] = style
        except Exception:
            # Si el archivo está dañado, se conservan los estilos incorporados
            pass

    def save(self):
        """Guarda todos los estilos en Settings/styles.xml usando AtomicStorage."""
        sfile = self.get_styles_file()
        if not sfile:
            return

        root = ET.Element("Styles")
        root.set("Version", "1.0")
        root.set("Creator", "Escritorio-StyleEngine")

        for s in self.list_styles():
            root.append(s.to_xml_element())

        raw_xml = ET.tostring(root, encoding="utf-8")
        parsed = xml.dom.minidom.parseString(raw_xml)
        pretty_xml = parsed.toprettyxml(indent="    ", encoding="utf-8").decode("utf-8")

        sfile.parent.mkdir(parents=True, exist_ok=True)
        AtomicStorage.write_atomic_text(sfile, pretty_xml, encoding="utf-8")
