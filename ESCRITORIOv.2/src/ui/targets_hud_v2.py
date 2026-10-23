"""
ESCRITORIO v2.0 - Project Targets HUD (Objetivos de Proyecto y Sesión)
Ventana flotante con barras de progreso de Borrador y Sesión diaria, cálculo de fecha límite y días laborables.
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QSpinBox, QDateEdit, QPushButton, QCheckBox, QFrame
)
from PyQt6.QtCore import Qt, QDate
from ..core.project_v2 import EscritorioProjectV2


class TargetsHudV2(QDialog):
    """Panel flotante de objetivos de escritura cuantitativos idéntico a Scrivener 3 macOS."""

    def __init__(self, project: EscritorioProjectV2, current_draft_words: int, current_session_words: int, parent=None):
        super().__init__(parent)
        self.project = project
        self.draft_words = current_draft_words
        self.session_words = current_session_words

        self.setWindowTitle("Objetivos del Proyecto (Project Targets)")
        self.setFixedSize(450, 360)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # 1. Objetivo de Borrador (Draft Target)
        box_draft = QFrame()
        box_draft.setStyleSheet("background-color: #1e1e24; border-radius: 8px; padding: 12px;")
        d_layout = QVBoxLayout(box_draft)

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Objetivo del Borrador:"))
        self.spin_draft = QSpinBox()
        self.spin_draft.setRange(1000, 1000000)
        self.spin_draft.setSingleStep(1000)
        self.spin_draft.setValue(self.project.project_target_words)
        self.spin_draft.valueChanged.connect(self._on_draft_target_changed)
        h1.addWidget(self.spin_draft)
        d_layout.addLayout(h1)

        self.bar_draft = QProgressBar()
        self.bar_draft.setMaximum(self.project.project_target_words)
        self.bar_draft.setValue(self.draft_words)
        pct_draft = (self.draft_words / self.project.project_target_words * 100) if self.project.project_target_words > 0 else 0
        self.bar_draft.setFormat(f"{self.draft_words} de {self.project.project_target_words} ({pct_draft:.1f}%)")
        self.bar_draft.setStyleSheet("""
            QProgressBar {
                border: 1px solid #323242; border-radius: 4px; text-align: center; height: 18px; color: #ffffff;
            }
            QProgressBar::chunk { background-color: #3498db; }
        """)
        d_layout.addWidget(self.bar_draft)
        layout.addWidget(box_draft)

        # 2. Objetivo de Sesión (Session Target)
        box_session = QFrame()
        box_session.setStyleSheet("background-color: #1e1e24; border-radius: 8px; padding: 12px;")
        s_layout = QVBoxLayout(box_session)

        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Objetivo de la Sesión:"))
        self.spin_session = QSpinBox()
        self.spin_session.setRange(100, 20000)
        self.spin_session.setSingleStep(250)
        self.spin_session.setValue(self.project.session_target_words)
        self.spin_session.valueChanged.connect(self._on_session_target_changed)
        h2.addWidget(self.spin_session)

        btn_reset = QPushButton("↺ Reiniciar Sesión")
        btn_reset.clicked.connect(self._reset_session)
        h2.addWidget(btn_reset)
        s_layout.addLayout(h2)

        self.bar_session = QProgressBar()
        self.bar_session.setMaximum(self.project.session_target_words)
        self.bar_session.setValue(self.session_words)
        pct_sess = (self.session_words / self.project.session_target_words * 100) if self.project.session_target_words > 0 else 0
        self.bar_session.setFormat(f"{self.session_words} de {self.project.session_target_words} ({pct_sess:.1f}%)")
        self.bar_session.setStyleSheet("""
            QProgressBar {
                border: 1px solid #323242; border-radius: 4px; text-align: center; height: 18px; color: #ffffff;
            }
            QProgressBar::chunk { background-color: #2ecc71; }
        """)
        s_layout.addWidget(self.bar_session)
        layout.addWidget(box_session)

        # 3. Fecha Límite y Días de Trabajo
        box_deadline = QFrame()
        box_deadline.setStyleSheet("background-color: #1e1e24; border-radius: 8px; padding: 12px;")
        dl_layout = QVBoxLayout(box_deadline)

        h3 = QHBoxLayout()
        self.chk_deadline = QCheckBox("Activar Fecha Límite:")
        h3.addWidget(self.chk_deadline)

        self.date_picker = QDateEdit()
        self.date_picker.setDate(QDate.currentDate().addDays(60))
        self.date_picker.setCalendarPopup(True)
        h3.addWidget(self.date_picker)
        dl_layout.addLayout(h3)

        self.lbl_daily_quota = QLabel("Ritmo sugerido: calcula automáticamente las palabras/día según plazo.")
        self.lbl_daily_quota.setStyleSheet("color: #a0a0b2; font-size: 11px;")
        dl_layout.addWidget(self.lbl_daily_quota)

        layout.addWidget(box_deadline)

        # Botón cerrar
        btn_close = QPushButton("Aceptar")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _on_draft_target_changed(self, val):
        self.project.project_target_words = val
        self.bar_draft.setMaximum(val)

    def _on_session_target_changed(self, val):
        self.project.session_target_words = val
        self.bar_session.setMaximum(val)

    def _reset_session(self):
        self.session_words = 0
        self.bar_session.setValue(0)
        self.bar_session.setFormat(f"0 de {self.project.session_target_words} (0%)")
