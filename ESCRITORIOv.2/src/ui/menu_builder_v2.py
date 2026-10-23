"""
ESCRITORIO v2.0 - Menu Builder (Complete Scrivener 3 Windows 11 Tree)
Construcción exhaustiva y fiel al 100% del árbol de menús según las
páginas 7, 8 y 9 del documento ESCRITORIO-especificacion.pdf:
1. Archivo
2. Editar
3. Ver
4. Navegar
5. Proyecto
6. Documentos
7. Formato
8. Ventana
9. Ayuda
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Callable

from PyQt6.QtWidgets import (
    QMenuBar, QMenu, QMessageBox, QFileDialog, QInputDialog,
    QColorDialog, QFontDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence, QFont, QTextCursor

from .theme_v2 import V2_THEMES


class MenuBuilderV2:
    """Constructor y orquestador maestro de la barra de menús de ESCRITORIO v2.0."""

    @classmethod
    def build(cls, shell) -> List[QAction]:
        """Construye todos los menús en la ventana shell y devuelve la lista de todas las acciones."""
        mb = shell.menuBar()
        mb.clear()
        all_actions: List[QAction] = []

        cls._build_archivo_menu(shell, mb, all_actions)
        cls._build_editar_menu(shell, mb, all_actions)
        cls._build_ver_menu(shell, mb, all_actions)
        cls._build_navegar_menu(shell, mb, all_actions)
        cls._build_proyecto_menu(shell, mb, all_actions)
        cls._build_documentos_menu(shell, mb, all_actions)
        cls._build_formato_menu(shell, mb, all_actions)
        cls._build_ventana_menu(shell, mb, all_actions)
        cls._build_ayuda_menu(shell, mb, all_actions)

        shell.all_menu_actions = all_actions
        return all_actions

    @staticmethod
    def _add_action(
        menu: QMenu,
        text: str,
        slot: Optional[Callable],
        shortcut: Optional[str] = None,
        all_actions: Optional[List[QAction]] = None,
        checkable: bool = False,
        checked: bool = False
    ) -> QAction:
        act = menu.addAction(text)
        if shortcut:
            act.setShortcut(QKeySequence(shortcut) if isinstance(shortcut, str) else shortcut)
        if slot:
            act.triggered.connect(slot)
        if checkable:
            act.setCheckable(True)
            act.setChecked(checked)
        if all_actions is not None:
            all_actions.append(act)
        return act

    # =========================================================================
    # 1. MENÚ ARCHIVO (Página 7)
    # =========================================================================
    @classmethod
    def _build_archivo_menu(cls, s, mb: QMenuBar, all_actions: List[QAction]):
        m = mb.addMenu("&Archivo")

        cls._add_action(m, "Nuevo proyecto…", s._on_new_project, "Ctrl+Shift+N", all_actions)
        cls._add_action(m, "Abrir…", s._on_open_project, "Ctrl+O", all_actions)

        # Proyectos recientes ▶
        m_recents = m.addMenu("Proyectos recientes")
        cls._populate_recent_projects(s, m_recents, all_actions)

        # Proyectos favoritos ▶
        m_favs = m.addMenu("Proyectos favoritos")
        cls._populate_favorite_projects(s, m_favs, all_actions)

        m.addSeparator()
        cls._add_action(m, "Mostrar proyecto en Explorador", s._show_in_explorer, None, all_actions)
        cls._add_action(m, "Cerrar proyecto / todos", s._close_project, None, all_actions)
        cls._add_action(m, "Guardar", s._on_save_project, "Ctrl+S", all_actions)
        cls._add_action(m, "Guardar como…", s._on_save_as_project, "Ctrl+Shift+S", all_actions)
        cls._add_action(m, "Guardar y reconstruir índices", s._save_and_rebuild_indexes, None, all_actions)

        m.addSeparator()

        # Importar ▶
        m_imp = m.addMenu("Importar")
        cls._add_action(m_imp, "Archivos…", s._import_files, None, all_actions)
        cls._add_action(m_imp, "Página web…", s._import_web_page, None, all_actions)
        cls._add_action(m_imp, "Recursos como alias…", s._import_alias, None, all_actions)
        cls._add_action(m_imp, "Guion de texto plano…", s._import_script, None, all_actions)
        cls._add_action(m_imp, "Proyecto…", s._import_project, None, all_actions)
        cls._add_action(m_imp, "Importar y dividir…", s._import_and_split, None, all_actions)

        # Exportar ▶
        m_exp = m.addMenu("Exportar")
        cls._add_action(m_exp, "Archivos…", s._export_files, None, all_actions)
        cls._add_action(m_exp, "OPML…", s._export_opml, None, all_actions)
        cls._add_action(m_exp, "Esquema como CSV…", s._export_csv, None, all_actions)
        cls._add_action(m_exp, "Comentarios y anotaciones…", s._export_comments, None, all_actions)
        cls._add_action(m_exp, "Proyecto compatible…", s._export_compatible, None, all_actions)

        # Sincronizar ▶
        m_sync = m.addMenu("Sincronizar")
        cls._add_action(m_sync, "Con carpeta externa…", s._open_external_sync, None, all_actions)
        cls._add_action(m_sync, "Con dispositivo móvil…", s._open_mobile_sync, None, all_actions)
        cls._add_action(m_sync, "Sincronizar ahora", s._run_sync_now, "Ctrl+Shift+K", all_actions)

        # Copia de seguridad ▶
        m_bak = m.addMenu("Copia de seguridad")
        cls._add_action(m_bak, "Crear en…", s._backup_to, None, all_actions)
        cls._add_action(m_bak, "Crear ahora", s._on_manual_backup, None, all_actions)
        cls._add_action(m_bak, "Crear de todos", s._backup_all, None, all_actions)
        cls._add_action(m_bak, "Abrir carpeta de copias", s._open_backups_folder, None, all_actions)

        m.addSeparator()
        cls._add_action(m, "Guardar como plantilla…", s._save_as_template, None, all_actions)
        cls._add_action(m, "Configurar página…", s._page_setup, None, all_actions)
        cls._add_action(m, "Imprimir documento actual…", s._print_document, "Ctrl+P", all_actions)
        cls._add_action(m, "Compilar…", s._on_compile, "Ctrl+Shift+E", all_actions)
        m.addSeparator()
        cls._add_action(m, "Salir", s.close, "Ctrl+Q", all_actions)

    @staticmethod
    def _populate_recent_projects(s, menu: QMenu, all_actions: List[QAction]):
        menu.clear()
        recents = s.settings.get("recent_projects", [])
        if recents:
            for p_path in recents:
                p = Path(p_path)
                act = menu.addAction(f"📄 {p.name}")
                act.triggered.connect(lambda checked, path=p_path: s.load_project(Path(path)))
                all_actions.append(act)
            menu.addSeparator()
        act_clear = menu.addAction("Borrar menú")
        act_clear.triggered.connect(s._clear_recent_projects)
        all_actions.append(act_clear)

    @staticmethod
    def _populate_favorite_projects(s, menu: QMenu, all_actions: List[QAction]):
        menu.clear()
        favs = s.settings.get("favorite_projects", [])
        if favs:
            for p_path in favs:
                p = Path(p_path)
                act = menu.addAction(f"⭐ {p.name}")
                act.triggered.connect(lambda checked, path=p_path: s.load_project(Path(path)))
                all_actions.append(act)
            menu.addSeparator()
        act_toggle = menu.addAction("Añadir/Quitar actual")
        act_toggle.triggered.connect(s._toggle_favorite_project)
        all_actions.append(act_toggle)

    # =========================================================================
    # 2. MENÚ EDITAR (Páginas 7 y 8)
    # =========================================================================
    @classmethod
    def _build_editar_menu(cls, s, mb: QMenuBar, all_actions: List[QAction]):
        m = mb.addMenu("&Editar")

        cls._add_action(m, "Deshacer", s._undo, "Ctrl+Z", all_actions)
        cls._add_action(m, "Rehacer", s._redo, "Ctrl+Y", all_actions)
        m.addSeparator()
        cls._add_action(m, "Cortar", s._cut, "Ctrl+X", all_actions)
        cls._add_action(m, "Copiar", s._copy, "Ctrl+C", all_actions)
        cls._add_action(m, "Pegar", s._paste, "Ctrl+V", all_actions)

        # Copiar especial ▶
        m_copy_sp = m.addMenu("Copiar especial")
        cls._add_action(m_copy_sp, "Documento como enlace externo", lambda: s._copy_special("link"), None, all_actions)
        cls._add_action(m_copy_sp, "Texto de documentos", lambda: s._copy_special("text"), None, all_actions)
        cls._add_action(m_copy_sp, "Documentos como TOC", lambda: s._copy_special("toc"), None, all_actions)
        cls._add_action(m_copy_sp, "Lista de enlaces estructurada", lambda: s._copy_special("links_list"), None, all_actions)
        cls._add_action(m_copy_sp, "Sin comentarios/notas", lambda: s._copy_special("no_notes"), None, all_actions)
        cls._add_action(m_copy_sp, "Como Markdown", lambda: s._copy_special("markdown"), None, all_actions)
        cls._add_action(m_copy_sp, "Como HTML (completo/básico)", lambda: s._copy_special("html"), None, all_actions)

        cls._add_action(m, "Pegar y adaptar estilo", s._paste_match_style, "Ctrl+Shift+V", all_actions)
        cls._add_action(m, "Pegar texto plano como guion", s._paste_as_script, None, all_actions)
        cls._add_action(m, "Eliminar", s._delete_selection, "Delete", all_actions)

        # Seleccionar ▶
        m_sel = m.addMenu("Seleccionar")
        cls._add_action(m_sel, "Todo / Nada", s._select_all_toggle, "Ctrl+A", all_actions)
        cls._add_action(m_sel, "Palabra / Frase / Párrafo", s._select_word_sentence_para, None, all_actions)
        cls._add_action(m_sel, "Rango / Todo / Siguiente en estilo", s._select_next_in_style, None, all_actions)
        cls._add_action(m_sel, "Formato similar", s._select_similar_format, None, all_actions)
        cls._add_action(m_sel, "Anotación o nota", s._select_annotation_or_note, None, all_actions)
        cls._add_action(m_sel, "Subgrupos", s._select_subgroups, None, all_actions)
        cls._add_action(m_sel, "Con subdocumentos / Incluidos", s._select_with_children, None, all_actions)

        # Completar ▶
        m_comp = m.addMenu("Completar")
        cls._add_action(m_comp, "Palabra", s._autocomplete_word, None, all_actions)
        cls._add_action(m_comp, "Título de documento", s._autocomplete_doc_title, None, all_actions)
        cls._add_action(m_comp, "Añadir a autocompletado", s._add_to_autocomplete, None, all_actions)

        # Mover ▶
        m_mov = m.addMenu("Mover")
        cls._add_action(m_mov, "Arriba", lambda: s._move_item("up"), "Ctrl+Alt+Up", all_actions)
        cls._add_action(m_mov, "Abajo", lambda: s._move_item("down"), "Ctrl+Alt+Down", all_actions)
        cls._add_action(m_mov, "Izquierda", lambda: s._move_item("left"), "Ctrl+Alt+Left", all_actions)
        cls._add_action(m_mov, "Derecha", lambda: s._move_item("right"), "Ctrl+Alt+Right", all_actions)
        cls._add_action(m_mov, "A…", s._move_item_to_dialog, None, all_actions)

        # Insertar ▶
        m_ins = m.addMenu("Insertar")
        cls._add_action(m_ins, "Imagen / Tabla / Regla", s._insert_image_table_ruler, None, all_actions)
        cls._add_action(m_ins, "Enlace / Comentario / Nota", s._insert_link_comment_note, None, all_actions)
        cls._add_action(m_ins, "Anotación en línea", s._insert_inline_annotation, "Ctrl+Shift+A", all_actions)
        cls._add_action(m_ins, "Fecha y hora / Carácter especial", s._insert_datetime_special_char, None, all_actions)
        cls._add_action(m_ins, "Token de compilación", s._insert_compile_token, None, all_actions)

        # Enlace ▶
        m_lnk = m.addMenu("Enlace")
        cls._add_action(m_lnk, "Añadir…", s._add_link, None, all_actions)
        cls._add_action(m_lnk, "Editar…", s._edit_link, None, all_actions)
        cls._add_action(m_lnk, "Quitar", s._remove_link, None, all_actions)
        cls._add_action(m_lnk, "Documento", s._link_to_document, None, all_actions)
        cls._add_action(m_lnk, "Abrir", s._open_link, None, all_actions)

        # Buscar ▶
        m_src = m.addMenu("Buscar")
        cls._add_action(m_src, "Buscar…", s._open_find_dialog, "Ctrl+F", all_actions)
        cls._add_action(m_src, "Siguiente", s._find_next, "F3", all_actions)
        cls._add_action(m_src, "Anterior", s._find_prev, "Shift+F3", all_actions)
        cls._add_action(m_src, "Reemplazar…", s._open_replace_dialog, "Ctrl+H", all_actions)
        cls._add_action(m_src, "Formato…", s._find_by_format, None, all_actions)

        # Transformaciones ▶
        m_trans = m.addMenu("Transformaciones")
        cls._add_action(m_trans, "Caja (Mayúsculas / Minúsculas / Título)", s._transform_case, None, all_actions)
        cls._add_action(m_trans, "Comillas (Tipográficas « » / “ ”)", s._transform_quotes, None, all_actions)
        cls._add_action(m_trans, "Guiones (Convertir a raya em —)", s._transform_dashes, None, all_actions)
        cls._add_action(m_trans, "Espacios (Limpiar espacios dobles)", s._transform_spaces, None, all_actions)

        # Voz ▶
        m_voice = m.addMenu("Voz")
        cls._add_action(m_voice, "Iniciar lectura", s._voice_start, None, all_actions)
        cls._add_action(m_voice, "Detener lectura", s._voice_stop, None, all_actions)
        cls._add_action(m_voice, "Configurar voz", s._voice_config, None, all_actions)

        cls._add_action(m, "Dictado del sistema", s._system_dictation, "Win+H", all_actions)
        cls._add_action(m, "Emoji y símbolos", s._system_emojis, "Win+.", all_actions)

    # =========================================================================
    # 3. MENÚ VER (Página 8)
    # =========================================================================
    @classmethod
    def _build_ver_menu(cls, s, mb: QMenuBar, all_actions: List[QAction]):
        m = mb.addMenu("&Ver")

        # Diseños ▶
        m_layouts = m.addMenu("Diseños")
        cls._add_action(m_layouts, "Guardar diseño actual…", s._save_layout, None, all_actions)
        cls._add_action(m_layouts, "Gestionar diseños…", s._manage_layouts, None, all_actions)
        cls._add_action(m_layouts, "Aplicar predeterminado", s._apply_default_layout, None, all_actions)

        cls._add_action(m, "Archivador", s._toggle_binder, "Ctrl+Shift+B", all_actions, checkable=True, checked=True)
        cls._add_action(m, "Colecciones", s._toggle_collections, "Ctrl+Shift+C", all_actions)
        cls._add_action(m, "Inspector", s._toggle_inspector, "Ctrl+Shift+I", all_actions, checkable=True, checked=True)

        cls._add_action(m, "Barra de formato", s._toggle_format_bar, None, all_actions, checkable=True, checked=True)
        cls._add_action(m, "Regla", s._toggle_ruler, None, all_actions, checkable=True, checked=True)
        cls._add_action(m, "Toolbar (Barra Principal)", s._toggle_toolbar, None, all_actions, checkable=True, checked=True)
        cls._add_action(m, "Pie (Barra de Estado)", s._toggle_footer, None, all_actions, checkable=True, checked=True)

        m.addSeparator()

        # Disposición del editor ▶
        m_split = m.addMenu("Disposición del editor")
        cls._add_action(m_split, "Sin división", s._split_none, None, all_actions)
        cls._add_action(m_split, "Vertical", s._toggle_split_v, "Ctrl+'", all_actions)
        cls._add_action(m_split, "Horizontal", s._toggle_split_h, "Ctrl+Shift+'", all_actions)
        cls._add_action(m_split, "Intercambiar editores", s._swap_splits, None, all_actions)
        cls._add_action(m_split, "Bloquear editor", s._lock_editor, None, all_actions)

        # Editor ▶
        m_ed = m.addMenu("Editor")
        cls._add_action(m_ed, "Documento", lambda: s._set_central_view(0), "Ctrl+1", all_actions)
        cls._add_action(m_ed, "Corcho", lambda: s._set_central_view(1), "Ctrl+2", all_actions)
        cls._add_action(m_ed, "Esquema", lambda: s._set_central_view(2), "Ctrl+3", all_actions)
        cls._add_action(m_ed, "Scrivenings", lambda: s._set_central_view(3), "Ctrl+4", all_actions)
        cls._add_action(m_ed, "Página", s._toggle_page_view, None, all_actions)

        # Copyholders ▶
        m_copyh = m.addMenu("Copyholders")
        cls._add_action(m_copyh, "Mostrar copyholder", s._show_copyholder, None, all_actions)
        cls._add_action(m_copyh, "Ocultar copyholder", s._hide_copyholder, None, all_actions)
        cls._add_action(m_copyh, "Cerrar", s._close_copyholder, None, all_actions)

        # Zoom ▶
        m_zoom = m.addMenu("Zoom")
        for z in [50, 75, 100, 125, 150, 200]:
            cls._add_action(m_zoom, f"{z}%", lambda ch, factor=z: s._set_zoom(factor), None, all_actions)
        cls._add_action(m_zoom, "Ajustar anchura", s._zoom_fit_width, None, all_actions)

        # Opciones de corcho ▶
        m_cork_opt = m.addMenu("Opciones de corcho")
        cls._add_action(m_cork_opt, "Distribución / Tamaño / Relación", s._corkboard_options_grid, None, all_actions)
        cls._add_action(m_cork_opt, "Etiqueta / Estado / Chinchetas", s._corkboard_options_pins, None, all_actions)
        cls._add_action(m_cork_opt, "Números / Keywords", s._corkboard_options_numbers, None, all_actions)
        cls._add_action(m_cork_opt, "Libre (Freeform)", s._corkboard_freeform, None, all_actions)
        cls._add_action(m_cork_opt, "Hilos (Storyboard)", s._corkboard_threads, None, all_actions)

        # Opciones del esquema ▶
        m_out_opt = m.addMenu("Opciones del esquema")
        cls._add_action(m_out_opt, "Columnas / Sinopsis / Totales", s._outliner_options, None, all_actions)

        # Colores de etiqueta en ▶
        m_col = m.addMenu("Colores de etiqueta en")
        cls._add_action(m_col, "Archivador", lambda: s._toggle_label_tint("binder"), None, all_actions)
        cls._add_action(m_col, "Iconos", lambda: s._toggle_label_tint("icons"), None, all_actions)
        cls._add_action(m_col, "Corcho", lambda: s._toggle_label_tint("corkboard"), None, all_actions)
        cls._add_action(m_col, "Esquema", lambda: s._toggle_label_tint("outliner"), None, all_actions)

        cls._add_action(m, "Invisibles / Saltos / Enlaces", s._toggle_invisibles, None, all_actions)
        cls._add_action(m, "Modo de enfoque", s._open_linguistic_focus, None, all_actions)
        cls._add_action(m, "Composición", s._open_composition, "F11", all_actions)
        cls._add_action(m, "Referencia rápida", s._open_quick_ref, "Space", all_actions)
        cls._add_action(m, "Pantalla completa", s._toggle_fullscreen, None, all_actions)

    # =========================================================================
    # 4. MENÚ NAVEGAR (Página 8)
    # =========================================================================
    @classmethod
    def _build_navegar_menu(cls, s, mb: QMenuBar, all_actions: List[QAction]):
        m = mb.addMenu("&Navegar")

        cls._add_action(m, "Atrás", s._nav_back, "Alt+Left", all_actions)
        cls._add_action(m, "Adelante", s._nav_forward, "Alt+Right", all_actions)
        cls._add_action(m, "Documento anterior", s._nav_prev_doc, "Ctrl+Up", all_actions)
        cls._add_action(m, "Documento siguiente", s._nav_next_doc, "Ctrl+Down", all_actions)
        cls._add_action(m, "Padre", s._nav_parent, None, all_actions)
        cls._add_action(m, "Primer hijo", s._nav_first_child, None, all_actions)

        # Ir a ▶
        m_goto = m.addMenu("Ir a")
        cls._add_action(m_goto, "Manuscrito", lambda: s._jump_to_special("DraftFolder"), None, all_actions)
        cls._add_action(m_goto, "Investigación", lambda: s._jump_to_special("ResearchFolder"), None, all_actions)
        cls._add_action(m_goto, "Papelera", lambda: s._jump_to_special("TrashFolder"), None, all_actions)
        cls._add_action(m_goto, "Selector de Árbol…", s._nav_jump_tree, "Ctrl+G", all_actions)

        cls._add_action(m, "Revelar en archivador / colección", s._reveal_in_binder, None, all_actions)

        # Abrir ▶
        m_open = m.addMenu("Abrir")
        cls._add_action(m_open, "Editor actual", lambda: s._open_in("current"), None, all_actions)
        cls._add_action(m_open, "Otra división", lambda: s._open_in("other_split"), None, all_actions)
        cls._add_action(m_open, "Copyholder", lambda: s._open_in("copyholder"), None, all_actions)
        cls._add_action(m_open, "Referencia rápida", s._open_quick_ref, None, all_actions)
        cls._add_action(m_open, "Ventana externa", s._open_in_external_window, None, all_actions)

        # Foco ▶
        m_focus = m.addMenu("Foco")
        cls._add_action(m_focus, "Archivador", s._focus_binder, "Alt+Shift+B", all_actions)
        cls._add_action(m_focus, "Editor", s._focus_editor, "Alt+Shift+E", all_actions)
        cls._add_action(m_focus, "Inspector", s._focus_inspector, "Alt+Shift+I", all_actions)
        cls._add_action(m_focus, "Sinopsis", s._focus_synopsis, None, all_actions)
        cls._add_action(m_focus, "Notas", s._focus_notes, None, all_actions)

        cls._add_action(m, "Historial", s._show_nav_history, None, all_actions)
        cls._add_action(m, "Favoritos", s._show_nav_favorites, None, all_actions)
        cls._add_action(m, "Siguiente/Anterior comentario, nota, marcador o cambio", s._nav_next_annotation, "Ctrl+Alt+N", all_actions)

    # =========================================================================
    # 5. MENÚ PROYECTO (Página 8)
    # =========================================================================
    @classmethod
    def _build_proyecto_menu(cls, s, mb: QMenuBar, all_actions: List[QAction]):
        m = mb.addMenu("&Proyecto")

        cls._add_action(m, "Nuevo texto", lambda: s.binder.create_new_node("Text"), "Ctrl+N", all_actions)
        cls._add_action(m, "Nueva carpeta", lambda: s.binder.create_new_node("Folder"), "Ctrl+Alt+N", all_actions)

        m_tpl = m.addMenu("Desde plantilla")
        cls._add_action(m_tpl, "Ficha de Personaje", lambda: s._create_from_template("Personaje"), None, all_actions)
        cls._add_action(m_tpl, "Ficha de Localización", lambda: s._create_from_template("Localización"), None, all_actions)
        cls._add_action(m_tpl, "Estructura de Capítulo de 3 Actos", lambda: s._create_from_template("Capitulo3Actos"), None, all_actions)

        m.addSeparator()
        cls._add_action(m, "Búsqueda…", s._open_project_search, "Ctrl+Shift+F", all_actions)
        cls._add_action(m, "Objetivos…", s._open_targets, "Ctrl+Shift+T", all_actions)
        cls._add_action(m, "Estadísticas del proyecto… / del texto…", s._open_project_stats, None, all_actions)
        cls._add_action(m, "Palabras clave…", s._open_keywords_hud, None, all_actions)

        # Metadatos… ▶
        m_meta = m.addMenu("Metadatos…")
        cls._add_action(m_meta, "Etiquetas / Estados / Tipos", lambda: s._open_metadata_dialog(0), None, all_actions)
        cls._add_action(m_meta, "Campos personalizados", lambda: s._open_metadata_dialog(3), None, all_actions)
        cls._add_action(m_meta, "Autocompletado", lambda: s._open_metadata_dialog(4), None, all_actions)

        # Ajustes del proyecto… ▶
        m_adj = m.addMenu("Ajustes del proyecto…")
        cls._add_action(m_adj, "General / Formato / Imágenes", s._open_project_settings, None, all_actions)
        cls._add_action(m_adj, "Guion / Compartir / Backup", s._open_project_settings_backup, None, all_actions)

        # Colecciones ▶
        m_col = m.addMenu("Colecciones")
        cls._add_action(m_col, "Crear colección", s._create_collection, None, all_actions)
        cls._add_action(m_col, "Crear desde selección", s._create_collection_from_selection, None, all_actions)
        cls._add_action(m_col, "Guardar búsqueda como colección", s._save_search_as_collection, None, all_actions)
        cls._add_action(m_col, "Gestionar colecciones", s._manage_collections, None, all_actions)

        # Plantillas ▶
        m_plan = m.addMenu("Plantillas")
        cls._add_action(m_plan, "Establecer carpeta de plantillas…", s._set_templates_folder, None, all_actions)
        cls._add_action(m_plan, "Gestionar plantillas…", s._manage_templates, None, all_actions)

        # Marcadores ▶
        m_bm = m.addMenu("Marcadores")
        cls._add_action(m_bm, "Añadir marcador…", s._add_bookmark, None, all_actions)
        cls._add_action(m_bm, "Gestionar marcadores…", s._manage_bookmarks, None, all_actions)

        cls._add_action(m, "Reemplazos…", s._open_replacements_dialog, None, all_actions)
        cls._add_action(m, "Vaciar papelera…", s._empty_trash, None, all_actions)
        cls._add_action(m, "Verificar/Reparar proyecto…", s._verify_repair_project, None, all_actions)

    # =========================================================================
    # 6. MENÚ DOCUMENTOS (Páginas 8 y 9)
    # =========================================================================
    @classmethod
    def _build_documentos_menu(cls, s, mb: QMenuBar, all_actions: List[QAction]):
        m = mb.addMenu("&Documentos")

        cls._add_action(m, "Abrir / Abrir con…", s._open_doc_with, None, all_actions)

        m_dup = m.addMenu("Duplicar")
        cls._add_action(m_dup, "Con hijos", lambda: s._duplicate_node(with_children=True), None, all_actions)
        cls._add_action(m_dup, "Solo elemento", lambda: s._duplicate_node(with_children=False), None, all_actions)

        cls._add_action(m, "Papelera / Eliminar definitivamente", s._delete_active_doc, "Delete", all_actions)

        # Instantáneas ▶
        m_snap = m.addMenu("Instantáneas")
        cls._add_action(m_snap, "Crear", lambda: s.inspector.take_snapshot(), "Ctrl+5", all_actions)
        cls._add_action(m_snap, "Con título…", s._snapshot_with_title, None, all_actions)
        cls._add_action(m_snap, "En seleccionados", s._snapshot_in_selected, None, all_actions)
        cls._add_action(m_snap, "Mostrar en inspector", s._show_snapshots_in_inspector, None, all_actions)
        cls._add_action(m_snap, "Restaurar / Eliminar / Exportar", s._manage_snapshots, None, all_actions)

        # Dividir ▶
        m_sp = m.addMenu("Dividir")
        cls._add_action(m_sp, "Selección", s._split_document, "Ctrl+K", all_actions)
        cls._add_action(m_sp, "Patrón…", s._split_by_pattern, None, all_actions)
        cls._add_action(m_sp, "Títulos", s._split_by_titles, None, all_actions)

        cls._add_action(m, "Combinar", s._merge_documents, None, all_actions)
        cls._add_action(m, "Mover selección a nuevo documento", s._move_selection_to_new_doc, None, all_actions)

        m_conv = m.addMenu("Convertir")
        cls._add_action(m_conv, "Texto a carpeta", lambda: s._convert_node_type("Folder"), None, all_actions)
        cls._add_action(m_conv, "Carpeta a texto", lambda: s._convert_node_type("Text"), None, all_actions)

        m_ico = m.addMenu("Cambiar icono")
        cls._add_action(m_ico, "Galería…", s._pick_custom_icon, None, all_actions)
        cls._add_action(m_ico, "Restablecer", s._reset_custom_icon, None, all_actions)

        # Tipo de sección ▶
        m_st = m.addMenu("Tipo de sección")
        types = getattr(s.project, "section_types", ["Heading", "Section", "Chapter", "Scene"]) if s.project else []
        for t in types:
            cls._add_action(m_st, t, lambda ch, tp=t: s._set_active_section_type(tp), None, all_actions)

        # Etiqueta ▶
        m_lbl = m.addMenu("Etiqueta")
        if s.project:
            for l in s.project.labels:
                cls._add_action(m_lbl, f"● {l['name']}", lambda ch, name=l['name']: s._set_active_label(name), None, all_actions)
        cls._add_action(m_lbl, "Editar etiquetas…", lambda: s._open_metadata_dialog(0), None, all_actions)

        # Estado ▶
        m_stat = m.addMenu("Estado")
        if s.project:
            for st in s.project.status_list:
                cls._add_action(m_stat, st, lambda ch, status=st: s._set_active_status(status), None, all_actions)
        cls._add_action(m_stat, "Editar estados…", lambda: s._open_metadata_dialog(1), None, all_actions)

        # Palabras clave ▶
        m_kw = m.addMenu("Palabras clave")
        cls._add_action(m_kw, "Añadir…", s._add_keyword_to_doc, None, all_actions)
        cls._add_action(m_kw, "Quitar…", s._remove_keyword_from_doc, None, all_actions)
        cls._add_action(m_kw, "HUD de palabras clave", s._open_keywords_hud, None, all_actions)

        # Añadir a colección ▶
        m_add_col = m.addMenu("Añadir a colección")
        cls._add_action(m_add_col, "Nueva colección…", s._create_collection, None, all_actions)

        cls._add_action(m, "Incluir en compilación / Bloquear", s._toggle_include_in_compile, None, all_actions)
        cls._add_action(m, "Objetivo…", s._set_doc_target, None, all_actions)

        # Ordenar ▶
        m_ord = m.addMenu("Ordenar")
        cls._add_action(m_ord, "Título", lambda: s._sort_children("title"), None, all_actions)
        cls._add_action(m_ord, "Fecha", lambda: s._sort_children("date"), None, all_actions)
        cls._add_action(m_ord, "Dirección (Ascendente/Descendente)", lambda: s._sort_children("reverse"), None, all_actions)

        # Transcribir ▶
        m_transc = m.addMenu("Transcribir")
        cls._add_action(m_transc, "Reproducir/Pausa", s._transcribe_play_pause, None, all_actions)
        cls._add_action(m_transc, "Saltos", s._transcribe_jump, None, all_actions)
        cls._add_action(m_transc, "Velocidad", s._transcribe_speed, None, all_actions)

        cls._add_action(m, "Enlaces, referencias y marcadores", s._show_doc_references, None, all_actions)

    # =========================================================================
    # 7. MENÚ FORMATO (Página 9)
    # =========================================================================
    @classmethod
    def _build_formato_menu(cls, s, mb: QMenuBar, all_actions: List[QAction]):
        m = mb.addMenu("&Formato")

        # Fuente ▶
        m_fnt = m.addMenu("Fuente")
        cls._add_action(m_fnt, "Familia…", s._pick_font_family, None, all_actions)
        cls._add_action(m_fnt, "Tamaño…", s._pick_font_size, None, all_actions)
        cls._add_action(m_fnt, "Aumentar", s._increase_font_size, "Ctrl+Shift+>", all_actions)
        cls._add_action(m_fnt, "Reducir", s._decrease_font_size, "Ctrl+Shift+<", all_actions)
        cls._add_action(m_fnt, "Panel de fuente…", s._open_font_dialog, None, all_actions)

        # Estilo ▶
        m_sty = m.addMenu("Estilo")
        styles = ["Normal", "Encabezado 1", "Encabezado 2", "Cita en Bloque", "Énfasis", "Código"]
        for st in styles:
            cls._add_action(m_sty, st, lambda ch, sn=st: s._apply_named_style(sn), None, all_actions)
        m_sty.addSeparator()
        cls._add_action(m_sty, "Nuevo…", s._create_named_style, None, all_actions)
        cls._add_action(m_sty, "Redefinir", s._redefine_named_style, None, all_actions)
        cls._add_action(m_sty, "Renombrar…", s._rename_named_style, None, all_actions)
        cls._add_action(m_sty, "Eliminar", s._delete_named_style, None, all_actions)

        # Texto ▶
        m_txt = m.addMenu("Texto")
        cls._add_action(m_txt, "Negrita", s._toggle_bold, "Ctrl+B", all_actions)
        cls._add_action(m_txt, "Cursiva", s._toggle_italic, "Ctrl+I", all_actions)
        cls._add_action(m_txt, "Subrayado", s._toggle_underline, "Ctrl+U", all_actions)
        cls._add_action(m_txt, "Tachado", s._toggle_strikethrough, None, all_actions)
        cls._add_action(m_txt, "Color de texto…", s._pick_text_color, None, all_actions)
        cls._add_action(m_txt, "Resaltado…", s._pick_highlight_color, None, all_actions)

        # Línea base ▶
        m_base = m.addMenu("Línea base")
        cls._add_action(m_base, "Superíndice", s._set_superscript, None, all_actions)
        cls._add_action(m_base, "Subíndice", s._set_subscript, None, all_actions)
        cls._add_action(m_base, "Normal", s._set_normal_baseline, None, all_actions)

        # Párrafo ▶
        m_par = m.addMenu("Párrafo")
        cls._add_action(m_par, "Alineación (Izquierda, Centro, Derecha, Justificado)", s._paragraph_align_dialog, None, all_actions)
        cls._add_action(m_par, "Sangrías / Tabuladores…", s._paragraph_indent_dialog, None, all_actions)
        cls._add_action(m_par, "Interlineado / Espaciado…", s._paragraph_spacing_dialog, None, all_actions)
        cls._add_action(m_par, "Mantener con siguiente / líneas juntas", s._paragraph_keep_together, None, all_actions)
        cls._add_action(m_par, "Viudas y huérfanas", s._paragraph_widow_orphan, None, all_actions)

        # Listas ▶
        m_lst = m.addMenu("Listas")
        cls._add_action(m_lst, "Viñetas", s._insert_bullet_list, None, all_actions)
        cls._add_action(m_lst, "Numeración", s._insert_numbered_list, None, all_actions)
        cls._add_action(m_lst, "Nivel (Aumentar / Reducir)", s._change_list_level, None, all_actions)
        cls._add_action(m_lst, "Personalizar…", s._customize_list, None, all_actions)

        # Tablas ▶
        m_tbl = m.addMenu("Tablas")
        cls._add_action(m_tbl, "Insertar…", s._insert_table_dialog, None, all_actions)
        cls._add_action(m_tbl, "Filas (Añadir / Eliminar)", s._table_rows_action, None, all_actions)
        cls._add_action(m_tbl, "Columnas (Añadir / Eliminar)", s._table_cols_action, None, all_actions)
        cls._add_action(m_tbl, "Combinar celdas", s._table_merge_cells, None, all_actions)
        cls._add_action(m_tbl, "Propiedades…", s._table_properties, None, all_actions)

        # Guion ▶
        m_scr = m.addMenu("Guion")
        cls._add_action(m_scr, "Elementos (Encabezado, Acción, Personaje, Diálogo)", s._script_elements, None, all_actions)
        cls._add_action(m_scr, "Opciones…", s._script_options, None, all_actions)
        cls._add_action(m_scr, "Mayúsculas automáticas", s._script_auto_caps, None, all_actions)
        cls._add_action(m_scr, "Numerar escenas", s._script_number_scenes, None, all_actions)

        # Comentario/nota ▶
        m_comm = m.addMenu("Comentario/nota")
        cls._add_action(m_comm, "Convertir", s._convert_comment_note, None, all_actions)
        cls._add_action(m_comm, "Color…", s._comment_color, None, all_actions)
        cls._add_action(m_comm, "Eliminar", s._delete_comment, None, all_actions)

        # Revisión ▶
        m_rev = m.addMenu("Revisión")
        cls._add_action(m_rev, "Nivel-color (1ª Roja, 2ª Azul, 3ª Verde, 4ª Púrpura, 5ª Marrón)", s._revision_level_color, None, all_actions)
        cls._add_action(m_rev, "Siguiente cambio", s._revision_next, None, all_actions)
        cls._add_action(m_rev, "Aceptar cambio", s._revision_accept, None, all_actions)
        cls._add_action(m_rev, "Quitar color", s._revision_remove_color, None, all_actions)

        cls._add_action(m, "Resaltar / Anotación", s._toggle_annotation_highlight, None, all_actions)

        # Formato predeterminado ▶
        m_def = m.addMenu("Formato predeterminado")
        cls._add_action(m_def, "Aplicar", s._apply_default_format, None, all_actions)
        cls._add_action(m_def, "Convertir documentos seleccionados", s._convert_to_default_format, None, all_actions)
        cls._add_action(m_def, "Guardar formato actual como predeterminado", s._save_current_as_default_format, None, all_actions)

        cls._add_action(m, "Panel de formatos", s._toggle_format_panel, None, all_actions)

    # =========================================================================
    # 8. MENÚ VENTANA (Página 9)
    # =========================================================================
    @classmethod
    def _build_ventana_menu(cls, s, mb: QMenuBar, all_actions: List[QAction]):
        m = mb.addMenu("&Ventana")

        cls._add_action(m, "Minimizar", s.showMinimized, None, all_actions)
        cls._add_action(m, "Maximizar / Restaurar", lambda: s.showNormal() if s.isMaximized() else s.showMaximized(), None, all_actions)
        cls._add_action(m, "Proyecto anterior / siguiente", s._cycle_project_windows, None, all_actions)
        cls._add_action(m, "Reunir/Mover ventanas", s._arrange_windows, None, all_actions)

        # Referencias rápidas ▶
        m_qr = m.addMenu("Referencias rápidas")
        cls._add_action(m_qr, "Abrir documento activo en Referencia Rápida", s._open_quick_ref, "Space", all_actions)

        # Paneles ▶
        m_pan = m.addMenu("Paneles")
        cls._add_action(m_pan, "Keywords (Palabras Clave)", s._open_keywords_hud, None, all_actions)
        cls._add_action(m_pan, "Objetivos (Targets & Work Hours)", s._open_targets, "Ctrl+Shift+T", all_actions)
        cls._add_action(m_pan, "Estilos", s._toggle_format_panel, None, all_actions)
        cls._add_action(m_pan, "Scratchpad (Bloc Flotante)", s._open_scratchpad, None, all_actions)

        # Temas Visuales
        m_thm = m.addMenu("🎨 Temas Visuales")
        for th_key, th_data in V2_THEMES.items():
            act = m_thm.addAction(f"🎨 {th_data['name']}")
            act.setCheckable(True)
            act.setChecked(th_key == s.current_theme)
            act.triggered.connect(lambda checked, key=th_key: s._apply_theme(key))
            all_actions.append(act)

        m.addSeparator()
        # [proyectos abiertos]
        cls._add_action(m, f"● {s.project.name if s.project else 'Sin proyecto'}", None, None, all_actions)

    # =========================================================================
    # 9. MENÚ AYUDA (Página 9)
    # =========================================================================
    @classmethod
    def _build_ayuda_menu(cls, s, mb: QMenuBar, all_actions: List[QAction]):
        m = mb.addMenu("A&yuda")

        cls._add_action(m, "Ayuda / Tutorial / Manual / Atajos", s._open_help_guide, "F1", all_actions)
        cls._add_action(m, "Vídeos y recursos", s._open_video_tutorials, None, all_actions)
        cls._add_action(m, "Buscar comando…", s._open_command_palette, "Ctrl+Shift+P", all_actions)
        cls._add_action(m, "Actualizaciones…", s._check_updates, None, all_actions)
        cls._add_action(m, "Diagnóstico / Paquete de soporte", s._generate_diagnostics, None, all_actions)
        cls._add_action(m, "Licencias de terceros", s._open_licenses, None, all_actions)
        m.addSeparator()
        cls._add_action(m, "Acerca de ESCRITORIO", s._on_about, None, all_actions)
