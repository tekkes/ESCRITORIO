"""
Writing Statistics and Word Frequency Engine para Escritorio.
Métricas editoriales avanzadas:
- Conteo exacto: palabras, caracteres (con y sin espacios), párrafos, oraciones.
- Estimaciones editoriales: páginas impresas estándar (250 palabras/página),
  páginas de libro de bolsillo (300 palabras/página), tiempo de lectura y locución.
- Índices de legibilidad: Flesch-Szigriszt y Fernández-Huerta adaptados al español.
- Tabla interactiva de Frecuencia de Palabras (Word Frequency) con filtro de stop-words
  en español e inglés para detección de redundancias y repeticiones léxicas.
- Análisis a nivel de documento individual o agregado a nivel de todo el proyecto.
"""

import re
from collections import Counter
from typing import Dict, Any, List, Optional, Set
from ..core.project import EscritorioProject, BinderItem
from ..core.rtf_engine import RTFEngine


# Lista completa de Stop-Words en Español (artículos, preposiciones, pronombres, conjunciones)
SPANISH_STOP_WORDS: Set[str] = {
    "de", "la", "que", "el", "en", "y", "a", "los", "se", "del", "las", "un", "por", "con", "no", "una",
    "su", "para", "es", "al", "lo", "como", "más", "pero", "sus", "le", "ya", "o", "fue", "este", "ha",
    "sí", "porque", "esta", "son", "entre", "está", "cuando", "muy", "sin", "sobre", "ser", "tiene", "también",
    "me", "hasta", "hay", "donde", "han", "quien", "están", "estado", "desde", "todo", "nos", "durante",
    "estados", "todos", "uno", "les", "ni", "contra", "otros", "fueron", "ese", "eso", "había", "ante",
    "ellos", "e", "esto", "mí", "antes", "algunos", "qué", "unos", "yo", "otro", "otras", "otra", "él",
    "tanto", "esa", "estos", "mucho", "quienes", "nada", "muchos", "cual", "sea", "poco", "ella", "estar",
    "haber", "estas", "estaba", "estamos", "algunas", "algo", "nosotros", "mi", "mis", "tú", "te", "ti",
    "tu", "tus", "aquel", "aquella", "aquello", "aquellas", "aquellos", "entonces", "hacia", "tras", "cada",
    "mas", "si", "tan", "bien", "solo", "sólo", "incluso", "aun", "aún", "mientras", "luego", "casi"
}

# Stop-Words en Inglés comunes
ENGLISH_STOP_WORDS: Set[str] = {
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on", "with",
    "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
    "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", "so", "up", "out", "if",
    "about", "who", "get", "which", "go", "me", "when", "make", "can", "like", "time", "no", "just", "him",
    "know", "take", "people", "into", "year", "your", "good", "some", "could", "them", "see", "other",
    "than", "then", "now", "look", "only", "come", "its", "over", "think", "also", "back", "after", "use",
    "two", "how", "our", "work", "first", "well", "way", "even", "new", "want", "because", "any", "these"
}

ALL_STOP_WORDS: Set[str] = SPANISH_STOP_WORDS.union(ENGLISH_STOP_WORDS)


