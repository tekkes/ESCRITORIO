"""
ESCRITORIO v2.0 - Linguistic Focus & Writing Statistics
Analizador estilístico para pulir la prosa y estadísticas avanzadas de legibilidad.
"""

import re
from typing import Dict, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTextEdit, QPushButton, QFrame, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


class LinguisticFocusDialog(QDialog):
    """Analizador de estilo y foco lingüístico."""

    def __init__(self, raw_text: str, parent=None):
        super().__init__(parent)
        self.raw_text = raw_text
        self.setWindowTitle("Foco Lingüístico y Estadísticas de Estilo")
        self.resize(650, 520)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        tabs = QTabWidget(self)

        # Tab 1: Foco Lingüístico
        tab_focus = QWidget()
        tf_layout = QVBoxLayout(tab_focus)

        h_ctrl = QHBoxLayout()
        h_ctrl.addWidget(QLabel("Resaltar categoría:"))
        self.combo_focus = QComboBox()
        self.combo_focus.addItems([
            "Todo el texto",
            "Solo Diálogos (comillas y rayas)",
            "Solo Narración (excluir diálogo)",
            "Adverbios en '-mente'",
            "Conjunciones y Conectores"
        ])
        self.combo_focus.currentIndexChanged.connect(self._apply_focus)
        h_ctrl.addWidget(self.combo_focus)
        h_ctrl.addStretch()
        tf_layout.addLayout(h_ctrl)

        self.txt_preview = QTextEdit()
        self.txt_preview.setFont(QFont("Georgia", 11))
        self.txt_preview.setReadOnly(True)
        tf_layout.addWidget(self.txt_preview)

        tabs.addTab(tab_focus, "🔍 Foco Lingüístico")

        # Tab 2: Estadísticas y Frecuencia de Palabras
        tab_stats = QWidget()
        ts_layout = QVBoxLayout(tab_stats)

        words = self.raw_text.split()
        num_words = len(words)
        num_chars = len(self.raw_text)
        sentences = [s for s in re.split(r'[.!?]+', self.raw_text) if s.strip()]
        num_sentences = max(1, len(sentences))
        avg_sentence_len = num_words / num_sentences

        stats_box = QFrame()
        stats_box.setStyleSheet("background-color: #1e1e24; border-radius: 6px; padding: 10px;")
        sb_layout = QVBoxLayout(stats_box)
        sb_layout.addWidget(QLabel(f"Total de palabras: {num_words:,}"))
        sb_layout.addWidget(QLabel(f"Total de caracteres: {num_chars:,}"))
        sb_layout.addWidget(QLabel(f"Total de oraciones: {num_sentences:,}"))
        sb_layout.addWidget(QLabel(f"Longitud media de oración: {avg_sentence_len:.1f} palabras"))
        sb_layout.addWidget(QLabel(f"Tiempo estimado de lectura: {max(1, num_words // 200)} min (a 200 ppm)"))
        ts_layout.addWidget(stats_box)

        # Tabla de frecuencia de palabras
        ts_layout.addWidget(QLabel("Frecuencia de términos más repetidos:"))
        self.table_freq = QTableWidget()
        self.table_freq.setColumnCount(2)
        self.table_freq.setHeaderLabels(["Palabra", "Repeticiones"])
        self.table_freq.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Contar palabras significativas (> 3 letras)
        word_counts: Dict[str, int] = {}
        for w in words:
            clean = re.sub(r'[^\w]', '', w.lower())
            if len(clean) > 3:
                word_counts[clean] = word_counts.get(clean, 0) + 1

        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:30]
        self.table_freq.setRowCount(len(sorted_words))
        for row, (term, count) in enumerate(sorted_words):
            self.table_freq.setItem(row, 0, QTableWidgetItem(term))
            self.table_freq.setItem(row, 1, QTableWidgetItem(str(count)))

        ts_layout.addWidget(self.table_freq)
        tabs.addTab(tab_stats, "📊 Frecuencia y Métricas")

        layout.addWidget(tabs)

        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        self._apply_focus(0)

    def _apply_focus(self, idx: int):
        text = self.raw_text
        if idx == 0:  # Todo
            self.txt_preview.setPlainText(text)
        elif idx == 1:  # Diálogos
            # Resaltar en verde lo que esté entre comillas o tras guion largo
            dialogues = re.findall(r'(["«][^"»]+["»]|—[^—\n]+—?)', text)
            html = "<br><br>".join([f"<p style='color: #2ecc71; font-weight: bold;'>{d}</p>" for d in dialogues])
            self.txt_preview.setHtml(html if html else "<i>No se encontraron diálogos explícitos.</i>")
        elif idx == 2:  # Narración
            # Atenuar diálogos
            clean_text = re.sub(r'(["«][^"»]+["»]|—[^—\n]+—?)', "<span style='color: #555566;'>[Diálogo]</span>", text)
            self.txt_preview.setHtml(f"<div style='color: #e1e1e6;'>{clean_text.replace(chr(10), '<br>')}</div>")
        elif idx == 3:  # Adverbios en -mente
            highlighted = re.sub(r'(\b\w+mente\b)', r"<span style='color: #e74c3c; background-color: rgba(231,76,60,0.2); font-weight: bold;'>\1</span>", text, flags=re.IGNORECASE)
            self.txt_preview.setHtml(highlighted.replace("\n", "<br>"))
        elif idx == 4:  # Conectores
            connectors = r'\b(sin embargo|no obstante|por lo tanto|además|por consiguiente|en cambio|asimismo)\b'
            highlighted = re.sub(connectors, r"<span style='color: #3498db; background-color: rgba(52,152,219,0.2); font-weight: bold;'>\1</span>", text, flags=re.IGNORECASE)
            self.txt_preview.setHtml(highlighted.replace("\n", "<br>"))
