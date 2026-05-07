#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import subprocess
import sys
from pathlib import Path


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


def parse_candidates(handoff_text: str) -> list[dict[str, str]]:
    count_raw = extract_key(handoff_text, "candidate_count")

    try:
        count = int(count_raw)
    except ValueError:
        return []

    base_count_raw = extract_key(handoff_text, "candidate_base_count")

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
                "source": extract_key(
                    handoff_text,
                    f"candidate_{index}_source",
                ),
                "is_base": "yes" if index <= base_count else "no",
            }
        )

    return rows


def lcm_many(values: list[int]) -> int:
    result = 1

    for value in values:
        result = math.lcm(result, value)

    return result


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


def study_row(
    n_text: str,
    merge_kind: str,
    values: list[int],
) -> str:
    if not values:
        return ""

    if merge_kind.startswith("product"):
        merged = math.prod(values)
    else:
        merged = lcm_many(values)

    status, gcd_value = verify(n_text, merged)

    return "\t".join(
        [
            n_text,
            merge_kind,
            str(len(values)),
            str(merged),
            status,
            gcd_value,
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("numbers", nargs="+")
    args = parser.parse_args()

    print(
        "\t".join(
            [
                "N",
                "merge_kind",
                "candidate_count",
                "merged_value",
                "status",
                "gcd_value",
            ]
        )
    )

    for n_text in args.numbers:
        handoff = run(
            [
                "tools/core/pet_classic_handoff_route.py",
                n_text,
                "--include-monster-route",
            ]
        )

        if handoff.returncode != 0:
            continue

        candidates = parse_candidates(handoff.stdout)

        all_values = [
            int(row["value"])
            for row in candidates
        ]

        base_values = [
            int(row["value"])
            for row in candidates
            if row["is_base"] == "yes"
        ]

        derived_values = [
            int(row["value"])
            for row in candidates
            if row["is_base"] == "no"
        ]

        rows = [
            study_row(n_text, "product_all", all_values),
            study_row(n_text, "lcm_all", all_values),
            study_row(n_text, "product_base", base_values),
            study_row(n_text, "lcm_base", base_values),
            study_row(n_text, "product_derived", derived_values),
            study_row(n_text, "lcm_derived", derived_values),
        ]

        for row in rows:
            if row:
                print(row)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
