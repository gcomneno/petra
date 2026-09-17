#!/usr/bin/env python3
"""Bounded executable probe for AIP-1 Terminal vs empty composition.

Research-only. This file does not define canonical PETRA semantics.

The probe compares the current two-constructor abstract presentation

    Form ::= Terminal | Composite(Multiset(Form+))

with a uniform one-constructor presentation

    Form ::= Node(Multiset(Form*))

where the zero-child node is the candidate image of Terminal.  Ordered tuples
are used only as temporary coordinates so current positional addresses can be
replayed; all ontological comparisons erase sibling order while preserving
multiplicity.
"""

from __future__ import annotations

from dataclasses import dataclass
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

OldForm: TypeAlias = tuple[str] | tuple[str, tuple["OldForm", ...]]
OldKey: TypeAlias = tuple[str] | tuple[str, tuple["OldKey", ...]]
BoxForm: TypeAlias = tuple["BoxForm", ...]
BoxKey: TypeAlias = tuple["BoxKey", ...]

TERMINAL: OldForm = ("terminal",)
EMPTY_BOX: BoxForm = ()


def container(*children: PetraShape) -> Container:
    """Build one valid current-model container from ordered child shapes."""

    return Container(
        terms=tuple(
            Term(root=Root(rank), exponent=child)
            for rank, child in enumerate(children)
        )
    )


def erase_ordered(shape: PetraShape) -> OldForm:
    """Erase Root/Term/^ vocabulary while retaining order as coordinates."""

    if isinstance(shape, Leaf):
        return TERMINAL
    return (
        "composite",
        tuple(erase_ordered(term.exponent) for term in shape.terms),
    )


def old_key(form: OldForm) -> OldKey:
    """Order-free, multiplicity-preserving key for the two-constructor model."""

    if form == TERMINAL:
        return ("terminal",)
    tag, children = form
    assert tag == "composite"
    return (
        "composite",
        tuple(sorted((old_key(child) for child in children), key=repr)),
    )


def encode_box(form: OldForm) -> BoxForm:
    """Map Terminal to zero children and Composite to one uniform Box node."""

    if form == TERMINAL:
        return EMPTY_BOX
    tag, children = form
    assert tag == "composite"
    assert children
    return tuple(encode_box(child) for child in children)


def decode_box(box: BoxForm) -> OldForm:
    """Inverse candidate mapping from the uniform Box model."""

    if not box:
        return TERMINAL
    return ("composite", tuple(decode_box(child) for child in box))


def box_key(box: BoxForm) -> BoxKey:
    """Erase sibling order from Box while preserving duplicate child count."""

    return tuple(sorted((box_key(child) for child in box), key=repr))


def shape_box_key(shape: PetraShape) -> BoxKey:
    return box_key(encode_box(erase_ordered(shape)))


def _replace_old(form: OldForm, path: tuple[int, ...], replacement: OldForm) -> OldForm:
    if not path:
        return replacement
    tag, children = form
    assert tag == "composite"
    rebuilt = list(children)
    rebuilt[path[0]] = _replace_old(rebuilt[path[0]], path[1:], replacement)
    return ("composite", tuple(rebuilt))


def _old_at(form: OldForm, path: tuple[int, ...]) -> OldForm:
    current = form
    for index in path:
        tag, children = current
        assert tag == "composite"
        current = children[index]
    return current


def _replace_box(box: BoxForm, path: tuple[int, ...], replacement: BoxForm) -> BoxForm:
    if not path:
        return replacement
    rebuilt = list(box)
    rebuilt[path[0]] = _replace_box(rebuilt[path[0]], path[1:], replacement)
    return tuple(rebuilt)


def _box_at(box: BoxForm, path: tuple[int, ...]) -> BoxForm:
    current = box
    for index in path:
        current = current[index]
    return current


def _old_sprout(form: OldForm, path: tuple[int, ...]) -> OldForm:
    target = _old_at(form, path)
    if target == TERMINAL:
        replacement: OldForm = ("composite", (TERMINAL,))
    else:
        tag, children = target
        assert tag == "composite"
        replacement = ("composite", (*children, TERMINAL))
    return _replace_old(form, path, replacement)


