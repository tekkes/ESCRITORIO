"""
Red Team Test: Pipeline de Compilación y Placeholders
Valida el ensamblaje de borradores, filtrado de nodos y resolución de comodines editoriales.
"""

import unittest
import tempfile
from pathlib import Path
from src.core.project import EscritorioProject
from src.core.rtf_engine import RTFEngine
from src.compile.compile_engine import CompileEngine, CompileConfig
from src.compile.placeholders import PlaceholderResolver

class TestCompilePipeline(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_placeholder_resolution(self):
        resolver = PlaceholderResolver({"title": "Odisea en Marte", "author": "H. G. Wells"})
        resolved = resolver.resolve("Obra: <$projecttitle> por <$author> - Cap <$n> y <$n>", item_title="Sección")
        self.assertIn("Odisea en Marte", resolved)
        self.assertIn("H. G. Wells", resolved)
        self.assertIn("Cap 1 y 2", resolved)

    def test_manuscript_compile_assembly(self):
        proj_path = self.base_path / "CompileTest.scriv"
        proj = EscritorioProject.create_new(proj_path, title="Antología Espacial")

        draft = proj.root_items[0]
        ch1 = proj.add_item(draft.uuid, "El Viaje", item_type="Folder")
        ch1.data.section_type = "Chapter"

        sc1 = proj.add_item(ch1.uuid, "Despegue", item_type="Text")
        sc1.data.section_type = "Scene"
        sc1.write_content_rtf(RTFEngine.plain_text_to_rtf("Los motores rugieron en la plataforma."))

        engine = CompileEngine(proj, CompileConfig(author_name="Isaac Asimov"))
        compiled = engine.assemble_manuscript()

        self.assertIn("# Capítulo 1: El Viaje", compiled)
        self.assertIn("Los motores rugieron en la plataforma.", compiled)

if __name__ == "__main__":
    unittest.main()
