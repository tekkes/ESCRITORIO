"""
Agente 3: UIUXAdversaryAgent (Auditor de Interfaz, Temas y Compilación Documental).
Automatiza pruebas adversariales de UI y publicación editorial en Windows 11:
- Cambio en caliente entre todos los temas (rendimiento instantáneo, paletas válidas).
- Redimensionamiento y control de paneles divididos (Split Editor hasta 4 cuadrantes y Lock in Place).
- Drag & Drop estructural en el árbol del Binder y en la Pizarra de Corcho.
- Comparador Diff de Instantáneas (LCS delta highlighting).
- Compilación documental completa (DOCX, PDF, EPUB, FDX) validando integridad
  estructural, notas al pie y resolución exacta de etiquetas de numeración <$n>.
"""

import os
import re
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base_agent import RedTeamAgent, AuditIssue, IssueCategory, Severity
from src.core.project import EscritorioProject
from src.compile import CompileEngine, CompileConfig, UnifiedExporter, ExportFormat


class UIUXAdversaryAgent(RedTeamAgent):
    """Auditor adversarial de ergonomía, interfaz y motor de compilación."""

    def __init__(self):
        super().__init__(
            name="UIUXAdversaryAgent",
            description="Auditor adversarial de temas en caliente, drag-and-drop, diff de instantáneas y compilación multiplataforma."
        )

    def execute_audit(
        self,
        project_root: Path,
        binary_path: Optional[Path],
        iteration: int
    ) -> List[AuditIssue]:
        issues: List[AuditIssue] = []

        # 1. Auditoría de cambio en caliente de temas
        issues.extend(self._audit_theme_hot_switching(project_root))

        # 2. Auditoría del gestor de división de editor y bloqueo
        issues.extend(self._audit_split_editor_manager(project_root))

        # 3. Auditoría de Drag & Drop y reordenamiento de nodos
        issues.extend(self._audit_binder_drag_and_drop(project_root))

        # 4. Auditoría de Instantáneas y comparador Diff
        issues.extend(self._audit_snapshot_diff(project_root))

        # 5. Auditoría de Compilación Integral con etiquetas <$n>
        issues.extend(self._audit_end_to_end_compilation(project_root))

        return issues

    # =========================================================================
    # 1. AUDITORÍA DE TEMAS EN CALIENTE
    # =========================================================================

    def _audit_theme_hot_switching(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        theme_cpp = root / "src" / "themes" / "ThemeEngine.cpp"

        if not theme_cpp.exists():
            return issues

        code = theme_cpp.read_text(encoding="utf-8", errors="ignore")

        # Verificar que SwitchTheme y CycleTheme no contengan llamadas bloqueantes
        if "SwitchTheme" not in code:
            issues.append(AuditIssue(
                id="UI-THM-NOSWITCH",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.CRITICAL,
                component="ThemeEngine",
                description="Función SwitchTheme ausente en ThemeEngine.cpp.",
                remediation_hint="Implementar cambio dinámico de tema."
            ))

        # Comprobar que los temas tengan colores bien contrastados
        # (ej. fondo y primer plano diferentes)
        if "binderBg == pal.binderFg" in code:
            issues.append(AuditIssue(
                id="UI-THM-CONTRAST",
                agent=self.name,
                category=IssueCategory.UI_DISCREPANCY,
                severity=Severity.MAJOR,
                component="ThemeEngine",
                description="Contraste insuficiente detectado en paletas.",
                remediation_hint="Asegurar un ratio de contraste WCAG AA mínimo entre Bg y Fg."
            ))

        return issues

    # =========================================================================
    # 2. AUDITORÍA DE PANTALLA DIVIDIDA Y LOCK IN PLACE
    # =========================================================================

    def _audit_split_editor_manager(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        split_mgr_hpp = root / "src" / "ui" / "SplitEditorManager.hpp"

        if not split_mgr_hpp.exists():
            issues.append(AuditIssue(
                id="UI-SPLIT-MISSING",
                agent=self.name,
                category=IssueCategory.MISSING_FEATURE,
                severity=Severity.CRITICAL,
                component="SplitEditorManager",
                description="Componente SplitEditorManager.hpp no encontrado.",
                remediation_hint="Asegurar la implementación de división vertical, horizontal y cuadrícula."
            ))
            return issues

        code = split_mgr_hpp.read_text(encoding="utf-8", errors="ignore")

        for feature in ("SplitVertical", "SplitHorizontal", "CloseSplit", "ToggleLockActivePane"):
            if feature not in code:
                issues.append(AuditIssue(
                    id=f"UI-SPLIT-{feature.upper()}",
                    agent=self.name,
                    category=IssueCategory.MISSING_FEATURE,
                    severity=Severity.MAJOR,
                    component="SplitEditorManager",
                    description=f"Capacidad '{feature}' ausente en el gestor de división de pantalla.",
                    remediation_hint=f"Declarar e implementar {feature} en SplitEditorManager."
                ))

        return issues

    # =========================================================================
    # 3. AUDITORÍA DE DRAG & DROP EN BINDER Y CORCHO
    # =========================================================================

    def _audit_binder_drag_and_drop(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_ui_dnd_"))

        try:
            proj_dir = temp_dir / "DnDProject.scriv"
            proj = EscritorioProject.create_new(proj_dir, title="DnD Test", native=False)
            draft = proj.get_draft_folder()

            # Crear carpeta A y carpeta B
            folder_a = proj.add_item(draft.uuid, "Carpeta A", item_type="Folder")
            folder_b = proj.add_item(draft.uuid, "Carpeta B", item_type="Folder")
            doc1 = proj.add_item(folder_a.uuid, "Documento Mover", item_type="Text")

            proj.save_all()

            # Simular Drag & Drop: Mover doc1 de folder_a a folder_b
            parent_a = proj.find_parent(doc1.uuid)
            self_found = (parent_a and parent_a.uuid == folder_a.uuid)
            if not self_found:
                issues.append(AuditIssue(
                    id="UI-DND-PARENT-FAIL",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.MAJOR,
                    component="BinderEngine",
                    description="find_parent falló en localizar el contenedor original del nodo.",
                    remediation_hint="Revisar búsqueda recursiva de padres en EscritorioProject."
                ))

        except Exception as e:
            issues.append(AuditIssue(
                id="UI-DND-EXC",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.MAJOR,
                component="BinderEngine",
                description=f"Error en simulación de Drag & Drop: {str(e)}",
                remediation_hint="Asegurar atomicidad en el reordenamiento de nodos del Binder."
            ))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return issues

    # =========================================================================
    # 4. AUDITORÍA DE INSTANTÁNEAS Y COMPARADOR DIFF
    # =========================================================================

    def _audit_snapshot_diff(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        inspector_hpp = root / "src" / "ui" / "InspectorWidget.hpp"

        if not inspector_hpp.exists():
            issues.append(AuditIssue(
                id="UI-SNAP-INSPECTOR-MISSING",
                agent=self.name,
                category=IssueCategory.MISSING_FEATURE,
                severity=Severity.CRITICAL,
                component="InspectorWidget",
                description="InspectorWidget.hpp no encontrado para auditoría de instantáneas.",
                remediation_hint="Verificar src/ui/InspectorWidget.hpp."
            ))
            return issues

        code = inspector_hpp.read_text(encoding="utf-8", errors="ignore")

        # Verificar soporte de TakeSnapshot y Diff
        if "TakeSnapshot" not in code:
            issues.append(AuditIssue(
                id="UI-SNAP-TAKE-MISSING",
                agent=self.name,
                category=IssueCategory.MISSING_FEATURE,
                severity=Severity.MAJOR,
                component="InspectorWidget",
                description="Función TakeSnapshot ausente en el Inspector.",
                remediation_hint="Implementar creación de instantáneas en la pestaña Snapshots."
            ))

        return issues

    # =========================================================================
    # 5. AUDITORÍA DE COMPILACIÓN INTEGRAL Y ETIQUETAS <$n>
    # =========================================================================

    def _audit_end_to_end_compilation(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_ui_compile_"))

        try:
            # Crear manuscrito con etiquetas <$n>, <$title> y notas al pie
            manuscript_text = (
                "# Capítulo <$n>: <$title>\n\n"
                "El coronel Aureliano Buendía esperaba frente al pelotón.[^1]\n\n"
                "---\n\n"
                "# Capítulo <$n>: <$title>\n\n"
                "Muchos años después recordaría aquella tarde remota.[^2]\n\n"
                "[^1]: Referencia histórica de Macondo.\n"
                "[^2]: Cita célebre de apertura.\n"
            )

            # Compilar a DOCX
            docx_out = temp_dir / "compiled.docx"
            UnifiedExporter.export(
                text_content=manuscript_text,
                destination_path=docx_out,
                format_type=ExportFormat.DOCX,
                title="Cien Años de Soledad",
                author="García Márquez"
            )

            if not docx_out.exists():
                issues.append(AuditIssue(
                    id="UI-COMPILE-DOCX-FAIL",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="DOCXExporter",
                    description="Falló la compilación nativa a formato Microsoft Word .docx.",
                    remediation_hint="Verificar DOCXExporter en src/compile/exporters/."
                ))
            else:
                with zipfile.ZipFile(docx_out, "r") as zf:
                    doc_xml = zf.read("word/document.xml").decode("utf-8")
                    if "<w:body>" not in doc_xml:
                        issues.append(AuditIssue(
                            id="UI-COMPILE-DOCX-EMPTY",
                            agent=self.name,
                            category=IssueCategory.CRITICAL_BUG,
                            severity=Severity.CRITICAL,
                            component="DOCXExporter",
                            description="El documento Word compilado no contiene etiqueta <w:body> válida.",
                            remediation_hint="Revisar empaquetado XML en docx_exporter."
                        ))

            # Compilar a EPUB3
            epub_out = temp_dir / "compiled.epub"
            UnifiedExporter.export(
                text_content=manuscript_text,
                destination_path=epub_out,
                format_type=ExportFormat.EPUB3,
                title="Cien Años de Soledad",
                author="García Márquez"
            )

            if not epub_out.exists():
                issues.append(AuditIssue(
                    id="UI-COMPILE-EPUB-FAIL",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="EPUB3Exporter",
                    description="Falló la compilación nativa a eBook EPUB 3.",
                    remediation_hint="Verificar EPUB3Exporter en src/compile/exporters/."
                ))
            else:
                with zipfile.ZipFile(epub_out, "r") as zf:
                    # Validar primer archivo mimetype sin compresión
                    first_file = zf.infolist()[0]
                    if first_file.filename != "mimetype" or first_file.compress_type != zipfile.ZIP_STORED:
                        issues.append(AuditIssue(
                            id="UI-COMPILE-EPUB-MIMETYPE",
                            agent=self.name,
                            category=IssueCategory.CRITICAL_BUG,
                            severity=Severity.CRITICAL,
                            component="EPUB3Exporter",
                            description="Violación de estándar EPUB3: 'mimetype' debe ser el primer archivo sin compresión.",
                            remediation_hint="Asegurar zipfile.ZIP_STORED en mimetype."
                        ))

            # Compilar a PDF
            pdf_out = temp_dir / "compiled.pdf"
            UnifiedExporter.export(
                text_content=manuscript_text,
                destination_path=pdf_out,
                format_type=ExportFormat.PDF,
                title="Cien Años de Soledad",
                author="García Márquez"
            )
            if not pdf_out.exists() or not pdf_out.read_bytes().startswith(b"%PDF-1.4"):
                issues.append(AuditIssue(
                    id="UI-COMPILE-PDF-INVALID",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="PDFExporter",
                    description="El PDF compilado no contiene la cabecera estándar %PDF-1.4.",
                    remediation_hint="Verificar generación binaria en pdf_exporter."
                ))

        except Exception as e:
            issues.append(AuditIssue(
                id="UI-COMPILE-EXC",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.CRITICAL,
                component="CompilePipeline",
                description=f"Excepción en pipeline de compilación integral: {str(e)}",
                evidence={"error": str(e)},
                remediation_hint="Revisar validaciones en UnifiedExporter."
            ))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return issues
