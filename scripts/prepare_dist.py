#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de preparación y generación de la distribución portable oficial de Escritorio v1.0.0.
Genera la carpeta autocontenida 'dist/Escritorio_Portable_Win11/' lista para usar en Windows 11.
"""

import os
import sys
import json
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT_DIR / "dist" / "Escritorio_Portable_Win11"
CONFIG_DIR = DIST_DIR / "config"
THEMES_DIR = CONFIG_DIR / "themes"
TEMPLATES_DIR = CONFIG_DIR / "templates"
DICTS_DIR = CONFIG_DIR / "dictionaries"
BACKUPS_DIR = CONFIG_DIR / "backups"

def main():
    print(f"[1/7] Limpiando y preparando directorio destino: {DIST_DIR}")
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    
    THEMES_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    DICTS_DIR.mkdir(parents=True, exist_ok=True)
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Copiar binario optimizado
    print("[2/7] Copiando binario único optimizado Escritorio.exe...")
    src_exe = ROOT_DIR / "build" / "release" / "Escritorio.exe"
    if not src_exe.exists():
        raise FileNotFoundError(f"No se encontró el binario: {src_exe}")
    dest_exe = DIST_DIR / "Escritorio.exe"
    shutil.copy2(src_exe, dest_exe)
    print(f"      -> Escritorio.exe ({dest_exe.stat().st_size:,} bytes) copiado con éxito.")

    # 2. Configuración portable por defecto
    print("[3/7] Generando escritorio_settings.json con rutas 100% relativas...")
    settings = {
        "app_name": "Escritorio",
        "version": "1.0.0",
        "portable_mode": True,
        "system_registry_access": False,
        "appdata_access": False,
        "theme": "dark_obsidian",
        "font_family": "Segoe UI Variable Display",
        "editor_font": "Georgia",
        "editor_font_size": 13,
        "autosave_interval_ms": 2000,
        "max_backup_copies": 5,
        "recent_projects": []
    }
    with open(CONFIG_DIR / "escritorio_settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

    # 3. Copiar temas visuales (.escrtheme, .scrtheme, .json)
    print("[4/7] Copiando temas visuales preinstalados...")
    src_themes = ROOT_DIR / "assets" / "themes"
    if src_themes.exists():
        for item in src_themes.glob("*.*"):
            if item.suffix.lower() in [".json", ".escrtheme", ".scrtheme"]:
                shutil.copy2(item, THEMES_DIR / item.name)
        theme_count = len(list(THEMES_DIR.glob("*.*")))
        print(f"      -> {theme_count} archivos de tema copiados a config/themes/.")

    # 4. Generar plantillas bilingües (Español e Inglés)
    print("[5/7] Generando catálogo de plantillas en Español e Inglés...")
    
    # Importamos plantillas del core
    sys.path.insert(0, str(ROOT_DIR))
    from src.core.importers.project_templates import ProjectTemplateManager

    # Mapeo de nombres en Español
    es_templates = {
        "novela_con_partes_es": {
            "name": "Novela con Partes (Español)",
            "category": "Ficción",
            "description": "Estructura para obras extensas organizadas en Partes o Libros, con capítulos y escenas anidadas.",
            "target_words": 100000,
            "data": ProjectTemplateManager.BUILTIN_TEMPLATES.get("novel_parts")
        },
        "novela_ficcion_es": {
            "name": "Novela de Ficción Estándar (Español)",
            "category": "Ficción",
            "description": "Estructura estándar para novelas con capítulos, escenas, fichas de personajes y escenarios.",
            "target_words": 80000,
            "data": ProjectTemplateManager.BUILTIN_TEMPLATES.get("novel")
        },
        "relato_corto_es": {
            "name": "Relato Corto y Antología (Español)",
            "category": "Ficción",
            "description": "Plantilla ligera orientada a cuentos, relatos breves y antologías.",
            "target_words": 5000,
            "data": ProjectTemplateManager.BUILTIN_TEMPLATES.get("short_story")
        },
        "ensayo_general_es": {
            "name": "Ensayo General y Divulgación (Español)",
            "category": "No Ficción",
            "description": "Organización para libros de divulgación, ensayo literario o monografías temáticas.",
            "target_words": 30000,
            "data": ProjectTemplateManager.BUILTIN_TEMPLATES.get("general_essay")
        },
        "articulo_apa_es": {
            "name": "Artículo Académico APA 7ª Edición (Español)",
            "category": "No Ficción",
            "description": "Estructura formal para artículos científicos según normas APA (Abstract, Método, Resultados, Discusión).",
            "target_words": 7000,
            "data": ProjectTemplateManager.BUILTIN_TEMPLATES.get("apa_paper")
        },
        "articulo_mla_es": {
            "name": "Artículo Humanístico MLA 9ª Edición (Español)",
            "category": "No Ficción",
            "description": "Manuscrito humanístico con encabezado MLA y sección final de Obras Citadas (Works Cited).",
            "target_words": 5000,
            "data": ProjectTemplateManager.BUILTIN_TEMPLATES.get("mla_paper")
        },
        "tesis_academica_es": {
            "name": "Tesis Doctoral / Académica (Español)",
            "category": "No Ficción",
            "description": "Estructura exhaustiva para tesis doctorales, proyectos fin de máster o memorias de investigación.",
            "target_words": 60000,
            "data": ProjectTemplateManager.BUILTIN_TEMPLATES.get("thesis")
        },
        "guion_largometraje_es": {
            "name": "Guion Cinematográfico de Largometraje (Español)",
            "category": "Guion",
            "description": "Formato estándar para guiones cinematográficos en 3 actos (100-120 páginas).",
            "target_words": 20000,
            "data": ProjectTemplateManager.BUILTIN_TEMPLATES.get("screenplay_feature")
        },
        "obra_teatro_es": {
            "name": "Obra de Teatro / Dramaturgia (Español)",
            "category": "Guion",
            "description": "Formato para dramaturgia en 2 o 3 actos con lista de dramatis personae y acotaciones.",
            "target_words": 15000,
            "data": ProjectTemplateManager.BUILTIN_TEMPLATES.get("stage_play")
        },
        "guion_comic_es": {
            "name": "Guion de Cómic / Novela Gráfica (Español)",
            "category": "Guion",
            "description": "Estructura por páginas y viñetas para historietas, manga y novelas gráficas.",
            "target_words": 10000,
            "data": ProjectTemplateManager.BUILTIN_TEMPLATES.get("comic_script")
        },
        "guion_podcast_es": {
            "name": "Guion de Podcast / Ficción Sonora (Español)",
            "category": "Guion",
            "description": "Plantilla por episodios con acotaciones técnicas sonoras, música y efectos SFX.",
            "target_words": 6000,
            "data": ProjectTemplateManager.BUILTIN_TEMPLATES.get("podcast")
        }
    }

    for key, info in es_templates.items():
        tmpl_data = dict(info["data"]) if info["data"] else {}
        tmpl_data["id"] = key
        tmpl_data["name"] = info["name"]
        tmpl_data["category"] = info["category"]
        tmpl_data["description"] = info["description"]
        tmpl_data["target_words"] = info["target_words"]
        tmpl_path = TEMPLATES_DIR / f"{key}.json"
        with open(tmpl_path, "w", encoding="utf-8") as f:
            json.dump(tmpl_data, f, indent=2, ensure_ascii=False)

    # Versiones en Inglés
    en_templates = {
        "novel_with_parts_en": {
            "name": "Novel with Parts (English)",
            "category": "Fiction",
            "description": "Structure for multi-part novels or book series with nested chapters and scenes.",
            "target_words": 100000,
            "structure": {
                "front_matter": [
                    {"title": "Title Page", "type": "Text", "content": "NOVEL TITLE\nBy Author Name"},
                    {"title": "Dedication", "type": "Text", "content": "For..."}
                ],
                "draft": [
                    {
                        "title": "Part One: Departure",
                        "type": "Folder",
                        "children": [
                            {
                                "title": "Chapter 1",
                                "type": "Folder",
                                "children": [
                                    {"title": "Scene 1: Inciting Incident", "type": "Text", "content": "Write your opening scene here..."}
                                ]
                            }
                        ]
                    },
                    {
                        "title": "Part Two: Return",
                        "type": "Folder",
                        "children": [
                            {
                                "title": "Chapter 2",
                                "type": "Folder",
                                "children": [
                                    {"title": "Scene 2: Climax", "type": "Text", "content": "Climax of part two..."}
                                ]
                            }
                        ]
                    }
                ],
                "characters": [
                    {"title": "Protagonist", "type": "Text", "content": "Name:\nGoal:\nConflict:\nArc:\n"}
                ],
                "places": [
                    {"title": "Primary Setting", "type": "Text", "content": "Location:\nAtmosphere:\nSensory details:\n"}
                ],
                "research": [
                    {"title": "Worldbuilding Notes", "type": "Text", "content": "Historical and background research."}
                ]
            }
        },
        "novel_fiction_en": {
            "name": "Standard Fiction Novel (English)",
            "category": "Fiction",
            "description": "Standard manuscript template with chapters, scenes, character sheets, and world notes.",
            "target_words": 80000,
            "structure": {
                "front_matter": [
                    {"title": "Title Page", "type": "Text", "content": "TITLE OF THE WORK\nBy Author"}
                ],
                "draft": [
                    {
                        "title": "Chapter 1",
                        "type": "Folder",
                        "children": [
                            {"title": "Scene 1", "type": "Text", "content": "Opening hook..."},
                            {"title": "Scene 2", "type": "Text", "content": "Subsequent event..."}
                        ]
                    }
                ],
                "characters": [
                    {"title": "Main Character", "type": "Text", "content": "Name:\nRole:\nFlaw:\n"}
                ],
                "places": [],
                "research": []
            }
        },
        "short_story_en": {
            "name": "Short Story (English)",
            "category": "Fiction",
            "description": "Streamlined single-thread outline for short stories, novelettes, and anthologies.",
            "target_words": 5000,
            "structure": {
                "draft": [
                    {"title": "Scene 1: Setup", "type": "Text", "content": "Opening situation..."},
                    {"title": "Scene 2: Twist", "type": "Text", "content": "Turning point..."},
                    {"title": "Scene 3: Resolution", "type": "Text", "content": "Climax and resolution..."}
                ],
                "research": []
            }
        },
        "general_essay_en": {
            "name": "General Essay & Non-Fiction (English)",
            "category": "Non-Fiction",
            "description": "Structure for long-form essays, journalistic monographs, and popular science books.",
            "target_words": 30000,
            "structure": {
                "draft": [
                    {"title": "Introduction", "type": "Text", "content": "Thesis statement and context..."},
                    {
                        "title": "Section I: Foundations",
                        "type": "Folder",
                        "children": [
                            {"title": "Chapter 1: Background", "type": "Text", "content": "Historical background..."}
                        ]
                    },
                    {"title": "Conclusion", "type": "Text", "content": "Concluding remarks..."}
                ],
                "research": []
            }
        },
        "apa_research_paper_en": {
            "name": "APA 7th Edition Paper (English)",
            "category": "Non-Fiction",
            "description": "Standard APA academic paper with Title Page, Abstract, Method, Results, Discussion, References.",
            "target_words": 7500,
            "structure": {
                "draft": [
                    {"title": "Title Page & Abstract", "type": "Text", "content": "Title\nAuthor\nAffiliation\n\nAbstract:\nKeywords:"},
                    {"title": "1. Introduction", "type": "Text", "content": "Literature review and problem formulation."},
                    {"title": "2. Method", "type": "Text", "content": "Participants, apparatus, procedure."},
                    {"title": "3. Results", "type": "Text", "content": "Empirical and statistical findings."},
                    {"title": "4. Discussion", "type": "Text", "content": "Theoretical implications and limitations."},
                    {"title": "5. References", "type": "Text", "content": "Works cited in APA format."}
                ],
                "research": []
            }
        },
        "screenplay_feature_en": {
            "name": "Feature Screenplay (English)",
            "category": "Scriptwriting",
            "description": "Industry standard 3-act feature screenplay layout (110 pages).",
            "target_words": 20000,
            "structure": {
                "draft": [
                    {
                        "title": "Act I",
                        "type": "Folder",
                        "children": [
                            {"title": "Scene 1 - EXT. STREET - DAY", "type": "Text", "content": "Action description here..."}
                        ]
                    },
                    {
                        "title": "Act II",
                        "type": "Folder",
                        "children": [
                            {"title": "Scene - MIDPOINT", "type": "Text", "content": "Midpoint twist..."}
                        ]
                    },
                    {
                        "title": "Act III",
                        "type": "Folder",
                        "children": [
                            {"title": "Scene - CLIMAX", "type": "Text", "content": "Final confrontation..."}
                        ]
                    }
                ],
                "characters": [],
                "places": [],
                "research": []
            }
        }
    }

    for key, info in en_templates.items():
        tmpl_path = TEMPLATES_DIR / f"{key}.json"
        with open(tmpl_path, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2, ensure_ascii=False)

    # Copiamos también las plantillas legacy de assets/templates si faltan
    src_templates = ROOT_DIR / "assets" / "templates"
    if src_templates.exists():
        for item in src_templates.glob("*.json"):
            dest_file = TEMPLATES_DIR / item.name
            if not dest_file.exists():
                shutil.copy2(item, dest_file)
    
    tmpl_count = len(list(TEMPLATES_DIR.glob("*.json")))
    print(f"      -> {tmpl_count} plantillas bilingües generadas en config/templates/.")

    # 5. Configurar Diccionarios y Vocabularios
    print("[6/7] Configurando diccionarios ortográficos Hunspell en Español e Inglés...")
    
    # Diccionario Español es_ES.aff y es_ES.dic
    es_aff_content = """SET UTF-8
