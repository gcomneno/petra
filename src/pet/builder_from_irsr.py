from __future__ import annotations

import json
import tempfile
from itertools import combinations, permutations
from math import comb, isqrt
from pathlib import Path
from typing import Any

from pet.core import is_prime
from pet.irsr_state import (
    run_hostile_semiprime_irsr_with_auto_seed_portfolios,
    run_hostile_semiprime_irsr_with_seed_candidates,
)

SQUAREFREE_POLICY_V0 = {
    "budget": {
        "max_k": 5,
        "max_radius": 64,
        "max_prime_count": 16,
        "max_combinations": 256,
    },
    "rollout": [
        {"k": 3, "radius": 16},
        {"k": 4, "radius": 16},
        {"k": 5, "radius": 64},
    ],
}

EXPONENT_PROFILE_BUDGET_V0 = {
    "max_k": 4,
    "max_radius": 16,
    "max_prime_count": 16,
    "max_combinations": 256,
    "max_assignments": 32,
}


def _default_budget_for_exponent_profile(exponent_profile: list[int]) -> dict[str, int]:
    """Return profile-aware default budget for the generic exponent backend."""
    if exponent_profile and all(exp == 1 for exp in exponent_profile):
        return {
            "max_k": SQUAREFREE_POLICY_V0["budget"]["max_k"],
            "max_radius": SQUAREFREE_POLICY_V0["budget"]["max_radius"],
            "max_prime_count": SQUAREFREE_POLICY_V0["budget"]["max_prime_count"],
            "max_combinations": SQUAREFREE_POLICY_V0["budget"]["max_combinations"],
            "max_assignments": 1,
        }

    return dict(EXPONENT_PROFILE_BUDGET_V0)

STRUCTURAL_PROFILE_SEARCH_SPACE_V1 = {
    "allowed_exponent_profiles": {
        "max_support_size": 3,
        "max_total_weight": 4,
        "radius_default": 16,
        "deferred_profiles": [
            [3, 1],
        ],
    },
    "squarefree_support_size_range": [3, 5],
    "squarefree_radius_default": 16,
    "squarefree_radius_overrides": {
        5: 64,
    },
}


def _structural_profile_policy_v1() -> dict[str, Any]:
    """Return the current data-driven structural profile policy."""
    return dict(STRUCTURAL_PROFILE_SEARCH_SPACE_V1)


def _normalize_slot_candidates(slot_candidates: dict[str, list[int]] | None) -> dict[str, list[int]]:
    normalized: dict[str, list[int]] = {}

    for slot_name, candidates in (slot_candidates or {}).items():
        cleaned = sorted({int(value) for value in candidates})
        if cleaned:
            normalized[str(slot_name)] = cleaned

    return normalized


def _iroot_floor(n: int, k: int) -> int:
    if k < 1:
        raise ValueError("k must be >= 1")
    if n < 0:
        raise ValueError("n must be >= 0")
    if n in (0, 1):
        return n

    lo = 0
    hi = 1
    while hi**k <= n:
        hi *= 2

    while lo + 1 < hi:
        mid = (lo + hi) // 2
        power = mid**k
        if power <= n:
            lo = mid
        else:
            hi = mid

    return lo


def _icbrt_floor(n: int) -> int:
    return _iroot_floor(n, 3)


def _candidate_primes_near_root(root: int, radius: int) -> list[int]:
    start = max(2, root - radius)
    stop = root + radius + 1
    return [p for p in range(start, stop + 1) if is_prime(p)]


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




