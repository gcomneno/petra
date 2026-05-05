#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from collections import Counter
from dataclasses import dataclass
from typing import Callable

from pet.core import shape_signature_dict


DEFAULT_TARGET_GENERATORS = (2, 4, 6, 12, 30, 36, 60, 210)
DEFAULT_SCALE_RULES = ("pi", "half", "third", "quarter", "sqrt-digits", "log2-digits")

CLAIM = "scale comparison only; visible segment projection only; not PET(N)"


@dataclass(frozen=True)
class ScaleRule:
    name: str
    center_length: int


@dataclass(frozen=True)
class SegmentMatch:
    start: int
    end: int
    segment: str
    generator: int


def parse_csv_ints(raw: str) -> tuple[int, ...]:
    values: list[int] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        values.append(int(item))
    return tuple(values)


def parse_csv_strings(raw: str) -> tuple[str, ...]:
    values: list[str] = []
    for item in raw.split(","):
        item = item.strip()
        if item:
            values.append(item)
    return tuple(values)


def clamp_length(value: int, digits: int) -> int:
    return max(1, min(digits, value))


def raw_center_for_scale(rule_name: str, digits: int) -> float:
    if rule_name == "pi":
        return digits / math.pi
    if rule_name == "half":
        return digits / 2
    if rule_name == "third":
        return digits / 3
    if rule_name == "quarter":
        return digits / 4
    if rule_name == "sqrt-digits":
        return math.sqrt(digits)
    if rule_name == "log2-digits":
        return math.log2(digits)
    raise ValueError(f"unknown scale rule: {rule_name}")


def center_for_scale(rule_name: str, digits: int) -> int:
    return round(raw_center_for_scale(rule_name, digits))


def effective_scale_alias(
    scale_name: str,
    center: int,
    digits: int,
    all_scale_names: tuple[str, ...],
) -> str:
    aliases = []
    for candidate in all_scale_names:
        if center_for_scale(candidate, digits) == center:
            aliases.append(candidate)
    if aliases == [scale_name]:
        return "-"
    return ",".join(aliases)


def segment_lengths(center: int, digits: int, radius: int) -> tuple[int, ...]:
    lengths = []
    for length in range(center - radius, center + radius + 1):
        lengths.append(clamp_length(length, digits))
    return tuple(sorted(set(lengths)))


def shape_basis_hint(
    matched_count: int,
    generator_unique_count: int,
    dominant_ratio: float,
    coverage_ratio: float,
) -> str:
    if matched_count == 0:
        return "no-visible-target-shape"

    if generator_unique_count == 1:
        return "single-generator-resonance"

    if dominant_ratio >= 0.50:
        return "strong-dominant-generator-resonance"

    if coverage_ratio >= 0.80:
        return "diffuse-full-coverage-shape-field"

    if dominant_ratio >= 0.30:
        return "weak-dominant-generator-resonance"

    return "mixed-shape-field"


def find_segment_matches(
    n_text: str,
    lengths: tuple[int, ...],
    target_generators: set[int],
    shape_signature_dict: Callable[[int], dict],
) -> list[SegmentMatch]:
    matches: list[SegmentMatch] = []
    cache: dict[str, int | None] = {}

    for length in lengths:
        if length > len(n_text):
            continue

        for start in range(0, len(n_text) - length + 1):
            segment = n_text[start : start + length]

            if set(segment) == {"0"}:
                continue

            cached = cache.get(segment)
            if cached is None and segment not in cache:
                try:
                    signature = shape_signature_dict(int(segment))
                    generator = int(signature["generator"])
                except Exception:
                    generator = -1
                cache[segment] = generator
            else:
                generator = cached if cached is not None else -1

            if generator in target_generators:
                matches.append(
                    SegmentMatch(
                        start=start,
                        end=start + length,
                        segment=segment,
                        generator=generator,
                    )
                )

    return matches


def coverage_ratio(matches: list[SegmentMatch], digits: int) -> float:
    covered: set[int] = set()
    for match in matches:
        covered.update(range(match.start, match.end))
    return len(covered) / digits if digits else 0.0


def format_counts(counter: Counter[int]) -> str:
    if not counter:
        return "-"
    return ",".join(f"{generator}:{count}" for generator, count in counter.most_common())


