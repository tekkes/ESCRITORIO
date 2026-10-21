"""
Writing Statistics para Escritorio
Métricas analíticas detalladas: palabras, caracteres, párrafos, tiempo de lectura y locución,
y fórmulas de legibilidad adaptadas al español (Fernández-Huerta / Flesch-Szigriszt).
"""

import re
from typing import Dict, Any

class WritingStatistics:
    """Calculador de estadísticas editoriales del texto."""

    @staticmethod
    def analyze_text(text: str) -> Dict[str, Any]:
        if not text.strip():
            return {
                "words": 0,
                "characters_with_spaces": 0,
                "characters_without_spaces": 0,
                "paragraphs": 0,
                "sentences": 0,
                "reading_time_minutes": 0,
                "speaking_time_minutes": 0,
                "average_words_per_sentence": 0.0,
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

        # Tiempos estimados (220 ppm lectura silenciosa, 140 ppm locución)
        reading_time = round(word_count / 220, 1)
        speaking_time = round(word_count / 140, 1)

        avg_words_sentence = round(word_count / sentence_count, 1)

        # Flesch-Szigriszt para español: 206.84 - (62.3 * silabas/palabras) - (palabras/frases)
        # Aproximación silábica simple basada en vocales
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
            "reading_time_minutes": reading_time,
            "speaking_time_minutes": speaking_time,
            "average_words_per_sentence": avg_words_sentence,
            "readability_score": score,
            "readability_level": level
        }
