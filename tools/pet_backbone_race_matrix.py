#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass

from pet_backbone_race import (
    digit_count,
    parse_orders,
    run_candidate,
    candidate_score,
    selection_quality,
)


@dataclass(frozen=True)
class Sample:
    label: str
    n: int


DEFAULT_SAMPLES = [
    Sample("prime", 101),
    Sample("prime", 137),
    Sample("prime", 997),
    Sample("prime", 1009),
    Sample("prime", 10007),
    Sample("power", 16),
    Sample("power", 64),
    Sample("power", 81),
    Sample("power", 256),
    Sample("power", 512),
    Sample("power", 625),
    Sample("power", 729),
    Sample("power", 4096),
    Sample("power", 32768),
    Sample("power", 65536),
    Sample("mixed", 210),
    Sample("mixed", 2310),
    Sample("mixed", 30030),
    Sample("mixed", 510510),
    Sample("mixed", 9699690),
    Sample("diagonal", 11111),
    Sample("diagonal", 99999),
    Sample("diagonal", 1111111111),
    Sample("diagonal", 9999999999),
    Sample("border", 10000),
    Sample("border", 10001),
    Sample("border", 99991),
    Sample("border", 12345),
    Sample("border", 54321),
    Sample("border", 2024),
]


def parse_sample(raw: str) -> Sample:
    if ":" not in raw:
        raise SystemExit("--sample expects CLASS:N entries")

    label, raw_n = raw.split(":", 1)
    label = label.strip()
    if not label:
        raise SystemExit("--sample expects a non-empty class label")

    n = int(raw_n)
    if n < 2:
        raise SystemExit("--sample expects N >= 2")

    return Sample(label, n)


def select_candidate(n: int, base: int, raw_orders: str | None, operator_depth: str):
    n_digits = digit_count(n, base)
    orders = parse_orders(raw_orders, n_digits)
    candidates = [
        run_candidate(n, order, operator_depth)
        for order in orders
    ]
    selected = min(candidates, key=lambda candidate: candidate_score(candidate, n_digits))
    return n_digits, selected


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print a compact PET backbone race diagnostic matrix."
    )
    parser.add_argument("--base", type=int, default=10)
    parser.add_argument("--orders")
    parser.add_argument("--operator-depth", default="auto")
    parser.add_argument(
        "--sample",
        action="append",
        help="Add one sample as CLASS:N. If omitted, the default diagnostic set is used.",
    )
    args = parser.parse_args()

    if args.base < 2:
        raise SystemExit("--base expects integers >= 2")

    samples = [parse_sample(raw) for raw in args.sample] if args.sample else DEFAULT_SAMPLES

    print(
        "N | class | n_digits | selected_backbone_order | "
        "selected_result | selected_move_count | selection_quality | selected_sequence"
    )

    for sample in samples:
        n_digits, selected = select_candidate(
            sample.n,
            args.base,
            args.orders,
            args.operator_depth,
        )
        print(
            f"{sample.n} | "
            f"{sample.label} | "
            f"{n_digits} | "
            f"{selected.order} | "
            f"{selected.result} | "
            f"{selected.move_count} | "
            f"{selection_quality(selected)} | "
            f"{selected.sequence}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
