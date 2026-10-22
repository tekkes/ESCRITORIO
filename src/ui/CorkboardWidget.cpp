#include "CorkboardWidget.hpp"
#include <algorithm>
#include <sstream>

namespace escritorio::ui {

CorkboardWidget::CorkboardWidget() {
    // Fichas de muestra iniciales
    NativeIndexCard c1;
    c1.uuid = L"card-1";
    c1.title = L"Escena 1.1: El Callejón";
    c1.synopsis = L"Isabel llega al callejón oscuro bajo la lluvia. Encuentra la primera pista grabada en la piedra.";
    c1.cardNumber = 1;
    c1.labelId = 1;
    c1.labelName = L"Trama Principal";
    c1.labelColor = RGB(234, 88, 12);
    c1.statusName = L"BORRADOR";
    c1.keywords = { L"Noche", L"Misterio" };
    c1.keywordColors = { RGB(59, 130, 246), RGB(239, 68, 68) };
    c1.freeformX = 40.0f;
    c1.freeformY = 50.0f;
    m_cards.push_back(c1);

    NativeIndexCard c2;
    c2.uuid = L"card-2";
    c2.title = L"Escena 1.2: El Umbral";
    c2.synopsis = L"La puerta secreta se abre con un chasquido. El vigilante pasa cerca sin percatarse de su presencia.";
    c2.cardNumber = 2;
    c2.labelId = 2;
    c2.labelName = L"Subtrama Marcos";
    c2.labelColor = RGB(16, 185, 129);
    c2.statusName = L"REVISADO";
    c2.keywords = { L"Tensión" };
    c2.keywordColors = { RGB(245, 158, 11) };
    c2.freeformX = 300.0f;
    c2.freeformY = 50.0f;
    m_cards.push_back(c2);

    NativeIndexCard c3;
    c3.uuid = L"card-3";
    c3.title = L"Escena 1.3: El Archivo Oculto";
    c3.synopsis = L"Dentro de la sala polvorienta, las estanterías de pergaminos revelan el mapa de las catacumbas.";
    c3.cardNumber = 3;
    c3.labelId = 1;
    c3.labelName = L"Trama Principal";
    c3.labelColor = RGB(234, 88, 12);
    c3.statusName = L"LISTO";
    c3.keywords = { L"Descubrimiento" };
    c3.keywordColors = { RGB(139, 92, 246) };
    c3.freeformX = 560.0f;
    c3.freeformY = 50.0f;
    m_cards.push_back(c3);
}

void CorkboardWidget::Clear() {
    m_cards.clear();
}

void CorkboardWidget::AddCard(const NativeIndexCard& card) {
    m_cards.push_back(card);
    m_cards.back().cardNumber = static_cast<int>(m_cards.size());
}

NativeIndexCard* CorkboardWidget::GetCard(size_t index) {
    if (index < m_cards.size()) {
        return &m_cards[index];
    }
    return nullptr;
}

NativeIndexCard* CorkboardWidget::GetCardByUuid(const std::wstring& uuid) {
    for (auto& c : m_cards) {
        if (c.uuid == uuid) {
            return &c;
        }
    }
    return nullptr;
}

void CorkboardWidget::SetMode(NativeCorkboardMode mode) {
    m_mode = mode;
}

void CorkboardWidget::CycleMode() {
    if (m_mode == NativeCorkboardMode::Grid) {
        m_mode = NativeCorkboardMode::Freeform;
    } else if (m_mode == NativeCorkboardMode::Freeform) {
        m_mode = NativeCorkboardMode::Swimlanes;
    } else {
        m_mode = NativeCorkboardMode::Grid;
    }
}

void CorkboardWidget::SetCardWidth(float width) {
    m_cardWidth = (std::max)(120.0f, (std::min)(500.0f, width));
}

void CorkboardWidget::SetAspectRatio(int ratioMode) {
    m_aspectRatioMode = (std::max)(0, (std::min)(2, ratioMode));
}

void CorkboardWidget::SetSpacing(float spacing) {
    m_spacing = (std::max)(4.0f, (std::min)(48.0f, spacing));
}

void CorkboardWidget::SetCardsPerRow(int count) {
    m_cardsPerRow = (std::max)(0, (std::min)(10, count));
}

bool CorkboardWidget::ToggleStatusStamps() {
    m_showStatusStamps = !m_showStatusStamps;
    return m_showStatusStamps;
}

bool CorkboardWidget::TogglePins() {
    m_showPins = !m_showPins;
    return m_showPins;
}

bool CorkboardWidget::ToggleNotebookLines() {
    m_showNotebookLines = !m_showNotebookLines;
    return m_showNotebookLines;
}

void CorkboardWidget::SetLabelStyle(NativeLabelStyle style) {
    m_labelStyle = style;
}

float CorkboardWidget::GetCardHeight() const {
    if (m_aspectRatioMode == 0) {
        return m_cardWidth / 1.666f; // 3x5
    } else if (m_aspectRatioMode == 1) {
        return m_cardWidth / 1.500f; // 4x6
    }
    return m_cardWidth; // 1x1
}

int CorkboardWidget::CalculateColumns(int availableWidth) const {
    if (m_cardsPerRow > 0) {
        return (std::min)(10, (std::max)(1, m_cardsPerRow));
    }
    float colW = m_cardWidth + m_spacing;
    int cols = static_cast<int>((availableWidth - m_spacing) / colW);
    return (std::min)(10, (std::max)(1, cols));
}

bool CorkboardWidget::ReorderGrid(size_t fromIdx, size_t toIdx) {
    if (fromIdx >= m_cards.size() || toIdx >= m_cards.size()) return false;
    auto card = m_cards[fromIdx];
    m_cards.erase(m_cards.begin() + fromIdx);
    m_cards.insert(m_cards.begin() + toIdx, card);

    for (size_t i = 0; i < m_cards.size(); ++i) {
        m_cards[i].cardNumber = static_cast<int>(i + 1);
    }
    return true;
}

void CorkboardWidget::CommitFreeformOrder() {
    // Ordenar de arriba a abajo y de izquierda a derecha
    std::sort(m_cards.begin(), m_cards.end(), [](const NativeIndexCard& a, const NativeIndexCard& b) {
        int rowA = static_cast<int>(a.freeformY / 80.0f);
        int rowB = static_cast<int>(b.freeformY / 80.0f);
        if (rowA != rowB) return rowA < rowB;
        return a.freeformX < b.freeformX;
    });

    for (size_t i = 0; i < m_cards.size(); ++i) {
        m_cards[i].cardNumber = static_cast<int>(i + 1);
    }
}

bool CorkboardWidget::MoveCardToSwimlane(const std::wstring& uuid, int targetLabelId) {
    auto* c = GetCardByUuid(uuid);
    if (!c) return false;
    c->labelId = targetLabelId;
    return true;
}

void CorkboardWidget::Render(HDC hdc, const RECT& area, const escritorio::themes::ThemePalette& pal,
                             const escritorio::themes::UIDensityMetrics& metrics, HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody) {
    int w = area.right - area.left;
    int h = area.bottom - area.top;
    if (w <= 0 || h <= 0) return;

    // Fondo del corcho con tono cálido adaptado al tema activo
    HBRUSH hBrBg = CreateSolidBrush(pal.corkboardBg);
    FillRect(hdc, &area, hBrBg);
    DeleteObject(hBrBg);

    int footerHeight = metrics.toolbarHeight > 0 ? metrics.toolbarHeight : 26;
    RECT contentArea = { area.left, area.top, area.right, area.bottom - footerHeight };
    RECT footerArea = { area.left, area.bottom - footerHeight, area.right, area.bottom };

    if (m_mode == NativeCorkboardMode::Grid) {
        RenderGrid(hdc, contentArea, pal, hFontTitle, hFontSmall, hFontBody);
    } else if (m_mode == NativeCorkboardMode::Freeform) {
        RenderFreeform(hdc, contentArea, pal, hFontTitle, hFontSmall, hFontBody);
    } else {
        RenderSwimlanes(hdc, contentArea, pal, hFontTitle, hFontSmall, hFontBody);
    }

    RenderFooter(hdc, footerArea, pal, hFontSmall);
}

void CorkboardWidget::RenderGrid(HDC hdc, const RECT& contentArea, const escritorio::themes::ThemePalette& pal,
                                 HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody) {
    int availW = contentArea.right - contentArea.left;
    int cols = CalculateColumns(availW);
    float cardH = GetCardHeight();

    for (size_t i = 0; i < m_cards.size(); ++i) {
        int r = static_cast<int>(i) / cols;
        int c = static_cast<int>(i) % cols;

        int x = contentArea.left + static_cast<int>(m_spacing + c * (m_cardWidth + m_spacing));
        int y = contentArea.top + static_cast<int>(m_spacing + r * (cardH + m_spacing));

        RECT cardRect = { x, y, x + static_cast<int>(m_cardWidth), y + static_cast<int>(cardH) };
        if (cardRect.bottom < contentArea.bottom) {
            RenderSingleCard(hdc, cardRect, m_cards[i], pal, hFontTitle, hFontSmall, hFontBody);
        }
    }
}

void CorkboardWidget::RenderFreeform(HDC hdc, const RECT& contentArea, const escritorio::themes::ThemePalette& pal,
                                     HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody) {
    // Cabecera indicadora de modo libre con botón de confirmación
    RECT rBanner = { contentArea.left + 16, contentArea.top + 8, contentArea.right - 16, contentArea.top + 32 };
    SelectObject(hdc, hFontSmall);
    SetTextColor(hdc, pal.binderSecondary);
    SetBkMode(hdc, TRANSPARENT);
    DrawTextW(hdc, L"MODO FORMA LIBRE 2D (Arrastra tarjetas libremente) - [ Confirmar orden al Binder ]", -1, &rBanner, DT_LEFT | DT_VCENTER | DT_SINGLELINE);

    float cardH = GetCardHeight();
    for (const auto& card : m_cards) {
        int x = contentArea.left + static_cast<int>(card.freeformX);
        int y = contentArea.top + static_cast<int>(card.freeformY);
        RECT cardRect = { x, y, x + static_cast<int>(m_cardWidth), y + static_cast<int>(cardH) };
        RenderSingleCard(hdc, cardRect, card, pal, hFontTitle, hFontSmall, hFontBody);
    }
}

void CorkboardWidget::RenderSwimlanes(HDC hdc, const RECT& contentArea, const escritorio::themes::ThemePalette& pal,
                                      HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody) {
    // Agrupar en 3 carriles de ejemplo: Trama Principal, Subtrama Marcos, Otras
    int availW = contentArea.right - contentArea.left;
    int laneW = (availW - 32) / 3;
    float cardH = GetCardHeight() * 0.85f;

    struct LaneDef {
        int id;
        const wchar_t* name;
        COLORREF color;
    };
    LaneDef lanes[] = {
        { 1, L"Trama Principal (Isabel)", RGB(234, 88, 12) },
        { 2, L"Subtrama Marcos (Vigilante)", RGB(16, 185, 129) },
        { -1, L"Sin Etiqueta", RGB(148, 163, 184) }
    };

    HPEN hPenBorder = CreatePen(PS_SOLID, 1, pal.toolbarBorder);
    HPEN hOldPen = static_cast<HPEN>(SelectObject(hdc, hPenBorder));

    for (int l = 0; l < 3; ++l) {
        int laneLeft = contentArea.left + 12 + l * laneW;
        int laneRight = laneLeft + laneW - 8;

        // Cabecera de carril
        RECT rLaneHeader = { laneLeft, contentArea.top + 8, laneRight, contentArea.top + 34 };
        HBRUSH hBrHdr = CreateSolidBrush(lanes[l].color);
        FillRect(hdc, &rLaneHeader, hBrHdr);
        DeleteObject(hBrHdr);

        SelectObject(hdc, hFontSmall);
        SetTextColor(hdc, RGB(255, 255, 255));
        SetBkMode(hdc, TRANSPARENT);
        DrawTextW(hdc, lanes[l].name, -1, &rLaneHeader, DT_CENTER | DT_VCENTER | DT_SINGLELINE);

        // Tarjetas en este carril
        int cardY = contentArea.top + 42;
        for (const auto& card : m_cards) {
            if ((lanes[l].id == -1 && card.labelId != 1 && card.labelId != 2) || card.labelId == lanes[l].id) {
                RECT cRect = { laneLeft + 8, cardY, laneRight - 8, cardY + static_cast<int>(cardH) };
                RenderSingleCard(hdc, cRect, card, pal, hFontTitle, hFontSmall, hFontBody);
                cardY += static_cast<int>(cardH) + 12;
            }
        }
    }

    SelectObject(hdc, hOldPen);
    DeleteObject(hPenBorder);
}

void CorkboardWidget::RenderSingleCard(HDC hdc, const RECT& rc, const NativeIndexCard& card,
                                       const escritorio::themes::ThemePalette& pal, HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody) {
    (void)hFontTitle;
    (void)hFontBody;
    // 1. Sombra suave de la tarjeta
    RECT rcShadow = { rc.left + 2, rc.top + 2, rc.right + 2, rc.bottom + 2 };
    HBRUSH hBrShadow = CreateSolidBrush(RGB(200, 200, 195));
    FillRect(hdc, &rcShadow, hBrShadow);
    DeleteObject(hBrShadow);

    // 2. Fondo de la tarjeta (blanco cálido o tintado con etiqueta)
    COLORREF cardBg = pal.corkboardCardBg;
    if (m_labelStyle == NativeLabelStyle::FullBackground) {
        cardBg = card.labelColor;
    }
    HBRUSH hBrCard = CreateSolidBrush(cardBg);
    FillRect(hdc, &rc, hBrCard);
    DeleteObject(hBrCard);

    // Borde de la tarjeta
    HPEN hPenCard = CreatePen(PS_SOLID, 1, pal.corkboardCardBorder);
    HPEN hOldPen = static_cast<HPEN>(SelectObject(hdc, hPenCard));
    Rectangle(hdc, rc.left, rc.top, rc.right, rc.bottom);

    // 3. Franja lateral de etiqueta (Stripe)
    if (m_labelStyle == NativeLabelStyle::Stripe) {
        RECT rStripe = { rc.left, rc.top, rc.left + 6, rc.bottom };
        HBRUSH hBrStripe = CreateSolidBrush(card.labelColor);
        FillRect(hdc, &rStripe, hBrStripe);
        DeleteObject(hBrStripe);
    }

    // 4. Alfiler de corcho (Pin) en parte superior central
    if (m_showPins && m_labelStyle == NativeLabelStyle::Pin) {
        int pinX = (rc.left + rc.right) / 2;
        int pinY = rc.top + 5;
        HBRUSH hBrPin = CreateSolidBrush(card.labelColor);
        HBRUSH hOldBr = static_cast<HBRUSH>(SelectObject(hdc, hBrPin));
        Ellipse(hdc, pinX - 4, pinY - 4, pinX + 4, pinY + 4);
        SelectObject(hdc, hOldBr);
        DeleteObject(hBrPin);
    }

    // 5. Cabecera de la ficha: Número y Título
    int contentLeft = rc.left + (m_labelStyle == NativeLabelStyle::Stripe ? 12 : 8);
    RECT rHeader = { contentLeft, rc.top + 10, rc.right - 8, rc.top + 28 };
    SelectObject(hdc, hFontSmall);
    SetTextColor(hdc, pal.corkboardCardFg);
    SetBkMode(hdc, TRANSPARENT);

    std::wstringstream ssTitle;
    if (card.showNumber) {
        ssTitle << L"[" << card.cardNumber << L"] ";
    }
    ssTitle << card.title;
    std::wstring strTitle = ssTitle.str();
    DrawTextW(hdc, strTitle.c_str(), -1, &rHeader, DT_LEFT | DT_SINGLELINE | DT_END_ELLIPSIS);

    // Línea separadora de cabecera
    MoveToEx(hdc, contentLeft, rc.top + 30, nullptr);
    LineTo(hdc, rc.right - 8, rc.top + 30);

    // 6. Líneas de libreta opcionales en el cuerpo
    if (m_showNotebookLines) {
        HPEN hPenRule = CreatePen(PS_SOLID, 1, RGB(230, 230, 235));
        SelectObject(hdc, hPenRule);
        int lineY = rc.top + 46;
        while (lineY < rc.bottom - 22) {
            MoveToEx(hdc, contentLeft, lineY, nullptr);
            LineTo(hdc, rc.right - 8, lineY);
            lineY += 16;
        }
        DeleteObject(hPenRule);
    }

    // 7. Texto de la sinopsis
    RECT rSynopsis = { contentLeft, rc.top + 34, rc.right - 8, rc.bottom - 22 };
    SelectObject(hdc, hFontSmall);
    SetTextColor(hdc, pal.corkboardCardFg);
    DrawTextW(hdc, card.synopsis.c_str(), -1, &rSynopsis, DT_LEFT | DT_WORDBREAK | DT_END_ELLIPSIS);

    // 8. Sello de Estado diagonal semitransparente (Status Stamp)
    if (m_showStatusStamps && card.showStatusStamp && !card.statusName.empty()) {
        RECT rStamp = { rc.left + 10, rc.top + 24, rc.right - 10, rc.bottom - 24 };
        SetTextColor(hdc, RGB(210, 210, 215));
        DrawTextW(hdc, card.statusName.c_str(), -1, &rStamp, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
    }

    // 9. Chips de palabras clave en el margen inferior
    if (!card.keywords.empty()) {
        int chipX = contentLeft;
        int chipY = rc.bottom - 16;
        for (size_t k = 0; k < card.keywords.size() && k < 3; ++k) {
            RECT rChip = { chipX, chipY, chipX + 42, chipY + 10 };
            COLORREF cColor = (k < card.keywordColors.size()) ? card.keywordColors[k] : RGB(59, 130, 246);
            HBRUSH hBrChip = CreateSolidBrush(cColor);
            FillRect(hdc, &rChip, hBrChip);
            DeleteObject(hBrChip);
            chipX += 48;
        }
    }

    SelectObject(hdc, hOldPen);
    DeleteObject(hPenCard);
}

void CorkboardWidget::RenderFooter(HDC hdc, const RECT& footerArea, const escritorio::themes::ThemePalette& pal,
                                   HFONT hFontSmall) {
    // Fondo de la barra inferior
    HBRUSH hBrFoot = CreateSolidBrush(pal.toolbarBg);
    FillRect(hdc, &footerArea, hBrFoot);
    DeleteObject(hBrFoot);

    HPEN hPenBorder = CreatePen(PS_SOLID, 1, pal.toolbarBorder);
    HPEN hOldPen = static_cast<HPEN>(SelectObject(hdc, hPenBorder));
    MoveToEx(hdc, footerArea.left, footerArea.top, nullptr);
    LineTo(hdc, footerArea.right, footerArea.top);

    SelectObject(hdc, hFontSmall);
    SetTextColor(hdc, pal.toolbarFg);
    SetBkMode(hdc, TRANSPARENT);

    // Submodos: [ Rejilla ] [ Forma Libre ] [ Swimlanes ]
    std::wstring modeStr = L"Submodo: ";
    if (m_mode == NativeCorkboardMode::Grid) modeStr += L"[Rejilla]  Libre  Swimlanes";
    else if (m_mode == NativeCorkboardMode::Freeform) modeStr += L"Rejilla  [Forma Libre]  Swimlanes";
    else modeStr += L"Rejilla  Libre  [Swimlanes]";

    RECT rMode = { footerArea.left + 16, footerArea.top, footerArea.left + 340, footerArea.bottom };
    DrawTextW(hdc, modeStr.c_str(), -1, &rMode, DT_LEFT | DT_VCENTER | DT_SINGLELINE);

    // Controles: Tamaño, Ratio (3x5), Fila (Auto)
    const wchar_t* ratioNames[] = { L"3x5", L"4x6", L"1:1" };
    std::wstringstream ssRight;
    ssRight << L"Ratio: " << ratioNames[m_aspectRatioMode]
            << L" | Tarjetas/Fila: " << (m_cardsPerRow == 0 ? L"Auto" : std::to_wstring(m_cardsPerRow).c_str())
            << L" | Sellos: " << (m_showStatusStamps ? L"ON" : L"OFF")
            << L" | Pines: " << (m_showPins ? L"ON" : L"OFF");
    std::wstring strRight = ssRight.str();

    RECT rRight = { footerArea.right - 420, footerArea.top, footerArea.right - 16, footerArea.bottom };
    SetTextColor(hdc, pal.accentPrimary);
    DrawTextW(hdc, strRight.c_str(), -1, &rRight, DT_RIGHT | DT_VCENTER | DT_SINGLELINE);

    SelectObject(hdc, hOldPen);
    DeleteObject(hPenBorder);
}

} // namespace escritorio::ui
