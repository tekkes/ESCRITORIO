"""
Red Team Test Suite para el Modo Composición y Herramientas de Productividad del Escritor:
1. Modo Composición (F11):
   - Pantalla completa sin distracciones, ancho de papel, posición, zoom, atenuación de fondo.
   - Barra de control inferior auto-ocultable al acercar el cursor al borde inferior.
   - Menú rápido Go To para saltar a cualquier escena del Binder y typewriter scrolling.
2. Objetivos de Proyecto y Sesión (Project Targets / Ctrl+Shift+T):
   - Barras de progreso duales (Manuscrito y Sesión) con umbrales de color.
   - Calculadora de Fecha Límite (Deadline), selección de días de escritura y cuota diaria dinámica.
3. Estadísticas del Proyecto y Frecuencia de Palabras (Project Statistics):
   - Palabras, caracteres, párrafos, páginas impresas (250 w/p), páginas de bolsillo (300 w/p), tiempos.
   - Tabla interactiva de Frecuencia de Palabras con filtro de stop-words en español e inglés.
4. Buscador Global de Proyecto y Búsqueda Regex (Project Search & Replace):
   - Búsqueda en Todo el Proyecto, solo Texto, Sinopsis, Notas o Títulos.
   - Soporte Regex y guardado de resultados como Colección en el Binder.
5. Generador de Nombres y Scratchpad Global (Ctrl+Alt+Shift+S):
   - Generación de nombres en 8 culturas con filtros de género, inicial, aliteración y títulos.
   - Scratchpad global: ciclo de vida de notas y envío al documento activo o como nuevo nodo en el Binder.
"""

import unittest
import shutil
import tempfile
import datetime
from pathlib import Path

from src.core.project import EscritorioProject, BinderItem
from src.core.rtf_engine import RTFEngine
from src.ui.CompositionMode import (
    CompositionMode,
    CompositionPaperSettings,
    PaperPosition,
    BottomControlBar,
    GoToItem
)
from src.tools import (
    ProjectTargetsTracker,
    WritingStatistics,
    SPANISH_STOP_WORDS,
    ALL_STOP_WORDS,
    ProjectSearchEngine,
    SearchScope,
    SearchMatch,
    CharacterNameGenerator,
    ScratchpadManager,
    ScratchpadNote
)


