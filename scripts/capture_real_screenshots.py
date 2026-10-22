"""
Generador automatizado de capturas de pantalla reales en alta resolución de Escritorio.
Instancia la interfaz gráfica PyQt6 real con datos narrativos profesionales de muestra
y captura imágenes nítidas de cada vista, diálogo y modo de la aplicación.
"""

import os
import sys
import tempfile
from pathlib import Path

# Activar modo offscreen para renderizado desatendido sin requerir monitor físico
os.environ["QT_QPA_PLATFORM"] = "offscreen"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QTextCursor

from src.core.project import EscritorioProject, BinderItem
from src.core.importers.project_templates import ProjectTemplateManager
from src.ui.qt.main_window_qt import MainWindowQt
from src.ui.qt.composition_qt import CompositionModeQt
from src.ui.qt.dialogs_qt import NewProjectDialogQt, ProjectTargetsDialogQt, ImportAndSplitDialogQt
from src.ui.qt.compile_dialog_qt import CompileDialogQt
from src.ui.qt.inspector_qt import DiffViewerDialog


def setup_sample_project(project_dir: Path) -> EscritorioProject:
    """Crea un proyecto literario rico con partes, capítulos, escenas y metadatos reales."""
    proj = ProjectTemplateManager.create_project_from_template(
        "novel_parts",
        project_dir,
        project_name="Cronicas_del_Abismo",
        native=True
    )

    draft = proj.get_draft_folder()
    if draft and draft.children:
        part1 = draft.children[0]
        part1.title = "Parte I: El Despertar de las Cenizas"
        
        # Poblar escenas con prosa real de ficción
        sample_texts = [
            (
                "Capítulo 1: La Niebla de Oakhaven",
                "El reloj de la torre municipal dio las tres de la madrugada cuando Julián cruzó el puente de piedra. La niebla se arrastraba sobre las aguas oscuras del río como un sudario gris que se negaba a disiparse.\n\n—No deberías haber venido esta noche —susurró una voz a sus espaldas.\n\nJulián se detuvo sin girarse. Conocía demasiado bien el timbre áspero de Marcus. Durante diez años había creído que aquel hombre yacía sepultado bajo los escombros de la fortaleza de San Telmo, pero la silueta recortada bajo el farol de gas no dejaba lugar a dudas.",
                "Julián llega a Oakhaven y se encuentra inesperadamente con Marcus en el puente de piedra tras diez años de ausencia."
            ),
            (
                "Capítulo 2: El Manuscrito Olvidado",
                "La biblioteca de la abadía olía a pergamino añejo, cera de abejas y humo de turba. Sobre la mesa de roble carcomido descansaba el legajo encuadernado en piel de cabra que había costado tres vidas.\n\n—Las runas del margen no son latinas ni germánicas —apuntó la hermana Elena, acercando el candelabro de latón—. Es un dialecto prediluviano que solo los guardianes del Círculo sabían descifrar antes de la Purga de 1842.",
                "Elena y Julián analizan el misterioso códice en la abadía y descubren inscripciones en un dialecto desconocido."
            ),
            (
                "Capítulo 3: La Huida por las Catacumbas",
                "El sonido de botas claveteadas resonando en la galería superior precipitó la marcha. El aire subterráneo era denso, impregnado de salitre y humedad centenaria.\n\n—¡Por aquí! —apremió Elena señalando una arcada de sillería medio cegada por el cascajo—. Si alcanzamos la esclusa del viejo acueducto antes del amanecer, la guardia de la ciudad perderá nuestro rastro.",
                "Perseguidos por la guardia, Elena y Julián se internan en las galerías subterráneas buscando la salida fluvial."
            ),
            (
                "Capítulo 4: El Juramento en la Cripta",
                "Frente al sarcófago del primer archivero, la luz de la antorcha tembló violentamente. Las palabras del juramento parecían pesar más que las losas de granito que los rodeaban.\n\n—Lo que se sella en la oscuridad, en la oscuridad permanece —recitó Julián, sintiendo el frío del acero contra la palma de su mano.",
                "Pacto solemne de silencio y lealtad sellado en la cripta antes de separarse hacia la capital."
            )
        ]

        for i, (title, content, syn) in enumerate(sample_texts):
            if i < len(part1.children):
                scene = part1.children[i]
                scene.title = title
            else:
                scene = proj.add_item(part1.uuid, title, "Text")
            
            scene.set_content_plain(content)
            scene.set_synopsis(syn)
            scene.data.status = "Primer borrador" if i % 2 == 0 else "En revisión"
            scene.data.label = "Trama Principal" if i < 2 else "Misterio"
            scene.create_snapshot("Borrador inicial de madrugada")

    proj.save_all()
    return proj


