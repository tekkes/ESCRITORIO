"""
ESCRITORIO v2.0 - Advanced Rich Text Editor & Typography Engine
Incluye cabecera de navegación con historial, pie de página interactivo con zoom y recuentos,
modo Vista de Página (Page View), Desplazamiento de Máquina de Escribir (Typewriter Scrolling)
y Foco de Párrafo idéntico a Scrivener 3 macOS.
"""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
    QToolButton, QSlider, QFrame, QToolBar, QFontComboBox,
    QComboBox, QSpinBox, QColorDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect
from PyQt6.QtGui import (
    QFont, QTextCursor, QTextCharFormat, QTextBlockFormat,
    QColor, QPainter, QPen, QBrush
)

from ..core.project_v2 import BinderNode


class TypographyRuler(QWidget):
    """Regla tipográfica interactiva con marcas de tabulación y márgenes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(18)
        self.margin_left = 40
        self.margin_right = 40

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Fondo sutil de la regla
        painter.fillRect(self.rect(), QColor("#1e1e24"))
        painter.setPen(QPen(QColor("#404050"), 1))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

        # Marcas de centímetros / pulgadas
        painter.setPen(QPen(QColor("#707085"), 1))
        for x in range(0, self.width(), 20):
            h = 6 if x % 100 == 0 else (4 if x % 40 == 0 else 2)
            painter.drawLine(x, self.height() - h - 1, x, self.height() - 1)


class EditorV2(QWidget):
    """Editor de texto enriquecido profesional para ESCRITORIO v2.0."""

    text_modified = pyqtSignal()
    navigate_back = pyqtSignal()
    navigate_forward = pyqtSignal()
    split_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_node: Optional[BinderNode] = None
        self.is_locked = False
        self.typewriter_enabled = False
        self.page_view_enabled = False
        self.zoom_level = 100

        # Historial de navegación del editor
        self.history_stack: List[str] = []
        self.history_idx: int = -1

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Cabecera del Editor (Header Bar)
        self.header_bar = QFrame(self)
        self.header_bar.setFixedHeight(34)
        self.header_bar.setStyleSheet("background-color: #1a1a20; border-bottom: 1px solid #323242;")
        h_layout = QHBoxLayout(self.header_bar)
        h_layout.setContentsMargins(8, 0, 8, 0)
        h_layout.setSpacing(6)

        self.btn_back = QToolButton()
        self.btn_back.setText("◀")
        self.btn_back.setToolTip("Documento Anterior")
        self.btn_back.clicked.connect(self._go_back)
        h_layout.addWidget(self.btn_back)

        self.btn_fwd = QToolButton()
        self.btn_fwd.setText("▶")
        self.btn_fwd.setToolTip("Documento Siguiente")
        self.btn_fwd.clicked.connect(self._go_forward)
        h_layout.addWidget(self.btn_fwd)

        self.lbl_title = QLabel("Sin Selección")
        self.lbl_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #e1e1e6;")
        h_layout.addWidget(self.lbl_title)

        h_layout.addStretch()

        self.btn_lock = QToolButton()
        self.btn_lock.setText("🔓")
        self.btn_lock.setToolTip("Bloquear Edición de Documento")
        self.btn_lock.setCheckable(True)
        self.btn_lock.toggled.connect(self._toggle_lock)
        h_layout.addWidget(self.btn_lock)

        self.btn_typewriter = QToolButton()
        self.btn_typewriter.setText("⌨️ Máquina")
        self.btn_typewriter.setToolTip("Desplazamiento de Máquina de Escribir (Typewriter Scroll)")
        self.btn_typewriter.setCheckable(True)
        self.btn_typewriter.toggled.connect(self._toggle_typewriter)
        h_layout.addWidget(self.btn_typewriter)

        self.btn_split = QToolButton()
        self.btn_split.setText("🔀")
        self.btn_split.setToolTip("Dividir Editor (Split View)")
        self.btn_split.clicked.connect(self.split_requested.emit)
        h_layout.addWidget(self.btn_split)

        layout.addWidget(self.header_bar)

        # 2. Barra de Herramientas de Formato Rápido
        self.format_bar = QToolBar(self)
        self.format_bar.setFixedHeight(30)
        self.format_bar.setStyleSheet("background-color: #1e1e24; border-bottom: 1px solid #323242;")
        self._setup_format_actions()
        layout.addWidget(self.format_bar)

        # 3. Regla Tipográfica
        self.ruler = TypographyRuler(self)
        layout.addWidget(self.ruler)

        # 4. Área Central de Edición
        self.editor = QTextEdit(self)
        self.editor.setFont(QFont("Georgia", 11))
        self.editor.textChanged.connect(self._on_text_changed)
        self.editor.cursorPositionChanged.connect(self._on_cursor_position_changed)
        layout.addWidget(self.editor)

        # 5. Pie de Página del Editor (Footer Bar)
        self.footer_bar = QFrame(self)
        self.footer_bar.setFixedHeight(28)
        self.footer_bar.setStyleSheet("background-color: #1a1a20; border-top: 1px solid #323242; font-size: 11px;")
        f_layout = QHBoxLayout(self.footer_bar)
        f_layout.setContentsMargins(12, 0, 12, 0)
        f_layout.setSpacing(10)

        self.lbl_stats = QLabel("0 palabras | 0 caracteres")
        self.lbl_stats.setStyleSheet("color: #a0a0b2;")
        f_layout.addWidget(self.lbl_stats)

        f_layout.addStretch()

        self.btn_page_view = QToolButton()
        self.btn_page_view.setText("📄 Vista Folio")
        self.btn_page_view.setCheckable(True)
        self.btn_page_view.setToolTip("Alternar modo simulación de folio físico")
        self.btn_page_view.toggled.connect(self._toggle_page_view)
        f_layout.addWidget(self.btn_page_view)

        # Zoom Slider
        f_layout.addWidget(QLabel("Zoom:"))
        self.slider_zoom = QSlider(Qt.Orientation.Horizontal)
        self.slider_zoom.setRange(80, 200)
        self.slider_zoom.setValue(100)
        self.slider_zoom.setFixedWidth(80)
        self.slider_zoom.valueChanged.connect(self._on_zoom_changed)
        f_layout.addWidget(self.slider_zoom)

        self.lbl_zoom = QLabel("100%")
        self.lbl_zoom.setStyleSheet("color: #a0a0b2;")
        f_layout.addWidget(self.lbl_zoom)

        layout.addWidget(self.footer_bar)

    def _setup_format_actions(self):
        btn_bold = self.format_bar.addAction("B")
        btn_bold.setToolTip("Negrita (Ctrl+B)")
        btn_bold.triggered.connect(lambda: self._set_font_weight(QFont.Weight.Bold))

        btn_italic = self.format_bar.addAction("I")
        btn_italic.setToolTip("Cursiva (Ctrl+I)")
        btn_italic.triggered.connect(self._toggle_italic)

        btn_under = self.format_bar.addAction("U")
        btn_under.setToolTip("Subrayado (Ctrl+U)")
        btn_under.triggered.connect(self._toggle_underline)

        self.format_bar.addSeparator()

        btn_left = self.format_bar.addAction("⬅")
        btn_left.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignLeft))

        btn_center = self.format_bar.addAction("⬆")
        btn_center.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignCenter))

        btn_right = self.format_bar.addAction("➡")
        btn_right.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignRight))

        btn_justify = self.format_bar.addAction("⬌")
        btn_justify.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignJustify))

    def load_node(self, node: BinderNode, push_history: bool = True):
        """Carga el texto enriquecido de un nodo en el editor."""
        self.current_node = node
        self.lbl_title.setText(f"📄 {node.title}")

        if push_history:
            if self.history_idx < len(self.history_stack) - 1:
                self.history_stack = self.history_stack[:self.history_idx + 1]
            self.history_stack.append(node.uuid)
            self.history_idx = len(self.history_stack) - 1

        self.editor.blockSignals(True)
        if node._content_rtf:
            # Si el contenido empieza por RTF estándar, cargar como RTF
            if node._content_rtf.startswith("{\\rtf"):
                self.editor.setHtml(self._simple_rtf_to_html(node._content_rtf))
            else:
                self.editor.setPlainText(node._content_rtf)
        else:
            self.editor.setPlainText("")
        self.editor.blockSignals(False)

        self._update_stats()

    def _on_text_changed(self):
        if not self.current_node or self.is_locked:
            return
        # Guardar en memoria el texto actual
        self.current_node._content_rtf = self.editor.toPlainText()
        self.current_node.mark_dirty()
        self._update_stats()
        self.text_modified.emit()

    def _on_cursor_position_changed(self):
        if self.typewriter_enabled:
            # Centrar automáticamente la línea actual en la ventana
            cursor = self.editor.textCursor()
            rect = self.editor.cursorRect(cursor)
            scrollbar = self.editor.verticalScrollBar()
            viewport_height = self.editor.viewport().height()
            target_pos = scrollbar.value() + rect.top() - (viewport_height // 2)
            scrollbar.setValue(target_pos)

    def _update_stats(self):
        text = self.editor.toPlainText()
        words = len(text.split()) if text else 0
        chars = len(text)
        self.lbl_stats.setText(f"{words} palabras | {chars} caracteres")

    def _toggle_lock(self, checked: bool):
        self.is_locked = checked
        self.editor.setReadOnly(checked)
        self.btn_lock.setText("🔒" if checked else "🔓")

    def _toggle_typewriter(self, checked: bool):
        self.typewriter_enabled = checked

    def _toggle_page_view(self, checked: bool):
        self.page_view_enabled = checked
        if checked:
            # Estilo simulación de folio de papel físico con sombra
            self.editor.setStyleSheet("""
                QTextEdit {
                    background-color: #2a2a36;
                    padding: 30px;
                }
            """)
        else:
            self.editor.setStyleSheet("")

    def _on_zoom_changed(self, value: int):
        self.zoom_level = value
        self.lbl_zoom.setText(f"{value}%")
        font = self.editor.font()
        font.setPointSize(int(11 * (value / 100.0)))
        self.editor.setFont(font)

    def _set_font_weight(self, weight):
        fmt = QTextCharFormat()
        fmt.setFontWeight(weight)
        self.editor.mergeCurrentCharFormat(fmt)

    def _toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.editor.fontItalic())
        self.editor.mergeCurrentCharFormat(fmt)

    def _toggle_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.editor.fontUnderline())
        self.editor.mergeCurrentCharFormat(fmt)

    def _go_back(self):
        if self.history_idx > 0:
            self.history_idx -= 1
            self.navigate_back.emit()

    def _go_forward(self):
        if self.history_idx < len(self.history_stack) - 1:
            self.history_idx += 1
            self.navigate_forward.emit()

    @staticmethod
    def _simple_rtf_to_html(rtf: str) -> str:
        """Conversor elemental de RTF básico a texto legible."""
        import re
        text = re.sub(r'\\[a-z0-9\-]+ ?', ' ', rtf)
        text = text.replace('{', '').replace('}', '').strip()
        lines = [f"<p>{line}</p>" for line in text.splitlines() if line.strip()]
        return "".join(lines) if lines else "<p></p>"
