"""
ScriptwritingEngine para Escritorio
Motor de escritura y formateo dramático con soporte para Cine, Teatro y Cómic.
Gestiona:
- Activación con Ctrl+8
- Máquina de estados para transiciones automáticas con Tab y Enter
- Formato tipográfico Courier 12pt e indentaciones estándar
- Indicador y selector de elemento para la barra de estado
- Integración con motor de autocompletado ScriptAutocomplete
"""

from typing import Tuple, Optional, List, Dict
from .script_elements import (
    ScriptFormat,
    ScriptElementType,
    ElementStyleRule,
    SCREENPLAY_RULES
)
from .script_autocomplete import ScriptAutocomplete


class ScriptwritingEngine:
    """Motor central para el Modo Guion (Ctrl+8)."""

    def __init__(self, script_format: ScriptFormat = ScriptFormat.SCREENPLAY):
        self.is_active: bool = False
        self.format: ScriptFormat = script_format
        self.current_element: ScriptElementType = ScriptElementType.SCENE_HEADING
        self.autocomplete = ScriptAutocomplete()

    def toggle_mode(self) -> bool:
        """Alterna el modo de escritura de guiones (Ctrl+8)."""
        self.is_active = not self.is_active
        if self.is_active:
            self.current_element = ScriptElementType.SCENE_HEADING
        return self.is_active

    def set_format(self, script_format: ScriptFormat):
        self.format = script_format

    def set_element(self, element: ScriptElementType):
        self.current_element = element

    def set_element_by_shortcut(self, shortcut_num: int) -> bool:
        """Selecciona el elemento mediante su atajo numérico (Ctrl+1 .. Ctrl+7)."""
        for elem, rule in SCREENPLAY_RULES.items():
            if rule.shortcut_num == shortcut_num:
                self.current_element = elem
                return True
        return False

    def get_status_label(self) -> str:
        """Etiqueta para la barra de estado inferior."""
        if not self.is_active:
            return ""

        rule = SCREENPLAY_RULES.get(self.current_element)
        name = rule.display_name if rule else self.current_element.value
        return f"[Guion ({self.format.value.upper()}): {name.upper()}]"

    def handle_enter(self, current_line_text: str) -> Tuple[ScriptElementType, str]:
        """
        Calcula la transición del elemento dramático al pulsar Enter.
        Devuelve (nuevo_elemento, texto_formateado_de_la_linea_actual).
        """
        line_clean = current_line_text.strip()
        elem = self.current_element

        # Reglas de mayúsculas y formateo para la línea que se acaba de terminar
        rule = SCREENPLAY_RULES.get(elem)
        if rule and rule.force_uppercase:
            line_clean = line_clean.upper()

        if elem == ScriptElementType.PARENTHETICAL:
            if line_clean and not line_clean.startswith("("):
                line_clean = "(" + line_clean
            if line_clean and not line_clean.endswith(")"):
                line_clean = line_clean + ")"

        # Aprender del texto completado
        if line_clean:
            self.autocomplete.learn_from_text(line_clean)

        # Máquina de transición con Enter
        if self.format == ScriptFormat.SCREENPLAY:
            if elem == ScriptElementType.SCENE_HEADING:
                next_elem = ScriptElementType.ACTION
            elif elem == ScriptElementType.ACTION:
                next_elem = ScriptElementType.ACTION
            elif elem == ScriptElementType.CHARACTER:
                next_elem = ScriptElementType.DIALOGUE
            elif elem == ScriptElementType.PARENTHETICAL:
                next_elem = ScriptElementType.DIALOGUE
            elif elem == ScriptElementType.DIALOGUE:
                # Si el diálogo termina con Enter, vuelve a Acción
                next_elem = ScriptElementType.ACTION
            elif elem == ScriptElementType.TRANSITION:
                next_elem = ScriptElementType.SCENE_HEADING
            elif elem == ScriptElementType.SHOT:
                next_elem = ScriptElementType.ACTION
            else:
                next_elem = ScriptElementType.ACTION

        elif self.format == ScriptFormat.COMIC_SCRIPT:
            if elem == ScriptElementType.PAGE_PANEL:
                next_elem = ScriptElementType.PANEL_DESCRIPTION
            elif elem == ScriptElementType.PANEL_DESCRIPTION:
                next_elem = ScriptElementType.CAPTION
            elif elem == ScriptElementType.CAPTION:
                next_elem = ScriptElementType.CHARACTER_BALLOON
            elif elem == ScriptElementType.CHARACTER_BALLOON:
                next_elem = ScriptElementType.PANEL_DESCRIPTION
            elif elem == ScriptElementType.SFX:
                next_elem = ScriptElementType.PANEL_DESCRIPTION
            else:
                next_elem = ScriptElementType.PANEL_DESCRIPTION

        elif self.format == ScriptFormat.STAGE_PLAY:
            if elem == ScriptElementType.ACT_SCENE:
                next_elem = ScriptElementType.STAGE_DIRECTIONS
            elif elem == ScriptElementType.STAGE_DIRECTIONS:
                next_elem = ScriptElementType.CHARACTER_THEATRE
            elif elem == ScriptElementType.CHARACTER_THEATRE:
                next_elem = ScriptElementType.DIALOGUE_THEATRE
            elif elem == ScriptElementType.DIALOGUE_THEATRE:
                next_elem = ScriptElementType.STAGE_DIRECTIONS
            else:
                next_elem = ScriptElementType.STAGE_DIRECTIONS
        else:
            next_elem = ScriptElementType.ACTION

        self.current_element = next_elem
        return next_elem, line_clean

    def handle_tab(self, current_line_text: str) -> Tuple[ScriptElementType, str]:
        """
        Calcula la alternancia del elemento dramático al pulsar Tab.
        Permite saltar entre Acción -> Personaje -> Paréntesis -> Transición.
        """
        elem = self.current_element
        line_clean = current_line_text.strip()

        if self.format == ScriptFormat.SCREENPLAY:
            if elem == ScriptElementType.ACTION:
                next_elem = ScriptElementType.CHARACTER
            elif elem == ScriptElementType.CHARACTER:
                next_elem = ScriptElementType.PARENTHETICAL
            elif elem == ScriptElementType.DIALOGUE:
                next_elem = ScriptElementType.PARENTHETICAL
            elif elem == ScriptElementType.PARENTHETICAL:
                next_elem = ScriptElementType.DIALOGUE
            elif elem == ScriptElementType.SCENE_HEADING:
                next_elem = ScriptElementType.TRANSITION
            elif elem == ScriptElementType.TRANSITION:
                next_elem = ScriptElementType.SCENE_HEADING
            else:
                next_elem = ScriptElementType.CHARACTER

        elif self.format == ScriptFormat.COMIC_SCRIPT:
            if elem == ScriptElementType.PANEL_DESCRIPTION:
                next_elem = ScriptElementType.SFX
            elif elem == ScriptElementType.SFX:
                next_elem = ScriptElementType.CAPTION
            elif elem == ScriptElementType.CAPTION:
                next_elem = ScriptElementType.CHARACTER_BALLOON
            else:
                next_elem = ScriptElementType.PANEL_DESCRIPTION
        else:
            next_elem = ScriptElementType.CHARACTER

        self.current_element = next_elem
        return next_elem, line_clean

    def get_element_rule(self, element: Optional[ScriptElementType] = None) -> Optional[ElementStyleRule]:
        target = element or self.current_element
        return SCREENPLAY_RULES.get(target)

    def get_available_elements(self) -> List[Dict]:
        """Lista de elementos con atajos y nombres para el selector de la UI."""
        result = []
        for elem, rule in SCREENPLAY_RULES.items():
            result.append({
                "type": elem.value,
                "display_name": rule.display_name,
                "shortcut": f"Ctrl+{rule.shortcut_num}",
                "is_active": (elem == self.current_element)
            })
        return result
