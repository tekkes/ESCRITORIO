"""
ESCRITORIO v2.0 - Composition Mode (Modo Pantalla Completa Libre de Distracciones)
Lienzo central de escritura con fondo personalizable, ancho de hoja ajustable y barra flotante auto-ocultable.
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
    QSlider, QToolButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor

from ..core.project_v2 import BinderNode


class CompositionModeV2(QWidget):
    """Modo composición inmersivo a pantalla completa (F11)."""

    exit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #121216;")

        self.current_node: Optional[BinderNode] = None
        self.paper_width = 800

        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # Contenedor central centrado
        center_box = QHBoxLayout()
        center_box.addStretch()

        self.paper_frame = QFrame()
        self.paper_frame.setFixedWidth(self.paper_width)
        self.paper_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a22;
                border: 1px solid #2a2a36;
                border-radius: 8px;
            }
        """)
        p_layout = QVBoxLayout(self.paper_frame)
        p_layout.setContentsMargins(40, 40, 40, 40)

        self.editor = QTextEdit()
        self.editor.setFont(QFont("Georgia", 13))
        self.editor.setStyleSheet("border: none; background: transparent; color: #e1e1e6; line-height: 1.8;")
        self.editor.textChanged.connect(self._on_text_changed)
        p_layout.addWidget(self.editor)

        center_box.addWidget(self.paper_frame)
        center_box.addStretch()
        root_layout.addLayout(center_box)

        # Barra de control inferior auto-ocultable
        self.control_bar = QFrame(self)
        self.control_bar.setFixedHeight(44)
        self.control_bar.setStyleSheet("""
            QFrame {
                background-color: rgba(26, 26, 34, 0.95);
                border-top: 1px solid #323242;
                border-radius: 8px;
                margin: 0 100px 10px 100px;
            }
        """)
        c_layout = QHBoxLayout(self.control_bar)
        c_layout.setContentsMargins(20, 0, 20, 0)
        c_layout.setSpacing(14)

        self.lbl_stats = QLabel("0 palabras")
        self.lbl_stats.setStyleSheet("color: #a0a0b2; font-size: 11px;")
        c_layout.addWidget(self.lbl_stats)

        c_layout.addStretch()

        # Ancho de papel
        c_layout.addWidget(QLabel("Ancho:"))
        self.slider_width = QSlider(Qt.Orientation.Horizontal)
        self.slider_width.setRange(500, 1200)
        self.slider_width.setValue(800)
        self.slider_width.setFixedWidth(100)
        self.slider_width.valueChanged.connect(self._on_width_changed)
        c_layout.addWidget(self.slider_width)

        # Botón salir
        self.btn_exit = QToolButton()
        self.btn_exit.setText("✖ Salir de Pantalla Completa (Esc)")
        self.btn_exit.clicked.connect(self._exit)
        c_layout.addWidget(self.btn_exit)

        root_layout.addWidget(self.control_bar)

    def load_node(self, node: BinderNode):
        self.current_node = node
        self.editor.blockSignals(True)
        self.editor.setPlainText(node.get_plain_text())
        self.editor.blockSignals(False)
        self._update_stats()

    def _on_text_changed(self):
        if self.current_node:
            self.current_node._content_rtf = self.editor.toPlainText()
            self.current_node.mark_dirty()
            self._update_stats()

    def _update_stats(self):
        text = self.editor.toPlainText()
        words = len(text.split()) if text else 0
        self.lbl_stats.setText(f"{words} palabras")

    def _on_width_changed(self, val):
        self.paper_frame.setFixedWidth(val)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self._exit()
        else:
            super().keyPressEvent(event)

    def _exit(self):
        self.hide()
        self.exit_requested.emit()
