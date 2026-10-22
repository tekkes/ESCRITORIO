"""
Red Team Test Suite para el componente Inspector (InspectorWidget) en Escritorio.
Valida la paridad visual, interactividad y capacidades especializadas con Scrivener 3:
1. Cabecera de iconos compactos de 16px para alternar entre las 6 pestañas especializadas.
2. Pestaña 1 - Sinopsis y Notas:
   - Sincronización con Corcho y conmutador entre Sinopsis de texto e Imagen de escena (drag-and-drop).
   - Editor RTF de Notas del Documento (notes.rtf).
   - Pie fijo del Inspector con selectores rápidos de Label y Status.
3. Pestaña 2 - Marcadores:
   - Conmutador entre Marcadores del Documento y Marcadores del Proyecto.
   - Visor previsualizador y editor inferior para leer/editar referencias sin cambiar el editor principal.
4. Pestaña 3 - Metadatos:
   - Configuración general (Incluir en compilación, Tipo de sección).
   - Panel de Metadatos Personalizados con soporte de Texto, Checkbox, Lista y Fecha.
   - Panel de Palabras Clave con ventana flotante Project Keywords HUD para jerarquías y colores.
5. Pestaña 4 - Instantáneas (Snapshots / Ctrl+5 / Ctrl+Shift+5):
   - Toma de instantáneas rápidas y tituladas guardadas en Snapshots/<UUID>/.
   - Motor de Comparación Diferencial (Myers Diff) con palabras eliminadas en rojo tachado y añadidas en verde/azul subrayado.
   - Botón Rollback con opción de instantánea de seguridad previa.
6. Pestaña 5 - Comentarios y Notas al Pie:
   - Lista interactiva vinculada a selecciones de texto, color, autor y marca de tiempo.
   - Navegación bidireccional (clic en comentario localiza rango y viceversa).
   - Persistencia en XML content.comments.
7. Integración y retrocompatibilidad total con InspectorView y MainWindow (Ctrl+Shift+I).
"""

import unittest
import shutil
import tempfile
from pathlib import Path

from src.core.project import EscritorioProject, BinderItem
from src.core.rtf_engine import RTFEngine
from src.ui.InspectorWidget import (
    InspectorWidget,
    InspectorTabId,
    TAB_METADATA,
    MyersDiffEngine,
    DiffGranularity,
    DiffOp,
    TabNotesSynopsis,
    TabBookmarks,
    BookmarkScope,
    BookmarkItem,
    TabMetadata,
    CustomFieldType,
    CustomFieldDefinition,
    ProjectKeywordsHUD,
    TabSnapshots,
    SnapshotItem,
    TabCommentsFootnotes,
    CommentItem
)
from src.ui.inspector import InspectorView


