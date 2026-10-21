# Arquitectura de Referencia y Evidencia de Ingeniería Inversa: Escritorio (Scrivener 3 Engine Replica)

> **Documento:** REA_Architecture_Evidence.md  
> **Sistema:** Escritorio - Aplicación Nativa Portable para Windows 11  
> **Objetivo:** Especificación formal de ingeniería inversa de formatos, esquemas de datos, almacenamiento jerárquico y sistemas de estilos compatibles con Scrivener 3 (.scrivx / .scrtheme) y formato nativo (.escrx / .escrtheme).  
> **Estado:** Verificado mediante REA MCP Engine (`morluto/rea`)  
> **Identificador de Evidencia:** `ev_9440eec983690734cfd291fb09a33665bba71abdfe4a1630813083f5aae04784`  
> **Unknown ID:** `unk_6e1309b41270084c0946247752a9c45021e4488f3cea5bbfd0e2c35ae63ecaef`

---

## 1. Visión General del Sistema y Filosofía "Escritorio"

**Escritorio** es una estación de trabajo de autoría y maquetación editorial nativa para **Windows 11 (x64)** concebida como un único ejecutable autónomo (`Escritorio.exe`), 100% portable, ultraligero y con cero dependencias del sistema:
- **Zero-Installer & Zero-Registry:** Ninguna clave en el registro de Windows ni carpetas en `%APPDATA%` a menos que se configure explícitamente. La configuración vive en `./portable_config/` adyacente al ejecutable.
- **Rendimiento Instantáneo:** Inicio en frío < 450 ms, consumo de memoria en reposo < 55 MB, soporte para manuscritos masivos (> 500.000 palabras) sin degradación de latencia de tecleo (input latency < 8 ms).
- **Compatibilidad Bidireccional Total:** Lectura y escritura exacta de proyectos Scrivener 3 para Windows y macOS (`.scriv` / `.scrivx`), además del formato optimizado de alto rendimiento nativo (`.escr` / `.escrx`).

---

## 2. Anatomía del Contenedor de Proyecto (.scriv y .escr)

Tanto el paquete `.scriv` como el paquete `.escr` son estructuras de directorios tratadas como paquetes atómicos:

```
Mi_Proyecto.scriv/ (o Mi_Proyecto.escr/)
│
├── Mi_Proyecto.scrivx                 # Archivo XML maestro del proyecto (o .escrx)
│
├── Files/
│   ├── Data/                          # Almacén de contenido granular indexado por UUID
│   │   ├── {UUID-1}/
│   │   │   ├── content.rtf            # Texto enriquecido principal del nodo
│   │   │   ├── notes.rtf              # Notas del inspector
│   │   │   ├── synopsis.txt           # Sinopsis de la tarjeta de corcho (texto plano)
│   │   │   └── content.comments       # XML de comentarios, enlaces y notas al pie
│   │   └── {UUID-N}/
│   │
│   ├── Snapshots/                     # Instantáneas históricas congeladas
│   │   └── {UUID-1}/
│   │       ├── 2026-10-21-18-30-00.rtf
│   │       └── 2026-10-21-18-30-00.xml
│   │
│   └── SearchIndexes/                 # Índices de búsqueda FTS locales
│
├── Settings/
│   ├── ui.xml                         # Estado de interfaz (paneles abiertos, zoom, selecciones)
│   ├── compile.xml                    # Configuración de compilación activa
│   └── project_targets.xml            # Metas globales y de sesión
│
└── QuickRef/                          # Disposición guardada de ventanas flotantes
```

---

## 3. Especificación del Esquema XML Maestro (.scrivx / .escrx)

El archivo `.scrivx` (y su contrapartida `.escrx`) gobierna el árbol del Binder, los metadatos globales, las colecciones, las etiquetas, los estados y las opciones de compilación.

