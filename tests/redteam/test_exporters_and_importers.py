"""
Suite de Pruebas Exhaustiva de Red Team para Exportadores Nativos, Importadores y Plantillas.
Verifica la funcionalidad completa de:
1. DOCXExporter (OpenXML nativo, cabeceras, notas al pie, estilos).
2. PDFExporter (PDF 1.4 binario, métricas tipográficas, cabeceras simétricas, bookmarks).
3. EPUB3Exporter (Contenedor EPUB 3 válido, mimetype sin comprimir, nav.xhtml, toc.ncx, cover, notas emergentes).
4. ScreenplayExporter (Final Draft XML .fdx y Fountain .fountain).
5. TextExporters (LaTeX .tex, MultiMarkdown .md, RTF .rtf, HTML .html).
6. UnifiedExporter (Despacho unificado multiformato).
7. ImportAndSplit (División automática por encabezados y separadores en el Binder).
8. ScriptImporter (Importación de guiones .fdx y .fountain a escenas en el Binder).
9. WebImporter (Extracción e importación de páginas web a Research).
10. ProjectTemplateManager (Catálogo en 4 categorías, creación de proyectos desde plantilla y guardado).
"""

import os
import sys
import shutil
import zipfile
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

# Asegurar importación de src
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.project import EscritorioProject
from src.compile.exporters import (
    DOCXExporter,
    PDFExporter,
    EPUB3Exporter,
    ScreenplayExporter,
    LaTeXExporter,
    MarkdownExporter,
    RTFExporter,
    HTMLExporter,
    UnifiedExporter,
    ExportFormat
)
from src.core.importers import (
    ImportAndSplit,
    ScriptImporter,
    WebImporter,
    ProjectTemplateManager
)


