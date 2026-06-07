import unittest
from decimal import Decimal
from tempfile import TemporaryDirectory
from pathlib import Path

from sum_csv_columns import read_csv_totals


class ReadCsvTotalsTests(unittest.TestCase):
    def test_sums_multiple_numeric_columns(self):
        with TemporaryDirectory() as tmpdir:
            csv_file = Path(tmpdir) / "numbers.csv"
            csv_file.write_text(
                "apples,oranges,pears\n"
                "1,2,3\n"
                "4.5,5,6\n"
                "0.5,8,9\n",
                encoding="utf-8",
            )

            self.assertEqual(
                read_csv_totals(csv_file),
                {
                    "apples": Decimal("6.0"),
                    "oranges": Decimal("15"),
                    "pears": Decimal("18"),
                },
            )

    def test_ignores_text_columns(self):
        with TemporaryDirectory() as tmpdir:
            csv_file = Path(tmpdir) / "mixed.csv"
            csv_file.write_text(
                "name,score,bonus\n"
                "Alice,10,1.5\n"
                "Bob,20,2.5\n"
                "Cara,30,3\n",
                encoding="utf-8",
            )

            self.assertEqual(
                read_csv_totals(csv_file),
                {
                    "score": Decimal("60"),
                    "bonus": Decimal("7.0"),
                },
            )


if __name__ == "__main__":
    unittest.main()
