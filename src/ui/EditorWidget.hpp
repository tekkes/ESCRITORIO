#pragma once

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <string>
#include <vector>
#include <memory>
#include <map>
#include "../themes/ThemeEngine.hpp"

namespace escritorio::ui {

enum class EditorViewMode {
    Continuous,
    PageView
};

enum class FocusScope {
    Off,
    Line,
    Sentence,
    Paragraph
};

enum class LinguisticCategory {
    None,
    Dialogues,
    Adverbs,
    Adjectives,
    Verbs,
    Conjunctions
};

enum class StyleType {
    None,
    Paragraph,
    Character,
    Combined
};

struct StyleItem {
    std::wstring id;
    std::wstring name;
    StyleType type = StyleType::None;
    std::wstring shortcut;
    bool isBuiltin = true;
    bool isDefault = false;
    float fontSize = 12.0f;
    bool bold = false;
    bool italic = false;
    std::wstring fontFamily = L"Segoe UI";
    COLORREF textColor = RGB(0, 0, 0);
    COLORREF bgColor = RGB(255, 255, 255);
    int alignment = 0; // 0=left, 1=center, 2=right, 3=justify
    float lineSpacing = 1.15f;
    float spaceBefore = 0.0f;
    float spaceAfter = 6.0f;
    float firstLineIndent = 0.0f;
    float leftIndent = 0.0f;
    float rightIndent = 0.0f;
};

struct HighlightSpanNative {
    size_t start;
    size_t end;
    LinguisticCategory category;
};

class EditorWidget {
public:
    EditorWidget();
    ~EditorWidget() = default;

    // Carga de texto y sincronización
    void SetPlainText(const std::wstring& text);
    const std::wstring& GetPlainText() const { return m_plainText; }
    void SetItemUuid(const std::wstring& uuid, const std::wstring& title);
    const std::wstring& GetItemUuid() const { return m_itemUuid; }

    // Métricas
    size_t GetWordCount() const;
    size_t GetCharacterCount() const;

    // Regla horizontal (Ctrl+Shift+R)
    bool ToggleRuler() { m_showRuler = !m_showRuler; return m_showRuler; }
    bool IsRulerVisible() const { return m_showRuler; }
    void SetFirstLineIndent(float pt) { m_firstLineIndent = pt; }
    void SetLeftIndent(float pt) { m_leftIndent = pt; }
    void SetRightIndent(float pt) { m_rightIndent = pt; }

    // Vista de Página (Alt+Shift+P)
    EditorViewMode TogglePageView();
    EditorViewMode GetViewMode() const { return m_viewMode; }
    int GetTotalPages() const { return m_totalPages; }
    int GetCurrentPage() const { return m_currentPage; }

    // Desplazamiento de Máquina de Escribir (Ctrl+Alt+T)
    bool ToggleTypewriterScrolling() { m_typewriterScrolling = !m_typewriterScrolling; return m_typewriterScrolling; }
    bool IsTypewriterScrolling() const { return m_typewriterScrolling; }

    // Modo Foco
    void SetFocusScope(FocusScope scope) { m_focusScope = scope; }
    FocusScope GetFocusScope() const { return m_focusScope; }

    // Foco Lingüístico
    void SetLinguisticCategory(LinguisticCategory cat) { m_linguisticCategory = cat; }
    LinguisticCategory GetLinguisticCategory() const { return m_linguisticCategory; }

    // Caracteres Invisibles
    bool ToggleInvisibles() { m_showInvisibles = !m_showInvisibles; return m_showInvisibles; }
    bool AreInvisiblesVisible() const { return m_showInvisibles; }

    // Estilos Semánticos (StyleEngine)
    void InitDefaultStyles();
    const std::vector<StyleItem>& GetStyles() const { return m_styles; }
    bool ApplyStyle(const std::wstring& styleId);
    std::wstring GetActiveStyleId() const { return m_activeStyleId; }
    bool CreateStyleFromSelection(const std::wstring& name, StyleType type);
    bool RedefineStyleFromSelection(const std::wstring& styleId);

    // Formato de Carácter / Párrafo
    void ToggleBold();
    void ToggleItalic();
    void ToggleUnderline();
    void SetAlignment(int align); // 0=left, 1=center, 2=right, 3=justify
    void SetLineSpacing(float spacing);
    void SetHighlightColor(COLORREF color);

    // Inserciones
    void InsertTable(int rows, int cols);
    void InsertBulletList();
    void InsertNumberedList();
    void InsertImage(const std::wstring& path);
    void InsertScrivenerLink(const std::wstring& targetUuid, const std::wstring& display);

    // Renderizado en HDC
    void Render(HDC hdc, const RECT& bounds, const escritorio::themes::ThemePalette& pal,
                const escritorio::themes::UIDensityMetrics& metrics);

private:
    std::wstring m_itemUuid;
    std::wstring m_itemTitle;
    std::wstring m_plainText;
    size_t m_cursorPos = 0;
    size_t m_selStart = 0;
    size_t m_selEnd = 0;

    // Modos y herramientas
    bool m_showRuler = true;
    EditorViewMode m_viewMode = EditorViewMode::Continuous;
    bool m_typewriterScrolling = false;
    FocusScope m_focusScope = FocusScope::Off;
    LinguisticCategory m_linguisticCategory = LinguisticCategory::None;
    bool m_showInvisibles = false;

    // Regla y sangrías
    float m_firstLineIndent = 0.0f;
    float m_leftIndent = 0.0f;
    float m_rightIndent = 0.0f;

    // Formato activo
    std::wstring m_fontFamily = L"Segoe UI";
    float m_fontSize = 12.0f;
    bool m_bold = false;
    bool m_italic = false;
    bool m_underline = false;
    COLORREF m_textColor = RGB(0, 0, 0);
    COLORREF m_highlightColor = CLR_INVALID;
    int m_alignment = 0;
    float m_lineSpacing = 1.15f;
    float m_spaceBefore = 0.0f;
    float m_spaceAfter = 6.0f;
    std::wstring m_activeStyleId = L"style-no-style";

    // Paginación
    int m_totalPages = 1;
    int m_currentPage = 1;

    // Estilos
    std::vector<StyleItem> m_styles;

    // Auxiliares de análisis
    std::vector<HighlightSpanNative> AnalyzeLinguisticFocus() const;
    std::pair<size_t, size_t> GetFocusedSpan() const;
};

} // namespace escritorio::ui