def _generate_allowed_exponent_profiles_v2(
    *,
    max_support_size: int,
    max_total_weight: int,
    deferred_profiles: list[list[int]] | None = None,
) -> list[list[int]]:
    """Generate the currently allowed non-squarefree exponent profiles in canonical order."""
    if max_support_size < 1:
        raise ValueError("max_support_size must be >= 1")
    if max_total_weight < 1:
        raise ValueError("max_total_weight must be >= 1")

    profiles: list[list[int]] = []
    deferred_keys = {
        tuple(profile)
        for profile in (deferred_profiles or [])
    }

    def rec(remaining: int, max_part: int, prefix: list[int]) -> None:
        if prefix:
            support_size = len(prefix)
            total_weight = sum(prefix)

            if support_size <= max_support_size and total_weight <= max_total_weight:
                all_ones = all(part == 1 for part in prefix)
                monoblock_heavy = (support_size == 1 and prefix[0] >= 3)
                all_equal_heavy = (support_size >= 2 and len(set(prefix)) == 1 and prefix[0] >= 2)

                explicitly_deferred = tuple(prefix) in deferred_keys

                if (
                    not all_ones
                    and not monoblock_heavy
                    and not all_equal_heavy
                    and not explicitly_deferred
                ):
                    profiles.append(list(prefix))

        if remaining == 0 or len(prefix) >= max_support_size:
            return

        upper = min(max_part, remaining)
        for part in range(upper, 0, -1):
            rec(remaining - part, part, prefix + [part])

    for total in range(1, max_total_weight + 1):
        rec(total, total, [])

    unique_profiles: list[list[int]] = []
    seen: set[tuple[int, ...]] = set()
    for profile in profiles:
        key = tuple(profile)
        if key not in seen:
            seen.add(key)
            unique_profiles.append(profile)

    return unique_profiles


