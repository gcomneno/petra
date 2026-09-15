"""Tests for the structural algebra (meet, join, contains)."""

from __future__ import annotations

from petra import parse_shape, serialize_shape
from resolver import (
    contains,
    int_to_shape,
    join,
    meet,
    structural_overlap,
)


def text(shape) -> str:
    return serialize_shape(shape)


# ---------------------------------------------------------------------------
# contains
# ---------------------------------------------------------------------------


def test_leaf_contained_in_everything() -> None:
    assert contains(parse_shape("1"), parse_shape("1"))
    assert contains(parse_shape("1"), parse_shape("C(r0^1)"))
    assert contains(parse_shape("1"), parse_shape("C(r0^C(r0^1))"))


def test_container_not_contained_in_leaf() -> None:
    assert not contains(parse_shape("C(r0^1)"), parse_shape("1"))


def test_identity_containment() -> None:
    s = parse_shape("C(r0^C(r0^1),r1^1)")
    assert contains(s, s)


def test_containment_simple_extension() -> None:
    a = parse_shape("C(r0^1)")
    b = parse_shape("C(r0^1,r1^1)")
    assert contains(a, b)
    assert not contains(b, a)


def test_containment_recursive() -> None:
    a = parse_shape("C(r0^C(r0^1))")
    b = parse_shape("C(r0^C(r0^C(r0^1)))")
    assert contains(a, b)
    assert not contains(b, a)


def test_containment_shorter_arity() -> None:
    a = parse_shape("C(r0^1,r1^1)")
    b = parse_shape("C(r0^1)")
    assert not contains(a, b)


# ---------------------------------------------------------------------------
# meet
# ---------------------------------------------------------------------------


def test_meet_identity() -> None:
    a = parse_shape("C(r0^1,r1^1)")
    assert meet(a, a) == a


def test_meet_with_leaf() -> None:
    assert meet(parse_shape("1"), parse_shape("C(r0^1)")) == parse_shape("1")


def test_meet_returns_smaller_when_contained() -> None:
    a = parse_shape("C(r0^1)")
    b = parse_shape("C(r0^1,r1^1)")
    assert meet(a, b) == a
    assert meet(b, a) == a


def test_meet_symmetric() -> None:
    a = parse_shape("C(r0^C(r0^1),r1^1)")
    b = parse_shape("C(r0^1,r1^C(r0^1))")
    assert meet(a, b) == meet(b, a)


def test_meet_12_18() -> None:
    # 12 = 2^2*3 -> C(r0^C(r0^1), r1^1)
    # 18 = 2*3^2 -> C(r0^1, r1^C(r0^1))
    # Meet should be C(r0^1, r1^1) (shape of 6)
    a = int_to_shape(12)
    b = int_to_shape(18)
    assert meet(a, b) == parse_shape("C(r0^1,r1^1)")


def test_meet_12_60() -> None:
    # 12 shape is contained in 60 shape
    a = int_to_shape(12)
    b = int_to_shape(60)
    assert meet(a, b) == a


def test_meet_same_shape_different_numbers() -> None:
    # 12 and 20 have the same shape; meet should be that shape
    a = int_to_shape(12)
    b = int_to_shape(20)
    assert a == b
    assert meet(a, b) == a


# ---------------------------------------------------------------------------
# join
# ---------------------------------------------------------------------------


def test_join_identity() -> None:
    a = parse_shape("C(r0^1,r1^1)")
    assert join(a, a) == a


def test_join_with_leaf() -> None:
    a = parse_shape("C(r0^1)")
    assert join(parse_shape("1"), a) == a
    assert join(a, parse_shape("1")) == a


def test_join_returns_larger_when_contains() -> None:
    a = parse_shape("C(r0^1)")
    b = parse_shape("C(r0^1,r1^1)")
    assert join(a, b) == b
    assert join(b, a) == b


def test_join_symmetric() -> None:
    a = parse_shape("C(r0^C(r0^1),r1^1)")
    b = parse_shape("C(r0^1,r1^C(r0^1))")
    assert join(a, b) == join(b, a)


def test_join_12_18() -> None:
    # 12 and 18: join should be C(r0^C(r0^1), r1^C(r0^1))
    a = int_to_shape(12)
    b = int_to_shape(18)
    assert join(a, b) == parse_shape("C(r0^C(r0^1),r1^C(r0^1))")


# ---------------------------------------------------------------------------
# structural_overlap
# ---------------------------------------------------------------------------


def test_overlap_identity_is_one() -> None:
    a = parse_shape("C(r0^1,r1^1)")
    assert structural_overlap(a, a) == 1.0


def test_overlap_with_leaf_is_small() -> None:
    a = parse_shape("C(r0^C(r0^C(r0^1)))")
    ov = structural_overlap(parse_shape("1"), a)
    assert 0.0 < ov < 0.5


def test_overlap_symmetric() -> None:
    a = int_to_shape(12)
    b = int_to_shape(18)
    assert structural_overlap(a, b) == structural_overlap(b, a)


def test_overlap_monotone() -> None:
    # 12 is contained in 60, so overlap(12, 60) should be higher than
    # overlap(12, 18) which only shares a shape prefix.
    a = int_to_shape(12)
    b = int_to_shape(60)
    c = int_to_shape(18)
    assert structural_overlap(a, b) > structural_overlap(a, c)
