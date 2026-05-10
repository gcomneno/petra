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


def _fallback_reason_for_context(
    context: Mapping[str, Any],
    *,
    target: str,
) -> str:
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

    return "unsupported context for PET advisory"


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
    reason = _fallback_reason_for_context(context, target=target)

    return _fallback_result(target=target, reason=reason)


__all__ = [
    "API_VERSION",
    "LENS_ID",
    "analyze",
]
