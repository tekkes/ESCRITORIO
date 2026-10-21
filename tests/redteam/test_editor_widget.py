"""
Red Team Test Suite para EditorWidget y StyleEngine de Escritorio.
Valida la paridad funcional total respecto a Scrivener 3:
1. Formato de texto enriquecido RTF, barra de formato compacta y regla horizontal (Ruler).
2. Tablas editables, listas, imágenes y Scrivener Links internos ([[Título]]).
3. Sistema de Estilos Semánticos (StyleEngine) con "Sin Estilo" por defecto y persistencia XML.
4. Vista de Página (Page View / Alt+Shift+P) frente a modo continuo.
5. Desplazamiento de Máquina de Escribir (Typewriter Scrolling / Ctrl+Alt+T).
6. Modo Foco (Línea, Oración, Párrafo).
7. Foco Lingüístico (Diálogos, Adverbios, Adjetivos, Verbos, Conjunciones).
8. Caracteres Invisibles (¶, ·, →).
"""

import unittest
import shutil
import tempfile
from pathlib import Path

from src.core.project import EscritorioProject
from src.core.rtf_engine import RTFEngine
from src.core.StyleEngine import StyleEngine, StyleDefinition, StyleType
from src.ui.EditorWidget import (
    EditorWidget,
    FormatToolbar,
    TextFormatState,
    RulerBar,
    PageViewEngine,
    EditorViewMode,
    PageFormat,
    LinguisticFocusEngine,
    LinguisticCategory,
    FocusModeEngine,
    FocusScope,
    InvisiblesEngine,
    ScrivenerLinksEngine,
    TableManager
)