def _box_sprout(box: BoxForm, path: tuple[int, ...]) -> BoxForm:
    target = _box_at(box, path)
    return _replace_box(box, path, (*target, EMPTY_BOX))


def _old_graft(form: OldForm, path: tuple[int, ...]) -> OldForm:
    assert _old_at(form, path) == TERMINAL
    return _replace_old(form, path, ("composite", (TERMINAL,)))


def _box_graft(box: BoxForm, path: tuple[int, ...]) -> BoxForm:
    assert _box_at(box, path) == EMPTY_BOX
    return _replace_box(box, path, (EMPTY_BOX,))


def _old_shed(form: OldForm, path: tuple[int, ...]) -> OldForm:
    assert path
    assert _old_at(form, path) == TERMINAL
    parent_path = path[:-1]
    index = path[-1]
    parent = _old_at(form, parent_path)
    tag, children = parent
    assert tag == "composite"
    remaining = children[:index] + children[index + 1 :]
    replacement: OldForm = (
        ("composite", remaining) if remaining else TERMINAL
    )
    return _replace_old(form, parent_path, replacement)


def _box_shed(box: BoxForm, path: tuple[int, ...]) -> BoxForm:
    assert path
    assert _box_at(box, path) == EMPTY_BOX
    parent_path = path[:-1]
    index = path[-1]
    parent = _box_at(box, parent_path)
    remaining = parent[:index] + parent[index + 1 :]
    return _replace_box(box, parent_path, remaining)


def _old_prune(form: OldForm, path: tuple[int, ...]) -> OldForm:
    assert _old_at(form, path) == ("composite", (TERMINAL,))
    return _replace_old(form, path, TERMINAL)


def _box_prune(box: BoxForm, path: tuple[int, ...]) -> BoxForm:
    assert _box_at(box, path) == (EMPTY_BOX,)
    return _replace_box(box, path, EMPTY_BOX)


def _all_shape_paths(shape: PetraShape) -> list[tuple[tuple[int, ...], PetraShape]]:
    result: list[tuple[tuple[int, ...], PetraShape]] = []

    def visit(current: PetraShape, path: tuple[int, ...]) -> None:
        result.append((path, current))
        if isinstance(current, Container):
            for index, term in enumerate(current.terms):
                visit(term.exponent, (*path, index))

    visit(shape, ())
    return result


def _leaf_paths(shape: PetraShape) -> list[tuple[int, ...]]:
    return [
        path
        for path, current in _all_shape_paths(shape)
        if path and isinstance(current, Leaf)
    ]


def _container_paths(shape: PetraShape) -> list[tuple[int, ...]]:
    return [
        path
        for path, current in _all_shape_paths(shape)
        if isinstance(current, Container)
    ]


def _prune_target_paths(shape: PetraShape) -> list[tuple[int, ...]]:
    eligible: list[tuple[int, ...]] = []
    by_path = dict(_all_shape_paths(shape))
    for leaf_path in _leaf_paths(shape):
        if len(leaf_path) < 2:
            continue
        parent_path = leaf_path[:-1]
        parent = by_path[parent_path]
        if isinstance(parent, Container) and len(parent.terms) == 1:
            eligible.append(leaf_path)
    return eligible


def representative_corpus(max_depth: int = 2, max_width: int = 3) -> list[PetraShape]:
    """Build one representative per bounded order-free multiset shape."""

    leaf = Leaf()
    representatives: dict[BoxKey, PetraShape] = {shape_box_key(leaf): leaf}

    for _depth in range(1, max_depth + 1):
        pool = list(representatives.values())
        added = False
        for width in range(1, max_width + 1):
            for children in combinations_with_replacement(pool, width):
                shape = container(*children)
                key = shape_box_key(shape)
                if key not in representatives:
                    representatives[key] = shape
                    added = True
        if not added:
            break

    return list(representatives.values())


