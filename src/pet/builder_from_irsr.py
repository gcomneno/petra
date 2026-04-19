from __future__ import annotations

import json
import tempfile
from math import isqrt
from pathlib import Path
from typing import Any

from pet.core import is_prime
from pet.irsr_state import (
    run_hostile_semiprime_irsr_with_auto_seed_portfolios,
    run_hostile_semiprime_irsr_with_seed_candidates,
)


def _normalize_slot_candidates(slot_candidates: dict[str, list[int]] | None) -> dict[str, list[int]]:
    normalized: dict[str, list[int]] = {}

    for slot_name, candidates in (slot_candidates or {}).items():
        cleaned = sorted({int(value) for value in candidates})
        if cleaned:
            normalized[str(slot_name)] = cleaned

    return normalized


def _icbrt_floor(n: int) -> int:
    lo = 0
    hi = 1
    while hi * hi * hi <= n:
        hi *= 2
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        cube = mid * mid * mid
        if cube <= n:
            lo = mid
        else:
            hi = mid
    return lo


def _looks_like_semiprime_model_mismatch(result: dict[str, Any], n: int) -> bool:
    if result.get("final_status") != "payloads-nonexact":
        return False

    payloads = result.get("payload_candidates") or []
    if len(payloads) != 1:
        return False

    payload = payloads[0]
    if payload.get("support_size") != 2:
        return False
    if list(payload.get("exponent_profile") or []) != [1, 1]:
        return False

    product = 1
    slots = payload.get("prime_slots") or []
    if len(slots) != 2:
        return False

    for slot in slots:
        candidates = slot.get("candidates") or []
        if len(candidates) != 1:
            return False
        product *= int(candidates[0])

    return product != int(n)


def _final_status_from_builder_report(builder_report: dict[str, Any]) -> str:
    final_build_output = builder_report.get("final_build_output") or {}
    support_report = builder_report.get("support_report") or {}

    if support_report.get("exact_target_match") is True:
        return "built-exact-match"
    if final_build_output.get("build_status") == "built":
        return "built"
    return "builder-attempted-no-build"


def _build_summary_from_builder_report(builder_report: dict[str, Any]) -> dict[str, int]:
    final_status = _final_status_from_builder_report(builder_report)
    built = 1 if final_status in {"built", "built-exact-match"} else 0
    exact = 1 if final_status == "built-exact-match" else 0

    return {
        "candidate_count": 1,
        "attempted_count": 1,
        "built_count": built,
        "exact_match_count": exact,
        "skipped_count": 0,
    }


def _run_builder_from_factorization(output_dir: str | Path, factors: list[list[int]]) -> dict[str, Any]:
    from pet.builder_from_factorization import build_from_factorization_pipeline

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        spec_path = td_path / "irsr_factorization.json"
        spec_path.write_text(
            json.dumps({"factors": factors}),
            encoding="utf-8",
        )
        return build_from_factorization_pipeline(spec_path, output_dir)


def _wrap_dedicated_solver_report(
    *,
    n: int,
    kind: str,
    strategy: str,
    support: list[int],
    exponent_profile: list[int],
    builder_report: dict[str, Any],
) -> dict[str, Any]:
    final_status = _final_status_from_builder_report(builder_report)
    final_build_output = builder_report.get("final_build_output") or {}
    built_pet_object = final_build_output.get("built_pet_object") or {}

    if final_status in {"built", "built-exact-match"}:
        terminal_state = {
            "status": "built",
            "reason": final_status,
            "input": {"n": str(n), "kind": kind},
            "known_support": sorted(support),
            "unresolved_residual": {"n": str(n)},
            "constraints": {
                "support_size": len(exponent_profile),
                "exponent_profile": list(exponent_profile),
                "joint_pet_constraints": [],
                "forbidden_patterns": [],
            },
            "builder_readiness": "ready",
            "next_missing_step": None,
            "build_status": final_build_output.get("build_status"),
            "assembly_status": built_pet_object.get("assembly_status"),
        }
    else:
        terminal_state = {
            "status": "blocked",
            "reason": final_status,
            "input": {"n": str(n), "kind": kind},
            "known_support": sorted(support),
            "unresolved_residual": {"n": str(n)},
            "constraints": {
                "support_size": len(exponent_profile),
                "exponent_profile": list(exponent_profile),
                "joint_pet_constraints": [],
                "forbidden_patterns": [],
            },
            "builder_readiness": "ready",
            "next_missing_step": "resolve the exact builder execution gap for the promoted payload candidate",
            "build_status": final_build_output.get("build_status"),
        }

    return {
        "schema": "pet-builder-from-irsr-v0",
        "input_n": n,
        "strategy": strategy,
        "slot_candidates": {},
        "auto_seed_radii": None,
        "max_steps": 0,
        "irsr_final_status": final_status,
        "payload_summary": {
            "payload_count": 1,
            "support_sizes": [len(exponent_profile)],
            "exponent_profiles": [list(exponent_profile)],
        },
        "build_summary": _build_summary_from_builder_report(builder_report),
        "terminal_state": terminal_state,
        "builder_report": builder_report,
    }


