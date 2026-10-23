"""
ESCRITORIO v2.0 - Unit Tests for Stats Manager & Editor Formatting
Verifica el cronometraje de horas de trabajo, estadísticas diarias/semanales,
edición interactiva de objetivos y la barra de formato mejorada del editor.
"""

import unittest
import tempfile
import time
from pathlib import Path

from src.core.stats_manager import WritingStatsManager
from src.core.project_v2 import EscritorioProjectV2, BinderNode


class TestStatsAndEditor(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.tmp_dir.name)
        self.mgr = WritingStatsManager(self.config_dir)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_session_time_and_activity_tracking(self):
        self.assertEqual(self.mgr.total_session_seconds, 0.0)
        self.assertEqual(self.mgr.active_session_seconds, 0.0)

        # Simular 3 ticks
        self.mgr.on_tick()
        self.mgr.on_tick()
        self.mgr.on_tick()

        self.assertEqual(self.mgr.total_session_seconds, 3.0)
        self.assertEqual(self.mgr.active_session_seconds, 3.0)

        # Simular inactividad (> 60s)
        self.mgr.last_activity_time = time.time() - 100.0
        self.mgr.on_tick()
        # total sube, activo no sube
        self.assertEqual(self.mgr.total_session_seconds, 4.0)
        self.assertEqual(self.mgr.active_session_seconds, 3.0)

        # Usuario teclea
        self.mgr.on_keystroke(words_delta=10)
        self.mgr.on_tick()
        self.assertEqual(self.mgr.total_session_seconds, 5.0)
        self.assertEqual(self.mgr.active_session_seconds, 4.0)
        self.assertEqual(self.mgr.session_words_written, 10)

    def test_document_time_tracking(self):
        doc_uuid = "doc-test-123"
        self.mgr.set_active_node(doc_uuid)
        self.mgr.on_keystroke(1)
        self.mgr.on_tick()
        self.mgr.on_tick()

        self.assertEqual(self.mgr.get_doc_time(doc_uuid), 2.0)

    def test_format_hms(self):
        self.assertEqual(WritingStatsManager.format_hms(45), "45s")
        self.assertEqual(WritingStatsManager.format_hms(125), "2m 05s")
        self.assertEqual(WritingStatsManager.format_hms(3665), "1h 01m 05s")

    def test_week_stats_calculation(self):
        week = self.mgr.get_week_stats()
        self.assertIn("total_seconds", week)
        self.assertIn("avg_daily_hours", week)
        self.assertEqual(len(week["days"]), 7)

    def test_project_target_fields(self):
        proj = EscritorioProjectV2(self.config_dir / "test_proj.escr")
        self.assertEqual(proj.project_target_words, 50000)
        self.assertEqual(proj.session_target_words, 1500)
        proj.project_target_words = 75000
        proj.session_target_words = 2000
        proj.daily_hours_target = 3.5
        proj.target_deadline = "2026-12-31"

        self.assertEqual(proj.project_target_words, 75000)
        self.assertEqual(proj.session_target_words, 2000)
        self.assertEqual(proj.daily_hours_target, 3.5)
        self.assertEqual(proj.target_deadline, "2026-12-31")

    def test_targets_xml_roundtrip(self):
        from src.core.xml_engine_v2 import XmlEngineV2
        proj = EscritorioProjectV2(self.config_dir / "roundtrip.escr")
        proj.path.mkdir(parents=True, exist_ok=True)
        xml_file = proj.path / "roundtrip.escrx"

        proj.project_target_words = 80000
        proj.session_target_words = 1200
        proj.daily_hours_target = 4.0
        proj.target_deadline = "2027-01-15"
        proj.target_work_days = [0, 1, 2, 3, 4]  # Lunes a Viernes

        XmlEngineV2.save_project_xml(proj, xml_file)
        self.assertTrue(xml_file.exists())

        loaded = EscritorioProjectV2(proj.path)
        XmlEngineV2.load_project_xml(loaded, xml_file)

        self.assertEqual(loaded.project_target_words, 80000)
        self.assertEqual(loaded.session_target_words, 1200)
        self.assertEqual(loaded.daily_hours_target, 4.0)
        self.assertEqual(loaded.target_deadline, "2027-01-15")
        self.assertEqual(loaded.target_work_days, [0, 1, 2, 3, 4])


if __name__ == "__main__":
    unittest.main()
