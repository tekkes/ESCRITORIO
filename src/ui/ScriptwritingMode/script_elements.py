"""
Script Elements para Escritorio
Definiciones de formatos y elementos dramáticos para el Modo Escritura de Guiones:
- Guion Cinematográfico (Screenplay)
- Guion Teatral (Stage Play)
- Guion de Cómic / Historieta (Comic Script)
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional


class ScriptFormat(Enum):
    SCREENPLAY = "screenplay"
    STAGE_PLAY = "stage_play"
    COMIC_SCRIPT = "comic_script"


class ScriptElementType(Enum):
    # Guion de Cine (Screenplay)
    SCENE_HEADING = "scene_heading"  # INT./EXT. CASA - DÍA
    ACTION = "action"                # Descripción de acciones y atmósfera
    CHARACTER = "character"          # Nombre del personaje en mayúsculas
    PARENTHETICAL = "parenthetical"  # (acotación o actitud)
    DIALOGUE = "dialogue"            # Texto hablado por el personaje
    TRANSITION = "transition"        # CORTE A:, FUNDIDO A NEGRO:
    SHOT = "shot"                    # PLANO DETALLE, ÁNGULO GENERAL

    # Guion Teatral (Stage Play)
    ACT_SCENE = "act_scene"
    STAGE_DIRECTIONS = "stage_directions"
    CHARACTER_THEATRE = "character_theatre"
    DIALOGUE_THEATRE = "dialogue_theatre"

    # Guion de Cómic (Comic Script)
    PAGE_PANEL = "page_panel"        # PÁGINA 1 - VIÑETA 1
    PANEL_DESCRIPTION = "panel_desc" # Descripción visual del encuadre
    CAPTION = "caption"              # Cartela / Narrador en off
    CHARACTER_BALLOON = "balloon"    # Globo de diálogo
    SFX = "sfx"                      # Efectos de sonido (¡BANG!, ¡CRASH!)


@dataclass
class ElementStyleRule:
    element: ScriptElementType
    display_name: str
    left_indent_pt: float
    right_indent_pt: float
    space_before_pt: float
    space_after_pt: float
    force_uppercase: bool
    shortcut_num: int  # 1 a 7 para Ctrl+1 .. Ctrl+7 en modo guion


SCREENPLAY_RULES: Dict[ScriptElementType, ElementStyleRule] = {
    ScriptElementType.SCENE_HEADING: ElementStyleRule(
        element=ScriptElementType.SCENE_HEADING,
        display_name="Encabezado de Escena",
        left_indent_pt=108.0,   # 1.5 pulgadas
        right_indent_pt=72.0,
        space_before_pt=18.0,
        space_after_pt=6.0,
        force_uppercase=True,
        shortcut_num=1
    ),
    ScriptElementType.ACTION: ElementStyleRule(
        element=ScriptElementType.ACTION,
        display_name="Acción",
        left_indent_pt=108.0,
        right_indent_pt=72.0,
        space_before_pt=6.0,
        space_after_pt=6.0,
        force_uppercase=False,
        shortcut_num=2
    ),
    ScriptElementType.CHARACTER: ElementStyleRule(
        element=ScriptElementType.CHARACTER,
        display_name="Personaje",
        left_indent_pt=252.0,   # 3.5 pulgadas
        right_indent_pt=72.0,
        space_before_pt=12.0,
        space_after_pt=0.0,
        force_uppercase=True,
        shortcut_num=3
    ),
    ScriptElementType.PARENTHETICAL: ElementStyleRule(
        element=ScriptElementType.PARENTHETICAL,
        display_name="Paréntesis (Acotación)",
        left_indent_pt=216.0,   # 3.0 pulgadas
        right_indent_pt=180.0,  # 2.5 pulgadas
        space_before_pt=0.0,
        space_after_pt=0.0,
        force_uppercase=False,
        shortcut_num=4
    ),
    ScriptElementType.DIALOGUE: ElementStyleRule(
        element=ScriptElementType.DIALOGUE,
        display_name="Diálogo",
        left_indent_pt=180.0,   # 2.5 pulgadas
        right_indent_pt=180.0,
        space_before_pt=0.0,
        space_after_pt=6.0,
        force_uppercase=False,
        shortcut_num=5
    ),
    ScriptElementType.TRANSITION: ElementStyleRule(
        element=ScriptElementType.TRANSITION,
        display_name="Transición",
        left_indent_pt=396.0,   # 5.5 pulgadas (alineado a la derecha)
        right_indent_pt=72.0,
        space_before_pt=12.0,
        space_after_pt=12.0,
        force_uppercase=True,
        shortcut_num=6
    ),
    ScriptElementType.SHOT: ElementStyleRule(
        element=ScriptElementType.SHOT,
        display_name="Plano / Toma",
        left_indent_pt=108.0,
        right_indent_pt=72.0,
        space_before_pt=12.0,
        space_after_pt=6.0,
        force_uppercase=True,
        shortcut_num=7
    )
}
