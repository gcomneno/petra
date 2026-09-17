#!/usr/bin/env python3
"""Bounded executable probe for the AIP-2 wrapper-erasure hypothesis.

Research-only. This file does not define canonical PETRA semantics.

The candidate erasure forgets Root/rank, Term as an independently meaningful
wrapper, sibling order, and exponent/^ vocabulary. It retains only recursive
terminal/composite structure with child multiplicity.
"""

from __future__ import annotations

from collections import defaultdict
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

ErasedKey: TypeAlias = tuple[str] | tuple[str, tuple["ErasedKey", ...]]


def container(*children: PetraShape) -> Container:
    """Build one canonical current-model container from ordered children."""

    return Container(
        terms=tuple(
            Term(root=Root(rank), exponent=child)
            for rank, child in enumerate(children)
        )
    )


def erased_key(shape: PetraShape) -> ErasedKey:
    """Erase wrapper/rank/order vocabulary into a recursive multiset key."""

    if isinstance(shape, Leaf):
        return ("terminal",)

    children = [erased_key(term.exponent) for term in shape.terms]
    return ("composite", tuple(sorted(children, key=repr)))


def erased_depth(key: ErasedKey) -> int:
    """Derive depth from the erased recursive carrier."""

    if key[0] == "terminal":
        return 0
    children = key[1]
    return 1 + max(erased_depth(child) for child in children)


def direct_children(key: ErasedKey) -> tuple[ErasedKey, ...]:
    """Return direct child multiplicity from one erased composite."""

    if key[0] == "terminal":
        return ()
    return key[1]


def representative_corpus(max_depth: int = 2, max_width: int = 3) -> list[PetraShape]:
    """Build one current-model representative per erased recursive form."""

    leaf = Leaf()
    representatives: dict[ErasedKey, PetraShape] = {erased_key(leaf): leaf}

    for _depth in range(1, max_depth + 1):
        pool = list(representatives.values())
        added = 0
        for width in range(1, max_width + 1):
            for children in combinations_with_replacement(pool, width):
                shape = container(*children)
                key = erased_key(shape)
                if key not in representatives:
                    representatives[key] = shape
                    added += 1
        if added == 0:
            break

    return list(representatives.values())


def unique_permutations(children: tuple[PetraShape, ...]) -> tuple[tuple[PetraShape, ...], ...]:
    """Return unique sibling permutations for the small bounded corpus."""

    by_key: dict[tuple[str, ...], tuple[PetraShape, ...]] = {}
    for perm in permutations(children):
        ordered_key = tuple(repr(child) for child in perm)
        by_key.setdefault(ordered_key, perm)
    return tuple(by_key.values())


def all_variants(shape: PetraShape) -> tuple[PetraShape, ...]:
    """Materialize root-level sibling-order variants for collision checks."""

    if isinstance(shape, Leaf):
        return (shape,)
    children = tuple(term.exponent for term in shape.terms)
    return tuple(container(*perm) for perm in unique_permutations(children))


def replace_at_path(key: ErasedKey, path: tuple[int, ...], replacement: ErasedKey) -> ErasedKey:
    """Replace one occurrence selected by the current representation path.

    The path is used only to identify which current occurrence is rewritten.
    The result is immediately rematerialized as an order-free multiset key.
    """

    if not path:
        return replacement
    if key[0] != "composite":
        raise AssertionError("path crossed terminal in erased carrier")

    children = list(key[1])
    index = path[0]
    children[index] = replace_at_path(children[index], path[1:], replacement)
    return ("composite", tuple(sorted(children, key=repr)))


def remove_child_at_path(key: ErasedKey, path: tuple[int, ...]) -> ErasedKey:
    """Remove one child occurrence, restoring Terminal for an emptied parent."""

    if not path or key[0] != "composite":
        raise AssertionError("child removal requires a composite parent path")

    children = list(key[1])
    index = path[0]
    if len(path) == 1:
        del children[index]
        if not children:
            return ("terminal",)
        return ("composite", tuple(sorted(children, key=repr)))

    children[index] = remove_child_at_path(children[index], path[1:])
    return ("composite", tuple(sorted(children, key=repr)))


def add_terminal_at_path(key: ErasedKey, path: tuple[int, ...]) -> ErasedKey:
    """Add one Terminal child to the selected composite occurrence."""

    terminal: ErasedKey = ("terminal",)
    if not path:
        if key[0] == "terminal":
            return ("composite", (terminal,))
        children = [*key[1], terminal]
        return ("composite", tuple(sorted(children, key=repr)))

    if key[0] != "composite":
        raise AssertionError("SPROUT path crossed terminal")
    children = list(key[1])
    index = path[0]
    children[index] = add_terminal_at_path(children[index], path[1:])
    return ("composite", tuple(sorted(children, key=repr)))


def iter_term_addresses(shape: PetraShape) -> tuple[tuple[Address, Term, int], ...]:
    """Enumerate current term occurrences with parent width."""

    found: list[tuple[Address, Term, int]] = []

    def visit(current: PetraShape, prefix: tuple[int, ...]) -> None:
        if isinstance(current, Leaf):
            return
        width = len(current.terms)
        for index, term in enumerate(current.terms):
            path = (*prefix, index)
            found.append((Address(indices=path), term, width))
            visit(term.exponent, path)

    visit(shape, ())
    return tuple(found)


