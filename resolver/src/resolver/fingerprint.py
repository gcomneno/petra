"""Bounded structural fingerprint of exponential sequences.

This module is a derived layer on top of the Resolver and the PETRA core.
It builds the shape of `base^n` directly from the factorization of
`base`, without factorizing the (possibly enormous) value `base^n`; and
it computes the empirical reduction/expansion/stability profile of the
resulting shape sequence over a chosen window.

The mathematical content is documented in
`docs/research/notes/exponential-base-structural-class.md`. In short:

    shape(k^n) = C(r0^shape(e1*n), ..., r_{r-1}^shape(er*n))

for `k = p1^e1 * ... * pr^er`. The fingerprint is a window average of
consecutive transition types, and it is NOT a class invariant: it
depends on the window. This module exposes it as a measurement, not as
a classification.
"""

from __future__ import annotations

from typing import Literal

from petra import Container, PetraShape, Root, Term, node_count

from .distance import int_to_shape

__all__ = [
    "Transition",
    "fingerprint_cumulative",
    "fingerprint_window",
    "transition",
]


Transition = Literal["red", "exp", "stab"]


def _shape_of_power(base: int, n: int) -> PetraShape:
    """Return `shape(base^n)` using only the factorization of `base`.

    Requires ``sympy`` (via ``int_to_shape`` for the exponent shapes).
    """

    from sympy import factorint  # type: ignore[import-untyped]

    factors = factorint(base)
    terms = [
        Term(root=Root(i), exponent=int_to_shape(exp * n))
        for i, exp in enumerate(factors[p] for p in sorted(factors))
    ]
    return Container(terms=tuple(terms))


def transition(a: PetraShape, b: PetraShape) -> Transition:
    """Classify the structural transition from shape `a` to shape `b`.

    - ``"red"``  if `b` has fewer model nodes than `a`;
    - ``"exp"``  if `b` has more model nodes than `a`;
    - ``"stab"`` if both have the same number of model nodes.
    """

    na = node_count(a)
    nb = node_count(b)
    if nb < na:
        return "red"
    if nb > na:
        return "exp"
    return "stab"


def fingerprint_window(
    base: int,
    lo: int,
    hi: int,
) -> tuple[float, float, float]:
    """Return the fingerprint over the transitions in `[lo, hi)`.

    The window covers the transitions `n -> n+1` with
    ``lo <= n <= hi - 1``. The result is
    ``(red_pct, exp_pct, stab_pct)`` in that order, each a percentage
    over the window's transitions.

    Requires ``hi >= lo + 1`` to include at least one transition.
    """

    if hi < lo + 1:
        raise ValueError("window must contain at least one transition")

    counts = {"red": 0, "exp": 0, "stab": 0}
    prev = _shape_of_power(base, lo)
    for n in range(lo + 1, hi + 1):
        current = _shape_of_power(base, n)
        counts[transition(prev, current)] += 1
        prev = current

    total = sum(counts.values())
    return (
        round(100.0 * counts["red"] / total, 2),
        round(100.0 * counts["exp"] / total, 2),
        round(100.0 * counts["stab"] / total, 2),
    )


def fingerprint_cumulative(
    base: int,
    N: int,
) -> tuple[float, float, float]:
    """Return the fingerprint over transitions in `[1, N)`.

    Equivalent to ``fingerprint_window(base, 1, N)``. Provided as a
    semantically explicit alias for the most common use.
    """

    return fingerprint_window(base, 1, N)
