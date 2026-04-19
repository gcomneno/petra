from __future__ import annotations

from pathlib import Path
from typing import Any

from pet.irsr_state import run_hostile_semiprime_irsr_with_seed_candidates


def _normalize_slot_candidates(slot_candidates: dict[str, list[int]] | None) -> dict[str, list[int]]:
    normalized: dict[str, list[int]] = {}

    for slot_name, candidates in (slot_candidates or {}).items():
        cleaned = sorted({int(value) for value in candidates})
        if cleaned:
            normalized[str(slot_name)] = cleaned

    return normalized


def build_from_irsr_pipeline(
    n: int,
    output_dir: str | Path,
    *,
    slot_candidates: dict[str, list[int]] | None,
    max_steps: int = 5,
) -> dict[str, Any]:
    normalized_slot_candidates = _normalize_slot_candidates(slot_candidates)
    if not normalized_slot_candidates:
        raise ValueError("build_from_irsr_pipeline requires non-empty slot_candidates")

    result = run_hostile_semiprime_irsr_with_seed_candidates(
        n,
        normalized_slot_candidates,
        max_steps=max_steps,
        output_dir=output_dir,
    )

    attempted = [item for item in result.get("build_results", []) if item.get("build_attempted")]
    builder_report = attempted[-1]["report"] if attempted else None

    return {
        "schema": "pet-builder-from-irsr-v0",
        "input_n": n,
        "strategy": "seed-candidates",
        "slot_candidates": normalized_slot_candidates,
        "max_steps": max_steps,
        "irsr_final_status": result["final_status"],
        "payload_summary": result["payload_summary"],
        "build_summary": result["build_summary"],
        "terminal_state": result["terminal_state"],
        "builder_report": builder_report,
    }
