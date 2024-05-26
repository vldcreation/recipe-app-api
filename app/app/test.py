"""
Sample test file
"""

from django.test import SimpleTestCase

from app import calc


class CalcTests(SimpleTestCase):
    """Test module for calc.py"""

    def test_add_numbers(self):
        self.assertEqual(calc.add(1, 2), 3)
        self.assertEqual(calc.add(0, 0), 0)
        self.assertEqual(calc.add(-1, -1), -2)

    def test_subtract_numbers(self):
        self.assertEqual(calc.subtract(3, 2), 1)
        self.assertEqual(calc.subtract(-1, -1), 0)
        self.assertEqual(calc.subtract(0, 0), 0)
