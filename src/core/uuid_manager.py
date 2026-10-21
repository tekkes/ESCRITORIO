"""
UUID Manager para Escritorio
Gestión, generación y resolución de identificadores únicos para nodos del Binder y recursos.
"""

import uuid
import re

class UUIDManager:
    """Generador y validador de UUIDs para elementos del proyecto Escritorio y Scrivener 3."""

    UUID_REGEX = re.compile(r"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$")

    @staticmethod
    def generate_uuid() -> str:
        """Genera un UUID v4 en formato estándar mayúsculas (compatible con Scrivener 3 Windows/Mac)."""
        return str(uuid.uuid4()).upper()

    @staticmethod
    def generate_deterministic_uuid(namespace_seed: str, name: str) -> str:
        """Genera un UUID v5 reproducible a partir de una semilla y nombre."""
        ns = uuid.uuid5(uuid.NAMESPACE_DNS, namespace_seed)
        return str(uuid.uuid5(ns, name)).upper()

    @classmethod
    def is_valid_uuid(cls, value: str) -> bool:
        """Verifica si una cadena cumple con el formato UUID canónico."""
        if not value or not isinstance(value, str):
            return False
        return bool(cls.UUID_REGEX.match(value))

    @staticmethod
    def normalize(value: str) -> str:
        """Normaliza un UUID eliminando corchetes y forzando mayúsculas."""
        cleaned = value.strip("{} \t\r\n")
        return cleaned.upper()
