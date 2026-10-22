"""
Project Targets Tracker para Escritorio.
Seguimiento avanzado de metas de redacción:
- Barras de progreso duales: Objetivo del Manuscrito (Draft Target) y Objetivo de la Sesión (Session Target).
- Configuración de Fecha Límite (Deadline).
- Selección de días semanales de escritura (e.g. Lunes a Viernes, fines de semana, etc.).
- Cálculo dinámico de la cuota diaria de palabras necesaria para completar la obra a tiempo.
- Métricas de ritmo (On Track, Ahead, Behind).
"""

import math
import datetime
from typing import List, Set, Dict, Optional, Any, Union
from ..core.project import EscritorioProject, BinderItem
from ..core.rtf_engine import RTFEngine


class ProjectTargetsTracker:
    """Rastreador de metas de escritura con calculadora de fecha límite y cuota diaria."""

    # Días de la semana estándar (0: Lunes, 6: Domingo)
    WEEKDAY_NAMES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    WEEKDAY_SHORT = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

    def __init__(
        self,
        draft_target: int = 50000,
        session_target: int = 1500,
        deadline_date: Optional[Union[str, datetime.date]] = None,
        writing_days: Optional[Set[int]] = None,
        project: Optional[EscritorioProject] = None
    ):
        self.project: Optional[EscritorioProject] = project

        # Objetivos numéricos
        self.draft_target: int = max(0, draft_target)
        self.session_target: int = max(0, session_target)

        # Contadores de progreso
        self.session_initial_words: int = 0
        self.current_draft_words: int = 0
        self.session_written_words: int = 0
        self.allow_negative_session: bool = False

        # Configuración de Fecha Límite (Deadline)
        self.deadline_date: Optional[datetime.date] = None
        if deadline_date:
            self.set_deadline(deadline_date)

        # Días de escritura semanales (por defecto Lunes a Viernes: {0, 1, 2, 3, 4})
        self.writing_days: Set[int] = writing_days if writing_days is not None else {0, 1, 2, 3, 4}

        # Estado de la ventana flotante (Ctrl+Shift+T)
        self.is_dialog_open: bool = False

        if self.project:
            self.recalculate_from_project()

    # =========================================================================
    # Configuración de Objetivos
    # =========================================================================

    def set_draft_target(self, target: int):
        self.draft_target = max(0, int(target))

    def set_session_target(self, target: int):
        self.session_target = max(0, int(target))

    def set_deadline(self, deadline: Union[str, datetime.date, datetime.datetime]):
        if isinstance(deadline, (datetime.date, datetime.datetime)):
            self.deadline_date = deadline if isinstance(deadline, datetime.date) else deadline.date()
        elif isinstance(deadline, str):
            # Parsear formatos comunes: YYYY-MM-DD o DD/MM/YYYY
            clean = deadline.strip()
            if "/" in clean:
                parts = clean.split("/")
                if len(parts) == 3:
                    self.deadline_date = datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
            else:
                self.deadline_date = datetime.date.fromisoformat(clean)

    def set_writing_days(self, days: Union[Set[int], List[int]]):
        self.writing_days = {d % 7 for d in days}

    def toggle_writing_day(self, weekday: int) -> bool:
        """Activa o desactiva un día de la semana (0=Lunes..6=Domingo)."""
        day = weekday % 7
        if day in self.writing_days:
            # Asegurar al menos un día activo
            if len(self.writing_days) > 1:
                self.writing_days.remove(day)
                return False
            return True
        else:
            self.writing_days.add(day)
            return True

    def toggle_dialog(self) -> bool:
        """Atajo Ctrl+Shift+T para conmutar la ventana flotante."""
        self.is_dialog_open = not self.is_dialog_open
        return self.is_dialog_open

    # =========================================================================
    # Actualización de Conteos
    # =========================================================================

    def set_session_baseline(self, initial_total_words: int):
        self.session_initial_words = initial_total_words
        self.current_draft_words = initial_total_words
        self.session_written_words = 0

    def update_current_words(self, current_total_words: int):
        self.current_draft_words = current_total_words
        diff = current_total_words - self.session_initial_words
        self.session_written_words = diff if self.allow_negative_session else max(0, diff)

    def reset_session(self):
        """Reinicia el contador de la sesión fijando la base en el número actual de palabras."""
        self.session_initial_words = self.current_draft_words
        self.session_written_words = 0

    def recalculate_from_project(self) -> int:
        """Calcula el total de palabras de todos los documentos dentro de la carpeta Borrador (Draft)."""
        if not self.project:
            return self.current_draft_words

        total_words = 0
        draft = self.project.get_draft_folder()

        def sum_words(node: BinderItem):
            nonlocal total_words
            if node.item_type.lower() == "text":
                content = node.read_content_rtf()
                text = RTFEngine.rtf_to_plain_text(content)
                total_words += len(text.split())
            for child in node.children:
                sum_words(child)

        if draft:
            sum_words(draft)

        self.update_current_words(total_words)
        return total_words

    # =========================================================================
    # Porcentajes y Colores de Progreso
    # =========================================================================

    def get_draft_progress_percent(self) -> float:
        if self.draft_target <= 0:
            return 100.0
        return min(100.0, (self.current_draft_words / self.draft_target) * 100.0)

    def get_session_progress_percent(self) -> float:
        if self.session_target <= 0:
            return 100.0
        return min(100.0, (self.session_written_words / self.session_target) * 100.0)

    @staticmethod
    def get_progress_color(percent: float) -> str:
        """Devuelve el código hexadecimal de color según el umbral Scrivener 3."""
        if percent < 50.0:
            return "#EF4444"  # Rojo
        elif percent < 100.0:
            return "#F59E0B"  # Ámbar
        else:
            return "#10B981"  # Verde esmeralda (Completado)

    # =========================================================================
    # Calculadora de Fecha Límite y Cuota Diaria (Deadline Calculator)
    # =========================================================================

    def get_days_remaining(self, today: Optional[datetime.date] = None) -> int:
        if not self.deadline_date:
            return 0
        ref_today = today or datetime.date.today()
        delta = (self.deadline_date - ref_today).days
        return max(0, delta)

    def get_writing_days_remaining(self, today: Optional[datetime.date] = None) -> int:
        """
        Cuenta los días efectivos de escritura configurados entre hoy y la fecha límite inclusive.
        """
        if not self.deadline_date:
            return 0
        ref_today = today or datetime.date.today()
        if ref_today > self.deadline_date:
            return 0

        count = 0
        cur = ref_today
        while cur <= self.deadline_date:
            if cur.weekday() in self.writing_days:
                count += 1
            cur += datetime.timedelta(days=1)
        return count

    def get_daily_word_quota(self, today: Optional[datetime.date] = None) -> int:
        """
        Calcula la cantidad de palabras que el autor debe escribir por sesión activa
        para alcanzar el objetivo del manuscrito a tiempo.
        """
        remaining_words = max(0, self.draft_target - self.current_draft_words)
        if remaining_words == 0:
            return 0

        writing_days_left = self.get_writing_days_remaining(today)
        if writing_days_left <= 0:
            # Si no quedan días de escritura pero aún faltan palabras
            return remaining_words

        return int(math.ceil(remaining_words / writing_days_left))

    def get_pacing_status(self, today: Optional[datetime.date] = None) -> str:
        """Evalúa si el autor va a buen ritmo para alcanzar la fecha límite."""
        if self.current_draft_words >= self.draft_target:
            return "Completado"

        if not self.deadline_date:
            return "Sin fecha límite"

        ref_today = today or datetime.date.today()
        if ref_today >= self.deadline_date:
            return "Fecha Límite Excedida"

        quota = self.get_daily_word_quota(ref_today)
        if self.session_written_words >= quota:
            return "Buen Ritmo (Cuota Diaria Alcanzada)"
        elif quota > self.session_target * 1.5:
            return "Ritmo Exigente (Atrás en el calendario)"
        else:
            return "En Curso (Ritmo adecuado)"

    # =========================================================================
    # Resumen y Estado de la Ventana Flotante (Ctrl+Shift+T)
    # =========================================================================

    def get_status_summary(self, today: Optional[datetime.date] = None) -> Dict[str, Any]:
        draft_pct = self.get_draft_progress_percent()
        sess_pct = self.get_session_progress_percent()

        return {
            "draft_target": self.draft_target,
            "draft_current": self.current_draft_words,
            "draft_remaining": max(0, self.draft_target - self.current_draft_words),
            "draft_percent": round(draft_pct, 1),
            "draft_color": self.get_progress_color(draft_pct),
            "session_target": self.session_target,
            "session_current": self.session_written_words,
            "session_percent": round(sess_pct, 1),
            "session_color": self.get_progress_color(sess_pct),
            "deadline_date": self.deadline_date.isoformat() if self.deadline_date else None,
            "days_remaining": self.get_days_remaining(today),
            "writing_days_remaining": self.get_writing_days_remaining(today),
            "daily_word_quota": self.get_daily_word_quota(today),
            "pacing_status": self.get_pacing_status(today),
            "active_writing_days": sorted(list(self.writing_days)),
            "is_dialog_open": self.is_dialog_open
        }

    to_dict = get_status_summary
