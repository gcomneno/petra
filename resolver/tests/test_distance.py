"""Tests for the Resolver distance layer."""

from __future__ import annotations

import pytest

from petra import parse_shape, serialize_shape
from resolver import (
    DistanceCache,
    DistanceError,
    int_to_shape,
    structural_distance_numbers,
    structural_distance_shapes,
)


# ---------------------------------------------------------------------------
# int_to_shape
# ---------------------------------------------------------------------------


def test_int_to_shape_one_is_leaf() -> None:
    assert int_to_shape(1) == parse_shape("1")


@pytest.mark.parametrize(
    ("n", "expected"),
    [
        (2, "C(r0^1)"),
        (3, "C(r0^1)"),
        (4, "C(r0^C(r0^1))"),
        (6, "C(r0^1,r1^1)"),
        (8, "C(r0^C(r0^1))"),
        (9, "C(r0^C(r0^1))"),
        (12, "C(r0^C(r0^1),r1^1)"),
        (30, "C(r0^1,r1^1,r2^1)"),
        (36, "C(r0^C(r0^1),r1^C(r0^1))"),
        (30030, "C(r0^1,r1^1,r2^1,r3^1,r4^1,r5^1)"),
    ],
)
def test_int_to_shape_canonical(n: int, expected: str) -> None:
    assert serialize_shape(int_to_shape(n)) == expected


def test_int_to_shape_same_shape_for_distinct_primes() -> None:
    assert int_to_shape(2) == int_to_shape(3)
    assert int_to_shape(2) == int_to_shape(5)
    assert int_to_shape(6) == int_to_shape(10)
    assert int_to_shape(6) == int_to_shape(35)


@pytest.mark.parametrize("value", [0, -1, -100])
def test_int_to_shape_rejects_non_positive(value: int) -> None:
    with pytest.raises(DistanceError):
        int_to_shape(value)


@pytest.mark.parametrize("value", [1.5, "2", None, True])
def test_int_to_shape_rejects_non_int(value: object) -> None:
    with pytest.raises(DistanceError):
        int_to_shape(value)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# structural_distance_shapes
# ---------------------------------------------------------------------------


def test_distance_shapes_identity_is_zero() -> None:
    shape = parse_shape("C(r0^1,r1^1)")
    assert structural_distance_shapes(shape, shape) == 0


def test_distance_shapes_leaf_to_singleton() -> None:
    assert structural_distance_shapes(
        parse_shape("1"), parse_shape("C(r0^1)")
    ) == 1


def test_distance_shapes_leaf_to_two_level_tower() -> None:
    assert structural_distance_shapes(
        parse_shape("1"), parse_shape("C(r0^C(r0^1))")
    ) == 2


def test_distance_shapes_is_symmetric() -> None:
    a = parse_shape("C(r0^1,r1^1)")
    b = parse_shape("C(r0^C(r0^1),r1^1)")
    assert structural_distance_shapes(a, b) == structural_distance_shapes(b, a)


# ---------------------------------------------------------------------------
# structural_distance_numbers
# ---------------------------------------------------------------------------


def test_distance_numbers_same_shape() -> None:
    assert structural_distance_numbers(6, 10) == 0
    assert structural_distance_numbers(6, 15) == 0
    assert structural_distance_numbers(2, 3) == 0


def test_distance_numbers_one_edit() -> None:
    assert structural_distance_numbers(6, 12) == 1


def test_distance_numbers_wide_gap() -> None:
    assert structural_distance_numbers(30030, 2) == 5


def test_distance_numbers_is_symmetric() -> None:
    for a, b in [(6, 12), (30030, 2), (2, 36), (12, 210)]:
        assert structural_distance_numbers(a, b) == (
            structural_distance_numbers(b, a)
        )


# ---------------------------------------------------------------------------
# DistanceCache
# ---------------------------------------------------------------------------


def test_distance_cache_identity_does_not_count_hit_or_miss() -> None:
    cache = DistanceCache()
    shape = parse_shape("C(r0^1)")
    assert cache.distance(shape, shape) == 0
    assert cache.hits == 0
    assert cache.misses == 0


def test_distance_cache_records_hits_on_repeat() -> None:
    cache = DistanceCache()
    a = parse_shape("C(r0^1)")
    b = parse_shape("C(r0^1,r1^1)")
    first = cache.distance(a, b)
    second = cache.distance(a, b)
    assert first == second
    assert cache.hits == 1
    assert cache.misses == 1
    assert cache.size == 1


def test_distance_cache_symmetry_reuses_entry() -> None:
    cache = DistanceCache()
    a = parse_shape("C(r0^1)")
    b = parse_shape("C(r0^1,r1^1)")
    cache.distance(a, b)
    cache.distance(b, a)
    assert cache.hits == 1
    assert cache.misses == 1
    assert cache.size == 1


def test_distance_cache_matches_direct_computation() -> None:
    cache = DistanceCache()
    direct = structural_distance_numbers(6, 12)
    cached = cache.distance(int_to_shape(6), int_to_shape(12))
    assert direct == cached
