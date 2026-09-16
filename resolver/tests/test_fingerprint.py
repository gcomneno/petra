"""Tests for the structural fingerprint layer."""

from __future__ import annotations

import pytest
from petra import parse_shape

from resolver import (
    fingerprint_cumulative,
    fingerprint_window,
    transition,
)

# ---------------------------------------------------------------------------
# transition
# ---------------------------------------------------------------------------


def test_transition_same_node_count_is_stable() -> None:
    a = parse_shape("C(r0^1)")
    b = parse_shape("C(r0^1,r1^1)")
    # 3 -> 5: expansion
    assert transition(a, b) == "exp"


def test_transition_shrink_is_reduction() -> None:
    a = parse_shape("C(r0^1,r1^1)")  # 5 nodes
    b = parse_shape("C(r0^1)")       # 3 nodes
    assert transition(a, b) == "red"


def test_transition_identical_shapes_is_stable() -> None:
    s = parse_shape("C(r0^C(r0^1))")
    assert transition(s, s) == "stab"


# ---------------------------------------------------------------------------
# fingerprint_window — basic shape
# ---------------------------------------------------------------------------


def test_fingerprint_returns_three_percentages_summing_to_100() -> None:
    red, exp, stab = fingerprint_window(2, 1, 20)
    assert abs(red + exp + stab - 100.0) < 0.01


def test_fingerprint_window_too_small_raises() -> None:
    with pytest.raises(ValueError):
        fingerprint_window(2, 5, 5)  # zero transitions


def test_fingerprint_window_of_one_transition() -> None:
    red, exp, stab = fingerprint_window(2, 1, 2)
    # exactly one transition
    assert (red, exp, stab) in {(100.0, 0.0, 0.0), (0.0, 100.0, 0.0), (0.0, 0.0, 100.0)}


# ---------------------------------------------------------------------------
# fingerprint_cumulative — equivalence with window(1, N)
# ---------------------------------------------------------------------------


def test_cumulative_equals_window_from_one() -> None:
    assert fingerprint_cumulative(2, 50) == fingerprint_window(2, 1, 50)
    assert fingerprint_cumulative(12, 40) == fingerprint_window(12, 1, 40)


def test_shape_of_power_matches_int_to_shape() -> None:
    """Internal consistency: shape_of_power(12, 3) == int_to_shape(12**3)."""

    from resolver import int_to_shape
    from resolver.fingerprint import _shape_of_power

    for base, n in [(2, 5), (12, 3), (6, 4), (30, 2)]:
        assert _shape_of_power(base, n) == int_to_shape(base ** n)


# ---------------------------------------------------------------------------
# Duplication lemma (from the research note)
# ---------------------------------------------------------------------------


def test_duplication_lemma_singleton_equals_double() -> None:
    """{a, a} has the same fingerprint as {a} for the tested a."""

    # 4 = 2^2, 36 = 2^2*3^2  (both {2})
    assert fingerprint_cumulative(4, 40) == fingerprint_cumulative(36, 40)


def test_duplication_lemma_for_a_three() -> None:
    # 8 = 2^3, 216 = 2^3*3^3  (both {3})
    assert fingerprint_cumulative(8, 40) == fingerprint_cumulative(216, 40)
