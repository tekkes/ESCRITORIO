"""
Character Name Generator para Escritorio.
Generador de nombres de personajes por cultura, época y arquetipo para novelistas y guionistas:
- Bases de datos integradas para:
  * Español (es)
  * Inglés (en)
  * Francés (fr)
  * Alemán (de)
  * Italiano (it)
  * Japonés (ja)
  * Fantasía (fantasy)
  * Mitología (mythology)
- Filtros avanzados:
  * Género (Masculino, Femenino, Cualquiera)
  * Filtro por letra inicial (Starts-with)
  * Aliteración (misma letra inicial para nombre y apellido, estilo cómic/literario clásico)
  * Títulos honoríficos / de profesión opcionales (Don/Doña, Lord/Lady, Dr., Capitán)
  * Generación en lote (Batch Generation).
"""

import random
from typing import List, Dict, Optional, Any


NAMES_DATABASE: Dict[str, Dict[str, List[str]]] = {
    "es": {
        "first_male": [
            "Mateo", "Lucas", "Alejandro", "Gabriel", "Rodrigo", "Javier", "Álvaro", "Hugo",
            "Santiago", "Diego", "Manuel", "Ignacio", "Fernando", "Gonzalo", "Tomás", "Emilio"
        ],
        "first_female": [
            "Isabel", "Valeria", "Elena", "Lucía", "Carmen", "Beatriz", "Sofía", "Clara",
            "Inés", "Teresa", "Catalina", "Adriana", "Leonor", "Marina", "Paula", "Daniela"
        ],
        "last": [
            "García", "Rodríguez", "Navarro", "Serrano", "Mendoza", "Castillo", "Vargas", "Morales",
            "Alonso", "Iriarte", "Bermúdez", "Cordero", "Salazar", "Montes", "Herrera", "Paredes",
            "Jiménez", "Juárez", "Fernández", "Flores", "Díaz", "Domínguez", "López", "Lozano",
            "Torres", "Trujillo", "Espinosa", "Escobar", "Hidalgo", "Hernández", "Vega", "Cruz"
        ],
        "titles": ["Don", "Doña", "Capitán", "Doctor", "Profesora", "Señor", "Marqués de"]
    },
    "en": {
        "first_male": [
            "Arthur", "Edward", "Julian", "Thomas", "Oliver", "Ethan", "William", "Henry",
            "Sebastian", "Alexander", "Charles", "Benjamin", "George", "James", "Victor", "Lucas"
        ],
        "first_female": [
            "Eleanor", "Charlotte", "Margaret", "Victoria", "Evelyn", "Alice", "Grace", "Rose",
            "Beatrice", "Penelope", "Gwendolyn", "Clara", "Florence", "Vivian", "Amelia", "Diana"
        ],
        "last": [
            "Blackwood", "Sterling", "Holloway", "Sinclair", "Vance", "Mercer", "Ashford", "Kingsley",
            "Waverly", "Pennington", "Hawthorne", "Kensington", "Fairfax", "Evergreen", "Cross", "Fletcher"
        ],
        "titles": ["Lord", "Lady", "Sir", "Dr.", "Professor", "Captain", "Baron"]
    },
    "fr": {
        "first_male": [
            "Pierre", "Louis", "Henri", "Julien", "Gabriel", "Antoine", "Alexandre", "Maxime",
            "Étienne", "Laurent", "Théodore", "Bastien", "Vincent", "Émile", "Sébastien", "Raphaël"
        ],
        "first_female": [
            "Camille", "Juliette", "Éloïse", "Madeleine", "Vivienne", "Amélie", "Geneviève", "Céleste",
            "Margaux", "Solène", "Aurélie", "Delphine", "Simone", "Clémence", "Adèle", "Hélène"
        ],
        "last": [
            "Dubois", "Moreau", "Laurent", "Lefebvre", "Fontaine", "Beaumont", "Girard", "Lambert",
            "Rousseau", "Mercier", "Chevalier", "Boucher", "Garnier", "Vidal", "Perrin", "Renaud"
        ],
        "titles": ["Monsieur", "Madame", "Comte de", "Docteur", "Capitaine", "Baronne"]
    },
    "de": {
        "first_male": [
            "Lukas", "Felix", "Maximilian", "Florian", "Sebastian", "Tobias", "Niklas", "Jonas",
            "Albrecht", "Heinrich", "Wolfgang", "Friedrich", "Klaus", "Dieter", "Matthias", "Stephan"
        ],
        "first_female": [
            "Hannah", "Sophie", "Mia", "Emma", "Lena", "Katharina", "Anna", "Johanna",
            "Ingrid", "Helena", "Greta", "Marlene", "Ursula", "Astrid", "Gisela", "Klara"
        ],
        "last": [
            "Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Richter", "Hartmann", "Zimmermann",
            "Hoffmann", "Schäfer", "Vogel", "Wagner", "Becker", "Krause", "Neumann", "Köhler"
        ],
        "titles": ["Herr", "Frau", "Doktor", "Professor", "Graf von"]
    },
    "it": {
        "first_male": [
            "Matteo", "Lorenzo", "Leonardo", "Alessandro", "Marco", "Federico", "Giovanni", "Davide",
            "Giacomo", "Fabrizio", "Marcello", "Gianluigi", "Pietro", "Stefano", "Vincenzo", "Andrea"
        ],
        "first_female": [
            "Chiara", "Giulia", "Francesca", "Valentina", "Silvia", "Beatrice", "Aurora", "Elena",
            "Vittoria", "Lucia", "Alessia", "Camilla", "Giorgia", "Martina", "Bianca", "Ginevra"
        ],
        "last": [
            "Rossi", "Ferrari", "Romano", "Colombo", "Ricci", "Marino", "Greco", "Lombardi",
            "Moretti", "Conti", "De Luca", "Mancini", "Costa", "Giordano", "Rizzo", "Barbieri"
        ],
        "titles": ["Signor", "Signora", "Dottor", "Conte", "Capitano"]
    },
    "ja": {
        "first_male": [
            "Ren", "Haruto", "Sota", "Yuto", "Riku", "Kaito", "Takumi", "Daiki",
            "Kenji", "Shinji", "Kazuki", "Ryo", "Tsubasa", "Hayato", "Kota", "Akira"
        ],
        "first_female": [
            "Yui", "Hina", "Aoi", "Sakura", "Nanami", "Rin", "Mei", "Misaki",
            "Kaori", "Akane", "Yukiko", "Ayumi", "Sayuri", "Tomoko", "Midori", "Haruka"
        ],
        "last": [
            "Sato", "Suzuki", "Takahashi", "Tanaka", "Watanabe", "Ito", "Yamamoto", "Nakamura",
            "Kobayashi", "Kato", "Yoshida", "Yamada", "Sasaki", "Yamaguchi", "Saito", "Matsumoto"
        ],
        "titles": ["San", "Sensei", "Sama", "Senpai"]
    },
    "fantasy": {
        "first_male": [
            "Eldrin", "Thorne", "Valen", "Kaelen", "Morrigan", "Baelor", "Zephyr", "Dorian",
            "Aethelgard", "Theron", "Malakor", "Faelan", "Corvus", "Vaelen", "Ignis", "Rune"
        ],
        "first_female": [
            "Lyra", "Sylvara", "Astraea", "Elysia", "Seraphina", "Isolde", "Vespera", "Morwen",
            "Aveline", "Nimue", "Selene", "Brynhild", "Thalassa", "Yvaine", "Lunaria", "Freya"
        ],
        "last": [
            "Stormcaller", "Shadowmend", "Starfall", "Ironwood", "Frostborne", "Nightshade", "Ravencrest",
            "Moonwhisper", "Drakeblood", "Windstrider", "Sunforged", "Spellweaver", "Emberfall", "Silverveil"
        ],
        "titles": ["Archimago", "Custodio", "Lord", "Dama", "Caballero", "Oráculo"]
    },
    "mythology": {
        "first_male": [
            "Ares", "Hermes", "Apollo", "Perseus", "Orion", "Castor", "Jason", "Hector",
            "Achilles", "Daedalus", "Theseus", "Prometheus", "Dionysus", "Oedipus", "Aeneas", "Pollux"
        ],
        "first_female": [
            "Athena", "Selene", "Artemis", "Daphne", "Cassandra", "Thalia", "Penelope", "Andromeda",
            "Calliope", "Ariadne", "Circe", "Hestia", "Persephone", "Electra", "Helen", "Medea"
        ],
        "last": [
            "Olympius", "Titans", "Delphi", "Arcadia", "Nemea", "Parnassus", "Corinth", "Thebes",
            "Argos", "Ithaca", "Spartan", "Mycenae", "Knossos", "Athenian", "Eleusis", "Elysian"
        ],
        "titles": ["Semidiós", "Profeta", "Héroe", "Oráculo de", "Guardián de"]
    }
}


