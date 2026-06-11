def is_prime(n):
    if n < 2:
        return False

    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False

    return True


def count_primes(numbers):
    """Đếm số lượng số nguyên tố trong list đầu vào."""
    return sum(1 for number in numbers if is_prime(number))