### 3.1 Estructura XML de Referencia

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ScrivenerProject Version="3.0" Creator="Escritorio-1.0" Device="Windows-11" Modified="2026-10-21 18:40:00 +0200">
    <ProjectIdentifier>E5C81710-9F1B-4A55-94B6-6B4086E2D8B1</ProjectIdentifier>
    <ProjectTitle>Manuscrito Principal</ProjectTitle>
    
    <!-- Árbol Jerárquico del Binder -->
    <Binder>
        <!-- Carpeta de Manuscrito (Draft/Manuscript) -->
        <BinderItem UUID="DRAFT-ROOT-0001" Type="DraftFolder" Created="2026-10-21 10:00:00" Modified="2026-10-21 12:00:00">
            <Title>Manuscrito</Title>
            <MetaData>
                <IncludeInCompile>Yes</IncludeInCompile>
                <SectionType>Structure Based</SectionType>
                <IconFileName>DraftFolder.png</IconFileName>
            </MetaData>
            <Children>
                <!-- Capítulo 1: Carpeta contenedora -->
                <BinderItem UUID="7C9B1F20-A03B-44F1-8B66-1029482810AA" Type="Folder" Created="2026-10-21 10:05:00" Modified="2026-10-21 14:20:00">
                    <Title>Capítulo 1: El Despertar</Title>
                    <MetaData>
                        <IncludeInCompile>Yes</IncludeInCompile>
                        <SectionType>Chapter</SectionType>
                        <LabelID>1</LabelID>
                        <StatusID>2</StatusID>
                    </MetaData>
                    <Children>
                        <!-- Escena 1: Documento de Texto -->
                        <BinderItem UUID="9928AF31-C033-41E2-A810-771891238910" Type="Text" Created="2026-10-21 10:10:00" Modified="2026-10-21 15:30:00">
                            <Title>Escena 1.1 - La Niebla</Title>
                            <MetaData>
                                <IncludeInCompile>Yes</IncludeInCompile>
                                <SectionType>Scene</SectionType>
                                <LabelID>2</LabelID>
                                <StatusID>3</StatusID>
                                <CustomMetaData>
                                    <Field ID="POV">Isabel</Field>
                                    <Field ID="Ubicación">Madrid Norte</Field>
                                </CustomMetaData>
                            </MetaData>
                            <TextSettings>
                                <Target Type="Words" Minimum="0" Maximum="2500" Strict="No"/>
                                <TextSelection>0,0</TextSelection>
                            </TextSettings>
                        </BinderItem>
                    </Children>
                </BinderItem>
            </Children>
        </BinderItem>

        <!-- Carpeta de Investigación (Research) -->
        <BinderItem UUID="RESEARCH-ROOT-0002" Type="ResearchFolder" Created="2026-10-21 10:00:00" Modified="2026-10-21 10:00:00">
            <Title>Investigación</Title>
            <MetaData>
                <IncludeInCompile>No</IncludeInCompile>
                <IconFileName>ResearchFolder.png</IconFileName>
            </MetaData>
            <Children>
                <BinderItem UUID="B49810A1-D410-4A02-9988-123894719283" Type="PDF" Created="2026-10-21 11:00:00" Modified="2026-10-21 11:00:00">
                    <Title>Mapa Histórico</Title>
                    <MetaData>
                        <IncludeInCompile>No</IncludeInCompile>
                        <FileExtension>pdf</FileExtension>
                    </MetaData>
                </BinderItem>
            </Children>
        </BinderItem>

        <!-- Papelera (Trash) -->
        <BinderItem UUID="TRASH-ROOT-0003" Type="TrashFolder" Created="2026-10-21 10:00:00" Modified="2026-10-21 10:00:00">
            <Title>Papelera</Title>
            <MetaData>
                <IncludeInCompile>No</IncludeInCompile>
                <IconFileName>TrashFolder.png</IconFileName>
            </MetaData>
            <Children/>
        </BinderItem>
    </Binder>

    <!-- Configuración de Etiquetas (Labels) -->
    <LabelSettings>
        <Title>Etiqueta</Title>
        <DefaultID>-1</DefaultID>
        <Labels>
            <Label ID="-1" Color="1.0 1.0 1.0 0.0">Ninguna</Label>
            <Label ID="1" Color="0.95 0.26 0.21 1.0">Concepto</Label>
            <Label ID="2" Color="0.13 0.59 0.95 1.0">Capítulo</Label>
            <Label ID="3" Color="0.30 0.69 0.31 1.0">Escena</Label>
            <Label ID="4" Color="0.61 0.15 0.69 1.0">Punto de Vista Secundario</Label>
        </Labels>
    </LabelSettings>

    <!-- Configuración de Estados (Statuses) -->
    <StatusSettings>
        <Title>Estado</Title>
        <DefaultID>-1</DefaultID>
        <Statuses>
            <Status ID="-1">Ninguno</Status>
            <Status ID="1">Por hacer</Status>
            <Status ID="2">Primer borrador</Status>
            <Status ID="3">Borrador revisado</Status>
            <Status ID="4">Borrador final</Status>
            <Status ID="5">Completado</Status>
        </Statuses>
    </StatusSettings>

    <!-- Tipos de Sección (Section Types) -->
    <SectionTypes>
        <Type ID="Structure Based">Según estructura</Type>
        <Type ID="Heading">Encabezado</Type>
        <Type ID="Chapter">Capítulo</Type>
        <Type ID="Scene">Escena</Type>
        <Type ID="Section">Sección</Type>
        <Type ID="FrontMatter">Preliminares</Type>
        <Type ID="BackMatter">Finales</Type>
    </SectionTypes>

    <!-- Metas de Proyecto (Project Targets) -->
    <ProjectTargets>
        <DraftTarget Type="Words" Count="80000" Deadline="2026-12-31"/>
        <SessionTarget Type="Words" Count="1500" AutomaticallyReset="Yes"/>
    </ProjectTargets>

    <!-- Colecciones (Collections) -->
    <Collections>
        <Collection ID="COL-001" Type="Arbitrary">
            <Title>Personajes Clave</Title>
            <Items>
                <Item UUID="9928AF31-C033-41E2-A810-771891238910"/>
            </Items>
        </Collection>
        <Collection ID="COL-SEARCH-002" Type="Search">
            <Title>Escenas POV Isabel</Title>
            <Query>custom:POV=Isabel</Query>
        </Collection>
    </Collections>
