"""
Escritorio - Aplicación Nativa Portable para Windows 11
Punto de entrada principal.
"""

import sys
from pathlib import Path

# Añadir la raíz al path de Python para imports limpios
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.project import EscritorioProject
from src.ui.main_window import MainWindow, CentralViewMode
from src.themes.theme_engine import ThemeEngine, ThemeMode
from src.tools.statistics import WritingStatistics

def main():
    print("=" * 60)
    print(" Escritorio v1.0.0 (100% Portable - Windows 11)")
    print(" Réplica de Arquitectura Scrivener 3")
    print("=" * 60)

    # Inicializar motor de temas
    theme_engine = ThemeEngine(ThemeMode.DARK_OBSIDIAN)
    print(f"[Tema] Modo activo: {theme_engine.current_mode.value}")

    # Inicializar UI
    window = MainWindow()
    print("[UI] Ventana principal y vistas (Binder, Editor, Corcho, Esquematizador, Inspector) inicializadas.")

    print("[Estado] Sistema listo.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
