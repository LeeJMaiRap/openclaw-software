def factorial(n: int) -> int:
    """Return n! for a non-negative integer n using recursion."""
    if n < 0:
        raise ValueError("factorial is only defined for non-negative integers")
    if n in (0, 1):
        return 1
    return n * factorial(n - 1)
