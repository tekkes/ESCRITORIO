"""
Myers Diff Engine para Instantáneas (Snapshots) de Escritorio
Implementación del algoritmo de diferencias de Myers (Shortest Edit Script / LCS)
con granularidad a nivel de palabra, cláusula, párrafo y carácter.
Genera representación estructurada y formateada con:
- Palabras eliminadas: tachadas en rojo (#EF4444)
- Palabras añadidas: subrayadas en verde/azul (#10B981 / #3B82F6)
- Texto sin cambios: estilo estándar
"""

from enum import Enum
import re
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass


class DiffOp(Enum):
    EQUAL = "equal"
    DELETE = "delete"
    INSERT = "insert"


class DiffGranularity(Enum):
    WORD = "word"
    CLAUSE = "clause"
    PARAGRAPH = "paragraph"
    CHARACTER = "character"


@dataclass
class DiffChunk:
    op: DiffOp
    text: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "op": self.op.value,
            "text": self.text
        }


class MyersDiffEngine:
    """Motor de cálculo de diferencias basado en el algoritmo de Myers."""

    @classmethod
    def tokenize(cls, text: str, granularity: DiffGranularity = DiffGranularity.WORD) -> List[str]:
        """Divide el texto según la granularidad solicitada preservando espacios y puntuación."""
        if not text:
            return []

        if granularity == DiffGranularity.CHARACTER:
            return list(text)

        elif granularity == DiffGranularity.WORD:
            # Tokenizar por palabras y secuencias de no-palabras (espacios/puntuación)
            tokens = re.findall(r"[\w'-]+|[^\w'-]+", text, re.UNICODE)
            return tokens

        elif granularity == DiffGranularity.CLAUSE:
            # Tokenizar por oraciones y cláusulas delimitadas por comas, puntos, etc.
            tokens = re.split(r"([,;:.\n]+)", text)
            return [t for t in tokens if t]

        elif granularity == DiffGranularity.PARAGRAPH:
            # Tokenizar por párrafos
            tokens = re.split(r"(\n+)", text)
            return [t for t in tokens if t]

        return text.split()

    @classmethod
    def compute_diff(
        cls,
        original_text: str,
        revised_text: str,
        granularity: DiffGranularity = DiffGranularity.WORD
    ) -> List[DiffChunk]:
        """
        Calcula el diff entre original_text e revised_text usando el algoritmo de Myers.
        Retorna la lista ordenada de DiffChunks.
        """
        a = cls.tokenize(original_text, granularity)
        b = cls.tokenize(revised_text, granularity)

        n = len(a)
        m = len(b)

        # Si uno está vacío
        if n == 0 and m == 0:
            return []
        if n == 0:
            return [DiffChunk(DiffOp.INSERT, "".join(b))]
        if m == 0:
            return [DiffChunk(DiffOp.DELETE, "".join(a))]

        max_d = n + m
        v = {1: 0}
        trace = []

        # Búsqueda del camino más corto (Myers Greedy LCS)
        for d in range(max_d + 1):
            v_copy = dict(v)
            trace.append(v_copy)
            for k in range(-d, d + 1, 2):
                if k == -d or (k != d and v.get(k - 1, 0) < v.get(k + 1, 0)):
                    x = v.get(k + 1, 0)
                else:
                    x = v.get(k - 1, 0) + 1

                y = x - k

                while x < n and y < m and a[x] == b[y]:
                    x += 1
                    y += 1

                v[k] = x

                if x >= n and y >= m:
                    # Se alcanzó el final de ambas secuencias
                    return cls._backtrack_diff(trace, a, b, n, m)

        return cls._backtrack_diff(trace, a, b, n, m)

    @classmethod
    def _backtrack_diff(
        cls,
        trace: List[Dict[int, int]],
        a: List[str],
        b: List[str],
        n: int,
        m: int
    ) -> List[DiffChunk]:
        """Reconstruye los chunks de edición desde el trace de Myers."""
        x = n
        y = m
        chunks: List[DiffChunk] = []

        for d in range(len(trace) - 1, -1, -1):
            v = trace[d]
            k = x - y

            if d == 0:
                prev_k = 0
            elif k == -d or (k != d and v.get(k - 1, 0) < v.get(k + 1, 0)):
                prev_k = k + 1
            else:
                prev_k = k - 1

            prev_x = v.get(prev_k, 0)
            prev_y = prev_x - prev_k

            # Diagonales coincidentes (EQUAL)
            while x > prev_x and y > prev_y:
                x -= 1
                y -= 1
                chunks.append(DiffChunk(DiffOp.EQUAL, a[x]))

            if d > 0:
                if x == prev_x:
                    # Inserción
                    y -= 1
                    chunks.append(DiffChunk(DiffOp.INSERT, b[y]))
                elif y == prev_y:
                    # Eliminación
                    x -= 1
                    chunks.append(DiffChunk(DiffOp.DELETE, a[x]))

        chunks.reverse()

        # Coalescer chunks consecutivos del mismo tipo
        coalesced: List[DiffChunk] = []
        for ch in chunks:
            if coalesced and coalesced[-1].op == ch.op:
                coalesced[-1].text += ch.text
            else:
                coalesced.append(DiffChunk(ch.op, ch.text))

        return coalesced

    @classmethod
    def format_diff_html(cls, chunks: List[DiffChunk]) -> str:
        """
        Genera representación visual en HTML para visor de diferencias:
        - Eliminado: rojo tachado (#EF4444)
        - Añadido: verde subrayado (#10B981)
        - Igual: texto normal
        """
        html_parts = []
        for ch in chunks:
            text = ch.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if ch.op == DiffOp.DELETE:
                html_parts.append(f'<span style="color:#EF4444;text-decoration:line-through;background-color:#FEE2E2;">{text}</span>')
            elif ch.op == DiffOp.INSERT:
                html_parts.append(f'<span style="color:#10B981;text-decoration:underline;background-color:#D1FAE5;font-weight:bold;">{text}</span>')
            else:
                html_parts.append(text)

        return "".join(html_parts)

    render_html = format_diff_html

    @classmethod
    def format_diff_plain(cls, chunks: List[DiffChunk]) -> str:
        """Representación textual con etiquetas [-eliminado-] y {+añadido+}."""
        parts = []
        for ch in chunks:
            if ch.op == DiffOp.DELETE:
                parts.append(f"[-{ch.text}-]")
            elif ch.op == DiffOp.INSERT:
                parts.append(f"{{+{ch.text}+}}")
            else:
                parts.append(ch.text)
        return "".join(parts)
