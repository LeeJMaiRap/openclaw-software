"""Simple integer sorting algorithms for tests and benchmarks."""


def bubble_sort(values):
    """Return a new list with input integers sorted in ascending order."""
    result = list(values)
    n = len(result)

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        if not swapped:
            break

    return result


def quick_sort(values):
    """Return a new list with input integers sorted in ascending order."""
    result = list(values)

    if len(result) <= 1:
        return result

    pivot = result[len(result) // 2]
    smaller = [item for item in result if item < pivot]
    equal = [item for item in result if item == pivot]
    larger = [item for item in result if item > pivot]

    return quick_sort(smaller) + equal + quick_sort(larger)


SORT_ALGORITHMS = {
    "bubble": bubble_sort,
    "quick": quick_sort,
}


def sort(values, algorithm="quick"):
    """Sort integers with a named algorithm: 'bubble' or 'quick'."""
    try:
        sorter = SORT_ALGORITHMS[algorithm]
    except KeyError as exc:
        available = ", ".join(sorted(SORT_ALGORITHMS))
        raise ValueError(f"Unknown sorting algorithm: {algorithm}. Available: {available}") from exc

    return sorter(values)
