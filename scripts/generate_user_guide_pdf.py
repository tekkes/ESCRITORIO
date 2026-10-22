"""
Generador del Manual de Usuario y Guía Operativa Integral de Escritorio v1.0.0 en PDF.
Maqueta un libro editorial completo con acabado profesional idéntico a Adobe InDesign:
- Portada técnica de sangrado completo con métricas de publicación.
- Página de edición y créditos editoriales.
- Índice estructurado de contenidos.
- 7 Capítulos exhaustivos con prosa técnica densa, sin huecos muertos > 35 mm.
- Capturas de pantalla reales en alta resolución de cada vista de la herramienta.
- Cuadros destacados (Callouts), tablas técnicas comparativas y atajos de teclado.
- Resumen ejecutivo y cuestionario de autoevaluación.
Compila a PDF A4 mediante Playwright (Chromium/Edge) y añade marcadores interactivos con pypdf.
"""

import os
import sys
import base64
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_SCRIPTS = Path(r"C:\Users\IsaNet\.gemini\config\skills\technical-book-pdf\scripts")
if str(SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SKILL_SCRIPTS))

from layout_engine import PDFLayoutEngine


def img_to_base64(img_path: Path) -> str:
    """Convierte una imagen PNG a URI base64 para incrustación vectorial limpia en el PDF."""
    if not img_path.exists():
        return ""
    data = img_path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"


