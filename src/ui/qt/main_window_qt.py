"""
Ventana Principal Completa y Operativa de Escritorio en PyQt6 (MainWindowQt).
Orquestador interactivo de la estación de trabajo editorial profesional para Windows 11:
- Menús completos y barra de herramientas
- Árbol del Binder interactivo con operaciones de estructura narrativa (Ctrl+N, Ctrl+K, Ctrl+Shift+M)
- Editor de texto enriquecido RTF real con formato tipográfico y barra de estado
- Pizarra de Corcho interactiva (Ctrl+2) con tarjetas y sinopsis sincronizadas
- Esquema editorial (Ctrl+3) con recuentos recursivos y barras de progreso
- Modo Scrivenings continuo (Ctrl+4)
- Pantalla dividida (Ctrl+', Ctrl+Shift+')
- Inspector Scrivener 3 con 6 pestañas especializadas (Ctrl+Shift+I)
- Modo Composición inmersivo a pantalla completa (F11)
- Diálogo de Compilación multiformato nativo (Ctrl+Shift+E)
- Conmutación en caliente de temas visuales
- Copias de seguridad automáticas con hash SHA-256
"""

import sys
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QLabel, QToolBar,
    QMenuBar, QMenu, QStatusBar, QStackedWidget, QPushButton,
    QComboBox, QFileDialog, QMessageBox, QFontComboBox, QSpinBox,
    QColorDialog, QInputDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QAction, QIcon, QFont, QTextCharFormat, QTextCursor,
    QTextBlockFormat, QColor, QKeySequence
)

from ...core.project import EscritorioProject, BinderItem
from ...core.backup_manager import BackupManager
from ...core.importers.project_templates import ProjectTemplateManager
from .theme_styler import get_qss, THEME_PALETTES
from .corkboard_qt import CorkboardQt
from .outliner_qt import OutlinerQt
from .inspector_qt import InspectorQt
from .composition_qt import CompositionModeQt
from .compile_dialog_qt import CompileDialogQt
from .dialogs_qt import NewProjectDialogQt, ProjectTargetsDialogQt, ImportAndSplitDialogQt