class TestMyersDiffEngine(unittest.TestCase):
    """Pruebas exhaustivas para el motor de comparación diferencial (Myers Diff)."""

    def setUp(self):
        self.diff = MyersDiffEngine()

    def test_identical_texts(self):
        text = "La noche caía sobre las torres antiguas con una quietud espectral."
        chunks = self.diff.compute_diff(text, text, DiffGranularity.WORD)
        self.assertTrue(all(c.op == DiffOp.EQUAL for c in chunks))
        reconstructed = "".join(c.text for c in chunks)
        self.assertEqual(reconstructed, text)

    def test_word_insertion_and_deletion(self):
        old_text = "El gato negro descansaba en el tejado húmedo."
        new_text = "El gato blanco corría velozmente por el tejado seco."

        chunks = self.diff.compute_diff(old_text, new_text, DiffGranularity.WORD)
        self.assertGreater(len(chunks), 0)

        # Verificar presencia de inserciones y eliminaciones
        ops = [c.op for c in chunks]
        self.assertIn(DiffOp.DELETE, ops)
        self.assertIn(DiffOp.INSERT, ops)
        self.assertIn(DiffOp.EQUAL, ops)

        # Verificar HTML con colores Scrivener (#EF4444 para borrar, #10B981 para añadir)
        html = self.diff.render_html(chunks)
        self.assertIn("#EF4444", html)
        self.assertIn("line-through", html)
        self.assertIn("#10B981", html)
        self.assertIn("underline", html)

    def test_granularities(self):
        old_clause = "Primera cláusula. Segunda cláusula. Tercera cláusula."
        new_clause = "Primera cláusula. Segunda cláusula modificada. Tercera cláusula."

        chunks_clause = self.diff.compute_diff(old_clause, new_clause, DiffGranularity.CLAUSE)
        self.assertGreater(len(chunks_clause), 0)

        old_para = "Párrafo 1.\n\nPárrafo 2.\n\nPárrafo 3."
        new_para = "Párrafo 1.\n\nPárrafo 2 editado.\n\nPárrafo 3."
        chunks_para = self.diff.compute_diff(old_para, new_para, DiffGranularity.PARAGRAPH)
        self.assertGreater(len(chunks_para), 0)

        chunks_char = self.diff.compute_diff("abc", "axc", DiffGranularity.CHARACTER)
        ops_char = [c.op for c in chunks_char]
        self.assertIn(DiffOp.DELETE, ops_char)
        self.assertIn(DiffOp.INSERT, ops_char)

    def test_empty_strings(self):
        chunks1 = self.diff.compute_diff("", "Nuevo contenido", DiffGranularity.WORD)
        self.assertEqual(len(chunks1), 1)
        self.assertEqual(chunks1[0].op, DiffOp.INSERT)

        chunks2 = self.diff.compute_diff("Contenido viejo", "", DiffGranularity.WORD)
        self.assertEqual(len(chunks2), 1)
        self.assertEqual(chunks2[0].op, DiffOp.DELETE)


