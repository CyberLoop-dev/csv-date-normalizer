import unittest
from main import normalize_value

class DateNormalizerTests(unittest.TestCase):
    def test_normalizes_date(self):
        self.assertEqual(normalize_value("19/11/2026", "%d/%m/%Y", "%Y-%m-%d"), "2026-11-19")
    def test_keeps_empty_value(self):
        self.assertEqual(normalize_value("", "%d/%m/%Y", "%Y-%m-%d"), "")

if __name__ == "__main__":
    unittest.main()
