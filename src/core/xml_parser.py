"""
XML Parser para Escritorio
Serialización y deserialización de alta fidelidad para especificaciones de proyecto
Scrivener 3 (.scrivx) y formato nativo Escritorio (.escrx).
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

@dataclass
class BinderItemData:
    uuid: str
    item_type: str
    title: str = "Sin Título"
    created: str = ""
    modified: str = ""
    include_in_compile: bool = True
    section_type: str = "Structure Based"
    label_id: int = -1
    status_id: int = -1
    file_extension: str = "rtf"
    icon_file_name: str = ""
    custom_metadata: Dict[str, str] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    target_words: int = 0
    children: List['BinderItemData'] = field(default_factory=list)

@dataclass
class LabelDefinition:
    id: int
    name: str
    color_rgba: str = "1.0 1.0 1.0 1.0"

@dataclass
class StatusDefinition:
    id: int
    name: str

@dataclass
class CollectionDefinition:
    id: str
    title: str
    collection_type: str = "Arbitrary"  # "Arbitrary" o "Search"
    item_uuids: List[str] = field(default_factory=list)
    search_query: str = ""

class ScrivenerXMLParser:
    """Parser bidireccional para esquemas XML .scrivx y .escrx."""

    @classmethod
    def parse_xml_file(cls, xml_path: str) -> Dict[str, Any]:
        """Carga y analiza un archivo XML de proyecto .scrivx o .escrx."""
        tree = ET.parse(xml_path)
        root = tree.getroot()

        project_info = {
            "version": root.get("Version", "3.0"),
            "creator": root.get("Creator", "Escritorio"),
            "identifier": "",
            "title": "Proyecto Escritorio",
            "binder": [],
            "labels": {},
            "statuses": {},
            "section_types": {},
            "targets": {},
            "collections": []
        }

        # Identifier & Title
        id_node = root.find("ProjectIdentifier")
        if id_node is not None and id_node.text:
            project_info["identifier"] = id_node.text.strip()

        title_node = root.find("ProjectTitle")
        if title_node is not None and title_node.text:
            project_info["title"] = title_node.text.strip()

        # Labels
        labels_node = root.find(".//LabelSettings/Labels")
        if labels_node is not None:
            for l_elem in labels_node.findall("Label"):
                lid = int(l_elem.get("ID", -1))
                color = l_elem.get("Color", "1.0 1.0 1.0 1.0")
                name = l_elem.text.strip() if l_elem.text else "Etiqueta"
                project_info["labels"][lid] = LabelDefinition(id=lid, name=name, color_rgba=color)

        # Statuses
        statuses_node = root.find(".//StatusSettings/Statuses")
        if statuses_node is not None:
            for s_elem in statuses_node.findall("Status"):
                sid = int(s_elem.get("ID", -1))
                name = s_elem.text.strip() if s_elem.text else "Estado"
                project_info["statuses"][sid] = StatusDefinition(id=sid, name=name)

        # Section Types
        sec_types_node = root.find("SectionTypes")
        if sec_types_node is not None:
            for st_elem in sec_types_node.findall("Type"):
                tid = st_elem.get("ID", "")
                tname = st_elem.text.strip() if st_elem.text else tid
                project_info["section_types"][tid] = tname

        # Targets
        targets_node = root.find("ProjectTargets")
        if targets_node is not None:
            draft_target = targets_node.find("DraftTarget")
            if draft_target is not None:
                project_info["targets"]["draft_words"] = int(draft_target.get("Count", 0))
                project_info["targets"]["deadline"] = draft_target.get("Deadline", "")
            session_target = targets_node.find("SessionTarget")
            if session_target is not None:
                project_info["targets"]["session_words"] = int(session_target.get("Count", 0))

        # Binder Items
        binder_node = root.find("Binder")
        if binder_node is not None:
            for item_elem in binder_node.findall("BinderItem"):
                project_info["binder"].append(cls._parse_binder_item(item_elem))

        # Collections
        collections_node = root.find("Collections")
        if collections_node is not None:
            for col_elem in collections_node.findall("Collection"):
                cid = col_elem.get("ID", "")
                ctype = col_elem.get("Type", "Arbitrary")
                ctitle_node = col_elem.find("Title")
                ctitle = ctitle_node.text.strip() if ctitle_node is not None and ctitle_node.text else "Colección"
                
                query_node = col_elem.find("Query")
                search_query = query_node.text.strip() if query_node is not None and query_node.text else ""
                
                items = []
                items_node = col_elem.find("Items")
                if items_node is not None:
                    for it_node in items_node.findall("Item"):
                        uuid_val = it_node.get("UUID", "")
                        if uuid_val:
                            items.append(uuid_val)

                project_info["collections"].append(CollectionDefinition(
                    id=cid,
                    title=ctitle,
                    collection_type=ctype,
                    item_uuids=items,
                    search_query=search_query
                ))

        return project_info

    @classmethod
    def _parse_binder_item(cls, elem: ET.Element) -> BinderItemData:
        uuid = elem.get("UUID", "")
        item_type = elem.get("Type", "Text")
        created = elem.get("Created", "")
        modified = elem.get("Modified", "")

        title_elem = elem.find("Title")
        title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Sin Título"

        include_in_compile = True
        section_type = "Structure Based"
        label_id = -1
        status_id = -1
        file_ext = "rtf"
        icon_file = ""
        custom_meta = {}
        keywords = []

        meta_elem = elem.find("MetaData")
        if meta_elem is not None:
            inc_comp = meta_elem.find("IncludeInCompile")
            if inc_comp is not None and inc_comp.text:
                include_in_compile = (inc_comp.text.strip().lower() == "yes")

            st_node = meta_elem.find("SectionType")
            if st_node is not None and st_node.text:
                section_type = st_node.text.strip()

            lbl_node = meta_elem.find("LabelID")
            if lbl_node is not None and lbl_node.text:
                try:
                    label_id = int(lbl_node.text.strip())
                except ValueError:
                    pass

            stat_node = meta_elem.find("StatusID")
            if stat_node is not None and stat_node.text:
                try:
                    status_id = int(stat_node.text.strip())
                except ValueError:
                    pass

            ext_node = meta_elem.find("FileExtension")
            if ext_node is not None and ext_node.text:
                file_ext = ext_node.text.strip()

            icon_node = meta_elem.find("IconFileName")
            if icon_node is not None and icon_node.text:
                icon_file = icon_node.text.strip()

            cust_meta_node = meta_elem.find("CustomMetaData")
            if cust_meta_node is not None:
                for fld in cust_meta_node.findall("Field"):
                    fid = fld.get("ID", "")
                    if fid and fld.text:
                        custom_meta[fid] = fld.text.strip()

            keywords_node = meta_elem.find("Keywords")
            if keywords_node is not None:
                for kw in keywords_node.findall("Keyword"):
                    if kw.text:
                        keywords.append(kw.text.strip())

        target_words = 0
        target_node = elem.find(".//TextSettings/Target")
        if target_node is not None:
            try:
                target_words = int(target_node.get("Maximum", 0))
            except ValueError:
                pass

        children = []
        children_node = elem.find("Children")
        if children_node is not None:
            for child_elem in children_node.findall("BinderItem"):
                children.append(cls._parse_binder_item(child_elem))

        return BinderItemData(
            uuid=uuid,
            item_type=item_type,
            title=title,
            created=created,
            modified=modified,
            include_in_compile=include_in_compile,
            section_type=section_type,
            label_id=label_id,
            status_id=status_id,
            file_extension=file_ext,
            icon_file_name=icon_file,
            custom_metadata=custom_meta,
            keywords=keywords,
            target_words=target_words,
            children=children
        )

    @classmethod
    def generate_xml_string(cls, project_data: Dict[str, Any]) -> str:
        """Genera el contenido XML formateado y con sangría limpia para un proyecto."""
        root = ET.Element("ScrivenerProject", {
            "Version": str(project_data.get("version", "3.0")),
            "Creator": str(project_data.get("creator", "Escritorio-1.0")),
            "Device": "Windows-11"
        })

        ident = ET.SubElement(root, "ProjectIdentifier")
        ident.text = project_data.get("identifier", "")

        title = ET.SubElement(root, "ProjectTitle")
        title.text = project_data.get("title", "Proyecto")

        # Binder
        binder_elem = ET.SubElement(root, "Binder")
        for item in project_data.get("binder", []):
            cls._build_binder_element(binder_elem, item)

        # Labels
        lbl_settings = ET.SubElement(root, "LabelSettings")
        ET.SubElement(lbl_settings, "Title").text = "Etiqueta"
        labels_container = ET.SubElement(lbl_settings, "Labels")
        for lid, ldef in project_data.get("labels", {}).items():
            l_node = ET.SubElement(labels_container, "Label", {
                "ID": str(lid),
                "Color": ldef.color_rgba if hasattr(ldef, "color_rgba") else "1.0 1.0 1.0 1.0"
            })
            l_node.text = ldef.name if hasattr(ldef, "name") else str(ldef)

        # Statuses
        stat_settings = ET.SubElement(root, "StatusSettings")
        ET.SubElement(stat_settings, "Title").text = "Estado"
        statuses_container = ET.SubElement(stat_settings, "Statuses")
        for sid, sdef in project_data.get("statuses", {}).items():
            s_node = ET.SubElement(statuses_container, "Status", {"ID": str(sid)})
            s_node.text = sdef.name if hasattr(sdef, "name") else str(sdef)

        # Section Types
        sec_types = ET.SubElement(root, "SectionTypes")
        for st_id, st_name in project_data.get("section_types", {}).items():
            st_node = ET.SubElement(sec_types, "Type", {"ID": st_id})
            st_node.text = st_name

        # Targets
        targets_elem = ET.SubElement(root, "ProjectTargets")
        targets_data = project_data.get("targets", {})
        draft_words = str(targets_data.get("draft_words", 50000))
        ET.SubElement(targets_elem, "DraftTarget", {"Type": "Words", "Count": draft_words})
        session_words = str(targets_data.get("session_words", 1000))
        ET.SubElement(targets_elem, "SessionTarget", {"Type": "Words", "Count": session_words})

        # Collections
        collections_elem = ET.SubElement(root, "Collections")
        for col in project_data.get("collections", []):
            col_id = col.id if hasattr(col, "id") else col.get("id", "COL-1")
            col_type = col.collection_type if hasattr(col, "collection_type") else col.get("type", "Arbitrary")
            col_title = col.title if hasattr(col, "title") else col.get("title", "Colección")
            
            c_node = ET.SubElement(collections_elem, "Collection", {
                "ID": str(col_id),
                "Type": str(col_type)
            })
            ET.SubElement(c_node, "Title").text = str(col_title)
            
            if col_type == "Search":
                query_val = col.search_query if hasattr(col, "search_query") else col.get("query", "")
                ET.SubElement(c_node, "Query").text = str(query_val)
            else:
                items_container = ET.SubElement(c_node, "Items")
                uuids = col.item_uuids if hasattr(col, "item_uuids") else col.get("items", [])
                for u in uuids:
                    ET.SubElement(items_container, "Item", {"UUID": str(u)})

        raw_xml = ET.tostring(root, encoding="utf-8")
        parsed = minidom.parseString(raw_xml)
        return parsed.toprettyxml(indent="    ", encoding="utf-8").decode("utf-8")

    @classmethod
    def _build_binder_element(cls, parent: ET.Element, item: BinderItemData):
        item_elem = ET.SubElement(parent, "BinderItem", {
            "UUID": item.uuid,
            "Type": item.item_type
        })
        if item.created:
            item_elem.set("Created", item.created)
        if item.modified:
            item_elem.set("Modified", item.modified)

        ET.SubElement(item_elem, "Title").text = item.title

        meta = ET.SubElement(item_elem, "MetaData")
        ET.SubElement(meta, "IncludeInCompile").text = "Yes" if item.include_in_compile else "No"
        ET.SubElement(meta, "SectionType").text = item.section_type
        if item.label_id != -1:
            ET.SubElement(meta, "LabelID").text = str(item.label_id)
        if item.status_id != -1:
            ET.SubElement(meta, "StatusID").text = str(item.status_id)
        if item.file_extension:
            ET.SubElement(meta, "FileExtension").text = item.file_extension
        if item.icon_file_name:
            ET.SubElement(meta, "IconFileName").text = item.icon_file_name

        if item.custom_metadata:
            cm_node = ET.SubElement(meta, "CustomMetaData")
            for k, v in item.custom_metadata.items():
                f_elem = ET.SubElement(cm_node, "Field", {"ID": k})
                f_elem.text = v

        if item.keywords:
            kw_node = ET.SubElement(meta, "Keywords")
            for kw in item.keywords:
                k_elem = ET.SubElement(kw_node, "Keyword")
                k_elem.text = kw

        if item.target_words > 0:
            txt_sett = ET.SubElement(item_elem, "TextSettings")
            ET.SubElement(txt_sett, "Target", {"Type": "Words", "Maximum": str(item.target_words)})

        children_elem = ET.SubElement(item_elem, "Children")
        for child in item.children:
            cls._build_binder_element(children_elem, child)
