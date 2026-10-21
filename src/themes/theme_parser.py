"""
Theme Parser para Escritorio
Deserialización e importación de paquetes .scrtheme (Scrivener 3 Windows)
y paquetes nativos .escrtheme con soporte de hojas de estilo QSS y paletas .pal.
"""

import os
import zipfile
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class ThemePackage:
    name: str
    author: str = "Escritorio"
    version: str = "1.0.0"
    base_theme: str = "Dark"
    palette: Dict[str, str] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    qss_stylesheet: str = ""

class ThemeParser:
    """Parser de temas para paquetes de Scrivener 3 (.scrtheme) y nativos (.escrtheme)."""

    @classmethod
    def load_theme(cls, file_path: str) -> ThemePackage:
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"Tema no encontrado: {file_path}")

        if p.suffix.lower() == ".scrtheme" or zipfile.is_zipfile(p):
            return cls._load_scrtheme_zip(p)
        elif p.suffix.lower() in (".json", ".escrtheme"):
            return cls._load_escrtheme_json(p)
        else:
            raise ValueError(f"Formato de tema no soportado: {p.suffix}")

    @classmethod
    def _load_scrtheme_zip(cls, zip_path: Path) -> ThemePackage:
        with zipfile.ZipFile(zip_path, "r") as zf:
            files = zf.namelist()

            # 1. Manifest
            manifest_name = next((f for f in files if f.lower().endswith("manifest.xml")), None)
            theme_name = zip_path.stem
            author = "Scrivener User"
            version = "1.0"
            base_theme = "Dark"

            if manifest_name:
                manifest_data = zf.read(manifest_name).decode("utf-8", errors="replace")
                root = ET.fromstring(manifest_data)
                theme_name = root.findtext("Name") or theme_name
                author = root.findtext("Author") or author
                version = root.findtext("Version") or version
                base_theme = root.findtext("BaseTheme") or base_theme

            # 2. Palette .pal
            pal_file = next((f for f in files if f.lower().endswith(".pal")), None)
            palette: Dict[str, str] = {}
            if pal_file:
                pal_text = zf.read(pal_file).decode("utf-8", errors="replace")
                palette = cls.parse_palette_text(pal_text)

            # 3. Preferences .prefs
            prefs_file = next((f for f in files if f.lower().endswith(".prefs")), None)
            preferences: Dict[str, Any] = {}
            if prefs_file:
                prefs_text = zf.read(prefs_file).decode("utf-8", errors="replace")
                try:
                    preferences = json.loads(prefs_text)
                except Exception:
                    pass

            # 4. QSS
            qss_file = next((f for f in files if f.lower().endswith(".qss")), None)
            qss_text = ""
            if qss_file:
                qss_text = zf.read(qss_file).decode("utf-8", errors="replace")

            return ThemePackage(
                name=theme_name,
                author=author,
                version=version,
                base_theme=base_theme,
                palette=palette,
                preferences=preferences,
                qss_stylesheet=qss_text
            )

    @classmethod
    def _load_escrtheme_json(cls, json_path: Path) -> ThemePackage:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return ThemePackage(
            name=data.get("name", json_path.stem),
            author=data.get("author", "Escritorio"),
            version=data.get("version", "1.0.0"),
            base_theme=data.get("base_theme", "Dark"),
            palette=data.get("palette", {}),
            preferences=data.get("preferences", {}),
            qss_stylesheet=data.get("stylesheet", "")
        )

    @staticmethod
    def parse_palette_text(text: str) -> Dict[str, str]:
        """Convierte sintaxis de archivo .pal ini-like a diccionario."""
        palette = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("["):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                palette[k.strip()] = v.strip()
        return palette
