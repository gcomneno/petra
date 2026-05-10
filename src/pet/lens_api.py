"""Stable PET lens advisory API for optional OCF integration.

This module intentionally exposes a small advisory boundary:

    analyze(context) -> result

PET suggests only. It does not read or write OCF artifacts, does not choose
final plans, does not verify OCF correctness, and does not perform hidden
side effects.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


API_VERSION = "pet.lens.v1"
LENS_ID = "pet"
UNKNOWN_TARGET = "unknown"


def _normalize_target(value: object) -> str:
    if value is None:
        return UNKNOWN_TARGET

    if isinstance(value, str):
        normalized = value.strip()
        return normalized if normalized else UNKNOWN_TARGET

    if isinstance(value, bool | int | float):
        return str(value)

    return UNKNOWN_TARGET


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


def analyze(context: Mapping[str, Any] | None) -> dict[str, Any]:
    """Return a deterministic PET advisory result.

    The v1 contract is intentionally conservative. When the context is empty,
    incomplete, or unsupported, PET returns an explicit fallback result.

    PET does not access network, filesystem, subprocesses, or mutable external
    state from this API.
    """

    if not isinstance(context, Mapping):
        return _fallback_result(
            reason="invalid context for PET advisory",
        )

    target = _normalize_target(context.get("target"))

    return _fallback_result(target=target)


__all__ = [
    "API_VERSION",
    "LENS_ID",
    "analyze",
]
