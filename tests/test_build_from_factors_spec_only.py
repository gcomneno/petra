import pet.core as core
from pet.cli import _build_from_factors_report


def test_shape_generator_from_factorization_matches_integer_path():
    factors = [(2, 2), (3, 2), (5, 1), (7, 3)]
    target_n = 1
    for p, e in factors:
        target_n *= p ** e

    assert core.shape_generator_from_factorization(list(factors)) == core.shape_generator(target_n)


def test_build_from_factors_report_does_not_factor_target_integer(monkeypatch):
    factors = ((2, 2), (3, 2), (5, 2), (7, 2), (11, 2), (13, 2))
    target_n = 1
    for p, e in factors:
        target_n *= p ** e

    original = core.prime_factorization

    def guarded_prime_factorization(n: int):
        if n == target_n:
            raise AssertionError("target integer was factored")
        return original(n)

    monkeypatch.setattr(core, "prime_factorization", guarded_prime_factorization)

    report = _build_from_factors_report(factors)

    assert report["target_n"] == target_n
    assert report["target_generator"] == core.shape_generator_from_factorization(list(factors))
    assert report["steps"] == 11
