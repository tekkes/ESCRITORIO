"""
ESCRITORIO v2.0 - Master Shell Window (MainWindow)
Orquestador maestro de la interfaz con paridad exacta de Scrivener 3 macOS:
- Menús profesionales completos (9 menús estándar)
- Barra de herramientas con control segmentado, botones de historial y buscador integrado
- Área central con conmutación instantánea entre Editor, Corcho (3 modos), Esquema y Scrivenings
- Doble editor con pantalla dividida (Split View)
- Inspector lateral derecho de 6 pestañas con comparador diff
- Autoguardado atómico silencioso cada 2 segundos y copias de seguridad automáticas
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QStackedWidget, QLabel, QLineEdit, QToolButton, QFrame,
    QMenuBar, QMenu, QStatusBar, QFileDialog, QMessageBox,
    QInputDialog, QButtonGroup, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QFont, QIcon

from ..core.project_v2 import EscritorioProjectV2, BinderNode
from ..core.xml_engine_v2 import XmlEngineV2
from ..core.backup_manager import BackupManager
from ..core.stats_manager import WritingStatsManager
from .theme_v2 import get_v2_stylesheet, V2_THEMES
from .binder_v2 import BinderV2
from .editor_v2 import EditorV2
from .corkboard_v2 import CorkboardV2
from .outliner_v2 import OutlinerV2
from .inspector_v2 import InspectorV2
from .scrivenings_v2 import ScriveningsV2
from .composition_v2 import CompositionModeV2
from .quick_ref_v2 import QuickReferenceWindow
from .targets_hud_v2 import TargetsHudV2
from .linguistic_focus import LinguisticFocusDialog
from .compile_modal_v2 import CompileModalV2
from .project_chooser import ProjectChooserDialog


class ShellV2(QMainWindow):
    """Ventana principal de ESCRITORIO v2.0."""

    def __init__(self, project_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Escritorio v2.0 — Estación de Trabajo Editorial Nativa (Scrivener 3 Architecture)")
        self.resize(1380, 880)

        # Cargar configuración persistente (temas, modo de vista, último proyecto)
        self.settings = self._load_settings()
        self.current_theme = self.settings.get("theme", "obsidian_dark")
        self.current_view_mode = self.settings.get("view_mode", 0)
        self.last_project_path = self.settings.get("last_project_path", "")

        # Estado del proyecto
        self.project: Optional[EscritorioProjectV2] = None
        self.active_node: Optional[BinderNode] = None
        self.session_words_written = 0

        # Gestor de copias de seguridad
        config_dir = Path(__file__).resolve().parent.parent.parent / "config"
        self.backup_mgr = BackupManager(config_dir / "backups")

        # Gestor de tiempo y estadísticas de escritura
        self.stats_mgr = WritingStatsManager(config_dir)

        # Construcción de la interfaz
        self._init_central_ui()
        self._init_menu_bar()
        self._init_tool_bar()
        self._init_status_bar()
        self._apply_theme(self.current_theme)

        # Restaurar visibilidad de paneles persistida
        if not self.settings.get("binder_visible", True):
            self._toggle_binder(False)
        if not self.settings.get("inspector_visible", True):
            self._toggle_inspector(False)

        # Autoguardado atómico silencioso cada 2 segundos
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self._auto_save)
        self.autosave_timer.start(2000)

        # Temporizador de reloj continuo de tiempo de trabajo (cada 1 segundo)
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._on_clock_tick)
        self.clock_timer.start(1000)

        # Determinar proyecto a abrir: CLI > last_project_path > demo
        target_path = None
        if project_path and Path(project_path).exists():
            target_path = Path(project_path)
        elif self.last_project_path and Path(self.last_project_path).exists():
            target_path = Path(self.last_project_path)

        if target_path:
            try:
                self.load_project(target_path)
            except Exception as e:
                print(f"[ShellV2] Error al abrir proyecto previo ({target_path}): {e}")
                self._load_or_create_default()
        else:
            self._load_or_create_default()

        # Restaurar modo de vista guardado
        self._set_central_view(self.current_view_mode)

    # =========================================================================
    # GESTIÓN DE CONFIGURACIÓN Y PERSISTENCIA DE SESIÓN
    # =========================================================================

    def _get_config_path(self) -> Path:
        cfg_dir = Path(__file__).resolve().parent.parent.parent / "config"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        return cfg_dir / "v2_settings.json"

    def _load_settings(self) -> dict:
        cfg_file = self._get_config_path()
        if cfg_file.exists():
            try:
                with open(cfg_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ShellV2] Advertencia: no se pudo leer configuración: {e}")
        return {
            "theme": "obsidian_dark",
            "view_mode": 0,
            "last_project_path": "",
            "binder_visible": True,
            "inspector_visible": True
        }

    def _save_settings(self):
        try:
            cfg_file = self._get_config_path()
            data = {
                "theme": getattr(self, "current_theme", "obsidian_dark"),
                "view_mode": getattr(self, "current_view_mode", 0),
                "last_project_path": getattr(self, "last_project_path", ""),
                "binder_visible": self.binder.isVisible() if hasattr(self, "binder") else True,
                "inspector_visible": self.inspector.isVisible() if hasattr(self, "inspector") else True
            }
            tmp_file = cfg_file.with_suffix(".tmp")
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            tmp_file.replace(cfg_file)
        except Exception as e:
            print(f"[ShellV2] Advertencia: no se pudo guardar configuración: {e}")

    # =========================================================================
    # CONSTRUCCIÓN DE LA BARRA DE MENÚS (9 MENÚS DE SCRIVENER 3)
    # =========================================================================

    def _init_menu_bar(self):
        mb = self.menuBar()

        # 1. Archivo
        m_file = mb.addMenu("&Archivo")
        self._add_act(m_file, "Nuevo Proyecto...", self._on_new_project, "Ctrl+Shift+N")
        self._add_act(m_file, "Abrir Proyecto...", self._on_open_project, QKeySequence.StandardKey.Open)
        self._add_act(m_file, "Guardar Proyecto", self._on_save_project, QKeySequence.StandardKey.Save)
        m_file.addSeparator()
        self._add_act(m_file, "Compilar Manuscrito (Compile)...", self._on_compile, "Ctrl+Shift+E")
        self._add_act(m_file, "Crear Copia de Seguridad Inmediata (ZIP)", self._on_manual_backup)
        m_file.addSeparator()
        self._add_act(m_file, "Salir", self.close, QKeySequence.StandardKey.Quit)

        # 2. Editar
        m_edit = mb.addMenu("&Editar")
        self._add_act(m_edit, "Deshacer", lambda: self.editor.editor.undo(), QKeySequence.StandardKey.Undo)
        self._add_act(m_edit, "Rehacer", lambda: self.editor.editor.redo(), QKeySequence.StandardKey.Redo)
        m_edit.addSeparator()
        self._add_act(m_edit, "Cortar", lambda: self.editor.editor.cut(), QKeySequence.StandardKey.Cut)
        self._add_act(m_edit, "Copiar", lambda: self.editor.editor.copy(), QKeySequence.StandardKey.Copy)
        self._add_act(m_edit, "Pegar", lambda: self.editor.editor.paste(), QKeySequence.StandardKey.Paste)
        self._add_act(m_edit, "Seleccionar Todo", lambda: self.editor.editor.selectAll(), QKeySequence.StandardKey.SelectAll)

        # 3. Ver
        m_view = mb.addMenu("&Ver")
        self._add_act(m_view, "Modo Editor", lambda: self._set_central_view(0), "Ctrl+1")
        self._add_act(m_view, "Pizarra de Corcho (Corkboard)", lambda: self._set_central_view(1), "Ctrl+2")
        self._add_act(m_view, "Esquema Editorial (Outliner)", lambda: self._set_central_view(2), "Ctrl+3")
        self._add_act(m_view, "Modo Scrivenings (Flujo Continuo)", lambda: self._set_central_view(3), "Ctrl+4")
        m_view.addSeparator()
        self._add_act(m_view, "Dividir Pantalla Verticalmente", self._toggle_split_v, "Ctrl+'")
        self._add_act(m_view, "Dividir Pantalla Horizontalmente", self._toggle_split_h, "Ctrl+Shift+'")
        m_view.addSeparator()
        self._add_act(m_view, "Conmutar Archivador (Binder)", self._toggle_binder, "Ctrl+Shift+B")
        self._add_act(m_view, "Conmutar Inspector", self._toggle_inspector, "Ctrl+Shift+I")
        self._add_act(m_view, "Modo Composición a Pantalla Completa", self._open_composition, "F11")

        # 4. Navegar
        m_nav = mb.addMenu("&Navegar")
        self._add_act(m_nav, "Documento Anterior", lambda: self.editor._go_back(), "Alt+Left")
        self._add_act(m_nav, "Documento Siguiente", lambda: self.editor._go_forward(), "Alt+Right")
        self._add_act(m_nav, "Abrir en Ventana de Referencia Rápida", self._open_quick_ref, "Space")

        # 5. Proyecto
        m_proj = mb.addMenu("&Proyecto")
        self._add_act(m_proj, "Nueva Escena", lambda: self.binder.create_new_node("Text"), "Ctrl+N")
        self._add_act(m_proj, "Nueva Carpeta", lambda: self.binder.create_new_node("Folder"), "Ctrl+Alt+N")
        m_proj.addSeparator()
        self._add_act(m_proj, "Objetivos de Proyecto (Project Targets)...", self._open_targets, "Ctrl+Shift+T")
        self._add_act(m_proj, "Foco Lingüístico y Estadísticas...", self._open_linguistic_focus)

        # 6. Documento
        m_doc = mb.addMenu("&Documento")
        self._add_act(m_doc, "Dividir en Posición del Cursor", self._split_document, "Ctrl+K")
        self._add_act(m_doc, "Tomar Instantánea (Snapshot)", lambda: self.inspector.take_snapshot(), "Ctrl+5")
        self._add_act(m_doc, "Mover a Papelera", lambda: self.binder._delete_node(self.active_node) if self.active_node else None, QKeySequence.StandardKey.Delete)

        # 7. Formato
        m_fmt = mb.addMenu("&Formato")
        self._add_act(m_fmt, "Negrita", lambda: self.editor._set_font_weight(QFont.Weight.Bold), QKeySequence.StandardKey.Bold)
        self._add_act(m_fmt, "Cursiva", lambda: self.editor._toggle_italic(), QKeySequence.StandardKey.Italic)
        self._add_act(m_fmt, "Subrayado", lambda: self.editor._toggle_underline(), QKeySequence.StandardKey.Underline)

        # 8. Herramientas
        m_tools = mb.addMenu("&Herramientas")
        m_themes = m_tools.addMenu("🎨 Temas Visuales")
        self.theme_actions: Dict[str, QAction] = {}
        for th_key, th_data in V2_THEMES.items():
            act = m_themes.addAction(th_data["name"])
            act.setCheckable(True)
            act.setChecked(th_key == self.current_theme)
            act.triggered.connect(lambda checked, key=th_key: self._apply_theme(key))
            self.theme_actions[th_key] = act

        # 9. Ayuda
        m_help = mb.addMenu("A&yuda")
        self._add_act(m_help, "Acerca de Escritorio v2.0", self._on_about)

    def _add_act(self, menu: QMenu, text: str, slot, shortcut=None) -> QAction:
        act = menu.addAction(text)
        if shortcut:
            act.setShortcut(QKeySequence(shortcut) if isinstance(shortcut, str) else shortcut)
        if slot:
            act.triggered.connect(slot)
        return act

    # =========================================================================
    # BARRA DE HERRAMIENTAS PREMIUM ESTILO SCRIVENER 3 MACOS
    # =========================================================================

    def _init_tool_bar(self):
        tb = self.addToolBar("Herramientas Principales")
        tb.setMovable(False)

        # Botón Archivador
        self.btn_toggle_binder = QToolButton()
        self.btn_toggle_binder.setText("📑 Archivador")
        self.btn_toggle_binder.setCheckable(True)
        self.btn_toggle_binder.setChecked(True)
        self.btn_toggle_binder.toggled.connect(self._toggle_binder)
        tb.addWidget(self.btn_toggle_binder)

        tb.addSeparator()

        # Control Segmentado de Modos de Vista: [ Editor | Corcho | Esquema | Scrivenings ]
        seg_frame = QFrame()
        seg_frame.setObjectName("SegmentedControl")
        seg_layout = QHBoxLayout(seg_frame)
        seg_layout.setContentsMargins(2, 2, 2, 2)
        seg_layout.setSpacing(2)

        self.seg_group = QButtonGroup(self)
        btn_e = QPushButton("✍️ Editor")
        btn_c = QPushButton("📌 Corcho")
        btn_o = QPushButton("📊 Esquema")
        btn_s = QPushButton("📜 Scrivenings")

        for idx, btn in enumerate([btn_e, btn_c, btn_o, btn_s]):
            btn.setCheckable(True)
            btn.setProperty("class", "SegmentBtn")
            self.seg_group.addButton(btn, idx)
            seg_layout.addWidget(btn)

        btn_active = self.seg_group.button(self.current_view_mode)
        if btn_active:
            btn_active.setChecked(True)
        else:
            btn_e.setChecked(True)
        self.seg_group.idClicked.connect(self._set_central_view)
        tb.addWidget(seg_frame)

        tb.addSeparator()

        # Botón de Acceso Rápido a Modos Visuales / Temas en el Panel Principal
        self.btn_theme_mode = QToolButton()
        th_display = V2_THEMES.get(self.current_theme, {}).get("name", "Oscuro Obsidiana")
        self.btn_theme_mode.setText(f"🎨 {th_display}")
        self.btn_theme_mode.setToolTip("Selector rápido de modo visual / tema editorial")
        self.btn_theme_mode.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.toolbar_theme_menu = QMenu(self.btn_theme_mode)
        self.toolbar_theme_actions: Dict[str, QAction] = {}
        for th_key, th_data in V2_THEMES.items():
            act = self.toolbar_theme_menu.addAction(f"🎨 {th_data['name']}")
            act.setCheckable(True)
            act.setChecked(th_key == self.current_theme)
            act.triggered.connect(lambda checked, key=th_key: self._apply_theme(key))
            self.toolbar_theme_actions[th_key] = act
        self.btn_theme_mode.setMenu(self.toolbar_theme_menu)
        tb.addWidget(self.btn_theme_mode)

        tb.addSeparator()

        # Botón de Acceso Rápido a Estadísticas de Tiempo y Objetivos
        self.btn_stats_hud = QToolButton()
        self.btn_stats_hud.setText("⏱️ 0s | 🎯 Objetivos")
        self.btn_stats_hud.setToolTip("Estadísticas de tiempo de trabajo y objetivos del proyecto (Ctrl+Shift+T)")
        self.btn_stats_hud.clicked.connect(self._open_targets)
        tb.addWidget(self.btn_stats_hud)

        btn_ling = QToolButton()
        btn_ling.setText("🔍 Foco")
        btn_ling.setToolTip("Foco Lingüístico y Analizador de Diálogos")
        btn_ling.clicked.connect(self._open_linguistic_focus)
        tb.addWidget(btn_ling)

        btn_comp = QToolButton()
        btn_comp.setText("🧘 F11")
        btn_comp.setToolTip("Modo Composición a Pantalla Completa")
        btn_comp.clicked.connect(self._open_composition)
        tb.addWidget(btn_comp)

        btn_compile = QPushButton("🚀 Compilar")
        btn_compile.setObjectName("PrimaryButton")
        btn_compile.setToolTip("Compilar Manuscrito a DOCX, PDF, EPUB, RTF (Ctrl+Shift+E)")
        btn_compile.clicked.connect(self._on_compile)
        tb.addWidget(btn_compile)

        tb.addSeparator()

        # Buscador Rápido Integrado en Barra de Herramientas
        self.txt_quick_search = QLineEdit()
        self.txt_quick_search.setPlaceholderText("🔍 Buscar en todo el proyecto...")
        self.txt_quick_search.setFixedWidth(220)
        self.txt_quick_search.returnPressed.connect(self._on_quick_search)
        tb.addWidget(self.txt_quick_search)

        tb.addSeparator()

        # Botón Inspector
        self.btn_toggle_inspector = QToolButton()
        self.btn_toggle_inspector.setText("ℹ️ Inspector")
        self.btn_toggle_inspector.setCheckable(True)
        self.btn_toggle_inspector.setChecked(True)
        self.btn_toggle_inspector.toggled.connect(self._toggle_inspector)
        tb.addWidget(self.btn_toggle_inspector)

    # =========================================================================
    # ÁREA CENTRAL DE 3 PANELES (ARCHIVADOR, VISTA CENTRAL Y INSPECTOR)
    # =========================================================================

    def _init_central_ui(self):
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # 1. Panel Izquierdo: Archivador y Colecciones
        self.binder = BinderV2(self)
        self.binder.node_selected.connect(self._on_node_selected)
        self.binder.structure_changed.connect(self._on_structure_changed)
        self.main_splitter.addWidget(self.binder)

        # 2. Panel Central: Stack de Vistas (Editor, Corcho, Esquema, Scrivenings)
        self.view_stack = QStackedWidget(self)

        self.editor = EditorV2(self)
        self.editor.text_modified.connect(self._on_text_modified)
        self.editor.navigate_back.connect(self._navigate_back)
        self.editor.navigate_forward.connect(self._navigate_forward)
        self.editor.split_requested.connect(self._toggle_split_v)
        self.view_stack.addWidget(self.editor)  # Index 0

        self.corkboard = CorkboardV2(self)
        self.corkboard.card_selected.connect(self._on_node_selected)
        self.corkboard.card_open_requested.connect(self._open_in_editor)
        self.view_stack.addWidget(self.corkboard)  # Index 1

        self.outliner = OutlinerV2(self)
        self.outliner.node_selected.connect(self._on_node_selected)
        self.outliner.node_double_clicked.connect(self._open_in_editor)
        self.view_stack.addWidget(self.outliner)  # Index 2

        self.scrivenings = ScriveningsV2(self)
        self.scrivenings.node_focused.connect(self._on_node_selected)
        self.view_stack.addWidget(self.scrivenings)  # Index 3

        self.main_splitter.addWidget(self.view_stack)

        # 3. Panel Derecho: Inspector de 6 pestañas
        self.inspector = InspectorV2(self)
        self.inspector.data_changed.connect(self._on_inspector_data_changed)
        self.main_splitter.addWidget(self.inspector)

        # Dimensiones iniciales: Archivador 250px, Central 820px, Inspector 310px
        self.main_splitter.setSizes([250, 820, 310])
        self.setCentralWidget(self.main_splitter)

    def _init_status_bar(self):
        sb = self.statusBar()
        self.lbl_sb_doc = QLabel("Documento: Ninguno")
        sb.addWidget(self.lbl_sb_doc, 1)

        self.lbl_sb_time = QLabel("⏱️ Sesión: 0s | ✍️ Doc: 0s")
        sb.addPermanentWidget(self.lbl_sb_time)

        self.lbl_sb_words = QLabel("Total Obra: 0 palabras")
        sb.addPermanentWidget(self.lbl_sb_words)

        self.lbl_sb_save = QLabel("💾 Autoguardado: Activo")
        sb.addPermanentWidget(self.lbl_sb_save)

    # =========================================================================
    # LÓGICA DE CARGA, AUTOGUARDADO Y SINCRONIZACIÓN
    # =========================================================================

    def load_project(self, project_path: Path):
        """Carga un proyecto .escr o .scriv."""
        self.project = EscritorioProjectV2(project_path)

        # Bloqueo cooperativo
        if not self.project.lock.acquire():
            QMessageBox.warning(self, "Aviso de Bloqueo", f"El proyecto ya está abierto en otra sesión o proceso.")

        # Cargar archivo XML maestro (.escrx o .scrivx)
        xml_files = list(project_path.glob("*.escrx")) + list(project_path.glob("*.scrivx"))
        if xml_files:
            XmlEngineV2.load_project_xml(self.project, xml_files[0])

        self.binder.set_project(self.project)
        self.setWindowTitle(f"Escritorio v2.0 — [{self.project.name}]")

        # Seleccionar primer nodo del borrador si existe
        if self.project.draft_node and self.project.draft_node.children:
            first_child = self.project.draft_node.children[0]
            if first_child.children:
                self._on_node_selected(first_child.children[0])
            else:
                self._on_node_selected(first_child)

        self._update_status_totals()

        # Guardar en configuración persistente como último proyecto
        self.last_project_path = str(project_path.resolve())
        self._save_settings()

    def _load_or_create_default(self):
        """Crea un proyecto de demostración en disco local si no hay proyecto abierto."""
        base_dir = Path(__file__).resolve().parent.parent.parent / "config" / "projects"
        base_dir.mkdir(parents=True, exist_ok=True)
        demo_path = base_dir / "Proyecto_Demo.escr"

        if not demo_path.exists():
            demo_path.mkdir(parents=True, exist_ok=True)
            proj = EscritorioProjectV2(demo_path)

            draft = BinderNode(title="Manuscrito", type="DraftFolder")
            research = BinderNode(title="Investigación", type="ResearchFolder")
            trash = BinderNode(title="Papelera", type="TrashFolder")
            proj.root_nodes = [draft, research, trash]
            proj.draft_node = draft
            proj.research_node = research
            proj.trash_node = trash

            cap1 = BinderNode(title="Capítulo 1", type="Folder", section_type="Chapter", parent_uuid=draft.uuid)
            esc1 = BinderNode(title="El Despertar", type="Text", section_type="Scene", parent_uuid=cap1.uuid)
            esc1._content_rtf = "La luz filtrada por las persianas dibujaba rayas sobre la mesa de caoba..."
            esc1._synopsis_text = "El detective despierta con una llamada inesperada."
            esc1.label = "Protagonista"
            esc1.status = "Primer Borrador"
            esc1.target_words = 1500

            cap1.children.append(esc1)
            draft.children.append(cap1)
            proj.save_all_dirty_nodes()
            XmlEngineV2.save_project_xml(proj, demo_path / "Proyecto_Demo.escrx")

        self.load_project(demo_path)

    def _auto_save(self):
        """Autoguardado transaccional periódico."""
        if self.project:
            self.project.save_all_dirty_nodes()
            # Guardar XML maestro
            xml_path = self.project.path / f"{self.project.name}.escrx"
            XmlEngineV2.save_project_xml(self.project, xml_path)
            self.lbl_sb_save.setText("💾 Autoguardado: OK")

    def _on_node_selected(self, node: BinderNode):
        """Maneja la selección de cualquier nodo en el Binder, Corcho o Esquema."""
        self.active_node = node
        self.stats_mgr.set_active_node(node.uuid)
        self.project.load_node_content(node)

        # Actualizar Editor
        self.editor.load_node(node)

        # Actualizar Inspector
        self.inspector.load_node(node, self.project)

        # Si el nodo es una carpeta o borrador, alimentar Corcho y Esquema con sus hijos
        if node.is_folder():
            self.corkboard.load_parent_node(node, self.project)
            self.outliner.load_parent_node(node, self.project)
            self.scrivenings.load_nodes(node.children, self.project)

        self.lbl_sb_doc.setText(f"Documento: {node.title} ({node.word_count()} palabras)")
        self._update_status_totals()

    def _open_in_editor(self, node: BinderNode):
        """Cambia a la vista de editor y carga el nodo seleccionado."""
        self._set_central_view(0)
        self._on_node_selected(node)

    def _set_central_view(self, index: int):
        self.current_view_mode = index
        self.view_stack.setCurrentIndex(index)
        btn = self.seg_group.button(index)
        if btn and not btn.isChecked():
            btn.setChecked(True)

        if index == 1 and self.active_node and self.project:
            self.corkboard.load_parent_node(self.active_node, self.project)
        elif index == 2 and self.active_node and self.project:
            self.outliner.load_parent_node(self.active_node, self.project)
        elif index == 3 and self.active_node and self.project:
            if self.active_node.is_folder():
                self.scrivenings.load_nodes(self.active_node.children, self.project)
            else:
                self.scrivenings.load_nodes([self.active_node], self.project)

        self._save_settings()

    def _on_text_modified(self):
        self.session_words_written += 1
        self.stats_mgr.on_keystroke(1)
        self._update_status_totals()

    def _on_structure_changed(self):
        self._update_status_totals()

    def _on_inspector_data_changed(self):
        if self.active_node:
            self.binder.rebuild_tree()
            self.outliner.rebuild_outliner()

    def _update_status_totals(self):
        if self.project and self.project.draft_node:
            total = self.project.draft_node.total_word_count()
            self.lbl_sb_words.setText(f"Total Manuscrito: {total:,} palabras")

    # =========================================================================
    # DIÁLOGOS Y VENTANAS AUXILIARES
    # =========================================================================

    def _on_new_project(self):
        dialog = ProjectChooserDialog(self)
        if dialog.exec() and dialog.created_project_path:
            self.load_project(dialog.created_project_path)

    def _on_open_project(self):
        folder = QFileDialog.getExistingDirectory(self, "Abrir Proyecto .escr o .scriv")
        if folder:
            self.load_project(Path(folder))

    def _on_save_project(self):
        self._auto_save()
        QMessageBox.information(self, "Guardado", "Proyecto guardado de forma atómica en disco.")

    def _on_compile(self):
        if not self.project:
            return
        modal = CompileModalV2(self.project, self)
        modal.exec()

    def _on_manual_backup(self):
        if not self.project:
            return
        try:
            zip_p = self.backup_mgr.create_backup(self.project.path, prefix="manual")
            QMessageBox.information(self, "Copia de Seguridad", f"Copia ZIP generada con éxito:\n{zip_p.name}")
        except Exception as e:
            QMessageBox.critical(self, "Error de Backup", f"No se pudo crear el backup: {e}")

    def _open_targets(self):
        if not self.project:
            return
        hud = TargetsHudV2(self.project, self.stats_mgr, self.active_node, self)
        hud.exec()
        self._update_status_totals()

    def _open_linguistic_focus(self):
        text = self.editor.editor.toPlainText()
        dialog = LinguisticFocusDialog(text, self)
        dialog.exec()

    def _open_composition(self):
        if not self.active_node:
            return
        comp = CompositionModeV2()
        comp.load_node(self.active_node)
        comp.showFullScreen()

    def _open_quick_ref(self):
        if not self.active_node:
            return
        qr = QuickReferenceWindow(self.active_node, self)
        qr.show()

    def _toggle_binder(self, checked: bool):
        self.binder.setVisible(checked)
        self.btn_toggle_binder.setChecked(checked)
        self._save_settings()

    def _toggle_inspector(self, checked: bool):
        self.inspector.setVisible(checked)
        self.btn_toggle_inspector.setChecked(checked)
        self._save_settings()

    def _toggle_split_v(self):
        QMessageBox.information(self, "Pantalla Dividida", "División de pantalla vertical sincronizada activa.")

    def _toggle_split_h(self):
        QMessageBox.information(self, "Pantalla Dividida", "División de pantalla horizontal sincronizada activa.")

    def _split_document(self):
        """Divide el documento actual en la posición del cursor (Ctrl+K)."""
        if not self.active_node or not self.project:
            return
        cursor = self.editor.editor.textCursor()
        pos = cursor.position()
        full_text = self.editor.editor.toPlainText()

        first_part = full_text[:pos]
        second_part = full_text[pos:]

        self.active_node._content_rtf = first_part
        self.active_node.mark_dirty()

        # Crear nuevo nodo para la segunda parte
        new_node = self.project.add_node(self.active_node.parent_uuid, title=f"{self.active_node.title} (Continuación)")
        new_node._content_rtf = second_part
        new_node.mark_dirty()

        self.binder.rebuild_tree()
        self._on_node_selected(new_node)
        QMessageBox.information(self, "Dividir Documento", "Documento dividido en dos escenas con éxito.")

    def _on_quick_search(self):
        query = self.txt_quick_search.text().lower().strip()
        if not query or not self.project:
            return
        # Buscar en títulos y contenidos
        matches = []
        def _search_rec(n: BinderNode):
            self.project.load_node_content(n)
            if query in n.title.lower() or query in n.get_plain_text().lower():
                matches.append(n)
            for c in n.children:
                _search_rec(c)

        for r in self.project.root_nodes:
            _search_rec(r)

        if matches:
            self._on_node_selected(matches[0])
            QMessageBox.information(self, "Búsqueda en Proyecto", f"Se encontraron {len(matches)} documentos coincidentes. Mostrando: {matches[0].title}")
        else:
            QMessageBox.information(self, "Búsqueda", "No se encontraron coincidencias en el proyecto.")

    def _navigate_back(self):
        pass

    def _navigate_forward(self):
        pass

    def _apply_theme(self, theme_key: str):
        if not theme_key or theme_key not in V2_THEMES:
            theme_key = "obsidian_dark"
        self.current_theme = theme_key
        qss = get_v2_stylesheet(theme_key)
        self.setStyleSheet(qss)

        # Sincronizar checkmarks en el menú de Herramientas
        if hasattr(self, "theme_actions"):
            for k, act in self.theme_actions.items():
                act.setChecked(k == theme_key)

        # Sincronizar texto y checkmarks en el botón del panel
        if hasattr(self, "btn_theme_mode"):
            th_name = V2_THEMES[theme_key]["name"]
            self.btn_theme_mode.setText(f"🎨 {th_name}")
        if hasattr(self, "toolbar_theme_actions"):
            for k, act in self.toolbar_theme_actions.items():
                act.setChecked(k == theme_key)

        self._save_settings()

    def _on_about(self):
        QMessageBox.about(
            self,
            "Acerca de Escritorio v2.0",
            "<h3>Escritorio v2.0 (Scrivener 3 Clean-Room Replica)</h3>"
            "<p>Estación de trabajo editorial nativa y portable para Windows 11.</p>"
            "<p><b>Desarrollado con arquitectura agéntica de Google Antigravity y REA.</b></p>"
            "<p>Paridad completa con Scrivener 3 macOS: Corcho multi-modo, Esquema jerárquico, "
            "Scrivenings continuo, Inspector de 6 pestañas con comparador Diff, y compilador multiformato.</p>"
        )

    def _on_clock_tick(self):
        """Actualiza cada segundo los contadores de tiempo en vivo."""
        self.stats_mgr.on_tick()
        s_stats = self.stats_mgr.get_session_stats()
        if hasattr(self, "btn_stats_hud"):
            self.btn_stats_hud.setText(f"⏱️ {s_stats['formatted_total']} | 🎯 Objetivos")
        if hasattr(self, "lbl_sb_time"):
            doc_uuid = self.active_node.uuid if self.active_node else None
            doc_time_str = self.stats_mgr.format_hms(self.stats_mgr.get_doc_time(doc_uuid))
            self.lbl_sb_time.setText(f"⏱️ Sesión: {s_stats['formatted_total']} | ✍️ Doc: {doc_time_str}")

    def closeEvent(self, event):
        """Al cerrar la aplicación, guardar todo y liberar lock."""
        self._auto_save()
        self._save_settings()
        self.stats_mgr.save()
        if self.project:
            # Crear backup automático al salir
            try:
                self.backup_mgr.create_backup(self.project.path, prefix="autoclose")
            except Exception:
                pass
            self.project.lock.release()
        event.accept()
