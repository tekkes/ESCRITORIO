"""
Compile Format Designer para Escritorio / Scrivener 3.
Controlador de edición profunda de Formatos de Compilación:
- Duplicación de formatos predefinidos a nivel de proyecto o global.
- Ajuste de página (tamaño, márgenes, orientación) y tipografía base.
- Editor de Diseños de Sección (Section Layouts) y Separadores.
- Transformaciones de texto y reglas de reemplazo automáticas.
- Serialización y exportación de formatos a formato JSON (.scrivformat / .escrformat).
"""

import copy
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from .models import (
    CompileFormat, SectionLayout, PageSize, PageOrientation, PageMargins,
    CompileReplacementRule, create_builtin_formats
)
from .separators import SectionSeparators, SeparatorType


class CompileFormatDesigner:
    """Diseñador y gestor de formatos de compilación personalizados."""

    def __init__(self, format_to_edit: Optional[CompileFormat] = None):
        if format_to_edit:
            self.current_format: CompileFormat = copy.deepcopy(format_to_edit)
        else:
            builtins = create_builtin_formats()
            self.current_format = copy.deepcopy(builtins["manuscript_standard"])
            self.current_format.id = "custom_format"
            self.current_format.name = "Nuevo Formato Personalizado"
            self.current_format.is_builtin = False
            self.current_format.is_project_format = True

    @classmethod
    def duplicate_format(cls, source_format: CompileFormat, new_name: Optional[str] = None, is_project: bool = True) -> 'CompileFormatDesigner':
        """Duplica un formato existente para permitir su edición sin alterar el predefinido."""
        new_fmt = copy.deepcopy(source_format)
        new_fmt.id = f"{source_format.id}_copy_{int(copy.copy(id(source_format)))}"
        new_fmt.name = new_name or f"{source_format.name} (Copia)"
        new_fmt.is_builtin = False
        new_fmt.is_project_format = is_project
        return cls(new_fmt)

    # =========================================================================
    # Edición de Propiedades Generales y Tipografía
    # =========================================================================

    def set_general_info(self, name: str, description: str, target_format: str):
        self.current_format.name = name.strip()
        self.current_format.description = description.strip()
        self.current_format.target_format = target_format.lower().strip()

    def set_page_settings(
        self,
        page_size: PageSize = PageSize.LETTER,
        orientation: PageOrientation = PageOrientation.PORTRAIT,
        margins: Optional[PageMargins] = None
    ):
        self.current_format.page_size = page_size
        self.current_format.orientation = orientation
        if margins:
            self.current_format.margins = margins

    def set_typography(
        self,
        font_family: str,
        font_size_pt: int,
        line_spacing: float,
        first_line_indent_pt: float
    ):
        self.current_format.font_family = font_family
        self.current_format.font_size_pt = max(6, min(72, font_size_pt))
        self.current_format.line_spacing = max(0.5, min(4.0, line_spacing))
        self.current_format.first_line_indent_pt = max(0.0, first_line_indent_pt)

    # =========================================================================
    # Edición de Diseños de Sección (Section Layouts)
    # =========================================================================

    def add_or_update_layout(self, layout: SectionLayout):
        """Añade o actualiza un diseño de sección dentro del formato."""
        self.current_format.layouts[layout.id] = copy.deepcopy(layout)

    def remove_layout(self, layout_id: str) -> bool:
        if layout_id in self.current_format.layouts:
            del self.current_format.layouts[layout_id]
            return True
        return False

    def get_layout(self, layout_id: str) -> Optional[SectionLayout]:
        return self.current_format.layouts.get(layout_id)

    # =========================================================================
    # Transformaciones de Texto y Reemplazos
    # =========================================================================

    def set_transformations(
        self,
        smart_quotes: bool = True,
        em_dashes: bool = True,
        ellipses: bool = True,
        strip_comments: bool = True,
        strip_footnotes: bool = False,
        footnotes_as_endnotes: bool = False
    ):
        self.current_format.smart_quotes = smart_quotes
        self.current_format.em_dashes = em_dashes
        self.current_format.ellipses = ellipses
        self.current_format.strip_comments = strip_comments
        self.current_format.strip_footnotes = strip_footnotes
        self.current_format.footnotes_as_endnotes = footnotes_as_endnotes

    def add_replacement_rule(
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
        self.current_format.replacements.append(rule)

    def remove_replacement_rule(self, index: int) -> bool:
        if 0 <= index < len(self.current_format.replacements):
            self.current_format.replacements.pop(index)
            return True
        return False

    # =========================================================================
    # Serialización y Persistencia
    # =========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el formato actual a un diccionario serializable."""
        fmt = self.current_format
        return {
            "id": fmt.id,
            "name": fmt.name,
            "description": fmt.description,
            "is_builtin": fmt.is_builtin,
            "is_project_format": fmt.is_project_format,
            "target_format": fmt.target_format,
            "page_size": fmt.page_size.value,
            "orientation": fmt.orientation.value,
            "margins": {
                "top": fmt.margins.top_in,
                "bottom": fmt.margins.bottom_in,
                "left": fmt.margins.left_in,
                "right": fmt.margins.right_in
            },
            "font_family": fmt.font_family,
            "font_size_pt": fmt.font_size_pt,
            "line_spacing": fmt.line_spacing,
            "first_line_indent_pt": fmt.first_line_indent_pt,
            "smart_quotes": fmt.smart_quotes,
            "em_dashes": fmt.em_dashes,
            "ellipses": fmt.ellipses,
            "strip_comments": fmt.strip_comments,
            "strip_footnotes": fmt.strip_footnotes,
            "footnotes_as_endnotes": fmt.footnotes_as_endnotes,
            "layouts": {
                k: {
                    "id": lay.id,
                    "name": lay.name,
                    "description": lay.description,
                    "title_prefix": lay.title_prefix,
                    "title_suffix": lay.title_suffix,
                    "include_title": lay.include_title,
                    "include_body": lay.include_body,
                    "include_synopsis": lay.include_synopsis,
                    "include_notes": lay.include_notes,
                    "title_uppercase": lay.title_uppercase,
                    "title_centered": lay.title_centered,
                    "separators": {
                        "before": lay.separators.before_section.value,
                        "custom_before": lay.separators.custom_before,
                        "between": lay.separators.between_sections.value,
                        "custom_between": lay.separators.custom_between,
                        "after": lay.separators.after_section.value,
                        "custom_after": lay.separators.custom_after
                    }
                }
                for k, lay in fmt.layouts.items()
            },
            "replacements": [
                {
                    "pattern": r.pattern,
                    "replacement": r.replacement,
                    "is_regex": r.is_regex,
                    "case_sensitive": r.case_sensitive,
                    "whole_word": r.whole_word
                }
                for r in fmt.replacements
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompileFormatDesigner':
        """Reconstruye un formato a partir de un diccionario."""
        margins = PageMargins(
            top_in=data.get("margins", {}).get("top", 1.0),
            bottom_in=data.get("margins", {}).get("bottom", 1.0),
            left_in=data.get("margins", {}).get("left", 1.0),
            right_in=data.get("margins", {}).get("right", 1.0)
        )

        layouts = {}
        for lid, ldata in data.get("layouts", {}).items():
            sep_data = ldata.get("separators", {})
            seps = SectionSeparators(
                before_section=SeparatorType(sep_data.get("before", "empty_line")),
                custom_before=sep_data.get("custom_before", ""),
                between_sections=SeparatorType(sep_data.get("between", "custom_symbol")),
                custom_between=sep_data.get("custom_between", "* * *"),
                after_section=SeparatorType(sep_data.get("after", "single_return")),
                custom_after=sep_data.get("custom_after", "")
            )
            layouts[lid] = SectionLayout(
                id=ldata.get("id", lid),
                name=ldata.get("name", lid),
                description=ldata.get("description", ""),
                title_prefix=ldata.get("title_prefix", ""),
                title_suffix=ldata.get("title_suffix", "\n\n"),
                include_title=ldata.get("include_title", True),
                include_body=ldata.get("include_body", True),
                include_synopsis=ldata.get("include_synopsis", False),
                include_notes=ldata.get("include_notes", False),
                title_uppercase=ldata.get("title_uppercase", False),
                title_centered=ldata.get("title_centered", False),
                separators=seps
            )

        replacements = [
            CompileReplacementRule(
                pattern=r["pattern"],
                replacement=r["replacement"],
                is_regex=r.get("is_regex", False),
                case_sensitive=r.get("case_sensitive", True),
                whole_word=r.get("whole_word", False)
            )
            for r in data.get("replacements", [])
        ]

        fmt = CompileFormat(
            id=data.get("id", "custom"),
            name=data.get("name", "Formato Personalizado"),
            description=data.get("description", ""),
            is_builtin=data.get("is_builtin", False),
            is_project_format=data.get("is_project_format", True),
            target_format=data.get("target_format", "docx"),
            page_size=PageSize(data.get("page_size", "letter")),
            orientation=PageOrientation(data.get("orientation", "portrait")),
            margins=margins,
            font_family=data.get("font_family", "Times New Roman"),
            font_size_pt=data.get("font_size_pt", 12),
            line_spacing=data.get("line_spacing", 2.0),
            first_line_indent_pt=data.get("first_line_indent_pt", 24.0),
            layouts=layouts,
            smart_quotes=data.get("smart_quotes", True),
            em_dashes=data.get("em_dashes", True),
            ellipses=data.get("ellipses", True),
            strip_comments=data.get("strip_comments", True),
            strip_footnotes=data.get("strip_footnotes", False),
            footnotes_as_endnotes=data.get("footnotes_as_endnotes", False),
            replacements=replacements
        )
        return cls(fmt)

    def save_to_file(self, file_path: Union[str, Path]):
        """Guarda el formato en disco en formato JSON (.escrformat)."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> 'CompileFormatDesigner':
        """Carga un formato desde archivo JSON."""
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
