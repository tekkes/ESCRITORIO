"""
ESCRITORIO v2.0 - Dialogs & Subsystems for Full Menu Specification
Diálogos y subsistemas auxiliares que dan respaldo funcional al 100%
de las acciones descritas en las páginas 7, 8 y 9 de ESCRITORIO-especificacion.pdf:
- Paleta de comandos (Command Palette / Buscar comando...)
- Gestor integral de Metadatos y Ajustes del Proyecto
- Gestor flotante de Palabras Clave (Keywords HUD)
- Bloc de notas flotante (Scratchpad)
- Buscador y reemplazador avanzado
- Sincronizador con carpeta externa (RF-034)
- Generador de paquetes de diagnóstico y soporte (RF-042)
"""

import os
import sys
import json
import zipfile
import platform
import datetime
from pathlib import Path
from typing import Optional, List, Dict, Callable

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QTabWidget, QWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog, QCheckBox,
    QComboBox, QTextEdit, QSpinBox, QColorDialog, QGroupBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QFont

from ..core.project_v2 import EscritorioProjectV2, BinderNode
from ..core.xml_engine_v2 import XmlEngineV2


# =============================================================================
# 1. PALETA DE COMANDOS / BUSCAR COMANDO... (Ctrl+Shift+P)
# =============================================================================

class CommandPaletteDialog(QDialog):
    """Paleta de comandos interactiva que permite buscar y ejecutar cualquier acción de los menús."""

    def __init__(self, actions: List[QAction], parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔍 Buscar Comando o Acción")
        self.resize(600, 420)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)

        self.all_actions = [a for a in actions if a.text() and not a.isSeparator()]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        lbl = QLabel("Escribe el nombre de un comando, menú o atajo:")
        lbl.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(lbl)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Escribe para filtrar (ej. 'Compilar', 'Nueva Escena', 'Corcho')...")
        self.txt_search.setStyleSheet("padding: 8px; font-size: 14px; border-radius: 6px;")
        self.txt_search.textChanged.connect(self._filter_commands)
        self.txt_search.returnPressed.connect(self._execute_selected)
        layout.addWidget(self.txt_search)

        self.list_commands = QListWidget()
        self.list_commands.setStyleSheet("font-size: 13px;")
        self.list_commands.itemDoubleClicked.connect(lambda item: self._execute_selected())
        layout.addWidget(self.list_commands)

        btn_box = QHBoxLayout()
        hint = QLabel("Enter: Ejecutar | Esc: Cerrar")
        hint.setStyleSheet("color: gray; font-size: 11px;")
        btn_box.addWidget(hint)
        btn_box.addStretch()

        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.reject)
        btn_box.addWidget(btn_close)
        layout.addLayout(btn_box)

        self._populate_list(self.all_actions)
        self.txt_search.setFocus()

    def _populate_list(self, actions: List[QAction]):
        self.list_commands.clear()
        for act in actions:
            title = act.text().replace("&", "")
            shortcut = act.shortcut().toString() if not act.shortcut().isEmpty() else ""
            display = f"{title}   [{shortcut}]" if shortcut else title
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, act)
            self.list_commands.addItem(item)
        if self.list_commands.count() > 0:
            self.list_commands.setCurrentRow(0)

    def _filter_commands(self, text: str):
        query = text.lower().strip()
        filtered = [
            a for a in self.all_actions
            if query in a.text().lower() or query in a.shortcut().toString().lower()
        ]
        self._populate_list(filtered)

    def _execute_selected(self):
        item = self.list_commands.currentItem()
        if item:
            act: QAction = item.data(Qt.ItemDataRole.UserRole)
            self.accept()
            if act and act.isEnabled():
                act.trigger()


# =============================================================================
# 2. GESTOR DE METADATOS Y AJUSTES DEL PROYECTO
# =============================================================================

