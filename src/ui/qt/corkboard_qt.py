"""
Pizarra de Corcho (Corkboard) interactiva para PyQt6.
Permite visualizar, ordenar y editar tarjetas de índice de escenas con sinopsis y etiquetas.
"""

from typing import List, Optional, Callable
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame,
    QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from ...core.project import EscritorioProject, BinderItem


class IndexCardWidget(QFrame):
    """Tarjeta de índice individual del Corcho."""
    clicked = pyqtSignal(str)
    contentChanged = pyqtSignal(str, str, str)  # uuid, title, synopsis

    def __init__(self, item: BinderItem, parent=None):
        super().__init__(parent)
        self.item = item
        self.uuid = item.uuid
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedSize(240, 180)
        self.setStyleSheet("""
            IndexCardWidget {
                background-color: #2b2b36;
                border: 1px solid #4a4a5a;
                border-radius: 8px;
            }
            IndexCardWidget:hover {
                border: 2px solid #7c5cbf;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Barra superior de la tarjeta (Color de etiqueta, título y estado)
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Pin o badge de color
        self.badge = QLabel()
        self.badge.setFixedSize(12, 12)
        color = getattr(item, "status_color", "#7c5cbf") or "#7c5cbf"
        self.badge.setStyleSheet(f"background-color: {color}; border-radius: 6px;")
        top_layout.addWidget(self.badge)

        # Título editable
        self.title_edit = QLineEdit(item.title)
        self.title_edit.setStyleSheet("font-weight: bold; border: none; background: transparent;")
        self.title_edit.textChanged.connect(self._on_title_changed)
        top_layout.addWidget(self.title_edit)

        # Sello de estado (Borrador, En Revisión, Final)
        status_text = getattr(item.data, "status", "Borrador") or "Borrador"
        self.status_lbl = QLabel(status_text)
        self.status_lbl.setStyleSheet("font-size: 8pt; color: #a0a0b0; padding: 2px 4px; background: rgba(0,0,0,0.2); border-radius: 4px;")
        top_layout.addWidget(self.status_lbl)

        layout.addLayout(top_layout)

        # Cuerpo: Sinopsis editable
        self.synopsis_edit = QTextEdit()
        synopsis_val = item.get_synopsis() if hasattr(item, "get_synopsis") else ""
        if not synopsis_val and hasattr(item, "synopsis"):
            synopsis_val = item.synopsis or ""
        self.synopsis_edit.setPlainText(synopsis_val)
        self.synopsis_edit.setPlaceholderText("Escribe aquí la sinopsis de la escena...")
        self.synopsis_edit.setStyleSheet("border: 1px solid #3a3a48; border-radius: 4px; font-size: 9pt;")
        self.synopsis_edit.textChanged.connect(self._on_synopsis_changed)
        layout.addWidget(self.synopsis_edit)

        # Pie de tarjeta: Recuento de palabras
        footer_layout = QHBoxLayout()
        wc = item.get_word_count() if hasattr(item, "get_word_count") else 0
        self.wc_lbl = QLabel(f"{wc} palabras")
        self.wc_lbl.setStyleSheet("font-size: 8pt; color: #888899;")
        footer_layout.addWidget(self.wc_lbl)

        layout.addLayout(footer_layout)

    def mousePressEvent(self, event):
        self.clicked.emit(self.uuid)
        super().mousePressEvent(event)

    def _on_title_changed(self, text: str):
        self.item.title = text
        if hasattr(self.item.data, "title"):
            self.item.data.title = text
        self.contentChanged.emit(self.uuid, text, self.synopsis_edit.toPlainText())

    def _on_synopsis_changed(self):
        text = self.synopsis_edit.toPlainText()
        if hasattr(self.item, "set_synopsis"):
            self.item.set_synopsis(text)
        elif hasattr(self.item, "synopsis"):
            self.item.synopsis = text
        self.contentChanged.emit(self.uuid, self.title_edit.text(), text)


class CorkboardQt(QWidget):
    """Panel principal del Corcho con soporte para cuadrícula y carriles de etiquetas."""
    cardSelected = pyqtSignal(str)

    def __init__(self, project: Optional[EscritorioProject] = None, parent=None):
        super().__init__(parent)
        self.project = project
        self.current_folder: Optional[BinderItem] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Barra superior de controles del corcho
        toolbar_layout = QHBoxLayout()
        self.lbl_title = QLabel("Pizarra de Corcho")
        self.lbl_title.setStyleSheet("font-size: 11pt; font-weight: bold;")
        toolbar_layout.addWidget(self.lbl_title)

        toolbar_layout.addStretch()

        self.btn_mode = QPushButton("Modo Rejilla")
        self.btn_mode.setCheckable(True)
        toolbar_layout.addWidget(self.btn_mode)

        layout.addLayout(toolbar_layout)

        # Área de scroll con cuadrícula de tarjetas
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.container = QWidget()
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

    def set_folder(self, folder: BinderItem):
        """Carga las escenas hijas de una carpeta en la pizarra de corcho."""
        self.current_folder = folder
        self.lbl_title.setText(f"Corcho: {folder.title}")

        # Limpiar cuadrícula previa
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        children = folder.children if hasattr(folder, "children") else []
        col_count = 3
        for i, child in enumerate(children):
            card = IndexCardWidget(child)
            card.clicked.connect(self.cardSelected.emit)
            row = i // col_count
            col = i % col_count
            self.grid_layout.addWidget(card, row, col)
