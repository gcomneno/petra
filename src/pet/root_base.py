from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from math import gcd
from typing import Any, Literal

from .core import prime_factorization
from .object_model import PETObject, pet_object_from_int


PETRootBaseStatus = Literal["exact", "non-power"]


@dataclass(frozen=True)
class PETRootBaseComponent:
    """Local exact root-base component inside a larger PET object.

    Example:

        72 = 2^3 * 3^2

    is not an exact whole-object root-base, but it contains local exact
    root-base components at addresses ``(2,)`` and ``(3,)``.
    """

    value: int
    address: tuple[int, ...]
    prime_label: int
    exponent: int
    exponent_object: PETObject
    base_value: int
    base_object: PETObject

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "address": list(self.address),
            "prime_label": self.prime_label,
            "exponent": self.exponent,
            "exponent_object": self.exponent_object.to_dict(),
            "base_value": self.base_value,
            "base_object": self.base_object.to_dict(),
        }


@dataclass(frozen=True)
class PETRootBase:
    """PET/PEG 2.0 root-base recursion result.

    Root-base recursion asks whether an integer can be represented as:

        N = R^k

    where R is itself a PET/PEG 2.0 object.

    The exact root-base form uses the maximal exponent:

        gcd(prime factor exponents)

    This makes the base structurally minimal with respect to power extraction.
    """

    value: int
    status: PETRootBaseStatus
    exponent: int | None
    exponent_object: PETObject | None
    base_value: int | None
    base_object: PETObject | None

    @property
    def is_exact(self) -> bool:
        return self.status == "exact"

    @property
    def is_power(self) -> bool:
        return self.is_exact

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "status": self.status,
            "exponent": self.exponent,
            "exponent_object": (
                None if self.exponent_object is None else self.exponent_object.to_dict()
            ),
            "base_value": self.base_value,
            "base_object": None if self.base_object is None else self.base_object.to_dict(),
        }


def _gcd_many(values: list[int]) -> int:
    return reduce(gcd, values)


def exact_root_base_from_int(n: int) -> PETRootBase:
    """Return the exact maximal root-base decomposition for n.

    If n is not a perfect power, return status ``non-power``.
    """

    if n < 2:
        raise ValueError("n must be >= 2")

    factors = prime_factorization(n)
    exponent_gcd = _gcd_many([exponent for _, exponent in factors])

    if exponent_gcd <= 1:
        return PETRootBase(
            value=n,
            status="non-power",
            exponent=None,
            exponent_object=None,
            base_value=None,
            base_object=None,
        )

    base_value = 1
    for prime, exponent in factors:
        base_value *= prime ** (exponent // exponent_gcd)

    return PETRootBase(
        value=n,
        status="exact",
        exponent=exponent_gcd,
        exponent_object=pet_object_from_int(exponent_gcd),
        base_value=base_value,
        base_object=pet_object_from_int(base_value),
    )



def partial_root_base_components_from_int(n: int) -> tuple[PETRootBaseComponent, ...]:
    """Return local exact root-base components inside n.

    This does not claim that the whole value is a perfect power.

    It reports child-level components ``p^e`` where ``e > 1``. Each component
    carries both the base and exponent as PET/PEG 2.0 objects.
    """

    if n < 2:
        raise ValueError("n must be >= 2")

    components: list[PETRootBaseComponent] = []

    for prime, exponent in prime_factorization(n):
        if exponent <= 1:
            continue

        value = prime**exponent
        components.append(
            PETRootBaseComponent(
                value=value,
                address=(prime,),
                prime_label=prime,
                exponent=exponent,
                exponent_object=pet_object_from_int(exponent),
                base_value=prime,
                base_object=pet_object_from_int(prime),
            )
        )

    return tuple(components)
