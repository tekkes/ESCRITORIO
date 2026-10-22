#include "EditorWidget.hpp"
#include <sstream>
#include <algorithm>
#include <cwctype>

namespace escritorio::ui {

EditorWidget::EditorWidget() {
    InitDefaultStyles();
}

void EditorWidget::InitDefaultStyles() {
    m_styles.clear();

    // 1. Sin Estilo (No Style)
    StyleItem noStyle;
    noStyle.id = L"style-no-style";
    noStyle.name = L"Sin Estilo";
    noStyle.type = StyleType::None;
    noStyle.shortcut = L"Ctrl+0";
    noStyle.isBuiltin = true;
    noStyle.isDefault = true;
    m_styles.push_back(noStyle);

    // 2. Título 1
    StyleItem h1;
    h1.id = L"style-heading-1";
    h1.name = L"Título 1";
    h1.type = StyleType::Paragraph;
    h1.shortcut = L"Ctrl+Alt+1";
    h1.fontSize = 18.0f;
    h1.bold = true;
    h1.spaceBefore = 14.0f;
    h1.spaceAfter = 6.0f;
    m_styles.push_back(h1);

    // 3. Título 2
    StyleItem h2;
    h2.id = L"style-heading-2";
    h2.name = L"Título 2";
    h2.type = StyleType::Paragraph;
    h2.shortcut = L"Ctrl+Alt+2";
    h2.fontSize = 14.0f;
    h2.bold = true;
    h2.spaceBefore = 10.0f;
    h2.spaceAfter = 4.0f;
    m_styles.push_back(h2);

    // 4. Cita en bloque
    StyleItem quote;
    quote.id = L"style-block-quote";
    quote.name = L"Cita en bloque";
    quote.type = StyleType::Combined;
    quote.shortcut = L"Ctrl+Alt+Q";
    quote.italic = true;
    quote.leftIndent = 36.0f;
    quote.rightIndent = 36.0f;
    quote.spaceBefore = 6.0f;
    quote.spaceAfter = 6.0f;
    m_styles.push_back(quote);

    // 5. Epígrafe
    StyleItem epigraph;
    epigraph.id = L"style-epigraph";
    epigraph.name = L"Epígrafe";
    epigraph.type = StyleType::Combined;
    epigraph.shortcut = L"Ctrl+Alt+E";
    epigraph.italic = true;
    epigraph.alignment = 2; // right
    epigraph.spaceAfter = 12.0f;
    m_styles.push_back(epigraph);

    // 6. Código
    StyleItem code;
    code.id = L"style-code";
    code.name = L"Código";
    code.type = StyleType::Character;
    code.shortcut = L"Ctrl+Alt+C";
    code.fontFamily = L"Consolas";
    code.fontSize = 10.0f;
    code.bgColor = RGB(242, 242, 242);
    m_styles.push_back(code);

    // 7. Verso
    StyleItem verse;
    verse.id = L"style-verse";
    verse.name = L"Verso";
    verse.type = StyleType::Paragraph;
    verse.shortcut = L"Ctrl+Alt+V";
    verse.italic = true;
    verse.leftIndent = 24.0f;
    verse.lineSpacing = 1.0f;
    m_styles.push_back(verse);
}

void EditorWidget::SetPlainText(const std::wstring& text) {
    m_plainText = text;
    // Estimar páginas (aprox 1800 caracteres por página estándar)
    m_totalPages = (std::max)(1, (static_cast<int>(m_plainText.length()) + 1799) / 1800);
    m_currentPage = 1;
}

void EditorWidget::SetItemUuid(const std::wstring& uuid, const std::wstring& title) {
    m_itemUuid = uuid;
    m_itemTitle = title;
}

size_t EditorWidget::GetWordCount() const {
    size_t count = 0;
    bool inWord = false;
    for (wchar_t c : m_plainText) {
        if (std::iswspace(c) || std::iswpunct(c)) {
            if (inWord) {
                count++;
                inWord = false;
            }
        } else {
            inWord = true;
        }
    }
    if (inWord) count++;
    return count;
}

size_t EditorWidget::GetCharacterCount() const {
    return m_plainText.length();
}

EditorViewMode EditorWidget::TogglePageView() {
    if (m_viewMode == EditorViewMode::Continuous) {
        m_viewMode = EditorViewMode::PageView;
    } else {
        m_viewMode = EditorViewMode::Continuous;
    }
    return m_viewMode;
}

bool EditorWidget::ApplyStyle(const std::wstring& styleId) {
    for (const auto& s : m_styles) {
        if (s.id == styleId) {
            m_activeStyleId = styleId;
            if (s.type != StyleType::None) {
                m_fontSize = s.fontSize;
                m_bold = s.bold;
                m_italic = s.italic;
                m_fontFamily = s.fontFamily;
                m_alignment = s.alignment;
                m_firstLineIndent = s.firstLineIndent;
                m_leftIndent = s.leftIndent;
                m_rightIndent = s.rightIndent;
            }
            return true;
        }
    }
    return false;
}

bool EditorWidget::CreateStyleFromSelection(const std::wstring& name, StyleType type) {
    StyleItem s;
    s.id = L"style-custom-" + std::to_wstring(m_styles.size() + 1);
    s.name = name;
    s.type = type;
    s.isBuiltin = false;
    s.isDefault = false;
    s.fontSize = m_fontSize;
    s.bold = m_bold;
    s.italic = m_italic;
    s.fontFamily = m_fontFamily;
    s.alignment = m_alignment;
    s.firstLineIndent = m_firstLineIndent;
    s.leftIndent = m_leftIndent;
    s.rightIndent = m_rightIndent;
    m_styles.push_back(s);
    m_activeStyleId = s.id;
    return true;
}

bool EditorWidget::RedefineStyleFromSelection(const std::wstring& styleId) {
    for (auto& s : m_styles) {
        if (s.id == styleId && s.type != StyleType::None) {
            s.fontSize = m_fontSize;
            s.bold = m_bold;
            s.italic = m_italic;
            s.fontFamily = m_fontFamily;
            s.alignment = m_alignment;
            s.firstLineIndent = m_firstLineIndent;
            s.leftIndent = m_leftIndent;
            s.rightIndent = m_rightIndent;
            return true;
        }
    }
    return false;
}

void EditorWidget::ToggleBold() { m_bold = !m_bold; }
void EditorWidget::ToggleItalic() { m_italic = !m_italic; }
void EditorWidget::ToggleUnderline() { m_underline = !m_underline; }
void EditorWidget::SetAlignment(int align) { if (align >= 0 && align <= 3) m_alignment = align; }
void EditorWidget::SetLineSpacing(float spacing) { m_lineSpacing = spacing; }
void EditorWidget::SetHighlightColor(COLORREF color) { m_highlightColor = color; }

void EditorWidget::InsertTable(int rows, int cols) {
    m_plainText += L"\n[Tabla " + std::to_wstring(rows) + L"x" + std::to_wstring(cols) + L"]\n";
}

void EditorWidget::InsertBulletList() {
    m_plainText += L"\n• ";
}

void EditorWidget::InsertNumberedList() {
    m_plainText += L"\n1. ";
}

void EditorWidget::InsertImage(const std::wstring& path) {
    m_plainText += L"\n[Imagen: " + path + L"]\n";
}

void EditorWidget::InsertScrivenerLink(const std::wstring& targetUuid, const std::wstring& display) {
    m_plainText += L"[" + display + L"](scrivener-link://" + targetUuid + L")";
}

std::vector<HighlightSpanNative> EditorWidget::AnalyzeLinguisticFocus() const {
    std::vector<HighlightSpanNative> spans;
    if (m_linguisticCategory == LinguisticCategory::None || m_plainText.empty()) {
        return spans;
    }

    if (m_linguisticCategory == LinguisticCategory::Dialogues) {
        // Buscar comillas o rayas
        bool inDialogue = false;
        size_t start = 0;
        for (size_t i = 0; i < m_plainText.length(); ++i) {
            wchar_t c = m_plainText[i];
            if (c == L'\x00AB' || c == L'"' || c == L'\x201C' || c == L'\x2014') {
                if (!inDialogue) {
                    inDialogue = true;
                    start = i;
                } else if (c == L'\x00BB' || c == L'"' || c == L'\x201D' || c == L'\x2014') {
                    inDialogue = false;
                    spans.push_back({start, i + 1, LinguisticCategory::Dialogues});
                }
            } else if (c == L'\n' && inDialogue) {
                inDialogue = false;
                spans.push_back({start, i, LinguisticCategory::Dialogues});
            }
        }
    } else if (m_linguisticCategory == LinguisticCategory::Adverbs) {
        // Palabras terminadas en mente o ly
        size_t wordStart = 0;
        bool inWord = false;
        for (size_t i = 0; i <= m_plainText.length(); ++i) {
            bool isEnd = (i == m_plainText.length()) || std::iswspace(m_plainText[i]) || std::iswpunct(m_plainText[i]);
            if (!inWord && !isEnd) {
                inWord = true;
                wordStart = i;
            } else if (inWord && isEnd) {
                inWord = false;
                std::wstring word = m_plainText.substr(wordStart, i - wordStart);
                std::transform(word.begin(), word.end(), word.begin(), ::towlower);
                if ((word.length() > 6 && word.rfind(L"mente") == word.length() - 5) ||
                    (word.length() > 3 && word.rfind(L"ly") == word.length() - 2) ||
                    word == L"muy" || word == L"casi" || word == L"siempre" || word == L"nunca") {
                    spans.push_back({wordStart, i, LinguisticCategory::Adverbs});
                }
            }
        }
    } else if (m_linguisticCategory == LinguisticCategory::Adjectives) {
        // Adjetivos comunes y sufijos descriptivos
        size_t wordStart = 0;
        bool inWord = false;
        for (size_t i = 0; i <= m_plainText.length(); ++i) {
            bool isEnd = (i == m_plainText.length()) || std::iswspace(m_plainText[i]) || std::iswpunct(m_plainText[i]);
            if (!inWord && !isEnd) {
                inWord = true;
                wordStart = i;
            } else if (inWord && isEnd) {
                inWord = false;
                std::wstring word = m_plainText.substr(wordStart, i - wordStart);
                std::transform(word.begin(), word.end(), word.begin(), ::towlower);
                if (word == L"bueno" || word == L"buena" || word == L"malo" || word == L"mala" ||
                    word == L"grande" || word == L"pequeño" || word == L"pequeña" || word == L"alto" ||
                    word == L"alta" || word == L"bajo" || word == L"baja" || word == L"nuevo" ||
                    word == L"nueva" || word == L"viejo" || word == L"vieja" || word == L"hermoso" ||
                    word == L"hermosa" || word == L"bello" || word == L"bella" || word == L"oscuro" ||
                    word == L"oscura" || word == L"claro" || word == L"clara" || word == L"brillante" ||
                    (word.length() > 5 && (word.rfind(L"oso") == word.length() - 3 || word.rfind(L"osa") == word.length() - 3 ||
                                           word.rfind(L"ible") == word.length() - 4 || word.rfind(L"able") == word.length() - 4 ||
                                           word.rfind(L"ante") == word.length() - 4 || word.rfind(L"ente") == word.length() - 4))) {
                    spans.push_back({wordStart, i, LinguisticCategory::Adjectives});
                }
            }
        }
    } else if (m_linguisticCategory == LinguisticCategory::Verbs) {
        // Formas verbales comunes y desinencias
        size_t wordStart = 0;
        bool inWord = false;
        for (size_t i = 0; i <= m_plainText.length(); ++i) {
            bool isEnd = (i == m_plainText.length()) || std::iswspace(m_plainText[i]) || std::iswpunct(m_plainText[i]);
            if (!inWord && !isEnd) {
                inWord = true;
                wordStart = i;
            } else if (inWord && isEnd) {
                inWord = false;
                std::wstring word = m_plainText.substr(wordStart, i - wordStart);
                std::transform(word.begin(), word.end(), word.begin(), ::towlower);
                if (word == L"es" || word == L"son" || word == L"era" || word == L"eran" ||
                    word == L"fue" || word == L"fueron" || word == L"está" || word == L"están" ||
                    word == L"estaba" || word == L"estaban" || word == L"ha" || word == L"han" ||
                    word == L"había" || word == L"habían" || word == L"tiene" || word == L"tienen" ||
                    word == L"tenía" || word == L"tenían" || word == L"hace" || word == L"hacen" ||
                    word == L"hizo" || word == L"hicieron" || word == L"dice" || word == L"dicen" ||
                    word == L"dijo" || word == L"dijeron" || word == L"va" || word == L"van" ||
                    word == L"ve" || word == L"ven" || word == L"vio" || word == L"vieron" ||
                    (word.length() > 4 && (word.rfind(L"ando") == word.length() - 4 || word.rfind(L"iendo") == word.length() - 5 ||
                                           word.rfind(L"aron") == word.length() - 4 || word.rfind(L"ieron") == word.length() - 5))) {
                    spans.push_back({wordStart, i, LinguisticCategory::Verbs});
                }
            }
        }
    } else if (m_linguisticCategory == LinguisticCategory::Conjunctions) {
        // Conjunciones en español e inglés
        size_t wordStart = 0;
        bool inWord = false;
        for (size_t i = 0; i <= m_plainText.length(); ++i) {
            bool isEnd = (i == m_plainText.length()) || std::iswspace(m_plainText[i]) || std::iswpunct(m_plainText[i]);
            if (!inWord && !isEnd) {
                inWord = true;
                wordStart = i;
            } else if (inWord && isEnd) {
                inWord = false;
                std::wstring word = m_plainText.substr(wordStart, i - wordStart);
                std::transform(word.begin(), word.end(), word.begin(), ::towlower);
                if (word == L"y" || word == L"e" || word == L"ni" || word == L"que" ||
                    word == L"o" || word == L"u" || word == L"pero" || word == L"mas" ||
                    word == L"sino" || word == L"porque" || word == L"pues" || word == L"como" ||
                    word == L"si" || word == L"aunque" || word == L"mientras" || word == L"luego" ||
                    word == L"and" || word == L"but" || word == L"or" || word == L"nor" ||
                    word == L"for" || word == L"yet" || word == L"so" || word == L"because") {
                    spans.push_back({wordStart, i, LinguisticCategory::Conjunctions});
                }
            }
        }
    }
    return spans;
}

std::pair<size_t, size_t> EditorWidget::GetFocusedSpan() const {
    if (m_focusScope == FocusScope::Off || m_plainText.empty()) {
        return {0, m_plainText.length()};
    }

    size_t pos = (std::min)(m_cursorPos, m_plainText.length());

    if (m_focusScope == FocusScope::Line) {
        size_t start = m_plainText.rfind(L'\n', pos);
        start = (start == std::wstring::npos) ? 0 : start + 1;
        size_t end = m_plainText.find(L'\n', pos);
        end = (end == std::wstring::npos) ? m_plainText.length() : end;
        return {start, end};
    } else if (m_focusScope == FocusScope::Sentence) {
        size_t start = m_plainText.find_last_of(L".!?", pos);
        start = (start == std::wstring::npos) ? 0 : start + 1;
        size_t end = m_plainText.find_first_of(L".!?", pos);
        end = (end == std::wstring::npos) ? m_plainText.length() : end + 1;
        return {start, end};
    } else if (m_focusScope == FocusScope::Paragraph) {
        size_t start = m_plainText.rfind(L"\n\n", pos);
        start = (start == std::wstring::npos) ? 0 : start + 2;
        size_t end = m_plainText.find(L"\n\n", pos);
        end = (end == std::wstring::npos) ? m_plainText.length() : end;
        return {start, end};
    }

    return {0, m_plainText.length()};
}

void EditorWidget::Render(HDC hdc, const RECT& bounds, const escritorio::themes::ThemePalette& pal,
                          const escritorio::themes::UIDensityMetrics& metrics) {
    int w = bounds.right - bounds.left;
    int h = bounds.bottom - bounds.top;
    if (w <= 0 || h <= 0) return;

    // Buffer GDI para parpadeo cero
    HDC memDC = CreateCompatibleDC(hdc);
    HBITMAP memBM = CreateCompatibleBitmap(hdc, w, h);
    HBITMAP oldBM = (HBITMAP)SelectObject(memDC, memBM);

    // 1. Fondo del editor
    HBRUSH bgBrush = CreateSolidBrush(pal.editorBg);
    RECT clientRect = {0, 0, w, h};
    FillRect(memDC, &clientRect, bgBrush);
    DeleteObject(bgBrush);

    // 2. Barra de formato superior compacta (FormatToolbar)
    int toolbarH = metrics.binderRowHeight + 6;
    RECT toolbarRect = {0, 0, w, toolbarH};
    HBRUSH tbBrush = CreateSolidBrush(pal.toolbarBg);
    FillRect(memDC, &toolbarRect, tbBrush);
    DeleteObject(tbBrush);

    // Borde inferior de la barra
    HPEN borderPen = CreatePen(PS_SOLID, 1, pal.toolbarBorder);
    HPEN oldPen = (HPEN)SelectObject(memDC, borderPen);
    MoveToEx(memDC, 0, toolbarH - 1, NULL);
    LineTo(memDC, w, toolbarH - 1);

    // Texto de la barra de formato: Estilo, Fuente, Tamaño, Botones
    SetBkMode(memDC, TRANSPARENT);
    SetTextColor(memDC, pal.toolbarFg);
    HFONT tbFont = CreateFontW(metrics.fontSizeUi, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
                              DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
                              CLEARTYPE_QUALITY, DEFAULT_PITCH | FF_DONTCARE, L"Segoe UI");
    HFONT oldFont = (HFONT)SelectObject(memDC, tbFont);

    std::wstring tbInfo = L"Estilo: [" + m_activeStyleId + L"]  |  " + m_fontFamily + L" " +
                          std::to_wstring((int)m_fontSize) + L"pt  |  " +
                          (m_bold ? L"[B] " : L"B ") +
                          (m_italic ? L"[I] " : L"I ") +
                          (m_underline ? L"[U] " : L"U ") +
                          L" |  Regla: " + (m_showRuler ? L"ON" : L"OFF") +
                          L" |  Modo: " + (m_viewMode == EditorViewMode::PageView ? L"Página" : L"Continuo") +
                          L" |  Foco: " + (m_focusScope != FocusScope::Off ? L"ACTIVO" : L"OFF") +
                          L" |  Invisibles: " + (m_showInvisibles ? L"ON" : L"OFF");
    RECT tbTextRect = {12, 4, w - 12, toolbarH};
    DrawTextW(memDC, tbInfo.c_str(), -1, &tbTextRect, DT_SINGLELINE | DT_VCENTER | DT_LEFT);

    // 3. Regla horizontal interactiva (si está visible)
    int rulerH = 0;
    if (m_showRuler) {
        rulerH = 18;
        RECT rulerRect = {0, toolbarH, w, toolbarH + rulerH};
        HBRUSH rulerBrush = CreateSolidBrush(RGB(240, 240, 242));
        FillRect(memDC, &rulerRect, rulerBrush);
        DeleteObject(rulerBrush);

        MoveToEx(memDC, 0, toolbarH + rulerH - 1, NULL);
        LineTo(memDC, w, toolbarH + rulerH - 1);

        // Marcas de regla cada 50 px
        for (int x = 50; x < w - 50; x += 50) {
            MoveToEx(memDC, x, toolbarH + rulerH - 6, NULL);
            LineTo(memDC, x, toolbarH + rulerH - 1);
        }
    }

    // 4. Área de contenido (Vista Continua o Vista de Página)
    int contentTop = toolbarH + rulerH + 16;
    RECT pageRect = {0, 0, 0, 0};

    if (m_viewMode == EditorViewMode::PageView) {
        // Folio físico A4 centrado con sombra
        int pageWidth = (std::min)(w - 40, 680);
        int pageHeight = (std::max)(h - contentTop - 20, 800);
        int pageLeft = (w - pageWidth) / 2;
        pageRect = {pageLeft, contentTop, pageLeft + pageWidth, contentTop + pageHeight};

        // Sombra suave del folio
        RECT shadowRect = {pageRect.left + 3, pageRect.top + 3, pageRect.right + 3, pageRect.bottom + 3};
        HBRUSH shadowBrush = CreateSolidBrush(RGB(210, 212, 216));
        FillRect(memDC, &shadowRect, shadowBrush);
        DeleteObject(shadowBrush);

        // Folio físico blanco
        HBRUSH pageBrush = CreateSolidBrush(RGB(255, 255, 255));
        FillRect(memDC, &pageRect, pageBrush);
        DeleteObject(pageBrush);

        // Borde del folio
        HPEN pagePen = CreatePen(PS_SOLID, 1, RGB(190, 192, 196));
        SelectObject(memDC, pagePen);
        Rectangle(memDC, pageRect.left, pageRect.top, pageRect.right, pageRect.bottom);
        DeleteObject(pagePen);

        // Cabecera / Número de página
        SetTextColor(memDC, RGB(140, 140, 140));
        std::wstring pageNumText = L"- " + std::to_wstring(m_currentPage) + L" -";
        RECT pageNumRect = {pageRect.left, pageRect.bottom - 30, pageRect.right, pageRect.bottom - 10};
        DrawTextW(memDC, pageNumText.c_str(), -1, &pageNumRect, DT_SINGLELINE | DT_CENTER | DT_VCENTER);
    } else {
        // Modo continuo centrado
        int contWidth = (std::min)(w - 40, 720);
        int contLeft = (w - contWidth) / 2;
        pageRect = {contLeft, contentTop, contLeft + contWidth, h - 20};
    }

    // 5. Renderizado de líneas de texto
    RECT textBounds = {pageRect.left + 40, pageRect.top + 30, pageRect.right - 40, pageRect.bottom - 40};
    SetTextColor(memDC, (m_viewMode == EditorViewMode::PageView) ? RGB(30, 30, 30) : pal.editorFg);

    // Preparar texto con invisibles si está activo
    std::wstring displayText = m_plainText;
    if (m_showInvisibles) {
        std::wstring invText;
        for (wchar_t c : m_plainText) {
            if (c == L' ') invText += L'\x00B7';
            else if (c == L'\t') invText += L'\x2192';
            else if (c == L'\n') { invText += L'\x00B6'; invText += L'\n'; }
            else invText += c;
        }
        displayText = invText;
    }

    if (!displayText.empty()) {
        DrawTextW(memDC, displayText.c_str(), -1, &textBounds, DT_WORDBREAK | DT_LEFT);
    } else {
        SetTextColor(memDC, RGB(160, 160, 160));
        std::wstring hint = L"Haz clic aquí para comenzar a escribir en el manuscrito...";
        DrawTextW(memDC, hint.c_str(), -1, &textBounds, DT_WORDBREAK | DT_LEFT);
    }

    // Transferencia final a pantalla (BitBlt)
    BitBlt(hdc, bounds.left, bounds.top, w, h, memDC, 0, 0, SRCCOPY);

    // Limpieza de objetos GDI
    SelectObject(memDC, oldFont);
    DeleteObject(tbFont);
    SelectObject(memDC, oldPen);
    DeleteObject(borderPen);
    SelectObject(memDC, oldBM);
    DeleteObject(memBM);
    DeleteDC(memDC);
}

} // namespace escritorio::ui
