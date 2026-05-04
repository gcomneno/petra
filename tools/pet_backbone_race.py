#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    order: int
    shape_fit: str
    result: str
    sequence: str
    move_count: int


def digit_count(n: int, base: int) -> int:
    count = 0
    current = n

    while current:
        current //= base
        count += 1

    return max(1, count)


def parse_orders(raw_orders: str | None, n_digits: int) -> list[int]:
    if raw_orders is None:
        return list(range(1, n_digits + 1))

    orders = []
    for raw in raw_orders.split(","):
        raw = raw.strip()
        if not raw:
            continue
        order = int(raw)
        if order < 1:
            raise SystemExit("--orders expects positive integers")
        orders.append(order)

    if not orders:
        raise SystemExit("--orders did not contain any valid order")

    return sorted(set(orders))


def move_count(sequence: str) -> int:
    if sequence == "none":
        return 0
    return sequence.count(" -> ") + 1


def run_candidate(n: int, order: int, operator_depth: str) -> Candidate:
    result = subprocess.run(
        [
            sys.executable,
            "tools/pet_local_probe_proposal.py",
            str(n),
            "--operator-depth",
            operator_depth,
            "--backbone-order",
            str(order),
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    shape_fit = "unknown"
    probe_result = "unknown"
    sequence = "none"

    for line in result.stdout.splitlines():
        if line.startswith("shape_fit = "):
            shape_fit = line.removeprefix("shape_fit = ")
        elif line.startswith("operator_probe_result = "):
            probe_result = line.removeprefix("operator_probe_result = ")
        elif line.startswith("selected_operator_sequence = "):
            sequence = line.removeprefix("selected_operator_sequence = ")

    return Candidate(
        order=order,
        shape_fit=shape_fit,
        result=probe_result,
        sequence=sequence,
        move_count=move_count(sequence),
    )


def candidate_score(candidate: Candidate, n_digits: int) -> tuple[int, int, int]:
    result_rank = {
        "already-matching": 0,
        "matched": 1,
        "exhausted": 2,
        "unavailable": 3,
    }.get(candidate.result, 4)

    return (
        result_rank,
        candidate.move_count,
        abs(candidate.order - n_digits),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Race PET primorial backbone candidates without factoring N."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument("--base", type=int, default=10)
    parser.add_argument("--orders")
    parser.add_argument("--operator-depth", default="auto")
    args = parser.parse_args()

    if args.n < 2:
        raise SystemExit("pet_backbone_race expects integers >= 2")
    if args.base < 2:
        raise SystemExit("--base expects integers >= 2")

    n_digits = digit_count(args.n, args.base)
    orders = parse_orders(args.orders, n_digits)
    candidates = [
        run_candidate(args.n, order, args.operator_depth)
        for order in orders
    ]
    selected = min(candidates, key=lambda candidate: candidate_score(candidate, n_digits))

    print("PET BACKBONE RACE PROTOTYPE")
    print()
    print(f"N = {args.n}")
    print(f"base = {args.base}")
    print(f"n_digits = {n_digits}")
    print(f"operator_depth = {args.operator_depth}")
    print(f"candidate_orders = {','.join(str(order) for order in orders)}")
    print()
    print("Candidates")
    for candidate in candidates:
        print(
            f"candidate_order = {candidate.order}; "
            f"shape_fit = {candidate.shape_fit}; "
            f"result = {candidate.result}; "
            f"move_count = {candidate.move_count}; "
            f"sequence = {candidate.sequence}"
        )

    print()
    print("Backbone race selection")
    print(f"selected_backbone_order = {selected.order}")
    print(f"selected_result = {selected.result}")
    print(f"selected_move_count = {selected.move_count}")
    print(f"selected_sequence = {selected.sequence}")
    print("selection_rule = prefer already-matching, then matched, then fewer moves, then order closest to n_digits")
    print()
    print("claim = PET backbone race prototype only; this does not factor N")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
