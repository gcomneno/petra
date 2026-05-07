#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def rank(row: dict[str, str]) -> int:
    try:
        return int(row["hit_rank"])
    except (KeyError, ValueError):
        return -1


def summarize(
    rows: list[dict[str, str]],
    key: str,
) -> list[tuple[str, int, float]]:
    sums: dict[str, int] = defaultdict(int)
    counts: dict[str, int] = defaultdict(int)

    for row in rows:
        value = row.get(key, "unknown")
        sums[value] += rank(row)
        counts[value] += 1

    summary: list[tuple[str, int, float]] = []

    for value in sorted(counts):
        count = counts[value]
        avg = sums[value] / count if count else 0.0
        summary.append((value, count, avg))

    return summary


def print_summary(
    title: str,
    rows: list[tuple[str, int, float]],
) -> None:
    print(f"\n== {title} ==")
    print("key\tcount\tavg_rank")

    for key, count, avg_rank in rows:
        print(f"{key}\t{count}\t{avg_rank:.3f}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize observed PET candidate transition TSV output."
    )
    parser.add_argument("tsv", type=Path)
    args = parser.parse_args()

    rows = read_rows(args.tsv)

    if not rows:
        print("No rows found.", file=sys.stderr)
        return 1

    for key in (
        "candidate_source",
        "candidate_kind",
        "candidate_is_base",
        "monster_class",
        "width_gap",
        "depth_sum_gap",
        "signature_prefix_match",
        "signature_suffix_match",
        "distance_to_n",
        "gcd_class",
    ):
        print_summary(
            key,
            summarize(rows, key),
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
