"""
ESCRITORIO v2.0 - Writing Targets & Time Statistics HUD
Ventana integral de estadísticas de horas de trabajo (sesión, documento, diarias, semanales),
velocidad de redacción y edición interactiva de objetivos de borrador, sesión y fecha límite.
"""

import datetime
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QSpinBox, QDoubleSpinBox, QDateEdit, QPushButton, QCheckBox,
    QFrame, QTabWidget, QWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, QTimer
from ..core.project_v2 import EscritorioProjectV2, BinderNode
from ..core.stats_manager import WritingStatsManager
from ..core.xml_engine_v2 import XmlEngineV2


class TargetsHudV2(QDialog):
    """Panel flotante de objetivos de escritura y estadísticas de tiempo de Scrivener 3."""

    def __init__(
        self,
        project: EscritorioProjectV2,
        stats_mgr: WritingStatsManager,
        active_node: Optional[BinderNode] = None,
        parent=None
    ):
        super().__init__(parent)
        self.project = project
        self.stats_mgr = stats_mgr
        self.active_node = active_node

        self.setWindowTitle("⏱️ Estadísticas de Trabajo y Objetivos del Proyecto")
        self.resize(650, 560)

        self._init_ui()

        # Temporizador en vivo para refrescar cronómetros mientras el diálogo esté abierto
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._update_live_ui)
        self.refresh_timer.start(1000)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        self.tabs = QTabWidget(self)

        # -------------------------------------------------------------
        # PESTAÑA 1: 🎯 OBJETIVOS DEL PROYECTO Y SESIÓN (EDITABLES)
        # -------------------------------------------------------------
        tab_targets = QWidget()
        t_layout = QVBoxLayout(tab_targets)
        t_layout.setSpacing(12)
        t_layout.setContentsMargins(12, 12, 12, 12)

        # 1.1 Objetivo del Borrador
        box_draft = QFrame()
        box_draft.setProperty("class", "StatCard")
        bd_layout = QVBoxLayout(box_draft)

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("📖 Objetivo Total de la Obra (Borrador):"))
        self.spin_draft = QSpinBox()
        self.spin_draft.setRange(1000, 2000000)
        self.spin_draft.setSingleStep(1000)
        self.spin_draft.setValue(self.project.project_target_words)
        self.spin_draft.valueChanged.connect(self._recalculate_targets)
        h1.addWidget(self.spin_draft)
        bd_layout.addLayout(h1)

        self.bar_draft = QProgressBar()
        bd_layout.addWidget(self.bar_draft)
        t_layout.addWidget(box_draft)

        # 1.2 Objetivo de la Sesión
        box_session = QFrame()
        box_session.setProperty("class", "StatCard")
        bs_layout = QVBoxLayout(box_session)

        h2 = QHBoxLayout()
        h2.addWidget(QLabel("✍️ Objetivo de Palabras por Sesión Diaria:"))
        self.spin_session = QSpinBox()
        self.spin_session.setRange(100, 50000)
        self.spin_session.setSingleStep(250)
        self.spin_session.setValue(self.project.session_target_words)
        self.spin_session.valueChanged.connect(self._recalculate_targets)
        h2.addWidget(self.spin_session)

        btn_reset_session = QPushButton("↺ Reiniciar Sesión")
        btn_reset_session.clicked.connect(self._reset_session_words)
        h2.addWidget(btn_reset_session)
        bs_layout.addLayout(h2)

        self.bar_session = QProgressBar()
        bs_layout.addWidget(self.bar_session)
        t_layout.addWidget(box_session)

        # 1.3 Objetivo de Horas Diarias de Trabajo
        box_hours = QFrame()
        box_hours.setProperty("class", "StatCard")
        bh_layout = QVBoxLayout(box_hours)

        h_h = QHBoxLayout()
        h_h.addWidget(QLabel("⏱️ Objetivo de Horas de Trabajo Diarias:"))
        self.spin_hours = QDoubleSpinBox()
        self.spin_hours.setRange(0.25, 16.0)
        self.spin_hours.setSingleStep(0.5)
        self.spin_hours.setValue(getattr(self.project, "daily_hours_target", 2.0))
        self.spin_hours.setSuffix(" horas/día")
        self.spin_hours.valueChanged.connect(self._recalculate_targets)
        h_h.addWidget(self.spin_hours)
        bh_layout.addLayout(h_h)

        self.bar_hours = QProgressBar()
        bh_layout.addWidget(self.bar_hours)
        t_layout.addWidget(box_hours)

        # 1.4 Plazo y Días Laborables
        box_deadline = QFrame()
        box_deadline.setProperty("class", "StatCard")
        bdl_layout = QVBoxLayout(box_deadline)

        h3 = QHBoxLayout()
        self.chk_deadline = QCheckBox("Activar Fecha Límite (Deadline):")
        self.chk_deadline.setChecked(bool(self.project.target_deadline))
        self.chk_deadline.toggled.connect(self._recalculate_targets)
        h3.addWidget(self.chk_deadline)

        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        if self.project.target_deadline:
            q_date = QDate.fromString(self.project.target_deadline, Qt.DateFormat.ISODate)
            self.date_picker.setDate(q_date if q_date.isValid() else QDate.currentDate().addDays(60))
        else:
            self.date_picker.setDate(QDate.currentDate().addDays(60))
        self.date_picker.dateChanged.connect(self._recalculate_targets)
        h3.addWidget(self.date_picker)
        bdl_layout.addLayout(h3)

        # Checkboxes días de la semana
        h_days = QHBoxLayout()
        h_days.addWidget(QLabel("Días de trabajo:"))
        self.day_checkboxes = []
        days_names_short = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        work_days = getattr(self.project, "target_work_days", [0, 1, 2, 3, 4])
        for idx, name in enumerate(days_names_short):
            chk = QCheckBox(name)
            chk.setChecked(idx in work_days)
            chk.toggled.connect(self._recalculate_targets)
            self.day_checkboxes.append(chk)
            h_days.addWidget(chk)
        bdl_layout.addLayout(h_days)

        self.lbl_rhythm_info = QLabel()
        self.lbl_rhythm_info.setStyleSheet("color: #3498db; font-weight: bold; font-size: 11px;")
        bdl_layout.addWidget(self.lbl_rhythm_info)
        t_layout.addWidget(box_deadline)

        # Botón Guardar Objetivos
        btn_save_targets = QPushButton("💾 Guardar Objetivos en el Proyecto")
        btn_save_targets.setObjectName("PrimaryButton")
        btn_save_targets.clicked.connect(self._save_targets_to_project)
        t_layout.addWidget(btn_save_targets)

        self.tabs.addTab(tab_targets, "🎯 Objetivos (Editar)")

        # -------------------------------------------------------------
        # PESTAÑA 2: ⏱️ HORAS DE TRABAJO Y TIEMPO DE DEDICACIÓN
        # -------------------------------------------------------------
        tab_time = QWidget()
        time_layout = QVBoxLayout(tab_time)
        time_layout.setSpacing(12)
        time_layout.setContentsMargins(12, 12, 12, 12)

        # Fila superior: Sesión Actual y Documento Actual
        h_current = QHBoxLayout()

        # Tarjeta Sesión Actual
        card_session = QFrame()
        card_session.setProperty("class", "StatCard")
        cs_layout = QVBoxLayout(card_session)
        cs_layout.addWidget(QLabel("<b>⏱️ Sesión Actual</b>"))
        self.lbl_session_total = QLabel("Total: 0s")
        self.lbl_session_active = QLabel("Activa: 0s")
        self.lbl_session_words = QLabel("Palabras: 0")
        self.lbl_session_wph = QLabel("Velocidad: 0 pal/hora")
        self.lbl_session_wph.setStyleSheet("color: #2ecc71; font-weight: bold;")
        cs_layout.addWidget(self.lbl_session_total)
        cs_layout.addWidget(self.lbl_session_active)
        cs_layout.addWidget(self.lbl_session_words)
        cs_layout.addWidget(self.lbl_session_wph)
        h_current.addWidget(card_session)

        # Tarjeta Documento Actual
        card_doc = QFrame()
        card_doc.setProperty("class", "StatCard")
        cd_layout = QVBoxLayout(card_doc)
        cd_layout.addWidget(QLabel("<b>📄 Documento Actual</b>"))
        self.lbl_doc_title = QLabel("Documento: Ninguno")
        self.lbl_doc_time = QLabel("Tiempo invertido: 0s")
        self.lbl_doc_words = QLabel("Palabras: 0")
        self.lbl_doc_read_time = QLabel("Lectura: ~0 min")
        cd_layout.addWidget(self.lbl_doc_title)
        cd_layout.addWidget(self.lbl_doc_time)
        cd_layout.addWidget(self.lbl_doc_words)
        cd_layout.addWidget(self.lbl_doc_read_time)
        h_current.addWidget(card_doc)

        time_layout.addLayout(h_current)

        # Tarjeta Resumen Hoy y Semana
        card_summary = QFrame()
        card_summary.setProperty("class", "StatCard")
        csum_layout = QHBoxLayout(card_summary)

        # Hoy
        v_today = QVBoxLayout()
        v_today.addWidget(QLabel("<b>📅 Hoy</b>"))
        self.lbl_today_time = QLabel("0h 00m")
        self.lbl_today_time.setProperty("class", "StatValue")
        self.lbl_today_words = QLabel("0 palabras")
        v_today.addWidget(self.lbl_today_time)
        v_today.addWidget(self.lbl_today_words)
        csum_layout.addLayout(v_today)

        # Esta Semana
        v_week = QVBoxLayout()
        v_week.addWidget(QLabel("<b>📊 Esta Semana (7 días)</b>"))
        self.lbl_week_time = QLabel("0h 00m")
        self.lbl_week_time.setProperty("class", "StatValue")
        self.lbl_week_words = QLabel("0 palabras")
        v_week.addWidget(self.lbl_week_time)
        v_week.addWidget(self.lbl_week_words)
        csum_layout.addLayout(v_week)

        # Promedio Diario
        v_avg = QVBoxLayout()
        v_avg.addWidget(QLabel("<b>⚡ Promedio Diario</b>"))
        self.lbl_avg_hours = QLabel("0.0 h/día")
        self.lbl_avg_hours.setProperty("class", "StatValue")
        self.lbl_avg_words = QLabel("0 pal/día")
        v_avg.addWidget(self.lbl_avg_hours)
        v_avg.addWidget(self.lbl_avg_words)
        csum_layout.addLayout(v_avg)

        time_layout.addWidget(card_summary)

        # Tabla de desglose de los últimos 7 días
        time_layout.addWidget(QLabel("<b>Historial Diario de Dedicación (Últimos 7 días):</b>"))
        self.tbl_history = QTableWidget()
        self.tbl_history.setColumnCount(5)
        self.tbl_history.setHorizontalHeaderLabels(["Fecha", "Día", "Horas Totales", "Horas Activas", "Palabras"])
        self.tbl_history.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_history.setFixedHeight(120)
        time_layout.addWidget(self.tbl_history)

        self.tabs.addTab(tab_time, "⏱️ Horas de Trabajo")

        # -------------------------------------------------------------
        # PESTAÑA 3: 📊 ESTADÍSTICAS DEL MANUSCRITO COMPLETO
        # -------------------------------------------------------------
        tab_manuscript = QWidget()
        m_layout = QVBoxLayout(tab_manuscript)
        m_layout.setSpacing(12)
        m_layout.setContentsMargins(12, 12, 12, 12)

        card_global = QFrame()
        card_global.setProperty("class", "StatCard")
        cg_layout = QVBoxLayout(card_global)

        self.lbl_m_words = QLabel()
        self.lbl_m_words.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.lbl_m_chars = QLabel()
        self.lbl_m_pages = QLabel()
        self.lbl_m_read = QLabel()

        cg_layout.addWidget(self.lbl_m_words)
        cg_layout.addWidget(self.lbl_m_chars)
        cg_layout.addWidget(self.lbl_m_pages)
        cg_layout.addWidget(self.lbl_m_read)
        m_layout.addWidget(card_global)

        m_layout.addStretch()

        self.tabs.addTab(tab_manuscript, "📊 Manuscrito Completo")

        main_layout.addWidget(self.tabs)

        # Barra inferior de cierre
        h_bot = QHBoxLayout()
        h_bot.addStretch()
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        h_bot.addWidget(btn_close)
        main_layout.addLayout(h_bot)

        # Cargar datos iniciales
        self._recalculate_targets()
        self._update_live_ui()

    def _recalculate_targets(self):
        """Calcula el progreso de objetivos y el ritmo diario necesario."""
        draft_words = self.project.draft_node.total_word_count() if self.project.draft_node else 0
        target_draft = max(1, self.spin_draft.value())
        pct_draft = min(100.0, (draft_words / target_draft) * 100.0)

        self.bar_draft.setMaximum(target_draft)
        self.bar_draft.setValue(draft_words)
        self.bar_draft.setFormat(f"{draft_words:,} de {target_draft:,} palabras ({pct_draft:.1f}%)")

        # Sesión
        session_words = self.stats_mgr.session_words_written
        target_session = max(1, self.spin_session.value())
        pct_session = min(100.0, (session_words / target_session) * 100.0)

        self.bar_session.setMaximum(target_session)
        self.bar_session.setValue(session_words)
        self.bar_session.setFormat(f"{session_words:,} de {target_session:,} palabras ({pct_session:.1f}%)")

        # Horas
        today_stats = self.stats_mgr.get_today_stats()
        today_hours = today_stats["hours"]
        target_hours = max(0.1, self.spin_hours.value())
        pct_hours = min(100.0, (today_hours / target_hours) * 100.0)

        self.bar_hours.setMaximum(int(target_hours * 60))
        self.bar_hours.setValue(int(today_hours * 60))
        self.bar_hours.setFormat(f"{today_hours:.1f}h de {target_hours:.1f}h ({pct_hours:.1f}%)")

        # Ritmo según Fecha Límite
        if self.chk_deadline.isChecked():
            target_date = self.date_picker.date().toPyDate()
            today = datetime.date.today()
            total_days = (target_date - today).days

            if total_days > 0:
                selected_days = [i for i, chk in enumerate(self.day_checkboxes) if chk.isChecked()]
                if not selected_days:
                    selected_days = [0, 1, 2, 3, 4]

                # Contar días hábiles reales hasta la fecha
                work_days_count = 0
                cur = today
                while cur < target_date:
                    if cur.weekday() in selected_days:
                        work_days_count += 1
                    cur += datetime.timedelta(days=1)

                work_days_count = max(1, work_days_count)
                words_needed = max(0, target_draft - draft_words)
                daily_quota = int(words_needed / work_days_count)
                hours_quota = round(daily_quota / 500.0, 1)  # Estimando 500 palabras/hora

                self.lbl_rhythm_info.setText(
                    f"📅 Quedan {work_days_count} días laborables. "
                    f"Ritmo necesario: {daily_quota:,} palabras/día (~{hours_quota}h diarias)."
                )
            else:
                self.lbl_rhythm_info.setText("⚠️ La fecha límite indicada ya ha transcurrido o es hoy.")
        else:
            self.lbl_rhythm_info.setText("💡 Activa la fecha límite para calcular el ritmo de trabajo sugerido.")

    def _update_live_ui(self):
        """Actualiza en tiempo real los cronómetros y tablas."""
        # Sesión actual
        s_stats = self.stats_mgr.get_session_stats()
        self.lbl_session_total.setText(f"Tiempo Total: <b>{s_stats['formatted_total']}</b>")
        self.lbl_session_active.setText(f"Escritura Activa: <b>{s_stats['formatted_active']}</b>")
        self.lbl_session_words.setText(f"Palabras Escritas: <b>{s_stats['words']:,}</b>")
        self.lbl_session_wph.setText(f"Velocidad: <b>{s_stats['wph']:,} palabras/hora</b>")

        # Documento actual
        if self.active_node:
            self.lbl_doc_title.setText(f"Documento: <b>{self.active_node.title}</b>")
            doc_sec = self.stats_mgr.get_doc_time(self.active_node.uuid)
            self.lbl_doc_time.setText(f"Tiempo dedicado: <b>{self.stats_mgr.format_hms(doc_sec)}</b>")
            words = self.active_node.word_count()
            self.lbl_doc_words.setText(f"Palabras: <b>{words:,}</b>")
            read_min = max(1, int(words / 200)) if words > 0 else 0
            self.lbl_doc_read_time.setText(f"Lectura: <b>~{read_min} minutos</b>")
        else:
            self.lbl_doc_title.setText("Documento: <i>Ninguno seleccionado</i>")

        # Hoy y Semana
        today = self.stats_mgr.get_today_stats()
        self.lbl_today_time.setText(today["formatted_total"])
        self.lbl_today_words.setText(f"{today['words']:,} palabras hoy")

        week = self.stats_mgr.get_week_stats()
        self.lbl_week_time.setText(week["formatted_total"])
        self.lbl_week_words.setText(f"{week['words']:,} palabras esta semana")

        self.lbl_avg_hours.setText(f"{week['avg_daily_hours']} h/día")
        self.lbl_avg_words.setText(f"{week['avg_daily_words']} pal/día")

        # Llenar tabla de historial de los últimos 7 días
        days = week["days"]
        self.tbl_history.setRowCount(len(days))
        for row, d in enumerate(days):
            self.tbl_history.setItem(row, 0, QTableWidgetItem(d["date"]))
            self.tbl_history.setItem(row, 1, QTableWidgetItem(d["day_name"]))
            self.tbl_history.setItem(row, 2, QTableWidgetItem(d["formatted_total"]))
            self.tbl_history.setItem(row, 3, QTableWidgetItem(d["formatted_active"]))
            self.tbl_history.setItem(row, 4, QTableWidgetItem(f"{d['words']:,}"))

        # Pestaña Manuscrito Completo
        if self.project.draft_node:
            total_w = self.project.draft_node.total_word_count()
            chars = total_w * 6  # Estimación
            pages = max(1, int(total_w / 250))
            read_hours = round(total_w / (200 * 60), 1)

            self.lbl_m_words.setText(f"📖 Total de Palabras de la Obra: {total_w:,}")
            self.lbl_m_chars.setText(f"🔤 Caracteres estimados: {chars:,}")
            self.lbl_m_pages.setText(f"📄 Páginas impresas estimadas (250 pal/pág): {pages:,} páginas")
            self.lbl_m_read.setText(f"⏳ Tiempo estimado de lectura completa: ~{read_hours} horas")

    def _reset_session_words(self):
        self.stats_mgr.session_words_written = 0
        self._recalculate_targets()

    def _save_targets_to_project(self):
        """Guarda las modificaciones de objetivos en el archivo del proyecto."""
        self.project.project_target_words = self.spin_draft.value()
        self.project.session_target_words = self.spin_session.value()
        self.project.daily_hours_target = self.spin_hours.value()

        if self.chk_deadline.isChecked():
            self.project.target_deadline = self.date_picker.date().toString(Qt.DateFormat.ISODate)
        else:
            self.project.target_deadline = None

        self.project.target_work_days = [i for i, chk in enumerate(self.day_checkboxes) if chk.isChecked()]

        # Guardar archivo maestro XML
        try:
            xml_path = self.project.path / f"{self.project.name}.escrx"
            XmlEngineV2.save_project_xml(self.project, xml_path)
            QMessageBox.information(
                self,
                "Objetivos Guardados",
                f"✅ Objetivos guardados con éxito en [{self.project.name}]:\n\n"
                f"• Borrador: {self.project.project_target_words:,} palabras\n"
                f"• Sesión diaria: {self.project.session_target_words:,} palabras\n"
                f"• Horas de trabajo: {self.project.daily_hours_target} horas/día"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error al Guardar", f"No se pudieron guardar los objetivos: {e}")
