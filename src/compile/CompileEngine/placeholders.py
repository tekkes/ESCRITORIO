"""
Placeholder Tags Parser para Escritorio / Scrivener 3.
Evaluador integral de variables dinámicas, numeración automática y metadatos:
- Contadores arábigos: <$n>, <$n:nombre>
- Contadores romanos: <$r> (minúscula), <$R> (mayúscula)
- Contadores en palabras: <$t> / <$w> (minúscula), <$T> / <$W> (Capitalizado)
- Numeración jerárquica: <$hn> (ej. 1, 1.1, 1.2, 1.2.1)
- Reinicio de contadores: <$rst_n>, <$rst>, <$rst_n:nombre>
- Metadatos: <$projecttitle>, <$author>, <$title>, <$synopsis>, <$notes>, <$wc>, <$date>, <$time>, <$p>
"""

import re
import datetime
from typing import Dict, Any, Optional, List


def int_to_roman(num: int, uppercase: bool = True) -> str:
    """Convierte un entero positivo a número romano (1 a 3999)."""
    if num <= 0:
        return "0"
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ""
    i = 0
    while num > 0 and i < len(val):
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num if uppercase else roman_num.lower()


def int_to_words_es(num: int, capitalize: bool = False) -> str:
    """Convierte un número a palabras en español (hasta 999.999)."""
    if num == 0:
        res = "cero"
        return res.capitalize() if capitalize else res
    if num < 0:
        res = f"menos {int_to_words_es(abs(num))}"
        return res.capitalize() if capitalize else res

    unidades = [
        "", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve",
        "diez", "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete",
        "dieciocho", "diecinueve"
    ]
    decenas = [
        "", "", "veinte", "treinta", "cuarenta", "cincuenta", "sesenta", "setenta", "ochenta", "noventa"
    ]
    veintis = [
        "veinte", "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco",
        "veintiséis", "veintisiete", "veintiocho", "veintinueve"
    ]
    centenas = [
        "", "ciento", "doscientos", "trescientos", "cuatrocientos", "quinientos",
        "seiscientos", "setecientos", "ochocientos", "novecientos"
    ]

    def _convert_below_1000(n: int) -> str:
        if n == 0:
            return ""
        if n == 100:
            return "cien"
        parts = []
        c = n // 100
        rem = n % 100
        if c > 0:
            parts.append(centenas[c])
        if rem > 0:
            if rem < 20:
                parts.append(unidades[rem])
            elif 20 <= rem < 30:
                parts.append(veintis[rem - 20])
            else:
                d = rem // 10
                u = rem % 10
                if u == 0:
                    parts.append(decenas[d])
                else:
                    parts.append(f"{decenas[d]} y {unidades[u]}")
        return " ".join(parts).strip()

    result = ""
    if num >= 1000:
        miles = num // 1000
        resto = num % 1000
        if miles == 1:
            miles_str = "mil"
        else:
            miles_str = f"{_convert_below_1000(miles)} mil"
        resto_str = _convert_below_1000(resto)
        result = f"{miles_str} {resto_str}".strip()
    else:
        result = _convert_below_1000(num)

    if capitalize:
        return result.capitalize()
    return result


