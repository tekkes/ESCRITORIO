"""
ESCRITORIO v2.0 - Core & Persistence Test Suite
Pruebas unitarias de persistencia atómica, modelo de datos y serialización XML.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from src.core.project_v2 import EscritorioProjectV2, BinderNode
from src.core.xml_engine_v2 import XmlEngineV2
from src.core.atomic_storage import AtomicStorage, ProjectLock
from src.core.backup_manager import BackupManager


class TestProjectCoreV2(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="escr_test_"))
        self.project_path = self.test_dir / "TestBook.escr"
        self.project = EscritorioProjectV2(self.project_path)

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_atomic_write_and_read(self):
        test_file = self.test_dir / "sample.txt"
        AtomicStorage.write_atomic_text(test_file, "Texto de prueba atómico")
        self.assertTrue(test_file.exists())
        read_back = AtomicStorage.read_text_safe(test_file)
        self.assertEqual(read_back, "Texto de prueba atómico")

    def test_project_structure_and_counts(self):
        draft = BinderNode(title="Manuscrito", type="DraftFolder")
        cap1 = BinderNode(title="Capítulo 1", type="Folder", parent_uuid=draft.uuid)
        esc1 = BinderNode(title="Escena 1", type="Text", parent_uuid=cap1.uuid)
        esc1._content_rtf = "Uno dos tres cuatro cinco"
        esc2 = BinderNode(title="Escena 2", type="Text", parent_uuid=cap1.uuid)
        esc2._content_rtf = "Seis siete ocho nueve diez"

        cap1.children = [esc1, esc2]
        draft.children = [cap1]
        self.project.root_nodes = [draft]
        self.project.draft_node = draft

        self.assertEqual(esc1.word_count(), 5)
        self.assertEqual(esc2.word_count(), 5)
        # Total acumulado recursivo
        self.assertEqual(cap1.total_word_count(), 10)
        self.assertEqual(draft.total_word_count(), 10)

    def test_xml_serialization_roundtrip(self):
        xml_file = self.project_path / "TestBook.escrx"
        self.project.path.mkdir(parents=True, exist_ok=True)

        draft = BinderNode(title="Manuscrito", type="DraftFolder")
        esc1 = BinderNode(title="Escena A", type="Text", parent_uuid=draft.uuid)
        esc1.section_type = "Scene"
        esc1.label = "Protagonista"
        esc1.status = "Primer Borrador"
        draft.children.append(esc1)
        self.project.root_nodes = [draft]
        self.project.draft_node = draft

        # Guardar XML
        XmlEngineV2.save_project_xml(self.project, xml_file)
        self.assertTrue(xml_file.exists())

        # Cargar en un nuevo proyecto
        loaded_proj = EscritorioProjectV2(self.project_path)
        success = XmlEngineV2.load_project_xml(loaded_proj, xml_file)
        self.assertTrue(success)
        self.assertEqual(len(loaded_proj.root_nodes), 1)
        self.assertEqual(loaded_proj.root_nodes[0].title, "Manuscrito")
        self.assertEqual(len(loaded_proj.root_nodes[0].children), 1)
        self.assertEqual(loaded_proj.root_nodes[0].children[0].title, "Escena A")
        self.assertEqual(loaded_proj.root_nodes[0].children[0].label, "Protagonista")

    def test_backup_manager_zip_and_sha256(self):
        backup_dir = self.test_dir / "backups"
        mgr = BackupManager(backup_dir, max_backups=3)

        self.project.path.mkdir(parents=True, exist_ok=True)
        (self.project.path / "file1.txt").write_text("Contenido para backup", encoding="utf-8")

        zip_path = mgr.create_backup(self.project.path, prefix="test")
        self.assertIsNotNone(zip_path)
        self.assertTrue(zip_path.exists())

        backups = mgr.list_backups()
        self.assertEqual(len(backups), 1)
        self.assertTrue("sha256" in backups[0])


if __name__ == "__main__":
    unittest.main()
