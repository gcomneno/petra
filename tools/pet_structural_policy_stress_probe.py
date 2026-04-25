#!/usr/bin/env python3
from __future__ import annotations

import random
import time
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


def _random_n(rng: random.Random, byte_count: int) -> int:
    raw = bytearray(rng.randbytes(byte_count))
    if raw:
        raw[0] |= 1
        raw[-1] |= 1
    return int.from_bytes(raw, "big")


def _run_case(
    *,
    name: str,
    n: int,
    byte_count: int,
    policy: dict[str, Any],
    radius: int,
) -> dict[str, Any]:
    started = time.perf_counter()

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

    elapsed = time.perf_counter() - started

    support = None
    if report.get("builder_report"):
        support = report["builder_report"]["support_report"].get("exponent_multiset")

    return {
        "name": name,
        "n": n,
        "digits": len(str(n)),
        "byte_count": byte_count,
        "elapsed_seconds": round(elapsed, 4),
        "terminal_outcome": report["terminal_outcome"],
        "terminal_state": report["terminal_state"],
        "exponent_multiset": support,
    }


def main() -> int:
    rng = random.Random(20260426)
    radius = 64
    policy = _policy_for(
        max_support_size=4,
        max_total_weight=5,
        deferred_profiles=[],
    )

    generated_profiles = [
        spec.get("exponent_profile")
        for spec in _generate_structural_profile_candidates_v1(
            policy=policy,
            structural_radius=radius,
        )
        if spec["backend"] == "generic-exponent"
    ]

    print("Structural policy stress probe")
    print(f"radius = {radius}")
    print(f"generated_profiles = {generated_profiles}")

    # Keep defaults intentionally small: wider random inputs can spend a long
    # time in prime-candidate generation with the current naive primality test.
    byte_sizes = [8, 12]
    cases_per_size = 2
    slow_threshold_seconds = 5.0

    failures = []
    slow_cases = []
    accidental_builds = []
    results = []

    for byte_count in byte_sizes:
        for idx in range(cases_per_size):
            name = f"random-{byte_count}b-{idx}"
            n = _random_n(rng, byte_count)

            result = _run_case(
                name=name,
                n=n,
                byte_count=byte_count,
                policy=policy,
                radius=radius,
            )

            ok = result["terminal_outcome"] in {"blocked", "built", "assembled"}
            if not ok:
                failures.append(result)

            if result["elapsed_seconds"] > slow_threshold_seconds:
                slow_cases.append(result)

            if result["terminal_outcome"] == "built":
                accidental_builds.append(result)

            results.append(result)

            print()
            print(f"{name}")
            print(f"  digits = {result['digits']}")
            print(f"  bytes = {result['byte_count']}")
            print(f"  elapsed_seconds = {result['elapsed_seconds']}")
            print(f"  terminal_outcome = {result['terminal_outcome']}")
            print(f"  terminal_state = {result['terminal_state']}")
            print(f"  exponent_multiset = {result['exponent_multiset']}")

    elapsed_values = [item["elapsed_seconds"] for item in results]
    total_elapsed = round(sum(elapsed_values), 4)
    average_elapsed = round(total_elapsed / len(elapsed_values), 4) if elapsed_values else 0.0
    max_elapsed = max(elapsed_values) if elapsed_values else 0.0
    slowest_cases = sorted(
        results,
        key=lambda item: item["elapsed_seconds"],
        reverse=True,
    )[:3]

    print()
    print(f"cases = {len(results)}")
    print(f"failures = {len(failures)}")
    print(f"slow_cases = {len(slow_cases)}")
    print(f"accidental_builds = {len(accidental_builds)}")
    print(f"total_elapsed_seconds = {total_elapsed}")
    print(f"average_elapsed_seconds = {average_elapsed}")
    print(f"max_elapsed_seconds = {max_elapsed}")

    print()
    print("Slowest cases:")
    for item in slowest_cases:
        print(
            f"- {item['name']} | bytes={item['byte_count']} "
            f"| elapsed={item['elapsed_seconds']}s "
            f"| outcome={item['terminal_outcome']}"
        )

    if accidental_builds:
        print()
        print("Accidental builds:")
        for item in accidental_builds:
            print(f"- {item['name']} profile={item['exponent_multiset']} n={item['n']}")

    return 1 if failures or slow_cases else 0


if __name__ == "__main__":
    raise SystemExit(main())
