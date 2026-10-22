"""
Generadores Nativos de Guion Profesional para Escritorio:
- Final Draft XML (.fdx): Conforme a la especificación estándar de Final Draft Version 3+.
- Fountain (.fountain): Sintaxis estándar de texto plano para guiones cinematográficos y televisivos.
"""

import re
import html
from pathlib import Path
from typing import Union, List, Dict, Any, Optional, Tuple


class ScreenplayExporter:
    """Exportador de guiones a Final Draft (.fdx) y Fountain (.fountain)."""

    # Patrones para detección sintáctica de elementos de guion
    SCENE_HEADING_REGEX = re.compile(
        r"^(?:\.?(?:INT|EXT|INT\./EXT|EXT\./INT|EST|I/E)\.?\b.*)$",
        re.IGNORECASE
    )
    TRANSITION_REGEX = re.compile(
        r"^(?:(?:[A-Z\s]+TO:|CORTE\s+A:|DISUELVE\s+A:|FUNDIDO\s+A:|FADE\s+IN:|FADE\s+OUT:?)|(?:>[^<>\n]+))$",
        re.IGNORECASE
    )
    CHARACTER_REGEX = re.compile(
        r"^[A-ZÁÉÍÓÚÑ0-9\s\.\-'\(\)]+$"
    )

    # =========================================================================
    # EXPORTACIÓN A FINAL DRAFT XML (.FDX)
    # =========================================================================

    @classmethod
    def export_fdx(
        cls,
        text_content: str,
        destination_path: Union[str, Path],
        title: str = "Guion",
        author: str = "Autor"
    ) -> Path:
        """
        Genera un archivo XML Final Draft (.fdx) estructurado con tipos de párrafo
        semánticos (Scene Heading, Action, Character, Dialogue, Parenthetical, Transition).
        """
        out_path = Path(destination_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        parsed_elements = cls._parse_screenplay_text(text_content)

        paragraphs_xml: List[str] = []
        for elem_type, text in parsed_elements:
            esc_text = html.escape(text)
            paragraphs_xml.append(
                f'        <Paragraph Type="{elem_type}">\n'
                f'            <Text>{esc_text}</Text>\n'
                f'        </Paragraph>'
            )

        body_xml = "\n".join(paragraphs_xml)
        esc_title = html.escape(title)
        esc_author = html.escape(author)

        fdx_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<FinalDraft DocumentType="Script" Template="No" Version="3">
    <Content>
{body_xml}
    </Content>
    <HeaderAndFooter>
        <Header>
            <Paragraph Alignment="Right">
                <Text>{esc_title} - {esc_author}</Text>
            </Paragraph>
        </Header>
        <Footer>
            <Paragraph Alignment="Right">
                <DynamicNumbering Type="Page"/>
            </Paragraph>
        </Footer>
    </HeaderAndFooter>
    <TitlePage>
        <Content>
            <Paragraph Alignment="Center">
                <Text AdornmentStyle="-1" Background="#FFFFFFFFFFFF" Color="#000000000000" Font="Courier Final Draft" RevisionID="0" Size="24" Style="Bold">{esc_title}</Text>
            </Paragraph>
            <Paragraph Alignment="Center">
                <Text AdornmentStyle="-1" Background="#FFFFFFFFFFFF" Color="#000000000000" Font="Courier Final Draft" RevisionID="0" Size="12" Style="Regular">escrito por</Text>
            </Paragraph>
            <Paragraph Alignment="Center">
                <Text AdornmentStyle="-1" Background="#FFFFFFFFFFFF" Color="#000000000000" Font="Courier Final Draft" RevisionID="0" Size="14" Style="Regular">{esc_author}</Text>
            </Paragraph>
        </Content>
    </TitlePage>
</FinalDraft>"""

        out_path.write_text(fdx_content, encoding="utf-8")
        return out_path

    # =========================================================================
    # EXPORTACIÓN A FOUNTAIN (.FOUNTAIN)
    # =========================================================================

    @classmethod
    def export_fountain(
        cls,
        text_content: str,
        destination_path: Union[str, Path],
        title: str = "Guion",
        author: str = "Autor"
    ) -> Path:
        """
        Genera un documento Fountain (.fountain) estándar con metadatos de portada
        y estructuración limpia de escenas, personajes y diálogos.
        """
        out_path = Path(destination_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        parsed_elements = cls._parse_screenplay_text(text_content)

        lines: List[str] = [
            f"Title: {title}",
            f"Credit: escrito por",
            f"Author: {author}",
            f"Draft date: {cls._get_current_date()}",
            "Contact: Escritorio Screenwriting Engine",
            "\n===\n"  # Separador oficial de página de título Fountain
        ]

        prev_type = ""
        for elem_type, text in parsed_elements:
            if elem_type == "Scene Heading":
                lines.append(f"\n{text.upper()}\n")
            elif elem_type == "Character":
                lines.append(f"\n{text.upper()}")
            elif elem_type == "Parenthetical":
                clean_p = text.strip()
                if not (clean_p.startswith("(") and clean_p.endswith(")")):
                    clean_p = f"({clean_p})"
                lines.append(clean_p)
            elif elem_type == "Dialogue":
                lines.append(f"{text}\n")
            elif elem_type == "Transition":
                if not text.startswith(">"):
                    lines.append(f"\n> {text.upper()}\n")
                else:
                    lines.append(f"\n{text}\n")
            elif elem_type == "Shot":
                lines.append(f"\n.{text.upper()}\n")
            else:  # Action / General
                lines.append(f"\n{text}\n")
            prev_type = elem_type

        fountain_text = "\n".join(lines)
        out_path.write_text(fountain_text, encoding="utf-8")
        return out_path

    # =========================================================================
    # PARSER DE ELEMENTOS DE GUION
    # =========================================================================

    @classmethod
    def _parse_screenplay_text(cls, text: str) -> List[Tuple[str, str]]:
        """
        Analiza texto sin procesar o preformateado y clasifica cada párrafo en:
        Scene Heading, Action, Character, Dialogue, Parenthetical, Transition, Shot.
        """
        elements: List[Tuple[str, str]] = []
        raw_lines = text.split("\n")

        i = 0
        n = len(raw_lines)
        last_was_character = False
        last_was_parenthetical = False

        while i < n:
            line = raw_lines[i].strip()
            if not line:
                last_was_character = False
                last_was_parenthetical = False
                i += 1
                continue

            # 1. Encabezado de Escena
            if cls.SCENE_HEADING_REGEX.match(line):
                # Eliminar punto inicial de Fountain si lo tiene
                heading = line[1:].strip() if line.startswith(".") else line
                elements.append(("Scene Heading", heading.upper()))
                last_was_character = False
                last_was_parenthetical = False
                i += 1
                continue

            # 2. Transición
            if cls.TRANSITION_REGEX.match(line):
                trans = line.lstrip(">").strip()
                elements.append(("Transition", trans.upper()))
                last_was_character = False
                last_was_parenthetical = False
                i += 1
                continue

            # 3. Paréntesis (Parenthetical)
            if line.startswith("(") and line.endswith(")"):
                elements.append(("Parenthetical", line))
                last_was_parenthetical = True
                i += 1
                continue

            # 4. Si la línea anterior fue Personaje o Paréntesis, esto es Diálogo
            if last_was_character or last_was_parenthetical:
                elements.append(("Dialogue", line))
                last_was_character = False
                last_was_parenthetical = False
                i += 1
                continue

            # 5. Detección de Personaje: línea corta en mayúsculas sin puntuación final
            # y que no sea una escena o transición
            is_all_caps = line.isupper() and len(line) < 40 and not line.endswith((".", ",", ";", ":", "!", "?"))
            if is_all_caps and cls.CHARACTER_REGEX.match(line):
                elements.append(("Character", line))
                last_was_character = True
                last_was_parenthetical = False
                i += 1
                continue

            # 6. Acción por defecto
            elements.append(("Action", line))
            last_was_character = False
            last_was_parenthetical = False
            i += 1

        return elements

    @staticmethod
    def _get_current_date() -> str:
        import datetime
        return datetime.date.today().strftime("%d/%m/%Y")
