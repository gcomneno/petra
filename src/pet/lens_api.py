"""Stable PET lens advisory API for optional OCF integration.

This module intentionally exposes a small advisory boundary:

    analyze(context) -> result

PET suggests only. It does not read or write OCF artifacts, does not choose
final plans, does not verify OCF correctness, and does not perform hidden
side effects.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


API_VERSION = "pet.lens.v1"
LENS_ID = "pet"
UNKNOWN_TARGET = "unknown"

REQUIRED_CONTEXT_FIELDS = (
    "scope",
    "metrics",
    "available_layers",
    "available_codecs",
)

NUMERIC_RATIO_THRESHOLD = 0.60


def _normalize_target(value: object) -> str:
    if value is None:
        return UNKNOWN_TARGET

    if isinstance(value, str):
        normalized = value.strip()
        return normalized if normalized else UNKNOWN_TARGET

    if isinstance(value, bool | int | float):
        return str(value)

    return UNKNOWN_TARGET


def _is_string_sequence(value: object) -> bool:
    if isinstance(value, str | bytes):
        return False

    if not isinstance(value, Sequence):
        return False

    return all(isinstance(item, str) and item.strip() for item in value)


def _normalized_string_set(values: Sequence[str]) -> set[str]:
    return {value.strip() for value in values}


def _max_candidates(context: Mapping[str, Any]) -> int:
    constraints = context.get("constraints")

    if not isinstance(constraints, Mapping):
        return 1

    raw_value = constraints.get("max_candidates", 1)

    if isinstance(raw_value, bool):
        return 1

    if isinstance(raw_value, int):
        return max(0, raw_value)

    return 1


def _numeric_ratio(metrics: Mapping[str, Any]) -> float:
    raw_value = metrics.get("numeric_ratio", 0.0)

    if isinstance(raw_value, bool):
        return 0.0

    if isinstance(raw_value, int | float):
        return float(raw_value)

    return 0.0


def _fallback_result(
    *,
    target: str = UNKNOWN_TARGET,
    reason: str = "insufficient context for PET advisory",
) -> dict[str, Any]:
    return {
        "lens_id": LENS_ID,
        "api_version": API_VERSION,
        "target": target,
        "hints": [],
        "candidate_plans": [],
        "resources": [],
        "confidence": "none",
        "reason": reason,
    }


def _base_result(
    *,
    target: str,
    hints: list[dict[str, Any]],
    candidate_plans: list[dict[str, Any]],
    confidence: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "lens_id": LENS_ID,
        "api_version": API_VERSION,
        "target": target,
        "hints": hints,
        "candidate_plans": candidate_plans,
        "resources": [],
        "confidence": confidence,
        "reason": reason,
    }


def _fallback_reason_for_context(
    context: Mapping[str, Any],
    *,
    target: str,
) -> str | None:
    if not context:
        return "insufficient context for PET advisory"

    if target == UNKNOWN_TARGET:
        return "insufficient context for PET advisory: missing target"

    for field in REQUIRED_CONTEXT_FIELDS:
        if field not in context:
            return f"insufficient context for PET advisory: missing {field}"

    if not isinstance(context["metrics"], Mapping):
        return "invalid context for PET advisory: invalid metrics"

    if not _is_string_sequence(context["available_layers"]):
        return "invalid context for PET advisory: invalid available_layers"

    if not _is_string_sequence(context["available_codecs"]):
        return "invalid context for PET advisory: invalid available_codecs"

    if "constraints" in context and not isinstance(context["constraints"], Mapping):
        return "invalid context for PET advisory: invalid constraints"

    return None


def _numeric_advisory_result(
    context: Mapping[str, Any],
    *,
    target: str,
) -> dict[str, Any] | None:
    metrics = context["metrics"]
    available_layers = _normalized_string_set(context["available_layers"])
    available_codecs = _normalized_string_set(context["available_codecs"])
    numeric_ratio = _numeric_ratio(metrics)

    if numeric_ratio < NUMERIC_RATIO_THRESHOLD:
        return None

    if _max_candidates(context) <= 0:
        return _base_result(
            target=target,
            hints=[
                {
                    "kind": "numeric-heavy",
                    "message": "target metrics suggest numeric stream structure",
                }
            ],
            candidate_plans=[],
            confidence="none",
            reason="numeric-heavy metrics found but max_candidates is zero",
        )

    if "NUMS" not in available_layers:
        return _base_result(
            target=target,
            hints=[
                {
                    "kind": "numeric-heavy",
                    "message": "target metrics suggest numeric stream structure",
                }
            ],
            candidate_plans=[],
            confidence="none",
            reason="numeric-heavy metrics found but NUMS layer is unavailable",
        )

    if "num_v2" not in available_codecs:
        return _base_result(
            target=target,
            hints=[
                {
                    "kind": "numeric-heavy",
                    "message": "target metrics suggest numeric stream structure",
                }
            ],
            candidate_plans=[],
            confidence="none",
            reason="numeric-heavy metrics found but num_v2 codec is unavailable",
        )

    return _base_result(
        target=target,
        hints=[
            {
                "kind": "numeric-heavy",
                "message": "target metrics suggest numeric stream structure",
            }
        ],
        candidate_plans=[
            {
                "layer_id": "NUMS",
                "codec_text": "num_v2",
                "stream_codecs": {
                    "NUMS": "num_v2",
                },
                "note": "PET advisory only; OCF autopick must measure and verify",
            }
        ],
        confidence="low",
        reason="numeric-heavy metrics and num_v2 available",
    )


def analyze(context: Mapping[str, Any] | None) -> dict[str, Any]:
    """Return a deterministic PET advisory result.

    The v1 fallback contract is intentionally conservative. When the context
    is empty, incomplete, invalid, or unsupported, PET returns an explicit
    fallback result.

    PET does not access network, filesystem, subprocesses, or mutable external
    state from this API.
    """

    if not isinstance(context, Mapping):
        return _fallback_result(
            reason="invalid context for PET advisory",
        )

    target = _normalize_target(context.get("target"))
    failure_reason = _fallback_reason_for_context(context, target=target)

    if failure_reason is not None:
        return _fallback_result(target=target, reason=failure_reason)

    numeric_result = _numeric_advisory_result(context, target=target)

    if numeric_result is not None:
        return numeric_result

    return _fallback_result(
        target=target,
        reason="unsupported context for PET advisory",
    )


__all__ = [
    "API_VERSION",
    "LENS_ID",
    "analyze",
]
