"""
Red Team Test Suite: Compile Engine, Section Layouts Mapper, Placeholders & 3-Column Compile Dialog.
Verifica de forma exhaustiva todos los requisitos de Scrivener 3:
1. Interfaz de 3 Columnas del Diálogo de Compilación (Formats, Section Layouts, Contents/Metadata/Replacements).
2. Diseñador de Formatos de Compilación (Compile Format Designer).
3. Evaluador completo de variables y comodines (Placeholders: <$n>, <$r>, <$R>, <$t>, <$T>, <$w>, <$W>, <$hn>, <$rst_n>).
4. Gestor de Separadores editoriales (Separators).
5. Motor de Compilación unificado con Front/Back Matter, filtros, transformaciones y exportación multiformato.
"""

import unittest
import tempfile
from pathlib import Path

from src.core.project import EscritorioProject
from src.core.rtf_engine import RTFEngine
from src.compile.CompileEngine.models import (
    CompileFormat, SectionLayout, BookMetadata, CompileFilterConfig,
    CompileReplacementRule, PageSize, PageOrientation, PageMargins,
    create_builtin_formats
)
from src.compile.CompileEngine.placeholders import (
    PlaceholderResolver, int_to_roman, int_to_words_es
)
from src.compile.CompileEngine.separators import (
    SeparatorType, SectionSeparators, SeparatorsManager
)
from src.compile.CompileEngine.section_layouts import (
    SectionLayoutEngine, SectionLayoutType
)
from src.compile.CompileEngine.format_designer import CompileFormatDesigner
from src.compile.CompileEngine.engine import CompileEngine, CompileConfig
from src.compile.exporters import ExportFormat

from src.ui.CompileDialog import (
    CompileDialog, RightPanelTab, FormatsColumn, FormatCategory,
    SectionLayoutsColumn, ContentsTab, MetadataTab, ReplacementsTab
)
from src.ui.main_window import MainWindow