class TestTabNotesSynopsis(unittest.TestCase):
    """Pruebas para Pestaña 1: Sinopsis y Notas con pie fijo."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_tab_notes_"))
        self.project_path = self.temp_dir / "TestNotes.escr"
        self.project = EscritorioProject.create_new(self.project_path, "Test Notes", native=True)
        draft = self.project.get_draft_folder()
        self.item = self.project.add_item(draft.uuid, "Escena Niebla", item_type="Text")
        self.project.save_structure()

        self.tab = TabNotesSynopsis(self.project)
        self.tab.set_item(self.item)

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_synopsis_text_persistence(self):
        self.tab.set_synopsis("Isabel llega a la ciudad vieja en plena noche de tormenta.")
        self.assertEqual(self.tab.get_synopsis(), "Isabel llega a la ciudad vieja en plena noche de tormenta.")

        # Verificar persistencia en disco a través del BinderItem
        loaded = self.item.read_synopsis()
        self.assertEqual(loaded, "Isabel llega a la ciudad vieja en plena noche de tormenta.")

    def test_synopsis_image_mode_toggle_and_drag_drop(self):
        self.assertFalse(self.tab.is_image_mode)
        self.tab.toggle_image_mode()
        self.assertTrue(self.tab.is_image_mode)

        # Crear archivo de imagen simulado
        fake_image = self.temp_dir / "portada_escena.png"
        fake_image.write_bytes(b"\x89PNG\r\n\x1a\nfakeimagecontent")

        assigned_path = self.tab.set_scene_image(str(fake_image))
        self.assertIsNotNone(assigned_path)
        self.assertTrue(Path(assigned_path).exists())

    def test_notes_rtf_editing_and_persistence(self):
        rtf_content = r"{\rtf1\ansi Recordar la campana de la iglesia a las doce.}"
        self.tab.set_notes_rtf(rtf_content)
        self.assertEqual(self.tab.get_notes_rtf(), rtf_content)

        # Verificar persistencia física en notes.rtf
        loaded_notes = self.item.read_notes_rtf()
        self.assertEqual(loaded_notes, rtf_content)

    def test_fixed_footer_label_and_status(self):
        self.tab.set_label(2)
        self.assertEqual(self.item.data.label_id, 2)

        self.tab.set_status(3)
        self.assertEqual(self.item.data.status_id, 3)

        footer = self.tab.get_footer_state()
        self.assertEqual(footer["label_id"], 2)
        self.assertEqual(footer["status_id"], 3)


class TestTabBookmarks(unittest.TestCase):
    """Pruebas para Pestaña 2: Marcadores con visor previsualizador inferior."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_tab_bookmarks_"))
        self.project_path = self.temp_dir / "TestBookmarks.escr"
        self.project = EscritorioProject.create_new(self.project_path, "Test Bookmarks", native=True)
        draft = self.project.get_draft_folder()
        self.item1 = self.project.add_item(draft.uuid, "Documento Principal", item_type="Text")
        self.item2 = self.project.add_item(draft.uuid, "Ficha Personaje: Isabel", item_type="Text")
        self.item2.write_content_rtf(r"{\rtf1\ansi Isabel: 28 anos, investigadora de la orden.}")
        self.item2.save_if_dirty()
        self.project.save_structure()

        self.tab = TabBookmarks(self.project)
        self.tab.set_item(self.item1)

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scope_switcher(self):
        self.assertEqual(self.tab.current_scope, BookmarkScope.DOCUMENT)
        self.tab.set_scope(BookmarkScope.PROJECT)
        self.assertEqual(self.tab.current_scope, BookmarkScope.PROJECT)
        self.tab.toggle_scope()
        self.assertEqual(self.tab.current_scope, BookmarkScope.DOCUMENT)

    def test_add_and_filter_bookmarks(self):
        # Añadir marcador de documento
        bm_doc = self.tab.add_bookmark(self.item2.uuid, title="Ficha Isabel", scope=BookmarkScope.DOCUMENT)
        self.assertIsNotNone(bm_doc)

        # Añadir marcador de proyecto
        bm_proj = self.tab.add_bookmark(self.item1.uuid, title="Doc Principal", scope=BookmarkScope.PROJECT)
        self.assertIsNotNone(bm_proj)

        # Filtrar por documento
        self.tab.set_scope(BookmarkScope.DOCUMENT)
        doc_list = self.tab.get_current_bookmarks()
        self.assertEqual(len(doc_list), 1)
        self.assertEqual(doc_list[0].title, "Ficha Isabel")

        # Filtrar por proyecto
        self.tab.set_scope(BookmarkScope.PROJECT)
        proj_list = self.tab.get_current_bookmarks()
        self.assertEqual(len(proj_list), 1)
        self.assertEqual(proj_list[0].title, "Doc Principal")

    def test_live_preview_viewer_read_and_edit_without_switching_main_editor(self):
        bm = self.tab.add_bookmark(self.item2.uuid, title="Ficha Isabel", scope=BookmarkScope.DOCUMENT)
        self.tab.select_bookmark(bm.id)

        # Leer contenido de referencia en visor inferior
        preview_text = self.tab.get_preview_content()
        self.assertIn("Isabel", preview_text)

        # Editar contenido en el visor de referencia integrado
        new_text = "Isabel: 29 anos, ascendida a custodia mayor."
        self.tab.update_preview_content(new_text)

        # Verificar que el documento referenciado se actualizó
        self.assertEqual(self.tab.get_preview_content(), new_text)


