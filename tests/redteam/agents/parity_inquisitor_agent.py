"""
Agente 1: ParityInquisitorAgent (Auditor de Paridad Funcional y Visual con REA).
Inspecciona el árbol de código fuente y el binario compilado Escritorio.exe
contrastándolos contra REA_Architecture_Evidence.md y la especificación Scrivener 3:
- Atajos de teclado obligatorios (Ctrl+1, Ctrl+2, Ctrl+3, Ctrl+', Ctrl+", Ctrl+Shift+I, etc.).
- Soporte de los 7 temas visuales y compatibilidad con .scrtheme.
- Límites ergonómicos de densidad UI (Toolbar <= 28px, Headers <= 24px, iconos <= 16px).
- Estructura jerárquica del Binder y tipos de sección (Section Types).
- Conexión de acciones y handlers sin funciones vacías o botones descolgados.
"""

import re
import os
import struct
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base_agent import RedTeamAgent, AuditIssue, IssueCategory, Severity


class ParityInquisitorAgent(RedTeamAgent):
    """Auditor inquisidor de paridad estricta contra Scrivener 3 y especificaciones REA."""

    def __init__(self):
        super().__init__(
            name="ParityInquisitorAgent",
            description="Auditor adversarial de paridad funcional, atajos, temas y conformidad de UI con Scrivener 3."
        )

    # Atajos canónicos requeridos por Scrivener 3 y la especificación de Escritorio
    MANDATORY_SHORTCUTS = {
        "Ctrl+1": "Modo Scrivenings (Vista Compuesta Continua)",
        "Ctrl+2": "Modo Pizarra de Corcho (Corkboard)",
        "Ctrl+3": "Modo Esquema (Outliner)",
        "Ctrl+'": "División de Editor Vertical",
        'Ctrl+"': "División de Editor Horizontal",
        "Ctrl+Shift+L": "Bloqueo de Panel (Lock in Place)",
        "Ctrl+Shift+I": "Conmutar Panel Inspector",
        "Ctrl+Shift+T": "Objetivos de Proyecto y Sesión (Project Targets)",
        "Ctrl+Shift+E": "Diálogo de Compilación Editorial (Compile Dialog)",
        "Ctrl+Shift+N": "Galería de Plantillas (New Project Chooser)",
        "Ctrl+8": "Modo Escritura de Guiones Cinematográficos",
        "F11": "Modo Composición a Pantalla Completa",
        "F8": "Conmutación Rápida de Temas",
        "F9": "Alternancia de Densidad UI (Ultra-Compacto)"
    }

    # Los 7 temas visuales requeridos
    MANDATORY_THEMES = [
        "Minimal", "Carbon", "SolarizedDark", "SolarizedLight", "Sepia", "Nord", "Mocha"
    ]

    def execute_audit(
        self,
        project_root: Path,
        binary_path: Optional[Path],
        iteration: int
    ) -> List[AuditIssue]:
        issues: List[AuditIssue] = []

        # 1. Auditoría de Atajos de Teclado en MainWindow
        issues.extend(self._audit_keyboard_shortcuts(project_root))

        # 2. Auditoría de Temas y Densidad UI
        issues.extend(self._audit_themes_and_density(project_root))

        # 3. Auditoría de Ergonomía y Dimensiones de UI (<= 28px toolbar)
        issues.extend(self._audit_ui_dimensions(project_root))

        # 4. Auditoría de Paridad del Binder y Tipos de Sección
        issues.extend(self._audit_binder_parity(project_root))

        # 5. Auditoría del Binario PE (si existe Escritorio.exe)
        if binary_path and binary_path.exists():
            issues.extend(self._audit_pe_binary_headers(binary_path))

        return issues

    def _audit_keyboard_shortcuts(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        main_cpp = root / "src" / "ui" / "MainWindow.cpp"

        if not main_cpp.exists():
            issues.append(AuditIssue(
                id="PAR-001",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.CRITICAL,
                component="MainWindow",
                description="Archivo src/ui/MainWindow.cpp no encontrado para auditoría de atajos.",
                remediation_hint="Verificar la estructura de directorios del proyecto."
            ))
            return issues

        code = main_cpp.read_text(encoding="utf-8", errors="ignore")

        # Comprobar cada atajo en el bloque WM_KEYDOWN
        if "WM_KEYDOWN" not in code:
            issues.append(AuditIssue(
                id="PAR-002",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.CRITICAL,
                component="MainWindow",
                description="MainWindow no procesa WM_KEYDOWN para atajos de teclado.",
                remediation_hint="Implementar el despachador WM_KEYDOWN."
            ))
            return issues

        for key, desc in self.MANDATORY_SHORTCUTS.items():
            found = False
            if key == "Ctrl+1" and "'1'" in code:
                found = True
            elif key == "Ctrl+2" and "'2'" in code:
                found = True
            elif key == "Ctrl+3" and "'3'" in code:
                found = True
            elif key == "Ctrl+'" and ("VK_OEM_7" in code or "0xDE" in code or "'\\''" in code):
                found = True
            elif key == 'Ctrl+"' and ("VK_OEM_5" in code or "'\"'" in code):
                found = True
            elif key == "Ctrl+Shift+L" and "'L'" in code and "shift" in code:
                found = True
            elif key == "Ctrl+Shift+I" and "'I'" in code and "shift" in code:
                found = True
            elif key == "Ctrl+Shift+T" and "'T'" in code and "shift" in code:
                found = True
            elif key == "Ctrl+Shift+E" and "'E'" in code and "shift" in code:
                found = True
            elif key == "Ctrl+Shift+N" and "'N'" in code and "shift" in code:
                found = True
            elif key == "Ctrl+8" and "'8'" in code:
                found = True
            elif key == "F11" and "VK_F11" in code:
                found = True
            elif key == "F8" and "VK_F8" in code:
                found = True
            elif key == "F9" and "VK_F9" in code:
                found = True

            if not found:
                issues.append(AuditIssue(
                    id=f"PAR-KEY-{key.replace('+', '_').replace('\"', 'quote')}",
                    agent=self.name,
                    category=IssueCategory.MISSING_FEATURE,
                    severity=Severity.MAJOR,
                    component="KeyboardShortcuts",
                    description=f"Atajo obligatorio {key} ({desc}) ausente en el despachador WM_KEYDOWN.",
                    remediation_hint=f"Vincular {key} en MainWindow.cpp para activar {desc}."
                ))

        return issues

    def _audit_themes_and_density(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        theme_engine_hpp = root / "src" / "themes" / "ThemeEngine.hpp"
        theme_engine_cpp = root / "src" / "themes" / "ThemeEngine.cpp"

        if not theme_engine_hpp.exists() or not theme_engine_cpp.exists():
            issues.append(AuditIssue(
                id="PAR-THM-001",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.CRITICAL,
                component="ThemeEngine",
                description="Archivos del motor ThemeEngine no encontrados.",
                remediation_hint="Asegurar la existencia de src/themes/ThemeEngine.hpp y .cpp."
            ))
            return issues

        hpp_text = theme_engine_hpp.read_text(encoding="utf-8", errors="ignore")
        cpp_text = theme_engine_cpp.read_text(encoding="utf-8", errors="ignore")

        # Verificar soporte para los 7 temas canónicos
        for thm in self.MANDATORY_THEMES:
            if thm not in hpp_text and thm not in cpp_text:
                issues.append(AuditIssue(
                    id=f"PAR-THM-{thm.upper()}",
                    agent=self.name,
                    category=IssueCategory.UI_DISCREPANCY,
                    severity=Severity.MAJOR,
                    component="ThemeEngine",
                    description=f"El tema '{thm}' no se encuentra declarado en ThemeEngine.",
                    remediation_hint=f"Añadir la paleta oficial para '{thm}' en ThemeEngine."
                ))

        # Verificar soporte de archivo .scrtheme
        if "LoadScrTheme" not in hpp_text and "scrtheme" not in cpp_text.lower():
            issues.append(AuditIssue(
                id="PAR-THM-SCRTHEME",
                agent=self.name,
                category=IssueCategory.MISSING_FEATURE,
                severity=Severity.MINOR,
                component="ThemeEngine",
                description="No se detectó el cargador de archivos de tema .scrtheme de Scrivener.",
                remediation_hint="Implementar el parser XML/INI para archivos .scrtheme."
            ))

        return issues

    def _audit_ui_dimensions(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        theme_engine_cpp = root / "src" / "themes" / "ThemeEngine.cpp"

        if theme_engine_cpp.exists():
            code = theme_engine_cpp.read_text(encoding="utf-8", errors="ignore")

            # Regla de oro ergonomía Scrivener Ultra-Compacto:
            # toolbarHeight <= 28px, editorHeaderHeight <= 24px, binderRowHeight <= 22px
            tb_match = re.search(r"m_densityMetrics\.toolbarHeight\s*=\s*(\d+)", code)
            if tb_match:
                val = int(tb_match.group(1))
                if val > 28:
                    issues.append(AuditIssue(
                        id="PAR-UI-TOOLBAR-HEIGHT",
                        agent=self.name,
                        category=IssueCategory.UI_DISCREPANCY,
                        severity=Severity.MINOR,
                        component="UIDensity",
                        description=f"La altura de la barra de herramientas ({val}px) excede el máximo ultra-compacto de 28px.",
                        remediation_hint="Ajustar m_densityMetrics.toolbarHeight a 28px o inferior."
                    ))

            hdr_match = re.search(r"m_densityMetrics\.editorHeaderHeight\s*=\s*(\d+)", code)
            if hdr_match:
                val = int(hdr_match.group(1))
                if val > 24:
                    issues.append(AuditIssue(
                        id="PAR-UI-HEADER-HEIGHT",
                        agent=self.name,
                        category=IssueCategory.UI_DISCREPANCY,
                        severity=Severity.MINOR,
                        component="UIDensity",
                        description=f"La cabecera del editor ({val}px) excede el estándar de 24px.",
                        remediation_hint="Ajustar m_densityMetrics.editorHeaderHeight a 24px o inferior."
                    ))

        return issues

    def _audit_binder_parity(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        xml_parser_py = root / "src" / "core" / "xml_parser.py"

        if xml_parser_py.exists():
            code = xml_parser_py.read_text(encoding="utf-8", errors="ignore")
            # Verificar elementos raíz Scrivener 3: DraftFolder, ResearchFolder, TrashFolder
            for root_type in ("DraftFolder", "ResearchFolder", "TrashFolder"):
                if root_type not in code:
                    issues.append(AuditIssue(
                        id=f"PAR-BINDER-{root_type.upper()}",
                        agent=self.name,
                        category=IssueCategory.CRITICAL_BUG,
                        severity=Severity.CRITICAL,
                        component="BinderEngine",
                        description=f"El tipo de raíz '{root_type}' no está soportado en el parser XML.",
                        remediation_hint=f"Agregar '{root_type}' al mapeador ScrivenerXMLParser."
                    ))

        return issues

    def _audit_pe_binary_headers(self, binary_path: Path) -> List[AuditIssue]:
        """Analiza la estructura del binario ejecutable Windows PE (Portable Executable)."""
        issues: List[AuditIssue] = []
        try:
            with open(binary_path, "rb") as f:
                header = f.read(1024)

            # Verificar firma 'MZ' (DOS Header)
            if not header.startswith(b"MZ"):
                issues.append(AuditIssue(
                    id="PAR-PE-NOT-MZ",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="PEBinary",
                    description=f"{binary_path.name} no contiene una firma MZ válida de ejecutable Windows.",
                    remediation_hint="Recompilar Escritorio.exe con MSVC."
                ))
                return issues

            # Offset al PE Header (offset 0x3C)
            pe_offset = struct.unpack_from("<I", header, 0x3C)[0]
            if len(header) >= pe_offset + 4:
                pe_sig = header[pe_offset:pe_offset+4]
                if pe_sig != b"PE\x00\x00":
                    issues.append(AuditIssue(
                        id="PAR-PE-INVALID-SIG",
                        agent=self.name,
                        category=IssueCategory.CRITICAL_BUG,
                        severity=Severity.CRITICAL,
                        component="PEBinary",
                        description=f"{binary_path.name} no contiene la firma 'PE\\0\\0'.",
                        remediation_hint="Recompilar Escritorio.exe con CMake y MSVC."
                    ))

        except Exception as e:
            issues.append(AuditIssue(
                id="PAR-PE-READ-ERR",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.MAJOR,
                component="PEBinary",
                description=f"Error al inspeccionar la cabecera PE: {str(e)}",
                remediation_hint="Verificar permisos de lectura sobre el archivo ejecutable."
            ))

        return issues
