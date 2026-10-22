"""
Columna 2: Diseños de Sección (Section Layouts Column) para Escritorio / Scrivener 3.
Visualización previa de cómo se maquetará cada Section Type del proyecto y
asignación interactiva mediante el diálogo 'Assign Section Layouts...'.
"""

from typing import Dict, List, Optional, Any
from ...compile.CompileEngine.models import CompileFormat, SectionLayout
from ...compile.CompileEngine.section_layouts import SectionLayoutEngine


class SectionLayoutsColumn:
    """Controlador de la Columna 2 del Diálogo de Compilación."""

    DEFAULT_SECTION_TYPES = [
        "Part",
        "Chapter",
        "Scene",
        "Heading",
        "Text"
    ]

    def __init__(self, current_format: CompileFormat):
        self.format: CompileFormat = current_format
        self.section_types: List[str] = list(self.DEFAULT_SECTION_TYPES)
        self.section_mappings: Dict[str, str] = {}
        self.is_assign_modal_open: bool = False
        self.selected_type_for_assignment: Optional[str] = None
        self.assign_default_mappings()

    def assign_default_mappings(self):
        """Asigna automáticamente los mejores layouts del formato activo a cada Section Type."""
        available_layouts = self.format.layouts
        if not available_layouts:
            return

        for st in self.section_types:
            st_lower = st.lower()
            matched_id = None
            for lid, lay in available_layouts.items():
                if st_lower in lid.lower() or st_lower in lay.name.lower():
                    matched_id = lid
                    break
            if not matched_id and st in ("Scene", "Text"):
                for lid in available_layouts:
                    if any(k in lid.lower() for k in ("text", "scene", "body")):
                        matched_id = lid
                        break
            if not matched_id and st in ("Chapter", "Folder", "Heading"):
                for lid in available_layouts:
                    if any(k in lid.lower() for k in ("chapter", "heading", "title")):
                        matched_id = lid
                        break
            if matched_id:
                self.section_mappings[st] = matched_id
            elif available_layouts:
                self.section_mappings[st] = next(iter(available_layouts.keys()))

    def update_format(self, new_format: CompileFormat):
        """Actualiza el formato activo y reconcilia los layouts disponibles."""
        self.format = new_format
        self.assign_default_mappings()

    def assign_layout(self, section_type: str, layout_id: str) -> bool:
        """Asigna un diseño de sección a un tipo de documento del proyecto."""
        if layout_id in self.format.layouts or any(l.id == layout_id for l in self.format.layouts.values()):
            self.section_mappings[section_type] = layout_id
            return True
        return False

    def open_assign_modal(self, section_type: Optional[str] = None):
        self.is_assign_modal_open = True
        self.selected_type_for_assignment = section_type or (self.section_types[0] if self.section_types else None)

    def close_assign_modal(self):
        self.is_assign_modal_open = False
        self.selected_type_for_assignment = None

    def get_layout_preview(self, layout: SectionLayout, sample_title: str = "Título de Ejemplo") -> str:
        """Genera una muestra visual previa de cómo se verá el diseño en página."""
        sample_body = (
            "El viento soplaba entre las copas de los robles antiguos. "
            "El silencio sólo era interrumpido por el crujir de las ramas secas bajo sus pasos."
        )
        return SectionLayoutEngine.format_with_layout(
            layout=layout,
            title=sample_title,
            body=sample_body,
            synopsis="Sinopsis descriptiva de la sección",
            notes="Notas editoriales internas",
            chapter_index=1
        )

    def get_mapping_items(self) -> List[Dict[str, Any]]:
        """Devuelve la lista estructurada de mapeos y previsualizaciones para la UI."""
        items = []
        for st in self.section_types:
            lid = self.section_mappings.get(st)
            layout = self.format.layouts.get(lid) if lid else None
            if not layout and self.format.layouts:
                layout = next(iter(self.format.layouts.values()))
                lid = layout.id

            items.append({
                "section_type": st,
                "layout_id": lid or "default",
                "layout_name": layout.name if layout else "Diseño Predeterminado",
                "title_prefix": layout.title_prefix if layout else "",
                "preview_text": self.get_layout_preview(layout, f"Sección {st}") if layout else "",
                "include_title": layout.include_title if layout else True,
                "include_body": layout.include_body if layout else True
            })
        return items

    def get_available_layouts_list(self) -> List[Dict[str, Any]]:
        """Devuelve todos los Section Layouts disponibles en el formato actual."""
        res = []
        for lid, lay in self.format.layouts.items():
            res.append({
                "id": lay.id,
                "name": lay.name,
                "description": lay.description,
                "preview_text": self.get_layout_preview(lay, "Capítulo de Prueba")
            })
        return res
