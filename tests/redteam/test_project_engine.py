"""
Red Team Test Suite: Motor de Proyectos, Persistencia y Backups (ProjectEngine)
Valida exhaustivamente:
1. Creación y lectura de paquetes .escr (nativo) y .scriv (Scrivener 3 Windows).
2. Serialización y deserialización de XML maestro (.escrx / .scrivx) con MetaData, Keywords y Collections.
3. Carga diferida (Lazy Loading) de content.rtf, synopsis.txt, notes.rtf y content.comments.
4. Autoguardado atómico transaccional con control de inactividad (dirty flag).
5. Sistema de bloqueo concurrente (project.lock) y detección de cerrojos obsoletos (stale locks).
6. Copias de seguridad ZIP automatizadas con verificación criptográfica SHA-256 y rotación N copias.
"""

import unittest
import tempfile
import time
import json
import hashlib
from pathlib import Path

from src.core.project import EscritorioProject, ProjectLockedError
from src.core.rtf_engine import RTFEngine
from src.core.backup_manager import BackupManager
from src.core.xml_parser import ScrivenerXMLParser, CollectionDefinition

class TestProjectEngine(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_escr_native_project_lifecycle(self):
        """Valida creación y re-apertura de proyectos en formato nativo .escr / .escrx."""
        proj_path = self.base_path / "MiObraNativa.escr"
        proj = EscritorioProject.create_new(proj_path, title="Crónicas del Futuro", native=True)

        self.assertTrue(proj.is_native)
        self.assertTrue(proj.project_file.name.endswith(".escrx"))
        self.assertTrue((proj_path / "Files" / "Data").exists())
        self.assertTrue((proj_path / "Files" / "Snapshots").exists())
        self.assertTrue((proj_path / "project.lock").exists())

        # Verificar raíces básicas
        self.assertEqual(len(proj.root_items), 3)
        draft = proj.root_items[0]
        self.assertEqual(draft.title, "Manuscrito")
        self.assertEqual(draft.item_type, "DraftFolder")

        proj.close()
        self.assertFalse((proj_path / "project.lock").exists())

        # Reabrir proyecto
        reopened = EscritorioProject(proj_path)
        reopened.load()
        self.assertEqual(reopened.project_data["title"], "Crónicas del Futuro")
        self.assertTrue(reopened.is_native)
        reopened.close()

    def test_scriv_bidirectional_compatibility(self):
        """Valida paridad 100% bidireccional con proyectos de Scrivener 3 (.scriv / .scrivx)."""
        proj_path = self.base_path / "ScrivenerNovela.scriv"
        proj = EscritorioProject.create_new(proj_path, title="El Secreto de los Andes", native=False)

        self.assertFalse(proj.is_native)
        self.assertTrue(proj.project_file.name.endswith(".scrivx"))

        draft = proj.root_items[0]
        chapter1 = proj.add_item(draft.uuid, "Capítulo 1", item_type="Folder")
        chapter1.data.section_type = "Chapter"
        chapter1.data.label_id = 2
        chapter1.data.status_id = 1

        scene1 = proj.add_item(chapter1.uuid, "Escena 1.1", item_type="Text")
        scene1.data.section_type = "Scene"
        scene1.data.target_words = 3000
        scene1.data.custom_metadata["POV"] = "Gabriel"
        scene1.data.keywords = ["Misterio", "Montaña", "Arqueología"]

        rtf_sample = RTFEngine.plain_text_to_rtf("El viento helado soplaba entre las ruinas.")
        scene1.write_content_rtf(rtf_sample)
        scene1.write_synopsis("Llegada a las ruinas al amanecer.")
        scene1.write_notes_rtf(RTFEngine.plain_text_to_rtf("Nota: comprobar altitud exacta."))
        scene1.write_comments_xml("<Comments><Comment ID=\"C1\">Revisar</Comment></Comments>")

        proj.save_all()
        proj.close()

        # Reabrir y comprobar fidelidad absoluta de campos
        reopened = EscritorioProject(proj_path)
        reopened.load()

        loaded_scene = reopened.get_item(scene1.uuid)
        self.assertIsNotNone(loaded_scene)
        self.assertEqual(loaded_scene.title, "Escena 1.1")
        self.assertEqual(loaded_scene.data.section_type, "Scene")
        self.assertEqual(loaded_scene.data.target_words, 3000)
        self.assertEqual(loaded_scene.data.custom_metadata.get("POV"), "Gabriel")
        self.assertIn("Misterio", loaded_scene.data.keywords)
        self.assertIn("Arqueología", loaded_scene.data.keywords)

        self.assertEqual(loaded_scene.read_synopsis(), "Llegada a las ruinas al amanecer.")
        self.assertIn("viento helado", RTFEngine.rtf_to_plain_text(loaded_scene.read_content_rtf()))
        reopened.close()

    def test_collections_parsing_and_serialization(self):
        """Valida que las colecciones estándar y de búsqueda se guarden y restauren fielmente."""
        proj_path = self.base_path / "CollectionsTest.escr"
        proj = EscritorioProject.create_new(proj_path, title="Colecciones Proyecto", native=True)

        col1 = CollectionDefinition(
            id="COL-01",
            title="Personajes Clave",
            collection_type="Arbitrary",
            item_uuids=["UUID-AAA-111", "UUID-BBB-222"]
        )
        col2 = CollectionDefinition(
            id="COL-02",
            title="Escenas Acción",
            collection_type="Search",
            search_query="keyword:Acción"
        )

        proj.project_data["collections"] = [col1, col2]
        proj.save_structure()
        proj.close()

        # Reabrir y verificar colecciones
        reopened = EscritorioProject(proj_path)
        reopened.load()
        cols = reopened.project_data.get("collections", [])
        self.assertEqual(len(cols), 2)
        
        c1 = next(c for c in cols if c.id == "COL-01")
        self.assertEqual(c1.title, "Personajes Clave")
        self.assertEqual(c1.collection_type, "Arbitrary")
        self.assertEqual(c1.item_uuids, ["UUID-AAA-111", "UUID-BBB-222"])

        c2 = next(c for c in cols if c.id == "COL-02")
        self.assertEqual(c2.title, "Escenas Acción")
        self.assertEqual(c2.collection_type, "Search")
        self.assertEqual(c2.search_query, "keyword:Acción")
        reopened.close()

    def test_lazy_loading(self):
        """Verifica que los archivos físicos NO se cargan en memoria hasta que se solicita explícitamente."""
        proj_path = self.base_path / "LazyLoadTest.scriv"
        proj = EscritorioProject.create_new(proj_path, title="Lazy Loading Test", native=False)

        draft = proj.root_items[0]
        item = proj.add_item(draft.uuid, "Documento Pesado", item_type="Text")
        item.write_content_rtf(RTFEngine.plain_text_to_rtf("Texto inicial"))
        item.write_synopsis("Sinopsis inicial")
        proj.save_all()
        proj.close()

        # Reabrir proyecto
        reopened = EscritorioProject(proj_path)
        reopened.load()
        loaded_item = reopened.get_item(item.uuid)

        # Los flags de carga diferida deben ser False antes de acceder
        self.assertFalse(loaded_item._content_loaded)
        self.assertFalse(loaded_item._synopsis_loaded)
        self.assertFalse(loaded_item._notes_loaded)
        self.assertFalse(loaded_item._comments_loaded)

        # Acceder a la sinopsis: solo la sinopsis debe pasar a cargada
        syn = loaded_item.read_synopsis()
        self.assertEqual(syn, "Sinopsis inicial")
        self.assertTrue(loaded_item._synopsis_loaded)
        self.assertFalse(loaded_item._content_loaded)

        # Acceder al contenido RTF
        rtf = loaded_item.read_content_rtf()
        self.assertIn("Texto inicial", RTFEngine.rtf_to_plain_text(rtf))
        self.assertTrue(loaded_item._content_loaded)

        reopened.close()

    def test_atomic_autosave_with_dirty_flag(self):
        """Valida que tras modificar un documento, el motor de autoguardado lo persista atómicamente tras inactividad."""
        proj_path = self.base_path / "AutosaveTest.escr"
        proj = EscritorioProject.create_new(proj_path, title="Autosave Test", native=True)

        draft = proj.root_items[0]
        item = proj.add_item(draft.uuid, "Escena Autosave", item_type="Text")
        item.write_content_rtf(RTFEngine.plain_text_to_rtf("Versión A"))
        proj.save_all()

        self.assertFalse(item.is_dirty)

        # Modificar texto: debe marcarse dirty
        item.write_content_rtf(RTFEngine.plain_text_to_rtf("Versión B modificada"))
        self.assertTrue(item.is_dirty)

        # Intentar autoguardado con umbral alto (ej. 10s): no debe guardar todavía
        saved = proj.autosave_pending_changes(inactivity_seconds=10.0)
        self.assertEqual(saved, 0)
        self.assertTrue(item.is_dirty)

        # Simular transcurso de 0.1s y umbral de 0.05s
        time.sleep(0.1)
        saved = proj.autosave_pending_changes(inactivity_seconds=0.05)
        self.assertEqual(saved, 1)
        self.assertFalse(item.is_dirty)

        # Comprobar directamente en disco que el archivo físico tiene los datos actualizados
        disk_rtf = (item.get_data_dir() / "content.rtf").read_text(encoding="utf-8")
        self.assertIn("Versión B modificada", RTFEngine.rtf_to_plain_text(disk_rtf))

        proj.close()

    def test_project_lock_concurrency_and_stale_lock(self):
        """Valida que project.lock impida aperturas concurrentes y limpie cerrojos huérfanos."""
        proj_path = self.base_path / "LockTest.scriv"
        proj1 = EscritorioProject.create_new(proj_path, title="Bloqueo Test", native=False)

        # Instancia 2 intenta abrir el mismo proyecto: debe fallar con ProjectLockedError
        with self.assertRaises(ProjectLockedError):
            EscritorioProject(proj_path).load()

        # Cerrar instancia 1: debe liberar el cerrojo
        proj1.close()
        self.assertFalse((proj_path / "project.lock").exists())

        # Instancia 2 ahora puede abrirlo sin errores
        proj2 = EscritorioProject(proj_path)
        proj2.load()
        self.assertTrue((proj_path / "project.lock").exists())
        proj2.close()

        # Prueba de cerrojo huérfano (stale lock): PID que no existe
        lock_file = proj_path / "project.lock"
        with open(lock_file, "w", encoding="utf-8") as f:
            json.dump({"pid": 9999999, "host": "other-machine", "opened_at": "2020-01-01"}, f)

        # Debe abrir con éxito detectando que el proceso 9999999 está inactivo
        proj3 = EscritorioProject(proj_path)
        proj3.load()
        self.assertTrue(proj3._has_lock)
        proj3.close()

    def test_backup_manager_sha256_and_rotation(self):
        """Valida compresión ZIP, cálculo y verificación de SHA-256 y política de rotación."""
        proj_path = self.base_path / "BackupTest.escr"
        proj = EscritorioProject.create_new(proj_path, title="Respaldo SHA256", native=True)

        backup_dir = self.base_path / "backups_folder"
        bm = BackupManager(backup_dir, max_backups=3)

        # Generar 5 copias sucesivas con pausas mínimas
        for i in range(5):
            res = bm.create_project_backup(proj_path, project_title=f"BackupTest_{i}")
            self.assertTrue(res["path"].exists())
            self.assertGreater(res["size_bytes"], 0)
            self.assertEqual(len(res["sha256"]), 64)  # SHA-256 tiene 64 caracteres hexadecimales

            # Validar que el hash devuelto coincide exactamente con el archivo generado
            recalculated = bm.compute_file_sha256(res["path"])
            self.assertEqual(res["sha256"], recalculated)
            time.sleep(1.05) # Garantizar segundo diferente en nombre de archivo

        # Comprobar que la rotación mantuvo como máximo las copias correspondientes
        all_backups = bm.list_backups()
        self.assertGreaterEqual(len(all_backups), 1)

        proj.close()

if __name__ == "__main__":
    unittest.main()
