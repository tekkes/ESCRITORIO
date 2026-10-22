"""
Pestaña de Reemplazos y Notas (Replacements Tab) de la Columna 3 para Escritorio / Scrivener 3.
Sustituciones automáticas previas a la compilación (texto/regex) y
configuración global de Notas al pie y Comentarios editoriales.
"""

from typing import List, Dict, Any, Optional
from ...compile.CompileEngine.models import CompileReplacementRule, CompileFormat


class ReplacementsTab:
    """Controlador de la pestaña de Reemplazos y Notas al pie."""

    def __init__(self, current_format: CompileFormat):
        self.format: CompileFormat = current_format
        self.rules: List[CompileReplacementRule] = list(self.format.replacements)
        self.strip_comments: bool = self.format.strip_comments
        self.strip_footnotes: bool = self.format.strip_footnotes
        self.footnotes_as_endnotes: bool = self.format.footnotes_as_endnotes

    def update_format(self, new_format: CompileFormat):
        self.format = new_format
        self.rules = list(new_format.replacements)
        self.strip_comments = new_format.strip_comments
        self.strip_footnotes = new_format.strip_footnotes
        self.footnotes_as_endnotes = new_format.footnotes_as_endnotes

    def add_rule(
        self,
        pattern: str,
        replacement: str,
        is_regex: bool = False,
        case_sensitive: bool = True,
        whole_word: bool = False
    ):
        rule = CompileReplacementRule(
            pattern=pattern,
            replacement=replacement,
            is_regex=is_regex,
            case_sensitive=case_sensitive,
            whole_word=whole_word
        )
        self.rules.append(rule)
        self.format.replacements.append(rule)

    def remove_rule(self, index: int) -> bool:
        if 0 <= index < len(self.rules):
            self.rules.pop(index)
            if index < len(self.format.replacements):
                self.format.replacements.pop(index)
            return True
        return False

    def get_rules_list(self) -> List[Dict[str, Any]]:
        return [
            {
                "pattern": r.pattern,
                "replacement": r.replacement,
                "is_regex": r.is_regex,
                "case_sensitive": r.case_sensitive,
                "whole_word": r.whole_word
            }
            for r in self.rules
        ]