class TestTabMetadata(unittest.TestCase):
    """Pruebas para Pestaña 3: Metadatos, Custom Metadata y Keywords HUD."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_tab_metadata_"))
        self.project_path = self.temp_dir / "TestMeta.escr"
        self.project = EscritorioProject.create_new(self.project_path, "Test Meta", native=True)
        draft = self.project.get_draft_folder()
        self.item = self.project.add_item(draft.uuid, "Capitulo 1", item_type="Text")
        self.project.save_structure()

        self.tab = TabMetadata(self.project)
        self.tab.set_item(self.item)

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_general_metadata(self):
        self.assertTrue(self.tab.get_include_in_compile())
        self.tab.set_include_in_compile(False)
        self.assertFalse(self.tab.get_include_in_compile())

        self.tab.set_section_type("Capítulo de Novela")
        self.assertEqual(self.tab.get_section_type(), "Capítulo de Novela")

    def test_custom_metadata_definitions_and_values(self):
        # 1. Campo de Texto
        self.tab.add_custom_field("f_pov", "POV", CustomFieldType.TEXT)
        self.tab.set_custom_value("f_pov", "Isabel")
        self.assertEqual(self.tab.get_custom_value("f_pov"), "Isabel")

        # 2. Campo Checkbox
        self.tab.add_custom_field("f_rev", "Revisión Estilo", CustomFieldType.CHECKBOX)
        self.tab.set_custom_value("f_rev", True)
        self.assertEqual(self.tab.get_custom_value("f_rev"), "True")

        # 3. Campo Lista
        self.tab.add_custom_field("f_int", "Intensidad", CustomFieldType.LIST, options=["Baja", "Media", "Alta", "Clímax"])
        self.tab.set_custom_value("f_int", "Alta")
        self.assertEqual(self.tab.get_custom_value("f_int"), "Alta")

        # 4. Campo Fecha
        self.tab.add_custom_field("f_date", "Fecha Histórica", CustomFieldType.DATE)
        self.tab.set_custom_value("f_date", "1894-10-22")
        self.assertEqual(self.tab.get_custom_value("f_date"), "1894-10-22")

    def test_project_keywords_hud_and_hierarchies(self):
        hud = self.tab.keywords_hud
        self.assertIsNotNone(hud)

        # Crear jerarquía de palabras clave con colores
        hud.add_keyword("Personajes", "#3B82F6")
        hud.add_keyword("Isabel", "#60A5FA", parent_id="kw-personajes")
        hud.add_keyword("Lugares", "#10B981")

        all_kws = {k.name: k for k in hud.get_all()}
        self.assertIn("Personajes", all_kws)
        self.assertIn("Isabel", all_kws)
        self.assertEqual(all_kws["Isabel"].parent_id, "kw-personajes")
        self.assertEqual(all_kws["Isabel"].color_hex, "#60A5FA")

        # Asignar palabra clave al documento
        self.tab.add_keyword("Isabel")
        self.assertIn("Isabel", self.tab.get_keywords())

        # Desasignar
        self.tab.remove_keyword("Isabel")
        self.assertNotIn("Isabel", self.tab.get_keywords())


class TestTabSnapshots(unittest.TestCase):
    """Pruebas para Pestaña 4: Instantáneas, Myers Diff y Rollback."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_tab_snapshots_"))
        self.project_path = self.temp_dir / "TestSnap.escr"
        self.project = EscritorioProject.create_new(self.project_path, "Test Snapshots", native=True)
        draft = self.project.get_draft_folder()
        self.item = self.project.add_item(draft.uuid, "Manuscrito Escena", item_type="Text")
        self.item.write_content_rtf(r"{\rtf1\ansi Version 1: La niebla cubria las viejas calles.}")
        self.item.save_if_dirty()
        self.project.save_structure()

        self.tab = TabSnapshots(self.project)
        self.tab.set_item(self.item)

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_take_snapshots_and_directory_structure(self):
        # Tomar instantánea rápida
        snap1 = self.tab.take_snapshot()
        self.assertIsNotNone(snap1)
        self.assertTrue(snap1.id)

        # Tomar instantánea con título personalizado (Ctrl+Shift+5)
        snap2 = self.tab.take_snapshot_with_title("Fin del Primer Acto")
        self.assertEqual(snap2.title, "Fin del Primer Acto")

        # Verificar almacenamiento físico bajo Files/Snapshots/<UUID>/
        snapshots_dir = self.tab._get_snapshots_dir()
        self.assertTrue(snapshots_dir.exists())
        self.assertTrue((snapshots_dir / "snapshots.json").exists())
        self.assertTrue((snapshots_dir / f"{snap1.id}.rtf").exists())
        self.assertTrue((snapshots_dir / f"{snap2.id}.rtf").exists())

    def test_myers_diff_comparison_view(self):
        # Versión 1 en snapshot
        self.item.write_content_rtf(r"{\rtf1\ansi El reloj dio las diez en la torre.}")
        self.item.save_if_dirty()
        snap = self.tab.take_snapshot(title="Versión Antigua")

        # Versión 2 actual en editor
        current_text = "El gran reloj dio las doce en la torre catedralicia."
        self.item.write_content_rtf(f"{{\\rtf1\\ansi {current_text}}}")
        self.item.save_if_dirty()

        # Ejecutar comparación diferencial
        self.tab.select_snapshot(snap.id)
        html_diff = self.tab.get_diff_html()
        self.assertIsNotNone(html_diff)

        # Verificar que el HTML contiene eliminaciones tachadas en rojo y adiciones subrayadas en verde
        self.assertIn("#EF4444", html_diff)
        self.assertIn("#10B981", html_diff)

    def test_rollback_with_safety_snapshot(self):
        self.item.write_content_rtf(r"{\rtf1\ansi Texto Original de la Escena.}")
        self.item.save_if_dirty()
        snap_orig = self.tab.take_snapshot(title="Version Original")

        # Modificación agresiva posterior
        self.item.write_content_rtf(r"{\rtf1\ansi Texto Completamente Reescribido Incorrectamente.}")
        self.item.save_if_dirty()

        # Ejecutar Rollback solicitando instantánea de seguridad
        restored = self.tab.rollback(snap_orig.id, create_safety_snapshot=True)
        self.assertTrue(restored)

        # Verificar que el texto actual volvió al original
        current_doc = self.item.read_content_rtf()
        self.assertIn("Texto Original de la Escena", current_doc)

        # Verificar que se creó la instantánea de seguridad
        snaps = self.tab.snapshots
        titles = [s.title for s in snaps]
        self.assertTrue(any("Seguridad" in t for t in titles))


