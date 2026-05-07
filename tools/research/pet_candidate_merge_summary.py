#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def gcd_score(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tsv", type=Path)
    args = parser.parse_args()

    with args.tsv.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    counts: dict[str, int] = defaultdict(int)
    verified: dict[str, int] = defaultdict(int)
    gcd_sum: dict[str, int] = defaultdict(int)

    for row in rows:
        key = row["merge_kind"]

        counts[key] += 1

        if row["status"] == "verified-factor":
            verified[key] += 1

        gcd_sum[key] += gcd_score(row["gcd_value"])

    print("merge_kind\tcount\tverified_ratio\tavg_gcd")

    for key in sorted(counts):
        count = counts[key]

        ratio = verified[key] / count
        avg_gcd = gcd_sum[key] / count

        print(
            f"{key}\t{count}\t{ratio:.3f}\t{avg_gcd:.3f}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
