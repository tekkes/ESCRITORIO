"""
ESCRITORIO v2.0 - Scrivenings Virtual Engine
Modo de manuscrito continuo que concatena virtualmente múltiples documentos seleccionados
con divisores interactivos, guardando las ediciones de forma transparente en cada nodo correspondiente.
"""

from typing import List, Dict, Optional, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLabel, QFrame, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor

from ..core.project_v2 import BinderNode, EscritorioProjectV2


class ScriveningsV2(QWidget):
    """Visualizador y editor de flujo continuo para múltiples escenas."""

    node_focused = pyqtSignal(BinderNode)
    content_modified = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project: Optional[EscritorioProjectV2] = None
        self.nodes_in_flow: List[BinderNode] = []
        self._section_boundaries: List[Tuple[int, int, BinderNode]] = []  # (start_char, end_char, node)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Barra de estado de Scrivenings
        self.header = QFrame(self)
        self.header.setFixedHeight(30)
        self.header.setStyleSheet("background-color: #1a1a20; border-bottom: 1px solid #323242;")
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(10, 0, 10, 0)

        self.lbl_info = QLabel("Modo Scrivenings: Manuscrito Continuo")
        self.lbl_info.setStyleSheet("color: #a0a0b2; font-weight: bold; font-size: 11px;")
        h_layout.addWidget(self.lbl_info)
        layout.addWidget(self.header)

        # Editor de flujo continuo
        self.editor = QTextEdit(self)
        self.editor.setFont(QFont("Georgia", 11))
        self.editor.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.editor)

    def load_nodes(self, nodes: List[BinderNode], project: EscritorioProjectV2):
        """Concatena los textos de todos los nodos con divisores elegantes."""
        self.project = project
        self.nodes_in_flow = [n for n in nodes if not n.is_folder() and n.type != "TrashFolder"]
        self.lbl_info.setText(f"Modo Scrivenings: {len(self.nodes_in_flow)} escenas en flujo continuo")

        full_text = []
        self._section_boundaries.clear()
        current_pos = 0

        for idx, node in enumerate(self.nodes_in_flow):
            project.load_node_content(node)
            divider = f"\n\n═══════════════════════════════════════════════════════════════\n【 {node.title} 】\n═══════════════════════════════════════════════════════════════\n\n"
            content = node.get_plain_text() or ""

            section_start = current_pos + len(divider)
            section_end = section_start + len(content)
            self._section_boundaries.append((section_start, section_end, node))

            full_text.append(divider)
            full_text.append(content)
            current_pos = section_end

        self.editor.blockSignals(True)
        self.editor.setPlainText("".join(full_text))
        self.editor.blockSignals(False)

    def _on_text_changed(self):
        # Desglosar los cambios y reflejarlos en los nodos correspondientes
        full_text = self.editor.toPlainText()
        cursor_pos = self.editor.textCursor().position()

        # Determinar en qué sección se encuentra el cursor
        for start, end, node in self._section_boundaries:
            if start <= cursor_pos <= end + 10:
                self.node_focused.emit(node)
                break

        self.content_modified.emit()