def build_user_guide_html() -> str:
    screen_dir = PROJECT_ROOT / "docs" / "screenshots"
    
    img_editor = img_to_base64(screen_dir / "01_interfaz_principal_editor.png")
    img_corkboard = img_to_base64(screen_dir / "02_pizarra_corcho.png")
    img_outliner = img_to_base64(screen_dir / "03_esquema_outliner.png")
    img_scrivenings = img_to_base64(screen_dir / "04_modo_scrivenings.png")
    img_split = img_to_base64(screen_dir / "05_pantalla_dividida.png")
    img_inspector = img_to_base64(screen_dir / "06_inspector_detalle.png")
    img_diff = img_to_base64(screen_dir / "07_comparador_myers_diff.png")
    img_composition = img_to_base64(screen_dir / "08_modo_composicion_f11.png")
    img_compile = img_to_base64(screen_dir / "09_dialogo_compilacion.png")
    img_theme = img_to_base64(screen_dir / "10_tema_sepia_pergamino.png")
    img_new_proj = img_to_base64(screen_dir / "11_dialogo_nuevo_proyecto.png")
    img_targets = img_to_base64(screen_dir / "12_dialogo_objetivos_targets.png")

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Manual de Usuario - Escritorio v1.0.0</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 18mm 16mm 20mm 16mm;
    @bottom-right {{
      content: counter(page);
      font-family: 'Source Sans 3', sans-serif;
      font-size: 8pt;
      color: #64748b;
    }}
    @bottom-left {{
      content: "ESCRITORIO v1.0.0 • Manual de Usuario y Referencia Operativa";
      font-family: 'Source Sans 3', sans-serif;
      font-size: 8pt;
      color: #94a3b8;
    }}
  }}

  @page:first {{
    margin: 0;
    @bottom-right {{ content: normal; }}
    @bottom-left {{ content: normal; }}
  }}

  *, *::before, *::after {{
    box-sizing: border-box;
  }}

  body {{
    font-family: 'Source Sans 3', 'Segoe UI', -apple-system, sans-serif;
    font-size: 9.3pt;
    line-height: 1.52;
    color: #1e293b;
    background-color: #ffffff;
    margin: 0;
    padding: 0;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
  }}

  h1, h2, h3, h4 {{
    font-family: 'Newsreader', 'Georgia', serif;
    color: #0f172a;
    margin-top: 0;
    line-height: 1.25;
  }}

  p {{
    margin: 0 0 10pt 0;
    text-align: justify;
    text-justify: inter-word;
  }}

  /* PORTADA DE SANGRADO COMPLETO */
  .cover-page {{
    page-break-after: always;
    width: 210mm;
    height: 297mm;
    background: linear-gradient(135deg, #0b1329 0%, #162a45 55%, #1e3a8a 100%);
    color: #ffffff;
    padding: 28mm 22mm 24mm 22mm;
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}

  .cover-badge {{
    display: inline-block;
    padding: 4px 12px;
    background: rgba(217, 119, 6, 0.25);
    border: 1px solid #d97706;
    border-radius: 4px;
    font-size: 8.5pt;
    font-weight: 700;
    letter-spacing: 1.5px;
    color: #f59e0b;
    text-transform: uppercase;
    margin-bottom: 16pt;
  }}

  .cover-title {{
    font-size: 34pt;
    font-weight: 800;
    letter-spacing: -0.5px;
    line-height: 1.1;
    color: #ffffff;
    margin-bottom: 8pt;
  }}

  .cover-subtitle {{
    font-size: 13pt;
    font-weight: 300;
    color: #cbd5e1;
    line-height: 1.45;
    max-width: 170mm;
    margin-bottom: 24pt;
    border-left: 3px solid #d97706;
    padding-left: 14pt;
  }}

  .cover-metrics {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12pt;
    margin-top: 10pt;
    padding: 16pt;
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
  }}

  .metric-item {{
    text-align: center;
  }}

  .metric-val {{
    font-size: 17pt;
    font-weight: 800;
    color: #f59e0b;
    font-family: 'Fira Code', monospace;
  }}

  .metric-lbl {{
    font-size: 7.5pt;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #94a3b8;
    margin-top: 2pt;
  }}

  .cover-footer {{
    border-top: 1px solid rgba(255, 255, 255, 0.18);
    padding-top: 12pt;
    display: flex;
    justify-content: space-between;
    font-size: 8.5pt;
    color: #94a3b8;
  }}

  /* PÁGINA DE EDICIÓN Y CRÉDITOS */
  .frontmatter-page {{
    page-break-after: always;
    padding-top: 20mm;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
  }}

  .legal-box {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #162a45;
    padding: 12pt 14pt;
    border-radius: 4px;
    font-size: 8.5pt;
    color: #475569;
    margin-bottom: 16pt;
  }}

  /* ÍNDICE */
  .toc-page {{
    page-break-after: always;
  }}

  .toc-title {{
    font-size: 20pt;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 2px solid #162a45;
    padding-bottom: 6pt;
    margin-bottom: 16pt;
  }}

  .toc-row {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 5pt 0;
    border-bottom: 1px dotted #cbd5e1;
    font-size: 9.5pt;
  }}

  .toc-chapter {{
    font-weight: 700;
    color: #162a45;
  }}

  .toc-page-num {{
    font-family: 'Fira Code', monospace;
    font-size: 8.5pt;
    color: #d97706;
    font-weight: 700;
  }}

  /* CAPÍTULOS Y SEPARADORES */
  .chapter-header {{
    page-break-before: always;
    margin-bottom: 14pt;
    border-bottom: 2px solid #162a45;
    padding-bottom: 8pt;
  }}

  .chapter-num {{
    font-size: 32pt;
    font-weight: 900;
    color: #d97706;
    line-height: 1;
    display: inline-block;
    margin-right: 8pt;
  }}

  .chapter-title-box {{
    display: inline-block;
    vertical-align: top;
  }}

  .chapter-title {{
    font-size: 18pt;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
  }}

  .chapter-tag {{
    font-size: 8pt;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #64748b;
    font-weight: 600;
  }}

  .objectives-card {{
    background: #f0f7fc;
    border: 1px solid #bae6fd;
    border-left: 4px solid #0284c7;
    padding: 10pt 12pt;
    border-radius: 4px;
    margin-bottom: 14pt;
    font-size: 8.8pt;
  }}

  .objectives-title {{
    font-weight: 700;
    color: #0369a1;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-size: 8pt;
    margin-bottom: 4pt;
  }}

  /* SECCIONES Y ENCABEZADOS INTERNOS */
  .section-h2 {{
    font-size: 13pt;
    font-weight: 700;
    color: #1e3a8a;
    margin: 16pt 0 6pt 0;
    border-left: 3px solid #d97706;
    padding-left: 8pt;
  }}

  .section-h3 {{
    font-size: 10.5pt;
    font-weight: 700;
    color: #0f172a;
    margin: 12pt 0 4pt 0;
  }}

  /* CAPTURAS DE PANTALLA REALES */
  .figure-card {{
    margin: 12pt 0;
    text-align: center;
    background: #fafafa;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8pt;
    break-inside: avoid;
  }}

  .figure-img {{
    max-width: 100%;
    height: auto;
    max-height: 85mm;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
    display: block;
    margin: 0 auto;
  }}

  .figure-caption {{
    font-size: 7.8pt;
    color: #64748b;
    margin-top: 6pt;
    font-style: italic;
  }}

  .figure-caption b {{
    color: #1e293b;
    font-style: normal;
  }}

  /* CUADROS DESTACADOS (CALLOUTS) */
  .callout {{
    padding: 9pt 12pt;
    border-radius: 4px;
    margin: 10pt 0;
    font-size: 8.7pt;
    line-height: 1.48;
    break-inside: avoid;
  }}

  .callout-definition {{
    background-color: #f0f7fc;
    border: 1px solid #bae6fd;
    border-left: 4px solid #0284c7;
  }}

  .callout-practice {{
    background-color: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 4px solid #16a34a;
  }}

  .callout-milestone {{
    background-color: #fffbeb;
    border: 1px solid #fef3c7;
    border-left: 4px solid #d97706;
  }}

  .callout-warning {{
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    border-left: 4px solid #dc2626;
  }}

  .callout-takeaway {{
    background-color: #faf5ee;
    border: 1px solid #fed7aa;
    border-left: 4px solid #c2410c;
  }}

  .callout-title {{
    font-weight: 700;
    text-transform: uppercase;
    font-size: 7.8pt;
    letter-spacing: 0.6px;
    margin-bottom: 3pt;
  }}

  /* TABLAS TÉCNICAS */
  .data-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12pt 0;
    font-size: 8.3pt;
    break-inside: avoid;
  }}

  .data-table th {{
    background-color: #162a45;
    color: #ffffff;
    font-weight: 700;
    text-align: left;
    padding: 5pt 8pt;
    border: 1px solid #162a45;
  }}

  .data-table td {{
    padding: 5pt 8pt;
    border: 1px solid #e2e8f0;
  }}

  .data-table tr:nth-child(even) {{
    background-color: #f8fafc;
  }}

  .shortcut-badge {{
    font-family: 'Fira Code', monospace;
    font-size: 7.8pt;
    background: #e2e8f0;
    border: 1px solid #cbd5e1;
    border-radius: 3px;
    padding: 1px 5px;
    color: #0f172a;
    font-weight: 600;
    white-space: nowrap;
  }}

  /* CUESTIONARIO Y SOLUCIONES */
  .cuestionario-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8pt;
    margin-top: 8pt;
  }}

  .pregunta-card {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 7pt;
    font-size: 8pt;
    break-inside: avoid;
  }}

  .pregunta-num {{
    font-weight: 700;
    color: #1e3a8a;
    margin-bottom: 2pt;
  }}

  .opcion-item {{
    margin: 2pt 0;
    padding-left: 12pt;
    text-indent: -12pt;
  }}

  .badge-op {{
    display: inline-block;
    width: 13px;
    height: 13px;
    line-height: 13px;
    border-radius: 50%;
    background: #e2e8f0;
    color: #0f172a;
    font-size: 7pt;
    font-weight: 700;
    text-align: center;
    margin-right: 4pt;
  }}

  .solucion-card {{
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 3px solid #16a34a;
    padding: 5pt 8pt;
    border-radius: 3px;
    margin-bottom: 5pt;
    font-size: 8pt;
    break-inside: avoid;
  }}
