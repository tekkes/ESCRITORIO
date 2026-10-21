"""
Red Team Test: Fidelidad Round-Trip de Formato Scrivener 3
Valida que un proyecto generado cumpla con el estándar XML .scrivx y su almacenamiento interno en Files/Data/<UUID>/.
"""

import unittest
import tempfile
from pathlib import Path
from src.core.project import EscritorioProject
from src.core.rtf_engine import RTFEngine

class TestScrivenerFidelity(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_project_creation_and_reopen(self):
        proj_path = self.base_path / "MiNovela.scriv"
        proj = EscritorioProject.create_new(proj_path, title="El Misterio de la Alhambra")

        self.assertEqual(len(proj.root_items), 3)
        self.assertEqual(proj.root_items[0].title, "Manuscrito")
        self.assertEqual(proj.root_items[1].title, "Investigación")
        self.assertEqual(proj.root_items[2].title, "Papelera")

        # Añadir un capítulo y una escena
        draft = proj.root_items[0]
        chapter = proj.add_item(draft.uuid, "Capítulo 1", item_type="Folder")
        scene = proj.add_item(chapter.uuid, "Escena 1.1", item_type="Text")

        sample_text = "La noche caía sobre las torres con una quietud espectral. Todo comenzaba aquí."
        scene.write_content_rtf(RTFEngine.plain_text_to_rtf(sample_text))
        scene.write_synopsis("Primera escena introductoria.")

        # Reabrir desde disco
        reopened = EscritorioProject(proj_path)
        reopened.load()

        self.assertEqual(reopened.project_data["title"], "El Misterio de la Alhambra")
        loaded_scene = reopened.get_item(scene.uuid)
        self.assertIsNotNone(loaded_scene)
        self.assertEqual(loaded_scene.title, "Escena 1.1")
        self.assertEqual(loaded_scene.read_synopsis(), "Primera escena introductoria.")

        raw_text = RTFEngine.rtf_to_plain_text(loaded_scene.read_content_rtf())
        self.assertIn("La noche caía sobre las torres", raw_text)
        self.assertGreater(loaded_scene.get_word_count(), 10)

if __name__ == "__main__":
    unittest.main()
