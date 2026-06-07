import unittest

from sorting import bubble_sort, quick_sort, sort


class TestSortingAlgorithms(unittest.TestCase):
    def setUp(self):
        self.samples = [
            [],
            [1],
            [3, 2, 1],
            [5, -1, 3, 3, 0, -10],
            [9, 8, 7, 6, 5],
        ]

    def test_bubble_sort_sorts_ascending(self):
        for sample in self.samples:
            with self.subTest(sample=sample):
                self.assertEqual(bubble_sort(sample), sorted(sample))

    def test_quick_sort_sorts_ascending(self):
        for sample in self.samples:
            with self.subTest(sample=sample):
                self.assertEqual(quick_sort(sample), sorted(sample))

    def test_sort_dispatcher_uses_named_algorithms(self):
        sample = [4, 1, 3, 2]
        self.assertEqual(sort(sample, "bubble"), [1, 2, 3, 4])
        self.assertEqual(sort(sample, "quick"), [1, 2, 3, 4])

    def test_sort_dispatcher_rejects_unknown_algorithm(self):
        with self.assertRaises(ValueError):
            sort([1, 2], "merge")

    def test_sorting_does_not_mutate_input(self):
        sample = [3, 1, 2]
        bubble_sort(sample)
        quick_sort(sample)
        self.assertEqual(sample, [3, 1, 2])


if __name__ == "__main__":
    unittest.main()
