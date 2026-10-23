"""
ESCRITORIO v2.0 - Binder (Archivador) & Collections Engine
Árbol documental jerárquico interactivo con soporte de drag & drop, carpetas especiales,
colecciones dinámicas y coloreado por etiquetas idéntico a Scrivener 3 macOS.
"""

from typing import Optional, List, Dict, Callable
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QPushButton, QMenu, QTabBar, QLabel, QInputDialog,
    QColorDialog, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QColor, QBrush, QAction, QFont

from ..core.project_v2 import EscritorioProjectV2, BinderNode, CollectionItem


class BinderItemWidget(QTreeWidgetItem):
    """Elemento visual personalizado en el árbol de Binder."""

    def __init__(self, node: BinderNode):
        super().__init__()
        self.node = node
        self.setText(0, node.title)
        self.setData(0, Qt.ItemDataRole.UserRole, node.uuid)
        self._update_visuals()

    def _update_visuals(self):
        """Actualiza icono, color de etiqueta y tipografía según el tipo de nodo."""
        # Icono según tipo de nodo
        if self.node.type == "DraftFolder":
            self.setText(0, f"📘 {self.node.title}")
            font = self.font(0)
            font.setBold(True)
            self.setFont(0, font)
        elif self.node.type == "ResearchFolder":
            self.setText(0, f"🔬 {self.node.title}")
            font = self.font(0)
            font.setBold(True)
            self.setFont(0, font)
        elif self.node.type == "TrashFolder":
            self.setText(0, f"🗑️ {self.node.title}")
        elif self.node.is_folder():
            self.setText(0, f"📁 {self.node.title}")
        else:
            self.setText(0, f"📄 {self.node.title}")

        # Indicador de etiqueta por color
        if self.node.label and self.node.label != "Sin Etiqueta":
            self.setToolTip(0, f"Etiqueta: {self.node.label} | Estado: {self.node.status} | Palabras: {self.node.word_count()}")


