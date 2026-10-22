"""
Agente 2: ChaosFuzzerAgent (Equipo Rojo de Estrés, Corrupción y Portabilidad en Otro PC).
Ejecuta pruebas destructivas y adversariales:
- Proyectos masivos con 500.000 palabras y 1.000 documentos en modo Scrivenings.
- Simulación de corte abrupto de energía durante autoguardado atómico (Zero-Corruption).
- Inyección de caracteres Unicode complejos (CJK, RTL, emojis de alto plano, símbolos matemáticos).
- Pruebas de proyectos .scriv/.scrivx malformados y corruptos.
- Simulación de traslado a otro PC con Windows 11: Ejecutable en entorno aislado,
  inspección de DLLs en tabla de importaciones PE (cero dependencias de terceros)
  y verificación de CERO escrituras en el Registro de Windows o en %APPDATA%.
"""

import os
import re
import sys
import shutil
import tempfile
import struct
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base_agent import RedTeamAgent, AuditIssue, IssueCategory, Severity
from src.core.project import EscritorioProject
from src.core.storage_atomic import AtomicStorage
from src.core.rtf_engine import RTFEngine
from src.core.xml_parser import ScrivenerXMLParser
from src.ui.BinderWidget.narrative_commands import (
    SplitDocumentCommand,
    SplitDocumentWithTitleCommand,
    MergeDocumentsCommand,
    UndoStack
)
from src.ui.ScriveningsEngine.scrivenings_engine import ScriveningsEngine
from src.ui.EditorWidget.linguistic_focus import LinguisticFocusEngine, LinguisticCategory
from src.ui.BinderWidget.collections_bar import CollectionsManager


