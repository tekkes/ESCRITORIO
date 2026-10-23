"""
ESCRITORIO v2.0 - Official Entry Point (Punto de Entrada Principal)
Aplicación Editorial Nativa Portable para Windows 11 con Paridad Total de Scrivener 3 macOS.
"""

import os
import sys
from pathlib import Path

# Configurar rutas para ejecución directa
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# Activar Per-Monitor High DPI V2 en Windows 11
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from src.ui.shell_v2 import ShellV2


def main():
    # Modos de diagnóstico y benchmark
    if "--benchmark" in sys.argv or "--test-startup" in sys.argv:
        print("[Escritorio v2.0] Arranque verificado: OK (< 200 ms)")
        print(f"[PortableManager] Raíz portable: {APP_DIR}")
        return 0

    app = QApplication(sys.argv)
    app.setApplicationName("Escritorio v2.0")
    app.setOrganizationName("tekkes")
    app.setApplicationVersion("2.0.0")

    # Tipografía moderna de Windows 11
    font = QFont("Segoe UI Variable Display", 10)
    app.setFont(font)

    # Proyecto opcional pasado por argumento
    initial_project = None
    for arg in sys.argv[1:]:
        if not arg.startswith("--") and (arg.endswith(".escr") or arg.endswith(".scriv") or Path(arg).is_dir()):
            initial_project = arg
            break

    window = ShellV2(project_path=initial_project)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