def analyze_one_scale(
    n_text: str,
    scale_name: str,
    radius: int,
    target_generators: set[int],
    shape_signature_dict: Callable[[int], dict],
) -> dict[str, object]:
    digits = len(n_text)
    center = clamp_length(center_for_scale(scale_name, digits), digits)
    lengths = segment_lengths(center, digits, radius)
    matches = find_segment_matches(
        n_text=n_text,
        lengths=lengths,
        target_generators=target_generators,
        shape_signature_dict=shape_signature_dict,
    )

    counts = Counter(match.generator for match in matches)
    matched_count = len(matches)
    unique_count = len(counts)
    coverage = coverage_ratio(matches, digits)

    if counts:
        dominant_generator, dominant_count = counts.most_common(1)[0]
        dominant_ratio = dominant_count / matched_count
    else:
        dominant_generator = "-"
        dominant_count = 0
        dominant_ratio = 0.0

    hint = shape_basis_hint(
        matched_count=matched_count,
        generator_unique_count=unique_count,
        dominant_ratio=dominant_ratio,
        coverage_ratio=coverage,
    )

    noise_score = unique_count * (1.0 - dominant_ratio) if matched_count else 0.0

    return {
        "N": n_text,
        "digits": digits,
        "scale_name": scale_name,
        "scale_ratio": f"{center / digits:.3f}",
        "effective_scale_alias": effective_scale_alias(
            scale_name=scale_name,
            center=center,
            digits=digits,
            all_scale_names=DEFAULT_SCALE_RULES,
        ),
        "center_length": center,
        "segment_lengths": ",".join(str(length) for length in lengths),
        "matched_segment_count": matched_count,
        "matched_position_coverage_ratio": f"{coverage:.3f}",
        "dominant_matched_generator": dominant_generator,
        "dominant_matched_generator_count": dominant_count,
        "dominant_matched_generator_ratio": f"{dominant_ratio:.3f}",
        "matched_generator_unique_count": unique_count,
        "matched_generator_counts": format_counts(counts),
        "shape_basis_hint": hint,
        "noise_score": f"{noise_score:.3f}",
        "shape_basis_claim": CLAIM,
    }


def print_tsv(rows: list[dict[str, object]]) -> None:
    columns = (
        "N",
        "digits",
        "scale_name",
        "scale_ratio",
        "effective_scale_alias",
        "center_length",
        "segment_lengths",
        "matched_segment_count",
        "matched_position_coverage_ratio",
        "dominant_matched_generator",
        "dominant_matched_generator_count",
        "dominant_matched_generator_ratio",
        "matched_generator_unique_count",
        "matched_generator_counts",
        "shape_basis_hint",
        "noise_score",
        "shape_basis_claim",
    )

    print("\t".join(columns))
    for row in rows:
        print("\t".join(str(row[column]) for column in columns))


def print_blocks(rows: list[dict[str, object]]) -> None:
    previous_n = None
    for row in rows:
        n_text = str(row["N"])
        if previous_n != n_text:
            if previous_n is not None:
                print()
            print(f"N = {n_text}")
            print(f"digits = {row['digits']}")
            print(f"shape_basis_claim = {row['shape_basis_claim']}")
            previous_n = n_text

        print(f"  scale_name = {row['scale_name']}")
        print(f"    scale_ratio = {row['scale_ratio']}")
        print(f"    effective_scale_alias = {row['effective_scale_alias']}")
        print(f"    center_length = {row['center_length']}")
        print(f"    segment_lengths = {row['segment_lengths']}")
        print(f"    matched_segment_count = {row['matched_segment_count']}")
        print(f"    matched_position_coverage_ratio = {row['matched_position_coverage_ratio']}")
        print(f"    matched_generator_counts = {row['matched_generator_counts']}")
        print(f"    dominant_matched_generator = {row['dominant_matched_generator']}")
        print(f"    dominant_matched_generator_ratio = {row['dominant_matched_generator_ratio']}")
        print(f"    matched_generator_unique_count = {row['matched_generator_unique_count']}")
        print(f"    shape_basis_hint = {row['shape_basis_hint']}")
        print(f"    noise_score = {row['noise_score']}")


def positive_integer_text(raw: str) -> str:
    value = raw.strip()
    if not value.isdigit():
        raise argparse.ArgumentTypeError(f"not a positive integer: {raw!r}")
    if int(value) <= 0:
        raise argparse.ArgumentTypeError(f"not a positive integer: {raw!r}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare PET shadow shape-aware segment projections across relative scale rules."
    )
    parser.add_argument("numbers", nargs="+", type=positive_integer_text)
    parser.add_argument(
        "--scale-rules",
        default=",".join(DEFAULT_SCALE_RULES),
        help="Comma-separated scale rules. Default: pi,half,third,quarter,sqrt-digits,log2-digits",
    )
    parser.add_argument(
        "--scale-radius",
        type=int,
        default=1,
        help="Radius around the center segment length. Default: 1",
    )
    parser.add_argument(
        "--target-generators",
        default=",".join(str(value) for value in DEFAULT_TARGET_GENERATORS),
        help="Comma-separated PET generator targets. Default: 2,4,6,12,30,36,60,210",
    )
    parser.add_argument(
        "--format",
        choices=("tsv", "blocks"),
        default="tsv",
        help="Output format. Default: tsv",
    )
    args = parser.parse_args()

    if args.scale_radius < 0:
        raise SystemExit("--scale-radius must be >= 0")

    scale_rules = parse_csv_strings(args.scale_rules)
    target_generators = set(parse_csv_ints(args.target_generators))
    rows: list[dict[str, object]] = []
    for n_text in args.numbers:
        for scale_name in scale_rules:
            rows.append(
                analyze_one_scale(
                    n_text=n_text,
                    scale_name=scale_name,
                    radius=args.scale_radius,
                    target_generators=target_generators,
                    shape_signature_dict=shape_signature_dict,
                )
            )

    if args.format == "blocks":
        print_blocks(rows)
    else:
        print_tsv(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
