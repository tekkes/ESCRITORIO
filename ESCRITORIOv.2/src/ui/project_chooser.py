"""
ESCRITORIO v2.0 - Project & Template Chooser (Selector de Proyectos y Plantillas)
Ventana de bienvenida y creación de proyectos basada en categorías (Ficción, No Ficción, Guion)
idéntica a Scrivener 3 macOS.
"""

from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget,
    QLabel, QPushButton, QFrame, QTextEdit, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt

from ..core.project_v2 import EscritorioProjectV2, BinderNode
from ..core.xml_engine_v2 import XmlEngineV2


class ProjectChooserDialog(QDialog):
    """Selector inicial de plantillas y apertura de proyectos."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Proyecto — Plantillas de Scrivener 3")
        self.resize(800, 500)
        self.created_project_path: Optional[Path] = None

        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(15, 15, 15, 15)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Categorías (Izquierda)
        panel_cat = QFrame()
        panel_cat.setStyleSheet("background-color: #1a1a20; border-radius: 6px;")
        pc_layout = QVBoxLayout(panel_cat)
        pc_layout.addWidget(QLabel("CATEGORÍAS:"))
        self.list_categories = QListWidget()
        self.list_categories.addItems(["Todo", "En Blanco", "Ficción", "No Ficción", "Guion", "Investigación"])
        self.list_categories.setCurrentRow(2)  # Ficción por defecto
        self.list_categories.currentRowChanged.connect(self._on_category_changed)
        pc_layout.addWidget(self.list_categories)
        splitter.addWidget(panel_cat)

        # Plantillas de la categoría (Centro)
        panel_templates = QFrame()
        panel_templates.setStyleSheet("background-color: #1e1e24; border-radius: 6px;")
        pt_layout = QVBoxLayout(panel_templates)
        pt_layout.addWidget(QLabel("PLANTILLAS DISPONIBLES:"))
        self.list_templates = QListWidget()
        self.list_templates.currentRowChanged.connect(self._on_template_changed)
        pt_layout.addWidget(self.list_templates)
        splitter.addWidget(panel_templates)

        # Descripción de la plantilla (Derecha)
        panel_desc = QFrame()
        panel_desc.setStyleSheet("background-color: #1a1a20; border-radius: 6px;")
        pd_layout = QVBoxLayout(panel_desc)
        pd_layout.addWidget(QLabel("DESCRIPCIÓN Y ESTRUCTURA:"))
        self.txt_desc = QTextEdit()
        self.txt_desc.setReadOnly(True)
        pd_layout.addWidget(self.txt_desc)
        splitter.addWidget(panel_desc)

        splitter.setSizes([160, 280, 360])
        root_layout.addWidget(splitter)

        # Barra de acciones inferior
        footer = QHBoxLayout()
        btn_open = QPushButton("📂 Abrir Proyecto Existente...")
        btn_open.clicked.connect(self._open_existing)
        footer.addWidget(btn_open)

        footer.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        footer.addWidget(btn_cancel)

        btn_create = QPushButton("✨ Crear Proyecto...")
        btn_create.setStyleSheet("background-color: #7c5cbf; color: #ffffff; font-weight: bold; padding: 6px 16px;")
        btn_create.clicked.connect(self._create_project)
        footer.addWidget(btn_create)

        root_layout.addLayout(footer)

        self._on_category_changed(2)

    def _on_category_changed(self, row: int):
        self.list_templates.clear()
        if row == 2 or row == 0:  # Ficción
            self.list_templates.addItem("📖 Novela Estándar (Novel)")
            self.list_templates.addItem("📑 Novela con Partes (Novel with Parts)")
            self.list_templates.addItem("✍️ Relato Corto (Short Story)")
        elif row == 1:  # En Blanco
            self.list_templates.addItem("📄 Proyecto en Blanco (Blank)")
        elif row == 3:  # No Ficción
            self.list_templates.addItem("🔬 Ensayo Académico con Referencias")
            self.list_templates.addItem("📚 Libro de Texto / No Ficción")
        elif row == 4:  # Guion
            self.list_templates.addItem("🎬 Guion de Largometraje (Screenplay)")
            self.list_templates.addItem("🎭 Guion Teatral")
        else:
            self.list_templates.addItem("🔍 Dossier de Investigación")

        self.list_templates.setCurrentRow(0)

    def _on_template_changed(self, row: int):
        item = self.list_templates.currentItem()
        if not item:
            return
        name = item.text()
        if "Novela" in name:
            self.txt_desc.setHtml("""
                <h3>Plantilla de Novela (Scrivener 3)</h3>
                <p>Configurada para escribir obras de ficción literaria o comercial.</p>
                <b>Estructura creada:</b>
                <ul>
                    <li><b>Manuscrito (Draft):</b> Capítulos y escenas con separadores automáticos.</li>
                    <li><b>Personajes:</b> Hojas de personaje con psicología, objetivos y trasfondo.</li>
                    <li><b>Lugares:</b> Fichas de ambientación y construcción de mundos.</li>
                    <li><b>Material Preliminar (Front Matter):</b> Portada, dedicatoria y agradecimientos.</li>
                    <li><b>Investigación (Research):</b> Notas históricas, fotos y referencias.</li>
                    <li><b>Papelera:</b> Elementos descartados seguros.</li>
                </ul>
            """)
        elif "Guion" in name:
            self.txt_desc.setHtml("""
                <h3>Plantilla de Guion Cinematográfico</h3>
                <p>Configurada para estándares de Hollywood (Courier 12pt, tabulador para diálogos y saltos de escena).</p>
            """)
        else:
            self.txt_desc.setHtml("""
                <h3>Plantilla Básica</h3>
                <p>Estructura limpia con carpetas esenciales de Manuscrito, Investigación y Papelera.</p>
            """)

    def _open_existing(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Proyecto (.escr o .scriv)")
        if folder:
            self.created_project_path = Path(folder)
            self.accept()

    def _create_project(self):
        folder = QFileDialog.getExistingDirectory(self, "Elegir Directorio donde Guardar el Nuevo Proyecto")
        if not folder:
            return

        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Nombre del Proyecto", "Introduce el nombre de la obra:", text="Mi Novela")
        if not ok or not name.strip():
            return

        proj_path = Path(folder) / f"{name.strip()}.escr"
        proj = EscritorioProjectV2(proj_path)
        proj.path.mkdir(parents=True, exist_ok=True)

        # Crear estructura estándar de novela
        draft = BinderNode(title="Manuscrito", type="DraftFolder")
        research = BinderNode(title="Investigación", type="ResearchFolder")
        trash = BinderNode(title="Papelera", type="TrashFolder")

        proj.root_nodes = [draft, research, trash]
        proj.draft_node = draft
        proj.research_node = research
        proj.trash_node = trash

        # Añadir Capítulo 1 y Escena 1
        cap1 = BinderNode(title="Capítulo 1", type="Folder", section_type="Chapter", parent_uuid=draft.uuid)
        esc1 = BinderNode(title="Escena 1", type="Text", section_type="Scene", parent_uuid=cap1.uuid)
        esc1._content_rtf = "Era una noche oscura y tormentosa cuando todo comenzó..."
        esc1._synopsis_text = "Presentación del protagonista y el incidente incitador."
        esc1.label = "Protagonista"
        esc1.status = "Primer Borrador"
        esc1.target_words = 2000

        cap1.children.append(esc1)
        draft.children.append(cap1)

        # Fichas de personaje en Investigación
        pers = BinderNode(title="Personajes", type="Folder", parent_uuid=research.uuid)
        ficha1 = BinderNode(title="Ficha del Protagonista", type="Text", parent_uuid=pers.uuid)
        ficha1._content_rtf = "Nombre: Alex Vance\nEdad: 32\nMotivación Principal: Descubrir la verdad."
        ficha1.include_in_compile = False
        pers.children.append(ficha1)
        research.children.append(pers)

        # Guardar todos los nodos
        proj.save_all_dirty_nodes()
        XmlEngineV2.save_project_xml(proj, proj_path / f"{name.strip()}.escrx")

        self.created_project_path = proj_path
        self.accept()
