"""
Red Team Test Suite para el componente Pizarra de Corcho (CorkboardWidget) en Escritorio.
Valida la paridad visual, interactividad y submodos de operacion con Scrivener 3:
1. Diseno de la Ficha de Indice (IndexCard):
   - Cabecera: icono, numeracion opcional, edicion de titulo in-situ / doble clic.
   - Cuerpo: persistencia transparente de sinopsis en synopsis.txt, lineas de libreta, imagen asociada.
   - Color de Etiqueta (Label): Pin (alfiler), Stripe (franja lateral), FullBackground (fondo tintado).
   - Sello de Estado (Status Stamp): texto diagonal semitransparente ("Borrador", "Revisado", "Listo").
   - Chips de Palabras Clave (Keywords): bloques de color en el margen.
2. Tres Submodos de Operacion:
   - Modo Rejilla (Arrange by Order): reordenacion fluida sincronizada con parent_item.children en Binder.
   - Modo Forma Libre (Freeform Corkboard): coordenadas 2D, zoom, paneo, y confirmacion de orden libre al Binder.
   - Modo Apilado por Etiqueta (Arrange by Label / Swimlanes): organizacion en carriles por etiqueta y reasignacion fluida.
3. Barra inferior ultra-compacta de control en vivo:
   - Ajustes de tamano, ratios (3x5, 4x6, 1:1), espaciado, tarjetas por fila (Auto o 1-10) y conmutadores.
4. Integracion con MainWindow y adaptacion dinamica a temas:
   - Atajo de teclado Ctrl+2 para conmutar modo Corcho.
   - Sincronizacion de vistas y retrocompatibilidad total.
"""

import unittest
import shutil
import tempfile
from pathlib import Path

from src.core.project import EscritorioProject, BinderItem
from src.ui.CorkboardWidget import (
    IndexCard,
    LabelColorStyle,
    CardAspectRatio,
    CorkboardMode,
    CorkboardSubmode,
    CorkboardGrid,
    CorkboardFreeform,
    CorkboardSwimlanes,
    SwimlaneColumn,
    CorkboardFooterBar,
    CorkboardWidget
)
from src.ui.corkboard import CorkboardView, CorkboardCard
from src.ui.main_window import MainWindow, CentralViewMode