class CharacterNameGenerator:
    """Generador aleatorio de nombres para personajes literarios."""

    AVAILABLE_CULTURES = list(NAMES_DATABASE.keys())

    @classmethod
    def generate(
        cls,
        culture: str = "es",
        gender: str = "any",
        starts_with: Optional[str] = None,
        alliteration: bool = False,
        include_title: bool = False
    ) -> str:
        """
        Genera un nombre completo según los criterios especificados.
        """
        data = NAMES_DATABASE.get(culture.lower(), NAMES_DATABASE["es"])

        # Determinar lista de nombres de pila
        gender_norm = gender.lower()
        if gender_norm == "male":
            first_pool = list(data["first_male"])
        elif gender_norm == "female":
            first_pool = list(data["first_female"])
        else:
            first_pool = data["first_male"] + data["first_female"]

        # Apellidos
        last_pool = list(data["last"])

        # Si se solicita aliteración, filtrar primero para iniciales compartidas
        if alliteration and not starts_with:
            last_initials = {l[0].upper() for l in last_pool if l}
            compatible_firsts = [n for n in first_pool if n[0].upper() in last_initials]
            if compatible_firsts:
                first_pool = compatible_firsts

        # Filtro de letra inicial
        if starts_with:
            char_filter = starts_with.upper()
            filtered = [n for n in first_pool if n.upper().startswith(char_filter)]
            if filtered:
                first_pool = filtered

        first_name = random.choice(first_pool) if first_pool else "Alex"

        # Filtro de aliteración: primera letra del apellido igual a la del nombre
        if alliteration:
            target_char = first_name[0].upper()
            allit_pool = [l for l in last_pool if l.upper().startswith(target_char)]
            if allit_pool:
                last_pool = allit_pool
            else:
                all_lasts = [l for c in NAMES_DATABASE.values() for l in c.get("last", [])]
                matching = [l for l in all_lasts if l.upper().startswith(target_char)]
                if matching:
                    last_pool = matching

        last_name = random.choice(last_pool) if last_pool else "Smith"

        full_name = f"{first_name} {last_name}"

        # Título opcional
        if include_title and "titles" in data and data["titles"]:
            title = random.choice(data["titles"])
            full_name = f"{title} {full_name}"

        return full_name

    @classmethod
    def generate_batch(
        cls,
        count: int = 10,
        culture: str = "es",
        gender: str = "any",
        starts_with: Optional[str] = None,
        alliteration: bool = False,
        include_title: bool = False
    ) -> List[str]:
        """Genera una lista de N nombres candidatos."""
        names = set()
        attempts = 0
        max_attempts = count * 5

        while len(names) < count and attempts < max_attempts:
            attempts += 1
            name = cls.generate(
                culture=culture,
                gender=gender,
                starts_with=starts_with,
                alliteration=alliteration,
                include_title=include_title
            )
            names.add(name)

        return sorted(list(names))
