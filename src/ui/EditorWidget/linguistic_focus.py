"""
LinguisticFocusEngine para Escritorio
Motor de análisis estilístico y foco lingüístico para español e inglés.
Permite resaltar de forma selectiva:
- Diálogos directos (comillas latinas «...», inglesas "..." o rayas de diálogo —...—)
- Adverbios (terminaciones en -mente / -ly y diccionario)
- Adjetivos (sufijos descriptivos y léxico canónico)
- Verbos (desinencias y formas conjugadas)
- Conjunciones (coordinantes y subordinantes)
Atenuando el resto del texto para revisión ortotipográfica y estilística.
"""

import re
from enum import Enum
from typing import List, Tuple, Dict, Set, Any
from dataclasses import dataclass


class LinguisticCategory(str, Enum):
    NONE = "None"
    DIALOGUES = "Dialogues"       # Diálogos Directos
    ADVERBS = "Adverbs"           # Adverbios
    ADJECTIVES = "Adjectives"     # Adjetivos
    VERBS = "Verbs"               # Verbos
    CONJUNCTIONS = "Conjunctions" # Conjunciones


@dataclass
class HighlightSpan:
    start: int
    end: int
    category: LinguisticCategory
    token: str


class LinguisticFocusEngine:
    """Motor analizador de foco lingüístico para ES y EN."""

    # =========================================================================
    # Diccionarios y Expresiones para Español (ES)
    # =========================================================================

    ES_IRREGULAR_ADVERBS: Set[str] = {
        "muy", "bien", "mal", "casi", "siempre", "nunca", "jamás", "ya", "todavía", "aún",
        "además", "tarde", "temprano", "aprisa", "despacio", "aquí", "allí", "allá", "acá",
        "cerca", "lejos", "arriba", "abajo", "delante", "detrás", "acaso", "quizás", "quizá",
        "demasiado", "bastante", "poco", "mucho", "tanto", "cuanto", "tan", "más", "menos",
        "solo", "solamente", "apenas", "inclusive", "siquiera", "así", "claro", "cierto"
    }

    ES_CONJUNCTIONS: Set[str] = {
        "y", "e", "ni", "que", "o", "u", "pero", "mas", "sino", "porque", "pues",
        "ya que", "puesto que", "como", "si", "aunque", "bien que", "conque",
        "mientras", "luego", "así que", "por tanto", "por consiguiente", "sin embargo",
        "no obstante", "antes bien", "ora", "ya", "bien", "sea", "fuera"
    }

    ES_ADJECTIVE_SUFFIXES = re.compile(
        r"\b\w{3,}(?:oso|osa|osos|osas|ible|ibles|able|ables|ico|ica|icos|icas|"
        r"ante|antes|ente|entes|iente|ientes|ivo|iva|ivos|ivas|al|ales|ar|ares|"
        r"ento|enta|entos|entas|eño|eña|eños|eñas|ano|ana|anos|anas|dor|dora|dores|doras)\b",
        re.IGNORECASE | re.UNICODE
    )

    ES_COMMON_ADJECTIVES: Set[str] = {
        "bueno", "buena", "buenos", "buenas", "buen", "malo", "mala", "malos", "malas", "mal",
        "grande", "grandes", "gran", "pequeño", "pequeña", "pequeños", "pequeñas",
        "alto", "alta", "altos", "altas", "bajo", "baja", "bajos", "bajas",
        "nuevo", "nueva", "nuevos", "nuevas", "viejo", "vieja", "viejos", "viejas",
        "joven", "jóvenes", "anciano", "anciana", "ancianos", "ancianas",
        "largo", "larga", "largos", "largas", "corto", "corta", "cortos", "cortas",
        "ancho", "ancha", "anchos", "anchas", "estrecho", "estrecha", "estrechos", "estrechas",
        "fuerte", "fuertes", "débil", "débiles", "rápido", "rápida", "rápidos", "rápidas",
        "lento", "lenta", "lentos", "lentas", "oscuro", "oscura", "oscuros", "oscuras",
        "claro", "clara", "claros", "claras", "brillante", "brillantes", "pálido", "pálida",
        "cálido", "cálida", "frío", "fría", "fríos", "frías", "dulce", "dulces", "amargo",
        "feliz", "felices", "triste", "tristes", "hermoso", "hermosa", "bello", "bella",
        "feo", "fea", "solitario", "solitaria", "antiguo", "antigua", "moderno", "moderna"
    }

    ES_VERB_ENDINGS = re.compile(
        r"\b\w{2,}(?:ar|er|ir|ando|iendo|ado|ada|ados|adas|ido|ida|idos|idas|"
        r"aba|abas|ábamos|abais|aban|ía|ías|íamos|íais|ían|"
        r"ó|ió|aron|ieron|aste|iste|asteis|isteis|amos|emos|imos|"
        r"ará|erá|irá|arán|erán|irán|aría|erían|irían|aría|arías)\b",
        re.IGNORECASE | re.UNICODE
    )

    ES_COMMON_VERBS: Set[str] = {
        "es", "son", "era", "eran", "fue", "fueron", "sea", "sean", "siendo", "sido",
        "está", "están", "estaba", "estaban", "estuvo", "estuvieron", "esté", "estado",
        "ha", "han", "había", "habían", "hubo", "hubieron", "haya", "hayan", "habiendo",
        "tiene", "tienen", "tenía", "tenían", "tuvo", "tuvieron", "tenga", "tenido",
        "hace", "hacen", "hacía", "hacían", "hizo", "hicieron", "haga", "hecho",
        "dice", "dicen", "decía", "decían", "dijo", "dijeron", "diga", "dicho",
        "va", "van", "iba", "iban", "fue", "fueron", "vaya", "ido",
        "ve", "ven", "veía", "veían", "vio", "vieron", "vea", "visto",
        "puede", "pueden", "podía", "podían", "pudo", "pudieron", "pueda", "podido",
        "sabe", "saben", "sabía", "sabían", "supo", "supieron", "sepa", "sabido",
        "pone", "ponen", "ponía", "ponían", "puso", "pusieron", "ponga", "puesto",
        "siente", "sienten", "sentía", "sentían", "sintió", "sintieron", "sentido",
        "quiere", "quieren", "quería", "querían", "quiso", "quisieron", "querido",
        "sale", "salen", "salía", "salían", "salió", "salieron", "salido"
    }

    # Patrón de diálogos: comillas latinas «...», inglesas "..." o rayas —...—
    DIALOGUE_PATTERN = re.compile(
        r"(?:«[^»]+»|\"[^\"]+\"|“[^”]+”|—[^—\n]+(?:—|$))",
        re.UNICODE
    )

    # =========================================================================
    # Diccionarios y Expresiones para Inglés (EN)
    # =========================================================================

    EN_IRREGULAR_ADVERBS: Set[str] = {
        "very", "well", "fast", "hard", "often", "never", "always", "quite", "rather",
        "already", "soon", "late", "almost", "together", "now", "then", "here", "there",
        "far", "near", "enough", "today", "yesterday", "tomorrow", "tonight", "seldom",
        "again", "ever", "too", "also", "even", "just", "still", "yet", "perhaps", "maybe"
    }

    EN_CONJUNCTIONS: Set[str] = {
        "and", "but", "or", "nor", "for", "yet", "so", "although", "because", "since",
        "unless", "while", "whereas", "if", "whether", "as", "though", "even though",
        "provided", "after", "before", "until", "once", "that", "inasmuch", "lest"
    }

    EN_ADJECTIVE_SUFFIXES = re.compile(
        r"\b\w{3,}(?:ful|less|ous|able|ible|ic|ical|ive|ish|al|ary|ent|ant)\b",
        re.IGNORECASE | re.UNICODE
    )

    EN_COMMON_ADJECTIVES: Set[str] = {
        "good", "bad", "big", "small", "old", "young", "new", "great", "high", "low",
        "tall", "short", "long", "wide", "narrow", "thick", "thin", "dark", "light",
        "bright", "pale", "warm", "cold", "hot", "cool", "sweet", "bitter", "sour",
        "happy", "sad", "angry", "calm", "strong", "weak", "rich", "poor", "hard", "soft",
        "red", "blue", "green", "yellow", "black", "white", "gray", "quiet", "loud"
    }

    EN_COMMON_VERBS: Set[str] = {
        "is", "are", "was", "were", "am", "be", "been", "being",
        "have", "has", "had", "having", "do", "does", "did", "doing", "done",
        "say", "says", "said", "saying", "go", "goes", "went", "gone", "going",
        "get", "gets", "got", "gotten", "getting", "make", "makes", "made", "making",
        "know", "knows", "knew", "known", "knowing", "think", "thinks", "thought", "thinking",
        "take", "takes", "took", "taken", "taking", "see", "sees", "saw", "seen", "seeing",
        "come", "comes", "came", "coming", "look", "looks", "looked", "looking",
        "want", "wants", "wanted", "wanting", "give", "gives", "gave", "given", "giving",
        "tell", "tells", "told", "telling", "ask", "asks", "asked", "asking",
        "work", "works", "worked", "working", "seem", "seems", "seemed", "seeming",
        "feel", "feels", "felt", "feeling", "try", "tries", "tried", "trying",
        "leave", "leaves", "left", "leaving", "call", "calls", "called", "calling"
    }

    def __init__(self, language: str = "es"):
        self.language = language.lower() if language.lower() in ("es", "en") else "es"
        self.active_category: LinguisticCategory = LinguisticCategory.NONE

    def set_category(self, cat: LinguisticCategory):
        self.active_category = cat

    def analyze(self, text: Optional[str] = None, category: Optional[Any] = None, language: str = "es") -> List[HighlightSpan]:
        """
        Analiza el texto y devuelve los tramos (spans) resaltados según la categoría activa.
        Soporta invocación como método de instancia o como llamada estática:
        - engine.analyze(text, category)
        - LinguisticFocusEngine.analyze(text, category, language="es")
        """
        if not isinstance(self, LinguisticFocusEngine):
            # Invocado como función estática / método no ligado
            actual_text = str(self) if self is not None else ""
            actual_cat = text
            actual_lang = category if isinstance(category, str) else language
            engine = LinguisticFocusEngine(language=actual_lang)
            return engine.analyze(actual_text, actual_cat)

        cat = category or self.active_category
        if isinstance(cat, str):
            for c in LinguisticCategory:
                if c.value.lower() == cat.lower() or c.name.lower() == cat.lower():
                    cat = c
                    break

        if cat == LinguisticCategory.NONE or not text:
            return []

        if cat == LinguisticCategory.DIALOGUES:
            return self._analyze_dialogues(text)
        elif cat == LinguisticCategory.ADVERBS:
            return self._analyze_adverbs(text)
        elif cat == LinguisticCategory.ADJECTIVES:
            return self._analyze_adjectives(text)
        elif cat == LinguisticCategory.VERBS:
            return self._analyze_verbs(text)
        elif cat == LinguisticCategory.CONJUNCTIONS:
            return self._analyze_conjunctions(text)

        return []

    def _analyze_dialogues(self, text: str) -> List[HighlightSpan]:
        spans: List[HighlightSpan] = []
        for m in self.DIALOGUE_PATTERN.finditer(text):
            spans.append(HighlightSpan(
                start=m.start(),
                end=m.end(),
                category=LinguisticCategory.DIALOGUES,
                token=m.group(0)
            ))
        return spans

    def _analyze_adverbs(self, text: str) -> List[HighlightSpan]:
        spans: List[HighlightSpan] = []
        word_pattern = re.compile(r"\b[\wáéíóúüñ'-]+\b", re.IGNORECASE | re.UNICODE)

        for m in word_pattern.finditer(text):
            word = m.group(0)
            word_lower = word.lower()

            is_adverb = False
            if self.language == "es":
                if word_lower.endswith("mente") and len(word_lower) > 6:
                    is_adverb = True
                elif word_lower in self.ES_IRREGULAR_ADVERBS:
                    is_adverb = True
            else:  # en
                if word_lower.endswith("ly") and len(word_lower) > 3 and not word_lower.endswith("friendly"):
                    is_adverb = True
                elif word_lower in self.EN_IRREGULAR_ADVERBS:
                    is_adverb = True

            if is_adverb:
                spans.append(HighlightSpan(
                    start=m.start(),
                    end=m.end(),
                    category=LinguisticCategory.ADVERBS,
                    token=word
                ))
        return spans

    def _analyze_adjectives(self, text: str) -> List[HighlightSpan]:
        spans: List[HighlightSpan] = []
        word_pattern = re.compile(r"\b[\wáéíóúüñ'-]+\b", re.IGNORECASE | re.UNICODE)

        for m in word_pattern.finditer(text):
            word = m.group(0)
            word_lower = word.lower()

            is_adj = False
            if self.language == "es":
                if word_lower in self.ES_COMMON_ADJECTIVES:
                    is_adj = True
                elif self.ES_ADJECTIVE_SUFFIXES.match(word_lower):
                    is_adj = True
            else:  # en
                if word_lower in self.EN_COMMON_ADJECTIVES:
                    is_adj = True
                elif self.EN_ADJECTIVE_SUFFIXES.match(word_lower):
                    is_adj = True

            if is_adj:
                spans.append(HighlightSpan(
                    start=m.start(),
                    end=m.end(),
                    category=LinguisticCategory.ADJECTIVES,
                    token=word
                ))
        return spans

    def _analyze_verbs(self, text: str) -> List[HighlightSpan]:
        spans: List[HighlightSpan] = []
        word_pattern = re.compile(r"\b[\wáéíóúüñ'-]+\b", re.IGNORECASE | re.UNICODE)

        for m in word_pattern.finditer(text):
            word = m.group(0)
            word_lower = word.lower()

            is_verb = False
            if self.language == "es":
                if word_lower in self.ES_COMMON_VERBS:
                    is_verb = True
                elif self.ES_VERB_ENDINGS.match(word_lower) and len(word_lower) >= 4:
                    is_verb = True
            else:  # en
                if word_lower in self.EN_COMMON_VERBS:
                    is_verb = True
                elif (word_lower.endswith("ed") or word_lower.endswith("ing") or word_lower.endswith("es")) and len(word_lower) >= 4:
                    is_verb = True

            if is_verb:
                spans.append(HighlightSpan(
                    start=m.start(),
                    end=m.end(),
                    category=LinguisticCategory.VERBS,
                    token=word
                ))
        return spans

    def _analyze_conjunctions(self, text: str) -> List[HighlightSpan]:
        spans: List[HighlightSpan] = []
        word_pattern = re.compile(r"\b[\wáéíóúüñ'-]+\b", re.IGNORECASE | re.UNICODE)

        for m in word_pattern.finditer(text):
            word = m.group(0)
            word_lower = word.lower()

            is_conj = False
            if self.language == "es":
                if word_lower in self.ES_CONJUNCTIONS:
                    is_conj = True
            else:  # en
                if word_lower in self.EN_CONJUNCTIONS:
                    is_conj = True

            if is_conj:
                spans.append(HighlightSpan(
                    start=m.start(),
                    end=m.end(),
                    category=LinguisticCategory.CONJUNCTIONS,
                    token=word
                ))
        return spans
