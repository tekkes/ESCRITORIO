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

enum class NativeCorkboardMode {
    Grid,        // Rejilla (Arrange by Order)
    Freeform,    // Forma Libre 2D (Zoom y Paneo)
    Swimlanes    // Apilado por Etiqueta (Columnas / Carriles)
};

enum class NativeLabelStyle {
    Pin,             // Alfiler en cabecera
    Stripe,          // Franja lateral
    FullBackground   // Fondo tintado completo
};

struct NativeIndexCard {
    std::wstring uuid;
    std::wstring title;
    std::wstring synopsis;
    int cardNumber = 1;
    bool showNumber = true;

    // Etiqueta
    int labelId = -1;
    std::wstring labelName = L"Sin Etiqueta";
    COLORREF labelColor = RGB(45, 114, 217);
    NativeLabelStyle labelStyle = NativeLabelStyle::Pin;

    // Estado y Sello
    int statusId = -1;
    std::wstring statusName = L"BORRADOR";
    bool showStatusStamp = true;

    // Estética de libreta y palabras clave
    bool notebookLines = true;
    std::vector<std::wstring> keywords;
    std::vector<COLORREF> keywordColors;

    // Posición en modo Libre 2D
    float freeformX = 40.0f;
    float freeformY = 40.0f;
};

class CorkboardWidget {
public:
    CorkboardWidget();
    ~CorkboardWidget() = default;

    void Clear();
    void AddCard(const NativeIndexCard& card);
    size_t GetCardCount() const { return m_cards.size(); }
    NativeIndexCard* GetCard(size_t index);
    NativeIndexCard* GetCardByUuid(const std::wstring& uuid);

    // Modos
    void SetMode(NativeCorkboardMode mode);
    NativeCorkboardMode GetMode() const { return m_mode; }
    void CycleMode();

    // Controles de barra inferior
    void SetCardWidth(float width);
    float GetCardWidth() const { return m_cardWidth; }
    void SetAspectRatio(int ratioMode); // 0=3x5, 1=4x6, 2=1x1
    int GetAspectRatio() const { return m_aspectRatioMode; }
    void SetSpacing(float spacing);
    float GetSpacing() const { return m_spacing; }
    void SetCardsPerRow(int count); // 0=Auto, 1..10
    int GetCardsPerRow() const { return m_cardsPerRow; }

    // Conmutadores
    bool ToggleStatusStamps();
    bool AreStatusStampsVisible() const { return m_showStatusStamps; }
    bool TogglePins();
    bool ArePinsVisible() const { return m_showPins; }
    bool ToggleNotebookLines();
    bool AreNotebookLinesVisible() const { return m_showNotebookLines; }
    void SetLabelStyle(NativeLabelStyle style);
    NativeLabelStyle GetLabelStyle() const { return m_labelStyle; }

    // Reordenaciones
    bool ReorderGrid(size_t fromIdx, size_t toIdx);
    void CommitFreeformOrder();
    bool MoveCardToSwimlane(const std::wstring& uuid, int targetLabelId);

    // Renderizado en HDC
    void Render(HDC hdc, const RECT& area, const escritorio::themes::ThemePalette& pal,
                const escritorio::themes::UIDensityMetrics& metrics, HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody);

private:
    NativeCorkboardMode m_mode = NativeCorkboardMode::Grid;
    std::vector<NativeIndexCard> m_cards;

    // Configuración visual
    float m_cardWidth = 220.0f;
    int m_aspectRatioMode = 0; // 0=3x5, 1=4x6, 2=1x1
    float m_spacing = 16.0f;
    int m_cardsPerRow = 0; // 0=Auto

    bool m_showStatusStamps = true;
    bool m_showPins = true;
    bool m_showNotebookLines = true;
    NativeLabelStyle m_labelStyle = NativeLabelStyle::Pin;

    // Forma Libre
    float m_freeformZoom = 1.0f;
    float m_freeformPanX = 0.0f;
    float m_freeformPanY = 0.0f;

    float GetCardHeight() const;
    int CalculateColumns(int availableWidth) const;

    void RenderGrid(HDC hdc, const RECT& contentArea, const escritorio::themes::ThemePalette& pal,
                    HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody);
    void RenderFreeform(HDC hdc, const RECT& contentArea, const escritorio::themes::ThemePalette& pal,
                        HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody);
    void RenderSwimlanes(HDC hdc, const RECT& contentArea, const escritorio::themes::ThemePalette& pal,
                         HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody);
    void RenderFooter(HDC hdc, const RECT& footerArea, const escritorio::themes::ThemePalette& pal,
                      HFONT hFontSmall);
    void RenderSingleCard(HDC hdc, const RECT& cardRect, const NativeIndexCard& card,
                          const escritorio::themes::ThemePalette& pal, HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody);
};

} // namespace escritorio::ui
