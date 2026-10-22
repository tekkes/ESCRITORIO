"""
Base Agent y Esquema de Auditoría Adversarial para Escritorio Red Team.
Define las estructuras de datos normalizadas para issues, severidad,
categorías de auditoría y reportes consolidados en formato JSON y Markdown.
"""

import json
import datetime
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    COSMETIC = "COSMETIC"


class IssueCategory(str, Enum):
    CRITICAL_BUG = "critical_bugs"
    MISSING_FEATURE = "missing_features"
    UI_DISCREPANCY = "ui_discrepancies"
    PORTABILITY_VIOLATION = "portability_violations"


@dataclass
class AuditIssue:
    """Representa una falla, carencia o discrepancia detectada por un agente."""
    id: str
    agent: str
    category: IssueCategory
    severity: Severity
    component: str
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    remediation_hint: str = ""
    fixed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["category"] = self.category.value if isinstance(self.category, IssueCategory) else str(self.category)
        d["severity"] = self.severity.value if isinstance(self.severity, Severity) else str(self.severity)
        return d


@dataclass
class AuditReport:
    """Reporte formal de iteración adversarial con conteos exactos."""
    iteration: int
    timestamp: str
    critical_bugs: int = 0
    missing_features: int = 0
    ui_discrepancies: int = 0
    portability_violations: int = 0
    total_issues: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    issues: List[AuditIssue] = field(default_factory=list)
    agent_summaries: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_issue(self, issue: AuditIssue):
        self.issues.append(issue)
        cat = issue.category
        if cat == IssueCategory.CRITICAL_BUG:
            self.critical_bugs += 1
        elif cat == IssueCategory.MISSING_FEATURE:
            self.missing_features += 1
        elif cat == IssueCategory.UI_DISCREPANCY:
            self.ui_discrepancies += 1
        elif cat == IssueCategory.PORTABILITY_VIOLATION:
            self.portability_violations += 1
        self.total_issues += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "iteration": self.iteration,
            "timestamp": self.timestamp,
            "counts": {
                "critical_bugs": self.critical_bugs,
                "missing_features": self.missing_features,
                "ui_discrepancies": self.ui_discrepancies,
                "portability_violations": self.portability_violations,
                "total_issues": self.total_issues,
            },
            "test_metrics": {
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "success_rate": f"{(self.passed_tests / max(1, self.passed_tests + self.failed_tests)) * 100:.1f}%"
            },
            "agent_summaries": self.agent_summaries,
            "metadata": self.metadata,
            "issues": [issue.to_dict() for issue in self.issues]
        }

    def save_json(self, destination_path: Path) -> Path:
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        with open(destination_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
        return destination_path

    def save_markdown(self, destination_path: Path) -> Path:
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        md_lines = [
            f"# Informe de Auditoría Adversarial - Iteración #{self.iteration}",
            f"> **Fecha y Hora:** {self.timestamp}  ",
            f"> **Estado General:** {'🔴 RECHAZADO (FALLOS DETECTADOS)' if self.total_issues > 0 else '🟢 APROBADO (CERO DISCREPANCIAS)'}",
            "",
            "## 1. Métricas Consolidadas del Equipo Rojo",
            "",
            "| Categoría de Hallazgo | Conteo | Estado |",
            "|:---|:---:|:---|",
            f"| **Bugs Críticos (`critical_bugs`)** | {self.critical_bugs} | {'❌ FALLO' if self.critical_bugs > 0 else '✅ OK'} |",
            f"| **Funcionalidades Faltantes (`missing_features`)** | {self.missing_features} | {'❌ FALLO' if self.missing_features > 0 else '✅ OK'} |",
            f"| **Discrepancias de UI (`ui_discrepancies`)** | {self.ui_discrepancies} | {'⚠️ REVISAR' if self.ui_discrepancies > 0 else '✅ OK'} |",
            f"| **Violaciones de Portabilidad (`portability_violations`)** | {self.portability_violations} | {'❌ VIOLACIÓN' if self.portability_violations > 0 else '✅ OK'} |",
            f"| **TOTAL HALLAZGOS ADVERSARIALES** | **{self.total_issues}** | {'🚨 REQUIERE PARCHEO' if self.total_issues > 0 else '🏆 100% PARIDAD'} |",
            "",
            "## 2. Detalle de Incidencias Detectadas",
            ""
        ]

        if not self.issues:
            md_lines.append("*No se detectaron discrepancias ni violaciones en esta iteración. El sistema cumple los requisitos de Scrivener 3 al 100%.*")
        else:
            for idx, issue in enumerate(self.issues, 1):
                md_lines.extend([
                    f"### {idx}. [{issue.severity.value}] {issue.id} - {issue.component}",
                    f"- **Agente Detector:** `{issue.agent}`",
                    f"- **Categoría:** `{issue.category.value}`",
                    f"- **Descripción:** {issue.description}",
                    f"- **Evidencia:** `{json.dumps(issue.evidence, ensure_ascii=False)}`",
                    f"- **Sugerencia de Remediación:** {issue.remediation_hint}",
                    ""
                ])

        content = "\n".join(md_lines)
        destination_path.write_text(content, encoding="utf-8")
        return destination_path


class RedTeamAgent:
    """Clase base para los agentes especializados del Equipo Rojo."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def execute_audit(
        self,
        project_root: Path,
        binary_path: Optional[Path],
        iteration: int
    ) -> List[AuditIssue]:
        """
        Ejecuta la auditoría específica del agente y devuelve la lista de fallos encontrados.
        Debe ser sobreescrito por cada agente.
        """
        raise NotImplementedError