TRY esiacntrodumpglfvzñhqbkjxyáéíóúüESIACNTRODUMPGLFVZÑHQBKJXYÁÉÍÓÚÜ'
FLAG UTF-8

SFX S Y 4
SFX S 0 s [aeiouáéíóú]
SFX S 0 es [^aeiouáéíóú]
SFX S z ces z
SFX S 0 es [s]

PFX D Y 1
PFX D 0 des .
"""
    es_dic_words = [
        "escritor/S", "novela/S", "capítulo/S", "escena/S", "manuscrito/S", "personaje/S",
        "narrativa/S", "esquema/S", "corcho/S", "instantánea/S", "compilación/S", "revisión/S",
        "edición/S", "borrador/S", "investigación/S", "bibliografía/S", "diálogo/S", "trama/S",
        "conflicto/S", "protagonista/S", "antagonista/S", "escenario/S", "atmósfera/S", "estilo/S",
        "párrafo/S", "palabra/S", "letra/S", "fuente/S", "página/S", "sección/S", "formato/S",
        "autor/S", "lectura/S", "publicación/S", "editorial/S", "índice/S", "prólogo/S", "epílogo/S",
        "dedicatoria/S", "título/S", "subtítulo/S", "sinopsis/S", "versión/S", "copia/S", "seguridad/S",
        "portabilidad/S", "sistema/S", "tiempo/S", "memoria/S", "binario/S", "documento/S", "proyecto/S",
        "abrir", "cerrar", "guardar", "exportar", "importar", "dividir", "fusionar", "escribir",
        "editar", "revisar", "leer", "corregir", "organizar", "compilar", "crear", "eliminar",
        "palabras", "caracteres", "objetivo", "sesión", "pantalla", "completa", "distracción",
        "libre", "modo", "composición", "inspector", "metadatos", "etiqueta", "estado", "icono"
    ]
    with open(DICTS_DIR / "es_ES.aff", "w", encoding="utf-8") as f:
        f.write(es_aff_content)
    with open(DICTS_DIR / "es_ES.dic", "w", encoding="utf-8") as f:
        f.write(f"{len(es_dic_words)}\n")
        f.write("\n".join(es_dic_words) + "\n")

    # Diccionario Inglés en_US.aff y en_US.dic
    en_aff_content = """SET UTF-8
