# ESCRITORIO v2.0 — Estación de Trabajo Editorial Nativa Portable (Scrivener 3 macOS Clean-Room Replica)

**Versión:** 2.0.0  
**Arquitectura:** Python 3.14+ / PyQt6 / Windows 11 High DPI v2  
**Referencia de Diseño:** Literature & Latte Scrivener 3 para macOS  
**Repositorio GitHub:** `https://github.com/tekkes/ESCRITORIO` (Rama `v2.0`)  

---

## 🚀 Novedades y Capacidades en la Versión 2.0

ESCRITORIO v2.0 ha sido reconstruido íntegramente para subsanar la totalidad de las carencias de la versión 1 y alcanzar paridad con Scrivener 3 en macOS:

1. **Interfaz Visual con Control Segmentado:**
   - Barra de herramientas rediseñada con control segmentado integrado `[ ✍️ Editor | 📌 Corcho | 📊 Esquema | 📜 Scrivenings ]`.
   - Historial de navegación atrás/adelante (`Alt+Left` / `Alt+Right`).
   - Buscador universal integrado directamente en la barra de herramientas.
   - Acceso directo con un solo clic a Objetivos, Foco Lingüístico y Compilador.

2. **Pizarra de Corcho Multi-Modo (Corkboard):**
   - **Modo Rejilla (Grid):** Tarjetas con proporción configurable, pin de etiqueta, sello diagonal de estado y sinopsis en tiempo real.
   - **Modo Forma Libre (Freeform 2D Canvas):** Posicionamiento bidimensional de tarjetas con opción de fijar el orden al Archivador.
   - **Modo Apilado por Etiquetas (Swimlanes):** Carriles verticales automáticos según las etiquetas (puntos de vista, tramas, etc.).

3. **Esquema Editorial Jerárquico (Outliner):**
   - Árbol-tabla con columnas dinámicas: Título, Tipo de Sección, Etiqueta, Estado, Palabras, Total Palabras (cálculo acumulativo recursivo de todos los descendientes), Objetivo, Progreso y Compilar.
   - Barras de progreso gráficas con degradado dinámico (rojo < 35%, ámbar < 75%, verde ≥ 100%).
   - Menú contextual en cabeceras para ocultar o mostrar cualquier columna.

4. **Editor Avanzado con Vista de Folio y Typewriter Scrolling:**
   - **Desplazamiento de Máquina de Escribir (Typewriter Scrolling):** Mantiene la línea activa de escritura centrada verticalmente.
   - **Simulación de Folio Físico (Page View):** Visualización en hoja con márgenes y sombras.
   - **Regla Tipográfica:** Marcas visuales de indentación y márgenes.
   - **Pie de Editor:** Recuento de palabras y caracteres en vivo más control deslizante de Zoom (80% a 200%).

5. **Inspector Scrivener 3 con 6 Pestañas:**
   - **Sinopsis y Metadatos:** Tarjeta de resumen, asignación de Tipo de Sección, Etiqueta, Estado y casilla de Compilación.
   - **Notas:** Cuaderno de notas exclusivo del documento.
   - **Marcadores:** Vínculos a documentos internos y URLs de investigación.
   - **Palabras Clave (Keywords):** Gestión de etiquetas cromáticas.
   - **Instantáneas (Snapshots):** Creación de versiones históricas con visor Diff interactivo (adiciones en verde, supresiones en rojo) y restauración con copia de seguridad previa.
   - **Comentarios:** Notas al margen con autor y hora.

6. **Compilador Editorial Maestro (Compile Dialog):**
   - Diálogo modal de 3 paneles (Formatos a la izquierda, Estructura del manuscrito al centro, Metadatos y transformaciones a la derecha).
   - Asignación de *Section Layouts* según el tipo de documento (Capítulo con título, Escena con separador `* * *`, etc.).
   - Sustitución de tokens (`<$projecttitle>`, `<$author>`, `<$date>`).
   - Exportadores a **DOCX (Word)**, **PDF (ReportLab)**, **EPUB 3 (EbookLib)**, **RTF** y **Markdown**.

7. **Herramientas de Planificación y Estilo:**
   - **Objetivos de Proyecto (Project Targets HUD):** Barras de avance de Borrador y Sesión diaria con hora de reinicio y cálculo de ritmo diario.
   - **Foco Lingüístico y Analizador de Diálogos:** Filtro dinámico de diálogos (comillas/rayas) frente a narración, detección de adverbios en *-mente* y conectores.
   - **Modo Composición a Pantalla Completa (`F11`):** Lienzo centrado de papel con ancho ajustable y controles auto-ocultables.
   - **Ventanas de Referencia Rápida (QR):** Ventanas flotantes desacopladas con fijación encima (*Always on Top*).

---

## 📁 Estructura del Proyecto

```
ESCRITORIOv.2/
├── main_v2.py                 # Punto de entrada ejecutable
├── build_v2.bat               # Compilador a ejecutable portable
├── src/
│   ├── core/                  # Modelo de datos, persistencia atómica y XML
│   │   ├── project_v2.py
│   │   ├── xml_engine_v2.py
│   │   ├── atomic_storage.py
│   │   └── backup_manager.py
│   ├── ui/                    # Interfaz gráfica (PyQt6)
│   │   ├── shell_v2.py        # Ventana principal
│   │   ├── binder_v2.py       # Archivador y colecciones
│   │   ├── editor_v2.py       # Editor con typewriter y page view
│   │   ├── corkboard_v2.py    # Corcho (3 modos)
│   │   ├── outliner_v2.py     # Esquema jerárquico con barras gráficas
│   │   ├── inspector_v2.py    # Inspector de 6 pestañas con diff
│   │   ├── scrivenings_v2.py  # Modo continuo
│   │   ├── composition_v2.py  # Modo pantalla completa F11
│   │   ├── quick_ref_v2.py    # Ventanas de referencia rápida
│   │   ├── targets_hud_v2.py  # HUD de objetivos
│   │   ├── linguistic_focus.py# Foco lingüístico
│   │   ├── compile_modal_v2.py# Compilador de 3 paneles
│   │   ├── project_chooser.py # Selector de plantillas
│   │   └── theme_v2.py        # Temas Claro, Oscuro, Sepia, Solarizado
│   └── compile/               # Pipeline de exportación
│       └── compile_engine.py  # Motores DOCX, PDF, EPUB, RTF, MD
└── tests/                     # Suite de pruebas automatizadas
    ├── test_project_core.py
    └── test_compile_pipeline.py
```

---

## 💻 Instrucciones de Uso

### Ejecución Directa
```bash
python main_v2.py
```

### Ejecutar Suite de Pruebas
```bash
python -m unittest discover tests
```

### Compilar Ejecutable Portable para Windows 11
```bash
build_v2.bat
```
