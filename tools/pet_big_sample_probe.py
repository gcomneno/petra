#!/usr/bin/env python3
from __future__ import annotations

import random
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from pet.builder_from_bytes import build_from_bytes_pipeline
from pet.core import is_prime_fast


def _next_primes(start: int, count: int) -> list[int]:
    x = start | 1
    primes: list[int] = []

    while len(primes) < count:
        if is_prime_fast(x):
            primes.append(x)
        x += 2

    return primes


def _write_int(path: Path, n: int) -> Path:
    path.write_bytes(n.to_bytes((n.bit_length() + 7) // 8, "big"))
    return path


def _broader_policy() -> dict[str, Any]:
    return {
        "allowed_exponent_profiles": {
            "max_support_size": 4,
            "max_total_weight": 5,
            "radius_default": 16,
            "deferred_profiles": [],
        },
        "squarefree_support_size_range": [3, 5],
        "squarefree_radius_default": 16,
        "squarefree_radius_overrides": {
            5: 64,
        },
    }


def _run_builder_case(
    *,
    name: str,
    n: int,
    radius: int | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    with TemporaryDirectory() as td:
        root = Path(td)
        path = _write_int(root / f"{name}.bin", n)

        report = build_from_bytes_pipeline(
            path,
            root / f"out-{name}",
            mode="irsr",
            irsr_structural_radius=radius,
            irsr_structural_policy=policy,
        )

    support = None
    produced = None
    if report.get("builder_report"):
        support = report["builder_report"]["support_report"].get("exponent_multiset")
        produced = report["builder_report"]["builder_execution"].get("produced_files")

    result = {
        "name": name,
        "n": n,
        "digits": len(str(n)),
        "bytes": (n.bit_length() + 7) // 8,
        "radius": radius,
        "policy": "broader" if policy else "default",
        "requested_mode": report["requested_mode"],
        "effective_mode": report["effective_mode"],
        "terminal_outcome": report["terminal_outcome"],
        "terminal_state": report["terminal_state"],
        "exponent_multiset": support,
        "produced_count": None if produced is None else len(produced),
    }

    return result


def _print_result(result: dict[str, Any]) -> None:
    print()
    print("=" * 88)
    print(result["name"])
    print(f"n = {result['n']}")
    print(f"digits = {result['digits']}")
    print(f"bytes = {result['bytes']}")
    print(f"radius = {result['radius']}")
    print(f"policy = {result['policy']}")
    print(f"requested_mode = {result['requested_mode']}")
    print(f"effective_mode = {result['effective_mode']}")
    print(f"terminal_outcome = {result['terminal_outcome']}")
    print(f"terminal_state = {result['terminal_state']}")
    print(f"exponent_multiset = {result['exponent_multiset']}")
    print(f"produced_count = {result['produced_count']}")


def main() -> int:
    rng = random.Random(20260426)
    policy = _broader_policy()

    # A. squarefree k5 around 1e10 => 51 digits / 21 bytes.
    support_a = _next_primes(10**10, 5)
    n_a = 1
    for p in support_a:
        n_a *= p

    # B. [2,1] around 1e8.
    support_b = _next_primes(10**8, 2)
    n_b = support_b[0] ** 2 * support_b[1]

    # C. [2,1,1] around 1e7.
    support_c = _next_primes(10**7, 3)
    n_c = support_c[0] ** 2 * support_c[1] * support_c[2]

    # D. [3,2] around 1e7, broader policy.
    support_d = _next_primes(10**7 + 1000, 2)
    n_d = support_d[0] ** 3 * support_d[1] ** 2

    # E. known asymmetric semiprime; classic IRSR is expected to block.
    n_e = 71 * 48_815_831

    # F/G/H. Random samples under current default guardrail.
    n_f = int.from_bytes(rng.randbytes(16), "big") | 1
    n_g = int.from_bytes(rng.randbytes(21), "big") | 1
    n_h = int.from_bytes(rng.randbytes(22), "big") | 1

    cases = [
        ("A-default-squarefree-k5-51digits", n_a, None, None),
        ("B-default-square-times-prime-[2,1]", n_b, None, None),
        ("B-radius64-square-times-prime-[2,1]", n_b, 64, None),
        ("C-default-square-times-two-primes-[2,1,1]", n_c, None, None),
        ("C-radius64-square-times-two-primes-[2,1,1]", n_c, 64, None),
        ("D-broader-radius64-cube-times-square-[3,2]", n_d, 64, policy),
        ("E-asymmetric-semiprime-classic-expected-block", n_e, None, None),
        ("F-random-16-byte-expected-block", n_f, None, None),
        ("G-random-21-byte-expected-block", n_g, None, None),
        ("H-random-22-byte-expected-block", n_h, None, None),
    ]

    print("PET big sample probe")
    print()
    print("Generated prime supports:")
    print(f"A squarefree k5 = {support_a}")
    print(f"B [2,1] = {support_b}")
    print(f"C [2,1,1] = {support_c}")
    print(f"D [3,2] = {support_d}")

    results = []
    for name, n, radius, case_policy in cases:
        result = _run_builder_case(
            name=name,
            n=n,
            radius=radius,
            policy=case_policy,
        )
        results.append(result)
        _print_result(result)

    built = [item for item in results if item["terminal_outcome"] == "built"]
    blocked = [item for item in results if item["terminal_outcome"] == "blocked"]

    print()
    print("=" * 88)
    print("Summary")
    print(f"cases = {len(results)}")
    print(f"built = {len(built)}")
    print(f"blocked = {len(blocked)}")

    print()
    print("Built cases:")
    for item in built:
        print(
            f"- {item['name']} | profile={item['exponent_multiset']} "
            f"| digits={item['digits']} | bytes={item['bytes']}"
        )

    print()
    print("Blocked cases:")
    for item in blocked:
        reason = item["terminal_state"].get("block_reason")
        print(
            f"- {item['name']} | reason={reason} "
            f"| digits={item['digits']} | bytes={item['bytes']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