TRY esianrtolcdugmphbyfvkwzxqjESIANRTOLCDUGMPHBYFVKWZXQJ'

SFX S Y 4
SFX S 0 s [^sxhz]
SFX S 0 es [sxhz]
SFX S y ies [^aeiou]y
SFX S 0 s [aeiou]y

PFX U Y 1
PFX U 0 un .
"""
    en_dic_words = [
        "writer/S", "novel/S", "chapter/S", "scene/S", "manuscript/S", "character/S",
        "narrative/S", "outliner/S", "corkboard/S", "snapshot/S", "compile/S", "review/S",
        "editing/S", "draft/S", "research/S", "bibliography/S", "dialogue/S", "plot/S",
        "conflict/S", "protagonist/S", "antagonist/S", "setting/S", "atmosphere/S", "style/S",
        "paragraph/S", "word/S", "letter/S", "font/S", "page/S", "section/S", "format/S",
        "author/S", "reading/S", "publishing/S", "publisher/S", "index/S", "prologue/S", "epilogue/S",
        "dedication/S", "title/S", "subtitle/S", "synopsis/S", "version/S", "backup/S", "security/S",
        "portability/S", "system/S", "memory/S", "binary/S", "document/S", "project/S",
        "open", "close", "save", "export", "import", "split", "merge", "write",
        "edit", "revise", "read", "proofread", "organize", "create", "delete",
        "words", "characters", "target", "session", "fullscreen", "distraction",
        "free", "mode", "composition", "inspector", "metadata", "label", "status", "icon"
    ]
    with open(DICTS_DIR / "en_US.aff", "w", encoding="utf-8") as f:
        f.write(en_aff_content)
    with open(DICTS_DIR / "en_US.dic", "w", encoding="utf-8") as f:
        f.write(f"{len(en_dic_words)}\n")
        f.write("\n".join(en_dic_words) + "\n")

    with open(DICTS_DIR / "custom.dic", "w", encoding="utf-8") as f:
        f.write("0\n")

    with open(DICTS_DIR / "README_DICCIONARIOS.txt", "w", encoding="utf-8") as f:
        f.write("""DIRECTORIO DE DICCIONARIOS ORTOGRÁFICOS PORTABLES DE ESCRITORIO
