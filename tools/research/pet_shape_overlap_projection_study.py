#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from collections import Counter, defaultdict
from dataclasses import dataclass

from pet.core import shape_signature_dict


DEFAULT_TARGET_GENERATORS = (2, 4, 6, 12, 30, 36, 60, 210)
DEFAULT_SCALE_RULES = ("pi", "third", "half", "quarter", "sqrt-digits", "log2-digits")

CLAIM = "overlap projection only; visible segment projection only; not PET(N)"


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
        if item:
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
    if rule_name == "third":
        return digits / 3
    if rule_name == "half":
        return digits / 2
    if rule_name == "quarter":
        return digits / 4
    if rule_name == "sqrt-digits":
        return math.sqrt(digits)
    if rule_name == "log2-digits":
        return math.log2(digits)
    raise ValueError(f"unknown scale rule: {rule_name}")


def center_for_scale(rule_name: str, digits: int) -> int:
    return round(raw_center_for_scale(rule_name, digits))


def segment_lengths(center: int, digits: int, radius: int) -> tuple[int, ...]:
    lengths = []
    for length in range(center - radius, center + radius + 1):
        lengths.append(clamp_length(length, digits))
    return tuple(sorted(set(lengths)))


def effective_scale_alias(
    scale_name: str,
    center: int,
    digits: int,
    all_scale_names: tuple[str, ...],
) -> str:
    aliases = [
        candidate
        for candidate in all_scale_names
        if center_for_scale(candidate, digits) == center
    ]
    if aliases == [scale_name]:
        return "-"
    return ",".join(aliases)


def find_segment_matches(
    n_text: str,
    lengths: tuple[int, ...],
    target_generators: set[int],
) -> list[SegmentMatch]:
    matches: list[SegmentMatch] = []
    cache: dict[str, int] = {}

    for length in lengths:
        if length > len(n_text):
            continue

        for start in range(0, len(n_text) - length + 1):
            segment = n_text[start : start + length]

            if set(segment) == {"0"}:
                continue

            if segment not in cache:
                try:
                    signature = shape_signature_dict(int(segment))
                    generator = int(signature["generator"])
                except Exception:
                    generator = -1
                cache[segment] = generator

            generator = cache[segment]
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


def overlap_counters(
    matches: list[SegmentMatch],
    digits: int,
) -> list[Counter[int]]:
    counters: list[Counter[int]] = [Counter() for _ in range(digits)]

    for match in matches:
        for index in range(match.start, match.end):
            counters[index][match.generator] += 1

    return counters


def entropy(counter: Counter[int]) -> float:
    total = sum(counter.values())
    if total <= 0:
        return 0.0

    score = 0.0
    for count in counter.values():
        probability = count / total
        score -= probability * math.log2(probability)
    return score


def overlap_hint(
    matched_count: int,
    coverage_ratio: float,
    agreement_ratio: float,
    dominant_position_ratio: float,
    average_entropy: float,
) -> str:
    if matched_count == 0 or coverage_ratio == 0.0:
        return "no-visible-overlap"

    if agreement_ratio >= 0.90 and dominant_position_ratio >= 0.90:
        return "coherent-single-generator-overlap"

    if agreement_ratio >= 0.70 and dominant_position_ratio >= 0.60:
        return "coherent-dominant-overlap"

    if (
        coverage_ratio >= 0.80
        and dominant_position_ratio >= 0.80
        and average_entropy >= 0.75
    ):
        return "dominant-diffuse-overlap"

    if coverage_ratio >= 0.80 and average_entropy >= 0.75:
        return "diffuse-overlap-field"

    if coverage_ratio < 0.50:
        return "sparse-overlap-field"

    return "mixed-overlap-field"


def analyze_scale(
    n_text: str,
    scale_name: str,
    radius: int,
    target_generators: set[int],
    all_scale_names: tuple[str, ...],
) -> dict[str, str]:
    digits = len(n_text)
    center = clamp_length(center_for_scale(scale_name, digits), digits)
    lengths = segment_lengths(center, digits, radius)
    matches = find_segment_matches(
        n_text=n_text,
        lengths=lengths,
        target_generators=target_generators,
    )

    position_counters = overlap_counters(matches, digits)
    covered = [counter for counter in position_counters if counter]
    coverage_ratio = len(covered) / digits if digits else 0.0

    single_generator_positions = 0
    dominant_generator_votes: Counter[int] = Counter()
    entropy_values: list[float] = []

    for counter in covered:
        entropy_values.append(entropy(counter))
        if len(counter) == 1:
            single_generator_positions += 1

        dominant_generator, _count = counter.most_common(1)[0]
        dominant_generator_votes[dominant_generator] += 1

    agreement_ratio = (
        single_generator_positions / len(covered)
        if covered
        else 0.0
    )

    if dominant_generator_votes:
        dominant_position_generator, dominant_position_count = dominant_generator_votes.most_common(1)[0]
        dominant_position_ratio = dominant_position_count / len(covered)
    else:
        dominant_position_generator = "-"
        dominant_position_count = 0
        dominant_position_ratio = 0.0

    average_entropy = (
        sum(entropy_values) / len(entropy_values)
        if entropy_values
        else 0.0
    )

    match_counts = Counter(match.generator for match in matches)

    hint = overlap_hint(
        matched_count=len(matches),
        coverage_ratio=coverage_ratio,
        agreement_ratio=agreement_ratio,
        dominant_position_ratio=dominant_position_ratio,
        average_entropy=average_entropy,
    )

    return {
        "N": n_text,
        "digits": str(digits),
        "scale_name": scale_name,
        "scale_ratio": f"{center / digits:.3f}",
        "effective_scale_alias": effective_scale_alias(
            scale_name=scale_name,
            center=center,
            digits=digits,
            all_scale_names=all_scale_names,
        ),
        "center_length": str(center),
        "segment_lengths": ",".join(str(length) for length in lengths),
        "matched_segment_count": str(len(matches)),
        "matched_generator_counts": (
            ",".join(f"{generator}:{count}" for generator, count in match_counts.most_common())
            if match_counts
            else "-"
        ),
        "position_coverage_ratio": f"{coverage_ratio:.3f}",
        "position_agreement_ratio": f"{agreement_ratio:.3f}",
        "dominant_position_generator": str(dominant_position_generator),
        "dominant_position_count": str(dominant_position_count),
        "dominant_position_ratio": f"{dominant_position_ratio:.3f}",
        "average_position_entropy": f"{average_entropy:.3f}",
        "overlap_hint": hint,
        "claim": CLAIM,
    }


