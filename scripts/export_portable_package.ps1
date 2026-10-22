<#
.SYNOPSIS
    Empaqueta y exporta la distribución oficial portable 'Escritorio_Portable_Win11' a un archivo ZIP verificable
    y permite copiar opcionalmente la carpeta limpia a una memoria USB (pendrive) o unidad de red compartida.

.DESCRIPTION
    1. Verifica la integridad de dist/Escritorio_Portable_Win11 (si no existe, ejecuta scripts/prepare_dist.py).
    2. Comprueba que no existan archivos residuales, locks ni temporales.
    3. Comprime la carpeta en dist/Escritorio_Portable_Win11.zip usando compresión óptima.
    4. Genera el archivo criptográfico dist/Escritorio_Portable_Win11.zip.sha256.
    5. Si se indica -DestinationPath (o si se introduce en modo interactivo), copia la carpeta completa al pendrive.

.PARAMETER DestinationPath
    Ruta opcional de destino hacia donde copiar la carpeta portable (por ejemplo: "E:\", "F:\Escritorio").

.PARAMETER OutputZip
    Ruta del archivo ZIP generado (por defecto: dist\Escritorio_Portable_Win11.zip).

.PARAMETER Regenerate
    Fuerza la regeneración de la carpeta dist/ ejecutando scripts/prepare_dist.py.

.EXAMPLE
    .\scripts\export_portable_package.ps1
    .\scripts\export_portable_package.ps1 -DestinationPath "E:\"
    .\scripts\export_portable_package.ps1 -Regenerate
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$DestinationPath = "",

    [Parameter(Mandatory=$false)]
    [string]$OutputZip = "",

    [Parameter(Mandatory=$false)]
    [switch]$Regenerate
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir

$distFolder = Join-Path $rootDir "dist\Escritorio_Portable_Win11"
$exePath = Join-Path $distFolder "Escritorio.exe"

if ([string]::IsNullOrWhiteSpace($OutputZip)) {
    $OutputZip = Join-Path $rootDir "dist\Escritorio_Portable_Win11.zip"
}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   ESCRITORIO - EXPORTADOR DE PAQUETE PORTABLE OFICIAL (WIN11)        " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Regeneración / Verificación
if ($Regenerate -or -not (Test-Path $exePath)) {
    Write-Host "[1/5] Ejecutando generador de distribución (scripts/prepare_dist.py)..." -ForegroundColor Yellow
    $pyScript = Join-Path $scriptDir "prepare_dist.py"
    & python $pyScript
    if ($LASTEXITCODE -ne 0) {
        throw "Error al ejecutar scripts/prepare_dist.py"
    }
} else {
    Write-Host "[1/5] Directorio portable verificado: $distFolder" -ForegroundColor Green
}

# 2. Limpieza preventiva de archivos residuales
Write-Host "[2/5] Comprobando pureza de la carpeta (sin locks, temporales ni cachés)..." -ForegroundColor Yellow
$dirtyFiles = Get-ChildItem -Path $distFolder -Recurse -Include "*.tmp", "*.lock", "*.bak", "*.pyc", "__pycache__" -ErrorAction SilentlyContinue
if ($dirtyFiles) {
    foreach ($df in $dirtyFiles) {
        Write-Host "      -> Eliminando archivo residual: $($df.FullName)" -ForegroundColor DarkGray
        Remove-Item -Path $df.FullName -Recurse -Force
    }
}
Write-Host "      -> Carpeta 100% limpia y validada." -ForegroundColor Green

# 3. Compresión a ZIP
Write-Host "[3/5] Comprimiendo a archivo ZIP de alta fidelidad: $OutputZip" -ForegroundColor Yellow
if (Test-Path $OutputZip) {
    Remove-Item $OutputZip -Force
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($distFolder, $OutputZip, [System.IO.Compression.CompressionLevel]::Optimal, $true)

$zipInfo = Get-Item $OutputZip
$zipSizeMb = [math]::Round($zipInfo.Length / 1MB, 2)
Write-Host "      -> ZIP generado con éxito ($zipSizeMb MB)." -ForegroundColor Green

# 4. Cálculo Criptográfico SHA-256
Write-Host "[4/5] Calculando hash de verificación SHA-256..." -ForegroundColor Yellow
$hashResult = Get-FileHash -Path $OutputZip -Algorithm SHA256
$sha256Hex = $hashResult.Hash
$sha256File = "$OutputZip.sha256"
"$sha256Hex *$([System.IO.Path]::GetFileName($OutputZip))" | Out-File -FilePath $sha256File -Encoding utf8

Write-Host "======================================================================" -ForegroundColor Green
Write-Host "  ARCHIVO:  $([System.IO.Path]::GetFileName($OutputZip))" -ForegroundColor White
Write-Host "  TAMAÑO:   $zipSizeMb MB" -ForegroundColor White
Write-Host "  SHA-256:  $sha256Hex" -ForegroundColor Green
Write-Host "  CHECKSUM: $(Split-Path -Leaf $sha256File)" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Green

# 5. Copia opcional a Pendrive o Unidad de Red
if (-not [string]::IsNullOrWhiteSpace($DestinationPath)) {
    Write-Host "[5/5] Copiando carpeta portable a destino: $DestinationPath" -ForegroundColor Yellow
    if (-not (Test-Path $DestinationPath)) {
        New-Item -ItemType Directory -Path $DestinationPath -Force | Out-Null
    }
    
    $targetDir = Join-Path $DestinationPath "Escritorio_Portable_Win11"
    if (Test-Path $targetDir) {
        Write-Host "      -> Actualizando carpeta existente en destino..." -ForegroundColor DarkYellow
    } else {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }

    Copy-Item -Path "$distFolder\*" -Destination $targetDir -Recurse -Force
    Write-Host "      -> ¡Copia al pendrive o unidad completada con éxito!" -ForegroundColor Green
    Write-Host "      -> Ubicación: $targetDir" -ForegroundColor White
} else {
    Write-Host "[5/5] No se especificó -DestinationPath. (Para copiar a un pendrive, ejecute: .\scripts\export_portable_package.ps1 -DestinationPath 'E:\')" -ForegroundColor Gray
}

Write-Host "`n[LISTO] Paquete portable finalizado y listo para distribución." -ForegroundColor Cyan
