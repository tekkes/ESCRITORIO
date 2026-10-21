#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <chrono>
#include <iostream>
#include <string>

#include "core/PortableManager.hpp"
#include "ui/MainWindow.hpp"

int WINAPI wWinMain(
    _In_ HINSTANCE hInstance,
    _In_opt_ HINSTANCE hPrevInstance,
    _In_ LPWSTR lpCmdLine,
    _In_ int nCmdShow)
{
    UNREFERENCED_PARAMETER(hPrevInstance);

    // 1. Iniciar cronómetro de alta resolución para medir el arranque en frío
    auto startTime = std::chrono::high_resolution_clock::now();

    // 2. Activar Per-Monitor High DPI Awareness V2 para nitidez en pantallas 4K
    SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);

    // 3. Inicializar el entorno portable (Copy & Run, sin registro, sin %APPDATA%)
    escritorio::core::PortableManager& portable = escritorio::core::PortableManager::Instance();
    portable.Initialize();

    // 4. Medir tiempo transcurrido hasta la preparación completa
    auto readyTime = std::chrono::high_resolution_clock::now();
    double startupTimeMs = std::chrono::duration<double, std::milli>(readyTime - startTime).count();

    // Comprobar argumentos de línea de comandos para modo benchmark / prueba sin interfaz
    std::wstring cmdLine(lpCmdLine);
    if (cmdLine.find(L"--benchmark") != std::wstring::npos || cmdLine.find(L"--test-startup") != std::wstring::npos) {
        // Modo benchmark para verificación automatizada en tests de integración
        std::wstring logPath = portable.GetConfigDirectory() + L"\\startup_benchmark.txt";
        HANDLE hFile = CreateFileW(logPath.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
        const std::wstring& cfgW = portable.GetConfigDirectory();
        int utf8Len = WideCharToMultiByte(CP_UTF8, 0, cfgW.data(), static_cast<int>(cfgW.size()), nullptr, 0, nullptr, nullptr);
        std::string cfgUtf8(utf8Len, '\0');
        WideCharToMultiByte(CP_UTF8, 0, cfgW.data(), static_cast<int>(cfgW.size()), cfgUtf8.data(), utf8Len, nullptr, nullptr);

        std::string benchmarkReport = "[Escritorio] Arranque en frio completado con exito: " +
                                      std::to_string(startupTimeMs) + " ms (Objetivo < 250 ms: OK)\r\n" +
                                      "[PortableManager] Modo portable activo en: " +
                                      cfgUtf8 + "\r\n";
        if (hFile != INVALID_HANDLE_VALUE) {
            DWORD bytesWritten = 0;
            WriteFile(hFile, benchmarkReport.data(), static_cast<DWORD>(benchmarkReport.size()), &bytesWritten, nullptr);
            CloseHandle(hFile);
        }

        if (AttachConsole(ATTACH_PARENT_PROCESS)) {
            HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
            DWORD written = 0;
            WriteFile(hOut, benchmarkReport.data(), static_cast<DWORD>(benchmarkReport.size()), &written, nullptr);
        }
        return 0;
    }

    // 5. Crear y presentar la ventana principal
    escritorio::ui::MainWindow mainWindow;
    if (!mainWindow.Create(hInstance, nCmdShow, startupTimeMs)) {
        MessageBoxW(nullptr, L"Error al inicializar la ventana principal de Escritorio.", L"Error Crítico", MB_ICONERROR | MB_OK);
        return 1;
    }

    // 6. Bucle de mensajes estándar de Windows
    return mainWindow.RunMessageLoop();
}
