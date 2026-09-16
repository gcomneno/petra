"""Composition and decomposition on canonical PETRA shapes.

This module defines two derived operations:

- `struct(A, B)`: the set of shapes obtained by grafting `B` onto
  every attachment point of `A`. An attachment point is a term whose
  exponent is currently the implicit leaf, plus append/prepend at the
  root, plus (when `inner=True`) append/prepend at every inner
  container.
- `destruct(A)`: the set of triples `(piece, rest, kind)` obtained by
  detaching one detachable point of `A`. Two kinds:

  - `"exponent"`: a term whose exponent is not `Leaf`. `piece` is the
    explicit exponent; `rest` is `A` with that exponent reduced to
    `Leaf`.
  - `"father"`: a term inside a container with at least 2 terms.
    `piece` is the exponent of that term (possibly `Leaf`); `rest` is
    `A` without that term, with ranks recomputed.

  One level only; recursion is not applied.

The leaf is implicit and is never detached: it is the neutral
placeholder. Composition makes it explicit; decomposition makes it
implicit again.

These operations are not canonical PETRA operators. They are analytic:
they consume shapes and produce shapes, and do not modify the runtime.
"""

from __future__ import annotations

from petra import Container, Leaf, PetraShape, Root, Term, node_count, validate_shape

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


def _inner_container_addresses(shape: PetraShape) -> list[tuple[int, ...]]:
    """Return addresses of every container reachable as an exponent.

    A container is "inner" if it is the exponent of a term, at any
    depth. The root container is not included (its address is `()`).
    """

    if isinstance(shape, Leaf):
        return []
    assert isinstance(shape, Container)
    addresses: list[tuple[int, ...]] = []
    for i, term in enumerate(shape.terms):
        if isinstance(term.exponent, Container):
            here = (i,)
            addresses.append(here)
            for sub in _inner_container_addresses(term.exponent):
                addresses.append((i, *sub))
    return addresses


def _attachment_points(
    shape: PetraShape,
    *,
    inner: bool = False,
) -> list[tuple[str, tuple[int, ...]]]:
    """Return the attachment points of `shape` for `struct`.

    Each point is a pair `(kind, address)` where:

    - `kind = "replace"`: replace the leaf at `address` with a shape.
      Ordered by shallowest-leaf depth ascending, ties left to right.
    - `kind = "append"`: add a new father at the end of `shape`.
      Address is `()`.
    - `kind = "prepend"`: add a new father at the beginning of `shape`.
      Address is `()`.
    - `kind = "inner_append"` / `"inner_prepend"`: add a new father at
      the end / beginning of an inner container. Address selects the
      container. Only included when `inner=True`.

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
    root_points = [("append", ()), ("prepend", ())]
    if not inner:
        return replace_positions + root_points
    inner_points: list[tuple[str, tuple[int, ...]]] = []
    for addr in _inner_container_addresses(shape):
        inner_points.append(("inner_append", addr))
        inner_points.append(("inner_prepend", addr))
    return replace_positions + root_points + inner_points


def _explicit_positions(
    shape: PetraShape,
    prefix: tuple[int, ...] = (),
) -> list[tuple[int, ...]]:
    """Return the addresses of every term whose exponent is not `Leaf`."""

    positions: list[tuple[int, ...]] = []
    if isinstance(shape, Leaf):
        return positions
    assert isinstance(shape, Container)
    for i, term in enumerate(shape.terms):
        here = (*prefix, i)
        if not isinstance(term.exponent, Leaf):
            positions.append(here)
    return positions


def _all_container_addresses(
    shape: PetraShape,
    prefix: tuple[int, ...] = (),
) -> list[tuple[int, ...]]:
    """Return the addresses of every container with at least 2 terms.

    Used by `destruct` to locate the containers from which a father can
    be detached. The address is the empty tuple for the root container.
    """

    if isinstance(shape, Leaf):
        return []
    assert isinstance(shape, Container)
    addresses: list[tuple[int, ...]] = []
    if len(shape.terms) >= 2:
        addresses.append(prefix)
    for i, term in enumerate(shape.terms):
        addresses.extend(
            _all_container_addresses(term.exponent, (*prefix, i))
        )
    return addresses


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


def _remove_father_at(
    shape: PetraShape,
    address: tuple[int, ...],
) -> PetraShape:
    """Return a copy of `shape` without the father at `address`.

    The ranks of the remaining terms are recomputed from zero in order.
    The address must select a term of a container with at least 2 terms,
    otherwise a `ValueError` is raised.
    """

    if not address:
        raise ValueError("address must select a term")
    head, *rest = address
    assert isinstance(shape, Container)
    term = shape.terms[head]
    if not rest:
        remaining = [t for i, t in enumerate(shape.terms) if i != head]
        if not remaining:
            raise ValueError("cannot remove the only father")
        rebuilt = tuple(
            Term(root=Root(i), exponent=t.exponent)
            for i, t in enumerate(remaining)
        )
        return Container(terms=rebuilt)
    new_exponent = _remove_father_at(term.exponent, tuple(rest))
    new_terms = tuple(
        Term(root=t.root, exponent=(new_exponent if i == head else t.exponent))
        for i, t in enumerate(shape.terms)
    )
    return Container(terms=new_terms)


def struct(
    a: PetraShape,
    b: PetraShape,
    *,
    max_nodes: int | None = None,
    inner: bool = False,
) -> frozenset[PetraShape]:
    """Return the set of shapes obtained by grafting `b` onto `a`.

    Every implicit-leaf term of `a` is a possible attachment point, plus
    append/prepend at the root. When `inner=True`, append/prepend at
    every inner container are also included.

    If `max_nodes` is not None, the total node count of all results
    (summed) must not exceed it; otherwise `ValueError` is raised.
    """

    validate_shape(a)
    validate_shape(b)

    # Special case: grafting the bare leaf ○.
    if isinstance(b, Leaf):
        results: set[PetraShape] = {a}
        if not isinstance(a, Leaf):
            assert isinstance(a, Container)
            results.add(_append_father(a, b, at_end=True))
            results.add(_append_father(a, b, at_end=False))
            if inner:
                for addr in _inner_container_addresses(a):
                    results.add(_append_father_at(a, addr, b, at_end=True))
                    results.add(_append_father_at(a, addr, b, at_end=False))
        _check_max_nodes(results, max_nodes)
        return frozenset(results)

    results: set[PetraShape] = set()
    for kind, pos in _attachment_points(a, inner=inner):
        candidate = _apply_attachment(a, kind, pos, b)
        validate_shape(candidate)
        results.add(candidate)
    _check_max_nodes(results, max_nodes)
    return frozenset(results)


def _check_max_nodes(
    results: set[PetraShape],
    max_nodes: int | None,
) -> None:
    if max_nodes is None:
        return
    total = sum(node_count(r) for r in results)
    if total > max_nodes:
        raise ValueError(
            f"struct: total node_count {total} exceeds max_nodes "
            f"{max_nodes}"
        )


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
    - `"inner_append"`: add `b` as a new father at the end of the
      container at `address`.
    - `"inner_prepend"`: add `b` as a new father at the beginning of
      the container at `address`.
    """

    if kind == "replace":
        return _replace_at(a, address, b)
    if kind == "append":
        return _append_father(a, b, at_end=True)
    if kind == "prepend":
        return _append_father(a, b, at_end=False)
    if kind == "inner_append":
        return _append_father_at(a, address, b, at_end=True)
    if kind == "inner_prepend":
        return _append_father_at(a, address, b, at_end=False)
    raise ValueError(f"unknown attachment kind: {kind}")