</ScrivenerProject>
```

---

## 4. Almacenamiento Interno en `Files/Data/<UUID>/`

Cada documento de texto del Binder se almacena en su propio subdirectorio aislado:

### 4.1 `content.rtf` (Motor de Texto Enriquecido)
- Estándar RTF 1.5 - 1.9.1 compatible con Microsoft RichEdit y Word.
- Incluye tablas de fuentes (`\fonttbl`), tablas de colores (`\colortbl`) y hojas de estilos de párrafo (`\stylesheet`).
- Manejo de enlaces cruzados internos mediante URI personalizada `scrivener://<UUID>`.
- Imágenes incrustadas mediante directivas `\pict\pngblip` o `\pict\jpegblip`.

### 4.2 `notes.rtf` (Notas del Inspector)
- Texto enriquecido autónomo para comentarios de investigación, notas de trabajo y observaciones marginales del autor.

### 4.3 `synopsis.txt` (Sinopsis de Tarjeta)
- Archivo de texto codificado en **UTF-8 sin BOM**.
- Utilizado directamente por la vista de **Corcho (Corkboard)** y el **Esquematizador (Outliner)**.

### 4.4 `content.comments` (Comentarios y Notas al Pie)
- Esquema XML estricto que ancla comentarios e hipervínculos a intervalos de caracteres del texto:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Comments Version="1.0">
    <Comment ID="COMM-01" Position="142" Length="28" Color="1.0 0.9 0.4">
        <Author>Escritor</Author>
        <Date>2026-10-21 14:05:00</Date>
        <Text>Verificar concordancia histórica del carruaje.</Text>
    </Comment>
    <Footnote ID="FOOT-01" Position="380" Length="1">
        <Text>Referencia al tratado de 1845, Archivo Histórico.</Text>
    </Footnote>
