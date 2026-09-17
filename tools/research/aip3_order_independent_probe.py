#!/usr/bin/env python3
"""Bounded AIP-3 probe for order-independent PETRA shape identity.

Research-only. This file does not define canonical PETRA semantics.

The candidate quotient forgets sibling position recursively while preserving
sibling multiplicity. It therefore models each container as a multiset of
recursive component shapes.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations_with_replacement, permutations
from typing import TypeAlias

from petra import Container, Leaf, PetraShape, Root, Term, node_count

OrderFreeKey: TypeAlias = tuple[str] | tuple[str, tuple["OrderFreeKey", ...]]


def container(*children: PetraShape) -> Container:
    """Build a canonical current-model container from ordered child shapes."""

    return Container(
        terms=tuple(
            Term(root=Root(rank), exponent=child)
            for rank, child in enumerate(children)
        )
    )


def order_free_key(shape: PetraShape) -> OrderFreeKey:
    """Return a recursive sibling-permutation-invariant shape key."""

    if isinstance(shape, Leaf):
        return ("leaf",)

    child_keys = [order_free_key(term.exponent) for term in shape.terms]
    return ("container", tuple(sorted(child_keys, key=repr)))


def structural_depth(shape: PetraShape) -> int:
    """Return recursive container depth, independent of sibling order."""

    if isinstance(shape, Leaf):
        return 0
    return 1 + max(structural_depth(term.exponent) for term in shape.terms)


def direct_multiplicity(shape: PetraShape) -> tuple[OrderFreeKey, ...]:
    """Return the direct-child multiset as a deterministic tuple."""

    if isinstance(shape, Leaf):
        return ()
    return tuple(
        sorted(
            (order_free_key(term.exponent) for term in shape.terms),
            key=repr,
        )
    )


def unique_permutations(children: tuple[PetraShape, ...]) -> tuple[tuple[PetraShape, ...], ...]:
    """Return unique ordered sibling permutations for a small bounded tuple."""

    by_key: dict[tuple[str, ...], tuple[PetraShape, ...]] = {}
    for perm in permutations(children):
        ordered_key = tuple(repr(order_free_key(child)) for child in perm)
        by_key.setdefault(ordered_key, perm)
    return tuple(by_key.values())


def representative_corpus(max_depth: int = 2, max_width: int = 3) -> list[PetraShape]:
    """Build a bounded corpus with one representative per unordered form.

    Depth 0 contains Leaf. Each later layer builds containers whose children
    are drawn with replacement from representatives already known at shallower
    depth. The order used to materialize a representative is arbitrary and is
    deliberately discarded by ``order_free_key``.
    """

    leaf = Leaf()
    representatives: dict[OrderFreeKey, PetraShape] = {order_free_key(leaf): leaf}
    frontier = [leaf]

    for _depth in range(1, max_depth + 1):
        pool = list(representatives.values())
        new_frontier: list[PetraShape] = []
        for width in range(1, max_width + 1):
            for children in combinations_with_replacement(pool, width):
                shape = container(*children)
                key = order_free_key(shape)
                if key not in representatives:
                    representatives[key] = shape
                    new_frontier.append(shape)
        frontier = new_frontier
        if not frontier:
            break

    return list(representatives.values())


def check_explicit_permutation_witness() -> None:
    """Show current ordered inequality but quotient equality."""

    leaf = Leaf()
    deep = container(Leaf())
    left = container(leaf, deep)
    right = container(deep, leaf)

    assert left != right
    assert order_free_key(left) == order_free_key(right)
    assert node_count(left) == node_count(right)
    assert structural_depth(left) == structural_depth(right)
    assert direct_multiplicity(left) == direct_multiplicity(right)


def check_recursive_permutation_witness() -> None:
    """Show that permutations nested below the root also disappear."""

    a = container(Leaf(), container(Leaf()))
    b = container(container(Leaf()), Leaf())
    left = container(a, Leaf())
    right = container(b, Leaf())

    assert left != right
    assert order_free_key(left) == order_free_key(right)
    assert node_count(left) == node_count(right)
    assert structural_depth(left) == structural_depth(right)


def check_multiplicity_is_preserved() -> None:
    """Ensure multiset semantics does not collapse duplicates like a set."""

    one = container(Leaf())
    two = container(Leaf(), Leaf())
    three = container(Leaf(), Leaf(), Leaf())

    assert order_free_key(one) != order_free_key(two)
    assert order_free_key(two) != order_free_key(three)
    assert len(direct_multiplicity(two)) == 2
    assert len(direct_multiplicity(three)) == 3


def bounded_counterexample_search() -> tuple[int, int, int]:
    """Search a bounded corpus for accidental quotient collisions.

    Returns ``(representatives, ordered_variants, quotient_classes)``.
    A collision is considered accidental if two variants with the same
    quotient key disagree on candidate order-independent observables.
    """

    corpus = representative_corpus(max_depth=2, max_width=3)
    classes: dict[OrderFreeKey, list[PetraShape]] = defaultdict(list)
    ordered_variants = 0

    for representative in corpus:
        if isinstance(representative, Leaf):
            variants = (representative,)
        else:
            children = tuple(term.exponent for term in representative.terms)
            variants = tuple(container(*perm) for perm in unique_permutations(children))

        for variant in variants:
            classes[order_free_key(variant)].append(variant)
            ordered_variants += 1

    assert len(classes) == len(corpus)

    for key, variants in classes.items():
        expected_nodes = node_count(variants[0])
        expected_depth = structural_depth(variants[0])
        expected_multiplicity = direct_multiplicity(variants[0])
        for variant in variants[1:]:
            assert order_free_key(variant) == key
            assert node_count(variant) == expected_nodes
            assert structural_depth(variant) == expected_depth
            assert direct_multiplicity(variant) == expected_multiplicity

    return len(corpus), ordered_variants, len(classes)


def main() -> int:
    check_explicit_permutation_witness()
    check_recursive_permutation_witness()
    check_multiplicity_is_preserved()
    representatives, ordered_variants, quotient_classes = bounded_counterexample_search()

    print("AIP3_EXPLICIT_PERMUTATION=PASS")
    print("AIP3_RECURSIVE_PERMUTATION=PASS")
    print("AIP3_MULTIPLICITY=PASS")
    print("AIP3_BOUNDED_COUNTEREXAMPLE_SEARCH=PASS")
    print(f"AIP3_REPRESENTATIVES={representatives}")
    print(f"AIP3_ORDERED_VARIANTS={ordered_variants}")
    print(f"AIP3_QUOTIENT_CLASSES={quotient_classes}")
    print("AIP3_SCOPE=max_depth=2,max_width=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
