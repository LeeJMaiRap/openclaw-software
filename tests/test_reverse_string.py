import unittest

from reverse_string import reverse_string


class ReverseStringTests(unittest.TestCase):
    def test_regular_string(self):
        self.assertEqual(reverse_string("hello"), "olleh")

    def test_empty_string(self):
        self.assertEqual(reverse_string(""), "")

    def test_single_character(self):
        self.assertEqual(reverse_string("a"), "a")

    def test_spaces_and_special_characters(self):
        self.assertEqual(reverse_string("a b!"), "!b a")


if __name__ == "__main__":
    unittest.main()
