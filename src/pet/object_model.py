from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .core import PET, PETExp, decode, prime_factorization, validate


class PETAddressError(LookupError):
    """Raised when a structural PET object address cannot be resolved."""


PETObjectRole = Literal["root", "child"]
PETObjectKind = Literal["atomic", "composite"]
PETAddressResolution = Literal["valid", "missing", "blocked-at-leaf"]
PETAddressOutcome = Literal[
    "stable",
    "created",
    "destroyed",
    "retargeted",
    "blocked-at-leaf",
    "missing",
]


@dataclass(frozen=True)
class PETAddressComparison:
    """Comparison of one structural address across two PET objects."""

    address: tuple[int, ...]
    outcome: PETAddressOutcome
    before_resolution: PETAddressResolution
    after_resolution: PETAddressResolution
    before_object: "PETObject | None"
    after_object: "PETObject | None"

    def to_dict(self) -> dict[str, Any]:
        return {
            "address": list(self.address),
            "outcome": self.outcome,
            "before_resolution": self.before_resolution,
            "after_resolution": self.after_resolution,
            "before_object": (
                None if self.before_object is None else self.before_object.to_dict()
            ),
            "after_object": (
                None if self.after_object is None else self.after_object.to_dict()
            ),
        }


@dataclass(frozen=True)
class PETObject:
    """PET/PEG 2.0 recursive object core.

    This is the PET/PEG 2.0 semantic object model, not the PET 1.0 tree
    representation.

    The legacy PET 1.0 tree may be used elsewhere during migration, but this
    type defines the new object vocabulary:

    - root vs child role
    - atomic vs composite kind
    - represented value
    - structural address
    - recursive children
    """

    value: int
    role: PETObjectRole
    kind: PETObjectKind
    address: tuple[int, ...]
    children: tuple["PETObject", ...] = ()
    prime_label: int | None = None

    @property
    def is_root(self) -> bool:
        return self.role == "root"

    @property
    def is_child(self) -> bool:
        return self.role == "child"

    @property
    def is_atomic(self) -> bool:
        return self.kind == "atomic"

    @property
    def is_composite(self) -> bool:
        return self.kind == "composite"

    def structural_signature(self) -> tuple[Any, ...]:
        """Return a value-independent recursive structure signature."""

        return tuple(
            sorted(
                (child.structural_signature() for child in self.children),
                key=repr,
            )
        )

    def walk(self) -> tuple["PETObject", ...]:
        """Return this object and all descendants in deterministic preorder."""

        descendants: list[PETObject] = [self]

        for child in self.children:
            descendants.extend(child.walk())

        return tuple(descendants)

    def addresses(self) -> tuple[tuple[int, ...], ...]:
        """Return all valid structural addresses in this object."""

        return tuple(obj.address for obj in self.walk())

    def address_map(self) -> dict[tuple[int, ...], "PETObject"]:
        """Return a mapping from valid structural address to selected object."""

        mapping: dict[tuple[int, ...], PETObject] = {}

        for obj in self.walk():
            if obj.address in mapping:
                raise ValueError(f"duplicate PET object address: {obj.address!r}")
            mapping[obj.address] = obj

        return mapping

    def has_address(self, address: tuple[int, ...]) -> bool:
        """Return whether an address is valid for this object."""

        return address in self.address_map()

    def address_resolution(self, address: tuple[int, ...]) -> PETAddressResolution:
        """Return whether an address is valid, missing, or blocked at a leaf."""

        if address in self.address_map():
            return "valid"

        current = self

        for index, prime in enumerate(address):
            matching_child = next(
                (child for child in current.children if child.prime_label == prime),
                None,
            )

            if matching_child is None:
                return "missing"

            if index < len(address) - 1 and matching_child.is_atomic:
                return "blocked-at-leaf"

            current = matching_child

        return "missing"

    def structural_identity_key(self) -> tuple[Any, ...]:
        """Return a concrete recursive identity key for this object.

        Unlike ``structural_signature()``, this key preserves role, kind,
        address, and prime labels. It identifies this concrete addressed object
        structure rather than only the prime-independent shape.
        """

        return (
            self.role,
            self.kind,
            self.prime_label,
            self.address,
            tuple(child.structural_identity_key() for child in self.children),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "role": self.role,
            "kind": self.kind,
            "prime_label": self.prime_label,
            "address": list(self.address),
            "children": [child.to_dict() for child in self.children],
        }

    def at(self, address: tuple[int, ...]) -> "PETObject":
        """Return the PET object at a structural address.

        The root object is addressed by ``()``. Child addresses are prime-label
        paths such as ``(2,)`` or ``(2, 2)``.
        """

        if address == self.address:
            return self

        if not address[: len(self.address)] == self.address:
            raise PETAddressError(
                f"address {address!r} is outside object rooted at {self.address!r}"
            )

        for child in self.children:
            if address[: len(child.address)] == child.address:
                return child.at(address)

        raise PETAddressError(f"address {address!r} not found")


