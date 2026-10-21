#include "MainWindow.hpp"
#include <commctrl.h>
#include <sstream>
#include <iomanip>
#include <algorithm>

namespace escritorio::ui {

namespace {
const wchar_t* CLASS_NAME = L"Escritorio_MainWindow_Class";
}

MainWindow::MainWindow() {
    m_themeEngine = std::make_unique<escritorio::themes::ThemeEngine>(
        escritorio::themes::ThemeMode::MinimalistDefault,
        escritorio::themes::UIDensityMode::UltraCompact
    );
}

MainWindow::~MainWindow() {
    if (m_hFontTitle) DeleteObject(m_hFontTitle);
    if (m_hFontBody) DeleteObject(m_hFontBody);
    if (m_hFontSmall) DeleteObject(m_hFontSmall);
    if (m_hFontMicro) DeleteObject(m_hFontMicro);
    if (m_hFontEditor) DeleteObject(m_hFontEditor);
}

void MainWindow::SwitchTheme(escritorio::themes::ThemeMode mode) {
    if (!m_themeEngine) return;
    m_lastThemeSwitchMs = m_themeEngine->SetMode(mode);
    ApplyWindows11Attributes();
    if (m_hwnd) {
        InvalidateRect(m_hwnd, nullptr, FALSE);
    }
}

void MainWindow::CycleTheme() {
    if (!m_themeEngine) return;
    int current = static_cast<int>(m_themeEngine->GetCurrentMode());
    int next = (current + 1) % 7;
    SwitchTheme(static_cast<escritorio::themes::ThemeMode>(next));
}

void MainWindow::SetUIDensity(escritorio::themes::UIDensityMode density) {
    if (!m_themeEngine) return;
    m_themeEngine->SetDensity(density);
    if (m_hwnd) {
        InvalidateRect(m_hwnd, nullptr, FALSE);
    }
}

bool MainWindow::Create(HINSTANCE hInstance, int nCmdShow, double startupTimeMs) {
    m_hInstance = hInstance;
    m_startupTimeMs = startupTimeMs;

    // Inicializar controles comunes
    INITCOMMONCONTROLSEX icex;
    icex.dwSize = sizeof(INITCOMMONCONTROLSEX);
    icex.dwICC = ICC_WIN95_CLASSES | ICC_STANDARD_CLASSES;
    InitCommonControlsEx(&icex);

    // Registro de la clase de ventana
    WNDCLASSEXW wc = { sizeof(WNDCLASSEXW) };
    wc.style = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc = MainWindow::WndProc;
    wc.cbClsExtra = 0;
    wc.cbWndExtra = sizeof(MainWindow*);
    wc.hInstance = hInstance;
    wc.hIcon = LoadIcon(nullptr, IDI_APPLICATION);
    wc.hCursor = LoadCursor(nullptr, IDC_ARROW);
    wc.hbrBackground = nullptr; // Controlado en WM_PAINT con doble búfer
    wc.lpszMenuName = nullptr;
    wc.lpszClassName = CLASS_NAME;
    wc.hIconSm = LoadIcon(nullptr, IDI_APPLICATION);

    RegisterClassExW(&wc);

    // Tipografías de Windows 11
    m_hFontTitle = CreateFontW(16, 0, 0, 0, FW_SEMIBOLD, FALSE, FALSE, FALSE, DEFAULT_CHARSET,
                               OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY, DEFAULT_PITCH | FF_DONTCARE,
                               L"Segoe UI Variable Display");
    m_hFontBody = CreateFontW(14, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE, DEFAULT_CHARSET,
                              OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY, DEFAULT_PITCH | FF_DONTCARE,
                              L"Segoe UI Variable Display");
    m_hFontSmall = CreateFontW(12, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE, DEFAULT_CHARSET,
                               OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY, DEFAULT_PITCH | FF_DONTCARE,
                               L"Segoe UI Variable Text");
    m_hFontMicro = CreateFontW(10, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE, DEFAULT_CHARSET,
                               OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY, DEFAULT_PITCH | FF_DONTCARE,
                               L"Segoe UI Variable Text");
    m_hFontEditor = CreateFontW(17, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE, DEFAULT_CHARSET,
                                OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY, DEFAULT_PITCH | FF_DONTCARE,
                                L"Georgia");

    // Dimensiones ergonómicas
    int screenW = GetSystemMetrics(SM_CXSCREEN);
    int screenH = GetSystemMetrics(SM_CYSCREEN);
    int winW = (std::min)(1366, screenW - 80);
    int winH = (std::min)(840, screenH - 80);
    int winX = (screenW - winW) / 2;
    int winY = (screenH - winH) / 2;

    std::wstring title = L"Escritorio - [Manuscrito] - Scrivener 3 Fidelity Workstation";

    m_hwnd = CreateWindowExW(
        0,
        CLASS_NAME,
        title.c_str(),
        WS_OVERLAPPEDWINDOW | WS_CLIPCHILDREN,
        winX, winY, winW, winH,
        nullptr,
        nullptr,
        hInstance,
        this
    );

    if (!m_hwnd) {
        return false;
    }

    ApplyWindows11Attributes();

    ShowWindow(m_hwnd, nCmdShow);
    UpdateWindow(m_hwnd);

    return true;
}

void MainWindow::ApplyWindows11Attributes() {
    if (!m_hwnd) return;

    // 1. Esquinas redondeadas de Windows 11 (DWMWA_WINDOW_CORNER_PREFERENCE = 33)
    DWORD cornerPref = 2; // DWMWCP_ROUND
    DwmSetWindowAttribute(m_hwnd, 33, &cornerPref, sizeof(cornerPref));

    // 2. Modo Oscuro / Claro en la barra de título (DWMWA_USE_IMMERSIVE_DARK_MODE = 20)
    BOOL darkMode = m_themeEngine ? (m_themeEngine->GetPalette().isDark ? TRUE : FALSE) : TRUE;
    DwmSetWindowAttribute(m_hwnd, 20, &darkMode, sizeof(darkMode));

    // 3. Color de borde refinado (DWMWA_BORDER_COLOR = 34)
    if (m_themeEngine) {
        COLORREF borderColor = m_themeEngine->GetPalette().windowBorder;
        DwmSetWindowAttribute(m_hwnd, 34, &borderColor, sizeof(borderColor));
    }
}

LRESULT CALLBACK MainWindow::WndProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    MainWindow* pThis = nullptr;

