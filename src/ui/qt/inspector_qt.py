"""
Inspector lateral derecho interactivo para PyQt6 con las 6 pestañas especializadas de Scrivener 3:
1. Sinopsis y Notas
2. Marcadores
3. Metadatos Personalizados
4. Instantáneas (Snapshots) con Myers Diff y Rollback
5. Comentarios y Notas al Pie
6. Sección y Compilación
"""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QTextEdit,
    QLineEdit, QComboBox, QPushButton, QListWidget, QListWidgetItem,
    QCheckBox, QMessageBox, QDialog, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal

from ...core.project import EscritorioProject, BinderItem
from ..InspectorWidget.myers_diff import MyersDiffEngine, DiffOp, DiffChunk


class DiffViewerDialog(QDialog):
    """Diálogo visual de diferencias diferenciales con algoritmo Myers Diff."""
    def __init__(self, original_text: str, modified_text: str, title: str = "Comparación Diferencial", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(700, 450)

        layout = QVBoxLayout(self)

        chunks = MyersDiffEngine.compute_diff(original_text, modified_text)
        additions = sum(1 for c in chunks if c.op == DiffOp.INSERT)
        deletions = sum(1 for c in chunks if c.op == DiffOp.DELETE)
        unchanged = sum(1 for c in chunks if c.op == DiffOp.EQUAL)

        # Barra de estadísticas
        lbl_stats = QLabel(f"Diferencias calculadas: +{additions} adiciones, -{deletions} eliminaciones, {unchanged} segmentos intactos.")
        lbl_stats.setStyleSheet("font-weight: bold; color: #a0a0b0; padding: 4px;")
        layout.addWidget(lbl_stats)

        # Visor de texto enriquecido coloreado
        viewer = QTextEdit()
        viewer.setReadOnly(True)

        html_lines = []
        for c in chunks:
            safe_text = c.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
            if c.op == DiffOp.INSERT:
                html_lines.append(f"<span style='background-color: rgba(46, 204, 113, 0.25); color: #2ecc71; font-weight: bold;'>+ {safe_text}</span>")
            elif c.op == DiffOp.DELETE:
                html_lines.append(f"<span style='background-color: rgba(231, 76, 60, 0.25); color: #e74c3c; text-decoration: line-through;'>- {safe_text}</span>")
            else:
                html_lines.append(f"<span style='color: #c0c0d0;'>  {safe_text}</span>")

        viewer.setHtml("<div style='font-family: Consolas, monospace; line-height: 1.4;'>" + "".join(html_lines) + "</div>")
        layout.addWidget(viewer)

        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)


