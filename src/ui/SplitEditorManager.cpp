#include "SplitEditorManager.hpp"
#include <algorithm>

namespace escritorio::ui {

SplitEditorManager::SplitEditorManager() {
    for (int i = 0; i < 4; ++i) {
        auto p = std::make_unique<NativeEditorPane>();
        p->id = L"pane_" + std::to_wstring(i);
        p->editor = std::make_unique<EditorWidget>();
        m_panes.push_back(std::move(p));
    }
}

void SplitEditorManager::SplitVertical() {
    m_mode = NativeSplitMode::Vertical;
}

void SplitEditorManager::SplitHorizontal() {
    m_mode = NativeSplitMode::Horizontal;
}

void SplitEditorManager::SplitGrid() {
    m_mode = NativeSplitMode::Grid4;
}

void SplitEditorManager::CloseSplit() {
    m_mode = NativeSplitMode::Single;
    m_activePaneId = L"pane_0";
}

void SplitEditorManager::SetActivePane(const std::wstring& id) {
    for (const auto& p : m_panes) {
        if (p->id == id) {
            m_activePaneId = id;
            break;
        }
    }
}

NativeEditorPane* SplitEditorManager::GetPane(const std::wstring& id) {
    for (const auto& p : m_panes) {
        if (p->id == id) {
            return p.get();
        }
    }
    return nullptr;
}

NativeEditorPane* SplitEditorManager::GetActivePane() {
    auto* p = GetPane(m_activePaneId);
    return p ? p : m_panes[0].get();
}

bool SplitEditorManager::ToggleLockActivePane() {
    auto* p = GetActivePane();
    return p ? p->ToggleLock() : false;
}

bool SplitEditorManager::IsActiveLocked() const {
    for (const auto& p : m_panes) {
        if (p->id == m_activePaneId) {
            return p->isLocked;
        }
    }
    return false;
}

bool SplitEditorManager::ToggleNavigateAffectsOther() {
    auto* p = GetActivePane();
    return p ? p->ToggleNavigateAffectsOther() : false;
}

std::vector<NativeEditorPane*> SplitEditorManager::GetVisiblePanes() {
    std::vector<NativeEditorPane*> res;
    if (m_mode == NativeSplitMode::Single) {
        res.push_back(m_panes[0].get());
    } else if (m_mode == NativeSplitMode::Vertical || m_mode == NativeSplitMode::Horizontal) {
        res.push_back(m_panes[0].get());
        res.push_back(m_panes[1].get());
    } else if (m_mode == NativeSplitMode::Grid4) {
        for (int i = 0; i < 4; ++i) {
            res.push_back(m_panes[i].get());
        }
    }
    return res;
}

NativeEditorPane* SplitEditorManager::GetOtherPane(NativeEditorPane* source) {
    auto visible = GetVisiblePanes();
    if (visible.size() <= 1) return nullptr;

    if (visible.size() == 2) {
        return (source == visible[0]) ? visible[1] : visible[0];
    }

    for (auto* p : visible) {
        if (p != source && !p->isLocked) {
            return p;
        }
    }
    for (auto* p : visible) {
        if (p != source) return p;
    }
    return nullptr;
}

NativeEditorPane* SplitEditorManager::RouteBinderItem(const std::wstring& uuid, const std::wstring& title, const std::wstring& text) {
    auto* active = GetActivePane();
    if (!active) return nullptr;

    // 1. Si navegación afecta al otro editor
    if (active->navigateAffectsOther) {
        auto* other = GetOtherPane(active);
        if (other && !other->isLocked) {
            other->docUuid = uuid;
            other->docTitle = title;
            other->editor->SetItemUuid(uuid, title);
            other->editor->SetPlainText(text);
            return other;
        }
    }

    // 2. Si el panel activo no está bloqueado
    if (!active->isLocked) {
        active->docUuid = uuid;
        active->docTitle = title;
        active->editor->SetItemUuid(uuid, title);
        active->editor->SetPlainText(text);
        return active;
    }

    // 3. Panel activo bloqueado: buscar el primer panel no bloqueado visible
    auto visible = GetVisiblePanes();
    for (auto* p : visible) {
        if (!p->isLocked) {
            p->docUuid = uuid;
            p->docTitle = title;
            p->editor->SetItemUuid(uuid, title);
            p->editor->SetPlainText(text);
            m_activePaneId = p->id;
            return p;
        }
    }

    // Todos los paneles visibles están bloqueados: no sobreescribir
    return nullptr;
}

void SplitEditorManager::Render(HDC hdc, const RECT& area, const escritorio::themes::ThemePalette& pal,
                                const escritorio::themes::UIDensityMetrics& metrics, HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody) {
    int w = area.right - area.left;
    int h = area.bottom - area.top;
    if (w <= 0 || h <= 0) return;
    (void)hFontTitle;

    auto visible = GetVisiblePanes();
    std::vector<RECT> rects;

    if (m_mode == NativeSplitMode::Single) {
        rects.push_back(area);
    } else if (m_mode == NativeSplitMode::Vertical) {
        int mid = area.left + w / 2;
        RECT r1 = { area.left, area.top, mid - 1, area.bottom };
        RECT r2 = { mid + 1, area.top, area.right, area.bottom };
        rects.push_back(r1);
        rects.push_back(r2);
    } else if (m_mode == NativeSplitMode::Horizontal) {
        int mid = area.top + h / 2;
        RECT r1 = { area.left, area.top, area.right, mid - 1 };
        RECT r2 = { area.left, mid + 1, area.right, area.bottom };
        rects.push_back(r1);
        rects.push_back(r2);
    } else if (m_mode == NativeSplitMode::Grid4) {
        int midX = area.left + w / 2;
        int midY = area.top + h / 2;
        rects.push_back({ area.left, area.top, midX - 1, midY - 1 });
        rects.push_back({ midX + 1, area.top, area.right, midY - 1 });
        rects.push_back({ area.left, midY + 1, midX - 1, area.bottom });
        rects.push_back({ midX + 1, midY + 1, area.right, area.bottom });
    }

    HPEN hPenBorder = CreatePen(PS_SOLID, 1, pal.toolbarBorder);
    HPEN hOldPen = static_cast<HPEN>(SelectObject(hdc, hPenBorder));

    for (size_t i = 0; i < visible.size() && i < rects.size(); ++i) {
        auto* pane = visible[i];
        const RECT& prc = rects[i];
        bool isActive = (pane->id == m_activePaneId);

        // Fondo del panel
        HBRUSH hBr = CreateSolidBrush(pal.editorBg);
        FillRect(hdc, &prc, hBr);
        DeleteObject(hBr);

        // Cabecera del panel (24px)
        int headerH = metrics.editorHeaderHeight > 0 ? metrics.editorHeaderHeight : 24;
        RECT rHeader = { prc.left, prc.top, prc.right, prc.top + headerH };
        HBRUSH hBrHdr = CreateSolidBrush(isActive ? pal.editorHeaderBg : pal.toolbarBg);
        FillRect(hdc, &rHeader, hBrHdr);
        DeleteObject(hBrHdr);

        // Título del documento en cabecera
        SelectObject(hdc, hFontSmall);
        SetBkMode(hdc, TRANSPARENT);
        SetTextColor(hdc, isActive ? pal.editorHeaderFg : pal.toolbarFg);

        std::wstring titleText = pane->docTitle.empty() ? L"[Sin Documento]" : pane->docTitle;
        if (pane->isLocked) {
            titleText = L"🔒 " + titleText + L" [BLOQUEADO]";
        }
        RECT rTitle = { prc.left + 8, prc.top, prc.right - 90, prc.top + headerH };
        DrawTextW(hdc, titleText.c_str(), -1, &rTitle, DT_LEFT | DT_VCENTER | DT_SINGLELINE | DT_END_ELLIPSIS);

        // Botones compactos de split a la derecha de la cabecera: [ | ] [ - ] [ 4 ] [ X ]
        RECT rButtons = { prc.right - 85, prc.top, prc.right - 4, prc.top + headerH };
        SetTextColor(hdc, pal.accentPrimary);
        DrawTextW(hdc, L"[ | ] [ - ] [田]", -1, &rButtons, DT_RIGHT | DT_VCENTER | DT_SINGLELINE);

        // Línea divisoria de cabecera
        MoveToEx(hdc, prc.left, prc.top + headerH - 1, nullptr);
        LineTo(hdc, prc.right, prc.top + headerH - 1);

        // Contenido del editor
        RECT rBody = { prc.left + 16, prc.top + headerH + 12, prc.right - 16, prc.bottom - 12 };
        SelectObject(hdc, hFontBody);
        SetTextColor(hdc, pal.editorFg);

        const std::wstring& bodyText = pane->editor->GetPlainText();
        if (!bodyText.empty()) {
            DrawTextW(hdc, bodyText.c_str(), -1, &rBody, DT_LEFT | DT_WORDBREAK);
        } else {
            SetTextColor(hdc, pal.binderSecondary);
            DrawTextW(hdc, L"(Panel vacío - Selecciona un documento en el Binder o usa Ctrl+Shift+L para bloquear)", -1, &rBody, DT_LEFT | DT_WORDBREAK);
        }
    }

    SelectObject(hdc, hOldPen);
    DeleteObject(hPenBorder);
}

} // namespace escritorio::ui
