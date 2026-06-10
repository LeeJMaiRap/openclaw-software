"""Utilities for converting Roman numerals."""

ROMAN_VALUES = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}

SUBTRACTIVE_PAIRS = {
    "IV": 4,
    "IX": 9,
    "XL": 40,
    "XC": 90,
    "CD": 400,
    "CM": 900,
}


def roman_to_int(roman: str) -> int:
    """Convert a Roman numeral string to an integer."""
    if not roman:
        raise ValueError("Roman numeral must not be empty")

    total = 0
    index = 0

    while index < len(roman):
        current = roman[index]
        if current not in ROMAN_VALUES:
            raise ValueError(f"Invalid Roman numeral character: {current}")

        pair = roman[index : index + 2]
        if pair in SUBTRACTIVE_PAIRS:
            total += SUBTRACTIVE_PAIRS[pair]
            index += 2
            continue

        if index + 1 < len(roman):
            next_char = roman[index + 1]
            if next_char not in ROMAN_VALUES:
                raise ValueError(f"Invalid Roman numeral character: {next_char}")
            if ROMAN_VALUES[current] < ROMAN_VALUES[next_char]:
                raise ValueError(f"Invalid subtractive pair: {pair}")

        total += ROMAN_VALUES[current]
        index += 1

    return total
