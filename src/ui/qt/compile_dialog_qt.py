"""
Diálogo de Compilación Multiformato de 3 Columnas para PyQt6.
Permite compilar la novela completa a .docx, .pdf, .epub, .html y .txt con resolución de variables.
"""

from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QComboBox, QLineEdit, QCheckBox, QPushButton, QFileDialog, QMessageBox,
    QGroupBox, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt

from ...core.project import EscritorioProject
from ...compile.CompileEngine.engine import CompileEngine
from ...compile.exporters.unified_exporter import ExportFormat


class CompileDialogQt(QDialog):
    """Diálogo de compilación multiformato estilo Scrivener 3."""

    def __init__(self, project: EscritorioProject, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Compilar Manuscrito - Escritorio")
        self.resize(850, 550)

        main_layout = QVBoxLayout(self)

        # Contenedor de 3 columnas
        cols_layout = QHBoxLayout()

        # Columna 1: Formatos
        col1_group = QGroupBox("1. Formatos de Salida")
        col1_layout = QVBoxLayout(col1_group)
        self.list_formats = QListWidget()
        formats = [
            ("Microsoft Word (.docx)", "docx"),
            ("PDF de Imprenta Editorial (.pdf)", "pdf"),
            ("eBook Estándar (.epub v3)", "epub"),
            ("Página Web / Manuscrito (.html)", "html"),
            ("Texto Plano Universal (.txt)", "txt"),
            ("Texto Enriquecido (.rtf)", "rtf")
        ]
        for name, fmt in formats:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, fmt)
            self.list_formats.addItem(item)
        self.list_formats.setCurrentRow(0)
        col1_layout.addWidget(self.list_formats)
        cols_layout.addWidget(col1_group, 1)

        # Columna 2: Diseños de Sección (Section Layouts)
        col2_group = QGroupBox("2. Estructura de Secciones")
        col2_layout = QVBoxLayout(col2_group)
        col2_layout.addWidget(QLabel("Mapeo de Tipos de Sección:"))

        self.list_sections = QListWidget()
        self.list_sections.addItem("Part -> Portadilla con Título de Parte")
        self.list_sections.addItem("Chapter -> Encabezado de Capítulo (Capítulo <$n>)")
        self.list_sections.addItem("Scene -> Texto continuo con sangría")
        self.list_sections.addItem("Front Matter -> Centrado sin numerar")
        col2_layout.addWidget(self.list_sections)

        col2_layout.addWidget(QLabel("Separador de Escenas:"))
        self.combo_sep = QComboBox()
        self.combo_sep.addItems(["Salto de Línea Doble", "Asteriscos centrados ( * * * )", "Línea decorativa (~)", "Salto de Página"])
        col2_layout.addWidget(self.combo_sep)

        cols_layout.addWidget(col2_group, 1)

        # Columna 3: Metadatos y Opciones
        col3_group = QGroupBox("3. Metadatos y Marcadores")
        col3_layout = QVBoxLayout(col3_group)

        col3_layout.addWidget(QLabel("Título de la Obra:"))
        self.edit_title = QLineEdit(getattr(project, "title", "Mi Novela"))
        col3_layout.addWidget(self.edit_title)

        col3_layout.addWidget(QLabel("Nombre del Autor:"))
        self.edit_author = QLineEdit("Autor Profesional")
        col3_layout.addWidget(self.edit_author)

        self.chk_resolve_tags = QCheckBox("Evaluar variables <$n> y <$t>")
        self.chk_resolve_tags.setChecked(True)
        col3_layout.addWidget(self.chk_resolve_tags)

        self.chk_toc = QCheckBox("Generar Tabla de Contenidos")
        self.chk_toc.setChecked(True)
        col3_layout.addWidget(self.chk_toc)

        col3_layout.addStretch()
        cols_layout.addWidget(col3_group, 1)

        main_layout.addLayout(cols_layout)

        # Barra inferior de exportación
        footer_layout = QHBoxLayout()
        self.lbl_dest = QLabel("Destino:")
        footer_layout.addWidget(self.lbl_dest)

        self.edit_dest_path = QLineEdit(str(Path(self.project.project_dir).parent / f"{self.project.title}.docx"))
        footer_layout.addWidget(self.edit_dest_path, 1)

        btn_browse = QPushButton("Examinar...")
        btn_browse.clicked.connect(self._browse_destination)
        footer_layout.addWidget(btn_browse)

        self.btn_compile = QPushButton("🚀 Compilar Manuscrito")
        self.btn_compile.setStyleSheet("font-weight: bold; background-color: #7c5cbf; color: white; padding: 8px 16px;")
        self.btn_compile.clicked.connect(self._do_compile)
        footer_layout.addWidget(self.btn_compile)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        footer_layout.addWidget(btn_cancel)

        main_layout.addLayout(footer_layout)

        self.list_formats.currentRowChanged.connect(self._on_format_changed)

    def _on_format_changed(self, row: int):
        item = self.list_formats.item(row)
        if not item:
            return
        fmt = item.data(Qt.ItemDataRole.UserRole)
        cur = Path(self.edit_dest_path.text())
        self.edit_dest_path.setText(str(cur.with_suffix(f".{fmt}")))

    def _browse_destination(self):
        sel_item = self.list_formats.currentItem()
        fmt = sel_item.data(Qt.ItemDataRole.UserRole) if sel_item else "docx"
        filt = f"Archivos {fmt.upper()} (*.{fmt})"
        path, _ = QFileDialog.getSaveFileName(self, "Guardar compilación como", self.edit_dest_path.text(), filt)
        if path:
            self.edit_dest_path.setText(path)

    def _do_compile(self):
        out_path = Path(self.edit_dest_path.text())
        sel_item = self.list_formats.currentItem()
        fmt = sel_item.data(Qt.ItemDataRole.UserRole) if sel_item else "docx"

        try:
            engine = CompileEngine(self.project)
            export_fmt = ExportFormat(fmt) if fmt in [e.value for e in ExportFormat] else ExportFormat.DOCX
            res_path = engine.compile_and_export(out_path, format_type=export_fmt)

            if res_path and Path(res_path).exists():
                QMessageBox.information(
                    self, "Compilación Exitosa",
                    f"¡Manuscrito compilado con éxito!\n\nArchivo generado:\n{res_path}\nTamaño: {Path(res_path).stat().st_size:,} bytes"
                )
                self.accept()
            else:
                QMessageBox.critical(self, "Error de Compilación", "No se pudo generar el archivo de salida.")
        except Exception as e:
            QMessageBox.critical(self, "Error de Compilación", f"Ocurrió una excepción al compilar:\n{str(e)}")