class TestTabCommentsFootnotes(unittest.TestCase):
    """Pruebas para Pestaña 5: Comentarios interactivos y Notas al pie."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_tab_comments_"))
        self.project_path = self.temp_dir / "TestComments.escr"
        self.project = EscritorioProject.create_new(self.project_path, "Test Comments", native=True)
        draft = self.project.get_draft_folder()
        self.item = self.project.add_item(draft.uuid, "Documento con Comentarios", item_type="Text")
        self.item.write_content_rtf(r"{\rtf1\ansi En 1894, la catedral iluminaba la plaza mayor con farolas de gas.}")
        self.item.save_if_dirty()
        self.project.save_structure()

        self.tab = TabCommentsFootnotes(self.project)
        self.tab.set_item(self.item)

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_comment_and_footnote(self):
        comm = self.tab.add_comment(
            text="Verificar precisión histórica del alumbrado público.",
            start_offset=35,
            length=23,
            author="Revisor",
            color_hex="#FEF08A"
        )
        self.assertIsNotNone(comm)
        self.assertEqual(comm.item_type, "Comment")
        self.assertEqual(comm.author, "Revisor")

        fn = self.tab.add_footnote(
            text="La catedral fue concluida en el siglo XV.",
            start_offset=8,
            length=8
        )
        self.assertIsNotNone(fn)
        self.assertEqual(fn.item_type, "Footnote")

        self.assertEqual(len(self.tab.comments), 2)

    def test_bidirectional_navigation_and_offset_lookup(self):
        c1 = self.tab.add_comment("Comentario A", start_offset=10, length=10)
        c2 = self.tab.add_comment("Comentario B", start_offset=50, length=20)

        # 1. Localizar comentario a partir del offset del cursor del editor
        match1 = self.tab.find_comment_at_offset(15)
        self.assertIsNotNone(match1)
        self.assertEqual(match1.id, c1.id)

        match2 = self.tab.find_comment_at_offset(62)
        self.assertIsNotNone(match2)
        self.assertEqual(match2.id, c2.id)

        self.assertIsNone(self.tab.find_comment_at_offset(35))

        # 2. Al seleccionar un comentario en la lista, recuperar rango de selección exacto
        sel_range = self.tab.select_comment(c2.id)
        self.assertEqual(sel_range, (50, 20))

    def test_xml_persistence_in_content_comments(self):
        self.tab.add_comment("Nota de revisión", start_offset=0, length=10, author="Isabel", color_hex="#FCA5A5")
        self.tab.add_footnote("Referencia bibliográfica", start_offset=20, length=10)
        self.tab.save_comments_to_xml()

        # Verificar lectura física del XML
        xml_str = self.item.read_comments_xml()
        self.assertIn("<Comments", xml_str)
        self.assertIn("Nota de revisión", xml_str)
        self.assertIn("Referencia bibliográfica", xml_str)

        # Crear una nueva instancia y verificar que carga los comentarios del XML
        new_tab = TabCommentsFootnotes(self.project)
        new_tab.set_item(self.item)
        self.assertEqual(len(new_tab.comments), 2)
        self.assertEqual(new_tab.comments[0].text, "Nota de revisión")
        self.assertEqual(new_tab.comments[1].item_type, "Footnote")


class TestInspectorWidgetIntegration(unittest.TestCase):
    """Pruebas de orquestación, barra de iconos de 16px, atajos y retrocompatibilidad."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_inspector_widget_"))
        self.project_path = self.temp_dir / "TestOrchestrator.escr"
        self.project = EscritorioProject.create_new(self.project_path, "Test Orchestrator", native=True)
        draft = self.project.get_draft_folder()
        self.item = self.project.add_item(draft.uuid, "Escena Principal", item_type="Text")
        self.project.save_structure()

        self.inspector = InspectorWidget(self.project)
        self.inspector.set_item(self.item)

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compact_16px_header_tabs(self):
        tabs = self.inspector.get_tabs_metadata()
        self.assertGreaterEqual(len(tabs), 5)
        tab_ids = [t["id"] for t in tabs]
        self.assertIn(InspectorTabId.NOTES_SYNOPSIS.value, tab_ids)
        self.assertIn(InspectorTabId.BOOKMARKS.value, tab_ids)
        self.assertIn(InspectorTabId.METADATA.value, tab_ids)
        self.assertIn(InspectorTabId.SNAPSHOTS.value, tab_ids)
        self.assertIn(InspectorTabId.COMMENTS_FOOTNOTES.value, tab_ids)

        # Cambiar de pestaña activa
        self.inspector.set_tab(InspectorTabId.SNAPSHOTS.value)
        self.assertEqual(self.inspector.active_tab, InspectorTabId.SNAPSHOTS.value)

    def test_visibility_toggle_ctrl_shift_i(self):
        self.assertTrue(self.inspector.is_visible)
        self.inspector.toggle_visibility()
        self.assertFalse(self.inspector.is_visible)
        self.inspector.toggle_visibility()
        self.assertTrue(self.inspector.is_visible)

    def test_telemetry_view_data(self):
        view_data = self.inspector.to_dict()
        self.assertTrue(view_data["visible"])
        self.assertEqual(view_data["item_uuid"], self.item.uuid)
        self.assertIn("tabs_header", view_data)

    def test_backward_compatibility_with_inspector_view(self):
        # InspectorView hereda de InspectorWidget
        view = InspectorView(self.project)
        view.set_item(self.item)
        self.assertIsInstance(view, InspectorWidget)

        # Verificar alias de métodos clásicos
        view.set_tab("notes")
        self.assertEqual(view.active_tab, InspectorTabId.NOTES_SYNOPSIS.value)

        view.set_tab("comments")
        self.assertEqual(view.active_tab, InspectorTabId.COMMENTS_FOOTNOTES.value)


if __name__ == "__main__":
    unittest.main()
