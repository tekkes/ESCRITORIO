"""
Esquema (Outliner) interactivo para PyQt6.
Tabla editorial con recuentos de palabras, metadatos y barras de progreso.
"""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal

from ...core.project import EscritorioProject, BinderItem


class OutlinerQt(QWidget):
    """Panel del Esquema con visualización tabular y jerárquica."""
    itemSelected = pyqtSignal(str)

    COLUMNS = [
        "Título", "Tipo", "Estado", "Etiqueta", "Palabras", "Palabras Totales", "Objetivo", "Progreso"
    ]

    def __init__(self, project: Optional[EscritorioProject] = None, parent=None):
        super().__init__(parent)
        self.project = project
        self.current_folder: Optional[BinderItem] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Cabecera
        self.lbl_title = QLabel("Esquema")
        self.lbl_title.setStyleSheet("font-size: 11pt; font-weight: bold; margin-bottom: 4px;")
        layout.addWidget(self.lbl_title)

        # Tabla del Outliner
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.table.itemChanged.connect(self._on_item_changed)

        layout.addWidget(self.table)

    def set_folder(self, folder: BinderItem):
        """Carga las escenas y carpetas hijas en el esquema."""
        self.current_folder = folder
        self.lbl_title.setText(f"Esquema: {folder.title}")

        children = folder.children if hasattr(folder, "children") else []
        self.table.blockSignals(True)
        self.table.setRowCount(len(children))

        for row, child in enumerate(children):
            uuid = child.uuid
            title = child.title
            item_type = getattr(child, "item_type", "Text")
            status = getattr(child.data, "status", "Borrador") or "Borrador"
            label = getattr(child.data, "label", "") or "General"
            
            wc = child.get_word_count() if hasattr(child, "get_word_count") else 0
            twc = child.get_total_word_count() if hasattr(child, "get_total_word_count") else wc
            target = getattr(child.data, "target_words", 2000) or 2000

            # 0. Título
            item_title = QTableWidgetItem(title)
            item_title.setData(Qt.ItemDataRole.UserRole, uuid)
            self.table.setItem(row, 0, item_title)

            # 1. Tipo
            self.table.setItem(row, 1, QTableWidgetItem(item_type))

            # 2. Estado
            self.table.setItem(row, 2, QTableWidgetItem(status))

            # 3. Etiqueta
            self.table.setItem(row, 3, QTableWidgetItem(label))

            # 4. Palabras
            item_wc = QTableWidgetItem(str(wc))
            item_wc.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 4, item_wc)

            # 5. Palabras Totales
            item_twc = QTableWidgetItem(str(twc))
            item_twc.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 5, item_twc)

            # 6. Objetivo
            item_tgt = QTableWidgetItem(str(target))
            item_tgt.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 6, item_tgt)

            # 7. Barra de Progreso
            pct = min(100, int((wc / target * 100))) if target > 0 else 0
            pbar = QProgressBar()
            pbar.setValue(pct)
            pbar.setFormat(f"{pct}%")
            self.table.setCellWidget(row, 7, pbar)

        self.table.blockSignals(False)

    def _on_item_double_clicked(self, item: QTableWidgetItem):
        row = item.row()
        title_item = self.table.item(row, 0)
        if title_item:
            uuid = title_item.data(Qt.ItemDataRole.UserRole)
            if uuid:
                self.itemSelected.emit(uuid)

    def _on_item_changed(self, item: QTableWidgetItem):
        row = item.row()
        col = item.column()
        title_item = self.table.item(row, 0)
        if not title_item or not self.project:
            return

        uuid = title_item.data(Qt.ItemDataRole.UserRole)
        child = self.project.get_item(uuid)
        if not child:
            return

        if col == 0:
            child.title = item.text()
            if hasattr(child.data, "title"):
                child.data.title = item.text()
        elif col == 2:
            if hasattr(child.data, "status"):
                child.data.status = item.text()
        elif col == 3:
            if hasattr(child.data, "label"):
                child.data.label = item.text()
