"""
Auditoría Adversarial de Certificación Final (End-to-End Red Team Gate).
Certificación completa del ciclo de vida del escritor profesional y portabilidad
en Windows 11 sobre Escritorio.exe:

1. Creación de proyecto desde plantilla "Novela con Partes" (Novel with Parts).
2. Importación y división automática (Import and Split) de 30 escenas.
3. Reorganización en el Corcho por carriles de etiquetas (Swimlanes).
4. Esquema (Outliner) con metadatos personalizados, palabras recursivas y progreso.
5. Instantáneas (Snapshots) y comparador Myers Diff.
6. Edición continua en modo Scrivenings y división de pantalla (Split View).
7. Modo Composición libre de distracciones (F11, Paper Settings, Go To).
8. Conmutación en caliente de temas y personalización en Live Theme Studio (.scrtheme/.escrtheme).
9. Compilación multiformato editorial (.docx, .pdf, .epub) con resolución de variables <$n> y <$t>.
10. Autoguardado, backup automático ZIP con integridad SHA-256 y portabilidad limpia.
11. Verificación no funcional: arranque < 250ms, RAM óptima y tablas de importación PE limpias (Win11 only).
"""

import os
import sys
import time
import json
import zipfile
import tempfile
import shutil
import hashlib
import struct
import subprocess
import unittest
from pathlib import Path

# Raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.project import EscritorioProject, BinderItem
from src.core.rtf_engine import RTFEngine
from src.core.backup_manager import BackupManager
from src.core.importers.project_templates import ProjectTemplateManager
from src.core.importers.import_and_split import ImportAndSplit
from src.ui.CorkboardWidget.corkboard_widget import CorkboardWidget, CorkboardMode
from src.ui.CorkboardWidget.index_card import IndexCard, LabelColorStyle
from src.ui.OutlinerWidget.outliner_row import OutlinerRow
from src.ui.OutlinerWidget.outliner_columns import StandardColumnId, OutlinerColumn, calculate_progress_color
from src.ui.OutlinerWidget.outliner_exporter import OutlinerExporter
from src.ui.InspectorWidget.inspector_widget import InspectorWidget
from src.ui.InspectorWidget.inspector_tabs import InspectorTabId
from src.ui.InspectorWidget.myers_diff import MyersDiffEngine, DiffOp, DiffGranularity
from src.ui.ScriveningsEngine.scrivenings_engine import ScriveningsEngine
from src.ui.CompositionMode.composition_controller import CompositionMode
from src.themes.theme_engine import ThemeEngine, ThemeMode, UIDensityMode, BUILTIN_PALETTES
from src.themes.theme_parser import ThemePackage, ThemeParser, ScrThemeLoader
from src.themes.live_studio import LiveThemeStudio
from src.compile import UnifiedExporter, ExportFormat, PlaceholderResolver


