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


@dataclass(frozen=True)
class PETGraphPath:
    """PET/PEG 2.0 graph path.

    A path records one concrete operator history through PET object states.
    """

    nodes: tuple[PETGraphNode, ...]
    edges: tuple[PETGraphEdge, ...]

    @classmethod
    def root(cls, obj: PETObject) -> "PETGraphPath":
        return cls(nodes=(PETGraphNode.from_object(obj),), edges=())

    @property
    def source(self) -> PETGraphNode:
        return self.nodes[0]

    @property
    def target(self) -> PETGraphNode:
        return self.nodes[-1]

    @property
    def depth(self) -> int:
        return len(self.edges)

    @property
    def labels(self) -> tuple[str, ...]:
        return tuple(edge.label for edge in self.edges)

    @property
    def values(self) -> tuple[int, ...]:
        return tuple(node.value for node in self.nodes)

    def identity_key(self) -> tuple[tuple[int, str, int], ...]:
        """Return a deterministic concrete path identity key."""

        return tuple(
            (edge.source.value, edge.label, edge.target.value)
            for edge in self.edges
        )

    def extend(self, edge: PETGraphEdge) -> "PETGraphPath":
        if edge.source.value != self.target.value:
            raise ValueError(
                "edge source does not match current path target: "
                f"{edge.source.value} != {self.target.value}"
            )

        return PETGraphPath(
            nodes=(*self.nodes, edge.target),
            edges=(*self.edges, edge),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "depth": self.depth,
            "values": list(self.values),
            "labels": list(self.labels),
            "source_value": self.source.value,
            "target_value": self.target.value,
            "edges": [edge.to_dict() for edge in self.edges],
        }


@dataclass(frozen=True)
class PETGraphTraversal:
    """Bounded deterministic PET/PEG 2.0 graph traversal result."""

    root: PETGraphNode
    max_depth: int
    max_paths: int | None
    paths: tuple[PETGraphPath, ...]
    truncated: bool

    @property
    def path_count(self) -> int:
        return len(self.paths)

    def paths_at_depth(self, depth: int) -> tuple[PETGraphPath, ...]:
        return tuple(path for path in self.paths if path.depth == depth)

    def to_dict(self) -> dict[str, Any]:
        return {
            "root_value": self.root.value,
            "max_depth": self.max_depth,
            "max_paths": self.max_paths,
            "path_count": self.path_count,
            "truncated": self.truncated,
            "paths": [path.to_dict() for path in self.paths],
        }


def path_equivalent(left: PETGraphPath, right: PETGraphPath) -> bool:
    """Return whether two graph paths have the same concrete path identity."""

    return left.identity_key() == right.identity_key()


def traverse_operator_graph_by_value(
    obj: PETObject,
    *,
    max_depth: int,
    max_paths: int | None = None,
) -> PETGraphTraversal:
    """Traverse the PET operator graph with deterministic bounded breadth-first order.

    This is traversal machinery, not routing policy. It records alternatives and
    stops at explicit bounds.
    """

    if max_depth < 0:
        raise ValueError("max_depth must be >= 0")

    if max_paths is not None and max_paths < 1:
        raise ValueError("max_paths must be >= 1")

    root = PETGraphNode.from_object(obj)
    root_path = PETGraphPath.root(obj)

    paths: list[PETGraphPath] = [root_path]
    frontier: tuple[PETGraphPath, ...] = (root_path,)

    for _ in range(max_depth):
        next_frontier: list[PETGraphPath] = []

        for path in frontier:
            for edge in operator_neighbors_by_value(path.target.pet_object):
                if max_paths is not None and len(paths) >= max_paths:
                    return PETGraphTraversal(
                        root=root,
                        max_depth=max_depth,
                        max_paths=max_paths,
                        paths=tuple(paths),
                        truncated=True,
                    )

                next_path = path.extend(edge)
                paths.append(next_path)
                next_frontier.append(next_path)

        frontier = tuple(next_frontier)

        if not frontier:
            break

    return PETGraphTraversal(
        root=root,
        max_depth=max_depth,
        max_paths=max_paths,
        paths=tuple(paths),
        truncated=False,
    )