class TestCompositionMode(unittest.TestCase):
    """Pruebas exhaustivas para el Modo Composición libre de distracciones (F11)."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_comp_mode_"))
        self.project_path = self.temp_dir / "TestComp.escr"
        self.project = EscritorioProject.create_new(self.project_path, "Test Comp", native=True)

        draft = self.project.get_draft_folder()
        self.doc1 = self.project.add_item(draft.uuid, "Capítulo 1: El Despertar", item_type="Text")
        self.doc2 = self.project.add_item(draft.uuid, "Capítulo 2: La Huida", item_type="Text")
        self.doc1.write_content_rtf(r"{\rtf1\ansi En una noche de tormenta, las campanas sonaron.}")
        self.doc1.save_if_dirty()
        self.project.save_structure()

        self.comp_mode = CompositionMode(self.project, self.doc1)

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_lifecycle_and_toggle(self):
        self.assertFalse(self.comp_mode.is_active)
        self.comp_mode.enter()
        self.assertTrue(self.comp_mode.is_active)
        self.comp_mode.exit()
        self.assertFalse(self.comp_mode.is_active)

        # F11 Toggle
        active = self.comp_mode.toggle()
        self.assertTrue(active)
        self.assertTrue(self.comp_mode.is_active)
        active = self.comp_mode.toggle()
        self.assertFalse(active)
        self.assertFalse(self.comp_mode.is_active)

    def test_paper_settings(self):
        # Ancho de papel (30% a 100%)
        self.comp_mode.set_paper_width(75)
        self.assertEqual(self.comp_mode.paper_settings.paper_width_percent, 75)
        self.comp_mode.set_paper_width(120)  # Clamp a 100
        self.assertEqual(self.comp_mode.paper_settings.paper_width_percent, 100)
        self.comp_mode.set_paper_width(15)   # Clamp a 30
        self.assertEqual(self.comp_mode.paper_settings.paper_width_percent, 30)

        # Posición del papel
        self.comp_mode.set_paper_position(PaperPosition.LEFT)
        self.assertEqual(self.comp_mode.paper_settings.position, PaperPosition.LEFT)

        # Fundido de fondo (Background Fade)
        self.comp_mode.set_background_fade(0.9)
        self.assertEqual(self.comp_mode.paper_settings.background_fade, 0.9)

        # Zoom de texto
        self.comp_mode.set_text_zoom(150)
        self.assertEqual(self.comp_mode.paper_settings.text_zoom_percent, 150)

    def test_auto_hiding_bottom_bar(self):
        bar = self.comp_mode.control_bar
        screen_height = 1080

        # Cursor en medio de la pantalla: barra oculta
        changed = bar.update_cursor_position(cursor_y=500, screen_height=screen_height)
        self.assertFalse(bar.is_visible)

        # Cursor se acerca al borde inferior (zona de detección 56px): barra emerge
        changed = bar.update_cursor_position(cursor_y=1050, screen_height=screen_height)
        self.assertTrue(changed)
        self.assertTrue(bar.is_visible)

        # Cursor se aleja de nuevo: barra se oculta
        changed = bar.update_cursor_position(cursor_y=400, screen_height=screen_height)
        self.assertTrue(changed)
        self.assertFalse(bar.is_visible)

        # Pin: al fijar la barra, permanece visible
        bar.toggle_pin()
        self.assertTrue(bar.is_pinned)
        self.assertTrue(bar.is_visible)
        bar.update_cursor_position(cursor_y=200, screen_height=screen_height)
        self.assertTrue(bar.is_visible)

    def test_go_to_navigation(self):
        self.assertEqual(self.comp_mode.active_item.uuid, self.doc1.uuid)

        # Saltar al Capítulo 2 desde el modo composición
        target = self.comp_mode.go_to_scene(self.doc2.uuid)
        self.assertIsNotNone(target)
        self.assertEqual(self.comp_mode.active_item.uuid, self.doc2.uuid)
        self.assertEqual(self.comp_mode.active_item.title, "Capítulo 2: La Huida")

    def test_typewriter_scrolling_calculation(self):
        # Línea 20, altura por línea 30px -> caret_y = 600px. Pantalla 800px (centro = 400px).
        offset = self.comp_mode.calculate_typewriter_scroll_offset(
            caret_line_index=20,
            total_lines=100,
            line_height_px=30,
            viewport_height_px=800
        )
        self.assertEqual(offset, 200)


class TestProjectTargets(unittest.TestCase):
    """Pruebas exhaustivas para Objetivos de Proyecto y Sesión con calculadora de Deadline."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_targets_"))
        self.project_path = self.temp_dir / "TestTargets.escr"
        self.project = EscritorioProject.create_new(self.project_path, "Test Targets", native=True)

        draft = self.project.get_draft_folder()
        self.doc = self.project.add_item(draft.uuid, "Escena 1", item_type="Text")
        self.doc.write_content_rtf(r"{\rtf1\ansi Cien palabras escritas en el manuscrito para prueba.}")
        self.doc.save_if_dirty()
        self.project.save_structure()

        self.targets = ProjectTargetsTracker(
            draft_target=50000,
            session_target=1000,
            project=self.project
        )

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_dual_progress_bars_and_colors(self):
        # Fijar conteo actual
        self.targets.update_current_words(25000)
        self.assertEqual(self.targets.get_draft_progress_percent(), 50.0)
        self.assertEqual(self.targets.get_progress_color(50.0), "#F59E0B")  # Ámbar

        self.targets.update_current_words(10000)
        self.assertEqual(self.targets.get_draft_progress_percent(), 20.0)
        self.assertEqual(self.targets.get_progress_color(20.0), "#EF4444")  # Rojo

        self.targets.update_current_words(50000)
        self.assertEqual(self.targets.get_draft_progress_percent(), 100.0)
        self.assertEqual(self.targets.get_progress_color(100.0), "#10B981")  # Verde

    def test_session_baseline_and_reset(self):
        self.targets.set_session_baseline(20000)
        self.targets.update_current_words(20500)
        self.assertEqual(self.targets.session_written_words, 500)
        self.assertEqual(self.targets.get_session_progress_percent(), 50.0)

        # Reset session
        self.targets.reset_session()
        self.assertEqual(self.targets.session_written_words, 0)
        self.assertEqual(self.targets.session_initial_words, 20500)

    def test_deadline_calculator_and_daily_quota(self):
        today = datetime.date(2026, 11, 1)      # Domingo
        deadline = datetime.date(2026, 11, 30)  # Lunes (30 días en Noviembre)

        self.targets.set_draft_target(30000)
        self.targets.update_current_words(10000)  # Faltan 20.000 palabras
        self.targets.set_deadline(deadline)

        # Escribir solo de Lunes a Viernes: {0, 1, 2, 3, 4}
        self.targets.set_writing_days({0, 1, 2, 3, 4})

        calendar_days = self.targets.get_days_remaining(today)
        self.assertEqual(calendar_days, 29)

        writing_days = self.targets.get_writing_days_remaining(today)
        self.assertGreater(writing_days, 0)
        self.assertLess(writing_days, 25)

        # Cuota diaria dinámica requerida
        quota = self.targets.get_daily_word_quota(today)
        self.assertGreater(quota, 0)
        # 20.000 palabras repartidas entre ~21 días de trabajo = ~953 palabras/día
        self.assertTrue(900 <= quota <= 1100)

    def test_pacing_status(self):
        today = datetime.date(2026, 11, 1)
        deadline = datetime.date(2026, 11, 30)
        self.targets.set_draft_target(50000)
        self.targets.update_current_words(10000)
        self.targets.set_deadline(deadline)

        status = self.targets.get_pacing_status(today)
        self.assertIn("Ritmo", status)

        # Cuando se completa
        self.targets.update_current_words(50000)
        self.assertEqual(self.targets.get_pacing_status(today), "Completado")


