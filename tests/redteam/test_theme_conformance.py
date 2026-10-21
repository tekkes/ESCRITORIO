"""
Red Team Test: Conformidad de Temas Visuales
Verifica que las paletas integradas contengan todos los tokens cromáticos obligatorios
y que la generación de estilos QSS sea válida.
"""

import unittest
from src.themes.theme_engine import ThemeEngine, ThemeMode, BUILTIN_PALETTES

class TestThemeConformance(unittest.TestCase):

    REQUIRED_TOKENS = [
        "window.background",
        "window.foreground",
        "binder.background",
        "binder.foreground",
        "binder.selected_bg",
        "editor.background",
        "editor.foreground",
        "editor.caret",
        "corkboard.background",
        "corkboard.card_bg",
        "inspector.background"
    ]

    def test_all_builtin_palettes_have_required_tokens(self):
        for mode, palette in BUILTIN_PALETTES.items():
            for token in self.REQUIRED_TOKENS:
                self.assertIn(token, palette, f"El token '{token}' falta en la paleta {mode.value}")
                self.assertTrue(palette[token].startswith("#"), f"Color inválido para {token} en {mode.value}")

    def test_theme_engine_qss_generation(self):
        engine = ThemeEngine(ThemeMode.DARK_OBSIDIAN)
        qss = engine.generate_qss()
        self.assertIn("QMainWindow", qss)
        self.assertIn("QTreeView#binder", qss)
        self.assertIn("QTextEdit#editor", qss)

if __name__ == "__main__":
    unittest.main()
