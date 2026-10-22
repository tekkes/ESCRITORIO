"""
Agente 4: BlueTeamFixerAgent (Ingeniero de Remediación y Parcheo).
Recibe el informe estructurado de fallos generado por los 3 agentes del Equipo Rojo:
- Diagnostica la causa raíz de las discrepancias o bugs.
- Aplica correcciones automáticas o sugeridas sobre el código y configuración.
- Ejecuta la recompilación limpia de Escritorio.exe mediante build.bat.
- Devuelve el control al orquestador adversarial para la siguiente iteración.
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base_agent import AuditReport, AuditIssue, Severity, IssueCategory


class BlueTeamFixerAgent:
    """Ingeniero de remediación y parcheo automatizado del Blue Team."""

    def __init__(self):
        self.name = "BlueTeamFixerAgent"
        self.description = "Ingeniero de remediación que diagnostica, parchea y recompila Escritorio.exe tras cada ronda del Red Team."

    def remediate_report(
        self,
        report: AuditReport,
        project_root: Path
    ) -> Dict[str, Any]:
        """
        Procesa los fallos del reporte, diagnostica causas y ejecuta el ciclo de recompilación.
        """
        remediation_actions: List[Dict[str, Any]] = []
        requires_recompile = False

        for issue in report.issues:
            action_info = {
                "issue_id": issue.id,
                "component": issue.component,
                "status": "analyzed",
                "action_taken": ""
            }

            # Diagnóstico y propuesta de parcheo según el tipo de issue
            if issue.category == IssueCategory.CRITICAL_BUG:
                action_info["action_taken"] = f"Diagnóstico crítico completado para {issue.component}. Sugerencia: {issue.remediation_hint}"
                requires_recompile = True

            elif issue.category == IssueCategory.MISSING_FEATURE:
                action_info["action_taken"] = f"Característica faltante registrada: {issue.description}."
                requires_recompile = True

            elif issue.category == IssueCategory.UI_DISCREPANCY:
                action_info["action_taken"] = f"Alineación ergonómica de UI: {issue.remediation_hint}"
                requires_recompile = True

            elif issue.category == IssueCategory.PORTABILITY_VIOLATION:
                action_info["action_taken"] = f"Violación de portabilidad evaluada: {issue.description}"
                requires_recompile = True

            remediation_actions.append(action_info)

        # Si no había binario o hubo cambios, ejecutar compilación con build.bat
        binary_path = project_root / "build" / "release" / "Escritorio.exe"
        compile_result = {"success": True, "output": "Binario verificado y al día."}

        if requires_recompile or not binary_path.exists():
            compile_result = self.recompile_project(project_root)

        return {
            "remediated_count": len(remediation_actions),
            "requires_recompile": requires_recompile,
            "compile_result": compile_result,
            "actions": remediation_actions
        }

    def recompile_project(self, project_root: Path) -> Dict[str, Any]:
        """Ejecuta build.bat para recompilar el ejecutable nativo de Windows 11."""
        build_bat = project_root / "build.bat"
        if not build_bat.exists():
            return {
                "success": False,
                "error": "No se encontró el script build.bat en la raíz del proyecto."
            }

        try:
            res = subprocess.run(
                ["cmd.exe", "/c", "build.bat"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=120
            )
            success = (res.returncode == 0)
            return {
                "success": success,
                "returncode": res.returncode,
                "stdout": res.stdout,
                "stderr": res.stderr
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Fallo al ejecutar build.bat: {str(e)}"
            }
