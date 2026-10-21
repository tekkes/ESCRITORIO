"""
Character Name Generator para Escritorio
Generador de nombres de personajes por nacionalidad, época y arquetipo para novelistas y guionistas.
"""

import random
from typing import List, Dict

NAMES_DATABASE: Dict[str, Dict[str, List[str]]] = {
    "es": {
        "first_male": ["Mateo", "Lucas", "Alejandro", "Gabriel", "Rodrigo", "Javier", "Álvaro", "Hugo"],
        "first_female": ["Isabel", "Valeria", "Elena", "Lucía", "Carmen", "Beatriz", "Sofía", "Clara"],
        "last": ["García", "Rodríguez", "Navarro", "Serrano", "Mendoza", "Castillo", "Vargas", "Morales"]
    },
    "en": {
        "first_male": ["Arthur", "Edward", "Julian", "Thomas", "Oliver", "Ethan", "William", "Henry"],
        "first_female": ["Eleanor", "Charlotte", "Margaret", "Victoria", "Evelyn", "Alice", "Grace", "Rose"],
        "last": ["Blackwood", "Sterling", "Holloway", "Sinclair", "Vance", "Mercer", "Ashford", "Kingsley"]
    },
    "fantasy": {
        "first_male": ["Eldrin", "Thorne", "Valen", "Kaelen", "Morrigan", "Baelor", "Zephyr", "Dorian"],
        "first_female": ["Lyra", "Sylvara", "Astraea", "Elysia", "Seraphina", "Isolde", "Vespera", "Morwen"],
        "last": ["Stormcaller", "Shadowmend", "Starfall", "Ironwood", "Frostborne", "Nightshade", "Ravencrest"]
    }
}

class CharacterNameGenerator:
    """Generador aleatorio de nombres para personajes."""

    @staticmethod
    def generate(culture: str = "es", gender: str = "female") -> str:
        data = NAMES_DATABASE.get(culture, NAMES_DATABASE["es"])
        first_list = data["first_female"] if gender.lower() == "female" else data["first_male"]
        first_name = random.choice(first_list)
        last_name = random.choice(data["last"])
        return f"{first_name} {last_name}"
