#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from pet.builder_from_bytes import build_from_bytes_pipeline
from pet.builder_from_irsr import _generate_structural_profile_candidates_v1


def _write_int(path: Path, n: int) -> Path:
    path.write_bytes(n.to_bytes((n.bit_length() + 7) // 8, "big"))
    return path


def _policy_for(
    *,
    max_support_size: int,
    max_total_weight: int,
    deferred_profiles: list[list[int]] | None = None,
) -> dict[str, Any]:
    return {
        "allowed_exponent_profiles": {
            "max_support_size": max_support_size,
            "max_total_weight": max_total_weight,
            "radius_default": 16,
            "deferred_profiles": deferred_profiles or [],
        },
        "squarefree_support_size_range": [3, 5],
        "squarefree_radius_default": 16,
        "squarefree_radius_overrides": {
            5: 64,
        },
    }


def _generated_exponent_profiles(policy: dict[str, Any], *, radius: int) -> list[list[int]]:
    return [
        list(spec["exponent_profile"])
        for spec in _generate_structural_profile_candidates_v1(
            policy=policy,
            structural_radius=radius,
        )
        if spec["backend"] == "generic-exponent"
    ]


def _run_case(
    *,
    name: str,
    n: int,
    expected_profile: list[int],
    policy: dict[str, Any],
    radius: int,
) -> dict[str, Any]:
    with TemporaryDirectory() as td:
        root = Path(td)
        input_file = _write_int(root / f"{name}.bin", n)

        report = build_from_bytes_pipeline(
            input_file,
            root / f"out-{name}",
            mode="irsr",
            irsr_structural_radius=radius,
            irsr_structural_policy=policy,
        )

    support = None
    if report.get("builder_report"):
        support = report["builder_report"]["support_report"].get("exponent_multiset")

    return {
        "name": name,
        "n": n,
        "digits": len(str(n)),
        "bytes": (n.bit_length() + 7) // 8,
        "expected_profile": expected_profile,
        "terminal_outcome": report["terminal_outcome"],
        "terminal_state": report["terminal_state"],
        "exponent_multiset": support,
    }


def main() -> int:
    radius = 64
    policy = _policy_for(
        max_support_size=4,
        max_total_weight=5,
        deferred_profiles=[],
    )

    print("Structural policy probe")
    print(f"radius = {radius}")
    print(f"generated_profiles = {_generated_exponent_profiles(policy, radius=radius)}")

    cases = [
        ("cube-times-prime", 100003**3 * 100019, [3, 1]),
        ("cube-times-square", 100003**3 * 100019**2, [3, 2]),
        ("square-times-three-primes", 100003**2 * 100019 * 100043 * 100049, [2, 1, 1, 1]),
    ]

    failures = []

    for name, n, expected_profile in cases:
        result = _run_case(
            name=name,
            n=n,
            expected_profile=expected_profile,
            policy=policy,
            radius=radius,
        )

        ok = (
            result["terminal_outcome"] == "built"
            and result["exponent_multiset"] == expected_profile
        )

        status = "OK" if ok else "FAIL"
        print()
        print(f"{status} {name}")
        print(f"  n = {result['n']}")
        print(f"  digits = {result['digits']}")
        print(f"  bytes = {result['bytes']}")
        print(f"  expected_profile = {result['expected_profile']}")
        print(f"  terminal_outcome = {result['terminal_outcome']}")
        print(f"  terminal_state = {result['terminal_state']}")
        print(f"  exponent_multiset = {result['exponent_multiset']}")

        if not ok:
            failures.append(result)

    print()
    print(f"cases = {len(cases)}")
    print(f"failures = {len(failures)}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