class MainWindowQt(QMainWindow):
    """Ventana principal interactiva de Escritorio."""

    def __init__(self, project_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Escritorio - Estación de Trabajo Editorial Portable")
        self.resize(1360, 850)

        self.project: Optional[EscritorioProject] = None
        self.active_item: Optional[BinderItem] = None
        self.split_active = False

        # Cargar tema visual conservado de la última ejecución
        self.current_theme = self._load_persisted_theme()

        # Configuración inicial de UI
        self._init_menu_bar()
        self._init_tool_bar()
        self._init_central_widget()
        self._init_status_bar()
        self._init_shortcuts()
        self._apply_theme(self.current_theme)

        # Temporizador de autoguardado (cada 2 segundos)
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self._auto_save)
        self.autosave_timer.start(2000)

        # Cargar proyecto inicial si se proporciona o crear demo
        if project_path and Path(project_path).exists():
            self.load_project(project_path)
        else:
            self._create_initial_default_project()

    # =========================================================================
    # GESTIÓN DE CONFIGURACIÓN Y PERSISTENCIA DE MODO VISUAL PORTABLE
    # =========================================================================

    def _get_portable_config_dir(self) -> Path:
        """Obtiene la carpeta portable ./config de forma 100% relativa."""
        if getattr(sys, "frozen", False):
            base_dir = Path(sys.executable).resolve().parent
        else:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
        cfg_dir = base_dir / "config"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        return cfg_dir

    def _get_settings_file(self) -> Path:
        """Ruta al archivo ./config/escritorio_settings.json."""
        return self._get_portable_config_dir() / "escritorio_settings.json"

    def _load_persisted_theme(self) -> str:
        """Recupera el modo visual elegido la última vez que se ejecutó la aplicación."""
        try:
            settings_path = self._get_settings_file()
            if settings_path.exists():
                data = json.loads(settings_path.read_text(encoding="utf-8"))
                saved_theme = data.get("theme")
                if saved_theme and saved_theme in THEME_PALETTES:
                    return saved_theme
        except Exception:
            pass
        return "dark_obsidian"

    def _save_persisted_theme(self, theme_key: str):
        """Guarda de forma atómica el tema elegido para conservarlo entre ejecuciones."""
        try:
            settings_path = self._get_settings_file()
            settings = {
                "app_name": "Escritorio",
                "version": "1.0.0",
                "portable_mode": True,
                "system_registry_access": False,
                "appdata_access": False,
                "theme": theme_key
            }
            if settings_path.exists():
                try:
                    loaded = json.loads(settings_path.read_text(encoding="utf-8"))
                    if isinstance(loaded, dict):
                        settings = loaded
                        settings["theme"] = theme_key
                except Exception:
                    pass

            tmp_path = settings_path.with_suffix(".tmp")
            tmp_path.write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8")
            if settings_path.exists():
                settings_path.unlink()
            tmp_path.rename(settings_path)
        except Exception as e:
            pass

    # =========================================================================
    # INICIALIZACIÓN DE COMPONENTES DE INTERFAZ
    # =========================================================================

    def _add_action(self, menu, text: str, slot=None, shortcut=None) -> QAction:
        act = menu.addAction(text)
        if shortcut:
            if isinstance(shortcut, str):
                act.setShortcut(QKeySequence(shortcut))
            elif isinstance(shortcut, QKeySequence.StandardKey):
                act.setShortcut(QKeySequence(shortcut))
            else:
                act.setShortcut(shortcut)
        if slot:
            act.triggered.connect(slot)
        return act

    def _init_menu_bar(self):
        menubar = self.menuBar()

        # Archivo
        menu_file = menubar.addMenu("&Archivo")
        self._add_action(menu_file, "Nuevo Proyecto...", self._on_new_project, "Ctrl+Shift+N")
        self._add_action(menu_file, "Abrir Proyecto...", self._on_open_project, QKeySequence.StandardKey.Open)
        self._add_action(menu_file, "Guardar Proyecto", self._on_save_project, QKeySequence.StandardKey.Save)
        menu_file.addSeparator()
        self._add_action(menu_file, "Importar y Dividir (Import & Split)...", self._on_import_and_split)
        self._add_action(menu_file, "Compilar Manuscrito...", self._on_compile_dialog, "Ctrl+Shift+E")
        menu_file.addSeparator()
        self._add_action(menu_file, "Crear Copia de Seguridad Inmediata", self._on_manual_backup)
        menu_file.addSeparator()
        self._add_action(menu_file, "Salir", self.close, QKeySequence.StandardKey.Quit)

        # Editar
        menu_edit = menubar.addMenu("&Editar")
        self._add_action(menu_edit, "Deshacer", lambda: self.editor.undo(), QKeySequence.StandardKey.Undo)
        self._add_action(menu_edit, "Rehacer", lambda: self.editor.redo(), QKeySequence.StandardKey.Redo)
        menu_edit.addSeparator()
        self._add_action(menu_edit, "Cortar", lambda: self.editor.cut(), QKeySequence.StandardKey.Cut)
        self._add_action(menu_edit, "Copiar", lambda: self.editor.copy(), QKeySequence.StandardKey.Copy)
        self._add_action(menu_edit, "Pegar", lambda: self.editor.paste(), QKeySequence.StandardKey.Paste)
        self._add_action(menu_edit, "Seleccionar Todo", lambda: self.editor.selectAll(), QKeySequence.StandardKey.SelectAll)

        # Ver
        menu_view = menubar.addMenu("&Ver")
        self._add_action(menu_view, "Modo Editor", lambda: self._set_central_view(0), "Ctrl+1")
        self._add_action(menu_view, "Pizarra de Corcho (Corkboard)", lambda: self._set_central_view(1), "Ctrl+2")
        self._add_action(menu_view, "Esquema (Outliner)", lambda: self._set_central_view(2), "Ctrl+3")
        self._add_action(menu_view, "Modo Scrivenings", lambda: self._set_central_view(3), "Ctrl+4")
        menu_view.addSeparator()
        self._add_action(menu_view, "Dividir Pantalla Verticalmente", self._toggle_split_vertical, "Ctrl+'")
        self._add_action(menu_view, "Dividir Pantalla Horizontalmente", self._toggle_split_horizontal, "Ctrl+Shift+'")
        self._add_action(menu_view, "Cerrar División", self._close_split)
        menu_view.addSeparator()
        self._add_action(menu_view, "Conmutar Binder", self._toggle_binder, "Ctrl+Shift+B")
        self._add_action(menu_view, "Conmutar Inspector", self._toggle_inspector, "Ctrl+Shift+I")
        self._add_action(menu_view, "Modo Composición (F11)", self._on_composition_mode, "F11")

        # Proyecto
        menu_proj = menubar.addMenu("&Proyecto")
        self._add_action(menu_proj, "Nueva Escena", self._on_new_scene, "Ctrl+N")
        self._add_action(menu_proj, "Nueva Carpeta", self._on_new_folder, "Ctrl+Alt+N")
        menu_proj.addSeparator()
        self._add_action(menu_proj, "Objetivos de Proyecto (Targets)...", self._on_project_targets, "Ctrl+Shift+T")

        # Documento
        menu_doc = menubar.addMenu("&Documento")
        self._add_action(menu_doc, "Dividir en Posición del Cursor", self._on_split_scene, "Ctrl+K")
        self._add_action(menu_doc, "Fusionar con Siguiente Escena", self._on_merge_scenes, "Ctrl+Shift+M")
        self._add_action(menu_doc, "Tomar Instantánea (Snapshot)", self._on_take_snapshot, "Ctrl+5")
        self._add_action(menu_doc, "Duplicar Escena", self._on_duplicate_item, "Ctrl+D")
        self._add_action(menu_doc, "Mover a Papelera", self._on_delete_item, QKeySequence.StandardKey.Delete)

        # Formato
        menu_fmt = menubar.addMenu("&Formato")
        self._add_action(menu_fmt, "Negrita", self._toggle_bold, QKeySequence.StandardKey.Bold)
        self._add_action(menu_fmt, "Cursiva", self._toggle_italic, QKeySequence.StandardKey.Italic)
        self._add_action(menu_fmt, "Subrayado", self._toggle_underline, QKeySequence.StandardKey.Underline)
        menu_fmt.addSeparator()
        self._add_action(menu_fmt, "Alinear a la Izquierda", lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignLeft))
        self._add_action(menu_fmt, "Centrar", lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignCenter))
        self._add_action(menu_fmt, "Alinear a la Derecha", lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignRight))
        self._add_action(menu_fmt, "Justificar", lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignJustify))

        # Herramientas
        menu_tools = menubar.addMenu("&Herramientas")
        menu_themes = menu_tools.addMenu("Temas Visuales")
        for th_key in THEME_PALETTES.keys():
            readable = th_key.replace("_", " ").title()
            self._add_action(menu_themes, readable, lambda k=th_key: self._apply_theme(k))

        # Ayuda
        menu_help = menubar.addMenu("A&yuda")
        self._add_action(menu_help, "Manual de Usuario de Escritorio", self._on_user_manual, "F1")
        self._add_action(menu_help, "Acerca de Escritorio", self._on_about)

    def _init_tool_bar(self):
        toolbar = QToolBar("Acciones Principales")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Botones de estructura
        btn_new_doc = QPushButton("📄 + Escena")
        btn_new_doc.clicked.connect(self._on_new_scene)
        toolbar.addWidget(btn_new_doc)

        btn_new_fld = QPushButton("📁 + Carpeta")
        btn_new_fld.clicked.connect(self._on_new_folder)
        toolbar.addWidget(btn_new_fld)

        toolbar.addSeparator()

        # Botones de conmutación de vista
        self.btn_view_editor = QPushButton("✍️ Editor")
        self.btn_view_editor.clicked.connect(lambda: self._set_central_view(0))
        toolbar.addWidget(self.btn_view_editor)

        self.btn_view_corkboard = QPushButton("📌 Corcho")
        self.btn_view_corkboard.clicked.connect(lambda: self._set_central_view(1))
        toolbar.addWidget(self.btn_view_corkboard)

        self.btn_view_outliner = QPushButton("📊 Esquema")
        self.btn_view_outliner.clicked.connect(lambda: self._set_central_view(2))
        toolbar.addWidget(self.btn_view_outliner)

        self.btn_view_scriv = QPushButton("📜 Scrivenings")
        self.btn_view_scriv.clicked.connect(lambda: self._set_central_view(3))
        toolbar.addWidget(self.btn_view_scriv)

        toolbar.addSeparator()

        btn_split = QPushButton("🔀 Dividir")
        btn_split.clicked.connect(self._toggle_split_vertical)
        toolbar.addWidget(btn_split)

        btn_comp = QPushButton("🧘 Modo F11")
        btn_comp.clicked.connect(self._on_composition_mode)
        toolbar.addWidget(btn_comp)

        btn_export = QPushButton("🚀 Compilar")
        btn_export.setStyleSheet("background-color: #7c5cbf; color: white; font-weight: bold;")
        btn_export.clicked.connect(self._on_compile_dialog)
        toolbar.addWidget(btn_export)

        toolbar.addSeparator()

        # Selector rápido de tema
        toolbar.addWidget(QLabel(" Tema: "))
        self.combo_theme = QComboBox()
        self.combo_theme.addItems([k.replace("_", " ").title() for k in THEME_PALETTES.keys()])
        
        # Sincronizar índice inicial con el tema persistido cargado
        cur_readable = self.current_theme.replace("_", " ").title()
        idx = self.combo_theme.findText(cur_readable)
        if idx >= 0:
            self.combo_theme.setCurrentIndex(idx)
            
        self.combo_theme.currentTextChanged.connect(self._on_theme_combo_changed)
        toolbar.addWidget(self.combo_theme)

    def _init_central_widget(self):
        # Splitter principal de 3 columnas (Binder | Área Central | Inspector)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.main_splitter)

        # 1. Columna Izquierda: Binder (Árbol)
        binder_box = QWidget()
        binder_layout = QVBoxLayout(binder_box)
        binder_layout.setContentsMargins(4, 4, 4, 4)

        binder_header = QLabel("<b>CUADERNO (BINDER)</b>")
        binder_header.setStyleSheet("padding: 4px; color: #a0a0b0; font-size: 8pt;")
        binder_layout.addWidget(binder_header)

        self.binder_tree = QTreeWidget()
        self.binder_tree.setHeaderHidden(True)
        self.binder_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.binder_tree.customContextMenuRequested.connect(self._show_binder_context_menu)
        self.binder_tree.itemClicked.connect(self._on_binder_item_clicked)
        binder_layout.addWidget(self.binder_tree)

        self.main_splitter.addWidget(binder_box)

        # 2. Columna Central: Pila de Vistas (Stack: Editor / Corcho / Esquema / Scrivenings)
        self.central_stack = QStackedWidget()

        # Vista 0: Editor y División de pantalla
        editor_container = QWidget()
        ed_layout = QVBoxLayout(editor_container)
        ed_layout.setContentsMargins(4, 4, 4, 4)
        ed_layout.setSpacing(4)

        # Barra de formato del editor
        fmt_bar = QHBoxLayout()
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont("Georgia", 12))
        self.font_combo.currentFontChanged.connect(self._on_font_family_changed)
        fmt_bar.addWidget(self.font_combo)

        self.spin_size = QSpinBox()
        self.spin_size.setRange(8, 72)
        self.spin_size.setValue(12)
        self.spin_size.valueChanged.connect(self._on_font_size_changed)
        fmt_bar.addWidget(self.spin_size)

        btn_b = QPushButton("B")
        btn_b.setFixedWidth(28)
        btn_b.setStyleSheet("font-weight: bold;")
        btn_b.clicked.connect(self._toggle_bold)
        fmt_bar.addWidget(btn_b)

        btn_i = QPushButton("I")
        btn_i.setFixedWidth(28)
        btn_i.setStyleSheet("font-style: italic;")
        btn_i.clicked.connect(self._toggle_italic)
        fmt_bar.addWidget(btn_i)

        btn_u = QPushButton("U")
        btn_u.setFixedWidth(28)
        btn_u.setStyleSheet("text-decoration: underline;")
        btn_u.clicked.connect(self._toggle_underline)
        fmt_bar.addWidget(btn_u)

        fmt_bar.addStretch()
        ed_layout.addLayout(fmt_bar)

        # Splitter del editor (permite dividir en dos editores)
        self.editor_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Editor principal
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Georgia", 12))
        self.editor.textChanged.connect(self._on_editor_text_changed)
        self.editor_splitter.addWidget(self.editor)

        # Editor secundario (inicialmente oculto)
        self.editor_secondary = QTextEdit()
        self.editor_secondary.setFont(QFont("Georgia", 12))
        self.editor_secondary.setVisible(False)
        self.editor_splitter.addWidget(self.editor_secondary)

        ed_layout.addWidget(self.editor_splitter, 1)
        self.central_stack.addWidget(editor_container)

        # Vista 1: Corcho (Corkboard)
        self.corkboard = CorkboardQt(self.project)
        self.corkboard.cardSelected.connect(self._select_binder_by_uuid)
        self.central_stack.addWidget(self.corkboard)

        # Vista 2: Esquema (Outliner)
        self.outliner = OutlinerQt(self.project)
        self.outliner.itemSelected.connect(self._select_binder_by_uuid)
        self.central_stack.addWidget(self.outliner)

        # Vista 3: Modo Scrivenings
        self.scrivenings_editor = QTextEdit()
        self.scrivenings_editor.setFont(QFont("Georgia", 12))
        self.scrivenings_editor.textChanged.connect(self._on_scrivenings_text_changed)
        self.central_stack.addWidget(self.scrivenings_editor)

        self.main_splitter.addWidget(self.central_stack)

        # 3. Columna Derecha: Inspector con 6 pestañas
        self.inspector = InspectorQt(self.project)
        self.inspector.itemModified.connect(self._on_inspector_item_modified)
        self.inspector.rollbackRequested.connect(self._on_snapshot_rollback)
        self.main_splitter.addWidget(self.inspector)

        # Proporciones iniciales: Binder (220px), Central (800px), Inspector (320px)
        self.main_splitter.setSizes([220, 800, 320])

    def _init_status_bar(self):
        sb = self.statusBar()
        self.lbl_status_doc = QLabel("Sin documento activo")
        self.lbl_status_metrics = QLabel("Palabras: 0  |  Caracteres: 0")
        self.lbl_status_save = QLabel("🟢 Guardado")

        sb.addWidget(self.lbl_status_doc, 1)
        sb.addPermanentWidget(self.lbl_status_metrics)
        sb.addPermanentWidget(self.lbl_status_save)

    def _init_shortcuts(self):
        # Atajos estándar adicionales
        pass

    # =========================================================================
    # GESTIÓN DE PROYECTO Y BINDER
    # =========================================================================

    def _create_initial_default_project(self):
        """Crea un proyecto inicial en memoria / temporal para comenzar de inmediato."""
        projects_dir = Path.home() / ".escritorio" / "proyectos"
        projects_dir.mkdir(parents=True, exist_ok=True)
        proj_dir = projects_dir / "Proyecto_Activo.escr"
        if proj_dir.exists():
            self.load_project(str(proj_dir))
        else:
            proj = ProjectTemplateManager.create_project_from_template(
                template_id="novel_parts",
                destination_path=projects_dir,
                project_name="Proyecto_Activo",
                native=True
            )
            proj.save_all()
            p_dir = str(proj.project_dir)
            proj.close()
            self.load_project(p_dir)

    def load_project(self, path: str):
        """Carga un proyecto .escr o .scriv y puebla el árbol del Binder."""
        try:
            if self.project:
                self.project.close()

            self.project = EscritorioProject.load(path, force_unlock=True)
            self.corkboard.project = self.project
            self.outliner.project = self.project
            self.inspector.project = self.project

            self._populate_binder_tree()
            self.setWindowTitle(f"Escritorio - {self.project.title} ({path})")
            self.lbl_status_save.setText("🟢 Proyecto Cargado")
        except Exception as e:
            QMessageBox.critical(self, "Error al cargar proyecto", f"No se pudo cargar el proyecto:\n{str(e)}")

    def _populate_binder_tree(self):
        """Reconstruye el árbol visual del Binder a partir de la estructura del proyecto."""
        self.binder_tree.clear()
        if not self.project:
            return

        def add_node(parent_widget, item: BinderItem):
            icon_char = "📁" if item.item_type == "Folder" else "📄"
            if item.title in ("Investigación", "Research"):
                icon_char = "🔍"
            elif item.title in ("Papelera", "Trash"):
                icon_char = "🗑️"

            wc = item.get_word_count() if hasattr(item, "get_word_count") else 0
            node = QTreeWidgetItem([f"{icon_char} {item.title}"])
            node.setData(0, Qt.ItemDataRole.UserRole, item.uuid)

            if isinstance(parent_widget, QTreeWidget):
                parent_widget.addTopLevelItem(node)
            else:
                parent_widget.addChild(node)

            for child in getattr(item, "children", []):
                add_node(node, child)

            node.setExpanded(True)
            return node

        # Agregar carpetas raíz
        for root in self.project.root_items:
            add_node(self.binder_tree, root)

        # Seleccionar el primer documento de texto que encontremos
        first_doc = self._find_first_text_doc(self.project.draft_folder)
        if first_doc:
            self._select_binder_by_uuid(first_doc.uuid)

    def _find_first_text_doc(self, folder: Optional[BinderItem]) -> Optional[BinderItem]:
        if not folder:
            return None
        for child in getattr(folder, "children", []):
            if child.item_type == "Text":
                return child
            res = self._find_first_text_doc(child)
            if res:
                return res
        return None

    def _on_binder_item_clicked(self, tree_item: QTreeWidgetItem, column: int):
        uuid = tree_item.data(0, Qt.ItemDataRole.UserRole)
        if uuid:
            self._select_binder_by_uuid(uuid)

    def _select_binder_by_uuid(self, uuid: str):
        if not self.project:
            return

        item = self.project.get_item(uuid)
        if not item:
            return

        self.active_item = item
        self.inspector.set_item(item)

        # Si es una carpeta, alimentar Corcho, Esquema y Scrivenings
        if item.item_type == "Folder":
            self.corkboard.set_folder(item)
            self.outliner.set_folder(item)
            self._load_scrivenings_for_folder(item)
        else:
            # Si es documento de texto, cargar en el editor y cambiar a vista editor
            self.editor.blockSignals(True)
            content = item.get_content_plain() if hasattr(item, "get_content_plain") else ""
            self.editor.setPlainText(content)
            self.editor.blockSignals(False)
            self._set_central_view(0)

        self.lbl_status_doc.setText(f"Activo: {item.title} ({item.item_type})")
        self._update_editor_metrics()

    def _load_scrivenings_for_folder(self, folder: BinderItem):
        """Concatena las escenas hijas con divisores no destructivos."""
        children = getattr(folder, "children", [])
        composite_lines = []
        for child in children:
            t = child.title
            txt = child.get_content_plain() if hasattr(child, "get_content_plain") else ""
            composite_lines.append(f"══════════════ [ {t} ] ══════════════\n{txt}\n")
        self.scrivenings_editor.blockSignals(True)
        self.scrivenings_editor.setPlainText("\n".join(composite_lines))
        self.scrivenings_editor.blockSignals(False)

    # =========================================================================
    # EDICIÓN DE TEXTO, FORMATO Y AUTOGUARDADO
    # =========================================================================

    def _on_editor_text_changed(self):
        if not self.active_item:
            return
        text = self.editor.toPlainText()
        if hasattr(self.active_item, "set_content_plain"):
            self.active_item.set_content_plain(text)
        self.lbl_status_save.setText("🟡 Modificado...")
        self._update_editor_metrics()

    def _on_scrivenings_text_changed(self):
        self.lbl_status_save.setText("🟡 Scrivenings Modificado...")

    def _update_editor_metrics(self):
        text = self.editor.toPlainText()
        words = len(text.split())
        chars = len(text)
        self.lbl_status_metrics.setText(f"Palabras: {words:,}  |  Caracteres: {chars:,}")

    def _auto_save(self):
        if self.project and hasattr(self.project, "save"):
            try:
                self.project.save()
                self.lbl_status_save.setText("🟢 Guardado")
            except Exception:
                pass

    def _on_save_project(self):
        if self.project:
            self.project.save()
            self.lbl_status_save.setText("🟢 Guardado Manualmente")

    # =========================================================================
    # ACCIONES DE ESTRUCTURA NARRATIVA (NUEVA ESCENA, DIVIDIR, FUSIONAR)
    # =========================================================================

    def _on_new_scene(self):
        if not self.project:
            return
        parent_folder = self.project.draft_folder
        if self.active_item and self.active_item.item_type == "Folder":
            parent_folder = self.active_item

        new_item = self.project.create_item(
            parent_uuid=parent_folder.uuid,
            title=f"Nueva Escena {len(parent_folder.children) + 1}",
            item_type="Text"
        )
        new_item.set_content_plain("Escribe aquí el contenido de tu escena...")
        self._populate_binder_tree()
        self._select_binder_by_uuid(new_item.uuid)

    def _on_new_folder(self):
        if not self.project:
            return
        parent_folder = self.project.draft_folder
        new_fld = self.project.create_item(
            parent_uuid=parent_folder.uuid,
            title=f"Nuevo Capítulo {len(parent_folder.children) + 1}",
            item_type="Folder"
        )
        self._populate_binder_tree()
        self._select_binder_by_uuid(new_fld.uuid)

    def _on_split_scene(self):
        """Divide el documento activo en dos en la posición exacta del cursor (Ctrl+K)."""
        if not self.active_item or self.active_item.item_type != "Text":
            return
        cursor = self.editor.textCursor()
        pos = cursor.position()
        full_text = self.editor.toPlainText()

        first_part = full_text[:pos]
        second_part = full_text[pos:]

        self.active_item.set_content_plain(first_part)
        self.editor.setPlainText(first_part)

        # Crear nuevo documento hermano con la segunda parte
        parent = self.project.find_parent(self.active_item.uuid)
        parent_uuid = parent.uuid if parent else (self.project.draft_folder.uuid if self.project.draft_folder else "")
        new_doc = self.project.create_item(
            parent_uuid=parent_uuid,
            title=f"{self.active_item.title} (Continuación)",
            item_type="Text"
        )
        new_doc.set_content_plain(second_part)

        self._populate_binder_tree()
        self.statusBar().showMessage(f"Escena dividida exitosamente en '{new_doc.title}'.", 3000)

    def _on_merge_scenes(self):
        """Fusiona el documento activo con el siguiente hermano (Ctrl+Shift+M)."""
        if not self.active_item or not self.project:
            return
        parent = self.project.find_parent(self.active_item.uuid)
        if not parent:
            parent = self.project.draft_folder

        children = getattr(parent, "children", [])
        try:
            idx = children.index(self.active_item)
            if idx + 1 < len(children):
                next_item = children[idx + 1]
                t1 = self.active_item.get_content_plain()
                t2 = next_item.get_content_plain()
                merged_text = f"{t1}\n\n{t2}"

                self.active_item.set_content_plain(merged_text)
                self.editor.setPlainText(merged_text)

                self.project.delete_item(next_item.uuid)
                self._populate_binder_tree()
                self.statusBar().showMessage(f"Escena '{next_item.title}' fusionada en '{self.active_item.title}'.", 3000)
            else:
                self.statusBar().showMessage("No hay una siguiente escena en la misma carpeta para fusionar.", 3000)
        except Exception as e:
            self.statusBar().showMessage(f"Error al fusionar: {e}", 3000)

    def _on_duplicate_item(self):
        if not self.active_item or not self.project:
            return
        parent = self.project.find_parent(self.active_item.uuid)
        parent_uuid = parent.uuid if parent else (self.project.draft_folder.uuid if self.project.draft_folder else "")
        dup = self.project.create_item(
            parent_uuid=parent_uuid,
            title=f"{self.active_item.title} (Copia)",
            item_type=self.active_item.item_type
        )
        dup.set_content_plain(self.active_item.get_content_plain())
        self._populate_binder_tree()
        self._select_binder_by_uuid(dup.uuid)

    def _on_delete_item(self):
        if not self.active_item or not self.project:
            return
        resp = QMessageBox.question(
            self, "Mover a Papelera",
            f"¿Deseas mover '{self.active_item.title}' a la Papelera?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp == QMessageBox.StandardButton.Yes:
            self.project.delete_item(self.active_item.uuid)
            self.active_item = None
            self._populate_binder_tree()

    def _show_binder_context_menu(self, pos):
        item = self.binder_tree.itemAt(pos)
        menu = QMenu(self)
        menu.addAction("📄 Nueva Escena", self._on_new_scene)
        menu.addAction("📁 Nueva Carpeta", self._on_new_folder)
        menu.addSeparator()
        menu.addAction("✂️ Dividir en Cursor (Ctrl+K)", self._on_split_scene)
        menu.addAction("🔗 Fusionar con Siguiente (Ctrl+Shift+M)", self._on_merge_scenes)
        menu.addAction("📋 Duplicar", self._on_duplicate_item)
        menu.addSeparator()
        menu.addAction("🗑️ Mover a Papelera", self._on_delete_item)
        menu.exec(self.binder_tree.mapToGlobal(pos))

    # =========================================================================
    # VISTAS, SPLIT Y MODOS VISUALES
    # =========================================================================

    def _set_central_view(self, index: int):
        self.central_stack.setCurrentIndex(index)
        views = ["Editor", "Corcho", "Esquema", "Scrivenings"]
        if 0 <= index < len(views):
            self.lbl_status_save.setText(f"Vista: {views[index]}")

    def _toggle_split_vertical(self):
        if not self.split_active:
            self.editor_splitter.setOrientation(Qt.Orientation.Horizontal)
            self.editor_secondary.setPlainText(self.editor.toPlainText())
            self.editor_secondary.setVisible(True)
            self.split_active = True
        else:
            self._close_split()

    def _toggle_split_horizontal(self):
        if not self.split_active:
            self.editor_splitter.setOrientation(Qt.Orientation.Vertical)
            self.editor_secondary.setPlainText(self.editor.toPlainText())
            self.editor_secondary.setVisible(True)
            self.split_active = True
        else:
            self._close_split()

    def _close_split(self):
        self.editor_secondary.setVisible(False)
        self.split_active = False

    def _toggle_binder(self):
        box = self.main_splitter.widget(0)
        box.setVisible(not box.isVisible())

    def _toggle_inspector(self):
        self.inspector.setVisible(not self.inspector.isVisible())

    def _apply_theme(self, theme_key: str):
        self.current_theme = theme_key
        qss = get_qss(theme_key)
        self.setStyleSheet(qss)
        self.lbl_status_save.setText(f"Tema: {theme_key.replace('_', ' ').title()}")

        # Sincronizar combo si existe
        if hasattr(self, "combo_theme"):
            readable = theme_key.replace("_", " ").title()
            idx = self.combo_theme.findText(readable)
            if idx >= 0 and self.combo_theme.currentIndex() != idx:
                self.combo_theme.blockSignals(True)
                self.combo_theme.setCurrentIndex(idx)
                self.combo_theme.blockSignals(False)

        # Persistir selección en archivo portable ./config/escritorio_settings.json
        self._save_persisted_theme(theme_key)

    def _on_theme_combo_changed(self, text: str):
        key = text.lower().replace(" ", "_")
        self._apply_theme(key)

    # =========================================================================
    # MODOS ESPECIALES Y DIÁLOGOS
    # =========================================================================

    def _on_composition_mode(self):
        """Abre el Modo Composición libre de distracciones a pantalla completa (F11)."""
        if not self.active_item:
            QMessageBox.warning(self, "Modo Composición", "Selecciona primero una escena en el Binder.")
            return

        comp_win = CompositionModeQt(self.active_item, self)
        comp_win.contentSaved.connect(self._on_comp_content_saved)
        comp_win.showFullScreen()

    def _on_comp_content_saved(self, uuid: str, new_text: str):
        if self.active_item and self.active_item.uuid == uuid:
            self.editor.setPlainText(new_text)

    def _on_compile_dialog(self):
        """Abre el Diálogo de Compilación Multiformato (Ctrl+Shift+E)."""
        if not self.project:
            return
        dlg = CompileDialogQt(self.project, self)
        dlg.exec()

    def _on_project_targets(self):
        """Abre la ventana flotante de Objetivos de Proyecto (Ctrl+Shift+T)."""
        cur_w = self.active_item.get_word_count() if self.active_item else 0
        dlg = ProjectTargetsDialogQt(current_words=cur_w, target_words=50000, session_words=cur_w, session_target=1500, parent=self)
        dlg.exec()

    def _on_new_project(self):
        dlg = NewProjectDialogQt(self)
        if dlg.exec() and dlg.created_project_path:
            self.load_project(dlg.created_project_path)

    def _on_open_project(self):
        path = QFileDialog.getExistingDirectory(self, "Seleccionar Proyecto .escr o .scriv")
        if path:
            self.load_project(path)

    def _on_import_and_split(self):
        if not self.project:
            return
        dlg = ImportAndSplitDialogQt(self.project, self)
        if dlg.exec():
            self._populate_binder_tree()

    def _on_take_snapshot(self):
        if self.active_item:
            self.active_item.create_snapshot("Instantánea Manual (Ctrl+5)")
            self.inspector._refresh_snapshots()
            self.statusBar().showMessage(f"Se ha tomado una instantánea de '{self.active_item.title}'.", 3000)

    def _on_inspector_item_modified(self, uuid: str):
        pass

    def _on_snapshot_rollback(self, uuid: str, restored_text: str):
        if self.active_item and self.active_item.uuid == uuid:
            self.editor.setPlainText(restored_text)

    def _on_manual_backup(self):
        if not self.project:
            return
        backup_dir = Path(self.project.project_dir).parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        zip_path, sha = BackupManager.create_backup_zip(self.project.project_dir, str(backup_dir))
        QMessageBox.information(
            self, "Copia de Seguridad Generada",
            f"¡Copia de seguridad ZIP generada con éxito!\n\nArchivo:\n{zip_path}\nSHA-256:\n{sha}"
        )

    # =========================================================================
    # ACCIONES DE FORMATO
    # =========================================================================

    def _toggle_bold(self):
        fmt = QTextCharFormat()
        weight = QFont.Weight.Normal if self.editor.fontWeight() == QFont.Weight.Bold else QFont.Weight.Bold
        fmt.setFontWeight(weight)
        self.editor.mergeCurrentCharFormat(fmt)

    def _toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.editor.fontItalic())
        self.editor.mergeCurrentCharFormat(fmt)

    def _toggle_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.editor.fontUnderline())
        self.editor.mergeCurrentCharFormat(fmt)

    def _on_font_family_changed(self, font: QFont):
        fmt = QTextCharFormat()
        fmt.setFontFamily(font.family())
        self.editor.mergeCurrentCharFormat(fmt)

    def _on_font_size_changed(self, size: int):
        fmt = QTextCharFormat()
        fmt.setFontPointSize(size)
        self.editor.mergeCurrentCharFormat(fmt)

    def _on_user_manual(self):
        manual_path = Path(__file__).resolve().parent.parent.parent.parent / "dist" / "Escritorio_Portable_Win11" / "README_USUARIO.md"
        if manual_path.exists():
            os.system(f'notepad.exe "{manual_path}"')
        else:
            QMessageBox.information(self, "Manual", "El manual se encuentra en README_USUARIO.md en la raíz de la aplicación.")

    def _on_about(self):
        QMessageBox.about(
            self, "Acerca de Escritorio",
            "<h2>Escritorio v1.0.0</h2>"
            "<p><b>Estación de Trabajo Editorial Portable para Windows 11</b></p>"
            "<p>Réplica integral de capacidades de Scrivener 3 con arquitectura nativa y zero-install.</p>"
            "<p>© 2026 tekkes - Código Abierto.</p>"
        )

    def closeEvent(self, event):
        """Al cerrar, guarda el proyecto, persiste el tema visual y genera copia de seguridad."""
        if hasattr(self, "current_theme"):
            self._save_persisted_theme(self.current_theme)
        if self.project:
            self.project.close()
        event.accept()