class TestCorkboardWidget(unittest.TestCase):

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_escritorio_corkboard_"))
        self.project_path = self.temp_dir / "ProyectoCorcho.escr"
        self.project = EscritorioProject.create_new(self.project_path, "Test Corkboard Project", native=True)

        # Crear estructura de prueba en el borrador: Carpeta Capitulo 1 con 3 escenas
        draft = self.project.get_draft_folder()
        self.assertIsNotNone(draft)

        self.cap1 = self.project.add_item(draft.uuid, "Capitulo 1: El Despertar", item_type="Folder")
        self.scene1 = self.project.add_item(self.cap1.uuid, "Escena 1.1: El Callejón", item_type="Text")
        self.scene2 = self.project.add_item(self.cap1.uuid, "Escena 1.2: El Umbral", item_type="Text")
        self.scene3 = self.project.add_item(self.cap1.uuid, "Escena 1.3: El Archivo Oculto", item_type="Text")

        # Asignar etiquetas
        self.scene1.data.label_id = 1
        self.scene2.data.label_id = 2
        self.scene3.data.label_id = 1
        self.project.save_structure()

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    # =========================================================================
    # 1. PRUEBAS DE LA FICHA DE ÍNDICE (IndexCard)
    # =========================================================================

    def test_index_card_initialization_from_binder_item(self):
        """Valida que una IndexCard se inicialice fielmente desde un BinderItem del proyecto."""
        card = IndexCard.from_binder_item(self.scene1, card_number=1)
        self.assertEqual(card.uuid, self.scene1.uuid)
        self.assertEqual(card.title, "Escena 1.1: El Callejón")
        self.assertEqual(card.card_number, 1)
        self.assertTrue(card.show_number)
        self.assertEqual(card.label_id, 1)
        self.assertTrue(card.notebook_lines)

    def test_index_card_synopsis_persistence(self):
        """Valida que la edición de la sinopsis se guarde de forma atómica en synopsis.txt."""
        card = IndexCard.from_binder_item(self.scene1, card_number=1)
        self.assertEqual(card.synopsis, "")

        # Editar sinopsis
        card.set_synopsis("Isabel camina bajo la lluvia y encuentra el medallón grabado.")
        self.assertEqual(card.synopsis, "Isabel camina bajo la lluvia y encuentra el medallón grabado.")

        # Verificar que el archivo en disco exista y contenga el texto
        synopsis_file = self.scene1.get_data_dir() / "synopsis.txt"
        self.assertTrue(synopsis_file.exists())
        self.assertIn("Isabel camina bajo la lluvia", synopsis_file.read_text(encoding="utf-8"))

        # Recargar otra tarjeta desde el mismo ítem y verificar lectura
        card2 = IndexCard.from_binder_item(self.scene1, card_number=1)
        self.assertEqual(card2.synopsis, "Isabel camina bajo la lluvia y encuentra el medallón grabado.")

    def test_index_card_title_editing(self):
        """Valida que el cambio de título de la ficha actualice la tarjeta y el BinderItem."""
        card = IndexCard.from_binder_item(self.scene2, card_number=2)
        card.set_title("Escena 1.2: El Umbral Secreto")

        self.assertEqual(card.title, "Escena 1.2: El Umbral Secreto")
        self.assertEqual(self.scene2.title, "Escena 1.2: El Umbral Secreto")
        self.assertEqual(self.scene2.data.title, "Escena 1.2: El Umbral Secreto")

    def test_index_card_label_styles_and_colors(self):
        """Valida los modos de visualización de color de etiqueta: Pin, Franja o Fondo completo."""
        card = IndexCard.from_binder_item(self.scene1)
        card.label_style = LabelColorStyle.PIN
        self.assertEqual(card.label_style.value, "pin")

        card.label_style = LabelColorStyle.STRIPE
        self.assertEqual(card.label_style.value, "stripe")

        card.label_style = LabelColorStyle.FULL_BACKGROUND
        self.assertEqual(card.label_style.value, "full")

        # Modificación de etiqueta
        card.set_label(3, "Misterio Pasado", "#8B5CF6")
        self.assertEqual(card.label_id, 3)
        self.assertEqual(card.label_name, "Misterio Pasado")
        self.assertEqual(card.label_color, "#8B5CF6")
        self.assertEqual(self.scene1.data.label_id, 3)

    def test_index_card_status_stamps_and_keywords(self):
        """Valida sellos de estado diagonales personalizables y chips de palabras clave."""
        card = IndexCard.from_binder_item(self.scene3)
        card.set_status(2, "REVISADO")
        self.assertEqual(card.status_name, "REVISADO")
        self.assertEqual(card.status_stamp_text, "REVISADO")
        self.assertTrue(card.show_status_stamp)

        # Chips de palabras clave
        card.add_keyword("Pista", "#3B82F6")
        card.add_keyword("Tensión", "#EF4444")
        self.assertEqual(len(card.keywords), 2)
        self.assertIn("Pista", card.keywords)
        self.assertEqual(card.keyword_colors["Pista"], "#3B82F6")
        self.assertEqual(card.keyword_colors["Tensión"], "#EF4444")

    # =========================================================================
    # 2. SUBMODO REJILLA (CorkboardGrid / Arrange by Order)
    # =========================================================================

    def test_corkboard_grid_reorder_and_binder_sync(self):
        """Valida que la reordenación de tarjetas en la rejilla sincronice automáticamente el Binder."""
        widget = CorkboardWidget(self.project)
        widget.load_container(self.cap1)
        self.assertEqual(len(widget.cards), 3)

        # Orden original: scene1, scene2, scene3
        self.assertEqual(self.cap1.children[0].uuid, self.scene1.uuid)
        self.assertEqual(self.cap1.children[1].uuid, self.scene2.uuid)
        self.assertEqual(self.cap1.children[2].uuid, self.scene3.uuid)

        # Reordenar: mover la escena 3 al primer lugar (índice 2 -> índice 0)
        success = widget.reorder_grid_cards(2, 0)
        self.assertTrue(success)

        # En el widget las tarjetas están reordenadas y renumeradas
        self.assertEqual(widget.cards[0].uuid, self.scene3.uuid)
        self.assertEqual(widget.cards[0].card_number, 1)
        self.assertEqual(widget.cards[1].uuid, self.scene1.uuid)
        self.assertEqual(widget.cards[1].card_number, 2)
        self.assertEqual(widget.cards[2].uuid, self.scene2.uuid)
        self.assertEqual(widget.cards[2].card_number, 3)

        # En el Binder (parent_item.children) también están reordenadas
        self.assertEqual(self.cap1.children[0].uuid, self.scene3.uuid)
        self.assertEqual(self.cap1.children[1].uuid, self.scene1.uuid)
        self.assertEqual(self.cap1.children[2].uuid, self.scene2.uuid)

    def test_corkboard_grid_aspect_ratios_and_columns(self):
        """Valida el cálculo de dimensiones según ratios 3x5, 4x6, 1:1 y columnas fijas o automáticas."""
        grid = CorkboardGrid()
        grid.card_base_width = 200.0
        grid.aspect_ratio = CardAspectRatio.RATIO_3x5
        grid.spacing_px = 16.0
        self.assertAlmostEqual(grid.card_height, 120.0, places=1)  # 200 / (5/3) = 120

        grid.aspect_ratio = CardAspectRatio.RATIO_4x6
        self.assertAlmostEqual(grid.card_height, 133.33, places=1) # 200 / (6/4) = 133.33

        grid.aspect_ratio = CardAspectRatio.RATIO_1x1
        self.assertEqual(grid.card_height, 200.0)

        # Columnas automáticas para un ancho de 700px con tarjetas de 200px + 16px espaciado
        cols_auto = grid.calculate_columns(available_width=700)
        self.assertEqual(cols_auto, 3)

        # Columnas fijas
        grid.cards_per_row = 5
        self.assertEqual(grid.calculate_columns(available_width=700), 5)

    # =========================================================================
    # 3. SUBMODO FORMA LIBRE (CorkboardFreeform / Freeform Corkboard)
    # =========================================================================

    def test_corkboard_freeform_positioning_and_zoom(self):
        """Valida que en modo Libre las tarjetas se posicionen libremente sin alterar el Binder."""
        widget = CorkboardWidget(self.project)
        widget.load_container(self.cap1)
        widget.set_mode(CorkboardMode.FREEFORM)

        # Modificar posiciones libres 2D
        widget.set_freeform_card_position(widget.cards[0].uuid, 450.0, 300.0)
        widget.set_freeform_card_position(widget.cards[1].uuid, 50.0, 60.0)
        widget.set_freeform_card_position(widget.cards[2].uuid, 220.0, 60.0)

        # El orden en el Binder NO ha cambiado
        self.assertEqual(self.cap1.children[0].uuid, self.scene1.uuid)
        self.assertEqual(self.cap1.children[1].uuid, self.scene2.uuid)
        self.assertEqual(self.cap1.children[2].uuid, self.scene3.uuid)

        # Zoom y paneo
        freeform = widget.freeform
        freeform.set_zoom(1.5)
        self.assertEqual(freeform.zoom, 1.5)
        freeform.pan(100.0, 50.0)
        self.assertEqual(freeform.pan_x, 100.0)
        self.assertEqual(freeform.pan_y, 50.0)

    def test_corkboard_freeform_commit_order_to_binder(self):
        """Valida que 'Confirmar orden libre al Binder' reorganice el manuscrito según las posiciones 2D."""
        widget = CorkboardWidget(self.project)
        widget.load_container(self.cap1)
        widget.set_mode(CorkboardMode.FREEFORM)

        # Ubicar tarjeta 2 arriba a la izquierda (x=40, y=50)
        widget.set_freeform_card_position(self.scene2.uuid, 40.0, 50.0)
        # Ubicar tarjeta 3 arriba a la derecha (x=300, y=50)
        widget.set_freeform_card_position(self.scene3.uuid, 300.0, 50.0)
        # Ubicar tarjeta 1 abajo (x=100, y=250)
        widget.set_freeform_card_position(self.scene1.uuid, 100.0, 250.0)

        # Confirmar orden al Binder
        ordered = widget.commit_freeform_order_to_binder()
        self.assertEqual(ordered, [self.scene2.uuid, self.scene3.uuid, self.scene1.uuid])

        # Nuevo orden esperado en el Binder: scene2 primero, luego scene3, luego scene1
        self.assertEqual(self.cap1.children[0].uuid, self.scene2.uuid)
        self.assertEqual(self.cap1.children[1].uuid, self.scene3.uuid)
        self.assertEqual(self.cap1.children[2].uuid, self.scene1.uuid)

    # =========================================================================
    # 4. SUBMODO APILADO POR ETIQUETA / SWIMLANES (CorkboardSwimlanes)
    # =========================================================================

    def test_corkboard_swimlanes_classification(self):
        """Valida que las tarjetas se agrupen en columnas/carriles según sus etiquetas."""
        widget = CorkboardWidget(self.project)
        widget.load_container(self.cap1)
        widget.set_mode(CorkboardMode.SWIMLANES)

        columns = widget.swimlanes.columns
        self.assertIn(1, columns)
        self.assertIn(2, columns)

        # Carril 1: contiene scene1 y scene3
        lane1 = columns[1]
        self.assertEqual(len(lane1.cards), 2)
        self.assertEqual(lane1.cards[0].uuid, self.scene1.uuid)
        self.assertEqual(lane1.cards[1].uuid, self.scene3.uuid)

        # Carril 2: contiene scene2
        lane2 = columns[2]
        self.assertEqual(len(lane2.cards), 1)
        self.assertEqual(lane2.cards[0].uuid, self.scene2.uuid)

    def test_corkboard_swimlanes_drag_and_drop_label_reassignment(self):
        """Valida que arrastrar una tarjeta a otro carril actualice su etiqueta y posición en el Binder."""
        widget = CorkboardWidget(self.project)
        widget.load_container(self.cap1)
        widget.set_mode(CorkboardMode.SWIMLANES)

        # Mover scene1 (que tenía etiqueta 1) al carril 2
        success = widget.move_card_to_swimlane(self.scene1.uuid, target_label_id=2)
        self.assertTrue(success)

        # Verificar que la tarjeta y el BinderItem ahora tengan label_id = 2
        card1 = widget.get_card(self.scene1.uuid)
        self.assertIsNotNone(card1)
        self.assertEqual(card1.label_id, 2)
        self.assertEqual(self.scene1.data.label_id, 2)

    # =========================================================================
    # 5. BARRA INFERIOR DE CONTROL Y ESTÉTICA (CorkboardFooterBar)
    # =========================================================================

    def test_corkboard_footer_controls(self):
        """Valida que los controles de la barra inferior modifiquen el estado visual en vivo."""
        footer = CorkboardFooterBar()
        self.assertEqual(footer.aspect_ratio, CardAspectRatio.RATIO_3x5)

        # Establecer ratio
        footer.set_aspect_ratio(CardAspectRatio.RATIO_4x6)
        self.assertEqual(footer.aspect_ratio, CardAspectRatio.RATIO_4x6)
        footer.set_aspect_ratio(CardAspectRatio.RATIO_1x1)
        self.assertEqual(footer.aspect_ratio, CardAspectRatio.RATIO_1x1)

        # Modificar tarjetas por fila
        footer.set_cards_per_row(4)
        self.assertEqual(footer.cards_per_row, 4)
        footer.set_cards_per_row(0)  # Auto
        self.assertEqual(footer.cards_per_row, 0)

        # Conmutadores de sellos, pines, líneas y palabras clave
        self.assertTrue(footer.show_status_stamps)
        self.assertFalse(footer.toggle_status_stamps())
        self.assertFalse(footer.show_status_stamps)

        self.assertTrue(footer.show_pins)
        self.assertFalse(footer.toggle_pins())
        self.assertFalse(footer.show_pins)

        self.assertTrue(footer.show_notebook_lines)
        self.assertFalse(footer.toggle_notebook_lines())
        self.assertFalse(footer.show_notebook_lines)

        self.assertTrue(footer.show_keyword_chips)
        self.assertFalse(footer.toggle_keyword_chips())
        self.assertFalse(footer.show_keyword_chips)

    # =========================================================================
    # 6. INTEGRACIÓN CON MAINWINDOW, ATAJOS Y TELEMETRÍA
    # =========================================================================

    def test_main_window_corkboard_toggle_shortcut(self):
        """Valida que MainWindow integre CorkboardWidget y que Ctrl+2 conmute el modo Corcho."""
        win = MainWindow(self.project)
        self.assertEqual(win.view_mode, CentralViewMode.EDITOR)

        # Simular activación con Ctrl+2
        win.toggle_corkboard_mode()
        self.assertEqual(win.view_mode, CentralViewMode.CORKBOARD)
        self.assertIsNotNone(win.corkboard_widget)

        # Conmutar de nuevo vuelve al editor
        win.toggle_corkboard_mode()
        self.assertEqual(win.view_mode, CentralViewMode.EDITOR)

    def test_corkboard_view_data_telemetry(self):
        """Valida la generación del árbol de datos para la capa gráfica/UI."""
        widget = CorkboardWidget(self.project)
        widget.load_container(self.cap1)
        data = widget.get_view_data(1200.0)

        self.assertEqual(data["mode"], "grid")
        self.assertEqual(data["card_count"], 3)
        self.assertIn("footer", data)
        self.assertIn("layout", data)

    def test_corkboard_backward_compatibility_adapter(self):
        """Valida que CorkboardView y CorkboardCard mantengan compatibilidad total con código previo."""
        view = CorkboardView()
        card = CorkboardCard(
            item_id=self.scene1.uuid,
            title="Escena 1.1",
            synopsis="Resumen breve",
            label_color="#EA580C",
            status="Borrador"
        )
        view.add_card(card)
        self.assertEqual(len(view.cards), 1)
        self.assertEqual(view.cards[0].title, "Escena 1.1")
        self.assertEqual(view.cards[0].label_color, "#EA580C")


if __name__ == "__main__":
    unittest.main()
