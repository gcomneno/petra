from pet.core import is_prime, is_prime_fast


def test_is_prime_fast_matches_trial_division_on_small_range() -> None:
    for n in range(0, 5000):
        assert is_prime_fast(n) is is_prime(n)


def test_is_prime_fast_handles_large_known_values() -> None:
    values = [
        1000000007,
        1000000009,
        1000000021,
        1000000033,
        1000000087,
        267496017439278,
        267496017439279,
        267496017439281,
    ]

    for n in values:
        assert is_prime_fast(n) is is_prime(n)
