"""
Generador Nativo de Libros Electrónicos EPUB 3 (.epub) para Escritorio.
Genera paquetes EPUB 3.2 válidos y conformes con el estándar IDPF / W3C sin dependencias externas:
- Archivo 'mimetype' sin compresión en el offset 0 del contenedor ZIP.
- Contenedor 'META-INF/container.xml'.
- Descriptor de paquete 'OEBPS/content.opf' con metadatos Dublin Core y Spine ordenado.
- Documento de navegación EPUB 3 'OEBPS/nav.xhtml' (HTML5) y fallback EPUB 2 'OEBPS/toc.ncx'.
- Hoja de estilos tipográficos editorial 'OEBPS/style.css'.
- Portada editorial XHTML ('OEBPS/cover.xhtml').
- División automática de capítulos y escenas en documentos XHTML individuales.
- Soporte para notas al pie de página semánticas interactivas tipo pop-up (epub:type="noteref" y epub:type="footnote").
"""

import io
import re
import uuid
import zipfile
import html
import datetime
from pathlib import Path
from typing import Union, List, Tuple, Dict, Any, Optional


class EPUB3Exporter:
    """Exportador nativo de libros electrónicos en formato EPUB3 estándar."""

    @classmethod
    def export(
        cls,
        text_content: str,
        destination_path: Union[str, Path],
        title: str = "Manuscrito",
        author: str = "Autor",
        language: str = "es",
        publisher: str = "Escritorio Publishing",
        cover_subtitle: Optional[str] = None
    ) -> Path:
        """
        Genera el archivo .epub empaquetado conforme a las especificaciones EPUB 3.
        """
        out_path = Path(destination_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        book_uuid = str(uuid.uuid4())
        mod_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # 1. Parsear contenido en capítulos y notas al pie
        chapters, footnotes = cls._parse_content_into_chapters(text_content, title)

        # 2. Generar buffer ZIP con compresión
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            # Requisito estricto EPUB: 'mimetype' DEBE ser el primer archivo, sin compresión
            mimetype_bytes = b"application/epub+zip"
            mimetype_info = zipfile.ZipInfo("mimetype")
            mimetype_info.compress_type = zipfile.ZIP_STORED
            mimetype_info.flag_bits = 0
            zf.writestr(mimetype_info, mimetype_bytes)

            # META-INF/container.xml
            zf.writestr("META-INF/container.xml", cls._generate_container_xml(), compress_type=zipfile.ZIP_DEFLATED)

            # OEBPS/style.css
            zf.writestr("OEBPS/style.css", cls._generate_css(), compress_type=zipfile.ZIP_DEFLATED)

            # OEBPS/cover.xhtml
            zf.writestr(
                "OEBPS/cover.xhtml",
                cls._generate_cover_xhtml(title, author, cover_subtitle or ""),
                compress_type=zipfile.ZIP_DEFLATED
            )

            # OEBPS/nav.xhtml y OEBPS/toc.ncx
            zf.writestr(
                "OEBPS/nav.xhtml",
                cls._generate_nav_xhtml(title, chapters),
                compress_type=zipfile.ZIP_DEFLATED
            )
            zf.writestr(
                "OEBPS/toc.ncx",
                cls._generate_toc_ncx(book_uuid, title, author, chapters),
                compress_type=zipfile.ZIP_DEFLATED
            )

            # Capítulos individuales XHTML
            for i, chap in enumerate(chapters, 1):
                filename = f"OEBPS/chapter_{i:03d}.xhtml"
                chap_html = cls._generate_chapter_xhtml(chap, i, footnotes)
                zf.writestr(filename, chap_html, compress_type=zipfile.ZIP_DEFLATED)

            # OEBPS/content.opf
            zf.writestr(
                "OEBPS/content.opf",
                cls._generate_content_opf(book_uuid, title, author, language, publisher, mod_time, chapters),
                compress_type=zipfile.ZIP_DEFLATED
            )

        # Guardar en disco
        out_path.write_bytes(buffer.getvalue())
        return out_path

    # =========================================================================
    # PARSER DE CONTENIDO Y NOTAS
    # =========================================================================

    @classmethod
    def _parse_content_into_chapters(
        cls,
        text: str,
        default_title: str
    ) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        """
        Divide el manuscrito en secciones / capítulos reconociendo:
        - Encabezados Markdown (# Título, ## Subtítulo)
        - Separadores '---' o '\\pagebreak'
        - Patrones como 'Capítulo X' o 'Chapter X'
        - Extrae notas al pie en formato [^1]: o [1]:
        """
        footnotes: Dict[str, str] = {}

        # 1. Extraer notas al pie declaradas al final o en párrafos
        fn_pattern = re.compile(r"^\[(?:\^)?(\d+)\]:\s*(.+)$", re.MULTILINE)
        for match in fn_pattern.finditer(text):
            fn_id = match.group(1)
            fn_text = match.group(2).strip()
            footnotes[fn_id] = fn_text

        cleaned_text = fn_pattern.sub("", text).strip()

        # 2. Dividir por saltos de página explícitos o líneas delimitadoras
        raw_sections = re.split(r"(?:\n|^)(?:---|\*\*\*|\\pagebreak)(?:\n|$)", cleaned_text)

        chapters: List[Dict[str, Any]] = []

        for sec_idx, sec in enumerate(raw_sections):
            sec = sec.strip()
            if not sec:
                continue

            # Buscar subcapítulos por encabezado # o Capítulo si la sección es larga
            lines = sec.split("\n")
            current_chap_title = ""
            current_paragraphs: List[str] = []

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue

                # Detección de encabezado
                if stripped.startswith("#"):
                    if current_paragraphs and current_chap_title:
                        chapters.append({
                            "title": current_chap_title,
                            "paragraphs": list(current_paragraphs)
                        })
                        current_paragraphs = []

                    heading_text = stripped.lstrip("#").strip()
                    current_chap_title = heading_text
                elif re.match(r"^(?:Cap[ií]tulo|Chapter|Parte|Part)\s+[\w\dIVXLCDM]+", stripped, re.IGNORECASE):
                    if current_paragraphs and current_chap_title:
                        chapters.append({
                            "title": current_chap_title,
                            "paragraphs": list(current_paragraphs)
                        })
                        current_paragraphs = []
                    current_chap_title = stripped
                else:
                    if not current_chap_title and not current_paragraphs:
                        # Asignar título de inicio
                        current_chap_title = f"Capítulo {len(chapters) + 1}"
                    current_paragraphs.append(stripped)

            if current_paragraphs:
                chapters.append({
                    "title": current_chap_title or (default_title if not chapters else f"Capítulo {len(chapters) + 1}"),
                    "paragraphs": current_paragraphs
                })

        if not chapters:
            chapters = [{
                "title": default_title,
                "paragraphs": [p.strip() for p in text.split("\n") if p.strip()]
            }]

        return chapters, footnotes

    # =========================================================================
    # GENERADORES XML / XHTML
    # =========================================================================

    @staticmethod
    def _generate_container_xml() -> str:
        return """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""

    @staticmethod
    def _generate_css() -> str:
        return """/* Hoja de Estilos Tipográfica Editorial para EPUB3 */
@charset "utf-8";

body {
    font-family: "Georgia", "Palatino", "Times New Roman", serif;
    font-size: 1.05em;
    line-height: 1.6;
    margin: 5% 7%;
    padding: 0;
    color: #1a1a1a;
    background-color: transparent;
    text-rendering: optimizeLegibility;
}

h1.chapter-title {
    font-size: 1.8em;
    font-weight: normal;
    text-align: center;
    margin-top: 15%;
    margin-bottom: 2em;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

h2 {
    font-size: 1.3em;
    font-weight: bold;
    margin-top: 1.8em;
    margin-bottom: 0.8em;
    text-align: center;
}

p {
    margin: 0;
    padding: 0;
    text-align: justify;
    text-indent: 1.5em;
}

p.first-line, h1 + p, h2 + p {
    text-indent: 0;
}

.scene-break {
    text-align: center;
    margin: 1.8em 0;
    letter-spacing: 0.5em;
}

/* Portada */
.cover-container {
    text-align: center;
    margin-top: 25%;
}

.book-title {
    font-size: 2.2em;
    font-weight: bold;
    letter-spacing: 0.08em;
    margin-bottom: 0.5em;
    text-transform: uppercase;
}

.book-subtitle {
    font-size: 1.2em;
    font-style: italic;
    color: #555;
    margin-bottom: 3em;
}

.book-author {
    font-size: 1.3em;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* Notas al pie de página emergentes (Pop-up Footnotes) */
a.noteref {
    vertical-align: super;
    font-size: 0.75em;
    font-weight: bold;
    text-decoration: none;
    color: #0d47a1;
    padding: 0 2px;
}

aside[epub|type~="footnote"], aside.footnote {
    font-size: 0.85em;
    line-height: 1.4;
    margin-top: 1.5em;
    padding-top: 0.8em;
    border-top: 1px solid #ddd;
    color: #444;
}

aside[epub|type~="footnote"] p, aside.footnote p {
    text-indent: 0;
}
"""

    @classmethod
    def _generate_cover_xhtml(cls, title: str, author: str, subtitle: str) -> str:
        esc_title = html.escape(title)
        esc_author = html.escape(author)
        esc_sub = html.escape(subtitle)

        sub_html = f'<p class="book-subtitle">{esc_sub}</p>' if esc_sub else ""

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="es" lang="es">
<head>
    <meta charset="utf-8"/>
    <title>{esc_title}</title>
    <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body epub:type="cover">
    <div class="cover-container">
        <h1 class="book-title">{esc_title}</h1>
        {sub_html}
        <div style="margin-top: 4em;">
            <p class="book-author">{esc_author}</p>
        </div>
    </div>
</body>
</html>"""

    @classmethod
    def _generate_chapter_xhtml(
        cls,
        chapter: Dict[str, Any],
        chap_index: int,
        all_footnotes: Dict[str, str]
    ) -> str:
        title = chapter.get("title", f"Capítulo {chap_index}")
        paragraphs = chapter.get("paragraphs", [])

        esc_title = html.escape(title)

        chap_footnotes: Dict[str, str] = {}
        body_lines: List[str] = [f'<h1 class="chapter-title">{esc_title}</h1>']

        for p_idx, raw_p in enumerate(paragraphs):
            # Procesar referencias a notas al pie: [^1] o [1]
            def replace_fn(match: re.Match) -> str:
                fn_id = match.group(1)
                if fn_id in all_footnotes:
                    chap_footnotes[fn_id] = all_footnotes[fn_id]
                else:
                    chap_footnotes[fn_id] = f"Nota {fn_id}"
                return f'<a epub:type="noteref" class="noteref" href="#fn{fn_id}">[{fn_id}]</a>'

            p_text = re.sub(r"\[(?:\^)?(\d+)\]", replace_fn, raw_p)
            esc_p = html.escape(p_text)
            # Revertir etiquetas <a> de las notas insertadas
            esc_p = re.sub(
                r"&lt;a epub:type=&quot;noteref&quot; class=&quot;noteref&quot; href=&quot;#fn(\d+)&quot;&gt;\[(\d+)\]&lt;/a&gt;",
                r'<a epub:type="noteref" class="noteref" href="#fn\1">[\2]</a>',
                esc_p
            )

            p_class = ' class="first-line"' if p_idx == 0 else ""
            body_lines.append(f'<p{p_class}>{esc_p}</p>')

        # Agregar notas al pie interactivas como <aside epub:type="footnote">
        if chap_footnotes:
            body_lines.append('<div class="footnotes-section">')
            for fn_id, fn_text in chap_footnotes.items():
                esc_fn = html.escape(fn_text)
                aside_tag = (
                    f'<aside id="fn{fn_id}" epub:type="footnote" class="footnote">'
                    f'<p><strong>[{fn_id}]</strong> {esc_fn} '
                    f'<a href="#fn{fn_id}" style="text-decoration:none;">&#8617;</a></p>'
                    f'</aside>'
                )
                body_lines.append(aside_tag)
            body_lines.append('</div>')

        body_content = "\n        ".join(body_lines)

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="es" lang="es">
<head>
    <meta charset="utf-8"/>
    <title>{esc_title}</title>
    <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body epub:type="bodymatter">
    <section epub:type="chapter">
        {body_content}
    </section>
</body>
</html>"""

    @classmethod
    def _generate_nav_xhtml(cls, title: str, chapters: List[Dict[str, Any]]) -> str:
        esc_title = html.escape(title)

        nav_items: List[str] = [
            '<li><a href="cover.xhtml">Portada</a></li>'
        ]

        for i, chap in enumerate(chapters, 1):
            chap_title = html.escape(chap.get("title", f"Capítulo {i}"))
            filename = f"chapter_{i:03d}.xhtml"
            nav_items.append(f'<li><a href="{filename}">{chap_title}</a></li>')

        nav_list_html = "\n                ".join(nav_items)

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="es" lang="es">
<head>
    <meta charset="utf-8"/>
    <title>Tabla de Contenidos - {esc_title}</title>
    <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
    <nav epub:type="toc" id="toc">
        <h1>Tabla de Contenidos</h1>
        <ol>
            {nav_list_html}
        </ol>
    </nav>
    <nav epub:type="landmarks" hidden="">
        <ol>
            <li><a epub:type="cover" href="cover.xhtml">Portada</a></li>
            <li><a epub:type="bodymatter" href="chapter_001.xhtml">Comienzo de lectura</a></li>
        </ol>
    </nav>
</body>
</html>"""

    @classmethod
    def _generate_toc_ncx(
        cls,
        book_uuid: str,
        title: str,
        author: str,
        chapters: List[Dict[str, Any]]
    ) -> str:
        esc_title = html.escape(title)
        esc_author = html.escape(author)

        nav_points: List[str] = [
            f"""        <navPoint id="navPoint-1" playOrder="1">
            <navLabel><text>Portada</text></navLabel>
            <content src="cover.xhtml"/>
        </navPoint>"""
        ]

        for i, chap in enumerate(chapters, 1):
            chap_title = html.escape(chap.get("title", f"Capítulo {i}"))
            filename = f"chapter_{i:03d}.xhtml"
            nav_points.append(f"""        <navPoint id="navPoint-{i + 1}" playOrder="{i + 1}">
            <navLabel><text>{chap_title}</text></navLabel>
            <content src="{filename}"/>
        </navPoint>""")

        points_html = "\n".join(nav_points)

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head>
        <meta name="dtb:uid" content="urn:uuid:{book_uuid}"/>
        <meta name="dtb:depth" content="1"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle><text>{esc_title}</text></docTitle>
    <docAuthor><text>{esc_author}</text></docAuthor>
    <navMap>
{points_html}
    </navMap>
</ncx>"""

    @classmethod
    def _generate_content_opf(
        cls,
        book_uuid: str,
        title: str,
        author: str,
        language: str,
        publisher: str,
        mod_time: str,
        chapters: List[Dict[str, Any]]
    ) -> str:
        esc_title = html.escape(title)
        esc_author = html.escape(author)
        esc_lang = html.escape(language)
        esc_pub = html.escape(publisher)

        # Manifest
        manifest_items: List[str] = [
            '<item id="style" href="style.css" media-type="text/css"/>',
            '<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>',
            '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
            '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>'
        ]

        # Spine
        spine_items: List[str] = [
            '<itemref idref="cover"/>'
        ]

        for i in range(1, len(chapters) + 1):
            chap_id = f"chap_{i:03d}"
            filename = f"chapter_{i:03d}.xhtml"
            manifest_items.append(f'<item id="{chap_id}" href="{filename}" media-type="application/xhtml+xml"/>')
            spine_items.append(f'<itemref idref="{chap_id}"/>')

        manifest_xml = "\n        ".join(manifest_items)
        spine_xml = "\n        ".join(spine_items)

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="pub-id" xml:lang="{esc_lang}">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:identifier id="pub-id">urn:uuid:{book_uuid}</dc:identifier>
        <dc:title>{esc_title}</dc:title>
        <dc:creator>{esc_author}</dc:creator>
        <dc:language>{esc_lang}</dc:language>
        <dc:publisher>{esc_pub}</dc:publisher>
        <meta property="dcterms:modified">{mod_time}</meta>
    </metadata>
    <manifest>
        {manifest_xml}
    </manifest>
    <spine toc="ncx">
        {spine_xml}
    </spine>
</package>"""