def ordered_variants(shape: PetraShape) -> tuple[PetraShape, ...]:
    if isinstance(shape, Leaf):
        return (shape,)
    children = tuple(term.exponent for term in shape.terms)
    by_repr: dict[str, PetraShape] = {}
    for perm in permutations(children):
        variant = container(*perm)
        by_repr.setdefault(repr(erase_ordered(variant)), variant)
    return tuple(by_repr.values())


def _node_count_old(form: OldForm) -> int:
    if form == TERMINAL:
        return 1
    tag, children = form
    assert tag == "composite"
    return 1 + sum(_node_count_old(child) for child in children)


def _node_count_box(box: BoxForm) -> int:
    return 1 + sum(_node_count_box(child) for child in box)


def _depth_old(form: OldForm) -> int:
    if form == TERMINAL:
        return 0
    tag, children = form
    assert tag == "composite"
    return 1 + max(_depth_old(child) for child in children)


def _depth_box(box: BoxForm) -> int:
    if not box:
        return 0
    return 1 + max(_depth_box(child) for child in box)


def _incidence_paths_old(form: OldForm) -> set[tuple[tuple[int, ...], tuple[int, ...]]]:
    edges: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()

    def visit(current: OldForm, parent_path: tuple[int, ...]) -> None:
        if current == TERMINAL:
            return
        tag, children = current
        assert tag == "composite"
        for index, child in enumerate(children):
            child_path = (*parent_path, index)
            edges.add((parent_path, child_path))
            visit(child, child_path)

    visit(form, ())
    return edges


def _incidence_paths_box(box: BoxForm) -> set[tuple[tuple[int, ...], tuple[int, ...]]]:
    edges: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()

    def visit(current: BoxForm, parent_path: tuple[int, ...]) -> None:
        for index, child in enumerate(current):
            child_path = (*parent_path, index)
            edges.add((parent_path, child_path))
            visit(child, child_path)

    visit(box, ())
    return edges


def check_bijection(corpus: list[PetraShape]) -> None:
    for representative in corpus:
        for shape in ordered_variants(representative):
            old = erase_ordered(shape)
            box = encode_box(old)
            assert decode_box(box) == old
            assert encode_box(decode_box(box)) == box
            assert old_key(old) == old_key(decode_box(box))


def check_zero_child_uniqueness(corpus: list[PetraShape]) -> None:
    assert encode_box(TERMINAL) == EMPTY_BOX
    assert decode_box(EMPTY_BOX) == TERMINAL
    for shape in corpus:
        old = erase_ordered(shape)
        if old != TERMINAL:
            assert encode_box(old) != EMPTY_BOX


def check_unary_distinction() -> None:
    assert EMPTY_BOX != (EMPTY_BOX,)
    assert box_key(EMPTY_BOX) != box_key((EMPTY_BOX,))
    assert decode_box((EMPTY_BOX,)) == ("composite", (TERMINAL,))


def check_structure_preservation(corpus: list[PetraShape]) -> None:
    for shape in corpus:
        old = erase_ordered(shape)
        box = encode_box(old)
        assert _node_count_old(old) == _node_count_box(box)
        assert _depth_old(old) == _depth_box(box)
        assert _incidence_paths_old(old) == _incidence_paths_box(box)
        if isinstance(shape, Container):
            assert len(shape.terms) == len(box)


@dataclass(frozen=True)
class OperatorCounts:
    sprout: int = 0
    shed: int = 0
    graft: int = 0
    prune: int = 0


