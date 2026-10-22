#pragma once

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <string>
#include <vector>
#include <memory>
#include <map>
#include "EditorWidget.hpp"
#include "../themes/ThemeEngine.hpp"

namespace escritorio::ui {

enum class NativeSplitMode {
    Single,
    Vertical,     // Ctrl+'
    Horizontal,   // Ctrl+"
    Grid4         // Cuadrícula de hasta 4 paneles
};

struct NativeEditorPane {
    std::wstring id;
    std::wstring docUuid;
    std::wstring docTitle;
    std::unique_ptr<EditorWidget> editor;
    bool isLocked = false;
    bool navigateAffectsOther = false;
    std::wstring mediaPath;
    int mediaType = 0; // 0=Editor RTF, 1=PDF, 2=Imagen, 3=Media/Transcripción, 4=Web

    bool ToggleLock() { isLocked = !isLocked; return isLocked; }
    bool ToggleNavigateAffectsOther() { navigateAffectsOther = !navigateAffectsOther; return navigateAffectsOther; }
};

class SplitEditorManager {
public:
    SplitEditorManager();
    ~SplitEditorManager() = default;

    // Modos de división
    void SplitVertical();
    void SplitHorizontal();
    void SplitGrid();
    void CloseSplit();
    NativeSplitMode GetMode() const { return m_mode; }

    // Selección de panel
    void SetActivePane(const std::wstring& id);
    const std::wstring& GetActivePaneId() const { return m_activePaneId; }
    NativeEditorPane* GetActivePane();
    NativeEditorPane* GetPane(const std::wstring& id);

    // Bloqueo y navegación cruzada
    bool ToggleLockActivePane();
    bool IsActiveLocked() const;
    bool ToggleNavigateAffectsOther();

    // Ruteo de documentos desde el Binder
    NativeEditorPane* RouteBinderItem(const std::wstring& uuid, const std::wstring& title, const std::wstring& text);

    // Renderizado en HDC
    void Render(HDC hdc, const RECT& area, const escritorio::themes::ThemePalette& pal,
                const escritorio::themes::UIDensityMetrics& metrics, HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody);

private:
    NativeSplitMode m_mode = NativeSplitMode::Single;
    std::wstring m_activePaneId = L"pane_0";
    std::vector<std::unique_ptr<NativeEditorPane>> m_panes;

    std::vector<NativeEditorPane*> GetVisiblePanes();
    NativeEditorPane* GetOtherPane(NativeEditorPane* source);
};

} // namespace escritorio::ui