def print_tsv(rows: list[dict[str, str]]) -> None:
    columns = (
        "N",
        "digits",
        "scale_name",
        "scale_ratio",
        "effective_scale_alias",
        "center_length",
        "segment_lengths",
        "matched_segment_count",
        "matched_generator_counts",
        "position_coverage_ratio",
        "position_agreement_ratio",
        "dominant_position_generator",
        "dominant_position_ratio",
        "average_position_entropy",
        "overlap_hint",
        "claim",
    )

    print("\t".join(columns))
    for row in rows:
        print("\t".join(row[column] for column in columns))


def print_summary_by_n(rows: list[dict[str, str]]) -> None:
    columns = (
        "N",
        "digits",
        "best_overlap_scale",
        "best_overlap_hint",
        "best_position_coverage_ratio",
        "best_position_agreement_ratio",
        "best_dominant_position_generator",
        "best_dominant_position_ratio",
        "best_average_position_entropy",
        "pi_effective_scale_alias",
        "claim",
    )

    print("\t".join(columns))

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["N"]].append(row)

    hint_rank = {
        "coherent-single-generator-overlap": 5,
        "coherent-dominant-overlap": 4,
        "dominant-diffuse-overlap": 3,
        "diffuse-overlap-field": 2,
        "mixed-overlap-field": 1,
        "sparse-overlap-field": 1,
        "no-visible-overlap": 0,
    }

    for n_text, group in grouped.items():
        best = max(
            group,
            key=lambda row: (
                hint_rank.get(row["overlap_hint"], -1),
                float(row["position_agreement_ratio"]),
                float(row["dominant_position_ratio"]),
                float(row["position_coverage_ratio"]),
                -float(row["average_position_entropy"]),
            ),
        )
        pi_rows = [row for row in group if row["scale_name"] == "pi"]
        pi_alias = pi_rows[0]["effective_scale_alias"] if pi_rows else "-"

        print(
            "\t".join(
                (
                    n_text,
                    best["digits"],
                    best["scale_name"],
                    best["overlap_hint"],
                    best["position_coverage_ratio"],
                    best["position_agreement_ratio"],
                    best["dominant_position_generator"],
                    best["dominant_position_ratio"],
                    best["average_position_entropy"],
                    pi_alias,
                    CLAIM,
                )
            )
        )


def positive_integer_text(raw: str) -> str:
    value = raw.strip()
    if not value.isdigit():
        raise argparse.ArgumentTypeError(f"not a positive integer: {raw!r}")
    if int(value) <= 0:
        raise argparse.ArgumentTypeError(f"not a positive integer: {raw!r}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Study positional overlap of PET-shadow visible segment projections."
    )
    parser.add_argument("numbers", nargs="+", type=positive_integer_text)
    parser.add_argument(
        "--scale-rules",
        default=",".join(DEFAULT_SCALE_RULES),
    )
    parser.add_argument(
        "--scale-radius",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--target-generators",
        default=",".join(str(value) for value in DEFAULT_TARGET_GENERATORS),
    )
    parser.add_argument(
        "--format",
        choices=("tsv", "summary-by-n"),
        default="tsv",
    )
    args = parser.parse_args()

    if args.scale_radius < 0:
        raise SystemExit("--scale-radius must be >= 0")

    scale_rules = parse_csv_strings(args.scale_rules)
    target_generators = set(parse_csv_ints(args.target_generators))

    rows: list[dict[str, str]] = []
    for n_text in args.numbers:
        for scale_name in scale_rules:
            rows.append(
                analyze_scale(
                    n_text=n_text,
                    scale_name=scale_name,
                    radius=args.scale_radius,
                    target_generators=target_generators,
                    all_scale_names=scale_rules,
                )
            )

    if args.format == "summary-by-n":
        print_summary_by_n(rows)
    else:
        print_tsv(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
