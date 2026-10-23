@echo off
echo ========================================================
echo  Compilando ESCRITORIO v2.0 - Version Nativa Portable
echo ========================================================

set PYTHONUNBUFFERED=1

echo 1. Verificando dependencias...
python -m pip install --quiet pyinstaller PyQt6 python-docx reportlab ebooklib

echo 2. Empaquetando con PyInstaller...
pyinstaller --noconfirm --onedir --windowed ^
    --name "Escritorio_v2" ^
    --add-data "src;src" ^
    --add-data "assets;assets" ^
    --hidden-import "PyQt6" ^
    --hidden-import "reportlab" ^
    --hidden-import "docx" ^
    --hidden-import "ebooklib" ^
    main_v2.py

echo 3. Preparando distribucion portable...
if not exist "dist\Escritorio_v2_Portable" mkdir "dist\Escritorio_v2_Portable"
xcopy /E /I /Y "dist\Escritorio_v2\*" "dist\Escritorio_v2_Portable\"
if not exist "dist\Escritorio_v2_Portable\config" mkdir "dist\Escritorio_v2_Portable\config"

echo ========================================================
echo  ESCRITORIO v2.0 compilado con exito en:
echo  dist\Escritorio_v2_Portable\Escritorio_v2.exe
echo ========================================================
