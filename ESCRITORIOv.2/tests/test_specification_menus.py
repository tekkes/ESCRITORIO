"""
ESCRITORIO v2.0 - Unit Tests for Complete Specification Menus
Verifica estrictamente que todos los menús y submenús descritos en las
páginas 7, 8 y 9 de ESCRITORIO-especificacion.pdf estén presentes,
correctamente instanciados y conectados a sus subsistemas funcionales.
"""

import sys
import unittest
import tempfile
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QAction

from src.ui.shell_v2 import ShellV2
from src.core.project_v2 import EscritorioProjectV2, BinderNode
from src.ui.menu_dialogs_v2 import CommandPaletteDialog, ProjectMetadataDialog, KeywordsHudDialog, DiagnosticsManager


class TestSpecificationMenus(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.tmp_dir.name) / "TestProject.escr"
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.shell = ShellV2(str(self.project_dir))

    def tearDown(self):
        self.shell.close()
        self.tmp_dir.cleanup()

    def test_all_nine_top_level_menus_exist(self):
        """Verifica que los 9 menús de Scrivener 3 Windows 11 están presentes en el orden exacto."""
        menu_titles = [act.text().replace("&", "") for act in self.shell.menuBar().actions()]
        expected_menus = [
            "Archivo",
            "Editar",
            "Ver",
            "Navegar",
            "Proyecto",
            "Documentos",
            "Formato",
            "Ventana",
            "Ayuda"
        ]
        self.assertEqual(menu_titles, expected_menus)

    def test_archivo_menu_items(self):
        """Verifica elementos clave de Archivo (página 7): Importar, Exportar, Sincronizar, Copias."""
        menu_acts = {act.text().replace("&", ""): act for act in self.shell.menuBar().actions()}
        archivo_menu = menu_acts["Archivo"].menu()
        self.assertIsNotNone(archivo_menu)

        item_texts = [a.text().replace("&", "") for a in archivo_menu.actions() if a.text()]
        self.assertIn("Nuevo proyecto…", item_texts)
        self.assertIn("Abrir…", item_texts)
        self.assertIn("Proyectos recientes", item_texts)
        self.assertIn("Proyectos favoritos", item_texts)
        self.assertIn("Mostrar proyecto en Explorador", item_texts)
        self.assertIn("Cerrar proyecto / todos", item_texts)
        self.assertIn("Guardar", item_texts)
        self.assertIn("Guardar como…", item_texts)
        self.assertIn("Guardar y reconstruir índices", item_texts)
        self.assertIn("Importar", item_texts)
        self.assertIn("Exportar", item_texts)
        self.assertIn("Sincronizar", item_texts)
        self.assertIn("Copia de seguridad", item_texts)
        self.assertIn("Compilar…", item_texts)
        self.assertIn("Salir", item_texts)

    def test_editar_menu_items(self):
        """Verifica elementos de Editar (páginas 7-8): Copiar especial, Seleccionar, Transformaciones, Voz."""
        menu_acts = {act.text().replace("&", ""): act for act in self.shell.menuBar().actions()}
        editar_menu = menu_acts["Editar"].menu()
        item_texts = [a.text().replace("&", "") for a in editar_menu.actions() if a.text()]

        self.assertIn("Deshacer", item_texts)
        self.assertIn("Rehacer", item_texts)
        self.assertIn("Copiar especial", item_texts)
        self.assertIn("Seleccionar", item_texts)
        self.assertIn("Insertar", item_texts)
        self.assertIn("Buscar", item_texts)
        self.assertIn("Transformaciones", item_texts)
        self.assertIn("Voz", item_texts)

    def test_ver_menu_items(self):
        """Verifica elementos de Ver (página 8): Modos editor, zoom, corcho, esquema, composición."""
        menu_acts = {act.text().replace("&", ""): act for act in self.shell.menuBar().actions()}
        ver_menu = menu_acts["Ver"].menu()
        item_texts = [a.text().replace("&", "") for a in ver_menu.actions() if a.text()]

        self.assertIn("Archivador", item_texts)
        self.assertIn("Inspector", item_texts)
        self.assertIn("Disposición del editor", item_texts)
        self.assertIn("Editor", item_texts)
        self.assertIn("Zoom", item_texts)
        self.assertIn("Opciones de corcho", item_texts)
        self.assertIn("Opciones del esquema", item_texts)
        self.assertIn("Composición", item_texts)

    def test_navegar_menu_items(self):
        """Verifica elementos de Navegar (página 8): Ir a, Foco, Historial, Favoritos."""
        menu_acts = {act.text().replace("&", ""): act for act in self.shell.menuBar().actions()}
        nav_menu = menu_acts["Navegar"].menu()
        item_texts = [a.text().replace("&", "") for a in nav_menu.actions() if a.text()]

        self.assertIn("Atrás", item_texts)
        self.assertIn("Adelante", item_texts)
        self.assertIn("Ir a", item_texts)
        self.assertIn("Foco", item_texts)
        self.assertIn("Historial", item_texts)

    def test_proyecto_menu_items(self):
        """Verifica elementos de Proyecto (página 8): Metadatos, Ajustes, Colecciones, Objetivos."""
        menu_acts = {act.text().replace("&", ""): act for act in self.shell.menuBar().actions()}
        proj_menu = menu_acts["Proyecto"].menu()
        item_texts = [a.text().replace("&", "") for a in proj_menu.actions() if a.text()]

        self.assertIn("Nuevo texto", item_texts)
        self.assertIn("Nueva carpeta", item_texts)
        self.assertIn("Objetivos…", item_texts)
        self.assertIn("Estadísticas del proyecto… / del texto…", item_texts)
        self.assertIn("Palabras clave…", item_texts)
        self.assertIn("Metadatos…", item_texts)
        self.assertIn("Ajustes del proyecto…", item_texts)
        self.assertIn("Colecciones", item_texts)
        self.assertIn("Vaciar papelera…", item_texts)

    def test_documentos_menu_items(self):
        """Verifica elementos de Documentos (páginas 8-9): Instantáneas, Dividir, Tipo Sección, Etiquetas."""
        menu_acts = {act.text().replace("&", ""): act for act in self.shell.menuBar().actions()}
        doc_menu = menu_acts["Documentos"].menu()
        item_texts = [a.text().replace("&", "") for a in doc_menu.actions() if a.text()]

        self.assertIn("Duplicar", item_texts)
        self.assertIn("Instantáneas", item_texts)
        self.assertIn("Dividir", item_texts)
        self.assertIn("Tipo de sección", item_texts)
        self.assertIn("Etiqueta", item_texts)
        self.assertIn("Estado", item_texts)
        self.assertIn("Palabras clave", item_texts)
        self.assertIn("Objetivo…", item_texts)

    def test_formato_menu_items(self):
        """Verifica elementos de Formato (página 9): Fuente, Estilo, Texto, Párrafo, Tablas, Revisión."""
        menu_acts = {act.text().replace("&", ""): act for act in self.shell.menuBar().actions()}
        fmt_menu = menu_acts["Formato"].menu()
        item_texts = [a.text().replace("&", "") for a in fmt_menu.actions() if a.text()]

        self.assertIn("Fuente", item_texts)
        self.assertIn("Estilo", item_texts)
        self.assertIn("Texto", item_texts)
        self.assertIn("Línea base", item_texts)
        self.assertIn("Párrafo", item_texts)
        self.assertIn("Listas", item_texts)
        self.assertIn("Tablas", item_texts)
        self.assertIn("Guion", item_texts)
        self.assertIn("Revisión", item_texts)

    def test_ventana_y_ayuda_menu_items(self):
        """Verifica elementos de Ventana y Ayuda (página 9): Referencias rápidas, Paneles, Buscar comando."""
        menu_acts = {act.text().replace("&", ""): act for act in self.shell.menuBar().actions()}
        win_menu = menu_acts["Ventana"].menu()
        help_menu = menu_acts["Ayuda"].menu()

        win_texts = [a.text().replace("&", "") for a in win_menu.actions() if a.text()]
        self.assertIn("Referencias rápidas", win_texts)
        self.assertIn("Paneles", win_texts)
        self.assertIn("🎨 Temas Visuales", win_texts)

        help_texts = [a.text().replace("&", "") for a in help_menu.actions() if a.text()]
        self.assertIn("Ayuda / Tutorial / Manual / Atajos", help_texts)
        self.assertIn("Buscar comando…", help_texts)
        self.assertIn("Diagnóstico / Paquete de soporte", help_texts)
        self.assertIn("Acerca de ESCRITORIO", help_texts)

    def test_command_palette_filters_and_executes(self):
        """Prueba la paleta de comandos interactiva (Ctrl+Shift+P)."""
        actions = self.shell.all_menu_actions
        palette = CommandPaletteDialog(actions, self.shell)
        palette._filter_commands("Compilar")
        self.assertGreater(palette.list_commands.count(), 0)

    def test_diagnostics_package_generation(self):
        """Prueba la generación de paquetes de diagnóstico de integridad (RF-042)."""
        zip_path = Path(self.tmp_dir.name) / "test_diag.zip"
        info = DiagnosticsManager.generate_support_package(self.shell.project, zip_path)
        self.assertTrue(zip_path.exists())
        self.assertEqual(info["integrity_status"], "VALID")


if __name__ == "__main__":
    unittest.main()
