"""
Modo Composición libre de distracciones a pantalla completa para PyQt6 (F11).
Hoja de papel central de ancho y posición ajustables con barra inferior flotante auto-ocultable.
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLabel, QSlider, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QColor

from ...core.project import BinderItem


class CompositionModeQt(QMainWindow):
    """Ventana a pantalla completa sin distracciones."""
    contentSaved = pyqtSignal(str, str)  # uuid, new_text

    def __init__(self, item: BinderItem, parent=None):
        super().__init__(parent)
        self.item = item
        self.uuid = item.uuid
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)

        self.backdrop = QWidget(self)
        self.setCentralWidget(self.backdrop)
        self.backdrop.setStyleSheet("background-color: #0f0f12;")

        main_layout = QVBoxLayout(self.backdrop)
        main_layout.setContentsMargins(0, 40, 0, 0)
        main_layout.setSpacing(0)

        # Hoja de papel central
        self.paper_container = QHBoxLayout()
        self.paper_container.addStretch(1)

        self.paper = QFrame()
        self.paper.setFixedWidth(850)
        self.paper.setStyleSheet("""
            QFrame {
                background-color: #1a1a22;
                border: 1px solid #2d2d3a;
                border-radius: 8px;
            }
        """)
        paper_layout = QVBoxLayout(self.paper)
        paper_layout.setContentsMargins(48, 48, 48, 48)

        # Título de la escena en la hoja
        self.lbl_title = QLabel(f"<h2>{item.title}</h2>")
        self.lbl_title.setStyleSheet("color: #e0e0ea; margin-bottom: 16px;")
        paper_layout.addWidget(self.lbl_title)

        # Editor de texto libre de distracciones
        self.editor = QTextEdit()
        self.editor.setStyleSheet("""
            QTextEdit {
                background: transparent;
                border: none;
                color: #e5e5f0;
                font-family: 'Georgia', serif;
                font-size: 13pt;
                line-height: 1.6;
            }
        """)
        plain = item.get_content_plain() if hasattr(item, "get_content_plain") else ""
        self.editor.setPlainText(plain)
        self.editor.textChanged.connect(self._on_text_changed)
        paper_layout.addWidget(self.editor)

        self.paper_container.addWidget(self.paper, 4)
        self.paper_container.addStretch(1)

        main_layout.addLayout(self.paper_container, 1)

        # Barra inferior auto-ocultable (HUD)
        self.hud_bar = QFrame()
        self.hud_bar.setFixedHeight(50)
        self.hud_bar.setStyleSheet("""
            QFrame {
                background-color: rgba(20, 20, 26, 0.92);
                border-top: 1px solid #333344;
            }
            QLabel { color: #aaaaee; font-size: 9pt; }
        """)
        hud_layout = QHBoxLayout(self.hud_bar)
        hud_layout.setContentsMargins(24, 0, 24, 0)

        hud_layout.addWidget(QLabel("Ancho de Hoja:"))
        self.slider_width = QSlider(Qt.Orientation.Horizontal)
        self.slider_width.setRange(500, 1400)
        self.slider_width.setValue(850)
        self.slider_width.setFixedWidth(120)
        self.slider_width.valueChanged.connect(self._on_width_changed)
        hud_layout.addWidget(self.slider_width)

        hud_layout.addSpacing(20)

        self.lbl_wc = QLabel("Palabras: 0  |  Caracteres: 0")
        hud_layout.addWidget(self.lbl_wc)
        self._update_metrics()

        hud_layout.addStretch()

        btn_exit = QPushButton("Salir de Composición (F11 / Esc)")
        btn_exit.setStyleSheet("padding: 4px 12px; background: #7c5cbf; color: white; border-radius: 4px;")
        btn_exit.clicked.connect(self.close)
        hud_layout.addWidget(btn_exit)

        main_layout.addWidget(self.hud_bar)

    def _on_width_changed(self, val: int):
        self.paper.setFixedWidth(val)

    def _on_text_changed(self):
        text = self.editor.toPlainText()
        if hasattr(self.item, "set_content_plain"):
            self.item.set_content_plain(text)
        self._update_metrics()
        self.contentSaved.emit(self.uuid, text)

    def _update_metrics(self):
        text = self.editor.toPlainText()
        words = len(text.split())
        chars = len(text)
        self.lbl_wc.setText(f"Palabras: {words:,}  |  Caracteres: {chars:,}")

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_F11):
            self.close()
        else:
            super().keyPressEvent(event)
