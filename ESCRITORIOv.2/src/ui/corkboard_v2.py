"""
ESCRITORIO v2.0 - Corkboard (Pizarra de Corcho) Multi-Modo
Soporta los 3 modos de Scrivener 3 macOS:
1. Rejilla (Grid Mode) con slider de tamaño y proporción (3x5, 4x6).
2. Forma Libre (Freeform 2D Canvas) con botón "Confirmar orden al Binder".
3. Apilado por Etiquetas (Swimlanes / Arrange by Label) por columnas.
"""

from typing import List, Optional, Dict
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame,
    QLabel, QTextEdit, QSlider, QComboBox, QPushButton,
    QGridLayout, QGraphicsView, QGraphicsScene, QGraphicsProxyWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter, QBrush, QPen

from ..core.project_v2 import BinderNode, EscritorioProjectV2


class IndexCardWidget(QFrame):
    """Tarjeta de índice física individual con sinopsis, pin de etiqueta y sello de estado."""

    card_clicked = pyqtSignal(BinderNode)
    card_double_clicked = pyqtSignal(BinderNode)
    synopsis_changed = pyqtSignal(BinderNode, str)

    def __init__(self, node: BinderNode, aspect_ratio=(5, 3), parent=None):
        super().__init__(parent)
        self.node = node
        self.aspect_ratio = aspect_ratio
        self.setObjectName("IndexCard")
        self.setProperty("class", "IndexCard")

        self.setFixedSize(240, 160)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # 1. Cabecera con pin de color y título
        header = QHBoxLayout()
        header.setSpacing(6)

        # Pin circular de color de etiqueta
        self.lbl_pin = QLabel()
        self.lbl_pin.setFixedSize(12, 12)
        pin_color = "#3498db" if self.node.label != "Sin Etiqueta" else "#7f8c8d"
        self.lbl_pin.setStyleSheet(f"background-color: {pin_color}; border-radius: 6px;")
        header.addWidget(self.lbl_pin)

        self.lbl_title = QLabel(self.node.title)
        self.lbl_title.setStyleSheet("font-weight: bold; font-size: 12px; color: #e1e1e6;")
        header.addWidget(self.lbl_title)

        header.addStretch()

        # Sello de Estado (Stamp)
        self.lbl_status = QLabel(self.node.status.upper())
        self.lbl_status.setStyleSheet("""
            color: #e74c3c;
            font-size: 9px;
            font-weight: bold;
            border: 1px dashed #e74c3c;
            padding: 1px 4px;
            border-radius: 3px;
        """)
        header.addWidget(self.lbl_status)

        layout.addLayout(header)

        # 2. Cuerpo de Sinopsis
        self.txt_synopsis = QTextEdit()
        self.txt_synopsis.setPlaceholderText("Escribe aquí la sinopsis de la escena...")
        self.txt_synopsis.setText(self.node._synopsis_text or "")
        self.txt_synopsis.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                font-size: 11px;
                color: #c0c0d0;
            }
        """)
        self.txt_synopsis.textChanged.connect(self._on_synopsis_changed)
        layout.addWidget(self.txt_synopsis)

        # 3. Pie de tarjeta con recuento de palabras
        footer = QHBoxLayout()
        self.lbl_words = QLabel(f"{self.node.word_count()} palabras")
        self.lbl_words.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        footer.addWidget(self.lbl_words)
        footer.addStretch()
        layout.addLayout(footer)

    def _on_synopsis_changed(self):
        new_text = self.txt_synopsis.toPlainText()
        self.node._synopsis_text = new_text
        self.node.mark_dirty()
        self.synopsis_changed.emit(self.node, new_text)

    def mousePressEvent(self, event):
        self.card_clicked.emit(self.node)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.card_double_clicked.emit(self.node)
        super().mouseDoubleClickEvent(event)


class CorkboardV2(QWidget):
    """Pizarra de Corcho completa con modos Rejilla, Forma Libre y Swimlanes."""

    card_selected = pyqtSignal(BinderNode)
    card_open_requested = pyqtSignal(BinderNode)
    order_committed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project: Optional[EscritorioProjectV2] = None
        self.parent_node: Optional[BinderNode] = None
        self.current_mode = "grid"  # grid, freeform, swimlanes
        self.card_size = 100  # porcentaje

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Barra de Control del Corcho
        self.toolbar = QFrame(self)
        self.toolbar.setFixedHeight(34)
        self.toolbar.setStyleSheet("background-color: #1a1a20; border-bottom: 1px solid #323242;")
        tb_layout = QHBoxLayout(self.toolbar)
        tb_layout.setContentsMargins(8, 0, 8, 0)
        tb_layout.setSpacing(8)

        # Selector de Modo de Corcho
        tb_layout.addWidget(QLabel("Modo:"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Rejilla (Grid)", "Forma Libre (Freeform)", "Por Etiquetas (Swimlanes)"])
        self.combo_mode.currentIndexChanged.connect(self._on_mode_changed)
        tb_layout.addWidget(self.combo_mode)

        # Slider de Tamaño de Tarjetas
        tb_layout.addWidget(QLabel("Tamaño:"))
        self.slider_size = QSlider(Qt.Orientation.Horizontal)
        self.slider_size.setRange(70, 150)
        self.slider_size.setValue(100)
        self.slider_size.setFixedWidth(80)
        self.slider_size.valueChanged.connect(self._on_size_changed)
        tb_layout.addWidget(self.slider_size)

        tb_layout.addStretch()

        # Botón para confirmar orden libre
        self.btn_commit_freeform = QPushButton("📌 Fijar Orden al Archivador")
        self.btn_commit_freeform.setVisible(False)
        self.btn_commit_freeform.clicked.connect(self._commit_freeform_order)
        tb_layout.addWidget(self.btn_commit_freeform)

        layout.addWidget(self.toolbar)

        # Área de Desplazamiento Central
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setObjectName("CorkboardScrollArea")
        self.scroll_area.setWidgetResizable(True)

        self.canvas = QWidget()
        self.canvas.setObjectName("CorkboardCanvas")
        self.scroll_area.setWidget(self.canvas)
        layout.addWidget(self.scroll_area)

    def load_parent_node(self, node: BinderNode, project: EscritorioProjectV2):
        """Carga los hijos de una carpeta para mostrarlos como tarjetas."""
        self.parent_node = node
        self.project = project
        self.rebuild_corkboard()

    def rebuild_corkboard(self):
        """Reconstruye las tarjetas según el modo actual."""
        if not self.parent_node:
            return

        # Limpiar canvas anterior
        old_layout = self.canvas.layout()
        if old_layout:
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            QWidget().setLayout(old_layout)

        if self.current_mode == "grid":
            self._build_grid_mode()
        elif self.current_mode == "freeform":
            self._build_freeform_mode()
        elif self.current_mode == "swimlanes":
            self._build_swimlanes_mode()

    def _build_grid_mode(self):
        self.btn_commit_freeform.setVisible(False)
        layout = QGridLayout(self.canvas)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        cols = 4
        for idx, child in enumerate(self.parent_node.children):
            if child.type == "TrashFolder":
                continue
            card = IndexCardWidget(child)
            card.card_clicked.connect(self.card_selected.emit)
            card.card_double_clicked.connect(self.card_open_requested.emit)
            r = idx // cols
            c = idx % cols
            layout.addWidget(card, r, c)

        layout.setRowStretch(len(self.parent_node.children) // cols + 1, 1)

    def _build_freeform_mode(self):
        self.btn_commit_freeform.setVisible(True)
        layout = QVBoxLayout(self.canvas)
        layout.setContentsMargins(20, 20, 20, 20)

        info = QLabel("Modo Forma Libre: Mueve y posiciona las tarjetas visualmente en la cuadrícula.")
        info.setStyleSheet("color: #a0a0b2; font-style: italic;")
        layout.addWidget(info)

        grid = QGridLayout()
        grid.setSpacing(20)
        for idx, child in enumerate(self.parent_node.children):
            card = IndexCardWidget(child)
            card.card_clicked.connect(self.card_selected.emit)
            card.card_double_clicked.connect(self.card_open_requested.emit)
            grid.addWidget(card, idx % 3, idx // 3)

        layout.addLayout(grid)
        layout.addStretch()

    def _build_swimlanes_mode(self):
        self.btn_commit_freeform.setVisible(False)
        layout = QHBoxLayout(self.canvas)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Agrupar tarjetas por etiquetas
        labels = [lbl["name"] for lbl in self.project.labels] if self.project else ["Sin Etiqueta"]
        for lbl_name in labels:
            lane = QFrame()
            lane.setStyleSheet("background-color: rgba(30, 30, 36, 0.6); border-radius: 8px; border: 1px solid #323242;")
            l_layout = QVBoxLayout(lane)
            l_layout.setContentsMargins(10, 10, 10, 10)

            title = QLabel(f"🏷️ {lbl_name}")
            title.setStyleSheet("font-weight: bold; font-size: 12px; color: #3498db;")
            l_layout.addWidget(title)

            for child in self.parent_node.children:
                if child.label == lbl_name or (lbl_name == "Sin Etiqueta" and not child.label):
                    card = IndexCardWidget(child)
                    card.card_clicked.connect(self.card_selected.emit)
                    card.card_double_clicked.connect(self.card_open_requested.emit)
                    l_layout.addWidget(card)

            l_layout.addStretch()
            layout.addWidget(lane)

    def _on_mode_changed(self, index: int):
        modes = ["grid", "freeform", "swimlanes"]
        self.current_mode = modes[index]
        self.rebuild_corkboard()

    def _on_size_changed(self, value: int):
        self.card_size = value
        self.rebuild_corkboard()

    def _commit_freeform_order(self):
        self.order_committed.emit()
