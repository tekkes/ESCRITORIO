"""
Pruebas Unitarias del Framework Multi-Agente de Validación y Verificación Adversarial.
Verifica que los 4 Agentes Especializados (ParityInquisitorAgent, ChaosFuzzerAgent,
UIUXAdversaryAgent, BlueTeamFixerAgent) y el orquestador generen reportes auditables válidos.
"""

import sys
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tests.redteam.agents import (
    ParityInquisitorAgent,
    ChaosFuzzerAgent,
    UIUXAdversaryAgent,
    BlueTeamFixerAgent,
    AuditReport,
    AuditIssue,
    Severity,
    IssueCategory
)
from tests.redteam.run_adversarial_suite import AdversarialSuiteOrchestrator


class TestAdversarialFramework(unittest.TestCase):
    """Pruebas del sistema multi-agente adversarial del Red Team."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_fw_test_"))
        self.project_root = ROOT_DIR
        self.binary_path = ROOT_DIR / "build" / "release" / "Escritorio.exe"

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parity_inquisitor_agent(self):
        agent = ParityInquisitorAgent()
        issues = agent.execute_audit(self.project_root, self.binary_path, iteration=1)
        self.assertIsInstance(issues, list)
        for issue in issues:
            self.assertIsInstance(issue, AuditIssue)
            self.assertIn(issue.category, list(IssueCategory))

    def test_chaos_fuzzer_agent(self):
        agent = ChaosFuzzerAgent()
        issues = agent.execute_audit(self.project_root, self.binary_path, iteration=1)
        self.assertIsInstance(issues, list)
        for issue in issues:
            self.assertIsInstance(issue, AuditIssue)

    def test_ui_ux_adversary_agent(self):
        agent = UIUXAdversaryAgent()
        issues = agent.execute_audit(self.project_root, self.binary_path, iteration=1)
        self.assertIsInstance(issues, list)
        for issue in issues:
            self.assertIsInstance(issue, AuditIssue)

    def test_blue_team_fixer_agent(self):
        agent = BlueTeamFixerAgent()
        sample_report = AuditReport(
            iteration=1,
            timestamp="2026-10-22 18:00:00"
        )
        sample_report.add_issue(AuditIssue(
            id="TEST-001",
            agent="ParityInquisitorAgent",
            category=IssueCategory.UI_DISCREPANCY,
            severity=Severity.MINOR,
            component="ThemeEngine",
            description="Discrepancia menor de prueba.",
            remediation_hint="Ajustar paleta de color."
        ))

        res = agent.remediate_report(sample_report, self.project_root)
        self.assertIn("remediated_count", res)
        self.assertEqual(res["remediated_count"], 1)

    def test_orchestrator_report_generation(self):
        reports_dir = self.temp_dir / "reports"
        orchestrator = AdversarialSuiteOrchestrator(self.project_root, reports_dir=reports_dir)
        report = orchestrator.run_iteration(iteration=1)

        self.assertIsInstance(report, AuditReport)
        self.assertEqual(report.iteration, 1)

        # Verificar conteos
        self.assertIsInstance(report.critical_bugs, int)
        self.assertIsInstance(report.missing_features, int)
        self.assertIsInstance(report.ui_discrepancies, int)
        self.assertIsInstance(report.portability_violations, int)
        self.assertEqual(
            report.total_issues,
            report.critical_bugs + report.missing_features + report.ui_discrepancies + report.portability_violations
        )

        # Verificar persistencia de archivos
        json_file = reports_dir / "audit_iteration_1.json"
        md_file = reports_dir / "audit_iteration_1.md"
        self.assertTrue(json_file.exists())
        self.assertTrue(md_file.exists())

        json_text = json_file.read_text(encoding="utf-8")
        self.assertIn('"critical_bugs":', json_text)
        self.assertIn('"missing_features":', json_text)
        self.assertIn('"ui_discrepancies":', json_text)
        self.assertIn('"portability_violations":', json_text)


if __name__ == "__main__":
    unittest.main()
