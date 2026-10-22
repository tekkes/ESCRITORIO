#include "ThemeEngine.hpp"
#include <fstream>
#include <sstream>
#include <chrono>

namespace escritorio::themes {

COLORREF ThemeEngine::ParseHexColor(const std::string& hex) {
    if (hex.empty()) return RGB(255, 255, 255);
    size_t offset = (hex[0] == '#') ? 1 : 0;
    if (hex.length() < offset + 6) return RGB(255, 255, 255);

    try {
        unsigned long val = std::stoul(hex.substr(offset, 6), nullptr, 16);
        int r = (val >> 16) & 0xFF;
        int g = (val >> 8) & 0xFF;
        int b = val & 0xFF;
        return RGB(r, g, b);
    } catch (...) {
        return RGB(255, 255, 255);
    }
}

const wchar_t* ThemeEngine::GetThemeName(ThemeMode mode) {
    switch (mode) {
    case ThemeMode::MinimalistDefault: return L"Modo Minimalista (Por Defecto)";
    case ThemeMode::CarbonDark:        return L"Modo Oscuro (Carbon Dark)";
    case ThemeMode::SolarizedDark:     return L"Modo Solarizado Oscuro";
    case ThemeMode::SolarizedLight:    return L"Modo Solarizado Claro";
    case ThemeMode::SepiaParchment:    return L"Modo Sepia (Classic Parchment)";
    case ThemeMode::NordicFrost:       return L"Modo Nord (Nordic Frost)";
    case ThemeMode::CatppuccinMocha:   return L"Modo Catppuccin Mocha";
    default:                           return L"Tema Personalizado";
    }
}

ThemeEngine::ThemeEngine(ThemeMode initialMode, UIDensityMode initialDensity)
    : m_currentMode(initialMode), m_densityMode(initialDensity) {
    InitPalette(initialMode);
    UpdateDensityMetrics();
}

void ThemeEngine::UpdateDensityMetrics() {
    switch (m_densityMode) {
    case UIDensityMode::UltraCompact:
        m_metrics = { 14, 28, 24, 10, 6, 22, 11, 10 };
        break;
    case UIDensityMode::Compact:
        m_metrics = { 16, 32, 26, 12, 6, 24, 12, 11 };
        break;
    case UIDensityMode::Comfortable:
    default:
        m_metrics = { 18, 38, 30, 14, 8, 28, 13, 12 };
        break;
    }
}

double ThemeEngine::SetMode(ThemeMode mode) {
    auto t0 = std::chrono::high_resolution_clock::now();
    m_currentMode = mode;
    InitPalette(mode);
    auto t1 = std::chrono::high_resolution_clock::now();
    return std::chrono::duration<double, std::milli>(t1 - t0).count();
}

double ThemeEngine::SwitchTheme(ThemeMode mode) {
    return SetMode(mode);
}

void ThemeEngine::SetDensity(UIDensityMode density) {
    m_densityMode = density;
    UpdateDensityMetrics();
}

void ThemeEngine::InitPalette(ThemeMode mode) {
    switch (mode) {
    case ThemeMode::MinimalistDefault:
        m_palette.windowBg           = ParseHexColor("#F7F7F5");
        m_palette.windowFg           = ParseHexColor("#242424");
        m_palette.windowBorder       = ParseHexColor("#E5E5E2");
        m_palette.toolbarBg          = ParseHexColor("#EFEFEC");
        m_palette.toolbarFg          = ParseHexColor("#242424");
        m_palette.toolbarBorder      = ParseHexColor("#E0E0DD");
        m_palette.statusBarBg        = ParseHexColor("#EFEFEC");
        m_palette.statusBarFg        = ParseHexColor("#6E6E6E");
        m_palette.binderBg           = ParseHexColor("#F7F7F5");
        m_palette.binderFg           = ParseHexColor("#242424");
        m_palette.binderSecondary    = ParseHexColor("#787878");
        m_palette.binderSelBg        = ParseHexColor("#E2E2DE");
        m_palette.binderSelFg        = ParseHexColor("#000000");
        m_palette.binderBorder       = ParseHexColor("#E5E5E2");
        m_palette.editorBg           = ParseHexColor("#FFFFFF");
        m_palette.editorFg           = ParseHexColor("#1A1A1A");
        m_palette.editorCaret        = ParseHexColor("#2D72D9");
        m_palette.editorSelection    = ParseHexColor("#D4E2F5");
        m_palette.editorHeaderBg     = ParseHexColor("#FAFAFA");
        m_palette.editorHeaderFg     = ParseHexColor("#4A4A4A");
        m_palette.corkboardBg        = ParseHexColor("#F2F2EE");
        m_palette.corkboardCardBg    = ParseHexColor("#FFFFFF");
        m_palette.corkboardCardFg    = ParseHexColor("#242424");
        m_palette.corkboardCardBorder= ParseHexColor("#D8D8D4");
        m_palette.corkboardPin       = ParseHexColor("#2D72D9");
        m_palette.outlinerBg         = ParseHexColor("#FFFFFF");
        m_palette.outlinerFg         = ParseHexColor("#242424");
        m_palette.outlinerAlternate  = ParseHexColor("#F9F9F8");
        m_palette.outlinerGrid       = ParseHexColor("#E8E8E4");
        m_palette.inspectorBg        = ParseHexColor("#F7F7F5");
        m_palette.inspectorFg        = ParseHexColor("#242424");
        m_palette.inspectorCardBg    = ParseHexColor("#FFFFFF");
        m_palette.accentPrimary      = ParseHexColor("#2D72D9");
        m_palette.accentSecondary    = ParseHexColor("#4A5568");
        m_palette.badgeLabelBg       = ParseHexColor("#E5EDF9");
        m_palette.badgeLabelFg       = ParseHexColor("#1E4F9E");
        m_palette.badgeStatusBg      = ParseHexColor("#E8E8E4");
        m_palette.badgeStatusFg      = ParseHexColor("#4A4A4A");
        m_palette.isDark             = false;
        break;

    case ThemeMode::CarbonDark:
        m_palette.windowBg           = ParseHexColor("#18191A");
        m_palette.windowFg           = ParseHexColor("#E4E6EB");
        m_palette.windowBorder       = ParseHexColor("#2E3033");
        m_palette.toolbarBg          = ParseHexColor("#202124");
        m_palette.toolbarFg          = ParseHexColor("#E4E6EB");
        m_palette.toolbarBorder      = ParseHexColor("#2E3033");
        m_palette.statusBarBg        = ParseHexColor("#141517");
        m_palette.statusBarFg        = ParseHexColor("#B0B3B8");
        m_palette.binderBg           = ParseHexColor("#18191A");
        m_palette.binderFg           = ParseHexColor("#E4E6EB");
        m_palette.binderSecondary    = ParseHexColor("#8A8D91");
        m_palette.binderSelBg        = ParseHexColor("#2D3748");
        m_palette.binderSelFg        = ParseHexColor("#FFFFFF");
        m_palette.binderBorder       = ParseHexColor("#2E3033");
        m_palette.editorBg           = ParseHexColor("#141517");
        m_palette.editorFg           = ParseHexColor("#E4E6EB");
        m_palette.editorCaret        = ParseHexColor("#4E95FF");
        m_palette.editorSelection    = ParseHexColor("#2C3E50");
        m_palette.editorHeaderBg     = ParseHexColor("#1C1D20");
        m_palette.editorHeaderFg     = ParseHexColor("#B0B3B8");
        m_palette.corkboardBg        = ParseHexColor("#1C1D1F");
        m_palette.corkboardCardBg    = ParseHexColor("#25272A");
        m_palette.corkboardCardFg    = ParseHexColor("#E4E6EB");
        m_palette.corkboardCardBorder= ParseHexColor("#36383D");
        m_palette.corkboardPin       = ParseHexColor("#EF4444");
        m_palette.outlinerBg         = ParseHexColor("#18191A");
        m_palette.outlinerFg         = ParseHexColor("#E4E6EB");
        m_palette.outlinerAlternate  = ParseHexColor("#1C1D20");
        m_palette.outlinerGrid       = ParseHexColor("#2E3033");
        m_palette.inspectorBg        = ParseHexColor("#18191A");
        m_palette.inspectorFg        = ParseHexColor("#E4E6EB");
        m_palette.inspectorCardBg    = ParseHexColor("#25272A");
        m_palette.accentPrimary      = ParseHexColor("#4E95FF");
        m_palette.accentSecondary    = ParseHexColor("#6366F1");
        m_palette.badgeLabelBg       = ParseHexColor("#1E3A8A");
        m_palette.badgeLabelFg       = ParseHexColor("#BFDBFE");
        m_palette.badgeStatusBg      = ParseHexColor("#374151");
        m_palette.badgeStatusFg      = ParseHexColor("#E5E7EB");
        m_palette.isDark             = true;
        break;

    case ThemeMode::SolarizedDark:
        m_palette.windowBg           = ParseHexColor("#002B36");
        m_palette.windowFg           = ParseHexColor("#839496");
        m_palette.windowBorder       = ParseHexColor("#073642");
        m_palette.toolbarBg          = ParseHexColor("#073642");
        m_palette.toolbarFg          = ParseHexColor("#93A1A1");
        m_palette.toolbarBorder      = ParseHexColor("#094959");
        m_palette.statusBarBg        = ParseHexColor("#073642");
        m_palette.statusBarFg        = ParseHexColor("#657B83");
        m_palette.binderBg           = ParseHexColor("#00212B");
        m_palette.binderFg           = ParseHexColor("#839496");
        m_palette.binderSecondary    = ParseHexColor("#586E75");
        m_palette.binderSelBg        = ParseHexColor("#073642");
        m_palette.binderSelFg        = ParseHexColor("#93A1A1");
        m_palette.binderBorder       = ParseHexColor("#073642");
        m_palette.editorBg           = ParseHexColor("#002B36");
        m_palette.editorFg           = ParseHexColor("#839496");
        m_palette.editorCaret        = ParseHexColor("#B58900");
        m_palette.editorSelection    = ParseHexColor("#073642");
        m_palette.editorHeaderBg     = ParseHexColor("#00242E");
        m_palette.editorHeaderFg     = ParseHexColor("#93A1A1");
        m_palette.corkboardBg        = ParseHexColor("#073642");
        m_palette.corkboardCardBg    = ParseHexColor("#002B36");
        m_palette.corkboardCardFg    = ParseHexColor("#839496");
        m_palette.corkboardCardBorder= ParseHexColor("#094959");
        m_palette.corkboardPin       = ParseHexColor("#DC322F");
        m_palette.outlinerBg         = ParseHexColor("#002B36");
        m_palette.outlinerFg         = ParseHexColor("#839496");
        m_palette.outlinerAlternate  = ParseHexColor("#00313E");
        m_palette.outlinerGrid       = ParseHexColor("#073642");
        m_palette.inspectorBg        = ParseHexColor("#00212B");
        m_palette.inspectorFg        = ParseHexColor("#839496");
        m_palette.inspectorCardBg    = ParseHexColor("#002B36");
        m_palette.accentPrimary      = ParseHexColor("#B58900");
        m_palette.accentSecondary    = ParseHexColor("#2AA198");
        m_palette.badgeLabelBg       = ParseHexColor("#073642");
        m_palette.badgeLabelFg       = ParseHexColor("#2AA198");
        m_palette.badgeStatusBg      = ParseHexColor("#073642");
        m_palette.badgeStatusFg      = ParseHexColor("#B58900");
        m_palette.isDark             = true;
        break;

    case ThemeMode::SolarizedLight:
        m_palette.windowBg           = ParseHexColor("#EEE8D5");
        m_palette.windowFg           = ParseHexColor("#657B83");
        m_palette.windowBorder       = ParseHexColor("#E0D9C4");
        m_palette.toolbarBg          = ParseHexColor("#E8E2CF");
        m_palette.toolbarFg          = ParseHexColor("#586E75");
        m_palette.toolbarBorder      = ParseHexColor("#DACFB7");
        m_palette.statusBarBg        = ParseHexColor("#E8E2CF");
        m_palette.statusBarFg        = ParseHexColor("#839496");
        m_palette.binderBg           = ParseHexColor("#EEE8D5");
        m_palette.binderFg           = ParseHexColor("#657B83");
        m_palette.binderSecondary    = ParseHexColor("#93A1A1");
        m_palette.binderSelBg        = ParseHexColor("#DFD7C2");
        m_palette.binderSelFg        = ParseHexColor("#073642");
        m_palette.binderBorder       = ParseHexColor("#DACFB7");
        m_palette.editorBg           = ParseHexColor("#FDF6E3");
        m_palette.editorFg           = ParseHexColor("#657B83");
        m_palette.editorCaret        = ParseHexColor("#B58900");
        m_palette.editorSelection    = ParseHexColor("#EEE8D5");
        m_palette.editorHeaderBg     = ParseHexColor("#F5EED9");
        m_palette.editorHeaderFg     = ParseHexColor("#586E75");
        m_palette.corkboardBg        = ParseHexColor("#E5DECB");
        m_palette.corkboardCardBg    = ParseHexColor("#FDF6E3");
        m_palette.corkboardCardFg    = ParseHexColor("#657B83");
        m_palette.corkboardCardBorder= ParseHexColor("#DACFB7");
        m_palette.corkboardPin       = ParseHexColor("#CB4B16");
        m_palette.outlinerBg         = ParseHexColor("#FDF6E3");
        m_palette.outlinerFg         = ParseHexColor("#657B83");
        m_palette.outlinerAlternate  = ParseHexColor("#F8F0DC");
        m_palette.outlinerGrid       = ParseHexColor("#EEE8D5");
        m_palette.inspectorBg        = ParseHexColor("#EEE8D5");
        m_palette.inspectorFg        = ParseHexColor("#657B83");
        m_palette.inspectorCardBg    = ParseHexColor("#FDF6E3");
        m_palette.accentPrimary      = ParseHexColor("#B58900");
        m_palette.accentSecondary    = ParseHexColor("#268BD2");
        m_palette.badgeLabelBg       = ParseHexColor("#DFD7C2");
        m_palette.badgeLabelFg       = ParseHexColor("#268BD2");
        m_palette.badgeStatusBg      = ParseHexColor("#DFD7C2");
        m_palette.badgeStatusFg      = ParseHexColor("#B58900");
        m_palette.isDark             = false;
        break;

    case ThemeMode::SepiaParchment:
        m_palette.windowBg           = ParseHexColor("#E8DEC3");
        m_palette.windowFg           = ParseHexColor("#3B2F2F");
        m_palette.windowBorder       = ParseHexColor("#D6C8A8");
        m_palette.toolbarBg          = ParseHexColor("#E2D7BB");
        m_palette.toolbarFg          = ParseHexColor("#3B2F2F");
        m_palette.toolbarBorder      = ParseHexColor("#D2C3A0");
        m_palette.statusBarBg        = ParseHexColor("#E2D7BB");
        m_palette.statusBarFg        = ParseHexColor("#6E5D4F");
        m_palette.binderBg           = ParseHexColor("#E8DEC3");
        m_palette.binderFg           = ParseHexColor("#3B2F2F");
        m_palette.binderSecondary    = ParseHexColor("#7A6856");
        m_palette.binderSelBg        = ParseHexColor("#D9CEB0");
        m_palette.binderSelFg        = ParseHexColor("#231B1B");
        m_palette.binderBorder       = ParseHexColor("#D6C8A8");
        m_palette.editorBg           = ParseHexColor("#F4ECD8");
        m_palette.editorFg           = ParseHexColor("#3B2F2F");
        m_palette.editorCaret        = ParseHexColor("#8C5333");
        m_palette.editorSelection    = ParseHexColor("#E4D5B7");
        m_palette.editorHeaderBg     = ParseHexColor("#ECE3CD");
        m_palette.editorHeaderFg     = ParseHexColor("#5C4A3E");
        m_palette.corkboardBg        = ParseHexColor("#DFD3B5");
        m_palette.corkboardCardBg    = ParseHexColor("#F7F1E1");
        m_palette.corkboardCardFg    = ParseHexColor("#3B2F2F");
        m_palette.corkboardCardBorder= ParseHexColor("#CCBE9E");
        m_palette.corkboardPin       = ParseHexColor("#8C5333");
        m_palette.outlinerBg         = ParseHexColor("#F4ECD8");
        m_palette.outlinerFg         = ParseHexColor("#3B2F2F");
        m_palette.outlinerAlternate  = ParseHexColor("#ECE4CE");
        m_palette.outlinerGrid       = ParseHexColor("#DFD3B5");
        m_palette.inspectorBg        = ParseHexColor("#E8DEC3");
        m_palette.inspectorFg        = ParseHexColor("#3B2F2F");
        m_palette.inspectorCardBg    = ParseHexColor("#F7F1E1");
        m_palette.accentPrimary      = ParseHexColor("#8C5333");
        m_palette.accentSecondary    = ParseHexColor("#5C4A3E");
        m_palette.badgeLabelBg       = ParseHexColor("#DACFB2");
        m_palette.badgeLabelFg       = ParseHexColor("#8C5333");
        m_palette.badgeStatusBg      = ParseHexColor("#D6C8A8");
        m_palette.badgeStatusFg      = ParseHexColor("#4A3B31");
        m_palette.isDark             = false;
        break;

    case ThemeMode::NordicFrost:
        m_palette.windowBg           = ParseHexColor("#2E3440");
        m_palette.windowFg           = ParseHexColor("#ECEFF4");
        m_palette.windowBorder       = ParseHexColor("#434C5E");
        m_palette.toolbarBg          = ParseHexColor("#3B4252");
        m_palette.toolbarFg          = ParseHexColor("#ECEFF4");
        m_palette.toolbarBorder      = ParseHexColor("#4C566A");
        m_palette.statusBarBg        = ParseHexColor("#2E3440");
        m_palette.statusBarFg        = ParseHexColor("#D8DEE9");
        m_palette.binderBg           = ParseHexColor("#2E3440");
        m_palette.binderFg           = ParseHexColor("#ECEFF4");
        m_palette.binderSecondary    = ParseHexColor("#9FB0C7");
        m_palette.binderSelBg        = ParseHexColor("#434C5E");
        m_palette.binderSelFg        = ParseHexColor("#ECEFF4");
        m_palette.binderBorder       = ParseHexColor("#434C5E");
        m_palette.editorBg           = ParseHexColor("#2E3440");
        m_palette.editorFg           = ParseHexColor("#ECEFF4");
        m_palette.editorCaret        = ParseHexColor("#88C0D0");
        m_palette.editorSelection    = ParseHexColor("#434C5E");
        m_palette.editorHeaderBg     = ParseHexColor("#353C4A");
        m_palette.editorHeaderFg     = ParseHexColor("#E5E9F0");
        m_palette.corkboardBg        = ParseHexColor("#3B4252");
        m_palette.corkboardCardBg    = ParseHexColor("#434C5E");
        m_palette.corkboardCardFg    = ParseHexColor("#ECEFF4");
        m_palette.corkboardCardBorder= ParseHexColor("#4C566A");
        m_palette.corkboardPin       = ParseHexColor("#BF616A");
        m_palette.outlinerBg         = ParseHexColor("#2E3440");
        m_palette.outlinerFg         = ParseHexColor("#ECEFF4");
        m_palette.outlinerAlternate  = ParseHexColor("#353C4A");
        m_palette.outlinerGrid       = ParseHexColor("#434C5E");
        m_palette.inspectorBg        = ParseHexColor("#2E3440");
        m_palette.inspectorFg        = ParseHexColor("#ECEFF4");
        m_palette.inspectorCardBg    = ParseHexColor("#434C5E");
        m_palette.accentPrimary      = ParseHexColor("#88C0D0");
        m_palette.accentSecondary    = ParseHexColor("#81A1C1");
        m_palette.badgeLabelBg       = ParseHexColor("#434C5E");
        m_palette.badgeLabelFg       = ParseHexColor("#88C0D0");
        m_palette.badgeStatusBg      = ParseHexColor("#4C566A");
        m_palette.badgeStatusFg      = ParseHexColor("#E5E9F0");
        m_palette.isDark             = true;
        break;

    case ThemeMode::CatppuccinMocha:
        m_palette.windowBg           = ParseHexColor("#181825");
        m_palette.windowFg           = ParseHexColor("#CDD6F4");
        m_palette.windowBorder       = ParseHexColor("#313244");
        m_palette.toolbarBg          = ParseHexColor("#11111B");
        m_palette.toolbarFg          = ParseHexColor("#CDD6F4");
        m_palette.toolbarBorder      = ParseHexColor("#313244");
        m_palette.statusBarBg        = ParseHexColor("#11111B");
        m_palette.statusBarFg        = ParseHexColor("#A6ADC8");
        m_palette.binderBg           = ParseHexColor("#181825");
        m_palette.binderFg           = ParseHexColor("#CDD6F4");
        m_palette.binderSecondary    = ParseHexColor("#6C7086");
        m_palette.binderSelBg        = ParseHexColor("#313244");
        m_palette.binderSelFg        = ParseHexColor("#CDD6F4");
        m_palette.binderBorder       = ParseHexColor("#313244");
        m_palette.editorBg           = ParseHexColor("#1E1E2E");
        m_palette.editorFg           = ParseHexColor("#CDD6F4");
        m_palette.editorCaret        = ParseHexColor("#CBA6F7");
        m_palette.editorSelection    = ParseHexColor("#45475A");
        m_palette.editorHeaderBg     = ParseHexColor("#181825");
        m_palette.editorHeaderFg     = ParseHexColor("#A6ADC8");
        m_palette.corkboardBg        = ParseHexColor("#181825");
        m_palette.corkboardCardBg    = ParseHexColor("#313244");
        m_palette.corkboardCardFg    = ParseHexColor("#CDD6F4");
        m_palette.corkboardCardBorder= ParseHexColor("#45475A");
        m_palette.corkboardPin       = ParseHexColor("#F38BA8");
        m_palette.outlinerBg         = ParseHexColor("#1E1E2E");
        m_palette.outlinerFg         = ParseHexColor("#CDD6F4");
        m_palette.outlinerAlternate  = ParseHexColor("#181825");
        m_palette.outlinerGrid       = ParseHexColor("#313244");
        m_palette.inspectorBg        = ParseHexColor("#181825");
        m_palette.inspectorFg        = ParseHexColor("#CDD6F4");
        m_palette.inspectorCardBg    = ParseHexColor("#313244");
        m_palette.accentPrimary      = ParseHexColor("#CBA6F7");
        m_palette.accentSecondary    = ParseHexColor("#B4BEFE");
        m_palette.badgeLabelBg       = ParseHexColor("#313244");
        m_palette.badgeLabelFg       = ParseHexColor("#B4BEFE");
        m_palette.badgeStatusBg      = ParseHexColor("#45475A");
        m_palette.badgeStatusFg      = ParseHexColor("#CDD6F4");
        m_palette.isDark             = true;
        break;
    }
}

void ThemeEngine::DrawMicroBadge(HDC hdc, int x, int y, const wchar_t* text, COLORREF bg, COLORREF fg, int height) const {
    if (!text || !*text) return;
    int len = static_cast<int>(wcslen(text));

    SIZE sz;
    GetTextExtentPoint32W(hdc, text, len, &sz);
    int width = sz.cx + 8;

    RECT rc = { x, y, x + width, y + height };

    HBRUSH hBr = CreateSolidBrush(bg);
    HPEN hPen = CreatePen(PS_NULL, 0, 0);
    HBRUSH hOldBr = static_cast<HBRUSH>(SelectObject(hdc, hBr));
    HPEN hOldPen = static_cast<HPEN>(SelectObject(hdc, hPen));

    RoundRect(hdc, rc.left, rc.top, rc.right, rc.bottom, height, height);

    SelectObject(hdc, hOldBr);
    SelectObject(hdc, hOldPen);
    DeleteObject(hBr);
    DeleteObject(hPen);

    COLORREF oldText = SetTextColor(hdc, fg);
    int oldBk = SetBkMode(hdc, TRANSPARENT);

    RECT rcText = { x + 4, y, x + width - 4, y + height };
    DrawTextW(hdc, text, len, &rcText, DT_CENTER | DT_VCENTER | DT_SINGLELINE);

    SetTextColor(hdc, oldText);
    SetBkMode(hdc, oldBk);
}

void ThemeEngine::DrawStatusDot(HDC hdc, int x, int y, COLORREF color, int size) const {
    HBRUSH hBr = CreateSolidBrush(color);
    HPEN hPen = CreatePen(PS_NULL, 0, 0);
    HBRUSH hOldBr = static_cast<HBRUSH>(SelectObject(hdc, hBr));
    HPEN hOldPen = static_cast<HPEN>(SelectObject(hdc, hPen));

    Ellipse(hdc, x, y, x + size, y + size);

    SelectObject(hdc, hOldBr);
    SelectObject(hdc, hOldPen);
    DeleteObject(hBr);
    DeleteObject(hPen);
}

bool ThemeEngine::LoadPalFile(const std::wstring& palPath) {
    std::ifstream file(palPath);
    if (!file.is_open()) return false;

    std::string line;
    while (std::getline(file, line)) {
        if (line.empty() || line[0] == '#' || line[0] == '[' || line[0] == ';') continue;
        size_t eqPos = line.find('=');
        if (eqPos != std::string::npos) {
            std::string key = line.substr(0, eqPos);
            std::string val = line.substr(eqPos + 1);

            // Eliminar espacios
            while (!key.empty() && isspace(static_cast<unsigned char>(key.front()))) key.erase(key.begin());
            while (!key.empty() && isspace(static_cast<unsigned char>(key.back()))) key.pop_back();
            while (!val.empty() && isspace(static_cast<unsigned char>(val.front()))) val.erase(val.begin());
            while (!val.empty() && isspace(static_cast<unsigned char>(val.back()))) val.pop_back();

            COLORREF c = ParseHexColor(val);
            if (key == "Window.Background" || key == "window.background") m_palette.windowBg = c;
            else if (key == "Window.Foreground" || key == "window.foreground") m_palette.windowFg = c;
            else if (key == "Binder.Background" || key == "binder.background") m_palette.binderBg = c;
            else if (key == "Binder.ItemText" || key == "binder.foreground") m_palette.binderFg = c;
            else if (key == "Editor.Background" || key == "editor.background") m_palette.editorBg = c;
            else if (key == "Editor.Foreground" || key == "editor.foreground") m_palette.editorFg = c;
            else if (key == "Corkboard.Background" || key == "corkboard.background") m_palette.corkboardBg = c;
            else if (key == "Corkboard.CardBackground" || key == "corkboard.card_bg") m_palette.corkboardCardBg = c;
            else if (key == "Inspector.Background" || key == "inspector.background") m_palette.inspectorBg = c;
        }
    }
    return true;
}

bool ThemeEngine::LoadScrTheme(const std::wstring& scrthemePath) {
    // Compatibilidad nativa con archivos de tema Scrivener 3 (.scrtheme)
    return LoadPalFile(scrthemePath);
}

} // namespace escritorio::themes
