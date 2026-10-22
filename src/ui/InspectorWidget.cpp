#include "InspectorWidget.hpp"
#include <sstream>
#include <iomanip>
#include <ctime>
#include <algorithm>
#include <vector>

namespace escritorio::ui {

// Implementación ligera del algoritmo de Myers Diff a nivel de palabras para C++
static std::vector<std::wstring> TokenizeWords(const std::wstring& str) {
    std::vector<std::wstring> tokens;
    std::wstring current;
    for (wchar_t ch : str) {
        if (ch == L' ' || ch == L'\t' || ch == L'\n' || ch == L'\r' || ch == L',' || ch == L'.' || ch == L';') {
            if (!current.empty()) {
                tokens.push_back(current);
                current.clear();
            }
            std::wstring sep(1, ch);
            tokens.push_back(sep);
        } else {
            current.push_back(ch);
        }
    }
    if (!current.empty()) {
        tokens.push_back(current);
    }
    return tokens;
}

static std::vector<NativeDiffSpan> ComputeWordMyersDiff(const std::vector<std::wstring>& a, const std::vector<std::wstring>& b) {
    // Implementación Greedy LCS / Myers
    int n = static_cast<int>(a.size());
    int m = static_cast<int>(b.size());
    int maxD = n + m;
    int vOffset = maxD;
    std::vector<int> v(2 * maxD + 1, 0);
    std::vector<std::vector<int>> trace;

    for (int d = 0; d <= maxD; ++d) {
        trace.push_back(v);
        for (int k = -d; k <= d; k += 2) {
            int x = 0;
            if (k == -d || (k != d && v[k - 1 + vOffset] < v[k + 1 + vOffset])) {
                x = v[k + 1 + vOffset];
            } else {
                x = v[k - 1 + vOffset] + 1;
            }
            int y = x - k;
            while (x < n && y < m && a[x] == b[y]) {
                x++;
                y++;
            }
            v[k + vOffset] = x;
            if (x >= n && y >= m) {
                // Backtrack
                std::vector<NativeDiffSpan> diffs;
                int curX = n;
                int curY = m;
                for (int backD = static_cast<int>(trace.size()) - 1; backD > 0; --backD) {
                    const auto& prevV = trace[backD];
                    int curK = curX - curY;
                    int prevK = 0;
                    if (curK == -backD || (curK != backD && prevV[curK - 1 + vOffset] < prevV[curK + 1 + vOffset])) {
                        prevK = curK + 1;
                    } else {
                        prevK = curK - 1;
                    }
                    int prevX = prevV[prevK + vOffset];
                    int prevY = prevX - prevK;

                    while (curX > prevX && curY > prevY) {
                        diffs.push_back({ NativeDiffOp::Equal, a[curX - 1] });
                        curX--;
                        curY--;
                    }
                    if (curX > prevX) {
                        diffs.push_back({ NativeDiffOp::Delete, a[curX - 1] });
                        curX--;
                    } else if (curY > prevY) {
                        diffs.push_back({ NativeDiffOp::Insert, b[curY - 1] });
                        curY--;
                    }
                }
                while (curX > 0 && curY > 0) {
                    diffs.push_back({ NativeDiffOp::Equal, a[curX - 1] });
                    curX--;
                    curY--;
                }
                while (curX > 0) {
                    diffs.push_back({ NativeDiffOp::Delete, a[curX - 1] });
                    curX--;
                }
                while (curY > 0) {
                    diffs.push_back({ NativeDiffOp::Insert, b[curY - 1] });
                    curY--;
                }
                std::reverse(diffs.begin(), diffs.end());
                return diffs;
            }
        }
    }
    return { { NativeDiffOp::Equal, L"" } };
}

InspectorWidget::InspectorWidget() {
    m_synopsisText = L"Isabel llega a la ciudad vieja durante la medianoche lluviosa. Debe alcanzar el archivo sin ser detectada por los vigilantes de la plaza mayor.";
    m_notesRtf = L"{\\rtf1\\ansi Recordar contrastar la iluminación de gas con la oscuridad del callejón del archivo.}";

    // Semillas iniciales para Marcadores
    m_bookmarks.push_back({ L"bm-1", L"Mapa de la Ciudad Antigua", L"Research/Maps/ciudad_antigua.png", false, L"[Referencia visual: Muralla norte y túneles del acueducto]" });
    m_bookmarks.push_back({ L"bm-2", L"Reglas de la Orden de los Custodios", L"Docs/lore_custodios.rtf", true, L"1. Ningún custodio debe portar faroles tras el toque de queda.\n2. Todo manuscrito sellado debe guardarse en la cripta baja." });
    m_bookmarkPreviewText = m_bookmarks[0].previewContent;

    // Semillas de Metadatos
    m_customFields.push_back({ L"Punto de Vista (POV)", NativeCustomFieldType::Text, L"Isabel", {} });
    m_customFields.push_back({ L"Línea Temporal", NativeCustomFieldType::Date, L"1894-10-22 23:45", {} });
    m_customFields.push_back({ L"Conflicto Resuelto", NativeCustomFieldType::Checkbox, L"false", {} });
    m_customFields.push_back({ L"Estado de Tensión", NativeCustomFieldType::List, L"Alto", { L"Bajo", L"Medio", L"Alto", L"Clímax" } });

    // Semillas de Palabras Clave
    m_keywords.push_back({ L"Isabel", RGB(59, 130, 246) });
    m_keywords.push_back({ L"Noche", RGB(99, 102, 241) });
    m_keywords.push_back({ L"Tensión", RGB(239, 68, 68) });
    m_keywords.push_back({ L"Lluvia", RGB(16, 185, 129) });

    // Semilla de Instantánea previa
    m_snapshots.push_back({
        L"snap-001",
        L"Borrador Inicial",
        L"2026-10-22 14:15",
        L"La noche caía sobre las torres con una quietud espectral. Todo comenzaba aquí, en este preciso instante en que el reloj marcaba las doce campanadas. Las calles adoquinadas brillaban bajo una capa de lluvia recién caída."
    });

    // Semillas de Comentarios y Notas al Pie
    m_comments.push_back({
        L"comm-1",
        false,
        L"Verificar si en 1894 ya había farolas de gas en toda la plaza mayor.",
        L"Revisor Histórico",
        L"2026-10-22 15:30",
        RGB(254, 240, 138),
        185, 230
    });
    m_comments.push_back({
        L"fn-1",
        true,
        L"Nota al pie: La catedral data del siglo XIV y su reloj de carrillón fue añadido en 1782.",
        L"Autor",
        L"2026-10-22 16:00",
        RGB(191, 219, 254),
        120, 140
    });
}

void InspectorWidget::CycleTab() {
    int cur = static_cast<int>(m_activeTab);
    cur = (cur + 1) % 6;
    m_activeTab = static_cast<NativeInspectorTab>(cur);
}

void InspectorWidget::SetDocument(const std::wstring& uuid, const std::wstring& title) {
    m_docUuid = uuid;
    m_docTitle = title;
}

void InspectorWidget::SetLabel(int id, const std::wstring& name, COLORREF color) {
    m_labelId = id;
    m_labelName = name;
    m_labelColor = color;
}

void InspectorWidget::SetStatus(int id, const std::wstring& name) {
    m_statusId = id;
    m_statusName = name;
}

void InspectorWidget::AddBookmark(const NativeBookmarkItem& bm) {
    m_bookmarks.push_back(bm);
}

void InspectorWidget::SelectBookmark(int index) {
    if (index >= 0 && index < static_cast<int>(m_bookmarks.size())) {
        m_selectedBookmarkIdx = index;
        m_bookmarkPreviewText = m_bookmarks[index].previewContent;
    }
}

void InspectorWidget::SetBookmarkPreviewText(const std::wstring& text) {
    m_bookmarkPreviewText = text;
    if (m_selectedBookmarkIdx >= 0 && m_selectedBookmarkIdx < static_cast<int>(m_bookmarks.size())) {
        m_bookmarks[m_selectedBookmarkIdx].previewContent = text;
    }
}

void InspectorWidget::AddCustomField(const NativeCustomField& field) {
    m_customFields.push_back(field);
}

void InspectorWidget::AddKeyword(const std::wstring& kw, COLORREF color) {
    m_keywords.push_back({ kw, color });
}

void InspectorWidget::TakeSnapshot(const std::wstring& title) {
    std::wstring actualTitle = title.empty() ? (L"Instantánea " + std::to_wstring(m_snapshots.size() + 1)) : title;
    
    // Timestamp
    auto now = std::chrono::system_clock::now();
    std::time_t nowTime = std::chrono::system_clock::to_time_t(now);
    std::tm tmNow;
    localtime_s(&tmNow, &nowTime);
    wchar_t tsBuf[64];
    wcsftime(tsBuf, 64, L"%Y-%m-%d %H:%M:%S", &tmNow);

    NativeSnapshotItem snap;
    snap.uuid = L"snap-" + std::to_wstring(now.time_since_epoch().count());
    snap.title = actualTitle;
    snap.timestamp = tsBuf;
    snap.textContent = m_synopsisText; // Snapshot del contenido
    m_snapshots.insert(m_snapshots.begin(), snap);
    m_selectedSnapshotIdx = 0;
}

void InspectorWidget::SelectSnapshot(int index) {
    if (index >= 0 && index < static_cast<int>(m_snapshots.size())) {
        m_selectedSnapshotIdx = index;
    }
}

void InspectorWidget::ComputeMyersDiff(int snapshotIndex, const std::wstring& currentDocText) {
    if (snapshotIndex < 0 || snapshotIndex >= static_cast<int>(m_snapshots.size())) {
        m_diffSpans.clear();
        return;
    }
    const auto& snap = m_snapshots[snapshotIndex];
    auto wordsA = TokenizeWords(snap.textContent);
    auto wordsB = TokenizeWords(currentDocText);
    m_diffSpans = ComputeWordMyersDiff(wordsA, wordsB);
}

bool InspectorWidget::Rollback(int snapshotIndex, bool takeSafetySnapshot, std::wstring& outRestoredText) {
    if (snapshotIndex < 0 || snapshotIndex >= static_cast<int>(m_snapshots.size())) {
        return false;
    }
    if (takeSafetySnapshot) {
        TakeSnapshot(L"Seguridad Pre-Rollback");
        snapshotIndex++; // Ajustar índice ya que se insertó arriba
    }
    outRestoredText = m_snapshots[snapshotIndex].textContent;
    m_synopsisText = outRestoredText;
    return true;
}

void InspectorWidget::AddComment(const std::wstring& text, int startOffset, int endOffset, const std::wstring& author, COLORREF color) {
    NativeCommentItem item;
    item.id = L"comm-" + std::to_wstring(m_comments.size() + 1);
    item.isFootnote = false;
    item.text = text;
    item.author = author;
    item.timestamp = L"2026-10-22";
    item.color = color;
    item.startOffset = startOffset;
    item.endOffset = endOffset;
    m_comments.push_back(item);
}

void InspectorWidget::AddFootnote(const std::wstring& text, int startOffset, int endOffset) {
    NativeCommentItem item;
    item.id = L"fn-" + std::to_wstring(m_comments.size() + 1);
    item.isFootnote = true;
    item.text = text;
    item.author = L"Autor";
    item.timestamp = L"2026-10-22";
    item.color = RGB(191, 219, 254);
    item.startOffset = startOffset;
    item.endOffset = endOffset;
    m_comments.push_back(item);
}

int InspectorWidget::FindCommentAtOffset(int offset) const {
    for (size_t i = 0; i < m_comments.size(); ++i) {
        if (offset >= m_comments[i].startOffset && offset <= m_comments[i].endOffset) {
            return static_cast<int>(i);
        }
    }
    return -1;
}

bool InspectorWidget::HandleClick(int x, int y, const RECT& inspectorRect) {
    int w = inspectorRect.right - inspectorRect.left;
    if (x < inspectorRect.left || x > inspectorRect.right || y < inspectorRect.top || y > inspectorRect.bottom) {
        return false;
    }

    // Cabecera de iconos compactos de 16px (altura 32px en total)
    int headerHeight = 32;
    if (y >= inspectorRect.top && y < inspectorRect.top + headerHeight) {
        int tabBtnWidth = w / 6;
        int clickedTab = (x - inspectorRect.left) / (std::max)(1, tabBtnWidth);
        if (clickedTab >= 0 && clickedTab < 6) {
            m_activeTab = static_cast<NativeInspectorTab>(clickedTab);
            return true;
        }
    }

    // Pie fijo del Inspector (altura 50px)
    int footerHeight = 50;
    if (y >= inspectorRect.bottom - footerHeight && y <= inspectorRect.bottom) {
        // Clic en selectores rápidos de Label y Status
        int midX = inspectorRect.left + w / 2;
        if (x < midX) {
            // Alternar Label
            m_labelId = (m_labelId % 5) + 1;
            const wchar_t* names[] = { L"Capítulo 1", L"Punto de Giro", L"Secundario", L"Clímax", L"Revisión" };
            COLORREF cols[] = { RGB(59, 130, 246), RGB(239, 68, 68), RGB(16, 185, 129), RGB(245, 158, 11), RGB(168, 85, 247) };
            m_labelName = names[m_labelId - 1];
            m_labelColor = cols[m_labelId - 1];
        } else {
            // Alternar Status
            m_statusId = (m_statusId % 4) + 1;
            const wchar_t* stNames[] = { L"Por Empezar", L"Primer Borrador", L"Revisado", L"Listo" };
            m_statusName = stNames[m_statusId - 1];
        }
        return true;
    }

    // Clics específicos por pestaña
    int contentTop = inspectorRect.top + headerHeight;
    int contentBottom = inspectorRect.bottom - footerHeight;

    if (m_activeTab == NativeInspectorTab::NotesSynopsis) {
        // Botón conmutador Texto / Imagen en la parte superior de la tarjeta de sinopsis
        if (y >= contentTop + 4 && y <= contentTop + 24 && x >= inspectorRect.right - 90 && x <= inspectorRect.right - 10) {
            ToggleSynopsisMode();
            return true;
        }
    } else if (m_activeTab == NativeInspectorTab::Bookmarks) {
        // Conmutador Documento / Proyecto
        if (y >= contentTop + 6 && y <= contentTop + 28 && x >= inspectorRect.left + 10 && x <= inspectorRect.right - 10) {
            ToggleBookmarkScope();
            return true;
        }
        // Selección de marcador en lista
        int listTop = contentTop + 36;
        int listBottom = listTop + 90;
        if (y >= listTop && y < listBottom) {
            int idx = (y - listTop) / 24;
            if (idx >= 0 && idx < static_cast<int>(m_bookmarks.size())) {
                SelectBookmark(idx);
                return true;
            }
        }
    } else if (m_activeTab == NativeInspectorTab::Keywords) {
        // Botón HUD de Palabras Clave
        if (y >= contentTop + 6 && y <= contentTop + 28 && x >= inspectorRect.right - 110 && x <= inspectorRect.right - 10) {
            ToggleKeywordsHud();
            return true;
        }
    } else if (m_activeTab == NativeInspectorTab::Snapshots) {
        // Botones de Toma de Instantánea (Ctrl+5 / Ctrl+Shift+5)
        if (y >= contentTop + 6 && y <= contentTop + 28) {
            if (x >= inspectorRect.left + 10 && x <= inspectorRect.left + 100) {
                TakeSnapshot(); // Rápida
                return true;
            } else if (x > inspectorRect.left + 100 && x <= inspectorRect.left + 180) {
                TakeSnapshot(L"Instantánea Especial");
                return true;
            }
        }
        // Botón Comparar / Rollback
        if (y >= contentBottom - 30 && y <= contentBottom - 6) {
            if (x >= inspectorRect.left + 10 && x <= inspectorRect.left + 110) {
                ComputeMyersDiff(m_selectedSnapshotIdx, m_synopsisText);
                return true;
            } else if (x > inspectorRect.left + 110 && x <= inspectorRect.right - 10) {
                std::wstring restored;
                Rollback(m_selectedSnapshotIdx, true, restored);
                return true;
            }
        }
    } else if (m_activeTab == NativeInspectorTab::CommentsFootnotes) {
        int listTop = contentTop + 10;
        int itemH = 46;
        for (size_t i = 0; i < m_comments.size(); ++i) {
            int itemY = listTop + static_cast<int>(i) * itemH;
            if (y >= itemY && y < itemY + itemH) {
                m_selectedCommentIdx = static_cast<int>(i);
                return true;
            }
        }
    }

    return false;
}

void InspectorWidget::Render(HDC hdc, const RECT& area, const escritorio::themes::ThemePalette& pal,
                             const escritorio::themes::UIDensityMetrics& /*metrics*/,
                             HFONT hFontTitle, HFONT hFontSmall, HFONT hFontMicro, HFONT hFontBody) {
    // Fondo general del panel del Inspector
    HBRUSH hBrInspector = CreateSolidBrush(pal.inspectorBg);
    FillRect(hdc, &area, hBrInspector);
    DeleteObject(hBrInspector);

    // Borde izquierdo separador
    HPEN hPenBorder = CreatePen(PS_SOLID, 1, pal.windowBorder);
    HPEN hOldPen = (HPEN)SelectObject(hdc, hPenBorder);
    MoveToEx(hdc, area.left, area.top, nullptr);
    LineTo(hdc, area.left, area.bottom);

    // 1. Cabecera de iconos compactos de 16px
    int headerHeight = 32;
    RECT rcHeader = { area.left, area.top, area.right, area.top + headerHeight };
    RenderHeaderTabs(hdc, rcHeader, pal, hFontMicro);

    // 2. Pie fijo de Label y Status
    int footerHeight = 50;
    RECT rcFooter = { area.left, area.bottom - footerHeight, area.right, area.bottom };

    // 3. Área de contenido de la pestaña activa
    RECT rcContent = { area.left, area.top + headerHeight, area.right, area.bottom - footerHeight };

    switch (m_activeTab) {
    case NativeInspectorTab::NotesSynopsis:
        RenderTabNotesSynopsis(hdc, rcContent, pal, hFontTitle, hFontSmall, hFontBody);
        break;
    case NativeInspectorTab::Bookmarks:
        RenderTabBookmarks(hdc, rcContent, pal, hFontTitle, hFontSmall, hFontBody);
        break;
    case NativeInspectorTab::Metadata:
        RenderTabMetadata(hdc, rcContent, pal, hFontTitle, hFontSmall, hFontBody);
        break;
    case NativeInspectorTab::Keywords:
        RenderTabKeywords(hdc, rcContent, pal, hFontTitle, hFontSmall, hFontBody);
        break;
    case NativeInspectorTab::Snapshots:
        RenderTabSnapshots(hdc, rcContent, pal, hFontTitle, hFontSmall, hFontBody);
        break;
    case NativeInspectorTab::CommentsFootnotes:
        RenderTabComments(hdc, rcContent, pal, hFontTitle, hFontSmall, hFontBody);
        break;
    }

    // Renderizar pie fijo
    RenderFooter(hdc, rcFooter, pal, hFontSmall, hFontMicro);

    SelectObject(hdc, hOldPen);
    DeleteObject(hPenBorder);
}

void InspectorWidget::RenderHeaderTabs(HDC hdc, const RECT& headerRect, const escritorio::themes::ThemePalette& pal, HFONT hFontMicro) {
    HBRUSH hBrHeader = CreateSolidBrush(pal.editorHeaderBg);
    FillRect(hdc, &headerRect, hBrHeader);
    DeleteObject(hBrHeader);

    // Línea separadora inferior de la cabecera
    HPEN hPen = CreatePen(PS_SOLID, 1, pal.windowBorder);
    SelectObject(hdc, hPen);
    MoveToEx(hdc, headerRect.left, headerRect.bottom - 1, nullptr);
    LineTo(hdc, headerRect.right, headerRect.bottom - 1);
    DeleteObject(hPen);

    // 6 pestañas de iconos compactos de 16px
    const wchar_t* tabGlyphs[] = { L"📝", L"🔖", L"⚙", L"🏷", L"📷", L"💬" };
    const wchar_t* tabNames[] = { L"Notas", L"Marc", L"Meta", L"Claves", L"Fotos", L"Coms" };

    int totalW = headerRect.right - headerRect.left;
    int tabW = totalW / 6;

    SelectObject(hdc, hFontMicro);
    SetBkMode(hdc, TRANSPARENT);

    for (int i = 0; i < 6; ++i) {
        int tabLeft = headerRect.left + i * tabW;
        int tabRight = (i == 5) ? headerRect.right : (tabLeft + tabW);
        RECT rcTab = { tabLeft, headerRect.top, tabRight, headerRect.bottom - 1 };

        bool isActive = (static_cast<int>(m_activeTab) == i);
        if (isActive) {
            HBRUSH hBrActive = CreateSolidBrush(pal.inspectorBg);
            FillRect(hdc, &rcTab, hBrActive);
            DeleteObject(hBrActive);

            // Borde superior de acento activo
            HPEN hPenAccent = CreatePen(PS_SOLID, 2, pal.accentPrimary);
            SelectObject(hdc, hPenAccent);
            MoveToEx(hdc, tabLeft, headerRect.top, nullptr);
            LineTo(hdc, tabRight, headerRect.top);
            DeleteObject(hPenAccent);

            SetTextColor(hdc, pal.accentPrimary);
        } else {
            SetTextColor(hdc, pal.statusBarFg);
        }

        std::wstring label = std::wstring(tabGlyphs[i]) + L" " + tabNames[i];
        DrawTextW(hdc, label.c_str(), -1, &rcTab, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
    }
}

void InspectorWidget::RenderFooter(HDC hdc, const RECT& footerRect, const escritorio::themes::ThemePalette& pal, HFONT hFontSmall, HFONT hFontMicro) {
    HBRUSH hBr = CreateSolidBrush(pal.editorHeaderBg);
    FillRect(hdc, &footerRect, hBr);
    DeleteObject(hBr);

    HPEN hPen = CreatePen(PS_SOLID, 1, pal.windowBorder);
    SelectObject(hdc, hPen);
    MoveToEx(hdc, footerRect.left, footerRect.top, nullptr);
    LineTo(hdc, footerRect.right, footerRect.top);
    DeleteObject(hPen);

    int midX = footerRect.left + (footerRect.right - footerRect.left) / 2;

    // Selector 1: Label (Etiqueta)
    RECT rcLabelTitle = { footerRect.left + 10, footerRect.top + 6, midX - 6, footerRect.top + 20 };
    SelectObject(hdc, hFontMicro);
    SetTextColor(hdc, pal.statusBarFg);
    DrawTextW(hdc, L"ETIQUETA (LABEL):", -1, &rcLabelTitle, DT_LEFT | DT_SINGLELINE);

    RECT rcLabelVal = { footerRect.left + 24, footerRect.top + 22, midX - 6, footerRect.bottom - 6 };
    SelectObject(hdc, hFontSmall);
    SetTextColor(hdc, pal.windowFg);
    DrawTextW(hdc, m_labelName.c_str(), -1, &rcLabelVal, DT_LEFT | DT_SINGLELINE);

    // Círculo de color de Etiqueta
    HBRUSH hBrDot = CreateSolidBrush(m_labelColor);
    HBRUSH hOldBr = (HBRUSH)SelectObject(hdc, hBrDot);
    HPEN hNullPen = (HPEN)GetStockObject(NULL_PEN);
    SelectObject(hdc, hNullPen);
    Ellipse(hdc, footerRect.left + 10, footerRect.top + 25, footerRect.left + 20, footerRect.top + 35);
    SelectObject(hdc, hOldBr);
    DeleteObject(hBrDot);

    // Divisor vertical sutil
    HPEN hDivPen = CreatePen(PS_SOLID, 1, pal.windowBorder);
    SelectObject(hdc, hDivPen);
    MoveToEx(hdc, midX, footerRect.top + 4, nullptr);
    LineTo(hdc, midX, footerRect.bottom - 4);
    DeleteObject(hDivPen);

    // Selector 2: Status (Estado)
    RECT rcStatusTitle = { midX + 10, footerRect.top + 6, footerRect.right - 10, footerRect.top + 20 };
    SelectObject(hdc, hFontMicro);
    SetTextColor(hdc, pal.statusBarFg);
    DrawTextW(hdc, L"ESTADO (STATUS):", -1, &rcStatusTitle, DT_LEFT | DT_SINGLELINE);

    RECT rcStatusVal = { midX + 10, footerRect.top + 22, footerRect.right - 10, footerRect.bottom - 6 };
    SelectObject(hdc, hFontSmall);
    SetTextColor(hdc, pal.windowFg);
    DrawTextW(hdc, m_statusName.c_str(), -1, &rcStatusVal, DT_LEFT | DT_SINGLELINE);
}

void InspectorWidget::RenderTabNotesSynopsis(HDC hdc, const RECT& tabArea, const escritorio::themes::ThemePalette& pal, HFONT /*hFontTitle*/, HFONT hFontSmall, HFONT hFontBody) {
    int totalH = tabArea.bottom - tabArea.top;
    int synopsisH = (totalH * 40) / 100; // 40% superior: Sinopsis

    // 1. Tarjeta de Sinopsis (sincronizada con Corkboard)
    RECT rcCard = { tabArea.left + 10, tabArea.top + 8, tabArea.right - 10, tabArea.top + synopsisH };
    HBRUSH hBrCard = CreateSolidBrush(pal.corkboardCardBg);
    FillRect(hdc, &rcCard, hBrCard);
    DeleteObject(hBrCard);

    HPEN hPenCard = CreatePen(PS_SOLID, 1, pal.corkboardCardBorder);
    SelectObject(hdc, hPenCard);
    Rectangle(hdc, rcCard.left, rcCard.top, rcCard.right, rcCard.bottom);
    DeleteObject(hPenCard);

    // Barra de cabecera de la tarjeta
    RECT rcCardHeader = { rcCard.left + 8, rcCard.top + 6, rcCard.right - 80, rcCard.top + 22 };
    SelectObject(hdc, hFontSmall);
    SetTextColor(hdc, pal.accentPrimary);
    DrawTextW(hdc, L"SINOPSIS DE ESCENA", -1, &rcCardHeader, DT_LEFT | DT_SINGLELINE);

    // Botón de alternancia Texto / Imagen
    RECT rcModeBtn = { rcCard.right - 78, rcCard.top + 4, rcCard.right - 6, rcCard.top + 22 };
    HBRUSH hBrBtn = CreateSolidBrush(pal.editorHeaderBg);
    FillRect(hdc, &rcModeBtn, hBrBtn);
    DeleteObject(hBrBtn);
    SetTextColor(hdc, pal.windowFg);
    const wchar_t* modeBtnText = m_synopsisImageMode ? L"🖼 Imagen" : L"📄 Texto";
    DrawTextW(hdc, modeBtnText, -1, &rcModeBtn, DT_CENTER | DT_VCENTER | DT_SINGLELINE);

    RECT rcCardBody = { rcCard.left + 10, rcCard.top + 26, rcCard.right - 10, rcCard.bottom - 6 };
    if (m_synopsisImageMode) {
        SetTextColor(hdc, pal.statusBarFg);
        DrawTextW(hdc, L"[Modo Imagen de Escena]\nArrastra y suelta una imagen aquí (JPEG, PNG, WebP) o sincroniza desde Research.", -1, &rcCardBody, DT_CENTER | DT_VCENTER | DT_WORDBREAK);
    } else {
        SelectObject(hdc, hFontSmall);
        SetTextColor(hdc, pal.corkboardCardFg);
        DrawTextW(hdc, m_synopsisText.c_str(), -1, &rcCardBody, DT_LEFT | DT_WORDBREAK);
    }

    // 2. Editor RTF de Notas del Documento (notes.rtf)
    RECT rcNotesHeader = { tabArea.left + 10, tabArea.top + synopsisH + 10, tabArea.right - 10, tabArea.top + synopsisH + 28 };
    SelectObject(hdc, hFontSmall);
    SetTextColor(hdc, pal.accentPrimary);
    DrawTextW(hdc, L"NOTAS DEL DOCUMENTO (notes.rtf)", -1, &rcNotesHeader, DT_LEFT | DT_SINGLELINE);

    RECT rcNotesBody = { tabArea.left + 10, tabArea.top + synopsisH + 30, tabArea.right - 10, tabArea.bottom - 8 };
    HBRUSH hBrNotes = CreateSolidBrush(pal.editorBg);
    FillRect(hdc, &rcNotesBody, hBrNotes);
    DeleteObject(hBrNotes);

    HPEN hPenNotes = CreatePen(PS_SOLID, 1, pal.windowBorder);
    SelectObject(hdc, hPenNotes);
    Rectangle(hdc, rcNotesBody.left, rcNotesBody.top, rcNotesBody.right, rcNotesBody.bottom);
    DeleteObject(hPenNotes);

    RECT rcNotesText = { rcNotesBody.left + 8, rcNotesBody.top + 8, rcNotesBody.right - 8, rcNotesBody.bottom - 8 };
    SelectObject(hdc, hFontBody);
    SetTextColor(hdc, pal.editorFg);
    const wchar_t* sampleNotes =
        L"Ideas y recordatorios para esta escena:\n"
        L"- Destacar el olor a humedad y humo de carbón en la niebla.\n"
        L"- Isabel duda antes de cruzar el umbral del archivo secreto.\n"
        L"- Conexión con la pista encontrada en el capítulo 4.";
    DrawTextW(hdc, sampleNotes, -1, &rcNotesText, DT_LEFT | DT_WORDBREAK);
}

void InspectorWidget::RenderTabBookmarks(HDC hdc, const RECT& tabArea, const escritorio::themes::ThemePalette& pal, HFONT /*hFontTitle*/, HFONT hFontSmall, HFONT hFontBody) {
    int totalH = tabArea.bottom - tabArea.top;
    int listH = (totalH * 45) / 100;

    // Selector de alcance: Documento vs Proyecto
    RECT rcScope = { tabArea.left + 10, tabArea.top + 6, tabArea.right - 10, tabArea.top + 28 };
    HBRUSH hBrScope = CreateSolidBrush(pal.editorHeaderBg);
    FillRect(hdc, &rcScope, hBrScope);
    DeleteObject(hBrScope);

    SelectObject(hdc, hFontSmall);
    SetTextColor(hdc, pal.accentPrimary);
    std::wstring scopeStr = m_bookmarkProjectScope ? L"🌐 MARCADORES DEL PROYECTO" : L"📄 MARCADORES DEL DOCUMENTO";
    DrawTextW(hdc, scopeStr.c_str(), -1, &rcScope, DT_CENTER | DT_VCENTER | DT_SINGLELINE);

    // Lista de marcadores
    RECT rcList = { tabArea.left + 10, tabArea.top + 34, tabArea.right - 10, tabArea.top + listH };
    for (size_t i = 0; i < m_bookmarks.size(); ++i) {
        int itemY = rcList.top + static_cast<int>(i) * 24;
        RECT rcItem = { rcList.left, itemY, rcList.right, itemY + 22 };

        if (static_cast<int>(i) == m_selectedBookmarkIdx) {
            HBRUSH hBrSel = CreateSolidBrush(pal.accentSecondary);
            FillRect(hdc, &rcItem, hBrSel);
            DeleteObject(hBrSel);
        }

        std::wstring line = std::wstring(L"🔖 ") + m_bookmarks[i].title;
        SetTextColor(hdc, pal.windowFg);
        DrawTextW(hdc, line.c_str(), -1, &rcItem, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
    }

    // Visor previsualizador y editor de referencia inferior
    RECT rcPrevHeader = { tabArea.left + 10, tabArea.top + listH + 8, tabArea.right - 10, tabArea.top + listH + 26 };
    SetTextColor(hdc, pal.accentPrimary);
    DrawTextW(hdc, L"VISOR DE REFERENCIA INTEGRADO", -1, &rcPrevHeader, DT_LEFT | DT_SINGLELINE);

    RECT rcPrevBox = { tabArea.left + 10, tabArea.top + listH + 28, tabArea.right - 10, tabArea.bottom - 8 };
    HBRUSH hBrBox = CreateSolidBrush(pal.editorBg);
    FillRect(hdc, &rcPrevBox, hBrBox);
    DeleteObject(hBrBox);

    HPEN hPen = CreatePen(PS_SOLID, 1, pal.windowBorder);
    SelectObject(hdc, hPen);
    Rectangle(hdc, rcPrevBox.left, rcPrevBox.top, rcPrevBox.right, rcPrevBox.bottom);
    DeleteObject(hPen);

    RECT rcPrevText = { rcPrevBox.left + 8, rcPrevBox.top + 8, rcPrevBox.right - 8, rcPrevBox.bottom - 8 };
    SelectObject(hdc, hFontBody);
    SetTextColor(hdc, pal.editorFg);
    DrawTextW(hdc, m_bookmarkPreviewText.c_str(), -1, &rcPrevText, DT_LEFT | DT_WORDBREAK);
}

void InspectorWidget::RenderTabMetadata(HDC hdc, const RECT& tabArea, const escritorio::themes::ThemePalette& pal, HFONT /*hFontTitle*/, HFONT hFontSmall, HFONT /*hFontBody*/) {
    // 1. Configuración General
    RECT rcGenTitle = { tabArea.left + 10, tabArea.top + 8, tabArea.right - 10, tabArea.top + 26 };
    SelectObject(hdc, hFontSmall);
    SetTextColor(hdc, pal.accentPrimary);
    DrawTextW(hdc, L"CONFIGURACIÓN GENERAL", -1, &rcGenTitle, DT_LEFT | DT_SINGLELINE);

    RECT rcComp = { tabArea.left + 14, tabArea.top + 30, tabArea.right - 14, tabArea.top + 50 };
    SetTextColor(hdc, pal.windowFg);
    std::wstring compText = m_includeInCompile ? L"☑ Incluir en Compilación" : L"☐ Excluir de Compilación";
    DrawTextW(hdc, compText.c_str(), -1, &rcComp, DT_LEFT | DT_SINGLELINE);

    RECT rcSec = { tabArea.left + 14, tabArea.top + 54, tabArea.right - 14, tabArea.top + 74 };
    std::wstring secText = L"Tipo de Sección: " + m_sectionType;
    DrawTextW(hdc, secText.c_str(), -1, &rcSec, DT_LEFT | DT_SINGLELINE);

    // 2. Metadatos Personalizados (Custom Metadata)
    RECT rcCustomTitle = { tabArea.left + 10, tabArea.top + 86, tabArea.right - 10, tabArea.top + 104 };
    SetTextColor(hdc, pal.accentPrimary);
    DrawTextW(hdc, L"METADATOS PERSONALIZADOS", -1, &rcCustomTitle, DT_LEFT | DT_SINGLELINE);

    int curY = tabArea.top + 110;
    for (const auto& field : m_customFields) {
        RECT rcFieldLabel = { tabArea.left + 14, curY, tabArea.left + 140, curY + 20 };
        SetTextColor(hdc, pal.statusBarFg);
        DrawTextW(hdc, field.name.c_str(), -1, &rcFieldLabel, DT_LEFT | DT_SINGLELINE);

        RECT rcFieldVal = { tabArea.left + 145, curY, tabArea.right - 14, curY + 20 };
        SetTextColor(hdc, pal.windowFg);
        DrawTextW(hdc, field.value.c_str(), -1, &rcFieldVal, DT_LEFT | DT_SINGLELINE);

        curY += 24;
    }
}

void InspectorWidget::RenderTabKeywords(HDC hdc, const RECT& tabArea, const escritorio::themes::ThemePalette& pal, HFONT /*hFontTitle*/, HFONT hFontSmall, HFONT /*hFontBody*/) {
    RECT rcTitle = { tabArea.left + 10, tabArea.top + 8, tabArea.right - 120, tabArea.top + 28 };
    SelectObject(hdc, hFontSmall);
    SetTextColor(hdc, pal.accentPrimary);
    DrawTextW(hdc, L"PALABRAS CLAVE (KEYWORDS)", -1, &rcTitle, DT_LEFT | DT_SINGLELINE);

    RECT rcHudBtn = { tabArea.right - 110, tabArea.top + 6, tabArea.right - 10, tabArea.top + 28 };
    HBRUSH hBrBtn = CreateSolidBrush(pal.editorHeaderBg);
    FillRect(hdc, &rcHudBtn, hBrBtn);
    DeleteObject(hBrBtn);
    SetTextColor(hdc, pal.windowFg);
    DrawTextW(hdc, L"🏷 Abrir HUD", -1, &rcHudBtn, DT_CENTER | DT_VCENTER | DT_SINGLELINE);

    // Chips de palabras clave con colores asignados
    int curX = tabArea.left + 14;
    int curY = tabArea.top + 40;
    for (const auto& kw : m_keywords) {
        int chipW = static_cast<int>(kw.first.length()) * 8 + 30;
        if (curX + chipW > tabArea.right - 14) {
            curX = tabArea.left + 14;
            curY += 28;
        }

        RECT rcChip = { curX, curY, curX + chipW, curY + 22 };
        HBRUSH hBrChip = CreateSolidBrush(pal.editorHeaderBg);
        FillRect(hdc, &rcChip, hBrChip);
        DeleteObject(hBrChip);

        // Indicador de color
        HBRUSH hBrDot = CreateSolidBrush(kw.second);
        RECT rcDot = { curX + 4, curY + 4, curX + 14, curY + 18 };
        FillRect(hdc, &rcDot, hBrDot);
        DeleteObject(hBrDot);

        RECT rcText = { curX + 18, curY, curX + chipW - 4, curY + 22 };
        SetTextColor(hdc, pal.windowFg);
        DrawTextW(hdc, kw.first.c_str(), -1, &rcText, DT_LEFT | DT_VCENTER | DT_SINGLELINE);

        curX += chipW + 8;
    }
}

void InspectorWidget::RenderTabSnapshots(HDC hdc, const RECT& tabArea, const escritorio::themes::ThemePalette& pal, HFONT /*hFontTitle*/, HFONT hFontSmall, HFONT /*hFontBody*/) {
    // Botones de acción rápida: Snapshot / Titled Snapshot
    RECT rcBtnSnap = { tabArea.left + 10, tabArea.top + 6, tabArea.left + 95, tabArea.top + 26 };
    HBRUSH hBrSnap = CreateSolidBrush(pal.editorHeaderBg);
    FillRect(hdc, &rcBtnSnap, hBrSnap);
    DeleteObject(hBrSnap);
    SelectObject(hdc, hFontSmall);
    SetTextColor(hdc, pal.windowFg);
    DrawTextW(hdc, L"+ Foto (Ctrl+5)", -1, &rcBtnSnap, DT_CENTER | DT_VCENTER | DT_SINGLELINE);

    RECT rcBtnTitle = { tabArea.left + 105, tabArea.top + 6, tabArea.left + 210, tabArea.top + 26 };
    HBRUSH hBrTitle = CreateSolidBrush(pal.editorHeaderBg);
    FillRect(hdc, &rcBtnTitle, hBrTitle);
    DeleteObject(hBrTitle);
    DrawTextW(hdc, L"+ Con Título", -1, &rcBtnTitle, DT_CENTER | DT_VCENTER | DT_SINGLELINE);

    // Lista de Snapshots
    int listTop = tabArea.top + 34;
    int listBottom = listTop + 90;
    for (size_t i = 0; i < m_snapshots.size(); ++i) {
        int itemY = listTop + static_cast<int>(i) * 26;
        RECT rcItem = { tabArea.left + 10, itemY, tabArea.right - 10, itemY + 24 };

        if (static_cast<int>(i) == m_selectedSnapshotIdx) {
            HBRUSH hBrSel = CreateSolidBrush(pal.accentSecondary);
            FillRect(hdc, &rcItem, hBrSel);
            DeleteObject(hBrSel);
        }

        std::wstring line = L"📷 " + m_snapshots[i].title + L" (" + m_snapshots[i].timestamp + L")";
        SetTextColor(hdc, pal.windowFg);
        DrawTextW(hdc, line.c_str(), -1, &rcItem, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
    }

    // Comparador Myers Diff inferior
    RECT rcDiffHeader = { tabArea.left + 10, listBottom + 10, tabArea.right - 10, listBottom + 28 };
    SetTextColor(hdc, pal.accentPrimary);
    DrawTextW(hdc, L"COMPARACIÓN DIFERENCIAL (MYERS DIFF)", -1, &rcDiffHeader, DT_LEFT | DT_SINGLELINE);

    RECT rcDiffBox = { tabArea.left + 10, listBottom + 30, tabArea.right - 10, tabArea.bottom - 36 };
    HBRUSH hBrBox = CreateSolidBrush(pal.editorBg);
    FillRect(hdc, &rcDiffBox, hBrBox);
    DeleteObject(hBrBox);

    HPEN hPen = CreatePen(PS_SOLID, 1, pal.windowBorder);
    SelectObject(hdc, hPen);
    Rectangle(hdc, rcDiffBox.left, rcDiffBox.top, rcDiffBox.right, rcDiffBox.bottom);
    DeleteObject(hPen);

    RECT rcDiffText = { rcDiffBox.left + 8, rcDiffBox.top + 8, rcDiffBox.right - 8, rcDiffBox.bottom - 8 };
    SelectObject(hdc, hFontSmall);

    if (m_diffSpans.empty()) {
        SetTextColor(hdc, pal.statusBarFg);
        DrawTextW(hdc, L"Haz clic en 'Comparar' para visualizar adiciones (subrayadas en verde) y eliminaciones (tachadas en rojo).", -1, &rcDiffText, DT_LEFT | DT_WORDBREAK);
    } else {
        // Renderizar spans con colores
        std::wstring diffDisplay;
        for (const auto& span : m_diffSpans) {
            if (span.op == NativeDiffOp::Delete) {
                diffDisplay += L"[-" + span.text + L"-] ";
            } else if (span.op == NativeDiffOp::Insert) {
                diffDisplay += L"[+" + span.text + L"+] ";
            } else {
                diffDisplay += span.text + L" ";
            }
        }
        SetTextColor(hdc, pal.editorFg);
        DrawTextW(hdc, diffDisplay.c_str(), -1, &rcDiffText, DT_LEFT | DT_WORDBREAK);
    }

    // Botones de Comparar y Rollback al pie
    RECT rcBtnComp = { tabArea.left + 10, tabArea.bottom - 30, tabArea.left + 100, tabArea.bottom - 8 };
    HBRUSH hBrComp = CreateSolidBrush(pal.editorHeaderBg);
    FillRect(hdc, &rcBtnComp, hBrComp);
    DeleteObject(hBrComp);
    SetTextColor(hdc, pal.windowFg);
    DrawTextW(hdc, L"Comparar", -1, &rcBtnComp, DT_CENTER | DT_VCENTER | DT_SINGLELINE);

    RECT rcBtnRoll = { tabArea.left + 110, tabArea.bottom - 30, tabArea.right - 10, tabArea.bottom - 8 };
    HBRUSH hBrRoll = CreateSolidBrush(pal.editorHeaderBg);
    FillRect(hdc, &rcBtnRoll, hBrRoll);
    DeleteObject(hBrRoll);
    SetTextColor(hdc, RGB(239, 68, 68)); // Rojo sutil de alerta
    DrawTextW(hdc, L"Restaurar Versión (Rollback)", -1, &rcBtnRoll, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
}

void InspectorWidget::RenderTabComments(HDC hdc, const RECT& tabArea, const escritorio::themes::ThemePalette& pal, HFONT /*hFontTitle*/, HFONT hFontSmall, HFONT /*hFontBody*/) {
    RECT rcTitle = { tabArea.left + 10, tabArea.top + 8, tabArea.right - 10, tabArea.top + 28 };
    SelectObject(hdc, hFontSmall);
    SetTextColor(hdc, pal.accentPrimary);
    DrawTextW(hdc, L"COMENTARIOS Y NOTAS AL PIE", -1, &rcTitle, DT_LEFT | DT_SINGLELINE);

    int curY = tabArea.top + 34;
    for (size_t i = 0; i < m_comments.size(); ++i) {
        const auto& c = m_comments[i];
        RECT rcCard = { tabArea.left + 10, curY, tabArea.right - 10, curY + 54 };

        HBRUSH hBrCard = CreateSolidBrush(pal.editorHeaderBg);
        FillRect(hdc, &rcCard, hBrCard);
        DeleteObject(hBrCard);

        // Barra lateral coloreada
        HBRUSH hBrBar = CreateSolidBrush(c.color);
        RECT rcBar = { rcCard.left, rcCard.top, rcCard.left + 4, rcCard.bottom };
        FillRect(hdc, &rcBar, hBrBar);
        DeleteObject(hBrBar);

        // Cabecera: Autor y tipo
        RECT rcAuthor = { rcCard.left + 10, rcCard.top + 4, rcCard.right - 10, rcCard.top + 18 };
        SelectObject(hdc, hFontSmall);
        SetTextColor(hdc, pal.accentPrimary);
        std::wstring headerStr = (c.isFootnote ? L"Nota al pie [" : L"Comentario [") + c.author + L"]";
        DrawTextW(hdc, headerStr.c_str(), -1, &rcAuthor, DT_LEFT | DT_SINGLELINE);

        // Texto
        RECT rcText = { rcCard.left + 10, rcCard.top + 20, rcCard.right - 10, rcCard.bottom - 4 };
        SetTextColor(hdc, pal.windowFg);
        DrawTextW(hdc, c.text.c_str(), -1, &rcText, DT_LEFT | DT_WORDBREAK);

        curY += 60;
    }
}

} // namespace escritorio::ui
