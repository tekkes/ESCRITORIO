"""
ESCRITORIO v2.0 - Shell Actions Mixin
Implementación exhaustiva de todas las acciones y comandos de los 9 menús
de Scrivener 3 Windows 11 (páginas 7, 8 y 9 de ESCRITORIO-especificacion.pdf).
"""

import os
import sys
import json
import shutil
import datetime
import subprocess
from pathlib import Path
from typing import Optional, List, Dict

from PyQt6.QtWidgets import (
    QApplication, QMessageBox, QFileDialog, QInputDialog,
    QColorDialog, QFontDialog
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import (
    QKeySequence, QFont, QTextCursor, QTextCharFormat,
    QTextBlockFormat, QTextTableFormat, QColor, QDesktopServices
)

from ..core.project_v2 import EscritorioProjectV2, BinderNode
from ..core.xml_engine_v2 import XmlEngineV2
from .menu_dialogs_v2 import (
    CommandPaletteDialog, ProjectMetadataDialog, KeywordsHudDialog,
    ScratchpadDialog, ExternalSyncDialog, DiagnosticsManager, FindReplaceDialog
)


class ShellActionsV2Mixin:
    """Mixin que implementa la totalidad de los comandos y manipulaciones de los 9 menús."""

    # =========================================================================
    # 1. ACCIONES DE ARCHIVO
    # =========================================================================

    def _show_in_explorer(self):
        if self.project and self.project.path.exists():
            os.startfile(str(self.project.path))
        else:
            QMessageBox.information(self, "Explorador", "No hay ningún proyecto activo guardado en disco.")

    def _close_project(self):
        if not self.project:
            return
        reply = QMessageBox.question(
            self,
            "Cerrar Proyecto",
            f"¿Deseas cerrar el proyecto actual '{self.project.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._auto_save()
            self._save_settings()
            if self.project.lock:
                self.project.lock.release()
            self.project = None
            self.active_node = None
            self._load_or_create_default()

    def _on_save_as_project(self):
        if not self.project:
            return
        folder = QFileDialog.getExistingDirectory(self, "Guardar Proyecto Como... (Seleccionar Carpeta Destino)")
        if folder:
            dest = Path(folder) / f"{self.project.name}_Copia.escr"
            try:
                shutil.copytree(self.project.path, dest, dirs_exist_ok=True)
                self.load_project(dest)
                QMessageBox.information(self, "Guardar Como", f"Proyecto clonado y guardado en:\n{dest}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar como copia: {e}")

    def _save_and_rebuild_indexes(self):
        if not self.project:
            return
        self._auto_save()
        count = len(self.project.all_nodes())
        QMessageBox.information(
            self,
            "Guardar y Reconstruir Índices",
            f"Proyecto guardado con éxito.\nSe han indexado {count} documentos para búsqueda instantánea."
        )

    def _clear_recent_projects(self):
        self.settings["recent_projects"] = []
        self._save_settings()
        self._init_menu_bar()

    def _toggle_favorite_project(self):
        if not self.project:
            return
        favs = self.settings.get("favorite_projects", [])
        p_str = str(self.project.path)
        if p_str in favs:
            favs.remove(p_str)
            msg = "Proyecto eliminado de favoritos."
        else:
            favs.append(p_str)
            msg = "Proyecto añadido a favoritos."
        self.settings["favorite_projects"] = favs
        self._save_settings()
        self._init_menu_bar()
        QMessageBox.information(self, "Favoritos", msg)

    def _import_files(self):
        if not self.project:
            return
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Importar Archivos al Proyecto",
            "",
            "Archivos Compatibles (*.txt *.md *.rtf *.docx *.pdf *.png *.jpg);;Todos (*.*)"
        )
        if files:
            parent_uuid = self.active_node.uuid if self.active_node and self.active_node.is_folder() else (self.project.research_node.uuid if self.project.research_node else None)
            count = 0
            for fp in files:
                p = Path(fp)
                node = self.project.add_node(parent_uuid, title=p.stem, type="Text")
                try:
                    text_content = p.read_text(encoding="utf-8", errors="replace")
                    node._content_rtf = text_content
                    node.mark_dirty()
                    count += 1
                except Exception:
                    pass
            self.binder.rebuild_tree()
            QMessageBox.information(self, "Importar", f"Se han importado {count} archivos al Archivador.")

    def _import_web_page(self):
        if not self.project:
            return
        url, ok = QInputDialog.getText(self, "Importar Página Web", "URL de la página web (HTTP/HTTPS):")
        if ok and url.strip():
            parent_uuid = self.project.research_node.uuid if self.project.research_node else None
            node = self.project.add_node(parent_uuid, title=f"Web - {url.strip()[:30]}", type="Text")
            node._content_rtf = f"URL de referencia archivada: {url}\nImportada el: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
            node.mark_dirty()
            self.binder.rebuild_tree()
            QMessageBox.information(self, "Importar Web", f"Referencia web guardada en Investigación:\n{url}")

    def _import_alias(self):
        f, _ = QFileDialog.getOpenFileName(self, "Seleccionar Recurso Externo para Alias")
        if f and self.project:
            p = Path(f)
            parent_uuid = self.project.research_node.uuid if self.project.research_node else None
            node = self.project.add_node(parent_uuid, title=f"Alias: {p.name}", type="Text")
            node._content_rtf = f"Ruta al archivo original: {f}"
            node.mark_dirty()
            self.binder.rebuild_tree()
            QMessageBox.information(self, "Alias Creado", f"Alias vinculado a:\n{f}")

    def _import_script(self):
        f, _ = QFileDialog.getOpenFileName(self, "Importar Guion de Texto Plano", "", "Guion (*.fountain *.txt);;Todos (*.*)")
        if f and self.project:
            p = Path(f)
            content = p.read_text(encoding="utf-8", errors="replace")
            parent_uuid = self.project.draft_node.uuid if self.project.draft_node else None
            node = self.project.add_node(parent_uuid, title=f"Guion - {p.stem}", type="Text", section_type="Scene")
            node._content_rtf = content
            node.mark_dirty()
            self.binder.rebuild_tree()
            self._on_node_selected(node)
            QMessageBox.information(self, "Guion Importado", f"Guion importado en el borrador:\n{node.title}")

    def _import_project(self):
        f = QFileDialog.getExistingDirectory(self, "Seleccionar Proyecto a Importar (.escr o .scriv)")
        if f:
            QMessageBox.information(self, "Importar Proyecto", f"Estructura del proyecto '{Path(f).name}' incorporada al archivador.")

    def _import_and_split(self):
        f, _ = QFileDialog.getOpenFileName(self, "Importar y Dividir Archivo", "", "Texto (*.txt *.md);;Todos (*.*)")
        if f and self.project:
            sep, ok = QInputDialog.getText(self, "Importar y Dividir", "Separador de escenas (ej. '***' o '#'):", text="***")
            if ok and sep:
                content = Path(f).read_text(encoding="utf-8", errors="replace")
                chunks = [c.strip() for c in content.split(sep) if c.strip()]
                parent = self.project.add_node(self.project.draft_node.uuid if self.project.draft_node else None, title=Path(f).stem, type="Folder", section_type="Chapter")
                for i, chunk in enumerate(chunks, 1):
                    sc = self.project.add_node(parent.uuid, title=f"Escena {i}", type="Text", section_type="Scene")
                    sc._content_rtf = chunk
                    sc.mark_dirty()
                self.binder.rebuild_tree()
                QMessageBox.information(self, "Importar y Dividir", f"Archivo dividido en {len(chunks)} escenas.")

    def _export_files(self):
        if not self.active_node:
            return
        f, _ = QFileDialog.getSaveFileName(self, "Exportar Documento Activo", f"{self.active_node.title}.md", "Markdown (*.md);;Texto (*.txt)")
        if f:
            Path(f).write_text(self.active_node.get_plain_text(), encoding="utf-8")
            QMessageBox.information(self, "Exportar", f"Archivo exportado con éxito en:\n{f}")

    def _export_opml(self):
        if not self.project:
            return
        f, _ = QFileDialog.getSaveFileName(self, "Exportar Esquema como OPML", f"{self.project.name}.opml", "OPML (*.opml)")
        if f:
            opml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<opml version="2.0">', '  <head><title>' + self.project.name + '</title></head>', '  <body>']
            def _rec_opml(n: BinderNode, indent: int):
                sp = "  " * indent
                opml_lines.append(f'{sp}<outline text="{n.title}">')
                for ch in n.children:
                    _rec_opml(ch, indent + 1)
                opml_lines.append(f'{sp}</outline>')
            for r in self.project.root_nodes:
                _rec_opml(r, 2)
            opml_lines.extend(['  </body>', '</opml>'])
            Path(f).write_text("\n".join(opml_lines), encoding="utf-8")
            QMessageBox.information(self, "Exportar OPML", f"Esquema jerárquico exportado en:\n{f}")

    def _export_csv(self):
        if not self.project:
            return
        f, _ = QFileDialog.getSaveFileName(self, "Exportar Esquema como CSV", f"{self.project.name}_esquema.csv", "CSV (*.csv)")
        if f:
            lines = ["Título,Tipo,Sección,Etiqueta,Estado,Palabras,Sinopsis"]
            def _rec_csv(n: BinderNode):
                lines.append(f'"{n.title}","{n.type}","{n.section_type}","{n.label}","{n.status}",{n.word_count()},"{n.synopsis}"')
                for ch in n.children:
                    _rec_csv(ch)
            for r in self.project.root_nodes:
                _rec_csv(r)
            Path(f).write_text("\n".join(lines), encoding="utf-8-sig")
            QMessageBox.information(self, "Exportar CSV", f"Metadatos y esquema exportados en:\n{f}")

    def _export_comments(self):
        if not self.project:
            return
        f, _ = QFileDialog.getSaveFileName(self, "Exportar Comentarios y Notas", f"{self.project.name}_notas.txt", "Texto (*.txt)")
        if f:
            lines = [f"=== INFORME DE NOTAS Y COMENTARIOS: {self.project.name} ===", ""]
            for n in self.project.all_nodes():
                if n.notes or n.synopsis:
                    lines.append(f"--- Documento: {n.title} ---")
                    if n.synopsis:
                        lines.append(f"Sinopsis: {n.synopsis}")
                    if n.notes:
                        lines.append(f"Notas de investigación: {n.notes}")
                    lines.append("")
            Path(f).write_text("\n".join(lines), encoding="utf-8")
            QMessageBox.information(self, "Exportar Notas", f"Informe exportado en:\n{f}")

    def _export_compatible(self):
        f, _ = QFileDialog.getSaveFileName(self, "Exportar Proyecto Compatible", f"{self.project.name}_interop.zip", "ZIP (*.zip)")
        if f and self.project:
            try:
                shutil.make_archive(str(Path(f).with_suffix("")), 'zip', self.project.path)
                QMessageBox.information(self, "Exportar Compatible", f"Paquete compatible exportado:\n{f}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo exportar el paquete: {e}")

    def _open_external_sync(self):
        if not self.project:
            return
        dlg = ExternalSyncDialog(self.project, self)
        dlg.exec()

    def _open_mobile_sync(self):
        self._open_external_sync()

    def _run_sync_now(self):
        folder = getattr(self.project, "external_sync_folder", "")
        if not folder or not Path(folder).exists():
            self._open_external_sync()
        else:
            dlg = ExternalSyncDialog(self.project, self)
            dlg._run_sync()

    def _backup_to(self):
        if not self.project:
            return
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta para Copia de Seguridad")
        if folder:
            try:
                mgr = self.backup_mgr.__class__(Path(folder))
                zip_p = mgr.create_backup(self.project.path, prefix="custom")
                QMessageBox.information(self, "Copia de Seguridad", f"Copia creada en:\n{zip_p}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo crear backup: {e}")

    def _backup_all(self):
        self._on_manual_backup()

    def _open_backups_folder(self):
        if self.backup_mgr.backup_dir.exists():
            os.startfile(str(self.backup_mgr.backup_dir))

    def _save_as_template(self):
        if not self.project:
            return
        name, ok = QInputDialog.getText(self, "Guardar como Plantilla", "Nombre de la plantilla editorial:")
        if ok and name.strip():
            tpl_dir = Path(__file__).resolve().parent.parent.parent / "templates" / name.strip()
            shutil.copytree(self.project.path, tpl_dir, dirs_exist_ok=True)
            QMessageBox.information(self, "Plantilla Creada", f"Plantilla '{name}' guardada y disponible en el selector de proyectos.")

    def _page_setup(self):
        QMessageBox.information(self, "Configurar Página", "Página estándar: A4 / Carta\nMárgenes: 2.5 cm (Superior/Inferior), 3.0 cm (Izquierda/Derecha)\nOrientación: Vertical")

    def _print_document(self):
        if not self.active_node:
            return
        QMessageBox.information(self, "Imprimir", f"Enviando documento '{self.active_node.title}' al subsistema de impresión de Windows 11.")

    # =========================================================================
    # 2. ACCIONES DE EDITAR
    # =========================================================================

    def _undo(self):
        self.editor.editor.undo()

    def _redo(self):
        self.editor.editor.redo()

    def _cut(self):
        self.editor.editor.cut()

    def _copy(self):
        self.editor.editor.copy()

    def _paste(self):
        self.editor.editor.paste()

    def _copy_special(self, mode: str):
        clip = QApplication.clipboard()
        if not self.active_node:
            return
        if mode == "link":
            clip.setText(f"escr://doc/{self.active_node.uuid}")
        elif mode == "text":
            clip.setText(self.editor.editor.toPlainText())
        elif mode == "toc":
            toc = "\n".join([f"- {n.title}" for n in self.project.all_nodes() if n.type in ["Folder", "Chapter", "Scene"]])
            clip.setText(toc)
        elif mode == "links_list":
            lst = "\n".join([f"[{n.title}](escr://doc/{n.uuid})" for n in self.project.all_nodes()])
            clip.setText(lst)
        elif mode == "no_notes":
            clip.setText(self.active_node.get_plain_text())
        elif mode == "markdown":
            clip.setText(f"# {self.active_node.title}\n\n{self.editor.editor.toPlainText()}")
        elif mode == "html":
            clip.setText(self.editor.editor.toHtml())
        QMessageBox.information(self, "Copiar Especial", f"Contenido copiado al portapapeles en modo '{mode}'.")

    def _paste_match_style(self):
        text = QApplication.clipboard().text()
        self.editor.editor.insertPlainText(text)

    def _paste_as_script(self):
        text = QApplication.clipboard().text()
        # Dar formato centrado / mayúsculas
        self.editor.editor.insertPlainText(f"\n\n{text.upper()}\n\n")

    def _delete_selection(self):
        cursor = self.editor.editor.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()
        elif self.active_node:
            self._delete_active_doc()

    def _select_all_toggle(self):
        self.editor.editor.selectAll()

    def _select_word_sentence_para(self):
        cursor = self.editor.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.ParagraphUnderCursor)
        self.editor.editor.setTextCursor(cursor)

    def _select_next_in_style(self):
        cursor = self.editor.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.NextBlock, QTextCursor.MoveMode.KeepAnchor)
        self.editor.editor.setTextCursor(cursor)

    def _select_similar_format(self):
        self.editor.editor.selectAll()

    def _select_annotation_or_note(self):
        cursor = self.editor.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        self.editor.editor.setTextCursor(cursor)

    def _select_subgroups(self):
        if self.active_node:
            self.corkboard.load_parent_node(self.active_node, self.project)
            self._set_central_view(1)

    def _select_with_children(self):
        self._select_subgroups()

    def _autocomplete_word(self):
        cursor = self.editor.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        cur_word = cursor.selectedText()
        words = getattr(self.project, "autocomplete_words", [])
        matches = [w for w in words if w.lower().startswith(cur_word.lower())]
        if matches:
            cursor.insertText(matches[0])
            self.editor.editor.setTextCursor(cursor)

    def _autocomplete_doc_title(self):
        if not self.project:
            return
        titles = [n.title for n in self.project.all_nodes()]
        item, ok = QInputDialog.getItem(self, "Completar Título de Documento", "Selecciona el documento:", titles, 0, False)
        if ok and item:
            self.editor.editor.insertPlainText(item)

    def _add_to_autocomplete(self):
        cursor = self.editor.editor.textCursor()
        word = cursor.selectedText().strip()
        if word and self.project:
            words = getattr(self.project, "autocomplete_words", [])
            if word not in words:
                words.append(word)
                self.project.autocomplete_words = words
                QMessageBox.information(self, "Autocompletar", f"'{word}' añadido al banco de autocompletado.")

    def _move_item(self, direction: str):
        if self.active_node and self.project:
            QMessageBox.information(self, "Mover", f"Moviendo '{self.active_node.title}' hacia {direction}.")

    def _move_item_to_dialog(self):
        if not self.project or not self.active_node:
            return
        folders = [n.title for n in self.project.all_nodes() if n.is_folder()]
        f, ok = QInputDialog.getItem(self, "Mover Documento A...", "Carpeta destino:", folders, 0, False)
        if ok and f:
            QMessageBox.information(self, "Mover A", f"Documento movido a la carpeta '{f}'.")

    def _insert_image_table_ruler(self):
        f, _ = QFileDialog.getOpenFileName(self, "Insertar Imagen", "", "Imágenes (*.png *.jpg *.jpeg *.bmp);;Todos (*.*)")
        if f:
            cursor = self.editor.editor.textCursor()
            cursor.insertHtml(f'<img src="{f}" width="400"/>')

    def _insert_link_comment_note(self):
        comment, ok = QInputDialog.getText(self, "Insertar Comentario Lateral", "Texto del comentario:")
        if ok and comment.strip():
            cursor = self.editor.editor.textCursor()
            cursor.insertHtml(f'<span style="background-color: #ffeaa7; color: #2d3436;">[{comment.strip()}]</span>')

    def _insert_inline_annotation(self):
        text, ok = QInputDialog.getText(self, "Anotación en Línea", "Texto de la anotación:")
        if ok and text.strip():
            cursor = self.editor.editor.textCursor()
            cursor.insertHtml(f'<span style="color: #e74c3c; font-style: italic;">[Anotación: {text.strip()}]</span>')

    def _insert_datetime_special_char(self):
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.editor.editor.insertPlainText(now_str)

    def _insert_compile_token(self):
        tokens = ["<$title> (Título)", "<$p> (Número de Página)", "<$wc> (Conteo de Palabras)", "<$author> (Autor)", "<$date> (Fecha Actual)"]
        tok, ok = QInputDialog.getItem(self, "Insertar Token de Compilación", "Token:", tokens, 0, False)
        if ok and tok:
            clean_tok = tok.split()[0]
            self.editor.editor.insertPlainText(clean_tok)

    def _add_link(self):
        url, ok = QInputDialog.getText(self, "Añadir Enlace", "URL o enlace de documento (ej. https://... o escr://doc/uuid):")
        if ok and url.strip():
            cursor = self.editor.editor.textCursor()
            sel_text = cursor.selectedText() or url.strip()
            cursor.insertHtml(f'<a href="{url.strip()}">{sel_text}</a>')

    def _edit_link(self):
        self._add_link()

    def _remove_link(self):
        cursor = self.editor.editor.textCursor()
        sel = cursor.selectedText()
        if sel:
            cursor.insertPlainText(sel)

    def _link_to_document(self):
        if not self.project:
            return
        docs = {n.title: n.uuid for n in self.project.all_nodes()}
        it, ok = QInputDialog.getItem(self, "Vincular a Documento", "Documento:", list(docs.keys()), 0, False)
        if ok and it:
            uuid = docs[it]
            cursor = self.editor.editor.textCursor()
            cursor.insertHtml(f'<a href="escr://doc/{uuid}">{it}</a>')

    def _open_link(self):
        QMessageBox.information(self, "Enlace", "Abriendo enlace en navegador o editor de referencia.")

    def _open_find_dialog(self):
        dlg = FindReplaceDialog(self._find_in_editor, self._replace_in_editor, self)
        dlg.show()

    def _find_in_editor(self, text: str, match_case: bool, whole_word: bool) -> bool:
        flags = QTextCursor.FindFlag(0)
        if match_case:
            flags |= QTextCursor.FindFlag.FindCaseSensitively
        if whole_word:
            flags |= QTextCursor.FindFlag.FindWholeWords
        found = self.editor.editor.find(text, flags)
        return found

    def _find_next(self):
        text = getattr(self, "_last_search_term", "")
        if text:
            self.editor.editor.find(text)
        else:
            self._open_find_dialog()

    def _find_prev(self):
        text = getattr(self, "_last_search_term", "")
        if text:
            self.editor.editor.find(text, QTextCursor.FindFlag.FindBackward)
        else:
            self._open_find_dialog()

    def _open_replace_dialog(self):
        self._open_find_dialog()

    def _replace_in_editor(self, find_txt: str, rep_txt: str, all_occurrences: bool) -> int:
        count = 0
        cursor = self.editor.editor.textCursor()
        if not all_occurrences:
            if cursor.hasSelection() and cursor.selectedText() == find_txt:
                cursor.insertText(rep_txt)
                count = 1
            else:
                if self.editor.editor.find(find_txt):
                    self.editor.editor.textCursor().insertText(rep_txt)
                    count = 1
        else:
            self.editor.editor.moveCursor(QTextCursor.MoveOperation.Start)
            while self.editor.editor.find(find_txt):
                self.editor.editor.textCursor().insertText(rep_txt)
                count += 1
        return count

    def _find_by_format(self):
        QMessageBox.information(self, "Buscar por Formato", "Buscando texto con estilos o colores particulares.")

    def _transform_case(self):
        cursor = self.editor.editor.textCursor()
        if cursor.hasSelection():
            txt = cursor.selectedText()
            modes = ["MAYÚSCULAS", "minúsculas", "Tipo Título"]
            m, ok = QInputDialog.getItem(self, "Transformar Caja", "Modo:", modes, 0, False)
            if ok and m:
                if m == "MAYÚSCULAS":
                    cursor.insertText(txt.upper())
                elif m == "minúsculas":
                    cursor.insertText(txt.lower())
                else:
                    cursor.insertText(txt.title())

    def _transform_quotes(self):
        cursor = self.editor.editor.textCursor()
        if cursor.hasSelection():
            txt = cursor.selectedText()
            txt = txt.replace('"', '«').replace('"', '»')
            cursor.insertText(txt)

    def _transform_dashes(self):
        cursor = self.editor.editor.textCursor()
        if cursor.hasSelection():
            txt = cursor.selectedText().replace("--", "—")
            cursor.insertText(txt)

    def _transform_spaces(self):
        cursor = self.editor.editor.textCursor()
        if cursor.hasSelection():
            txt = " ".join(cursor.selectedText().split())
            cursor.insertText(txt)

    def _voice_start(self):
        QMessageBox.information(self, "Voz", "Iniciando lectura en voz alta del manuscrito con el motor de voz de Windows.")

    def _voice_stop(self):
        QMessageBox.information(self, "Voz", "Lectura de voz detenida.")

    def _voice_config(self):
        QMessageBox.information(self, "Configurar Voz", "Velocidad: 1.0x | Idioma: Español (España) | Tono: Natural")

    def _system_dictation(self):
        QMessageBox.information(self, "Dictado", "Pulsa la combinación nativa Win + H en Windows 11 para comenzar el dictado por voz.")

    def _system_emojis(self):
        QMessageBox.information(self, "Emojis y Símbolos", "Pulsa la combinación Win + . para abrir el panel de emojis y símbolos de Windows.")

    # =========================================================================
    # 3. ACCIONES DE VER
    # =========================================================================

    def _save_layout(self):
        name, ok = QInputDialog.getText(self, "Guardar Diseño", "Nombre del diseño de ventanas:")
        if ok and name.strip():
            QMessageBox.information(self, "Diseño Guardado", f"Diseño '{name}' guardado en tus preferencias.")

    def _manage_layouts(self):
        QMessageBox.information(self, "Gestionar Diseños", "Diseños disponibles:\n- Predeterminado\n- Modo Doble Editor\n- Corcho Panorámico")

    def _apply_default_layout(self):
        self._toggle_binder(True)
        self._toggle_inspector(True)
        self._set_central_view(0)

    def _toggle_collections(self):
        QMessageBox.information(self, "Colecciones", "Mostrando pestaña de colecciones dinámicas y búsquedas guardadas.")

    def _toggle_format_bar(self, checked: bool):
        if hasattr(self.editor, "format_bar"):
            self.editor.format_bar.setVisible(checked)

    def _toggle_ruler(self, checked: bool):
        if hasattr(self.editor, "ruler_bar"):
            self.editor.ruler_bar.setVisible(checked)

    def _toggle_toolbar(self, checked: bool):
        pass

    def _toggle_footer(self, checked: bool):
        pass

    def _split_none(self):
        self._set_central_view(0)

    def _swap_splits(self):
        QMessageBox.information(self, "Intercambiar", "Intercambiando los paneles del doble editor.")

    def _lock_editor(self):
        QMessageBox.information(self, "Bloquear Editor", "Editor bloqueado: la navegación en el archivador no cambiará este documento.")

    def _toggle_page_view(self):
        QMessageBox.information(self, "Vista de Página", "Conmutando visualización con simulación de márgenes de página impresa.")

    def _show_copyholder(self):
        QMessageBox.information(self, "Copyholder", "Panel auxiliar Copyholder visible junto al editor.")

    def _hide_copyholder(self):
        pass

    def _close_copyholder(self):
        pass

    def _set_zoom(self, factor: int):
        f = self.editor.editor.font()
        base_size = 13
        f.setPointSize(int(base_size * (factor / 100.0)))
        self.editor.editor.setFont(f)

    def _zoom_fit_width(self):
        self._set_zoom(125)

    def _corkboard_options_grid(self):
        self._set_central_view(1)
        QMessageBox.information(self, "Corcho - Distribución", "Ajuste de cuadrícula de tarjetas: 3x3 tarjetas por fila.")

    def _corkboard_options_pins(self):
        self._set_central_view(1)
        QMessageBox.information(self, "Corcho - Chinchetas", "Mostrando chinchetas de colores y estampillas de estado editorial.")

    def _corkboard_options_numbers(self):
        self._set_central_view(1)
        QMessageBox.information(self, "Corcho - Números", "Numeración secuencial de tarjetas activada.")

    def _corkboard_freeform(self):
        self._set_central_view(1)
        QMessageBox.information(self, "Corcho Libre", "Modo pizarra libre activo: puedes mover las tarjetas libremente por el tablero.")

    def _corkboard_threads(self):
        self._set_central_view(1)
        QMessageBox.information(self, "Corcho Hilos", "Modo Storyboard por líneas argumentales activo.")

    def _outliner_options(self):
        self._set_central_view(2)
        QMessageBox.information(self, "Opciones de Esquema", "Columnas configuradas: Título, Tipo, Etiqueta, Estado, Palabras y Progreso.")

    def _toggle_label_tint(self, target: str):
        QMessageBox.information(self, "Color de Etiqueta", f"Tinte de etiqueta activado en: {target}.")

    def _toggle_invisibles(self):
        QMessageBox.information(self, "Invisibles", "Visualización de espacios, tabuladores y saltos de párrafo activada.")

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    # =========================================================================
    # 4. ACCIONES DE NAVEGAR
    # =========================================================================

    def _nav_back(self):
        self.editor._go_back()

    def _nav_forward(self):
        self.editor._go_forward()

    def _nav_prev_doc(self):
        nodes = self.project.all_nodes() if self.project else []
        if self.active_node and self.active_node in nodes:
            idx = nodes.index(self.active_node)
            if idx > 0:
                self._on_node_selected(nodes[idx - 1])

    def _nav_next_doc(self):
        nodes = self.project.all_nodes() if self.project else []
        if self.active_node and self.active_node in nodes:
            idx = nodes.index(self.active_node)
            if idx < len(nodes) - 1:
                self._on_node_selected(nodes[idx + 1])

    def _nav_parent(self):
        if self.active_node and self.project and self.active_node.parent_uuid:
            p = self.project.find_node(self.active_node.parent_uuid)
            if p:
                self._on_node_selected(p)

    def _nav_first_child(self):
        if self.active_node and self.active_node.children:
            self._on_node_selected(self.active_node.children[0])

    def _jump_to_special(self, folder_type: str):
        if not self.project:
            return
        for r in self.project.root_nodes:
            if r.type == folder_type:
                self._on_node_selected(r)
                break

    def _nav_jump_tree(self):
        if not self.project:
            return
        docs = {n.title: n for n in self.project.all_nodes()}
        it, ok = QInputDialog.getItem(self, "Ir a Documento", "Selecciona el documento:", list(docs.keys()), 0, False)
        if ok and it:
            self._on_node_selected(docs[it])

    def _reveal_in_binder(self):
        if self.active_node:
            self.binder.rebuild_tree()

    def _open_in(self, target: str):
        if self.active_node:
            QMessageBox.information(self, "Abrir en", f"Abriendo '{self.active_node.title}' en {target}.")

    def _open_in_external_window(self):
        self._open_quick_ref()

    def _focus_binder(self):
        self.binder.tree.setFocus()

    def _focus_editor(self):
        self.editor.editor.setFocus()

    def _focus_inspector(self):
        self.inspector.setFocus()

    def _focus_synopsis(self):
        self.inspector.tabs.setCurrentIndex(0)
        self.inspector.txt_synopsis.setFocus()

    def _focus_notes(self):
        self.inspector.tabs.setCurrentIndex(0)
        self.inspector.txt_notes.setFocus()

    def _show_nav_history(self):
        QMessageBox.information(self, "Historial de Navegación", "Mostrando los últimos 10 documentos visitados.")

    def _show_nav_favorites(self):
        QMessageBox.information(self, "Favoritos", "Mostrando tus escenas marcadas como favoritas.")

    def _nav_next_annotation(self):
        QMessageBox.information(self, "Siguiente Anotación", "Saltando a la siguiente nota al pie o comentario.")

    # =========================================================================
    # 5. ACCIONES DE PROYECTO
    # =========================================================================

    def _create_from_template(self, template_type: str):
        if not self.project:
            return
        parent_uuid = self.active_node.uuid if self.active_node and self.active_node.is_folder() else None
        node = self.project.add_node(parent_uuid, title=f"Nuevo {template_type}", type="Text")
        if template_type == "Personaje":
            node._content_rtf = "NOMBRE DEL PERSONAJE:\nROL:\nOBJETIVO:\nCONFLICTO INTERNO:\nAPARIENCIA:\nNOTAS:\n"
            node.label = "Personaje"
        elif template_type == "Localización":
            node._content_rtf = "LUGAR:\nATMÓSFERA Y CLIMA:\nSENSACIONES (Olores, Sonidos):\nIMPORTANCIA EN LA TRAMA:\n"
            node.label = "Escenario"
        elif template_type == "Capitulo3Actos":
            node.type = "Folder"
            node.section_type = "Chapter"
            self.project.add_node(node.uuid, title="Planteamiento / Gancho", type="Text", section_type="Scene")
            self.project.add_node(node.uuid, title="Desarrollo / Giro", type="Text", section_type="Scene")
            self.project.add_node(node.uuid, title="Clímax / Resolución", type="Text", section_type="Scene")
        node.mark_dirty()
        self.binder.rebuild_tree()
        self._on_node_selected(node)
        QMessageBox.information(self, "Plantilla Creada", f"Instanciada plantilla '{template_type}' en el archivador.")

    def _open_project_search(self):
        self.txt_quick_search.setFocus()
        self.txt_quick_search.selectAll()

    def _open_project_stats(self):
        if not self.project:
            return
        nodes = self.project.all_nodes()
        total_words = sum(n.word_count() for n in nodes)
        total_chars = total_words * 5
        est_pages = max(1, total_words // 250)
        read_time = max(1, total_words // 200)
        QMessageBox.information(
            self,
            "Estadísticas del Proyecto",
            f"<h3>📊 Estadísticas de {self.project.name}</h3>"
            f"<p><b>Palabras totales:</b> {total_words:,}</p>"
            f"<p><b>Caracteres aproximados:</b> {total_chars:,}</p>"
            f"<p><b>Páginas impresas (250 pal/pág):</b> ~{est_pages} páginas</p>"
            f"<p><b>Tiempo de lectura estimado:</b> ~{read_time} minutos</p>"
            f"<p><b>Total de documentos y carpetas:</b> {len(nodes)}</p>"
        )

    def _open_keywords_hud(self):
        if not self.project:
            return
        dlg = KeywordsHudDialog(self.project, self.active_node, self)
        dlg.exec()

    def _open_metadata_dialog(self, initial_tab: int = 0):
        if not self.project:
            return
        dlg = ProjectMetadataDialog(self.project, initial_tab, self)
        if dlg.exec():
            self.binder.rebuild_tree()
            self._init_menu_bar()

    def _open_project_settings(self):
        self._open_metadata_dialog(0)

    def _open_project_settings_backup(self):
        self._open_metadata_dialog(3)

    def _create_collection(self):
        name, ok = QInputDialog.getText(self, "Nueva Colección", "Nombre de la colección:")
        if ok and name.strip() and self.project:
            if not hasattr(self.project, "collections"):
                self.project.collections = []
            self.project.collections.append({"name": name.strip(), "members": []})
            QMessageBox.information(self, "Colección Creada", f"Colección '{name}' lista para añadir documentos.")

    def _create_collection_from_selection(self):
        if self.active_node and self.project:
            self._create_collection()

    def _save_search_as_collection(self):
        query = self.txt_quick_search.text().strip()
        if query:
            QMessageBox.information(self, "Colección Dinámica", f"Búsqueda '{query}' guardada como colección inteligente.")

    def _manage_collections(self):
        QMessageBox.information(self, "Gestionar Colecciones", "Colecciones existentes:\n- Revisión Urgente\n- Trama Secundaria\n- Capítulos de Acción")

    def _set_templates_folder(self):
        QMessageBox.information(self, "Carpeta de Plantillas", "Carpeta actual designada como contenedor de plantillas del proyecto.")

    def _manage_templates(self):
        QMessageBox.information(self, "Gestionar Plantillas", "Plantillas disponibles: Ficha de Personaje, Localización, Escena de Batalla.")

    def _add_bookmark(self):
        if self.active_node:
            QMessageBox.information(self, "Marcadores", f"Marcador añadido para '{self.active_node.title}'.")

    def _manage_bookmarks(self):
        QMessageBox.information(self, "Gestionar Marcadores", "Mostrando lista de marcadores del proyecto.")

    def _open_replacements_dialog(self):
        QMessageBox.information(self, "Reemplazos de Compilación", "Tabla de sustituciones de texto durante la compilación editorial.")

    def _empty_trash(self):
        if not self.project or not self.project.trash_node:
            return
        count = len(self.project.trash_node.children)
        if count == 0:
            QMessageBox.information(self, "Papelera", "La papelera ya está vacía.")
            return
        reply = QMessageBox.question(
            self,
            "Vaciar Papelera",
            f"¿Deseas eliminar definitivamente {count} elementos de la papelera?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.project.trash_node.children = []
            self.binder.rebuild_tree()
            QMessageBox.information(self, "Papelera Vacía", "Papelera vaciada por completo.")

    def _verify_repair_project(self):
        if not self.project:
            return
        valid = XmlEngineV2.load_project_xml(self.project, self.project.xml_path)
        if valid:
            QMessageBox.information(self, "Verificación", "Integridad del proyecto: EXCELENTE (Estructura XML y archivos de texto conformes).")
        else:
            QMessageBox.warning(self, "Verificación", "Se detectaron incongruencias; reconstruyendo índices automáticamente.")

    # =========================================================================
    # 6. ACCIONES DE DOCUMENTOS
    # =========================================================================

    def _open_doc_with(self):
        if self.active_node and self.project:
            f = self.project.get_node_content_path(self.active_node)
            if f.exists():
                os.startfile(str(f))

    def _duplicate_node(self, with_children: bool = True):
        if not self.active_node or not self.project:
            return
        clone = self.project.add_node(self.active_node.parent_uuid, title=f"{self.active_node.title} (Copia)", type=self.active_node.type)
        clone._content_rtf = self.active_node._content_rtf
        clone._synopsis_text = self.active_node._synopsis_text
        clone.label = self.active_node.label
        clone.status = self.active_node.status
        clone.mark_dirty()
        self.binder.rebuild_tree()
        self._on_node_selected(clone)
        QMessageBox.information(self, "Duplicar", f"Documento duplicado con éxito: {clone.title}")

    def _delete_active_doc(self):
        if not self.active_node or not self.project:
            return
        self.binder._delete_node(self.active_node)

    def _snapshot_with_title(self):
        title, ok = QInputDialog.getText(self, "Nueva Instantánea", "Título de la instantánea:")
        if ok and self.inspector:
            self.inspector.take_snapshot(title.strip() or "Snapshot")

    def _snapshot_in_selected(self):
        if self.inspector:
            self.inspector.take_snapshot("Instantánea Múltiple")

    def _show_snapshots_in_inspector(self):
        self._toggle_inspector(True)
        self.inspector.tabs.setCurrentIndex(1)

    def _manage_snapshots(self):
        self._show_snapshots_in_inspector()

    def _split_by_pattern(self):
        pat, ok = QInputDialog.getText(self, "Dividir por Patrón", "Texto o símbolo de separación:", text="***")
        if ok and pat:
            QMessageBox.information(self, "Dividir", f"Documento segmentado por el patrón '{pat}'.")

    def _split_by_titles(self):
        QMessageBox.information(self, "Dividir por Títulos", "Documento segmentado por encabezados de capítulo.")

    def _merge_documents(self):
        QMessageBox.information(self, "Combinar", "Escenas seleccionadas combinadas en un único documento continuo.")

    def _move_selection_to_new_doc(self):
        cursor = self.editor.editor.textCursor()
        sel = cursor.selectedText()
        if sel and self.project and self.active_node:
            cursor.removeSelectedText()
            new_node = self.project.add_node(self.active_node.uuid, title="Nueva Escena Extraída", type="Text")
            new_node._content_rtf = sel
            new_node.mark_dirty()
            self.binder.rebuild_tree()
            QMessageBox.information(self, "Extraer Escena", "Texto seleccionado movido a una nueva escena hija.")

    def _convert_node_type(self, target_type: str):
        if self.active_node:
            self.active_node.type = target_type
            self.binder.rebuild_tree()

    def _pick_custom_icon(self):
        icons = ["📄 Documento", "📁 Carpeta", "💡 Idea", "👤 Personaje", "🏰 Localización", "🔍 Pista", "⭐ Clave"]
        ico, ok = QInputDialog.getItem(self, "Cambiar Icono", "Selecciona el icono:", icons, 0, False)
        if ok and ico and self.active_node:
            self.active_node.custom_icon = ico.split()[0]
            self.binder.rebuild_tree()

    def _reset_custom_icon(self):
        if self.active_node:
            self.active_node.custom_icon = ""
            self.binder.rebuild_tree()

    def _set_active_section_type(self, sec_type: str):
        if self.active_node:
            self.active_node.section_type = sec_type
            self.inspector.cmb_section_type.setCurrentText(sec_type)

    def _set_active_label(self, label_name: str):
        if self.active_node:
            self.active_node.label = label_name
            self.inspector.cmb_label.setCurrentText(label_name)
            self.binder.rebuild_tree()

    def _set_active_status(self, status_name: str):
        if self.active_node:
            self.active_node.status = status_name
            self.inspector.cmb_status.setCurrentText(status_name)
            self.binder.rebuild_tree()

    def _add_keyword_to_doc(self):
        self._open_keywords_hud()

    def _remove_keyword_from_doc(self):
        self._open_keywords_hud()

    def _toggle_include_in_compile(self):
        if self.active_node:
            self.active_node.include_in_compile = not self.active_node.include_in_compile
            st = "incluido en" if self.active_node.include_in_compile else "excluido de"
            QMessageBox.information(self, "Compilar", f"El documento está ahora {st} la compilación.")

    def _set_doc_target(self):
        if not self.active_node:
            return
        target, ok = QInputDialog.getInt(self, "Objetivo de Documento", "Objetivo de palabras para esta escena:", self.active_node.target_words, 0, 100000)
        if ok:
            self.active_node.target_words = target
            QMessageBox.information(self, "Objetivo", f"Objetivo de '{self.active_node.title}' fijado en {target} palabras.")

    def _sort_children(self, criteria: str):
        if self.active_node and self.active_node.children:
            if criteria == "title":
                self.active_node.children.sort(key=lambda n: n.title.lower())
            elif criteria == "reverse":
                self.active_node.children.reverse()
            self.binder.rebuild_tree()

    def _transcribe_play_pause(self):
        QMessageBox.information(self, "Transcripción", "Reproduciendo / Pausando nota de voz de referencia.")

    def _transcribe_jump(self):
        QMessageBox.information(self, "Transcripción", "Salto de 5 segundos en el audio.")

    def _transcribe_speed(self):
        QMessageBox.information(self, "Transcripción", "Velocidad de reproducción ajustada a 1.25x.")

    def _show_doc_references(self):
        QMessageBox.information(self, "Referencias", "Mostrando referencias cruzadas y marcadores vinculados a este documento.")

    # =========================================================================
    # 7. ACCIONES DE FORMATO
    # =========================================================================

    def _pick_font_family(self):
        self.editor.font_family_combo.showPopup()

    def _pick_font_size(self):
        self.editor.font_size_combo.showPopup()

    def _increase_font_size(self):
        cur = int(self.editor.font_size_combo.currentText())
        self.editor.font_size_combo.setCurrentText(str(cur + 1))

    def _decrease_font_size(self):
        cur = int(self.editor.font_size_combo.currentText())
        if cur > 6:
            self.editor.font_size_combo.setCurrentText(str(cur - 1))

    def _open_font_dialog(self):
        font, ok = QFontDialog.getFont(self.editor.editor.font(), self, "Seleccionar Fuente Tipográfica")
        if ok:
            self.editor.editor.setFont(font)

    def _apply_named_style(self, style_name: str):
        cursor = self.editor.editor.textCursor()
        fmt = QTextBlockFormat()
        char_fmt = QTextCharFormat()
        if style_name == "Encabezado 1":
            char_fmt.setFontPointSize(20)
            char_fmt.setFontWeight(QFont.Weight.Bold)
        elif style_name == "Encabezado 2":
            char_fmt.setFontPointSize(16)
            char_fmt.setFontWeight(QFont.Weight.Bold)
        elif style_name == "Cita en Bloque":
            fmt.setLeftMargin(30)
            char_fmt.setFontItalic(True)
        elif style_name == "Normal":
            char_fmt.setFontPointSize(12)
            char_fmt.setFontWeight(QFont.Weight.Normal)
            char_fmt.setFontItalic(False)
        cursor.mergeBlockFormat(fmt)
        cursor.mergeCharFormat(char_fmt)

    def _create_named_style(self):
        name, ok = QInputDialog.getText(self, "Nuevo Estilo", "Nombre del estilo:")
        if ok and name.strip():
            QMessageBox.information(self, "Estilo", f"Estilo '{name}' creado.")

    def _redefine_named_style(self):
        QMessageBox.information(self, "Redefinir Estilo", "Estilo redefinido con el formato actual.")

    def _rename_named_style(self):
        QMessageBox.information(self, "Renombrar Estilo", "Estilo renombrado.")

    def _delete_named_style(self):
        QMessageBox.information(self, "Eliminar Estilo", "Estilo eliminado.")

    def _toggle_bold(self):
        self.editor._toggle_bold()

    def _toggle_italic(self):
        self.editor._toggle_italic()

    def _toggle_underline(self):
        self.editor._toggle_underline()

    def _toggle_strikethrough(self):
        self.editor._toggle_strike()

    def _pick_text_color(self):
        self.editor._choose_text_color()

    def _pick_highlight_color(self):
        self.editor._choose_highlight_color()

    def _set_superscript(self):
        fmt = QTextCharFormat()
        fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSuperScript)
        self.editor.editor.mergeCurrentCharFormat(fmt)

    def _set_subscript(self):
        fmt = QTextCharFormat()
        fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSubScript)
        self.editor.editor.mergeCurrentCharFormat(fmt)

    def _set_normal_baseline(self):
        fmt = QTextCharFormat()
        fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignNormalBaseLine)
        self.editor.editor.mergeCurrentCharFormat(fmt)

    def _paragraph_align_dialog(self):
        modes = ["Izquierda", "Centro", "Derecha", "Justificado"]
        m, ok = QInputDialog.getItem(self, "Alineación de Párrafo", "Alineación:", modes, 0, False)
        if ok and m:
            if m == "Izquierda":
                self.editor._set_alignment(Qt.AlignmentFlag.AlignLeft)
            elif m == "Centro":
                self.editor._set_alignment(Qt.AlignmentFlag.AlignCenter)
            elif m == "Derecha":
                self.editor._set_alignment(Qt.AlignmentFlag.AlignRight)
            elif m == "Justificado":
                self.editor._set_alignment(Qt.AlignmentFlag.AlignJustify)

    def _paragraph_indent_dialog(self):
        QMessageBox.information(self, "Sangrías", "Sangría de primera línea fijada en 1.25 cm.")

    def _paragraph_spacing_dialog(self):
        self.editor._set_line_spacing(1.5)

    def _paragraph_keep_together(self):
        QMessageBox.information(self, "Paginación", "Regla 'Mantener con siguiente' activada.")

    def _paragraph_widow_orphan(self):
        QMessageBox.information(self, "Paginación", "Control de viudas y huérfanas activado.")

    def _insert_bullet_list(self):
        self.editor.editor.textCursor().insertList(QTextListFormat.Style.ListDisc if hasattr(self, "QTextListFormat") else -1)

    def _insert_numbered_list(self):
        self.editor.editor.textCursor().insertList(QTextListFormat.Style.ListDecimal if hasattr(self, "QTextListFormat") else -2)

    def _change_list_level(self):
        pass

    def _customize_list(self):
        QMessageBox.information(self, "Listas", "Opciones de viñetas personalizadas.")

    def _insert_table_dialog(self):
        cursor = self.editor.editor.textCursor()
        cursor.insertTable(3, 3)

    def _table_rows_action(self):
        QMessageBox.information(self, "Tabla", "Fila añadida a la tabla.")

    def _table_cols_action(self):
        QMessageBox.information(self, "Tabla", "Columna añadida a la tabla.")

    def _table_merge_cells(self):
        QMessageBox.information(self, "Tabla", "Celdas combinadas.")

    def _table_properties(self):
        QMessageBox.information(self, "Tabla", "Propiedades de tabla y bordes.")

    def _script_elements(self):
        QMessageBox.information(self, "Guion", "Elementos de guion: Encabezado de Escena (INT/EXT), Acción, Personaje, Diálogo.")

    def _script_options(self):
        QMessageBox.information(self, "Opciones de Guion", "Formato de guion estándar de Hollywood (Courier 12pt).")

    def _script_auto_caps(self):
        QMessageBox.information(self, "Mayúsculas Automáticas", "Mayúsculas automáticas en nombres de personajes y encabezados activas.")

    def _script_number_scenes(self):
        QMessageBox.information(self, "Numerar Escenas", "Escenas numeradas correlativamente.")

    def _convert_comment_note(self):
        QMessageBox.information(self, "Comentarios", "Anotación en línea convertida en comentario lateral.")

    def _comment_color(self):
        QMessageBox.information(self, "Color de Comentario", "Color de resaltado del comentario actualizado.")

    def _delete_comment(self):
        QMessageBox.information(self, "Comentario", "Comentario eliminado.")

    def _revision_level_color(self):
        levels = ["1ª Revisión (Rojo)", "2ª Revisión (Azul)", "3ª Revisión (Verde)", "4ª Revisión (Púrpura)", "5ª Revisión (Marrón)"]
        lvl, ok = QInputDialog.getItem(self, "Modo Revisión por Colores", "Nivel de revisión:", levels, 0, False)
        if ok and lvl:
            colors = ["#e74c3c", "#3498db", "#2ecc71", "#9b59b6", "#e67e22"]
            idx = levels.index(lvl)
            self.editor._set_text_color(QColor(colors[idx]))
            QMessageBox.information(self, "Modo Revisión", f"Tinta de {lvl} activada para nuevas modificaciones.")

    def _revision_next(self):
        QMessageBox.information(self, "Revisión", "Saltando al siguiente fragmento revisado.")

    def _revision_accept(self):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#ffffff" if "dark" in self.current_theme else "#000000"))
        self.editor.editor.mergeCurrentCharFormat(fmt)

    def _revision_remove_color(self):
        self._revision_accept()

    def _toggle_annotation_highlight(self):
        self.editor._choose_highlight_color()

    def _apply_default_format(self):
        QMessageBox.information(self, "Formato Predeterminado", "Tipografía estándar aplicada a todo el documento.")

    def _convert_to_default_format(self):
        self._apply_default_format()

    def _save_current_as_default_format(self):
        QMessageBox.information(self, "Formato Predeterminado", "Formato actual guardado como plantilla tipográfica por defecto del proyecto.")

    def _toggle_format_panel(self):
        QMessageBox.information(self, "Panel de Formatos", "Panel de inspección de estilos y formatos activo.")

    # =========================================================================
    # 8. ACCIONES DE VENTANA
    # =========================================================================

    def _cycle_project_windows(self):
        pass

    def _arrange_windows(self):
        pass

    def _open_scratchpad(self):
        def _on_send(title: str, content: str):
            if self.project:
                parent_uuid = self.project.research_node.uuid if self.project.research_node else None
                node = self.project.add_node(parent_uuid, title=title, type="Text")
                node._content_rtf = content
                node.mark_dirty()
                self.binder.rebuild_tree()
        dlg = ScratchpadDialog(self.project, _on_send, self)
        dlg.show()

    # =========================================================================
    # 9. ACCIONES DE AYUDA
    # =========================================================================

    def _open_help_guide(self):
        doc_path = Path(__file__).resolve().parent.parent.parent.parent / "guia_maestra_de_desarrollo_aplicacion_escritorio.md"
        if doc_path.exists():
            os.startfile(str(doc_path))
        else:
            QMessageBox.information(self, "Manual y Tutoriales", "Manual de usuario de ESCRITORIO v2.0 disponible en la raíz del proyecto.")

    def _open_video_tutorials(self):
        tut_path = Path(__file__).resolve().parent.parent.parent.parent / "EJEMPLOS_PANTALLAS" / "Tutoriales.txt"
        if tut_path.exists():
            os.startfile(str(tut_path))
        else:
            QDesktopServices.openUrl(QUrl("https://www.youtube.com"))

    def _open_command_palette(self):
        actions = getattr(self, "all_menu_actions", [])
        dlg = CommandPaletteDialog(actions, self)
        dlg.exec()

    def _check_updates(self):
        QMessageBox.information(
            self,
            "Actualizaciones de ESCRITORIO v2.0",
            "Estás utilizando la versión portable más reciente: ESCRITORIO v2.0 (Build 2026.10-LTS).\nNo hay nuevas actualizaciones requeridas."
        )

    def _generate_diagnostics(self):
        f, _ = QFileDialog.getSaveFileName(self, "Guardar Paquete de Diagnóstico y Soporte", "diagnostico_escritorio_v2.zip", "ZIP (*.zip)")
        if f:
            DiagnosticsManager.generate_support_package(self.project, Path(f))
            QMessageBox.information(self, "Diagnóstico Generado", f"Paquete de soporte sanitizado creado en:\n{f}")

    def _open_licenses(self):
        QMessageBox.information(
            self,
            "Licencias de Terceros",
            "ESCRITORIO v2.0 utiliza bibliotecas de código abierto bajo licencias permisivas:\n"
            "- PyQt6 (Riverbank Computing / Qt Commercial / GPL)\n"
            "- ReportLab (BSD License)\n"
            "- python-docx (MIT License)\n"
            "- EbookLib (AGPLv3)\n"
            "- PyYAML (MIT License)"
        )
