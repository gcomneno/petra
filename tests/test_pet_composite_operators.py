from __future__ import annotations

from collections import Counter

from pet.core import prime_factorization, shape_signature_dict


PET_UNIT = 1
PET_UNIT_SIGNATURE: list = []


def factor_counter(n: int) -> Counter[int]:
    if n == PET_UNIT:
        return Counter()

    factors: Counter[int] = Counter()
    for prime, exponent in prime_factorization(n):
        factors[int(prime)] += int(exponent)

    return factors


def value_from_factors(factors: Counter[int]) -> int:
    value = PET_UNIT
    for prime, exponent in factors.items():
        value *= prime ** exponent
    return value


def pet_data(n: int) -> dict:
    if n == PET_UNIT:
        return {
            "generator": PET_UNIT,
            "signature": PET_UNIT_SIGNATURE,
        }

    data = shape_signature_dict(n)
    return {
        "generator": data["generator"],
        "signature": data["signature"],
    }


def pet_merge(a: int, b: int) -> int:
    """PET-MERGE / somma PET: overlay two PET structures by adding multiplicities."""
    return value_from_factors(factor_counter(a) + factor_counter(b))


def pet_unmerge(a: int, b: int) -> int | None:
    """PET-UNMERGE / sottrazione PET: subtract multiplicities when structurally contained."""
    result = Counter(factor_counter(a))

    for prime, exponent in factor_counter(b).items():
        if result[prime] < exponent:
            return None

        result[prime] -= exponent
        if result[prime] == 0:
            del result[prime]

    return value_from_factors(result)


def test_pet_unit_is_identity_for_merge_and_self_unmerge() -> None:
    assert pet_data(PET_UNIT) == {
        "generator": PET_UNIT,
        "signature": PET_UNIT_SIGNATURE,
    }

    for generator in [PET_UNIT, 2, 6, 30, 210, 2310]:
        assert pet_merge(PET_UNIT, generator) == generator
        assert pet_merge(generator, PET_UNIT) == generator
        assert pet_unmerge(generator, generator) == PET_UNIT


def test_pet_unmerge_is_undefined_when_rhs_is_not_contained() -> None:
    assert pet_unmerge(PET_UNIT, 2) is None
    assert pet_unmerge(2, 6) is None
    assert pet_unmerge(6, 30) is None


def test_flat_generator_unmerge_reduces_pet_mass() -> None:
    cases = [
        (6, 2, 2, [[]]),
        (30, 2, 6, [[], []]),
        (30, 6, 2, [[]]),
        (210, 30, 2, [[]]),
        (2310, 30, 6, [[], []]),
        (2310, 210, 2, [[]]),
    ]

    for left, right, expected_generator, expected_signature in cases:
        result = pet_unmerge(left, right)
        assert result is not None

        result_data = pet_data(result)
        assert result_data["generator"] == expected_generator
        assert result_data["signature"] == expected_signature


def test_flat_generator_merge_raises_overlapping_leaves() -> None:
    cases = [
        (2, 2, 4, [[[]]]),
        (6, 6, 36, [[[]], [[]]]),
        (30, 30, 900, [[[]], [[]], [[]]]),
        (30, 6, 180, [[], [[]], [[]]]),
        (210, 30, 6300, [[], [[]], [[]], [[]]]),
    ]

    for left, right, expected_generator, expected_signature in cases:
        result = pet_merge(left, right)
        result_data = pet_data(result)

        assert result_data["generator"] == expected_generator
        assert result_data["signature"] == expected_signature


def test_composite_operators_work_on_canonical_generators_not_raw_values() -> None:
    left = pet_data(30030)["generator"]
    right = pet_data(55)["generator"]

    assert left == 30030
    assert right == 6

    unmerged = pet_unmerge(left, right)
    assert unmerged == 5005

    unmerged_data = pet_data(unmerged)
    assert unmerged_data["generator"] == 210
    assert unmerged_data["signature"] == [[], [], [], []]

    merged = pet_merge(left, right)
    merged_data = pet_data(merged)
    assert merged_data["generator"] == 180180
    assert merged_data["signature"] == [[], [], [], [], [[]], [[]]]
