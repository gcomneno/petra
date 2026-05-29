from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .core import prime_factorization


class PETAddressError(LookupError):
    """Raised when a structural PET object address cannot be resolved."""


PETObjectRole = Literal["root", "child"]
PETObjectKind = Literal["atomic", "composite"]


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


def _children_from_int(n: int, parent_address: tuple[int, ...]) -> tuple[PETObject, ...]:
    return tuple(
        _make_child_from_factor(
            prime=prime,
            exponent=exponent,
            address=(*parent_address, prime),
        )
        for prime, exponent in prime_factorization(n)
    )


def pet_object_from_int(n: int) -> PETObject:
    """Build a PET/PEG 2.0 recursive object from an integer."""

    if n < 2:
        raise ValueError("n must be >= 2")

    return PETObject(
        value=n,
        role="root",
        kind="composite",
        prime_label=None,
        address=(),
        children=_children_from_int(n, ()),
    )


def structurally_equivalent(left: PETObject, right: PETObject) -> bool:
    """Return whether two PET objects have the same recursive structure."""

    return left.structural_signature() == right.structural_signature()
