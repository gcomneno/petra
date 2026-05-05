#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class DigitBlock:
    digit: str
    start: int
    end: int

    @property
    def length(self) -> int:
        return self.end - self.start + 1


def digit_blocks(s: str) -> list[DigitBlock]:
    if not s:
        return []

    blocks: list[DigitBlock] = []
    start = 0
    current = s[0]

    for index, digit in enumerate(s[1:], start=1):
        if digit != current:
            blocks.append(DigitBlock(current, start, index - 1))
            start = index
            current = digit

    blocks.append(DigitBlock(current, start, len(s) - 1))
    return blocks


def head_positional_weight(block: DigitBlock, n_digits: int) -> float:
    if n_digits <= 1:
        return 1.0

    center = (block.start + block.end) / 2
    return 1.0 - (center / (n_digits - 1))


def tail_positional_weight(block: DigitBlock, n_digits: int) -> float:
    if n_digits <= 1:
        return 1.0

    center = (block.start + block.end) / 2
    return center / (n_digits - 1)


def weighted_run_pressure(blocks: list[DigitBlock], n_digits: int, digit: str) -> float:
    scores = []
    for block in blocks:
        if block.digit != digit:
            continue

        length_ratio = block.length / n_digits
        positional_weight = max(
            head_positional_weight(block, n_digits),
            tail_positional_weight(block, n_digits),
        )
        scores.append(length_ratio * positional_weight)

    return max(scores, default=0.0)


def nonzero_islands(blocks: list[DigitBlock]) -> list[DigitBlock]:
    return [block for block in blocks if block.digit != "0"]


def island_span_ratio(islands: list[DigitBlock], n_digits: int) -> float:
    if not islands or n_digits <= 1:
        return 0.0

    start = islands[0].start
    end = islands[-1].end
    return (end - start + 1) / n_digits


def transition_pressure(blocks: list[DigitBlock], n_digits: int) -> float:
    if len(blocks) <= 1 or n_digits <= 1:
        return 0.0

    score = 0.0
    for left, right in zip(blocks, blocks[1:]):
        special = {left.digit, right.digit}
        if special & {"0", "9"}:
            boundary_index = left.end
            edge_weight = max(
                1.0 - (boundary_index / (n_digits - 1)),
                boundary_index / (n_digits - 1),
            )
            contrast = abs(int(left.digit) - int(right.digit)) / 9
            score = max(score, edge_weight * contrast)

    return score


def decimal_boundary_profile(n: int) -> dict[str, object]:
    s = str(n)
    n_digits = len(s)
    blocks = digit_blocks(s)
    islands = nonzero_islands(blocks)

    longest_digit_run = max((block.length for block in blocks), default=0)
    longest_zero_run = max((block.length for block in blocks if block.digit == "0"), default=0)
    longest_nine_run = max((block.length for block in blocks if block.digit == "9"), default=0)

    zero_pressure = weighted_run_pressure(blocks, n_digits, "0")
    nine_pressure = weighted_run_pressure(blocks, n_digits, "9")
    decimal_pressure = max(zero_pressure, nine_pressure)
    digit_transition = transition_pressure(blocks, n_digits)
    decimal_rigid_border_score = decimal_pressure * digit_transition
    decimal_rigid_border_hint = (
        "yes" if n_digits >= 18 and decimal_rigid_border_score >= 0.28 else "no"
    )

    return {
        "N": n,
        "digits": n_digits,
        "digit_block_count": len(blocks),
        "longest_digit_run": longest_digit_run,
        "longest_zero_run": longest_zero_run,
        "longest_nine_run": longest_nine_run,
        "zero_run_weighted_pressure": zero_pressure,
        "nine_run_weighted_pressure": nine_pressure,
        "decimal_boundary_pressure": decimal_pressure,
        "digit_island_count": len(islands),
        "digit_island_span_ratio": island_span_ratio(islands, n_digits),
        "digit_transition_pressure": digit_transition,
        "decimal_rigid_border_score": decimal_rigid_border_score,
        "decimal_rigid_border_hint": decimal_rigid_border_hint,
    }


def format_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("numbers", nargs="+", type=int)
    args = parser.parse_args()

    fields = [
        "N",
        "digits",
        "digit_block_count",
        "longest_digit_run",
        "longest_zero_run",
        "longest_nine_run",
        "zero_run_weighted_pressure",
        "nine_run_weighted_pressure",
        "decimal_boundary_pressure",
        "digit_island_count",
        "digit_island_span_ratio",
        "digit_transition_pressure",
        "decimal_rigid_border_score",
        "decimal_rigid_border_hint",
    ]

    print(" ".join(fields))
    for n in args.numbers:
        profile = decimal_boundary_profile(n)
        print(" ".join(format_value(profile[field]) for field in fields))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
