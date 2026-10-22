"""
Red Team Test Suite para el componente Esquema (OutlinerWidget) en Escritorio.
Valida la paridad visual, interactividad y capacidades de planificación estructural con Scrivener 3:
1. Árbol tabular multinivel:
   - Título y sinopsis combinados debajo del título en la misma celda o en columnas separadas.
   - Edición directa in-situ de título y sinopsis con persistencia.
   - Expansión, colapso y aplanado de filas respetando la jerarquía.
2. Selector compacto de columnas visibles:
   - Title & Synopsis, Label, Status, Section Type, Include in Compile.
   - Words, Total Words (recursivo), Characters, Total Characters (recursivo).
   - Target, Total Target (recursivo) y Progress con barra de gradiente cromático (rojo 0% -> ámbar 50% -> verde 100%).
   - Keywords, Created Date, Modified Date y Metadatos Personalizados (Custom Metadata).
3. Ordenación multi-criterio:
   - Clic en cabecera cicla: Ascendente -> Descendente -> Restaurar orden original del Binder.
4. Filtrado rápido por texto:
   - Búsqueda en tiempo real que preserva ramas contenedoras con descendientes coincidentes.
5. Exportación directa a archivo .csv:
   - Formato CSV estándar con comillas multilínea, indentación y codificación UTF-8.
6. Integración en MainWindow:
   - Atajo de teclado Ctrl+3 para conmutar modo Esquema y retrocompatibilidad total con OutlinerView.
"""

import unittest
import shutil
import tempfile
import csv
from pathlib import Path

from src.core.project import EscritorioProject, BinderItem
from src.core.rtf_engine import RTFEngine
from src.ui.OutlinerWidget import (
    OutlinerWidget,
    OutlinerColumn,
    ColumnSelector,
    ColumnType,
    StandardColumnId,
    calculate_progress_color,
    OutlinerRow,
    OutlinerExporter
)
from src.ui.outliner import OutlinerView
from src.ui.main_window import MainWindow, CentralViewMode