def check_operator_conjugacy(corpus: list[PetraShape]) -> OperatorCounts:
    sprout_count = 0
    shed_count = 0
    graft_count = 0
    prune_count = 0

    for representative in corpus:
        for shape in ordered_variants(representative):
            old = erase_ordered(shape)
            box = encode_box(old)

            sprout_paths = [()] + [path for path in _container_paths(shape) if path]
            for path in sprout_paths:
                runtime = apply_sprout(shape, ExplicitTarget(Address(indices=path)))
                assert isinstance(runtime, SuccessfulResult)
                old_after = _old_sprout(old, path)
                box_after = _box_sprout(box, path)
                assert encode_box(old_after) == box_after
                assert shape_box_key(runtime.after_shape) == box_key(box_after)
                sprout_count += 1

            for path in _leaf_paths(shape):
                runtime = apply_shed(shape, ExplicitTarget(Address(indices=path)))
                assert isinstance(runtime, SuccessfulResult)
                old_after = _old_shed(old, path)
                box_after = _box_shed(box, path)
                assert encode_box(old_after) == box_after
                assert shape_box_key(runtime.after_shape) == box_key(box_after)
                shed_count += 1

                runtime = apply_graft(
                    shape,
                    ExplicitTarget(Address(indices=path, is_slot=True)),
                )
                assert isinstance(runtime, SuccessfulResult)
                old_after = _old_graft(old, path)
                box_after = _box_graft(box, path)
                assert encode_box(old_after) == box_after
                assert shape_box_key(runtime.after_shape) == box_key(box_after)
                graft_count += 1

            for leaf_path in _prune_target_paths(shape):
                runtime = apply_prune(
                    shape,
                    ExplicitTarget(Address(indices=leaf_path)),
                )
                assert isinstance(runtime, SuccessfulResult)
                parent_path = leaf_path[:-1]
                old_after = _old_prune(old, parent_path)
                box_after = _box_prune(box, parent_path)
                assert encode_box(old_after) == box_after
                assert shape_box_key(runtime.after_shape) == box_key(box_after)
                prune_count += 1

    return OperatorCounts(
        sprout=sprout_count,
        shed=shed_count,
        graft=graft_count,
        prune=prune_count,
    )


def bounded_counterexample_search(corpus: list[PetraShape]) -> tuple[int, int, int, int]:
    variants = 0
    old_classes: set[OldKey] = set()
    box_classes: set[BoxKey] = set()
    correspondence: dict[OldKey, BoxKey] = {}

    for representative in corpus:
        for variant in ordered_variants(representative):
            variants += 1
            old = erase_ordered(variant)
            old_class = old_key(old)
            box_class = box_key(encode_box(old))
            old_classes.add(old_class)
            box_classes.add(box_class)
            previous = correspondence.setdefault(old_class, box_class)
            assert previous == box_class

    assert len(old_classes) == len(box_classes) == len(corpus)
    assert len(set(correspondence.values())) == len(correspondence)
    return len(corpus), variants, len(old_classes), len(box_classes)


def main() -> int:
    corpus = representative_corpus(max_depth=2, max_width=3)

    check_bijection(corpus)
    check_zero_child_uniqueness(corpus)
    check_unary_distinction()
    check_structure_preservation(corpus)
    counts = check_operator_conjugacy(corpus)
    representatives, variants, old_classes, box_classes = bounded_counterexample_search(corpus)

    print("AIP1_TERMINAL_EMPTY_BIJECTION=PASS")
    print("AIP1_ZERO_CHILD_UNIQUENESS=PASS")
    print("AIP1_UNARY_DISTINCTION=PASS")
    print("AIP1_INCIDENCE_PRESERVATION=PASS")
    print("AIP1_MULTIPLICITY_PRESERVATION=PASS")
    print("AIP1_LEVEL_DEPTH_PRESERVATION=PASS")
    print("AIP1_OPERATOR_CONJUGACY=PASS")
    print("AIP1_BOUNDED_COUNTEREXAMPLE_SEARCH=PASS")
    print(f"AIP1_SPROUT_CASES={counts.sprout}")
    print(f"AIP1_SHED_CASES={counts.shed}")
    print(f"AIP1_GRAFT_CASES={counts.graft}")
    print(f"AIP1_PRUNE_CASES={counts.prune}")
    print(f"AIP1_REPRESENTATIVES={representatives}")
    print(f"AIP1_ORDERED_VARIANTS={variants}")
    print(f"AIP1_OLD_CLASSES={old_classes}")
    print(f"AIP1_BOX_CLASSES={box_classes}")
    print("AIP1_SCOPE=max_depth=2,max_width=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