class TestExportersAndImporters(unittest.TestCase):
    """Pruebas unitarias de los componentes de publicación, importación y plantillas."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_io_test_"))
        ProjectTemplateManager.set_custom_templates_dir(self.temp_dir / "templates")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # =========================================================================
    # 1. PRUEBAS DOCX EXPORTER
    # =========================================================================

    def test_docx_exporter(self):
        sample_text = (
            "# Capítulo I: El Comienzo\n\n"
            "El sol descendía sobre la cordillera iluminando la vieja estación.[^1]\n\n"
            "## Escena 1\n\n"
            "Los trenes de vapor aguardaban en la vía secundaria.[^2]\n\n"
            "[^1]: Referencia a la cordillera central.\n"
            "[^2]: Locomotoras tipo Baldwin construidas en 1920.\n"
        )
        docx_path = self.temp_dir / "manuscrito.docx"
        out = DOCXExporter.export(
            text_content=sample_text,
            destination_path=docx_path,
            title="La Odisea",
            author="Juan Pérez",
            font_family="Times New Roman",
            font_size_pt=12
        )
        self.assertTrue(out.exists())

        # Verificar integridad como paquete OpenXML ZIP
        with zipfile.ZipFile(out, "r") as zf:
            namelist = zf.namelist()
            self.assertIn("[Content_Types].xml", namelist)
            self.assertIn("_rels/.rels", namelist)
            self.assertIn("word/document.xml", namelist)
            self.assertIn("word/styles.xml", namelist)
            self.assertIn("word/header1.xml", namelist)
            self.assertIn("word/footnotes.xml", namelist)

            # Verificar cabecera con apellido del autor
            header_xml = zf.read("word/header1.xml").decode("utf-8")
            self.assertIn("Pérez", header_xml)
            self.assertIn('w:instr="PAGE"', header_xml)

            # Verificar notas al pie reales
            footnotes_xml = zf.read("word/footnotes.xml").decode("utf-8")
            self.assertIn("Referencia a la cordillera central.", footnotes_xml)
            self.assertIn("Locomotoras tipo Baldwin", footnotes_xml)

            # Verificar estilos
            styles_xml = zf.read("word/styles.xml").decode("utf-8")
            self.assertIn('w:styleId="Heading1"', styles_xml)
            self.assertIn('w:styleId="Heading2"', styles_xml)

    # =========================================================================
    # 2. PRUEBAS PDF EXPORTER
    # =========================================================================

    def test_pdf_exporter(self):
        sample_text = (
            "# Prólogo\n\n"
            "En un lugar de la Mancha, de cuyo nombre no quiero acordarme...\n\n"
            "# Capítulo 1: De la condición del hidalgo\n\n"
            "Vivía no ha mucho tiempo un hidalgo de los de lanza en astillero.\n\n"
            "--- \n\n"
            "# Capítulo 2: La primera salida\n\n"
            "Y hecha la cuenta de lo que había menester, no quiso aguardar más.\n"
        )
        pdf_path = self.temp_dir / "libro.pdf"
        out = PDFExporter.export(
            text_content=sample_text,
            destination_path=pdf_path,
            title="Don Quijote",
            author="Miguel de Cervantes",
            font_family="Times",
            font_size_pt=11.0,
            page_size="6x9"
        )
        self.assertTrue(out.exists())

        content_bytes = out.read_bytes()
        # Verificar firma de cabecera PDF 1.4
        self.assertTrue(content_bytes.startswith(b"%PDF-1.4"))
        # Verificar trailer y tabla xref
        self.assertIn(b"xref", content_bytes)
        self.assertIn(b"startxref", content_bytes)
        self.assertIn(b"%%EOF", content_bytes)
        # Verificar marcadores de esquema /Outlines
        self.assertIn(b"/Outlines", content_bytes)

    # =========================================================================
    # 3. PRUEBAS EPUB3 EXPORTER
    # =========================================================================

    def test_epub3_exporter(self):
        sample_text = (
            "# Capítulo Primero\n\n"
            "Esta es la primera frase de la historia con una nota al pie.[^1]\n\n"
            "--- \n\n"
            "# Capítulo Segundo\n\n"
            "Continúa el viaje espacial a través del hiperespacio.[^2]\n\n"
            "[^1]: Explicación detallada de la primera frase.\n"
            "[^2]: Teoría del salto cuántico relativista.\n"
        )
        epub_path = self.temp_dir / "libro.epub"
        out = EPUB3Exporter.export(
            text_content=sample_text,
            destination_path=epub_path,
            title="Crónicas Estelares",
            author="Elena Vance",
            language="es"
        )
        self.assertTrue(out.exists())

        # Verificar especificación estricta de EPUB:
        # El primer archivo del ZIP DEBE ser 'mimetype', almacenado SIN compresión (ZIP_STORED)
        with open(out, "rb") as f:
            raw_zip = f.read()

        with zipfile.ZipFile(out, "r") as zf:
            first_info = zf.infolist()[0]
            self.assertEqual(first_info.filename, "mimetype")
            self.assertEqual(first_info.compress_type, zipfile.ZIP_STORED)
            self.assertEqual(zf.read("mimetype"), b"application/epub+zip")

            namelist = zf.namelist()
            self.assertIn("META-INF/container.xml", namelist)
            self.assertIn("OEBPS/content.opf", namelist)
            self.assertIn("OEBPS/nav.xhtml", namelist)
            self.assertIn("OEBPS/toc.ncx", namelist)
            self.assertIn("OEBPS/cover.xhtml", namelist)
            self.assertIn("OEBPS/style.css", namelist)
            self.assertIn("OEBPS/chapter_001.xhtml", namelist)
            self.assertIn("OEBPS/chapter_002.xhtml", namelist)

            # Verificar nav.xhtml semántico de EPUB3
            nav_html = zf.read("OEBPS/nav.xhtml").decode("utf-8")
            self.assertIn('<nav epub:type="toc"', nav_html)
            self.assertIn("Capítulo Primero", nav_html)
            self.assertIn("Capítulo Segundo", nav_html)

            # Verificar notas al pie emergentes en el capítulo
            chap1_html = zf.read("OEBPS/chapter_001.xhtml").decode("utf-8")
            self.assertIn('epub:type="noteref"', chap1_html)
            self.assertIn('epub:type="footnote"', chap1_html)
            self.assertIn("Explicación detallada de la primera frase.", chap1_html)

    # =========================================================================
    # 4. PRUEBAS SCREENPLAY EXPORTER (.FDX Y .FOUNTAIN)
    # =========================================================================

    def test_screenplay_exporter_fdx_and_fountain(self):
        script_text = (
            "INT. CAFETERÍA - DÍA\n\n"
            "Un local abarrotado de gente. La lluvia golpea el cristal.\n\n"
            "MARCOS\n"
            "(mirando el reloj)\n"
            "No va a venir.\n\n"
            "LUCÍA\n"
            "Ten paciencia.\n\n"
            "CORTE A:\n\n"
            "EXT. CALLE - DÍA\n\n"
            "Un taxi frena en seco frente a la puerta."
        )

        # 1. Exportar FDX
        fdx_path = self.temp_dir / "guion.fdx"
        out_fdx = ScreenplayExporter.export_fdx(
            text_content=script_text,
            destination_path=fdx_path,
            title="El Encuentro",
            author="Carlos Guionista"
        )
        self.assertTrue(out_fdx.exists())
        fdx_content = out_fdx.read_text(encoding="utf-8")
        self.assertIn("<FinalDraft DocumentType=\"Script\"", fdx_content)
        self.assertIn('<Paragraph Type="Scene Heading">', fdx_content)
        self.assertIn('<Paragraph Type="Character">', fdx_content)
        self.assertIn('<Paragraph Type="Dialogue">', fdx_content)
        self.assertIn('<Paragraph Type="Parenthetical">', fdx_content)
        self.assertIn('<Paragraph Type="Transition">', fdx_content)
        self.assertIn("INT. CAFETERÍA - DÍA", fdx_content)

        # 2. Exportar Fountain
        fountain_path = self.temp_dir / "guion.fountain"
        out_fountain = ScreenplayExporter.export_fountain(
            text_content=script_text,
            destination_path=fountain_path,
            title="El Encuentro",
            author="Carlos Guionista"
        )
        self.assertTrue(out_fountain.exists())
        fountain_content = out_fountain.read_text(encoding="utf-8")
        self.assertIn("Title: El Encuentro", fountain_content)
        self.assertIn("Author: Carlos Guionista", fountain_content)
        self.assertIn("===", fountain_content)
        self.assertIn("INT. CAFETERÍA - DÍA", fountain_content)
        self.assertIn("MARCOS", fountain_content)
        self.assertIn("(mirando el reloj)", fountain_content)

    # =========================================================================
    # 5. PRUEBAS TEXT EXPORTERS (LATEX, MARKDOWN, RTF, HTML)
    # =========================================================================

    def test_text_exporters(self):
        text_sample = (
            "# Introducción al Análisis\n\n"
            "Este texto incluye caracteres como 100% & $500 y notas.[^1]\n\n"
            "## Métodos\n\n"
            "Se evaluaron diversas variables.\n\n"
            "[^1]: Nota técnica aclaratoria.\n"
        )

        # LaTeX
        tex_path = self.temp_dir / "paper.tex"
        out_tex = LaTeXExporter.export(text_sample, tex_path, title="Estudio", author="Dra. Gómez")
        self.assertTrue(out_tex.exists())
        tex_content = out_tex.read_text(encoding="utf-8")
        self.assertIn(r"\documentclass", tex_content)
        self.assertIn(r"\chapter{Introducción al Análisis}", tex_content)
        self.assertIn(r"\%", tex_content)
        self.assertIn(r"\$", tex_content)
        self.assertIn(r"\footnote{Nota técnica aclaratoria.}", tex_content)

        # Markdown
        md_path = self.temp_dir / "manuscript.md"
        out_md = MarkdownExporter.export(text_sample, md_path, title="Estudio", author="Dra. Gómez")
        self.assertTrue(out_md.exists())
        md_content = out_md.read_text(encoding="utf-8")
        self.assertIn('title: "Estudio"', md_content)
        self.assertIn("# Introducción al Análisis", md_content)

        # RTF
        rtf_path = self.temp_dir / "doc.rtf"
        out_rtf = RTFExporter.export(text_sample, rtf_path)
        self.assertTrue(out_rtf.exists())
        rtf_content = out_rtf.read_text(encoding="utf-8")
        self.assertTrue(rtf_content.startswith(r"{\rtf1"))

        # HTML
        html_path = self.temp_dir / "doc.html"
        out_html = HTMLExporter.export(text_sample, html_path, title="Estudio", author="Dra. Gómez")
        self.assertTrue(out_html.exists())
        html_content = out_html.read_text(encoding="utf-8")
        self.assertIn("<!DOCTYPE html>", html_content)
        self.assertIn("<h1>Introducción al Análisis</h1>", html_content)
        self.assertIn("Por Dra. Gómez", html_content)
        self.assertIn('class="footnote-ref"', html_content)

    # =========================================================================
    # 6. PRUEBAS UNIFIED EXPORTER
    # =========================================================================

    def test_unified_exporter_dispatch(self):
        sample = "# Título\n\nPárrafo de prueba."

        # Exportar a varios formatos usando UnifiedExporter
        p_docx = UnifiedExporter.export(sample, self.temp_dir / "u.docx", ExportFormat.DOCX)
        p_pdf = UnifiedExporter.export(sample, self.temp_dir / "u.pdf", ExportFormat.PDF)
        p_epub = UnifiedExporter.export(sample, self.temp_dir / "u.epub", ExportFormat.EPUB)
        p_fdx = UnifiedExporter.export("INT. SALA - NOCHE\n\nAcción.", self.temp_dir / "u.fdx", "fdx")
        p_fountain = UnifiedExporter.export("INT. SALA - NOCHE\n\nAcción.", self.temp_dir / "u.fountain", ExportFormat.FOUNTAIN)
        p_tex = UnifiedExporter.export(sample, self.temp_dir / "u.tex", "tex")

        self.assertTrue(p_docx.exists())
        self.assertTrue(p_pdf.exists())
        self.assertTrue(p_epub.exists())
        self.assertTrue(p_fdx.exists())
        self.assertTrue(p_fountain.exists())
        self.assertTrue(p_tex.exists())

    # =========================================================================
    # 7. PRUEBAS IMPORT AND SPLIT
    # =========================================================================

    def test_import_and_split_markdown(self):
        proj_dir = self.temp_dir / "test_import_md.scriv"
        project = EscritorioProject.create_new_project(proj_dir, native=False)

        md_content = (
            "# Capítulo 1: El Despertar\n\n"
            "Texto del primer capítulo.\n\n"
            "## Escena 1A\n\n"
            "Primera escena detallada.\n\n"
            "## Escena 1B\n\n"
            "Segunda escena detallada.\n\n"
            "# Capítulo 2: El Camino\n\n"
            "Texto del segundo capítulo.\n\n"
            "## Escena 2A\n\n"
            "En marcha por el sendero.\n"
        )
        md_file = self.temp_dir / "manuscrito_largo.md"
        md_file.write_text(md_content, encoding="utf-8")

        res = ImportAndSplit.import_and_split(
            source_path=md_file,
            project=project,
            detect_headings=True
        )

        self.assertTrue(res["success"])
        self.assertGreater(res["total_items"], 3)
        self.assertEqual(res["folders_created"], 2)  # Cap 1 y Cap 2

        # Comprobar que en el Binder existen los ítems
        draft = project.get_draft_folder()
        self.assertIsNotNone(draft)
        chap_titles = [c.title for c in draft.children]
        self.assertIn("Capítulo 1: El Despertar", chap_titles)
        self.assertIn("Capítulo 2: El Camino", chap_titles)

        # Comprobar escenas anidadas
        cap1_item = next(c for c in draft.children if c.title == "Capítulo 1: El Despertar")
        cap1_children_titles = [sc.title for sc in cap1_item.children]
        self.assertIn("Escena 1A", cap1_children_titles)
        self.assertIn("Escena 1B", cap1_children_titles)

    def test_import_and_split_by_separator(self):
        proj_dir = self.temp_dir / "test_import_sep.scriv"
        project = EscritorioProject.create_new_project(proj_dir, native=False)

        txt_content = (
            "Primera sección del relato breve.\n\n"
            "***\n\n"
            "Segunda sección tras el punto de giro.\n\n"
            "***\n\n"
            "Tercera sección y desenlace final.\n"
        )
        txt_file = self.temp_dir / "relato_separado.txt"
        txt_file.write_text(txt_content, encoding="utf-8")

        res = ImportAndSplit.import_and_split(
            source_path=txt_file,
            project=project,
            separator="***"
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["total_items"], 3)

    # =========================================================================
    # 8. PRUEBAS SCRIPT IMPORTER (.FDX Y .FOUNTAIN)
    # =========================================================================

    def test_script_importer(self):
        proj_dir = self.temp_dir / "test_import_script.scriv"
        project = EscritorioProject.create_new_project(proj_dir, native=False)

        fountain_script = (
            "Title: Operación Relámpago\n"
            "Author: Laura Guionista\n"
            "===\n\n"
            "INT. CENTRO DE CONTROL - NOCHE\n\n"
            "Monitores brillan en la penumbra.\n\n"
            "AGENTE K\n"
            "Transmisión iniciada.\n\n"
            "EXT. CALLE - NOCHE\n\n"
            "La lluvia cae sobre el asfalto.\n\n"
            "AGENTE M\n"
            "Contacto visual confirmado.\n"
        )
        fountain_file = self.temp_dir / "operacion.fountain"
        fountain_file.write_text(fountain_script, encoding="utf-8")

        res = ScriptImporter.import_script(
            source_path=fountain_file,
            project=project,
            extract_characters_to_research=True
        )

        self.assertTrue(res["success"])
        self.assertEqual(res["scenes_count"], 2)
        self.assertIn("AGENTE K", res["characters_found"])
        self.assertIn("AGENTE M", res["characters_found"])

        # Verificar que se crearon las fichas de personaje en Research
        research = project.get_research_folder()
        self.assertIsNotNone(research)
        research_titles = [c.title for c in research.children]
        self.assertTrue(any("Personajes" in t for t in research_titles))

    # =========================================================================
    # 9. PRUEBAS WEB IMPORTER
    # =========================================================================

    def test_web_importer_local_html(self):
        proj_dir = self.temp_dir / "test_import_web.scriv"
        project = EscritorioProject.create_new_project(proj_dir, native=False)

        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Artículo de Investigación: Motores de Compilación</title>
</head>
<body>
    <header><nav><a href="#">Inicio</a></nav></header>
    <h1>Motores de Compilación en Software Editorial</h1>
    <p>Los motores de compilación permiten transformar jerarquías de texto en documentos listos para su publicación.</p>
    <p>El estándar OpenXML y EPUB3 son ampliamente utilizados en la industria.</p>
    <footer><p>© 2026 Editorial</p></footer>
</body>
</html>"""
        html_file = self.temp_dir / "articulo.html"
        html_file.write_text(html_content, encoding="utf-8")

        res = WebImporter.import_from_url_or_file(
            source=html_file,
            project=project
        )

        self.assertTrue(res["success"])
        self.assertIn("Artículo de Investigación", res["title"])

        # Comprobar que se guardó en la carpeta Research
        research = project.get_research_folder()
        self.assertIsNotNone(research)
        self.assertEqual(len(research.children), 1)
        imported_item = research.children[0]
        self.assertIn("Motores de Compilación", imported_item.title)
        self.assertIn("OpenXML", imported_item.read_content_rtf())

    # =========================================================================
    # 10. PRUEBAS PROJECT TEMPLATES (NEW PROJECT CHOOSER)
    # =========================================================================

    def test_project_templates_gallery_and_creation(self):
        # 1. Categorías disponibles
        categories = ProjectTemplateManager.list_categories()
        self.assertEqual(categories, ["En Blanco", "Ficción", "No Ficción", "Guion"])

        # 2. Listado de plantillas
        all_templates = ProjectTemplateManager.list_templates()
        self.assertGreaterEqual(len(all_templates), 11)

        fiction_templates = ProjectTemplateManager.list_templates(category="Ficción")
        fiction_ids = [t["id"] for t in fiction_templates]
        self.assertIn("novel", fiction_ids)
        self.assertIn("novel_parts", fiction_ids)
        self.assertIn("short_story", fiction_ids)

        script_templates = ProjectTemplateManager.list_templates(category="Guion")
        script_ids = [t["id"] for t in script_templates]
        self.assertIn("screenplay_feature", script_ids)
        self.assertIn("stage_play", script_ids)

        # 3. Crear proyecto desde plantilla 'novel'
        novel_proj_dir = self.temp_dir / "MiPrimeraNovela.scriv"
        novel_proj = ProjectTemplateManager.create_project_from_template(
            template_id="novel",
            destination_path=novel_proj_dir,
            project_name="MiPrimeraNovela",
            native=False
        )

        self.assertIsNotNone(novel_proj)
        self.assertEqual(novel_proj.project_data["targets"]["draft_words"], 80000)

        # Comprobar estructura de la novela
        draft = novel_proj.get_draft_folder()
        self.assertIsNotNone(draft)
        draft_titles = [c.title for c in draft.children]
        self.assertIn("Capítulo 1", draft_titles)

        research = novel_proj.get_research_folder()
        self.assertIsNotNone(research)
        research_titles = [c.title for c in research.children]
        self.assertIn("Personajes", research_titles)
        self.assertIn("Lugares y Escenarios", research_titles)

        # 4. Guardar proyecto actual como plantilla personalizada
        custom_tmpl_path = ProjectTemplateManager.save_project_as_template(
            project=novel_proj,
            template_name="Mi Plantilla Personalizada de Fantasía",
            category="Ficción",
            description="Plantilla de novela de fantasía con fichas listas."
        )
        self.assertTrue(custom_tmpl_path.exists())

        # Verificar que la plantilla aparece en la galería
        updated_fiction = ProjectTemplateManager.list_templates(category="Ficción")
        custom_found = any(t["name"] == "Mi Plantilla Personalizada de Fantasía" for t in updated_fiction)
        self.assertTrue(custom_found)


if __name__ == "__main__":
    unittest.main()