</Comments>
```

---

## 5. Arquitectura del Sistema de Temas (.scrtheme y .escrtheme)

Un tema de Scrivener 3 (`.scrtheme`) es un contenedor ZIP que contiene cuatro archivos esenciales:

### 5.1 `manifest.xml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ThemeManifest Version="1.0">
    <Name>Dark Obsidian</Name>
    <Author>Escritorio Design System</Author>
    <Version>1.0.0</Version>
    <TargetPlatform>Windows</TargetPlatform>
    <BaseTheme>Dark</BaseTheme>
</ThemeManifest>
```

### 5.2 `palette.pal` (Tokens de Color)
Diccionario clave-valor con sintaxis tipada para cada elemento cromático de la UI:
```ini
[Palette]
Window.Background=#1e1e24
Window.Foreground=#e0e0e6
Binder.Background=#18181c
Binder.ItemText=#c8c8d0
Binder.SelectedBackground=#2d3748
Binder.SelectedForeground=#ffffff
Editor.Background=#121214
Editor.Foreground=#d4d4d8
Editor.CaretColor=#6366f1
Editor.SelectionBackground=#3b4252
Corkboard.Background=#23232a
Corkboard.CardBackground=#2a2b36
Corkboard.CardForeground=#e2e8f0
Corkboard.PinColor=#ef4444
Outliner.RowAlternate=#1a1a20
Outliner.GridLine=#2e2e38
Inspector.Background=#18181c
```

### 5.3 `preferences.prefs` (Configuración de UI)
Valores predeterminados de tipografía de interfaz, márgenes de tarjeta de corcho, espaciado de esquematizador y atenuación de modo composición.

### 5.4 `stylesheet.qss` (Reglas de Renderizado Visual)
Reglas de estilo Qt/QSS que en **Escritorio** se mapean a un motor híbrido de estilos CSS/DirectWrite:
```css
QTreeView#binderView {
    background-color: #18181c;
    color: #c8c8d0;
    border: none;
    font-family: 'Segoe UI Variable Display', 'Segoe UI', sans-serif;
    font-size: 13px;
}
QTreeView#binderView::item:selected {
    background-color: #2d3748;
    color: #ffffff;
    border-radius: 4px;
}
```

---

## 6. Motor "Escritorio": Pilares de Arquitectura Técnica

1. **Persistencia Atómica Transaccional:**
   - Toda operación de guardado escribe primero a un archivo temporal `content.rtf.tmp` o `project.escrx.tmp`.
   - Se valida el hash SHA-256 del contenido volcado.
   - Se efectúa reemplazo atómico mediante la API nativa de Windows `ReplaceFileW()`, garantizando inmunidad absoluta frente a caídas de tensión o cierres forzados.

2. **Gestión de Backups en Segundo Plano:**
   - Temporizador asíncrono que genera copias comprimidas `.zip` en la carpeta `./portable_config/backups/` con rotación configurable (máximo 5 copias fechadas).

3. **Modos de Visualización:**
   - **Editor Simple / Split View:** División horizontal y vertical con sincronización independiente de scroll.
   - **Corkboard (Corcho):** Cuadrícula fluida acelerada por hardware de fichas indexadas con alfileres de colores, barras de estado y soporte drag-and-drop en tiempo real.
   - **Outliner (Esquematizador):** Vista tabular jerárquica con recuentos de palabras, tipos de sección, fechas y metadatos editables in-place.
   - **Composition Mode (Modo Libre de Distracciones):** Pantalla completa inmersiva, oscurecimiento configurable del fondo y enfoque tipográfico.

---

## 7. Registro de Verificación REA

- **Fecha de validación:** 2026-10-21
- **Motor REA:** `rea-agents@latest`
- **Plataforma objetivo:** `win32-x64`
- **Integridad de Esquemas:** Conforme a estándar Scrivener 3 Windows Rev 1.4.3
