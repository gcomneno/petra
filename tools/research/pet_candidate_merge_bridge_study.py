#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import math
import subprocess
import sys
from pathlib import Path
from typing import Callable


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=repo_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def extract_key(text: str, key: str) -> str:
    prefix = f"{key} = "

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix):]

    return "unknown"


def dynamic_symbol(module_names: list[str], symbol_name: str):
    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue

        if hasattr(module, symbol_name):
            return getattr(module, symbol_name)

    raise RuntimeError(f"Could not import {symbol_name}")


shape_signature_dict: Callable[[int], dict] = dynamic_symbol(
    ["pet.core", "src.pet.core"],
    "shape_signature_dict",
)


def signature_width(value: int) -> int:
    return len(shape_signature_dict(value)["signature"])


def parse_candidates(handoff_text: str) -> list[dict[str, str]]:
    count_raw = extract_key(handoff_text, "candidate_count")
    base_count_raw = extract_key(handoff_text, "candidate_base_count")

    try:
        count = int(count_raw)
    except ValueError:
        return []

    try:
        base_count = int(base_count_raw)
    except ValueError:
        base_count = count

    rows: list[dict[str, str]] = []

    for index in range(1, count + 1):
        rows.append(
            {
                "value": extract_key(
                    handoff_text,
                    f"candidate_{index}_value",
                ),
                "is_base": "yes" if index <= base_count else "no",
            }
        )

    return rows


def primes() -> list[int]:
    return [
        2,
        3,
        5,
        7,
        11,
        13,
        17,
        19,
        23,
        29,
        31,
        37,
        41,
        43,
        47,
    ]


def width_lift_to_target(value: int, target_width: int) -> int:
    lifted = value

    for prime in primes():
        if signature_width(lifted) >= target_width:
            break

        if lifted % prime != 0:
            lifted *= prime

    return lifted


def proper_divisors_desc(value: int) -> list[int]:
    divisors: list[int] = []

    for candidate in range(2, int(value**0.5) + 1):
        if value % candidate != 0:
            continue

        other = value // candidate

        if other != value:
            divisors.append(other)

        if candidate != other:
            divisors.append(candidate)

    return sorted(set(divisors), reverse=True)


def verify(n_text: str, candidate_value: int) -> tuple[str, str]:
    result = run(
        [
            sys.executable,
            "tools/core/pet_classic_candidate_verify.py",
            n_text,
            "--candidate",
            str(candidate_value),
        ]
    )

    if result.returncode != 0:
        return ("verify-failed", "-")

    return (
        extract_key(result.stdout, "candidate_1_status"),
        extract_key(result.stdout, "candidate_1_gcd"),
    )


def bridge_variants(
    *,
    merged_value: int,
    n_width: int,
) -> list[tuple[str, int]]:
    variants: list[tuple[str, int]] = [
        ("derived_lcm_identity", merged_value),
    ]

    lifted = width_lift_to_target(
        merged_value,
        n_width,
    )

    if lifted != merged_value:
        variants.append(("heuristic_width_lift", lifted))

    for divisor in proper_divisors_desc(merged_value)[:6]:
        variants.append(("observed_merge_divisor", divisor))

    dedup: list[tuple[str, int]] = []
    seen: set[int] = set()

    for kind, value in variants:
        if value < 2:
            continue
        if value in seen:
            continue

        seen.add(value)
        dedup.append((kind, value))

    return dedup


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Study multi-step PET candidate merge bridges."
    )
    parser.add_argument("numbers", nargs="+")
    args = parser.parse_args()

    print(
        "\t".join(
            [
                "N",
                "n_width",
                "derived_lcm",
                "bridge_kind",
                "candidate_value",
                "candidate_width",
                "status",
                "gcd_value",
            ]
        )
    )

    for n_text in args.numbers:
        handoff = run(
            [
                sys.executable,
                "tools/core/pet_classic_handoff_route.py",
                n_text,
                "--include-monster-route",
            ]
        )

        if handoff.returncode != 0:
            continue

        n_width = signature_width(int(n_text))
        candidates = parse_candidates(handoff.stdout)

        derived_values = [
            int(row["value"])
            for row in candidates
            if row["is_base"] == "no"
        ]

        if not derived_values:
            continue

        derived_lcm = math.lcm(*derived_values)

        for bridge_kind, candidate_value in bridge_variants(
            merged_value=derived_lcm,
            n_width=n_width,
        ):
            status, gcd_value = verify(
                n_text,
                candidate_value,
            )

            print(
                "\t".join(
                    [
                        n_text,
                        str(n_width),
                        str(derived_lcm),
                        bridge_kind,
                        str(candidate_value),
                        str(signature_width(candidate_value)),
                        status,
                        gcd_value,
                    ]
                )
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
