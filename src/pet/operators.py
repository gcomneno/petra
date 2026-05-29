from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .core import is_prime
from .object_model import PETObject, pet_object_from_int


PETOperatorName = Literal["NEW", "DROP", "INC", "DEC"]
PETOperatorAxis = Literal["X", "Y"]
PETOperatorTargetKind = Literal["parent-support", "selected-root"]


@dataclass(frozen=True)
class PETOperatorApplication:
    """PET/PEG 2.0 operator application result.

    Operator application currently mutates by represented integer value and then
    rebuilds a PETObject. It does not yet manually rewrite object internals.
    """

    op: PETOperatorName
    address: tuple[int, ...]
    argument: int | None
    target: "PETOperatorTarget"
    valid: bool
    reason: str
    before_value: int
    after_value: int | None
    before_object: PETObject
    after_object: PETObject | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "op": self.op,
            "address": list(self.address),
            "argument": self.argument,
            "valid": self.valid,
            "reason": self.reason,
            "before_value": self.before_value,
            "after_value": self.after_value,
            "target": self.target.to_dict(),
            "before_object": self.before_object.to_dict(),
            "after_object": (
                None if self.after_object is None else self.after_object.to_dict()
            ),
        }


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



def _product(values: list[int]) -> int:
    result = 1
    for value in values:
        result *= value
    return result


def _child_values(obj: PETObject) -> list[int]:
    return [child.value for child in obj.children]


def _exponent_value(obj: PETObject) -> int:
    if obj.is_atomic:
        return 1
    return _product(_child_values(obj))


def _value_from_child_values(obj: PETObject, child_values: list[int]) -> int:
    if obj.prime_label is None:
        return _product(child_values)

    return obj.prime_label ** _product(child_values)


def _replace_descendant_value(
    obj: PETObject,
    target_address: tuple[int, ...],
    new_value: int,
) -> int:
    if obj.address == target_address:
        return new_value

    child_values: list[int] = []
    changed = False

    for child in obj.children:
        if target_address[: len(child.address)] == child.address:
            child_values.append(
                _replace_descendant_value(child, target_address, new_value)
            )
            changed = True
        else:
            child_values.append(child.value)

    if not changed:
        raise ValueError(f"target address {target_address!r} is not inside object")

    return _value_from_child_values(obj, child_values)


def _apply_x_value(
    obj: PETObject,
    *,
    op: Literal["NEW", "DROP"],
    parent_address: tuple[int, ...],
    argument: int,
) -> int:
    target = obj.at(parent_address)

    if target.prime_label is None:
        if op == "NEW":
            new_target_value = target.value * argument
        else:
            child = next(
                child for child in target.children if child.prime_label == argument
            )
            new_target_value = target.value // child.value
    else:
        current_exponent = _exponent_value(target)

        if op == "NEW":
            new_exponent = current_exponent * argument
        else:
            child = next(
                child for child in target.children if child.prime_label == argument
            )
            new_exponent = current_exponent // child.value

        new_target_value = target.prime_label**new_exponent

    return _replace_descendant_value(obj, parent_address, new_target_value)


def _apply_y_value(
    obj: PETObject,
    *,
    op: Literal["INC", "DEC"],
    address: tuple[int, ...],
) -> int:
    target = obj.at(address)

    if target.prime_label is None:
        raise ValueError("Y-axis operator target must be a selected child root")

    current_exponent = _exponent_value(target)
    new_exponent = current_exponent + 1 if op == "INC" else current_exponent - 1

    if new_exponent < 1:
        raise ValueError("Y-axis operator produced exponent below one")

    new_target_value = target.prime_label**new_exponent

    return _replace_descendant_value(obj, address, new_target_value)


def apply_operator_by_value(
    obj: PETObject,
    op: PETOperatorName,
    address: tuple[int, ...],
    argument: int | None = None,
) -> PETOperatorApplication:
    """Apply a PET/PEG 2.0 operator by represented integer value.

    This is value-level application, not manual structural rewriting.
    """

    target = resolve_operator_target(obj, op, address, argument)

    if not target.valid:
        return PETOperatorApplication(
            op=op,
            address=address,
            argument=argument,
            target=target,
            valid=False,
            reason=target.reason,
            before_value=obj.value,
            after_value=None,
            before_object=obj,
            after_object=None,
        )

    if op == "NEW":
        if argument is None:
            raise ValueError("NEW requires argument q")
        after_value = _apply_x_value(
            obj,
            op="NEW",
            parent_address=address,
            argument=argument,
        )
    elif op == "DROP":
        if argument is None:
            raise ValueError("DROP requires argument p")
        after_value = _apply_x_value(
            obj,
            op="DROP",
            parent_address=address,
            argument=argument,
        )
    elif op == "INC":
        after_value = _apply_y_value(obj, op="INC", address=address)
    elif op == "DEC":
        after_value = _apply_y_value(obj, op="DEC", address=address)
    else:
        raise ValueError(f"unknown PET operator: {op}")

    return PETOperatorApplication(
        op=op,
        address=address,
        argument=argument,
        target=target,
        valid=True,
        reason=f"{op.lower()}-applied-by-value",
        before_value=obj.value,
        after_value=after_value,
        before_object=obj,
        after_object=pet_object_from_int(after_value),
    )
