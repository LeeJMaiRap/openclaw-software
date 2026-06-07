"""Benchmark bubble sort and quick sort on identical datasets."""

from random import Random
from time import perf_counter

from sorting import bubble_sort, quick_sort


DATA_SIZES = [100, 500, 1000]
RANDOM_SEED = 20260607
SORTERS = [
    ("Bubble sort", bubble_sort),
    ("Quick sort", quick_sort),
]


def build_dataset(size, seed=RANDOM_SEED):
    """Create a deterministic integer dataset for a given size."""
    rng = Random(seed + size)
    return [rng.randint(-10_000, 10_000) for _ in range(size)]


def benchmark_sorters(data_sizes=DATA_SIZES):
    """Run benchmarks and validate each sorted result before recording time."""
    rows = []

    for size in data_sizes:
        dataset = build_dataset(size)
        expected = sorted(dataset)

        for name, sorter in SORTERS:
            started_at = perf_counter()
            result = sorter(dataset)
            elapsed_ms = (perf_counter() - started_at) * 1000

            if result != expected:
                raise AssertionError(f"{name} produced invalid sorted result for size {size}")

            rows.append(
                {
                    "size": size,
                    "algorithm": name,
                    "elapsed_ms": elapsed_ms,
                    "valid": True,
                }
            )

    return rows


def print_results(rows):
    """Print benchmark rows in Vietnamese."""
    print("Kết quả benchmark sắp xếp")
    print("Kích thước | Thuật toán | Thời gian (ms) | Hợp lệ")
    print("-" * 55)
    for row in rows:
        valid_text = "có" if row["valid"] else "không"
        print(
            f"{row['size']:>10} | {row['algorithm']:<11} | "
            f"{row['elapsed_ms']:>14.3f} | {valid_text}"
        )


def main():
    print_results(benchmark_sorters())


if __name__ == "__main__":
    main()
