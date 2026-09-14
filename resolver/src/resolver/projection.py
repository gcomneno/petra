"""Optional numeric projection layer for the Resolver.

This module is a derived layer. It computes a numeric value from a
canonical PETRA shape and an explicit prime assignment. The assignment
is supplied by the caller; the Resolver does not derive it.

The projection follows the shape-first direction: the shape is primary,
and the numeric value is a derived interpretation. This module does not
extend PETRA semantics and does not influence operator behavior.

To keep the layer practical, the projection refuses to materialize
values that would exceed a fixed exponent bound. The bound is not a
mathematical property of the shape: it is a guard against values whose
decimal expansion has millions of digits.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from petra import Container, Leaf, PetraShape, validate_shape

_MAX_EXPONENT = 10**6
_MAX_RESULT_BITS = 10_000


class ProjectionError(ValueError):
    """A deterministic projection failure."""


class ProjectionLimitExceeded(ProjectionError):
    """The projected value would exceed the projection bound."""


@dataclass(frozen=True)
class PrimeKey:
    """An explicit assignment from positional addresses to primes."""

    assignments: Mapping[tuple[int, ...], int]

    def __post_init__(self) -> None:
        frozen = MappingProxyType(dict(self.assignments))
        object.__setattr__(self, "assignments", frozen)

        for address, prime in frozen.items():
            if not isinstance(address, tuple):
                raise TypeError("key addresses must be tuples")
            for index in address:
                if isinstance(index, bool) or not isinstance(index, int):
                    raise TypeError("key address indices must be ints")
                if index < 0:
                    raise ValueError("key address indices must be >= 0")
            if isinstance(prime, bool) or not isinstance(prime, int):
                raise TypeError("key primes must be ints")
            if prime < 2:
                raise ValueError("key primes must be >= 2")

    def get(self, address: tuple[int, ...]) -> int:
        prime = self.assignments.get(address)
        if prime is None:
            raise ProjectionError(
                f"missing prime assignment for address {address}"
            )
        return prime


def project(shape: PetraShape, key: PrimeKey) -> int:
    """Compute the numeric value of a shape under an explicit prime key."""

    if not isinstance(key, PrimeKey):
        raise TypeError("key must be a PrimeKey")

    validate_shape(shape)

    return _project(shape, key, ())


def _project(
    shape: PetraShape,
    key: PrimeKey,
    prefix: tuple[int, ...],
) -> int:
    if isinstance(shape, Leaf):
        return 1

    assert isinstance(shape, Container)
    product = 1
    for index, term in enumerate(shape.terms):
        address = (*prefix, index)
        prime = key.get(address)
        exponent = _project(term.exponent, key, address)
        if exponent > _MAX_EXPONENT:
            raise ProjectionLimitExceeded(
                "exponent exceeds the projection bound "
                f"{_MAX_EXPONENT}"
            )
        product *= prime ** exponent
        if product.bit_length() > _MAX_RESULT_BITS:
            raise ProjectionLimitExceeded(
                "result exceeds the projection bound "
                f"({_MAX_RESULT_BITS} bits)"
            )
    return product