    if (uMsg == WM_NCCREATE) {
        auto pCreate = reinterpret_cast<CREATESTRUCTW*>(lParam);
        pThis = reinterpret_cast<MainWindow*>(pCreate->lpCreateParams);
        SetWindowLongPtrW(hwnd, GWLP_USERDATA, reinterpret_cast<LONG_PTR>(pThis));
        pThis->m_hwnd = hwnd;
    } else {
        pThis = reinterpret_cast<MainWindow*>(GetWindowLongPtrW(hwnd, GWLP_USERDATA));
    }

    if (pThis) {
        return pThis->HandleMessage(uMsg, wParam, lParam);
    }
    return DefWindowProcW(hwnd, uMsg, wParam, lParam);
}

LRESULT MainWindow::HandleMessage(UINT uMsg, WPARAM wParam, LPARAM lParam) {
    switch (uMsg) {
    case WM_PAINT: {
        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(m_hwnd, &ps);
        OnPaint(hdc);
        EndPaint(m_hwnd, &ps);
        return 0;
    }

    case WM_ERASEBKGND:
        return 1; // Doble búfer previene parpadeos

    case WM_SIZE:
        InvalidateRect(m_hwnd, nullptr, FALSE);
        return 0;

    case WM_KEYDOWN:
        if (wParam == VK_F8) { // F8 para ciclar temas instantáneamente
            CycleTheme();
            return 0;
        }
        if (wParam == VK_F9) { // F9 para alternar densidad
            auto cur = m_themeEngine->GetCurrentDensity();
            auto next = (cur == escritorio::themes::UIDensityMode::UltraCompact)
                            ? escritorio::themes::UIDensityMode::Compact
                            : escritorio::themes::UIDensityMode::UltraCompact;
            SetUIDensity(next);
            return 0;
        }
        break;

    case WM_LBUTTONDOWN: {
        int x = LOWORD(lParam);
        int y = HIWORD(lParam);
        int tbH = m_themeEngine ? m_themeEngine->GetDensityMetrics().toolbarHeight : 28;

        if (y < tbH) {
            // Clic en la barra superior: selectores rápidos de tema
            RECT rc;
            GetClientRect(m_hwnd, &rc);
            int width = rc.right - rc.left;
            int themeX = width - 580;

            if (x >= themeX && x <= width - 10) {
                // Hay 7 botones de tema en la derecha
                int index = (x - themeX) / 80;
                if (index >= 0 && index < 7) {
                    SwitchTheme(static_cast<escritorio::themes::ThemeMode>(index));
                    return 0;
                }
            }
        }
        break;
    }

    case WM_DESTROY:
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProcW(m_hwnd, uMsg, wParam, lParam);
}

void MainWindow::OnPaint(HDC hdc) {
    RECT rc;
    GetClientRect(m_hwnd, &rc);

    // Doble búfer en memoria
    HDC memDC = CreateCompatibleDC(hdc);
    HBITMAP memBitmap = CreateCompatibleBitmap(hdc, rc.right - rc.left, rc.bottom - rc.top);
    HBITMAP oldBitmap = static_cast<HBITMAP>(SelectObject(memDC, memBitmap));

    // Renderizar componentes con el tema activo
    RenderUI(memDC, rc);

    // Volcar a pantalla
    BitBlt(hdc, 0, 0, rc.right - rc.left, rc.bottom - rc.top, memDC, 0, 0, SRCCOPY);

    SelectObject(memDC, oldBitmap);
    DeleteObject(memBitmap);
    DeleteDC(memDC);
}

void MainWindow::RenderUI(HDC hdc, const RECT& clientRect) {
    int width = clientRect.right - clientRect.left;
    int height = clientRect.bottom - clientRect.top;

    const auto& pal = m_themeEngine->GetPalette();
    const auto& d = m_themeEngine->GetDensityMetrics();

    int toolbarHeight = d.toolbarHeight;            // 28px en Ultra-compacto
    int editorHeaderHeight = d.editorHeaderHeight;  // 24px en Ultra-compacto
    int statusBarHeight = 24;
    int mainAreaTop = toolbarHeight;
    int mainAreaBottom = height - statusBarHeight;

    int binderWidth = 230;
    int inspectorWidth = 250;
    int editorLeft = binderWidth;
    int editorWidth = (std::max)(200, width - binderWidth - inspectorWidth);
    int inspectorLeft = editorLeft + editorWidth;

    // 1. Barra de Herramientas (Toolbar compacta 28px)
    RECT rcToolbar = { 0, 0, width, toolbarHeight };
    HBRUSH hBrToolbar = CreateSolidBrush(pal.toolbarBg);
    FillRect(hdc, &rcToolbar, hBrToolbar);
    DeleteObject(hBrToolbar);

    SelectObject(hdc, m_hFontSmall);
    SetBkMode(hdc, TRANSPARENT);
    SetTextColor(hdc, pal.toolbarFg);

    // Botones de acción principales
    const wchar_t* toolButtons[] = {
        L"[+ Doc]", L"[+ Carpeta]", L"|",
        L"[ Editor ]", L"[ Corcho ]", L"[ Esquema ]", L"|",
        L"[ Composición ]", L"[ Compilar ]"
    };
    int toolX = 10;
    for (const auto* btn : toolButtons) {
        RECT rcBtn = { toolX, 0, toolX + 160, toolbarHeight };
        DrawTextW(hdc, btn, -1, &rcBtn, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
        SIZE sz;
        GetTextExtentPoint32W(hdc, btn, static_cast<int>(wcslen(btn)), &sz);
        toolX += sz.cx + 8;
    }

    // Selectores rápidos de los 7 modos de visualización a la derecha
    const wchar_t* themeLabels[] = {
        L"Minimal", L"Carbon", L"Sol-D", L"Sol-L", L"Sepia", L"Nord", L"Mocha"
    };
    int currentModeIdx = static_cast<int>(m_themeEngine->GetCurrentMode());
    int selX = width - 580;

    SetTextColor(hdc, pal.binderSecondary);
    RECT rcThemeLabel = { selX - 55, 0, selX - 5, toolbarHeight };
    DrawTextW(hdc, L"Temas:", -1, &rcThemeLabel, DT_RIGHT | DT_VCENTER | DT_SINGLELINE);

    for (int i = 0; i < 7; ++i) {
        bool isActive = (i == currentModeIdx);
        RECT rcTab = { selX + (i * 80), 3, selX + (i * 80) + 74, toolbarHeight - 3 };

        if (isActive) {
            HBRUSH hBrActive = CreateSolidBrush(pal.binderSelBg);
            FillRect(hdc, &rcTab, hBrActive);
            DeleteObject(hBrActive);
            SetTextColor(hdc, pal.binderSelFg);
        } else {
            SetTextColor(hdc, pal.toolbarFg);
        }

        DrawTextW(hdc, themeLabels[i], -1, &rcTab, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
    }

    // Separador inferior de la barra de herramientas
    HPEN hPenBorder = CreatePen(PS_SOLID, 1, pal.toolbarBorder);
    HPEN hOldPen = static_cast<HPEN>(SelectObject(hdc, hPenBorder));
    MoveToEx(hdc, 0, toolbarHeight - 1, nullptr);
    LineTo(hdc, width, toolbarHeight - 1);

    // 2. Panel lateral izquierdo: BINDER
    RECT rcBinder = { 0, mainAreaTop, binderWidth, mainAreaBottom };
    HBRUSH hBrBinder = CreateSolidBrush(pal.binderBg);
    FillRect(hdc, &rcBinder, hBrBinder);
    DeleteObject(hBrBinder);

    // Cabecera del Binder
    SelectObject(hdc, m_hFontSmall);
    SetTextColor(hdc, pal.binderSecondary);
    RECT rcBinderHeader = { 12, mainAreaTop + 6, binderWidth - 12, mainAreaTop + 22 };
    DrawTextW(hdc, L"BINDER / MANUSCRITO", -1, &rcBinderHeader, DT_LEFT | DT_SINGLELINE);

    // Elementos del Binder con micro-píldoras e indicadores
    SelectObject(hdc, m_hFontBody);
    struct BinderItemDraw {
        int indent;
        const wchar_t* text;
        bool isSelected;
        COLORREF statusColor;
        const wchar_t* labelText;
    };
    BinderItemDraw binderItems[] = {
        { 0, L"v Manuscrito", true, pal.accentPrimary, L"TODO" },
        { 1, L"v Cap. 1: El Despertar", false, RGB(234, 88, 12), L"REV" },
        { 2, L"   Escena 1.1: La Niebla", false, RGB(16, 185, 129), L"OK" },
        { 2, L"   Escena 1.2: El Umbral", false, RGB(239, 68, 68), L"BORR" },
        { 1, L"> Cap. 2: La Ciudad", false, RGB(156, 163, 175), L"IDEA" },
        { 0, L"> Investigación", false, pal.accentSecondary, nullptr },
        { 0, L"> Papelera", false, RGB(239, 68, 68), nullptr }
    };

    int itemY = mainAreaTop + 28;
    for (const auto& item : binderItems) {
        if (item.isSelected) {
            RECT rcSel = { 6, itemY - 2, binderWidth - 6, itemY + d.binderRowHeight - 2 };
            HBRUSH hBrSel = CreateSolidBrush(pal.binderSelBg);
            FillRect(hdc, &rcSel, hBrSel);
            DeleteObject(hBrSel);
            SetTextColor(hdc, pal.binderSelFg);
        } else {
            SetTextColor(hdc, pal.binderFg);
        }

        // Indicador cromático de estado (6px dot)
        m_themeEngine->DrawStatusDot(hdc, 10 + (item.indent * 10), itemY + 6, item.statusColor, d.statusDotSize);

        // Texto del elemento
        RECT rcItem = { 20 + (item.indent * 10), itemY, binderWidth - 45, itemY + d.binderRowHeight };
        DrawTextW(hdc, item.text, -1, &rcItem, DT_LEFT | DT_SINGLELINE);

        // Micro-badge de etiqueta (10px pill)
        if (item.labelText) {
            SelectObject(hdc, m_hFontMicro);
            m_themeEngine->DrawMicroBadge(hdc, binderWidth - 42, itemY + 4, item.labelText, pal.badgeLabelBg, pal.badgeLabelFg, d.badgeHeight);
            SelectObject(hdc, m_hFontBody);
        }

        itemY += d.binderRowHeight;
    }

    // Separador Binder / Editor
    SelectObject(hdc, hPenBorder);
    MoveToEx(hdc, binderWidth - 1, mainAreaTop, nullptr);
    LineTo(hdc, binderWidth - 1, mainAreaBottom);

    // 3. Panel Central: EDITOR RTF
    RECT rcEditor = { editorLeft, mainAreaTop, inspectorLeft, mainAreaBottom };
    HBRUSH hBrEditor = CreateSolidBrush(pal.editorBg);
    FillRect(hdc, &rcEditor, hBrEditor);
    DeleteObject(hBrEditor);

    // Cabecera compacta del Editor (24px)
    RECT rcEditorHeader = { editorLeft, mainAreaTop, inspectorLeft, mainAreaTop + editorHeaderHeight };
    HBRUSH hBrEdHeader = CreateSolidBrush(pal.editorHeaderBg);
    FillRect(hdc, &rcEditorHeader, hBrEdHeader);
    DeleteObject(hBrEdHeader);

    SelectObject(hdc, m_hFontSmall);
    SetTextColor(hdc, pal.editorHeaderFg);
    RECT rcDocPath = { editorLeft + 16, mainAreaTop, inspectorLeft - 120, mainAreaTop + editorHeaderHeight };
    DrawTextW(hdc, L"Manuscrito > Cap. 1: El Despertar > Escena 1.1: La Niebla", -1, &rcDocPath, DT_LEFT | DT_VCENTER | DT_SINGLELINE);

    // Micro-badge de estado en cabecera
    SelectObject(hdc, m_hFontMicro);
    m_themeEngine->DrawMicroBadge(hdc, inspectorLeft - 110, mainAreaTop + 6, L"BORRADOR FINAL", pal.badgeStatusBg, pal.badgeStatusFg, d.badgeHeight);

    // Línea divisoria de cabecera
    MoveToEx(hdc, editorLeft, mainAreaTop + editorHeaderHeight - 1, nullptr);
    LineTo(hdc, inspectorLeft, mainAreaTop + editorHeaderHeight - 1);

    // Título y contenido del documento
    RECT rcDocTitle = { editorLeft + 24, mainAreaTop + editorHeaderHeight + 16, inspectorLeft - 24, mainAreaTop + editorHeaderHeight + 46 };
    SelectObject(hdc, m_hFontTitle);
    SetTextColor(hdc, pal.editorFg);
    DrawTextW(hdc, L"Escena 1.1: La Niebla", -1, &rcDocTitle, DT_LEFT | DT_SINGLELINE);

    RECT rcDocBody = { editorLeft + 24, mainAreaTop + editorHeaderHeight + 52, inspectorLeft - 24, mainAreaBottom - 16 };
    SelectObject(hdc, m_hFontEditor);
    SetTextColor(hdc, pal.editorFg);
    const wchar_t* sampleParagraph =
        L"La noche caía sobre las torres antiguas con una quietud espectral. Todo comenzaba aquí, en "
        L"este preciso instante en que el reloj de la catedral marcaba las doce campanadas. Las calles "
        L"adoquinadas brillaban bajo una fina capa de lluvia recién caída, reflejando la tímida luz ámbar de "
        L"las farolas de gas.\n\n"
        L"Isabel apretó el abrigo contra su pecho y aceleró el paso. Sabía que cada segundo contaba antes "
        L"de que las sombras volvieran a moverse entre los soportales de la plaza mayor. En el bolsillo interior, "
        L"el cuaderno encuadernado en piel contenía las coordenadas que nadie más debía descubrir.";
    DrawTextW(hdc, sampleParagraph, -1, &rcDocBody, DT_LEFT | DT_WORDBREAK);

    // Separador Editor / Inspector
    SelectObject(hdc, hPenBorder);
    MoveToEx(hdc, inspectorLeft - 1, mainAreaTop, nullptr);
    LineTo(hdc, inspectorLeft - 1, mainAreaBottom);

    // 4. Panel lateral derecho: INSPECTOR
    RECT rcInspector = { inspectorLeft, mainAreaTop, width, mainAreaBottom };
    HBRUSH hBrInspector = CreateSolidBrush(pal.inspectorBg);
    FillRect(hdc, &rcInspector, hBrInspector);
    DeleteObject(hBrInspector);

    SelectObject(hdc, m_hFontSmall);
    SetTextColor(hdc, pal.binderSecondary);
    RECT rcInspectorHeader = { inspectorLeft + 12, mainAreaTop + 6, width - 12, mainAreaTop + 22 };
    DrawTextW(hdc, L"INSPECTOR (6 EN 1)", -1, &rcInspectorHeader, DT_LEFT | DT_SINGLELINE);

    RECT rcInspectorTabs = { inspectorLeft + 12, mainAreaTop + 24, width - 12, mainAreaTop + 40 };
    DrawTextW(hdc, L"[ Sinopsis ]  Notas  Metadatos", -1, &rcInspectorTabs, DT_LEFT | DT_SINGLELINE);

    // Tarjeta de Sinopsis
    RECT rcCard = { inspectorLeft + 12, mainAreaTop + 46, width - 12, mainAreaTop + 170 };
    HBRUSH hBrCard = CreateSolidBrush(pal.corkboardCardBg);
    FillRect(hdc, &rcCard, hBrCard);
    DeleteObject(hBrCard);

    HPEN hPenCard = CreatePen(PS_SOLID, 1, pal.corkboardCardBorder);
    SelectObject(hdc, hPenCard);
    Rectangle(hdc, rcCard.left, rcCard.top, rcCard.right, rcCard.bottom);
    DeleteObject(hPenCard);

    RECT rcCardText = { rcCard.left + 10, rcCard.top + 8, rcCard.right - 10, rcCard.bottom - 8 };
    SelectObject(hdc, m_hFontSmall);
    SetTextColor(hdc, pal.corkboardCardFg);
    const wchar_t* synopsisText =
        L"Sinopsis de Escena:\n"
        L"Isabel llega a la ciudad vieja durante la medianoche lluviosa. Debe alcanzar el archivo "
        L"sin ser detectada por los vigilantes.";
    DrawTextW(hdc, synopsisText, -1, &rcCardText, DT_LEFT | DT_WORDBREAK);

    // Metadatos con micro-badges
    RECT rcMeta = { inspectorLeft + 12, mainAreaTop + 180, width - 12, mainAreaTop + 300 };
    SetTextColor(hdc, pal.windowFg);
    const wchar_t* metaText =
        L"Metadatos:\n\n"
        L"* Sección: Escena Capítulo\n"
        L"* Palabras Objetivo: 2.500\n"
        L"* Compilar: Activado\n"
        L"* Densidad UI: Ultra-Compacta (28px)";
    DrawTextW(hdc, metaText, -1, &rcMeta, DT_LEFT | DT_WORDBREAK);

    // 5. Barra de Estado (Status Bar)
    RECT rcStatusBar = { 0, mainAreaBottom, width, height };
    HBRUSH hBrStatusBar = CreateSolidBrush(pal.statusBarBg);
    FillRect(hdc, &rcStatusBar, hBrStatusBar);
    DeleteObject(hBrStatusBar);

    SelectObject(hdc, hPenBorder);
    MoveToEx(hdc, 0, mainAreaBottom, nullptr);
    LineTo(hdc, width, mainAreaBottom);

    SelectObject(hdc, m_hFontSmall);
    SetTextColor(hdc, pal.statusBarFg);

    RECT rcStatusLeft = { 12, mainAreaBottom + 3, width / 2, height - 1 };
    DrawTextW(hdc, L"Palabras: 142 | Caracteres: 890 | Formato: .escr / .scrivx compatible", -1, &rcStatusLeft, DT_LEFT | DT_SINGLELINE);

    std::wstringstream ssRight;
    ssRight << escritorio::themes::ThemeEngine::GetThemeName(m_themeEngine->GetCurrentMode())
            << L" | Latencia Conmutación: " << std::fixed << std::setprecision(2) << m_lastThemeSwitchMs << L" ms"
            << L" | Windows 11 Native";
    std::wstring strRight = ssRight.str();

    RECT rcStatusRight = { width / 2, mainAreaBottom + 3, width - 12, height - 1 };
    SetTextColor(hdc, pal.accentPrimary);
    DrawTextW(hdc, strRight.c_str(), -1, &rcStatusRight, DT_RIGHT | DT_SINGLELINE);

    SelectObject(hdc, hOldPen);
    DeleteObject(hPenBorder);
}

int MainWindow::RunMessageLoop() {
    MSG msg = {};
    while (GetMessageW(&msg, nullptr, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }
    return static_cast<int>(msg.wParam);
}

} // namespace escritorio::ui
