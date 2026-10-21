#pragma once

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <string>
#include <vector>
#include <map>
#include <memory>

namespace escritorio::themes {

enum class ThemeMode {
    MinimalistDefault,
    CarbonDark,
    SolarizedDark,
    SolarizedLight,
    SepiaParchment,
    NordicFrost,
    CatppuccinMocha
};

enum class UIDensityMode {
    UltraCompact, // Toolbar 28px, Header 24px, Icon 14px, Badge 10px, Dot 6px
    Compact,      // Toolbar 32px, Header 26px, Icon 16px, Badge 12px, Dot 6px
    Comfortable   // Toolbar 38px, Header 30px, Icon 18px, Badge 14px, Dot 8px
};

struct UIDensityMetrics {
    int iconSize;
    int toolbarHeight;
    int editorHeaderHeight;
    int badgeHeight;
    int statusDotSize;
    int binderRowHeight;
    int fontSizeUi;
    int fontSizeSmall;
};

struct ThemePalette {
    COLORREF windowBg;
    COLORREF windowFg;
    COLORREF windowBorder;

    COLORREF toolbarBg;
    COLORREF toolbarFg;
    COLORREF toolbarBorder;

    COLORREF statusBarBg;
    COLORREF statusBarFg;

    COLORREF binderBg;
    COLORREF binderFg;
    COLORREF binderSecondary;
    COLORREF binderSelBg;
    COLORREF binderSelFg;
    COLORREF binderBorder;

    COLORREF editorBg;
    COLORREF editorFg;
    COLORREF editorCaret;
    COLORREF editorSelection;
    COLORREF editorHeaderBg;
    COLORREF editorHeaderFg;

    COLORREF corkboardBg;
    COLORREF corkboardCardBg;
    COLORREF corkboardCardFg;
    COLORREF corkboardCardBorder;
    COLORREF corkboardPin;

    COLORREF outlinerBg;
    COLORREF outlinerFg;
    COLORREF outlinerAlternate;
    COLORREF outlinerGrid;

    COLORREF inspectorBg;
    COLORREF inspectorFg;
    COLORREF inspectorCardBg;

    COLORREF accentPrimary;
    COLORREF accentSecondary;

    COLORREF badgeLabelBg;
    COLORREF badgeLabelFg;
    COLORREF badgeStatusBg;
    COLORREF badgeStatusFg;

    bool isDark;
};

class ThemeEngine {
public:
    ThemeEngine(ThemeMode initialMode = ThemeMode::MinimalistDefault,
                UIDensityMode initialDensity = UIDensityMode::UltraCompact);
    ~ThemeEngine() = default;

    double SetMode(ThemeMode mode); // Retorna latencia en ms
    void SetDensity(UIDensityMode density);

    ThemeMode GetCurrentMode() const { return m_currentMode; }
    UIDensityMode GetCurrentDensity() const { return m_densityMode; }

    const ThemePalette& GetPalette() const { return m_palette; }
    const UIDensityMetrics& GetDensityMetrics() const { return m_metrics; }

    static const wchar_t* GetThemeName(ThemeMode mode);
    static COLORREF ParseHexColor(const std::string& hex);

    // Renderizadores nativos GDI de alta densidad
    void DrawMicroBadge(HDC hdc, int x, int y, const wchar_t* text, COLORREF bg, COLORREF fg, int height = 10) const;
    void DrawStatusDot(HDC hdc, int x, int y, COLORREF color, int size = 6) const;

    // Carga básica de temas .pal / .scrtheme en caliente
    bool LoadPalFile(const std::wstring& palPath);

private:
    void InitPalette(ThemeMode mode);
    void UpdateDensityMetrics();

    ThemeMode m_currentMode;
    UIDensityMode m_densityMode;
    ThemePalette m_palette;
    UIDensityMetrics m_metrics;
};

} // namespace escritorio::themes
