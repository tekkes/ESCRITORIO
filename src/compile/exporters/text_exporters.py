"""
Exportadores Nativos de Texto y Publicación Académica/Web para Escritorio:
- LaTeX (.tex): Documentos tipográficos con clases 'book' o 'article', paquetes de microtipografía y notas al pie reales.
- MultiMarkdown (.md): Manuscritos estructurados con bloque de metadatos YAML/MMD y notas al pie [^1].
- Rich Text Format (.rtf): Formato de intercambio enriquecido con tabla de fuentes y codificación ANSI.
- Web Semántica (.html): Documento HTML5 responsivo con diseño editorial y notas al pie semánticas.
"""

import re
import html
from pathlib import Path
from typing import Union, List, Dict, Any, Optional
from ...core.rtf_engine import RTFEngine
from ...core.storage_atomic import AtomicStorage


class LaTeXExporter:
    """Exportador nativo a LaTeX (.tex) de calidad tipográfica editorial."""

    LATEX_SPECIAL_CHARS = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    @classmethod
    def escape_latex(cls, text: str) -> str:
        """Escapa caracteres reservados de LaTeX preservando saltos."""
        # Primero proteger la barra invertida
        res = text.replace("\\", cls.LATEX_SPECIAL_CHARS["\\"])
        for char, replacement in cls.LATEX_SPECIAL_CHARS.items():
            if char != "\\":
                res = res.replace(char, replacement)
        return res

    @classmethod
    def export(
        cls,
        text_content: str,
        destination_path: Union[str, Path],
        title: str = "Manuscrito",
        author: str = "Autor",
        doc_class: str = "book",
        paper_size: str = "a4paper",
        font_size: str = "11pt"
    ) -> Path:
        """
        Genera un archivo .tex listo para compilar con pdflatex, xelatex o lualatex.
        """
        out_path = Path(destination_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        esc_title = cls.escape_latex(title)
        esc_author = cls.escape_latex(author)

        # Parsear párrafos, encabezados y notas al pie
        lines = text_content.split("\n")
        body_elements: List[str] = []

        # Extraer notas al pie declaradas [^1]: o [1]:
        footnotes: Dict[str, str] = {}
        fn_pattern = re.compile(r"^\[(?:\^)?(\d+)\]:\s*(.+)$")

        filtered_lines: List[str] = []
        for line in lines:
            m = fn_pattern.match(line.strip())
            if m:
                footnotes[m.group(1)] = m.group(2).strip()
            else:
                filtered_lines.append(line)

        for line in filtered_lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Encabezados
            if stripped.startswith("# "):
                heading = cls.escape_latex(stripped[2:].strip())
                macro = r"\chapter" if doc_class == "book" else r"\section"
                body_elements.append(f"{macro}{{{heading}}}\n")
            elif stripped.startswith("## "):
                heading = cls.escape_latex(stripped[3:].strip())
                macro = r"\section" if doc_class == "book" else r"\subsection"
                body_elements.append(f"{macro}{{{heading}}}\n")
            elif stripped.startswith("### "):
                heading = cls.escape_latex(stripped[4:].strip())
                macro = r"\subsection" if doc_class == "book" else r"\subsubsection"
                body_elements.append(f"{macro}{{{heading}}}\n")
            elif stripped in ("---", "***", r"\pagebreak"):
                body_elements.append(r"\clearpage" + "\n")
            else:
                # Reemplazar referencias a notas al pie [^1] por \footnote{...}
                tokens: Dict[str, str] = {}
                def fn_sub(match: re.Match) -> str:
                    fn_id = match.group(1)
                    fn_txt = footnotes.get(fn_id, f"Nota {fn_id}")
                    tok = f"XXLATEXFN{len(tokens)}XX"
                    tokens[tok] = f"\\footnote{{{cls.escape_latex(fn_txt)}}}"
                    return tok

                p_marked = re.sub(r"\[(?:\^)?(\d+)\]", fn_sub, stripped)
                p_escaped = cls.escape_latex(p_marked)
                for tok, macro in tokens.items():
                    p_escaped = p_escaped.replace(tok, macro)
                body_elements.append(f"{p_escaped}\n")

        body_tex = "\n".join(body_elements)

        tex_document = f"""\\documentclass[{font_size},{paper_size}]{{{doc_class}}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage[spanish,es-nodecimaldot]{{babel}}
\\usepackage{{geometry}}
\\geometry{{margin=2.5cm}}
\\usepackage{{microtype}}
\\usepackage{{setspace}}
\\onehalfspacing
\\usepackage{{parskip}}
\\usepackage{{hyperref}}
\\hypersetup{{
    colorlinks=true,
    linkcolor=black,
    urlcolor=blue,
    citecolor=black
}}

\\title{{{esc_title}}}
\\author{{{esc_author}}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle
\\tableofcontents
\\clearpage

{body_tex}

\\end{{document}}
"""
        out_path.write_text(tex_document, encoding="utf-8")
        return out_path


class MarkdownExporter:
    """Exportador de MultiMarkdown (.md) con encabezado YAML y enlaces semánticos."""

    @classmethod
    def export(
        cls,
        text_content: str,
        destination_path: Union[str, Path],
        title: str = "Manuscrito",
        author: str = "Autor"
    ) -> Path:
        out_path = Path(destination_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        header = f"""---
title: "{title}"
author: "{author}"
date: "{cls._get_current_date()}"
generator: "Escritorio Publishing Engine"
---

"""
        full_content = header + text_content.strip() + "\n"
        AtomicStorage.write_atomic_text(out_path, full_content, encoding="utf-8")
        return out_path

    @staticmethod
    def _get_current_date() -> str:
        import datetime
        return datetime.date.today().isoformat()


class RTFExporter:
    """Exportador nativo de texto enriquecido (.rtf)."""

    @classmethod
    def export(
        cls,
        text_content: str,
        destination_path: Union[str, Path],
        font_family: str = "Times New Roman",
        font_size_pt: int = 12
    ) -> Path:
        out_path = Path(destination_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        rtf_data = RTFEngine.plain_text_to_rtf(
            text_content,
            font_name=font_family,
            font_size_pt=font_size_pt
        )
        AtomicStorage.write_atomic_text(out_path, rtf_data, encoding="utf-8")
        return out_path


class HTMLExporter:
    """Exportador HTML5 semántico de maquetación editorial responsiva."""

    @classmethod
    def export(
        cls,
        text_content: str,
        destination_path: Union[str, Path],
        title: str = "Manuscrito",
        author: str = "Autor"
    ) -> Path:
        out_path = Path(destination_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        esc_title = html.escape(title)
        esc_author = html.escape(author)

        lines = text_content.split("\n")
        body_elements: List[str] = []

        # Extraer notas al pie [^1]: texto
        footnotes: Dict[str, str] = {}
        fn_pattern = re.compile(r"^\[(?:\^)?(\d+)\]:\s*(.+)$")
        filtered_lines: List[str] = []

        for line in lines:
            m = fn_pattern.match(line.strip())
            if m:
                footnotes[m.group(1)] = m.group(2).strip()
            else:
                filtered_lines.append(line)

        for line in filtered_lines:
            stripped = line.strip()
            if not stripped:
                continue

            if stripped.startswith("# "):
                body_elements.append(f"<h1>{html.escape(stripped[2:].strip())}</h1>")
            elif stripped.startswith("## "):
                body_elements.append(f"<h2>{html.escape(stripped[3:].strip())}</h2>")
            elif stripped.startswith("### "):
                body_elements.append(f"<h3>{html.escape(stripped[4:].strip())}</h3>")
            elif stripped in ("---", "***", r"\pagebreak"):
                body_elements.append('<hr class="scene-divider"/>')
            else:
                def fn_replace(match: re.Match) -> str:
                    fn_id = match.group(1)
                    return f'<sup class="footnote-ref"><a href="#fn{fn_id}" id="ref{fn_id}">[{fn_id}]</a></sup>'

                p_escaped = html.escape(stripped)
                p_with_fn = re.sub(r"\[(?:\^)?(\d+)\]", fn_replace, p_escaped)
                # Restaurar etiquetas HTML generadas
                p_with_fn = re.sub(
                    r"&lt;sup class=&quot;footnote-ref&quot;&gt;&lt;a href=&quot;#fn(\d+)&quot; id=&quot;ref(\d+)&quot;&gt;\[(\d+)\]&lt;/a&gt;&lt;/sup&gt;",
                    r'<sup class="footnote-ref"><a href="#fn\1" id="ref\2">[\3]</a></sup>',
                    p_with_fn
                )
                body_elements.append(f"<p>{p_with_fn}</p>")

        # Añadir sección de notas al pie si existen
        if footnotes:
            body_elements.append('<section class="footnotes">')
            body_elements.append('<hr/><h3>Notas</h3><ol>')
            for fn_id, fn_text in footnotes.items():
                body_elements.append(
                    f'<li id="fn{fn_id}">{html.escape(fn_text)} <a href="#ref{fn_id}">&#8617;</a></li>'
                )
            body_elements.append('</ol></section>')

        body_html = "\n        ".join(body_elements)

        full_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc_title}</title>
    <style>
        body {{
            font-family: 'Georgia', 'Palatino', serif;
            line-height: 1.7;
            max-width: 780px;
            margin: 40px auto;
            padding: 0 25px;
            color: #222;
            background: #fdfdfd;
        }}
        header.title-block {{
            text-align: center;
            margin-bottom: 50px;
            padding-bottom: 30px;
            border-bottom: 1px solid #e0e0e0;
        }}
        h1.main-title {{
            font-size: 2.2em;
            letter-spacing: 0.05em;
            margin-bottom: 0.2em;
        }}
        p.author-byline {{
            font-size: 1.15em;
            color: #555;
            font-style: italic;
        }}
        h1, h2, h3 {{
            color: #111;
        }}
        p {{
            margin: 0 0 1em 0;
            text-align: justify;
            text-indent: 1.5em;
        }}
        p:first-of-type, h1 + p, h2 + p {{
            text-indent: 0;
        }}
        hr.scene-divider {{
            border: none;
            border-top: 1px solid #ccc;
            width: 30%;
            margin: 2.5em auto;
        }}
        .footnotes {{
            margin-top: 50px;
            font-size: 0.9em;
            color: #555;
        }}
        sup.footnote-ref a {{
            text-decoration: none;
            font-weight: bold;
            color: #0d47a1;
        }}
    </style>
</head>
<body>
    <header class="title-block">
        <h1 class="main-title">{esc_title}</h1>
        <p class="author-byline">Por {esc_author}</p>
    </header>
    <main>
        {body_html}
    </main>
</body>
</html>"""

        AtomicStorage.write_atomic_text(out_path, full_html, encoding="utf-8")
        return out_path
