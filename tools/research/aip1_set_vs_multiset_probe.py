#!/usr/bin/env python3
"""Bounded executable probe for AIP-1 Set vs Multiset composition.

Research-only. This file does not define canonical PETRA semantics.

The probe compares two order-free abstractions of the current recursive shape:

- multiset semantics preserve duplicate child occurrences;
- set semantics erase duplicate child occurrences.

It then checks whether accepted structural rewrites remain observable under both.
"""

from __future__ import annotations

from itertools import combinations_with_replacement, permutations
from typing import TypeAlias

from petra import (
    Address,
    Container,
    ExplicitTarget,
    Leaf,
    PetraShape,
    Root,
    SuccessfulResult,
    Term,
    apply_graft,
    apply_prune,
    apply_shed,
    apply_sprout,
)

MultiKey: TypeAlias = tuple[str] | tuple[str, tuple["MultiKey", ...]]
SetKey: TypeAlias = tuple[str] | tuple[str, tuple["SetKey", ...]]

MULTI_TERMINAL: MultiKey = ("terminal",)
SET_TERMINAL: SetKey = ("terminal",)


def container(*children: PetraShape) -> Container:
    """Build one valid current-model container from ordered child shapes."""

    return Container(
        terms=tuple(
            Term(root=Root(rank), exponent=child)
            for rank, child in enumerate(children)
        )
    )


def multiset_key(shape: PetraShape) -> MultiKey:
    """Erase sibling order while preserving duplicate child counts."""

    if isinstance(shape, Leaf):
        return MULTI_TERMINAL
    children = [multiset_key(term.exponent) for term in shape.terms]
    return ("composite", tuple(sorted(children, key=repr)))


def set_key(shape: PetraShape) -> SetKey:
    """Erase sibling order and collapse recursively equal duplicate children."""

    if isinstance(shape, Leaf):
        return SET_TERMINAL
    unique_children = {
        set_key(term.exponent)
        for term in shape.terms
    }
    return ("composite", tuple(sorted(unique_children, key=repr)))


def representative_corpus(max_depth: int = 2, max_width: int = 3) -> list[PetraShape]:
    """Build one current-model representative per bounded multiset form."""

    leaf = Leaf()
    representatives: dict[MultiKey, PetraShape] = {multiset_key(leaf): leaf}

    for _depth in range(1, max_depth + 1):
        pool = list(representatives.values())
        added = False
        for width in range(1, max_width + 1):
            for children in combinations_with_replacement(pool, width):
                shape = container(*children)
                key = multiset_key(shape)
                if key not in representatives:
                    representatives[key] = shape
                    added = True
        if not added:
            break

    return list(representatives.values())


def ordered_variants(shape: PetraShape) -> tuple[PetraShape, ...]:
    """Return unique root-level sibling permutations for a bounded shape."""

    if isinstance(shape, Leaf):
        return (shape,)

    children = tuple(term.exponent for term in shape.terms)
    by_repr: dict[str, PetraShape] = {}
    for perm in permutations(children):
        variant = container(*perm)
        by_repr.setdefault(repr(variant), variant)
    return tuple(by_repr.values())


def check_permutation_erasure() -> None:
    """Both abstractions must ignore sibling order."""

    deep = container(Leaf())
    left = container(Leaf(), deep)
    right = container(deep, Leaf())

    assert left != right
    assert multiset_key(left) == multiset_key(right)
    assert set_key(left) == set_key(right)


def check_duplicate_count_witness() -> None:
    """Multiset distinguishes width 1/2 while set semantics collapses them."""

    one = container(Leaf())
    two = container(Leaf(), Leaf())
    three = container(Leaf(), Leaf(), Leaf())

    assert multiset_key(one) != multiset_key(two)
    assert multiset_key(two) != multiset_key(three)
    assert set_key(one) == set_key(two) == set_key(three)


def check_sprout_visibility() -> None:
    """Adding an already-present Terminal disappears under set erasure."""

    before = container(Leaf())
    result = apply_sprout(before, ExplicitTarget(Address()))
    assert isinstance(result, SuccessfulResult)

    assert multiset_key(before) != multiset_key(result.after_shape)
    assert set_key(before) == set_key(result.after_shape)


def check_shed_visibility() -> None:
    """Reducing duplicate multiplicity two -> one disappears under set erasure."""

    before = container(Leaf(), Leaf())
    result = apply_shed(before, ExplicitTarget(Address(indices=(0,))))
    assert isinstance(result, SuccessfulResult)

    assert multiset_key(before) != multiset_key(result.after_shape)
    assert set_key(before) == set_key(result.after_shape)


def check_graft_prune_visibility() -> None:
    """Depth-changing singleton rewrites remain visible under both abstractions."""

    before = container(Leaf())
    grafted = apply_graft(
        before,
        ExplicitTarget(Address(indices=(0,), is_slot=True)),
    )
    assert isinstance(grafted, SuccessfulResult)

    assert multiset_key(before) != multiset_key(grafted.after_shape)
    assert set_key(before) != set_key(grafted.after_shape)

    pruned = apply_prune(
        grafted.after_shape,
        ExplicitTarget(Address(indices=(0, 0))),
    )
    assert isinstance(pruned, SuccessfulResult)

    assert multiset_key(grafted.after_shape) != multiset_key(pruned.after_shape)
    assert set_key(grafted.after_shape) != set_key(pruned.after_shape)
    assert multiset_key(pruned.after_shape) == multiset_key(before)
    assert set_key(pruned.after_shape) == set_key(before)


def bounded_class_search(corpus: list[PetraShape]) -> tuple[int, int, int, int, int]:
    """Compare bounded equivalence-class counts under both abstractions."""

    variants = 0
    multiset_classes: set[MultiKey] = set()
    set_classes: set[SetKey] = set()

    for representative in corpus:
        for variant in ordered_variants(representative):
            variants += 1
            multiset_classes.add(multiset_key(variant))
            set_classes.add(set_key(variant))

    assert len(multiset_classes) == len(corpus)
    assert len(set_classes) < len(multiset_classes)

    set_collapses = len(multiset_classes) - len(set_classes)
    return (
        len(corpus),
        variants,
        len(multiset_classes),
        len(set_classes),
        set_collapses,
    )


def main() -> int:
    check_permutation_erasure()
    check_duplicate_count_witness()
    check_sprout_visibility()
    check_shed_visibility()
    check_graft_prune_visibility()

    corpus = representative_corpus(max_depth=2, max_width=3)
    representatives, variants, multi_classes, set_classes, collapses = bounded_class_search(
        corpus
    )

    print("AIP1_PERMUTATION_ERASURE=PASS")
    print("AIP1_MULTISET_DUPLICATE_COUNT=PASS")
    print("AIP1_SET_DUPLICATE_COLLAPSE=PASS")
    print("AIP1_SPROUT_SET_INVISIBILITY=PASS")
    print("AIP1_SHED_SET_INVISIBILITY=PASS")
    print("AIP1_GRAFT_PRUNE_VISIBILITY=PASS")
    print("AIP1_BOUNDED_CLASS_SEARCH=PASS")
    print(f"AIP1_REPRESENTATIVES={representatives}")
    print(f"AIP1_ORDERED_VARIANTS={variants}")
    print(f"AIP1_MULTISET_CLASSES={multi_classes}")
    print(f"AIP1_SET_CLASSES={set_classes}")
    print(f"AIP1_SET_COLLAPSES={collapses}")
    print("AIP1_SCOPE=max_depth=2,max_width=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