class InspectorQt(QWidget):
    """Inspector con 6 pestañas especializadas."""
    itemModified = pyqtSignal(str)
    rollbackRequested = pyqtSignal(str, str)  # uuid, text_restored

    def __init__(self, project: Optional[EscritorioProject] = None, parent=None):
        super().__init__(parent)
        self.project = project
        self.current_item: Optional[BinderItem] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self._init_tab_notes_synopsis()
        self._init_tab_bookmarks()
        self._init_tab_metadata()
        self._init_tab_snapshots()
        self._init_tab_comments_footnotes()
        self._init_tab_section_compile()

    def set_item(self, item: Optional[BinderItem]):
        """Carga el elemento activo del Binder en todas las pestañas."""
        self.current_item = item
        if not item:
            self.setEnabled(False)
            return

        self.setEnabled(True)

        # 1. Sinopsis y Notas
        syn = item.get_synopsis() if hasattr(item, "get_synopsis") else getattr(item, "synopsis", "")
        self.synopsis_edit.blockSignals(True)
        self.synopsis_edit.setPlainText(syn or "")
        self.synopsis_edit.blockSignals(False)

        notes = item.get_notes_plain() if hasattr(item, "get_notes_plain") else getattr(item, "notes", "")
        self.notes_edit.blockSignals(True)
        self.notes_edit.setPlainText(notes or "")
        self.notes_edit.blockSignals(False)

        # 3. Metadatos
        st = getattr(item.data, "status", "Borrador") or "Borrador"
        idx = self.combo_status.findText(st)
        if idx >= 0:
            self.combo_status.setCurrentIndex(idx)

        lb = getattr(item.data, "label", "Sin Etiqueta") or "Sin Etiqueta"
        idx = self.combo_label.findText(lb)
        if idx >= 0:
            self.combo_label.setCurrentIndex(idx)

        # 4. Instantáneas
        self._refresh_snapshots()

        # 6. Ajustes de Sección
        stype = getattr(item.data, "section_type", "Scene") or "Scene"
        idx = self.combo_section_type.findText(stype)
        if idx >= 0:
            self.combo_section_type.setCurrentIndex(idx)

        inc = getattr(item.data, "include_in_compile", True)
        self.chk_include_compile.setChecked(inc)

    def _init_tab_notes_synopsis(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(6, 6, 6, 6)

        l.addWidget(QLabel("<b>Sinopsis de Tarjeta</b>"))
        self.synopsis_edit = QTextEdit()
        self.synopsis_edit.setPlaceholderText("Sinopsis para tarjetas de corcho...")
        self.synopsis_edit.textChanged.connect(self._on_synopsis_changed)
        l.addWidget(self.synopsis_edit, 1)

        l.addWidget(QLabel("<b>Notas del Documento</b>"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Notas privadas del autor...")
        self.notes_edit.textChanged.connect(self._on_notes_changed)
        l.addWidget(self.notes_edit, 1)

        self.tabs.addTab(w, "Sinopsis")

    def _init_tab_bookmarks(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(6, 6, 6, 6)

        l.addWidget(QLabel("<b>Marcadores del Documento</b>"))
        self.list_bookmarks = QListWidget()
        l.addWidget(self.list_bookmarks, 1)

        btn_box = QHBoxLayout()
        self.btn_add_bm = QPushButton("+ Añadir")
        self.btn_add_bm.clicked.connect(self._add_bookmark)
        self.btn_del_bm = QPushButton("- Eliminar")
        self.btn_del_bm.clicked.connect(self._del_bookmark)
        btn_box.addWidget(self.btn_add_bm)
        btn_box.addWidget(self.btn_del_bm)
        l.addLayout(btn_box)

        self.tabs.addTab(w, "Marcadores")

    def _init_tab_metadata(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(6, 6, 6, 6)

        l.addWidget(QLabel("<b>Estado:</b>"))
        self.combo_status = QComboBox()
        self.combo_status.addItems(["Borrador", "En Revisión", "Revisado", "Final", "Hecho"])
        self.combo_status.currentTextChanged.connect(self._on_status_changed)
        l.addWidget(self.combo_status)

        l.addWidget(QLabel("<b>Etiqueta / Línea Narrativa:</b>"))
        self.combo_label = QComboBox()
        self.combo_label.addItems(["Sin Etiqueta", "Trama Principal", "Subtrama Romántica", "Misterio", "Clímax"])
        self.combo_label.currentTextChanged.connect(self._on_label_changed)
        l.addWidget(self.combo_label)

        l.addWidget(QLabel("<b>Punto de Vista (POV):</b>"))
        self.edit_pov = QLineEdit()
        self.edit_pov.setPlaceholderText("Nombre del personaje con POV...")
        l.addWidget(self.edit_pov)

        l.addWidget(QLabel("<b>Ubicación / Escenario:</b>"))
        self.edit_location = QLineEdit()
        self.edit_location.setPlaceholderText("Localización de la escena...")
        l.addWidget(self.edit_location)

        l.addStretch()
        self.tabs.addTab(w, "Metadatos")

    def _init_tab_snapshots(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(6, 6, 6, 6)

        l.addWidget(QLabel("<b>Historial de Instantáneas</b>"))
        self.list_snapshots = QListWidget()
        l.addWidget(self.list_snapshots, 1)

        btn_take = QPushButton("📸 Tomar Instantánea")
        btn_take.clicked.connect(self._take_snapshot)
        l.addWidget(btn_take)

        btn_diff = QPushButton("🔍 Comparar Diferencias (Diff)")
        btn_diff.clicked.connect(self._compare_diff)
        l.addWidget(btn_diff)

        btn_rollback = QPushButton("⏮️ Restaurar Versión (Rollback)")
        btn_rollback.clicked.connect(self._rollback_snapshot)
        l.addWidget(btn_rollback)

        self.tabs.addTab(w, "Instantáneas")

    def _init_tab_comments_footnotes(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(6, 6, 6, 6)

        l.addWidget(QLabel("<b>Comentarios y Notas al Pie</b>"))
        self.list_comments = QListWidget()
        l.addWidget(self.list_comments, 1)

        btn_box = QHBoxLayout()
        btn_comm = QPushButton("+ Comentario")
        btn_comm.clicked.connect(self._add_comment)
        btn_fn = QPushButton("+ Nota al Pie")
        btn_fn.clicked.connect(self._add_footnote)
        btn_box.addWidget(btn_comm)
        btn_box.addWidget(btn_fn)
        l.addLayout(btn_box)

        self.tabs.addTab(w, "Comentarios")

    def _init_tab_section_compile(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(6, 6, 6, 6)

        l.addWidget(QLabel("<b>Tipo de Sección Editorial:</b>"))
        self.combo_section_type = QComboBox()
        self.combo_section_type.addItems(["Part", "Chapter", "Scene", "Front Matter", "Appendix", "Notes"])
        self.combo_section_type.currentTextChanged.connect(self._on_section_type_changed)
        l.addWidget(self.combo_section_type)

        self.chk_include_compile = QCheckBox("Incluir en Compilación")
        self.chk_include_compile.setChecked(True)
        self.chk_include_compile.toggled.connect(self._on_include_compile_toggled)
        l.addWidget(self.chk_include_compile)

        l.addStretch()
        self.tabs.addTab(w, "Sección")

    # Callbacks
    def _on_synopsis_changed(self):
        if self.current_item:
            text = self.synopsis_edit.toPlainText()
            if hasattr(self.current_item, "set_synopsis"):
                self.current_item.set_synopsis(text)
            self.itemModified.emit(self.current_item.uuid)

    def _on_notes_changed(self):
        if self.current_item:
            text = self.notes_edit.toPlainText()
            if hasattr(self.current_item, "set_notes_plain"):
                self.current_item.set_notes_plain(text)
            self.itemModified.emit(self.current_item.uuid)

    def _on_status_changed(self, val: str):
        if self.current_item and hasattr(self.current_item, "data"):
            self.current_item.data.status = val
            self.itemModified.emit(self.current_item.uuid)

    def _on_label_changed(self, val: str):
        if self.current_item and hasattr(self.current_item, "data"):
            self.current_item.data.label = val
            self.itemModified.emit(self.current_item.uuid)

    def _on_section_type_changed(self, val: str):
        if self.current_item and hasattr(self.current_item, "data"):
            self.current_item.data.section_type = val
            self.itemModified.emit(self.current_item.uuid)

    def _on_include_compile_toggled(self, val: bool):
        if self.current_item and hasattr(self.current_item, "data"):
            self.current_item.data.include_in_compile = val
            self.itemModified.emit(self.current_item.uuid)

    def _refresh_snapshots(self):
        self.list_snapshots.clear()
        if not self.current_item:
            return
        snaps = self.current_item.get_snapshots() if hasattr(self.current_item, "get_snapshots") else []
        for s in snaps:
            title = s.get("title", "Instantánea")
            ts = s.get("timestamp", "")
            item = QListWidgetItem(f"[{ts}] {title}")
            item.setData(Qt.ItemDataRole.UserRole, s)
            self.list_snapshots.addItem(item)

    def _take_snapshot(self):
        if not self.current_item:
            return
        title = f"Revisión {self.list_snapshots.count() + 1}"
        if hasattr(self.current_item, "create_snapshot"):
            self.current_item.create_snapshot(title)
        self._refresh_snapshots()

    def _compare_diff(self):
        sel = self.list_snapshots.currentItem()
        if not sel or not self.current_item:
            QMessageBox.information(self, "Comparar Diferencias", "Selecciona primero una instantánea del historial.")
            return

        snap_data = sel.data(Qt.ItemDataRole.UserRole)
        snap_content = snap_data.get("content", "")
        current_content = self.current_item.get_content_plain() if hasattr(self.current_item, "get_content_plain") else ""

        dlg = DiffViewerDialog(snap_content, current_content, f"Diff: {sel.text()}", self)
        dlg.exec()

    def _rollback_snapshot(self):
        sel = self.list_snapshots.currentItem()
        if not sel or not self.current_item:
            return

        snap_data = sel.data(Qt.ItemDataRole.UserRole)
        snap_content = snap_data.get("content", "")

        resp = QMessageBox.question(
            self, "Confirmar Restauración",
            f"¿Deseas restaurar la versión '{sel.text()}' en el documento activo? Se sobrescribirá el texto actual.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp == QMessageBox.StandardButton.Yes:
            if hasattr(self.current_item, "set_content_plain"):
                self.current_item.set_content_plain(snap_content)
            self.rollbackRequested.emit(self.current_item.uuid, snap_content)

    def _add_bookmark(self):
        self.list_bookmarks.addItem("https://es.wikipedia.org/wiki/Novela")

    def _del_bookmark(self):
        row = self.list_bookmarks.currentRow()
        if row >= 0:
            self.list_bookmarks.takeItem(row)

    def _add_comment(self):
        self.list_comments.addItem(f"💬 Comentario #{self.list_comments.count() + 1}: Revisar tono.")

    def _add_footnote(self):
        self.list_comments.addItem(f"📌 Nota al Pie #{self.list_comments.count() + 1}: Fuente histórica.")