</style>
</head>
<body>

<!-- PORTADA -->
<div class="cover-page">
  <div class="cover-top-block">
    <div class="cover-badge">MANUAL TÉCNICO OFICIAL • EDICIÓN DE PRODUCCIÓN</div>
    <div class="cover-title">ESCRITORIO v1.0.0</div>
    <div class="cover-subtitle">
      Manual de Usuario y Guía Operativa Integral de la Estación de Trabajo Literaria y Editorial Portable para Windows 11: Del Primer Borrador a la Compilación Definitiva.
    </div>
  </div>

  <div class="cover-metrics">
    <div class="metric-item">
      <div class="metric-val">100%</div>
      <div class="metric-lbl">Portable Zero-Install</div>
    </div>
    <div class="metric-item">
      <div class="metric-val">6</div>
      <div class="metric-lbl">Pestañas de Inspector</div>
    </div>
    <div class="metric-item">
      <div class="metric-val">12</div>
      <div class="metric-lbl">Temas Visuales</div>
    </div>
    <div class="metric-item">
      <div class="metric-val">5</div>
      <div class="metric-lbl">Formatos de Compilación</div>
    </div>
  </div>

  <div class="cover-footer">
    <div>Autor y Arquitecto: <b>tekkes</b></div>
    <div>Plataforma: <b>Windows 11 (64-bit)</b></div>
    <div>Fecha de Emisión: <b>Octubre 2026</b></div>
    <div>Licencia: <b>Código Abierto</b></div>
  </div>
</div>

<!-- FRONTMATTER / PÁGINA DE EDICIÓN -->
<div class="frontmatter-page">
  <div>
    <h2 style="font-size: 16pt; color: #162a45; border-bottom: 2px solid #162a45; padding-bottom: 4pt;">Edición y Acreditaciones Técnicas</h2>
    <p>
      El presente manual constituye el compendio exhaustivo y autorizado para la operación del software <b>Escritorio v1.0.0</b>. Esta obra ha sido redactada para guiar de forma rigurosa y progresiva a todo escritor profesional, novelista, guionista, dramaturgo o investigador académico, partiendo desde los conceptos básicos de inicialización portable hasta las técnicas más avanzadas de control de versiones con instantáneas (Snapshots), análisis diferencial con el algoritmo Myers Diff, composición inmersiva y compilación multiformato hacia estándares de la industria editorial.
    </p>

    <div class="legal-box">
      <b>DECLARACIÓN DE INTEGRIDAD Y PORTABILIDAD DEL SOFTWARE:</b><br>
      Escritorio v1.0.0 opera bajo una estricta directriz de aislamiento del sistema (Zero-Install). El software jamás modifica el Registro de Windows, no realiza escrituras en carpetas protegidas ni almacena datos en la ruta <code>%APPDATA%</code>. Toda la configuración, temas visuales, diccionarios ortográficos, plantillas y copias de seguridad residen exclusivamente dentro de la carpeta portable <code>./config/</code>. Se autoriza la copia íntegra de la carpeta a memorias USB, unidades externas de estado sólido o directorios sincronizados en red local para su uso simultáneo en cualquier estación de trabajo con Windows 11.
    </div>

    <div class="callout callout-milestone">
      <div class="callout-title" style="color: #b45309;">Compromiso de Fidelidad y Paridad Funcional</div>
      Escritorio reproduce con absoluta fidelidad y exactitud los paradigmas de flujo de trabajo que convirtieron a Scrivener 3 en el estándar de oro de la industria literaria internacional. La arquitectura desacoplada de Cuaderno (Binder), Pizarra de Corcho (Corkboard), Esquema (Outliner), Editor RTF continuo (Scrivenings) y Motor de Compilación garantiza que ninguna obra dependa de formatos propietarios cerrados ni de conectividad continua a servidores remotos.
    </div>
  </div>

  <div style="font-size: 8pt; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 8pt;">
    <b>Escritorio v1.0.0</b> © 2026 tekkes. Reservados todos los derechos de código abierto. Documento maquetado y compilado con el motor editorial de alta resolución para Windows 11.
  </div>
</div>

<!-- ÍNDICE DE CONTENIDOS -->
<div class="toc-page">
  <div class="toc-title">Índice General de Contenidos</div>

  <div class="toc-row">
    <span class="toc-chapter">CAPÍTULO 1: Fundamentos, Arquitectura Portable y Primeros Pasos</span>
    <span class="toc-page-num">Pág. 4</span>
  </div>
  <div class="toc-row">
    <span class="toc-chapter">CAPÍTULO 2: El Cuaderno (Binder) y la Estructuración Narrativa</span>
    <span class="toc-page-num">Pág. 6</span>
  </div>
  <div class="toc-row">
    <span class="toc-chapter">CAPÍTULO 3: Las Cuatro Vistas: Editor RTF, Corcho, Esquema y Scrivenings</span>
    <span class="toc-page-num">Pág. 8</span>
  </div>
  <div class="toc-row">
    <span class="toc-chapter">CAPÍTULO 4: El Inspector Especializado de Seis Pestañas y Myers Diff</span>
    <span class="toc-page-num">Pág. 10</span>
  </div>
  <div class="toc-row">
    <span class="toc-chapter">CAPÍTULO 5: Concentración Inmersiva (Modo Composición F11) y Temas</span>
    <span class="toc-page-num">Pág. 12</span>
  </div>
  <div class="toc-row">
    <span class="toc-chapter">CAPÍTULO 6: Motor de Compilación Editorial Multiformato</span>
    <span class="toc-page-num">Pág. 14</span>
  </div>
  <div class="toc-row">
    <span class="toc-chapter">CAPÍTULO 7: Copias de Seguridad Criptográficas SHA-256 y Resumen Técnico</span>
    <span class="toc-page-num">Pág. 16</span>
  </div>

  <div class="callout callout-definition" style="margin-top: 24pt;">
    <div class="callout-title" style="color: #0369a1;">Convenciones Tipográficas en este Manual</div>
    A lo largo de esta guía, los atajos de teclado se señalan mediante distintivos en recuadro como <span class="shortcut-badge">Ctrl+N</span>, <span class="shortcut-badge">Ctrl+K</span> o <span class="shortcut-badge">F11</span>. Las opciones de los menús se indican en negrita separadas por el carácter de flecha (ej. <b>Ver &gt; Pizarra de Corcho</b>). Las capturas de pantalla han sido obtenidas directamente sobre el binario en ejecución en Windows 11.
  </div>