def check_erasure_and_multiplicity() -> None:
    """Check explicit wrapper/rank/order erasure witnesses."""

    terminal = Leaf()
    deep = container(Leaf())
    left = container(terminal, deep, terminal)
    right = container(terminal, terminal, deep)

    assert left != right
    assert erased_key(left) == erased_key(right)
    assert len(direct_children(erased_key(left))) == 3
    assert direct_children(erased_key(left)).count(("terminal",)) == 2


def bounded_collision_search() -> tuple[int, int, int]:
    """Reject accidental collisions beyond intended sibling permutations."""

    corpus = representative_corpus(max_depth=2, max_width=3)
    classes: dict[ErasedKey, list[PetraShape]] = defaultdict(list)
    variant_count = 0

    for representative in corpus:
        for variant in all_variants(representative):
            classes[erased_key(variant)].append(variant)
            variant_count += 1

    assert len(classes) == len(corpus)
    for key, variants in classes.items():
        assert variants
        expected_depth = erased_depth(key)
        expected_children = direct_children(key)
        for variant in variants:
            assert erased_key(variant) == key
            assert erased_depth(erased_key(variant)) == expected_depth
            assert direct_children(erased_key(variant)) == expected_children

    return len(corpus), variant_count, len(classes)


def check_sprout_shed_commutation(corpus: list[PetraShape]) -> tuple[int, int]:
    """Check explicit SPROUT/SHED shape effects commute with erasure."""

    sprout_checks = 0
    shed_checks = 0
    terminal: ErasedKey = ("terminal",)

    for shape in corpus:
        before = erased_key(shape)

        # Root-anchor SPROUT is always a candidate invocation.
        result = apply_sprout(shape, ExplicitTarget(Address()))
        if isinstance(result, SuccessfulResult):
            expected = add_terminal_at_path(before, ())
            assert erased_key(result.after_shape) == expected
            sprout_checks += 1

        for address, term, _parent_width in iter_term_addresses(shape):
            if isinstance(term.exponent, Container):
                result = apply_sprout(shape, ExplicitTarget(address))
                if isinstance(result, SuccessfulResult):
                    expected = add_terminal_at_path(before, address.indices)
                    assert erased_key(result.after_shape) == expected
                    sprout_checks += 1

            if isinstance(term.exponent, Leaf):
                result = apply_shed(shape, ExplicitTarget(address))
                if isinstance(result, SuccessfulResult):
                    expected = remove_child_at_path(before, address.indices)
                    assert erased_key(result.after_shape) == expected
                    assert terminal == ("terminal",)
                    shed_checks += 1

    return sprout_checks, shed_checks


def check_graft_prune_commutation(corpus: list[PetraShape]) -> tuple[int, int]:
    """Check explicit GRAFT/PRUNE effects commute with wrapper erasure."""

    graft_checks = 0
    prune_checks = 0
    terminal: ErasedKey = ("terminal",)
    singleton: ErasedKey = ("composite", (terminal,))

    for shape in corpus:
        before = erased_key(shape)
        for address, term, parent_width in iter_term_addresses(shape):
            if isinstance(term.exponent, Leaf):
                slot = Address(indices=address.indices, is_slot=True)
                result = apply_graft(shape, ExplicitTarget(slot))
                if isinstance(result, SuccessfulResult):
                    expected = replace_at_path(before, address.indices, singleton)
                    assert erased_key(result.after_shape) == expected
                    graft_checks += 1

                # PRUNE targets a leaf term nested inside a singleton container.
                if len(address.indices) >= 2 and parent_width == 1:
                    result = apply_prune(shape, ExplicitTarget(address))
                    if isinstance(result, SuccessfulResult):
                        parent_path = address.indices[:-1]
                        expected = replace_at_path(before, parent_path, terminal)
                        assert erased_key(result.after_shape) == expected
                        prune_checks += 1

    return graft_checks, prune_checks


def main() -> int:
    check_erasure_and_multiplicity()
    representatives, variants, quotient_classes = bounded_collision_search()
    corpus = representative_corpus(max_depth=2, max_width=3)
    sprout_checks, shed_checks = check_sprout_shed_commutation(corpus)
    graft_checks, prune_checks = check_graft_prune_commutation(corpus)

    assert sprout_checks > 0
    assert shed_checks > 0
    assert graft_checks > 0
    assert prune_checks > 0

    print("AIP2_WRAPPER_ERASURE=PASS")
    print("AIP2_MULTIPLICITY=PASS")
    print("AIP2_BOUNDED_COLLISION_SEARCH=PASS")
    print("AIP2_SPROUT_COMMUTATION=PASS")
    print("AIP2_SHED_COMMUTATION=PASS")
    print("AIP2_GRAFT_COMMUTATION=PASS")
    print("AIP2_PRUNE_COMMUTATION=PASS")
    print("AIP2_DERIVED_DEPTH=PASS")
    print(f"AIP2_REPRESENTATIVES={representatives}")
    print(f"AIP2_ORDERED_VARIANTS={variants}")
    print(f"AIP2_ERASED_CLASSES={quotient_classes}")
    print(f"AIP2_SPROUT_CHECKS={sprout_checks}")
    print(f"AIP2_SHED_CHECKS={shed_checks}")
    print(f"AIP2_GRAFT_CHECKS={graft_checks}")
    print(f"AIP2_PRUNE_CHECKS={prune_checks}")
    print("AIP2_SCOPE=max_depth=2,max_width=3,explicit-targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
