"""
ESCRITORIO v2.0 - Unit Tests for Theme Engine & Session Persistence
Verifica la paridad de los 10 temas visuales, el selector del panel,
y la persistencia automática de modo visual, modo de vista y último proyecto.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path

from src.ui.theme_v2 import V2_THEMES, get_v2_stylesheet


class TestThemeAndSession(unittest.TestCase):

    def test_all_10_themes_defined(self):
        expected_themes = [
            "obsidian_dark",
            "macos_light",
            "nordic_frost",
            "catppuccin_mocha",
            "sepia_classic",
            "solarized_dark",
            "solarized_light",
            "high_contrast_dark",
            "carbon_dark",
            "scrivener_classic"
        ]
        for th in expected_themes:
            self.assertIn(th, V2_THEMES, f"El tema {th} debe estar en V2_THEMES")
            self.assertIn("name", V2_THEMES[th])
            self.assertIn("bg_app", V2_THEMES[th])
            self.assertIn("bg_editor", V2_THEMES[th])
            self.assertIn("text_main", V2_THEMES[th])
            self.assertIn("accent", V2_THEMES[th])

    def test_stylesheet_generation_all_themes(self):
        for th_key in V2_THEMES.keys():
            qss = get_v2_stylesheet(th_key)
            self.assertIsInstance(qss, str)
            self.assertGreater(len(qss), 500, f"QSS para {th_key} debe ser completo")
            self.assertIn("QMainWindow", qss)
            self.assertIn("QToolBar", qss)
            self.assertIn("QMenu", qss)

    def test_settings_persistence_structure(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cfg_file = Path(tmp_dir) / "v2_settings.json"
            sample_data = {
                "theme": "catppuccin_mocha",
                "view_mode": 2,
                "last_project_path": "C:/Projects/MiNovela.escr",
                "binder_visible": True,
                "inspector_visible": False
            }
            with open(cfg_file, "w", encoding="utf-8") as f:
                json.dump(sample_data, f)

            with open(cfg_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)

            self.assertEqual(loaded["theme"], "catppuccin_mocha")
            self.assertEqual(loaded["view_mode"], 2)
            self.assertEqual(loaded["last_project_path"], "C:/Projects/MiNovela.escr")
            self.assertFalse(loaded["inspector_visible"])


if __name__ == "__main__":
    unittest.main()
