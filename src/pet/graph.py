from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .core import is_prime
from .object_model import PETObject
from .operators import (
    PETOperatorApplication,
    PETOperatorName,
    apply_operator_by_value,
)


@dataclass(frozen=True)
class PETGraphNode:
    """PET/PEG 2.0 graph node.

    A graph node wraps one PET object state.
    """

    value: int
    pet_object: PETObject

    @classmethod
    def from_object(cls, obj: PETObject) -> "PETGraphNode":
        return cls(value=obj.value, pet_object=obj)

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "object": self.pet_object.to_dict(),
        }


@dataclass(frozen=True)
class PETGraphEdge:
    """PET/PEG 2.0 graph edge produced by one operator application."""

    source: PETGraphNode
    target: PETGraphNode
    op: PETOperatorName
    address: tuple[int, ...]
    argument: int | None
    application: PETOperatorApplication

    @property
    def label(self) -> str:
        return operator_label(self.op, self.address, self.argument)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_value": self.source.value,
            "target_value": self.target.value,
            "op": self.op,
            "address": list(self.address),
            "argument": self.argument,
            "label": self.label,
            "application": self.application.to_dict(),
        }


def operator_label(
    op: PETOperatorName,
    address: tuple[int, ...],
    argument: int | None = None,
) -> str:
    if op == "NEW":
        return f"NEW(parent_address={list(address)},q={argument})"

    if op == "DROP":
        return f"DROP(parent_address={list(address)},p={argument})"

    if op == "INC":
        return f"INC(address={list(address)})"

    if op == "DEC":
        return f"DEC(address={list(address)})"

    raise ValueError(f"unknown PET operator: {op}")


def _address_sort_key(address: tuple[int, ...]) -> tuple[int, tuple[int, ...]]:
    return (len(address), address)


def _child_prime_labels(obj: PETObject) -> tuple[int, ...]:
    return tuple(
        sorted(
            child.prime_label
            for child in obj.children
            if child.prime_label is not None
        )
    )


def _next_fresh_prime(labels: tuple[int, ...]) -> int:
    candidate = max(labels, default=1) + 1

    while not is_prime(candidate) or candidate in labels:
        candidate += 1

    return candidate


def _composite_parent_addresses(obj: PETObject) -> tuple[tuple[int, ...], ...]:
    return tuple(
        sorted(
            (node.address for node in obj.walk() if node.is_composite),
            key=_address_sort_key,
        )
    )


def _selected_root_addresses(obj: PETObject) -> tuple[tuple[int, ...], ...]:
    return tuple(
        sorted(
            (address for address in obj.addresses() if address != ()),
            key=_address_sort_key,
        )
    )


def operator_applications_by_value(obj: PETObject) -> tuple[PETOperatorApplication, ...]:
    """Return deterministic valid one-step operator applications by value.

    This enumerates valid one-step applications only. Invalid operator targets
    are not graph edges.
    """

    applications: list[PETOperatorApplication] = []

    for parent_address in _composite_parent_addresses(obj):
        parent = obj.at(parent_address)
        labels = _child_prime_labels(parent)

        applications.append(
            apply_operator_by_value(
                obj,
                "NEW",
                parent_address,
                _next_fresh_prime(labels),
            )
        )

        for label in labels:
            applications.append(
                apply_operator_by_value(obj, "DROP", parent_address, label)
            )

    for address in _selected_root_addresses(obj):
        applications.append(apply_operator_by_value(obj, "INC", address))

        dec_application = apply_operator_by_value(obj, "DEC", address)
        if dec_application.valid:
            applications.append(dec_application)

    return tuple(
        application
        for application in applications
        if application.valid and application.after_object is not None
    )


def operator_neighbors_by_value(obj: PETObject) -> tuple[PETGraphEdge, ...]:
    """Return deterministic one-step PET graph edges from an object."""

    source = PETGraphNode.from_object(obj)
    edges: list[PETGraphEdge] = []

    for application in operator_applications_by_value(obj):
        if application.after_object is None:
            raise AssertionError("valid graph application must have after_object")

        target = PETGraphNode.from_object(application.after_object)
        edges.append(
            PETGraphEdge(
                source=source,
                target=target,
                op=application.op,
                address=application.address,
                argument=application.argument,
                application=application,
            )
        )

    return tuple(edges)
