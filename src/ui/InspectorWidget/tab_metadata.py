"""
Pestaña 3 del Inspector: Metadatos (Metadata)
- Configuración general: 'Incluir en compilación', 'Tipo de sección'
- Panel de Metadatos Personalizados (Custom Metadata) con campos Texto, Checkbox, Lista o Fecha
- Panel de Palabras Clave (Keywords) con HUD flotante para gestionar la jerarquía y colores
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from ...core.project import BinderItem, EscritorioProject


class CustomFieldType(Enum):
    TEXT = "text"
    CHECKBOX = "checkbox"
    LIST = "list"
    DATE = "date"


@dataclass
class CustomFieldDefinition:
    id: str
    name: str
    field_type: CustomFieldType = CustomFieldType.TEXT
    options: List[str] = field(default_factory=list)  # Para tipo LIST
    default_value: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "field_type": self.field_type.value,
            "options": list(self.options),
            "default_value": self.default_value
        }


@dataclass
class KeywordDefinition:
    id: str
    name: str
    color_hex: str = "#3B82F6"
    parent_id: Optional[str] = None
    children: List['KeywordDefinition'] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "color_hex": self.color_hex,
            "parent_id": self.parent_id,
            "children": [c.to_dict() for c in self.children]
        }


class ProjectKeywordsHUD:
    """Ventana flotante / gestor HUD de Palabras Clave del Proyecto."""

    def __init__(self):
        self.keywords: Dict[str, KeywordDefinition] = {}
        self.is_visible: bool = False
        self._init_defaults()

    def _init_defaults(self):
        defaults = [
            ("kw-plot", "Trama Principal", "#EA580C"),
            ("kw-clue", "Pista", "#3B82F6"),
            ("kw-tension", "Tensión", "#EF4444"),
            ("kw-lore", "Historia Pasada", "#8B5CF6"),
            ("kw-character", "Desarrollo Personaje", "#10B981")
        ]
        for kid, name, col in defaults:
            self.keywords[kid] = KeywordDefinition(id=kid, name=name, color_hex=col)

    def add_keyword(self, name: str, color_hex: str = "#3B82F6", parent_id: Optional[str] = None) -> KeywordDefinition:
        clean = name.strip()
        kid = f"kw-{clean.lower().replace(' ', '_')}"
        kw = KeywordDefinition(id=kid, name=clean, color_hex=color_hex, parent_id=parent_id)
        self.keywords[kid] = kw
        if parent_id and parent_id in self.keywords:
            self.keywords[parent_id].children.append(kw)
        return kw

    def remove_keyword(self, kid: str):
        self.keywords.pop(kid, None)

    def toggle_visibility(self) -> bool:
        self.is_visible = not self.is_visible
        return self.is_visible

    def get_all(self) -> List[KeywordDefinition]:
        return list(self.keywords.values())


class TabMetadata:
    """Controlador de la Pestaña 3: Configuración, Metadatos Personalizados y Keywords."""

    def __init__(self, project: Optional[EscritorioProject] = None):
        self.project: Optional[EscritorioProject] = project
        self.active_item: Optional[BinderItem] = None

        # Definiciones de campos de metadatos personalizados a nivel de proyecto
        self.custom_field_defs: Dict[str, CustomFieldDefinition] = {}

        # HUD de Palabras Clave del proyecto
        self.keywords_hud = ProjectKeywordsHUD()

        self._init_default_fields()

    def _init_default_fields(self):
        self.add_custom_field("POV", "Punto de Vista", CustomFieldType.TEXT)
        self.add_custom_field("Ubicacion", "Ubicación", CustomFieldType.TEXT)
        self.add_custom_field("Revisado", "Revisión Finalizada", CustomFieldType.CHECKBOX)

    def set_item(self, item: Optional[BinderItem]):
        self.active_item = item
        if not self.project and item and getattr(item, "project", None):
            self.project = item.project

    # =========================================================================
    # Configuración General (Compilar y Tipo de Sección)
    # =========================================================================

    def get_include_in_compile(self) -> bool:
        return getattr(self.active_item.data, "include_in_compile", True) if self.active_item else True

    def set_include_in_compile(self, include: bool):
        if self.active_item and hasattr(self.active_item, "data"):
            self.active_item.data.include_in_compile = bool(include)
            self.active_item.mark_dirty()

    def get_section_type(self) -> str:
        return getattr(self.active_item.data, "section_type", "Structure Based") if self.active_item else "Structure Based"

    def set_section_type(self, sec_type: str):
        if self.active_item and hasattr(self.active_item, "data"):
            self.active_item.data.section_type = sec_type
            self.active_item.mark_dirty()

    # =========================================================================
    # Panel de Metadatos Personalizados (Custom Metadata)
    # =========================================================================

    def add_custom_field(
        self,
        field_id: str,
        name: str,
        field_type: CustomFieldType = CustomFieldType.TEXT,
        options: Optional[List[str]] = None,
        default_value: str = ""
    ) -> CustomFieldDefinition:
        fdef = CustomFieldDefinition(
            id=field_id,
            name=name,
            field_type=field_type,
            options=options or [],
            default_value=default_value
        )
        self.custom_field_defs[field_id] = fdef
        return fdef

    def remove_custom_field(self, field_id: str):
        self.custom_field_defs.pop(field_id, None)

    def get_custom_value(self, field_id: str) -> str:
        if not self.active_item or not hasattr(self.active_item.data, "custom_metadata"):
            return ""
        return self.active_item.data.custom_metadata.get(field_id, "")

    def set_custom_value(self, field_id: str, value: Any):
        if self.active_item and hasattr(self.active_item, "data"):
            if not hasattr(self.active_item.data, "custom_metadata") or self.active_item.data.custom_metadata is None:
                self.active_item.data.custom_metadata = {}
            self.active_item.data.custom_metadata[field_id] = str(value)
            self.active_item.mark_dirty()

    # =========================================================================
    # Panel de Palabras Clave (Keywords)
    # =========================================================================

    def get_keywords(self) -> List[str]:
        if not self.active_item or not hasattr(self.active_item.data, "keywords"):
            return []
        return list(self.active_item.data.keywords)

    def add_keyword(self, keyword_name: str):
        if self.active_item and hasattr(self.active_item, "data"):
            clean = keyword_name.strip()
            if clean and clean not in self.active_item.data.keywords:
                self.active_item.data.keywords.append(clean)
                self.active_item.mark_dirty()

    def remove_keyword(self, keyword_name: str):
        if self.active_item and hasattr(self.active_item, "data"):
            if keyword_name in self.active_item.data.keywords:
                self.active_item.data.keywords.remove(keyword_name)
                self.active_item.mark_dirty()

    def toggle_keywords_hud(self) -> bool:
        return self.keywords_hud.toggle_visibility()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "include_in_compile": self.get_include_in_compile(),
            "section_type": self.get_section_type(),
            "custom_fields": [f.to_dict() for f in self.custom_field_defs.values()],
            "custom_values": {f_id: self.get_custom_value(f_id) for f_id in self.custom_field_defs.keys()},
            "keywords": self.get_keywords(),
            "hud_visible": self.keywords_hud.is_visible
        }