def _make_child_from_factor(
    prime: int,
    exponent: int,
    address: tuple[int, ...],
) -> PETObject:
    value = prime**exponent

    if exponent == 1:
        return PETObject(
            value=value,
            role="child",
            kind="atomic",
            prime_label=prime,
            address=address,
            children=(),
        )

    return PETObject(
        value=value,
        role="child",
        kind="composite",
        prime_label=prime,
        address=address,
        children=_children_from_int(exponent, address),
    )


def _children_from_int(
    n: int, parent_address: tuple[int, ...]
) -> tuple[PETObject, ...]:
    return tuple(
        _make_child_from_factor(
            prime=prime,
            exponent=exponent,
            address=(*parent_address, prime),
        )
        for prime, exponent in prime_factorization(n)
    )


def pet_object_from_int(n: int) -> PETObject:
    """Build a PET/PEG 2.0 recursive object from an integer.

    ``1`` is the canonical generative seed object: a composite root with no
    children. It is not a factored value target; it is the empty PET root from
    which structural routes may be composed.
    """

    if n < 1:
        raise ValueError("n must be >= 1")

    return PETObject(
        value=n,
        role="root",
        kind="composite",
        prime_label=None,
        address=(),
        children=() if n == 1 else _children_from_int(n, ()),
    )


def _legacy_tree_from_children(children: tuple[PETObject, ...]) -> PET:
    tree: PET = []

    for child in children:
        if child.prime_label is None:
            raise ValueError("child PET objects must have a prime label")

        exp_repr: PETExp
        if child.is_atomic:
            exp_repr = None
        else:
            exp_repr = _legacy_tree_from_children(child.children)

        tree.append((child.prime_label, exp_repr))

    return tree


def pet_object_to_legacy_tree(obj: PETObject) -> PET:
    """Convert a PET/PEG 2.0 object into the legacy PET tree representation.

    This is a migration bridge, not the PET/PEG 2.0 conceptual core.
    """

    if obj.prime_label is None:
        tree = _legacy_tree_from_children(obj.children)
    else:
        exp_repr: PETExp = (
            None if obj.is_atomic else _legacy_tree_from_children(obj.children)
        )
        tree = [(obj.prime_label, exp_repr)]

    validate(tree)
    return tree


def pet_object_from_legacy_tree(tree: PET) -> PETObject:
    """Convert a legacy PET tree into a PET/PEG 2.0 object.

    This rebuilds through the represented integer value.
    """

    validate(tree)
    return pet_object_from_int(decode(tree))


def structurally_equivalent(left: PETObject, right: PETObject) -> bool:
    """Return whether two PET objects have the same recursive structure."""

    return left.structural_signature() == right.structural_signature()


def compare_address(
    before: PETObject,
    after: PETObject,
    address: tuple[int, ...],
) -> PETAddressComparison:
    """Classify one structural address across two PET objects."""

    before_resolution = before.address_resolution(address)
    after_resolution = after.address_resolution(address)

    before_object = before.at(address) if before_resolution == "valid" else None
    after_object = after.at(address) if after_resolution == "valid" else None

    if before_resolution == "valid" and after_resolution == "valid":
        if before_object is None or after_object is None:
            raise AssertionError("valid address resolution must yield objects")

        outcome: PETAddressOutcome = (
            "stable"
            if before_object.structural_identity_key()
            == after_object.structural_identity_key()
            else "retargeted"
        )
    elif before_resolution != "valid" and after_resolution == "valid":
        outcome = "created"
    elif before_resolution == "valid" and after_resolution != "valid":
        outcome = (
            "blocked-at-leaf" if after_resolution == "blocked-at-leaf" else "destroyed"
        )
    elif (
        before_resolution == "blocked-at-leaf" or after_resolution == "blocked-at-leaf"
    ):
        outcome = "blocked-at-leaf"
    else:
        outcome = "missing"

    return PETAddressComparison(
        address=address,
        outcome=outcome,
        before_resolution=before_resolution,
        after_resolution=after_resolution,
        before_object=before_object,
        after_object=after_object,
    )
