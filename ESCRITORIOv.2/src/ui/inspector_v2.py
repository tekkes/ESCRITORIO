"""
ESCRITORIO v2.0 - Inspector Scrivener 3 (6 Pestañas Especializadas)
1. Sinopsis y Metadatos generales (con soporte de imagen de tarjeta).
2. Notas de Documento.
3. Marcadores (Bookmarks internos y enlaces externos).
4. Palabras Clave (Keywords con colores).
5. Instantáneas (Snapshots con visor Diff cromático y restaurador seguro).
6. Comentarios y Notas al Pie vinculados.
"""

import time
import difflib
from typing import Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QTextEdit, QComboBox, QCheckBox, QPushButton, QListWidget,
    QListWidgetItem, QInputDialog, QMessageBox, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from ..core.project_v2 import BinderNode, SnapshotItem, CommentItem, EscritorioProjectV2


class InspectorV2(QWidget):
    """Panel Inspector lateral derecho de 6 pestañas."""

    data_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_node: Optional[BinderNode] = None
        self.project: Optional[EscritorioProjectV2] = None

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Cabecera del Inspector
        header = QFrame(self)
        header.setFixedHeight(34)
        header.setStyleSheet("background-color: #1a1a20; border-bottom: 1px solid #323242;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(10, 0, 10, 0)

        self.lbl_header = QLabel("Inspector")
        self.lbl_header.setStyleSheet("font-weight: bold; font-size: 13px; color: #e1e1e6;")
        h_layout.addWidget(self.lbl_header)
        layout.addWidget(header)

        # Pestañas del Inspector
        self.tabs = QTabWidget(self)

        # Tab 1: Sinopsis y Metadatos
        self.tab_synopsis = QWidget()
        self._init_tab_synopsis()
        self.tabs.addTab(self.tab_synopsis, "📝 Sinopsis")

        # Tab 2: Notas
        self.tab_notes = QWidget()
        self._init_tab_notes()
        self.tabs.addTab(self.tab_notes, "🗒️ Notas")

        # Tab 3: Marcadores
        self.tab_bookmarks = QWidget()
        self._init_tab_bookmarks()
        self.tabs.addTab(self.tab_bookmarks, "🔖 Marcadores")

        # Tab 4: Palabras Clave
        self.tab_keywords = QWidget()
        self._init_tab_keywords()
        self.tabs.addTab(self.tab_keywords, "🏷️ Keywords")

        # Tab 5: Instantáneas (Snapshots con Diff)
        self.tab_snapshots = QWidget()
        self._init_tab_snapshots()
        self.tabs.addTab(self.tab_snapshots, "📸 Snapshots")

        # Tab 6: Comentarios
        self.tab_comments = QWidget()
        self._init_tab_comments()
        self.tabs.addTab(self.tab_comments, "💬 Comentarios")

        layout.addWidget(self.tabs)

    def _init_tab_synopsis(self):
        layout = QVBoxLayout(self.tab_synopsis)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Tarjeta de Sinopsis
        layout.addWidget(QLabel("Sinopsis:"))
        self.txt_synopsis = QTextEdit()
        self.txt_synopsis.setPlaceholderText("Resumen de la escena o tarjeta...")
        self.txt_synopsis.setFixedHeight(120)
        self.txt_synopsis.textChanged.connect(self._on_synopsis_changed)
        layout.addWidget(self.txt_synopsis)

        layout.addWidget(QLabel("Metadatos Generales:"))

        # Tipo de Sección
        f_type = QHBoxLayout()
        f_type.addWidget(QLabel("Tipo:"))
        self.combo_section_type = QComboBox()
        self.combo_section_type.currentTextChanged.connect(self._on_section_type_changed)
        f_type.addWidget(self.combo_section_type)
        layout.addLayout(f_type)

        # Etiqueta
        f_label = QHBoxLayout()
        f_label.addWidget(QLabel("Etiqueta:"))
        self.combo_label = QComboBox()
        self.combo_label.currentTextChanged.connect(self._on_label_changed)
        f_label.addWidget(self.combo_label)
        layout.addLayout(f_label)

        # Estado
        f_status = QHBoxLayout()
        f_status.addWidget(QLabel("Estado:"))
        self.combo_status = QComboBox()
        self.combo_status.currentTextChanged.connect(self._on_status_changed)
        f_status.addWidget(self.combo_status)
        layout.addLayout(f_status)

        # Casilla Incluir en Compilación
        self.chk_compile = QCheckBox("Incluir en Compilación")
        self.chk_compile.toggled.connect(self._on_compile_toggled)
        layout.addWidget(self.chk_compile)

        layout.addStretch()

    def _init_tab_notes(self):
        layout = QVBoxLayout(self.tab_notes)
        layout.setContentsMargins(8, 8, 8, 8)

        layout.addWidget(QLabel("Notas de la escena:"))
        self.txt_notes = QTextEdit()
        self.txt_notes.setPlaceholderText("Anotaciones y recordatorios del documento...")
        self.txt_notes.textChanged.connect(self._on_notes_changed)
        layout.addWidget(self.txt_notes)

    def _init_tab_bookmarks(self):
        layout = QVBoxLayout(self.tab_bookmarks)
        layout.setContentsMargins(8, 8, 8, 8)

        layout.addWidget(QLabel("Marcadores y Vínculos de Investigación:"))
        self.list_bookmarks = QListWidget()
        layout.addWidget(self.list_bookmarks)

        btn_box = QHBoxLayout()
        btn_add = QPushButton("+ Añadir Enlace...")
        btn_add.clicked.connect(self._add_bookmark)
        btn_box.addWidget(btn_add)
        layout.addLayout(btn_box)

    def _init_tab_keywords(self):
        layout = QVBoxLayout(self.tab_keywords)
        layout.setContentsMargins(8, 8, 8, 8)

        layout.addWidget(QLabel("Palabras Clave Asignadas:"))
        self.list_keywords = QListWidget()
        layout.addWidget(self.list_keywords)

        btn_box = QHBoxLayout()
        btn_add = QPushButton("+ Añadir")
        btn_add.clicked.connect(self._add_keyword)
        btn_box.addWidget(btn_add)

        btn_del = QPushButton("- Quitar")
        btn_del.clicked.connect(self._remove_keyword)
        btn_box.addWidget(btn_del)
        layout.addLayout(btn_box)

    def _init_tab_snapshots(self):
        layout = QVBoxLayout(self.tab_snapshots)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        layout.addWidget(QLabel("Versiones Históricas:"))
        self.list_snapshots = QListWidget()
        self.list_snapshots.setFixedHeight(110)
        self.list_snapshots.itemSelectionChanged.connect(self._on_snapshot_selected)
        layout.addWidget(self.list_snapshots)

        btn_box = QHBoxLayout()
        btn_take = QPushButton("📸 Tomar Instantánea")
        btn_take.clicked.connect(self.take_snapshot)
        btn_box.addWidget(btn_take)

        btn_restore = QPushButton("↺ Restaurar")
        btn_restore.clicked.connect(self._restore_snapshot)
        btn_box.addWidget(btn_restore)
        layout.addLayout(btn_box)

        layout.addWidget(QLabel("Diferencias visuales (Diff):"))
        self.txt_diff = QTextEdit()
        self.txt_diff.setReadOnly(True)
        self.txt_diff.setPlaceholderText("Selecciona una instantánea para ver cambios...")
        layout.addWidget(self.txt_diff)

    def _init_tab_comments(self):
        layout = QVBoxLayout(self.tab_comments)
        layout.setContentsMargins(8, 8, 8, 8)

        layout.addWidget(QLabel("Comentarios en el margen:"))
        self.list_comments = QListWidget()
        layout.addWidget(self.list_comments)

        btn_box = QHBoxLayout()
        btn_add_comment = QPushButton("💬 + Comentario")
        btn_add_comment.clicked.connect(self._add_comment)
        btn_box.addWidget(btn_add_comment)
        layout.addLayout(btn_box)

    def load_node(self, node: BinderNode, project: EscritorioProjectV2):
        """Carga los datos del nodo seleccionado en el inspector."""
        self.current_node = node
        self.project = project
        self.lbl_header.setText(f"Inspector: {node.title[:18]}")

        # Sinopsis y notas
        self.txt_synopsis.blockSignals(True)
        self.txt_synopsis.setText(node._synopsis_text or "")
        self.txt_synopsis.blockSignals(False)

        self.txt_notes.blockSignals(True)
        self.txt_notes.setText(node._notes_rtf or "")
        self.txt_notes.blockSignals(False)

        # Metadatos
        self.combo_section_type.blockSignals(True)
        self.combo_section_type.clear()
        self.combo_section_type.addItems(project.section_types)
        self.combo_section_type.setCurrentText(node.section_type)
        self.combo_section_type.blockSignals(False)

        self.combo_label.blockSignals(True)
        self.combo_label.clear()
        for lbl in project.labels:
            self.combo_label.addItem(lbl["name"])
        self.combo_label.setCurrentText(node.label)
        self.combo_label.blockSignals(False)

        self.combo_status.blockSignals(True)
        self.combo_status.clear()
        for st in project.statuses:
            self.combo_status.addItem(st["name"])
        self.combo_status.setCurrentText(node.status)
        self.combo_status.blockSignals(False)

        self.chk_compile.blockSignals(True)
        self.chk_compile.setChecked(node.include_in_compile)
        self.chk_compile.blockSignals(False)

        # Keywords
        self._refresh_keywords()

        # Snapshots
        self._refresh_snapshots()

    def _on_synopsis_changed(self):
        if self.current_node:
            self.current_node._synopsis_text = self.txt_synopsis.toPlainText()
            self.current_node.mark_dirty()
            self.data_changed.emit()

    def _on_notes_changed(self):
        if self.current_node:
            self.current_node._notes_rtf = self.txt_notes.toPlainText()
            self.current_node.mark_dirty()

    def _on_section_type_changed(self, text):
        if self.current_node and text:
            self.current_node.section_type = text
            self.current_node.mark_dirty()
            self.data_changed.emit()

    def _on_label_changed(self, text):
        if self.current_node and text:
            self.current_node.label = text
            self.current_node.mark_dirty()
            self.data_changed.emit()

    def _on_status_changed(self, text):
        if self.current_node and text:
            self.current_node.status = text
            self.current_node.mark_dirty()
            self.data_changed.emit()

    def _on_compile_toggled(self, checked):
        if self.current_node:
            self.current_node.include_in_compile = checked
            self.current_node.mark_dirty()
            self.data_changed.emit()

    def _refresh_keywords(self):
        self.list_keywords.clear()
        if self.current_node:
            for kw in self.current_node.keywords:
                self.list_keywords.addItem(f"🏷️ {kw}")

    def _add_keyword(self):
        if not self.current_node:
            return
        kw, ok = QInputDialog.getText(self, "Palabra Clave", "Introduce la etiqueta o palabra clave:")
        if ok and kw.strip():
            if kw.strip() not in self.current_node.keywords:
                self.current_node.keywords.append(kw.strip())
                self.current_node.mark_dirty()
                self._refresh_keywords()

    def _remove_keyword(self):
        row = self.list_keywords.currentRow()
        if row >= 0 and self.current_node and row < len(self.current_node.keywords):
            self.current_node.keywords.pop(row)
            self.current_node.mark_dirty()
            self._refresh_keywords()

    def take_snapshot(self):
        if not self.current_node:
            return
        title, ok = QInputDialog.getText(self, "Tomar Instantánea", "Nombre o nota de la instantánea:", text=f"Versión {time.strftime('%H:%M:%S')}")
        if ok and title.strip():
            if self.current_node._snapshots is None:
                self.current_node._snapshots = []

            snap = SnapshotItem(
                title=title.strip(),
                content_rtf=self.current_node._content_rtf or "",
                word_count=self.current_node.word_count()
            )
            self.current_node._snapshots.insert(0, snap)
            self.current_node.mark_dirty()
            self._refresh_snapshots()

    def _refresh_snapshots(self):
        self.list_snapshots.clear()
        self.txt_diff.clear()
        if self.current_node and self.current_node._snapshots:
            for snap in self.current_node._snapshots:
                item = QListWidgetItem(f"📸 {snap.title} ({snap.date_str})")
                self.list_snapshots.addItem(item)

    def _on_snapshot_selected(self):
        row = self.list_snapshots.currentRow()
        if row >= 0 and self.current_node and self.current_node._snapshots and row < len(self.current_node._snapshots):
            snap = self.current_node._snapshots[row]
            current_text = self.current_node.get_plain_text().splitlines(keepends=True)
            snap_text = snap.content_rtf.splitlines(keepends=True)

            diff = difflib.unified_diff(snap_text, current_text, fromfile="Instantánea", tofile="Actual")
            diff_lines = list(diff)

            html_lines = []
            for line in diff_lines:
                if line.startswith("+"):
                    html_lines.append(f"<span style='color: #2ecc71; background-color: rgba(46, 204, 113, 0.2);'>{line}</span><br>")
                elif line.startswith("-"):
                    html_lines.append(f"<span style='color: #e74c3c; background-color: rgba(231, 76, 60, 0.2); text-decoration: line-through;'>{line}</span><br>")
                else:
                    html_lines.append(f"<span style='color: #a0a0b2;'>{line}</span><br>")

            self.txt_diff.setHtml("".join(html_lines) if html_lines else "<i>Sin diferencias con la versión actual.</i>")

    def _restore_snapshot(self):
        row = self.list_snapshots.currentRow()
        if row >= 0 and self.current_node and self.current_node._snapshots and row < len(self.current_node._snapshots):
            confirm = QMessageBox.question(self, "Restaurar", "¿Deseas restaurar esta versión anterior? Se creará una instantánea de seguridad antes de sustituir el texto.")
            if confirm == QMessageBox.StandardButton.Yes:
                # Tomar snapshot de seguridad
                safety_snap = SnapshotItem(title="Automática antes de restaurar", content_rtf=self.current_node._content_rtf or "")
                self.current_node._snapshots.insert(0, safety_snap)

                snap = self.current_node._snapshots[row + 1]
                self.current_node._content_rtf = snap.content_rtf
                self.current_node.mark_dirty()
                self._refresh_snapshots()
                self.data_changed.emit()

    def _add_bookmark(self):
        url, ok = QInputDialog.getText(self, "Añadir Marcador", "Introduce URL o enlace:")
        if ok and url.strip():
            self.list_bookmarks.addItem(f"🌐 {url.strip()}")

    def _add_comment(self):
        txt, ok = QInputDialog.getText(self, "Añadir Comentario", "Texto del comentario al margen:")
        if ok and txt.strip():
            self.list_comments.addItem(f"💬 {txt.strip()} ({time.strftime('%H:%M')})")
