# Guía Maestra de Ingeniería y Desarrollo: Aplicación «Escritorio» (Réplica Exacta y Portable de Scrivener para Windows 11 mediante Google Antigravity IDE y REA)

* **Directorio Raíz Oficial del Proyecto (Disco Local):** `M:\61_PROYECTOS_IA\18_ESCRITORIO`

* **Carpeta de Distribución Portable Generada:** `M:\61_PROYECTOS_IA\18_ESCRITORIO\dist\Escritorio_Portable_Win11`

* **Usuario de GitHub:** `tekkes`

* **Repositorio Oficial en GitHub:** `https://github.com/tekkes/ESCRITORIO` (`https://github.com/tekkes/ESCRITORIO.git`)

## Índice de Contenidos

1. [Análisis Exhaustivo de Funcionalidades, Capacidades y Arquitectura de Scrivener](#1-análisis-exhaustivo-de-funcionalidades-capacidades-y-arquitectura-de-scrivener)

2. [Especificación Completa de Requisitos de Desarrollo Software (SRS) para «Escritorio»](#2-especificación-completa-de-requisitos-de-desarrollo-software-srs-para-escritorio)

3. [Investigación e Implementación Técnica de Estilos, Temas y Modos Visuales](#3-investigación-e-implementación-técnica-de-estilos-temas-y-modos-visuales)

4. [Configuración Paso a Paso de Google Antigravity IDE con MCP de REA (Morluto)](#4-configuración-paso-a-paso-de-google-antigravity-ide-con-mcp-de-rea-morluto)

5. [Gestión de Control de Versiones, Integración con GitHub (tekkes/ESCRITORIO) y Flujo DevSecOps](#5-gestión-de-control-de-versiones-integración-con-github-tekkesescritorio-y-flujo-devsecops)

6. [Catálogo Maestro Secuencial de Prompts para Google Antigravity IDE](#6-catálogo-maestro-secuencial-de-prompts-para-google-antigravity-ide)

7. [Arquitectura de Agentes de Validación y Verificación Adversarial (Red Team Loop)](#7-arquitectura-de-agentes-de-validación-y-verificación-adversarial-red-team-loop)

8. [Instrucciones Rápidas para Exportar esta Guía a PDF](#8-instrucciones-rápidas-para-exportar-esta-guía-a-pdf)

## 1. Análisis Exhaustivo de Funcionalidades, Capacidades y Arquitectura de Scrivener

A partir de la inspección profunda de la documentación oficial de *Literature & Latte*, los tutoriales especializados de *Scrivener.es*, los flujos audiovisuales de formación y el análisis estructural de binarios de Scrivener 3 para Windows (basado en el framework C++/Qt), se desglosan la totalidad de sus sistemas y capacidades operativas que serán clonadas en **Escritorio**.

### 1.1. Filosofía del Contenedor de Proyecto y Estructura Física

A diferencia de los procesadores lineales tradicionales, Scrivener opera sobre un paquete de directorio estructurado (`.scriv` en el original, que en nuestra aplicación será `.escr` manteniendo compatibilidad directa con `.scriv`):

* **Archivo de Índice Maestro (`.scrivx` / `.escrx`):** Un documento XML jerárquico que mapea identificadores únicos globales (UUID) de cada elemento del proyecto, su jerarquía, metadatos, estados de compilación, etiquetas, objetivos y vínculos.

* **Subdirectorio `Files/Data/<UUID>/`:** Almacenamiento atómico donde cada escena, capítulo o nota vive en su propia subcarpeta aislada:

  * `content.rtf`: El texto enriquecido principal de la escena o documento.

  * `synopsis.txt`: El resumen en texto plano mostrado en las fichas del corcho y el esquema.

  * `notes.rtf`: Notas específicas asociadas al documento en el Inspector.

  * `content.comments`: Archivo XML con comentarios en margen y notas al pie vinculadas a rangos de texto.

* **Subdirectorio `Snapshots/<UUID>/`:** Almacena copias históricas fechadas (`.rtf`) generadas manual o automáticamente antes de cambios destructivos.

* **Subdirectorio `Settings/`:** Configuraciones locales del proyecto, formatos de compilación personalizados y estado de la interfaz (posición de divisores, pestañas abiertas, selecciones activas).

### 1.2. El Cuaderno (*Binder*) y Gestión Documental Jerárquica

El *Binder* es el árbol neurálgico lateral izquierdo que gobierna toda la obra:

* **Nodos Raíz Especiales e Inmutables:**

  1. **Manuscrito / Borrador (*Draft / Manuscript*):** Admite exclusivamente documentos de texto y carpetas. Es el objetivo primario del motor de compilación.

  2. **Investigación (*Research*):** Admite cualquier activo digital (PDF, imágenes PNG/JPG/WebP/SVG, archivos de audio WAV/MP3/AAC, vídeo MP4, páginas web archivadas MHTML/HTML y hojas de cálculo).

  3. **Papelera (*Trash*):** Almacena elementos eliminados conservando su jerarquía original hasta el vaciado explícito.

* **Operaciones de Estructura Narrativa:**

  * *Drag & Drop* libre con reordenación en tiempo real de capítulos y escenas.

  * **Agrupar (*Group*)** selecciones múltiples en una nueva carpeta contenedora.

  * **Desagrupar (*Ungroup*)** carpetas promoviendo sus hijos al nivel superior.

  * **Dividir documento (*Split at Selection* / `Ctrl+K`):** Parte un documento en dos nodos independientes en la posición exacta del cursor, o utiliza el texto seleccionado como título automático del nuevo subdocumento (*Split with Selection as Title*).

  * **Fusionar documentos (*Merge* / `Ctrl+Shift+M`):** Concatena virtual o físicamente múltiples nodos en un único documento, preservando sus notas y sinopsis.

  * **Carpetas como textos y Textos como carpetas:** En Scrivener, cualquier carpeta puede contener texto propio en el editor, y cualquier archivo de texto puede tener subdocumentos hijos anidados.

* **Colecciones (*Collections*):**

  * **Colecciones Estándar:** Listas arbitrarias y ordenables manualmente de documentos (ej. "Escenas con el personaje X") sin alterar su posición real en el *Binder*.

  * **Colecciones de Búsqueda Guardada (*Saved Search Collections*):** Pestañas dinámicas que se actualizan automáticamente según reglas de consulta (por palabra clave, etiqueta, estado o metadato).

* **Plantillas de Documento e Iconografía:**

  * Carpeta especial de *Plantillas* (*Templates*) para instanciar fichas de Personaje (*Character Sheets*) o fichas de Ubicación (*Location Sheets*) preconfiguradas.

  * Sistema de asignación de iconos vectoriales personalizados a cualquier carpeta o archivo (`Change Icon`), incluyendo iconos basados en texto o emojis.

### 1.3. Los Tres Modos de Vista de Grupo (*Group View Modes*)

Cuando el usuario selecciona una carpeta o un conjunto de documentos en el *Binder*, el panel central puede alternar instantáneamente entre tres paradigmas de trabajo:

#### A. Modo *Scrivenings* (Vista de Manuscrito Continuo)

* Concatena en tiempo real todos los archivos hijos de una carpeta en un único flujo de edición continua.

* Muestra divisores horizontales configurables (líneas punteadas, títulos integrados o saltos de página) entre cada subdocumento.

* Permite editar cualquier fragmento en el flujo continuo y guarda los cambios de forma transparente e individual en cada archivo `content.rtf` correspondiente sin que el usuario perciba la fragmentación física.

#### B. El Corcho (*Corkboard*)

* Representa cada subdocumento como una tarjeta de índice física (*Index Card*) dispuesta sobre un tablero.

* **Anatomía de la Tarjeta:** Cabecera con icono de documento, numeración opcional, título editable, cuerpo con texto de la sinopsis (con rayado opcional de libreta) o imagen representativa (*Card Image*), sello diagonal de Estado (*Stamp*), pin o borde lateral con el color de Etiqueta (*Label*), e indicadores inferiores de palabras clave (*Keywords*).

* **Tres Submodos de Disposición:**

  1. **Rejilla (*Grid Mode*):** Tarjetas ordenadas secuencialmente con control deslizante de tamaño, proporción (*Aspect Ratio*: $3 \times 5$, $4 \times 6$, etc.), espaciado y número de tarjetas por fila. Reordenar tarjetas reordena el *Binder*.

  2. **Forma Libre (*Freeform Mode*):** Lienzo bidimensional infinito donde el usuario posiciona las tarjetas en cualquier coordenada $(x, y)$ sin alterar el orden del *Binder*, con opción de "Confirmar orden libre al Binder" (*Commit Freeform Order*).

  3. **Apilado por Etiqueta (*Arrange by Label / Stacked Corkboard*):** Organiza las tarjetas en carriles verticales u horizontales (*Swimlanes*) según los hilos narrativos, puntos de vista (POV) o líneas temporales representadas por las etiquetas.

#### C. El Esquema (*Outliner*)

* Vista matricial avanzada tipo hoja de cálculo jerárquica con expansión y contracción de ramas.

* **Columnas Configurables:** Título y Sinopsis, Etiqueta (*Label*), Estado (*Status*), Tipo de Sección (*Section Type*), Recuento de palabras (*Word Count*), Recuento total acumulado (*Total Word Count*), Caracteres, Objetivo de palabras (*Target*), Barra de progreso visual coloreada (de rojo a verde según cumplimiento de objetivo), Fecha de creación, Fecha de modificación, Incluir en Compilación (*Include in Compile*) y todas las columnas de Metadatos Personalizados.

* Ordenación ascendente/descendente haciendo clic en cualquier cabecera de columna sin destruir el orden real del *Binder* (con opción de aplicar el orden).

### 1.4. El Editor de Texto Enriquecido y Pantalla Dividida (*Split Editor*)

* **División Cuádruple y Dual (*Split Screen*):** Capacidad de dividir el área central vertical u horizontalmente (hasta 4 paneles independientes en vistas avanzadas).

* **Sincronización entre Paneles:**

  * *Navigate Selection Affects Other Pane:* Hacer clic en una tarjeta del Corcho en el Panel A carga automáticamente su texto completo en el Panel B.

  * *QR (Quick Reference) Panels:* Ventanas flotantes ligeras e independientes para abrir múltiples documentos de investigación, fotos o capítulos simultáneamente en varios monitores.

* **Capacidades Tipográficas y de Edición:**

  * Motor RTF completo: fuentes, estilos de párrafo y carácter, resaltadores multimodo, listas numeradas/viñetas, tablas anidadas e inserción de imágenes vinculadas o incrustadas.

  * **Modo Vista de Página (*Page View*):** Simulación de folios físicos con márgenes reales en pantalla frente al modo continuo de ancho fijo o adaptable.

  * **Desplazamiento de Máquina de Escribir (*Typewriter Scrolling*):** Mantiene la línea activa de escritura anclada verticalmente en el centro (o tercio) de la pantalla para evitar fatiga visual cervical.

  * **Foco de Línea / Párrafo / Oración (*Focus Mode*):** Atenúa todo el texto del editor excepto la oración o párrafo que se está redactando en ese instante.

  * **Foco Lingüístico (*Linguistic Focus*):** Analizador morfosintáctico que resalta dinámicamente solo los diálogos hablados, adverbios, adjetivos, verbos o conjunciones para pulir el estilo literario.

  * **Modo Guion Literario (*Scriptwriting Mode*):** Conmutador (`Ctrl+8`) que transforma el tabulador y la tecla `Enter` para formatear automáticamente Encabezado de Escena (*Scene Heading*), Acción, Personaje, Paréntesis (*Parenthetical*), Diálogo y Transición según estándares de Hollywood (compatible con *Final Draft* `.fdx`), teatro o cómic.

### 1.5. El Inspector Lateral Derecho (6 Pestañas Especializadas)

El Inspector proporciona control granular sobre el documento activo:

1. **Sinopsis e Imagen (*Synopsis & Main Card*):** Editor del resumen del documento o conmutador para usar una fotografía como portada visual de la escena en el Corcho.

2. **Notas del Documento (*Notes*):** Bloc de notas RTF privado adjunto a la escena.

3. **Marcadores (*Bookmarks*):**

   * *Document Bookmarks:* Enlaces rápidos a documentos de referencia específicos para esa escena.

   * *Project Bookmarks:* Referencias globales accesibles desde cualquier punto del libro, con previsualización integrada y edición *in-situ* dentro del propio Inspector.

4. **Metadatos (*Metadata*):**

   * Propiedades generales: *Include in Compile*, *Section Type* (asignado por estructura o manualmente).

   * *Custom Metadata:* Campos definidos por el usuario de tipo Texto, Casilla de verificación (*Checkbox*), Lista desplegable (*List*) o Fecha (*Date*).

   * *Keywords:* Sistema de etiquetas múltiples jerárquicas con código de color asignables por arrastre.

5. **Instantáneas (*Snapshots*):**

   * Toma de fotografías del estado del texto (`Ctrl+5`) con sonido opcional de obturador de cámara.

   * **Comparador Diferencial (*Compare*):** Muestra en tiempo real qué palabras se añadieron (subrayado azul/verde) y cuáles se eliminaron (tachado rojo) entre la versión actual y cualquier instantánea histórica, a nivel de palabra, cláusula o párrafo, con botón de *Rollback* seguro.

6. **Comentarios y Notas al Pie (*Comments & Footnotes*):**

   * *Inspector Comments:* Cajas de color ancladas a fragmentos de texto (con autor y fecha).

   * *Inline Annotations:* Burbujas de texto dentro del propio flujo del documento que se omiten al compilar.

   * *Inspector Footnotes & Inline Footnotes:* Notas al pie que el compilador convierte automáticamente en notas a pie de página reales o notas al final del libro (*Endnotes*).

### 1.6. Modo Composición Libre de Distracciones (*Composition Mode*)

* Oculta por completo la interfaz de Windows 11, barras de tareas y paneles laterales (`F11`).

* Permite personalizar el ancho del papel (*Paper Width*), posición horizontal del folio, escala de zoom, opacidad del fondo (*Background Fade*) desde negro absoluto hasta mostrar una imagen o textura de fondo personalizada.

* Panel de control flotante auto-ocultable en el borde inferior para controlar ancho de papel, zoom, inspector rápido y acceso a documentos sin salir de pantalla completa.

### 1.7. Herramientas de Productividad, Estadísticas y Objetivos

* **Objetivos del Proyecto (*Project Targets*):**

  * Meta total del manuscrito (*Draft Target*) con fecha límite (*Deadline*) y cálculo automático de cuántas palabras por día se deben escribir según los días de la semana seleccionados como laborables.

  * Meta de sesión (*Session Target*) que se reinicia cada día o al cerrar el programa.

* **Estadísticas (*Statistics*):** Tiempo estimado de lectura, recuento exacto de palabras, caracteres, páginas impresas estimadas y páginas de bolsillo (*Paperback pages*), además de un analizador de **Frecuencia de Palabras (*Word Frequency*)** para detectar muletillas y repeticiones léxicas.

* **Generador de Nombres (*Name Generator*):** Base de datos integrada de nombres y apellidos por origen étnico, país, época histórica, género, aliteración y nivel de oscuridad.

* **Scratchpad (Bloc Flotante Global):** Ventana siempre disponible a nivel de sistema operativo (incluso cuando se navega por internet fuera del programa) para capturar ideas al vuelo y enviarlas directamente al *Binder* de cualquier proyecto abierto.

* **Sistema de Copias de Seguridad Automáticas (*Automatic Backups*):** Empaquetado automático en `.zip` al abrir/cerrar proyectos o manualmente, con rotación de las últimas $N$ copias verificadas.

### 1.8. El Motor de Compilación (*Compile Engine*)

La joya arquitectónica de Scrivener 3: desacopla por completo el formato de escritura del formato de publicación:

* **Tipos de Sección (*Section Types*) vs. Diseños de Sección (*Section Layouts*):**

  * Cada documento del *Binder* tiene un significado semántico (ej. "Carpeta de Parte", "Carpeta de Capítulo", "Escena de Texto", "Portadilla").

  * En el diálogo de Compilación (`Ctrl+Shift+E`), el usuario vincula mediante *Assign Section Layouts* cómo quiere que se maquete cada tipo semántico (ej. "Añadir prefijo 'CAPÍTULO <\$t>' en versalitas, ocultar título de carpeta y cambiar fuente del cuerpo a Garamond 11pt").

* **Variables de Marcador de Posición (*Placeholders*):** Sistema de etiquetas dinámicas evaluadas durante la compilación: `<$n>` (1, 2, 3), `<$R>` (I, II, III), `<$t>` (Uno, Dos, Tres), `<$W>` (UNO, DOS, TRES), `<$title>`, `<$synopsis>`, `<$projecttitle>`, `<$author>`, `<$wc>` (recuento de palabras).

* **Separadores Automáticos:** Inserción automática de líneas en blanco, saltos de página o símbolos personalizados (como `* * *` o `#`) entre escenas contiguas.

* **Formatos de Salida Nativos:** Impresión directa, PDF con marcas de corte, Microsoft Word (`.docx`), Rich Text (`.rtf`), Libros Electrónicos (`.epub` versiones 2 y 3 con tabla de contenidos dinámica y validación Kindle), Final Draft (`.fdx`), Fountain (`.fountain`), MultiMarkdown (`.mmd`), LaTeX (`.tex`), HTML y Texto Plano (`.txt`).

## 2. Especificación Completa de Requisitos de Desarrollo Software (SRS) para «Escritorio»

Para garantizar que **Escritorio** sea un binario único (`Escritorio.exe`), ultrarrápido en arranque ($< 250\text{ ms}$), ligero en memoria y 100% portable en Windows 11 —capaz de copiarse junto con su carpeta a cualquier otro ordenador con Windows 11 y ejecutarse directamente sin instalar nada—, se establece la siguiente arquitectura e ingeniería de requisitos dentro de `M:\61_PROYECTOS_IA\18_ESCRITORIO`.

### 2.1. Pila Tecnológica Recomendada para Portabilidad Absoluta

* **Lenguaje y Framework Principal:**

  * **Opción A (Nativa Clásica / Paridad Binaria con Scrivener):** **C++20 con Qt 6.8+ compilado estáticamente (MSVC 2022 / Clang-CL)**. Dado que Scrivener 3 en Windows está construido sobre Qt (como evidencian sus clases internas `SCRInspectorSynopsis`, `SCRIndexCardWidget` y hojas de estilo `.qss`), usar C++/Qt 6 enlazado de forma estática genera un único archivo `Escritorio.exe` que interpreta nativamente las hojas QSS y paletas de Scrivener sin requerir DLLs externas de Qt ni el instalador de VC++ Redistributable (`/MT`).

  * **Opción B (Moderna / Ultra-ligera de Memoria):** **Rust + Tauri v2 (con WebView2 nativo de Windows 11)** o **Rust + Slint/Iced**. Dado que Windows 11 incluye el motor WebView2 preinstalado de fábrica en el sistema operativo, un binario en Rust compila en un único `.exe` de apenas $8\text{ MB}$ a $14\text{ MB}$, con backend multihilo en Rust para indexación instantánea, compilación de documentos y compatibilidad mediante un transpilador interno de `.scrtheme` (QSS/XML) a variables CSS modernas.

  * *Decisión Arquitectónica para la Guía:* Implementaremos una arquitectura en **C++20 / Qt 6 Estático con CRT estático (`/MT`) (o Rust con CRT estático `+crt-static`)** diseñada específicamente para producir un **único ejecutable monolítico `Escritorio.exe`** acompañado de su carpeta local `./config/` para portabilidad total entre ordenadores con Windows 11.

### 2.2. Requisitos Funcionales (RF)

| ID | Módulo | Descripción Técnica del Requisito | Prioridad | 
| ----- | ----- | ----- | ----- | 
| **RF-01** | Motor de Proyecto | Lectura y escritura nativa de contenedores `.escr` y compatibilidad total de importación/apertura directa de proyectos `.scriv` de Scrivener 3 (parsing del árbol XML `.scrivx` y subcarpetas UUID). | Crítica | 
| **RF-02** | Binder Jerárquico | Árbol infinito (`TreeView`) con soporte para drag-and-drop múltiple, iconos SVG/PNG de $16 \times 16\text{ px}$ personalizables, etiquetas de color en el fondo de fila o punto lateral, carpetas de Borrador, Investigación y Papelera, y Colecciones dinámicas. | Crítica | 
| **RF-03** | Modo Scrivenings | Renderizado virtualizado de múltiples documentos RTF/Markdown en un único flujo de edición continua sin latencia, manteniendo el cursor y el historial `Undo/Redo` independiente por subdocumento. | Crítica | 
| **RF-04** | Pizarra de Corcho | Lienzo acelerado por GPU que renderiza tarjetas con aspecto configurable, sellos diagonales con transparencia alfa, pines de color, modo rejilla, modo libre $(x, y)$ y modo apilado por etiquetas (*swimlanes*). | Crítica | 
| **RF-05** | Esquema (Outliner) | Tabla jerárquica multinivel con columnas ordenables en tiempo real, edición *inline* de sinopsis y metadatos, y barras de progreso cromáticas calculadas según la fórmula $P = \min\left(100, \frac{\text{Palabras}_{\text{actual}}}{\text{Palabras}_{\text{meta}}} \times 100\right)$. | Crítica | 
| **RF-06** | Editor y Split View | División horizontal/vertical hasta 4 paneles independientes, bloqueo de editor (*Lock in Place*), modo Vista de Página física, *Typewriter Scrolling*, resaltado morfosintáctico en español e inglés, y modo Guion (*Scriptwriting*). | Crítica | 
| **RF-07** | Inspector 6-en-1 | Panel colapsable con las 6 vistas (Sinopsis/Imagen, Notas, Marcadores de documento/proyecto, Metadatos y Keywords, Instantáneas con motor Diff visual palabra por palabra, y Comentarios/Notas al pie). | Crítica | 
| **RF-08** | Motor de Compilación | Compilador asíncrono multihilo que procesa *Section Types*, aplica *Section Layouts*, evalúa expresiones regulares y variables `<$n>`, `<$t>`, etc., y genera archivos `.docx`, `.pdf`, `.epub`, `.rtf`, `.fdx`, `.md`, `.tex` y `.html` sin depender de MS Word instalado. | Crítica | 
| **RF-09** | Modos Visuales y Temas | Soporte nativo para el Modo Minimalista por defecto, Modo Oscuro, Modo Solarizado (Claro y Oscuro), Modo Sepia, Temas Modernos Compactos y un Editor Visual de Temas con importación/exportación de paquetes `.scrtheme` y `.escrtheme`. | Crítica | 
| **RF-10** | Herramientas Auxiliares | Modo Composición a pantalla completa (`F11`), Objetivos de Proyecto/Sesión con velocímetro visual, Frecuencia de Palabras, Generador de Nombres multilingüe, *Scratchpad* global y Backups ZIP automáticos con suma de verificación SHA-256. | Alta | 

### 2.3. Requisitos No Funcionales (RNF) y Portabilidad Total en Windows 11

* **RNF-01 (Portabilidad Estricta "Copy & Run" en cualquier PC con Windows 11):** La aplicación compilada se alojará en `M:\61_PROYECTOS_IA\18_ESCRITORIO\dist\Escritorio_Portable_Win11\`. Contendrá el fichero ejecutable `Escritorio.exe` (enlazado estáticamente sin dependencia de `vcruntime140.dll` externo) y la subcarpeta `./config/`. Al copiar esta carpeta a un pendrive USB o a cualquier otro ordenador con Windows 11, ejecutará directamente al hacer doble clic sin pedir permisos de Administrador (UAC `asInvoker`), sin escribir claves en el Registro de Windows (`HKEY_CURRENT_USER`) ni archivos ocultos en `%APPDATA%`. Todas las rutas de proyectos recientes y diccionarios dentro de `./config/` se guardarán como **rutas relativas** si están dentro del directorio portable.

* **RNF-02 (Rendimiento y Arranque Frío):** El tiempo de arranque en frío (*cold start*) en Windows 11 debe ser $\le 250\text{ ms}$. La apertura de un manuscrito de $300\,000$ palabras distribuido en $500$ nodos debe completarse en $< 500\text{ ms}$ mediante carga diferida (*lazy loading*) de archivos RTF.

* **RNF-03 (Densidad Visual y Ergonomía de Espacio):** Los botones de la barra de herramientas, cabeceras de editor, iconos del *Binder* y etiquetas de estado utilizarán micro-iconografía vectorial SVG ($14\text{ px}$ a $16\text{ px}$) y tipografía compacta (`Segoe UI Variable Small` a $11\text{ pt}$ / $12\text{ px}$), maximizando el área útil de lectura y escritura.

* **RNF-04 (Integración con Windows 11 Fluent Design):** Soporte para esquinas redondeadas nativas de Windows 11 (`DWMWA_WINDOW_CORNER_PREFERENCE`), barra de título integrada opcional para ganar $32\text{ px}$ verticales, y soporte de *Snap Layouts* al pasar el cursor sobre el botón de maximizar.

* **RNF-05 (Seguridad de Datos y Guardado Atómico):** Cada escritura de un documento `content.rtf` o del índice `.escrx` debe realizarse primero en un fichero temporal `.tmp` y renombrarse atómicamente mediante la API de Windows `MoveFileExW` con `MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH`, impidiendo la corrupción de datos ante un apagado súbito o extracción de unidad.

## 3. Investigación e Implementación Técnica de Estilos, Temas y Modos Visuales

En Scrivener 3 para Windows, los estilos y los temas son dos subsistemas completamente distintos que debemos replicar y superar en **Escritorio**.

### 3.1. Subsistema de Estilos Tipográficos (*Text Styles*)

A diferencia de Microsoft Word (donde todo párrafo tiene el estilo "Normal"), Scrivener utiliza el concepto de **"Sin Estilo" (*No Style*)** para el 95% del cuerpo del texto:

1. **Arquitectura "No Style":** El texto normal no tiene una etiqueta de estilo rígida asociada; adopta el formato por defecto del editor y permite que el Compilador lo transforme libremente a cualquier tipografía en el libro final.

2. **Estilos Semánticos (Párrafo, Carácter o Ambos):** Solo se aplican estilos explícitos a elementos excepcionales: *Citas en bloque (Block Quote)*, *Títulos*, *Epígrafes*, *Versos/Poesía* o *Código*.

3. **Almacenamiento Técnico:** Los estilos del proyecto se guardan en `<Proyecto>.escr/Settings/styles.xml` definiendo atributos RTF (`\fs`, `\fi`, `\li`, `\sa`, `\sb`) y un identificador único de estilo que el Compilador intercepta para aplicar reglas específicas según el formato de salida.

### 3.2. Ingeniería Inversa del Formato `.scrtheme` de Scrivener 3 en Windows

Nuestra investigación sobre la arquitectura interna de Scrivener 3 en Windows revela que un archivo `.scrtheme` es en realidad un **contenedor comprimido ZIP** que aloja cuatro archivos fundamentales:

1. **`<ThemeName>.xml` (Manifiesto):** Define el nombre del tema, el estilo base del motor gráfico (`Fusion` o `WindowsVista`) y las referencias a los archivos internos.

2. **`<ThemeName>.pal` (Paleta Base):** Define los roles cromáticos globales de la interfaz (`Window`, `WindowText`, `Base`, `AlternateBase`, `ToolTipBase`, `Text`, `Button`, `ButtonText`, `BrightText`, `Highlight`, `HighlightedText`, `Link`).

3. **`<ThemeName>.prefs` (Preferencias de Color de Componentes):** Archivo INI/XML que controla los colores específicos de elementos internos de Scrivener: color del lienzo del editor, color de fondo del modo composición, color del corcho, líneas de las fichas de índice, colores de la regla (*Ruler*) y colores del texto invisible.

4. **`<ThemeName>.qss` (Hoja de Estilos Qt Style Sheet):** Un archivo similar a CSS que aplica reglas de diseño granular a los *widgets* específicos (bordes de botones, *scrollbars* minimalistas, flechas de expansión del *Binder*, pestañas del Inspector y *padding* de barras de herramientas).

### 3.3. Catálogo de Modos de Visualización Requeridos en «Escritorio»

**Escritorio** implementará un motor de temas dual capaz de cargar archivos `.scrtheme` originales de la comunidad de Scrivener y sus propios temas nativos `.escrtheme` de alta densidad visual. Incluirá de fábrica los siguientes modos conmutables en caliente:

#### 1. Modo Minimalista por Defecto (*Default Minimalist Zen*)

* **Estética:** Limpieza extrema inspirada en papel neutro cálido, sin bordes gruesos ni biseles antiguos.

* **Compactación:** Barras de herramientas de $28\text{ px}$ de alto, iconos vectoriales monocromáticos de trazo fino ($1.5\text{ px}$), etiquetas de texto ocultables o reducidas a micro-píldoras (*micro-badges*) de $10\text{ px}$.

* **Paleta:** Fondo general `#F7F7F5`, Binder `#EFEFEC`, Hoja del Editor `#FFFFFF`, Texto `#1E1E1E`, Acento `#2B579A`.

#### 2. Modo Oscuro Profesional (*Modern Carbon Dark*)

* **Estética:** Diseñado para sesiones nocturnas prolongadas evitando el negro puro (`#000000`) que produce astigmatismo halation en pantallas OLED/IPS.

* **Paleta:** Fondo de ventana `#18191A`, Binder e Inspector `#202124`, Hoja del Editor `#141517`, Texto principal `#E4E6EB`, Texto secundario `#9AA0A6`, Acento `#60A5FA`, Tarjetas del Corcho `#282A2E` con texto `#E4E6EB`.

#### 3. Modo Solarizado (*Solarized Dark & Solarized Light* - Estándar Ethan Schoonover)

Implementación matemáticamente exacta de la paleta simétrica CIELAB de Ethan Schoonover:

* **Solarized Dark:**

  * Base03 (Fondo Editor): `#002B36` | Base02 (Binder/Inspector): `#073642`

  * Base0 (Texto Principal): `#839496` | Base1 (Texto Enfatizado): `#93A1A1`

  * Acentos: Amarillo `#B58900`, Naranja `#CB4B16`, Cian `#2AA198`, Azul `#268BD2`.

* **Solarized Light:**

  * Base3 (Fondo Editor): `#FDF6E3` | Base2 (Binder/Inspector): `#EEE8D5`

  * Base00 (Texto Principal): `#657B83` | Base01 (Texto Enfatizado): `#586E75`.

#### 4. Modo Sepia Literario (*Classic Parchment Sepia*)

* **Estética:** Emulación cálida de papel libro clásico y tinta estilográfica, ideal para lectura y corrección de borradores largos reduciendo la emisión de luz azul en un $65\%$.

* **Paleta:** Hoja del Editor `#F4ECD8`, Binder `#E8DEC3`, Inspector `#EDE4CC`, Texto Tinta `#3B2F2F`, Líneas de fichas del Corcho `#D5C7A3`, Acento Terracota `#8C4A27`.

#### 5. Modos Predefinidos Modernos Adicionales

* **Nordic Frost (Nord):** Tonos árticos azulados (`#2E3440`, `#3B4252`, `#ECEFF4`, acento `#88C0D0`).

* **Catppuccin Mocha:** Tonos pastel oscuros suaves de alto confort visual (`#1E1E2E`, `#181825`, `#CDD6F4`, acento `#CBA6F7`).

* **e-Ink High Contrast:** Emulación de pantalla de tinta electrónica en escala de grises de alto contraste para máxima legibilidad diurna.

#### 6. Motor de Temas Configurables por el Usuario y Diseño Ultra-Compacto

* **Editor Visual de Temas en Vivo (*Live Theme Studio*):** Panel interactivo dentro de `Opciones > Apariencia` que permite al usuario modificar con selectores de color RGB/HSL/HEX cada componente, cambiar la tipografía de la interfaz, ajustar el radio de redondeo de las tarjetas y guardar su creación como un nuevo preajuste o exportarlo en `.escrtheme` / `.scrtheme`.

* **Sistema de Densidad de Interfaz (*UI Density Toggle*):** Tres niveles seleccionables:

  * *Ultra-Compacto:* Iconos de $14\text{ px}$, filas del *Binder* de $20\text{ px}$ de alto, etiquetas reducidas a puntos de color de $6\text{ px}$ o micro-píldoras con iniciales, liberando hasta un $22\%$ más de superficie de pantalla que Scrivener original.

  * *Compacto (Por defecto):* Iconos de $16\text{ px}$, filas de $24\text{ px}$, etiquetas con texto abreviado.

  * *Confort:* Iconos de $18\text{ px}$, filas de $28\text{ px}$ para pantallas táctiles o 4K sin escalado.

## 4. Configuración Paso a Paso de Google Antigravity IDE con MCP de REA (Morluto)

Dado que ya utilizaste **REA (`morluto/rea`)** en este equipo para el desarrollo previo de **ODISEA**, el entorno cuenta con las dependencias base instaladas. A continuación se detalla cómo conectar REA y el repositorio `https://github.com/tekkes/ESCRITORIO` en tu carpeta ya creada `M:\61_PROYECTOS_IA\18_ESCRITORIO` dentro de **Google Antigravity IDE**.

### 4.1. Verificación y Actualización del Entorno Local de REA

1. Abre una terminal de **PowerShell 7** en Windows 11.

2. Verifica la instalación existente que usaste en ODISEA y actualízala a la última versión estable:

   ```
   # Comprobar versión actual instalada desde el proyecto ODISEA
   rea --version
   
   # Actualizar REA globalmente
   rea update
   # Alternativamente si se instaló vía npm global:
   npm install --global rea-agents@latest
   
   ```

3. Verifica qué proveedores de ingeniería inversa nativos están activos en tu máquina (Ghidra, Rizin, IDA o GNU objdump):

   ```
   rea doctor
   
   ```

### 4.2. Apertura del Espacio de Trabajo en Google Antigravity IDE

1. Abre **Google Antigravity IDE** y selecciona **File > Open Folder...** apuntando a tu carpeta:
   `M:\61_PROYECTOS_IA\18_ESCRITORIO`

2. Abre la terminal integrada de Antigravity IDE y crea las subcarpetas de configuración local de agentes dentro del proyecto:

   ```
   Set-Location -Path "M:\61_PROYECTOS_IA\18_ESCRITORIO"
   New-Item -ItemType Directory -Force -Path ".agents\rules", ".agents\workflows"
   
   ```

### 4.3. Conexión del Servidor MCP de REA y GitHub (`tekkes/ESCRITORIO`) en Google Antigravity IDE

#### Método 1: Configuración Automática mediante el Asistente de REA

Ejecuta en la terminal integrada de Antigravity IDE (situada en `M:\61_PROYECTOS_IA\18_ESCRITORIO`):

```
npx rea-agents@latest setup

```

Selecciona el perfil compatible con **Antigravity / Gemini CLI**, aprueba la inyección del servidor MCP y las reglas basadas en evidencias, y reinicia el panel del Agente.

#### Método 2: Configuración Manual Explícita en `.agents/mcp_config.json`

1. En **Google Antigravity IDE**, abre o crea el archivo:
   `M:\61_PROYECTOS_IA\18_ESCRITORIO\.agents\mcp_config.json`

2. Inserta la siguiente configuración que conecta **REA MCP** y **GitHub MCP** fijando el directorio de trabajo exacto `M:\61_PROYECTOS_IA\18_ESCRITORIO` y tu cuenta `tekkes`:

```
{
  "mcpServers": {
    "rea": {
      "command": "npx",
      "args": ["-y", "rea-agents@latest", "mcp"],
      "cwd": "M:\\61_PROYECTOS_IA\\18_ESCRITORIO",
      "env": {
        "REA_MAX_OUTPUT_MIB": "4",
        "REA_EVIDENCE_STRICT": "true",
        "REA_PLATFORM": "win32-x64",
        "REA_WORKSPACE": "M:\\61_PROYECTOS_IA\\18_ESCRITORIO"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "cwd": "M:\\61_PROYECTOS_IA\\18_ESCRITORIO",
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<TU_TOKEN_GITHUB_DE_TEKKES_AQUI>",
        "GITHUB_OWNER": "tekkes",
        "GITHUB_REPO": "ESCRITORIO"
      }
    }
  },
  "permissions": {
    "allow": [
      "mcp(rea/*)",
      "mcp(github/*)"
    ]
  }
}

```

3. Presiona `Ctrl + ,` en Antigravity IDE para abrir **Agent Settings > Customizations > Installed MCP Servers** y haz clic en **Refresh**. Comprueba que el indicador junto a `rea` y `github` aparece en color **Verde (Active)**.

### 4.4. Plugins y Reglas de Agente Necesarias en Antigravity IDE

1. **Extensiones del IDE:**

   * *C/C++ Extension Pack / clangd* (o *rust-analyzer* según el motor compilado elegido).

   * *CMake Tools* y *Qt Tools* (para previsualización de QSS/UI).

   * *GitLens / GitHub Pull Requests* para trazabilidad visual de ramas en `tekkes/ESCRITORIO`.

   * *Markdown PDF* para exportar la documentación generada directamente a PDF.

2. **Archivo de Reglas Globales del Proyecto (`M:\61_PROYECTOS_IA\18_ESCRITORIO\.agents\rules\escritorio_architecture.md`):**

   * Fija la ruta base del proyecto en `M:\61_PROYECTOS_IA\18_ESCRITORIO` y el repositorio remoto en `https://github.com/tekkes/ESCRITORIO.git`.

   * Exige portabilidad estricta "Copy & Run" en un único `Escritorio.exe` en Windows 11 sin requerir instalación en otros PCs.

   * Uso obligatorio de REA MCP para verificar con evidencias cualquier formato de archivo de Scrivener (`.scrivx`, `.scrtheme`, `styles.xml`, `compile.xml`).

   * Prohibición absoluta de dejar funciones *stub*, comentarios `// TODO` o simulaciones incompletas.

## 5. Gestión de Control de Versiones, Integración con GitHub (`tekkes/ESCRITORIO`) y Flujo DevSecOps

### 5.1. Funcionalidades y Ventajas de Usar GitHub en el Desarrollo de «Escritorio»

Al trabajar sobre tu unidad local `M:\61_PROYECTOS_IA\18_ESCRITORIO` y sincronizar con tu repositorio **`https://github.com/tekkes/ESCRITORIO`**, obtienes cinco ventajas críticas:

1. **Puntos de Restauración Atómicos ante Agentes Autónomos:** Como utilizaremos agentes de IA y un bucle de Equipo Rojo que modifica múltiples archivos simultáneamente, cada funcionalidad validada queda sellada en un *commit* o *tag* inmutable (`v0.1.0`, `v0.2.0`, `v1.0.0`). Si un agente introduce una regresión, podemos revertir en un segundo.

2. **Compilación Automatizada en la Nube (GitHub Actions CI/CD):** Configuraremos `.github/workflows/release-windows11.yml` en `tekkes/ESCRITORIO` para que, con cada *push*, los servidores de GitHub compilen `Escritorio.exe` en una máquina limpia de Windows Server, ejecuten la suite de pruebas y publiquen el ejecutable portable en la sección **Releases** de `https://github.com/tekkes/ESCRITORIO/releases`.

3. **Trazabilidad de Auditorías del Equipo Rojo:** Los agentes adversariales registran y cierran *Issues* en `tekkes/ESCRITORIO` vinculándolos al *commit* exacto que soluciona cada defecto.

4. **Respaldo en la Nube sin Bloqueos de Archivos:** Git sincroniza el código fuente de forma controlada sin bloquear jamás los archivos `.obj` o `.exe` durante la compilación en `M:\61_PROYECTOS_IA\18_ESCRITORIO`.

5. **Trabajo en Ramas (*Branching*):** Permite desarrollar sobre `develop` y probar refactorizaciones agresivas del Equipo Rojo en una rama `redteam/audit` manteniendo la rama principal `main` siempre estable.

### 5.2. Paso a Paso: Cómo Conectar `M:\61_PROYECTOS_IA\18_ESCRITORIO` con `https://github.com/tekkes/ESCRITORIO`

En la terminal integrada de Antigravity IDE, ejecuta los siguientes comandos para enlazar tu carpeta local con tu repositorio `tekkes/ESCRITORIO`:

```
# 1. Ir al directorio exacto del proyecto ya creado
Set-Location -Path "M:\61_PROYECTOS_IA\18_ESCRITORIO"

# 2. Marcar el directorio en la unidad M:\ como seguro en Git
git config --global --add safe.directory "M:/61_PROYECTOS_IA/18_ESCRITORIO"

# 3. Inicializar el repositorio en la rama main y configurar tu usuario tekkes
git init -b main
git config core.longpaths true
git config user.name "tekkes"
git config user.email "tekkes@users.noreply.github.com"

# 4. Conectar con el repositorio remoto https://github.com/tekkes/ESCRITORIO
# (Si el repositorio ya existe en GitHub, lo vinculamos; si no, gh lo crea o se enlaza directamente)
git remote remove origin 2>$null
git remote add origin https://github.com/tekkes/ESCRITORIO.git

# 5. Verificar la conexión remota
git remote -v

```

*(Nota: Si aún no habías creado el repositorio vacío en la web de GitHub, también puedes ejecutar `gh repo create tekkes/ESCRITORIO --private --source=. --remote=origin`).*

## 6. Catálogo Maestro Secuencial de Prompts para Google Antigravity IDE

A continuación tienes la secuencia completa de **18 Prompts Maestros de Ingeniería** personalizados con tu ruta `M:\61_PROYECTOS_IA\18_ESCRITORIO` y tu repositorio `https://github.com/tekkes/ESCRITORIO.git`. Ejecútalos en orden dentro del panel de Agente de **Google Antigravity IDE**.

### Fase 1: Descubrimiento con REA, Arquitectura Base y Estructura del Proyecto

#### PROMPT 01: Auditoría de Ingeniería Inversa con REA y Creación de Estructura en `M:\61_PROYECTOS_IA\18_ESCRITORIO`

```
Actúa como Arquitecto Principal de Sistemas e Ingeniero Inverso Senior. Vamos a desarrollar "Escritorio", una aplicación nativa y 100% portable para Windows 11 (un único ejecutable Escritorio.exe rápido, ligero y capaz de copiarse y ejecutarse directamente en cualquier otro PC con Windows 11 sin instalar nada) que replica de forma exacta y completa todas las funcionalidades, capacidades y temas visuales de Scrivener 3 para Windows.

Datos oficiales del entorno del proyecto:
- Directorio raíz del proyecto (ya creado): `M:\61_PROYECTOS_IA\18_ESCRITORIO`
- Usuario de GitHub: `tekkes`
- Repositorio remoto de GitHub: `https://github.com/tekkes/ESCRITORIO.git`
- En este ordenador ya está instalado REA (`morluto/rea`) porque lo utilizamos previamente en el proyecto ODISEA, y tienes conectados los servidores MCP de REA y de GitHub.

Ejecuta las siguientes tareas paso a paso dentro de `M:\61_PROYECTOS_IA\18_ESCRITORIO`:
1. Invoca las herramientas del servidor MCP de REA para verificar tu conexión y analizar la estructura de datos y comportamiento de referencia de Scrivener 3 (en caso de existir binarios, plantillas o archivos de muestra .scriv / .scrtheme en el sistema, o bien mediante reconstrucción formal de formatos):
   - Estructura exacta del archivo XML de proyecto (.scrivx) y su versión nativa (.escrx), incluyendo UUIDs, BinderItems, Children, MetaData, LabelSettings, StatusSettings, SectionTypes, Targets y Collections.
   - Estructura interna de la carpeta Files/Data/<UUID>/ (content.rtf, notes.rtf, synopsis.txt, content.comments) y Snapshots/<UUID>/.
   - Estructura interna de los paquetes de temas (.scrtheme): manifiesto XML, paleta .pal, preferencias .prefs y hoja de estilos .qss.
2. Genera en `M:\61_PROYECTOS_IA\18_ESCRITORIO\docs\rea_evidence\REA_Architecture_Evidence.md` un documento técnico exhaustivo con todas las estructuras de datos exactas, esquemas XML y reglas de estilo descubiertas.
3. Inicializa la estructura completa de carpetas del proyecto dentro de `M:\61_PROYECTOS_IA\18_ESCRITORIO`:
   - `/src/core` (Motor de proyectos, parser XML/RTF, gestor de UUIDs, autoguardado atómico, backups ZIP)
   - `/src/ui` (Ventana principal, Binder, Editor RTF, Split View, Corkboard, Outliner, Inspector, Composition Mode)
   - `/src/themes` (Motor de temas, parser .scrtheme/.escrtheme, modos Minimalista, Oscuro, Solarizado, Sepia, Modernos y Live Theme Studio)
   - `/src/compile` (Motor de compilación multihilo, Section Layouts, Placeholders, exportadores DOCX, PDF, EPUB, RTF, FDX, MD, HTML)
   - `/src/tools` (Project Targets, Linguistic Focus, Statistics, Name Generator, Scratchpad)
   - `/assets/icons` (Iconos vectoriales SVG compactos de 14px-16px)
   - `/assets/themes` (Temas predefinidos integrados)
   - `/assets/templates` (Plantillas de Ficción, No Ficción, Guion, Investigación)
   - `/tests/redteam` (Suite de validación adversarial y pruebas de regresión)
   - `/portable_config` (Estructura auxiliar de configuración portable)
4. Crea el archivo `.gitignore` optimizado (excluyendo directorios de compilación intermedia `/build/`, `/target/`, `.vs/`, archivos `.tmp` y `.lock`).
5. Verifica que Git está inicializado en `M:\61_PROYECTOS_IA\18_ESCRITORIO` con `user.name "tekkes"` y el remoto `origin` apuntando a `https://github.com/tekkes/ESCRITORIO.git`. Realiza el primer commit en la rama `main`, crea la rama `develop` y haz push de ambas ramas (`git push -u origin main` y `git push -u origin develop`) con el mensaje: "chore(init): initialize Escritorio project structure and REA evidence specs".

```

#### PROMPT 02: Configuración del Sistema de Compilación Monolítico Portable (`Escritorio.exe`) "Copy & Run"

```
Actúa como Ingeniero de Sistemas Windows 11. Trabajando en el directorio raíz `M:\61_PROYECTOS_IA\18_ESCRITORIO`, configura el sistema de construcción (Build System) del proyecto Escritorio para generar un único ejecutable nativo, estático, ligero y de arranque instantáneo llamado `Escritorio.exe`, garantizando portabilidad total ("Copy & Run") en cualquier otro ordenador con Windows 11 sin necesidad de instalar librerías ni runtimes.

Tareas a implementar:
1. Configura el archivo maestro de construcción en `M:\61_PROYECTOS_IA\18_ESCRITORIO` (`CMakeLists.txt` con enlace estático MSVC `/MT` o Clang-CL, o bien `Cargo.toml` con configuración release optimizada `lto = true`, `codegen-units = 1`, `strip = true`, `panic = "abort"`, `target-feature = "+crt-static"` y subsistema `windows`). El binario resultante NO debe depender de DLLs de Visual C++ (`vcruntime140.dll`) ni de frameworks externos no incluidos de serie en una instalación limpia de Windows 11.
2. Implementa el módulo `/src/core/PortableManager`:
   - Al arrancar `Escritorio.exe`, debe detectar la ruta exacta del propio ejecutable en cualquier ordenador o unidad USB mediante `GetModuleFileNameW`.
   - Debe leer o crear automáticamente el archivo auxiliar `./config/escritorio_settings.json` y las carpetas `./config/themes/`, `./config/templates/`, `./config/backups/` y `./config/dictionaries/` en el mismo directorio donde resida `Escritorio.exe`.
   - Almacenará las rutas de proyectos y plantillas situadas dentro de su árbol como **rutas relativas** para que, al copiar la carpeta a otro ordenador con distinta letra de unidad (ej. de `M:\` a `C:\` o `D:\`), todo siga funcionando sin romper enlaces.
   - Garantiza que NUNCA se escriba en el Registro de Windows ni en `%APPDATA%`.
3. Implementa el manifiesto de aplicación de Windows 11 (`app.manifest` y `resources.rc`) con soporte para:
   - Ejecución sin requerir permisos de administrador (`requestedExecutionLevel level="asInvoker"`).
   - `longPathAware` activado en el manifiesto XML.
   - Per-Monitor High DPI V2 Awareness (escalado nítido en monitores 4K).
   - Esquinas redondeadas de Windows 11 (`DWMWA_WINDOW_CORNER_PREFERENCE`).
4. Crea la ventana principal base y verifica que el proyecto compila generando `Escritorio.exe` dentro de `M:\61_PROYECTOS_IA\18_ESCRITORIO\build\release\` y arranca en menos de 250 ms.
5. Realiza commit y push al repositorio `https://github.com/tekkes/ESCRITORIO.git` en la rama `develop`: "feat(core): implement static single-exe build pipeline and copy-and-run Windows 11 portable manager".

```

### Fase 2: Motor de Datos, Guardado Atómico y Compatibilidad `.scriv` / `.escr`

#### PROMPT 03: Motor de Proyectos (`.escr` y `.scriv`), Guardado Atómico y Backups ZIP

```
Desarrolla de forma completa y sin omisiones el núcleo de persistencia de datos en `M:\61_PROYECTOS_IA\18_ESCRITORIO\src\core\ProjectEngine` basándote en las evidencias extraídas con REA en `docs/rea_evidence/REA_Architecture_Evidence.md`.

Requisitos de implementación:
1. Soporte nativo de lectura y escritura para paquetes de proyecto `.escr` (formato nativo de Escritorio) y compatibilidad 100% bidireccional para abrir, editar y guardar proyectos `.scriv` de Scrivener 3 para Windows.
2. Implementa el parser y serializador del índice maestro XML (`.escrx` / `.scrivx`) que gestione:
   - Árbol jerárquico completo de `BinderItem` con sus `UUID` (v4), `Type` (`DraftFolder`, `ResearchFolder`, `TrashFolder`, `Folder`, `Text`, `PDF`, `Image`, `Media`, `WebArchive`), `Title`, `Created`, `Modified`.
   - Configuraciones de `MetaData` (`IncludeInCompile`, `SectionType`, `Target`, `StatusID`, `LabelID`, `CustomMetaData`, `Keywords`).
   - `Collections` (tanto colecciones estándar como colecciones de búsqueda dinámica).
3. Implementa la estructura física en disco `Files/Data/<UUID>/`:
   - Carga diferida (Lazy Loading) de `content.rtf`, `synopsis.txt`, `notes.rtf` y `content.comments`.
   - Motor de Autoguardado Atómico: cada documento modificado ("dirty flag") se guarda tras 2 segundos de inactividad escribiendo primero en `content.rtf.tmp`, sincronizando el buffer a disco (`FlushFileBuffers`) y renombrando atómicamente con `MoveFileExW` (`MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH`).
4. Implementa un sistema de bloqueo de proyecto (`project.lock`) para advertir al usuario si el proyecto ya está abierto en otra instancia.
5. Implementa `/src/core/BackupManager`:
   - Compresión automática del proyecto en un archivo `.zip` con marca de tiempo al abrir o cerrar el proyecto, guardando las últimas N copias (por defecto 5, configurable) en `./config/backups/` y verificando su integridad con SHA-256.
6. Escribe pruebas unitarias exhaustivas de creación, lectura, modificación y backup de proyectos dentro de `M:\61_PROYECTOS_IA\18_ESCRITORIO`, ejecútalas y haz commit y push a `https://github.com/tekkes/ESCRITORIO.git` (`develop`): "feat(core): complete .escr/.scriv project engine, atomic autosave and ZIP backups".

```

### Fase 3: Sistema de Temas, Estilos y Modos de Visualización Compactos

#### PROMPT 04: Motor de Temas Visuales (`.scrtheme` / `.escrtheme`), Modo Minimalista, Oscuro, Solarizado, Sepia y Alta Densidad

```
Desarrolla el motor visual completo de Escritorio en `M:\61_PROYECTOS_IA\18_ESCRITORIO\src\themes\ThemeEngine` y `\assets\themes\`, cumpliendo estrictamente los requisitos de modos de visualización, soporte de temas de Scrivener y diseño compacto de iconos y etiquetas.

Tareas de desarrollo:
1. Utiliza las evidencias de REA sobre los archivos `.scrtheme` de Scrivener 3 en Windows para construir un cargador nativo (`ScrThemeLoader`) capaz de descomprimir cualquier archivo `.scrtheme` en memoria y parsear:
   - El archivo `.xml` de manifiesto.
   - La paleta `.pal` de colores del sistema.
   - El archivo `.prefs` de colores específicos del editor, corcho, esquema y modo composición.
   - La hoja de estilos `.qss` aplicando las reglas visuales a todos los controles de Escritorio.
2. Implementa e integra de serie los siguientes 7 modos de visualización predefinidos, accesibles instantáneamente desde un selector rápido en la barra superior y desde el menú `Ventana > Temas`:
   - **Modo Minimalista (Por Defecto):** Estética limpia, sin bordes superfluos, papel blanco cálido (`#FFFFFF`), paneles `#F7F7F5` y `#EFEFEC`.
   - **Modo Oscuro (Carbon Dark):** `#18191A` / `#202124` / `#141517`, texto `#E4E6EB`, alto confort nocturno.
   - **Modo Solarizado Oscuro (Solarized Dark):** Paleta exacta `#002B36`, `#073642`, texto `#839496`, acentos `#B58900` y `#2AA198`.
   - **Modo Solarizado Claro (Solarized Light):** Paleta exacta `#FDF6E3`, `#EEE8D5`, texto `#657B83`.
   - **Modo Sepia (Classic Parchment):** Fondo `#F4ECD8`, paneles `#E8DEC3`, texto tinta `#3B2F2F`.
   - **Modo Nord (Nordic Frost)** y **Modo Catppuccin Mocha**.
3. Implementa el **Control de Densidad Visual (UI Density)** con diseño moderno y compacto:
   - Iconos vectoriales SVG nítidos de pequeño tamaño ($14\text{ px}$ en modo Ultra-Compacto y $16\text{ px}$ en modo Compacto).
   - Barras de herramientas de altura reducida ($28\text{ px}$) y cabeceras de editor de $24\text{ px}$ para no restar espacio de trabajo al escritor.
   - Etiquetas de documento (*Labels*) y Estados (*Status*) renderizados como micro-píldoras (*micro-badges*) de $10\text{ px}$ o indicadores cromáticos de $6\text{ px}$.
4. Desarrolla la ventana **Live Theme Studio (Configurador de Temas del Usuario)** que permita personalizar cada color, fuente de interfaz, textura de fondo y tamaño de iconos en tiempo real, y guardar/exportar el tema en formato `.escrtheme` o `.scrtheme`.
5. Verifica que el cambio entre los 7 modos ocurre en menos de 50 ms sin parpadeos ni reinicios. Haz commit y push a `https://github.com/tekkes/ESCRITORIO.git` (`develop`): "feat(themes): implement ScrTheme engine, 7 visual modes, compact UI density and Live Theme Studio".

```

### Fase 4: Interfaz Principal, el Cuaderno (*Binder*) y Colecciones

#### PROMPT 05: Desarrollo Completo del Cuaderno (*Binder*), Operaciones de Estructura Narrativa y Colecciones

```
Desarrolla el componente completo del Cuaderno (*Binder*) en `M:\61_PROYECTOS_IA\18_ESCRITORIO\src\ui\BinderWidget` replicando todas las capacidades estructurales de Scrivener.

Funcionalidades obligatorias a programar:
1. Árbol jerárquico multinivel (`BinderTreeView`) con las 3 carpetas raíz especiales: **Manuscrito (Draft)**, **Investigación (Research)** y **Papelera (Trash)**, además de soporte para carpeta de **Plantillas (Templates)**.
2. Capacidad dual de nodos: cualquier carpeta puede tener texto propio editable y cualquier documento de texto puede contener subdocumentos hijos.
3. Operaciones de estructura narrativa con soporte completo de Deshacer/Rehacer (`Ctrl+Z` / `Ctrl+Y`):
   - *Drag & Drop* de selección simple y múltiple para reordenar escenas, mover capítulos enteros o anidar documentos.
   - **Agrupar (`Ctrl+G`):** Crea una nueva carpeta y mueve dentro los ítems seleccionados.
   - **Desagrupar (`Ctrl+Shift+G`):** Extrae los hijos al nivel superior y elimina la carpeta contenedora.
   - **Dividir en la selección (`Ctrl+K`)** y **Dividir usando la selección como título (`Ctrl+Shift+K`)**.
   - **Fusionar documentos (`Ctrl+Shift+M`):** Une varios documentos seleccionados en uno solo concatenando su texto, notas y sinopsis.
   - **Duplicar (`Ctrl+D`)** y **Enviar a la Papelera (`Supr`)** con restauración intacta.
4. Personalización visual en el *Binder*:
   - Menú contextual `Cambiar Icono` con biblioteca integrada de más de 80 micro-iconos vectoriales SVG (carpetas, documentos de texto, fichas de personaje, ubicaciones, bocetos, alertas, banderas de colores, etc.) e iconos a partir de texto/emoji.
   - Opción `Mostrar color de etiqueta en el Binder` (como punto de color a la derecha, tinte en el icono o resaltado suave de toda la fila).
5. Sistema de **Colecciones (*Collections*)**:
   - Barra de pestañas compacta en la parte superior del *Binder* para alternar entre el *Binder* completo, **Colecciones Estándar** (listas manuales mediante arrastrar y soltar) y **Colecciones de Búsqueda Guardada** (actualizadas en tiempo real).
6. Haz commit y push a `https://github.com/tekkes/ESCRITORIO.git` (`develop`): "feat(binder): implement hierarchical Binder, split/merge narrative tools, custom SVG icons and Collections".

```

### Fase 5: El Editor de Texto Enriquecido, Estilos, Pantalla Dividida y Modo Scrivenings

#### PROMPT 06: Motor de Edición RTF, Sistema de Estilos Semánticos, Vista de Página y Foco Lingüístico

```
Desarrolla el Editor Principal de Escritorio en `M:\61_PROYECTOS_IA\18_ESCRITORIO\src\ui\EditorWidget` y `\src\core\StyleEngine` con paridad funcional total respecto al editor de Scrivener 3.

Implementa de forma completa:
1. Procesador de texto enriquecido RTF de alto rendimiento con barra de formato compacta:
   - Selección de fuente, tamaño, negrita, cursiva, subrayado, tachado, superíndice, subíndice, color de texto, resaltadores multicolores, alineación, interlineado ($1.0$, $1.15$, $1.5$, $2.0$ y personalizado), espaciado entre párrafos y sangrías de primera línea mediante una **Regla horizontal (*Ruler*)** interactiva (`Ctrl+Shift+R`).
   - Inserción de tablas editables, listas con viñetas y numeradas, imágenes incrustadas o vinculadas al proyecto con redimensionamiento visual, e hipervínculos internos entre documentos del propio proyecto (*Scrivener Links* / `[[Título del Documento]]`).
2. **Sistema de Estilos Semánticos de Scrivener (`StyleEngine`):**
   - Implementa el estado por defecto **"Sin Estilo" (*No Style*)** para el cuerpo principal del manuscrito.
   - Implementa estilos de Párrafo, de Carácter o Mixtos (Cita en bloque, Epígrafe, Título 1, Título 2, Código, Verso) con las funciones `Crear estilo desde la selección` y `Redefinir estilo desde la selección`, persistiendo en `Settings/styles.xml`.
3. **Modos de Visualización y Ergonomía del Editor:**
   - **Vista de Página (*Page View* / `Alt+Shift+P`):** Renderiza folios físicos paginados con márgenes reales frente al modo continuo de ancho fijo centrado.
   - **Desplazamiento de Máquina de Escribir (*Typewriter Scrolling* / `Ctrl+Alt+T`):** Mantiene la línea de edición centrada verticalmente al escribir.
   - **Modo Foco (*Focus Mode*):** Atenúa el resto del texto resaltando solo la Línea, Oración o Párrafo actual.
   - **Foco Lingüístico (*Linguistic Focus*):** Motor analizador para español e inglés que permite resaltar exclusivamente los *Diálogos Directos* (entre comillas latinas «...», inglesas "..." o rayas de diálogo —...—), *Adverbios* (terminados en -mente / -ly y diccionario), *Adjetivos*, *Verbos* o *Conjunciones*.
   - **Caracteres Invisibles (*Show Invisibles*):** Muestra marcas de párrafo ($\P$), espacios, tabulaciones y saltos de página.
4. Haz commit y push a `https://github.com/tekkes/ESCRITORIO.git` (`develop`): "feat(editor): implement rich text editor, No-Style semantic system, Page View, Typewriter scroll and Linguistic Focus".

```

#### PROMPT 07: Modo Scrivenings (Edición Continua), Pantalla Dividida (*Split View*), Modo Guion y Visores Multimedia

```
Amplía el Editor Central en `M:\61_PROYECTOS_IA\18_ESCRITORIO\src\ui\SplitEditorManager` y `\src\ui\ScriveningsEngine` para soportar la edición de documentos compuestos, pantalla dividida y archivos de investigación.

Tareas de programación:
1. **Modo Scrivenings (Vista Compuesta de Manuscrito):**
   - Al seleccionar una carpeta o múltiples documentos en el *Binder* y activar el modo *Scrivenings* (`Ctrl+1`), concatena virtualmente todos los textos en una sola vista continua.
   - Permite mostrar títulos de sección editables in-situ y separadores configurables (línea horizontal sutil, esquinas recortadas o salto de página).
   - Cualquier edición realizada en cualquier parte del flujo continuo debe sincronizarse y guardarse de forma transparente en el archivo `content.rtf` individual del nodo correspondiente.
2. **Pantalla Dividida (*Split Screen*) y Paneles de Referencia Rápida (*Quick Reference*):**
   - Botones compactos en la cabecera del editor para dividir la vista verticalmente (`Ctrl+'`), horizontalmente (`Ctrl+"`) o en cuadrícula de hasta 4 paneles.
   - Opción **Bloquear Editor (*Lock in Place* / `Ctrl+Shift+L`)** con indicador visual en la cabecera para que los clics en el *Binder* solo cambien el documento del otro panel.
   - Opción **Navegación afecta al otro editor** (ej. hacer clic en una ficha del Corcho en el panel izquierdo abre su texto en el panel derecho).
   - Ventanas flotantes **Quick Reference (QR)** para abrir cualquier documento o imagen en ventanas independientes multi-monitor.
3. **Modo Escritura de Guiones (*Scriptwriting Mode* / `Ctrl+8`):**
   - Motor de autocompletado y transición automática de elementos con `Tab` y `Enter` para Guion de Cine (Encabezado `INT./EXT.`, Acción, Personaje, Paréntesis, Diálogo, Transición), Teatro y Cómic, mostrando el selector de elemento en la barra de estado inferior.
4. **Visores Integrados de Investigación (*Research Viewers*):**
   - Visor nativo de archivos PDF (con zoom, búsqueda y paso de páginas), visor de imágenes (con rotación, zoom y ajuste), reproductor de audio/vídeo integrado con atajos de teclado para transcripción de entrevistas (pausar/retroceder 5 segundos sin quitar las manos del editor de texto) y visor de páginas web archivadas.
5. Haz commit y push a `https://github.com/tekkes/ESCRITORIO.git` (`develop`): "feat(editor): implement Scrivenings continuous mode, 4-way split screen, Scriptwriting mode and Research media viewers".

```

### Fase 6: La Pizarra de Corcho (*Corkboard*) y el Esquema (*Outliner*)

#### PROMPT 08: Desarrollo Completo de la Pizarra de Corcho (*Corkboard*) en Modos Rejilla, Libre y Apilado por Etiquetas

```
Desarrolla el componente de la Pizarra de Corcho en `M:\61_PROYECTOS_IA\18_ESCRITORIO\src\ui\CorkboardWidget` (`Ctrl+2`) replicando fielmente el diseño visual, interactividad y modos de trabajo de Scrivener 3, adaptándose dinámicamente al tema activo (Minimalista, Oscuro, Solarizado, Sepia, etc.).

Funcionalidades a implementar:
1. **Diseño de la Ficha de Índice (*Index Card Widget*):**
   - Cabecera con icono del documento, numeración opcional y título editable con doble clic.
   - Cuerpo con edición directa del texto de la sinopsis (`synopsis.txt`) sobre líneas de libreta opcionales, o visualización de la imagen asociada a la tarjeta.
   - **Color de Etiqueta (*Label*):** Representado como un pin en la parte superior, una franja lateral o coloreando todo el fondo de la ficha.
   - **Sello de Estado (*Status Stamp*):** Texto diagonal semitransparente personalizable (ej. "Borrador", "Revisado", "Listo") sobre la tarjeta.
   - **Chips de Palabras Clave (*Keywords*):** Pequeños bloques de color en el margen derecho o inferior de la tarjeta.
2. **Tres Submodos de Operación:**
   - **Modo Rejilla (*Arrange by Order*):** Arrastrar y soltar tarjetas con animación suave que reordena automáticamente los capítulos o escenas en el *Binder*.
   - **Modo Forma Libre (*Freeform Corkboard*):** Lienzo libre 2D con zoom y paneo donde las tarjetas pueden colocarse en cualquier posición sin alterar el *Binder*, más un botón para confirmar el orden libre al *Binder* cuando el escritor decida la estructura.
   - **Modo Apilado por Etiqueta (*Arrange by Label / Swimlanes*):** Organiza las tarjetas en columnas verticales o filas horizontales por cada Etiqueta (ideal para seguir arcos de personajes o líneas temporales), permitiendo arrastrar una tarjeta de una fila a otra para cambiar su etiqueta y posición simultáneamente.
3. Barra inferior ultra-compacta de control del Corcho para ajustar en vivo: Tamaño de tarjeta, Ratio de aspecto ($3 \times 5$, $4 \times 6$, $1:1$), Espaciado, Tarjetas por fila (`Auto` o de 1 a 10) y conmutadores de sellos/pines.
4. Haz commit y push a `https://github.com/tekkes/ESCRITORIO.git` (`develop`): "feat(corkboard): implement Grid, Freeform and Label-Swimlane Corkboard with customizable Index Cards".

```

#### PROMPT 09: Desarrollo Completo del Esquema (*Outliner*) con Metadatos, Objetivos y Barras de Progreso

```
Desarrolla la vista de Esquema en `M:\61_PROYECTOS_IA\18_ESCRITORIO\src\ui\OutlinerWidget` (`Ctrl+3`) como una vista matricial jerárquica de alto rendimiento para la planificación estructural de obras complejas.

Funcionalidades a implementar:
1. Árbol tabular multinivel capaz de mostrar el título y la sinopsis debajo del título en la misma celda (como en Scrivener 3) o en columnas separadas, con edición directa in-situ.
2. Selector compacto de columnas visibles con soporte para:
   - `Title & Synopsis`, `Label` (con selector desplegable de color), `Status` (selector desplegable), `Section Type` (selector desplegable), `Include in Compile` (checkbox).
   - `Words`, `Total Words` (suma recursiva de la carpeta y todos sus descendientes), `Characters`, `Total Characters`.
   - `Target` (objetivo numérico editable por escena/capítulo), `Total Target` y `Progress` (barra de progreso visual que cambia gradualmente de color desde rojo `0%` pasando por ámbar `50%` hasta verde/azul `100%`).
   - `Keywords`, `Created Date`, `Modified Date` y todas las columnas de **Metadatos Personalizados (*Custom Metadata*)** creadas por el usuario en el proyecto.
3. Ordenación multi-criterio al hacer clic en los encabezados de columna (ascendente, descendente, restaurar orden del *Binder*), filtrado rápido por texto en el esquema y exportación directa de la tabla del Esquema a archivo `.csv`.
4. Haz commit y push a `https://github.com/tekkes/ESCRITORIO.git` (`develop`): "feat(outliner): implement hierarchical Outliner with custom metadata columns and visual target progress bars".

```

### Fase 7: El Inspector Lateral Derecho y Modo Composición

#### PROMPT 10: El Inspector Completo (Sinopsis, Notas, Marcadores, Metadatos, Instantáneas con Diff y Comentarios)

```
Desarrolla el panel lateral derecho del Inspector en `M:\61_PROYECTOS_IA\18_ESCRITORIO\src\ui\InspectorWidget` (`Ctrl+Shift+I`) integrando las 6 pestañas especializadas de Scrivener con una cabecera de iconos compactos de 16px.

Desarrolla íntegramente cada una de las 6 pestañas:
1. **Pestaña 1 - Sinopsis y Notas (`Notes & Synopsis`):**
   - Parte superior: Tarjeta de sinopsis sincronizada con el Corcho, con botón para alternar entre Sinopsis de texto e Imagen de escena (con soporte drag-and-drop de imágenes).
   - Parte inferior: Editor RTF de Notas del Documento (`notes.rtf`).
   - Pie fijo del Inspector: Selectores rápidos de `Label` y `Status`.
2. **Pestaña 2 - Marcadores (`Bookmarks`):**
   - Conmutador entre *Marcadores del Documento* y *Marcadores del Proyecto*.
   - Visor previsualizador integrado en la mitad inferior del Inspector que permite leer y editar documentos de referencia sin cambiar el documento abierto en el editor principal.
3. **Pestaña 3 - Metadatos (`Metadata`):**
   - Configuración general (`Incluir en compilación`, `Tipo de sección`).
   - Panel de *Metadatos Personalizados* con botón de configuración para añadir campos de tipo Texto, Checkbox, Lista o Fecha.
   - Panel de *Palabras Clave (Keywords)* con ventana flotante `Project Keywords HUD` para gestionar jerarquías de palabras clave con colores y arrastrarlas a los documentos.
4. **Pestaña 4 - Instantáneas (`Snapshots` / `Ctrl+5`):**
   - Toma de instantáneas manuales o con título (`Ctrl+Shift+5`) de la versión actual del documento, guardándolas en `Snapshots/<UUID>/`.
   - **Motor de Comparación Diferencial (`Compare`):** Implementa el algoritmo de diferencias (Myers Diff a nivel de palabra, cláusula o párrafo) que muestre en el visor inferior las palabras eliminadas tachadas en rojo y las palabras añadidas subrayadas en azul/verde entre la versión actual y la instantánea seleccionada.
   - Botón `Rollback` que restaura la versión antigua ofreciendo tomar antes una instantánea de seguridad del estado actual.
5. **Pestaña 5 - Comentarios y Notas al Pie (`Comments & Footnotes`):**
   - Lista interactiva de comentarios enlazados a selecciones de texto (con color personalizable, autor y marca de tiempo) y notas al pie del Inspector. Hacer clic en un comentario desplaza el editor al texto exacto y viceversa.
6. Haz commit y push a `https://github.com/tekkes/ESCRITORIO.git` (`develop`): "feat(inspector): implement all 6 Inspector tabs including Snapshot Myers-diff comparator and Footnotes".

```

#### PROMPT 11: Modo Composición a Pantalla Completa (*Composition Mode*), Objetivos, Estadísticas y Herramientas Auxiliares

```
Desarrolla el Modo Composición libre de distracciones y el conjunto completo de herramientas de productividad del escritor en `M:\61_PROYECTOS_IA\18_ESCRITORIO\src\ui\CompositionMode` y `\src\tools\`.

Implementa:
1. **Modo Composición (`F11`):**
   - Pantalla completa sin bordes sobre Windows 11.
   - Hoja de papel central de ancho y posición ajustables, con capacidad de mostrar una imagen o textura de fondo personalizada y un deslizador de opacidad (*Background Fade*) desde transparente hasta negro absoluto.
   - Barra de control inferior auto-ocultable (aparece solo al acercar el ratón al borde inferior) con controles de: Ancho de papel (`Paper Width`), Posición del papel, Zoom de texto, Fundido de fondo, botón `Go To` para saltar a cualquier escena del *Binder*, panel flotante del Inspector y contador de palabras en vivo.
2. **Objetivos de Proyecto y Sesión (`Project Targets` / `Ctrl+Shift+T`):**
   - Ventana flotante compacta con barras de progreso duales: *Objetivo del Manuscrito* y *Objetivo de la Sesión*.
   - Configuración de Fecha Límite (*Deadline*), selección de días de escritura semanales y cálculo dinámico de la cuota diaria de palabras necesaria para terminar el libro a tiempo.
3. **Estadísticas del Proyecto y Frecuencia de Palabras (`Project Statistics`):**
   - Cálculo exacto de palabras, caracteres (con y sin espacios), párrafos, páginas impresas estimadas, páginas de libro de bolsillo y tiempo de lectura estimado.
   - Tabla interactiva de **Frecuencia de Palabras (*Word Frequency*)** con filtro de *stop-words* opcional para detectar repeticiones léxicas.
4. **Buscador Global de Proyecto y Búsqueda Regex (`Project Search & Replace`):**
   - Búsqueda instantánea en Todo el Proyecto, solo en Texto, Sinopsis, Notas o Títulos, con soporte de Expresiones Regulares (PCRE2) y opción de guardar la búsqueda como Colección.
5. **Generador de Nombres (`Name Generator`) y Scratchpad Global:**
   - Herramienta generadora de nombres de personajes con bases de datos integradas (Español, Inglés, Francés, Alemán, Italiano, Japonés, Fantasía, Mitología, Apellidos) y filtros de inicial/aliteración.
   - Ventana flotante global **Scratchpad** accesible mediante atajo global de Windows (`Ctrl+Alt+Shift+S`) para tomar notas rápidas desde cualquier aplicación y enviarlas al proyecto activo.
6. Haz commit y push a `https://github.com/tekkes/ESCRITORIO.git` (`develop`): "feat(tools): implement Composition Mode, Project Targets with deadline calculator, Statistics, Name Generator and Scratchpad".

```

### Fase 8: El Motor de Compilación (*Compile Engine*) y Plantillas de Proyecto

#### PROMPT 12: Arquitectura del Compilador de Scrivener 3 (Section Types, Section Layouts, Placeholders y Transformaciones)

```
Desarrolla el núcleo del Motor de Compilación en `M:\61_PROYECTOS_IA\18_ESCRITORIO\src\compile\CompileEngine` y su interfaz de usuario de 3 columnas en `\src\ui\CompileDialog` (`Ctrl+Shift+E`), replicando exactamente el paradigma de Scrivener 3.

Requisitos de implementación:
1. **Interfaz del Diálogo de Compilación (3 Columnas):**
   - **Columna 1 (Formats):** Lista de formatos predefinidos integrados (*Manuscrito Estándar Courier/Times*, *Novela Moderna*, *Libro de Bolsillo 6x9*, *Ebook Estándar*, *Guion Hollywood*, *Ensayo Académico APA/MLA*, *Esquema de Sinopsis*) y formatos personalizados del proyecto o globales, con un **Diseñador Completo de Formatos de Compilación (`Compile Format Designer`)** al hacer doble clic.
   - **Columna 2 (Section Layouts):** Vista previa visual de cómo se maquetará cada `Section Type` del proyecto y botón `Assign Section Layouts...` para mapear semánticamente carpetas de Partes, Capítulos y Escenas.
   - **Columna 3 (Contents, Metadata, Replacements):**
     - Pestaña de Contenidos con árbol de selección de qué documentos compilar, filtro por etiqueta/colección y opción de añadir *Front Matter* (Portadilla, Créditos, Dedicatoria) y *Back Matter* (Epílogo, Sobre el autor).
     - Pestaña de Metadatos del libro (Título, Autor, ISBN, Derechos, Portada para ePub).
     - Pestaña de Reemplazos automáticos de texto/Regex durante la compilación y configuración global de Notas al pie/Comentarios.
2. **Evaluador de Variables (*Placeholder Tags Parser*):**
   - Soporte completo para todas las variables de numeración y metadatos de Scrivener: `<$n>`, `<$r>`, `<$R>`, `<$t>`, `<$T>`, `<$w>`, `<$W>`, `<$hn>` (numeración jerárquica `1.1`, `1.2`), `<$title>`, `<$synopsis>`, `<$notes>`, `<$projecttitle>`, `<$author>`, `<$wc>`, `<$date>`, y reinicio de contadores `<$rst_n>`.
3. **Gestor de Separadores (`Separators`):**
   - Reglas configurables de separación antes de una sección y entre secciones del mismo tipo (Salto de página, Línea en blanco, Retorno simple o Símbolo personalizado centrado como `* * *`).
4. Haz commit y push a `https://github.com/tekkes/ESCRITORIO.git` (`develop`): "feat(compile): implement Scrivener 3 3-column Compile UI, Section Layouts mapper and Placeholder tag evaluator".

```

#### PROMPT 13: Exportadores e Importadores Nativos (DOCX, PDF, EPUB 3, RTF, Final Draft FDX, Markdown y LaTeX)

```
Completa el Motor de Compilación e Importación implementando en `M:\61_PROYECTOS_IA\18_ESCRITORIO\src\compile\exporters\` y `\src\core\importers\` los generadores nativos de formatos de publicación sin requerir software externo instalado en Windows 11.

Tareas a programar:
1. **Exportadores del Compilador:**
   - **Microsoft Word (`.docx`):** Generador nativo de paquetes OpenXML (`word/document.xml`, `styles.xml`, `numbering.xml`, cabeceras con apellido del autor y número de página, notas a pie de página reales `footnotes.xml`).
   - **PDF de Maquetación Editorial (`.pdf`) e Impresión:** Generador PDF con incrustación de fuentes, cabeceras/pies de página simétricos para páginas pares/impares, tabla de contenidos con enlaces clicables y márgenes de imprenta configurables.
   - **eBook Estándar (`.epub` v3):** Generador de paquete EPUB3 válido con portada (`cover.xhtml`), hoja CSS limpia, capítulos divididos automáticamente en cada salto de sección, navegación `nav.xhtml` / `toc.ncx` generada automáticamente y notas al pie interactivas tipo *pop-up*.
   - **Guion Profesional (`.fdx` y `.fountain`):** Exportador nativo a XML de Final Draft y sintaxis Fountain.
   - **Rich Text (`.rtf`), MultiMarkdown (`.md`), LaTeX (`.tex`) y Web (`.html`)**.
2. **Importadores Avanzados (`Archivo > Importar`):**
   - **Importar y Dividir (`Import and Split...`):** Permite importar un manuscrito lineal largo desde `.docx`, `.rtf`, `.txt` o `.md` y dividirlo automáticamente en escenas y capítulos en el *Binder* detectando los estilos de encabezado (`Heading 1`, `Heading 2`) o un separador especificado (como `#` o `***`).
   - Importador de guiones `.fdx` / `.fountain` y páginas web.
3. **Galería de Plantillas de Proyecto (`New Project Chooser`):**
   - Ventana de inicio con categorías: *En Blanco*, *Ficción (Novela, Novela con Partes, Relato Corto)*, *No Ficción (Ensayo General, Artículo APA, Artículo MLA, Tesis)*, *Guion (Cine, Teatro, Cómic, Podcast)* y función `Guardar Proyecto como Plantilla`.
4. Haz commit y push a `https://github.com/tekkes/ESCRITORIO.git` (`develop`): "feat(io): implement native DOCX, PDF, EPUB3, FDX, Markdown exporters, Import-and-Split and Project Templates".

```

### Fase 9: Agentes Adversariales de Equipo Rojo (*Red Team*) y Bucle de Validación Hasta Cero Defectos

#### PROMPT 14: Creación del Framework de Agentes de Validación y Verificación Adversarial (Red Team Loop)

```
Actúa como Director de Ciberseguridad Ofensiva y QA Adversarial (Red Team Lead). Necesitamos crear dentro de `M:\61_PROYECTOS_IA\18_ESCRITORIO` un sistema automatizado multi-agente de Validación y Verificación que opere en modo adversarial contra la aplicación "Escritorio" en bucle interactivo hasta alcanzar CERO errores, carencias o discrepancias respecto a Scrivener 3.

Desarrolla en `M:\61_PROYECTOS_IA\18_ESCRITORIO\tests\redteam\` y `.agents\workflows\redteam_loop.md` la siguiente arquitectura de 4 Agentes Especializados:

1. **Agente 1: `ParityInquisitorAgent` (Auditor de Paridad Funcional y Visual con REA):**
   - Utiliza las evidencias de REA (`docs/rea_evidence/REA_Architecture_Evidence.md`) y la Matriz de Requisitos SRS de Escritorio para inspeccionar el árbol de código y la ejecución del binario `Escritorio.exe`.
   - Busca implacablemente funciones incompletas, botones sin acción conectada, atajos de teclado faltantes, discrepancias en el renderizado de `.scrtheme`, modos visuales faltantes (Minimalista, Oscuro, Solarizado, Sepia) o etiquetas/iconos que excedan las dimensiones compactas requeridas.
2. **Agente 2: `ChaosFuzzerAgent` (Equipo Rojo de Estrés, Corrupción y Portabilidad en Otro PC):**
   - Ejecuta pruebas destructivas contra `Escritorio.exe` dentro de `M:\61_PROYECTOS_IA\18_ESCRITORIO`:
     * Proyectos masivos con $500\,000$ palabras y $1\,000$ documentos en modo *Scrivenings*.
     * Simulaciones de corte de energía en mitad del autoguardado atómico para verificar que ningún archivo `.rtf` ni `.escrx` se corrompe.
     * Inyección de caracteres Unicode complejos (CJK, emojis, RTL, símbolos matemáticos) y archivos `.scriv` antiguos o malformados.
     * **Simulación de traslado a otro ordenador con Windows 11:** Copia el ejecutable y `./config/` a un directorio temporal aislado en otra ruta/unidad, ejecuta el programa y verifica mediante monitoreo e inspección de tablas PE (con REA MCP) que NO requiere DLLs instaladas en el sistema ni escribe un solo byte en el Registro de Windows o en `%APPDATA%`.
3. **Agente 3: `UIUXAdversaryAgent` (Auditor de Interfaz, Temas y Compilación Documental):**
   - Automatiza pruebas de interfaz (UI Automation en Windows 11): prueba el cambio en caliente entre todos los temas, el redimensionamiento de divisores, el *Drag & Drop* en el Binder y el Corcho, el comparador Diff de Instantáneas y compila un proyecto completo a `.docx`, `.pdf`, `.epub` y `.fdx`, validando que los archivos exportados sean estructuralmente íntegros y contengan el texto y numeración `<$n>` exactos.
4. **Agente 4: `BlueTeamFixerAgent` (Ingeniero de Remediación y Parcheo):**
   - Recibe el informe JSON/Markdown de fallos generado por los 3 agentes del Equipo Rojo, diagnostica la causa raíz en el código fuente, implementa la corrección completa, recompila `Escritorio.exe` y devuelve el control al Equipo Rojo para la siguiente iteración del bucle.

Implementa el ejecutor automatizado `tests/redteam/run_adversarial_suite` que orquesta las pruebas y genera un informe auditable `tests/redteam/reports/audit_iteration_<N>.json` con conteo exacto de `critical_bugs`, `missing_features`, `ui_discrepancies` y `portability_violations`.
Haz commit y push a `https://github.com/tekkes/ESCRITORIO.git` (`develop`): "test(redteam): create adversarial verification & validation multi-agent framework in M:\61_PROYECTOS_IA\18_ESCRITORIO".

```

#### PROMPT 15: Ejecución del Bucle Adversarial Iterativo (Ciclo 1: Núcleo, Portabilidad, Binder y Editor)

```
Trabajando sobre `M:\61_PROYECTOS_IA\18_ESCRITORIO`, inicia el **Bucle Adversarial Interactivo (Red Team vs. Blue Team) - Fase A** enfocado en el Motor Portable, compatibilidad `.scriv`/`.escr`, el Cuaderno (*Binder*), Colecciones, el Editor RTF, Estilos y Modo *Scrivenings*.

Ejecuta el siguiente bucle autónomo e iterativo sin detenerte hasta que el contador de defectos sea exactamente 0:
1. **PASO 1 (Ataque Red Team):** Ejecuta los agentes `ParityInquisitorAgent` y `ChaosFuzzerAgent` sobre los módulos Core, Binder y Editor.
2. **PASO 2 (Evaluación):** Analiza el reporte generado. Si existe cualquier error de compilación, fuga de memoria, escritura fuera de la carpeta portable, dependencia de librerías externas no portables, fallo al dividir/fusionar escenas (`Ctrl+K` / `Ctrl+Shift+M`), desincronización en modo *Scrivenings* o fallo en el Foco Lingüístico:
   - Registra el hallazgo detallado en `tests/redteam/reports/`.
3. **PASO 3 (Remediación Blue Team):** Activa `BlueTeamFixerAgent` para programar la solución exacta en el código fuente (prohibido usar parches superficiales o deshabilitar tests).
4. **PASO 4 (Re-verificación en Bucle):** Recompila `Escritorio.exe` y vuelve al PASO 1.
5. Repite este ciclo iterativamente hasta que todos los tests pasen al 100% con `0 errores`, `0 carencias` y `0 discrepancias`.
6. Una vez alcanzado el estado limpio verificable, realiza commit y push a `https://github.com/tekkes/ESCRITORIO.git` (`develop`): "fix(core,editor): pass Red Team adversarial loop Phase A with zero defects".

```

#### PROMPT 16: Ejecución del Bucle Adversarial Iterativo (Ciclo 2: Corcho, Esquema, Inspector, Temas y Compilador)

```
Trabajando sobre `M:\61_PROYECTOS_IA\18_ESCRITORIO`, inicia el **Bucle Adversarial Interactivo (Red Team vs. Blue Team) - Fase B** enfocado en la Pizarra de Corcho, el Esquema, las 6 pestañas del Inspector, el Motor de Temas Visuales (`.scrtheme` / `.escrtheme`), el Modo Composición y el Motor de Compilación multiformato.

Ejecuta el bucle autónomo e iterativo hasta alcanzar CERO defectos:
1. **PASO 1 (Ataque Red Team):** Ejecuta `ParityInquisitorAgent`, `ChaosFuzzerAgent` y `UIUXAdversaryAgent` validando:
   - Los 3 modos del Corcho (Rejilla, Forma Libre y Apilado por Etiquetas) y la sincronización de sinopsis/imágenes.
   - El cálculo recursivo de palabras y barras de progreso en el Esquema (*Outliner*).
   - El comparador diferencial (*Myers Diff*) de Instantáneas y el `Rollback` en el Inspector.
   - La fidelidad cromática y visual de los modos Minimalista, Oscuro, Solarizado Claro/Oscuro, Sepia, Nord, Catppuccin y el cargador de temas `.scrtheme` de Scrivener, verificando que los iconos y etiquetas mantengan el tamaño compacto especificado.
   - La generación real y validación estructural de archivos compilados `.docx`, `.pdf`, `.epub`, `.rtf`, `.fdx` y `.md`.
2. **PASO 2 (Detección y Remediación en Bucle):** Por cada discrepancia visual, error de maquetación en la compilación o carencia funcional detectada, aplica la corrección en el código fuente, recompila `Escritorio.exe` y vuelve a lanzar el ataque del Equipo Rojo.
3. No finalices la ejecución hasta que el informe de auditoría confirme: `critical_bugs: 0`, `missing_features: 0`, `ui_discrepancies: 0`, `portability_violations: 0`.
4. Realiza commit y push a `https://github.com/tekkes/ESCRITORIO.git` (`develop`): "fix(ui,compile,themes): pass Red Team adversarial loop Phase B with zero defects".

```

#### PROMPT 17: Auditoría Integral de Extremo a Extremo (End-to-End Red Team Final Gate) y Certificación de Portabilidad

```
Ejecuta la **Auditoría Adversarial de Certificación Final (End-to-End Red Team Gate)** sobre el binario completo `Escritorio.exe` alojado en `M:\61_PROYECTOS_IA\18_ESCRITORIO` en Windows 11.

1. Ejecuta una simulación completa del flujo de vida de un escritor profesional en `Escritorio.exe`:
   - Crear un proyecto desde la plantilla "Novela con Partes".
   - Importar y dividir automáticamente (`Import and Split`) un documento externo en 30 escenas.
   - Reorganizar escenas en el Corcho por carriles de etiquetas (*Swimlanes*), añadir metadatos personalizados en el Esquema, tomar Instantáneas, editar en modo *Scrivenings* con pantalla dividida y usar el Modo Composición (`F11`).
   - Alternar en vivo entre el Modo Minimalista, Modo Oscuro, Modo Solarizado y Modo Sepia, y personalizar un tema en el *Live Theme Studio*.
   - Compilar la novela completa a `.docx`, `.pdf` y `.epub` evaluando todas las variables `<$n>`, `<$t>` y formatos de capítulo.
   - Cerrar el proyecto y verificar la generación automática del backup `.zip` verificable con SHA-256 y la portabilidad 100% limpia del directorio.
2. Verifica las métricas no funcionales y de portabilidad entre equipos:
   - Tiempo de arranque de `Escritorio.exe` $< 250\text{ ms}$.
   - Consumo de memoria RAM en reposo y bajo carga óptimo.
   - **Verificación de Tablas de Importación PE mediante REA MCP:** Confirma con evidencia binaria que `Escritorio.exe` tiene el runtime estáticamente enlazado y solo importa DLLs base del sistema operativo Windows 11 (`kernel32.dll`, `user32.dll`, `gdi32.dll`, `dwmapi.dll`, `shell32.dll`, `ole32.dll`, `comdlg32.dll`), garantizando que al copiar la carpeta a otro ordenador con Windows 11 funcionará al primer clic sin instalar nada.
3. Si cualquier métrica o prueba falla, entra en bucle de corrección hasta superarla al 100%.
4. Haz commit y push a `https://github.com/tekkes/ESCRITORIO.git` (`develop`): "perf(release): pass final E2E Red Team certification and optimize portable single-exe binary".

```

#### PROMPT 18: Empaquetado Portable Final, Script de Exportación, Pipeline CI/CD en GitHub Actions (`tekkes/ESCRITORIO`) y Release `v1.0.0`

```
Finaliza el proyecto en `M:\61_PROYECTOS_IA\18_ESCRITORIO` preparando la distribución portable de producción lista para copiar a cualquier ordenador con Windows 11 y el despliegue automatizado en el repositorio `https://github.com/tekkes/ESCRITORIO`.

Tareas finales:
1. Genera la carpeta autocontenida lista para entregar y copiar a otros equipos en `M:\61_PROYECTOS_IA\18_ESCRITORIO\dist\Escritorio_Portable_Win11\`:
   - `Escritorio.exe` (binario único estático optimizado).
   - `./config/` (archivos auxiliares iniciales de configuración portable con rutas relativas, temas preinstalados `.escrtheme`/`.scrtheme`, plantillas en español e inglés y diccionarios).
   - `README_USUARIO.md` (Manual de usuario completo en español explicando que basta con copiar esta carpeta a cualquier PC con Windows 11 y ejecutar `Escritorio.exe`).
2. Crea un script auxiliar `M:\61_PROYECTOS_IA\18_ESCRITORIO\scripts\export_portable_package.ps1` que empaquete `dist\Escritorio_Portable_Win11\` en `Escritorio_Portable_Win11.zip` y permita copiar únicamente esa carpeta limpia a un pendrive o unidad compartida cuando el usuario lo desee.
3. Crea el flujo de integración y entrega continua en `.github/workflows/release-windows11.yml` para el repositorio `tekkes/ESCRITORIO` de modo que GitHub Actions compile automáticamente `Escritorio.exe`, ejecute la suite del Equipo Rojo y adjunte el paquete portable en cada nueva etiqueta de versión (*Git Tag*).
4. Fusiona la rama `develop` en `main` (`git checkout main && git merge --no-ff develop`), crea el tag anotado `v1.0.0` y súbelo a `https://github.com/tekkes/ESCRITORIO.git` (`git push origin main --tags`).
5. Publica la Release oficial `v1.0.0` en `https://github.com/tekkes/ESCRITORIO/releases` usando GitHub MCP o `gh release create v1.0.0` adjuntando el paquete portable `Escritorio_Portable_Win11.zip` y el informe de certificación del Equipo Rojo con 0 defectos.

```

## 7. Arquitectura de Agentes de Validación y Verificación Adversarial (Red Team Loop)

Para garantizar que el bucle interactivo funcione con rigor matemático dentro de **Google Antigravity IDE**, a continuación se detalla el protocolo algorítmico y la plantilla de configuración del flujo adversarial en `M:\61_PROYECTOS_IA\18_ESCRITORIO`.

### 7.1. Diagrama Lógico del Bucle Adversarial en Antigravity IDE

$$
\text{Estado Inicial } S_0 \xrightarrow{\text{Compilación}} \text{Binario } \texttt{Escritorio.exe} \xrightarrow{\text{Ataque Equipo Rojo}} \Delta_{\text{errores}} = E_{\text{func}} + E_{\text{visual}} + E_{\text{portabilidad}} + E_{\text{crash}}
$$

* **Condición de Continuación del Bucle:** Mientras $\Delta_{\text{errores}} > 0$:

  1. El **Agente Inquisidor (Red Team)** extrae la traza exacta de fallo y la evidencia de discrepancia con Scrivener 3 (apoyándose en REA).

  2. El **Agente Constructor/Corrector (Blue Team)** genera el parche en el código fuente, añade un test de regresión específico para ese fallo y recompila `Escritorio.exe`.

  3. Se incrementa el contador de iteración $i \leftarrow i + 1$ y se re-ejecuta toda la batería desde el principio.

* **Condición de Parada y Entrega:** Cuando y solo cuando $\Delta_{\text{errores}} = 0$ en dos ejecuciones consecutivas independientes, el sistema declara el binario como **Certificado para Entrega** y sincroniza los cambios con `https://github.com/tekkes/ESCRITORIO.git`.

### 7.2. Archivo de Regla de Workflow para Antigravity IDE (`M:\61_PROYECTOS_IA\18_ESCRITORIO\.agents\workflows\redteam_loop.md`)

Guarda el siguiente bloque en `M:\61_PROYECTOS_IA\18_ESCRITORIO\.agents\workflows\redteam_loop.md` para poder invocarlo en cualquier momento escribiendo `/redteam_loop` en Antigravity IDE:

```
---
description: Ejecuta el bucle interactivo adversarial de Equipo Rojo (Red Team) y Equipo Azul (Blue Team) en M:\61_PROYECTOS_IA\18_ESCRITORIO hasta alcanzar cero errores, carencias o discrepancias en Escritorio.exe
---

# Protocolo de Ejecución del Bucle Adversarial (Red Team V&V Loop)

Directorio de trabajo: `M:\61_PROYECTOS_IA\18_ESCRITORIO`
Repositorio remoto: `https://github.com/tekkes/ESCRITORIO.git`

1. **Inspección de Binario Portable con REA MCP:**
   - Ejecuta la verificación de tablas de importación y símbolos sobre `M:\61_PROYECTOS_IA\18_ESCRITORIO\build\release\Escritorio.exe` usando las herramientas MCP de `rea` para confirmar que es un ejecutable 100% autónomo con runtime estático (`/MT` o `+crt-static`) capaz de ejecutarse en cualquier otro PC con Windows 11 sin instalar dependencias.

2. **Matriz de Verificación Adversarial Obligatoria (Checklist de Equipo Rojo):**
   - [ ] **Portabilidad "Copy & Run":** Copiar `Escritorio.exe` y `./config/` a un directorio temporal aislado, ejecutarlo y auditar que 0 bytes se escriben en `%APPDATA%` o en el Registro de Windows, y que todas las configuraciones usan rutas relativas.
   - [ ] **Compatibilidad de Proyecto:** Abrir un proyecto `.scriv` real y un proyecto `.escr`, editar 10 documentos, forzar cierre abrupto y verificar recuperación íntegra.
   - [ ] **Binder y Estructura:** Probar `Split at Selection`, `Merge`, `Group`, `Ungroup`, cambio de micro-iconos SVG y `Collections`.
   - [ ] **Vistas de Grupo:** Probar fluidez en modo `Scrivenings` (edición continua multipartita), `Corkboard` (modos Grid, Freeform y Swimlanes por Label) y `Outliner` (ordenación y barras de progreso).
   - [ ] **Editor e Inspector:** Probar `Split Screen` (2 y 4 paneles), `Page View`, `Typewriter Scrolling`, `Linguistic Focus`, `Scriptwriting Mode` y las 6 pestañas del Inspector incluyendo el comparador `Diff` de `Snapshots`.
   - [ ] **Modos Visuales y Densidad:** Verificar renderizado sin artefactos en Modo Minimalista, Modo Oscuro, Modo Solarizado (Oscuro/Claro), Modo Sepia, temas `.scrtheme` importados y tamaño compacto de iconos ($14\text{--}16\text{ px}$) y micro-etiquetas.
   - [ ] **Compilador:** Compilar el proyecto de prueba a `.docx`, `.pdf`, `.epub`, `.rtf`, `.fdx` y `.md` y verificar que los archivos de salida existen, no están vacíos y pasan la validación de esquema.

3. **Regla de Iteración Incondicional:**
   - Si CUALQUIER punto de la matriz anterior falla o presenta una carencia, tienes PROHIBIDO dar por terminada la tarea o pedir intervención manual al usuario.
   - Debes diagnosticar el fallo, editar los archivos de código fuente correspondientes, recompilar `Escritorio.exe` y volver al Paso 1 automáticamente hasta que el 100% de la matriz esté validada sin errores.

```

## 8. Instrucciones Rápidas para Exportar esta Guía a PDF

1. **Desde Google Antigravity IDE o VS Code:** Abre este archivo alojado en `M:\61_PROYECTOS_IA\18_ESCRITORIO\guia_desarrollo_escritorio.md` con la extensión *Markdown PDF* y selecciona `Clic derecho > Markdown PDF: Export (pdf)`.

2. **Con Pandoc en PowerShell 7:**

   ```
   Set-Location -Path "M:\61_PROYECTOS_IA\18_ESCRITORIO"
   pandoc "guia_desarrollo_escritorio.md" -o "Guia_Desarrollo_Escritorio_Win11.pdf" --pdf-engine=xelatex -V geometry:margin=2cm --toc
   
   ```