"""
ScrThemeLoader & Theme Parser para Escritorio
Soporte completo y bidireccional para paquetes .scrtheme (Scrivener 3 Windows)
y paquetes nativos .escrtheme, con descompresión en memoria, análisis de manifest XML,
paleta .pal, preferencias .prefs y hojas de estilo Qt/QSS.
"""

import io
import os
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional, Union, BinaryIO
from dataclasses import dataclass, field

# Mapeo bidireccional entre tokens de Scrivener 3 (.pal) y tokens internos de Escritorio
SCRIVENER_TO_ESCRITORIO_TOKENS = {
    "window.background": "window.background",
    "window.foreground": "window.foreground",
    "window.text": "window.foreground",
    "binder.background": "binder.background",
    "binder.itemtext": "binder.foreground",
    "binder.text": "binder.foreground",
    "binder.foreground": "binder.foreground",
    "binder.selectedbackground": "binder.selected_bg",
    "binder.selectedforeground": "binder.selected_fg",
    "binder.selected_bg": "binder.selected_bg",
    "binder.selected_fg": "binder.selected_fg",
    "editor.background": "editor.background",
    "editor.foreground": "editor.foreground",
    "editor.text": "editor.foreground",
    "editor.caretcolor": "editor.caret",
    "editor.caret": "editor.caret",
    "editor.selectionbackground": "editor.selection",
    "editor.selection": "editor.selection",
    "editor.headerbackground": "editor.header_bg",
    "editor.headerforeground": "editor.header_fg",
    "corkboard.background": "corkboard.background",
    "corkboard.cardbackground": "corkboard.card_bg",
    "corkboard.cardforeground": "corkboard.card_fg",
    "corkboard.card_bg": "corkboard.card_bg",
    "corkboard.card_fg": "corkboard.card_fg",
    "corkboard.pincolor": "corkboard.pin_color",
    "corkboard.cardborder": "corkboard.card_border",
    "outliner.gridline": "outliner.grid",
    "outliner.grid": "outliner.grid",
    "outliner.rowalternate": "outliner.row_alternate",
    "outliner.background": "outliner.background",
    "outliner.foreground": "outliner.foreground",
    "inspector.background": "inspector.background",
    "inspector.foreground": "inspector.foreground",
    "inspector.cardbackground": "inspector.card_bg",
    "toolbar.background": "toolbar.background",
    "toolbar.foreground": "toolbar.foreground",
    "statusbar.background": "statusbar.background",
    "statusbar.foreground": "statusbar.foreground",
}

ESCRITORIO_TO_SCRIVENER_TOKENS = {
    "window.background": "Window.Background",
    "window.foreground": "Window.Foreground",
    "binder.background": "Binder.Background",
    "binder.foreground": "Binder.ItemText",
    "binder.selected_bg": "Binder.SelectedBackground",
    "binder.selected_fg": "Binder.SelectedForeground",
    "editor.background": "Editor.Background",
    "editor.foreground": "Editor.Foreground",
    "editor.caret": "Editor.CaretColor",
    "editor.selection": "Editor.SelectionBackground",
    "editor.header_bg": "Editor.HeaderBackground",
    "editor.header_fg": "Editor.HeaderForeground",
    "corkboard.background": "Corkboard.Background",
    "corkboard.card_bg": "Corkboard.CardBackground",
    "corkboard.card_fg": "Corkboard.CardForeground",
    "corkboard.pin_color": "Corkboard.PinColor",
    "corkboard.card_border": "Corkboard.CardBorder",
    "outliner.grid": "Outliner.GridLine",
    "outliner.row_alternate": "Outliner.RowAlternate",
    "outliner.background": "Outliner.Background",
    "outliner.foreground": "Outliner.Foreground",
    "inspector.background": "Inspector.Background",
    "inspector.foreground": "Inspector.Foreground",
    "inspector.card_bg": "Inspector.CardBackground",
    "toolbar.background": "Toolbar.Background",
    "toolbar.foreground": "Toolbar.Foreground",
    "statusbar.background": "StatusBar.Background",
    "statusbar.foreground": "StatusBar.Foreground",
}


@dataclass
class ThemePackage:
    """Representación en memoria de un tema visual completo."""
    name: str
    author: str = "Escritorio"
    version: str = "1.0.0"
    base_theme: str = "Dark"
    target_platform: str = "Windows"
    palette: Dict[str, str] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    qss_stylesheet: str = ""
    raw_pal_text: str = ""


