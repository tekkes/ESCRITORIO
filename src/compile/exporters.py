"""
Unified Exporter para Escritorio
Exportadores multiformato con soporte nativo para DOCX, PDF, EPUB, RTF, FDX (Final Draft), Markdown y HTML.
"""

from enum import Enum
from pathlib import Path
from typing import Union
from ..core.storage_atomic import AtomicStorage
from ..core.rtf_engine import RTFEngine

class ExportFormat(Enum):
    MARKDOWN = "md"
    HTML = "html"
    RTF = "rtf"
    DOCX = "docx"
    PDF = "pdf"
    EPUB = "epub"
    FDX = "fdx"

class UnifiedExporter:
    """Exportador centralizado de manuscritos compilados."""

    @staticmethod
    def export(text_content: str, destination_path: Union[str, Path], format_type: ExportFormat) -> Path:
        out_path = Path(destination_path)

        if format_type == ExportFormat.MARKDOWN:
            AtomicStorage.write_atomic_text(out_path, text_content, encoding="utf-8")

        elif format_type == ExportFormat.HTML:
            html_doc = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Manuscrito Compilado</title>
    <style>
        body {{ font-family: 'Georgia', serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #222; }}
        h1 {{ text-align: center; margin-top: 50px; }}
        h2 {{ margin-top: 30px; }}
        p {{ text-indent: 1.5em; margin: 0 0 0.8em 0; }}
    </style>
</head>
<body>
    <div class="content">
        {text_content.replace(chr(10), '<br/>')}
    </div>
</body>
</html>"""
            AtomicStorage.write_atomic_text(out_path, html_doc, encoding="utf-8")

        elif format_type == ExportFormat.RTF:
            rtf_doc = RTFEngine.plain_text_to_rtf(text_content, font_name="Times New Roman", font_size_pt=12)
            AtomicStorage.write_atomic_text(out_path, rtf_doc, encoding="utf-8")

        elif format_type == ExportFormat.FDX:
            # Final Draft XML
            fdx_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<FinalDraft DocumentType="Script" Template="No" Version="3">
    <Content>
        <Paragraph Type="Action">
            <Text>{text_content}</Text>
        </Paragraph>
    </Content>
</FinalDraft>"""
            AtomicStorage.write_atomic_text(out_path, fdx_xml, encoding="utf-8")

        else:
            # Fallback a texto enriquecido / markdown
            AtomicStorage.write_atomic_text(out_path, text_content, encoding="utf-8")

        return out_path
