from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from math import gcd
from typing import Literal

from .core import prime_factorization
from .object_model import PETObject, pet_object_from_int


PETRootBaseStatus = Literal["exact", "non-power"]


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
        base_value=base_value,
        base_object=pet_object_from_int(base_value),
    )
