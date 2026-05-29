from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .core import is_prime
from .object_model import PETObject


PETOperatorName = Literal["NEW", "DROP", "INC", "DEC"]
PETOperatorAxis = Literal["X", "Y"]
PETOperatorTargetKind = Literal["parent-support", "selected-root"]


@dataclass(frozen=True)
class PETOperatorTarget:
    """PET/PEG 2.0 operator target semantics.

    This describes whether an operator invocation has a valid target.

    It does not mutate PET objects.
    """

    op: PETOperatorName
    axis: PETOperatorAxis
    target_kind: PETOperatorTargetKind
    address: tuple[int, ...]
    argument: int | None
    valid: bool
    reason: str
    address_resolution: str
    target_object: PETObject | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "op": self.op,
            "axis": self.axis,
            "target_kind": self.target_kind,
            "address": list(self.address),
            "argument": self.argument,
            "valid": self.valid,
            "reason": self.reason,
            "address_resolution": self.address_resolution,
            "target_object": (
                None if self.target_object is None else self.target_object.to_dict()
            ),
        }


def _child_prime_labels(obj: PETObject) -> set[int]:
    return {
        child.prime_label
        for child in obj.children
        if child.prime_label is not None
    }


def _resolve_x_target(
    obj: PETObject,
    *,
    op: Literal["NEW", "DROP"],
    parent_address: tuple[int, ...],
    argument: int,
) -> PETOperatorTarget:
    resolution = obj.address_resolution(parent_address)
    target_object = obj.at(parent_address) if resolution == "valid" else None

    if not is_prime(argument):
        return PETOperatorTarget(
            op=op,
            axis="X",
            target_kind="parent-support",
            address=parent_address,
            argument=argument,
            valid=False,
            reason="argument-not-prime",
            address_resolution=resolution,
            target_object=target_object,
        )

    if resolution != "valid":
        return PETOperatorTarget(
            op=op,
            axis="X",
            target_kind="parent-support",
            address=parent_address,
            argument=argument,
            valid=False,
            reason=f"parent-address-{resolution}",
            address_resolution=resolution,
            target_object=None,
        )

    if target_object is None:
        raise AssertionError("valid parent address must resolve to a target object")

    if target_object.is_atomic:
        return PETOperatorTarget(
            op=op,
            axis="X",
            target_kind="parent-support",
            address=parent_address,
            argument=argument,
            valid=False,
            reason="parent-address-selects-atomic-leaf",
            address_resolution=resolution,
            target_object=target_object,
        )

    child_labels = _child_prime_labels(target_object)

    if op == "NEW":
        valid = argument not in child_labels
        reason = "new-target-valid" if valid else "q-already-in-target-baseline"
    else:
        valid = argument in child_labels
        reason = "drop-target-valid" if valid else "p-not-in-target-baseline"

    return PETOperatorTarget(
        op=op,
        axis="X",
        target_kind="parent-support",
        address=parent_address,
        argument=argument,
        valid=valid,
        reason=reason,
        address_resolution=resolution,
        target_object=target_object,
    )


def _resolve_y_target(
    obj: PETObject,
    *,
    op: Literal["INC", "DEC"],
    address: tuple[int, ...],
) -> PETOperatorTarget:
    if address == ():
        return PETOperatorTarget(
            op=op,
            axis="Y",
            target_kind="selected-root",
            address=address,
            argument=None,
            valid=False,
            reason="empty-address-does-not-select-root",
            address_resolution=obj.address_resolution(address),
            target_object=obj,
        )

    resolution = obj.address_resolution(address)
    target_object = obj.at(address) if resolution == "valid" else None

    if resolution != "valid":
        return PETOperatorTarget(
            op=op,
            axis="Y",
            target_kind="selected-root",
            address=address,
            argument=None,
            valid=False,
            reason=f"address-{resolution}",
            address_resolution=resolution,
            target_object=None,
        )

    if target_object is None:
        raise AssertionError("valid selected address must resolve to a target object")

    if op == "INC":
        return PETOperatorTarget(
            op=op,
            axis="Y",
            target_kind="selected-root",
            address=address,
            argument=None,
            valid=True,
            reason="inc-target-valid",
            address_resolution=resolution,
            target_object=target_object,
        )

    if target_object.is_atomic:
        return PETOperatorTarget(
            op=op,
            axis="Y",
            target_kind="selected-root",
            address=address,
            argument=None,
            valid=False,
            reason="selected-object-is-atomic-leaf",
            address_resolution=resolution,
            target_object=target_object,
        )

    return PETOperatorTarget(
        op=op,
        axis="Y",
        target_kind="selected-root",
        address=address,
        argument=None,
        valid=True,
        reason="dec-target-valid",
        address_resolution=resolution,
        target_object=target_object,
    )


def new_target(
    obj: PETObject,
    parent_address: tuple[int, ...],
    q: int,
) -> PETOperatorTarget:
    return _resolve_x_target(obj, op="NEW", parent_address=parent_address, argument=q)


def drop_target(
    obj: PETObject,
    parent_address: tuple[int, ...],
    p: int,
) -> PETOperatorTarget:
    return _resolve_x_target(obj, op="DROP", parent_address=parent_address, argument=p)


def inc_target(obj: PETObject, address: tuple[int, ...]) -> PETOperatorTarget:
    return _resolve_y_target(obj, op="INC", address=address)


def dec_target(obj: PETObject, address: tuple[int, ...]) -> PETOperatorTarget:
    return _resolve_y_target(obj, op="DEC", address=address)


def resolve_operator_target(
    obj: PETObject,
    op: PETOperatorName,
    address: tuple[int, ...],
    argument: int | None = None,
) -> PETOperatorTarget:
    """Resolve a PET/PEG 2.0 operator target without mutating the object."""

    if op == "NEW":
        if argument is None:
            raise ValueError("NEW requires argument q")
        return new_target(obj, address, argument)

    if op == "DROP":
        if argument is None:
            raise ValueError("DROP requires argument p")
        return drop_target(obj, address, argument)

    if op == "INC":
        if argument is not None:
            raise ValueError("INC does not accept an argument")
        return inc_target(obj, address)

    if op == "DEC":
        if argument is not None:
            raise ValueError("DEC does not accept an argument")
        return dec_target(obj, address)

    raise ValueError(f"unknown PET operator: {op}")
