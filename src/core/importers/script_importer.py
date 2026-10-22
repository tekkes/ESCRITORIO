"""
Importador de Guiones Cinematográficos y Teatrales (.fdx y .fountain) para Escritorio.
Parsea archivos de guion y los divide automáticamente por encabezados de escena (Scene Headings),
creando un nodo de texto en el Binder por cada escena con su diálogo, acción y personajes formateados:
- Soporte nativo para Final Draft XML (.fdx).
- Soporte para guiones en formato Fountain (.fountain).
- Extracción opcional de personajes y localizaciones para la carpeta de Investigación (Research).
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union, List, Dict, Any, Optional, Tuple

from ..project import EscritorioProject, BinderItem
from ..rtf_engine import RTFEngine


class ScriptScene:
    """Representa una escena de guion parseada."""
    def __init__(self, heading: str, body: str, scene_number: Optional[str] = None):
        self.heading = heading.strip()
        self.body = body.strip()
        self.scene_number = scene_number
        self.characters: List[str] = []


class ScriptImporter:
    """Importador y conversor de guiones a la estructura de escenas del Binder."""

    SCENE_HEADING_PATTERN = re.compile(
        r"^(?:\.?(?:INT|EXT|INT\./EXT|EXT\./INT|EST|I/E)\.?\b.*)$",
        re.IGNORECASE
    )

    @classmethod
    def import_script(
        cls,
        source_path: Union[str, Path],
        project: EscritorioProject,
        parent_uuid: Optional[str] = None,
        extract_characters_to_research: bool = True
    ) -> Dict[str, Any]:
        """
        Importa un archivo .fdx o .fountain y divide las escenas en el Binder.
        """
        path = Path(source_path)
        if not path.exists():
            raise FileNotFoundError(f"Archivo de guion no encontrado: {path}")

        # Determinar carpeta de destino en el Binder
        if not parent_uuid:
            draft = project.get_draft_folder()
            target_uuid = draft.uuid if draft else (project.root_items[0].uuid if project.root_items else "")
        else:
            target_uuid = parent_uuid

        ext = path.suffix.lower()
        if ext == ".fdx":
            scenes, script_title = cls._parse_fdx(path)
        elif ext in (".fountain", ".spmd"):
            scenes, script_title = cls._parse_fountain(path)
        else:
            # Intentar detectar XML vs Fountain por contenido
            content = path.read_text(encoding="utf-8", errors="ignore")
            if "<FinalDraft" in content:
                scenes, script_title = cls._parse_fdx(path)
            else:
                scenes, script_title = cls._parse_fountain(path)

        if not scenes:
            return {"success": False, "message": "No se encontraron escenas en el guion.", "items": []}

        # Crear carpeta contenedora para el guion si son varias escenas
        folder_title = script_title or path.stem
        script_folder = project.add_item(
            parent_uuid=target_uuid,
            title=folder_title,
            item_type="Folder"
        )

        all_characters = set()
        created_items: List[BinderItem] = [script_folder]

        for idx, scene in enumerate(scenes, 1):
            title = scene.heading or f"Escena {idx}"
            scene_item = project.add_item(
                parent_uuid=script_folder.uuid,
                title=title,
                item_type="Text"
            )

            # Escribir contenido RTF de la escena
            scene_rtf = RTFEngine.plain_text_to_rtf(scene.body, font_name="Courier New", font_size_pt=12)
            scene_item.write_content_rtf(scene_rtf)

            # Guardar encabezado en la sinopsis
            scene_item.write_synopsis(f"Encabezado: {scene.heading}")
            created_items.append(scene_item)

            for char in scene.characters:
                all_characters.add(char)

        # Opcional: Crear fichas de personajes en la carpeta Research
        if extract_characters_to_research and all_characters:
            research_folder = project.get_research_folder()
            if research_folder:
                chars_folder = project.add_item(
                    parent_uuid=research_folder.uuid,
                    title=f"Personajes - {folder_title}",
                    item_type="Folder"
                )
                created_items.append(chars_folder)

                for char_name in sorted(all_characters):
                    char_item = project.add_item(
                        parent_uuid=chars_folder.uuid,
                        title=char_name.title(),
                        item_type="Text"
                    )
                    char_bio = f"Ficha de Personaje: {char_name}\nGuion: {folder_title}\n\nDescripción:\n"
                    char_item.write_content_rtf(RTFEngine.plain_text_to_rtf(char_bio))
                    created_items.append(char_item)

        project.save_all()

        return {
            "success": True,
            "script_title": folder_title,
            "scenes_count": len(scenes),
            "characters_found": sorted(list(all_characters)),
            "created_items": created_items
        }

    # =========================================================================
    # PARSER FINAL DRAFT XML (.FDX)
    # =========================================================================

    @classmethod
    def _parse_fdx(cls, fdx_path: Path) -> Tuple[List[ScriptScene], str]:
        """Extrae escenas, párrafos y tipos semánticos desde un XML de Final Draft."""
        try:
            tree = ET.parse(str(fdx_path))
            root = tree.getroot()
        except Exception:
            return [], ""

        # Extraer título si existe en TitlePage
        script_title = ""
        title_elem = root.find(".//TitlePage/Content/Paragraph[1]/Text")
        if title_elem is not None and title_elem.text:
            script_title = title_elem.text.strip()

        content = root.find("Content")
        if content is None:
            return [], script_title

        scenes: List[ScriptScene] = []
        current_heading = ""
        current_lines: List[str] = []
        current_chars: List[str] = []

        for p in content.findall("Paragraph"):
            p_type = p.attrib.get("Type", "Action")
            # Extraer todo el texto del párrafo
            p_text = "".join(t.text for t in p.findall("Text") if t.text).strip()
            if not p_text:
                continue

            if p_type == "Scene Heading":
                has_content = any(l.strip() for l in current_lines)
                if current_heading or has_content:
                    scene_body = "\n".join(current_lines).strip()
                    s = ScriptScene(current_heading or "INICIO", scene_body)
                    s.characters = list(current_chars)
                    scenes.append(s)
                    current_lines = []
                    current_chars = []

                current_heading = p_text
                current_lines.append(p_text.upper())
            else:
                if p_type == "Character":
                    current_chars.append(p_text.upper())
                    current_lines.append(f"\n{p_text.upper()}")
                elif p_type == "Parenthetical":
                    current_lines.append(f"({p_text.strip('()')})")
                elif p_type == "Dialogue":
                    current_lines.append(f"    {p_text}")
                elif p_type == "Transition":
                    current_lines.append(f"\n> {p_text.upper()}\n")
                else:  # Action / Shot / General
                    current_lines.append(f"{p_text}")

        # Guardar última escena
        has_content = any(l.strip() for l in current_lines)
        if current_heading or has_content:
            s = ScriptScene(current_heading or "FINAL", "\n".join(current_lines).strip())
            s.characters = list(current_chars)
            scenes.append(s)

        return scenes, script_title

    # =========================================================================
    # PARSER FOUNTAIN (.FOUNTAIN)
    # =========================================================================

    @classmethod
    def _parse_fountain(cls, fountain_path: Path) -> Tuple[List[ScriptScene], str]:
        """Extrae escenas, personajes y texto desde un archivo de sintaxis Fountain."""
        content = fountain_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")

        script_title = ""
        title_match = re.search(r"^Title:\s*(.+)$", content, re.MULTILINE | re.IGNORECASE)
        if title_match:
            script_title = title_match.group(1).strip()

        scenes: List[ScriptScene] = []
        current_heading = ""
        current_lines: List[str] = []
        current_chars: List[str] = []

        in_title_page = True

        for line in lines:
            stripped = line.strip()

            # Saltear bloque de página de título inicial
            if in_title_page:
                if stripped == "===":
                    in_title_page = False
                    continue
                if stripped.lower().startswith(("title:", "credit:", "author:", "draft date:", "contact:")):
                    continue
                if stripped:
                    in_title_page = False

            if not stripped:
                current_lines.append("")
                continue

            # Detección de Scene Heading
            if cls.SCENE_HEADING_PATTERN.match(stripped):
                has_content = any(l.strip() for l in current_lines)
                if current_heading or has_content:
                    s = ScriptScene(current_heading or "INICIO", "\n".join(current_lines).strip())
                    s.characters = list(current_chars)
                    scenes.append(s)
                    current_lines = []
                    current_chars = []

                clean_heading = stripped[1:].strip() if stripped.startswith(".") else stripped
                current_heading = clean_heading
                current_lines.append(clean_heading.upper())
            else:
                # Detección de Personaje (línea mayúsculas corta)
                if stripped.isupper() and len(stripped) < 35 and not stripped.endswith((".", ",", ":")):
                    current_chars.append(stripped)
                current_lines.append(stripped)

        has_content = any(l.strip() for l in current_lines)
        if current_heading or has_content:
            s = ScriptScene(current_heading or "FINAL", "\n".join(current_lines).strip())
            s.characters = list(current_chars)
            scenes.append(s)

        return scenes, script_title
