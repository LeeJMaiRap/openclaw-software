import unittest

from sorting import bubble_sort, quick_sort


class TestSortingCorrectness(unittest.TestCase):
    def setUp(self):
        self.cases = [
            ("empty", [], []),
            ("single_item", [7], [7]),
            ("already_sorted", [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
            ("reversed", [5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
            ("duplicates", [3, 1, 2, 3, 1], [1, 1, 2, 3, 3]),
        ]
        self.algorithms = [
            ("bubble_sort", bubble_sort),
            ("quick_sort", quick_sort),
        ]

    def test_sorting_algorithms_handle_typical_and_edge_cases(self):
        for algorithm_name, algorithm in self.algorithms:
            for case_name, values, expected in self.cases:
                with self.subTest(algorithm=algorithm_name, case=case_name):
                    self.assertEqual(algorithm(values), expected)


if __name__ == "__main__":
    unittest.main()