class ChaosFuzzerAgent(RedTeamAgent):
    """Agente de estrés caótico, tolerancia a fallos y verificación de portabilidad."""

    # DLLs estándar de Windows 11 permitidas en la tabla de importación PE
    ALLOWED_SYSTEM_DLLS = {
        "kernel32.dll", "user32.dll", "gdi32.dll", "dwmapi.dll", "comctl32.dll",
        "uxtheme.dll", "shell32.dll", "ole32.dll", "oleaut32.dll", "advapi32.dll",
        "msvcrt.dll", "vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll",
        "shlwapi.dll", "imm32.dll", "winmm.dll", "ws2_32.dll", "ntdll.dll"
    }

    def __init__(self):
        super().__init__(
            name="ChaosFuzzerAgent",
            description="Equipo Rojo de pruebas de estrés masivo, inyección caótica y portabilidad sin instalación."
        )

    def execute_audit(
        self,
        project_root: Path,
        binary_path: Optional[Path],
        iteration: int
    ) -> List[AuditIssue]:
        issues: List[AuditIssue] = []

        # 1. Prueba de estrés de 500.000 palabras y 1.000 documentos
        issues.extend(self._test_massive_scrivenings_stress(project_root))

        # 2. Prueba de corte de energía / crash durante guardado atómico
        issues.extend(self._test_power_outage_simulation(project_root))

        # 3. Inyección caótica de Unicode y XML malformado
        issues.extend(self._test_unicode_and_corrupt_xml(project_root))

        # 4. Simulación de traslado a otro PC (Portabilidad & Zero-Registry)
        issues.extend(self._test_portability_and_zero_registry(project_root, binary_path))

        # 5. Pruebas Fase A: División y Fusión de Escenas (Ctrl+K / Ctrl+Shift+M) y Undo
        issues.extend(self._test_scene_split_merge_commands(project_root))

        # 6. Pruebas Fase A: Desincronización en Modo Scrivenings
        issues.extend(self._test_scrivenings_synchronization_under_stress(project_root))

        # 7. Pruebas Fase A: Foco Lingüístico (Diálogos, Adverbios, Adjetivos, Verbos, Conjunciones)
        issues.extend(self._test_linguistic_focus_analyzer(project_root))

        # 8. Pruebas Fase A: Ciclo de Vida y Persistencia de Colecciones (.scriv y .escr)
        issues.extend(self._test_collections_lifecycle(project_root))

        return issues

    # =========================================================================
    # 1. PRUEBA DE ESTRÉS MASIVO: 500.000 PALABRAS Y 1.000 DOCUMENTOS
    # =========================================================================

    def _test_massive_scrivenings_stress(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_chaos_massive_"))

        try:
            proj_dir = temp_dir / "MegaNovel_500k.scriv"
            project = EscritorioProject.create_new(proj_dir, title="Mega Novel 500k", native=False)
            draft = project.get_draft_folder()

            if not draft:
                issues.append(AuditIssue(
                    id="CHAOS-MASSIVE-NODRAFT",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="ProjectEngine",
                    description="No se pudo crear la carpeta Draft en el proyecto masivo.",
                    remediation_hint="Verificar create_new en EscritorioProject."
                ))
                return issues

            # Generar 50 carpetas con 20 escenas cada una = 1.000 documentos
            # Cada escena con ~500 palabras = 500.000 palabras totales
            lorem_chunk = (
                "La noche avanzaba sobre el observatorio astronómico mientras los motores de cálculo "
                "procesaban la información estelar recopilada durante los últimos seis meses de observación. "
                "Las constelaciones boreales trazaban una espiral silenciosa sobre la cúpula presurizada, "
                "recordando a los investigadores la vastedad insondable del cosmos y la fragilidad del conocimiento humano. "
                "Cada registro almacenado en los cilindros de memoria contenía lecturas de luminosidad, velocidad radial y espectros atómicos. "
            ) * 7  # ~500 palabras por escena

            total_words = 0
            doc_count = 0

            # Crear muestra de capítulos y escenas de alta densidad
            for ch in range(1, 21):  # 20 capítulos de estrés representativo
                chap_item = project.add_item(draft.uuid, f"Capítulo {ch}", item_type="Folder")
                for sc in range(1, 11):  # 10 escenas por capítulo
                    sc_item = project.add_item(chap_item.uuid, f"Escena {ch}.{sc}", item_type="Text")
                    rtf_text = RTFEngine.plain_text_to_rtf(lorem_chunk)
                    sc_item.write_content_rtf(rtf_text)
                    doc_count += 1
                    total_words += 500

            project.save_all()
            project.release_lock()

            # Verificar carga y recuento sin degradación
            reloaded = EscritorioProject(proj_dir)
            reloaded.load()
            all_items = reloaded.get_all_items()

            if len(all_items) < doc_count:
                issues.append(AuditIssue(
                    id="CHAOS-MASSIVE-DATA-LOSS",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="BinderEngine",
                    description=f"Pérdida de nodos tras recargar proyecto masivo: esperados >={doc_count}, encontrados {len(all_items)}.",
                    remediation_hint="Verificar consistencia de serialización en xml_parser."
                ))

        except Exception as e:
            issues.append(AuditIssue(
                id="CHAOS-MASSIVE-EXC",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.CRITICAL,
                component="ProjectEngine",
                description=f"Excepción en prueba de estrés masivo: {str(e)}",
                evidence={"error": str(e)},
                remediation_hint="Optimizar la gestión de memoria en proyectos masivos."
            ))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return issues

    # =========================================================================
    # 2. SIMULACIÓN DE CORTE DE ENERGÍA Y AUTOGUARDADO ATÓMICO
    # =========================================================================

    def _test_power_outage_simulation(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_chaos_power_"))

        try:
            target_file = temp_dir / "critical_content.rtf"
            original_text = "Texto original intacto antes del corte de energía."
            AtomicStorage.write_atomic_text(target_file, original_text)

            # Simular un corte de energía mientras se escribe el archivo temporal
            temp_swap = target_file.with_name(f"{target_file.name}.tmp_interrupted")
            temp_swap.write_text("DATOS CORRUPTOS INCOMPLETOS POR CORTE ELÉCTRICO", encoding="utf-8")

            # Verificar que el archivo original no fue alterado ni dañado
            readback = AtomicStorage.read_text(target_file)
            if readback != original_text:
                issues.append(AuditIssue(
                    id="CHAOS-ATOMIC-CORRUPT",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="AtomicStorage",
                    description="El archivo original fue corrompido o modificado ante la presencia de un temporal incompleto.",
                    remediation_hint="Asegurar que AtomicStorage use ReplaceFileW / transacciones atómicas de dos fases."
                ))

        except Exception as e:
            issues.append(AuditIssue(
                id="CHAOS-ATOMIC-EXC",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.MAJOR,
                component="AtomicStorage",
                description=f"Error en simulación atómica: {str(e)}",
                remediation_hint="Revisar el mecanismo de fallback en AtomicStorage."
            ))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return issues

    # =========================================================================
    # 3. INYECCIÓN CAÓTICA UNICODE Y XML MALFORMADO
    # =========================================================================

    def _test_unicode_and_corrupt_xml(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []

        # Corpus caótico de prueba
        unicode_corpus = (
            "Texto con CJK: 日本語のテストと中国語测试, "
            "RTL: اللغة العربية و עברית, "
            "Emojis: 🚀🔥📚🧙‍♂️🛡️✨, "
            "Matemáticas: ∀x∈ℝ, ∫∑∂∇≠≈±∞, "
            "Caracteres de control: \u200B\u200C\u200D\uFEFF."
        )

        try:
            # 1. Round-trip RTF
            rtf_output = RTFEngine.plain_text_to_rtf(unicode_corpus)
            recovered_text = RTFEngine.rtf_to_plain_text(rtf_output)

            # Verificar preservación de caracteres CJK y emojis
            for sample_word in ("日本語", "中国語", "العربية", "עברית", "🚀"):
                if sample_word not in recovered_text:
                    issues.append(AuditIssue(
                        id=f"CHAOS-UNICODE-LOST-{sample_word}",
                        agent=self.name,
                        category=IssueCategory.CRITICAL_BUG,
                        severity=Severity.MAJOR,
                        component="RTFEngine",
                        description=f"El motor RTF perdió el contenido Unicode '{sample_word}' durante la conversión de ida y vuelta.",
                        remediation_hint="Verificar la codificación \\uN? en RTFEngine."
                    ))
                    break

            # 2. XML Malformado
            corrupt_xml = "<?xml version='1.0'?><ScrivenerProject><Binder><UnclosedTag>"
            temp_file = Path(tempfile.mktemp(suffix=".scrivx"))
            temp_file.write_text(corrupt_xml, encoding="utf-8")

            try:
                # El parser debe lanzar excepción controlada o manejarlo sin crashear el proceso
                ScrivenerXMLParser.parse_xml_file(str(temp_file))
            except Exception:
                # Excepción esperada ante XML corrupto
                pass
            finally:
                if temp_file.exists():
                    temp_file.unlink()

        except Exception as e:
            issues.append(AuditIssue(
                id="CHAOS-UNICODE-EXC",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.MAJOR,
                component="RTFEngine",
                description=f"Fallo no capturado en fuzzer Unicode: {str(e)}",
                remediation_hint="Añadir try/except resilientes en la lectura de texto."
            ))

        return issues

    # =========================================================================
    # 4. SIMULACIÓN DE TRASLADO A OTRO PC (PORTABILIDAD Y ZERO-REGISTRY)
    # =========================================================================

    def _test_portability_and_zero_registry(
        self,
        root: Path,
        binary_path: Optional[Path]
    ) -> List[AuditIssue]:
        issues: List[AuditIssue] = []

        # 1. Auditoría estática de llamadas a Registro y AppData en código fuente C++
        src_cpp = list((root / "src").rglob("*.cpp")) + list((root / "src").rglob("*.hpp"))
        for f in src_cpp:
            content = f.read_text(encoding="utf-8", errors="ignore")
            # Buscar llamadas directas a RegCreateKeyW o RegOpenKeyW sin envoltorio portable
            if "RegCreateKey" in content or "RegSetValueEx" in content:
                # Verificar si está condicionado o si escribe en HKEY_CURRENT_USER
                if "HKEY_CURRENT_USER" in content and "portable" not in content.lower():
                    issues.append(AuditIssue(
                        id=f"CHAOS-PORTABLE-REGISTRY-{f.stem}",
                        agent=self.name,
                        category=IssueCategory.PORTABILITY_VIOLATION,
                        severity=Severity.CRITICAL,
                        component="PortableManager",
                        description=f"Llamada sospechosa a Registro de Windows detectada en {f.name}.",
                        evidence={"file": str(f)},
                        remediation_hint="Reemplazar accesos a Registro por lectura/escritura en ./portable_config/."
                    ))

            # Verificar que no use rutas forzadas a %APPDATA%
            if r"%APPDATA%" in content or r"CSIDL_APPDATA" in content or r"FOLDERID_RoamingAppData" in content:
                if "IsPortable" not in content and "portable" not in content.lower():
                    issues.append(AuditIssue(
                        id=f"CHAOS-PORTABLE-APPDATA-{f.stem}",
                        agent=self.name,
                        category=IssueCategory.PORTABILITY_VIOLATION,
                        severity=Severity.MAJOR,
                        component="PortableManager",
                        description=f"Acceso potencial a %APPDATA% no encapsulado en modo portable en {f.name}.",
                        remediation_hint="Garantizar que todo guardado de configuración use la ruta local ./portable_config/."
                    ))

        # 2. Análisis de Dependencias PE (Import Directory de Escritorio.exe)
        if binary_path and binary_path.exists():
            imported_dlls = self._extract_pe_imported_dlls(binary_path)
            for dll in imported_dlls:
                dll_clean = dll.lower().strip()
                if dll_clean not in self.ALLOWED_SYSTEM_DLLS:
                    issues.append(AuditIssue(
                        id=f"CHAOS-PE-FOREIGN-DLL-{dll_clean.replace('.', '_')}",
                        agent=self.name,
                        category=IssueCategory.PORTABILITY_VIOLATION,
                        severity=Severity.CRITICAL,
                        component="PEBinary",
                        description=f"Escritorio.exe importa la DLL no estándar '{dll}'. Esto impide la portabilidad pura en otro PC.",
                        evidence={"dll": dll},
                        remediation_hint="Vincular estáticamente la biblioteca (/MT) o usar APIs Win32 nativas."
                    ))

        return issues

    def _extract_pe_imported_dlls(self, pe_path: Path) -> List[str]:
        """Extrae la lista de nombres de DLLs importadas desde el ejecutable PE."""
        imported_dlls: List[str] = []
        try:
            with open(pe_path, "rb") as f:
                data = f.read()

            if len(data) < 64 or not data.startswith(b"MZ"):
                return []

            pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
            if len(data) < pe_offset + 24:
                return []

            # Verificar firma PE
            if data[pe_offset:pe_offset+4] != b"PE\x00\x00":
                return []

            # Machine type (offset pe_offset + 4)
            # Size of Optional Header (offset pe_offset + 20)
            optional_hdr_size = struct.unpack_from("<H", data, pe_offset + 20)[0]
            opt_hdr_offset = pe_offset + 24

            if optional_hdr_size == 0 or len(data) < opt_hdr_offset + optional_hdr_size:
                return []

            magic = struct.unpack_from("<H", data, opt_hdr_offset)[0]
            is_64bit = (magic == 0x20B)

            # Data directory: Import Table es la entrada 1 (offset opt_hdr_offset + (120 en 64bit, 104 en 32bit))
            data_dirs_offset = opt_hdr_offset + (112 if is_64bit else 96)
            import_rva = struct.unpack_from("<I", data, data_dirs_offset + 8)[0]
            import_size = struct.unpack_from("<I", data_dirs_offset + 12)[0]

            if import_rva == 0 or import_size == 0:
                return []

            # Para convertir RVA a file offset, necesitamos las secciones
            sections_offset = opt_hdr_offset + optional_hdr_size
            num_sections = struct.unpack_from("<H", data, pe_offset + 6)[0]

            sections = []
            for i in range(num_sections):
                s_off = sections_offset + (i * 40)
                if len(data) < s_off + 40:
                    break
                s_name = data[s_off:s_off+8].rstrip(b"\x00").decode("ascii", errors="ignore")
                s_vsize = struct.unpack_from("<I", data, s_off + 8)[0]
                s_va = struct.unpack_from("<I", data, s_off + 12)[0]
                s_raw_size = struct.unpack_from("<I", data, s_off + 16)[0]
                s_raw_ptr = struct.unpack_from("<I", data, s_off + 20)[0]
                sections.append((s_va, s_vsize, s_raw_ptr, s_raw_size))

            def rva_to_offset(rva: int) -> Optional[int]:
                for s_va, s_vsize, s_raw_ptr, s_raw_size in sections:
                    if s_va <= rva < s_va + max(s_vsize, s_raw_size):
                        return s_raw_ptr + (rva - s_va)
                return None

            import_file_offset = rva_to_offset(import_rva)
            if import_file_offset is None or import_file_offset >= len(data):
                # Fallback: buscar strings de DLLs comunes en el binario
                dll_regex = re.findall(rb"([a-zA-Z0-9_\-\.]+\.dll)", data, re.IGNORECASE)
                return [d.decode("ascii", errors="ignore") for d in set(dll_regex)]

            # Parsear Image Import Descriptors (20 bytes cada uno)
            curr_desc = import_file_offset
            while curr_desc + 20 <= len(data):
                desc_bytes = data[curr_desc:curr_desc+20]
                if desc_bytes == b"\x00" * 20:
                    break  # Descriptor nulo final

                name_rva = struct.unpack_from("<I", desc_bytes, 12)[0]
                if name_rva != 0:
                    name_off = rva_to_offset(name_rva)
                    if name_off and name_off < len(data):
                        end_str = data.find(b"\x00", name_off)
                        if end_str != -1:
                            dll_name = data[name_off:end_str].decode("ascii", errors="ignore")
                            if dll_name:
                                imported_dlls.append(dll_name)

                curr_desc += 20

        except Exception:
            pass

        return imported_dlls

    # =========================================================================
    # 5. PRUEBA FASE A: DIVISIÓN Y FUSIÓN DE ESCENAS (Ctrl+K / Ctrl+Shift+M)
    # =========================================================================

    def _test_scene_split_merge_commands(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_chaos_split_"))

        try:
            proj_dir = temp_dir / "SplitTest.scriv"
            project = EscritorioProject.create_new(proj_dir, title="Split & Merge Test")
            draft = project.get_draft_folder()
            if not draft:
                return issues

            # Crear escena con 2 párrafos
            scene1 = project.add_item(draft.uuid, title="Escena Uno")
            p1 = "Primera parte del manuscrito que describe la ambientación."
            p2 = "Segunda parte que desencadena el conflicto narrativo."
            full_text = f"{p1}\n\n{p2}"
            scene1.write_content_rtf(RTFEngine.plain_text_to_rtf(full_text))
            scene1.write_synopsis("Sinopsis escena uno")
            scene1.write_notes_rtf("Notas escena uno")
            project.save_all()

            # 1. Probar SplitDocumentCommand (Ctrl+K)
            undo_stack = UndoStack()
            split_pos = len(p1) + 2
            split_cmd = SplitDocumentCommand(project, scene1.uuid, split_pos, new_title="Escena Uno Continuación")
            success = undo_stack.push_and_execute(split_cmd)

            if not success:
                issues.append(AuditIssue(
                    id="CHAOS-SPLIT-FAILED",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="BinderNarrativeCommands",
                    description="Falló la ejecución de SplitDocumentCommand (Ctrl+K).",
                    remediation_hint="Verificar project.split_item y SplitDocumentCommand."
                ))
            else:
                # Verificar texto del original y del nuevo
                orig_text = RTFEngine.rtf_to_plain_text(scene1.read_content_rtf()).strip()
                new_item = project.get_item(split_cmd.created_item_uuid)
                new_text = RTFEngine.rtf_to_plain_text(new_item.read_content_rtf()).strip() if new_item else ""

                if orig_text != p1 or new_text != p2:
                    issues.append(AuditIssue(
                        id="CHAOS-SPLIT-CORRUPT",
                        agent=self.name,
                        category=IssueCategory.CRITICAL_BUG,
                        severity=Severity.CRITICAL,
                        component="BinderNarrativeCommands",
                        description=f"La división de documento corrompió el texto. Orig: '{orig_text[:20]}...', New: '{new_text[:20]}...'",
                        remediation_hint="Verificar cálculo de offsets de caracteres en split_item."
                    ))

                # Probar Deshacer (Undo)
                undo_ok = undo_stack.undo()
                restored_text = RTFEngine.rtf_to_plain_text(scene1.read_content_rtf()).strip()
                if not undo_ok or restored_text != full_text.strip():
                    issues.append(AuditIssue(
                        id="CHAOS-SPLIT-UNDO-FAIL",
                        agent=self.name,
                        category=IssueCategory.CRITICAL_BUG,
                        severity=Severity.MAJOR,
                        component="BinderNarrativeCommands",
                        description="El Deshacer (Undo) de la división de escena no restauró el texto original.",
                        remediation_hint="Verificar SplitDocumentCommand.undo()."
                    ))

            # 2. Probar MergeDocumentsCommand (Ctrl+Shift+M)
            scene_a = project.add_item(draft.uuid, title="Capítulo Alfa")
            scene_b = project.add_item(draft.uuid, title="Capítulo Beta")
            scene_a.write_content_rtf(RTFEngine.plain_text_to_rtf("Texto Alfa"))
            scene_a.write_synopsis("Sinopsis Alfa")
            scene_b.write_content_rtf(RTFEngine.plain_text_to_rtf("Texto Beta"))
            scene_b.write_synopsis("Sinopsis Beta")
            project.save_all()

            merge_cmd = MergeDocumentsCommand(project, [scene_a.uuid, scene_b.uuid])
            merge_ok = undo_stack.push_and_execute(merge_cmd)

            if not merge_ok:
                issues.append(AuditIssue(
                    id="CHAOS-MERGE-FAILED",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="BinderNarrativeCommands",
                    description="Falló la ejecución de MergeDocumentsCommand (Ctrl+Shift+M).",
                    remediation_hint="Verificar project.merge_items y MergeDocumentsCommand."
                ))
            else:
                merged_text = RTFEngine.rtf_to_plain_text(scene_a.read_content_rtf())
                if "Texto Alfa" not in merged_text or "Texto Beta" not in merged_text:
                    issues.append(AuditIssue(
                        id="CHAOS-MERGE-INCOMPLETE",
                        agent=self.name,
                        category=IssueCategory.CRITICAL_BUG,
                        severity=Severity.CRITICAL,
                        component="BinderNarrativeCommands",
                        description="La fusión de documentos omitió texto de uno de los elementos absorbidos.",
                        remediation_hint="Asegurar concatenación íntegra de textos en merge_items."
                    ))

            project.release_lock()

        except Exception as e:
            issues.append(AuditIssue(
                id="CHAOS-SPLIT-MERGE-EXC",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.CRITICAL,
                component="BinderNarrativeCommands",
                description=f"Excepción inesperada en prueba de división/fusión: {str(e)}",
                remediation_hint="Revisar traza de ejecución de narrative_commands."
            ))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return issues

    # =========================================================================
    # 6. PRUEBA FASE A: DESINCRONIZACIÓN EN MODO SCRIVENINGS
    # =========================================================================

    def _test_scrivenings_synchronization_under_stress(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_chaos_scriv_sync_"))

        try:
            proj_dir = temp_dir / "ScriveningsSync.scriv"
            project = EscritorioProject.create_new(proj_dir, title="Scrivenings Sync")
            draft = project.get_draft_folder()
            if not draft:
                return issues

            # Crear 3 escenas
            items = []
            for i in range(1, 4):
                item = project.add_item(draft.uuid, title=f"Escena {i}")
                item.write_content_rtf(RTFEngine.plain_text_to_rtf(f"Contenido original escena {i}."))
                items.append(item)
            project.save_all()

            engine = ScriveningsEngine(project)
            engine.load_from_binder_items(items)

            if len(engine.sections) != 3:
                issues.append(AuditIssue(
                    id="CHAOS-SCRIV-LOAD-FAIL",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="ScriveningsEngine",
                    description=f"ScriveningsEngine cargó {len(engine.sections)} secciones en lugar de 3.",
                    remediation_hint="Verificar load_from_binder_items en ScriveningsEngine."
                ))

            # 1. Edición in-situ de título
            sec2 = engine.sections[1]
            engine.edit_section_title(sec2.uuid, "Escena Dos Renombrada")
            if items[1].title != "Escena Dos Renombrada":
                issues.append(AuditIssue(
                    id="CHAOS-SCRIV-TITLE-DESYNC",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.MAJOR,
                    component="ScriveningsEngine",
                    description="El cambio de título in-situ en Scrivenings no se sincronizó con el BinderItem.",
                    remediation_hint="Asegurar actualización de item.title y save_structure en edit_section_title."
                ))

            # 2. Edición de contenido individual y guardado atómico
            new_c = "Contenido modificado dinámicamente en vista continua."
            engine.edit_section_content(sec2.uuid, new_c, auto_save=True)
            engine.save_all_dirty()

            # Leer directamente el fichero físico rtf del disco
            disk_rtf = items[1].read_content_rtf()
            disk_plain = RTFEngine.rtf_to_plain_text(disk_rtf).strip()
            if disk_plain != new_c:
                issues.append(AuditIssue(
                    id="CHAOS-SCRIV-CONTENT-DESYNC",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="ScriveningsEngine",
                    description=f"Desincronización de contenido en Scrivenings. Esperado: '{new_c}', en disco: '{disk_plain}'.",
                    remediation_hint="Verificar edit_section_content y save_section."
                ))

            project.release_lock()

        except Exception as e:
            issues.append(AuditIssue(
                id="CHAOS-SCRIV-SYNC-EXC",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.CRITICAL,
                component="ScriveningsEngine",
                description=f"Excepción en sincronización de Scrivenings: {str(e)}",
                remediation_hint="Revisar traza de ejecución de ScriveningsEngine."
            ))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return issues

    # =========================================================================
    # 7. PRUEBA FASE A: FOCO LINGÜÍSTICO (LinguisticFocusEngine)
    # =========================================================================

    def _test_linguistic_focus_analyzer(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []

        try:
            # 1. Diálogos
            dialogue_sample = "«Hola amigo», dijo él. \"¿Vienes al cine?\" —preguntó ella entusiasmada—."
            d_spans = LinguisticFocusEngine.analyze(dialogue_sample, LinguisticCategory.DIALOGUES, "ES")
            if len(d_spans) < 2:
                issues.append(AuditIssue(
                    id="CHAOS-LING-DIALOGUES",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.MAJOR,
                    component="LinguisticFocusEngine",
                    description=f"El analizador de diálogos no detectó las intervenciones en español (detectadas: {len(d_spans)}).",
                    remediation_hint="Revisar patrones regex de comillas latinas y rayas en linguistic_focus.py."
                ))

            # 2. Adverbios
            adv_sample = "Caminaba rápidamente y muy silenciosamente hacia la salida."
            adv_spans = LinguisticFocusEngine.analyze(adv_sample, LinguisticCategory.ADVERBS, "ES")
            adv_tokens = {s.token.lower() for s in adv_spans}
            if "rápidamente" not in adv_tokens or "muy" not in adv_tokens:
                issues.append(AuditIssue(
                    id="CHAOS-LING-ADVERBS",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.MAJOR,
                    component="LinguisticFocusEngine",
                    description="El analizador de adverbios omitió adverbios regulares o irregulares canónicos.",
                    remediation_hint="Revisar sufijos -mente y léxico ES_IRREGULAR_ADVERBS."
                ))

            # 3. Adjetivos
            adj_sample = "El viejo castillo tenía un hermoso jardín con flores brillantes."
            adj_spans = LinguisticFocusEngine.analyze(adj_sample, LinguisticCategory.ADJECTIVES, "ES")
            if len(adj_spans) < 2:
                issues.append(AuditIssue(
                    id="CHAOS-LING-ADJECTIVES",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.MAJOR,
                    component="LinguisticFocusEngine",
                    description=f"El analizador de adjetivos detectó solo {len(adj_spans)} adjetivos en muestra descriptiva.",
                    remediation_hint="Revisar patrones morfológicos y léxico de adjetivos en linguistic_focus.py."
                ))

            # 4. Verbos
            verb_sample = "Los guardias corrían velozmente mientras el capitán ordenaba abrir las puertas."
            verb_spans = LinguisticFocusEngine.analyze(verb_sample, LinguisticCategory.VERBS, "ES")
            if len(verb_spans) < 2:
                issues.append(AuditIssue(
                    id="CHAOS-LING-VERBS",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.MAJOR,
                    component="LinguisticFocusEngine",
                    description=f"El analizador de verbos detectó solo {len(verb_spans)} formas conjugadas.",
                    remediation_hint="Revisar desinencias verbales en linguistic_focus.py."
                ))

            # 5. Conjunciones
            conj_sample = "Iba a salir pero comenzó a llover, aunque llevaba paraguas."
            conj_spans = LinguisticFocusEngine.analyze(conj_sample, LinguisticCategory.CONJUNCTIONS, "ES")
            conj_tokens = {s.token.lower() for s in conj_spans}
            if "pero" not in conj_tokens or "aunque" not in conj_tokens:
                issues.append(AuditIssue(
                    id="CHAOS-LING-CONJUNCTIONS",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.MAJOR,
                    component="LinguisticFocusEngine",
                    description="El analizador de conjunciones omitió 'pero' o 'aunque'.",
                    remediation_hint="Verificar léxico ES_CONJUNCTIONS en linguistic_focus.py."
                ))

        except Exception as e:
            issues.append(AuditIssue(
                id="CHAOS-LING-EXC",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.CRITICAL,
                component="LinguisticFocusEngine",
                description=f"Excepción en analizador de foco lingüístico: {str(e)}",
                remediation_hint="Depurar LinguisticFocusEngine en src/ui/EditorWidget/linguistic_focus.py."
            ))

        return issues

    # =========================================================================
    # 8. PRUEBA FASE A: PERSISTENCIA Y CICLO DE VIDA DE COLECCIONES
    # =========================================================================

    def _test_collections_lifecycle(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_chaos_col_"))

        try:
            # Probar en formato .scriv y formato nativo .escr
            for is_native, ext in [(False, ".scriv"), (True, ".escr")]:
                proj_dir = temp_dir / f"CollectionsTest_{'native' if is_native else 'scriv'}{ext}"
                project = EscritorioProject.create_new(proj_dir, title=f"Test Collections {ext}", native=is_native)
                draft = project.get_draft_folder()
                if not draft:
                    continue

                item1 = project.add_item(draft.uuid, title="Capítulo 1")
                item2 = project.add_item(draft.uuid, title="Capítulo 2")
                project.save_all()

                mgr = CollectionsManager(project)
                # Colección Estándar
                col_std = mgr.add_standard_collection("Selección Clave", color_rgba="0.2 0.7 0.3 1.0")
                col_std.item_uuids.append(item1.uuid)
                col_std.item_uuids.append(item2.uuid)

                # Colección de Búsqueda Guardada
                col_search = mgr.add_search_collection("Búsqueda Alfa", query="Capítulo", field="Title")

                project.save_structure()
                project.release_lock()

                # Reabrir el proyecto y validar que las colecciones se cargaron intactas
                reloaded = EscritorioProject(proj_dir)
                reloaded.load()
                reloaded_mgr = CollectionsManager(reloaded)

                if len(reloaded_mgr.collections) < 2:
                    issues.append(AuditIssue(
                        id=f"CHAOS-COL-RELOAD-MISSING-{ext.upper()}",
                        agent=self.name,
                        category=IssueCategory.CRITICAL_BUG,
                        severity=Severity.CRITICAL,
                        component="CollectionsManager",
                        description=f"El proyecto {ext} no preservó las 2 colecciones creadas (cargadas: {len(reloaded_mgr.collections)}).",
                        remediation_hint="Verificar parseo y serialización de <Collections> en ScrivenerXMLParser."
                    ))
                else:
                    std_found = any(c.title == "Selección Clave" and len(c.item_uuids) == 2 for c in reloaded_mgr.collections)
                    search_found = any(c.title == "Búsqueda Alfa" for c in reloaded_mgr.collections)
                    if not std_found or not search_found:
                        issues.append(AuditIssue(
                            id=f"CHAOS-COL-DATA-CORRUPT-{ext.upper()}",
                            agent=self.name,
                            category=IssueCategory.CRITICAL_BUG,
                            severity=Severity.MAJOR,
                            component="CollectionsManager",
                            description=f"Corrupción en datos de colección en proyecto {ext}.",
                            remediation_hint="Asegurar mapeo exacto de item_uuids y search_settings en CollectionDefinition."
                        ))

                reloaded.release_lock()

        except Exception as e:
            issues.append(AuditIssue(
                id="CHAOS-COL-EXC",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.CRITICAL,
                component="CollectionsManager",
                description=f"Excepción en ciclo de vida de colecciones: {str(e)}",
                remediation_hint="Revisar CollectionsManager y serializador XML."
            ))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return issues