def _append_father(
    a: PetraShape,
    b: PetraShape,
    *,
    at_end: bool,
) -> PetraShape:
    """Add `b` as a new father of the root container of `a`, at head or tail."""

    if isinstance(a, Leaf):
        new_term = Term(root=Root(0), exponent=b)
        return Container(terms=(new_term,))

    assert isinstance(a, Container)
    existing = list(a.terms)
    new_term = Term(root=Root(0), exponent=b)
    if at_end:
        ordered = existing + [new_term]
    else:
        ordered = [new_term] + existing
    rebuilt = tuple(
        Term(root=Root(i), exponent=term.exponent)
        for i, term in enumerate(ordered)
    )
    return Container(terms=rebuilt)


def _append_father_at(
    shape: PetraShape,
    address: tuple[int, ...],
    b: PetraShape,
    *,
    at_end: bool,
) -> PetraShape:
    """Add `b` as a new father of the inner container at `address`.

    `address` must select a container reachable as an exponent of
    `shape`. The empty address is not allowed here; use
    `_append_father` for the root.
    """

    if not address:
        raise ValueError("address must select an inner container")
    head, *rest = address
    assert isinstance(shape, Container)
    term = shape.terms[head]
    assert isinstance(term.exponent, Container)
    if not rest:
        new_exponent = _append_father(term.exponent, b, at_end=at_end)
    else:
        new_exponent = _append_father_at(term.exponent, tuple(rest), b, at_end=at_end)
    new_terms = tuple(
        Term(root=t.root, exponent=(new_exponent if i == head else t.exponent))
        for i, t in enumerate(shape.terms)
    )
    return Container(terms=new_terms)


def destruct(
    a: PetraShape,
) -> frozenset[tuple[PetraShape, PetraShape, str]]:
    """Return the set of triples `(piece, rest, kind)` from `a`.

    One level only. Two kinds of detachable points:

    - `"exponent"`: a term whose exponent is not `Leaf`. `piece` is the
      explicit exponent; `rest` is `a` with that exponent reduced to
      `Leaf`.
    - `"father"`: a term inside a container with at least 2 terms.
      `piece` is the exponent of that term (possibly `Leaf`); `rest` is
      `a` without that term, with ranks recomputed.

    A shape with no detachable point gives the empty set.
    """

    validate_shape(a)

    results: set[tuple[PetraShape, PetraShape, str]] = set()

    for pos in _explicit_positions(a):
        detached = _extract_at(a, pos)
        reduced = _replace_at(a, pos, Leaf())
        validate_shape(reduced)
        results.add((detached, reduced, "exponent"))

    for container_addr in _all_container_addresses(a):
        if container_addr == ():
            container = a
        else:
            container = _extract_at(a, container_addr)
        assert isinstance(container, Container)
        for i in range(len(container.terms)):
            full_addr = (*container_addr, i)
            piece = _extract_at(a, full_addr)
            try:
                rest = _remove_father_at(a, full_addr)
            except ValueError:
                continue
            validate_shape(rest)
            results.add((piece, rest, "father"))

    return frozenset(results)
