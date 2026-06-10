import unittest

from roman_numerals import roman_to_int


class RomanToIntTests(unittest.TestCase):
    def test_basic_numerals(self):
        self.assertEqual(roman_to_int("I"), 1)
        self.assertEqual(roman_to_int("III"), 3)
        self.assertEqual(roman_to_int("V"), 5)

    def test_subtractive_pairs(self):
        self.assertEqual(roman_to_int("IV"), 4)
        self.assertEqual(roman_to_int("IX"), 9)
        self.assertEqual(roman_to_int("XL"), 40)
        self.assertEqual(roman_to_int("CM"), 900)

    def test_long_combined_numeral(self):
        self.assertEqual(roman_to_int("MCMXCIV"), 1994)


if __name__ == "__main__":
    unittest.main()
