"""
ESCRITORIO v2.0 - Outliner (Esquema Editorial Jerárquico)
Vista matricial avanzada tipo tabla-árbol con columnas configurables, recuentos recursivos,
barras de progreso gráficas coloreadas y casillas de compilación idénticas a Scrivener 3 macOS.
"""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QProgressBar, QHeaderView, QMenu, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QBrush, QFont

from ..core.project_v2 import BinderNode, EscritorioProjectV2


class ProgressBarWidget(QProgressBar):
    """Barra de progreso visual con degradado dinámico de rojo a verde."""

    def __init__(self, current: int, target: int, parent=None):
        super().__init__(parent)
        self.setFixedHeight(14)
        self.setTextVisible(True)
        self.setMaximum(max(1, target))
        self.setValue(min(current, target))

        pct = (current / target * 100) if target > 0 else 0
        if pct < 35:
            col = "#e74c3c"  # Rojo
        elif pct < 75:
            col = "#f39c12"  # Ámbar
        else:
            col = "#2ecc71"  # Verde

        self.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #323242;
                border-radius: 4px;
                text-align: center;
                font-size: 9px;
                color: #ffffff;
                background-color: #1e1e24;
            }}
            QProgressBar::chunk {{
                background-color: {col};
                border-radius: 3px;
            }}
        """)


class OutlinerV2(QWidget):
    """Esquema editorial con columnas dinámicas y totales acumulados."""

    node_selected = pyqtSignal(BinderNode)
    node_double_clicked = pyqtSignal(BinderNode)

    COL_TITLE = 0
    COL_SECTION_TYPE = 1
    COL_LABEL = 2
    COL_STATUS = 3
    COL_WORDS = 4
    COL_TOTAL_WORDS = 5
    COL_TARGET = 6
    COL_PROGRESS = 7
    COL_COMPILE = 8

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_node: Optional[BinderNode] = None
        self.project: Optional[EscritorioProjectV2] = None

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tree = QTreeWidget(self)
        self.tree.setColumnCount(9)
        self.tree.setHeaderLabels([
            "Título", "Tipo", "Etiqueta", "Estado",
            "Palabras", "Total Palabras", "Objetivo", "Progreso", "Compilar"
        ])

        header = self.tree.header()
        header.setSectionResizeMode(self.COL_TITLE, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(self.COL_PROGRESS, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(self.COL_PROGRESS, 120)
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self._on_header_context_menu)

        self.tree.setSortingEnabled(True)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.itemDoubleClicked.connect(self._on_double_clicked)
        self.tree.itemChanged.connect(self._on_item_changed)

        layout.addWidget(self.tree)

    def load_parent_node(self, node: BinderNode, project: EscritorioProjectV2):
        """Carga y calcula recursivamente las columnas del esquema."""
        self.parent_node = node
        self.project = project
        self.rebuild_outliner()

    def rebuild_outliner(self):
        self.tree.clear()
        if not self.parent_node:
            return

        for child in self.parent_node.children:
            self._add_child_recursive(self.tree.invisibleRootItem(), child)

        self.tree.expandAll()

    def _add_child_recursive(self, parent_item, node: BinderNode):
        item = QTreeWidgetItem()
        item.setText(self.COL_TITLE, node.title)
        item.setText(self.COL_SECTION_TYPE, node.section_type)
        item.setText(self.COL_LABEL, node.label)
        item.setText(self.COL_STATUS, node.status)

        words = node.word_count()
        total_words = node.total_word_count()
        item.setText(self.COL_WORDS, str(words))
        item.setText(self.COL_TOTAL_WORDS, str(total_words))
        item.setText(self.COL_TARGET, str(node.target_words))

        # Checkbox para Incluir en Compilación
        item.setCheckState(self.COL_COMPILE, Qt.CheckState.Checked if node.include_in_compile else Qt.CheckState.Unchecked)
        item.setData(0, Qt.ItemDataRole.UserRole, node.uuid)

        parent_item.addChild(item)

        # Barra de progreso gráfica
        if node.target_words > 0:
            bar = ProgressBarWidget(words, node.target_words)
            self.tree.setItemWidget(item, self.COL_PROGRESS, bar)

        for child in node.children:
            self._add_child_recursive(item, child)

    def _on_selection_changed(self):
        items = self.tree.selectedItems()
        if items and self.project:
            uuid_str = items[0].data(0, Qt.ItemDataRole.UserRole)
            node = self.project.find_node_by_uuid(uuid_str)
            if node:
                self.node_selected.emit(node)

    def _on_double_clicked(self, item, col):
        if self.project:
            uuid_str = item.data(0, Qt.ItemDataRole.UserRole)
            node = self.project.find_node_by_uuid(uuid_str)
            if node:
                self.node_double_clicked.emit(node)

    def _on_item_changed(self, item, col):
        if col == self.COL_COMPILE and self.project:
            uuid_str = item.data(0, Qt.ItemDataRole.UserRole)
            node = self.project.find_node_by_uuid(uuid_str)
            if node:
                node.include_in_compile = (item.checkState(col) == Qt.CheckState.Checked)
                node.mark_dirty()

    def _on_header_context_menu(self, pos):
        menu = QMenu(self)
        cols = [
            ("Tipo de Sección", self.COL_SECTION_TYPE),
            ("Etiqueta", self.COL_LABEL),
            ("Estado", self.COL_STATUS),
            ("Palabras", self.COL_WORDS),
            ("Total Palabras", self.COL_TOTAL_WORDS),
            ("Objetivo", self.COL_TARGET),
            ("Progreso", self.COL_PROGRESS),
            ("Compilar", self.COL_COMPILE),
        ]
        for name, col_idx in cols:
            act = menu.addAction(name)
            act.setCheckable(True)
            act.setChecked(not self.tree.isColumnHidden(col_idx))
            act.toggled.connect(lambda chk, c=col_idx: self.tree.setColumnHidden(c, not chk))

        menu.exec(self.tree.header().mapToGlobal(pos))
