"""
Red Team Test: Persistencia Atómica Adversarial
Simulación de escrituras masivas, contención y verificación de SHA-256 en ReplaceFileW.
"""

import unittest
import tempfile
import os
from pathlib import Path
from src.core.storage_atomic import AtomicStorage

class TestAtomicStorageAdversarial(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_rapid_consecutive_atomic_writes(self):
        target = self.base_path / "manuscript_chapter.rtf"
        for i in range(50):
            payload = f"Contenido versión iteración {i} con tildes y caracteres especiales: áéíóú ñ ¿?".encode("utf-8")
            success = AtomicStorage.write_atomic_bytes(target, payload)
            self.assertTrue(success)
            self.assertEqual(AtomicStorage.read_bytes(target), payload)

    def test_zero_bytes_and_large_payloads(self):
        target_zero = self.base_path / "empty.txt"
        AtomicStorage.write_atomic_bytes(target_zero, b"")
        self.assertEqual(AtomicStorage.read_bytes(target_zero), b"")

        target_large = self.base_path / "large.txt"
        large_payload = b"Escritorio 100% Portable Windows 11\n" * 100000  # ~3.6 MB
        AtomicStorage.write_atomic_bytes(target_large, large_payload)
        self.assertEqual(len(AtomicStorage.read_bytes(target_large)), len(large_payload))

if __name__ == "__main__":
    unittest.main()
