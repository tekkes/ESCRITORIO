"""
ESCRITORIO v2.0 - Scrivener 3 Compile Modal Dialog (Diálogo Maestro de 3 Paneles)
Panel Izquierdo: Formatos predefinidos de compilación.
Panel Central: Árbol documental con casillas y asignación de Section Layouts.
Panel Derecho: Metadatos, transformaciones y reemplazos.
"""

from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget,
    QTreeWidget, QTreeWidgetItem, QLabel, QLineEdit, QComboBox,
    QPushButton, QTabWidget, QWidget, QFileDialog, QMessageBox,
    QCheckBox, QFrame
)
from PyQt6.QtCore import Qt

from ..core.project_v2 import EscritorioProjectV2, BinderNode
from ..compile.compile_engine import CompileEngineV2


class CompileModalV2(QDialog):
    """Diálogo modal de compilación idéntico al de Scrivener 3 macOS."""

    def __init__(self, project: EscritorioProjectV2, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Compilar Manuscrito — Scrivener 3 Architecture")
        self.resize(1000, 650)

        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        # Divisor de 3 paneles
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # -------------------------------------------------------------
        # PANEL 1 (IZQUIERDA): Formatos de Compilación
        # -------------------------------------------------------------
        panel_left = QFrame()
        panel_left.setStyleSheet("background-color: #1a1a20; border-radius: 6px;")
        pl_layout = QVBoxLayout(panel_left)
        pl_layout.setContentsMargins(8, 8, 8, 8)

        pl_layout.addWidget(QLabel("FORMATOS DE SALIDA:"))
        self.list_formats = QListWidget()
        self.list_formats.addItems([
            "📖 Novela Estándar (Standard Manuscript)",
            "📚 Libro Impreso (Paperback 5x8)",
            "📑 Novela con Partes (Novel with Parts)",
            "📱 Libro Electrónico (Epub 3)",
            "🎬 Guion Cinematográfico (Screenplay)",
            "📝 Texto Plano y Markdown"
        ])
        self.list_formats.setCurrentRow(0)
        pl_layout.addWidget(self.list_formats)
        splitter.addWidget(panel_left)

        # -------------------------------------------------------------
        # PANEL 2 (CENTRO): Contenido y Árbol de Compilación
        # -------------------------------------------------------------
        panel_center = QFrame()
        panel_center.setStyleSheet("background-color: #1e1e24; border-radius: 6px;")
        pc_layout = QVBoxLayout(panel_center)
        pc_layout.setContentsMargins(8, 8, 8, 8)

        h_ctrl = QHBoxLayout()
        h_ctrl.addWidget(QLabel("ESTRUCTURA DEL MANUSCRITO:"))
        btn_assign_layouts = QPushButton("⚙️ Asignar Diseños de Sección...")
        btn_assign_layouts.clicked.connect(self._assign_layouts_dialog)
        h_ctrl.addWidget(btn_assign_layouts)
        pc_layout.addLayout(h_ctrl)

        self.tree_compile = QTreeWidget()
        self.tree_compile.setHeaderLabels(["Documento", "Tipo de Sección"])
        self.tree_compile.setColumnWidth(0, 260)
        self._populate_compile_tree()
        pc_layout.addWidget(self.tree_compile)

        splitter.addWidget(panel_center)

        # -------------------------------------------------------------
        # PANEL 3 (DERECHA): Metadatos, Opciones y Reemplazos
        # -------------------------------------------------------------
        panel_right = QFrame()
        panel_right.setStyleSheet("background-color: #1a1a20; border-radius: 6px;")
        pr_layout = QVBoxLayout(panel_right)
        pr_layout.setContentsMargins(8, 8, 8, 8)

        tabs_meta = QTabWidget()

        # Tab Metadatos
        tab_m = QWidget()
        tm_layout = QVBoxLayout(tab_m)
        tm_layout.addWidget(QLabel("Título de la Obra:"))
        self.txt_title = QLineEdit(self.project.name)
        tm_layout.addWidget(self.txt_title)

        tm_layout.addWidget(QLabel("Nombre del Autor:"))
        self.txt_author = QLineEdit("Autor")
        tm_layout.addWidget(self.txt_author)

        tm_layout.addWidget(QLabel("Subtítulo:"))
        self.txt_subtitle = QLineEdit("")
        tm_layout.addWidget(self.txt_subtitle)
        tm_layout.addStretch()
        tabs_meta.addTab(tab_m, "Metadatos")

        # Tab Opciones
        tab_o = QWidget()
        to_layout = QVBoxLayout(tab_o)
        self.chk_smart_quotes = QCheckBox("Tipografía inteligente (comillas curvas)")
        self.chk_smart_quotes.setChecked(True)
        to_layout.addWidget(self.chk_smart_quotes)

        self.chk_remove_comments = QCheckBox("Excluir comentarios y notas al pie del inspector")
        self.chk_remove_comments.setChecked(True)
        to_layout.addWidget(self.chk_remove_comments)
        to_layout.addStretch()
        tabs_meta.addTab(tab_o, "Transformaciones")

        pr_layout.addWidget(tabs_meta)
        splitter.addWidget(panel_right)

        splitter.setSizes([220, 480, 280])
        root_layout.addWidget(splitter)

        # -------------------------------------------------------------
        # BARRA INFERIOR DE ACCIONES
        # -------------------------------------------------------------
        footer = QHBoxLayout()
        footer.addWidget(QLabel("Formato de Archivo:"))
        self.combo_file_fmt = QComboBox()
        self.combo_file_fmt.addItems(["DOCX (Word)", "PDF (Imprimible)", "EPUB (Ebook)", "RTF (Texto Enriquecido)", "Markdown", "Texto Plano"])
        footer.addWidget(self.combo_file_fmt)

        footer.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        footer.addWidget(btn_cancel)

        btn_compile = QPushButton("🚀 Compilar Ahora...")
        btn_compile.setStyleSheet("background-color: #7c5cbf; color: #ffffff; font-weight: bold; padding: 6px 18px;")
        btn_compile.clicked.connect(self._execute_compile)
        footer.addWidget(btn_compile)

        root_layout.addLayout(footer)

    def _populate_compile_tree(self):
        self.tree_compile.clear()
        if self.project.draft_node:
            for child in self.project.draft_node.children:
                self._add_tree_node(self.tree_compile.invisibleRootItem(), child)
        self.tree_compile.expandAll()

    def _add_tree_node(self, parent_item, node: BinderNode):
        item = QTreeWidgetItem([node.title, node.section_type])
        item.setCheckState(0, Qt.CheckState.Checked if node.include_in_compile else Qt.CheckState.Unchecked)
        item.setData(0, Qt.ItemDataRole.UserRole, node.uuid)
        parent_item.addChild(item)

        for child in node.children:
            self._add_tree_node(item, child)

    def _assign_layouts_dialog(self):
        QMessageBox.information(self, "Section Layouts", "Diseños de Sección asignados automáticamente según el nivel jerárquico:\n- Part -> Título en página impar\n- Chapter -> Encabezado numerado con salto de página\n- Scene -> Separador editorial * * *")

    def _execute_compile(self):
        fmt_idx = self.combo_file_fmt.currentIndex()
        fmt_map = {0: "DOCX", 1: "PDF", 2: "EPUB", 3: "RTF", 4: "MARKDOWN", 5: "TXT"}
        ext_map = {0: "docx", 1: "pdf", 2: "epub", 3: "rtf", 4: "md", 5: "txt"}

        fmt_str = fmt_map.get(fmt_idx, "DOCX")
        ext = ext_map.get(fmt_idx, "docx")

        default_name = f"{self.project.name}.{ext}"
        save_path, _ = QFileDialog.getSaveFileName(self, "Guardar Archivo Compilado", default_name, f"Archivos (*.{ext})")

        if not save_path:
            return

        engine = CompileEngineV2(self.project)
        success = engine.compile_project(
            output_path=Path(save_path),
            format_type=fmt_str,
            author=self.txt_author.text().strip(),
            title=self.txt_title.text().strip()
        )

        if success:
            QMessageBox.information(self, "Compilación Exitosa", f"El manuscrito se ha compilado con éxito en:\n{save_path}")
            self.accept()
        else:
            QMessageBox.warning(self, "Aviso de Compilación", "La compilación finalizó con advertencias.")
