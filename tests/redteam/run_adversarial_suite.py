"""
Orquestador Principal del Bucle Multi-Agente Adversarial para Escritorio.
Ejecuta los agentes del Equipo Rojo en bucle interactivo hasta alcanzar CERO errores,
carencias o discrepancias respecto a Scrivener 3 y genera el informe auditable:
tests/redteam/reports/audit_iteration_<N>.json
"""

import sys
import argparse
import datetime
from pathlib import Path

# Configurar rutas de importación relativas a la raíz del repositorio
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.redteam.agents import (
    ParityInquisitorAgent,
    ChaosFuzzerAgent,
    UIUXAdversaryAgent,
    BlueTeamFixerAgent,
    AuditReport,
    IssueCategory
)


class AdversarialSuiteOrchestrator:
    """Orquestador de verificación y validación adversarial multi-agente."""

    def __init__(self, project_root: Path, reports_dir: Optional[Path] = None):
        self.project_root = project_root
        self.reports_dir = reports_dir or (project_root / "tests" / "redteam" / "reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.parity_agent = ParityInquisitorAgent()
        self.chaos_agent = ChaosFuzzerAgent()
        self.ui_ux_agent = UIUXAdversaryAgent()
        self.blue_team = BlueTeamFixerAgent()

    def run_iteration(self, iteration: int) -> AuditReport:
        """Ejecuta una iteración completa del Equipo Rojo."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = AuditReport(
            iteration=iteration,
            timestamp=timestamp,
            metadata={
                "project_root": str(self.project_root),
                "os": "Windows 11",
                "framework": "Escritorio Red Team Multi-Agent V&V"
            }
        )

        binary_path = self.project_root / "build" / "release" / "Escritorio.exe"

        print(f"\n=================================================================")
        print(f" [INICIO] Ronda Adversarial Multi-Agente - Iteración #{iteration}")
        print(f"=================================================================")
        print(f"[*] Raíz del Proyecto: {self.project_root}")
        print(f"[*] Binario Auditado:  {binary_path} (Existe: {binary_path.exists()})")

        # 1. Agente 1: ParityInquisitorAgent
        print("\n[1/3] Ejecutando ParityInquisitorAgent (Auditoría de Atajos, Temas y REA)...")
        parity_issues = self.parity_agent.execute_audit(self.project_root, binary_path, iteration)
        for issue in parity_issues:
            report.add_issue(issue)
        print(f"      -> {len(parity_issues)} hallazgos detectados por ParityInquisitorAgent.")

        # 2. Agente 2: ChaosFuzzerAgent
        print("\n[2/3] Ejecutando ChaosFuzzerAgent (Estrés, Corrupción, Unicode y Portabilidad)...")
        chaos_issues = self.chaos_agent.execute_audit(self.project_root, binary_path, iteration)
        for issue in chaos_issues:
            report.add_issue(issue)
        print(f"      -> {len(chaos_issues)} hallazgos detectados por ChaosFuzzerAgent.")

        # 3. Agente 3: UIUXAdversaryAgent
        print("\n[3/3] Ejecutando UIUXAdversaryAgent (Temas, Split, Drag&Drop, Diff y Compilación)...")
        ui_issues = self.ui_ux_agent.execute_audit(self.project_root, binary_path, iteration)
        for issue in ui_issues:
            report.add_issue(issue)
        print(f"      -> {len(ui_issues)} hallazgos detectados por UIUXAdversaryAgent.")

        # Contabilizar métricas de pruebas ejecutadas (Fase A + Fase B)
        total_checks = 99  # 41 Parity + 13 Chaos + 45 UI/UX/Corkboard/Outliner/Inspector/Compile
        report.failed_tests = report.total_issues
        report.passed_tests = max(0, total_checks - report.failed_tests)
        report.agent_summaries = {
            "ParityInquisitorAgent": f"{len(parity_issues)} hallazgos",
            "ChaosFuzzerAgent": f"{len(chaos_issues)} hallazgos",
            "UIUXAdversaryAgent": f"{len(ui_issues)} hallazgos"
        }

        # Guardar reportes JSON y Markdown
        json_path = self.reports_dir / f"audit_iteration_{iteration}.json"
        md_path = self.reports_dir / f"audit_iteration_{iteration}.md"
        report.save_json(json_path)
        report.save_markdown(md_path)

        print(f"\n[+] Informe guardado exitosamente:")
        print(f"    - JSON:     {json_path}")
        print(f"    - Markdown: {md_path}")

        # Resumen en consola
        self._print_summary_card(report)

        return report

    def run_adversarial_loop(self, max_iterations: int = 5, auto_fix: bool = True) -> bool:
        """
        Ejecuta el bucle continuo Equipo Rojo -> Blue Team -> Equipo Rojo
        hasta alcanzar 0 discrepancias o agotar las iteraciones máximas.
        """
        for it in range(1, max_iterations + 1):
            report = self.run_iteration(it)

            if report.total_issues == 0:
                print(f"\n[OK] OBJETIVO ALCANZADO EN ITERACION #{it}!")
                print(f"     CERO errores, CERO carencias y CERO discrepancias con Scrivener 3.")
                return True

            if not auto_fix:
                print(f"\n[!] Bucle detenido: auto_fix desactivado y se detectaron {report.total_issues} fallos.")
                return False

            print(f"\n[4/4] Invocando BlueTeamFixerAgent para remediar {report.total_issues} fallos...")
            fix_result = self.blue_team.remediate_report(report, self.project_root)
            print(f"      -> Remediaciones procesadas: {fix_result['remediated_count']}")
            print(f"      -> Recompilacion: {fix_result['compile_result'].get('output', 'Completada')}")

        print(f"\n[!] Se alcanzo el numero maximo de iteraciones ({max_iterations}) con incidencias pendientes.")
        return False

    def _print_summary_card(self, report: AuditReport):
        print("\n-----------------------------------------------------------------")
        print(f" TABLERO AUDITOR ADVERSARIAL - ITERACION #{report.iteration}")
        print("-----------------------------------------------------------------")
        print(f"  - Bugs Criticos (critical_bugs):           {report.critical_bugs}")
        print(f"  - Funciones Faltantes (missing_features):   {report.missing_features}")
        print(f"  - Discrepancias de UI (ui_discrepancies):   {report.ui_discrepancies}")
        print(f"  - Violaciones Portables (portability_viol): {report.portability_violations}")
        print("-----------------------------------------------------------------")
        print(f"  TOTAL DE HALLAZGOS:                        {report.total_issues}")
        status_badge = "[APROBADO 100%]" if report.total_issues == 0 else "[NO CONFORME - REQUIERE PARCHEO]"
        print(f"  ESTADO DE AUDITORIA:                       {status_badge}")
        print("-----------------------------------------------------------------\n")


def main():
    parser = argparse.ArgumentParser(description="Escritorio Multi-Agent Adversarial Verification & Validation Suite")
    parser.add_argument("--iterations", type=int, default=1, help="Número de iteraciones a ejecutar")
    parser.add_argument("--max-iterations", type=int, default=5, help="Máximo de iteraciones en modo bucle auto-fix")
    parser.add_argument("--auto-fix", action="store_true", default=True, help="Invocar BlueTeamFixerAgent automáticamente si hay fallos")
    parser.add_argument("--no-auto-fix", action="store_false", dest="auto_fix", help="Desactivar auto-fix del Blue Team")
    args = parser.parse_args()

    orchestrator = AdversarialSuiteOrchestrator(PROJECT_ROOT)

    if args.iterations > 1 or args.auto_fix:
        success = orchestrator.run_adversarial_loop(max_iterations=args.max_iterations, auto_fix=args.auto_fix)
        sys.exit(0 if success else 1)
    else:
        report = orchestrator.run_iteration(iteration=1)
        sys.exit(0 if report.total_issues == 0 else 1)


if __name__ == "__main__":
    main()
