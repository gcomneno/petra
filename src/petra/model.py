"""Immutable shape-first object model for PETRA."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias, TypeGuard


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


def _is_shape(value: object) -> TypeGuard[PetraShape]:
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
            current_right.terms, strict=False,
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
    """Return a structural shape hash with an iterative post-order walk.

    Container hashes are cached on the object itself via an internal
    non-dataclass attribute. Because PETRA shapes are immutable, the hash
    of a Container never changes during its lifetime. The cache is
    garbage-collected together with the Container, so there is no risk of
    identity reuse or cross-call contamination.
    """

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

        cached = current.__dict__.get("_petra_hash_cache")
        if cached is not None:
            hashes[current_id] = cached
            continue

        if not expanded:
            pending.append((current, True))
            for term in current.terms:
                child = term.exponent
                if id(child) not in hashes:
                    pending.append((child, False))
            continue

        result = hash(
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
        hashes[current_id] = result
        object.__setattr__(current, "_petra_hash_cache", result)

    return hashes[id(shape)]


def _require_shape(value: object) -> PetraShape:
    if not _is_shape(value):
        raise TypeError("expected a PETRA Leaf or Container")
    return value


def validate_shape(shape: PetraShape) -> None:
    """Validate grammar and canonical ranks without call-stack recursion.

    Validation results are memoized on the shape object itself via an
    internal non-dataclass attribute. Because PETRA shapes are immutable,
    a shape that has already been validated never needs to be re-validated.
    This reduces repeated validation of the same object from O(N) to O(1).
    """

    current = _require_shape(shape)

    if current.__dict__.get("_petra_validated"):
        return

    pending: list[tuple[PetraShape, int]] = [(current, 0)]

    while pending:
        node, next_term = pending.pop()

        if isinstance(node, Leaf):
            object.__setattr__(node, "_petra_validated", True)
            continue

        if node.__dict__.get("_petra_validated"):
            continue

        if next_term >= len(node.terms):
            object.__setattr__(node, "_petra_validated", True)
            continue

        term = node.terms[next_term]
        expected_name = f"r{next_term}"

        if term.root.rank != next_term:
            raise ValueError(
                "non-canonical root rank: "
                f"expected {expected_name}, got {term.root.name}"
            )

        # Match the recursive traversal contract exactly: finish validating
        # this exponent before inspecting the next sibling term.
        pending.append((node, next_term + 1))
        pending.append((_require_shape(term.exponent), 0))


def normalize_shape(shape: PetraShape) -> PetraShape:
    """Return a rank-normalized shape using iterative post-order traversal."""

    current = _require_shape(shape)
    normalized: dict[int, PetraShape] = {}
    pending: list[tuple[PetraShape, bool]] = [(current, False)]

    while pending:
        node, expanded = pending.pop()
        node_id = id(node)

        if node_id in normalized:
            continue

        if isinstance(node, Leaf):
            normalized[node_id] = node
            continue

        if not expanded:
            pending.append((node, True))
            for term in reversed(node.terms):
                child = _require_shape(term.exponent)
                if id(child) not in normalized:
                    pending.append((child, False))
            continue

        normalized[node_id] = Container(
            terms=tuple(
                Term(
                    root=Root(rank),
                    exponent=normalized[id(term.exponent)],
                )
                for rank, term in enumerate(node.terms)
            )
        )

    return normalized[id(current)]


def to_canonical_data(shape: PetraShape) -> CanonicalData:
    """Return deterministic immutable fixture/debug data.

    This representation is intentionally internal. It is not the future
    PETRA invocation, result, or persistence schema.
    """

    current = _require_shape(shape)
    validate_shape(current)

    data: dict[int, CanonicalData] = {}
    pending: list[tuple[PetraShape, bool]] = [(current, False)]

    while pending:
        node, expanded = pending.pop()
        node_id = id(node)

        if node_id in data:
            continue

        if isinstance(node, Leaf):
            data[node_id] = ("leaf",)
            continue

        if not expanded:
            pending.append((node, True))
            for term in reversed(node.terms):
                child = _require_shape(term.exponent)
                if id(child) not in data:
                    pending.append((child, False))
            continue

        data[node_id] = (
            "container",
            tuple(
                (
                    term.root.name,
                    data[id(term.exponent)],
                )
                for term in node.terms
            ),
        )

    return data[id(current)]


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
