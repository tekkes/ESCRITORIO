"""
Red Team Test: Conformidad Exhaustiva del Motor de Temas Visuales
Verifica:
1. Paletas exactas de los 7 modos visuales predefinidos.
2. ScrThemeLoader: descompresión en memoria de .scrtheme y parseo de manifest XML, .pal, .prefs y .qss.
3. Control de Densidad Visual (UI Density), micro-badges (10px) e indicadores cromáticos (6px).
4. Live Theme Studio: personalización en tiempo real y exportación bidireccional a .escrtheme y .scrtheme.
5. Conmutación en caliente de sub-50ms entre todos los modos.
"""

import io
import time
import zipfile
import unittest
from pathlib import Path

from src.themes.theme_engine import (
    ThemeEngine,
    ThemeMode,
    UIDensityMode,
    BUILTIN_PALETTES,
    DENSITY_CONFIGS
)
from src.themes.theme_parser import (
    ThemeParser,
    ThemePackage,
    ScrThemeLoader
)
from src.themes.live_studio import LiveThemeStudio
from src.ui.main_window import MainWindow, CentralViewMode


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
        """Verifica que todas las paletas contengan los tokens obligatorios."""
        for mode, palette in BUILTIN_PALETTES.items():
            for token in self.REQUIRED_TOKENS:
                self.assertIn(token, palette, f"El token '{token}' falta en la paleta {mode.value}")
                self.assertTrue(palette[token].startswith("#"), f"Color inválido para {token} en {mode.value}")

    def test_exact_color_definitions_of_the_7_modes(self):
        """Verifica las definiciones cromáticas exactas exigidas para los 7 modos."""
        # 1. Modo Minimalista (Por Defecto)
        p_min = BUILTIN_PALETTES[ThemeMode.MINIMALIST_DEFAULT]
        self.assertEqual(p_min["editor.background"].upper(), "#FFFFFF")
        self.assertIn(p_min["window.background"].upper(), ("#F7F7F5", "#EFEFEC"))

        # 2. Modo Oscuro (Carbon Dark)
        p_dark = BUILTIN_PALETTES[ThemeMode.CARBON_DARK]
        self.assertIn(p_dark["binder.background"].upper(), ("#18191A", "#202124", "#141517"))
        self.assertEqual(p_dark["editor.foreground"].upper(), "#E4E6EB")

        # 3. Modo Solarizado Oscuro (Solarized Dark)
        p_sd = BUILTIN_PALETTES[ThemeMode.SOLARIZED_DARK]
        self.assertEqual(p_sd["editor.background"].upper(), "#002B36")
        self.assertEqual(p_sd["toolbar.background"].upper(), "#073642")
        self.assertEqual(p_sd["editor.foreground"].upper(), "#839496")
        self.assertEqual(p_sd["accent.primary"].upper(), "#B58900")
        self.assertEqual(p_sd["accent.secondary"].upper(), "#2AA198")

        # 4. Modo Solarizado Claro (Solarized Light)
        p_sl = BUILTIN_PALETTES[ThemeMode.SOLARIZED_LIGHT]
        self.assertEqual(p_sl["editor.background"].upper(), "#FDF6E3")
        self.assertEqual(p_sl["window.background"].upper(), "#EEE8D5")
        self.assertEqual(p_sl["editor.foreground"].upper(), "#657B83")

        # 5. Modo Sepia (Classic Parchment)
        p_sepia = BUILTIN_PALETTES[ThemeMode.SEPIA_PARCHMENT]
        self.assertEqual(p_sepia["editor.background"].upper(), "#F4ECD8")
        self.assertEqual(p_sepia["window.background"].upper(), "#E8DEC3")
        self.assertEqual(p_sepia["editor.foreground"].upper(), "#3B2F2F")

        # 6. Modo Nord (Nordic Frost)
        p_nord = BUILTIN_PALETTES[ThemeMode.NORDIC_FROST]
        self.assertEqual(p_nord["editor.background"].upper(), "#2E3440")
        self.assertEqual(p_nord["toolbar.background"].upper(), "#3B4252")
        self.assertEqual(p_nord["editor.foreground"].upper(), "#ECEFF4")
        self.assertEqual(p_nord["accent.primary"].upper(), "#88C0D0")

        # 7. Modo Catppuccin Mocha
        p_cat = BUILTIN_PALETTES[ThemeMode.CATPPUCCIN_MOCHA]
        self.assertEqual(p_cat["editor.background"].upper(), "#1E1E2E")
        self.assertEqual(p_cat["binder.background"].upper(), "#181825")
        self.assertEqual(p_cat["toolbar.background"].upper(), "#11111B")
        self.assertEqual(p_cat["editor.foreground"].upper(), "#CDD6F4")
        self.assertEqual(p_cat["accent.primary"].upper(), "#CBA6F7")

    def test_scrtheme_loader_in_memory_and_parsing(self):
        """
        Verifica que ScrThemeLoader descomprima en memoria cualquier .scrtheme
        y parsee fielmente manifest.xml, palette.pal, preferences.prefs y stylesheet.qss.
        """
        # Crear un .scrtheme en memoria con las 4 estructuras
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            manifest_xml = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<ThemeManifest Version="1.0">\n'
                '    <Name>Test Scrivener Theme</Name>\n'
                '    <Author>Test Author</Author>\n'
                '    <Version>2.1.0</Version>\n'
                '    <TargetPlatform>Windows</TargetPlatform>\n'
                '    <BaseTheme>Dark</BaseTheme>\n'
                '</ThemeManifest>\n'
            )
            zf.writestr("manifest.xml", manifest_xml.encode("utf-8"))

            palette_pal = (
                "[Palette]\n"
                "Window.Background=#121216\n"
                "Window.Foreground=#F0F0F5\n"
                "Binder.Background=#101014\n"
                "Binder.ItemText=#D0D0DC\n"
                "Editor.Background=#0E0E12\n"
                "Editor.Foreground=#F5F5FA\n"
                "Editor.CaretColor=#60A5FA\n"
                "Corkboard.CardBackground=#1E1E24\n"
                "Corkboard.PinColor=#EF4444\n"
            )
            zf.writestr("palette.pal", palette_pal.encode("utf-8"))

            preferences_prefs = (
                '{\n'
                '    "Editor.DefaultFont": "Consolas",\n'
                '    "Editor.FontSize": 14,\n'
                '    "Corkboard.CardWidth": 200\n'
                '}\n'
            )
            zf.writestr("preferences.prefs", preferences_prefs.encode("utf-8"))

            stylesheet_qss = (
                "QTreeView#binderView { background-color: #101014; color: #D0D0DC; }\n"
                "QTextEdit#editor { background-color: #0E0E12; color: #F5F5FA; }\n"
            )
            zf.writestr("stylesheet.qss", stylesheet_qss.encode("utf-8"))

        raw_zip = zip_buf.getvalue()

        # Cargar con ScrThemeLoader
        package = ScrThemeLoader.load_from_memory(raw_zip)
        self.assertEqual(package.name, "Test Scrivener Theme")
        self.assertEqual(package.author, "Test Author")
        self.assertEqual(package.version, "2.1.0")
        self.assertEqual(package.base_theme, "Dark")

        # Verificar tokens parseados y normalizados
        self.assertIn("editor.background", package.palette)
        self.assertEqual(package.palette["editor.background"].lower(), "#0e0e12")
        self.assertEqual(package.palette["editor.caret"].lower(), "#60a5fa")

        # Verificar preferencias
        self.assertEqual(package.preferences.get("Editor.DefaultFont"), "Consolas")

        # Verificar QSS
        self.assertIn("QTreeView#binderView", package.qss_stylesheet)

    def test_ui_density_and_micro_badges(self):
        """
        Verifica el control de densidad UI:
        - Dimensiones exactas (28px toolbar, 24px header, 10px micro-badge, 6px dot).
        - Generadores de micro-badges e indicadores cromáticos.
        """
        engine = ThemeEngine(ThemeMode.MINIMALIST_DEFAULT, UIDensityMode.ULTRA_COMPACT)
        metrics = engine.density_metrics

        self.assertEqual(metrics.toolbar_height, 28)
        self.assertEqual(metrics.editor_header_height, 24)
        self.assertEqual(metrics.icon_size, 14)
        self.assertEqual(metrics.badge_height, 10)
        self.assertEqual(metrics.status_indicator_size, 6)

        # Micro-badge
        badge_css = engine.generate_micro_badge("BORRADOR", "#E5EDF9", "#1E4F9E")
        self.assertIn("height: 10px", badge_css)
        self.assertIn("line-height: 10px", badge_css)
        self.assertIn("border-radius: 5px", badge_css)

        # Indicador cromático de estado (6px circle)
        dot_css = engine.generate_status_dot("#10B981")
        self.assertIn("width: 6px", dot_css)
        self.assertIn("height: 6px", dot_css)
        self.assertIn("border-radius: 3px", dot_css)

        # QSS incluye las alturas compactas
        qss = engine.generate_qss()
        self.assertIn("min-height: 28px;", qss)
        self.assertIn("min-height: 24px;", qss)

    def test_live_theme_studio_editing_and_export(self):
        """
        Verifica la funcionalidad de Live Theme Studio:
        - Modificación de colores, tipografía, texturas y densidad.
        - Notificación de vista previa sin parpadeos.
        - Exportación a .escrtheme y a contenedor .scrtheme.
        """
        engine = ThemeEngine(ThemeMode.MINIMALIST_DEFAULT)
        studio = LiveThemeStudio(engine)

        preview_events = []
        studio.on_preview_update = lambda state: preview_events.append(state)

        # Modificar color
        studio.update_color_token("editor.background", "#112233")
        self.assertEqual(len(preview_events), 1)
        self.assertEqual(studio.working_palette["editor.background"], "#112233")

        # Modificar tipografía y textura
        studio.update_typography("font_family_editor", "Merriweather")
        studio.set_texture("cork_grain")
        self.assertEqual(studio.working_texture, "cork_grain")

        # Aplicar cambios definitivamente
        studio.commit_changes()
        self.assertEqual(engine.get_color("editor.background"), "#112233")

        # Exportar a .escrtheme (JSON)
        escr_json = studio.export_as_escrtheme(name="Custom Studio Theme", author="Studio Author")
        self.assertIn("Custom Studio Theme", escr_json)
        self.assertIn("#112233", escr_json)

        # Exportar a .scrtheme (ZIP)
        scr_zip_bytes = studio.export_as_scrtheme(name="Custom Scrivener Theme", author="Studio Author")
        self.assertTrue(len(scr_zip_bytes) > 0)

        # Validar que el .scrtheme exportado es recargable por ScrThemeLoader
        reloaded = ScrThemeLoader.load_from_memory(scr_zip_bytes)
        self.assertEqual(reloaded.name, "Custom Scrivener Theme")
        self.assertEqual(reloaded.palette.get("editor.background"), "#112233")

    def test_sub_50ms_theme_switching_benchmark(self):
        """
        Requisito 5: Verifica que el cambio entre los 7 modos ocurre en menos de 50 ms
        sin parpadeos ni reinicios.
        """
        engine = ThemeEngine(ThemeMode.MINIMALIST_DEFAULT)
        benchmarks = engine.benchmark_mode_switching()

        for mode_name, elapsed_ms in benchmarks.items():
            self.assertLess(
                elapsed_ms,
                50.0,
                f"La conmutación al modo '{mode_name}' tardó {elapsed_ms:.2f} ms (supera el límite de 50 ms)"
            )

    def test_main_window_theme_integration(self):
        """Verifica la conmutación de temas en la ventana principal MainWindow."""
        win = MainWindow(theme_mode=ThemeMode.MINIMALIST_DEFAULT)
        self.assertEqual(win.theme_engine.current_mode, ThemeMode.MINIMALIST_DEFAULT)

        # Cambiar a Sepia
        elapsed = win.set_theme(ThemeMode.SEPIA_PARCHMENT)
        self.assertLess(elapsed, 50.0)
        self.assertEqual(win.theme_engine.current_mode, ThemeMode.SEPIA_PARCHMENT)

        # Obtener lista de los 7 modos disponibles
        avail = win.get_available_themes()
        self.assertEqual(len(avail), 7)

        # Telemetría en status_info
        status = win.get_status_info()
        self.assertEqual(status["active_theme"], "sepia_parchment")
        self.assertEqual(status["ui_density"], "ultra_compact")


if __name__ == "__main__":
    unittest.main()