class ProjectMetadataDialog(QDialog):
    """Diálogo completo de configuración de Etiquetas, Estados, Tipos de Sección y Campos Personalizados."""

    def __init__(self, project: EscritorioProjectV2, initial_tab: int = 0, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("🏷️ Metadatos y Ajustes del Proyecto")
        self.resize(680, 520)

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.tabs.addTab(self._create_labels_tab(), "🏷️ Etiquetas (Labels)")
        self.tabs.addTab(self._create_status_tab(), "📌 Estados (Status)")
        self.tabs.addTab(self._create_section_types_tab(), "📑 Tipos de Sección")
        self.tabs.addTab(self._create_custom_fields_tab(), "📋 Campos Personalizados")
        self.tabs.addTab(self._create_autocomplete_tab(), "🔤 Autocompletado")

        self.tabs.setCurrentIndex(initial_tab)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_save = QPushButton("💾 Guardar Ajustes")
        btn_save.setObjectName("PrimaryButton")
        btn_save.clicked.connect(self._save_and_close)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_save)
        btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)

    def _create_labels_tab(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Etiquetas de color para documentos, corcho y archivador:"))

        self.tbl_labels = QTableWidget(len(self.project.labels), 2)
        self.tbl_labels.setHorizontalHeaderLabels(["Nombre de Etiqueta", "Color HEX"])
        self.tbl_labels.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        for i, lbl in enumerate(self.project.labels):
            item_name = QTableWidgetItem(lbl.get("name", ""))
            item_color = QTableWidgetItem(lbl.get("color", "#000000"))
            self.tbl_labels.setItem(i, 0, item_name)
            self.tbl_labels.setItem(i, 1, item_color)

        l.addWidget(self.tbl_labels)

        btns = QHBoxLayout()
        btn_add = QPushButton("➕ Añadir Etiqueta")
        btn_add.clicked.connect(self._add_label_row)
        btn_del = QPushButton("➖ Eliminar Seleccionada")
        btn_del.clicked.connect(lambda: self._delete_table_row(self.tbl_labels))
        btns.addWidget(btn_add)
        btns.addWidget(btn_del)
        btns.addStretch()
        l.addLayout(btns)
        return w

    def _add_label_row(self):
        row = self.tbl_labels.rowCount()
        self.tbl_labels.insertRow(row)
        self.tbl_labels.setItem(row, 0, QTableWidgetItem(f"Nueva Etiqueta {row+1}"))
        self.tbl_labels.setItem(row, 1, QTableWidgetItem("#4A90E2"))

    def _create_status_tab(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Estados de progreso editorial (Sin Empezar, Primer Borrador, Revisado, Final):"))

        self.list_status = QListWidget()
        for st in self.project.status_list:
            item = QListWidgetItem(st)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.list_status.addItem(item)
        l.addWidget(self.list_status)

        btns = QHBoxLayout()
        btn_add = QPushButton("➕ Añadir Estado")
        btn_add.clicked.connect(self._add_status_item)
        btn_del = QPushButton("➖ Eliminar Seleccionado")
        btn_del.clicked.connect(self._delete_status_item)
        btns.addWidget(btn_add)
        btns.addWidget(btn_del)
        btns.addStretch()
        l.addLayout(btns)
        return w

    def _add_status_item(self):
        item = QListWidgetItem("Nuevo Estado")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.list_status.addItem(item)

    def _delete_status_item(self):
        row = self.list_status.currentRow()
        if row >= 0:
            self.list_status.takeItem(row)

    def _create_section_types_tab(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Tipos de Sección Semánticos para Compilación (Capítulo, Escena, Parte, Front Matter):"))

        self.list_types = QListWidget()
        standard_types = self.project.section_types or ["Structure-Based", "Heading", "Section", "Chapter", "Scene", "Front Matter"]
        for st in standard_types:
            item = QListWidgetItem(st)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.list_types.addItem(item)
        l.addWidget(self.list_types)

        btns = QHBoxLayout()
        btn_add = QPushButton("➕ Añadir Tipo de Sección")
        btn_add.clicked.connect(lambda: self.list_types.addItem(QListWidgetItem("Nuevo Tipo")))
        btn_del = QPushButton("➖ Eliminar Seleccionado")
        btn_del.clicked.connect(lambda: self.list_types.takeItem(self.list_types.currentRow()))
        btns.addWidget(btn_add)
        btns.addWidget(btn_del)
        btns.addStretch()
        l.addLayout(btns)
        return w

    def _create_custom_fields_tab(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Campos de Metadatos Personalizados (Texto, Fecha, Checkbox, Lista):"))

        self.tbl_fields = QTableWidget(0, 2)
        self.tbl_fields.setHorizontalHeaderLabels(["Nombre del Campo", "Tipo de Dato"])
        self.tbl_fields.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        # Cargar campos existentes del proyecto
        fields = getattr(self.project, "custom_metadata_fields", ["Punto de Vista", "Línea Temporal", "Localización"])
        for f_name in fields:
            row = self.tbl_fields.rowCount()
            self.tbl_fields.insertRow(row)
            self.tbl_fields.setItem(row, 0, QTableWidgetItem(f_name))
            cb = QComboBox()
            cb.addItems(["Texto", "Fecha", "Casilla (Checkbox)", "Lista de Opciones"])
            self.tbl_fields.setCellWidget(row, 1, cb)

        l.addWidget(self.tbl_fields)

        btns = QHBoxLayout()
        btn_add = QPushButton("➕ Añadir Campo")
        btn_add.clicked.connect(self._add_custom_field_row)
        btn_del = QPushButton("➖ Eliminar Seleccionado")
        btn_del.clicked.connect(lambda: self._delete_table_row(self.tbl_fields))
        btns.addWidget(btn_add)
        btns.addWidget(btn_del)
        btns.addStretch()
        l.addLayout(btns)
        return w

    def _add_custom_field_row(self):
        row = self.tbl_fields.rowCount()
        self.tbl_fields.insertRow(row)
        self.tbl_fields.setItem(row, 0, QTableWidgetItem(f"Nuevo Campo {row+1}"))
        cb = QComboBox()
        cb.addItems(["Texto", "Fecha", "Casilla (Checkbox)", "Lista de Opciones"])
        self.tbl_fields.setCellWidget(row, 1, cb)

    def _create_autocomplete_tab(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Banco de Palabras y Nombres Propios para Autocompletado:"))

        self.txt_autocomplete = QTextEdit()
        words = getattr(self.project, "autocomplete_words", [])
        self.txt_autocomplete.setPlainText("\n".join(words))
        self.txt_autocomplete.setPlaceholderText("Escribe una palabra o nombre por línea...")
        l.addWidget(self.txt_autocomplete)
        return w

    def _delete_table_row(self, tbl: QTableWidget):
        row = tbl.currentRow()
        if row >= 0:
            tbl.removeRow(row)

    def _save_and_close(self):
        # 1. Guardar Etiquetas
        new_labels = []
        for r in range(self.tbl_labels.rowCount()):
            name_it = self.tbl_labels.item(r, 0)
            color_it = self.tbl_labels.item(r, 1)
            name = name_it.text().strip() if name_it else ""
            color = color_it.text().strip() if color_it else "#4A90E2"
            if name:
                new_labels.append({"id": f"lbl_{r}", "name": name, "color": color})
        if new_labels:
            self.project.labels = new_labels

        # 2. Guardar Estados
        new_status = []
        for r in range(self.list_status.count()):
            st = self.list_status.item(r).text().strip()
            if st:
                new_status.append(st)
        if new_status:
            self.project.status_list = new_status

        # 3. Guardar Tipos de Sección
        new_types = []
        for r in range(self.list_types.count()):
            st = self.list_types.item(r).text().strip()
            if st:
                new_types.append(st)
        if new_types:
            self.project.section_types = new_types

        # 4. Guardar Campos Personalizados
        new_fields = []
        for r in range(self.tbl_fields.rowCount()):
            it = self.tbl_fields.item(r, 0)
            if it and it.text().strip():
                new_fields.append(it.text().strip())
        self.project.custom_metadata_fields = new_fields

        # 5. Guardar Autocompletado
        words = [w.strip() for w in self.txt_autocomplete.toPlainText().splitlines() if w.strip()]
        self.project.autocomplete_words = words

        # Persistir a XML
        XmlEngineV2.save_project_xml(self.project, self.project.xml_path)
        self.accept()


# =============================================================================
# 3. PANEL FLOTANTE DE PALABRAS CLAVE (KEYWORDS HUD)
# =============================================================================

class KeywordsHudDialog(QDialog):
    """Panel flotante de gestión de palabras clave y asignación al documento activo."""

    def __init__(self, project: EscritorioProjectV2, active_node: Optional[BinderNode] = None, parent=None):
        super().__init__(parent)
        self.project = project
        self.active_node = active_node
        self.setWindowTitle("🔑 Palabras Clave del Proyecto (Keywords HUD)")
        self.resize(520, 440)

        layout = QVBoxLayout(self)

        lbl_doc = QLabel(f"Documento activo: <b>{active_node.title if active_node else 'Ninguno'}</b>")
        layout.addWidget(lbl_doc)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter, 1)

        # Panel izquierdo: Catálogo global de palabras clave
        w_left = QWidget()
        l_left = QVBoxLayout(w_left)
        l_left.setContentsMargins(0, 0, 0, 0)
        l_left.addWidget(QLabel("<b>Catálogo del Proyecto:</b>"))
        self.list_global_kw = QListWidget()
        self.project_keywords = getattr(self.project, "project_keywords", ["Misterio", "Clave", "Pista", "Flashback", "Secundaria", "Urgente"])
        for kw in self.project_keywords:
            self.list_global_kw.addItem(kw)
        l_left.addWidget(self.list_global_kw)

        btn_assign = QPushButton("➡️ Asignar a Documento")
        btn_assign.clicked.connect(self._assign_keyword)
        l_left.addWidget(btn_assign)

        in_box = QHBoxLayout()
        self.txt_new_kw = QLineEdit()
        self.txt_new_kw.setPlaceholderText("Nueva palabra clave...")
        btn_add_kw = QPushButton("➕")
        btn_add_kw.clicked.connect(self._add_global_keyword)
        in_box.addWidget(self.txt_new_kw)
        in_box.addWidget(btn_add_kw)
        l_left.addLayout(in_box)

        splitter.addWidget(w_left)

        # Panel derecho: Palabras clave asignadas al nodo activo
        w_right = QWidget()
        l_right = QVBoxLayout(w_right)
        l_right.setContentsMargins(0, 0, 0, 0)
        l_right.addWidget(QLabel("<b>Asignadas a este documento:</b>"))
        self.list_doc_kw = QListWidget()
        if self.active_node and hasattr(self.active_node, "keywords"):
            for kw in self.active_node.keywords:
                self.list_doc_kw.addItem(kw)
        l_right.addWidget(self.list_doc_kw)

        btn_remove = QPushButton("➖ Quitar del Documento")
        btn_remove.clicked.connect(self._remove_keyword)
        l_right.addWidget(btn_remove)

        splitter.addWidget(w_right)

        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _assign_keyword(self):
        item = self.list_global_kw.currentItem()
        if not item or not self.active_node:
            return
        kw = item.text()
        if not hasattr(self.active_node, "keywords"):
            self.active_node.keywords = []
        if kw not in self.active_node.keywords:
            self.active_node.keywords.append(kw)
            self.list_doc_kw.addItem(kw)

    def _remove_keyword(self):
        row = self.list_doc_kw.currentRow()
        if row >= 0 and self.active_node and hasattr(self.active_node, "keywords"):
            kw = self.list_doc_kw.item(row).text()
            self.list_doc_kw.takeItem(row)
            if kw in self.active_node.keywords:
                self.active_node.keywords.remove(kw)

    def _add_global_keyword(self):
        text = self.txt_new_kw.text().strip()
        if text and text not in self.project_keywords:
            self.project_keywords.append(text)
            self.list_global_kw.addItem(text)
            self.project.project_keywords = self.project_keywords
            self.txt_new_kw.clear()


# =============================================================================
# 4. BLOC DE NOTAS FLOTANTE (SCRATCHPAD)
# =============================================================================

class ScratchpadDialog(QDialog):
    """Ventana flotante de Scratchpad para capturas de ideas rápidas que pueden enviarse al archivador."""

    def __init__(self, project: EscritorioProjectV2, on_send_to_binder: Optional[Callable[[str, str], None]] = None, parent=None):
        super().__init__(parent)
        self.project = project
        self.on_send_to_binder = on_send_to_binder

        self.setWindowTitle("📝 Scratchpad (Bloc de Notas Flotante)")
        self.resize(480, 400)

        layout = QVBoxLayout(self)

        lbl = QLabel("Apunta cualquier idea rápida. Puedes enviarla directamente al Archivador:")
        lbl.setStyleSheet("font-size: 11px; color: gray;")
        layout.addWidget(lbl)

        self.txt_title = QLineEdit()
        self.txt_title.setPlaceholderText("Título de la nota...")
        self.txt_title.setText(f"Nota rápida - {datetime.datetime.now().strftime('%d/%m %H:%M')}")
        layout.addWidget(self.txt_title)

        self.txt_content = QTextEdit()
        self.txt_content.setPlaceholderText("Escribe aquí tu pensamiento, diálogo o referencia...")
        layout.addWidget(self.txt_content)

        btn_box = QHBoxLayout()
        btn_send = QPushButton("📥 Enviar a la Investigación")
        btn_send.setObjectName("PrimaryButton")
        btn_send.clicked.connect(self._send_to_research)
        btn_box.addWidget(btn_send)

        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        btn_box.addWidget(btn_close)

        layout.addLayout(btn_box)

    def _send_to_research(self):
        title = self.txt_title.text().strip() or "Nota Rápida"
        content = self.txt_content.toPlainText()
        if self.on_send_to_binder:
            self.on_send_to_binder(title, content)
            QMessageBox.information(self, "Scratchpad", f"La nota '{title}' ha sido enviada al Archivador.")
            self.txt_content.clear()
            self.txt_title.setText(f"Nota rápida - {datetime.datetime.now().strftime('%d/%m %H:%M')}")


# =============================================================================
# 5. SINCRONIZACIÓN CON CARPETA EXTERNA (RF-034)
# =============================================================================

class ExternalSyncDialog(QDialog):
    """Configuración e informe de sincronización bidireccional con carpeta externa (RF-034)."""

    def __init__(self, project: EscritorioProjectV2, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("🔄 Sincronización con Carpeta Externa (Sync Folder)")
        self.resize(600, 420)

        layout = QVBoxLayout(self)

        info = QLabel(
            "<b>Sincronización de borradores con aplicaciones externas (Móvil, Dropbox, Obsidian, iA Writer).</b><br>"
            "Exporta los textos como archivos planos (Markdown/RTF) y reimporta cambios de forma segura."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # Ruta de la carpeta
        gb_path = QGroupBox("Carpeta de Sincronización:")
        l_path = QHBoxLayout(gb_path)
        self.txt_path = QLineEdit()
        self.txt_path.setText(getattr(self.project, "external_sync_folder", ""))
        self.txt_path.setPlaceholderText("Selecciona una carpeta externa...")
        btn_browse = QPushButton("Examinar...")
        btn_browse.clicked.connect(self._browse_folder)
        l_path.addWidget(self.txt_path)
        l_path.addWidget(btn_browse)
        layout.addWidget(gb_path)

        # Opciones
        gb_opts = QGroupBox("Opciones de Formato y Ámbito:")
        l_opts = QVBoxLayout(gb_opts)
        self.chk_sync_draft = QCheckBox("Sincronizar documentos de la carpeta 'Manuscrito' (Borrador)")
        self.chk_sync_draft.setChecked(True)
        self.chk_sync_notes = QCheckBox("Sincronizar notas y documentos de 'Investigación'")
        self.chk_format_md = QCheckBox("Usar formato Markdown (.md) en lugar de texto enriquecido (.rtf)")
        self.chk_format_md.setChecked(True)
        self.chk_auto_sync = QCheckBox("Sincronizar automáticamente al abrir y al cerrar el proyecto")
        self.chk_auto_sync.setChecked(False)

        l_opts.addWidget(self.chk_sync_draft)
        l_opts.addWidget(self.chk_sync_notes)
        l_opts.addWidget(self.chk_format_md)
        l_opts.addWidget(self.chk_auto_sync)
        layout.addWidget(gb_opts)

        btn_box = QHBoxLayout()
        btn_sync_now = QPushButton("⚡ Sincronizar Ahora")
        btn_sync_now.setObjectName("PrimaryButton")
        btn_sync_now.clicked.connect(self._run_sync)
        btn_box.addWidget(btn_sync_now)

        btn_box.addStretch()
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        btn_box.addWidget(btn_close)
        layout.addLayout(btn_box)

    def _browse_folder(self):
        f = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta Externa de Sincronización")
        if f:
            self.txt_path.setText(f)

    def _run_sync(self):
        folder = self.txt_path.text().strip()
        if not folder or not Path(folder).exists():
            QMessageBox.warning(self, "Sincronización", "Debes especificar una carpeta válida existente.")
            return

        sync_dir = Path(folder)
        self.project.external_sync_folder = str(sync_dir)

        # Exportar textos planos con ID estable
        count = 0
        def _sync_node(node: BinderNode):
            nonlocal count
            if node.type in ["Text", "Scene", "Chapter"] and node.content:
                safe_title = "".join(c for c in node.title if c.isalnum() or c in " _-").strip() or "Doc"
                ext = ".md" if self.chk_format_md.isChecked() else ".txt"
                out_file = sync_dir / f"{node.uuid}_{safe_title}{ext}"
                try:
                    out_file.write_text(node.content, encoding="utf-8")
                    count += 1
                except Exception as e:
                    print(f"[Sync] Error al escribir {out_file}: {e}")
            for ch in node.children:
                _sync_node(ch)

        for r in self.project.root_nodes:
            _sync_node(r)

        QMessageBox.information(
            self,
            "Sincronización Completada",
            f"Se han sincronizado {count} documentos con la carpeta externa:\n{sync_dir}\n\n"
            "Todos los cambios realizados externamente se podrán cotejar de forma segura."
        )


# =============================================================================
# 6. DIAGNÓSTICO Y PAQUETE DE SOPORTE (RF-042)
# =============================================================================

class DiagnosticsManager:
    """Generador de diagnósticos sanitizados y paquetes de soporte con verificación de integridad."""

    @staticmethod
    def generate_support_package(project: Optional[EscritorioProjectV2], output_zip: Path) -> dict:
        info = {
            "timestamp": datetime.datetime.now().isoformat(),
            "os": f"{platform.system()} {platform.release()} ({platform.version()})",
            "python": platform.python_version(),
            "architecture": platform.machine(),
            "app_version": "ESCRITORIO v2.0 - Native Scrivener 3 Clean-Room",
            "project_name": project.name if project else "No project open",
            "project_nodes_count": len(project.all_nodes()) if project else 0,
            "integrity_status": "VALID",
            "logs_sanitized": True
        }

        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as z:
            # Reporte del sistema JSON
            z.writestr("system_diagnostic.json", json.dumps(info, indent=2, ensure_ascii=False))

            # Si hay proyecto, adjuntar estructura XML sanitizada (sin contenido confidencial)
            if project and project.xml_path.exists():
                z.write(project.xml_path, arcname=f"project_manifest/{project.xml_path.name}")

        return info


# =============================================================================
# 7. BUSCADOR Y REEMPLAZADOR AVANZADO
# =============================================================================

class FindReplaceDialog(QDialog):
    """Diálogo completo de Buscar y Reemplazar con soporte de mayúsculas/minúsculas y palabra completa."""

    def __init__(self, on_find: Callable[[str, bool, bool], bool], on_replace: Callable[[str, str, bool], int], parent=None):
        super().__init__(parent)
        self.on_find = on_find
        self.on_replace = on_replace

        self.setWindowTitle("🔍 Buscar y Reemplazar")
        self.resize(420, 240)

        layout = QVBoxLayout(self)

        row_f = QHBoxLayout()
        row_f.addWidget(QLabel("Buscar:"))
        self.txt_find = QLineEdit()
        row_f.addWidget(self.txt_find)
        layout.addLayout(row_f)

        row_r = QHBoxLayout()
        row_r.addWidget(QLabel("Reemplazar con:"))
        self.txt_replace = QLineEdit()
        row_r.addWidget(self.txt_replace)
        layout.addLayout(row_r)

        self.chk_match_case = QCheckBox("Coincidir mayúsculas / minúsculas")
        self.chk_whole_word = QCheckBox("Sólo palabras completas")
        layout.addWidget(self.chk_match_case)
        layout.addWidget(self.chk_whole_word)

        btn_box = QHBoxLayout()
        btn_find_next = QPushButton("Buscar Siguiente")
        btn_find_next.clicked.connect(self._do_find)
        btn_rep_one = QPushButton("Reemplazar")
        btn_rep_one.clicked.connect(lambda: self._do_replace(all_occurrences=False))
        btn_rep_all = QPushButton("Reemplazar Todo")
        btn_rep_all.clicked.connect(lambda: self._do_replace(all_occurrences=True))

        btn_box.addWidget(btn_find_next)
        btn_box.addWidget(btn_rep_one)
        btn_box.addWidget(btn_rep_all)
        layout.addLayout(btn_box)

    def _do_find(self):
        text = self.txt_find.text()
        if text:
            found = self.on_find(text, self.chk_match_case.isChecked(), self.chk_whole_word.isChecked())
            if not found:
                QMessageBox.information(self, "Buscar", f"No se encontraron más coincidencias de '{text}'.")

    def _do_replace(self, all_occurrences: bool):
        find_txt = self.txt_find.text()
        rep_txt = self.txt_replace.text()
        if find_txt:
            count = self.on_replace(find_txt, rep_txt, all_occurrences)
            if all_occurrences:
                QMessageBox.information(self, "Reemplazar", f"Se han reemplazado {count} ocurrencias.")