class TestPlaceholderResolverComprehensive(unittest.TestCase):
    """Pruebas exhaustivas para el Evaluador de Variables y Comodines (Placeholders)."""

    def setUp(self):
        self.resolver = PlaceholderResolver({
            "title": "La Ciudad y las Estrellas",
            "author": "Arthur C. Clarke"
        })

    def test_roman_numerals_conversion(self):
        self.assertEqual(int_to_roman(1, uppercase=True), "I")
        self.assertEqual(int_to_roman(4, uppercase=True), "IV")
        self.assertEqual(int_to_roman(9, uppercase=True), "IX")
        self.assertEqual(int_to_roman(14, uppercase=True), "XIV")
        self.assertEqual(int_to_roman(40, uppercase=True), "XL")
        self.assertEqual(int_to_roman(90, uppercase=True), "XC")
        self.assertEqual(int_to_roman(2026, uppercase=True), "MMXXVI")
        self.assertEqual(int_to_roman(4, uppercase=False), "iv")
        self.assertEqual(int_to_roman(8, uppercase=False), "viii")

    def test_words_conversion_spanish(self):
        self.assertEqual(int_to_words_es(1, capitalize=False), "uno")
        self.assertEqual(int_to_words_es(1, capitalize=True), "Uno")
        self.assertEqual(int_to_words_es(15, capitalize=False), "quince")
        self.assertEqual(int_to_words_es(21, capitalize=True), "Veintiuno")
        self.assertEqual(int_to_words_es(35, capitalize=False), "treinta y cinco")
        self.assertEqual(int_to_words_es(100, capitalize=True), "Cien")
        self.assertEqual(int_to_words_es(105, capitalize=False), "ciento cinco")

    def test_arabic_and_roman_counters(self):
        text = "Capítulo <$n>, Libro <$R>, Escena <$r>, Siguiente <$n>"
        resolved = self.resolver.resolve(text)
        self.assertEqual(resolved, "Capítulo 1, Libro II, Escena iii, Siguiente 4")

    def test_word_counters(self):
        text = "Capítulo <$T>: El principio. En palabras minúsculas: <$t>. Cardinal: <$W>"
        resolved = self.resolver.resolve(text)
        self.assertEqual(resolved, "Capítulo Uno: El principio. En palabras minúsculas: dos. Cardinal: Tres")

    def test_hierarchical_numbering(self):
        self.resolver.reset_counters()
        # Nivel 1 -> 1
        h1 = self.resolver.resolve("Sección <$hn>", depth=1)
        self.assertEqual(h1, "Sección 1")
        # Nivel 2 -> 1.1
        h2 = self.resolver.resolve("Subsección <$hn>", depth=2)
        self.assertEqual(h2, "Subsección 1.1")
        # Nivel 2 -> 1.2
        h3 = self.resolver.resolve("Subsección <$hn>", depth=2)
        self.assertEqual(h3, "Subsección 1.2")
        # Nivel 3 -> 1.2.1
        h4 = self.resolver.resolve("Punto <$hn>", depth=3)
        self.assertEqual(h4, "Punto 1.2.1")
        # Vuelta a Nivel 1 -> 2
        h5 = self.resolver.resolve("Nueva Sección <$hn>", depth=1)
        self.assertEqual(h5, "Nueva Sección 2")
        # Nivel 2 bajo 2 -> 2.1
        h6 = self.resolver.resolve("Subsección <$hn>", depth=2)
        self.assertEqual(h6, "Subsección 2.1")

    def test_reset_counters(self):
        text1 = "Cap <$n> y <$n>"
        self.assertEqual(self.resolver.resolve(text1), "Cap 1 y 2")
        # Reiniciar contador
        text2 = "<$rst_n>Cap <$n>"
        self.assertEqual(self.resolver.resolve(text2), "Cap 1")

    def test_named_counters(self):
        text = "Figura <$n:fig>, Tabla <$n:tbl>, Figura <$n:fig>"
        resolved = self.resolver.resolve(text)
        self.assertEqual(resolved, "Figura 1, Tabla 1, Figura 2")

    def test_metadata_and_document_placeholders(self):
        text = (
            "Obra: <$projecttitle> | Autor: <$author>\n"
            "Capítulo: <$title>\n"
            "Sinopsis: <$synopsis>\n"
            "Notas: <$notes>\n"
            "Palabras: <$wc>"
        )
        resolved = self.resolver.resolve(
            text,
            item_title="El Despertar",
            item_synopsis="El protagonista descubre la nave.",
            item_notes="Revisar ritmo del diálogo.",
            word_count=3500
        )
        self.assertIn("La Ciudad y las Estrellas", resolved)
        self.assertIn("Arthur C. Clarke", resolved)
        self.assertIn("El Despertar", resolved)
        self.assertIn("El protagonista descubre la nave.", resolved)
        self.assertIn("Revisar ritmo del diálogo.", resolved)
        self.assertIn("3.500", resolved)


class TestSeparatorsAndSectionLayouts(unittest.TestCase):
    """Pruebas para el Gestor de Separadores y Diseños de Sección."""

    def test_separator_formatting(self):
        seps = SectionSeparators(
            before_section=SeparatorType.PAGE_BREAK,
            between_sections=SeparatorType.CUSTOM_SYMBOL,
            custom_between="* * *"
        )
        # Primera sección -> before_section
        boundary_first = SeparatorsManager.format_boundary(
            prev_type=None,
            current_type="Chapter",
            current_separators=seps,
            is_first_section=True
        )
        self.assertEqual(boundary_first, SeparatorsManager.PAGE_BREAK_TEXT)

        # Mismo tipo -> between_sections (* * *)
        boundary_same = SeparatorsManager.format_boundary(
            prev_type="Chapter",
            current_type="Chapter",
            current_separators=seps,
            is_first_section=False
        )
        self.assertIn("* * *", boundary_same)

        # Distinto tipo -> before_section
        boundary_diff = SeparatorsManager.format_boundary(
            prev_type="Part",
            current_type="Chapter",
            current_separators=seps,
            is_first_section=False
        )
        self.assertEqual(boundary_diff, SeparatorsManager.PAGE_BREAK_TEXT)

    def test_section_layout_formatting(self):
        layout = SectionLayout(
            id="test_layout",
            name="Capítulo Completo",
            title_prefix="CAPÍTULO <$n>: ",
            title_uppercase=True,
            title_centered=True,
            include_title=True,
            include_body=True,
            include_synopsis=True
        )
        formatted = SectionLayoutEngine.format_with_layout(
            layout=layout,
            title="el gran viaje",
            body="Texto de la escena.",
            synopsis="Resumen breve.",
            chapter_index=1
        )
        self.assertIn("CAPÍTULO <$n>: EL GRAN VIAJE", formatted)
        self.assertIn("<center>", formatted)
        self.assertIn("Sinopsis:", formatted)
        self.assertIn("Texto de la escena.", formatted)