class BinderV2(QWidget):
    """Componente completo del Archivador y Colecciones."""

    node_selected = pyqtSignal(BinderNode)
    node_renamed = pyqtSignal(BinderNode, str)
    structure_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project: Optional[EscritorioProjectV2] = None

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Barra superior con conmutador de pestañas: [ Archivador | Colecciones ]
        self.tab_bar = QTabBar(self)
        self.tab_bar.addTab("Archivador")
        self.tab_bar.addTab("Colecciones")
        self.tab_bar.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self.tab_bar)

        # Caja de búsqueda rápida en el Archivador
        search_box = QHBoxLayout()
        search_box.setContentsMargins(6, 2, 6, 2)
        self.txt_filter = QLineEdit()
        self.txt_filter.setPlaceholderText("🔍 Filtrar manuscrito...")
        self.txt_filter.textChanged.connect(self._filter_tree)
        search_box.addWidget(self.txt_filter)
        layout.addLayout(search_box)

        # Árbol del Binder
        self.tree = QTreeWidget(self)
        self.tree.setHeaderHidden(True)
        self.tree.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._on_context_menu)
        layout.addWidget(self.tree)

        # Lista de Colecciones (oculta por defecto hasta pulsar la pestaña)
        self.collections_tree = QTreeWidget(self)
        self.collections_tree.setHeaderHidden(True)
        self.collections_tree.setVisible(False)
        self.collections_tree.itemSelectionChanged.connect(self._on_collection_selected)
        layout.addWidget(self.collections_tree)

    def set_project(self, project: EscritorioProjectV2):
        """Asigna el proyecto y reconstruye el árbol completo."""
        self.project = project
        self.rebuild_tree()

    def rebuild_tree(self):
        """Reconstruye los elementos visuales del árbol."""
        self.tree.clear()
        if not self.project:
            return

        for node in self.project.root_nodes:
            self._add_node_recursive(self.tree.invisibleRootItem(), node)

        self.tree.expandAll()

    def _add_node_recursive(self, parent_item, node: BinderNode):
        item = BinderItemWidget(node)
        parent_item.addChild(item)
        for child in node.children:
            self._add_node_recursive(item, child)

    def _on_selection_changed(self):
        selected_items = self.tree.selectedItems()
        if selected_items and isinstance(selected_items[0], BinderItemWidget):
            self.node_selected.emit(selected_items[0].node)

    def get_selected_node(self) -> Optional[BinderNode]:
        selected_items = self.tree.selectedItems()
        if selected_items and isinstance(selected_items[0], BinderItemWidget):
            return selected_items[0].node
        return None

    def _on_tab_changed(self, index: int):
        if index == 0:
            self.tree.setVisible(True)
            self.collections_tree.setVisible(False)
        else:
            self.tree.setVisible(False)
            self.collections_tree.setVisible(True)
            self._rebuild_collections()

    def _rebuild_collections(self):
        self.collections_tree.clear()
        if not self.project:
            return

        for col in self.project.collections:
            icon = "🔍" if col.is_search else "🏷️"
            item = QTreeWidgetItem([f"{icon} {col.name} ({len(col.member_uuids)} docs)"])
            item.setData(0, Qt.ItemDataRole.UserRole, col.id)
            self.collections_tree.addTopLevelItem(item)

    def _on_collection_selected(self):
        selected = self.collections_tree.selectedItems()
        if not selected or not self.project:
            return
        col_id = selected[0].data(0, Qt.ItemDataRole.UserRole)
        col = next((c for c in self.project.collections if c.id == col_id), None)
        if col and col.member_uuids:
            first_node = self.project.find_node_by_uuid(col.member_uuids[0])
            if first_node:
                self.node_selected.emit(first_node)

    def _filter_tree(self, text: str):
        text = text.lower().strip()
        iterator = QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            if not text:
                item.setHidden(False)
            else:
                match = text in item.text(0).lower()
                item.setHidden(not match)
                if match:
                    parent = item.parent()
                    while parent:
                        parent.setHidden(False)
                        parent.setExpanded(True)
                        parent = parent.parent()
            iterator += 1

    def _on_context_menu(self, pos: QPoint):
        item = self.tree.itemAt(pos)
        node = item.node if isinstance(item, BinderItemWidget) else None
        menu = QMenu(self)

        act_new_doc = menu.addAction("📄 Nueva Escena (Ctrl+N)")
        act_new_doc.triggered.connect(lambda: self.create_new_node("Text"))

        act_new_fld = menu.addAction("📁 Nueva Carpeta (Ctrl+Alt+N)")
        act_new_fld.triggered.connect(lambda: self.create_new_node("Folder"))

        if node:
            menu.addSeparator()
            act_rename = menu.addAction("✏️ Renombrar...")
            act_rename.triggered.connect(lambda: self._rename_node(node, item))

            act_dup = menu.addAction("📋 Duplicar Escena (Ctrl+D)")
            act_dup.triggered.connect(lambda: self._duplicate_node(node))

            menu.addSeparator()
            # Submenú Etiquetas
            label_menu = menu.addMenu("🏷️ Asignar Etiqueta")
            for lbl in self.project.labels:
                act_lbl = label_menu.addAction(lbl["name"])
                act_lbl.triggered.connect(lambda checked, l=lbl["name"]: self._set_node_label(node, l))

            # Submenú Estados
            status_menu = menu.addMenu("📊 Asignar Estado")
            for st in self.project.statuses:
                act_st = status_menu.addAction(st["name"])
                act_st.triggered.connect(lambda checked, s=st["name"]: self._set_node_status(node, s))

            # Submenú Tipos de Sección
            sec_menu = menu.addMenu("📑 Tipo de Sección")
            for s_type in self.project.section_types:
                act_sec = sec_menu.addAction(s_type)
                act_sec.triggered.connect(lambda checked, t=s_type: self._set_node_section_type(node, t))

            menu.addSeparator()
            act_del = menu.addAction("🗑️ Mover a Papelera (Del)")
            act_del.triggered.connect(lambda: self._delete_node(node))

        menu.exec(self.tree.mapToGlobal(pos))

    def create_new_node(self, node_type: str = "Text"):
        if not self.project:
            return
        selected = self.get_selected_node()
        parent_uuid = selected.uuid if selected and selected.is_folder() else (selected.parent_uuid if selected else (self.project.draft_node.uuid if self.project.draft_node else None))

        title = "Nueva Escena" if node_type == "Text" else "Nuevo Capítulo"
        new_node = self.project.add_node(parent_uuid, title=title, node_type=node_type)
        self.rebuild_tree()
        self.structure_changed.emit()
        self.node_selected.emit(new_node)

    def _rename_node(self, node: BinderNode, item: QTreeWidgetItem):
        new_title, ok = QInputDialog.getText(self, "Renombrar", "Nuevo título:", text=node.title)
        if ok and new_title.strip():
            node.title = new_title.strip()
            node.mark_dirty()
            item._update_visuals()
            self.node_renamed.emit(node, node.title)

    def _duplicate_node(self, node: BinderNode):
        if not self.project:
            return
        self.project.load_node_content(node)
        dup = self.project.add_node(node.parent_uuid, title=f"{node.title} (Copia)", node_type=node.type)
        dup._content_rtf = node._content_rtf
        dup._synopsis_text = node._synopsis_text
        dup._notes_rtf = node._notes_rtf
        dup.label = node.label
        dup.status = node.status
        dup.section_type = node.section_type
        dup.mark_dirty()
        self.rebuild_tree()
        self.structure_changed.emit()

    def _set_node_label(self, node: BinderNode, label_name: str):
        node.label = label_name
        node.mark_dirty()
        self.rebuild_tree()

    def _set_node_status(self, node: BinderNode, status_name: str):
        node.status = status_name
        node.mark_dirty()
        self.rebuild_tree()

    def _set_node_section_type(self, node: BinderNode, sec_type: str):
        node.section_type = sec_type
        node.mark_dirty()

    def _delete_node(self, node: BinderNode):
        if not self.project:
            return
        if self.project.move_to_trash(node.uuid):
            self.rebuild_tree()
            self.structure_changed.emit()


from PyQt6.QtWidgets import QTreeWidgetItemIterator
