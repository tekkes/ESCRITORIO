#include "OutlinerWidget.hpp"
#include <algorithm>
#include <sstream>
#include <iomanip>

namespace escritorio::ui {

OutlinerWidget::OutlinerWidget() {
    // Configurar columnas predeterminadas
    m_columns = {
        { L"title_synopsis", L"Título y Sinopsis", 320, 160, true },
        { L"label", L"Etiqueta", 110, 80, true },
        { L"status", L"Estado", 100, 70, true },
        { L"section_type", L"Tipo Sección", 120, 80, true },
        { L"include_in_compile", L"Compilar", 75, 60, true },
        { L"words", L"Palabras", 80, 60, true },
        { L"total_words", L"Total Pal.", 95, 70, true },
        { L"target", L"Objetivo", 80, 60, true },
        { L"progress", L"Progreso", 130, 90, true },
        { L"pov", L"POV", 90, 60, true }
    };

    // Datos iniciales de muestra con jerarquía
    NativeOutlinerItem cap1;
    cap1.uuid = L"cap-1";
    cap1.title = L"Capítulo 1: El Despertar";
    cap1.synopsis = L"Isabel despierta ante la inminencia de la lluvia y sale en busca del manuscrito.";
    cap1.level = 0;
    cap1.isFolder = true;
    cap1.expanded = true;
    cap1.words = 200;
    cap1.totalWords = 3760;
    cap1.characters = 1200;
    cap1.totalCharacters = 22500;
    cap1.target = 500;
    cap1.totalTarget = 4500;
    cap1.progressPercent = 83.5f;
    cap1.includeInCompile = true;
    cap1.sectionType = L"Chapter";
    cap1.labelId = 1;
    cap1.labelName = L"Trama Principal";
    cap1.labelColor = RGB(234, 88, 12);
    cap1.statusId = 1;
    cap1.statusName = L"En Progreso";
    cap1.customMetadata[L"POV"] = L"Isabel";
    m_items.push_back(cap1);

    NativeOutlinerItem sc1;
    sc1.uuid = L"sc-1-1";
    sc1.title = L"Escena 1.1: El Callejón";
    sc1.synopsis = L"Isabel sortea las patrullas nocturnas bajo la tormenta.";
    sc1.level = 1;
    sc1.isFolder = false;
    sc1.words = 1250;
    sc1.totalWords = 1250;
    sc1.characters = 7500;
    sc1.totalCharacters = 7500;
    sc1.target = 1500;
    sc1.totalTarget = 1500;
    sc1.progressPercent = 83.3f;
    sc1.includeInCompile = true;
    sc1.sectionType = L"Scene";
    sc1.labelId = 1;
    sc1.labelName = L"Trama Principal";
    sc1.labelColor = RGB(234, 88, 12);
    sc1.statusId = 2;
    sc1.statusName = L"Revisado";
    sc1.customMetadata[L"POV"] = L"Isabel";
    m_items.push_back(sc1);

    NativeOutlinerItem sc2;
    sc2.uuid = L"sc-1-2";
    sc2.title = L"Escena 1.2: El Umbral";
    sc2.synopsis = L"Marcos vigila el portón de la catedral cuando escucha pasos aproximarse.";
    sc2.level = 1;
    sc2.isFolder = false;
    sc2.words = 890;
    sc2.totalWords = 890;
    sc2.characters = 5400;
    sc2.totalCharacters = 5400;
    sc2.target = 1000;
    sc2.totalTarget = 1000;
    sc2.progressPercent = 89.0f;
    sc2.includeInCompile = true;
    sc2.sectionType = L"Scene";
    sc2.labelId = 2;
    sc2.labelName = L"Subtrama Marcos";
    sc2.labelColor = RGB(16, 185, 129);
    sc2.statusId = 3;
    sc2.statusName = L"Listo";
    sc2.customMetadata[L"POV"] = L"Marcos";
    m_items.push_back(sc2);

    NativeOutlinerItem sc3;
    sc3.uuid = L"sc-1-3";
    sc3.title = L"Escena 1.3: El Archivo Oculto";
    sc3.synopsis = L"Dentro de la cripta, se descubre el mapa sellado en cera negra.";
    sc3.level = 1;
    sc3.isFolder = false;
    sc3.words = 1420;
    sc3.totalWords = 1420;
    sc3.characters = 8400;
    sc3.totalCharacters = 8400;
    sc3.target = 2000;
    sc3.totalTarget = 2000;
    sc3.progressPercent = 71.0f;
    sc3.includeInCompile = true;
    sc3.sectionType = L"Scene";
    sc3.labelId = 1;
    sc3.labelName = L"Trama Principal";
    sc3.labelColor = RGB(234, 88, 12);
    sc3.statusId = 1;
    sc3.statusName = L"Borrador";
    sc3.customMetadata[L"POV"] = L"Isabel";
    m_items.push_back(sc3);
}

void OutlinerWidget::Clear() {
    m_items.clear();
}

void OutlinerWidget::AddItem(const NativeOutlinerItem& item) {
    m_items.push_back(item);
}

NativeOutlinerItem* OutlinerWidget::GetItem(size_t index) {
    if (index < m_items.size()) {
        return &m_items[index];
    }
    return nullptr;
}

NativeOutlinerItem* OutlinerWidget::GetItemByUuid(const std::wstring& uuid) {
    for (auto& it : m_items) {
        if (it.uuid == uuid) return &it;
    }
    return nullptr;
}

void OutlinerWidget::SetSort(const std::wstring& colId, OutlinerSortDirection dir) {
    m_sortColId = colId;
    m_sortDir = dir;
}

void OutlinerWidget::CycleSort(const std::wstring& colId) {
    if (m_sortColId != colId) {
        m_sortColId = colId;
        m_sortDir = OutlinerSortDirection::Ascending;
    } else {
        if (m_sortDir == OutlinerSortDirection::Ascending) {
            m_sortDir = OutlinerSortDirection::Descending;
        } else if (m_sortDir == OutlinerSortDirection::Descending) {
            m_sortDir = OutlinerSortDirection::None;
            m_sortColId.clear();
        } else {
            m_sortDir = OutlinerSortDirection::Ascending;
        }
    }
}

void OutlinerWidget::ToggleColumn(const std::wstring& colId) {
    for (auto& col : m_columns) {
        if (col.id == colId) {
            col.visible = !col.visible;
            break;
        }
    }
}

COLORREF OutlinerWidget::CalculateProgressColor(float percent) {
    float p = (std::max)(0.0f, (std::min)(100.0f, percent));
    if (p <= 50.0f) {
        // Rojo (239, 68, 68) a Ámbar (245, 158, 11)
        float factor = p / 50.0f;
        int r = static_cast<int>(239 + (245 - 239) * factor);
        int g = static_cast<int>(68 + (158 - 68) * factor);
        int b = static_cast<int>(68 + (11 - 68) * factor);
        return RGB(r, g, b);
    } else {
        // Ámbar (245, 158, 11) a Verde (16, 185, 129)
        float factor = (p - 50.0f) / 50.0f;
        int r = static_cast<int>(245 + (16 - 245) * factor);
        int g = static_cast<int>(158 + (185 - 158) * factor);
        int b = static_cast<int>(11 + (129 - 11) * factor);
        return RGB(r, g, b);
    }
}

std::wstring OutlinerWidget::ExportToCsvString() const {
    std::wstringstream ss;

    // Cabeceras
    bool first = true;
    for (const auto& c : m_columns) {
        if (!c.visible) continue;
        if (!first) ss << L",";
        ss << L"\"" << c.title << L"\"";
        first = false;
    }
    ss << L"\r\n";

    // Filas
    for (const auto& item : m_items) {
        first = true;
        for (const auto& c : m_columns) {
            if (!c.visible) continue;
            if (!first) ss << L",";

            if (c.id == L"title_synopsis") {
                ss << L"\"" << item.title << L" - " << item.synopsis << L"\"";
            } else if (c.id == L"label") {
                ss << L"\"" << item.labelName << L"\"";
            } else if (c.id == L"status") {
                ss << L"\"" << item.statusName << L"\"";
            } else if (c.id == L"section_type") {
                ss << L"\"" << item.sectionType << L"\"";
            } else if (c.id == L"include_in_compile") {
                ss << (item.includeInCompile ? L"\"Sí\"" : L"\"No\"");
            } else if (c.id == L"words") {
                ss << item.words;
            } else if (c.id == L"total_words") {
                ss << item.totalWords;
            } else if (c.id == L"target") {
                ss << item.target;
            } else if (c.id == L"progress") {
                ss << std::fixed << std::setprecision(1) << item.progressPercent << L"%";
            } else if (c.id == L"pov") {
                auto it = item.customMetadata.find(L"POV");
                ss << L"\"" << (it != item.customMetadata.end() ? it->second : L"") << L"\"";
            } else {
                ss << L"\"\"";
            }
            first = false;
        }
        ss << L"\r\n";
    }

    return ss.str();
}

void OutlinerWidget::Render(HDC hdc, const RECT& area, const escritorio::themes::ThemePalette& pal,
                            const escritorio::themes::UIDensityMetrics& metrics, HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody) {
    (void)hFontTitle;
    int w = area.right - area.left;
    int h = area.bottom - area.top;
    if (w <= 0 || h <= 0) return;

    // Fondo del área del esquema
    HBRUSH hBrBg = CreateSolidBrush(pal.editorBg);
    FillRect(hdc, &area, hBrBg);
    DeleteObject(hBrBg);

    int footerHeight = metrics.toolbarHeight > 0 ? metrics.toolbarHeight : 26;
    RECT headerRect = { area.left, area.top, area.right, area.top + m_headerHeight };
    RECT contentRect = { area.left, area.top + m_headerHeight, area.right, area.bottom - footerHeight };
    RECT footerRect = { area.left, area.bottom - footerHeight, area.right, area.bottom };

    // 1. Cabecera tabular
    RenderHeader(hdc, headerRect, pal, hFontSmall);

    // 2. Filas de datos
    int rowY = contentRect.top;
    for (size_t i = 0; i < m_items.size(); ++i) {
        if (rowY + m_rowHeight > contentRect.bottom) break;

        RECT rowRect = { contentRect.left, rowY, contentRect.right, rowY + m_rowHeight };
        RenderRow(hdc, rowRect, m_items[i], false, pal, hFontTitle, hFontSmall, hFontBody);
        rowY += m_rowHeight;
    }

    // 3. Barra inferior de control
    RenderFooter(hdc, footerRect, pal, hFontSmall);
}

void OutlinerWidget::RenderHeader(HDC hdc, const RECT& headerRect, const escritorio::themes::ThemePalette& pal, HFONT hFontSmall) {
    HBRUSH hBrHdr = CreateSolidBrush(pal.editorHeaderBg);
    FillRect(hdc, &headerRect, hBrHdr);
    DeleteObject(hBrHdr);

    HPEN hPenBorder = CreatePen(PS_SOLID, 1, pal.toolbarBorder);
    HPEN hOldPen = static_cast<HPEN>(SelectObject(hdc, hPenBorder));

    MoveToEx(hdc, headerRect.left, headerRect.bottom - 1, nullptr);
    LineTo(hdc, headerRect.right, headerRect.bottom - 1);

    SelectObject(hdc, hFontSmall);
    SetTextColor(hdc, pal.editorHeaderFg);
    SetBkMode(hdc, TRANSPARENT);

    int curX = headerRect.left;
    for (const auto& c : m_columns) {
        if (!c.visible) continue;

        RECT rcCol = { curX + 8, headerRect.top, curX + c.width - 8, headerRect.bottom };
        std::wstring titleText = c.title;

        // Añadir flecha de ordenación si es la columna activa
        if (c.id == m_sortColId) {
            titleText += (m_sortDir == OutlinerSortDirection::Ascending ? L" ▲" : L" ▼");
        }

        DrawTextW(hdc, titleText.c_str(), -1, &rcCol, DT_LEFT | DT_VCENTER | DT_SINGLELINE);

        // Separador vertical de columna
        MoveToEx(hdc, curX + c.width - 1, headerRect.top + 3, nullptr);
        LineTo(hdc, curX + c.width - 1, headerRect.bottom - 3);

        curX += c.width;
    }

    SelectObject(hdc, hOldPen);
    DeleteObject(hPenBorder);
}

void OutlinerWidget::RenderRow(HDC hdc, const RECT& rowRect, const NativeOutlinerItem& item, bool isSelected,
                               const escritorio::themes::ThemePalette& pal, HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody) {
    (void)isSelected;
    (void)hFontTitle;

    HPEN hPenBorder = CreatePen(PS_SOLID, 1, pal.toolbarBorder);
    HPEN hOldPen = static_cast<HPEN>(SelectObject(hdc, hPenBorder));

    // Línea separadora inferior de fila
    MoveToEx(hdc, rowRect.left, rowRect.bottom - 1, nullptr);
    LineTo(hdc, rowRect.right, rowRect.bottom - 1);

    int curX = rowRect.left;

    for (const auto& c : m_columns) {
        if (!c.visible) continue;

        RECT cellRect = { curX + 8, rowRect.top, curX + c.width - 8, rowRect.bottom };

        if (c.id == L"title_synopsis") {
            int indent = item.level * 18;
            RECT rTitle = { curX + 8 + indent, rowRect.top + 3, curX + c.width - 8, rowRect.top + 19 };
            RECT rSynop = { curX + 8 + indent, rowRect.top + 19, curX + c.width - 8, rowRect.bottom - 2 };

            // Flecha de jerarquía para carpetas
            std::wstring prefix = item.isFolder ? (item.expanded ? L"▼ " : L"▶ ") : L"• ";
            std::wstring titleDisplay = prefix + item.title;

            SelectObject(hdc, hFontBody);
            SetTextColor(hdc, pal.editorFg);
            DrawTextW(hdc, titleDisplay.c_str(), -1, &rTitle, DT_LEFT | DT_SINGLELINE | DT_END_ELLIPSIS);

            SelectObject(hdc, hFontSmall);
            SetTextColor(hdc, pal.binderSecondary);
            DrawTextW(hdc, item.synopsis.c_str(), -1, &rSynop, DT_LEFT | DT_SINGLELINE | DT_END_ELLIPSIS);

        } else if (c.id == L"label") {
            // Píldora de color de etiqueta
            RECT rPill = { curX + 8, rowRect.top + 8, curX + c.width - 12, rowRect.bottom - 8 };
            HBRUSH hBrLabel = CreateSolidBrush(item.labelColor);
            FillRect(hdc, &rPill, hBrLabel);
            DeleteObject(hBrLabel);

            SelectObject(hdc, hFontSmall);
            SetTextColor(hdc, RGB(255, 255, 255));
            DrawTextW(hdc, item.labelName.c_str(), -1, &rPill, DT_CENTER | DT_VCENTER | DT_SINGLELINE);

        } else if (c.id == L"status") {
            SelectObject(hdc, hFontSmall);
            SetTextColor(hdc, pal.editorFg);
            DrawTextW(hdc, item.statusName.c_str(), -1, &cellRect, DT_LEFT | DT_VCENTER | DT_SINGLELINE);

        } else if (c.id == L"section_type") {
            SelectObject(hdc, hFontSmall);
            SetTextColor(hdc, pal.editorFg);
            DrawTextW(hdc, item.sectionType.c_str(), -1, &cellRect, DT_LEFT | DT_VCENTER | DT_SINGLELINE);

        } else if (c.id == L"include_in_compile") {
            // Checkbox visual
            int chkX = curX + (c.width - 14) / 2;
            int chkY = rowRect.top + (m_rowHeight - 14) / 2;
            RECT rBox = { chkX, chkY, chkX + 14, chkY + 14 };

            HPEN hPenBox = CreatePen(PS_SOLID, 1, pal.toolbarBorder);
            SelectObject(hdc, hPenBox);
            Rectangle(hdc, rBox.left, rBox.top, rBox.right, rBox.bottom);
            DeleteObject(hPenBox);

            if (item.includeInCompile) {
                SetTextColor(hdc, pal.accentPrimary);
                DrawTextW(hdc, L"✓", -1, &rBox, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
            }

        } else if (c.id == L"words") {
            SelectObject(hdc, hFontSmall);
            SetTextColor(hdc, pal.editorFg);
            std::wstring strWords = std::to_wstring(item.words);
            DrawTextW(hdc, strWords.c_str(), -1, &cellRect, DT_RIGHT | DT_VCENTER | DT_SINGLELINE);

        } else if (c.id == L"total_words") {
            SelectObject(hdc, hFontSmall);
            SetTextColor(hdc, pal.editorFg);
            std::wstring strWords = std::to_wstring(item.totalWords);
            DrawTextW(hdc, strWords.c_str(), -1, &cellRect, DT_RIGHT | DT_VCENTER | DT_SINGLELINE);

        } else if (c.id == L"target") {
            SelectObject(hdc, hFontSmall);
            SetTextColor(hdc, pal.editorFg);
            std::wstring strTgt = std::to_wstring(item.target);
            DrawTextW(hdc, strTgt.c_str(), -1, &cellRect, DT_RIGHT | DT_VCENTER | DT_SINGLELINE);

        } else if (c.id == L"progress") {
            RECT barRect = { curX + 8, rowRect.top + 9, curX + c.width - 8, rowRect.bottom - 9 };
            RenderProgressBar(hdc, barRect, item.progressPercent, pal, hFontSmall);

        } else if (c.id == L"pov") {
            auto it = item.customMetadata.find(L"POV");
            const wchar_t* povText = (it != item.customMetadata.end()) ? it->second.c_str() : L"-";
            SelectObject(hdc, hFontSmall);
            SetTextColor(hdc, pal.editorFg);
            DrawTextW(hdc, povText, -1, &cellRect, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
        }

        // Separador vertical de columna
        MoveToEx(hdc, curX + c.width - 1, rowRect.top, nullptr);
        LineTo(hdc, curX + c.width - 1, rowRect.bottom);

        curX += c.width;
    }

    SelectObject(hdc, hOldPen);
    DeleteObject(hPenBorder);
}

void OutlinerWidget::RenderProgressBar(HDC hdc, const RECT& barRect, float percent, const escritorio::themes::ThemePalette& pal, HFONT hFontSmall) {
    // Fondo de la barra (track)
    HBRUSH hBrTrack = CreateSolidBrush(pal.toolbarBorder);
    FillRect(hdc, &barRect, hBrTrack);
    DeleteObject(hBrTrack);

    // Barra de relleno con gradiente dinámico
    int fillW = static_cast<int>((barRect.right - barRect.left) * (std::min)(100.0f, percent) / 100.0f);
    if (fillW > 0) {
        RECT rFill = { barRect.left, barRect.top, barRect.left + fillW, barRect.bottom };
        COLORREF barColor = CalculateProgressColor(percent);
        HBRUSH hBrFill = CreateSolidBrush(barColor);
        FillRect(hdc, &rFill, hBrFill);
        DeleteObject(hBrFill);
    }

    // Porcentaje textual centrado
    std::wstringstream ss;
    ss << std::fixed << std::setprecision(1) << percent << L"%";
    std::wstring pctStr = ss.str();

    SelectObject(hdc, hFontSmall);
    SetTextColor(hdc, RGB(255, 255, 255));
    SetBkMode(hdc, TRANSPARENT);
    RECT rText = barRect;
    DrawTextW(hdc, pctStr.c_str(), -1, &rText, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
}

void OutlinerWidget::RenderFooter(HDC hdc, const RECT& footerRect, const escritorio::themes::ThemePalette& pal, HFONT hFontSmall) {
    HBRUSH hBrFoot = CreateSolidBrush(pal.toolbarBg);
    FillRect(hdc, &footerRect, hBrFoot);
    DeleteObject(hBrFoot);

    HPEN hPenBorder = CreatePen(PS_SOLID, 1, pal.toolbarBorder);
    HPEN hOldPen = static_cast<HPEN>(SelectObject(hdc, hPenBorder));
    MoveToEx(hdc, footerRect.left, footerRect.top, nullptr);
    LineTo(hdc, footerRect.right, footerRect.top);

    SelectObject(hdc, hFontSmall);
    SetTextColor(hdc, pal.toolbarFg);
    SetBkMode(hdc, TRANSPARENT);

    // Texto de estado del esquema
    std::wstringstream ssLeft;
    ssLeft << L"Filas: " << m_items.size()
           << L" | Vista: " << (m_combinedTitleSynopsis ? L"Título & Sinopsis" : L"Separados")
           << L" | [ Exportar CSV ]";
    std::wstring strLeft = ssLeft.str();

    RECT rLeft = { footerRect.left + 16, footerRect.top, footerRect.left + 400, footerRect.bottom };
    DrawTextW(hdc, strLeft.c_str(), -1, &rLeft, DT_LEFT | DT_VCENTER | DT_SINGLELINE);

    std::wstring sortInfo = L"Ordenación: Binder Original";
    if (!m_sortColId.empty()) {
        sortInfo = L"Ordenación: " + m_sortColId + (m_sortDir == OutlinerSortDirection::Ascending ? L" (Asc)" : L" (Desc)");
    }
    RECT rRight = { footerRect.right - 350, footerRect.top, footerRect.right - 16, footerRect.bottom };
    SetTextColor(hdc, pal.accentPrimary);
    DrawTextW(hdc, sortInfo.c_str(), -1, &rRight, DT_RIGHT | DT_VCENTER | DT_SINGLELINE);

    SelectObject(hdc, hOldPen);
    DeleteObject(hPenBorder);
}

} // namespace escritorio::ui
