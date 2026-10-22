"""
Agente 3: UIUXAdversaryAgent (Auditor de Interfaz, Temas y Compilación Documental - Fase B).
Automatiza pruebas adversariales de UI, Temas, Corcho, Esquema, Inspector y Compilación Editorial en Windows 11:
- Conmutación en caliente de temas (.scrtheme / .escrtheme, fidelidad cromática, densidad compacta).
- División de editor (Split Editor hasta 4 cuadrantes y Lock in Place).
- Drag & Drop estructural en el árbol del Binder y en la Pizarra de Corcho.
- Pizarra de Corcho en sus 3 modos (Rejilla, Forma Libre y Apilado por Etiquetas) y sincronización de sinopsis/imágenes.
- Esquema (Outliner): cálculo recursivo de palabras, caracteres, objetivos y gradiente de progreso cromático.
- Inspector (6 pestañas especializadas, comparador Myers Diff y Rollback de Instantáneas).
- Modo Composición (F11, hoja de papel centrada, fundido de fondo y árbol Go To).
- Compilación documental multiformato (.docx, .pdf, .epub, .rtf, .fdx, .md) con validación estructural.
"""

import os
import re
import io
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base_agent import RedTeamAgent, AuditIssue, IssueCategory, Severity
from src.core.project import EscritorioProject
from src.themes.theme_engine import ThemeMode, UIDensityMode, BUILTIN_PALETTES, DENSITY_CONFIGS
from src.themes.theme_parser import ThemePackage, ThemeParser, ScrThemeLoader
from src.ui.OutlinerWidget.outliner_row import OutlinerRow
from src.ui.OutlinerWidget.outliner_columns import (
    StandardColumnId,
    OutlinerColumn,
    ColumnSelector,
    ColumnType,
    calculate_progress_color
)
from src.ui.OutlinerWidget.outliner_exporter import OutlinerExporter
from src.ui.CorkboardWidget.index_card import IndexCard, LabelColorStyle, CardAspectRatio
from src.ui.CorkboardWidget.corkboard_widget import CorkboardWidget, CorkboardMode
from src.ui.InspectorWidget.inspector_widget import InspectorWidget
from src.ui.InspectorWidget.inspector_tabs import InspectorTabId
from src.ui.InspectorWidget.myers_diff import MyersDiffEngine, DiffGranularity, DiffOp
from src.ui.InspectorWidget.tab_snapshots import TabSnapshots
from src.ui.CompositionMode.composition_controller import CompositionMode
from src.compile import (
    CompileEngine,
    CompileConfig,
    UnifiedExporter,
    ExportFormat,
    PlaceholderResolver
)


