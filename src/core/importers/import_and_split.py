"""
Motor de Importación y División Avanzada (Import and Split) para Escritorio.
Permite importar manuscritos lineales largos desde .docx, .rtf, .txt o .md
y dividirlos automáticamente en capítulos y escenas en el Binder:
- Detección de estilos de encabezado (Heading 1, Heading 2, Heading 3).
- Detección de separadores explícitos (#, ##, ***, * * *, ---, o cadenas personalizadas).
- Creación de jerarquía automática (Carpetas para Nivel 1 y Documentos de Texto para Nivel 2).
"""

import os
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union, List, Dict, Any, Optional, Tuple

from ..project import EscritorioProject, BinderItem
from ..rtf_engine import RTFEngine


class SectionUnit:
    """Representa una unidad de texto detectada para la importación."""
    def __init__(self, title: str, content: str, level: int = 1):
        self.title = title.strip() or f"Sección Nivel {level}"
        self.content = content.strip()
        self.level = level
        self.children: List['SectionUnit'] = []


class ImportAndSplit:
    """Importador y divisor estructural de manuscritos."""

    # Namespace estándar de OpenXML WordprocessingML
    WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

    @classmethod
    def import_and_split(
        cls,
        source_path: Union[str, Path],
        project: EscritorioProject,
        parent_uuid: Optional[str] = None,
        separator: Optional[str] = None,
        detect_headings: bool = True
    ) -> Dict[str, Any]:
        """
        Importa un archivo largo, lo divide y crea los nodos correspondientes en el Binder.
        """
        # Permitir argumentos en orden (source_path, project) o (project, source_path)
        if hasattr(source_path, "get_draft_folder") or hasattr(source_path, "project_dir"):
            source_path, project = project, source_path

        path = Path(source_path)
        if not path.exists():
            raise FileNotFoundError(f"Archivo de origen no encontrado: {path}")

        # Determinar carpeta de destino en el Binder
        if not parent_uuid:
            draft = project.get_draft_folder()
            if draft:
                target_uuid = draft.uuid
            else:
                target_uuid = project.root_items[0].uuid if project.root_items else ""
        else:
            target_uuid = parent_uuid

        # 1. Parsear el archivo según su formato y extraer unidades seccionales
        ext = path.suffix.lower()
        if ext == ".docx":
            units = cls._parse_docx(path, separator, detect_headings)
        elif ext == ".rtf":
            units = cls._parse_rtf(path, separator, detect_headings)
        elif ext in (".md", ".markdown"):
            units = cls._parse_markdown(path, separator, detect_headings)
        else:  # .txt o cualquier texto plano
            units = cls._parse_text(path, separator, detect_headings)

        if not units:
            # Fallback: importar el archivo completo como un solo documento
            content = path.read_text(encoding="utf-8", errors="ignore")
            units = [SectionUnit(title=path.stem, content=content, level=1)]

        # 2. Insertar las unidades en el Binder de forma jerárquica
        created_items: List[BinderItem] = []
        created_folders = 0
        created_texts = 0

        for unit in units:
            items_res = cls._insert_unit(project, target_uuid, unit)
            for it in items_res:
                created_items.append(it)
                if it.item_type == "Folder":
                    created_folders += 1
                else:
                    created_texts += 1

        project.save_all()

        return {
            "success": True,
            "source_file": str(path),
            "total_items": len(created_items),
            "folders_created": created_folders,
            "texts_created": created_texts,
            "items": created_items
        }

    # =========================================================================
    # PARSERS POR FORMATO
    # =========================================================================

    @classmethod
    def _parse_docx(
        cls,
        docx_path: Path,
        separator: Optional[str],
        detect_headings: bool
    ) -> List[SectionUnit]:
        """Extrae texto y estilos de encabezado desde document.xml de un .docx."""
        try:
            with zipfile.ZipFile(docx_path, "r") as zf:
                if "word/document.xml" not in zf.namelist():
                    return []
                xml_data = zf.read("word/document.xml")
        except Exception:
            return []

        root = ET.fromstring(xml_data)
        paragraphs_data: List[Tuple[str, str, int]] = []  # (text, style, level)

        for p in root.iter(f"{{{cls.WORD_NS['w']}}}p"):
            # Obtener texto del párrafo
            p_text = "".join(t.text for t in p.iter(f"{{{cls.WORD_NS['w']}}}t") if t.text).strip()
            if not p_text:
                continue

            # Obtener estilo
            pPr = p.find(f"{{{cls.WORD_NS['w']}}}pPr")
            style_name = ""
            if pPr is not None:
                pStyle = pPr.find(f"{{{cls.WORD_NS['w']}}}pStyle")
                if pStyle is not None:
                    style_name = pStyle.attrib.get(f"{{{cls.WORD_NS['w']}}}val", "")

            level = 0
            if detect_headings and style_name:
                style_lower = style_name.lower()
                if "heading1" in style_lower or "heading 1" in style_lower or "titre1" in style_lower:
                    level = 1
                elif "heading2" in style_lower or "heading 2" in style_lower or "titre2" in style_lower:
                    level = 2
                elif "heading3" in style_lower or "heading 3" in style_lower or "titre3" in style_lower:
                    level = 3

            paragraphs_data.append((p_text, style_name, level))

        # Si hay separador explícito
        if separator:
            return cls._split_by_separator([p[0] for p in paragraphs_data], separator)

        # Si se detectaron encabezados Heading 1 o Heading 2
        has_headings = any(p[2] > 0 for p in paragraphs_data)
        if has_headings and detect_headings:
            return cls._build_hierarchy_from_paragraphs(paragraphs_data)

        # Si no hay encabezados, dividir por patrones de capítulo o página
        full_text = "\n\n".join(p[0] for p in paragraphs_data)
        return cls._split_by_common_patterns(full_text)

    @classmethod
    def _parse_rtf(
        cls,
        rtf_path: Path,
        separator: Optional[str],
        detect_headings: bool
    ) -> List[SectionUnit]:
        """Lee archivo RTF y extrae su texto plano para dividirlo."""
        raw_rtf = rtf_path.read_text(encoding="utf-8", errors="ignore")
        plain_text = RTFEngine.rtf_to_plain_text(raw_rtf)

        if separator:
            return cls._split_text_by_separator(plain_text, separator)
        return cls._split_by_common_patterns(plain_text, detect_headings)

    @classmethod
    def _parse_markdown(
        cls,
        md_path: Path,
        separator: Optional[str],
        detect_headings: bool
    ) -> List[SectionUnit]:
        """Divide documentos Markdown por encabezados (#, ##) o separadores."""
        text = md_path.read_text(encoding="utf-8", errors="ignore")

        if separator:
            return cls._split_text_by_separator(text, separator)

        if detect_headings:
            lines = text.split("\n")
            paragraphs_data: List[Tuple[str, str, int]] = []

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("# "):
                    paragraphs_data.append((stripped[2:].strip(), "Heading 1", 1))
                elif stripped.startswith("## "):
                    paragraphs_data.append((stripped[3:].strip(), "Heading 2", 2))
                elif stripped.startswith("### "):
                    paragraphs_data.append((stripped[4:].strip(), "Heading 3", 3))
                else:
                    paragraphs_data.append((stripped, "Normal", 0))

            has_h = any(p[2] > 0 for p in paragraphs_data)
            if has_h:
                return cls._build_hierarchy_from_paragraphs(paragraphs_data)

        return cls._split_by_common_patterns(text, detect_headings)

    @classmethod
    def _parse_text(
        cls,
        txt_path: Path,
        separator: Optional[str],
        detect_headings: bool
    ) -> List[SectionUnit]:
        """Divide texto plano general por separador o patrones de capítulo."""
        text = txt_path.read_text(encoding="utf-8", errors="ignore")
        if separator:
            return cls._split_text_by_separator(text, separator)
        return cls._split_by_common_patterns(text, detect_headings)

    # =========================================================================
    # ESTRATEGIAS DE DIVISIÓN Y CONSTRUCCIÓN JERÁRQUICA
    # =========================================================================

    @classmethod
    def _build_hierarchy_from_paragraphs(
        cls,
        paragraphs_data: List[Tuple[str, str, int]]
    ) -> List[SectionUnit]:
        """
        Construye una jerarquía de SectionUnits a partir de una lista de párrafos con niveles.
        Level 1 -> Carpeta / Capítulo mayor
        Level 2 -> Escena / Subsección
        """
        root_units: List[SectionUnit] = []
        current_l1: Optional[SectionUnit] = None
        current_l2: Optional[SectionUnit] = None
        unassigned_text: List[str] = []

        for p_text, style, level in paragraphs_data:
            if level == 1:
                # Si había texto previo sin encabezado
                if not current_l1 and unassigned_text:
                    pre_unit = SectionUnit("Prólogo / Inicio", "\n\n".join(unassigned_text), level=1)
                    root_units.append(pre_unit)
                    unassigned_text = []

                current_l1 = SectionUnit(title=p_text, content="", level=1)
                root_units.append(current_l1)
                current_l2 = None

            elif level == 2:
                if not current_l1:
                    # Crear carpeta contenedor implícita si no hubo Level 1
                    current_l1 = SectionUnit(title="Manuscrito", content="", level=1)
                    root_units.append(current_l1)

                current_l2 = SectionUnit(title=p_text, content="", level=2)
                current_l1.children.append(current_l2)

            else:
                # Texto ordinario
                if current_l2:
                    current_l2.content = (current_l2.content + "\n\n" + p_text).strip()
                elif current_l1:
                    current_l1.content = (current_l1.content + "\n\n" + p_text).strip()
                else:
                    unassigned_text.append(p_text)

        if unassigned_text and not root_units:
            root_units.append(SectionUnit("Manuscrito", "\n\n".join(unassigned_text), level=1))

        return root_units

    @classmethod
    def _split_text_by_separator(cls, text: str, separator: str) -> List[SectionUnit]:
        """Divide el texto usando un separador explícito (ej. '#', '***', '---')."""
        escaped_sep = re.escape(separator)
        pattern = rf"(?:^|\n)[ \t]*{escaped_sep}(?:[ \t]+([^\n\r]*)|[ \t]*)(?:\n|$)"
        matches = list(re.finditer(pattern, text))
        units: List[SectionUnit] = []
        if matches:
            for idx, match in enumerate(matches):
                start_content = match.end()
                end_content = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
                content = text[start_content:end_content].strip()
                title_cand = match.group(1)
                if not title_cand:
                    first_line = content.split("\n")[0][:40].strip() if content else ""
                    title = first_line if first_line else f"Sección {idx + 1}"
                else:
                    title = title_cand.strip()
                units.append(SectionUnit(title=title, content=content, level=1))
        else:
            # Fallback a split tradicional por delimitador exacto
            parts = re.split(rf"(?:\n|^)\s*{escaped_sep}\s*(?:\n|$)", text)
            for i, part in enumerate(parts, 1):
                stripped = part.strip()
                if not stripped:
                    continue
                first_line = stripped.split("\n")[0][:40].strip()
                title = first_line if first_line else f"Sección {i}"
                units.append(SectionUnit(title=title, content=stripped, level=1))
        return units

    @classmethod
    def _split_by_separator(cls, paragraphs: List[str], separator: str) -> List[SectionUnit]:
        full_text = "\n\n".join(paragraphs)
        return cls._split_text_by_separator(full_text, separator)

    @classmethod
    def _split_by_common_patterns(cls, text: str, detect_headings: bool = True) -> List[SectionUnit]:
        """
        Divide el manuscrito buscando patrones clásicos:
        - 'Capítulo I', 'Capítulo 1', 'Chapter 1', 'Acto I', 'Escena 1'
        - Separadores como '***', '---', '* * *'
        """
        # Expresión regular para localizar inicios de capítulo
        chap_regex = re.compile(
            r"(?:\n|^)\s*((?:Cap[ií]tulo|Chapter|Parte|Part|Acto|Act|Escena|Scene)\s+[\w\dIVXLCDM]+[^\n]*)(?:\n|$)",
            re.IGNORECASE
        )

        matches = list(chap_regex.finditer(text))
        if len(matches) > 1 and detect_headings:
            units: List[SectionUnit] = []
            prev_end = 0
            prev_title = "Prólogo"

            for i, match in enumerate(matches):
                chunk = text[prev_end:match.start()].strip()
                if chunk and (i > 0 or prev_end > 0):
                    units.append(SectionUnit(title=prev_title, content=chunk, level=1))
                elif chunk and i == 0:
                    units.append(SectionUnit(title="Prólogo", content=chunk, level=1))

                prev_title = match.group(1).strip()
                prev_end = match.end()

            # Último capítulo
            last_chunk = text[prev_end:].strip()
            if last_chunk:
                units.append(SectionUnit(title=prev_title, content=last_chunk, level=1))

            return units

        # Si no hay capítulos, probar con separadores visuales típicos
        for sep in ("***", "* * *", "---", "###"):
            if sep in text:
                return cls._split_text_by_separator(text, sep)

        # Si nada aplica, devolver unidad única
        return [SectionUnit(title="Manuscrito Importado", content=text.strip(), level=1)]

    # =========================================================================
    # INSERCIÓN EN EL BINDER
    # =========================================================================

    @classmethod
    def _insert_unit(
        cls,
        project: EscritorioProject,
        parent_uuid: str,
        unit: SectionUnit
    ) -> List[BinderItem]:
        """
        Inserta recursivamente la unidad y sus hijos en el Binder del proyecto.
        Si la unidad tiene hijos, se crea como 'Folder'; si no, como 'Text'.
        """
        created: List[BinderItem] = []

        is_folder = bool(unit.children)
        item_type = "Folder" if is_folder else "Text"

        new_item = project.add_item(
            parent_uuid=parent_uuid,
            title=unit.title,
            item_type=item_type
        )
        created.append(new_item)

        # Guardar el contenido si tiene texto
        if unit.content:
            rtf_content = RTFEngine.plain_text_to_rtf(unit.content)
            new_item.write_content_rtf(rtf_content)

        # Insertar los hijos debajo de este nuevo nodo
        for child in unit.children:
            child_items = cls._insert_unit(project, new_item.uuid, child)
            created.extend(child_items)

        return created