class TestCompileFormatDesigner(unittest.TestCase):
    """Pruebas para el Diseñador de Formatos de Compilación."""

    def test_duplicate_and_modify_format(self):
        builtins = create_builtin_formats()
        source = builtins["manuscript_standard"]

        designer = CompileFormatDesigner.duplicate_format(source, new_name="Mi Manuscrito Editorial")
        self.assertEqual(designer.current_format.name, "Mi Manuscrito Editorial")
        self.assertFalse(designer.current_format.is_builtin)
        self.assertTrue(designer.current_format.is_project_format)

        # Modificar tipografía y página
        designer.set_typography("Georgia", 11, 1.5, 18.0)
        designer.set_page_settings(PageSize.PAPERBACK_6X9, PageOrientation.PORTRAIT)
        self.assertEqual(designer.current_format.font_family, "Georgia")
        self.assertEqual(designer.current_format.font_size_pt, 11)
        self.assertEqual(designer.current_format.page_size, PageSize.PAPERBACK_6X9)

        # Añadir regla de reemplazo
        designer.add_replacement_rule("--", "—", is_regex=False)
        self.assertEqual(len(designer.current_format.replacements), 1)

    def test_format_json_serialization(self):
        designer = CompileFormatDesigner()
        designer.set_general_info("Formato Prueba", "Descripción", "pdf")
        designer.add_replacement_rule("Dr\\.", "Doctor", is_regex=True)

        data = designer.to_dict()
        self.assertEqual(data["name"], "Formato Prueba")
        self.assertEqual(data["target_format"], "pdf")

        # Cargar de vuelta desde el diccionario
        reloaded = CompileFormatDesigner.from_dict(data)
        self.assertEqual(reloaded.current_format.name, "Formato Prueba")
        self.assertEqual(len(reloaded.current_format.replacements), 1)
        self.assertEqual(reloaded.current_format.replacements[0].pattern, "Dr\\.")


class TestCompileEnginePipeline(unittest.TestCase):
    """Pruebas de integración del pipeline completo de compilación."""

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.proj_path = Path(self.test_dir.name) / "TestBook.scriv"
        self.project = EscritorioProject.create_new(self.proj_path, title="Crónicas Marcianas")

        # Configurar estructura del manuscrito
        draft = self.project.root_items[0]

        # Capítulo 1
        self.ch1 = self.project.add_item(draft.uuid, "Ylla", item_type="Folder")
        self.ch1.data.section_type = "Chapter"
        self.ch1.write_synopsis("Historia de Ylla y el señor K.")

        # Escena 1.1
        self.sc1 = self.project.add_item(self.ch1.uuid, "El Valle Dormido", item_type="Text")
        self.sc1.data.section_type = "Scene"
        self.sc1.write_content_rtf(RTFEngine.plain_text_to_rtf("Tenían una casa de columnas de cristal junto al mar vacío..."))

        # Escena 1.2
        self.sc2 = self.project.add_item(self.ch1.uuid, "La Nave Dorada", item_type="Text")
        self.sc2.data.section_type = "Scene"
        self.sc2.write_content_rtf(RTFEngine.plain_text_to_rtf("Un sueño extraño la despertó a medianoche -- dijo ella."))

    def tearDown(self):
        self.test_dir.cleanup()

    def test_full_pipeline_assembly(self):
        engine = CompileEngine(self.project, "modern_novel")
        compiled = engine.assemble_manuscript()

        # Debe contener la numeración en palabras de 'modern_novel' (<$T>)
        self.assertIn("Uno", compiled)
        self.assertIn("Ylla", compiled)
        self.assertIn("Tenían una casa de columnas de cristal", compiled)
        # Debe contener el separador * * * entre escenas
        self.assertIn("* * *", compiled)
        # Transformación em-dash: '--' -> '—'
        self.assertIn("medianoche — dijo ella", compiled)
        # Transformación elipsis: '...' -> '…'
        self.assertIn("mar vacío…", compiled)

    def test_export_to_markdown_and_html(self):
        engine = CompileEngine(self.project, "manuscript_standard")
        md_file = Path(self.test_dir.name) / "Output.md"
        engine.compile_and_export(md_file, ExportFormat.MARKDOWN)
        self.assertTrue(md_file.exists())
        self.assertGreater(md_file.stat().st_size, 50)

        html_file = Path(self.test_dir.name) / "Output.html"
        engine.compile_and_export(html_file, ExportFormat.HTML)
        self.assertTrue(html_file.exists())
        self.assertGreater(html_file.stat().st_size, 100)


