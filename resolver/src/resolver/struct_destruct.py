"""Composition and decomposition on canonical PETRA shapes.

This module defines two derived operations:

- `compose(A, B)`: the set of shapes obtained by grafting `B` onto
  every attachment point of `A`. An attachment point is a term whose
  exponent is currently the implicit leaf.
- `decompose(A)`: the set of pairs `(B, C)` obtained by detaching one
  explicit exponent of `A`. One level only; recursion is not applied.

The leaf is implicit and is never detached: it is the neutral
placeholder. Composition makes it explicit; decomposition makes it
implicit again.

These operations are not canonical PETRA operators. They are analytic:
they consume shapes and produce shapes, and do not modify the runtime.
"""

from __future__ import annotations

from petra import Container, Leaf, PetraShape, Root, Term, validate_shape

__all__ = ["compose", "decompose"]


def _leaf_positions(shape: PetraShape) -> list[tuple[int, ...]]:
    """Return the addresses of the implicit-leaf terms of `shape`.

    An implicit-leaf term is a term of the root container whose exponent
    is `Leaf`. Only the first level is considered: the interior of an
    explicit exponent is not an attachment point.

    Addresses are tuples of indices from the root, so `(i,)` for the
    i-th term of the root container.
    """

    positions: list[tuple[int, ...]] = []
    if isinstance(shape, Leaf):
        return positions
    assert isinstance(shape, Container)
    for i, term in enumerate(shape.terms):
        if isinstance(term.exponent, Leaf):
            positions.append((i,))
    return positions


def _explicit_positions(shape: PetraShape, prefix: tuple[int, ...] = ()) -> list[tuple[int, ...]]:
    """Return the addresses of every term whose exponent is not `Leaf`."""

    positions: list[tuple[int, ...]] = []
    if isinstance(shape, Leaf):
        return positions
    assert isinstance(shape, Container)
    for i, term in enumerate(shape.terms):
        here = (*prefix, i)
        if not isinstance(term.exponent, Leaf):
            positions.append(here)
            # one level only: do NOT recurse into this exponent
    return positions


def _replace_at(
    shape: PetraShape,
    address: tuple[int, ...],
    replacement: PetraShape,
) -> PetraShape:
    """Return a copy of `shape` with the term at `address` replaced by `replacement`.

    `address` selects a term (index inside a container, possibly nested).
    The replacement replaces the *exponent* of that term, keeping the root.
    """

    if not address:
        raise ValueError("address must select a term")

    head, *rest = address
    assert isinstance(shape, Container)
    term = shape.terms[head]
    if not rest:
        new_term = Term(root=term.root, exponent=replacement)
    else:
        new_exponent = _replace_at(term.exponent, tuple(rest), replacement)
        new_term = Term(root=term.root, exponent=new_exponent)
    new_terms = tuple(
        new_term if i == head else shape.terms[i]
        for i in range(len(shape.terms))
    )
    return Container(terms=new_terms)


def _extract_at(shape: PetraShape, address: tuple[int, ...]) -> PetraShape:
    """Return the exponent at `address` (which must be explicit)."""

    if not address:
        raise ValueError("address must select a term")
    head, *rest = address
    assert isinstance(shape, Container)
    term = shape.terms[head]
    if not rest:
        return term.exponent
    return _extract_at(term.exponent, tuple(rest))


def compose(a: PetraShape, b: PetraShape) -> frozenset[PetraShape]:
    """Return the set of shapes obtained by grafting `b` onto `a`.

    Every implicit-leaf term of `a` is a possible attachment point. For
    each, the implicit leaf is replaced by `b`. The result is a set,
    because `a` may have several attachment points.
    """

    validate_shape(a)
    validate_shape(b)

    results: set[PetraShape] = set()
    for pos in _leaf_positions(a):
        candidate = _replace_at(a, pos, b)
        validate_shape(candidate)
        results.add(candidate)
    return frozenset(results)


def decompose(a: PetraShape) -> frozenset[tuple[PetraShape, PetraShape]]:
    """Return the set of pairs `(b, c)` obtained by detaching one explicit exponent from `a`.

    One level only. `b` is `a` with the exponent reduced to a leaf; `c`
    is the detached exponent. A shape with no explicit exponents gives
    the empty set.
    """

    validate_shape(a)

    pairs: set[tuple[PetraShape, PetraShape]] = set()
    for pos in _explicit_positions(a):
        detached = _extract_at(a, pos)
        reduced = _replace_at(a, pos, Leaf())
        validate_shape(reduced)
        pairs.add((reduced, detached))
    return frozenset(pairs)