class TestOutlinerWidget(unittest.TestCase):

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_escritorio_outliner_"))
        self.project_path = self.temp_dir / "ProyectoEsquema.escr"
        self.project = EscritorioProject.create_new(self.project_path, "Test Outliner Project", native=True)

        draft = self.project.get_draft_folder()
        self.assertIsNotNone(draft)

        # Crear estructura jerárquica de 2 niveles:
        # Capítulo 1 (Folder)
        #   ├── Escena 1.1 (Text)
        #   ├── Escena 1.2 (Text)
        #   └── Subcarpeta Investigación (Folder)
        #         └── Nota Histórica (Text)
        self.cap1 = self.project.add_item(draft.uuid, "Capítulo 1: La Niebla", item_type="Folder")
        self.scene1 = self.project.add_item(self.cap1.uuid, "Escena 1.1: El Callejón", item_type="Text")
        self.scene2 = self.project.add_item(self.cap1.uuid, "Escena 1.2: El Umbral", item_type="Text")
        self.subfolder = self.project.add_item(self.cap1.uuid, "Investigación", item_type="Folder")
        self.note = self.project.add_item(self.subfolder.uuid, "Nota Histórica", item_type="Text")

        # Configurar contenidos de texto con diferentes recuentos de palabras
        # Escena 1.1: ~20 palabras
        self.scene1.write_content_rtf(RTFEngine.plain_text_to_rtf(
            "La lluvia caía intensamente sobre las piedras del viejo campanario. "
            "Isabel se cubrió el rostro con la capucha oscura y aceleró."
        ))
        self.scene1.write_synopsis("Isabel huye por el callejón.")
        self.scene1.data.target_words = 100
        self.scene1.data.label_id = 1
        self.scene1.data.status_id = 2
        self.scene1.data.section_type = "Scene"
        self.scene1.data.include_in_compile = True
        self.scene1.data.custom_metadata["POV"] = "Isabel"
        self.scene1.data.custom_metadata["Ubicacion"] = "Callejón Antiguo"
        self.scene1.data.keywords = ["Noche", "Misterio"]
        self.scene1.save_if_dirty()

        # Escena 1.2: ~30 palabras
        self.scene2.write_content_rtf(RTFEngine.plain_text_to_rtf(
            "El portón de madera rechinó suavemente al ceder. "
            "Marcos encendió un fósforo y observó las sombras proyectadas en los muros de piedra. "
            "No había nadie cerca."
        ))
        self.scene2.write_synopsis("Marcos llega a la entrada secreta.")
        self.scene2.data.target_words = 200
        self.scene2.data.label_id = 2
        self.scene2.data.status_id = 1
        self.scene2.data.section_type = "Scene"
        self.scene2.data.include_in_compile = True
        self.scene2.data.custom_metadata["POV"] = "Marcos"
        self.scene2.data.custom_metadata["Ubicacion"] = "Catedral"
        self.scene2.data.keywords = ["Tensión"]
        self.scene2.save_if_dirty()

        # Nota Histórica: ~10 palabras
        self.note.write_content_rtf(RTFEngine.plain_text_to_rtf(
            "Documento hallado en los archivos secretos de la abadía."
        ))
        self.note.write_synopsis("Registro del año 1845.")
        self.note.data.target_words = 50
        self.note.data.include_in_compile = False
        self.note.save_if_dirty()

        self.project.save_structure()

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    # =========================================================================
    # 1. ÁRBOL TABULAR MULTINIVEL Y MODO TÍTULO/SINOPSIS
    # =========================================================================

    def test_outliner_hierarchical_tree_loading(self):
        """Valida que el Esquematizador construya el árbol multinivel con niveles de profundidad precisos."""
        widget = OutlinerWidget(self.project)
        widget.load_container(self.cap1)

        # Hijos directos de cap1: scene1, scene2, subfolder
        self.assertEqual(len(widget.root_rows), 3)

        row_sc1 = widget.root_rows[0]
        self.assertEqual(row_sc1.uuid, self.scene1.uuid)
        self.assertEqual(row_sc1.level, 0)
        self.assertFalse(row_sc1.is_folder)

        row_sub = widget.root_rows[2]
        self.assertEqual(row_sub.uuid, self.subfolder.uuid)
        self.assertEqual(row_sub.level, 0)
        self.assertTrue(row_sub.is_folder)
        self.assertEqual(len(row_sub.children), 1)

        # Nieto: nota histórica con nivel 1
        row_note = row_sub.children[0]
        self.assertEqual(row_note.uuid, self.note.uuid)
        self.assertEqual(row_note.level, 1)

    def test_outliner_title_and_synopsis_combined_vs_separated(self):
        """Valida la alternancia entre 'Title & Synopsis' en una celda y columnas separadas."""
        widget = OutlinerWidget(self.project, combined_title_synopsis=True)
        widget.load_container(self.cap1)

        sel = widget.column_selector
        self.assertTrue(sel.is_visible(StandardColumnId.TITLE_AND_SYNOPSIS.value))
        self.assertFalse(sel.is_visible(StandardColumnId.TITLE.value))
        self.assertFalse(sel.is_visible(StandardColumnId.SYNOPSIS.value))

        cell_data = widget.root_rows[0].get_cell_value(StandardColumnId.TITLE_AND_SYNOPSIS.value)
        self.assertIsInstance(cell_data, dict)
        self.assertEqual(cell_data["title"], "Escena 1.1: El Callejón")
        self.assertEqual(cell_data["synopsis"], "Isabel huye por el callejón.")

        # Alternar a columnas separadas
        widget.combined_title_synopsis = False
        self.assertFalse(sel.is_visible(StandardColumnId.TITLE_AND_SYNOPSIS.value))
        self.assertTrue(sel.is_visible(StandardColumnId.TITLE.value))
        self.assertTrue(sel.is_visible(StandardColumnId.SYNOPSIS.value))

        self.assertEqual(widget.root_rows[0].get_cell_value(StandardColumnId.TITLE.value), "Escena 1.1: El Callejón")
        self.assertEqual(widget.root_rows[0].get_cell_value(StandardColumnId.SYNOPSIS.value), "Isabel huye por el callejón.")

    def test_outliner_in_situ_editing(self):
        """Valida que la edición in-situ de celdas actualice el nodo y sincronice el proyecto."""
        widget = OutlinerWidget(self.project)
        widget.load_container(self.cap1)

        # Modificar título
        success = widget.update_cell(self.scene1.uuid, StandardColumnId.TITLE.value, "Escena 1.1: La Fuga")
        self.assertTrue(success)
        self.assertEqual(self.scene1.title, "Escena 1.1: La Fuga")

        # Modificar sinopsis
        widget.update_cell(self.scene1.uuid, StandardColumnId.SYNOPSIS.value, "Nueva sinopsis editada.")
        self.assertEqual(self.scene1.read_synopsis(), "Nueva sinopsis editada.")

        # Modificar target
        widget.update_cell(self.scene1.uuid, StandardColumnId.TARGET.value, 1500)
        self.assertEqual(self.scene1.data.target_words, 1500)

        # Modificar include_in_compile
        widget.update_cell(self.scene1.uuid, StandardColumnId.INCLUDE_IN_COMPILE.value, False)
        self.assertFalse(self.scene1.data.include_in_compile)

    def test_outliner_expansion_and_flattening(self):
        """Valida el colapso y expansión de carpetas al aplanar la cuadrícula para renderizado."""
        widget = OutlinerWidget(self.project)
        widget.load_container(self.cap1)

        # Inicialmente todo expandido: scene1, scene2, subfolder, note -> 4 filas
        flat_all = widget.get_flattened_rows()
        self.assertEqual(len(flat_all), 4)

        # Colapsar la subcarpeta
        widget.toggle_expand(self.subfolder.uuid)
        row_sub = widget.find_row_by_uuid(self.subfolder.uuid)
        self.assertFalse(row_sub.expanded)

        # Ahora el hijo 'note' no aparece en la vista aplanada -> 3 filas
        flat_collapsed = widget.get_flattened_rows()
        self.assertEqual(len(flat_collapsed), 3)
        self.assertNotIn(self.note.uuid, [r.uuid for r in flat_collapsed])

        # Expandir todo de nuevo
        widget.expand_all()
        self.assertEqual(len(widget.get_flattened_rows()), 4)

    # =========================================================================
    # 2. SELECTOR DE COLUMNAS, MÉTRICAS Y BARRAS DE PROGRESO
    # =========================================================================

    def test_outliner_metrics_recursive_calculations(self):
        """Valida el cálculo de palabras directas vs Total Words recursivo y Total Target."""
        widget = OutlinerWidget(self.project)
        widget.load_container(self.cap1)

        row_sc1 = widget.find_row_by_uuid(self.scene1.uuid)
        self.assertGreater(row_sc1.words, 15)
        self.assertEqual(row_sc1.words, row_sc1.total_words)
        self.assertEqual(row_sc1.target, 100)
        self.assertEqual(row_sc1.total_target, 100)

        row_sub = widget.find_row_by_uuid(self.subfolder.uuid)
        # La subcarpeta tiene 0 palabras directas pero su hijo note tiene ~10 palabras
        self.assertEqual(row_sub.words, 0)
        self.assertGreater(row_sub.total_words, 5)
        self.assertEqual(row_sub.target, 0)
        self.assertEqual(row_sub.total_target, 50) # note.target = 50

    def test_outliner_progress_bar_color_gradient(self):
        """Valida que la barra de progreso calcule el porcentaje y su gradiente cromático."""
        # 0% -> Rojo
        color_0 = calculate_progress_color(0.0)
        self.assertEqual(color_0.upper(), "#EF4444")

        # 50% -> Ámbar
        color_50 = calculate_progress_color(50.0)
        self.assertEqual(color_50.upper(), "#F59E0B")

        # 100% -> Verde
        color_100 = calculate_progress_color(100.0)
        self.assertEqual(color_100.upper(), "#10B981")

        # Verificar porcentaje de progreso en una fila
        widget = OutlinerWidget(self.project)
        widget.load_container(self.cap1)
        row_sc1 = widget.find_row_by_uuid(self.scene1.uuid)

        # scene1 tiene ~20 palabras y target=100 -> ~20%
        self.assertGreaterEqual(row_sc1.progress_percent, 15.0)
        self.assertLessEqual(row_sc1.progress_percent, 25.0)
        self.assertTrue(row_sc1.progress_color.startswith("#"))

    def test_outliner_custom_metadata_discovery_and_editing(self):
        """Valida el descubrimiento automático de columnas de Custom Metadata y su edición in-situ."""
        widget = OutlinerWidget(self.project)
        widget.load_container(self.cap1)

        # Comprobar que descubrió las columnas 'custom:POV' y 'custom:Ubicacion'
        cols = widget.column_selector.columns
        self.assertIn("custom:POV", cols)
        self.assertIn("custom:Ubicacion", cols)

        row_sc1 = widget.find_row_by_uuid(self.scene1.uuid)
        self.assertEqual(row_sc1.get_cell_value("custom:POV"), "Isabel")
        self.assertEqual(row_sc1.get_cell_value("custom:Ubicacion"), "Callejón Antiguo")

        # Edición in-situ de metadato personalizado
        widget.update_cell(self.scene1.uuid, "custom:POV", "Isabel / Elena")
        self.assertEqual(self.scene1.data.custom_metadata["POV"], "Isabel / Elena")

    # =========================================================================
    # 3. ORDENACIÓN MULTI-CRITERIO EN CABECERAS
    # =========================================================================

    def test_outliner_header_click_sorting_cycle(self):
        """Valida que hacer clic en los encabezados cicle Asc -> Desc -> Original Binder."""
        widget = OutlinerWidget(self.project)
        widget.load_container(self.cap1)

        # 1er clic en 'words': Ascendente
        dir1 = widget.click_header_sort(StandardColumnId.WORDS.value)
        self.assertTrue(dir1)
        self.assertEqual(widget.sort_column, StandardColumnId.WORDS.value)
        self.assertTrue(widget.sort_ascending)

        flat_asc = widget.get_flattened_rows()
        # En nivel 0: subfolder (0 palabras), scene1 (~20 pal), scene2 (~30 pal)
        level0_uuids = [r.uuid for r in flat_asc if r.level == 0]
        self.assertEqual(level0_uuids, [self.subfolder.uuid, self.scene1.uuid, self.scene2.uuid])

        # 2do clic en 'words': Descendente
        dir2 = widget.click_header_sort(StandardColumnId.WORDS.value)
        self.assertFalse(dir2)
        self.assertFalse(widget.sort_ascending)

        flat_desc = widget.get_flattened_rows()
        level0_uuids_desc = [r.uuid for r in flat_desc if r.level == 0]
        self.assertEqual(level0_uuids_desc, [self.scene2.uuid, self.scene1.uuid, self.subfolder.uuid])

        # 3er clic en 'words': Restaurar orden del Binder
        dir3 = widget.click_header_sort(StandardColumnId.WORDS.value)
        self.assertIsNone(dir3)
        self.assertIsNone(widget.sort_column)

        flat_orig = widget.get_flattened_rows()
        level0_orig = [r.uuid for r in flat_orig if r.level == 0]
        self.assertEqual(level0_orig, [self.scene1.uuid, self.scene2.uuid, self.subfolder.uuid])

    # =========================================================================
    # 4. FILTRADO RÁPIDO POR TEXTO
    # =========================================================================

    def test_outliner_quick_text_filtering(self):
        """Valida que el filtro encuentre texto y mantenga visible la jerarquía hacia el resultado."""
        widget = OutlinerWidget(self.project)
        widget.load_container(self.cap1)

        # Filtrar por "Marcos" (está en scene2)
        widget.set_filter_text("Marcos")
        flat = widget.get_flattened_rows()
        self.assertEqual(len(flat), 1)
        self.assertEqual(flat[0].uuid, self.scene2.uuid)

        # Filtrar por "abadía" (está en note, que es hijo de subfolder)
        # La subcarpeta debe mantenerse visible para dar contexto a la nota encontrada
        widget.set_filter_text("abadía")
        flat_nested = widget.get_flattened_rows()
        self.assertEqual(len(flat_nested), 2)
        self.assertEqual(flat_nested[0].uuid, self.subfolder.uuid)
        self.assertEqual(flat_nested[1].uuid, self.note.uuid)

        # Limpiar filtro
        widget.set_filter_text("")
        self.assertEqual(len(widget.get_flattened_rows()), 4)

    # =========================================================================
    # 5. EXPORTACIÓN DIRECTA A ARCHIVO .CSV
    # =========================================================================

    def test_outliner_csv_export(self):
        """Valida que la exportación a archivo .csv genere cabeceras y filas válidas con comillas."""
        widget = OutlinerWidget(self.project)
        widget.load_container(self.cap1)

        csv_file = self.temp_dir / "EsquemaCapitulo1.csv"
        csv_text = widget.export_csv(output_file_or_path=csv_file)

        self.assertTrue(csv_file.exists())
        self.assertIn("Título y Sinopsis", csv_text)
        self.assertIn("Palabras", csv_text)

        # Verificar que sea un CSV válido mediante el módulo estándar csv
        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            self.assertGreaterEqual(len(reader), 5) # 1 header + 4 rows
            headers = reader[0]
            self.assertIn("Título y Sinopsis", headers)
            self.assertIn("Total Palabras", headers)

    # =========================================================================
    # 6. INTEGRACIÓN CON MAINWINDOW Y TELEMETRÍA
    # =========================================================================

    def test_main_window_outliner_toggle_shortcut(self):
        """Valida que MainWindow integre OutlinerWidget y que Ctrl+3 conmute el modo Esquema."""
        win = MainWindow(self.project)
        self.assertEqual(win.view_mode, CentralViewMode.EDITOR)

        # Simular activación con Ctrl+3
        win.toggle_outliner_mode()
        self.assertEqual(win.view_mode, CentralViewMode.OUTLINER)
        self.assertIsNotNone(win.outliner_widget)

        # Conmutar de nuevo vuelve al editor
        win.toggle_outliner_mode()
        self.assertEqual(win.view_mode, CentralViewMode.EDITOR)

    def test_outliner_view_data_telemetry(self):
        """Valida la generación de datos estructurados para la capa gráfica/UI."""
        widget = OutlinerWidget(self.project)
        widget.load_container(self.cap1)
        data = widget.get_view_data()

        self.assertEqual(data["parent_uuid"], self.cap1.uuid)
        self.assertEqual(data["total_rows"], 4)
        self.assertIn("columns", data)
        self.assertIn("rows", data)


if __name__ == "__main__":
    unittest.main()