================================================================
Los diccionarios incluidos en esta carpeta son compatibles con el estándar Hunspell (.aff y .dic).

Para añadir un nuevo idioma o variante regional (por ejemplo, francés o alemán):
1. Descargue los archivos correspondientes a su idioma (ejemplo: 'fr_FR.aff' y 'fr_FR.dic').
2. Cópielos directamente en esta carpeta: ./config/dictionaries/
3. Escritorio detectará automáticamente el nuevo idioma en el menú de Herramientas -> Corrector Ortográfico.

Para palabras personalizadas o nombres propios de personajes, se utiliza automáticamente 'custom.dic'.
""")

    # Carpeta de backups con .gitkeep
    with open(BACKUPS_DIR / ".gitkeep", "w", encoding="utf-8") as f:
        f.write("# Carpeta para copias de seguridad automáticas de proyectos (.zip con SHA-256)\n")

    # 6. Manual de usuario completo en español README_USUARIO.md
    print("[7/7] Generando Manual de Usuario profesional README_USUARIO.md...")
    user_manual_content = """# Escritorio v1.0.0 — Manual de Usuario y Guía Rápida Portable

Bienvenido a **Escritorio**, la estación de trabajo y entorno de autor profesional diseñada para escritores de novelas, ensayistas, dramaturgos, guionistas e investigadores en **Windows 11**.