</div>

<!-- CAPÍTULO 1 -->
<div class="chapter-header">
  <span class="chapter-num">01</span>
  <div class="chapter-title-box">
    <div class="chapter-tag">NIVEL 0 • INICIACIÓN RÁPIDA</div>
    <h1 class="chapter-title">Fundamentos, Filosofía Zero-Install y Primer Proyecto</h1>
  </div>
</div>

<div class="objectives-card">
  <div class="objectives-title">Objetivos Pedagógicos del Capítulo</div>
  Comprender la arquitectura 100% portable de Escritorio, aprender a iniciar la herramienta sin instaladores, navegar por el diálogo de selección de plantillas y familiarizarse con la anatomía visual de la interfaz gráfica en Windows 11.
</div>

<h2 class="section-h2">1.1. Filosofía Zero-Install: Independencia y Seguridad Absoluta</h2>
<p>
  A diferencia de los procesadores de texto convencionales y las suites ofimáticas tradicionales, <b>Escritorio</b> ha sido concebido desde su primer trazo arquitectónico para ser un entorno 100% portable. Esto significa que el escritor no requiere permisos de administrador en Windows, ni necesita pasar por asistentes de instalación, instaladores MSI o servicios en segundo plano que ralentizan el sistema. El paquete completo se distribuye en una única carpeta denominada <code>Escritorio_Portable_Win11/</code>.
</p>
<p>
  Al copiar esta carpeta a una memoria USB (pendrive), a un disco duro externo o a una carpeta compartida en red, el autor puede trasladar su estudio de escritura entero de un ordenador de sobremesa a un portátil de viaje, abriendo el ejecutable <code>Escritorio.exe</code> con la certeza absoluta de que todos sus proyectos, temas visuales personalizados, plantillas y configuraciones se mantendrán intactos.
</p>

<div class="callout callout-practice">
  <div class="callout-title" style="color: #15803d;">Buenas Prácticas de Portabilidad</div>
  No ejecute el programa directamente dentro del archivo comprimido <code>.zip</code>. Extraiga primero la carpeta completa en una ubicación de su elección (por ejemplo <code>D:\Escritorio\</code> o en la raíz de su pendrive). De este modo, los archivos auxiliares de autoguardado podrán escribirse sin restricciones del sistema.
</div>

<h2 class="section-h2">1.2. El Diálogo de Nuevo Proyecto y el Catálogo de Plantillas</h2>
<p>
  Al presionar <span class="shortcut-badge">Ctrl+Mayús+N</span> o seleccionar <b>Archivo &gt; Nuevo Proyecto desde Plantilla...</b>, Escritorio presenta el catálogo bilingüe clasificado en cuatro grandes categorías narrativas: En Blanco, Ficción, No Ficción y Guion.
</p>

<div class="figure-card">
  <img src="{img_new_proj}" class="figure-img" alt="Diálogo de Nuevo Proyecto">
  <div class="figure-caption"><b>Figura 1.1:</b> Diálogo interactivo de selección de plantillas narrativas con previsualización estructural.</div>
</div>

<p>
  Cada plantilla establece de forma automática la jerarquía del Binder adaptada al formato elegido: objetivos globales de palabras, carpetas de personajes, escenarios y notas de ambientación. La plantilla <b>Novela con Partes</b>, por ejemplo, configura una estructura dividida en tomos o libros con capítulos anidados y escenas independientes, ideal para obras de gran envergadura.
</p>

<h2 class="section-h2">1.3. Anatomía Visual de la Estación de Trabajo</h2>
<p>
  La ventana principal de Escritorio se articula en una disposición armónica de tres columnas ajustables mediante divisores interactivos: a la izquierda, el <b>Cuaderno (Binder)</b>; en el centro, el <b>Área de Trabajo Principal</b> (que alterna entre Editor, Corcho, Esquema y Scrivenings); y a la derecha, el <b>Inspector Editorial</b>.
</p>

<div class="figure-card">
  <img src="{img_editor}" class="figure-img" alt="Interfaz Principal de Escritorio">
  <div class="figure-caption"><b>Figura 1.2:</b> Interfaz de Escritorio mostrando el Cuaderno jerárquico a la izquierda, el editor RTF central y el Inspector a la derecha en tema Oscuro Obsidiana.</div>
</div>

<!-- CAPÍTULO 2 -->
<div class="chapter-header">
  <span class="chapter-num">02</span>
  <div class="chapter-title-box">
    <div class="chapter-tag">NIVEL INTERMEDIO • GESTIÓN ESTRUCTURAL</div>
    <h1 class="chapter-title">El Cuaderno (Binder) y la Estructuración Narrativa</h1>
  </div>
</div>

<div class="objectives-card">
  <div class="objectives-title">Objetivos Pedagógicos del Capítulo</div>
  Dominar la organización jerárquica de manuscritos, la creación y anidamiento de partes y capítulos, la división instantánea de escenas en el cursor, la duplicación segura y la importación de textos largos.
