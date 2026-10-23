"""
ESCRITORIO v2.0 - XML Engine (.escrx / .scrivx)
Serializador y parser XML de máxima fidelidad y compatibilidad con Scrivener 3.
"""

import time
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Optional, List
from .project_v2 import EscritorioProjectV2, BinderNode, CollectionItem
from .atomic_storage import AtomicStorage


class XmlEngineV2:
    """Motor de serialización e importación XML para proyectos .escr y .scriv."""

    @staticmethod
    def save_project_xml(project: EscritorioProjectV2, target_file: Path) -> bool:
        """Genera el documento XML maestro del proyecto."""
        root = ET.Element("ScrivenerProject", {
            "Version": "2.0",
            "Creator": "Escritorio v2.0",
            "SyncDate": str(int(project.path.stat().st_mtime if project.path.exists() else 0))
        })

        # Metadatos globales y configuraciones
        meta_elem = ET.SubElement(root, "ProjectSettings")
        targets_elem = ET.SubElement(meta_elem, "ProjectTargets")
        ET.SubElement(targets_elem, "DraftTarget").text = str(project.project_target_words)
        ET.SubElement(targets_elem, "SessionTarget").text = str(project.session_target_words)
        ET.SubElement(targets_elem, "DailyHoursTarget").text = str(getattr(project, "daily_hours_target", 2.0))
        if project.target_deadline:
            ET.SubElement(targets_elem, "Deadline").text = project.target_deadline
        if hasattr(project, "target_work_days"):
            ET.SubElement(targets_elem, "WorkDays").text = ",".join(map(str, project.target_work_days))

        # Etiquetas
        labels_elem = ET.SubElement(meta_elem, "LabelSettings")
        for lbl in project.labels:
            ET.SubElement(labels_elem, "Label", {"ID": lbl["id"], "Color": lbl["color"]}).text = lbl["name"]

        # Estados
        status_elem = ET.SubElement(meta_elem, "StatusSettings")
        for st in project.statuses:
            ET.SubElement(status_elem, "Status", {"ID": st["id"]}).text = st["name"]

        # Palabras clave globales
        kw_elem = ET.SubElement(meta_elem, "ProjectKeywords")
        for kw in project.project_keywords:
            ET.SubElement(kw_elem, "Keyword", {"Color": kw.get("color", "#4a90e2")}).text = kw["name"]

        # Colecciones
        colls_elem = ET.SubElement(root, "Collections")
        for col in project.collections:
            c_elem = ET.SubElement(colls_elem, "Collection", {
                "ID": col.id,
                "Name": col.name,
                "Color": col.color,
                "IsSearch": "Yes" if col.is_search else "No"
            })
            if col.is_search:
                ET.SubElement(c_elem, "Query").text = col.search_query
                ET.SubElement(c_elem, "Scope").text = col.search_scope
            else:
                members_elem = ET.SubElement(c_elem, "Members")
                for m_uuid in col.member_uuids:
                    ET.SubElement(members_elem, "Member").text = m_uuid

        # Árbol del Binder
        binder_elem = ET.SubElement(root, "Binder")
        for node in project.root_nodes:
            XmlEngineV2._serialize_binder_node(binder_elem, node)

        # Formatear XML bonito con indentación
        raw_xml = ET.tostring(root, encoding="utf-8")
        parsed = minidom.parseString(raw_xml)
        pretty_xml = parsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

        return AtomicStorage.write_atomic_text(target_file, pretty_xml)

    @staticmethod
    def _serialize_binder_node(parent_elem: ET.Element, node: BinderNode):
        item_elem = ET.SubElement(parent_elem, "BinderItem", {
            "ID": node.uuid,
            "Type": node.type,
            "Created": str(node.created),
            "Modified": str(node.modified)
        })

        ET.SubElement(item_elem, "Title").text = node.title
        if node.icon:
            ET.SubElement(item_elem, "Icon").text = node.icon

        # Metadatos del nodo
        meta = ET.SubElement(item_elem, "MetaData")
        ET.SubElement(meta, "IncludeInCompile").text = "Yes" if node.include_in_compile else "No"
        ET.SubElement(meta, "SectionType").text = node.section_type
        ET.SubElement(meta, "Label").text = node.label
        ET.SubElement(meta, "Status").text = node.status
        ET.SubElement(meta, "TargetWords").text = str(node.target_words)

        if node.keywords:
            kws = ET.SubElement(meta, "Keywords")
            for kw in node.keywords:
                ET.SubElement(kws, "Keyword").text = kw

        # Nodos hijos
        if node.children:
            children_elem = ET.SubElement(item_elem, "Children")
            for child in node.children:
                XmlEngineV2._serialize_binder_node(children_elem, child)

    @staticmethod
    def load_project_xml(project: EscritorioProjectV2, source_file: Path) -> bool:
        """Carga y reconstruye la jerarquía completa a partir de un archivo .escrx o .scrivx."""
        if not source_file.exists():
            return False

        try:
            tree = ET.parse(source_file)
            root = tree.getroot()

            # Cargar configuraciones de proyecto
            settings = root.find("ProjectSettings")
            if settings is not None:
                targets = settings.find("ProjectTargets")
                if targets is not None:
                    d_elem = targets.find("DraftTarget")
                    if d_elem is not None and d_elem.text:
                        project.project_target_words = int(d_elem.text)
                    s_elem = targets.find("SessionTarget")
                    if s_elem is not None and s_elem.text:
                        project.session_target_words = int(s_elem.text)
                    dh_elem = targets.find("DailyHoursTarget")
                    if dh_elem is not None and dh_elem.text:
                        project.daily_hours_target = float(dh_elem.text)
                    dl_elem = targets.find("Deadline")
                    if dl_elem is not None and dl_elem.text:
                        project.target_deadline = dl_elem.text
                    wd_elem = targets.find("WorkDays")
                    if wd_elem is not None and wd_elem.text:
                        project.target_work_days = [int(x) for x in wd_elem.text.split(",") if x.isdigit()]

            # Cargar Colecciones
            colls_elem = root.find("Collections")
            if colls_elem is not None:
                project.collections = []
                for c in colls_elem.findall("Collection"):
                    col = CollectionItem(
                        id=c.attrib.get("ID", ""),
                        name=c.attrib.get("Name", "Colección"),
                        color=c.attrib.get("Color", "#4a90e2"),
                        is_search=c.attrib.get("IsSearch") == "Yes"
                    )
                    if col.is_search:
                        q = c.find("Query")
                        col.search_query = q.text if q is not None and q.text else ""
                    else:
                        m_elem = c.find("Members")
                        if m_elem is not None:
                            col.member_uuids = [m.text for m in m_elem.findall("Member") if m.text]
                    project.collections.append(col)

            # Cargar Árbol de Binder
            binder_elem = root.find("Binder")
            if binder_elem is not None:
                project.root_nodes = []
                for item_elem in binder_elem.findall("BinderItem"):
                    node = XmlEngineV2._deserialize_binder_node(item_elem, None)
                    project.root_nodes.append(node)

                    # Clasificar nodos especiales
                    if node.type == "DraftFolder":
                        project.draft_node = node
                    elif node.type == "ResearchFolder":
                        project.research_node = node
                    elif node.type == "TrashFolder":
                        project.trash_node = node

            return True
        except Exception as e:
            raise IOError(f"Error parseando el archivo maestro XML {source_file}: {e}")

    @staticmethod
    def _deserialize_binder_node(elem: ET.Element, parent_uuid: Optional[str]) -> BinderNode:
        uuid_str = elem.attrib.get("ID", "")
        node_type = elem.attrib.get("Type", "Text")
        created = float(elem.attrib.get("Created", time.time()))
        modified = float(elem.attrib.get("Modified", time.time()))

        title_elem = elem.find("Title")
        title = title_elem.text if title_elem is not None and title_elem.text else "Sin Título"

        node = BinderNode(
            uuid=uuid_str,
            title=title,
            type=node_type,
            created=created,
            modified=modified,
            parent_uuid=parent_uuid
        )

        meta = elem.find("MetaData")
        if meta is not None:
            inc = meta.find("IncludeInCompile")
            if inc is not None:
                node.include_in_compile = inc.text == "Yes"
            st = meta.find("SectionType")
            if st is not None and st.text:
                node.section_type = st.text
            lbl = meta.find("Label")
            if lbl is not None and lbl.text:
                node.label = lbl.text
            sta = meta.find("Status")
            if sta is not None and sta.text:
                node.status = sta.text
            tw = meta.find("TargetWords")
            if tw is not None and tw.text:
                node.target_words = int(tw.text)

            kws_elem = meta.find("Keywords")
            if kws_elem is not None:
                node.keywords = [k.text for k in kws_elem.findall("Keyword") if k.text]

        # Nodos hijos
        children_elem = elem.find("Children")
        if children_elem is not None:
            for child_item in children_elem.findall("BinderItem"):
                child_node = XmlEngineV2._deserialize_binder_node(child_item, node.uuid)
                node.children.append(child_node)

        return node
