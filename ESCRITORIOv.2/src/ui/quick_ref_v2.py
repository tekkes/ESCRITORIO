"""
ESCRITORIO v2.0 - Quick Reference Windows (Ventanas Flotantes de Referencia Rápida)
Permite abrir múltiples documentos, notas o imágenes en ventanas independientes para configuraciones multimonitor.
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTextEdit, QLabel, QToolBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction

from ..core.project_v2 import BinderNode


class QuickReferenceWindow(QMainWindow):
    """Ventana flotante independiente para un documento de referencia rápida."""

    def __init__(self, node: BinderNode, parent=None):
        super().__init__(parent)
        self.node = node
        self.setWindowTitle(f"Referencia Rápida: {node.title}")
        self.resize(550, 600)

        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)

        # Barra superior con opciones
        toolbar = QToolBar("QR Controls")
        self.addToolBar(toolbar)

        act_pin = toolbar.addAction("📌 Fijar Siempre Encima")
        act_pin.setCheckable(True)
        act_pin.toggled.connect(self._toggle_pin)

        # Editor de solo lectura o edición ligera
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Georgia", 11))
        self.editor.setPlainText(self.node.get_plain_text())
        self.editor.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.editor)

        self.setCentralWidget(central)

    def _toggle_pin(self, checked: bool):
        flags = self.windowFlags()
        if checked:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()

    def _on_text_changed(self):
        self.node._content_rtf = self.editor.toPlainText()
        self.node.mark_dirty()
