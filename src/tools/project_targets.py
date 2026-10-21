"""
Project Targets Tracker para Escritorio
Seguimiento de objetivos de palabras globales del manuscrito y de la sesión diaria,
con cálculo de porcentaje de progreso y umbrales cromáticos.
"""

from typing import Dict, Any

class ProjectTargetsTracker:
    """Rastreador de metas de escritura."""

    def __init__(self, draft_target: int = 50000, session_target: int = 1500):
        self.draft_target = draft_target
        self.session_target = session_target
        self.session_initial_words = 0
        self.current_draft_words = 0
        self.session_written_words = 0

    def set_session_baseline(self, initial_total_words: int):
        self.session_initial_words = initial_total_words
        self.current_draft_words = initial_total_words
        self.session_written_words = 0

    def update_current_words(self, current_total_words: int):
        self.current_draft_words = current_total_words
        self.session_written_words = max(0, current_total_words - self.session_initial_words)

    def get_draft_progress_percent(self) -> float:
        if self.draft_target <= 0:
            return 100.0
        return min(100.0, (self.current_draft_words / self.draft_target) * 100.0)

    def get_session_progress_percent(self) -> float:
        if self.session_target <= 0:
            return 100.0
        return min(100.0, (self.session_written_words / self.session_target) * 100.0)

    def get_status_summary(self) -> Dict[str, Any]:
        return {
            "draft_target": self.draft_target,
            "draft_current": self.current_draft_words,
            "draft_percent": round(self.get_draft_progress_percent(), 1),
            "session_target": self.session_target,
            "session_current": self.session_written_words,
            "session_percent": round(self.get_session_progress_percent(), 1)
        }
