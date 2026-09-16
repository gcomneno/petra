"""Composition and decomposition on canonical PETRA shapes.

This module defines two derived operations:

- `struct(A, B)`: the set of shapes obtained by grafting `B` onto
  every attachment point of `A`. An attachment point is a term whose
  exponent is currently the implicit leaf.
- `destruct(A)`: the set of pairs `(B, C)` obtained by detaching one
  explicit exponent of `A`. One level only; recursion is not applied.

The leaf is implicit and is never detached: it is the neutral
placeholder. Composition makes it explicit; decomposition makes it
implicit again.

These operations are not canonical PETRA operators. They are analytic:
they consume shapes and produce shapes, and do not modify the runtime.
"""

from __future__ import annotations

from petra import Container, Leaf, PetraShape, Root, Term, validate_shape

__all__ = ["destruct", "struct"]


def _term_depth(shape: PetraShape) -> int:
    """Return the depth of the shallowest leaf inside `shape` (Leaf = 0)."""

    if isinstance(shape, Leaf):
        return 0
    assert isinstance(shape, Container)
    best: int | None = None
    for term in shape.terms:
        d = 1 + _term_depth(term.exponent)
        if best is None or d < best:
            best = d
    assert best is not None
    return best


def _attachment_points(shape: PetraShape) -> list[tuple[str, tuple[int, ...]]]:
    """Return the attachment points of `shape` for `struct`.

    Each point is a pair `(kind, address)` where:

    - `kind = "replace"`: replace the leaf at `address` with a shape.
      Ordered by shallowest-leaf depth ascending, ties left to right.
    - `kind = "append"`: add a new father at the end of `shape`.
      Address is `()` (no position needed).
    - `kind = "prepend"`: add a new father at the beginning of `shape`.
      Address is `()` (no position needed).

    Special case: the bare leaf `○` has one attachment point of kind
    `"replace"` at address `()`, representing the mother hook.
    """

    if isinstance(shape, Leaf):
        return [("replace", ())]

    assert isinstance(shape, Container)
    indexed = list(enumerate(shape.terms))
    indexed.sort(key=lambda pair: _term_depth(pair[1].exponent))
    replace_positions = [
        ("replace", (i,))
        for i, term in indexed
        if isinstance(term.exponent, Leaf)
    ]
    return replace_positions + [("append", ()), ("prepend", ())]


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
        return replacement

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


def struct(a: PetraShape, b: PetraShape) -> frozenset[PetraShape]:
    """Return the set of shapes obtained by grafting `b` onto `a`.

    Every implicit-leaf term of `a` is a possible attachment point. For
    each, the implicit leaf is replaced by `b`. The result is a set,
    because `a` may have several attachment points.
    """

    validate_shape(a)
    validate_shape(b)

    # Neutral right: grafting the leaf onto any shape is the identity.
    if isinstance(b, Leaf):
        return frozenset({a})

    results: set[PetraShape] = set()
    for kind, pos in _attachment_points(a):
        candidate = _apply_attachment(a, kind, pos, b)
        validate_shape(candidate)
        results.add(candidate)
    return frozenset(results)


def _apply_attachment(
    a: PetraShape,
    kind: str,
    address: tuple[int, ...],
    b: PetraShape,
) -> PetraShape:
    """Apply one attachment of `b` onto `a`.

    - `"replace"`: replace the leaf at `address` with `b`.
    - `"append"`: add `b` as a new father at the end of `a`'s root container.
    - `"prepend"`: add `b` as a new father at the beginning of `a`'s
      root container.
    """

    if kind == "replace":
        return _replace_at(a, address, b)
    if kind == "append":
        return _append_father(a, b, at_end=True)
    if kind == "prepend":
        return _append_father(a, b, at_end=False)
    raise ValueError(f"unknown attachment kind: {kind}")


def _append_father(
    a: PetraShape,
    b: PetraShape,
    *,
    at_end: bool,
) -> PetraShape:
    """Add `b` as a new father of the root container of `a`, at head or tail.

    The new father is a term with the next rank at the boundary and
    exponent `b`. Ranks are recomputed from zero in order.
    """

    if isinstance(a, Leaf):
        # adding a father to the bare leaf produces a one-father container
        new_term = Term(root=Root(0), exponent=b)
        return Container(terms=(new_term,))

    assert isinstance(a, Container)
    existing = list(a.terms)
    new_term = Term(root=Root(0), exponent=b)
    if at_end:
        ordered = existing + [new_term]
    else:
        ordered = [new_term] + existing
    # recompute ranks from zero in order
    rebuilt = tuple(
        Term(root=Root(i), exponent=term.exponent)
        for i, term in enumerate(ordered)
    )
    return Container(terms=rebuilt)


def destruct(a: PetraShape) -> frozenset[tuple[PetraShape, PetraShape]]:
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
