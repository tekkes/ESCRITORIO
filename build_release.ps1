# ==============================================================================
# Script de Construcción Oficial: Escritorio.exe (Release Portable Windows 11)
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " Compilando Escritorio.exe (Release Estático /MT - Windows 11)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Localizar CMake
$cmakePath = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
if (-not (Test-Path $cmakePath)) {
    $cmd = Get-Command cmake.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        $cmakePath = $cmd.Source
    }
}
if (-not $cmakePath -or -not (Test-Path $cmakePath)) {
    Write-Error "No se encontro cmake.exe en el sistema."
}

# 2. Configurar con CMake
Write-Host "`n[1/3] Configurando proyecto con CMake (MSVC 2022 x64)..." -ForegroundColor Yellow
& $cmakePath -B "$projectRoot\build" -S "$projectRoot" -G "Visual Studio 17 2022" -A x64

# 3. Compilar en configuración Release
Write-Host "`n[2/3] Compilando binario monolítico optimizado en Release..." -ForegroundColor Yellow
& $cmakePath --build "$projectRoot\build" --config Release --parallel

# 4. Verificar ejecutable resultante
$exePath = "$projectRoot\build\release\Escritorio.exe"
if (Test-Path $exePath) {
    $sizeKb = [Math]::Round((Get-Item $exePath).Length / 1KB, 1)
    Write-Host "`n[3/3] Compilacion Exitosa!" -ForegroundColor Green
    Write-Host "  -> Ejecutable: $exePath" -ForegroundColor Green
    Write-Host "  -> Tamano: $sizeKb KB" -ForegroundColor Green
    
    # Ejecutar benchmark rápido de arranque
    & $exePath --benchmark
    if (Test-Path "$projectRoot\build\release\config\startup_benchmark.txt") {
        Get-Content "$projectRoot\build\release\config\startup_benchmark.txt" | ForEach-Object {
            Write-Host "  $_" -ForegroundColor Magenta
        }
    }
} else {
    Write-Error "Fallo en la generacion de $exePath"
}
