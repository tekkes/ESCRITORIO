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
}

MainWindow::~MainWindow() {
    if (m_hFontTitle) DeleteObject(m_hFontTitle);
    if (m_hFontBody) DeleteObject(m_hFontBody);
    if (m_hFontSmall) DeleteObject(m_hFontSmall);
    if (m_hFontEditor) DeleteObject(m_hFontEditor);
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
    m_hFontTitle = CreateFontW(17, 0, 0, 0, FW_SEMIBOLD, FALSE, FALSE, FALSE, DEFAULT_CHARSET,
                               OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY, DEFAULT_PITCH | FF_DONTCARE,
                               L"Segoe UI Variable Display");
    m_hFontBody = CreateFontW(15, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE, DEFAULT_CHARSET,
                              OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY, DEFAULT_PITCH | FF_DONTCARE,
                              L"Segoe UI Variable Display");
    m_hFontSmall = CreateFontW(13, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE, DEFAULT_CHARSET,
                               OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY, DEFAULT_PITCH | FF_DONTCARE,
                               L"Segoe UI Variable Text");
    m_hFontEditor = CreateFontW(18, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE, DEFAULT_CHARSET,
                                OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY, DEFAULT_PITCH | FF_DONTCARE,
                                L"Georgia");

    // Dimensiones iniciales ergonómicas
    int screenW = GetSystemMetrics(SM_CXSCREEN);
    int screenH = GetSystemMetrics(SM_CYSCREEN);
    int winW = (std::min)(1366, screenW - 80);
    int winH = (std::min)(840, screenH - 80);
    int winX = (screenW - winW) / 2;
    int winY = (screenH - winH) / 2;

    std::wstring title = L"Escritorio - [Manuscrito Principal] - Estación de Trabajo Editorial Scrivener 3";

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

    // Aplicar atributos avanzados de Windows 11
    ApplyWindows11Attributes();

    ShowWindow(m_hwnd, nCmdShow);
    UpdateWindow(m_hwnd);

    return true;
}

