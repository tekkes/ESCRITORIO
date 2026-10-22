"""
Módulo de Agentes Especializados de Validación y Verificación Adversarial para Escritorio.
"""

from .base_agent import (
    RedTeamAgent,
    AuditIssue,
    AuditReport,
    Severity,
    IssueCategory
)
from .parity_inquisitor_agent import ParityInquisitorAgent
from .chaos_fuzzer_agent import ChaosFuzzerAgent
from .ui_ux_adversary_agent import UIUXAdversaryAgent
from .blue_team_fixer_agent import BlueTeamFixerAgent

__all__ = [
    "RedTeamAgent",
    "AuditIssue",
    "AuditReport",
    "Severity",
    "IssueCategory",
    "ParityInquisitorAgent",
    "ChaosFuzzerAgent",
    "UIUXAdversaryAgent",
    "BlueTeamFixerAgent",
]