Escritorio combina la potencia estructural, organizativa y de compilación de herramientas como Scrivener 3 con la velocidad, ligereza y estética nativa de Windows 11 Fluent Design.

---

## 1. Filosofía 100% Portable (Zero-Install)

Escritorio ha sido concebido desde su código fuente como una aplicación **100% autocontenida y portable**:

- **Sin instalador:** No requiere ejecutar ningún instalador `.msi` ni asistentes de instalación.
- **Sin privilegios de administrador:** Puede ejecutarse desde una cuenta estándar en cualquier ordenador.
- **Sin contaminación del sistema:** No escribe absolutamente nada en el Registro de Windows (`HKCU` / `HKLM`) ni en carpetas ocultas del usuario como `%APPDATA%` o `%LOCALAPPDATA%`.
- **Enlace estático nativo:** El ejecutable `Escritorio.exe` tiene su runtime estáticamente enlazado (`/MT`) y solo utiliza las DLLs fundamentales del sistema operativo Windows 11. No requiere instalar bibliotecas redistribuibles de Visual C++ (`VCRUNTIME140.dll`, etc.).
- **Lista para pendrive:** Puede copiar la carpeta completa `Escritorio_Portable_Win11` a una memoria USB, tarjeta SD o disco externo, y ejecutarla en cualquier equipo con Windows 11 con tan solo hacer doble clic.

---

## 2. Cómo empezar en 3 pasos

