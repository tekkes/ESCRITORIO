#pragma once

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <dwmapi.h>
#include <string>

#pragma comment(lib, "dwmapi.lib")
#pragma comment(lib, "comctl32.lib")
#pragma comment(lib, "uxtheme.lib")

namespace escritorio::ui {

/**
 * @brief Ventana Principal de Escritorio optimizada para Windows 11.
 * 
 * Integra:
 * - Esquinas redondeadas nativas de Windows 11 (DWMWA_WINDOW_CORNER_PREFERENCE).
 * - Barra de título en Dark Mode inmersivo (DWMWA_USE_IMMERSIVE_DARK_MODE).
 * - Per-Monitor DPI Awareness V2.
 * - Renderizado en memoria de doble búfer libre de parpadeos.
 * - Estructura visual tripartita de Scrivener 3 (Binder, Editor, Inspector).
 */
class MainWindow {
public:
    MainWindow();
    ~MainWindow();

    bool Create(HINSTANCE hInstance, int nCmdShow, double startupTimeMs);
    int RunMessageLoop();
    HWND GetHwnd() const { return m_hwnd; }

private:
    static LRESULT CALLBACK WndProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);
    LRESULT HandleMessage(UINT uMsg, WPARAM wParam, LPARAM lParam);

    void ApplyWindows11Attributes();
    void OnPaint(HDC hdc);
    void RenderUI(HDC hdc, const RECT& clientRect);

    HINSTANCE m_hInstance = nullptr;
    HWND m_hwnd = nullptr;
    double m_startupTimeMs = 0.0;

    // Colores del tema activo (Dark Obsidian)
    COLORREF m_colWindowBg = RGB(30, 30, 36);       // #1e1e24
    COLORREF m_colBinderBg = RGB(24, 24, 28);       // #18181c
    COLORREF m_colEditorBg = RGB(20, 20, 22);       // #141416
    COLORREF m_colInspectorBg = RGB(24, 24, 28);    // #18181c
    COLORREF m_colToolbarBg = RGB(36, 36, 44);      // #24242c
    COLORREF m_colStatusBarBg = RGB(24, 24, 28);    // #18181c
    COLORREF m_colCardBg = RGB(42, 43, 54);         // #2a2b36
    COLORREF m_colTextPrimary = RGB(224, 224, 230); // #e0e0e6
    COLORREF m_colTextSecondary = RGB(148, 163, 184);// #94a3b8
    COLORREF m_colAccent = RGB(99, 102, 241);       // #6366f1 (Indigo)
    COLORREF m_colBorder = RGB(46, 46, 56);         // #2e2e38

    HFONT m_hFontTitle = nullptr;
    HFONT m_hFontBody = nullptr;
    HFONT m_hFontSmall = nullptr;
    HFONT m_hFontEditor = nullptr;
};

} // namespace escritorio::ui
