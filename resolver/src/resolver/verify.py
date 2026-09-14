"""Path verifier for PETRA structural edit sequences.

Given a source shape, a target shape, and a sequence of operator
invocations, the verifier:

1. applies every step in order against the evolving shape;
2. rejects the sequence on the first failed step;
3. checks that the final shape equals the target;
4. optionally checks that the sequence length equals the minimum
   structural distance between source and target.

The verifier is additive. It does not generate paths and does not
replace the Resolver. It validates paths produced by the caller, whether
by a human, another tool, or the Resolver itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from petra import (
    Address,
    DefaultTarget,
    ExplicitTarget,
    FailedResult,
    Operator,
    PetraShape,
    SuccessfulResult,
    apply_graft,
    apply_prune,
    apply_shed,
    apply_sprout,
    parse_shape,
    serialize_shape,
    validate_shape,
)

from .distance import DistanceError, structural_distance_shapes


class VerifyError(ValueError):
    """A deterministic path verification failure."""


_APPLY = {
    Operator.SPROUT: apply_sprout,
    Operator.SHED: apply_shed,
    Operator.GRAFT: apply_graft,
    Operator.PRUNE: apply_prune,
}


@dataclass(frozen=True)
class VerifyStep:
    """One proposed edit in a path being verified."""

    operator: Operator
    invocation_target: DefaultTarget | ExplicitTarget


@dataclass(frozen=True)
class StepFailure:
    """The result of a step that failed to apply."""

    index: int
    operator: Operator
    invocation_target: DefaultTarget | ExplicitTarget
    before_shape: PetraShape
    reason: str


@dataclass(frozen=True)
class VerificationResult:
    """The outcome of verifying a proposed path."""

    source: PetraShape
    target: PetraShape
    steps: tuple[VerifyStep, ...]
    final_shape: PetraShape
    valid: bool
    minimal: bool | None
    expected_length: int | None
    reason: str
    failed_step: StepFailure | None = None


def verify_path(
    source: str | PetraShape,
    target: str | PetraShape,
    steps: Iterable[VerifyStep | dict[str, object]],
    *,
    check_minimal: bool = True,
    max_depth: int = 30,
    max_nodes: int = 80,
    max_visited: int = 200_000,
    min_distance: int | None = None,
) -> VerificationResult:
    """Verify a proposed path between two canonical PETRA shapes.

    Parameters
    ----------
    source, target
        Canonical shapes or their textual form.
    steps
        Iterable of VerifyStep or JSON-like dicts with keys
        ``operator`` and ``target``.
    check_minimal
        If True, compute the minimum distance and compare.
    max_depth, max_nodes, max_visited
        Bounds forwarded to the Resolver when computing the minimum.
    min_distance
        Optional precomputed minimum distance. If provided and
        ``check_minimal`` is True, no Resolver call is made.
    """

    source_shape = _coerce(source)
    target_shape = _coerce(target)
    normalized_steps = tuple(_normalize_step(s) for s in steps)

    current = source_shape
    for index, step in enumerate(normalized_steps):
        apply = _APPLY[step.operator]
        result = apply(current, step.invocation_target)
        if isinstance(result, FailedResult):
            return VerificationResult(
                source=source_shape,
                target=target_shape,
                steps=normalized_steps,
                final_shape=current,
                valid=False,
                minimal=None,
                expected_length=None,
                reason="invalid-step",
                failed_step=StepFailure(
                    index=index,
                    operator=step.operator,
                    invocation_target=step.invocation_target,
                    before_shape=current,
                    reason=result.reason,
                ),
            )
        assert isinstance(result, SuccessfulResult)
        current = result.after_shape

    valid = current == target_shape
    expected_length: int | None = None
    minimal: bool | None = None

    if not valid:
        return VerificationResult(
            source=source_shape,
            target=target_shape,
            steps=normalized_steps,
            final_shape=current,
            valid=False,
            minimal=None,
            expected_length=None,
            reason="target-not-reached",
        )

    if check_minimal:
        if min_distance is None:
            try:
                expected_length = structural_distance_shapes(
                    source_shape,
                    target_shape,
                    max_depth=max_depth,
                    max_nodes=max_nodes,
                    max_visited=max_visited,
                )
            except DistanceError as error:
                raise VerifyError(str(error)) from error
        else:
            expected_length = min_distance

        minimal = len(normalized_steps) == expected_length
        reason = (
            "valid-and-minimal" if minimal else "valid-but-suboptimal"
        )
    else:
        reason = "valid"

    return VerificationResult(
        source=source_shape,
        target=target_shape,
        steps=normalized_steps,
        final_shape=current,
        valid=True,
        minimal=minimal,
        expected_length=expected_length,
        reason=reason,
    )


def _coerce(value: str | PetraShape) -> PetraShape:
    if isinstance(value, str):
        return parse_shape(value)
    validate_shape(value)
    return value


def _normalize_step(
    step: VerifyStep | dict[str, object],
) -> VerifyStep:
    if isinstance(step, VerifyStep):
        return step

    if not isinstance(step, dict):
        raise VerifyError("step must be VerifyStep or dict")

    operator_text = step.get("operator")
    if not isinstance(operator_text, str):
        raise VerifyError("step missing string 'operator'")
    try:
        operator = Operator(operator_text)
    except ValueError as error:
        raise VerifyError(
            f"unknown operator: {operator_text}"
        ) from error

    target_data = step.get("target")
    if not isinstance(target_data, dict):
        raise VerifyError("step missing dict 'target'")

    mode = target_data.get("mode")
    if mode == "default":
        return VerifyStep(
            operator=operator,
            invocation_target=DefaultTarget(),
        )
    if mode == "explicit":
        address_text = target_data.get("address")
        if not isinstance(address_text, str):
            raise VerifyError(
                "explicit target missing string 'address'"
            )
        from petra import parse_address

        try:
            address = parse_address(address_text)
        except Exception as error:
            raise VerifyError(
                f"invalid address: {address_text}"
            ) from error
        return VerifyStep(
            operator=operator,
            invocation_target=ExplicitTarget(address),
        )

    raise VerifyError(f"unknown target mode: {mode}")