class TestCompileDialogThreeColumns(unittest.TestCase):
    """Pruebas para la interfaz de 3 Columnas de CompileDialog (Ctrl+Shift+E)."""

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.proj_path = Path(self.test_dir.name) / "DialogBook.scriv"
        self.project = EscritorioProject.create_new(self.proj_path, title="El Fin de la Eternidad")
        draft = self.project.root_items[0]
        c1 = self.project.add_item(draft.uuid, "Capítulo Inicial", item_type="Folder")
        c1.data.section_type = "Chapter"
        s1 = self.project.add_item(c1.uuid, "Elevador Temporal", item_type="Text")
        s1.data.section_type = "Scene"
        s1.write_content_rtf(RTFEngine.plain_text_to_rtf("Andrew Harlan entró en la cápsula."))

        self.dialog = CompileDialog(self.project)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_column_1_formats_selection_and_designer(self):
        # 7 formatos predefinidos cargados
        formats = self.dialog.formats_column.get_formats_list()
        self.assertGreaterEqual(len(formats), 7)

        # Seleccionar Novela Moderna
        ok = self.dialog.formats_column.select_format("modern_novel")
        self.assertTrue(ok)
        self.assertEqual(self.dialog.formats_column.current_format.name, "Novela Moderna")

        # Duplicar formato
        custom_fmt = self.dialog.formats_column.duplicate_current_format("Novela Personalizada")
        self.assertEqual(custom_fmt.name, "Novela Personalizada")
        self.assertIn(custom_fmt.id, self.dialog.formats_column.project_formats)

        # Abrir Diseñador de Formatos
        designer = self.dialog.formats_column.open_format_designer()
        self.assertTrue(self.dialog.formats_column.is_designer_open)
        self.assertIsNotNone(designer)
        self.dialog.formats_column.close_designer()
        self.assertFalse(self.dialog.formats_column.is_designer_open)

    def test_column_2_section_layouts_mapping(self):
        mappings = self.dialog.section_layouts_column.get_mapping_items()
        self.assertGreater(len(mappings), 0)

        # Reasignar 'Chapter'
        available = self.dialog.section_layouts_column.get_available_layouts_list()
        if available:
            target_layout_id = available[0]["id"]
            assigned = self.dialog.section_layouts_column.assign_layout("Chapter", target_layout_id)
            self.assertTrue(assigned)
            self.assertEqual(self.dialog.section_layouts_column.section_mappings["Chapter"], target_layout_id)

    def test_column_3_tabs_and_compilation(self):
        # Pestaña Contenidos
        self.dialog.switch_tab(RightPanelTab.CONTENTS)
        tree = self.dialog.contents_tab.get_compilation_tree()
        self.assertGreater(len(tree), 0)
        self.assertIn("Elevador Temporal", [item["title"] for item in tree])

        # Pestaña Metadatos
        self.dialog.switch_tab(RightPanelTab.METADATA)
        self.dialog.metadata_tab.update_field("isbn", "978-84-9999-000-1")
        self.assertEqual(self.dialog.metadata_tab.metadata.isbn, "978-84-9999-000-1")

        # Pestaña Reemplazos
        self.dialog.switch_tab(RightPanelTab.REPLACEMENTS)
        self.dialog.replacements_tab.add_rule("cápsula", "nave temporal")
        self.assertEqual(len(self.dialog.replacements_tab.rules), 1)

        # Compilar en memoria
        output_text = self.dialog.compile()
        self.assertIn("Andrew Harlan entró en la nave temporal", output_text)

    def test_main_window_toggle_compile_dialog(self):
        win = MainWindow(self.project)
        self.assertFalse(win.compile_dialog.is_open)

        # Conmutar Ctrl+Shift+E
        is_open = win.toggle_compile_dialog()
        self.assertTrue(is_open)
        self.assertTrue(win.compile_dialog.is_open)

        # Conmutar de nuevo para cerrar
        is_open = win.toggle_compile_dialog()
        self.assertFalse(is_open)
        self.assertFalse(win.compile_dialog.is_open)


if __name__ == "__main__":
    unittest.main()
