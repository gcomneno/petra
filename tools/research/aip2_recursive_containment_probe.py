#!/usr/bin/env python3
"""Bounded executable probe for AIP-2 recursive containment.

Research-only. This file does not define canonical PETRA semantics.

The probe erases the current Root/Term/exponent relation wrapper into a neutral
recursive carrier, then checks whether the four current structural rewrites can
be reproduced on that wrapper-erased carrier over a bounded corpus.
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

RawForm: TypeAlias = tuple[str] | tuple[str, tuple["RawForm", ...]]
AbstractKey: TypeAlias = tuple[str] | tuple[str, tuple["AbstractKey", ...]]

TERMINAL: RawForm = ("terminal",)


def container(*children: PetraShape) -> Container:
    """Build one valid current-model container from ordered child shapes."""

    return Container(
        terms=tuple(
            Term(root=Root(rank), exponent=child)
            for rank, child in enumerate(children)
        )
    )


def erase_ordered(shape: PetraShape) -> RawForm:
    """Erase Root/Term/exponent vocabulary while retaining order as test harness.

    Retaining sequence order here is only a temporary coordinate device so that
    current positional addresses can be mapped into the neutral recursive form.
    ``abstract_key`` removes that order before any ontological comparison.
    """

    if isinstance(shape, Leaf):
        return TERMINAL
    return (
        "composite",
        tuple(erase_ordered(term.exponent) for term in shape.terms),
    )


def abstract_key(form: RawForm) -> AbstractKey:
    """Return the order-free recursive containment key with multiplicity."""

    if form == TERMINAL:
        return ("terminal",)
    tag, children = form
    assert tag == "composite"
    return (
        "composite",
        tuple(sorted((abstract_key(child) for child in children), key=repr)),
    )


def erase_key(shape: PetraShape) -> AbstractKey:
    """Map one current PETRA shape into the candidate abstract carrier."""

    return abstract_key(erase_ordered(shape))


def _replace_form(form: RawForm, path: tuple[int, ...], replacement: RawForm) -> RawForm:
    if not path:
        return replacement
    tag, children = form
    assert tag == "composite"
    index = path[0]
    rebuilt = list(children)
    rebuilt[index] = _replace_form(rebuilt[index], path[1:], replacement)
    return ("composite", tuple(rebuilt))


def _form_at(form: RawForm, path: tuple[int, ...]) -> RawForm:
    current = form
    for index in path:
        tag, children = current
        assert tag == "composite"
        current = children[index]
    return current


def _sprout(form: RawForm, target_path: tuple[int, ...]) -> RawForm:
    target = _form_at(form, target_path)
    if target == TERMINAL:
        replacement: RawForm = ("composite", (TERMINAL,))
    else:
        tag, children = target
        assert tag == "composite"
        replacement = ("composite", (*children, TERMINAL))
    return _replace_form(form, target_path, replacement)


def _graft(form: RawForm, terminal_path: tuple[int, ...]) -> RawForm:
    assert _form_at(form, terminal_path) == TERMINAL
    return _replace_form(
        form,
        terminal_path,
        ("composite", (TERMINAL,)),
    )


def _shed(form: RawForm, terminal_path: tuple[int, ...]) -> RawForm:
    assert terminal_path
    assert _form_at(form, terminal_path) == TERMINAL
    parent_path = terminal_path[:-1]
    selected_index = terminal_path[-1]
    parent = _form_at(form, parent_path)
    tag, children = parent
    assert tag == "composite"
    remaining = children[:selected_index] + children[selected_index + 1 :]
    replacement: RawForm
    if remaining:
        replacement = ("composite", remaining)
    else:
        replacement = TERMINAL
    return _replace_form(form, parent_path, replacement)


def _prune(form: RawForm, singleton_composite_path: tuple[int, ...]) -> RawForm:
    target = _form_at(form, singleton_composite_path)
    assert target == ("composite", (TERMINAL,))
    return _replace_form(form, singleton_composite_path, TERMINAL)


def _all_form_paths(shape: PetraShape) -> list[tuple[tuple[int, ...], PetraShape]]:
    result: list[tuple[tuple[int, ...], PetraShape]] = []

    def visit(current: PetraShape, path: tuple[int, ...]) -> None:
        result.append((path, current))
        if isinstance(current, Container):
            for index, term in enumerate(current.terms):
                visit(term.exponent, (*path, index))

    visit(shape, ())
    return result


def _leaf_term_paths(shape: PetraShape) -> list[tuple[int, ...]]:
    return [
        path
        for path, current in _all_form_paths(shape)
        if path and isinstance(current, Leaf)
    ]


def _container_paths(shape: PetraShape) -> list[tuple[int, ...]]:
    return [
        path
        for path, current in _all_form_paths(shape)
        if isinstance(current, Container)
    ]


def _prune_target_paths(shape: PetraShape) -> list[tuple[int, ...]]:
    """Return current leaf-term addresses eligible for explicit PRUNE."""

    eligible: list[tuple[int, ...]] = []
    for leaf_path in _leaf_term_paths(shape):
        if len(leaf_path) < 2:
            continue
        parent_path = leaf_path[:-1]
        parent = next(
            current
            for path, current in _all_form_paths(shape)
            if path == parent_path
        )
        if isinstance(parent, Container) and len(parent.terms) == 1:
            eligible.append(leaf_path)
    return eligible


def representative_corpus(max_depth: int = 2, max_width: int = 3) -> list[PetraShape]:
    """Build one current-model representative per bounded abstract form."""

    leaf = Leaf()
    representatives: dict[AbstractKey, PetraShape] = {erase_key(leaf): leaf}

    for _depth in range(1, max_depth + 1):
        pool = list(representatives.values())
        added = False
        for width in range(1, max_width + 1):
            for children in combinations_with_replacement(pool, width):
                shape = container(*children)
                key = erase_key(shape)
                if key not in representatives:
                    representatives[key] = shape
                    added = True
        if not added:
            break

    return list(representatives.values())


def ordered_variants(shape: PetraShape) -> tuple[PetraShape, ...]:
    """Materialize unique root sibling permutations for a bounded shape."""

    if isinstance(shape, Leaf):
        return (shape,)
    children = tuple(term.exponent for term in shape.terms)
    by_repr: dict[str, PetraShape] = {}
    for perm in permutations(children):
        variant = container(*perm)
        by_repr.setdefault(repr(erase_ordered(variant)), variant)
    return tuple(by_repr.values())


def check_wrapper_erasure() -> None:
    leaf = Leaf()
    deep = container(Leaf())
    current = container(leaf, deep, leaf)
    raw = erase_ordered(current)

    assert raw == (
        "composite",
        (
            TERMINAL,
            ("composite", (TERMINAL,)),
            TERMINAL,
        ),
    )
    assert "r" not in repr(raw)
    assert "^" not in repr(raw)
    assert "exponent" not in repr(raw)


def check_aip3_compatibility() -> None:
    left = container(Leaf(), container(Leaf()))
    right = container(container(Leaf()), Leaf())
    assert left != right
    assert erase_key(left) == erase_key(right)


def check_multiplicity() -> None:
    assert erase_key(container(Leaf())) != erase_key(container(Leaf(), Leaf()))
    assert erase_key(container(Leaf(), Leaf())) != erase_key(
        container(Leaf(), Leaf(), Leaf())
    )


@dataclass(frozen=True)
class OperatorCounts:
    sprout: int = 0
    shed: int = 0
    graft: int = 0
    prune: int = 0


def check_operator_commutation(corpus: list[PetraShape]) -> OperatorCounts:
    sprout_count = 0
    shed_count = 0
    graft_count = 0
    prune_count = 0

    for representative in corpus:
        for shape in ordered_variants(representative):
            before = erase_ordered(shape)

            # SPROUT: root anchor is always legal; nested targets are legal only
            # when the selected current term owns a materialized Container.
            result = apply_sprout(shape, ExplicitTarget(Address()))
            assert isinstance(result, SuccessfulResult)
            assert erase_key(result.after_shape) == abstract_key(_sprout(before, ()))
            sprout_count += 1

            for path in _container_paths(shape):
                if not path:
                    continue
                result = apply_sprout(shape, ExplicitTarget(Address(indices=path)))
                assert isinstance(result, SuccessfulResult)
                assert erase_key(result.after_shape) == abstract_key(_sprout(before, path))
                sprout_count += 1

            # SHED: every terminal child occurrence is an explicit candidate.
            for path in _leaf_term_paths(shape):
                result = apply_shed(shape, ExplicitTarget(Address(indices=path)))
                assert isinstance(result, SuccessfulResult)
                assert erase_key(result.after_shape) == abstract_key(_shed(before, path))
                shed_count += 1

            # GRAFT: every terminal child occurrence exposes the current latent
            # slot, but the abstract effect is simply Terminal -> Composite(T).
            for path in _leaf_term_paths(shape):
                result = apply_graft(
                    shape,
                    ExplicitTarget(Address(indices=path, is_slot=True)),
                )
                assert isinstance(result, SuccessfulResult)
                assert erase_key(result.after_shape) == abstract_key(_graft(before, path))
                graft_count += 1

            # PRUNE: current explicit target is the terminal child inside a
            # nested singleton composite; the abstract rewrite collapses that
            # singleton composite occurrence directly to Terminal.
            for leaf_path in _prune_target_paths(shape):
                result = apply_prune(
                    shape,
                    ExplicitTarget(Address(indices=leaf_path)),
                )
                assert isinstance(result, SuccessfulResult)
                parent_path = leaf_path[:-1]
                assert erase_key(result.after_shape) == abstract_key(
                    _prune(before, parent_path)
                )
                prune_count += 1

    return OperatorCounts(
        sprout=sprout_count,
        shed=shed_count,
        graft=graft_count,
        prune=prune_count,
    )


def bounded_collision_search(corpus: list[PetraShape]) -> tuple[int, int, int]:
    """Check that bounded collisions are exactly intended order erasures."""

    variants = 0
    classes: dict[AbstractKey, set[str]] = {}

    for representative in corpus:
        for variant in ordered_variants(representative):
            variants += 1
            key = erase_key(variant)
            classes.setdefault(key, set()).add(repr(erase_ordered(variant)))

    assert len(classes) == len(corpus)
    return len(corpus), variants, len(classes)


def main() -> int:
    check_wrapper_erasure()
    check_aip3_compatibility()
    check_multiplicity()

    corpus = representative_corpus(max_depth=2, max_width=3)
    counts = check_operator_commutation(corpus)
    representatives, variants, classes = bounded_collision_search(corpus)

    print("AIP2_WRAPPER_ERASURE=PASS")
    print("AIP2_AIP3_COMPATIBILITY=PASS")
    print("AIP2_MULTIPLICITY=PASS")
    print("AIP2_OPERATOR_COMMUTATION=PASS")
    print("AIP2_BOUNDED_COLLISION_SEARCH=PASS")
    print(f"AIP2_SPROUT_CASES={counts.sprout}")
    print(f"AIP2_SHED_CASES={counts.shed}")
    print(f"AIP2_GRAFT_CASES={counts.graft}")
    print(f"AIP2_PRUNE_CASES={counts.prune}")
    print(f"AIP2_REPRESENTATIVES={representatives}")
    print(f"AIP2_ORDERED_VARIANTS={variants}")
    print(f"AIP2_ABSTRACT_CLASSES={classes}")
    print("AIP2_SCOPE=max_depth=2,max_width=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