void MainWindow::ApplyWindows11Attributes() {
    if (!m_hwnd) return;

    // 1. Esquinas redondeadas de Windows 11 (DWMWA_WINDOW_CORNER_PREFERENCE = 33)
    // DWMWCP_ROUND = 2
    DWORD cornerPref = 2;
    DwmSetWindowAttribute(m_hwnd, 33, &cornerPref, sizeof(cornerPref));

    // 2. Modo Oscuro Inmersivo en la barra de título (DWMWA_USE_IMMERSIVE_DARK_MODE = 20)
    BOOL darkMode = TRUE;
    DwmSetWindowAttribute(m_hwnd, 20, &darkMode, sizeof(darkMode));

    // 3. Color de borde refinado (DWMWA_BORDER_COLOR = 34)
    COLORREF borderColor = RGB(46, 46, 56);
    DwmSetWindowAttribute(m_hwnd, 34, &borderColor, sizeof(borderColor));
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
        // Evitar parpadeos: el doble búfer de WM_PAINT dibuja la totalidad del área cliente
        return 1;

    case WM_SIZE:
        InvalidateRect(m_hwnd, nullptr, FALSE);
        return 0;

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

    // Renderizar componentes
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

    int toolbarHeight = 42;
    int statusBarHeight = 26;
    int mainAreaTop = toolbarHeight;
    int mainAreaBottom = height - statusBarHeight;

    int binderWidth = 240;
    int inspectorWidth = 260;
    int editorLeft = binderWidth;
    int editorWidth = (std::max)(200, width - binderWidth - inspectorWidth);
    int inspectorLeft = editorLeft + editorWidth;

    // 1. Fondo de la barra de herramientas (Toolbar)
    RECT rcToolbar = { 0, 0, width, toolbarHeight };
    HBRUSH hBrToolbar = CreateSolidBrush(m_colToolbarBg);
    FillRect(hdc, &rcToolbar, hBrToolbar);
    DeleteObject(hBrToolbar);

    // Botones de la barra de herramientas
    SelectObject(hdc, m_hFontSmall);
    SetBkMode(hdc, TRANSPARENT);
    SetTextColor(hdc, m_colTextPrimary);

    const wchar_t* toolButtons[] = {
        L"[+ Doc]", L"[+ Carpeta]", L"|",
        L"[ Documento ]", L"[ Corcho ]", L"[ Esquema ]", L"|",
        L"[ Modo Composición (F11) ]", L"[ Compilar (Ctrl+Shift+E) ]"
    };
    int toolX = 12;
    for (const auto* btn : toolButtons) {
        RECT rcBtn = { toolX, 10, toolX + 180, toolbarHeight - 6 };
        DrawTextW(hdc, btn, -1, &rcBtn, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
        SIZE sz;
        GetTextExtentPoint32W(hdc, btn, static_cast<int>(wcslen(btn)), &sz);
        toolX += sz.cx + 14;
    }

    // Línea separadora inferior de la barra de herramientas
    HPEN hPenBorder = CreatePen(PS_SOLID, 1, m_colBorder);
    HPEN hOldPen = static_cast<HPEN>(SelectObject(hdc, hPenBorder));
    MoveToEx(hdc, 0, toolbarHeight - 1, nullptr);
    LineTo(hdc, width, toolbarHeight - 1);

    // 2. Panel lateral izquierdo: BINDER
    RECT rcBinder = { 0, mainAreaTop, binderWidth, mainAreaBottom };
    HBRUSH hBrBinder = CreateSolidBrush(m_colBinderBg);
    FillRect(hdc, &rcBinder, hBrBinder);
    DeleteObject(hBrBinder);

    // Cabecera del Binder
    SelectObject(hdc, m_hFontSmall);
    SetTextColor(hdc, m_colTextSecondary);
    RECT rcBinderHeader = { 16, mainAreaTop + 10, binderWidth - 16, mainAreaTop + 28 };
    DrawTextW(hdc, L"BINDER / CUADERNO", -1, &rcBinderHeader, DT_LEFT | DT_SINGLELINE);

    // Elementos del Binder
    SelectObject(hdc, m_hFontBody);
    struct BinderItemDraw {
        int indent;
        const wchar_t* text;
        bool isSelected;
        COLORREF color;
    };
    BinderItemDraw binderItems[] = {
        { 0, L"v [Manuscrito]", true, m_colAccent },
        { 1, L"v Cap. 1: El Despertar", false, m_colTextPrimary },
        { 2, L"   Escena 1.1: La Niebla", false, m_colTextPrimary },
        { 2, L"   Escena 1.2: El Umbral", false, m_colTextSecondary },
        { 1, L"> Cap. 2: La Ciudad", false, m_colTextSecondary },
        { 0, L"> [Investigación]", false, RGB(16, 185, 129) },
        { 0, L"> [Papelera]", false, RGB(239, 68, 68) }
    };

    int itemY = mainAreaTop + 36;
    for (const auto& item : binderItems) {
        if (item.isSelected) {
            RECT rcSel = { 8, itemY - 2, binderWidth - 8, itemY + 22 };
            HBRUSH hBrSel = CreateSolidBrush(RGB(45, 55, 72));
            FillRect(hdc, &rcSel, hBrSel);
            DeleteObject(hBrSel);
        }
        SetTextColor(hdc, item.color);
        RECT rcItem = { 16 + (item.indent * 12), itemY, binderWidth - 16, itemY + 20 };
        DrawTextW(hdc, item.text, -1, &rcItem, DT_LEFT | DT_SINGLELINE);
        itemY += 26;
    }

    // Línea separadora del Binder con el Editor
    MoveToEx(hdc, binderWidth - 1, mainAreaTop, nullptr);
    LineTo(hdc, binderWidth - 1, mainAreaBottom);

    // 3. Panel Central: EDITOR RTF
    RECT rcEditor = { editorLeft, mainAreaTop, inspectorLeft, mainAreaBottom };
    HBRUSH hBrEditor = CreateSolidBrush(m_colEditorBg);
    FillRect(hdc, &rcEditor, hBrEditor);
    DeleteObject(hBrEditor);

    // Encabezado de ruta del documento
    RECT rcDocPath = { editorLeft + 30, mainAreaTop + 12, inspectorLeft - 30, mainAreaTop + 32 };
    SelectObject(hdc, m_hFontSmall);
    SetTextColor(hdc, m_colTextSecondary);
    DrawTextW(hdc, L"Manuscrito > Cap. 1: El Despertar > Escena 1.1: La Niebla", -1, &rcDocPath, DT_LEFT | DT_SINGLELINE);

    // Título del documento en el editor
    RECT rcDocTitle = { editorLeft + 30, mainAreaTop + 40, inspectorLeft - 30, mainAreaTop + 75 };
    SelectObject(hdc, m_hFontTitle);
    SetTextColor(hdc, m_colTextPrimary);
    DrawTextW(hdc, L"Escena 1.1: La Niebla", -1, &rcDocTitle, DT_LEFT | DT_SINGLELINE);

    // Cuerpo de texto
    RECT rcDocBody = { editorLeft + 30, mainAreaTop + 85, inspectorLeft - 30, mainAreaBottom - 20 };
    SelectObject(hdc, m_hFontEditor);
    SetTextColor(hdc, RGB(212, 212, 216));
    const wchar_t* sampleParagraph =
        L"La noche caía sobre las torres antiguas con una quietud espectral. Todo comenzaba aquí, en "
        L"este preciso instante en que el reloj de la catedral marcaba las doce campanadas. Las calles "
        L"adoquinadas brillaban bajo una fina capa de lluvia recién caída, reflejando la tímida luz ámbar de "
        L"las farolas de gas.\n\n"
        L"Isabel apretó el abrigo contra su pecho y aceleró el paso. Sabía que cada segundo contaba antes "
        L"de que las sombras volvieran a moverse entre los soportales de la plaza mayor. En el bolsillo interior, "
        L"el cuaderno encuadernado en piel contenía las coordenadas que nadie más debía descubrir.";
    DrawTextW(hdc, sampleParagraph, -1, &rcDocBody, DT_LEFT | DT_WORDBREAK);

    // Línea separadora del Editor con el Inspector
    MoveToEx(hdc, inspectorLeft - 1, mainAreaTop, nullptr);
    LineTo(hdc, inspectorLeft - 1, mainAreaBottom);

    // 4. Panel lateral derecho: INSPECTOR
    RECT rcInspector = { inspectorLeft, mainAreaTop, width, mainAreaBottom };
    HBRUSH hBrInspector = CreateSolidBrush(m_colInspectorBg);
    FillRect(hdc, &rcInspector, hBrInspector);
    DeleteObject(hBrInspector);

    // Cabecera del Inspector
    SelectObject(hdc, m_hFontSmall);
    SetTextColor(hdc, m_colTextSecondary);
    RECT rcInspectorHeader = { inspectorLeft + 16, mainAreaTop + 10, width - 16, mainAreaTop + 28 };
    DrawTextW(hdc, L"INSPECTOR (6 EN 1)", -1, &rcInspectorHeader, DT_LEFT | DT_SINGLELINE);

    // Pestañas del Inspector
    RECT rcInspectorTabs = { inspectorLeft + 16, mainAreaTop + 32, width - 16, mainAreaTop + 50 };
    DrawTextW(hdc, L"[ Sinopsis ]  Notas  Metadatos", -1, &rcInspectorTabs, DT_LEFT | DT_SINGLELINE);

    // Tarjeta de Sinopsis (Ficha virtual)
    RECT rcCard = { inspectorLeft + 16, mainAreaTop + 60, width - 16, mainAreaTop + 200 };
    HBRUSH hBrCard = CreateSolidBrush(m_colCardBg);
    FillRect(hdc, &rcCard, hBrCard);
    DeleteObject(hBrCard);

    // Borde de la tarjeta
    HPEN hPenCard = CreatePen(PS_SOLID, 1, m_colBorder);
    SelectObject(hdc, hPenCard);
    Rectangle(hdc, rcCard.left, rcCard.top, rcCard.right, rcCard.bottom);
    DeleteObject(hPenCard);

    // Contenido de la sinopsis
    RECT rcCardText = { rcCard.left + 12, rcCard.top + 12, rcCard.right - 12, rcCard.bottom - 12 };
    SelectObject(hdc, m_hFontSmall);
    SetTextColor(hdc, RGB(226, 232, 240));
    const wchar_t* synopsisText =
        L"Sinopsis de Escena:\n"
        L"Isabel llega a la ciudad vieja durante la medianoche lluviosa. Debe alcanzar el archivo "
        L"sin ser detectada por los vigilantes.";
    DrawTextW(hdc, synopsisText, -1, &rcCardText, DT_LEFT | DT_WORDBREAK);

    // Metadatos rápidos
    RECT rcMeta = { inspectorLeft + 16, mainAreaTop + 220, width - 16, mainAreaTop + 340 };
    const wchar_t* metaText =
        L"Metadatos de Documento:\n\n"
        L"* Tipo: Escena\n"
        L"* Estado: Primer borrador\n"
        L"* Etiqueta: Punto de Vista Isabel\n"
        L"* Incluir en Compilación: Sí\n"
        L"* Objetivo: 2.500 palabras";
    DrawTextW(hdc, metaText, -1, &rcMeta, DT_LEFT | DT_WORDBREAK);

    // 5. Barra de Estado inferior (Status Bar)
    RECT rcStatusBar = { 0, mainAreaBottom, width, height };
    HBRUSH hBrStatusBar = CreateSolidBrush(m_colStatusBarBg);
    FillRect(hdc, &rcStatusBar, hBrStatusBar);
    DeleteObject(hBrStatusBar);

    // Línea superior de la barra de estado
    MoveToEx(hdc, 0, mainAreaBottom, nullptr);
    LineTo(hdc, width, mainAreaBottom);

    SelectObject(hdc, m_hFontSmall);
    SetTextColor(hdc, m_colTextSecondary);

    // Métricas a la izquierda
    RECT rcStatusLeft = { 16, mainAreaBottom + 4, width / 2, height - 2 };
    DrawTextW(hdc, L"Palabras: 142 | Caracteres: 890 | Proyecto: Manuscrito (Portable .escr)", -1, &rcStatusLeft, DT_LEFT | DT_SINGLELINE);

    // Indicador de arranque y portabilidad a la derecha
    std::wstringstream ssRight;
    ssRight << L"Windows 11 Native | 100% Portable (Copy & Run) | Arranque: "
            << std::fixed << std::setprecision(1) << m_startupTimeMs << L" ms";
    std::wstring strRight = ssRight.str();

    RECT rcStatusRight = { width / 2, mainAreaBottom + 4, width - 16, height - 2 };
    SetTextColor(hdc, RGB(56, 189, 248)); // Sky blue highlight
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