class TestWritingStatisticsAndFrequency(unittest.TestCase):
    """Pruebas exhaustivas para Estadísticas y Análisis de Frecuencia de Palabras."""

    def test_volume_metrics_and_page_estimates(self):
        # 500 palabras de prueba
        sample_text = (
            "La lluvia caía sobre los adoquines de la ciudad vieja mientras la noche avanzaba en silencio. "
            "Isabel observaba las luces de las farolas reflejadas en los charcos oscuros de la plaza mayor. "
        ) * 15  # ~510 palabras

        stats = WritingStatistics.analyze_text(sample_text)
        self.assertGreater(stats["words"], 400)
        self.assertGreater(stats["characters_with_spaces"], 2000)
        self.assertGreater(stats["characters_without_spaces"], 1800)

        # Páginas estándar (250 palabras)
        self.assertAlmostEqual(stats["printed_pages"], round(stats["words"] / 250, 1), places=1)
        # Páginas de bolsillo (300 palabras)
        self.assertAlmostEqual(stats["paperback_pages"], round(stats["words"] / 300, 1), places=1)

        # Tiempo de lectura y legibilidad
        self.assertGreater(stats["reading_time_minutes"], 1.0)
        self.assertIn("readability_score", stats)
        self.assertIn("readability_level", stats)

    def test_word_frequency_with_and_without_stopwords(self):
        text = (
            "El archivo secreto estaba en la catedral. "
            "Isabel buscaba el archivo porque el archivo contenía la clave del misterio. "
            "La catedral guardaba el archivo con recelo."
        )

        # Con filtro de stop-words activado (elimina 'el', 'la', 'en', 'del', 'porque', etc.)
        freq_filtered = WritingStatistics.compute_word_frequency(text, filter_stopwords=True)
        top_words = [item["word"] for item in freq_filtered]

        # 'archivo' y 'catedral' son las palabras clave más repetidas
        self.assertEqual(top_words[0], "archivo")
        self.assertIn("catedral", top_words)
        self.assertNotIn("el", top_words)
        self.assertNotIn("la", top_words)
        self.assertNotIn("en", top_words)

        # Sin filtro de stop-words (incluye artículos)
        freq_unfiltered = WritingStatistics.compute_word_frequency(text, filter_stopwords=False)
        top_unfiltered_words = [item["word"] for item in freq_unfiltered]
        self.assertTrue("el" in top_unfiltered_words or "la" in top_unfiltered_words)


