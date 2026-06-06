import unittest

from prime import is_prime


class TestIsPrime(unittest.TestCase):
    def test_numbers_less_than_two_are_not_prime(self):
        self.assertFalse(is_prime(-5))
        self.assertFalse(is_prime(0))
        self.assertFalse(is_prime(1))

    def test_prime_numbers(self):
        self.assertTrue(is_prime(2))
        self.assertTrue(is_prime(3))
        self.assertTrue(is_prime(17))

    def test_composite_numbers(self):
        self.assertFalse(is_prime(4))
        self.assertFalse(is_prime(9))
        self.assertFalse(is_prime(21))


if __name__ == "__main__":
    unittest.main()
