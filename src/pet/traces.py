from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .graph import PETGraphPath
from .operators import PETOperatorName


@dataclass(frozen=True)
class PETTraceStep:
    """One recorded PET/PEG 2.0 trace step.

    A trace step records what happened. It does not explain why the route was
    selected.
    """

    index: int
    source_value: int
    target_value: int
    op: PETOperatorName
    address: tuple[int, ...]
    argument: int | None
    label: str
    application_reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "source_value": self.source_value,
            "target_value": self.target_value,
            "op": self.op,
            "address": list(self.address),
            "argument": self.argument,
            "label": self.label,
            "application_reason": self.application_reason,
        }


@dataclass(frozen=True)
class PETTrace:
    """PET/PEG 2.0 trace.

    A trace records a concrete path history. It is validity evidence for what
    happened, not a route-quality claim.
    """

    root_value: int
    target_value: int
    depth: int
    path_identity: tuple[tuple[int, str, int], ...]
    steps: tuple[PETTraceStep, ...]

    @property
    def labels(self) -> tuple[str, ...]:
        return tuple(step.label for step in self.steps)

    @property
    def values(self) -> tuple[int, ...]:
        if not self.steps:
            return (self.root_value,)

        return (
            self.root_value,
            *(step.target_value for step in self.steps),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "root_value": self.root_value,
            "target_value": self.target_value,
            "depth": self.depth,
            "values": list(self.values),
            "labels": list(self.labels),
            "path_identity": [
                [source, label, target]
                for source, label, target in self.path_identity
            ],
            "steps": [step.to_dict() for step in self.steps],
        }


def trace_from_path(path: PETGraphPath) -> PETTrace:
    """Build a trace from a concrete graph path."""

    steps = tuple(
        PETTraceStep(
            index=index,
            source_value=edge.source.value,
            target_value=edge.target.value,
            op=edge.op,
            address=edge.address,
            argument=edge.argument,
            label=edge.label,
            application_reason=edge.application.reason,
        )
        for index, edge in enumerate(path.edges, start=1)
    )

    return PETTrace(
        root_value=path.source.value,
        target_value=path.target.value,
        depth=path.depth,
        path_identity=path.identity_key(),
        steps=steps,
    )
