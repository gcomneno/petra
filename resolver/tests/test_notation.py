"""Tests for the mother notation."""

from __future__ import annotations

from petra import parse_shape
from resolver import int_to_shape
from resolver.notation import to_mother_notation


def test_leaf_is_mother_alone() -> None:
    assert to_mother_notation(parse_shape("1")) == "○"


def test_single_leaf_term_is_mother_with_a() -> None:
    assert to_mother_notation(parse_shape("C(r0^1)")) == "○^A"


def test_two_leaf_terms_are_siblings() -> None:
    assert to_mother_notation(parse_shape("C(r0^1,r1^1)")) == "○^A × B"


def test_one_level_nesting() -> None:
    assert to_mother_notation(parse_shape("C(r0^C(r0^1))")) == "○^A^A"


def test_nested_and_flat_sibling() -> None:
    assert (
        to_mother_notation(parse_shape("C(r0^C(r0^1),r1^1)"))
        == "○^A^A × B"
    )


def test_flat_first_nested_second() -> None:
    assert (
        to_mother_notation(parse_shape("C(r0^1,r1^C(r0^1))"))
        == "○^A × B^A"
    )


def test_three_siblings() -> None:
    assert (
        to_mother_notation(parse_shape("C(r0^1,r1^1,r2^1)"))
        == "○^A × B × C"
    )


def test_shape_of_small_numbers() -> None:
    # a few fixed points of the notation on shape(n)
    assert to_mother_notation(int_to_shape(2)) == "○^A"
    assert to_mother_notation(int_to_shape(4)) == "○^A^A"
    assert to_mother_notation(int_to_shape(6)) == "○^A × B"
    assert to_mother_notation(int_to_shape(12)) == "○^A^A × B"
    assert to_mother_notation(int_to_shape(30)) == "○^A × B × C"
