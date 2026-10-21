@echo off
setlocal
echo =================================================================
echo  Construccion Nativa de Escritorio.exe (Release Win11 Portable)
echo =================================================================

set CMAKE_PATH="C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"

if not exist %CMAKE_PATH% (
    set CMAKE_PATH=cmake.exe
)

echo [1/2] Generando solucion con CMake...
%CMAKE_PATH% -B build -S . -G "Visual Studio 17 2022" -A x64
if %ERRORLEVEL% NEQ 0 (
    echo Error al configurar CMake.
    exit /b %ERRORLEVEL%
)

echo [2/2] Compilando en configuracion Release...
%CMAKE_PATH% --build build --config Release
if %ERRORLEVEL% NEQ 0 (
    echo Error durante la compilacion.
    exit /b %ERRORLEVEL%
)

echo Compilacion finalizada con exito: build\release\Escritorio.exe
build\release\Escritorio.exe --benchmark
exit /b 0
