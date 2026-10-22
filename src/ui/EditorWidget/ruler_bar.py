"""
RulerBar para Escritorio EditorWidget
Regla horizontal interactiva (Ctrl+Shift+R) para control de sangrías y márgenes:
- Sangría de primera línea (First Line Indent)
- Sangría izquierda (Left Margin / Indent)
- Sangría derecha (Right Margin / Indent)
- Tabulaciones (Tab Stops: izquierda, centrada, derecha, decimal)
- Soporte para unidades de medida: puntos (pt), cm, mm, pulgadas (in).
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class TabStop:
    position_pt: float
    align: str = "left"  # "left", "center", "right", "decimal"


@dataclass
class RulerState:
    is_visible: bool = True
    unit: str = "cm"  # "cm", "mm", "in", "pt"
    page_width_pt: float = 595.28  # A4 por defecto (210mm)
    left_margin_pt: float = 72.0   # 1 pulgada (2.54 cm)
    right_margin_pt: float = 72.0
    first_line_indent_pt: float = 0.0
    left_indent_pt: float = 0.0
    right_indent_pt: float = 0.0
    tab_stops: List[TabStop] = field(default_factory=list)

    # Factores de conversión respecto a puntos tipográficos (1 pt = 1/72 in)
    PT_PER_CM = 28.3465
    PT_PER_MM = 2.83465
    PT_PER_INCH = 72.0

    def pt_to_unit(self, val_pt: float) -> float:
        if self.unit == "cm":
            return round(val_pt / self.PT_PER_CM, 2)
        elif self.unit == "mm":
            return round(val_pt / self.PT_PER_MM, 1)
        elif self.unit == "in":
            return round(val_pt / self.PT_PER_INCH, 3)
        return round(val_pt, 1)

    def unit_to_pt(self, val: float) -> float:
        if self.unit == "cm":
            return val * self.PT_PER_CM
        elif self.unit == "mm":
            return val * self.PT_PER_MM
        elif self.unit == "in":
            return val * self.PT_PER_INCH
        return val


class RulerBar:
    """Controlador de la regla horizontal interactiva."""

    def __init__(self, initial_state: Optional[RulerState] = None):
        self.state = initial_state or RulerState()

    def toggle_visibility(self) -> bool:
        """Alterna la visibilidad de la regla (Ctrl+Shift+R)."""
        self.state.is_visible = not self.state.is_visible
        return self.state.is_visible

    def set_first_line_indent(self, indent_pt: float):
        self.state.first_line_indent_pt = max(-100.0, min(indent_pt, 300.0))

    def set_left_indent(self, indent_pt: float):
        self.state.left_indent_pt = max(0.0, min(indent_pt, 300.0))

    def set_right_indent(self, indent_pt: float):
        self.state.right_indent_pt = max(0.0, min(indent_pt, 300.0))

    def add_tab_stop(self, pos_pt: float, align: str = "left"):
        self.state.tab_stops.append(TabStop(position_pt=pos_pt, align=align))
        self.state.tab_stops.sort(key=lambda t: t.position_pt)

    def remove_tab_stop(self, index: int) -> bool:
        if 0 <= index < len(self.state.tab_stops):
            self.state.tab_stops.pop(index)
            return True
        return False

    def clear_tab_stops(self):
        self.state.tab_stops.clear()

    def get_render_data(self) -> Dict[str, Any]:
        """Devuelve los parámetros de renderizado de la regla para UI (GDI / Web / Qt)."""
        return {
            "visible": self.state.is_visible,
            "unit": self.state.unit,
            "page_width_pt": self.state.page_width_pt,
            "left_margin_pt": self.state.left_margin_pt,
            "right_margin_pt": self.state.right_margin_pt,
            "first_line_indent_pt": self.state.first_line_indent_pt,
            "left_indent_pt": self.state.left_indent_pt,
            "right_indent_pt": self.state.right_indent_pt,
            "first_line_indent_display": self.state.pt_to_unit(self.state.first_line_indent_pt),
            "left_indent_display": self.state.pt_to_unit(self.state.left_indent_pt),
            "right_indent_display": self.state.pt_to_unit(self.state.right_indent_pt),
            "tab_stops": [
                {"pos_pt": ts.position_pt, "pos_display": self.state.pt_to_unit(ts.position_pt), "align": ts.align}
                for ts in self.state.tab_stops
            ]
        }
