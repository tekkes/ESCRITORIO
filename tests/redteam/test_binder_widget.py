"""
Red Team Test: Suite Exhaustiva del Cuaderno (BinderWidget)
Verifica todas las capacidades estructurales y visuales de Scrivener 3:
1. Árbol multinivel con las 3 carpetas raíz (Draft, Research, Trash) + Templates.
2. Capacidad dual de nodos (carpetas con texto propio y documentos con hijos).
3. Operaciones narrativas con Deshacer / Rehacer (Ctrl+Z / Ctrl+Y):
   - Drag & Drop / Mover
   - Agrupar (Ctrl+G) / Desagrupar (Ctrl+Shift+G)
   - Dividir (Ctrl+K) / Dividir con título (Ctrl+Shift+K)
   - Fusionar documentos (Ctrl+Shift+M)
   - Duplicar (Ctrl+D) / Papelera y Restauración
4. Biblioteca de más de 80 micro-iconos SVG, emojis y modos de color de etiqueta.
5. Sistema de Colecciones (Estándar y Búsqueda Guardada evaluada en tiempo real).
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from src.core.project import EscritorioProject, BinderItem
from src.core.rtf_engine import RTFEngine
from src.ui.BinderWidget import (
    BinderWidget,
    BinderTreeView,
    LabelColorMode,
    CollectionsManager,
    IconLibrary,
    UndoStack
)


class TestBinderWidget(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.proj_path = Path(self.temp_dir) / "Novela_Test.escr"
        self.project = EscritorioProject.create_new(self.proj_path, "Novela Test", native=True)
        self.binder = BinderWidget(self.project)

    def tearDown(self):
        if self.project:
            self.project.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_root_folders_and_templates(self):
        """Verifica las 3 carpetas raíz especiales (Draft, Research, Trash) y soporte de Plantillas."""
        draft = self.project.get_draft_folder()
        research = self.project.get_research_folder()
        trash = self.project.get_trash_folder()

        self.assertIsNotNone(draft, "Falta la carpeta DraftFolder")
        self.assertIsNotNone(research, "Falta la carpeta ResearchFolder")
        self.assertIsNotNone(trash, "Falta la carpeta TrashFolder")

        # Configurar carpeta de Plantillas
        templates = self.project.add_item("", "Plantillas de Proyecto", item_type="Folder")
        self.project.set_templates_folder(templates.uuid)

        tpl_found = self.project.get_templates_folder()
        self.assertIsNotNone(tpl_found)
        self.assertEqual(tpl_found.uuid, templates.uuid)
        self.assertEqual(tpl_found.item_type, "TemplatesFolder")

    def test_dual_capacity_nodes(self):
        """Verifica que cualquier carpeta puede almacenar texto y cualquier documento puede tener hijos."""
        draft = self.project.get_draft_folder()

        # 1. Carpeta con texto propio
        capitulo = self.project.add_item(draft.uuid, "Capítulo 1", item_type="Folder")
        capitulo.write_content_rtf(RTFEngine.plain_text_to_rtf("Texto introductorio del capítulo."))
        capitulo.write_synopsis("Sinopsis del capítulo completo.")

        self.assertTrue(capitulo.get_word_count() > 0)
        self.assertIn("Texto introductorio", RTFEngine.rtf_to_plain_text(capitulo.read_content_rtf()))
        self.assertEqual(capitulo.read_synopsis(), "Sinopsis del capítulo completo.")

        # 2. Documento de texto que contiene subdocumentos hijos
        escena_padre = self.project.add_item(capitulo.uuid, "Escena Principal", item_type="Text")
        escena_padre.write_content_rtf(RTFEngine.plain_text_to_rtf("Texto de la escena madre."))

        sub_escena_a = self.project.add_item(escena_padre.uuid, "Latido A: La Llegada", item_type="Text")
        sub_escena_b = self.project.add_item(escena_padre.uuid, "Latido B: El Encuentro", item_type="Text")

        self.assertEqual(len(escena_padre.children), 2)
        self.assertEqual(escena_padre.children[0].title, "Latido A: La Llegada")
        self.assertEqual(escena_padre.children[1].title, "Latido B: El Encuentro")

        # Verificar renderizado en el árbol
        render_tree = self.binder.tree_view.get_render_tree()
        self.assertTrue(len(render_tree) >= 3)

    def test_group_and_ungroup_with_undo(self):
        """Verifica Agrupar (Ctrl+G) y Desagrupar (Ctrl+Shift+G) con reversión completa."""
        draft = self.project.get_draft_folder()
        doc1 = self.project.add_item(draft.uuid, "Documento 1", item_type="Text")
        doc2 = self.project.add_item(draft.uuid, "Documento 2", item_type="Text")
        doc3 = self.project.add_item(draft.uuid, "Documento 3", item_type="Text")

        # Seleccionar doc1 y doc2 y agrupar (Ctrl+G)
        self.binder.tree_view.select_multiple([doc1.uuid, doc2.uuid])
        ok = self.binder.group_selection("Nuevo Acto")
        self.assertTrue(ok)

        # La carpeta fue creada
        folder_uuid = self.binder.selected_uuid
        folder = self.project.get_item(folder_uuid)
        self.assertEqual(folder.title, "Nuevo Acto")
        self.assertEqual(len(folder.children), 2)

        # Deshacer Agrupar (Ctrl+Z)
        self.assertTrue(self.binder.can_undo)
        self.binder.undo()

        # Los documentos vuelven a ser hijos directos del borrador
        self.assertEqual(self.project.find_parent(doc1.uuid).uuid, draft.uuid)
        self.assertEqual(self.project.find_parent(doc2.uuid).uuid, draft.uuid)

        # Rehacer Agrupar (Ctrl+Y)
        self.binder.redo()
        self.assertEqual(len(self.project.get_item(folder_uuid).children), 2)

        # Desagrupar (Ctrl+Shift+G)
        self.binder.tree_view.select_item(folder_uuid)
        ok_ungroup = self.binder.ungroup_selection()
        self.assertTrue(ok_ungroup)

        # Los hijos ahora están de nuevo en el padre
        self.assertEqual(self.project.find_parent(doc1.uuid).uuid, draft.uuid)

        # Deshacer Desagrupar
        self.binder.undo()
        self.assertIsNotNone(self.project.get_item(folder_uuid))

    def test_split_document_with_undo(self):
        """Verifica Dividir (Ctrl+K) y Dividir con Selección como Título (Ctrl+Shift+K)."""
        draft = self.project.get_draft_folder()
        doc = self.project.add_item(draft.uuid, "Escena Larga", item_type="Text")
        doc.write_content_rtf(RTFEngine.plain_text_to_rtf("Primera mitad del texto. Segunda mitad del texto."))

        self.binder.tree_view.select_item(doc.uuid)

        # Dividir simple en el carácter 23 (Ctrl+K)
        ok = self.binder.split_document(23, "Escena Dividida")
        self.assertTrue(ok)

        created_uuid = self.binder.selected_uuid
        created_doc = self.project.get_item(created_uuid)
        self.assertEqual(created_doc.title, "Escena Dividida")
        self.assertIn("Segunda mitad", RTFEngine.rtf_to_plain_text(created_doc.read_content_rtf()))
        self.assertIn("Primera mitad", RTFEngine.rtf_to_plain_text(doc.read_content_rtf()))

        # Deshacer división (Ctrl+Z)
        self.binder.undo()
        self.assertIn("Segunda mitad", RTFEngine.rtf_to_plain_text(doc.read_content_rtf()))

        # Dividir con selección como título (Ctrl+Shift+K)
        # "Capítulo Dos: El Rescate"
        self.binder.tree_view.select_item(doc.uuid)
        full_text = "Antes del rescate. Capítulo Dos: El Rescate. Después del rescate."
        doc.write_content_rtf(RTFEngine.plain_text_to_rtf(full_text))

        start_p = full_text.find("Capítulo Dos: El Rescate")
        end_p = start_p + len("Capítulo Dos: El Rescate")

        ok_title = self.binder.split_document_with_title(start_p, end_p)
        self.assertTrue(ok_title)

        new_doc = self.project.get_item(self.binder.selected_uuid)
        self.assertEqual(new_doc.title, "Capítulo Dos: El Rescate")
        self.assertIn("Después del rescate", RTFEngine.rtf_to_plain_text(new_doc.read_content_rtf()))

    def test_merge_documents_with_undo(self):
        """Verifica Fusionar documentos (Ctrl+Shift+M) con concatenación y reversibilidad."""
        draft = self.project.get_draft_folder()
        d1 = self.project.add_item(draft.uuid, "Parte 1", item_type="Text")
        d1.write_content_rtf(RTFEngine.plain_text_to_rtf("Texto parte 1."))
        d1.write_synopsis("Sinopsis 1.")

        d2 = self.project.add_item(draft.uuid, "Parte 2", item_type="Text")
        d2.write_content_rtf(RTFEngine.plain_text_to_rtf("Texto parte 2."))
        d2.write_synopsis("Sinopsis 2.")

        # Seleccionar ambos y fusionar (Ctrl+Shift+M)
        self.binder.tree_view.select_multiple([d1.uuid, d2.uuid])
        ok = self.binder.merge_selection()
        self.assertTrue(ok)

        # d1 tiene ambos textos concatenados
        merged_text = RTFEngine.rtf_to_plain_text(d1.read_content_rtf())
        self.assertIn("Texto parte 1.", merged_text)
        self.assertIn("Texto parte 2.", merged_text)
        self.assertIn("* * *", merged_text)
        self.assertIn("Sinopsis 1.", d1.read_synopsis())
        self.assertIn("Sinopsis 2.", d1.read_synopsis())

        # d2 fue movido a la papelera
        trash = self.project.get_trash_folder()
        self.assertIn(d2.uuid, [c.uuid for c in trash.children])

        # Deshacer fusión (Ctrl+Z)
        self.binder.undo()
        self.assertEqual(RTFEngine.rtf_to_plain_text(d1.read_content_rtf()), "Texto parte 1.")
        # d2 restaurado a su padre original
        self.assertEqual(self.project.find_parent(d2.uuid).uuid, draft.uuid)
        self.assertEqual(RTFEngine.rtf_to_plain_text(d2.read_content_rtf()), "Texto parte 2.")

    def test_duplicate_and_trash_restoration(self):
        """Verifica Duplicar (Ctrl+D), Papelera (Supr) y Restauración intacta."""
        draft = self.project.get_draft_folder()
        doc = self.project.add_item(draft.uuid, "Escena Original", item_type="Text")
        doc.write_content_rtf(RTFEngine.plain_text_to_rtf("Contenido importante."))

        # 1. Duplicar
        self.binder.tree_view.select_item(doc.uuid)
        ok_dup = self.binder.duplicate_selection()
        self.assertTrue(ok_dup)

        dup_uuid = self.binder.selected_uuid
        dup_doc = self.project.get_item(dup_uuid)
        self.assertEqual(dup_doc.title, "Escena Original (Copia)")
        self.assertEqual(RTFEngine.rtf_to_plain_text(dup_doc.read_content_rtf()), "Contenido importante.")

        # Deshacer duplicación
        self.binder.undo()
        self.assertIsNone(self.project.get_item(dup_uuid))

        # 2. Papelera y Restaurar
        self.binder.tree_view.select_item(doc.uuid)
        ok_trash = self.binder.trash_selection()
        self.assertTrue(ok_trash)

        trash = self.project.get_trash_folder()
        self.assertIn(doc.uuid, [c.uuid for c in trash.children])

        # Deshacer envío a la papelera
        self.binder.undo()
        self.assertEqual(self.project.find_parent(doc.uuid).uuid, draft.uuid)

    def test_icon_library_and_customization(self):
        """Verifica la biblioteca de más de 80 micro-iconos y asignación de emojis y colores."""
        self.assertGreaterEqual(IconLibrary.count(), 80, "La biblioteca debe contener al menos 80 iconos")

        cats = IconLibrary.get_categories()
        self.assertIn("Carpetas", cats)
        self.assertIn("Documentos", cats)
        self.assertIn("Personajes", cats)
        self.assertIn("Lugares", cats)
        self.assertIn("Banderas", cats)

        # Generador de emoji
        emoji_svg = IconLibrary.generate_emoji_svg("🧙")
        self.assertIn("<svg", emoji_svg)
        self.assertIn("🧙", emoji_svg)

        # Asignar icono a un documento
        draft = self.project.get_draft_folder()
        doc = self.project.add_item(draft.uuid, "Personaje Mágico", item_type="Text")

        ok = self.binder.change_icon(doc.uuid, "char_protagonist")
        self.assertTrue(ok)
        self.assertEqual(doc.data.icon_file_name, "char_protagonist")

        # Modos de color de etiqueta en el Binder
        tree = self.binder.tree_view
        tree.set_label_color_mode(LabelColorMode.DOT_RIGHT)
        self.assertEqual(tree.label_color_mode, LabelColorMode.DOT_RIGHT)

        tree.set_label_color_mode("row_highlight")
        self.assertEqual(tree.label_color_mode, LabelColorMode.ROW_HIGHLIGHT)

    def test_collections_system_standard_and_live_search(self):
        """Verifica las colecciones estándar y la evaluación dinámica de búsquedas guardadas."""
        mgr = self.binder.collections_mgr
        draft = self.project.get_draft_folder()

        doc_accion = self.project.add_item(draft.uuid, "Batalla en la Plaza", item_type="Text")
        doc_accion.write_content_rtf(RTFEngine.plain_text_to_rtf("Las espadas chocaban con furia bajo la lluvia."))

        doc_calma = self.project.add_item(draft.uuid, "Diálogo en la Posada", item_type="Text")
        doc_calma.write_content_rtf(RTFEngine.plain_text_to_rtf("Bebían vino caliente junto al fuego."))

        # 1. Colección Estándar (Manual)
        col_std = mgr.add_standard_collection("Escenas Clave")
        mgr.add_item_to_collection(col_std.collection_id, doc_accion.uuid)

        items_std = mgr.get_items_for_collection(col_std)
        self.assertEqual(len(items_std), 1)
        self.assertEqual(items_std[0].title, "Batalla en la Plaza")

        # 2. Colección de Búsqueda Guardada (Dinámica en tiempo real)
        col_search = mgr.add_search_collection("Búsqueda Espadas", query="espadas", field="All")

        # Debe encontrar doc_accion dinámicamente por coincidencia en el texto
        items_search = mgr.get_items_for_collection(col_search)
        self.assertEqual(len(items_search), 1)
        self.assertEqual(items_search[0].uuid, doc_accion.uuid)

        # Si modificamos doc_calma añadiendo la palabra "espadas", la búsqueda debe incluirlo en caliente
        doc_calma.write_content_rtf(RTFEngine.plain_text_to_rtf("Afilaban sus espadas en silencio."))
        items_search_updated = mgr.get_items_for_collection(col_search)
        self.assertEqual(len(items_search_updated), 2)

        # 3. Pestañas de renderizado
        tabs = mgr.get_tabs_render_data()
        self.assertEqual(len(tabs), 3) # Cuaderno + Escenas Clave + Búsqueda Espadas
        self.assertEqual(tabs[0]["title"], "Cuaderno")
        self.assertTrue(tabs[2]["is_search"])


if __name__ == "__main__":
    unittest.main()