def main():
    print("[Captura] Iniciando motor de capturas reales de Escritorio...")
    app = QApplication.instance() or QApplication(sys.argv)
    
    font = QFont("Segoe UI Variable Display", 10)
    app.setFont(font)

    temp_dir = Path(tempfile.mkdtemp(prefix="escritorio_screen_gen_"))
    proj = setup_sample_project(temp_dir)
    
    out_dir = PROJECT_ROOT / "docs" / "screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Ventana Principal: Modo Editor RTF
    win = MainWindowQt(project_path=str(proj.project_dir))
    win.resize(1400, 900)
    win.show()
    app.processEvents()

    # Seleccionar la escena 1
    draft = proj.get_draft_folder()
    if draft and draft.children and draft.children[0].children:
        target_scene = draft.children[0].children[0]
        win._select_binder_by_uuid(target_scene.uuid)
        app.processEvents()

    # Captura 1: Editor Principal con Binder e Inspector
    pix = win.grab()
    pix.save(str(out_dir / "01_interfaz_principal_editor.png"))
    print("  -> Captura 01: Interfaz Principal guardada.")

    # Captura 2: Pizarra de Corcho (Corkboard)
    win._set_central_view(1)  # Modo Corcho
    app.processEvents()
    pix = win.grab()
    pix.save(str(out_dir / "02_pizarra_corcho.png"))
    print("  -> Captura 02: Pizarra de Corcho guardada.")

    # Captura 3: Esquema Editorial (Outliner)
    win._set_central_view(2)  # Modo Outliner
    app.processEvents()
    pix = win.grab()
    pix.save(str(out_dir / "03_esquema_outliner.png"))
    print("  -> Captura 03: Esquema Editorial guardado.")

    # Captura 4: Modo Scrivenings continuo
    win._set_central_view(3)  # Modo Scrivenings
    app.processEvents()
    pix = win.grab()
    pix.save(str(out_dir / "04_modo_scrivenings.png"))
    print("  -> Captura 04: Modo Scrivenings guardado.")

    # Captura 5: Pantalla Dividida (Split Screen)
    win._set_central_view(0)  # Volver a Editor
    win._toggle_split_vertical()
    app.processEvents()
    pix = win.grab()
    pix.save(str(out_dir / "05_pantalla_dividida.png"))
    win._close_split()
    app.processEvents()
    print("  -> Captura 05: Pantalla Dividida guardada.")

    # Captura 6: Inspector con Pestaña de Snapshots / Metadatos
    win.inspector.tabs.setCurrentIndex(2)  # Metadatos
    app.processEvents()
    pix = win.inspector.grab()
    pix.save(str(out_dir / "06_inspector_detalle.png"))
    print("  -> Captura 06: Panel Inspector detallado guardado.")

    # Captura 7: Comparador Myers Diff
    orig_text = "El reloj de la torre municipal dio las tres de la madrugada cuando Julián cruzó el puente de piedra. La niebla cubría el agua."
    modified_text = "El reloj de la vieja catedral dio las tres y cuarto de la madrugada cuando Julián cruzó sigilosamente el puente de piedra. La densa niebla carmesí cubría el agua oscura del foso."
    diff_dlg = DiffViewerDialog(orig_text, modified_text, title="Comparación Myers Diff - Escena 1", parent=win)
    diff_dlg.resize(800, 500)
    diff_dlg.show()
    app.processEvents()
    pix = diff_dlg.grab()
    pix.save(str(out_dir / "07_comparador_myers_diff.png"))
    diff_dlg.close()
    print("  -> Captura 07: Comparador Myers Diff guardado.")

    # Captura 8: Modo Composición a Pantalla Completa (F11)
    if draft and draft.children and draft.children[0].children:
        scene = draft.children[0].children[0]
        comp = CompositionModeQt(scene, parent=win)
        comp.resize(1360, 850)
        comp.show()
        app.processEvents()
        pix = comp.grab()
        pix.save(str(out_dir / "08_modo_composicion_f11.png"))
        comp.close()
        print("  -> Captura 08: Modo Composición guardado.")

    # Captura 9: Diálogo de Compilación Editorial
    compile_dlg = CompileDialogQt(proj, parent=win)
    compile_dlg.resize(950, 600)
    compile_dlg.show()
    app.processEvents()
    pix = compile_dlg.grab()
    pix.save(str(out_dir / "09_dialogo_compilacion.png"))
    compile_dlg.close()
    print("  -> Captura 09: Diálogo de Compilación guardado.")

    # Captura 10: Tema Sepia Pergamino
    win._apply_theme("sepia_parchment")
    win._set_central_view(0)
    app.processEvents()
    pix = win.grab()
    pix.save(str(out_dir / "10_tema_sepia_pergamino.png"))
    print("  -> Captura 10: Tema Sepia Pergamino guardado.")

    # Captura 11: Diálogo de Nuevo Proyecto con Catálogo de Plantillas
    new_dlg = NewProjectDialogQt(parent=win)
    new_dlg.resize(850, 550)
    new_dlg.show()
    app.processEvents()
    pix = new_dlg.grab()
    pix.save(str(out_dir / "11_dialogo_nuevo_proyecto.png"))
    new_dlg.close()
    print("  -> Captura 11: Diálogo de Nuevo Proyecto guardado.")

    # Captura 12: Objetivos de Proyecto (Targets)
    targets_dlg = ProjectTargetsDialogQt(current_words=24850, target_words=80000, session_words=1420, session_target=1500, parent=win)
    targets_dlg.resize(500, 360)
    targets_dlg.show()
    app.processEvents()
    pix = targets_dlg.grab()
    pix.save(str(out_dir / "12_dialogo_objetivos_targets.png"))
    targets_dlg.close()
    print("  -> Captura 12: Diálogo de Objetivos guardado.")

    win.close()
    print("[Captura] ¡Todas las capturas reales de la herramienta han sido generadas con éxito!")


if __name__ == "__main__":
    main()
