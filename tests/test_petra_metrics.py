"""Tests for petra.metrics.node_count."""

from __future__ import annotations

import pytest

from petra import (
    Container,
    Leaf,
    Root,
    Term,
    node_count,
    parse_shape,
)


def leaf_term(rank: int) -> Term:
    return Term(root=Root(rank), exponent=Leaf())


def test_leaf_is_one_node() -> None:
    assert node_count(Leaf()) == 1


def test_single_leaf_container_is_three_nodes() -> None:
    # Container + Term + Leaf = 3
    assert node_count(parse_shape("C(r0^1)")) == 3


def test_two_leaf_terms_is_five_nodes() -> None:
    # Container + 2 * (Term + Leaf) = 5
    assert node_count(parse_shape("C(r0^1,r1^1)")) == 5


def test_nested_container_counts_recursively() -> None:
    # C(r0^C(r0^1)):
    #   outer Container
    #   outer Term
    #   inner Container
    #   inner Term
    #   inner Leaf
    # = 5
    assert node_count(parse_shape("C(r0^C(r0^1))")) == 5


def test_deeper_nesting() -> None:
    # C(r0^C(r0^C(r0^1))):
    #   outer Container + Term
    #   middle Container + Term
    #   inner Container + Term + Leaf
    # = 7
    assert node_count(parse_shape("C(r0^C(r0^C(r0^1)))")) == 7


def test_root_is_not_counted_separately() -> None:
    # If Root were counted separately, the value would be 4, not 3.
    assert node_count(parse_shape("C(r0^1)")) == 3


def test_deep_iterative_no_recursion_limit() -> None:
    shape: Leaf | Container = Leaf()
    depth = 1500  # well beyond default Python recursion limit
    for _ in range(depth):
        shape = Container(terms=(Term(root=Root(0), exponent=shape),))
    assert node_count(shape) == 1 + 2 * depth


def test_invalid_shape_raises() -> None:
    # A non-canonical container with wrong root ranks fails validation.
    bad = Container(terms=(Term(root=Root(1), exponent=Leaf()),))
    with pytest.raises(ValueError):
        node_count(bad)
