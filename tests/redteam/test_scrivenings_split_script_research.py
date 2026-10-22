"""
Red Team Test Suite para Modo Scrivenings, Pantalla Dividida (Split Screen),
Modo Escritura de Guiones y Visores Integrados de Investigación en Escritorio.
Valida la paridad funcional total respecto a Scrivener 3:
1. Modo Scrivenings (Ctrl+1): concatenación virtual continua, separadores configurables,
   títulos in-situ y guardado atómico en content.rtf por ítem.
2. Pantalla Dividida (Ctrl+', Ctrl+", Grid 4), Bloqueo de Editor (Lock in Place / Ctrl+Shift+L),
   navegación cruzada y ventanas flotantes Quick Reference (QR).
3. Modo Escritura de Guiones (Ctrl+8): transiciones automáticas con Tab y Enter para Cine,
   Teatro y Cómic, selector de elemento y autocompletado inteligente.
4. Visores de Investigación: PDFViewer (zoom, búsqueda, páginas), ImageViewer (zoom, rotación),
   TranscriptionPlayer (play/pause, retroceso 5s, marcas de tiempo), WebArchiveViewer (Reader Mode)
   y ResearchViewerRouter.
"""

import unittest
import shutil
import tempfile
from pathlib import Path

from src.core.project import EscritorioProject, BinderItem
from src.core.rtf_engine import RTFEngine
from src.ui.ScriveningsEngine import (
    ScriveningsEngine,
    ScriveningsSection,
    DividerStyle,
    ScriveningsDivider
)
from src.ui.SplitEditorManager import (
    SplitEditorManager,
    SplitLayoutMode,
    EditorPane,
    PaneContentType,
    QuickReferenceManager,
    QuickReferenceWindow
)
from src.ui.ScriptwritingMode import (
    ScriptwritingEngine,
    ScriptFormat,
    ScriptElementType,
    SCREENPLAY_RULES,
    ScriptAutocomplete
)
from src.ui.ResearchViewers import (
    PDFViewer,
    ImageViewer,
    TranscriptionPlayer,
    WebArchiveViewer,
    ResearchViewerRouter
)
from src.ui.main_window import MainWindow, CentralViewMode


