"""
ESCRITORIO v2.0 - Compiler Pipeline Test Suite
Pruebas de integración para exportadores multiformato (DOCX, PDF, EPUB, RTF, MD).
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from src.core.project_v2 import EscritorioProjectV2, BinderNode
from src.compile.compile_engine import CompileEngineV2


class TestCompilePipelineV2(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="escr_compile_test_"))
        self.project_path = self.test_dir / "CompileBook.escr"
        self.project_path.mkdir(parents=True, exist_ok=True)
        self.project = EscritorioProjectV2(self.project_path)

        # Preparar manuscrito con capítulo y dos escenas
        draft = BinderNode(title="Manuscrito", type="DraftFolder")
        cap1 = BinderNode(title="Capítulo Primero", type="Folder", section_type="Chapter", parent_uuid=draft.uuid)
        esc1 = BinderNode(title="Escena 1", type="Text", section_type="Scene", parent_uuid=cap1.uuid)
        esc1._content_rtf = "El sol brillaba en lo alto de la colina verde."

        esc2 = BinderNode(title="Escena 2", type="Text", section_type="Scene", parent_uuid=cap1.uuid)
        esc2._content_rtf = "Un viento frío sopló de repente agitando las hojas."

        cap1.children = [esc1, esc2]
        draft.children = [cap1]
        self.project.root_nodes = [draft]
        self.project.draft_node = draft

        self.engine = CompileEngineV2(self.project)

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_compile_markdown(self):
        out_md = self.test_dir / "output.md"
        success = self.engine.compile_project(out_md, format_type="MD", title="Prueba Markdown", author="Tester")
        self.assertTrue(success)
        self.assertTrue(out_md.exists())
        text = out_md.read_text(encoding="utf-8")
        self.assertIn("CAPÍTULO 1: CAPÍTULO PRIMERO", text)
        self.assertIn("El sol brillaba", text)
        self.assertIn("* * *", text)

    def test_compile_rtf(self):
        out_rtf = self.test_dir / "output.rtf"
        success = self.engine.compile_project(out_rtf, format_type="RTF", title="Prueba RTF")
        self.assertTrue(success)
        self.assertTrue(out_rtf.exists())
        text = out_rtf.read_text(encoding="utf-8")
        self.assertIn(r"\rtf1", text)

    def test_compile_docx(self):
        out_docx = self.test_dir / "output.docx"
        success = self.engine.compile_project(out_docx, format_type="DOCX", title="Prueba DOCX")
        self.assertTrue(success)
        self.assertTrue(out_docx.exists())
        self.assertGreater(out_docx.stat().st_size, 500)

    def test_compile_pdf(self):
        out_pdf = self.test_dir / "output.pdf"
        success = self.engine.compile_project(out_pdf, format_type="PDF", title="Prueba PDF")
        self.assertTrue(success)
        self.assertTrue(out_pdf.exists())
        self.assertGreater(out_pdf.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
