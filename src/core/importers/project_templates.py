"""
Galería de Plantillas de Proyecto (New Project Chooser) para Escritorio.
Administra las plantillas integradas y personalizadas en 4 categorías:
1. En Blanco: Proyecto vacío sin estructura preconcebida.
2. Ficción: Novela Estándar, Novela con Partes, Relato Corto.
3. No Ficción: Ensayo General, Artículo APA, Artículo MLA, Tesis Doctoral.
4. Guion: Guion de Cine (Largometraje), Obra de Teatro, Cómic / Novela Gráfica, Podcast.

Permite además 'Guardar Proyecto como Plantilla' y 'Crear Proyecto desde Plantilla'.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from ..project import EscritorioProject, BinderItem
from ..rtf_engine import RTFEngine


class ProjectTemplateManager:
    """Gestor de catálogo de plantillas de proyecto."""

    _TEMPLATES_STORAGE_DIR: Optional[Path] = None

    @classmethod
    def get_custom_templates_dir(cls) -> Path:
        """Directorio donde se persisten las plantillas creadas por el usuario."""
        if cls._TEMPLATES_STORAGE_DIR:
            return cls._TEMPLATES_STORAGE_DIR
        base_dir = Path.home() / ".escritorio" / "templates"
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir

    @classmethod
    def set_custom_templates_dir(cls, path: Union[str, Path]):
        cls._TEMPLATES_STORAGE_DIR = Path(path).resolve()
        cls._TEMPLATES_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # CATÁLOGO DE PLANTILLAS INTEGRADAS
    # =========================================================================

    BUILTIN_TEMPLATES: Dict[str, Dict[str, Any]] = {
        # --- EN BLANCO ---
        "blank": {
            "id": "blank",
            "name": "En Blanco",
            "category": "En Blanco",
            "description": "Proyecto vacío con la estructura básica del Binder (Manuscrito, Investigación y Papelera).",
            "icon": "template_blank.png",
            "target_words": 0,
            "structure": {
                "draft": [],
                "research": [],
                "trash": []
            }
        },

        # --- FICCIÓN ---
        "novel": {
            "id": "novel",
            "name": "Novela",
            "category": "Ficción",
            "description": "Estructura estándar para novelas con capítulos, escenas, fichas de personajes y escenarios.",
            "icon": "template_novel.png",
            "target_words": 80000,
            "structure": {
                "front_matter": [
                    {"title": "Página de Título", "type": "Text", "content": "TÍTULO DE LA NOVELA\nPor Autor"},
                    {"title": "Dedicatoria", "type": "Text", "content": "Para..."}
                ],
                "draft": [
                    {
                        "title": "Capítulo 1",
                        "type": "Folder",
                        "children": [
                            {"title": "Escena 1: El comienzo", "type": "Text", "content": "Escribe aquí la primera escena..."},
                            {"title": "Escena 2", "type": "Text", "content": "Segunda escena..."}
                        ]
                    },
                    {
                        "title": "Capítulo 2",
                        "type": "Folder",
                        "children": [
                            {"title": "Escena 1", "type": "Text", "content": "Comienzo del segundo capítulo..."}
                        ]
                    }
                ],
                "characters": [
                    {"title": "Protagonista", "type": "Text", "content": "Nombre:\nEdad:\nMotivación:\nConflicto principal:\nArco de transformación:\n"},
                    {"title": "Antagonista", "type": "Text", "content": "Nombre:\nMotivación:\nFuerza antagónica:\n"}
                ],
                "places": [
                    {"title": "Escenario Principal", "type": "Text", "content": "Nombre del lugar:\nAtmósfera:\nDetalles sensoriales:\n"}
                ],
                "research": [
                    {"title": "Notas de Ambientación", "type": "Text", "content": "Investigación y trasfondo histórico/social."}
                ],
                "templates_folder": [
                    {"title": "Plantilla de Personaje", "type": "Text", "content": "Nombre:\nRol:\nAspecto físico:\nPersonalidad:\nSecretos:\n"},
                    {"title": "Plantilla de Lugar", "type": "Text", "content": "Nombre:\nUbicación:\nImportancia en la trama:\n"}
                ]
            }
        },

        "novel_parts": {
            "id": "novel_parts",
            "name": "Novela con Partes",
            "category": "Ficción",
            "description": "Estructura para obras extensas organizadas en Partes o Libros, con capítulos y escenas anidadas.",
            "icon": "template_novel_parts.png",
            "target_words": 100000,
            "structure": {
                "draft": [
                    {
                        "title": "Parte Primera: La Partida",
                        "type": "Folder",
                        "children": [
                            {
                                "title": "Capítulo 1",
                                "type": "Folder",
                                "children": [
                                    {"title": "Escena 1", "type": "Text", "content": "Inicio del viaje..."}
                                ]
                            },
                            {
                                "title": "Capítulo 2",
                                "type": "Folder",
                                "children": [
                                    {"title": "Escena 1", "type": "Text", "content": "Desarrollo..."}
                                ]
                            }
                        ]
                    },
                    {
                        "title": "Parte Segunda: El Retorno",
                        "type": "Folder",
                        "children": [
                            {
                                "title": "Capítulo 3",
                                "type": "Folder",
                                "children": [
                                    {"title": "Escena 1", "type": "Text", "content": "Clímax de la segunda parte..."}
                                ]
                            }
                        ]
                    }
                ],
                "characters": [],
                "places": [],
                "research": []
            }
        },

        "short_story": {
            "id": "short_story",
            "name": "Relato Corto",
            "category": "Ficción",
            "description": "Plantilla ligera orientada a cuentos, relatos breves y antologías.",
            "icon": "template_short_story.png",
            "target_words": 5000,
            "structure": {
                "draft": [
                    {"title": "Escena 1: Planteamiento", "type": "Text", "content": "Gancho inicial y situación."},
                    {"title": "Escena 2: Giro o Revelación", "type": "Text", "content": "Punto de giro del relato."},
                    {"title": "Escena 3: Desenlace", "type": "Text", "content": "Resolución e impacto final."}
                ],
                "research": [
                    {"title": "Idea Original", "type": "Text", "content": "Premisa y notas iniciales."}
                ]
            }
        },

        # --- NO FICCIÓN ---
        "general_essay": {
            "id": "general_essay",
            "name": "Ensayo General",
            "category": "No Ficción",
            "description": "Organización para libros de divulgación, ensayo literario o monografías temáticas.",
            "icon": "template_essay.png",
            "target_words": 30000,
            "structure": {
                "draft": [
                    {"title": "Introducción", "type": "Text", "content": "Planteamiento de la tesis y justificación temática."},
                    {
                        "title": "Bloque I: Fundamentos",
                        "type": "Folder",
                        "children": [
                            {"title": "Capítulo 1: Antecedentes", "type": "Text", "content": "Contextualización..."},
                            {"title": "Capítulo 2: Estado de la Cuestión", "type": "Text", "content": "Análisis preliminar..."}
                        ]
                    },
                    {
                        "title": "Bloque II: Análisis Crítico",
                        "type": "Folder",
                        "children": [
                            {"title": "Capítulo 3: Desarrollo de la Tesis", "type": "Text", "content": "Argumentación central..."}
                        ]
                    },
                    {"title": "Conclusiones", "type": "Text", "content": "Síntesis y reflexiones finales."},
                    {"title": "Bibliografía y Fuentes", "type": "Text", "content": "Listado de referencias citadas."}
                ],
                "research": [
                    {"title": "Citas y Notas Bibliográficas", "type": "Text", "content": "Fichas de lectura."}
                ]
            }
        },

        "apa_paper": {
            "id": "apa_paper",
            "name": "Artículo APA (7ª Edición)",
            "category": "No Ficción",
            "description": "Estructura formal para artículos científicos según normas APA (Abstract, Método, Resultados, Discusión).",
            "icon": "template_apa.png",
            "target_words": 7000,
            "structure": {
                "draft": [
                    {"title": "Página de Título y Resumen (Abstract)", "type": "Text", "content": "Título del Trabajo\nAutor\nFiliación Institucional\n\nResumen:\nPalabras clave:"},
                    {"title": "1. Introducción y Marco Teórico", "type": "Text", "content": "Problema de investigación y objetivos."},
                    {
                        "title": "2. Método",
                        "type": "Folder",
                        "children": [
                            {"title": "2.1 Participantes y Muestra", "type": "Text", "content": "Descripción de la muestra..."},
                            {"title": "2.2 Instrumentos y Materiales", "type": "Text", "content": "Herramientas de medida..."},
                            {"title": "2.3 Procedimiento", "type": "Text", "content": "Fases de la recolección de datos..."}
                        ]
                    },
                    {"title": "3. Resultados", "type": "Text", "content": "Análisis estadístico y hallazgos principales."},
                    {"title": "4. Discusión", "type": "Text", "content": "Interpretación teórica, limitaciones y futuras líneas."},
                    {"title": "5. Referencias", "type": "Text", "content": "Referencias formateadas según APA 7th."}
                ],
                "research": [
                    {"title": "Tablas y Figuras", "type": "Text", "content": "Borradores de tablas estadísticas y gráficos."}
                ]
            }
        },

        "mla_paper": {
            "id": "mla_paper",
            "name": "Artículo MLA (9ª Edición)",
            "category": "No Ficción",
            "description": "Manuscrito humanístico con encabezado MLA y sección final de Obras Citadas (Works Cited).",
            "icon": "template_mla.png",
            "target_words": 5000,
            "structure": {
                "draft": [
                    {"title": "Encabezado y Apertura", "type": "Text", "content": "Nombre del Estudiante\nProfesor\nCurso\nFecha\n\nTítulo del Ensayo\n\nPárrafo de apertura y tesis..."},
                    {"title": "Cuerpo Argumentativo", "type": "Text", "content": "Argumentos respaldados por citas textuales en formato (Apellido Página)."},
                    {"title": "Conclusión", "type": "Text", "content": "Cierre y significación de la obra analizada."},
                    {"title": "Obras Citadas (Works Cited)", "type": "Text", "content": "Fuentes primarias y secundarias ordenadas alfabéticamente."}
                ],
                "research": []
            }
        },

        "thesis": {
            "id": "thesis",
            "name": "Tesis Doctoral / Académica",
            "category": "No Ficción",
            "description": "Estructura rigurosa y completa para tesis de máster o doctorado con capítulos, anexos y metodología.",
            "icon": "template_thesis.png",
            "target_words": 90000,
            "structure": {
                "front_matter": [
                    {"title": "Portada Institucional", "type": "Text", "content": "UNIVERSIDAD...\nFACULTAD...\nTESIS DOCTORAL"},
                    {"title": "Agradecimientos", "type": "Text", "content": "Agradecimientos..."},
                    {"title": "Resumen / Abstract", "type": "Text", "content": "Resumen en castellano e inglés."}
                ],
                "draft": [
                    {"title": "Capítulo 1: Introducción y Justificación", "type": "Folder", "children": [
                        {"title": "1.1 Planteamiento del Problema", "type": "Text", "content": "..."},
                        {"title": "1.2 Preguntas de Investigación e Hipótesis", "type": "Text", "content": "..."}
                    ]},
                    {"title": "Capítulo 2: Estado del Arte", "type": "Folder", "children": [
                        {"title": "2.1 Revisión Sistemática", "type": "Text", "content": "..."}
                    ]},
                    {"title": "Capítulo 3: Metodología y Diseño Experimental", "type": "Folder", "children": [
                        {"title": "3.1 Fases del Estudio", "type": "Text", "content": "..."}
                    ]},
                    {"title": "Capítulo 4: Resultados y Discusión", "type": "Folder", "children": [
                        {"title": "4.1 Presentación de Resultados", "type": "Text", "content": "..."}
                    ]},
                    {"title": "Capítulo 5: Conclusiones y Prospectiva", "type": "Folder", "children": [
                        {"title": "5.1 Conclusiones Generales", "type": "Text", "content": "..."}
                    ]},
                    {"title": "Bibliografía", "type": "Text", "content": "Referencias bibliográficas completas."}
                ],
                "research": [
                    {"title": "Anexos e Instrumentos", "type": "Text", "content": "Cuestionarios, autorizaciones éticas y transcripciones."}
                ]
            }
        },

        # --- GUION ---
        "screenplay_feature": {
            "id": "screenplay_feature",
            "name": "Guion de Cine (Largometraje)",
            "category": "Guion",
            "description": "Estructura dramática en Tres Actos para largometrajes con escaleta de escenas y fichas de personajes.",
            "icon": "template_script_film.png",
            "target_words": 20000,
            "structure": {
                "front_matter": [
                    {"title": "Página de Título", "type": "Text", "content": "TÍTULO DEL LARGOMETRAJE\n\nescrito por\n\nNombre del Guionista\n\nBasado en..."}
                ],
                "draft": [
                    {
                        "title": "Acto I: Planteamiento",
                        "type": "Folder",
                        "children": [
                            {"title": "ESC. 1 - INT. HABITACIÓN - DÍA", "type": "Text", "content": "INT. HABITACIÓN - DÍA\n\nLuz tenue a través de las persianas. JUAN (30) mira el reloj.\n\nJUAN\n(susurrando)\nHa llegado la hora.\n"},
                            {"title": "ESC. 2 - EXT. CALLE - DÍA", "type": "Text", "content": "EXT. CALLE - DÍA\n\nTráfico intenso. Juan camina apresurado."}
                        ]
                    },
                    {
                        "title": "Acto II: Confrontación",
                        "type": "Folder",
                        "children": [
                            {"title": "ESC. 15 - Punto Medio", "type": "Text", "content": "Punto de no retorno..."}
                        ]
                    },
                    {
                        "title": "Acto III: Resolución",
                        "type": "Folder",
                        "children": [
                            {"title": "ESC. 30 - Clímax", "type": "Text", "content": "Confrontación definitiva..."}
                        ]
                    }
                ],
                "characters": [
                    {"title": "Protagonista", "type": "Text", "content": "Nombre:\nObjetivo visible:\nNecesidad interna:\nDefecto fatal:\n"},
                    {"title": "Oponente / Antagonista", "type": "Text", "content": "Nombre:\nObjetivo opuesto:\nJustificación moral:\n"}
                ],
                "research": [
                    {"title": "Escaleta de Secuencias (Step Outline)", "type": "Text", "content": "Lista de las 40 secuencias clave de la película."}
                ]
            }
        },

        "stage_play": {
            "id": "stage_play",
            "name": "Obra de Teatro",
            "category": "Guion",
            "description": "Formato teatral con Dramatis Personae, acotaciones escénicas y división en Actos.",
            "icon": "template_stage_play.png",
            "target_words": 15000,
            "structure": {
                "front_matter": [
                    {"title": "Dramatis Personae", "type": "Text", "content": "REPARTO DE PERSONAJES\n\nDON CARLOS, anciano hidalgo.\nCLARA, su hija menor.\nMARCOS, el pretendiente."}
                ],
                "draft": [
                    {
                        "title": "Acto Primero",
                        "type": "Folder",
                        "children": [
                            {"title": "Escena I", "type": "Text", "content": "(El salón principal de una casa solariega. Se escucha el viento en el exterior.)\n\nDON CARLOS\n¿Quién ronda a estas horas?"}
                        ]
                    },
                    {
                        "title": "Acto Segundo",
                        "type": "Folder",
                        "children": [
                            {"title": "Escena I", "type": "Text", "content": "Desarrollo del segundo acto..."}
                        ]
                    }
                ],
                "research": [
                    {"title": "Plano de Escenografía", "type": "Text", "content": "Disposición de puertas, muebles e iluminación."}
                ]
            }
        },

        "comic_script": {
            "id": "comic_script",
            "name": "Cómic / Novela Gráfica",
            "category": "Guion",
            "description": "Guion técnico dividido por Páginas y Viñetas para dibujantes y coloristas.",
            "icon": "template_comic.png",
            "target_words": 10000,
            "structure": {
                "draft": [
                    {
                        "title": "Página 1",
                        "type": "Folder",
                        "children": [
                            {"title": "Página 1 - Guion", "type": "Text", "content": "PÁGINA 1\n\nVIÑETA 1 (Plano general)\nVista aérea de la metrópolis bajo la lluvia ácida.\nCARTELA: Neo-Toledo, 2099.\n\nVIÑETA 2 (Primer plano)\nEl detective enciende un cigarrillo sintético.\nDETECTIVE: Otro caso sin resolver."}
                        ]
                    },
                    {
                        "title": "Página 2",
                        "type": "Folder",
                        "children": [
                            {"title": "Página 2 - Guion", "type": "Text", "content": "PÁGINA 2\n\nVIÑETA 1..."}
                        ]
                    }
                ],
                "research": [
                    {"title": "Hojas de Personaje (Model Sheets)", "type": "Text", "content": "Paleta de colores y referencias visuales."}
                ]
            }
        },

        "podcast": {
            "id": "podcast",
            "name": "Podcast / Ficción Sonora",
            "category": "Guion",
            "description": "Estructura para programas de audio y audiodramas con marcas de FX, música y voz.",
            "icon": "template_podcast.png",
            "target_words": 6000,
            "structure": {
                "draft": [
                    {
                        "title": "Episodio 1",
                        "type": "Folder",
                        "children": [
                            {"title": "Intro y Sintonía", "type": "Text", "content": "[SFX: Careta musical entra y baja a segundo plano]\n\nLOCUTOR:\nBienvenidos a 'Escritorio Sonoro'...\n\n[SFX: Fade out sintonía]"},
                            {"title": "Bloque 1: Tema Central", "type": "Text", "content": "Desarrollo del primer segmento."},
                            {"title": "Cierre y Créditos", "type": "Text", "content": "Despedida y agradecimiento a patrocinadores."}
                        ]
                    }
                ],
                "research": [
                    {"title": "Librería de Efectos de Sonido (SFX)", "type": "Text", "content": "Lista de archivos de audio necesarios y licencias."}
                ]
            }
        }
    }

    # =========================================================================
    # CONSULTAS DE LA GALERÍA
    # =========================================================================

    @classmethod
    def list_categories(cls) -> List[str]:
        """Devuelve las 4 categorías maestras de plantillas."""
        return ["En Blanco", "Ficción", "No Ficción", "Guion"]

    @classmethod
    def list_templates(cls, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista todas las plantillas disponibles, incluyendo integradas y creadas por el usuario."""
        all_templates: List[Dict[str, Any]] = list(cls.BUILTIN_TEMPLATES.values())

        # Cargar plantillas personalizadas de disco
        custom_dir = cls.get_custom_templates_dir()
        if custom_dir.exists():
            for tfile in custom_dir.glob("*.json"):
                try:
                    with open(tfile, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        data["is_custom"] = True
                        all_templates.append(data)
                except Exception:
                    pass

        if category:
            cat_lower = category.lower().strip()
            return [t for t in all_templates if t.get("category", "").lower().strip() == cat_lower]

        return all_templates

    @classmethod
    def get_template(cls, template_id: str) -> Optional[Dict[str, Any]]:
        """Recupera la definición de una plantilla por su identificador."""
        if template_id in cls.BUILTIN_TEMPLATES:
            return cls.BUILTIN_TEMPLATES[template_id]

        custom_path = cls.get_custom_templates_dir() / f"{template_id}.json"
        if custom_path.exists():
            try:
                with open(custom_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    # =========================================================================
    # CREACIÓN DE PROYECTO DESDE PLANTILLA
    # =========================================================================

    @classmethod
    def create_project_from_template(
        cls,
        template_id: str,
        destination_path: Union[str, Path],
        project_name: str,
        native: bool = True
    ) -> EscritorioProject:
        """
        Crea un nuevo proyecto (.scriv o .escr) poblado con la jerarquía y contenidos de la plantilla.
        """
        template = cls.get_template(template_id)
        if not template:
            template = cls.BUILTIN_TEMPLATES["blank"]

        dest = Path(destination_path)
        ext = ".escr" if native else ".scriv"
        if not dest.name.endswith(ext):
            project_dir = dest / f"{project_name}{ext}"
        else:
            project_dir = dest

        # Crear proyecto base con EscritorioProject.create_new_project
        project = EscritorioProject.create_new_project(project_dir, native=native)

        # Aplicar objetivos si están definidos
        if template.get("target_words", 0) > 0:
            project.project_data["targets"]["draft_words"] = template["target_words"]

        structure = template.get("structure", {})

        # 1. Front Matter (si existe, crear carpeta bajo Draft o antes de Draft)
        if "front_matter" in structure and structure["front_matter"]:
            draft = project.get_draft_folder()
            if draft:
                fm_folder = project.add_item(draft.uuid, "Páginas Preliminares (Front Matter)", item_type="Folder")
                cls._populate_children(project, fm_folder.uuid, structure["front_matter"])

        # 2. Contenido de Draft (Manuscrito)
        if "draft" in structure and structure["draft"]:
            draft = project.get_draft_folder()
            if draft:
                cls._populate_children(project, draft.uuid, structure["draft"])

        # 3. Personajes (Characters)
        if "characters" in structure and structure["characters"]:
            research = project.get_research_folder()
            target_parent = research.uuid if research else ""
            char_folder = project.add_item(target_parent, "Personajes", item_type="Folder")
            cls._populate_children(project, char_folder.uuid, structure["characters"])

        # 4. Lugares (Places)
        if "places" in structure and structure["places"]:
            research = project.get_research_folder()
            target_parent = research.uuid if research else ""
            places_folder = project.add_item(target_parent, "Lugares y Escenarios", item_type="Folder")
            cls._populate_children(project, places_folder.uuid, structure["places"])

        # 5. Investigación adicional (Research)
        if "research" in structure and structure["research"]:
            research = project.get_research_folder()
            if research:
                cls._populate_children(project, research.uuid, structure["research"])

        # 6. Carpeta de Plantillas del Proyecto (Templates Folder)
        if "templates_folder" in structure and structure["templates_folder"]:
            tmpl_folder = project.add_item("", "Hojas de Plantilla", item_type="TemplatesFolder")
            project.set_templates_folder(tmpl_folder.uuid)
            cls._populate_children(project, tmpl_folder.uuid, structure["templates_folder"])

        project.save_all()
        return project

    @classmethod
    def _populate_children(cls, project: EscritorioProject, parent_uuid: str, items: List[Dict[str, Any]]):
        """Puebla recursivamente nodos del Binder desde la especificación de plantilla."""
        for item_def in items:
            title = item_def.get("title", "Sin Título")
            item_type = item_def.get("type", "Text")
            content = item_def.get("content", "")
            children = item_def.get("children", [])

            new_node = project.add_item(parent_uuid, title, item_type=item_type)
            if content:
                new_node.write_content_rtf(RTFEngine.plain_text_to_rtf(content))

            if children:
                cls._populate_children(project, new_node.uuid, children)

    # =========================================================================
    # GUARDAR PROYECTO ACTUAL COMO PLANTILLA
    # =========================================================================

    @classmethod
    def save_project_as_template(
        cls,
        project: EscritorioProject,
        template_name: str,
        category: str = "Ficción",
        description: str = "",
        icon: str = "template_custom.png"
    ) -> Path:
        """
        Exporta la estructura actual de un proyecto como una nueva plantilla reutilizable.
        """
        template_id = "".join(c.lower() if c.isalnum() else "_" for c in template_name).strip("_")

        draft_items = []
        research_items = []

        draft_folder = project.get_draft_folder()
        if draft_folder:
            draft_items = cls._serialize_binder_item(draft_folder).get("children", [])

        research_folder = project.get_research_folder()
        if research_folder:
            research_items = cls._serialize_binder_item(research_folder).get("children", [])

        target_words = project.project_data.get("targets", {}).get("draft_words", 0)

        template_data = {
            "id": template_id,
            "name": template_name,
            "category": category,
            "description": description or f"Plantilla basada en {project.project_dir.name}",
            "icon": icon,
            "target_words": target_words,
            "structure": {
                "draft": draft_items,
                "research": research_items
            }
        }

        custom_dir = cls.get_custom_templates_dir()
        out_file = custom_dir / f"{template_id}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(template_data, f, indent=4, ensure_ascii=False)

        return out_file

    @classmethod
    def _serialize_binder_item(cls, item: BinderItem) -> Dict[str, Any]:
        """Serializa recursivamente un ítem del Binder a diccionario limpio de plantilla."""
        children_serialized = [cls._serialize_binder_item(c) for c in item.children]
        raw_rtf = item.read_content_rtf()
        plain_content = RTFEngine.rtf_to_plain_text(raw_rtf)

        return {
            "title": item.title,
            "type": item.item_type,
            "content": plain_content,
            "children": children_serialized
        }
