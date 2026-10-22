"""
RTF Engine para Escritorio
Manipulación, lectura, conversión y generación de documentos Rich Text Format (RTF 1.5 - 1.9),
preservando tipografía, negritas, cursivas, tablas de color y anotaciones editoriales.
"""

import re
from typing import Tuple, List, Dict, Any

class RTFEngine:
    """Motor de lectura y serialización RTF para nodos de documento y notas."""

    @staticmethod
    def plain_text_to_rtf(text: str, font_name: str = "Segoe UI", font_size_pt: int = 12) -> str:
        """
        Convierte texto plano en un documento RTF válido con codificación Unicode universal (\\uN?).
        """
        half_pts = font_size_pt * 2
        # Escapado RTF de caracteres especiales
        escaped_chars = []
        for char in text:
            code = ord(char)
            if char == '\\':
                escaped_chars.append(r"\\")
            elif char == '{':
                escaped_chars.append(r"\{")
            elif char == '}':
                escaped_chars.append(r"\}")
            elif char == '\n':
                escaped_chars.append(r"\par ")
            elif char == '\r':
                continue
            elif code < 128:
                escaped_chars.append(char)
            elif code <= 0xFFFF:
                # Carácter Unicode en el Plano Multilingüe Básico (BMP)
                signed_code = code if code <= 32767 else code - 65536
                escaped_chars.append(f"\\u{signed_code}?")
            else:
                # Caracteres de plano astral (ej. emojis) codificados como pares de sustitutos UTF-16
                high = 0xD800 + ((code - 0x10000) >> 10)
                low = 0xDC00 + ((code - 0x10000) & 0x3FF)
                signed_high = high - 65536
                signed_low = low - 65536
                escaped_chars.append(f"\\u{signed_high}?\\u{signed_low}?")

        body_rtf = "".join(escaped_chars)

        rtf_doc = (
            r"{\rtf1\ansi\ansicpg1252\deff0\nouicompat"
            rf"{{\fonttbl{{\f0\fnil\fcharset0 {font_name};}}}}"
            r"{\colortbl ;\red0\green0\blue0;\red30\green30\blue30;}"
            rf"\viewkind4\uc1\pard\cf1\f0\fs{half_pts} {body_rtf}\par}}"
        )
        return rtf_doc

    @staticmethod
    def rtf_to_plain_text(rtf_content: str) -> str:
        """
        Extrae el texto plano de un bloque RTF eliminando tags de control, grupos y resolviendo entidades Unicode.
        """
        if not rtf_content:
            return ""

        # Eliminar grupos ignorables como {\*\generator ...}
        text = re.sub(r"\{\\\*[^}]*\}", "", rtf_content)
        # Eliminar tablas de fuentes y colores iniciales
        text = re.sub(r"\{\\(fonttbl|colortbl|stylesheet)[^}]*\}", "", text)

        # Convertir saltos de línea y párrafos RTF
        text = re.sub(r"\\(line|par)\b\s*", "\n", text)
        text = re.sub(r"\\tab\b\s*", "\t", text)

        # Resolver caracteres unicode \uN?
        def replace_unicode(match):
            val = int(match.group(1))
            if val < 0:
                val += 65536
            try:
                return chr(val)
            except ValueError:
                return ""

        text = re.sub(r"\\u(-?\d+)\??", replace_unicode, text)
        try:
            text = text.encode("utf-16", "surrogatepass").decode("utf-16")
        except Exception:
            pass

        # Eliminar comandos restantes de control de RTF tipo \b, \i, \fs24, \cf0, etc.
        text = re.sub(r"\\[a-zA-Z]+(-?\d+)?\s?", "", text)

        # Eliminar llaves { y }
        text = text.replace("{", "").replace("}", "")

        # Reemplazar escapes de caracteres literales
        text = text.replace(r"\\", "\\")

        return text.strip()

    @classmethod
    def count_words(cls, content: str, is_rtf: bool = False) -> int:
        """Calcula el número de palabras del contenido de texto plano o RTF."""
        raw_text = cls.rtf_to_plain_text(content) if is_rtf else content
        words = re.findall(r"\b[\w'-]+\b", raw_text, re.UNICODE)
        return len(words)

    @classmethod
    def count_characters(cls, content: str, is_rtf: bool = False, count_spaces: bool = True) -> int:
        """Calcula el recuento de caracteres con o sin espacios."""
        raw_text = cls.rtf_to_plain_text(content) if is_rtf else content
        if count_spaces:
            return len(raw_text)
        return len(re.sub(r"\s+", "", raw_text))