def _generate_structural_profile_candidates_v1(
    *,
    structural_radius: int | None = None,
    policy: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Generate structural profile candidates from the current search-space rules."""
    candidates: list[dict[str, Any]] = []

    policy = _structural_profile_policy_v1() if policy is None else policy
    exponent_cfg = policy["allowed_exponent_profiles"]
    exponent_radius = structural_radius or exponent_cfg["radius_default"]

    for exponent_profile in _generate_allowed_exponent_profiles_v2(
        max_support_size=exponent_cfg["max_support_size"],
        max_total_weight=exponent_cfg["max_total_weight"],
        deferred_profiles=exponent_cfg["deferred_profiles"],
    ):
        candidates.append(
            {
                "backend": "generic-exponent",
                "exponent_profile": list(exponent_profile),
                "radius": exponent_radius,
            }
        )

    lo, hi = policy["squarefree_support_size_range"]
    default_radius = policy["squarefree_radius_default"]
    overrides = policy["squarefree_radius_overrides"]

    for support_size in range(lo, hi + 1):
        candidates.append(
            {
                "backend": "generic-squarefree",
                "support_size": support_size,
                "radius": overrides.get(support_size, default_radius),
            }
        )

    return candidates


def _generate_structural_profile_candidates_v0() -> list[dict[str, Any]]:
    """Backward-compatible wrapper over the current structural search-space generator."""
    return _generate_structural_profile_candidates_v1()


def _run_structural_profile_policy_v0(
    n: int,
    output_dir: str | Path,
    *,
    structural_radius: int | None = None,
) -> dict[str, Any] | None:
    """Run the current structural profile policy over canonical generic backends."""
    for spec in _generate_structural_profile_candidates_v1(
        structural_radius=structural_radius,
    ):
        backend = spec["backend"]
        if backend == "generic-exponent":
            report = _run_generic_exponent_profile_solver(
                n,
                output_dir,
                exponent_profile=list(spec["exponent_profile"]),
                radius=spec["radius"],
                max_radius=max(spec["radius"], EXPONENT_PROFILE_BUDGET_V0["max_radius"]),
            )
        elif backend == "generic-squarefree":
            report = _run_generic_squarefree_profile_solver(
                n,
                output_dir,
                support_size=spec["support_size"],
                radius=spec["radius"],
            )
        else:
            raise ValueError(f"unknown structural backend: {backend!r}")

        if report is not None:
            return report

    return None


def _run_prime_square_solver(n: int, output_dir: str | Path) -> dict[str, Any] | None:
    """Backward-compatible adapter over the canonical generic exponent-profile backend."""
    return _run_generic_exponent_profile_solver(
        n,
        output_dir,
        exponent_profile=[2],
        radius=1,
    )


def _run_square_times_prime_solver(
    n: int,
    output_dir: str | Path,
    *,
    radius: int = 1,
) -> dict[str, Any] | None:
    """Backward-compatible adapter over the canonical generic exponent-profile backend."""
    return _run_generic_exponent_profile_solver(
        n,
        output_dir,
        exponent_profile=[2, 1],
        radius=radius,
    )


def _run_generic_squarefree_profile_solver(
    n: int,
    output_dir: str | Path,
    *,
    support_size: int,
    radius: int,
    max_k: int | None = None,
    max_radius: int | None = None,
    max_prime_count: int | None = None,
    max_combinations: int | None = None,
) -> dict[str, Any] | None:
    """Compatibility adapter for squarefree profile-driven support search."""
    if support_size < 2:
        raise ValueError("support_size must be >= 2")

    return _run_generic_exponent_profile_solver(
        n,
        output_dir,
        exponent_profile=[1] * support_size,
        radius=radius,
        max_k=max_k,
        max_radius=max_radius,
        max_prime_count=max_prime_count,
        max_combinations=max_combinations,
    )



def _run_generic_exponent_profile_solver(
    n: int,
    output_dir: str | Path,
    *,
    exponent_profile: list[int],
    radius: int,
    max_k: int | None = None,
    max_radius: int | None = None,
    max_prime_count: int | None = None,
    max_combinations: int | None = None,
    max_assignments: int | None = None,
) -> dict[str, Any] | None:
    """Generic profile-driven backend for exponent-bearing support search."""
    if not exponent_profile:
        raise ValueError("exponent_profile cannot be empty")
    if any(exp < 1 for exp in exponent_profile):
        raise ValueError("all exponents must be >= 1")

    support_size = len(exponent_profile)
    total_weight = sum(exponent_profile)

    budget_defaults = _default_budget_for_exponent_profile(exponent_profile)

    if max_k is None:
        max_k = budget_defaults["max_k"]
    if max_radius is None:
        max_radius = budget_defaults["max_radius"]
    if max_prime_count is None:
        max_prime_count = budget_defaults["max_prime_count"]
    if max_combinations is None:
        max_combinations = budget_defaults["max_combinations"]
    if max_assignments is None:
        max_assignments = budget_defaults["max_assignments"]

    if support_size > max_k:
        return None
    if radius > max_radius:
        return None

    root = _iroot_floor(n, total_weight)
    primes = _candidate_primes_near_root(root, radius)

    if len(primes) > max_prime_count:
        return None
    if len(primes) < support_size:
        return None
    if comb(len(primes), support_size) > max_combinations:
        return None

    assignments = sorted(set(permutations(exponent_profile)))
    if len(assignments) > max_assignments:
        return None

    for combo in combinations(primes, support_size):
        for exps in assignments:
            product = 1
            for p, exp in zip(combo, exps):
                product *= p ** exp

            if product != n:
                continue

            factors = [[p, exp] for p, exp in zip(combo, exps)]
            builder_report = _run_builder_from_factorization(output_dir, factors)
            return _wrap_dedicated_solver_report(
                n=n,
                kind="generic-exponent-profile",
                strategy="generic-exponent-profile-auto",
                support=list(combo),
                exponent_profile=list(exps),
                builder_report=builder_report,
            )

    return None


def _run_squarefree_k_support_solver(
    n: int,
    output_dir: str | Path,
    *,
    k: int,
    radius: int = 1,
    max_k: int | None = None,
    max_radius: int | None = None,
    max_prime_count: int | None = None,
    max_combinations: int | None = None,
) -> dict[str, Any] | None:
    """Backward-compatible adapter over the canonical generic squarefree backend."""
    return _run_generic_squarefree_profile_solver(
        n,
        output_dir,
        support_size=k,
        radius=radius,
        max_k=max_k,
        max_radius=max_radius,
        max_prime_count=max_prime_count,
        max_combinations=max_combinations,
    )


def build_from_irsr_pipeline(
    n: int,
    output_dir: str | Path,
    *,
    slot_candidates: dict[str, list[int]] | None,
    max_steps: int = 5,
    auto_seed_radii: list[int] | None = None,
    structural_radius: int | None = None,
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
        policy_report = _run_structural_profile_policy_v0(
            n,
            output_dir,
            structural_radius=structural_radius,
        )
        if policy_report is not None:
            return policy_report

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
        "structural_radius": structural_radius,
        "irsr_final_status": result["final_status"],
        "payload_summary": result["payload_summary"],
        "build_summary": result["build_summary"],
        "terminal_state": result["terminal_state"],
        "builder_report": builder_report,
    }
