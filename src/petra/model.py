"""Immutable shape-first object model for PETRA."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias


@dataclass(frozen=True)
class Leaf:
    """The unique terminal PETRA shape."""


@dataclass(frozen=True)
class Root:
    """A container-scoped canonical positional root identity."""

    rank: int

    def __post_init__(self) -> None:
        if isinstance(self.rank, bool) or not isinstance(self.rank, int):
            raise TypeError("root rank must be an int")
        if self.rank < 0:
            raise ValueError("root rank must be >= 0")

    @property
    def name(self) -> str:
        """Return the canonical textual spelling of this rank."""

        return f"r{self.rank}"


@dataclass(frozen=True)
class Term:
    """One positional root and its complete PETRA exponent target."""

    root: Root
    exponent: PetraShape

    def __post_init__(self) -> None:
        if not isinstance(self.root, Root):
            raise TypeError("term root must be a Root")
        if not _is_shape(self.exponent):
            raise TypeError(
                "term exponent must be a complete PETRA shape"
            )


@dataclass(frozen=True)
class Container:
    """An ordered, non-empty sequence of visible PETRA terms."""

    terms: tuple[Term, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.terms, tuple):
            raise TypeError("container terms must be a tuple")
        if not self.terms:
            raise ValueError("container terms must be non-empty")
        if not all(isinstance(term, Term) for term in self.terms):
            raise TypeError("container terms must contain only Term objects")


PetraShape: TypeAlias = Leaf | Container
CanonicalData: TypeAlias = (
    tuple[str]
    | tuple[str, tuple[tuple[str, "CanonicalData"], ...]]
)


def _is_shape(value: object) -> bool:
    return isinstance(value, (Leaf, Container))


def _require_shape(value: object) -> PetraShape:
    if not _is_shape(value):
        raise TypeError("expected a PETRA Leaf or Container")
    return value


def validate_shape(shape: PetraShape) -> None:
    """Validate grammar and canonical positional ranks recursively."""

    current = _require_shape(shape)

    if isinstance(current, Leaf):
        return

    for expected_rank, term in enumerate(current.terms):
        expected_name = f"r{expected_rank}"

        if term.root.rank != expected_rank:
            raise ValueError(
                "non-canonical root rank: "
                f"expected {expected_name}, got {term.root.name}"
            )

        validate_shape(term.exponent)


def normalize_shape(shape: PetraShape) -> PetraShape:
    """Return a recursively rank-normalized shape without reordering."""

    current = _require_shape(shape)

    if isinstance(current, Leaf):
        return current

    return Container(
        terms=tuple(
            Term(
                root=Root(rank),
                exponent=normalize_shape(term.exponent),
            )
            for rank, term in enumerate(current.terms)
        )
    )


def to_canonical_data(shape: PetraShape) -> CanonicalData:
    """Return deterministic immutable fixture/debug data.

    This representation is intentionally internal. It is not the future
    PETRA invocation, result, or persistence schema.
    """

    current = _require_shape(shape)
    validate_shape(current)

    if isinstance(current, Leaf):
        return ("leaf",)

    return (
        "container",
        tuple(
            (
                term.root.name,
                to_canonical_data(term.exponent),
            )
            for term in current.terms
        ),
    )


__all__ = [
    "CanonicalData",
    "Container",
    "Leaf",
    "PetraShape",
    "Root",
    "Term",
    "normalize_shape",
    "to_canonical_data",
    "validate_shape",
]