class PlaceholderResolver:
    """
    Evaluador y resolutor de comodines de Scrivener 3 durante el proceso de compilación.
    Mantiene estado de contadores secuenciales, nombrados y jerárquicos.
    """

    def __init__(
        self,
        project_metadata: Optional[Dict[str, Any]] = None,
        project_title: str = "",
        author: str = ""
    ):
        self.meta: Dict[str, Any] = dict(project_metadata) if project_metadata else {}
        if project_title:
            self.meta["project_title"] = project_title
        if author:
            self.meta["author"] = author
        # Contadores primarios
        self.counters: Dict[str, int] = {
            "n": 0,
            "r": 0,
            "R": 0,
            "t": 0,
            "T": 0,
            "w": 0,
            "W": 0,
            "ch": 0,
            "sc": 0
        }
        # Contadores con nombre (ej. "n:figure": 0, "n:table": 0)
        self.named_counters: Dict[str, int] = {}
        # Niveles jerárquicos para <$hn>
        self.hierarchical_counters: List[int] = [0] * 10
        self.last_hn_depth: int = 1

    def reset_counters(self):
        """Reinicia todos los contadores a su estado inicial cero."""
        for k in self.counters:
            self.counters[k] = 0
        self.named_counters.clear()
        self.hierarchical_counters = [0] * 10
        self.last_hn_depth = 1

    def reset_counter(self, counter_name: str):
        """Reinicia un contador específico o con nombre."""
        c_name = counter_name.lower().strip()
        if c_name in self.counters:
            self.counters[c_name] = 0
        if c_name in self.named_counters:
            self.named_counters[c_name] = 0

    def get_hierarchical_number(self, depth: int = 1) -> str:
        """
        Calcula la numeración jerárquica <$hn> para un nivel de profundidad dado (1-based).
        Ejemplo: nivel 1 -> "1", nivel 2 -> "1.1", nivel 2 siguiente -> "1.2".
        """
        d = max(1, min(depth, len(self.hierarchical_counters)))
        idx = d - 1
        self.hierarchical_counters[idx] += 1
        # Reiniciar niveles más profundos
        for i in range(idx + 1, len(self.hierarchical_counters)):
            self.hierarchical_counters[i] = 0
        self.last_hn_depth = d

        parts = [str(self.hierarchical_counters[i]) for i in range(d)]
        return ".".join(parts)

    def resolve(
        self,
        text: str,
        item_title: str = "",
        item_synopsis: str = "",
        item_notes: str = "",
        word_count: int = 0,
        current_page: int = 1,
        depth: int = 1,
        custom_replacements: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Reemplaza todas las variables y comodines presentes en el texto.
        """
        if not text:
            return ""

        result = text
        now = datetime.datetime.now()

        # 1. Comandos de reinicio de contadores: <$rst_n>, <$rst>, <$rst_n:nombre>
        def handle_reset(m):
            tag = m.group(1)
            name = m.group(2) if len(m.groups()) >= 2 else None
            if name:
                full_name = f"{tag}:{name.strip()}"
                self.reset_counter(full_name)
            else:
                self.reset_counter(tag)
                self.reset_counter("n")
            return ""

        result = re.sub(r"<\$rst(?:_([a-zA-Z0-9_]+))?(?::([a-zA-Z0-9_]+))?>", handle_reset, result)

        # 2. Metadatos del proyecto y documento
        result = result.replace("<$projecttitle>", str(self.meta.get("title", "Sin Título")))
        result = result.replace("<$author>", str(self.meta.get("author", "Autor")))
        result = result.replace("<$title>", item_title)
        result = result.replace("<$synopsis>", item_synopsis)
        result = result.replace("<$notes>", item_notes)
        result = result.replace("<$wc>", f"{word_count:,}".replace(",", "."))
        result = result.replace("<$p>", str(current_page))
        result = result.replace("<$date>", now.strftime("%Y-%m-%d"))
        result = result.replace("<$time>", now.strftime("%H:%M"))

        # Metadatos adicionales opcionales
        if custom_replacements:
            for k, v in custom_replacements.items():
                result = result.replace(f"<{k}>", str(v))

        # 3. Numerador jerárquico <$hn> o <$hn_depth>
        def handle_hn(m):
            custom_depth_str = m.group(1)
            d = int(custom_depth_str) if custom_depth_str else depth
            return self.get_hierarchical_number(d)

        result = re.sub(r"<\$hn(?:_(\d+))?>", handle_hn, result)

        # 4. Contadores secuenciales nombrados: <$n:figura>, <$R:seccion>, etc.
        def handle_named_counter(m):
            tag_type = m.group(1)
            counter_name = m.group(2).lower().strip()
            key = f"{tag_type}:{counter_name}"
            val = self.named_counters.get(key, 0) + 1
            self.named_counters[key] = val

            if tag_type == "n":
                return str(val)
            elif tag_type == "r":
                return int_to_roman(val, uppercase=False)
            elif tag_type == "R":
                return int_to_roman(val, uppercase=True)
            elif tag_type in ("t", "w"):
                return int_to_words_es(val, capitalize=False)
            elif tag_type in ("T", "W"):
                return int_to_words_es(val, capitalize=True)
            return str(val)

        result = re.sub(r"<\$([n|r|R|t|T|w|W]):([a-zA-Z0-9_\-]+)>", handle_named_counter, result)

        # 5. Contadores secuenciales estándar
        def handle_standard_counter(m):
            tag = m.group(1)
            # Manejar compatibilidad con ch y sc
            if tag == "ch":
                val = self.counters.get("ch", 0) + 1
                self.counters["ch"] = val
                return str(val)
            elif tag == "sc":
                val = self.counters.get("sc", 0) + 1
                self.counters["sc"] = val
                return str(val)

            # Contadores de numeración de Scrivener 3:
            # Los contadores n, r, R, t, T, w, W incrementan el contador principal de número
            current_n = self.counters.get("n", 0) + 1
            self.counters["n"] = current_n

            if tag == "n":
                return str(current_n)
            elif tag == "r":
                return int_to_roman(current_n, uppercase=False)
            elif tag == "R":
                return int_to_roman(current_n, uppercase=True)
            elif tag in ("t", "w"):
                return int_to_words_es(current_n, capitalize=False)
            elif tag in ("T", "W"):
                return int_to_words_es(current_n, capitalize=True)
            return str(current_n)

        result = re.sub(r"<\$([n|r|R|t|T|w|W|ch|sc])>", handle_standard_counter, result)

        return result