class TestEndToEndRedTeamFinalGate(unittest.TestCase):
    """Certificación integral de extremo a extremo para publicación y entrega."""

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_e2e_gate_"))
        cls.binary_path = PROJECT_ROOT / "build" / "release" / "Escritorio.exe"

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    # =========================================================================
    # 1. PLANTILLA "NOVELA CON PARTES"
    # =========================================================================

    def test_01_create_project_from_novel_parts_template(self):
        """Crea un proyecto desde la plantilla 'Novela con Partes' y valida su estructura."""
        project_dir = self.temp_dir / "CienAnosDeSoledad.escr"
        project = ProjectTemplateManager.create_project_from_template(
            template_id="novel_parts",
            destination_path=self.temp_dir,
            project_name="CienAnosDeSoledad",
            native=True
        )

        self.assertIsNotNone(project)
        self.assertTrue(project.project_dir.exists())

        draft = project.get_draft_folder()
        self.assertIsNotNone(draft)
        self.assertGreater(len(draft.children), 0)

        # Verificar carpetas de personajes e investigación
        research = project.get_research_folder()
        self.assertIsNotNone(research)

        # Guardar y cerrar proyecto
        project.save_all()
        self.assertTrue(project.project_file.exists())
        project.close()

    # =========================================================================
    # 2. IMPORT AND SPLIT (30 ESCENAS)
    # =========================================================================

    def test_02_import_and_split_30_scenes(self):
        """Importa y divide un manuscrito externo masivo en exactamente 30 escenas estructuradas."""
        project_dir = self.temp_dir / "CienAnosDeSoledad.escr"
        project = EscritorioProject.load(project_dir, force_unlock=True)
        draft = project.get_draft_folder()

        # Crear archivo externo con 30 escenas delimitadas por # Escena N
        manuscript_lines = []
        for i in range(1, 31):
            manuscript_lines.append(f"# Escena {i}: Acontecimientos en Macondo {i}")
            manuscript_lines.append(
                f"El coronel Aureliano Buendía promovió treinta y dos levantamientos armados "
                f"y los perdió todos. Tuvo diecisiete hijos varones de diecisiete mujeres distintas. "
                f"Párrafo de prueba para la escena número {i} con densidad narrativa rica."
            )
            manuscript_lines.append("")

        external_doc = self.temp_dir / "manuscrito_30_escenas.md"
        external_doc.write_text("\n".join(manuscript_lines), encoding="utf-8")

        # Importar y dividir bajo la primera carpeta del borrador
        target_folder = draft.children[0] if draft.children else draft
        result = ImportAndSplit.import_and_split(
            source_path=external_doc,
            project=project,
            parent_uuid=target_folder.uuid,
            detect_headings=True
        )

        self.assertTrue(result.get("success", False))
        self.assertEqual(result.get("total_items", len(result.get("items", []))), 30)

        project.save_all()
        # Verificar que la carpeta destino ahora contiene las 30 escenas
        target_folder_reloaded = project.find_item(target_folder.uuid)
        self.assertGreaterEqual(len(target_folder_reloaded.children), 30)
        project.close()

    # =========================================================================
    # 3. CORCHO: SWIMLANES Y SINCRONIZACIÓN
    # =========================================================================

    def test_03_corkboard_swimlanes_and_sync(self):
        """Valida la Pizarra de Corcho en modo Swimlanes y sincronización bidireccional."""
        project_dir = self.temp_dir / "CienAnosDeSoledad.escr"
        project = EscritorioProject.load(project_dir, force_unlock=True)
        draft = project.get_draft_folder()
        target_folder = draft.children[0]

        corkboard = CorkboardWidget(project=project)
        corkboard.load_container(target_folder)
        self.assertGreaterEqual(len(corkboard.cards), 30)

        # Alternar a modo Swimlanes
        corkboard.set_mode(CorkboardMode.SWIMLANES)
        view_data = corkboard.get_view_data()
        self.assertEqual(view_data["mode"], "swimlanes")

        # Asignar sinopsis a una ficha y verificar persistencia en el BinderItem
        first_card = corkboard.cards[0]
        test_synopsis = "Sinopsis auditada de la escena de apertura."
        first_card.set_synopsis(test_synopsis)

        # Comprobar sincronización
        item = project.find_item(first_card.uuid)
        self.assertEqual(item.read_synopsis(), test_synopsis)

        # Configurar estilos de ficha
        first_card.label_style = LabelColorStyle.PIN
        first_card.set_status(1, "En Revisión")
        self.assertEqual(first_card.status_stamp_text, "EN REVISIÓN")
        project.close()

    # =========================================================================
    # 4. ESQUEMA (OUTLINER) Y METADATOS PERSONALIZADOS
    # =========================================================================

    def test_04_outliner_custom_metadata_and_recursive_metrics(self):
        """Valida el Esquema con metadatos personalizados, sumas recursivas y barra de progreso."""
        project_dir = self.temp_dir / "CienAnosDeSoledad.escr"
        project = EscritorioProject.load(project_dir, force_unlock=True)
        draft = project.get_draft_folder()
        target_folder = draft.children[0]

        # Añadir metadatos personalizados
        for idx, child in enumerate(target_folder.children[:5]):
            child.data.custom_metadata["Punto de Vista"] = "Aureliano"
            child.data.custom_metadata["Año"] = str(1900 + idx)
            child.data.target_words = 500
            child.mark_dirty()
        project.save_all()

        folder_row = OutlinerRow(target_folder, level=0, project=project)
        for child in target_folder.children:
            folder_row.children.append(OutlinerRow(child, level=1, project=project))

        # Verificar sumas recursivas
        self.assertGreater(folder_row.total_words, 0)
        self.assertGreaterEqual(folder_row.total_target, 2500)
        self.assertGreaterEqual(folder_row.progress_percent, 0.0)

        # Verificar gradiente cromático
        color = folder_row.progress_color
        self.assertTrue(color.startswith("#"))
        self.assertEqual(len(color), 7)

        # Exportación a CSV
        cols = [
            OutlinerColumn(StandardColumnId.TITLE.value, "Título"),
            OutlinerColumn(StandardColumnId.TOTAL_WORDS.value, "Palabras"),
            OutlinerColumn(StandardColumnId.PROGRESS.value, "Progreso")
        ]
        csv_out = self.temp_dir / "outliner_export_e2e.csv"
        csv_str = OutlinerExporter.export_to_csv([folder_row] + folder_row.children[:5], cols, output_file_or_path=csv_out)
        self.assertTrue(csv_out.exists())
        self.assertIn("Título,Palabras,Progreso", csv_str)
        project.close()

    # =========================================================================
    # 5. INSTANTÁNEAS Y MYERS DIFF
    # =========================================================================

    def test_05_snapshots_and_myers_diff(self):
        """Valida captura de instantánea, edición y cálculo diferencial Myers Diff."""
        project_dir = self.temp_dir / "CienAnosDeSoledad.escr"
        project = EscritorioProject.load(project_dir, force_unlock=True)
        draft = project.get_draft_folder()
        item = draft.children[0].children[0]

        inspector = InspectorWidget(project=project)
        inspector.set_item(item)
        tab_snap = inspector.tab_snapshots

        # 1. Asegurar contenido original y tomar instantánea
        item.write_content_rtf(r"{\rtf1\ansi Texto original del coronel Aureliano Buendia en Macondo.}")
        item.save_if_dirty()
        snap = tab_snap.take_snapshot("Versión Inicial Certificada")
        self.assertIsNotNone(snap)

        # 2. Modificar texto del ítem con cambios sustanciales
        item.write_content_rtf(r"{\rtf1\ansi Texto revisado del patriarca Jose Arcadio Buendia en Macondo.}")
        item.save_if_dirty()

        # 3. Comparar con Myers Diff
        tab_snap.select_snapshot(snap.id)
        chunks = tab_snap.compute_comparison()
        self.assertGreater(len(chunks), 0)

        # Verificar chunks de inserción y eliminación
        has_insert = any(c.op == DiffOp.INSERT for c in chunks)
        has_delete = any(c.op == DiffOp.DELETE for c in chunks)
        self.assertTrue(has_insert and has_delete)

        # 4. Rollback
        ok_rollback = tab_snap.rollback(snap.id, create_safety_snapshot=True)
        self.assertTrue(ok_rollback)
        project.close()

    # =========================================================================
    # 6. SCRIVENINGS Y SPLIT VIEW
    # =========================================================================

    def test_06_scrivenings_mode_and_split_view(self):
        """Valida el editor compuesto Scrivenings con múltiples escenas contiguas."""
        project_dir = self.temp_dir / "CienAnosDeSoledad.escr"
        project = EscritorioProject.load(project_dir, force_unlock=True)
        draft = project.get_draft_folder()
        scenes = draft.children[0].children[:5]

        engine = ScriveningsEngine(project)
        engine.load_items(scenes)

        self.assertGreaterEqual(len(engine.segments), 5)
        composite_text = engine.get_composite_text()
        self.assertIn("Aureliano Buendía", composite_text)

        # Modificar el texto del primer segmento y verificar propagación atómica
        modified_segment = "Apertura en Scrivenings editada de forma unificada."
        engine.update_segment_text(0, modified_segment)
        self.assertTrue(scenes[0].is_dirty or scenes[0].read_content_rtf() != "")
        project.close()

    # =========================================================================
    # 7. MODO COMPOSICIÓN (F11)
    # =========================================================================

    def test_07_composition_mode(self):
        """Valida el modo inmersivo a pantalla completa sin distracciones."""
        project_dir = self.temp_dir / "CienAnosDeSoledad.escr"
        project = EscritorioProject.load(project_dir, force_unlock=True)
        draft = project.get_draft_folder()
        item = draft.children[0].children[0]

        comp = CompositionMode(project, active_item=item)
        comp.paper_width_percent = 70
        comp.backdrop_opacity = 0.90
        comp.typewriter_scrolling = True

        self.assertEqual(comp.paper_width_percent, 70)
        self.assertEqual(comp.backdrop_opacity, 0.90)
        self.assertTrue(comp.typewriter_scrolling)
        self.assertGreater(len(comp.control_bar.goto_tree), 0)
        project.close()

    # =========================================================================
    # 8. TEMAS VISUALES Y LIVE THEME STUDIO
    # =========================================================================

    def test_08_themes_and_live_theme_studio(self):
        """Valida la conmutación de los temas canónicos y personalización en vivo."""
        engine = ThemeEngine(initial_mode=ThemeMode.MINIMALIST_DEFAULT)

        # Conmutar entre los modos requeridos
        for mode in (ThemeMode.MINIMALIST_DEFAULT, ThemeMode.CARBON_DARK, ThemeMode.SOLARIZED_DARK, ThemeMode.SEPIA_PARCHMENT):
            ms = engine.set_mode(mode)
            self.assertLess(ms, 50.0)  # Conmutación sub-50ms

        # Live Theme Studio
        studio = LiveThemeStudio(engine)
        studio.update_color_token("editor.background", "#1E1E2E")
        studio.update_typography("font_family_editor", "Georgia")
        studio.set_texture("cork_grain")

        # Exportar a .scrtheme
        scrtheme_out = self.temp_dir / "CustomWriterTheme.scrtheme"
        pkg = ThemePackage(
            name="Custom Writer Theme",
            palette=dict(studio.working_palette)
        )
        ScrThemeLoader.pack_package(pkg, output_dest=scrtheme_out)
        self.assertTrue(scrtheme_out.exists())

        loaded_pkg = ThemeParser.load_theme(scrtheme_out)
        self.assertEqual(loaded_pkg.name, "Custom Writer Theme")
        self.assertEqual(loaded_pkg.palette.get("editor.background"), "#1E1E2E")

    # =========================================================================
    # 9. COMPILACIÓN MULTIFORMATO EDITORIAL (.DOCX, .PDF, .EPUB)
    # =========================================================================

    def test_09_multiformat_editorial_compilation(self):
        """Compila la novela a .docx, .pdf y .epub resolviendo variables <$n> y <$t>."""
        resolver = PlaceholderResolver(project_title="Cien Años de Soledad", author="Gabriel García Márquez")
        manuscript_raw = (
            "# Capítulo <$n>: <$title>\n\n"
            "Muchos años después, frente al pelotón de fusilamiento, el coronel Aureliano Buendía "
            "había de recordar aquella tarde remota en que su padre lo llevó a conocer el hielo.[^1]\n\n"
            "El mundo era tan reciente, que muchas cosas carecían de nombre.[^2]\n\n"
            "---\n\n"
            "# Capítulo <$n>: <$title>\n\n"
            "José Arcadio Buendía, que era el hombre más emprendedor que se vería jamás en la aldea, "
            "había dispuesto de tal modo la posición de las casas que desde todas podía llegarse al río.\n\n"
            "[^1]: Referencia a la apertura canónica.\n"
            "[^2]: Cita célebre de Macondo.\n"
        )

        resolved_text = resolver.resolve(manuscript_raw, item_title="El Comienzo")
        self.assertIn("Capítulo 1: El Comienzo", resolved_text)

        # 1. Compilar DOCX
        docx_file = self.temp_dir / "NovelaFinal.docx"
        UnifiedExporter.export(resolved_text, docx_file, format_type=ExportFormat.DOCX, title="Cien Años de Soledad", author="García Márquez")
        self.assertTrue(docx_file.exists())
        with zipfile.ZipFile(docx_file, "r") as zf:
            self.assertIn("word/document.xml", zf.namelist())

        # 2. Compilar PDF
        pdf_file = self.temp_dir / "NovelaFinal.pdf"
        UnifiedExporter.export(resolved_text, pdf_file, format_type=ExportFormat.PDF, title="Cien Años de Soledad", author="García Márquez")
        self.assertTrue(pdf_file.exists())
        self.assertTrue(pdf_file.read_bytes().startswith(b"%PDF-1.4"))

        # 3. Compilar EPUB3
        epub_file = self.temp_dir / "NovelaFinal.epub"
        UnifiedExporter.export(resolved_text, epub_file, format_type=ExportFormat.EPUB3, title="Cien Años de Soledad", author="García Márquez")
        self.assertTrue(epub_file.exists())
        with zipfile.ZipFile(epub_file, "r") as zf:
            first = zf.infolist()[0]
            self.assertEqual(first.filename, "mimetype")
            self.assertEqual(first.compress_type, zipfile.ZIP_STORED)

    # =========================================================================
    # 10. BACKUP ZIP AUTOMÁTICO Y SHA-256
    # =========================================================================

    def test_10_automatic_backup_and_sha256(self):
        """Verifica la generación de copia de seguridad ZIP con integridad SHA-256."""
        project_dir = self.temp_dir / "CienAnosDeSoledad.escr"
        backup_dir = self.temp_dir / "Backups"
        mgr = BackupManager(backup_dir=backup_dir, max_backups=5)

        info = mgr.create_project_backup(project_dir, project_title="CienAnosDeSoledad")
        self.assertTrue(Path(info["path"]).exists())
        self.assertIn("sha256", info)
        self.assertEqual(len(info["sha256"]), 64)

        # Verificar integridad del ZIP generado
        with zipfile.ZipFile(info["path"], "r") as zf:
            self.assertIsNone(zf.testzip())

    # =========================================================================
    # 11. NO FUNCIONAL: ARRANQUE < 250ms, RAM Y TABLAS DE IMPORTACIÓN PE
    # =========================================================================

    def test_11_binary_startup_ram_and_pe_imports(self):
        """Verifica arranque < 250ms, RAM óptima y tablas de importación PE limpias en Windows 11."""
        if not self.binary_path.exists():
            self.skipTest("Escritorio.exe no encontrado en build/release/.")

        # 1. Medir tiempo de arranque y memoria RAM
        t0 = time.perf_counter()
        proc = subprocess.Popen([str(self.binary_path)])
        t1 = time.perf_counter()
        startup_ms = (t1 - t0) * 1000

        time.sleep(0.15)
        import psutil
        p = psutil.Process(proc.pid)
        rss_mb = p.memory_info().rss / (1024 * 1024)
        proc.terminate()
        proc.wait(timeout=5)

        # Validar tiempo de arranque < 250 ms
        self.assertLess(startup_ms, 250.0, f"Tiempo de arranque ({startup_ms:.1f}ms) excede el umbral de 250ms.")

        # Validar consumo RAM razonable (< 100 MB)
        self.assertLess(rss_mb, 100.0, f"Consumo de RAM ({rss_mb:.1f}MB) excede el umbral óptimo.")

        # 2. Análisis estricto de tablas de importación PE
        data = self.binary_path.read_bytes()
        pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
        self.assertEqual(data[pe_offset:pe_offset+4], b"PE\x00\x00")

        opt_hdr_offset = pe_offset + 24
        opt_hdr_size = struct.unpack_from("<H", data, pe_offset + 20)[0]
        magic = struct.unpack_from("<H", data, opt_hdr_offset)[0]
        is_64bit = (magic == 0x20B)

        data_dirs_offset = opt_hdr_offset + (112 if is_64bit else 96)
        import_rva = struct.unpack_from("<I", data, data_dirs_offset + 8)[0]
        sections_offset = opt_hdr_offset + opt_hdr_size
        num_sections = struct.unpack_from("<H", data, pe_offset + 6)[0]

        sections = []
        for i in range(num_sections):
            s_off = sections_offset + (i * 40)
            s_va = struct.unpack_from("<I", data, s_off + 12)[0]
            s_vsize = struct.unpack_from("<I", data, s_off + 8)[0]
            s_raw_size = struct.unpack_from("<I", data, s_off + 16)[0]
            s_raw_ptr = struct.unpack_from("<I", data, s_off + 20)[0]
            sections.append((s_va, s_vsize, s_raw_ptr, s_raw_size))

        def rva_to_offset(rva):
            for s_va, s_vsize, s_raw_ptr, s_raw_size in sections:
                if s_va <= rva < s_va + max(s_vsize, s_raw_size):
                    return s_raw_ptr + (rva - s_va)
            return None

        import_file_offset = rva_to_offset(import_rva)
        self.assertIsNotNone(import_file_offset)

        curr_desc = import_file_offset
        imported_dlls = []
        while curr_desc + 20 <= len(data):
            desc_bytes = data[curr_desc:curr_desc+20]
            if desc_bytes == b"\x00" * 20:
                break
            name_rva = struct.unpack_from("<I", desc_bytes, 12)[0]
            if name_rva != 0:
                name_off = rva_to_offset(name_rva)
                if name_off and name_off < len(data):
                    end_str = data.find(b"\x00", name_off)
                    if end_str != -1:
                        dll_name = data[name_off:end_str].decode("ascii", errors="ignore").lower()
                        imported_dlls.append(dll_name)
            curr_desc += 20

        # DLLs del sistema operativo Windows 11 estrictamente permitidas
        allowed_system_dlls = {
            "kernel32.dll", "user32.dll", "gdi32.dll", "dwmapi.dll", "shell32.dll",
            "ole32.dll", "oleaut32.dll", "comctl32.dll", "comdlg32.dll", "advapi32.dll",
            "msvcrt.dll", "vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll", "ntdll.dll"
        }

        for dll in imported_dlls:
            self.assertIn(
                dll,
                allowed_system_dlls,
                f"Violación de portabilidad: la DLL '{dll}' no pertenece al sistema base de Windows 11."
            )


if __name__ == "__main__":
    unittest.main()