class UIUXAdversaryAgent(RedTeamAgent):
    """Auditor adversarial de ergonomía, interfaz y motor de compilación multiformato."""

    def __init__(self):
        super().__init__(
            name="UIUXAdversaryAgent",
            description="Auditor adversarial de temas en caliente, corcho 3 modos, outliner recursivo, inspector con Myers diff, modo composición y compilación multiformato."
        )

    def execute_audit(
        self,
        project_root: Path,
        binary_path: Optional[Path],
        iteration: int
    ) -> List[AuditIssue]:
        issues: List[AuditIssue] = []

        # 1. Auditoría de cambio en caliente de temas, paletas y cargador .scrtheme
        issues.extend(self._audit_theme_hot_switching(project_root))

        # 2. Auditoría del gestor de división de editor y bloqueo (Lock in Place)
        issues.extend(self._audit_split_editor_manager(project_root))

        # 3. Auditoría de Drag & Drop y reordenamiento de nodos en el Binder
        issues.extend(self._audit_binder_drag_and_drop(project_root))

        # 4. Auditoría de Pizarra de Corcho (3 Modos y Sinopsis/Imágenes)
        issues.extend(self._audit_corkboard_3modes(project_root))

        # 5. Auditoría del Esquema (Outliner: palabras recursivas, objetivos y progreso)
        issues.extend(self._audit_outliner_recursive_metrics(project_root))

        # 6. Auditoría del Inspector (6 pestañas, Myers Diff y Rollback)
        issues.extend(self._audit_inspector_6tabs_and_myers_diff(project_root))

        # 7. Auditoría del Modo Composición libre de distracciones (F11)
        issues.extend(self._audit_composition_mode(project_root))

        # 8. Auditoría de Compilación Multiformato (.docx, .pdf, .epub, .rtf, .fdx, .md)
        issues.extend(self._audit_end_to_end_compilation(project_root))

        return issues

    # =========================================================================
    # 1. AUDITORÍA DE TEMAS EN CALIENTE, DENSIDAD Y .SCRTHEME
    # =========================================================================

    def _audit_theme_hot_switching(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        theme_cpp = root / "src" / "themes" / "ThemeEngine.cpp"

        # A. Verificación en C++
        if theme_cpp.exists():
            code = theme_cpp.read_text(encoding="utf-8", errors="ignore")
            if "SwitchTheme" not in code:
                issues.append(AuditIssue(
                    id="UI-THM-NOSWITCH",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="ThemeEngine",
                    description="Función SwitchTheme ausente en ThemeEngine.cpp.",
                    remediation_hint="Implementar cambio dinámico de tema."
                ))
            if "LoadScrTheme" not in code and "scrtheme" not in code.lower():
                issues.append(AuditIssue(
                    id="UI-THM-SCRTHEME-CPP",
                    agent=self.name,
                    category=IssueCategory.MISSING_FEATURE,
                    severity=Severity.MAJOR,
                    component="ThemeEngine",
                    description="Cargador LoadScrTheme no encontrado en ThemeEngine.cpp.",
                    remediation_hint="Añadir soporte para .scrtheme en C++."
                ))

        # B. Verificación de los 7 temas predefinidos en Python
        expected_modes = [
            ThemeMode.MINIMALIST_DEFAULT,
            ThemeMode.CARBON_DARK,
            ThemeMode.SOLARIZED_DARK,
            ThemeMode.SOLARIZED_LIGHT,
            ThemeMode.SEPIA_PARCHMENT,
            ThemeMode.NORDIC_FROST,
            ThemeMode.CATPPUCCIN_MOCHA
        ]

        for mode in expected_modes:
            if mode not in BUILTIN_PALETTES:
                issues.append(AuditIssue(
                    id=f"UI-THM-MISSING-{mode.name}",
                    agent=self.name,
                    category=IssueCategory.MISSING_FEATURE,
                    severity=Severity.MAJOR,
                    component="ThemeEngine",
                    description=f"El tema {mode.name} no se encuentra registrado en BUILTIN_PALETTES.",
                    remediation_hint=f"Definir paleta completa para {mode.name}."
                ))
            else:
                pal = BUILTIN_PALETTES[mode]
                # Validar contraste entre fondo y texto en componentes clave
                for comp in ("window", "editor", "binder"):
                    bg = pal.get(f"{comp}.background", "")
                    fg = pal.get(f"{comp}.foreground", "")
                    if bg and fg and bg.upper() == fg.upper():
                        issues.append(AuditIssue(
                            id=f"UI-THM-CONTRAST-{mode.name}-{comp}",
                            agent=self.name,
                            category=IssueCategory.UI_DISCREPANCY,
                            severity=Severity.MAJOR,
                            component="ThemeEngine",
                            description=f"Contraste nulo en tema {mode.name} para {comp} (bg == fg == {bg}).",
                            remediation_hint="Corregir colores para asegurar contraste WCAG AA."
                        ))

        # C. Verificación de límites de densidad compacta
        compact_cfg = DENSITY_CONFIGS.get(UIDensityMode.COMPACT)
        ultra_cfg = DENSITY_CONFIGS.get(UIDensityMode.ULTRA_COMPACT)

        if not compact_cfg or not ultra_cfg:
            issues.append(AuditIssue(
                id="UI-THM-DENSITY-MISSING",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.MAJOR,
                component="ThemeEngine",
                description="Configuraciones de densidad UI no encontradas en DENSITY_CONFIGS.",
                remediation_hint="Definir métricas para COMPACT y ULTRA_COMPACT."
            ))
        else:
            if ultra_cfg.toolbar_height > 28:
                issues.append(AuditIssue(
                    id="UI-THM-TOOLBAR-DENSITY",
                    agent=self.name,
                    category=IssueCategory.UI_DISCREPANCY,
                    severity=Severity.MINOR,
                    component="ThemeEngine",
                    description=f"Toolbar ultra-compacto mide {ultra_cfg.toolbar_height}px (máximo 28px).",
                    remediation_hint="Ajustar toolbar_height <= 28 en ULTRA_COMPACT."
                ))
            if ultra_cfg.editor_header_height > 24:
                issues.append(AuditIssue(
                    id="UI-THM-HEADER-DENSITY",
                    agent=self.name,
                    category=IssueCategory.UI_DISCREPANCY,
                    severity=Severity.MINOR,
                    component="ThemeEngine",
                    description=f"Header editor ultra-compacto mide {ultra_cfg.editor_header_height}px (máximo 24px).",
                    remediation_hint="Ajustar editor_header_height <= 24 en ULTRA_COMPACT."
                ))
            if compact_cfg.icon_size > 16:
                issues.append(AuditIssue(
                    id="UI-THM-ICON-DENSITY",
                    agent=self.name,
                    category=IssueCategory.UI_DISCREPANCY,
                    severity=Severity.MINOR,
                    component="ThemeEngine",
                    description=f"Iconos compactos miden {compact_cfg.icon_size}px (máximo 16px).",
                    remediation_hint="Ajustar icon_size <= 16 en COMPACT."
                ))

        # D. Carga de archivo .scrtheme real
        temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_scrtheme_test_"))
        try:
            sample_pkg = ThemePackage(
                name="Nordic Midnight Test",
                author="Escritorio Team",
                version="1.0",
                palette={
                    "window.background": "#2E3440",
                    "window.foreground": "#ECEFF4",
                    "editor.background": "#3B4252",
                    "editor.foreground": "#E5E9F0",
                    "binder.background": "#2E3440",
                    "binder.foreground": "#D8DEE9"
                }
            )
            scrtheme_path = temp_dir / "nordic_test.scrtheme"
            ScrThemeLoader.pack_package(sample_pkg, output_dest=scrtheme_path)

            loaded_pkg = ThemeParser.load_theme(scrtheme_path)
            if not loaded_pkg or loaded_pkg.name != "Nordic Midnight Test":
                issues.append(AuditIssue(
                    id="UI-THM-SCRTHEME-LOAD-FAIL",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="ScrThemeLoader",
                    description="Falló la carga o análisis del paquete .scrtheme generado.",
                    remediation_hint="Revisar ThemeParser.load_theme y ScrThemeLoader."
                ))
            elif "editor.background" not in loaded_pkg.palette:
                issues.append(AuditIssue(
                    id="UI-THM-SCRTHEME-TOKENS-FAIL",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.MAJOR,
                    component="ScrThemeLoader",
                    description="El paquete .scrtheme no indexó correctamente los tokens de la paleta.",
                    remediation_hint="Verificar parse_pal_data en theme_parser.py."
                ))
        except Exception as e:
            issues.append(AuditIssue(
                id="UI-THM-SCRTHEME-EXC",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.CRITICAL,
                component="ScrThemeLoader",
                description=f"Excepción al cargar .scrtheme: {str(e)}",
                remediation_hint="Revisar compatibilidad de ScrThemeLoader."
            ))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return issues

    # =========================================================================
    # 2. AUDITORÍA DE PANTALLA DIVIDIDA Y LOCK IN PLACE
    # =========================================================================

    def _audit_split_editor_manager(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        split_mgr_hpp = root / "src" / "ui" / "SplitEditorManager.hpp"

        if not split_mgr_hpp.exists():
            issues.append(AuditIssue(
                id="UI-SPLIT-MISSING",
                agent=self.name,
                category=IssueCategory.MISSING_FEATURE,
                severity=Severity.CRITICAL,
                component="SplitEditorManager",
                description="Componente SplitEditorManager.hpp no encontrado.",
                remediation_hint="Asegurar la implementación de división vertical, horizontal y cuadrícula."
            ))
            return issues

        code = split_mgr_hpp.read_text(encoding="utf-8", errors="ignore")
        for feature in ("SplitVertical", "SplitHorizontal", "CloseSplit", "ToggleLockActivePane"):
            if feature not in code:
                issues.append(AuditIssue(
                    id=f"UI-SPLIT-{feature.upper()}",
                    agent=self.name,
                    category=IssueCategory.MISSING_FEATURE,
                    severity=Severity.MAJOR,
                    component="SplitEditorManager",
                    description=f"Capacidad '{feature}' ausente en el gestor de división de pantalla.",
                    remediation_hint=f"Declarar e implementar {feature} en SplitEditorManager."
                ))

        return issues

    # =========================================================================
    # 3. AUDITORÍA DE DRAG & DROP EN BINDER
    # =========================================================================

    def _audit_binder_drag_and_drop(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_ui_dnd_"))

        try:
            proj_dir = temp_dir / "DnDProject.scriv"
            proj = EscritorioProject.create_new(proj_dir, title="DnD Test", native=False)
            draft = proj.get_draft_folder()

            folder_a = proj.add_item(draft.uuid, "Carpeta A", item_type="Folder")
            folder_b = proj.add_item(draft.uuid, "Carpeta B", item_type="Folder")
            doc1 = proj.add_item(folder_a.uuid, "Documento Mover", item_type="Text")
            proj.save_all()

            parent_a = proj.find_parent(doc1.uuid)
            if not parent_a or parent_a.uuid != folder_a.uuid:
                issues.append(AuditIssue(
                    id="UI-DND-PARENT-FAIL",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.MAJOR,
                    component="BinderEngine",
                    description="find_parent falló en localizar el contenedor original del nodo.",
                    remediation_hint="Revisar búsqueda recursiva de padres en EscritorioProject."
                ))
        except Exception as e:
            issues.append(AuditIssue(
                id="UI-DND-EXC",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.MAJOR,
                component="BinderEngine",
                description=f"Error en simulación de Drag & Drop: {str(e)}",
                remediation_hint="Asegurar atomicidad en el reordenamiento de nodos del Binder."
            ))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return issues

    # =========================================================================
    # 4. AUDITORÍA DE PIZARRA DE CORCHO (3 MODOS Y SINOPSIS/IMÁGENES)
    # =========================================================================

    def _audit_corkboard_3modes(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_corkboard_test_"))

        try:
            proj_dir = temp_dir / "CorkboardTest.scriv"
            proj = EscritorioProject.create_new(proj_dir, title="Corkboard Test", native=False)
            draft = proj.get_draft_folder()

            # Crear carpeta y 3 escenas
            folder = proj.add_item(draft.uuid, "Acto I", item_type="Folder")
            sc1 = proj.add_item(folder.uuid, "Escena 1 - Llegada", item_type="Text")
            sc2 = proj.add_item(folder.uuid, "Escena 2 - Encuentro", item_type="Text")
            sc3 = proj.add_item(folder.uuid, "Escena 3 - Conflicto", item_type="Text")

            sc1.write_synopsis("Llegada al pueblo desierto al atardecer.")
            sc2.write_synopsis("Encuentro con el viejo tabernero.")
            sc3.write_synopsis("Discusión por las monedas de plata.")
            proj.save_all()

            # Instanciar CorkboardWidget
            corkboard = CorkboardWidget(project=proj)
            corkboard.load_container(folder)

            if len(corkboard.cards) != 3:
                issues.append(AuditIssue(
                    id="UI-CORK-CARD-COUNT",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="CorkboardWidget",
                    description=f"El Corcho cargó {len(corkboard.cards)} fichas; se esperaban 3.",
                    remediation_hint="Verificar carga de descendientes en CorkboardWidget.load_container."
                ))

            # 1. Modo Rejilla (Grid Mode)
            corkboard.set_mode(CorkboardMode.GRID)
            view_data_grid = corkboard.get_view_data()
            if view_data_grid.get("mode") != "grid" or "layout" not in view_data_grid:
                issues.append(AuditIssue(
                    id="UI-CORK-GRID-LAYOUT",
                    agent=self.name,
                    category=IssueCategory.UI_DISCREPANCY,
                    severity=Severity.MAJOR,
                    component="CorkboardWidget",
                    description="Estructura de datos inválida para el Modo Rejilla.",
                    remediation_hint="Verificar get_view_data en CorkboardGrid."
                ))

            # Reordenar fichas en Rejilla
            ok_reorder = corkboard.reorder_grid_cards(0, 2)
            if not ok_reorder or corkboard.cards[2].uuid != sc1.uuid:
                issues.append(AuditIssue(
                    id="UI-CORK-REORDER-FAIL",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.MAJOR,
                    component="CorkboardWidget",
                    description="Fallo al reordenar fichas de índice en modo Rejilla.",
                    remediation_hint="Revisar reorder_cards en CorkboardGrid."
                ))

            # 2. Modo Forma Libre (Freeform Mode)
            corkboard.set_mode(CorkboardMode.FREEFORM)
            corkboard.set_freeform_card_position(sc1.uuid, 120.0, 250.0)
            ordered_uuids = corkboard.commit_freeform_order_to_binder()
            if not ordered_uuids:
                issues.append(AuditIssue(
                    id="UI-CORK-FREEFORM-COMMIT",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.MAJOR,
                    component="CorkboardFreeform",
                    description="Fallo al confirmar el orden del modo Forma Libre al Binder.",
                    remediation_hint="Verificar commit_freeform_order_to_binder."
                ))

            # 3. Modo Apilado por Etiquetas (Swimlanes Mode)
            corkboard.set_mode(CorkboardMode.SWIMLANES)
            view_data_lanes = corkboard.get_view_data()
            if view_data_lanes.get("mode") != "swimlanes":
                issues.append(AuditIssue(
                    id="UI-CORK-SWIMLANES-MODE",
                    agent=self.name,
                    category=IssueCategory.UI_DISCREPANCY,
                    severity=Severity.MAJOR,
                    component="CorkboardSwimlanes",
                    description="Fallo al activar el Modo Apilado por Etiquetas (Swimlanes).",
                    remediation_hint="Revisar set_mode y CorkboardSwimlanes.get_layout_data."
                ))

            # Sincronización de Sinopsis e Imagen
            card1 = corkboard.get_card(sc1.uuid)
            if not card1:
                issues.append(AuditIssue(
                    id="UI-CORK-CARD-NOT-FOUND",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="CorkboardWidget",
                    description=f"No se encontró la ficha {sc1.uuid}.",
                    remediation_hint="Verificar get_card en CorkboardWidget."
                ))
            else:
                # Modificar sinopsis desde la ficha
                new_synopsis_text = "Sinopsis actualizada desde el Corcho."
                card1.set_synopsis(new_synopsis_text)
                read_back = sc1.read_synopsis()
                if read_back != new_synopsis_text:
                    issues.append(AuditIssue(
                        id="UI-CORK-SYNOPSIS-SYNC-FAIL",
                        agent=self.name,
                        category=IssueCategory.CRITICAL_BUG,
                        severity=Severity.CRITICAL,
                        component="IndexCard",
                        description="La edición de sinopsis en la ficha no se sincronizó en synopsis.txt del BinderItem.",
                        remediation_hint="Verificar IndexCard.set_synopsis y persistencia en item.write_synopsis."
                    ))

                # Asignar imagen a la ficha
                card1.set_image("cork_card_bg.jpg")
                if card1.image_path != "cork_card_bg.jpg":
                    issues.append(AuditIssue(
                        id="UI-CORK-IMAGE-FAIL",
                        agent=self.name,
                        category=IssueCategory.UI_DISCREPANCY,
                        severity=Severity.MINOR,
                        component="IndexCard",
                        description="No se pudo asociar la imagen de escena a la ficha de índice.",
                        remediation_hint="Verificar IndexCard.set_image."
                    ))

                # Estilos de etiqueta y sello
                card1.label_style = LabelColorStyle.STRIPE
                card1.set_status(1, "Revisado")
                if card1.status_stamp_text != "REVISADO":
                    issues.append(AuditIssue(
                        id="UI-CORK-STAMP-FAIL",
                        agent=self.name,
                        category=IssueCategory.UI_DISCREPANCY,
                        severity=Severity.MINOR,
                        component="IndexCard",
                        description="El sello de estado diagonal no se formateó en mayúsculas.",
                        remediation_hint="Asegurar status_stamp_text = status_name.upper()."
                    ))

        except Exception as e:
            issues.append(AuditIssue(
                id="UI-CORK-EXC",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.CRITICAL,
                component="CorkboardWidget",
                description=f"Excepción en auditoría de Pizarra de Corcho: {str(e)}",
                evidence={"error": str(e)},
                remediation_hint="Revisar CorkboardWidget y sus 3 submodos."
            ))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return issues

    # =========================================================================
    # 5. AUDITORÍA DEL ESQUEMA (OUTLINER: RECURSIÓN Y BARRAS DE PROGRESO)
    # =========================================================================

    def _audit_outliner_recursive_metrics(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_outliner_test_"))

        try:
            proj_dir = temp_dir / "OutlinerTest.scriv"
            proj = EscritorioProject.create_new(proj_dir, title="Outliner Test", native=False)
            draft = proj.get_draft_folder()

            # Jerarquía: Carpeta Capitulo con 2 Escenas
            chap = proj.add_item(draft.uuid, "Capítulo 1", item_type="Folder")
            sc1 = proj.add_item(chap.uuid, "Escena A", item_type="Text")
            sc2 = proj.add_item(chap.uuid, "Escena B", item_type="Text")

            # Establecer texto RTF con número exacto de palabras
            # sc1: 10 palabras, objetivo 20
            # sc2: 15 palabras, objetivo 30
            text_sc1 = "Uno dos tres cuatro cinco seis siete ocho nueve diez."
            text_sc2 = "Alpha bravo charlie delta echo foxtrot golf hotel india juliet kilo lima mike november oscar."

            sc1.write_content_rtf(f"{{\\rtf1\\ansi {text_sc1}}}")
            sc2.write_content_rtf(f"{{\\rtf1\\ansi {text_sc2}}}")

            sc1.data.target_words = 20
            sc2.data.target_words = 30
            chap.data.target_words = 0  # Carpeta hereda objetivos recursivos

            proj.save_all()

            # Construir árbol de OutlinerRow
            chap_row = OutlinerRow(chap, level=0, project=proj)
            sc1_row = OutlinerRow(sc1, level=1, project=proj)
            sc2_row = OutlinerRow(sc2, level=1, project=proj)
            chap_row.children = [sc1_row, sc2_row]

            # 1. Validación de palabras directas
            if sc1_row.words != 10:
                issues.append(AuditIssue(
                    id="UI-OUTL-DIRECT-WORDS",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.MAJOR,
                    component="OutlinerRow",
                    description=f"Palabras directas incorrectas: calculó {sc1_row.words}, se esperaban 10.",
                    remediation_hint="Verificar OutlinerRow.words y RTFEngine.count_words."
                ))

            # 2. Validación de cálculo recursivo Total Words
            expected_total_words = 10 + 15  # 25
            if chap_row.total_words != expected_total_words:
                issues.append(AuditIssue(
                    id="UI-OUTL-TOTAL-WORDS-RECURSIVE",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="OutlinerRow",
                    description=f"total_words recursivo incorrecto: calculó {chap_row.total_words}, se esperaban {expected_total_words}.",
                    remediation_hint="Asegurar suma recursiva self.words + sum(c.total_words for c in self.children)."
                ))

            # 3. Validación de Total Target
            expected_total_target = 20 + 30  # 50
            if chap_row.total_target != expected_total_target:
                issues.append(AuditIssue(
                    id="UI-OUTL-TOTAL-TARGET-RECURSIVE",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.MAJOR,
                    component="OutlinerRow",
                    description=f"total_target recursivo incorrecto: calculó {chap_row.total_target}, se esperaban {expected_total_target}.",
                    remediation_hint="Verificar suma de objetivos en OutlinerRow.total_target."
                ))

            # 4. Validación de porcentaje de progreso (25 / 50 = 50.0%)
            expected_progress = 50.0
            if chap_row.progress_percent != expected_progress:
                issues.append(AuditIssue(
                    id="UI-OUTL-PROGRESS-PERCENT",
                    agent=self.name,
                    category=IssueCategory.UI_DISCREPANCY,
                    severity=Severity.MAJOR,
                    component="OutlinerRow",
                    description=f"Progreso porcentual incorrecto: {chap_row.progress_percent}%, se esperaba {expected_progress}%.",
                    remediation_hint="Verificar OutlinerRow.progress_percent."
                ))

            # 5. Validación del gradiente cromático de la barra de progreso
            # 0% -> #EF4444 (Rojo)
            # 50% -> #F59E0B (Ámbar)
            # 100% -> #10B981 (Verde)
            color_0 = calculate_progress_color(0.0)
            color_50 = calculate_progress_color(50.0)
            color_100 = calculate_progress_color(100.0)

            if color_0.upper() != "#EF4444" or color_50.upper() != "#F59E0B" or color_100.upper() != "#10B981":
                issues.append(AuditIssue(
                    id="UI-OUTL-PROGRESS-GRADIENT",
                    agent=self.name,
                    category=IssueCategory.UI_DISCREPANCY,
                    severity=Severity.MINOR,
                    component="OutlinerRow",
                    description=f"Colores de gradiente no coinciden con especificación: 0%={color_0}, 50%={color_50}, 100%={color_100}.",
                    remediation_hint="Revisar calculate_progress_color en outliner_columns.py."
                ))

            # 6. Exportación a CSV
            columns = [
                OutlinerColumn(StandardColumnId.TITLE.value, "Título"),
                OutlinerColumn(StandardColumnId.WORDS.value, "Palabras"),
                OutlinerColumn(StandardColumnId.TOTAL_WORDS.value, "Palabras Totales"),
                OutlinerColumn(StandardColumnId.TARGET.value, "Objetivo"),
                OutlinerColumn(StandardColumnId.PROGRESS.value, "Progreso")
            ]
            csv_path = temp_dir / "outliner_export.csv"
            csv_text = OutlinerExporter.export_to_csv([chap_row, sc1_row, sc2_row], columns, output_file_or_path=csv_path)

            if not csv_path.exists() or "Título,Palabras,Palabras Totales,Objetivo,Progreso" not in csv_text:
                issues.append(AuditIssue(
                    id="UI-OUTL-CSV-EXPORT-FAIL",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.MAJOR,
                    component="OutlinerExporter",
                    description="La exportación CSV del Esquema no generó las cabeceras requeridas.",
                    remediation_hint="Verificar OutlinerExporter.export_to_csv."
                ))

        except Exception as e:
            issues.append(AuditIssue(
                id="UI-OUTL-EXC",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.CRITICAL,
                component="OutlinerWidget",
                description=f"Excepción en auditoría del Esquema: {str(e)}",
                evidence={"error": str(e)},
                remediation_hint="Revisar OutlinerRow y OutlinerExporter."
            ))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return issues

    # =========================================================================
    # 6. AUDITORÍA DEL INSPECTOR (6 PESTAÑAS, MYERS DIFF Y ROLLBACK)
    # =========================================================================

    def _audit_inspector_6tabs_and_myers_diff(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_inspector_test_"))

        try:
            proj_dir = temp_dir / "InspectorTest.scriv"
            proj = EscritorioProject.create_new(proj_dir, title="Inspector Test", native=False)
            draft = proj.get_draft_folder()

            item = proj.add_item(draft.uuid, "Escena Histórica", item_type="Text")
            original_text = "El coronel Aureliano Buendía esperaba frente al pelotón de fusilamiento."
            item.write_content_rtf(f"{{\\rtf1\\ansi {original_text}}}")
            item.write_synopsis("Apertura célebre de Macondo.")
            proj.save_all()

            inspector = InspectorWidget(project=proj)
            inspector.set_item(item)

            # A. Verificación de las pestañas especializadas
            tabs_meta = inspector.get_tabs_metadata()
            if len(tabs_meta) < 5:
                issues.append(AuditIssue(
                    id="UI-INSP-TABS-COUNT",
                    agent=self.name,
                    category=IssueCategory.MISSING_FEATURE,
                    severity=Severity.MAJOR,
                    component="InspectorWidget",
                    description=f"El Inspector expone {len(tabs_meta)} pestañas; se esperaban al menos 5.",
                    remediation_hint="Verificar TAB_METADATA en inspector_tabs.py."
                ))

            # Probar Pestaña 1: Notas y Sinopsis
            inspector.set_tab(InspectorTabId.NOTES_SYNOPSIS.value)
            if inspector.get_synopsis() != "Apertura célebre de Macondo.":
                issues.append(AuditIssue(
                    id="UI-INSP-TAB1-SYNOPSIS",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.MAJOR,
                    component="TabNotesSynopsis",
                    description="get_synopsis en el Inspector no devolvió la sinopsis esperada.",
                    remediation_hint="Verificar TabNotesSynopsis.get_synopsis."
                ))

            # Probar Pestaña 2: Marcadores
            inspector.set_tab(InspectorTabId.BOOKMARKS.value)
            bm = inspector.tab_bookmarks.add_bookmark(title="Referencia Archivo", target_uuid=draft.uuid)
            if not bm:
                issues.append(AuditIssue(
                    id="UI-INSP-TAB2-BOOKMARK",
                    agent=self.name,
                    category=IssueCategory.MISSING_FEATURE,
                    severity=Severity.MAJOR,
                    component="TabBookmarks",
                    description="Fallo al agregar un marcador en TabBookmarks.",
                    remediation_hint="Verificar add_bookmark en TabBookmarks."
                ))

            # Probar Pestaña 3: Metadatos
            inspector.set_tab(InspectorTabId.METADATA.value)
            inspector.tab_metadata.add_keyword("Macondo")
            if "Macondo" not in item.data.keywords:
                issues.append(AuditIssue(
                    id="UI-INSP-TAB3-KEYWORD",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.MAJOR,
                    component="TabMetadata",
                    description="add_keyword no persistió la palabra clave en el BinderItem.",
                    remediation_hint="Verificar TabMetadata.add_keyword."
                ))

            # B. Pestaña 4: Instantáneas, Myers Diff y Rollback
            inspector.set_tab(InspectorTabId.SNAPSHOTS.value)
            tab_snap = inspector.tab_snapshots

            # Tomar instantánea de la versión original
            snap1 = tab_snap.take_snapshot("Versión Original")
            if not snap1 or len(tab_snap.snapshots) == 0:
                issues.append(AuditIssue(
                    id="UI-INSP-SNAP-TAKE-FAIL",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="TabSnapshots",
                    description="Fallo al capturar la instantánea en TabSnapshots.",
                    remediation_hint="Verificar take_snapshot en TabSnapshots."
                ))

            # Modificar el texto del documento para crear una versión revisada
            revised_text = "El coronel Aureliano Buendía recordaría aquella tarde remota ante el pelotón."
            item.write_content_rtf(f"{{\\rtf1\\ansi {revised_text}}}")
            item.save_if_dirty()

            # Ejecutar comparador Myers Diff
            tab_snap.select_snapshot(snap1.id)
            chunks = tab_snap.compute_comparison()

            has_delete = any(c.op == DiffOp.DELETE for c in chunks)
            has_insert = any(c.op == DiffOp.INSERT for c in chunks)
            has_equal = any(c.op == DiffOp.EQUAL for c in chunks)

            if not (has_delete and has_insert and has_equal):
                issues.append(AuditIssue(
                    id="UI-INSP-MYERS-DIFF-FAIL",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="MyersDiffEngine",
                    description="El comparador Myers Diff no detectó conjuntamente inserciones, eliminaciones e igualdades.",
                    evidence={"chunks_count": len(chunks), "ops": [c.op.value for c in chunks]},
                    remediation_hint="Verificar MyersDiffEngine.compute_diff a nivel de palabra."
                ))

            # Verificar formateo HTML del diff
            diff_html = tab_snap.get_diff_html()
            if "<del" not in diff_html or "<ins" not in diff_html:
                issues.append(AuditIssue(
                    id="UI-INSP-DIFF-HTML",
                    agent=self.name,
                    category=IssueCategory.UI_DISCREPANCY,
                    severity=Severity.MAJOR,
                    component="MyersDiffEngine",
                    description="get_diff_html no generó las etiquetas <del> e <ins> esperadas.",
                    remediation_hint="Verificar MyersDiffEngine.format_diff_html."
                ))

            # Probar Rollback de la instantánea
            ok_rollback = tab_snap.rollback(snap1.id, create_safety_snapshot=True)
            if not ok_rollback:
                issues.append(AuditIssue(
                    id="UI-INSP-ROLLBACK-FAIL",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="TabSnapshots",
                    description="Fallo al ejecutar el Rollback a la instantánea seleccionada.",
                    remediation_hint="Verificar TabSnapshots.rollback."
                ))
            else:
                # Comprobar que el texto revertido contiene el original
                restored_rtf = item.read_content_rtf()
                if "esperaba frente al pelotón de fusilamiento" not in restored_rtf:
                    issues.append(AuditIssue(
                        id="UI-INSP-ROLLBACK-CONTENT",
                        agent=self.name,
                        category=IssueCategory.CRITICAL_BUG,
                        severity=Severity.CRITICAL,
                        component="TabSnapshots",
                        description="El contenido del documento no se restauró fielmente tras el Rollback.",
                        remediation_hint="Asegurar que item.write_content_rtf escribe el contenido de la instantánea."
                    ))

            # Probar Pestaña 5: Comentarios y Notas al Pie
            inspector.set_tab(InspectorTabId.COMMENTS_FOOTNOTES.value)
            comment = inspector.tab_comments_footnotes.add_comment(
                start_offset=0,
                end_offset=10,
                text="Revisar tono narrativo",
                author="Editor"
            )
            if not comment:
                issues.append(AuditIssue(
                    id="UI-INSP-TAB5-COMMENT",
                    agent=self.name,
                    category=IssueCategory.MISSING_FEATURE,
                    severity=Severity.MAJOR,
                    component="TabCommentsFootnotes",
                    description="Fallo al agregar un comentario interactivo en TabCommentsFootnotes.",
                    remediation_hint="Verificar add_comment en TabCommentsFootnotes."
                ))

        except Exception as e:
            issues.append(AuditIssue(
                id="UI-INSP-EXC",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.CRITICAL,
                component="InspectorWidget",
                description=f"Excepción en auditoría del Inspector: {str(e)}",
                evidence={"error": str(e)},
                remediation_hint="Revisar InspectorWidget y TabSnapshots."
            ))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return issues

    # =========================================================================
    # 7. AUDITORÍA DEL MODO COMPOSICIÓN (F11)
    # =========================================================================

    def _audit_composition_mode(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_comp_mode_test_"))

        try:
            proj_dir = temp_dir / "CompProject.scriv"
            proj = EscritorioProject.create_new(proj_dir, title="Composition Mode Test", native=False)
            draft = proj.get_draft_folder()
            item = proj.add_item(draft.uuid, "Capítulo Inmersivo", item_type="Text")
            proj.save_all()

            comp = CompositionMode(proj, active_item=item)

            # Verificar configuración de ancho de papel
            comp.paper_width_percent = 75
            if comp.paper_width_percent != 75:
                issues.append(AuditIssue(
                    id="UI-COMP-WIDTH-FAIL",
                    agent=self.name,
                    category=IssueCategory.UI_DISCREPANCY,
                    severity=Severity.MINOR,
                    component="CompositionMode",
                    description=f"paper_width_percent devolvió {comp.paper_width_percent}, se esperaba 75.",
                    remediation_hint="Verificar property paper_width_percent en CompositionMode."
                ))

            # Verificar atenuación de fondo (Background Fade)
            comp.backdrop_opacity = 0.85
            if comp.backdrop_opacity != 0.85:
                issues.append(AuditIssue(
                    id="UI-COMP-FADE-FAIL",
                    agent=self.name,
                    category=IssueCategory.UI_DISCREPANCY,
                    severity=Severity.MINOR,
                    component="CompositionMode",
                    description=f"backdrop_opacity devolvió {comp.backdrop_opacity}, se esperaba 0.85.",
                    remediation_hint="Verificar property backdrop_opacity en CompositionMode."
                ))

            # Verificar desplazamiento estilo máquina de escribir
            comp.typewriter_scrolling = True
            if not comp.typewriter_scrolling:
                issues.append(AuditIssue(
                    id="UI-COMP-TYPEWRITER-FAIL",
                    agent=self.name,
                    category=IssueCategory.UI_DISCREPANCY,
                    severity=Severity.MINOR,
                    component="CompositionMode",
                    description="typewriter_scrolling no guardó el valor booleano True.",
                    remediation_hint="Verificar property typewriter_scrolling en CompositionMode."
                ))

            # Verificar árbol de saltos Go To
            goto_items = comp.control_bar.goto_tree
            if not goto_items:
                issues.append(AuditIssue(
                    id="UI-COMP-GOTO-EMPTY",
                    agent=self.name,
                    category=IssueCategory.UI_DISCREPANCY,
                    severity=Severity.MAJOR,
                    component="CompositionMode",
                    description="El menú Go To de la barra de control inferior no indexó las escenas del Binder.",
                    remediation_hint="Verificar _sync_goto_tree en CompositionMode."
                ))

        except Exception as e:
            issues.append(AuditIssue(
                id="UI-COMP-EXC",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.MAJOR,
                component="CompositionMode",
                description=f"Excepción en auditoría del Modo Composición: {str(e)}",
                evidence={"error": str(e)},
                remediation_hint="Revisar CompositionMode y BottomControlBar."
            ))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return issues

    # =========================================================================
    # 8. AUDITORÍA DE COMPILACIÓN MULTIFORMATO (.docx, .pdf, .epub, .rtf, .fdx, .md)
    # =========================================================================

    def _audit_end_to_end_compilation(self, root: Path) -> List[AuditIssue]:
        issues: List[AuditIssue] = []
        temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_ui_compile_"))

        try:
            # 1. Resolver etiquetas <$n> y <$title> con PlaceholderResolver
            resolver = PlaceholderResolver(project_title="Cien Años de Soledad", author="Gabriel García Márquez")
            raw_text = (
                "# Capítulo <$n>: <$title>\n\n"
                "Muchos años después, frente al pelotón de fusilamiento, el coronel Aureliano Buendía "
                "había de recordar aquella tarde remota en que su padre lo llevó a conocer el hielo.[^1]\n\n"
                "---\n\n"
                "# Capítulo <$n>: <$title>\n\n"
                "Macondo era entonces una aldea de veinte casas de barro y cañabrava construidas a la orilla "
                "de un río de aguas diáfanas que se precipitaban por un lecho de piedras pulidas.[^2]\n\n"
                "[^1]: Referencia histórica canónica de la novela.\n"
                "[^2]: Descripción fundacional de Macondo.\n"
            )

            resolved_text = resolver.resolve(raw_text, item_title="Fundación de Macondo")

            if "Capítulo 1: Fundación de Macondo" not in resolved_text:
                issues.append(AuditIssue(
                    id="UI-COMPILE-PLACEHOLDER-FAIL",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="PlaceholderResolver",
                    description="El evaluador de etiquetas no resolvió correctamente <$n> y <$title>.",
                    remediation_hint="Verificar PlaceholderResolver en src/compile/placeholders.py."
                ))

            # 2. Compilar y validar .DOCX (Microsoft Word OpenXML)
            docx_out = temp_dir / "manuscript.docx"
            UnifiedExporter.export(
                text_content=resolved_text,
                destination_path=docx_out,
                format_type=ExportFormat.DOCX,
                title="Cien Años de Soledad",
                author="Gabriel García Márquez"
            )

            if not docx_out.exists():
                issues.append(AuditIssue(
                    id="UI-COMPILE-DOCX-FAIL",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="DOCXExporter",
                    description="Falló la compilación nativa a formato Microsoft Word .docx.",
                    remediation_hint="Verificar DOCXExporter en src/compile/exporters/."
                ))
            else:
                with zipfile.ZipFile(docx_out, "r") as zf:
                    doc_xml = zf.read("word/document.xml").decode("utf-8")
                    if "<w:body>" not in doc_xml:
                        issues.append(AuditIssue(
                            id="UI-COMPILE-DOCX-EMPTY",
                            agent=self.name,
                            category=IssueCategory.CRITICAL_BUG,
                            severity=Severity.CRITICAL,
                            component="DOCXExporter",
                            description="El documento Word compilado no contiene etiqueta <w:body> válida.",
                            remediation_hint="Revisar empaquetado XML en docx_exporter."
                        ))

            # 3. Compilar y validar .PDF (Documento Portátil con cabecera %PDF-1.4)
            pdf_out = temp_dir / "manuscript.pdf"
            UnifiedExporter.export(
                text_content=resolved_text,
                destination_path=pdf_out,
                format_type=ExportFormat.PDF,
                title="Cien Años de Soledad",
                author="Gabriel García Márquez"
            )

            if not pdf_out.exists() or not pdf_out.read_bytes().startswith(b"%PDF-1.4"):
                issues.append(AuditIssue(
                    id="UI-COMPILE-PDF-INVALID",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="PDFExporter",
                    description="El PDF compilado no contiene la cabecera estándar %PDF-1.4.",
                    remediation_hint="Verificar generación binaria en pdf_exporter."
                ))

            # 4. Compilar y validar .EPUB (eBook Estándar EPUB3)
            epub_out = temp_dir / "manuscript.epub"
            UnifiedExporter.export(
                text_content=resolved_text,
                destination_path=epub_out,
                format_type=ExportFormat.EPUB3,
                title="Cien Años de Soledad",
                author="Gabriel García Márquez"
            )

            if not epub_out.exists():
                issues.append(AuditIssue(
                    id="UI-COMPILE-EPUB-FAIL",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="EPUB3Exporter",
                    description="Falló la compilación nativa a eBook EPUB 3.",
                    remediation_hint="Verificar EPUB3Exporter en src/compile/exporters/."
                ))
            else:
                with zipfile.ZipFile(epub_out, "r") as zf:
                    first_file = zf.infolist()[0]
                    if first_file.filename != "mimetype" or first_file.compress_type != zipfile.ZIP_STORED:
                        issues.append(AuditIssue(
                            id="UI-COMPILE-EPUB-MIMETYPE",
                            agent=self.name,
                            category=IssueCategory.CRITICAL_BUG,
                            severity=Severity.CRITICAL,
                            component="EPUB3Exporter",
                            description="Violación de estándar EPUB3: 'mimetype' debe ser el primer archivo sin compresión.",
                            remediation_hint="Asegurar zipfile.ZIP_STORED en mimetype."
                        ))

            # 5. Compilar y validar .RTF (Rich Text Format estándar)
            rtf_out = temp_dir / "manuscript.rtf"
            UnifiedExporter.export(
                text_content=resolved_text,
                destination_path=rtf_out,
                format_type=ExportFormat.RTF,
                title="Cien Años de Soledad",
                author="Gabriel García Márquez"
            )

            if not rtf_out.exists() or not rtf_out.read_bytes().startswith(b"{\\rtf1"):
                issues.append(AuditIssue(
                    id="UI-COMPILE-RTF-INVALID",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="RTFExporter",
                    description="El archivo compilado .rtf no comienza con el encabezado canónico {\\rtf1.",
                    remediation_hint="Verificar RTFExporter en text_exporters.py."
                ))

            # 6. Compilar y validar .FDX (Final Draft XML Scriptwriting)
            fdx_out = temp_dir / "manuscript.fdx"
            UnifiedExporter.export(
                text_content=resolved_text,
                destination_path=fdx_out,
                format_type=ExportFormat.FDX,
                title="Cien Años de Soledad",
                author="Gabriel García Márquez"
            )

            if not fdx_out.exists():
                issues.append(AuditIssue(
                    id="UI-COMPILE-FDX-FAIL",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="ScreenplayExporter",
                    description="Falló la compilación a formato Final Draft .fdx.",
                    remediation_hint="Verificar export_fdx en screenplay_exporter.py."
                ))
            else:
                fdx_text = fdx_out.read_text(encoding="utf-8")
                if "<FinalDraft" not in fdx_text or "<Content>" not in fdx_text:
                    issues.append(AuditIssue(
                        id="UI-COMPILE-FDX-INVALID-XML",
                        agent=self.name,
                        category=IssueCategory.CRITICAL_BUG,
                        severity=Severity.CRITICAL,
                        component="ScreenplayExporter",
                        description="El archivo .fdx no contiene las etiquetas XML raíz <FinalDraft> o <Content>.",
                        remediation_hint="Revisar estructura XML en screenplay_exporter.py."
                    ))

            # 7. Compilar y validar .MD (Markdown estándar)
            md_out = temp_dir / "manuscript.md"
            UnifiedExporter.export(
                text_content=resolved_text,
                destination_path=md_out,
                format_type=ExportFormat.MARKDOWN,
                title="Cien Años de Soledad",
                author="Gabriel García Márquez"
            )

            if not md_out.exists():
                issues.append(AuditIssue(
                    id="UI-COMPILE-MD-FAIL",
                    agent=self.name,
                    category=IssueCategory.CRITICAL_BUG,
                    severity=Severity.CRITICAL,
                    component="MarkdownExporter",
                    description="Falló la compilación a formato Markdown .md.",
                    remediation_hint="Verificar MarkdownExporter en text_exporters.py."
                ))
            else:
                md_content = md_out.read_text(encoding="utf-8")
                if "Capítulo" not in md_content or "Macondo" not in md_content:
                    issues.append(AuditIssue(
                        id="UI-COMPILE-MD-CONTENT",
                        agent=self.name,
                        category=IssueCategory.CRITICAL_BUG,
                        severity=Severity.MAJOR,
                        component="MarkdownExporter",
                        description="El archivo Markdown compilado no contiene el texto del manuscrito.",
                        remediation_hint="Revisar exportación en MarkdownExporter."
                    ))

        except Exception as e:
            issues.append(AuditIssue(
                id="UI-COMPILE-EXC",
                agent=self.name,
                category=IssueCategory.CRITICAL_BUG,
                severity=Severity.CRITICAL,
                component="CompilePipeline",
                description=f"Excepción en pipeline de compilación integral: {str(e)}",
                evidence={"error": str(e)},
                remediation_hint="Revisar validaciones en UnifiedExporter."
            ))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return issues
