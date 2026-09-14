"""Canonical positional structural addresses for PETRA."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TypeAlias

from .model import Leaf, PetraShape, Term, validate_shape

ADDRESS_MALFORMED = "address-malformed"
ADDRESS_OUT_OF_RANGE = "address-out-of-range"
ADDRESS_CROSSES_LEAF = "address-crosses-leaf"

_ADDRESS_REASONS = frozenset(
    {
        ADDRESS_MALFORMED,
        ADDRESS_OUT_OF_RANGE,
        ADDRESS_CROSSES_LEAF,
    }
)

_TERM_ADDRESS_PATTERN = re.compile(
    r"@/(?:0|[1-9][0-9]*)(?:/(?:0|[1-9][0-9]*))*"
)


class AddressError(ValueError):
    """A deterministic generic PETRA address failure."""

    def __init__(self, reason: str) -> None:
        if not isinstance(reason, str):
            raise TypeError("address reason must be a str")

        if reason not in _ADDRESS_REASONS:
            raise ValueError(f"unknown address reason: {reason}")

        self.reason = reason
        super().__init__(reason)


@dataclass(frozen=True)
class Address:
    """One canonical positional PETRA address."""

    indices: tuple[int, ...] = ()
    is_slot: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.indices, tuple):
            raise TypeError("address indices must be a tuple")

        for index in self.indices:
            if isinstance(index, bool) or not isinstance(index, int):
                raise TypeError("address indices must be integers")
            if index < 0:
                raise ValueError("address indices must be >= 0")

        if not isinstance(self.is_slot, bool):
            raise TypeError("address is_slot must be a bool")

        if self.is_slot and not self.indices:
            raise ValueError("the root anchor cannot be a slot address")

    @property
    def kind(self) -> str:
        """Return the structural address kind."""

        if self.is_slot:
            return "slot"
        if self.indices:
            return "term"
        return "anchor"

    def __str__(self) -> str:
        return render_address(self)


@dataclass(frozen=True)
class ResolvedAnchor:
    """The semantic root anchor in one pre-rewrite shape state."""

    address: Address
    shape: PetraShape

    def __post_init__(self) -> None:
        if not isinstance(self.address, Address):
            raise TypeError(
                "resolved anchor address must be an Address"
            )
        if self.address.kind != "anchor":
            raise ValueError(
                "resolved anchor requires an anchor address"
            )

        validate_shape(self.shape)

    @property
    def kind(self) -> str:
        return "anchor"


@dataclass(frozen=True)
class ResolvedTerm:
    """One term selected in a pre-rewrite shape state."""

    address: Address
    term: Term

    def __post_init__(self) -> None:
        if not isinstance(self.address, Address):
            raise TypeError(
                "resolved term address must be an Address"
            )
        if self.address.kind != "term":
            raise ValueError(
                "resolved term requires a term address"
            )
        if not isinstance(self.term, Term):
            raise TypeError(
                "resolved term value must be a Term"
            )
        if self.term.root.rank != self.address.indices[-1]:
            raise ValueError(
                "resolved term rank does not match address"
            )

    @property
    def kind(self) -> str:
        return "term"


@dataclass(frozen=True)
class ResolvedSlot:
    """The exponent relation owned by one selected term."""

    address: Address
    owner: Term
    target: PetraShape

    def __post_init__(self) -> None:
        if not isinstance(self.address, Address):
            raise TypeError(
                "resolved slot address must be an Address"
            )
        if self.address.kind != "slot":
            raise ValueError(
                "resolved slot requires a slot address"
            )
        if not isinstance(self.owner, Term):
            raise TypeError(
                "resolved slot owner must be a Term"
            )
        if self.owner.root.rank != self.address.indices[-1]:
            raise ValueError(
                "resolved slot owner rank does not match address"
            )
        if self.target is not self.owner.exponent:
            raise ValueError(
                "resolved slot target must be the owner exponent"
            )

    @property
    def kind(self) -> str:
        return "slot"


ResolvedAddress: TypeAlias = (
    ResolvedAnchor | ResolvedTerm | ResolvedSlot
)


def parse_address(value: object) -> Address:
    """Parse one exact canonical PETRA address."""

    if not isinstance(value, str):
        raise AddressError(ADDRESS_MALFORMED)

    if value == "@/":
        return Address()

    is_slot = value.endswith("/^")
    term_text = value[:-2] if is_slot else value

    if _TERM_ADDRESS_PATTERN.fullmatch(term_text) is None:
        raise AddressError(ADDRESS_MALFORMED)

    indices = tuple(
        int(segment)
        for segment in term_text[2:].split("/")
    )

    return Address(indices=indices, is_slot=is_slot)


def render_address(address: Address) -> str:
    """Render one address in canonical serialized form."""

    if not isinstance(address, Address):
        raise TypeError("expected an Address")

    if not address.indices:
        return "@/"

    rendered = "@/" + "/".join(
        str(index)
        for index in address.indices
    )

    if address.is_slot:
        return f"{rendered}/^"

    return rendered


def resolve_address(
    shape: PetraShape,
    address: object,
) -> ResolvedAddress:
    """Resolve an address against one valid pre-rewrite shape."""

    validate_shape(shape)

    parsed = (
        address
        if isinstance(address, Address)
        else parse_address(address)
    )

    if not parsed.indices:
        return ResolvedAnchor(
            address=parsed,
            shape=shape,
        )

    current: PetraShape = shape
    selected: Term | None = None
    final_position = len(parsed.indices) - 1

    for position, index in enumerate(parsed.indices):
        if isinstance(current, Leaf):
            reason = (
                ADDRESS_OUT_OF_RANGE
                if position == 0
                else ADDRESS_CROSSES_LEAF
            )
            raise AddressError(reason)

        if index >= len(current.terms):
            raise AddressError(ADDRESS_OUT_OF_RANGE)

        selected = current.terms[index]

        if position == final_position:
            break

        if isinstance(selected.exponent, Leaf):
            raise AddressError(ADDRESS_CROSSES_LEAF)

        current = selected.exponent

    if selected is None:
        raise AssertionError(
            "a non-anchor address must select one term"
        )

    if parsed.is_slot:
        return ResolvedSlot(
            address=parsed,
            owner=selected,
            target=selected.exponent,
        )

    return ResolvedTerm(
        address=parsed,
        term=selected,
    )


__all__ = [
    "Address",
    "AddressError",
    "ResolvedAnchor",
    "ResolvedSlot",
    "ResolvedTerm",
    "parse_address",
    "render_address",
    "resolve_address",
]