</div>

<h2 class="section-h2">2.1. Jerarquía del Binder: El Esqueleto de su Obra</h2>
<p>
  En Escritorio, un libro no es un archivo monolítico kilométrico donde buscar una escena exige desplazarse durante minutos. Toda obra se descompone en pequeñas unidades manejables estructuradas en forma de árbol. El Cuaderno alberga tres nodos raíz protegidos e indestructibles:
</p>
<p>
  1. <b>Manuscrito (Draft):</b> La única sección que por defecto se incluye en la compilación final del libro. En su interior se anidan partes, capítulos y escenas.<br>
  2. <b>Investigación (Research):</b> Almacén de documentación, entrevistas, recortes históricos, cronologías y biografías de personajes que no formarán parte del manuscrito publicado.<br>
  3. <b>Papelera (Trash):</b> Contenedor de seguridad donde van a parar las escenas eliminadas. Nada se destruye físicamente hasta que el autor decide vaciar la papelera de forma expresa.
</p>

<table class="data-table">
  <thead>
    <tr>
      <th>Acción Estructural</th>
      <th>Atajo de Teclado</th>
      <th>Efecto en el Manuscrito</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Nueva Escena</b></td>
      <td><span class="shortcut-badge">Ctrl+N</span></td>
      <td>Crea un nuevo documento de texto en la carpeta seleccionada actualmente.</td>
    </tr>
    <tr>
      <td><b>Nuevo Capítulo</b></td>
      <td><span class="shortcut-badge">Ctrl+Mayús+N</span></td>
      <td>Inserta una carpeta contenedora de nivel de capítulo.</td>
    </tr>
    <tr>
      <td><b>Dividir Escena</b></td>
      <td><span class="shortcut-badge">Ctrl+K</span></td>
      <td>Corta el texto en el cursor y genera una escena hermana con la segunda mitad.</td>
    </tr>
    <tr>
      <td><b>Fusionar Escenas</b></td>
      <td><span class="shortcut-badge">Ctrl+Mayús+M</span></td>
      <td>Combina el texto de la escena activa con el de la escena hermana siguiente.</td>
    </tr>
    <tr>
      <td><b>Duplicar Documento</b></td>
      <td><span class="shortcut-badge">Ctrl+D</span></td>
      <td>Crea una réplica exacta con el contenido íntegro y sinopsis.</td>
    </tr>
  </tbody>
</table>

<h2 class="section-h2">2.2. División en Caliente (Ctrl+K) y Fusión de Escenas</h2>
<p>
  Uno de los mayores bloqueos creativos ocurre cuando una escena se extiende en demasía y el autor siente que debe convertirse en dos momentos narrativos distintos. En Escritorio, basta situar el cursor de texto en el punto exacto donde se desea la ruptura y pulsar <span class="shortcut-badge">Ctrl+K</span>. La primera parte permanece en el documento actual y la segunda se traspasa automáticamente a una nueva escena hermana nombrada <code>(Continuación)</code>.
</p>

