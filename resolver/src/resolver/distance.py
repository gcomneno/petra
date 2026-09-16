"""Structural distance between numbers with known factorization.

This module is a derived layer on top of the Resolver. It converts an
integer into its canonical PETRA shape, then delegates to the Resolver
to compute the minimum number of canonical edits between two shapes.

The conversion requires the prime factorization of the input. If the
factorization is not known, the conversion is not possible. This is the
same construction boundary that PETRA declares in its specification: a
shape is built from a known structure, never discovered from an opaque
integer.
"""

from __future__ import annotations

from petra import (
    Container,
    Leaf,
    PetraShape,
    Root,
    Term,
    validate_shape,
)

from .search import ResolverError, resolve


class DistanceError(ValueError):
    """A deterministic structural distance failure."""


def int_to_shape(n: int) -> PetraShape:
    """Return the canonical PETRA shape of a positive integer.

    Requires the prime factorization of ``n``. This function imports
    ``sympy`` lazily so that the rest of the Resolver does not depend on
    it. Raises ``DistanceError`` if ``sympy`` is unavailable or if the
    input is not a positive integer.
    """

    if isinstance(n, bool) or not isinstance(n, int):
        raise DistanceError("expected a positive integer")
    if n < 1:
        raise DistanceError("expected a positive integer")

    if n == 1:
        return Leaf()

    try:
        from sympy import factorint  # type: ignore[import-untyped]
    except ImportError as error:
        raise DistanceError(
            "int_to_shape requires sympy; install with "
            "pip install -e ./resolver[numeric]"
        ) from error

    factors = factorint(n)
    terms: list[Term] = []
    for rank, prime in enumerate(sorted(factors)):
        exponent = factors[prime]
        terms.append(
            Term(
                root=Root(rank),
                exponent=int_to_shape(exponent),
            )
        )

    shape = Container(terms=tuple(terms))
    validate_shape(shape)
    return shape


def structural_distance_numbers(
    a: int,
    b: int,
    *,
    max_depth: int = 30,
    max_nodes: int = 200,
    max_visited: int = 500_000,
) -> int:
    """Return the structural edit distance between two integers."""

    shape_a = int_to_shape(a)
    shape_b = int_to_shape(b)
    return structural_distance_shapes(
        shape_a,
        shape_b,
        max_depth=max_depth,
        max_nodes=max_nodes,
        max_visited=max_visited,
    )


def structural_distance_shapes(
    a: PetraShape,
    b: PetraShape,
    *,
    max_depth: int = 30,
    max_nodes: int = 200,
    max_visited: int = 500_000,
) -> int:
    """Return the structural edit distance between two canonical shapes."""

    if a == b:
        return 0

    try:
        path = resolve(
            a,
            b,
            max_depth=max_depth,
            max_nodes=max_nodes,
            max_visited=max_visited,
        )
    except ResolverError as error:
        raise DistanceError(str(error)) from error

    return path.length

class DistanceCache:
    """Memoized structural distance between canonical shapes.

    Because the canonical operators form an undirected graph (each
    operator has a matching inverse under the shape-first semantics),
    the structural distance is symmetric: ``d(a, b) == d(b, a)``.
    The cache therefore normalizes each lookup to a canonical key.
    """

    def __init__(
        self,
        *,
        max_depth: int = 30,
        max_nodes: int = 200,
        max_visited: int = 500_000,
    ) -> None:
        self._cache: dict[tuple[PetraShape, PetraShape], int] = {}
        self._max_depth = max_depth
        self._max_nodes = max_nodes
        self._max_visited = max_visited
        self.hits = 0
        self.misses = 0

    def distance(self, a: PetraShape, b: PetraShape) -> int:
        if a == b:
            return 0

        key = (a, b) if hash(a) <= hash(b) else (b, a)

        cached = self._cache.get(key)
        if cached is not None:
            self.hits += 1
            return cached

        self.misses += 1
        result = structural_distance_shapes(
            a,
            b,
            max_depth=self._max_depth,
            max_nodes=self._max_nodes,
            max_visited=self._max_visited,
        )
        self._cache[key] = result
        return result

    def distance_numbers(self, a: int, b: int) -> int:
        return self.distance(int_to_shape(a), int_to_shape(b))

    @property
    def size(self) -> int:
        return len(self._cache)