class TestEditorWidget(unittest.TestCase):

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_editor_"))
        self.project_path = self.temp_dir / "TestEditorProject.escr"
        self.project = EscritorioProject.create_new(self.project_path, "Proyecto Editor", native=True)
        self.editor = EditorWidget(self.project)

    def tearDown(self):
        if hasattr(self, "project") and self.project:
            self.project.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_rich_text_formatting_and_toolbar(self):
        """Verifica la barra de formato: fuente, tamaño, estilos, colores y alineación."""
        tb = self.editor.toolbar

        # Modificación de fuente y tamaño
        tb.set_font_family("Georgia")
        self.assertEqual(tb.state.font_family, "Georgia")
        tb.set_font_size(14.0)
        self.assertEqual(tb.state.font_size_pt, 14.0)

        # Alternar negrita, cursiva, subrayado, tachado
        self.assertTrue(tb.toggle_bold())
        self.assertTrue(tb.toggle_italic())
        self.assertTrue(tb.toggle_underline())
        self.assertTrue(tb.toggle_strikethrough())

        # Superíndice y subíndice mutuamente excluyentes
        self.assertTrue(tb.toggle_superscript())
        self.assertTrue(tb.state.superscript)
        self.assertFalse(tb.state.subscript)
        self.assertTrue(tb.toggle_subscript())
        self.assertTrue(tb.state.subscript)
        self.assertFalse(tb.state.superscript)

        # Colores de texto y resaltador
        tb.set_text_color("#1A2B3C")
        self.assertEqual(tb.state.text_color, "#1A2B3C")
        tb.set_highlight_color("#FFFF00")  # Amarillo
        self.assertEqual(tb.state.highlight_color, "#FFFF00")

        # Alineación e interlineado
        tb.set_alignment("justify")
        self.assertEqual(tb.state.alignment, "justify")
        tb.set_line_spacing(1.5)
        self.assertEqual(tb.state.line_spacing, 1.5)

        # Espaciado de párrafo
        tb.set_paragraph_spacing(6.0, 12.0)
        self.assertEqual(tb.state.space_before_pt, 6.0)
        self.assertEqual(tb.state.space_after_pt, 12.0)

        # Comprobar render data
        render_data = tb.get_render_data()
        self.assertEqual(render_data["font_family"], "Georgia")
        self.assertEqual(render_data["alignment"], "justify")
        self.assertIn("Naranja", [h["name"] for h in render_data["highlighters"]])

    def test_interactive_ruler_bar(self):
        """Verifica la regla horizontal (Ctrl+Shift+R), sangrías, márgenes y conversiones."""
        ruler = self.editor.ruler

        # Visibilidad (Ctrl+Shift+R)
        initial_vis = ruler.state.is_visible
        self.assertEqual(self.editor.toggle_ruler(), not initial_vis)
        self.assertEqual(self.editor.toggle_ruler(), initial_vis)

        # Sangría de primera línea y márgenes
        ruler.set_first_line_indent(36.0)  # 36 pt = 0.5 in
        ruler.set_left_indent(18.0)
        ruler.set_right_indent(18.0)
        self.assertEqual(ruler.state.first_line_indent_pt, 36.0)
        self.assertEqual(ruler.state.left_indent_pt, 18.0)

        # Conversiones de unidad (pt -> cm, in)
        ruler.state.unit = "in"
        self.assertAlmostEqual(ruler.state.pt_to_unit(72.0), 1.0, places=2)
        ruler.state.unit = "cm"
        self.assertAlmostEqual(ruler.state.pt_to_unit(28.3465), 1.0, places=2)

        # Tabuladores
        ruler.clear_tab_stops()
        ruler.add_tab_stop(72.0, "left")
        ruler.add_tab_stop(144.0, "center")
        ruler.add_tab_stop(216.0, "decimal")
        self.assertEqual(len(ruler.state.tab_stops), 3)
        self.assertTrue(ruler.remove_tab_stop(1))
        self.assertEqual(len(ruler.state.tab_stops), 2)

    def test_scrivener_style_engine_semantic_system(self):
        """Verifica el sistema de estilos con 'Sin Estilo' por defecto, presets y persistencia XML."""
        engine = self.editor.style_engine

        # 1. 'Sin Estilo' es el estilo por defecto inmutable
        default_style = engine.get_default_style()
        self.assertEqual(default_style.name, "Sin Estilo")
        self.assertEqual(default_style.style_type, StyleType.NONE)
        self.assertTrue(default_style.is_default)
        self.assertFalse(engine.delete_style(default_style.id))  # No se puede eliminar

        # 2. Estilos predefinidos canónicos de Scrivener
        h1 = engine.get_style_by_name("Título 1")
        self.assertIsNotNone(h1)
        self.assertEqual(h1.style_type, StyleType.PARAGRAPH)
        self.assertEqual(h1.font_size, 18.0)
        self.assertTrue(h1.bold)

        quote = engine.get_style_by_name("Cita en bloque")
        self.assertIsNotNone(quote)
        self.assertEqual(quote.style_type, StyleType.COMBINED)
        self.assertTrue(quote.italic)
        self.assertEqual(quote.left_indent, 36.0)

        code = engine.get_style_by_name("Código")
        self.assertIsNotNone(code)
        self.assertEqual(code.style_type, StyleType.CHARACTER)
        self.assertEqual(code.font_family, "Consolas")

        # 3. Crear estilo desde la selección activa
        self.editor.toolbar.set_font_family("Palatino Linotype")
        self.editor.toolbar.set_font_size(13.0)
        self.editor.toolbar.state.italic = True
        self.editor.ruler.set_left_indent(40.0)

        new_style = self.editor.create_style_from_selection(
            name="Voz Interior",
            style_type=StyleType.COMBINED,
            shortcut="Ctrl+Alt+I"
        )
        self.assertEqual(new_style.name, "Voz Interior")
        self.assertEqual(new_style.font_family, "Palatino Linotype")
        self.assertEqual(new_style.left_indent, 40.0)

        # 4. Redefinir estilo desde la selección
        self.editor.toolbar.set_font_size(15.0)
        redefined = self.editor.redefine_style_from_selection(new_style.id)
        self.assertIsNotNone(redefined)
        self.assertEqual(redefined.font_size, 15.0)

        # 5. Persistencia y recarga desde Settings/styles.xml
        styles_file = engine.get_styles_file()
        self.assertTrue(styles_file.exists())

        fresh_engine = StyleEngine(self.project.project_dir)
        loaded_style = fresh_engine.get_style(new_style.id)
        self.assertIsNotNone(loaded_style)
        self.assertEqual(loaded_style.name, "Voz Interior")
        self.assertEqual(loaded_style.font_size, 15.0)

    def test_page_view_and_typewriter_scrolling(self):
        """Verifica la Vista de Página (Alt+Shift+P) y el desplazamiento de Máquina de Escribir (Ctrl+Alt+T)."""
        draft = self.project.get_draft_folder()
        doc = self.project.add_item(draft.uuid, "Capítulo 1", item_type="Text")
        self.editor.load_item(doc)

        # Generar texto largo (~4000 caracteres)
        sample_paragraph = (
            "La lluvia caía sin descanso sobre los tejados de la ciudadela. "
            "Isabel observaba las luces distantes a través del cristal empañado, "
            "sabiendo que el amanecer traería noticias inevitables.\n\n"
        )
        full_text = sample_paragraph * 20
        self.editor.update_text(full_text)

        # 1. Modo Continuo vs Vista de Página (Alt+Shift+P)
        self.assertEqual(self.editor.page_view.mode, EditorViewMode.CONTINUOUS)
        new_mode = self.editor.toggle_page_view()
        self.assertEqual(new_mode, EditorViewMode.PAGE_VIEW)
        self.assertTrue(self.editor.page_view.get_render_data()["is_page_view"])

        # Paginación calculada
        total_pages = len(self.editor.page_view.pages)
        self.assertGreaterEqual(total_pages, 2)

        # Cursor en la mitad del texto debe dar la página correcta
        half_pos = len(full_text) // 2
        page_at_cursor = self.editor.page_view.get_current_page_for_cursor(half_pos)
        self.assertGreaterEqual(page_at_cursor, 1)
        self.assertLessEqual(page_at_cursor, total_pages)

        # 2. Desplazamiento de Máquina de Escribir (Ctrl+Alt+T)
        self.assertFalse(self.editor.focus_mode.typewriter_scrolling)
        self.assertTrue(self.editor.toggle_typewriter_scrolling())
        self.assertTrue(self.editor.focus_mode.typewriter_scrolling)

        # Cálculo de offset de desplazamiento centrado al 50%
        offset = self.editor.focus_mode.calculate_typewriter_scroll_offset(
            cursor_line_index=20,
            line_height_px=24.0,
            viewport_height_px=600.0
        )
        self.assertGreater(offset, 0.0)

    def test_focus_mode_scopes(self):
        """Verifica el Modo Foco en ámbitos de Línea, Oración y Párrafo."""
        text = (
            "Primera oración del texto. Segunda oración con misterio. Tercera oración conclusiva.\n\n"
            "Segundo párrafo comienza aquí. Continúa con detalles cruciales. Termina aquí.\n\n"
            "Tercer párrafo final."
        )

        # 1. Foco en Línea
        self.editor.set_focus_mode(FocusScope.LINE)
        cursor_pos = text.find("misterio")
        start, end = self.editor.focus_mode.get_focused_span(text, cursor_pos)
        focused_text = text[start:end]
        self.assertIn("Segunda oración con misterio", focused_text)

        # 2. Foco en Oración
        self.editor.set_focus_mode(FocusScope.SENTENCE)
        start, end = self.editor.focus_mode.get_focused_span(text, cursor_pos)
        focused_sentence = text[start:end].strip()
        self.assertEqual(focused_sentence, "Segunda oración con misterio.")

        # 3. Foco en Párrafo
        self.editor.set_focus_mode(FocusScope.PARAGRAPH)
        cursor_p2 = text.find("detalles cruciales")
        start, end = self.editor.focus_mode.get_focused_span(text, cursor_p2)
        focused_para = text[start:end].strip()
        self.assertTrue(focused_para.startswith("Segundo párrafo comienza"))
        self.assertTrue(focused_para.endswith("Termina aquí."))

    def test_linguistic_focus_analyzer(self):
        """Verifica el análisis de Diálogos, Adverbios, Adjetivos, Verbos y Conjunciones."""
        text = (
            "«No podemos rendirnos tan fácilmente», susurró ella con voz temblorosa.\n"
            "—Es verdad —respondió él tranquilamente—, aunque la noche sea profundamente oscura.\n"
            "El viejo puente de madera crujía bajo sus pies cansados y hambrientos."
        )

        lf = self.editor.linguistic_focus

        # 1. Diálogos Directos (comillas latinas y rayas)
        dialogue_spans = lf.analyze(text, LinguisticCategory.DIALOGUES)
        self.assertGreaterEqual(len(dialogue_spans), 2)
        dialogue_tokens = [s.token for s in dialogue_spans]
        self.assertTrue(any("«No podemos rendirnos" in t for t in dialogue_tokens))
        self.assertTrue(any("—Es verdad" in t for t in dialogue_tokens))

        # 2. Adverbios (-mente y léxicos)
        adverb_spans = lf.analyze(text, LinguisticCategory.ADVERBS)
        adverb_tokens = [s.token.lower() for s in adverb_spans]
        self.assertIn("fácilmente", adverb_tokens)
        self.assertIn("tranquilamente", adverb_tokens)
        self.assertIn("profundamente", adverb_tokens)

        # 3. Adjetivos (-oso, viejo, cansados)
        adj_spans = lf.analyze(text, LinguisticCategory.ADJECTIVES)
        adj_tokens = [s.token.lower() for s in adj_spans]
        self.assertTrue(any("temblorosa" in t for t in adj_tokens))
        self.assertTrue(any("viejo" in t for t in adj_tokens) or any("oscura" in t for t in adj_tokens))

        # 4. Conjunciones (aunque, y)
        conj_spans = lf.analyze(text, LinguisticCategory.CONJUNCTIONS)
        conj_tokens = [s.token.lower() for s in conj_spans]
        self.assertIn("aunque", conj_tokens)
        self.assertIn("y", conj_tokens)

    def test_invisibles_tables_and_scrivener_links(self):
        """Verifica Caracteres Invisibles, Tablas editables y enlaces Scrivener."""
        draft = self.project.get_draft_folder()
        doc_dest = self.project.add_item(draft.uuid, "Ficha de Personaje: Isabel", item_type="Text")
        doc_main = self.project.add_item(draft.uuid, "Capítulo 2", item_type="Text")

        self.editor.load_item(doc_main)
        self.editor.update_text("Texto inicial con espacios\ty saltos.\nSegunda línea.")

        # 1. Caracteres Invisibles (¶, ·, →)
        self.editor.toggle_invisibles()
        self.assertTrue(self.editor.invisibles.is_visible)
        rendered_inv = self.editor.invisibles.render_text_with_invisibles(self.editor.plain_text)
        self.assertIn("·", rendered_inv)
        self.assertIn("→", rendered_inv)
        self.assertIn("¶", rendered_inv)

        # 2. Inserción de Tablas editables
        table = self.editor.insert_table(rows=3, cols=2, cell_width_pt=120.0)
        self.assertEqual(table.row_count, 3)
        self.assertEqual(table.col_count, 2)
        TableManager.add_row(table)
        self.assertEqual(table.row_count, 4)
        rtf_table = TableManager.table_to_rtf(table)
        self.assertIn(r"\trowd", rtf_table)
        self.assertIn(r"\cellx", rtf_table)

        # 3. Inserción de Hipervínculos Internos Scrivener ([[Título]] / scrivener-link://)
        self.editor.insert_scrivener_link(doc_dest.uuid, "Ver Isabel")
        self.editor.insert_wiki_link("Ficha de Personaje: Isabel")

        # Resolución automática de enlaces hacia el documento de destino
        links = ScrivenerLinksEngine.find_all_links(self.editor.plain_text, self.project)
        self.assertGreaterEqual(len(links), 2)

        # Resolución por Wiki-link [[Título]]
        resolved_uuid = ScrivenerLinksEngine.resolve_link_destination(
            "[[Ficha de Personaje: Isabel]]",
            self.project
        )
        self.assertEqual(resolved_uuid, doc_dest.uuid)

        # Manejo de click en enlace
        clicked_dest = self.editor.handle_link_click(f"scrivener-link://{doc_dest.uuid}")
        self.assertEqual(clicked_dest, doc_dest.uuid)


if __name__ == "__main__":
    unittest.main()