def _run_prime_square_solver(n: int, output_dir: str | Path) -> dict[str, Any] | None:
    root = isqrt(n)
    if root * root != n:
        return None
    if not is_prime(root):
        return None

    builder_report = _run_builder_from_factorization(output_dir, [[root, 2]])
    return _wrap_dedicated_solver_report(
        n=n,
        kind="hostile-prime-square",
        strategy="prime-square-auto",
        support=[root],
        exponent_profile=[2],
        builder_report=builder_report,
    )


def _run_square_times_prime_solver(
    n: int,
    output_dir: str | Path,
    *,
    radius: int = 1,
) -> dict[str, Any] | None:
    root = _icbrt_floor(n)

    start = max(2, root - radius)
    stop = root + radius + 1

    for p in range(start, stop + 1):
        if not is_prime(p):
            continue
        p2 = p * p
        if n % p2 != 0:
            continue

        q = n // p2
        if q == p:
            continue
        if q < 2 or not is_prime(q):
            continue

        factors = [[p, 2], [q, 1]]
        builder_report = _run_builder_from_factorization(output_dir, factors)
        return _wrap_dedicated_solver_report(
            n=n,
            kind="hostile-square-times-prime",
            strategy="square-times-prime-auto",
            support=[p, q],
            exponent_profile=[2, 1],
            builder_report=builder_report,
        )

    return None


def build_from_irsr_pipeline(
    n: int,
    output_dir: str | Path,
    *,
    slot_candidates: dict[str, list[int]] | None,
    max_steps: int = 5,
    auto_seed_radii: list[int] | None = None,
) -> dict[str, Any]:
    normalized_slot_candidates = _normalize_slot_candidates(slot_candidates)

    if normalized_slot_candidates:
        result = run_hostile_semiprime_irsr_with_seed_candidates(
            n,
            normalized_slot_candidates,
            max_steps=max_steps,
            output_dir=output_dir,
        )
        strategy = "seed-candidates"
    else:
        radii = list(auto_seed_radii or [1])
        result = run_hostile_semiprime_irsr_with_auto_seed_portfolios(
            n,
            sqrt_radii=radii,
            max_steps=max_steps,
            output_dir=output_dir,
        )
        strategy = "auto-seed"

    if strategy == "auto-seed":
        square_report = _run_prime_square_solver(n, output_dir)
        if square_report is not None:
            return square_report

        p2q_report = _run_square_times_prime_solver(n, output_dir, radius=1)
        if p2q_report is not None:
            return p2q_report

        if _looks_like_semiprime_model_mismatch(result, n):
            result = dict(result)
            result["final_status"] = "semiprime-model-mismatch"

    attempted = [item for item in result.get("build_results", []) if item.get("build_attempted")]
    builder_report = attempted[-1]["report"] if attempted else None

    return {
        "schema": "pet-builder-from-irsr-v0",
        "input_n": n,
        "strategy": strategy,
        "slot_candidates": normalized_slot_candidates,
        "auto_seed_radii": None if normalized_slot_candidates else list(auto_seed_radii or [1]),
        "max_steps": max_steps,
        "irsr_final_status": result["final_status"],
        "payload_summary": result["payload_summary"],
        "build_summary": result["build_summary"],
        "terminal_state": result["terminal_state"],
        "builder_report": builder_report,
    }
