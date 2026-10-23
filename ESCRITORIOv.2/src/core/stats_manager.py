"""
ESCRITORIO v2.0 - Writing Statistics & Time Tracking Engine
Mide con precisión atómica las horas de trabajo en sesión, por documento, diarias y semanales,
con detección de inactividad, cálculo de ritmo (palabras/hora) y persistencia en disco.
"""

import time
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class WritingStatsManager:
    """Gestor de tiempo y métricas cuantitativas de trabajo editorial."""

    DAY_NAMES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.stats_file = self.config_dir / "writing_stats.json"

        # Tiempos de la sesión actual en memoria
        self.session_start_time: float = time.time()
        self.total_session_seconds: float = 0.0
        self.active_session_seconds: float = 0.0
        self.last_activity_time: float = time.time()
        self.active_node_uuid: Optional[str] = None
        self.session_words_written: int = 0

        # Tiempos acumulados por documento
        self.doc_seconds: Dict[str, float] = {}

        # Historial persistente en disco
        self.history: Dict[str, Any] = self._load_history()

    def _load_history(self) -> Dict[str, Any]:
        if self.stats_file.exists():
            try:
                with open(self.stats_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.doc_seconds = data.get("doc_seconds", {})
                    return data
            except Exception:
                pass
        return {"days": {}, "doc_seconds": {}}

    def save(self):
        """Guarda atómicamente el historial en disco."""
        today_str = datetime.date.today().isoformat()
        days = self.history.setdefault("days", {})
        today_entry = days.setdefault(today_str, {"total_seconds": 0.0, "active_seconds": 0.0, "words": 0})

        # Actualizar datos de hoy
        today_entry["total_seconds"] += self.total_session_seconds
        today_entry["active_seconds"] += self.active_session_seconds
        today_entry["words"] += self.session_words_written

        # Reestablecer contadores de sesión volcados a hoy
        self.total_session_seconds = 0.0
        self.active_session_seconds = 0.0
        self.session_words_written = 0

        self.history["doc_seconds"] = self.doc_seconds

        tmp = self.stats_file.with_suffix(".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            tmp.replace(self.stats_file)
        except Exception:
            pass

    def on_tick(self):
        """Llamado cada segundo por el temporizador principal."""
        self.total_session_seconds += 1.0

        # Si el usuario escribió o interactuó en los últimos 60 segundos, cuenta como tiempo activo
        now = time.time()
        if now - self.last_activity_time <= 60.0:
            self.active_session_seconds += 1.0
            if self.active_node_uuid:
                self.doc_seconds[self.active_node_uuid] = self.doc_seconds.get(self.active_node_uuid, 0.0) + 1.0

    def on_keystroke(self, words_delta: int = 0):
        """Registra actividad del usuario en el teclado."""
        self.last_activity_time = time.time()
        if words_delta > 0:
            self.session_words_written += words_delta

    def set_active_node(self, node_uuid: Optional[str]):
        """Actualiza el documento sobre el que se está trabajando."""
        self.active_node_uuid = node_uuid

    def get_session_stats(self) -> Dict[str, Any]:
        """Obtiene las estadísticas de la sesión actual."""
        active = self.active_session_seconds
        wph = int(self.session_words_written / (active / 3600.0)) if active >= 30.0 else 0
        return {
            "total_seconds": self.total_session_seconds,
            "active_seconds": self.active_session_seconds,
            "words": self.session_words_written,
            "wph": wph,
            "formatted_total": self.format_hms(self.total_session_seconds),
            "formatted_active": self.format_hms(self.active_session_seconds),
        }

    def get_doc_time(self, node_uuid: Optional[str]) -> float:
        """Segundos dedicados al documento solicitado."""
        if not node_uuid:
            return 0.0
        return self.doc_seconds.get(node_uuid, 0.0)

    def get_today_stats(self) -> Dict[str, Any]:
        """Obtiene las estadísticas agregadas del día de hoy."""
        today_str = datetime.date.today().isoformat()
        day_hist = self.history.get("days", {}).get(today_str, {"total_seconds": 0.0, "active_seconds": 0.0, "words": 0})
        total_sec = day_hist.get("total_seconds", 0.0) + self.total_session_seconds
        active_sec = day_hist.get("active_seconds", 0.0) + self.active_session_seconds
        words = day_hist.get("words", 0) + self.session_words_written
        return {
            "total_seconds": total_sec,
            "active_seconds": active_sec,
            "words": words,
            "formatted_total": self.format_hms(total_sec),
            "formatted_active": self.format_hms(active_sec),
            "hours": total_sec / 3600.0,
            "active_hours": active_sec / 3600.0,
        }

    def get_week_stats(self) -> Dict[str, Any]:
        """Calcula el tiempo y palabras de los últimos 7 días."""
        days_breakdown: List[Dict[str, Any]] = []
        total_week_seconds = 0.0
        active_week_seconds = 0.0
        words_week = 0

        today = datetime.date.today()
        history_days = self.history.get("days", {})

        # Iterar los últimos 7 días (de hace 6 días a hoy)
        for i in range(6, -1, -1):
            d = today - datetime.timedelta(days=i)
            d_str = d.isoformat()
            day_entry = history_days.get(d_str, {"total_seconds": 0.0, "active_seconds": 0.0, "words": 0})

            t_sec = day_entry.get("total_seconds", 0.0)
            a_sec = day_entry.get("active_seconds", 0.0)
            w = day_entry.get("words", 0)

            # Si es hoy, sumar los datos en caliente de la sesión actual
            if i == 0:
                t_sec += self.total_session_seconds
                a_sec += self.active_session_seconds
                w += self.session_words_written

            total_week_seconds += t_sec
            active_week_seconds += a_sec
            words_week += w

            days_breakdown.append({
                "date": d_str,
                "day_name": self.DAY_NAMES[d.weekday()],
                "total_hours": round(t_sec / 3600.0, 2),
                "active_hours": round(a_sec / 3600.0, 2),
                "formatted_total": self.format_hms(t_sec),
                "formatted_active": self.format_hms(a_sec),
                "words": w
            })

        avg_daily_hours = round((total_week_seconds / 3600.0) / 7.0, 2)
        avg_daily_words = int(words_week / 7.0)

        return {
            "total_seconds": total_week_seconds,
            "active_seconds": active_week_seconds,
            "words": words_week,
            "formatted_total": self.format_hms(total_week_seconds),
            "formatted_active": self.format_hms(active_week_seconds),
            "avg_daily_hours": avg_daily_hours,
            "avg_daily_words": avg_daily_words,
            "days": days_breakdown
        }

    @staticmethod
    def format_hms(seconds: float) -> str:
        """Formatea segundos a 'Xh Ym' o 'Xh Ym Zs'."""
        sec = int(seconds)
        hours = sec // 3600
        minutes = (sec % 3600) // 60
        rem_sec = sec % 60
        if hours > 0:
            return f"{hours}h {minutes:02d}m {rem_sec:02d}s"
        elif minutes > 0:
            return f"{minutes}m {rem_sec:02d}s"
        else:
            return f"{rem_sec}s"
