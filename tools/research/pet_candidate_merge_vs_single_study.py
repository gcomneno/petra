#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
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


def rank(status: str, gcd_value: str) -> int:
    if status == "verified-factor":
        return 3
    if status == "usable-hit":
        return 2
    if status == "weak-hit":
        return 1

    try:
        if int(gcd_value) > 1:
            return 1
    except ValueError:
        pass

    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("numbers", nargs="+")
    args = parser.parse_args()

    print(
        "\t".join(
            [
                "N",
                "best_single_rank",
                "best_single_gcd",
                "lcm_derived_status",
                "lcm_derived_gcd",
                "lcm_derived_rank",
                "merge_beats_single",
            ]
        )
    )

    for n_text in args.numbers:
        single = run(
            [
                sys.executable,
                "tools/research/pet_operator_bridge_study.py",
                n_text,
            ]
        )

        merge = run(
            [
                sys.executable,
                "tools/research/pet_candidate_merge_study.py",
                n_text,
            ]
        )

        if single.returncode != 0 or merge.returncode != 0:
            continue

        single_rows = list(csv.DictReader(single.stdout.splitlines(), delimiter="\t"))
        merge_rows = list(csv.DictReader(merge.stdout.splitlines(), delimiter="\t"))

        best_single_rank = -1
        best_single_gcd = "-"

        for row in single_rows:
            row_rank = int(row.get("hit_rank", "-1"))
            if row_rank > best_single_rank:
                best_single_rank = row_rank
                best_single_gcd = row.get("gcd_value", "-")

        lcm_derived_status = "missing"
        lcm_derived_gcd = "-"
        lcm_derived_rank = -1

        for row in merge_rows:
            if row.get("merge_kind") != "lcm_derived":
                continue

            lcm_derived_status = row.get("status", "unknown")
            lcm_derived_gcd = row.get("gcd_value", "-")
            lcm_derived_rank = rank(
                lcm_derived_status,
                lcm_derived_gcd,
            )
            break

        merge_beats_single = (
            "yes"
            if lcm_derived_rank > best_single_rank
            else "no"
        )

        print(
            "\t".join(
                [
                    n_text,
                    str(best_single_rank),
                    best_single_gcd,
                    lcm_derived_status,
                    lcm_derived_gcd,
                    str(lcm_derived_rank),
                    merge_beats_single,
                ]
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
