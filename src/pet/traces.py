from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .graph import PETGraphPath, operator_label
from .object_model import pet_object_from_int
from .operators import PETOperatorName, apply_operator_by_value


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



@dataclass(frozen=True)
class PETTraceCheckStep:
    """One replay/check result for a trace step."""

    index: int
    source_value: int
    expected_target_value: int
    actual_target_value: int | None
    op: PETOperatorName
    address: tuple[int, ...]
    argument: int | None
    label: str
    valid: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "source_value": self.source_value,
            "expected_target_value": self.expected_target_value,
            "actual_target_value": self.actual_target_value,
            "op": self.op,
            "address": list(self.address),
            "argument": self.argument,
            "label": self.label,
            "valid": self.valid,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class PETTraceCertificate:
    """Replay certificate for a PET/PEG 2.0 trace.

    A certificate verifies whether the recorded steps replay from the root value.
    It does not claim that the route was optimal, preferred, or useful.
    """

    trace: PETTrace
    valid: bool
    reason: str
    checked_steps: int
    step_checks: tuple[PETTraceCheckStep, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "reason": self.reason,
            "checked_steps": self.checked_steps,
            "root_value": self.trace.root_value,
            "target_value": self.trace.target_value,
            "trace": self.trace.to_dict(),
            "step_checks": [step.to_dict() for step in self.step_checks],
        }


def check_trace(trace: PETTrace) -> PETTraceCertificate:
    """Replay a PET trace and return a validity certificate."""

    current = pet_object_from_int(trace.root_value)
    checks: list[PETTraceCheckStep] = []

    for step in trace.steps:
        expected_label = operator_label(step.op, step.address, step.argument)

        if step.label != expected_label:
            check = PETTraceCheckStep(
                index=step.index,
                source_value=current.value,
                expected_target_value=step.target_value,
                actual_target_value=None,
                op=step.op,
                address=step.address,
                argument=step.argument,
                label=step.label,
                valid=False,
                reason="label-mismatch",
            )
            checks.append(check)
            return PETTraceCertificate(
                trace=trace,
                valid=False,
                reason="label-mismatch",
                checked_steps=len(checks),
                step_checks=tuple(checks),
            )

        if current.value != step.source_value:
            check = PETTraceCheckStep(
                index=step.index,
                source_value=current.value,
                expected_target_value=step.target_value,
                actual_target_value=None,
                op=step.op,
                address=step.address,
                argument=step.argument,
                label=step.label,
                valid=False,
                reason="source-value-mismatch",
            )
            checks.append(check)
            return PETTraceCertificate(
                trace=trace,
                valid=False,
                reason="source-value-mismatch",
                checked_steps=len(checks),
                step_checks=tuple(checks),
            )

        application = apply_operator_by_value(
            current,
            step.op,
            step.address,
            step.argument,
        )
        actual_target_value = application.after_value

        if not application.valid:
            check = PETTraceCheckStep(
                index=step.index,
                source_value=step.source_value,
                expected_target_value=step.target_value,
                actual_target_value=actual_target_value,
                op=step.op,
                address=step.address,
                argument=step.argument,
                label=step.label,
                valid=False,
                reason=application.reason,
            )
            checks.append(check)
            return PETTraceCertificate(
                trace=trace,
                valid=False,
                reason=application.reason,
                checked_steps=len(checks),
                step_checks=tuple(checks),
            )

        if actual_target_value != step.target_value:
            check = PETTraceCheckStep(
                index=step.index,
                source_value=step.source_value,
                expected_target_value=step.target_value,
                actual_target_value=actual_target_value,
                op=step.op,
                address=step.address,
                argument=step.argument,
                label=step.label,
                valid=False,
                reason="target-value-mismatch",
            )
            checks.append(check)
            return PETTraceCertificate(
                trace=trace,
                valid=False,
                reason="target-value-mismatch",
                checked_steps=len(checks),
                step_checks=tuple(checks),
            )

        check = PETTraceCheckStep(
            index=step.index,
            source_value=step.source_value,
            expected_target_value=step.target_value,
            actual_target_value=actual_target_value,
            op=step.op,
            address=step.address,
            argument=step.argument,
            label=step.label,
            valid=True,
            reason="step-replayed",
        )
        checks.append(check)

        if application.after_object is None:
            raise AssertionError("valid replay application must have after_object")

        current = application.after_object

    if current.value != trace.target_value:
        return PETTraceCertificate(
            trace=trace,
            valid=False,
            reason="trace-target-mismatch",
            checked_steps=len(checks),
            step_checks=tuple(checks),
        )

    return PETTraceCertificate(
        trace=trace,
        valid=True,
        reason="trace-replayed",
        checked_steps=len(checks),
        step_checks=tuple(checks),
    )


def certificate_from_path(path: PETGraphPath) -> PETTraceCertificate:
    """Build and check a trace certificate from a graph path."""

    return check_trace(trace_from_path(path))