class TestProjectSearchEngine(unittest.TestCase):
    """Pruebas exhaustivas para el Buscador Global del Proyecto con Regex y Colecciones."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_search_"))
        self.project_path = self.temp_dir / "TestSearch.escr"
        self.project = EscritorioProject.create_new(self.project_path, "Test Search", native=True)

        draft = self.project.get_draft_folder()
        self.doc1 = self.project.add_item(draft.uuid, "Escena de la Catedral", item_type="Text")
        self.doc1.write_content_rtf(r"{\rtf1\ansi Isabel descubrio las coordenadas 1894 en el pergamino.}")
        self.doc1.write_synopsis("Isabel inspecciona la catedral buscando pistas.")
        self.doc1.write_notes_rtf(r"{\rtf1\ansi Recordar el ano 1894 como clave.}")
        self.doc1.save_if_dirty()

        self.doc2 = self.project.add_item(draft.uuid, "Escena del Callejón", item_type="Text")
        self.doc2.write_content_rtf(r"{\rtf1\ansi La niebla impedia ver las coordenadas del mapa.}")
        self.doc2.save_if_dirty()

        self.project.save_structure()

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_search_scopes(self):
        # 1. Búsqueda en Todo (ALL): encuentra en texto, sinopsis y notas
        matches_all, err = ProjectSearchEngine.search_project(self.project, "coordenadas", SearchScope.ALL)
        self.assertIsNone(err)
        self.assertEqual(len(matches_all), 2)  # En doc1 y doc2

        # 2. Solo en Sinopsis: solo en doc1
        matches_syn, err = ProjectSearchEngine.search_project(self.project, "catedral", SearchScope.SYNOPSIS)
        self.assertIsNone(err)
        self.assertEqual(len(matches_syn), 1)
        self.assertEqual(matches_syn[0].item_uuid, self.doc1.uuid)

        # 3. Solo en Títulos
        matches_title, err = ProjectSearchEngine.search_project(self.project, "Callejón", SearchScope.TITLES)
        self.assertIsNone(err)
        self.assertEqual(len(matches_title), 1)
        self.assertEqual(matches_title[0].item_uuid, self.doc2.uuid)

    def test_regex_search(self):
        # Buscar patrón de año de 4 dígitos: \b\d{4}\b (encontrará '1894')
        matches_regex, err = ProjectSearchEngine.search_project(
            self.project,
            r"\b\d{4}\b",
            SearchScope.TEXT,
            use_regex=True
        )
        self.assertIsNone(err)
        self.assertEqual(len(matches_regex), 1)
        self.assertEqual(matches_regex[0].match_text, "1894")

        # Manejo seguro de sintaxis regex inválida
        matches_bad, err_bad = ProjectSearchEngine.search_project(
            self.project,
            r"[a-z(",
            SearchScope.TEXT,
            use_regex=True
        )
        self.assertIsNotNone(err_bad)
        self.assertEqual(len(matches_bad), 0)

    def test_replace_all_and_save_collection(self):
        # Reemplazar 'coordenadas' por 'claves' en todo el proyecto
        count, err = ProjectSearchEngine.replace_all(
            self.project,
            query="coordenadas",
            replacement="claves",
            scope=SearchScope.TEXT
        )
        self.assertIsNone(err)
        self.assertEqual(count, 2)

        # Verificar que el contenido se actualizó
        plain1 = RTFEngine.rtf_to_plain_text(self.doc1.read_content_rtf())
        self.assertIn("claves", plain1)
        self.assertNotIn("coordenadas", plain1)

        # Guardar resultados como Colección
        matches, _ = ProjectSearchEngine.search_project(self.project, "claves", SearchScope.TEXT)
        saved = ProjectSearchEngine.save_as_collection(self.project, "Colección Claves", matches)
        self.assertTrue(saved)


class TestCharacterNameGenerator(unittest.TestCase):
    """Pruebas exhaustivas para el Generador de Nombres de Personajes."""

    def test_all_cultures_generation(self):
        cultures = ["es", "en", "fr", "de", "it", "ja", "fantasy", "mythology"]
        for cult in cultures:
            name = CharacterNameGenerator.generate(culture=cult, gender="any")
            self.assertTrue(len(name.split()) >= 2)

    def test_gender_and_starting_letter_filter(self):
        # Femenino con letra inicial 'M'
        for _ in range(5):
            name = CharacterNameGenerator.generate(culture="es", gender="female", starts_with="M")
            first_name = name.split()[0]
            self.assertTrue(first_name.startswith("M"))

    def test_alliteration_filter(self):
        # Aliteración: Nombre y Apellido con la misma letra inicial
        for _ in range(10):
            name = CharacterNameGenerator.generate(culture="en", alliteration=True)
            parts = name.split()
            self.assertEqual(parts[0][0].upper(), parts[1][0].upper())

    def test_batch_generation(self):
        batch = CharacterNameGenerator.generate_batch(count=8, culture="fantasy", include_title=True)
        self.assertEqual(len(batch), 8)
        self.assertTrue(all(len(n.split()) >= 2 for n in batch))


class TestGlobalScratchpad(unittest.TestCase):
    """Pruebas exhaustivas para el Bloc de Notas Flotante Global (Ctrl+Alt+Shift+S)."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_scratchpad_"))
        self.storage_dir = self.temp_dir / "ScratchpadNotes"
        self.manager = ScratchpadManager(self.storage_dir)

        # Proyecto de prueba para enviar notas
        self.project_path = self.temp_dir / "TestScratchProject.escr"
        self.project = EscritorioProject.create_new(self.project_path, "Test Scratch Project", native=True)
        draft = self.project.get_draft_folder()
        self.active_doc = self.project.add_item(draft.uuid, "Documento Borrador", item_type="Text")
        self.active_doc.write_content_rtf(r"{\rtf1\ansi Texto inicial del documento.}")
        self.active_doc.save_if_dirty()
        self.project.save_structure()

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_note_lifecycle(self):
        # Crear nota
        note = self.manager.create_note("Cita Catedral", "La arquitectura de la catedral refleja el siglo XIV.")
        self.assertIsNotNone(note)
        self.assertTrue(Path(note.file_path).exists())

        # Listar
        notes = self.manager.list_notes()
        self.assertEqual(len(notes), 1)

        # Actualizar
        updated = self.manager.update_note(note.id, "Texto actualizado de la cita.")
        self.assertIsNotNone(updated)
        self.assertEqual(updated.content, "Texto actualizado de la cita.")

        # Eliminar
        deleted = self.manager.delete_note(note.id)
        self.assertTrue(deleted)
        self.assertEqual(len(self.manager.list_notes()), 0)

    def test_send_to_active_document_as_text_and_notes(self):
        note = self.manager.create_note("Idea Clave", "El vigilante nocturno es hermano del alcalde.")

        # 1. Enviar anexando al texto principal
        success_text = self.manager.send_to_active_document(
            note_id=note.id,
            project=self.project,
            target_item_uuid=self.active_doc.uuid,
            destination="text"
        )
        self.assertTrue(success_text)
        content = RTFEngine.rtf_to_plain_text(self.active_doc.read_content_rtf())
        self.assertIn("El vigilante nocturno es hermano del alcalde.", content)

        # 2. Enviar anexando a las notas del documento
        success_notes = self.manager.send_to_active_document(
            note_id=note.id,
            project=self.project,
            target_item_uuid=self.active_doc.uuid,
            destination="notes"
        )
        self.assertTrue(success_notes)
        notes_plain = RTFEngine.rtf_to_plain_text(self.active_doc.read_notes_rtf())
        self.assertIn("Idea Clave", notes_plain)

        # 3. Enviar creando un nuevo documento en el Binder
        success_new = self.manager.send_to_active_document(
            note_id=note.id,
            project=self.project,
            destination="new_document"
        )
        self.assertTrue(success_new)
        draft = self.project.get_draft_folder()
        titles = [c.title for c in draft.children]
        self.assertIn("Idea Clave", titles)


if __name__ == "__main__":
    unittest.main()