class WritingStatistics:
    """Calculador de estadísticas editoriales y frecuencia de palabras."""

    WORDS_PER_PRINTED_PAGE: int = 250    # Estándar editorial de manuscrito (hoja A4 doble espacio)
    WORDS_PER_PAPERBACK_PAGE: int = 300  # Estándar de libro de bolsillo impreso
    WORDS_PER_MINUTE_READING: int = 220  # Lectura silenciosa adulta
    WORDS_PER_MINUTE_SPEAKING: int = 140 # Locución / lectura dramatizada en voz alta

    @classmethod
    def analyze_text(cls, text: str) -> Dict[str, Any]:
        """Calcula todas las métricas de volumen, legibilidad y páginas estimadas."""
        if not text or not text.strip():
            return {
                "words": 0,
                "characters_with_spaces": 0,
                "characters_without_spaces": 0,
                "paragraphs": 0,
                "sentences": 0,
                "printed_pages": 0.0,
                "paperback_pages": 0.0,
                "reading_time_minutes": 0.0,
                "speaking_time_minutes": 0.0,
                "average_words_per_sentence": 0.0,
                "average_words_per_paragraph": 0.0,
                "readability_score": 100.0,
                "readability_level": "Muy Fácil"
            }

        # Palabras
        words = re.findall(r"\b[\w'-]+\b", text, re.UNICODE)
        word_count = len(words)

        # Caracteres
        char_with_spaces = len(text)
        char_without_spaces = len(re.sub(r"\s+", "", text))

        # Párrafos
        paragraphs = [p for p in text.splitlines() if p.strip()]
        para_count = len(paragraphs)

        # Oraciones
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        sentence_count = max(1, len(sentences))

        # Páginas estimadas
        printed_pages = round(word_count / cls.WORDS_PER_PRINTED_PAGE, 1)
        paperback_pages = round(word_count / cls.WORDS_PER_PAPERBACK_PAGE, 1)

        # Tiempos estimados
        reading_time = round(word_count / cls.WORDS_PER_MINUTE_READING, 1)
        speaking_time = round(word_count / cls.WORDS_PER_MINUTE_SPEAKING, 1)

        avg_words_sentence = round(word_count / sentence_count, 1)
        avg_words_paragraph = round(word_count / max(1, para_count), 1)

        # Fórmula Flesch-Szigriszt / Fernández-Huerta para español:
        # Flesch-Szigriszt = 206.84 - (62.3 * sílabas/palabra) - (palabras/frase)
        vowels = len(re.findall(r'[aeiouáéíóúü]', text, re.IGNORECASE))
        syllables_per_word = vowels / max(1, word_count)
        score = 206.84 - (62.3 * syllables_per_word) - avg_words_sentence
        score = max(0.0, min(100.0, round(score, 1)))

        if score >= 80:
            level = "Muy Fácil (Estilo ágil / divulgación)"
        elif score >= 65:
            level = "Fácil (Novela popular / prensa)"
        elif score >= 50:
            level = "Normal (Estándar literario)"
        elif score >= 35:
            level = "Difícil (Ensayo / académico)"
        else:
            level = "Muy Difícil (Técnico / filosófico)"

        return {
            "words": word_count,
            "characters_with_spaces": char_with_spaces,
            "characters_without_spaces": char_without_spaces,
            "paragraphs": para_count,
            "sentences": sentence_count,
            "printed_pages": printed_pages,
            "paperback_pages": paperback_pages,
            "reading_time_minutes": reading_time,
            "speaking_time_minutes": speaking_time,
            "average_words_per_sentence": avg_words_sentence,
            "average_words_per_paragraph": avg_words_paragraph,
            "readability_score": score,
            "readability_level": level
        }

    @classmethod
    def compute_word_frequency(
        cls,
        text: str,
        filter_stopwords: bool = True,
        min_length: int = 2,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Calcula la tabla de frecuencia de palabras:
        - Soporta exclusión opcional de stop-words para detectar redundancias léxicas.
        - Devuelve lista ordenada de diccionario con rank, palabra, apariciones y porcentaje.
        """
        if not text or not text.strip():
            return []

        raw_words = re.findall(r"\b[\w'-]+\b", text.lower(), re.UNICODE)
        total_valid_words = len(raw_words)
        if total_valid_words == 0:
            return []

        filtered_words = []
        for w in raw_words:
            if len(w) < min_length:
                continue
            if filter_stopwords and w in ALL_STOP_WORDS:
                continue
            filtered_words.append(w)

        counts = Counter(filtered_words).most_common(max_results)

        results = []
        for rank, (word, count) in enumerate(counts, start=1):
            pct = round((count / total_valid_words) * 100.0, 2)
            results.append({
                "rank": rank,
                "word": word,
                "count": count,
                "percentage": pct
            })

        return results

    @classmethod
    def analyze_project(cls, project: EscritorioProject, filter_stopwords: bool = True) -> Dict[str, Any]:
        """
        Realiza un análisis integral del manuscrito completo del proyecto,
        recorriendo todos los documentos de la carpeta Borrador (Draft).
        """
        all_text_parts = []
        doc_count = 0

        draft = project.get_draft_folder()

        def collect(node: BinderItem):
            nonlocal doc_count
            if node.item_type.lower() == "text":
                doc_count += 1
                rtf = node.read_content_rtf()
                plain = RTFEngine.rtf_to_plain_text(rtf)
                all_text_parts.append(plain)
            for child in node.children:
                collect(child)

        if draft:
            collect(draft)

        full_text = "\n\n".join(all_text_parts)
        stats = cls.analyze_text(full_text)
        stats["documents_analyzed"] = doc_count
        stats["word_frequency"] = cls.compute_word_frequency(full_text, filter_stopwords=filter_stopwords)

        return stats