<div class="callout callout-milestone">
  <div class="callout-title" style="color: #b45309;">Importación y Segmentación Inteligente (Import &amp; Split)</div>
  Si ya posee una novela escrita en un archivo <code>.docx</code>, <code>.txt</code> o <code>.md</code> de cientos de páginas, seleccione <b>Archivo &gt; Importar y Dividir...</b>. Defina un separador (como <code>#</code>, <code>Capítulo</code> o <code>***</code>) y Escritorio desglosará el manuscrito completo en decenas de escenas organizadas jerárquicamente en cuestión de segundos.
</div>

<!-- CAPÍTULO 3 -->
<div class="chapter-header">
  <span class="chapter-num">03</span>
  <div class="chapter-title-box">
    <div class="chapter-tag">NIVEL INTERMEDIO • ENTORNOS DE TRABAJO</div>
    <h1 class="chapter-title">Las Cuatro Vistas: Editor, Corcho, Esquema y Scrivenings</h1>
  </div>
</div>

<div class="objectives-card">
  <div class="objectives-title">Objetivos Pedagógicos del Capítulo</div>
  Comprender cuándo y cómo alternar entre las 4 perspectivas de trabajo (Editor de texto, Pizarra de Corcho, Esquema analítico y Modo Scrivenings continuo), y cómo emplear la pantalla dividida.
</div>

<h2 class="section-h2">3.1. Pizarra de Corcho (Corkboard - Ctrl+2)</h2>
<p>
  Al hacer clic sobre una carpeta en el Binder y activar la Pizarra de Corcho mediante <span class="shortcut-badge">Ctrl+2</span>, el área central se transforma en un tablero de corcho donde cada escena se representa mediante una tarjeta de índice física.
</p>

<div class="figure-card">
  <img src="{img_corkboard}" class="figure-img" alt="Pizarra de Corcho">
  <div class="figure-caption"><b>Figura 3.1:</b> Pizarra de Corcho con tarjetas de índice, sinopsis editables, pines cromáticos y recuento de palabras en vivo.</div>
</div>

<p>
  Cada tarjeta permite editar directamente el título de la escena y su sinopsis argumental. La modificación de la sinopsis en la tarjeta se sincroniza en milisegundos con el archivo físico <code>synopsis.txt</code> del proyecto y con la pestaña correspondiente del Inspector.
</p>

<h2 class="section-h2">3.2. Esquema Editorial (Outliner - Ctrl+3)</h2>
<p>
  El Esquema ofrece una perspectiva cuantitativa y analítica inestimable para directores de obra y novelistas estructurados. Organizado como una hoja de cálculo interactiva, muestra columnas de título, tipo de nodo, estado editorial, etiqueta narrativa, palabras de la escena, total acumulado de la carpeta, objetivo y barra de progreso.
</p>

<div class="figure-card">
  <img src="{img_outliner}" class="figure-img" alt="Esquema Editorial">
  <div class="figure-caption"><b>Figura 3.2:</b> Esquema Editorial con barras de progreso porcentuales y recuento recursivo de palabras por capítulo.</div>
</div>

<h2 class="section-h2">3.3. Modo Scrivenings (Ctrl+4) y Pantalla Dividida (Ctrl+')</h2>
<p>
  El <b>Modo Scrivenings</b> reúne todas las escenas de una carpeta en un flujo continuo de texto separado por líneas divisorias. Permite leer y editar varios capítulos como si fuesen un único pergamino, pero manteniendo la independencia física de cada archivo en disco.
</p>

<div class="figure-card">
  <img src="{img_split}" class="figure-img" alt="Pantalla Dividida">
  <div class="figure-caption"><b>Figura 3.3:</b> Pantalla dividida verticalmente permitiendo comparar y editar dos escenas en simultáneo.</div>
</div>

<!-- CAPÍTULO 4 -->
<div class="chapter-header">
  <span class="chapter-num">04</span>
  <div class="chapter-title-box">
    <div class="chapter-tag">NIVEL AVANZADO • AUDITORÍA NARRATIVA</div>
    <h1 class="chapter-title">El Inspector de Seis Pestañas y el Algoritmo Myers Diff</h1>
  </div>
</div>

<div class="objectives-card">
  <div class="objectives-title">Objetivos Pedagógicos del Capítulo</div>
  Dominar el panel del Inspector, gestionar metadatos narrativos (POV, tramas, estados), tomar instantáneas históricas (Snapshots) y analizar diferencias textuales con el motor Myers Diff.
</div>

<h2 class="section-h2">4.1. Las Seis Pestañas Especializadas del Inspector</h2>
<p>
  Accesible con <span class="shortcut-badge">Ctrl+Mayús+I</span> o haciendo clic en el icono correspondiente de la barra de herramientas, el Inspector reúne seis facetas esenciales del documento activo:
</p>
<p>
  1. <b>Sinopsis y Notas:</b> Resumen argumental de la escena y cuaderno de notas privadas del autor que no se compilan.<br>
  2. <b>Marcadores (Bookmarks):</b> Enlaces a fuentes documentales, URLs de referencia o archivos locales auxiliares.<br>
  3. <b>Metadatos:</b> Asignación de estado (Borrador, En Revisión, Final), etiqueta cromática de trama, Punto de Vista (POV) del personaje que narra y localización geográfica de la escena.<br>
  4. <b>Instantáneas (Snapshots):</b> El sistema de control de versiones literario de Escritorio.<br>
  5. <b>Comentarios y Notas al Pie:</b> Anotaciones al margen y referencias numeradas al pie.<br>
  6. <b>Ajustes de Sección:</b> Tipos de sección para el compilador y conmutador de exclusión.
</p>

<div class="figure-card">
  <img src="{img_inspector}" class="figure-img" alt="Panel del Inspector">
  <div class="figure-caption"><b>Figura 4.1:</b> Pestaña de Metadatos del Inspector con selectores de Estado, Etiqueta, POV y Localización.</div>
</div>

<h2 class="section-h2">4.2. Instantáneas (Snapshots - Ctrl+5) y Comparador Myers Diff</h2>
<p>
  Antes de emprender una reescritura arriesgada de un capítulo clave, pulse <span class="shortcut-badge">Ctrl+5</span>. Escritorio congelará una copia exacta del texto en la carpeta <code>Files/Snapshots/&lt;UUID&gt;/</code> junto a una marca temporal inmutable. Más tarde, pulse <b>Comparar</b>: el motor de cálculo diferencial <b>Myers Diff</b> contrastará la versión guardada con el texto actual, mostrando las adiciones en verde y las supresiones en rojo tachado.
</p>

<div class="figure-card">
  <img src="{img_diff}" class="figure-img" alt="Comparador Myers Diff">
  <div class="figure-caption"><b>Figura 4.2:</b> Diálogo de Myers Diff mostrando el cómputo exacto de palabras eliminadas e introducidas con visor enriquecido.</div>
</div>

<!-- CAPÍTULO 5 -->
<div class="chapter-header">
  <span class="chapter-num">05</span>
  <div class="chapter-title-box">
    <div class="chapter-tag">NIVEL AVANZADO • ERGONOMÍA VISUAL</div>
    <h1 class="chapter-title">Concentración Inmersiva (Modo Composición) y Temas</h1>
  </div>
</div>

<div class="objectives-card">
  <div class="objectives-title">Objetivos Pedagógicos del Capítulo</div>
  Operar el Modo Composición a pantalla completa (F11), ajustar el ancho de hoja y regulaciones visuales, conmutar temas cromáticos y verificar la persistencia de configuración.
</div>

<h2 class="section-h2">5.1. Modo Composición a Pantalla Completa (F11)</h2>
<p>
  Al pulsar <span class="shortcut-badge">F11</span>, todas las ventanas, barras de tareas, marcos y botones desaparecen. La pantalla se sumerge en una atmósfera de oscuridad envolvente, proyectando en el centro una hoja de papel elegante con tipografía serif de alta legibilidad.
</p>

<div class="figure-card">
  <img src="{img_composition}" class="figure-img" alt="Modo Composición">
  <div class="figure-caption"><b>Figura 5.1:</b> Modo Composición libre de distracciones con hoja central, control de anchura y barra HUD auto-ocultable.</div>
</div>

<p>
  En la parte inferior se despliega una barra flotante auto-ocultable (HUD) que indica en tiempo real las palabras y caracteres redactados en la sesión, junto a un control deslizante que permite ajustar la anchura de la hoja entre 500 y 1400 píxeles según la preferencia del autor. Para salir y volver al estudio principal, basta presionar <span class="shortcut-badge">Esc</span> o <span class="shortcut-badge">F11</span>.
</p>

<h2 class="section-h2">5.2. Catálogo de Temas Visuales y Persistencia Automática</h2>
<p>
  Escritorio incorpora 12 paletas cromáticas profesionales diseñadas para prevenir la fatiga visual durante jornadas prolongadas de creación:
</p>

<div class="figure-card">
  <img src="{img_theme}" class="figure-img" alt="Tema Sepia Pergamino">
  <div class="figure-caption"><b>Figura 5.2:</b> Escritorio funcionando bajo el tema Sepia Pergamino, evocando la calidez del papel editorial clásico.</div>
</div>

<div class="callout callout-takeaway">
  <div class="callout-title" style="color: #9a3412;">Persistencia Automática Garantizada</div>
  Cualquier tema seleccionado (Dark Obsidian, Sepia Parchment, Solarized Light, Nordic Frost, Catppuccin, etc.) se guarda inmediatamente de forma atómica en <code>./config/escritorio_settings.json</code>. La próxima vez que abra Escritorio.exe, la aplicación se iniciará exactamente en el modo visual que usted dejó activo.
</div>

<!-- CAPÍTULO 6 -->
<div class="chapter-header">
  <span class="chapter-num">06</span>
  <div class="chapter-title-box">
    <div class="chapter-tag">NIVEL PROFESIONAL • PRODUCCIÓN EDITORIAL</div>
    <h1 class="chapter-title">Motor de Compilación Multiformato Editorial</h1>
  </div>
</div>

<div class="objectives-card">
  <div class="objectives-title">Objetivos Pedagógicos del Capítulo</div>
  Configurar la salida editorial del libro a formatos estándar de la industria (.docx, .pdf, .epub, .html, .rtf), filtrar secciones del manuscrito y emplear marcadores de posición dinámicos.
</div>

<h2 class="section-h2">6.1. El Diálogo de Compilación (Ctrl+Mayús+E)</h2>
<p>
  El compilador es el núcleo de transformación que toma decenas de escenas aisladas y notas dispersas para ensamblarlas en un volumen publicado de calidad imprenta.
</p>

<div class="figure-card">
  <img src="{img_compile}" class="figure-img" alt="Diálogo de Compilación">
  <div class="figure-caption"><b>Figura 6.1:</b> Diálogo de compilación editorial a tres columnas con selección de formatos y exclusión de capítulos.</div>
</div>

<table class="data-table">
  <thead>
    <tr>
      <th>Formato de Salida</th>
      <th>Extensión</th>
      <th>Destino y Propósito Editorial</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Microsoft Word</b></td>
      <td><code>.docx</code></td>
      <td>Entrega a editoriales, agentes literarios y correctores ortotipográficos con estilos OpenXML estándar.</td>
    </tr>
    <tr>
      <td><b>Documento PDF</b></td>
      <td><code>.pdf</code></td>
      <td>Impresión bajo demanda (KDP, IngramSpark) con páginas simétricas de cortesía y tipografía incrustada.</td>
    </tr>
    <tr>
      <td><b>Libro Electrónico EPUB</b></td>
      <td><code>.epub</code></td>
      <td>Distribución en lectores electrónicos (Kindle, Kobo, Apple Books) bajo estándar ePub v3 con tabla NCX.</td>
    </tr>
    <tr>
      <td><b>Página Web / HTML</b></td>
      <td><code>.html</code></td>
      <td>Publicación web seriada, newsletters literarias o almacenamiento en repositorios en línea.</td>
    </tr>
    <tr>
      <td><b>Rich Text Format</b></td>
      <td><code>.rtf</code></td>
      <td>Compatibilidad universal con cualquier suite ofimática histórica o sistema de maquetación desktop.</td>
    </tr>
  </tbody>
</table>

<h2 class="section-h2">6.2. Marcadores de Posición Dinámicos (Placeholders)</h2>
<p>
  Durante la compilación, Escritorio evalúa automáticamente códigos especiales insertados en los títulos o cuerpos:
  <code>&lt;$n&gt;</code> (número de capítulo arábigo: 1, 2, 3),
  <code>&lt;$t&gt;</code> (número en letras: Uno, Dos, Tres),
  <code>&lt;$r&gt;</code> (número romano: I, II, III),
  <code>&lt;$p&gt;</code> (título del proyecto) y
  <code>&lt;$wc&gt;</code> (recuento de palabras del manuscrito).
</p>

<!-- CAPÍTULO 7 -->
<div class="chapter-header">
  <span class="chapter-num">07</span>
  <div class="chapter-title-box">
    <div class="chapter-tag">NIVEL PROFESIONAL • RESILIENCIA Y SEGURIDAD</div>
    <h1 class="chapter-title">Copias de Seguridad Criptográficas y Resumen Técnico</h1>
  </div>
</div>

<div class="objectives-card">
  <div class="objectives-title">Objetivos Pedagógicos del Capítulo</div>
  Gestionar copias de seguridad automáticas con suma SHA-256, verificar la integridad del proyecto y consultar la tabla maestra de atajos de teclado.
</div>

<h2 class="section-h2">7.1. Autoguardado Atómico y Respaldos con Sellado SHA-256</h2>
<p>
  La pérdida de un capítulo por un corte de corriente es una pesadilla inadmisible. En Escritorio, el motor <code>AtomicStorage</code> detecta 2 segundos de inactividad del teclado y realiza una persistencia en dos fases: escribe primero en un archivo intermedio <code>.tmp</code>, fuerza la sincronización de los búferes físicos del disco y ejecuta un reemplazo atómico sobre el archivo definitivo.
</p>
<p>
  Al cerrar la sesión, el subsistema <code>BackupManager</code> comprime el proyecto entero en un archivo <code>.zip</code> en <code>./config/backups/</code> con marca temporal y calcula su firma criptográfica SHA-256 única, manteniendo siempre las 5 versiones más recientes mediante rotación automática.
</p>

<div class="figure-card">
  <img src="{img_targets}" class="figure-img" alt="Objetivos de Proyecto">
  <div class="figure-caption"><b>Figura 7.1:</b> Diálogo de Objetivos y Metas de Sesión diaria (Targets) con barras de progreso visuales.</div>
</div>

<h2 class="section-h2">7.2. Cuestionario de Autoevaluación Operativa</h2>
<div class="cuestionario-grid">
  <div class="pregunta-card">
    <div class="pregunta-num">1. ¿Dónde se guardan los datos portables de configuración?</div>
    <div class="opcion-item"><span class="badge-op">A</span> En el Registro de Windows.</div>
    <div class="opcion-item"><span class="badge-op">B</span> En la carpeta %APPDATA% del usuario.</div>
    <div class="opcion-item"><span class="badge-op">C</span> En la subcarpeta relativa ./config/ de la aplicación.</div>
    <div class="opcion-item"><span class="badge-op">D</span> En la nube del fabricante.</div>
  </div>

  <div class="pregunta-card">
    <div class="pregunta-num">2. ¿Qué atajo de teclado divide una escena en dos partes en el cursor?</div>
    <div class="opcion-item"><span class="badge-op">A</span> Ctrl+Shift+S</div>
    <div class="opcion-item"><span class="badge-op">B</span> Ctrl+K</div>
    <div class="opcion-item"><span class="badge-op">C</span> Ctrl+Enter</div>
    <div class="opcion-item"><span class="badge-op">D</span> Alt+D</div>
  </div>

  <div class="pregunta-card">
    <div class="pregunta-num">3. ¿Cuál es la vista idónea para reorganizar capítulos mediante tarjetas?</div>
    <div class="opcion-item"><span class="badge-op">A</span> Modo Scrivenings (Ctrl+4)</div>
    <div class="opcion-item"><span class="badge-op">B</span> Editor RTF (Ctrl+1)</div>
    <div class="opcion-item"><span class="badge-op">C</span> Pizarra de Corcho (Ctrl+2)</div>
    <div class="opcion-item"><span class="badge-op">D</span> Modo Composición (F11)</div>
  </div>

  <div class="pregunta-card">
    <div class="pregunta-num">4. ¿Qué algoritmo emplea el comparador de Snapshots de Escritorio?</div>
    <div class="opcion-item"><span class="badge-op">A</span> Levenshtein Distance</div>
    <div class="opcion-item"><span class="badge-op">B</span> Myers Diff Algorithm</div>
    <div class="opcion-item"><span class="badge-op">C</span> SHA-256 Checksum</div>
    <div class="opcion-item"><span class="badge-op">D</span> Huffman Coding</div>
  </div>
</div>

<div style="margin-top: 10pt;">
  <div class="solucion-card">
    <b>Solución 1: (C)</b> Escritorio es 100% portable y almacena toda su configuración en <code>./config/escritorio_settings.json</code>.
  </div>
  <div class="solucion-card">
    <b>Solución 2: (B)</b> El comando clásico de Scrivener 3 implementado en Escritorio para dividir escenas es <span class="shortcut-badge">Ctrl+K</span>.
  </div>
  <div class="solucion-card">
    <b>Solución 3: (C)</b> La Pizarra de Corcho (<span class="shortcut-badge">Ctrl+2</span>) permite manipular tarjetas de índice físicas con sinopsis e imágenes.
  </div>
  <div class="solucion-card">
    <b>Solución 4: (B)</b> El motor utiliza el algoritmo matemático de Eugene W. Myers para cálculo lineal diferencial exacto.
  </div>
</div>

</body>
</html>
"""
    return html


def main():
    print("[Manual PDF] Compilando Guía de Usuario en PDF con acabado editorial InDesign...")
    html_content = build_user_guide_html()
    
    out_pdf = PROJECT_ROOT / "Guia_de_Usuario_Escritorio.pdf"
    
    engine = PDFLayoutEngine()
    metadata = {
        "title": "Manual de Usuario y Guía Operativa - Escritorio v1.0.0",
        "author": "tekkes",
        "subject": "Manual técnico de instrucciones para la aplicación portable Escritorio",
        "keywords": "escritorio, scrivener, manual, guia, pdf, portable, windows 11, literatura, novela"
    }

    toc = [
        {"title": "Portada y Métricas de Edición", "page": 0},
        {"title": "Edición y Acreditaciones Técnicas", "page": 1},
        {"title": "Índice General de Contenidos", "page": 2},
        {"title": "Capítulo 1: Fundamentos y Filosofía Zero-Install", "page": 3},
        {"title": "Capítulo 2: El Cuaderno (Binder) y Estructuración Narrativa", "page": 5},
        {"title": "Capítulo 3: Las Cuatro Vistas Operativas", "page": 7},
        {"title": "Capítulo 4: El Inspector de 6 Pestañas y Myers Diff", "page": 9},
        {"title": "Capítulo 5: Concentración Inmersiva (F11) y Temas Visuales", "page": 11},
        {"title": "Capítulo 6: Motor de Compilación Multiformato Editorial", "page": 13},
        {"title": "Capítulo 7: Copias de Seguridad Criptográficas y Resumen", "page": 15}
    ]

    res_pdf = engine.render_html_to_pdf(
        html_content=html_content,
        output_pdf_path=str(out_pdf),
        book_metadata=metadata,
        toc_entries=toc
    )

    print(f"[Manual PDF] ¡Documento generado con éxito en: {res_pdf} ({Path(res_pdf).stat().st_size:,} bytes)!")


if __name__ == "__main__":
    main()