class ScrThemeLoader:
    """
    Cargador nativo para paquetes de tema .scrtheme de Scrivener 3.
    Capaz de descomprimir el contenedor ZIP en memoria sin escribir archivos temporales
    y analizar el manifiesto XML, paleta .pal, preferencias .prefs y hoja de estilos QSS.
    """

    @classmethod
    def load_from_memory(cls, source: Union[bytes, BinaryIO, str, Path]) -> ThemePackage:
        """Carga y parsea un archivo .scrtheme directamente desde memoria o ruta de disco."""
        if isinstance(source, (str, Path)):
            p = Path(source)
            if not p.exists():
                raise FileNotFoundError(f"Archivo .scrtheme no encontrado: {source}")
            with open(p, "rb") as f:
                data = f.read()
            zip_buffer = io.BytesIO(data)
            theme_default_name = p.stem
        elif isinstance(source, bytes):
            zip_buffer = io.BytesIO(source)
            theme_default_name = "ImportedTheme"
        else:
            # Archivo o buffer binario
            data = source.read()
            zip_buffer = io.BytesIO(data)
            theme_default_name = "ImportedTheme"

        if not zipfile.is_zipfile(zip_buffer):
            raise ValueError("El archivo no es un paquete ZIP .scrtheme válido.")

        zip_buffer.seek(0)
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            namelist = zf.namelist()

            # 1. Manifiesto XML
            manifest_file = next(
                (f for f in namelist if f.lower().endswith("manifest.xml") or f.lower().endswith(".xml")),
                None
            )
            theme_name = theme_default_name
            author = "Scrivener User"
            version = "1.0.0"
            base_theme = "Dark"
            target_platform = "Windows"

            if manifest_file:
                xml_data = zf.read(manifest_file).decode("utf-8", errors="replace")
                try:
                    root = ET.fromstring(xml_data)
                    theme_name = root.findtext("Name") or root.findtext("name") or theme_name
                    author = root.findtext("Author") or root.findtext("author") or author
                    version = root.findtext("Version") or root.findtext("version") or version
                    base_theme = root.findtext("BaseTheme") or root.findtext("baseTheme") or base_theme
                    target_platform = root.findtext("TargetPlatform") or target_platform
                except Exception:
                    pass

            # 2. Paleta .pal
            pal_file = next((f for f in namelist if f.lower().endswith(".pal")), None)
            palette: Dict[str, str] = {}
            raw_pal_text = ""
            if pal_file:
                raw_pal_text = zf.read(pal_file).decode("utf-8", errors="replace")
                palette = cls.parse_pal_data(raw_pal_text)

            # 3. Preferencias .prefs
            prefs_file = next((f for f in namelist if f.lower().endswith(".prefs")), None)
            preferences: Dict[str, Any] = {}
            if prefs_file:
                prefs_raw = zf.read(prefs_file).decode("utf-8", errors="replace")
                preferences = cls.parse_prefs_data(prefs_raw)

            # 4. Hoja de estilos .qss
            qss_file = next((f for f in namelist if f.lower().endswith(".qss")), None)
            qss_text = ""
            if qss_file:
                qss_text = zf.read(qss_file).decode("utf-8", errors="replace")

            return ThemePackage(
                name=theme_name,
                author=author,
                version=version,
                base_theme=base_theme,
                target_platform=target_platform,
                palette=palette,
                preferences=preferences,
                qss_stylesheet=qss_text,
                raw_pal_text=raw_pal_text
            )

    @classmethod
    def parse_pal_data(cls, text: str) -> Dict[str, str]:
        """
        Parsea un archivo .pal de Scrivener 3 (formato INI con sección [Palette])
        e indexa tanto las claves originales de Scrivener como los tokens canónicos normalizados.
        """
        palette: Dict[str, str] = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith(";"):
                continue
            if line.startswith("[") and line.endswith("]"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                k = key.strip()
                v = val.strip()
                # Guardar clave original
                palette[k] = v

                # Normalizar clave a formato en minúsculas con punto
                norm_key = k.lower().replace("_", ".")
                palette[norm_key] = v

                # Mapear a token interno si existe en el diccionario
                if norm_key in SCRIVENER_TO_ESCRITORIO_TOKENS:
                    canonical = SCRIVENER_TO_ESCRITORIO_TOKENS[norm_key]
                    palette[canonical] = v
        return palette

    @classmethod
    def parse_prefs_data(cls, text: str) -> Dict[str, Any]:
        """
        Parsea el archivo .prefs, tolerando tanto formato JSON moderno
        como formato clave-valor estilo Scrivener clásico.
        """
        text = text.strip()
        if not text:
            return {}

        # Intentar JSON
        try:
            return json.loads(text)
        except Exception:
            pass

        # Parsear como líneas clave=valor
        prefs: Dict[str, Any] = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith(";"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip()
                # Intentar conversión de tipos
                if v.lower() == "true":
                    prefs[k] = True
                elif v.lower() == "false":
                    prefs[k] = False
                elif v.isdigit():
                    prefs[k] = int(v)
                else:
                    try:
                        prefs[k] = float(v)
                    except ValueError:
                        prefs[k] = v
        return prefs

    @classmethod
    def export_to_scrtheme(cls, package: ThemePackage, output_dest: Optional[Union[str, Path, BinaryIO]] = None) -> bytes:
        """
        Empaqueta un ThemePackage en un archivo .scrtheme (contenedor ZIP válido para Scrivener 3)
        que contiene manifest.xml, palette.pal, preferences.prefs y stylesheet.qss.
        """
        zip_buf = io.BytesIO()

        with zipfile.ZipFile(zip_buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            # 1. manifest.xml
            manifest_xml = (
                f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<ThemeManifest Version="1.0">\n'
                f'    <Name>{package.name}</Name>\n'
                f'    <Author>{package.author}</Author>\n'
                f'    <Version>{package.version}</Version>\n'
                f'    <TargetPlatform>{package.target_platform}</TargetPlatform>\n'
                f'    <BaseTheme>{package.base_theme}</BaseTheme>\n'
                f'</ThemeManifest>\n'
            )
            zf.writestr("manifest.xml", manifest_xml.encode("utf-8"))

            # 2. palette.pal
            pal_lines = ["[Palette]"]
            written_keys = set()
            for k, v in package.palette.items():
                scriv_key = ESCRITORIO_TO_SCRIVENER_TOKENS.get(k, k)
                if scriv_key not in written_keys:
                    pal_lines.append(f"{scriv_key}={v}")
                    written_keys.add(scriv_key)
            pal_content = "\n".join(pal_lines) + "\n"
            zf.writestr("palette.pal", pal_content.encode("utf-8"))

            # 3. preferences.prefs
            prefs_content = json.dumps(package.preferences, indent=4) if package.preferences else "{\n}\n"
            zf.writestr("preferences.prefs", prefs_content.encode("utf-8"))

            # 4. stylesheet.qss
            qss_content = package.qss_stylesheet or ""
            zf.writestr("stylesheet.qss", qss_content.encode("utf-8"))

        raw_bytes = zip_buf.getvalue()

        if output_dest is not None:
            if isinstance(output_dest, (str, Path)):
                out_p = Path(output_dest)
                out_p.parent.mkdir(parents=True, exist_ok=True)
                with open(out_p, "wb") as f:
                    f.write(raw_bytes)
            else:
                output_dest.write(raw_bytes)

        return raw_bytes


class ThemeParser:
    """Punto de entrada unificado para carga y serialización de temas de Scrivener y Escritorio."""

    @classmethod
    def load_theme(cls, file_path: Union[str, Path]) -> ThemePackage:
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"Tema no encontrado: {file_path}")

        if p.suffix.lower() == ".scrtheme" or zipfile.is_zipfile(p):
            return ScrThemeLoader.load_from_memory(p)
        elif p.suffix.lower() in (".json", ".escrtheme"):
            return cls._load_escrtheme_json(p)
        else:
            raise ValueError(f"Formato de tema no soportado: {p.suffix}")

    @classmethod
    def _load_escrtheme_json(cls, json_path: Path) -> ThemePackage:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return ThemePackage(
            name=data.get("name", json_path.stem),
            author=data.get("author", "Escritorio"),
            version=data.get("version", "1.0.0"),
            base_theme=data.get("base_theme", "Dark"),
            target_platform=data.get("target_platform", "Windows"),
            palette=data.get("palette", {}),
            preferences=data.get("preferences", {}),
            qss_stylesheet=data.get("stylesheet", "")
        )

    @classmethod
    def save_escrtheme(cls, package: ThemePackage, output_path: Union[str, Path]) -> str:
        data = {
            "name": package.name,
            "author": package.author,
            "version": package.version,
            "base_theme": package.base_theme,
            "target_platform": package.target_platform,
            "palette": package.palette,
            "preferences": package.preferences,
            "stylesheet": package.qss_stylesheet
        }
        json_str = json.dumps(data, indent=4, ensure_ascii=False)
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            f.write(json_str)
        return json_str
