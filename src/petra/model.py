"""Immutable shape-first object model for PETRA."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias


@dataclass(frozen=True)
class Leaf:
    """The unique terminal PETRA shape."""

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return True

    def __hash__(self) -> int:
        return _leaf_hash()


@dataclass(frozen=True)
class Root:
    """A container-scoped canonical positional root identity."""

    rank: int

    def __post_init__(self) -> None:
        if type(self.rank) is not int:
            raise TypeError("root rank must be an int")
        if self.rank < 0:
            raise ValueError("root rank must be >= 0")

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return self.rank == other.rank

    def __hash__(self) -> int:
        return hash(("petra.root", self.rank))

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

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return _terms_equal(self, other)

    def __hash__(self) -> int:
        return _term_hash(self)


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

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return _shape_equal(self, other)

    def __hash__(self) -> int:
        return _shape_hash(self)


PetraShape: TypeAlias = Leaf | Container
CanonicalData: TypeAlias = (
    tuple[str]
    | tuple[str, tuple[tuple[str, "CanonicalData"], ...]]
)


def _is_shape(value: object) -> bool:
    return isinstance(value, (Leaf, Container))


def _leaf_hash() -> int:
    """Return the structural hash shared by all Leaf instances."""

    return hash(("petra.leaf",))


def _terms_equal(left: Term, right: Term) -> bool:
    """Compare two terms without recursing through their exponents."""

    return left.root == right.root and _shape_equal(
        left.exponent,
        right.exponent,
    )


def _shape_equal(left: PetraShape, right: PetraShape) -> bool:
    """Compare two PETRA shapes with an explicit structural stack."""

    pending: list[tuple[PetraShape, PetraShape]] = [(left, right)]
    compared: set[tuple[int, int]] = set()

    while pending:
        current_left, current_right = pending.pop()
        if current_left is current_right:
            continue
        if type(current_left) is not type(current_right):
            return False

        pair = (id(current_left), id(current_right))
        if pair in compared:
            continue
        compared.add(pair)

        if isinstance(current_left, Leaf):
            continue

        assert isinstance(current_left, Container)
        assert isinstance(current_right, Container)
        if len(current_left.terms) != len(current_right.terms):
            return False

        for left_term, right_term in zip(
            current_left.terms,
            current_right.terms,
        ):
            if type(left_term) is not type(right_term):
                return False
            if left_term.root != right_term.root:
                return False
            pending.append((left_term.exponent, right_term.exponent))

    return True


def _term_hash(term: Term) -> int:
    """Return a structural term hash without hashing its exponent directly."""

    return hash(
        ("petra.term", hash(term.root), _shape_hash(term.exponent))
    )


def _shape_hash(shape: PetraShape) -> int:
    """Return a structural shape hash with an iterative post-order walk."""

    hashes: dict[int, int] = {}
    pending: list[tuple[PetraShape, bool]] = [(shape, False)]

    while pending:
        current, expanded = pending.pop()
        current_id = id(current)
        if current_id in hashes:
            continue

        if isinstance(current, Leaf):
            hashes[current_id] = _leaf_hash()
            continue

        assert isinstance(current, Container)
        if not expanded:
            pending.append((current, True))
            for term in current.terms:
                child = term.exponent
                if id(child) not in hashes:
                    pending.append((child, False))
            continue

        hashes[current_id] = hash(
            (
                "petra.container",
                tuple(
                    hash(
                        (
                            "petra.term",
                            hash(term.root),
                            hashes[id(term.exponent)],
                        )
                    )
                    for term in current.terms
                ),
            )
        )

    return hashes[id(shape)]


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
