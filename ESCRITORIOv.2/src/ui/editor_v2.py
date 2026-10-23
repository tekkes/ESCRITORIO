"""
ESCRITORIO v2.0 - Advanced Rich Text Editor & Typography Engine
Incluye cabecera de navegación con historial, barra de formato enriquecida, regla tipográfica,
pie de página interactivo con zoom y recuentos, modo Vista de Página (Page View),
Desplazamiento de Máquina de Escribir (Typewriter Scrolling) y sincronización tipográfica.
"""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
    QToolButton, QSlider, QFrame, QToolBar, QFontComboBox,
    QComboBox, QButtonGroup, QColorDialog
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

        # Fondo sutil de la regla dependiente del tema
        bg_col = self.palette().window().color()
        painter.fillRect(self.rect(), bg_col)

        pen_border = QPen(self.palette().mid().color(), 1)
        painter.setPen(pen_border)
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

        # Marcas de centímetros / tabulaciones
        pen_tick = QPen(self.palette().text().color(), 1)
        pen_tick.setColor(QColor(140, 140, 150, 160))
        painter.setPen(pen_tick)
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
        self.header_bar.setObjectName("EditorHeaderBar")
        self.header_bar.setFixedHeight(38)
        h_layout = QHBoxLayout(self.header_bar)
        h_layout.setContentsMargins(8, 2, 8, 2)
        h_layout.setSpacing(8)

        self.btn_back = QToolButton(self.header_bar)
        self.btn_back.setProperty("class", "EditorActionBtn")
        self.btn_back.setFixedSize(28, 28)
        self.btn_back.setText("◀")
        self.btn_back.setToolTip("Documento Anterior (Alt+Izquierda)")
        self.btn_back.clicked.connect(self._go_back)
        h_layout.addWidget(self.btn_back)

        self.btn_fwd = QToolButton(self.header_bar)
        self.btn_fwd.setProperty("class", "EditorActionBtn")
        self.btn_fwd.setFixedSize(28, 28)
        self.btn_fwd.setText("▶")
        self.btn_fwd.setToolTip("Documento Siguiente (Alt+Derecha)")
        self.btn_fwd.clicked.connect(self._go_forward)
        h_layout.addWidget(self.btn_fwd)

        self.lbl_title = QLabel("Sin Selección", self.header_bar)
        self.lbl_title.setStyleSheet("font-weight: 600; font-size: 13px;")
        h_layout.addWidget(self.lbl_title)

        h_layout.addStretch()

        self.btn_lock = QToolButton(self.header_bar)
        self.btn_lock.setProperty("class", "EditorActionBtn")
        self.btn_lock.setFixedSize(28, 28)
        self.btn_lock.setText("🔓")
        self.btn_lock.setToolTip("Bloquear Edición de Documento")
        self.btn_lock.setCheckable(True)
        self.btn_lock.toggled.connect(self._toggle_lock)
        h_layout.addWidget(self.btn_lock)

        self.btn_typewriter = QToolButton(self.header_bar)
        self.btn_typewriter.setProperty("class", "EditorActionBtn")
        self.btn_typewriter.setFixedHeight(28)
        self.btn_typewriter.setText("⌨️ Máquina")
        self.btn_typewriter.setToolTip("Desplazamiento de Máquina de Escribir (Typewriter Scroll)")
        self.btn_typewriter.setCheckable(True)
        self.btn_typewriter.toggled.connect(self._toggle_typewriter)
        h_layout.addWidget(self.btn_typewriter)

        self.btn_split = QToolButton(self.header_bar)
        self.btn_split.setProperty("class", "EditorActionBtn")
        self.btn_split.setFixedSize(28, 28)
        self.btn_split.setText("🔀")
        self.btn_split.setToolTip("Dividir Editor (Split View)")
        self.btn_split.clicked.connect(self.split_requested.emit)
        h_layout.addWidget(self.btn_split)

        layout.addWidget(self.header_bar)

        # 2. Barra de Herramientas de Formato Rápido
        self.format_bar = QToolBar(self)
        self.format_bar.setObjectName("EditorFormatBar")
        self.format_bar.setFixedHeight(38)
        self.format_bar.setMovable(False)
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
        self.footer_bar.setObjectName("EditorFooterBar")
        self.footer_bar.setFixedHeight(30)
        f_layout = QHBoxLayout(self.footer_bar)
        f_layout.setContentsMargins(12, 0, 12, 0)
        f_layout.setSpacing(10)

        self.lbl_stats = QLabel("0 palabras | 0 caracteres", self.footer_bar)
        f_layout.addWidget(self.lbl_stats)

        f_layout.addStretch()

        self.btn_page_view = QToolButton(self.footer_bar)
        self.btn_page_view.setProperty("class", "EditorActionBtn")
        self.btn_page_view.setText("📄 Vista Folio")
        self.btn_page_view.setCheckable(True)
        self.btn_page_view.setToolTip("Alternar modo simulación de folio físico con márgenes")
        self.btn_page_view.toggled.connect(self._toggle_page_view)
        f_layout.addWidget(self.btn_page_view)

        # Zoom Slider
        f_layout.addWidget(QLabel("Zoom:", self.footer_bar))
        self.slider_zoom = QSlider(Qt.Orientation.Horizontal, self.footer_bar)
        self.slider_zoom.setRange(80, 200)
        self.slider_zoom.setValue(100)
        self.slider_zoom.setFixedWidth(80)
        self.slider_zoom.valueChanged.connect(self._on_zoom_changed)
        f_layout.addWidget(self.slider_zoom)

        self.lbl_zoom = QLabel("100%", self.footer_bar)
        f_layout.addWidget(self.lbl_zoom)

        layout.addWidget(self.footer_bar)

    def _setup_format_actions(self):
        # Selector de Fuente Tipográfica
        self.combo_font = QFontComboBox(self.format_bar)
        self.combo_font.setFixedWidth(145)
        self.combo_font.setFixedHeight(28)
        self.combo_font.setCurrentFont(QFont("Georgia"))
        self.combo_font.currentFontChanged.connect(self._set_font_family)
        self.format_bar.addWidget(self.combo_font)

        # Selector de Tamaño de Fuente
        self.combo_size = QComboBox(self.format_bar)
        self.combo_size.setFixedWidth(54)
        self.combo_size.setFixedHeight(28)
        for s in [9, 10, 11, 12, 13, 14, 16, 18, 20, 24, 28, 32]:
            self.combo_size.addItem(str(s), s)
        self.combo_size.setCurrentText("11")
        self.combo_size.currentIndexChanged.connect(self._set_font_size)
        self.format_bar.addWidget(self.combo_size)

        self.format_bar.addSeparator()

        # Botones de Estilo de Carácter: B, I, U, S
        self.btn_bold = QToolButton(self.format_bar)
        self.btn_bold.setProperty("class", "FormatToolButton")
        self.btn_bold.setFixedSize(28, 28)
        self.btn_bold.setText("B")
        self.btn_bold.setStyleSheet("font-weight: 900; font-family: 'Times New Roman', serif; font-size: 13px;")
        self.btn_bold.setCheckable(True)
        self.btn_bold.setToolTip("Negrita (Ctrl+B)")
        self.btn_bold.clicked.connect(self._toggle_bold)
        self.format_bar.addWidget(self.btn_bold)

        self.btn_italic = QToolButton(self.format_bar)
        self.btn_italic.setProperty("class", "FormatToolButton")
        self.btn_italic.setFixedSize(28, 28)
        self.btn_italic.setText("I")
        self.btn_italic.setStyleSheet("font-style: italic; font-family: 'Times New Roman', serif; font-size: 13px; font-weight: bold;")
        self.btn_italic.setCheckable(True)
        self.btn_italic.setToolTip("Cursiva (Ctrl+I)")
        self.btn_italic.clicked.connect(self._toggle_italic)
        self.format_bar.addWidget(self.btn_italic)

        self.btn_under = QToolButton(self.format_bar)
        self.btn_under.setProperty("class", "FormatToolButton")
        self.btn_under.setFixedSize(28, 28)
        self.btn_under.setText("U")
        self.btn_under.setStyleSheet("text-decoration: underline; font-family: 'Times New Roman', serif; font-size: 13px; font-weight: bold;")
        self.btn_under.setCheckable(True)
        self.btn_under.setToolTip("Subrayado (Ctrl+U)")
        self.btn_under.clicked.connect(self._toggle_underline)
        self.format_bar.addWidget(self.btn_under)

        self.btn_strike = QToolButton(self.format_bar)
        self.btn_strike.setProperty("class", "FormatToolButton")
        self.btn_strike.setFixedSize(28, 28)
        self.btn_strike.setText("S")
        self.btn_strike.setStyleSheet("text-decoration: line-through; font-family: 'Times New Roman', serif; font-size: 13px; font-weight: bold;")
        self.btn_strike.setCheckable(True)
        self.btn_strike.setToolTip("Tachado")
        self.btn_strike.clicked.connect(self._toggle_strikethrough)
        self.format_bar.addWidget(self.btn_strike)

        self.format_bar.addSeparator()

        # Botones de Alineación de Párrafo
        self.align_group = QButtonGroup(self)
        self.btn_align_left = QToolButton(self.format_bar)
        self.btn_align_left.setProperty("class", "FormatToolButton")
        self.btn_align_left.setFixedSize(28, 28)
        self.btn_align_left.setText("⯇")
        self.btn_align_left.setToolTip("Alinear a la izquierda (Ctrl+L)")
        self.btn_align_left.setCheckable(True)
        self.btn_align_left.setChecked(True)
        self.align_group.addButton(self.btn_align_left, 0)
        self.format_bar.addWidget(self.btn_align_left)

        self.btn_align_center = QToolButton(self.format_bar)
        self.btn_align_center.setProperty("class", "FormatToolButton")
        self.btn_align_center.setFixedSize(28, 28)
        self.btn_align_center.setText("≡")
        self.btn_align_center.setToolTip("Centrar (Ctrl+E)")
        self.btn_align_center.setCheckable(True)
        self.align_group.addButton(self.btn_align_center, 1)
        self.format_bar.addWidget(self.btn_align_center)

        self.btn_align_right = QToolButton(self.format_bar)
        self.btn_align_right.setProperty("class", "FormatToolButton")
        self.btn_align_right.setFixedSize(28, 28)
        self.btn_align_right.setText("⯈")
        self.btn_align_right.setToolTip("Alinear a la derecha (Ctrl+R)")
        self.btn_align_right.setCheckable(True)
        self.align_group.addButton(self.btn_align_right, 2)
        self.format_bar.addWidget(self.btn_align_right)

        self.btn_align_justify = QToolButton(self.format_bar)
        self.btn_align_justify.setProperty("class", "FormatToolButton")
        self.btn_align_justify.setFixedSize(28, 28)
        self.btn_align_justify.setText("⬌")
        self.btn_align_justify.setToolTip("Justificar (Ctrl+J)")
        self.btn_align_justify.setCheckable(True)
        self.align_group.addButton(self.btn_align_justify, 3)
        self.format_bar.addWidget(self.btn_align_justify)

        self.align_group.idClicked.connect(self._on_alignment_clicked)

        self.format_bar.addSeparator()

        # Selector de Interlineado
        self.combo_spacing = QComboBox(self.format_bar)
        self.combo_spacing.setFixedWidth(68)
        self.combo_spacing.setFixedHeight(28)
        self.combo_spacing.addItem("1.0x", 1.0)
        self.combo_spacing.addItem("1.15x", 1.15)
        self.combo_spacing.addItem("1.25x", 1.25)
        self.combo_spacing.addItem("1.5x", 1.5)
        self.combo_spacing.addItem("2.0x", 2.0)
        self.combo_spacing.setToolTip("Interlineado de párrafo")
        self.combo_spacing.currentIndexChanged.connect(self._on_line_spacing_changed)
        self.format_bar.addWidget(self.combo_spacing)

        self.format_bar.addSeparator()

        # Colores: Texto y Resaltador
        self.btn_color = QToolButton(self.format_bar)
        self.btn_color.setProperty("class", "FormatToolButton")
        self.btn_color.setFixedSize(28, 28)
        self.btn_color.setText("🎨")
        self.btn_color.setToolTip("Color del texto")
        self.btn_color.clicked.connect(self._pick_text_color)
        self.format_bar.addWidget(self.btn_color)

        self.btn_highlight = QToolButton(self.format_bar)
        self.btn_highlight.setProperty("class", "FormatToolButton")
        self.btn_highlight.setFixedSize(28, 28)
        self.btn_highlight.setText("🖍️")
        self.btn_highlight.setToolTip("Color de resaltado")
        self.btn_highlight.clicked.connect(self._pick_highlight_color)
        self.format_bar.addWidget(self.btn_highlight)

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
        self.current_node._content_rtf = self.editor.toPlainText()
        self.current_node.mark_dirty()
        self._update_stats()
        self.text_modified.emit()

    def _on_cursor_position_changed(self):
        if self.typewriter_enabled:
            cursor = self.editor.textCursor()
            rect = self.editor.cursorRect(cursor)
            scrollbar = self.editor.verticalScrollBar()
            viewport_height = self.editor.viewport().height()
            target_pos = scrollbar.value() + rect.top() - (viewport_height // 2)
            scrollbar.setValue(target_pos)

        # Sincronizar estado de los botones de formato con la posición actual del cursor
        fmt = self.editor.currentCharFormat()
        self.btn_bold.blockSignals(True)
        self.btn_bold.setChecked(fmt.fontWeight() >= QFont.Weight.Bold)
        self.btn_bold.blockSignals(False)

        self.btn_italic.blockSignals(True)
        self.btn_italic.setChecked(fmt.fontItalic())
        self.btn_italic.blockSignals(False)

        self.btn_under.blockSignals(True)
        self.btn_under.setChecked(fmt.fontUnderline())
        self.btn_under.blockSignals(False)

        self.btn_strike.blockSignals(True)
        self.btn_strike.setChecked(fmt.fontStrikeOut())
        self.btn_strike.blockSignals(False)

        # Sincronizar alineación
        align = self.editor.alignment()
        self.align_group.blockSignals(True)
        if align & Qt.AlignmentFlag.AlignHCenter:
            self.btn_align_center.setChecked(True)
        elif align & Qt.AlignmentFlag.AlignRight:
            self.btn_align_right.setChecked(True)
        elif align & Qt.AlignmentFlag.AlignJustify:
            self.btn_align_justify.setChecked(True)
        else:
            self.btn_align_left.setChecked(True)
        self.align_group.blockSignals(False)

    def _update_stats(self):
        text = self.editor.toPlainText()
        words = len(text.split()) if text else 0
        chars = len(text)
        self.lbl_stats.setText(f"{words:,} palabras | {chars:,} caracteres")

    def _toggle_lock(self, checked: bool):
        self.is_locked = checked
        self.editor.setReadOnly(checked)
        self.btn_lock.setText("🔒" if checked else "🔓")

    def _toggle_typewriter(self, checked: bool):
        self.typewriter_enabled = checked

    def _toggle_page_view(self, checked: bool):
        self.page_view_enabled = checked
        if checked:
            self.editor.setStyleSheet("""
                QTextEdit {
                    padding: 30px 60px;
                    margin: 10px 40px;
                    border: 1px solid rgba(0, 0, 0, 0.2);
                    border-radius: 4px;
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

    # Métodos de Formato de Texto
    def _set_font_family(self, font: QFont):
        fmt = QTextCharFormat()
        fmt.setFontFamily(font.family())
        self.editor.mergeCurrentCharFormat(fmt)

    def _set_font_size(self):
        try:
            sz = int(self.combo_size.currentText())
            fmt = QTextCharFormat()
            fmt.setFontPointSize(sz)
            self.editor.mergeCurrentCharFormat(fmt)
        except ValueError:
            pass

    def _toggle_bold(self):
        fmt = QTextCharFormat()
        new_weight = QFont.Weight.Normal if self.btn_bold.isChecked() is False else QFont.Weight.Bold
        fmt.setFontWeight(new_weight)
        self.editor.mergeCurrentCharFormat(fmt)

    def _toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.btn_italic.isChecked())
        self.editor.mergeCurrentCharFormat(fmt)

    def _toggle_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.btn_under.isChecked())
        self.editor.mergeCurrentCharFormat(fmt)

    def _toggle_strikethrough(self):
        fmt = QTextCharFormat()
        fmt.setFontStrikeOut(self.btn_strike.isChecked())
        self.editor.mergeCurrentCharFormat(fmt)

    def _on_alignment_clicked(self, id: int):
        if id == 0:
            self.editor.setAlignment(Qt.AlignmentFlag.AlignLeft)
        elif id == 1:
            self.editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        elif id == 2:
            self.editor.setAlignment(Qt.AlignmentFlag.AlignRight)
        elif id == 3:
            self.editor.setAlignment(Qt.AlignmentFlag.AlignJustify)

    def _on_line_spacing_changed(self):
        mult = self.combo_spacing.currentData()
        if mult:
            block_fmt = QTextBlockFormat()
            block_fmt.setLineHeight(int(mult * 100), 1)  # ProportionalHeight
            cursor = self.editor.textCursor()
            cursor.setBlockFormat(block_fmt)

    def _pick_text_color(self):
        col = QColorDialog.getColor(Qt.GlobalColor.white, self, "Seleccionar color de texto")
        if col.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(col)
            self.editor.mergeCurrentCharFormat(fmt)

    def _pick_highlight_color(self):
        col = QColorDialog.getColor(QColor("#f1c40f"), self, "Seleccionar color de resaltado")
        if col.isValid():
            fmt = QTextCharFormat()
            fmt.setBackground(col)
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