class TestScriveningsSplitScriptResearch(unittest.TestCase):

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_escritorio_prompt07_"))
        self.project_path = self.temp_dir / "ProyectoPrompt07.escr"
        self.project = EscritorioProject.create_new(self.project_path, "Test Prompt 07 Project", native=True)

        # Crear estructura de prueba en el Binder:
        # Manuscrito > Cap. 1 > Escena 1.1 y Escena 1.2
        draft = self.project.get_draft_folder()
        self.cap1 = self.project.add_item(draft.uuid, "Capítulo 1: El Inicio", item_type="Folder")
        self.escena1 = self.project.add_item(self.cap1.uuid, "Escena 1.1: El Callejón", item_type="Text")
        self.escena2 = self.project.add_item(self.cap1.uuid, "Escena 1.2: La Puerta Oculta", item_type="Text")

        # Asignar textos iniciales a cada escena
        self.escena1.write_content_rtf(RTFEngine.plain_text_to_rtf("La niebla espesa cubría los adoquines húmedos de la ciudad vieja."))
        self.escena1.save_if_dirty()

        self.escena2.write_content_rtf(RTFEngine.plain_text_to_rtf("Una llave dorada colgaba del marco de piedra carcomido por el tiempo."))
        self.escena2.save_if_dirty()

    def tearDown(self):
        if hasattr(self, "project") and self.project:
            self.project.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # =========================================================================
    # 1. PRUEBAS DE MODO SCRIVENINGS (VISTA COMPUESTA CONTINUA)
    # =========================================================================

    def test_scrivenings_virtual_concatenation_and_dividers(self):
        """Verifica la concatenación virtual de carpetas y selección de separadores."""
        engine = ScriveningsEngine(self.project)

        # Cargar la carpeta 'Capítulo 1' (debe incluir recursivamente Escena 1.1 y Escena 1.2)
        engine.load_from_binder_items([self.cap1])
        self.assertTrue(engine.is_active)
        # La carpeta y sus 2 escenas
        self.assertGreaterEqual(len(engine.sections), 2)

        # Verificar presencia de los textos y títulos en el flujo compuesto continuo
        comp_text = engine.composite_text
        self.assertIn("La niebla espesa", comp_text)
        self.assertIn("Una llave dorada", comp_text)
        self.assertIn("Escena 1.1: El Callejón", comp_text)
        self.assertIn("Escena 1.2: La Puerta Oculta", comp_text)

        # Probar separadores: Línea Sutil
        engine.set_divider_style(DividerStyle.SUBTLE_LINE)
        self.assertIn("─", engine.composite_text)

        # Probar separadores: Esquinas Recortadas (Corner Cuts)
        engine.set_divider_style(DividerStyle.CORNER_CUTS)
        self.assertIn("✂", engine.composite_text)

        # Probar separadores: Salto de Página (Page Break)
        engine.set_divider_style(DividerStyle.PAGE_BREAK)
        self.assertIn("\f", engine.composite_text)

    def test_scrivenings_in_situ_title_editing(self):
        """Verifica que editar el título in-situ actualiza el BinderItem sin recargar todo."""
        engine = ScriveningsEngine(self.project)
        engine.load_from_binder_items([self.escena1, self.escena2])

        new_title = "Escena 1.1: El Callejón de las Sombras (Renombrado)"
        ok = engine.edit_section_title(self.escena1.uuid, new_title)
        self.assertTrue(ok)

        # Comprobar actualización en el ítem del Binder
        self.assertEqual(self.escena1.title, new_title)
        # Comprobar actualización en el texto compuesto
        self.assertIn(new_title, engine.composite_text)

    def test_scrivenings_transparent_content_saving(self):
        """
        Verifica que modificar cualquier parte del flujo continuo se sincroniza
        y persiste de forma individual en el content.rtf del nodo correspondiente.
        """
        engine = ScriveningsEngine(self.project)
        engine.load_from_binder_items([self.escena1, self.escena2])

        sec1 = engine.get_section_by_uuid(self.escena1.uuid)
        self.assertIsNotNone(sec1)

        # Modificar el contenido de la Escena 1.1
        nuevo_texto_1 = "La niebla espesa se disipó cuando el reloj de la catedral marcó las doce."
        engine.edit_section_content(self.escena1.uuid, nuevo_texto_1, auto_save=True)

        # Verificar que el archivo individual content.rtf de la Escena 1.1 se actualizó en disco
        rtf_disco_1 = self.escena1.read_content_rtf()
        self.assertIn("reloj de la catedral", RTFEngine.rtf_to_plain_text(rtf_disco_1))

        # Verificar que la Escena 1.2 permanece INTACTA
        rtf_disco_2 = self.escena2.read_content_rtf()
        self.assertIn("Una llave dorada", RTFEngine.rtf_to_plain_text(rtf_disco_2))
        self.assertNotIn("reloj de la catedral", RTFEngine.rtf_to_plain_text(rtf_disco_2))

        # Métricas totales
        self.assertGreater(engine.get_total_word_count(), 10)
        self.assertGreater(engine.get_total_character_count(), 50)

    # =========================================================================
    # 2. PRUEBAS DE PANTALLA DIVIDIDA, LOCK IN PLACE Y QUICK REFERENCE
    # =========================================================================

    def test_split_screen_modes_vertical_horizontal_grid(self):
        """Verifica la división en vertical (Ctrl+'), horizontal (Ctrl+\") y cuadrícula de 4."""
        mgr = SplitEditorManager(self.project)

        # Estado inicial
        self.assertEqual(mgr.layout_mode, SplitLayoutMode.SINGLE)
        self.assertEqual(len(mgr.get_visible_pane_ids()), 1)

        # División vertical (Ctrl+')
        mgr.split_vertical()
        self.assertEqual(mgr.layout_mode, SplitLayoutMode.VERTICAL)
        self.assertEqual(mgr.get_visible_pane_ids(), ["pane_0", "pane_1"])

        # División horizontal (Ctrl+\")
        mgr.split_horizontal()
        self.assertEqual(mgr.layout_mode, SplitLayoutMode.HORIZONTAL)
        self.assertEqual(mgr.get_visible_pane_ids(), ["pane_0", "pane_1"])

        # Cuadrícula de 4 paneles
        mgr.split_grid()
        self.assertEqual(mgr.layout_mode, SplitLayoutMode.GRID_4)
        self.assertEqual(mgr.get_visible_pane_ids(), ["pane_0", "pane_1", "pane_2", "pane_3"])

        # Cierre de división
        mgr.close_split()
        self.assertEqual(mgr.layout_mode, SplitLayoutMode.SINGLE)
        self.assertEqual(mgr.get_visible_pane_ids(), ["pane_0"])

    def test_lock_in_place_prevents_binder_override(self):
        """
        Verifica que Bloquear Editor (Lock in Place / Ctrl+Shift+L) impide que los clics
        en el Binder modifiquen el panel bloqueado, redirigiéndolos al otro panel.
        """
        mgr = SplitEditorManager(self.project)
        mgr.split_vertical()

        pane0 = mgr.panes["pane_0"]
        pane1 = mgr.panes["pane_1"]

        # Cargar escena 1 en pane_0
        mgr.set_active_pane("pane_0")
        mgr.load_item_from_binder(self.escena1)
        self.assertEqual(pane0.editor.current_item.uuid, self.escena1.uuid)

        # BLOQUEAR pane_0 (Lock in Place / Ctrl+Shift+L)
        mgr.toggle_lock_active_pane()
        self.assertTrue(pane0.is_locked)
        self.assertTrue(mgr.is_active_locked())

        # Ahora hacer clic en el Binder sobre escena 2
        # Como pane_0 está bloqueado, debe cargarse automáticamente en pane_1
        target_pane = mgr.load_item_from_binder(self.escena2)
        self.assertEqual(target_pane.pane_id, "pane_1")
        self.assertEqual(pane1.editor.current_item.uuid, self.escena2.uuid)

        # Comprobar que pane_0 SIGUE mostrando la escena 1 sin alterarse
        self.assertEqual(pane0.editor.current_item.uuid, self.escena1.uuid)

        # Si bloqueamos también pane_1 y hacemos clic en el Binder, ningún panel se sobreescribe
        pane1.set_lock(True)
        res = mgr.load_item_from_binder(self.escena1)
        self.assertIsNone(res)

    def test_navigate_affects_other_editor(self):
        """Verifica que la opción 'Navegación afecta al otro editor' rutea hacia el panel opuesto."""
        mgr = SplitEditorManager(self.project)
        mgr.split_vertical()

        pane0 = mgr.panes["pane_0"]
        pane1 = mgr.panes["pane_1"]

        mgr.set_active_pane("pane_0")
        mgr.load_item_from_binder(self.escena1)

        # Activar 'Navegación afecta al otro editor' en pane_0
        mgr.toggle_navigate_affects_other("pane_0")
        self.assertTrue(pane0.navigate_affects_other)

        # Al seleccionar escena 2 mientras pane_0 está activo, debe ir directamente a pane_1
        routed = mgr.load_item_from_binder(self.escena2)
        self.assertEqual(routed.pane_id, "pane_1")
        self.assertEqual(pane1.editor.current_item.uuid, self.escena2.uuid)
        self.assertEqual(pane0.editor.current_item.uuid, self.escena1.uuid)

    def test_quick_reference_floating_windows(self):
        """Verifica las ventanas flotantes Quick Reference (QR) multi-monitor."""
        qr_mgr = QuickReferenceManager(self.project)

        # Abrir documento en ventana flotante
        win1 = qr_mgr.open_document(self.escena1, geometry=(200, 200, 700, 500))
        self.assertIsNotNone(win1)
        self.assertEqual(win1.item.uuid, self.escena1.uuid)
        self.assertTrue(win1.is_open)
        self.assertEqual(win1.geometry, (200, 200, 700, 500))

        # Reabrir el mismo documento debe devolver la misma ventana
        win1_dup = qr_mgr.open_document(self.escena1)
        self.assertEqual(win1.window_id, win1_dup.window_id)

        # Abrir un segundo documento en ventana separada
        win2 = qr_mgr.open_document(self.escena2)
        self.assertNotEqual(win1.window_id, win2.window_id)
        self.assertEqual(len(qr_mgr.get_open_windows()), 2)

        # Edición dentro de la ventana QR con persistencia
        win1.editor.update_text("Texto editado desde la ventana flotante Quick Reference.")
        win1.save_changes()

        rtf_saved = self.escena1.read_content_rtf()
        self.assertIn("Quick Reference", RTFEngine.rtf_to_plain_text(rtf_saved))

        # Cierre de ventanas
        qr_mgr.close_window(win1.window_id)
        self.assertFalse(win1.is_open)
        self.assertEqual(len(qr_mgr.get_open_windows()), 1)

    # =========================================================================
    # 3. PRUEBAS DE MODO ESCRITURA DE GUIONES (SCRIPTWRITING MODE / Ctrl+8)
    # =========================================================================

    def test_scriptwriting_transitions_enter_and_tab(self):
        """
        Verifica la máquina de transiciones automáticas con Enter y Tab:
        Heading -> Action -> Character -> Dialogue -> Action, etc.
        """
        engine = ScriptwritingEngine(ScriptFormat.SCREENPLAY)

        # Activar modo guion (Ctrl+8)
        engine.toggle_mode()
        self.assertTrue(engine.is_active)
        self.assertEqual(engine.current_element, ScriptElementType.SCENE_HEADING)

        # 1. Encabezado de Escena + Enter -> Acción
        next_elem, formatted_line = engine.handle_enter("int. cafeteria - dia")
        self.assertEqual(next_elem, ScriptElementType.ACTION)
        self.assertEqual(formatted_line, "INT. CAFETERIA - DIA")  # Mayúsculas automáticas

        # 2. En Acción + Tab -> Personaje
        next_elem, _ = engine.handle_tab("Isabel entra a la cafeteria.")
        self.assertEqual(next_elem, ScriptElementType.CHARACTER)

        # 3. En Personaje + Enter -> Diálogo
        next_elem, char_line = engine.handle_enter("isabel")
        self.assertEqual(next_elem, ScriptElementType.DIALOGUE)
        self.assertEqual(char_line, "ISABEL")

        # 4. En Diálogo + Tab -> Paréntesis (Acotación)
        next_elem, _ = engine.handle_tab("")
        self.assertEqual(next_elem, ScriptElementType.PARENTHETICAL)

        # 5. En Paréntesis + Enter -> Diálogo
        next_elem, paren_line = engine.handle_enter("mirando el reloj")
        self.assertEqual(next_elem, ScriptElementType.DIALOGUE)
        self.assertEqual(paren_line, "(mirando el reloj)")  # Cierre automático de paréntesis

        # 6. En Diálogo + Enter -> Acción
        next_elem, dial_line = engine.handle_enter("Llegas tarde, Marcos.")
        self.assertEqual(next_elem, ScriptElementType.ACTION)

        # 7. Atajos directos y selector de barra de estado
        engine.set_element_by_shortcut(6)  # Ctrl+6: Transición
        self.assertEqual(engine.current_element, ScriptElementType.TRANSITION)
        self.assertIn("TRANSICIÓN", engine.get_status_label())

    def test_script_autocomplete_learning_and_suggestions(self):
        """Verifica el autocompletado inteligente de locaciones, momentos y personajes."""
        auto = ScriptAutocomplete()

        # Aprender de un texto existente
        script_sample = """
        INT. ARCHIVO CENTRAL - NOCHE
        ISABEL
        No puedo creer que esté aquí.
        EXT. PLAZA MAYOR - DÍA
        MARCOS
        Date prisa.
        """
        auto.learn_from_text(script_sample)

        # Verificar que aprendió los personajes
        self.assertIn("ISABEL", auto.characters)
        self.assertIn("MARCOS", auto.characters)

        # Verificar sugerencias de personaje
        char_sugg = auto.get_suggestions(ScriptElementType.CHARACTER, "I")
        self.assertIn("ISABEL", char_sugg)

        # Verificar sugerencias de prefijo de escena
        scene_sugg = auto.get_suggestions(ScriptElementType.SCENE_HEADING, "")
        self.assertIn("INT.", scene_sugg)
        self.assertIn("EXT.", scene_sugg)

        # Verificar sugerencias de transición
        trans_sugg = auto.get_suggestions(ScriptElementType.TRANSITION, "CORTE")
        self.assertIn("CORTE A:", trans_sugg)

    # =========================================================================
    # 4. PRUEBAS DE VISORES INTEGRADOS DE INVESTIGACIÓN (RESEARCH VIEWERS)
    # =========================================================================

    def test_pdf_viewer_navigation_zoom_search(self):
        """Verifica el visor de PDF: páginas, zoom y búsqueda de texto."""
        pdf_path = self.temp_dir / "documento_investigacion.pdf"
        # Crear un archivo de prueba con estructura binaria de PDF simulada
        pdf_content = (
            b"%PDF-1.4\n"
            b"1 0 obj <</Type /Page>> endobj\n"
            b"(Evidencia historica manuscrita sobre el archivo central) Tj\n"
            b"2 0 obj <</Type /Page>> endobj\n"
            b"(Segunda pagina con el mapa de las catacumbas secretas) Tj\n"
            b"%%EOF\n"
        )
        pdf_path.write_bytes(pdf_content)

        viewer = PDFViewer()
        ok = viewer.load_file(str(pdf_path))
        self.assertTrue(ok)
        self.assertGreaterEqual(viewer.total_pages, 2)
        self.assertEqual(viewer.current_page, 1)

        # Navegación
        self.assertTrue(viewer.next_page())
        self.assertEqual(viewer.current_page, 2)
        self.assertFalse(viewer.next_page())  # Llegó al final
        self.assertTrue(viewer.previous_page())
        self.assertEqual(viewer.current_page, 1)

        # Zoom
        viewer.zoom_in()
        self.assertGreater(viewer.zoom, 1.0)
        viewer.fit_width()
        self.assertEqual(viewer.fit_mode, "width")
        viewer.reset_zoom()
        self.assertEqual(viewer.zoom, 1.0)

        # Búsqueda de texto
        results = viewer.search("catacumbas")
        self.assertGreaterEqual(len(results), 1)
        self.assertIn("catacumbas", results[0].context.lower())

    def test_image_viewer_zoom_rotation_metadata(self):
        """Verifica el visor de imágenes: zoom, rotación 90/180° y formatos."""
        img_path = self.temp_dir / "mapa_boceto.bmp"
        # Cabecera BMP 100x100
        bmp_data = bytearray(b"BM" + (b"\x00" * 52))
        bmp_data[18:22] = (100).to_bytes(4, "little")  # width
        bmp_data[22:26] = (100).to_bytes(4, "little")  # height
        img_path.write_bytes(bytes(bmp_data))

        viewer = ImageViewer()
        ok = viewer.load_file(str(img_path))
        self.assertTrue(ok)
        self.assertEqual(viewer.width_px, 100)
        self.assertEqual(viewer.height_px, 100)

        # Zoom
        viewer.zoom_in()
        self.assertGreater(viewer.zoom, 1.0)
        viewer.toggle_fit_to_window()
        self.assertTrue(viewer.fit_to_window)

        # Rotación
        self.assertEqual(viewer.rotation_degrees, 0)
        viewer.rotate_clockwise()
        self.assertEqual(viewer.rotation_degrees, 90)
        viewer.rotate_180()
        self.assertEqual(viewer.rotation_degrees, 270)
        viewer.rotate_clockwise()
        self.assertEqual(viewer.rotation_degrees, 0)

    def test_transcription_player_shortcuts_and_timestamps(self):
        """
        Verifica el reproductor para transcripción de entrevistas:
        Pausar/Reanudar, retroceso 5 segundos, avance 5s y marca de tiempo.
        """
        audio_path = self.temp_dir / "entrevista_testigo.mp3"
        audio_path.write_bytes(b"\xFF\xFB\x90\x00" * 50)  # Dummy MP3 frames

        player = TranscriptionPlayer()
        ok = player.load_media(str(audio_path), simulated_duration=120.0)
        self.assertTrue(ok)
        self.assertFalse(player.is_video)

        # Reproducción (F5 / Ctrl+Shift+Space)
        player.toggle_play_pause()
        self.assertTrue(player.is_playing)

        # Simular avance a 35 segundos
        player.seek(35.0)
        self.assertEqual(player.current_position, 35.0)

        # Retroceder 5 segundos sin despegar las manos (F6)
        player.rewind_seconds(5.0)
        self.assertEqual(player.current_position, 30.0)

        # Avanzar 5 segundos (F7)
        player.forward_seconds(5.0)
        self.assertEqual(player.current_position, 35.0)

        # Marca de tiempo para inserción en editor (F8)
        ts = player.get_timestamp_string()
        self.assertEqual(ts, "[00:35]")

        # Velocidad de reproducción ajustable (0.5x .. 2.0x)
        player.set_speed(1.25)
        self.assertEqual(player.playback_speed, 1.25)

    def test_web_archive_viewer_and_reader_mode(self):
        """Verifica el visor de páginas web archivadas y modo lectura limpio."""
        html_path = self.temp_dir / "articulo_prensa.html"
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Descubrimiento Arqueológico en Toledo</title>
            <style>body { font-size: 14px; }</style>
            <script>console.log("analytics");</script>
        </head>
        <body>
            <h1>Hallazgo Histórico</h1>
            <p>Un equipo de investigadores ha descubierto un manuscrito inédito del siglo XVI.</p>
            <a href="https://example.com/fuente">Fuente original</a>
        </body>
        </html>
        """
        html_path.write_text(html_content, encoding="utf-8")

        viewer = WebArchiveViewer()
        ok = viewer.load_file(str(html_path))
        self.assertTrue(ok)
        self.assertEqual(viewer.page_title, "Descubrimiento Arqueológico en Toledo")
        self.assertIn("https://example.com/fuente", viewer.links)

        # Modo Lectura: los tags y scripts desaparecen
        reader_text = viewer.get_display_content()
        self.assertIn("manuscrito inédito", reader_text)
        self.assertNotIn("<script>", reader_text)
        self.assertNotIn("analytics", reader_text)

        # Búsqueda
        search_res = viewer.search("siglo XVI")
        self.assertEqual(len(search_res), 1)

    def test_research_viewer_router(self):
        """Verifica el despacho automático de archivos de investigación."""
        self.assertEqual(ResearchViewerRouter.identify_type("doc.pdf"), "pdf")
        self.assertEqual(ResearchViewerRouter.identify_type("foto.png"), "image")
        self.assertEqual(ResearchViewerRouter.identify_type("grabacion.mp3"), "media")
        self.assertEqual(ResearchViewerRouter.identify_type("video.mp4"), "media")
        self.assertEqual(ResearchViewerRouter.identify_type("pagina.html"), "web")
        self.assertEqual(ResearchViewerRouter.identify_type("datos.xyz"), "unknown")

    # =========================================================================
    # 5. INTEGRACIÓN EN MAIN WINDOW
    # =========================================================================

    def test_main_window_integration(self):
        """Verifica la integración completa en MainWindow."""
        win = MainWindow(self.project)

        # Conmutación de Modo Scrivenings (Ctrl+1)
        self.assertEqual(win.current_view_mode, CentralViewMode.EDITOR)
        active_scriv = win.toggle_scrivenings_mode()
        self.assertTrue(active_scriv)
        self.assertEqual(win.current_view_mode, CentralViewMode.SCRIVENINGS)

        # Pantalla dividida
        win.split_vertical()
        self.assertEqual(win.split_manager.layout_mode, SplitLayoutMode.VERTICAL)

        # Bloqueo del editor
        locked = win.toggle_lock_editor()
        self.assertTrue(locked)

        # Modo guion (Ctrl+8)
        script_on = win.toggle_scriptwriting_mode()
        self.assertTrue(script_on)

        # Telemetría de estado
        status = win.get_status_info()
        self.assertTrue(status["is_locked"])
        self.assertTrue(status["scriptwriting_active"])
        self.assertEqual(status["split_layout"], "vertical")


if __name__ == "__main__":
    unittest.main()
