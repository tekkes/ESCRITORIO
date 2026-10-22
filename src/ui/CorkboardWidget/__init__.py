"""
Paquete CorkboardWidget de Escritorio.
"""

from .index_card import IndexCard, CardAspectRatio, LabelColorStyle
from .corkboard_grid import CorkboardGrid
from .corkboard_freeform import CorkboardFreeform
from .corkboard_swimlanes import CorkboardSwimlanes, SwimlaneColumn
from .corkboard_footer import CorkboardFooterBar
from .corkboard_widget import CorkboardWidget, CorkboardMode

CorkboardSubmode = CorkboardMode

__all__ = [
    "IndexCard",
    "CardAspectRatio",
    "LabelColorStyle",
    "CorkboardGrid",
    "CorkboardFreeform",
    "CorkboardSwimlanes",
    "SwimlaneColumn",
    "CorkboardFooterBar",
    "CorkboardWidget",
    "CorkboardMode",
    "CorkboardSubmode"
]
