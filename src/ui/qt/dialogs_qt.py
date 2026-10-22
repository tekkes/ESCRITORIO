"""
Diálogos complementarios de Escritorio en PyQt6:
- Galería de Plantillas y Nuevo Proyecto
- Objetivos de Proyecto y Sesión (Project Targets)
- Importar y Dividir Automáticamente (Import and Split)
"""

from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QLineEdit, QPushButton, QFileDialog, QProgressBar, QSpinBox, QGroupBox,
    QMessageBox
)
from PyQt6.QtCore import Qt

from ...core.project import EscritorioProject
from ...core.importers.project_templates import ProjectTemplateManager
from ...core.importers.import_and_split import ImportAndSplit


class NewProjectDialogQt(QDialog):
    """Galería de plantillas para instanciar nuevos proyectos editoriales."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Proyecto - Galería de Plantillas")
        self.resize(750, 480)
        self.created_project_path: Optional[str] = None

        layout = QVBoxLayout(self)

        content_layout = QHBoxLayout()

        # Lista de plantillas
        self.list_templates = QListWidget()
        self.list_templates.setFixedWidth(260)

        templates_info = [
            ("novel_parts", "Novela con Partes", "Ficción", "Estructura épica organizada en libros/partes, capítulos y escenas."),
            ("novel", "Novela de Ficción", "Ficción", "Estructura estándar de novela con fichas de personajes y lugares."),
            ("short_story", "Relato Corto", "Ficción", "Plantilla ligera para cuentos, antologías y microrrelatos."),
            ("general_essay", "Ensayo General", "No Ficción", "Estructura para libros divulgativos, monografías y no ficción."),
            ("apa_paper", "Artículo Científico APA", "No Ficción", "Manuscrito con Abstract, Método, Resultados y Discusión."),
            ("screenplay_feature", "Guion Cinematográfico", "Guion", "Formato estándar para largometrajes en 3 actos."),
            ("blank", "Proyecto en Blanco", "General", "Estructura mínima limpia (Borrador, Investigación, Papelera).")
        ]

        for tid, name, cat, desc in templates_info:
            item = QListWidgetItem(f"[{cat}] {name}")
            item.setData(Qt.ItemDataRole.UserRole, tid)
            item.setData(Qt.ItemDataRole.UserRole + 1, desc)
            self.list_templates.addItem(item)

        self.list_templates.setCurrentRow(0)
        content_layout.addWidget(self.list_templates)

        # Panel de descripción y configuración
        right_panel = QVBoxLayout()
        self.lbl_title = QLabel("<b>Novela con Partes</b>")
        self.lbl_title.setStyleSheet("font-size: 12pt;")
        right_panel.addWidget(self.lbl_title)

        self.lbl_desc = QLabel("Descripción...")
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color: #a0a0b0; margin-bottom: 16px;")
        right_panel.addWidget(self.lbl_desc)

        right_panel.addWidget(QLabel("Nombre del Proyecto:"))
        self.edit_name = QLineEdit("Mi Nueva Novela")
        right_panel.addWidget(self.edit_name)

        right_panel.addWidget(QLabel("Carpeta de Destino:"))
        dest_h = QHBoxLayout()
        default_dir = str(Path.home() / "Documents")
        self.edit_dir = QLineEdit(default_dir)
        dest_h.addWidget(self.edit_dir, 1)

        btn_browse = QPushButton("Examinar...")
        btn_browse.clicked.connect(self._browse_dir)
        dest_h.addWidget(btn_browse)
        right_panel.addLayout(dest_h)

        right_panel.addStretch()
        content_layout.addLayout(right_panel, 1)

        layout.addLayout(content_layout)

        # Barra inferior
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_create = QPushButton("Crear Proyecto")
        self.btn_create.setStyleSheet("background-color: #7c5cbf; color: white; font-weight: bold; padding: 6px 18px;")
        self.btn_create.clicked.connect(self._create_project)
        btn_layout.addWidget(self.btn_create)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

        self.list_templates.currentRowChanged.connect(self._on_template_changed)
        self._on_template_changed(0)

    def _on_template_changed(self, row: int):
        item = self.list_templates.item(row)
        if not item:
            return
        self.lbl_title.setText(f"<b>{item.text()}</b>")
        self.lbl_desc.setText(item.data(Qt.ItemDataRole.UserRole + 1))

    def _browse_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta", self.edit_dir.text())
        if folder:
            self.edit_dir.setText(folder)

    def _create_project(self):
        name = self.edit_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Atención", "Introduce un nombre para el proyecto.")
            return

        sel_item = self.list_templates.currentItem()
        tid = sel_item.data(Qt.ItemDataRole.UserRole) if sel_item else "novel_parts"

        dest_parent = Path(self.edit_dir.text())
        dest_parent.mkdir(parents=True, exist_ok=True)
        try:
            proj = ProjectTemplateManager.create_project_from_template(
                template_id=tid,
                destination_path=dest_parent,
                project_name=name,
                native=True
            )
            proj.save_all()
            proj_path = str(proj.project_dir)
            proj.close()
            self.created_project_path = proj_path
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error al Crear", f"No se pudo crear el proyecto:\n{str(e)}")


class ProjectTargetsDialogQt(QDialog):
    """Ventana flotante de Objetivos de Proyecto y Sesión."""

    def __init__(self, current_words: int = 0, target_words: int = 80000, session_words: int = 0, session_target: int = 1500, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Objetivos de Escritura - Project Targets")
        self.resize(460, 260)

        layout = QVBoxLayout(self)

        # Objetivo del Manuscrito
        grp_draft = QGroupBox("Objetivo del Manuscrito Completo")
        l1 = QVBoxLayout(grp_draft)

        self.lbl_draft_metrics = QLabel(f"{current_words:,} de {target_words:,} palabras")
        self.lbl_draft_metrics.setStyleSheet("font-weight: bold;")
        l1.addWidget(self.lbl_draft_metrics)

        self.pbar_draft = QProgressBar()
        pct_draft = min(100, int(current_words / max(1, target_words) * 100))
        self.pbar_draft.setValue(pct_draft)
        self.pbar_draft.setFormat(f"{pct_draft}%")
        l1.addWidget(self.pbar_draft)

        layout.addWidget(grp_draft)

        # Objetivo de la Sesión Actual
        grp_session = QGroupBox("Objetivo de la Sesión de Hoy")
        l2 = QVBoxLayout(grp_session)

        self.lbl_session_metrics = QLabel(f"{session_words:,} de {session_target:,} palabras redactadas hoy")
        self.lbl_session_metrics.setStyleSheet("font-weight: bold;")
        l2.addWidget(self.lbl_session_metrics)

        self.pbar_session = QProgressBar()
        pct_session = min(100, int(session_words / max(1, session_target) * 100))
        self.pbar_session.setValue(pct_session)
        self.pbar_session.setFormat(f"{pct_session}%")
        l2.addWidget(self.pbar_session)

        layout.addWidget(grp_session)

        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)


class ImportAndSplitDialogQt(QDialog):
    """Diálogo para importar un manuscrito externo y dividirlo en escenas automáticamente."""

    def __init__(self, project: EscritorioProject, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Importar y Dividir en Escenas (Import and Split)")
        self.resize(550, 240)
        self.imported_count = 0

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Selecciona un documento de texto (.txt, .docx, .md) para dividir automáticamente:"))

        file_h = QHBoxLayout()
        self.edit_file = QLineEdit()
        file_h.addWidget(self.edit_file, 1)

        btn_browse = QPushButton("Examinar...")
        btn_browse.clicked.connect(self._browse)
        file_h.addWidget(btn_browse)
        layout.addLayout(file_h)

        layout.addWidget(QLabel("Separador de escenas:"))
        self.combo_sep = QLineEdit("#")
        self.combo_sep.setPlaceholderText("Ejemplo: # o Capítulo o ***")
        layout.addWidget(self.combo_sep)

        layout.addStretch()

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_ok = QPushButton("Importar y Dividir")
        btn_ok.setStyleSheet("background-color: #7c5cbf; color: white; font-weight: bold; padding: 6px 14px;")
        btn_ok.clicked.connect(self._do_import)
        btn_box.addWidget(btn_ok)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)

    def _browse(self):
        f, _ = QFileDialog.getOpenFileName(self, "Seleccionar documento", "", "Documentos (*.txt *.md *.docx)")
        if f:
            self.edit_file.setText(f)

    def _do_import(self):
        p = self.edit_file.text().strip()
        if not p or not Path(p).exists():
            QMessageBox.warning(self, "Atención", "Selecciona un archivo existente.")
            return

        sep = self.combo_sep.text() or "#"
        try:
            res = ImportAndSplit.import_and_split(self.project, p, separator=sep)
            count = res.get("total_items", 0)
            self.imported_count = count
            QMessageBox.information(self, "Importación Finalizada", f"¡Se han importado y dividido {count} escenas en el Manuscrito!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al importar y dividir:\n{str(e)}")
