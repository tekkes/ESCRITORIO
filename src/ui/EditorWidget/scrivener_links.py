"""
ScrivenerLinksEngine para Escritorio
Gestor de hipervínculos internos entre documentos del proyecto:
- Formato URI canónico: scrivener-link://{UUID}
- Formato Wiki / Título: [[Título del Documento]] o [[UUID|Texto alternativo]]
- Formato Markdown: [Texto de Enlace](scrivener-link://{UUID})
- Generación de campos RTF: {\\field{\\*\\fldinst{HYPERLINK "scrivener-link://..."}}{\\fldrslt{...}}}
- Resolución automática hacia nodos del Binder por UUID o Título.
"""

import re
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class ScrivenerLinkMatch:
    start_pos: int
    end_pos: int
    raw_text: str
    target_uuid: str
    target_title: str
    display_text: str


class ScrivenerLinksEngine:
    """Motor analizador y creador de enlaces internos Scrivener."""

    WIKI_PATTERN = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
    MD_PATTERN = re.compile(r"\[([^\]]+)\]\((?:scrivener-link://|#)([a-zA-Z0-9_-]+)\)")
    RTF_HYPERLINK_PATTERN = re.compile(
        r"\{\\field\{\\\*\\fldinst\{HYPERLINK\s+\"scrivener-link://([a-zA-Z0-9_-]+)\"\}\}\{\\fldrslt\{([^}]+)\}\}\}"
    )

    @classmethod
    def create_link_uri(cls, target_uuid: str) -> str:
        return f"scrivener-link://{target_uuid}"

    @classmethod
    def create_wiki_link(cls, target_title: str, display_text: Optional[str] = None) -> str:
        if display_text and display_text != target_title:
            return f"[[{target_title}|{display_text}]]"
        return f"[[{target_title}]]"

    @classmethod
    def create_rtf_hyperlink(cls, target_uuid: str, display_text: str) -> str:
        """Genera el bloque RTF estándar de Scrivener para un enlace interno."""
        uri = cls.create_link_uri(target_uuid)
        return rf'{{\field{{\*\fldinst{{HYPERLINK "{uri}"}}}}{{\fldrslt{{\ul\cf2 {display_text}}}}}}}'

    @classmethod
    def find_all_links(cls, plain_text: str, project=None) -> List[ScrivenerLinkMatch]:
        """Detecta todos los enlaces Scrivener y wiki-links dentro de un texto plano."""
        matches: List[ScrivenerLinkMatch] = []

        # 1. Wiki-links [[Título]] o [[Título|Texto]]
        for m in cls.WIKI_PATTERN.finditer(plain_text):
            target_key = m.group(1).strip()
            display = (m.group(2) or target_key).strip()

            target_uuid = ""
            target_title = target_key
            if project:
                # Intentar buscar por UUID directo
                item = project.get_item(target_key)
                if item:
                    target_uuid = item.uuid
                    target_title = item.title
                else:
                    # Buscar por título
                    for it in project.items_by_uuid.values():
                        if it.title.lower() == target_key.lower():
                            target_uuid = it.uuid
                            target_title = it.title
                            break

            matches.append(ScrivenerLinkMatch(
                start_pos=m.start(),
                end_pos=m.end(),
                raw_text=m.group(0),
                target_uuid=target_uuid,
                target_title=target_title,
                display_text=display
            ))

        # 2. Markdown links [Texto](scrivener-link://UUID)
        for m in cls.MD_PATTERN.finditer(plain_text):
            display = m.group(1).strip()
            uuid = m.group(2).strip()
            title = display
            if project:
                item = project.get_item(uuid)
                if item:
                    title = item.title

            matches.append(ScrivenerLinkMatch(
                start_pos=m.start(),
                end_pos=m.end(),
                raw_text=m.group(0),
                target_uuid=uuid,
                target_title=title,
                display_text=display
            ))

        matches.sort(key=lambda x: x.start_pos)
        return matches

    @classmethod
    def resolve_link_destination(cls, raw_uri_or_title: str, project) -> Optional[str]:
        """
        Resuelve una cadena (URI scrivener-link:// o título entre [[...]])
        hacia el UUID del documento destino.
        """
        if not project:
            return None

        # Limpiar prefijo URI si existe
        clean = raw_uri_or_title.strip()
        if clean.startswith("scrivener-link://"):
            uuid_part = clean[len("scrivener-link://"):].split("?")[0]
            if project.get_item(uuid_part):
                return uuid_part

        # Limpiar corchetes si es [[Título]]
        if clean.startswith("[[") and clean.endswith("]]"):
            clean = clean[2:-2].split("|")[0].strip()

        # Buscar por UUID
        if project.get_item(clean):
            return clean

        # Buscar por Título
        clean_lower = clean.lower()
        for it in project.items_by_uuid.values():
            if it.title.lower() == clean_lower:
                return it.uuid

        return None
