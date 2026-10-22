#pragma once

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <dwmapi.h>
#include <string>
#include <memory>
#include "../themes/ThemeEngine.hpp"
#include "ScriveningsEngine.hpp"
#include "SplitEditorManager.hpp"
#include "CorkboardWidget.hpp"
#include "OutlinerWidget.hpp"

#pragma comment(lib, "dwmapi.lib")
#pragma comment(lib, "comctl32.lib")
#pragma comment(lib, "uxtheme.lib")

namespace escritorio::ui {

/**
 * @brief Ventana Principal de Escritorio optimizada para Windows 11.
 * 
 * Integra:
 * - Esquinas redondeadas nativas de Windows 11 (DWMWA_WINDOW_CORNER_PREFERENCE).
 * - Barra de título en Dark Mode inmersivo adaptativo según el tema activo.
 * - Per-Monitor DPI Awareness V2.
 * - Renderizado en memoria de doble búfer libre de parpadeos (< 1ms por frame).
 * - Estructura visual tripartita de Scrivener 3 (Binder, Editor, Inspector).
 * - Motor visual con los 7 modos predefinidos y conmutación de densidad UI (Ultra-Compacto 28px/24px/10px).
 * - Modo Scrivenings continuo (Ctrl+1) con títulos in-situ y separadores configurables.
 * - Modo Pizarra de Corcho (Ctrl+2) en modos Rejilla, Forma Libre y Swimlanes.
 * - Pantalla dividida hasta 4 paneles (Ctrl+', Ctrl+", Grid) y Lock in Place (Ctrl+Shift+L).
 * - Modo Escritura de Guiones (Ctrl+8).
 */
class MainWindow {
public:
    MainWindow();
    ~MainWindow();

    bool Create(HINSTANCE hInstance, int nCmdShow, double startupTimeMs);
    int RunMessageLoop();
    HWND GetHwnd() const { return m_hwnd; }

    void SwitchTheme(escritorio::themes::ThemeMode mode);
    void CycleTheme();
    void SetUIDensity(escritorio::themes::UIDensityMode density);

    // Nuevas funciones de Prompt 07 y Prompt 08
    void ToggleScrivenings();
    void ToggleCorkboard();
    void ToggleOutliner();
    void SplitVertical();
    void SplitHorizontal();
    void SplitGrid();
    void CloseSplit();
    void ToggleLockActivePane();
    void ToggleScriptwritingMode();

    ScriveningsEngine* GetScriveningsEngine() { return m_scriveningsEngine.get(); }
    SplitEditorManager* GetSplitManager() { return m_splitManager.get(); }
    CorkboardWidget* GetCorkboardWidget() { return m_corkboardWidget.get(); }
    OutlinerWidget* GetOutlinerWidget() { return m_outlinerWidget.get(); }

private:
    static LRESULT CALLBACK WndProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);
    LRESULT HandleMessage(UINT uMsg, WPARAM wParam, LPARAM lParam);

    void ApplyWindows11Attributes();
    void OnPaint(HDC hdc);
    void RenderUI(HDC hdc, const RECT& clientRect);

    HINSTANCE m_hInstance = nullptr;
    HWND m_hwnd = nullptr;
    double m_startupTimeMs = 0.0;
    double m_lastThemeSwitchMs = 0.0;

    std::unique_ptr<escritorio::themes::ThemeEngine> m_themeEngine;
    std::unique_ptr<ScriveningsEngine> m_scriveningsEngine;
    std::unique_ptr<SplitEditorManager> m_splitManager;
    std::unique_ptr<CorkboardWidget> m_corkboardWidget;
    std::unique_ptr<OutlinerWidget> m_outlinerWidget;
    bool m_isScriptwritingMode = false;
    bool m_isCorkboardActive = false;
    bool m_isOutlinerActive = false;

    HFONT m_hFontTitle = nullptr;
    HFONT m_hFontBody = nullptr;
    HFONT m_hFontSmall = nullptr;
    HFONT m_hFontMicro = nullptr;
    HFONT m_hFontEditor = nullptr;
};

} // namespace escritorio::ui