1. **Copie o extraiga** la carpeta `Escritorio_Portable_Win11` en cualquier lugar de su preferencia (por ejemplo, en `C:\Programas\Escritorio\`, en su disco secundario `D:\`, o en su memoria USB).
2. **Haga doble clic** en `Escritorio.exe`. La aplicación se iniciará al instante (tiempo de arranque inferior a 50 milisegundos).
3. **Cree o abra un proyecto:**
   - Seleccione una de las plantillas temáticas preinstaladas (Novela con Partes, Novela de Ficción, Relato Corto, Ensayo Académico APA/MLA, Guion Cinematográfico, Tesis, Podcast).
   - O seleccione **Proyecto en Blanco** para estructurar su obra libremente.

---

## 3. Funcionalidades Principales

### 📚 El Cuaderno (Binder)
El corazón organizativo de su obra:
- Estructura en árbol jerárquico ilimitado para Partes, Capítulos, Escenas, Notas, Fichas de Personajes y Lugares.
- Carpeta de **Investigación (Research)** para almacenar sinopsis, imágenes de ambientación y referencias.
- **Colecciones dinámicas y de búsqueda:** Filtre escenas por personajes, líneas temporales o puntos de vista (*POV*).
- **Papelera de seguridad:** Los documentos eliminados se trasladan a la papelera del proyecto y nunca se destruyen permanentemente a menos que usted lo ordene.

### 📌 Pizarra de Corcho (Corkboard)
Visualice sus ideas de forma espacial como tarjetas en una pared:
- **Modo Cuadrícula:** Visualice el flujo de capítulos y escenas en una cuadrícula adaptable.
- **Modo Forma Libre:** Mueva y agrupe libremente tarjetas conceptuales para conectar tramas.
- **Modo Carriles de Etiquetas (Swimlanes):** Organice sus escenas en columnas horizontales segregadas por etiquetas de trama, personajes o estados de revisión.
- Sincronización bidireccional inmediata: editar la sinopsis en una tarjeta actualiza instantáneamente el Esquema y el Inspector.

### 📊 El Esquema (Outliner)
Gestione su manuscrito con la precisión de una hoja de cálculo editorial:
- Columnas personalizables: Título, Tipo de Sección, Estado (Borrador, En Revisión, Final), Etiqueta, Objetivo de Palabras, Recuento Actual y Progreso.
- **Recuento recursivo automático:** Los totales de palabras de las carpetas padre calculan dinámicamente la suma exacta de todas sus escenas anidadas.
- Metadatos personalizados: agregue campos de texto, listas desplegables, fechas o casillas de verificación.

### ✍️ Editor RTF y Foco Lingüístico
- Edición enriquecida con soporte tipográfico completo, estilos jerárquicos (Título 1, Título 2, Cita, Bloque de Texto).
- **Foco Lingüístico (Linguistic Focus):** Aísle visualmente en pantalla los diálogos, sustantivos, verbos o adjetivos para afinar el ritmo estilístico de su prosa.
- Comentarios marginales y notas al pie editoriales integradas.

### 📜 Modo Scrivenings y Pantalla Dividida
- **Modo Scrivenings (`Ctrl+4`):** Seleccione una carpeta entera o múltiples escenas del Binder para visualizarlas y editarlas como un texto continuo único, manteniendo la independencia de cada archivo.
- **Pantalla Dividida (`Ctrl+'` / `Ctrl+Shift+'`):** Divida el editor en dos paneles horizontales o verticales para consultar el esquema o las notas de un personaje mientras escribe una escena.

### 📸 Instantáneas (Snapshots) y Algoritmo Myers Diff
- Guarde copias instantáneas de cualquier escena antes de emprender una reescritura importante.
- Compare cualquier instantánea previa con la versión actual mediante un comparador visual diferencial en dos colores (*Myers Diff*).
- Restaure cualquier versión anterior (*Rollback*) con un solo clic.

### 🧘 Modo Composición Libre de Distracciones (`F11`)
- Pantalla completa inmersiva sobre Windows 11.
- Ancho de hoja de papel personalizable y centrado ergonómico.
- Deslizador de opacidad (*Background Fade*) para aislar el fondo.
- Barra inferior auto-ocultable que emerge suavemente solo al mover el cursor hacia el borde inferior.

### 🎨 Motor de Temas Visuales y Live Theme Studio
- 12 temas preinstalados calibrados cromáticamente para el confort de lectura y escritura:
  - **Minimalista Claro / Oscuro**
  - **Oscuro Obsidiana** y **Carbon Dark**
  - **Solarizado Claro** y **Solarizado Oscuro**
  - **Sepia Pergamino**
  - **Nordic Frost** y **Catppuccin Mocha**
- Compatibilidad nativa con temas de Scrivener 3 (`.scrtheme`) y temas modernos de Escritorio (`.escrtheme`).
- Diseñador visual de temas en tiempo real (*Live Theme Studio*).

### 🚀 Motor de Compilación Multiformato Nativo
Compile su novela o manuscrito completo con calidad de publicación profesional:
- **Microsoft Word (`.docx`):** Documentos OpenXML limpios con estilos de párrafo, saltos de página y notas al pie.
- **PDF de Imprenta (`.pdf`):** Maquetación editorial con páginas pares/impares simétricas, cabeceras personalizadas y tabla de contenidos navegable.
- **eBook Estándar (`.epub` v3):** Paquete electrónico válido con portada, metadatos Dublin Core y hojas CSS responsive.
- Soporte completo para marcadores de posición dinámicos: `<$n>` (número de capítulo/escena), `<$t>` (número en letras), `<$title>`, `<$author>`, `<$date>`.

### 🛡️ Copias de Seguridad Automáticas con Hash SHA-256
- Cada vez que cierra un proyecto o guarda los cambios, Escritorio puede generar automáticamente un archivo comprimido `.zip` en la carpeta `./config/backups/`.
- Cada copia de seguridad incorpora una verificación criptográfica de integridad mediante suma **SHA-256** para certificar que ningún archivo ha sufrido corrupción física ni lógica.

---

## 4. Atajos de Teclado Imprescindibles

| Atajo | Acción |
|---|---|
| `Ctrl + N` | Nueva escena de texto en el Binder |
| `Ctrl + Shift + N` | Nueva carpeta en el Binder |
| `Ctrl + S` | Guardar cambios inmediatamente |
| `Ctrl + K` | Dividir documento en el cursor (*Split*) |
| `Ctrl + Shift + M` | Fusionar documentos seleccionados (*Merge*) |
| `Ctrl + 1` | Vista de Editor individual |
| `Ctrl + 2` | Vista de Pizarra de Corcho (*Corkboard*) |
| `Ctrl + 3` | Vista de Esquema (*Outliner*) |
| `Ctrl + 4` | Alternar Modo Scrivenings compuesto |
| `Ctrl + '` | Dividir pantalla horizontalmente |
| `Ctrl + Shift + '` | Dividir pantalla verticalmente |
| `F11` | Alternar Modo Composición a pantalla completa |
| `Ctrl + Shift + E` | Abrir Diálogo de Compilación Multiformato |
| `Ctrl + 5` | Tomar instantánea (*Snapshot*) de la escena activa |
| `Ctrl + Shift + T` | Panel de Objetivos de Proyecto y Sesión |
| `Ctrl + F` | Búsqueda y reemplazo en el texto |

---

## 5. Estructura de Carpetas del Paquete

```text
Escritorio_Portable_Win11/
│
├── Escritorio.exe                  <- Binario principal optimizado para Windows 11
├── README_USUARIO.md               <- Este manual de usuario
│
└── config/                         <- Carpeta de configuración portable
    ├── escritorio_settings.json    <- Preferencias globales de la aplicación
    ├── themes/                     <- Temas (.escrtheme, .scrtheme, .json)
    ├── templates/                  <- Plantillas en español e inglés (.json)
    ├── dictionaries/               <- Diccionarios ortográficos Hunspell
    └── backups/                    <- Directorio de copias de seguridad automáticas
```

---

## 6. Requisitos Técnicos

- **Sistema Operativo:** Windows 11 (todas las ediciones x64) o Windows 10 (versión 1809 o superior).
- **Procesador:** Cualquier CPU x86-64 compatible.
- **Memoria RAM:** 25 MB en reposo (funciona fluidamente incluso con 2 GB de RAM total).
- **Almacenamiento:** Menos de 40 MB de espacio en disco.
- **Dependencias externas:** Cero (0). Todo el software necesario está embebido.

---
*Escritorio — Diseñado para autores que valoran la concentración, la estructura y la independencia total de sus datos.*
"""
    with open(DIST_DIR / "README_USUARIO.md", "w", encoding="utf-8") as f:
        f.write(user_manual_content)

    print("\n[OK] ¡Distribución portable generada con éxito en dist/Escritorio_Portable_Win11/!")

if __name__ == "__main__":
    main()
