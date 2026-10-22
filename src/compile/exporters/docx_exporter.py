"""
Generador Nativo de Microsoft Word OpenXML (.docx) para Escritorio.
Genera paquetes .docx válidos y conformes al estándar ECMA-376 / ISO/IEC 29500 sin dependencias externas:
- [Content_Types].xml y relaciones OpenXML (_rels/.rels, word/_rels/document.xml.rels).
- word/document.xml con estilos tipográficos, interlineado, sangrías y saltos de página.
- word/styles.xml con estilos Normal, Heading 1, Heading 2, Heading 3, Header y Footnote.
- word/header1.xml con cabecera editorial (Apellido del Autor / Título / Número de página dinámico PAGE).
- word/footnotes.xml con notas al pie de página reales enlazadas.
- word/settings.xml con márgenes estándar y configuración de visualización.
"""

import io
import re
import zipfile
import html
from pathlib import Path
from typing import Union, Optional, List, Dict, Any, Tuple


class DOCXExporter:
    """Exportador nativo de documentos Microsoft Word (.docx)."""

    @classmethod
    def export(
        cls,
        text_content: str,
        destination_path: Union[str, Path],
        title: str = "Manuscrito",
        author: str = "Autor",
        font_family: str = "Times New Roman",
        font_size_pt: int = 12,
        line_spacing: float = 2.0,
        margin_inches: float = 1.0,
        page_size: str = "letter"
    ) -> Path:
        """
        Genera el archivo .docx completo y empaquetado en formato ZIP.
        """
        out_path = Path(destination_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # 1. [Content_Types].xml
            zf.writestr("[Content_Types].xml", cls._generate_content_types())

            # 2. _rels/.rels
            zf.writestr("_rels/.rels", cls._generate_root_rels())

            # 3. word/_rels/document.xml.rels
            zf.writestr("word/_rels/document.xml.rels", cls._generate_document_rels())

            # 4. word/styles.xml
            zf.writestr("word/styles.xml", cls._generate_styles(font_family, font_size_pt))

            # 5. word/settings.xml
            zf.writestr("word/settings.xml", cls._generate_settings())

            # 6. word/header1.xml
            author_last_name = author.strip().split()[-1] if author.strip() else "Autor"
            zf.writestr("word/header1.xml", cls._generate_header(author_last_name, title))

            # 7. Procesar párrafos y notas al pie
            paragraphs_xml, footnotes_xml = cls._parse_content_to_xml(
                text_content=text_content,
                font_family=font_family,
                font_size_pt=font_size_pt,
                line_spacing=line_spacing
            )

            # 8. word/document.xml
            zf.writestr(
                "word/document.xml",
                cls._generate_document(
                    body_paragraphs=paragraphs_xml,
                    margin_inches=margin_inches,
                    page_size=page_size
                )
            )

            # 9. word/footnotes.xml
            zf.writestr("word/footnotes.xml", footnotes_xml)

        # Escritura atómica a disco
        buffer.seek(0)
        with open(out_path, "wb") as f:
            f.write(buffer.read())

        return out_path

    # =========================================================================
    # Generadores de Archivos de Estructura OpenXML
    # =========================================================================

    @staticmethod
    def _generate_content_types() -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
            '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
            '  <Default Extension="xml" ContentType="application/xml"/>\n'
            '  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>\n'
            '  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>\n'
            '  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>\n'
            '  <Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>\n'
            '  <Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/>\n'
            '</Types>'
        )

    @staticmethod
    def _generate_root_rels() -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>\n'
            '</Relationships>'
        )

    @staticmethod
    def _generate_document_rels() -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            '  <Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>\n'
            '  <Relationship Id="rIdSettings" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>\n'
            '  <Relationship Id="rIdHeader1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>\n'
            '  <Relationship Id="rIdFootnotes" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/>\n'
            '</Relationships>'
        )

    @staticmethod
    def _generate_styles(font_family: str, font_size_pt: int) -> str:
        half_pts = font_size_pt * 2
        heading1_half_pts = (font_size_pt + 6) * 2
        heading2_half_pts = (font_size_pt + 2) * 2

        return (
            f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            f'<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">\n'
            f'  <w:docDefaults>\n'
            f'    <w:rPrDefault>\n'
            f'      <w:rPr>\n'
            f'        <w:rFonts w:ascii="{font_family}" w:hAnsi="{font_family}" w:cs="{font_family}"/>\n'
            f'        <w:sz w:val="{half_pts}"/>\n'
            f'        <w:szCs w:val="{half_pts}"/>\n'
            f'        <w:lang w:val="es-ES"/>\n'
            f'      </w:rPr>\n'
            f'    </w:rPrDefault>\n'
            f'  </w:docDefaults>\n'
            f'  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">\n'
            f'    <w:name w:val="Normal"/>\n'
            f'    <w:qFormat/>\n'
            f'  </w:style>\n'
            f'  <w:style w:type="paragraph" w:styleId="Heading1">\n'
            f'    <w:name w:val="heading 1"/>\n'
            f'    <w:basedOn w:val="Normal"/>\n'
            f'    <w:qFormat/>\n'
            f'    <w:pPr>\n'
            f'      <w:spacing w:before="360" w:after="240"/>\n'
            f'      <w:jc w:val="center"/>\n'
            f'    </w:pPr>\n'
            f'    <w:rPr>\n'
            f'      <w:b/>\n'
            f'      <w:sz w:val="{heading1_half_pts}"/>\n'
            f'    </w:rPr>\n'
            f'  </w:style>\n'
            f'  <w:style w:type="paragraph" w:styleId="Heading2">\n'
            f'    <w:name w:val="heading 2"/>\n'
            f'    <w:basedOn w:val="Normal"/>\n'
            f'    <w:qFormat/>\n'
            f'    <w:pPr>\n'
            f'      <w:spacing w:before="240" w:after="120"/>\n'
            f'    </w:pPr>\n'
            f'    <w:rPr>\n'
            f'      <w:b/>\n'
            f'      <w:sz w:val="{heading2_half_pts}"/>\n'
            f'    </w:rPr>\n'
            f'  </w:style>\n'
            f'  <w:style w:type="paragraph" w:styleId="Header">\n'
            f'    <w:name w:val="header"/>\n'
            f'    <w:basedOn w:val="Normal"/>\n'
            f'    <w:pPr>\n'
            f'      <w:jc w:val="right"/>\n'
            f'    </w:pPr>\n'
            f'    <w:rPr>\n'
            f'      <w:sz w:val="20"/>\n'
            f'    </w:rPr>\n'
            f'  </w:style>\n'
            f'  <w:style w:type="paragraph" w:styleId="FootnoteText">\n'
            f'    <w:name w:val="footnote text"/>\n'
            f'    <w:basedOn w:val="Normal"/>\n'
            f'    <w:rPr>\n'
            f'      <w:sz w:val="20"/>\n'
            f'    </w:rPr>\n'
            f'  </w:style>\n'
            f'</w:styles>'
        )

    @staticmethod
    def _generate_settings() -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">\n'
            '  <w:defaultTabStop w:val="720"/>\n'
            '  <w:evenAndOddHeaders/>\n'
            '</w:settings>'
        )

    @staticmethod
    def _generate_header(author_last_name: str, title: str) -> str:
        esc_author = html.escape(author_last_name)
        esc_title = html.escape(title[:25])
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">\n'
            '  <w:p>\n'
            '    <w:pPr>\n'
            '      <w:pStyle w:val="Header"/>\n'
            '      <w:jc w:val="right"/>\n'
            '    </w:pPr>\n'
            f'    <w:r><w:t xml:space="preserve">{esc_author} / {esc_title} / </w:t></w:r>\n'
            '    <w:fldSimple w:instr="PAGE"/>\n'
            '  </w:p>\n'
            '</w:hdr>'
        )

    @classmethod
    def _parse_content_to_xml(
        cls,
        text_content: str,
        font_family: str,
        font_size_pt: int,
        line_spacing: float
    ) -> Tuple[str, str]:
        """
        Convierte el texto compilado en párrafos WordML y extrae notas al pie.
        """
        line_rule = int(line_spacing * 240)  # 240 dxa = 1.0 línea
        half_pts = font_size_pt * 2

        paragraphs_xml: List[str] = []
        footnotes: List[Tuple[int, str]] = []
        footnote_counter = 1

        # Extraer definiciones de notas al pie [^id]: texto
        raw_paragraphs = text_content.replace("\r\n", "\n").split("\n")
        fn_defs: Dict[str, str] = {}
        fn_def_pattern = re.compile(r"^\[(?:\^)?(\w+)\]:\s*(.+)$")
        filtered_lines: List[str] = []
        for raw_l in raw_paragraphs:
            m = fn_def_pattern.match(raw_l.strip())
            if m:
                fn_defs[m.group(1)] = m.group(2).strip()
            else:
                filtered_lines.append(raw_l)

        for raw_line in filtered_lines:
            line = raw_line.strip()
            if not line:
                continue

            # 1. Salto de página
            if "\\pagebreak" in line or line == "=== PAGE BREAK ===":
                paragraphs_xml.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
                continue

            # 2. Encabezados Markdown
            if line.startswith("# "):
                heading_text = html.escape(line[2:].strip())
                paragraphs_xml.append(
                    f'<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr>'
                    f'<w:r><w:t>{heading_text}</w:t></w:r></w:p>'
                )
                continue
            elif line.startswith("## "):
                heading_text = html.escape(line[3:].strip())
                paragraphs_xml.append(
                    f'<w:p><w:pPr><w:pStyle w:val="Heading2"/></w:pPr>'
                    f'<w:r><w:t>{heading_text}</w:t></w:r></w:p>'
                )
                continue
            elif line.startswith("### "):
                heading_text = html.escape(line[4:].strip())
                paragraphs_xml.append(
                    f'<w:p><w:pPr><w:pStyle w:val="Heading2"/></w:pPr>'
                    f'<w:r><w:b/><w:t>{heading_text}</w:t></w:r></w:p>'
                )
                continue

            # 3. Separador de escena centrado (ej. * * * o #)
            if line in ("* * *", "#", "---", "***", "~ ~ ~"):
                paragraphs_xml.append(
                    f'<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:before="240" w:after="240"/></w:pPr>'
                    f'<w:r><w:t>{html.escape(line)}</w:t></w:r></w:p>'
                )
                continue

            # 4. Texto centrado HTML <center>...</center>
            is_centered = False
            if line.startswith("<center>") and line.endswith("</center>"):
                is_centered = True
                line = line[8:-9].strip()

            # 5. Detección y extracción de notas al pie [^nota] o [[nota]]
            # Convertir sintaxis [^1]: texto o [^1] en WordML footnotes
            fn_matches = re.findall(r"\[\^(.*?)\]", line)
            runs_xml: List[str] = []

            # Reemplazar notas con referencias de notas al pie
            pos = 0
            for m in re.finditer(r"\[\^(.*?)\]", line):
                pre_text = line[pos:m.start()]
                if pre_text:
                    runs_xml.append(f'<w:r><w:t xml:space="preserve">{html.escape(pre_text)}</w:t></w:r>')

                fn_id_raw = m.group(1)
                fn_content = fn_defs.get(fn_id_raw, fn_id_raw)
                current_id = footnote_counter
                footnote_counter += 1
                footnotes.append((current_id, fn_content))

                # Referencia en el cuerpo
                runs_xml.append(
                    f'<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr>'
                    f'<w:footnoteReference w:id="{current_id}"/></w:r>'
                )
                pos = m.end()

            rest_text = line[pos:]
            if rest_text:
                runs_xml.append(f'<w:r><w:t xml:space="preserve">{html.escape(rest_text)}</w:t></w:r>')

            if not runs_xml:
                runs_xml.append(f'<w:r><w:t xml:space="preserve">{html.escape(line)}</w:t></w:r>')

            # Propiedades del párrafo (sangría de primera línea e interlineado)
            jc_val = "center" if is_centered else "both"
            indent_xml = '<w:ind w:firstLine="720"/>' if not is_centered else ""

            p_xml = (
                f'<w:p>'
                f'<w:pPr>'
                f'<w:spacing w:line="{line_rule}" w:lineRule="auto" w:after="120"/>'
                f'<w:jc w:val="{jc_val}"/>'
                f'{indent_xml}'
                f'</w:pPr>'
                f'{"".join(runs_xml)}'
                f'</w:p>'
            )
            paragraphs_xml.append(p_xml)

        # 6. Generar word/footnotes.xml
        footnotes_body = []
        # Entradas reservadas obligatorias por la especificación OpenXML (-1 = separador, 0 = continuación)
        footnotes_body.append(
            '<w:footnote w:type="separator" w:id="-1">\n'
            '  <w:p><w:r><w:separator/></w:r></w:p>\n'
            '</w:footnote>'
        )
        footnotes_body.append(
            '<w:footnote w:type="continuationSeparator" w:id="0">\n'
            '  <w:p><w:r><w:continuationSeparator/></w:r></w:p>\n'
            '</w:footnote>'
        )

        for fid, ftext in footnotes:
            footnotes_body.append(
                f'<w:footnote w:id="{fid}">\n'
                f'  <w:p><w:pPr><w:pStyle w:val="FootnoteText"/></w:pPr>\n'
                f'    <w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr><w:footnoteRef/></w:r>\n'
                f'    <w:r><w:t xml:space="preserve"> {html.escape(ftext)}</w:t></w:r>\n'
                f'  </w:p>\n'
                f'</w:footnote>'
            )

        footnotes_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">\n'
            + "\n".join(footnotes_body)
            + "\n</w:footnotes>"
        )

        return "\n".join(paragraphs_xml), footnotes_xml

    @classmethod
    def _generate_document(cls, body_paragraphs: str, margin_inches: float, page_size: str) -> str:
        # 1440 twips = 1 pulgada
        mar_twips = int(margin_inches * 1440)

        # Dimensiones de página en twips
        if page_size.lower() == "a4":
            w_twips = 11906
            h_twips = 16838
        elif page_size.lower() == "6x9":
            w_twips = 8640
            h_twips = 12960
        else:  # Letter
            w_twips = 12240
            h_twips = 15840

        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">\n'
            '  <w:body>\n'
            f'{body_paragraphs}\n'
            '    <w:sectPr>\n'
            '      <w:headerReference w:type="default" r:id="rIdHeader1"/>\n'
            f'      <w:pgSz w:w="{w_twips}" w:h="{h_twips}"/>\n'
            f'      <w:pgMar w:top="{mar_twips}" w:right="{mar_twips}" w:bottom="{mar_twips}" w:left="{mar_twips}" '
            f'w:header="720" w:footer="720" w:gutter="0"/>\n'
            '    </w:sectPr>\n'
            '  </w:body>\n'
            '</w:document>'
        )
