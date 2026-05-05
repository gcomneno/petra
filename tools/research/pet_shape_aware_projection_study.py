#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from collections import Counter
from typing import Any

from pet.core import shape_signature_dict


DEFAULT_TARGET_GENERATORS = [2, 4, 6, 12, 30, 36, 60, 210]


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def signature_for_value(value: int) -> dict[str, Any] | None:
    if value < 2:
        return None
    return shape_signature_dict(value)


def iter_segments(
    digits: str,
    segment_lengths: set[int],
) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []

    for start in range(len(digits)):
        for length in sorted(segment_lengths):
            end = start + length
            if end > len(digits):
                continue
            text = digits[start:end]
            value = int(text)

            if value < 2:
                continue

            signature = signature_for_value(value)
            if signature is None:
                continue

            segments.append(
                {
                    "start": start,
                    "end": end,
                    "text": text,
                    "value": value,
                    "digits": len(text),
                    "generator": int(signature["generator"]),
                    "signature": signature["signature"],
                }
            )

    return segments


def classify_projection(
    matched_segments: list[dict[str, Any]],
    target_generators: set[int],
) -> str:
    if not matched_segments:
        return "no-target-shape-match"

    generator_counts = Counter(segment["generator"] for segment in matched_segments)
    dominant_generator, dominant_count = sorted(
        generator_counts.items(),
        key=lambda item: (-item[1], item[0]),
    )[0]

    if len(generator_counts) == 1:
        return "single-shape-resonance"

    if dominant_count >= max(2, len(matched_segments) // 2):
        return "dominant-shape-resonance"

    if len(generator_counts) >= min(4, len(target_generators)):
        return "mixed-shape-field"

    return "weak-shape-resonance"


def covered_positions(segments: list[dict[str, Any]], digits: int) -> int:
    covered = set()
    for segment in segments:
        covered.update(range(segment["start"], segment["end"]))
    return len(covered)


def format_counter(counter: Counter[int]) -> str:
    if not counter:
        return "none"
    return ",".join(
        f"{key}:{value}"
        for key, value in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Study visible decimal segments that resonate with known PET shape generators."
    )
    parser.add_argument("numbers", nargs="+", type=int, metavar="N")
    parser.add_argument("--max-segment-digits", type=int, default=4)
    parser.add_argument(
        "--scale-rule",
        choices=("up-to-max", "pi"),
        default="up-to-max",
        help="Segment scale rule. up-to-max scans all lengths up to max; pi scans around round(digits/pi).",
    )
    parser.add_argument(
        "--scale-radius",
        type=int,
        default=1,
        help="Radius around the selected scale for --scale-rule pi.",
    )
    parser.add_argument(
        "--target-generators",
        default=",".join(str(value) for value in DEFAULT_TARGET_GENERATORS),
        help="Comma-separated PET generators to treat as known target shapes.",
    )
    parser.add_argument("--max-matches", type=int, default=40)
    args = parser.parse_args()

    if args.max_segment_digits < 1:
        raise SystemExit("--max-segment-digits expects integers >= 1")
    if args.scale_radius < 0:
        raise SystemExit("--scale-radius expects integers >= 0")

    target_generators = {
        int(part)
        for part in args.target_generators.split(",")
        if part.strip()
    }

    if not target_generators:
        raise SystemExit("--target-generators must contain at least one integer")

    for index, n in enumerate(args.numbers):
        if index:
            print()
            print("=" * 64)
            print()

        digits = str(n)
        if args.scale_rule == "pi":
            pi_scale = max(1, round(len(digits) / math.pi))
            segment_lengths = {
                length
                for length in range(
                    pi_scale - args.scale_radius,
                    pi_scale + args.scale_radius + 1,
                )
                if 1 <= length <= len(digits)
            }
        else:
            pi_scale = 0
            segment_lengths = set(range(1, args.max_segment_digits + 1))

        segments = iter_segments(digits, segment_lengths)
        matched_segments = [
            segment
            for segment in segments
            if segment["generator"] in target_generators
        ]

        generator_counts = Counter(
            segment["generator"]
            for segment in matched_segments
        )
        if generator_counts:
            dominant_generator, dominant_count = sorted(
                generator_counts.items(),
                key=lambda item: (-item[1], item[0]),
            )[0]
        else:
            dominant_generator = "none"
            dominant_count = 0

        matched_count = len(matched_segments)
        dominant_ratio = dominant_count / matched_count if matched_count else 0.0
        generator_unique_count = len(generator_counts)

        covered = covered_positions(matched_segments, len(digits))
        coverage_ratio = covered / len(digits) if digits else 0.0
        projection_hint = classify_projection(matched_segments, target_generators)

        print("PET SHAPE-AWARE PROJECTION STUDY")
        print()
        print(f"N = {n}")
        print(f"N_digits = {len(digits)}")
        print(f"scale_rule = {args.scale_rule}")
        print(f"max_segment_digits = {args.max_segment_digits}")
        print(f"pi_scale_digits = {pi_scale if args.scale_rule == 'pi' else 'n/a'}")
        print(f"segment_lengths = {','.join(str(length) for length in sorted(segment_lengths))}")
        print(f"target_generators = {','.join(str(value) for value in sorted(target_generators))}")
        print(f"segment_count = {len(segments)}")
        print(f"matched_segment_count = {len(matched_segments)}")
        print(f"matched_position_coverage = {covered}/{len(digits)}")
        print(f"matched_position_coverage_ratio = {coverage_ratio:.3f}")
        print(f"matched_generator_counts = {format_counter(generator_counts)}")
        print(f"matched_generator_unique_count = {generator_unique_count}")
        print(f"dominant_matched_generator = {dominant_generator}")
        print(f"dominant_matched_generator_count = {dominant_count}")
        print(f"dominant_matched_generator_ratio = {dominant_ratio:.3f}")
        print(f"shape_aware_projection_hint = {projection_hint}")
        print()
        print("Matched segments")
        print("start end text value digits generator signature")

        for segment in matched_segments[: args.max_matches]:
            print(
                f"{segment['start']} "
                f"{segment['end']} "
                f"{segment['text']} "
                f"{segment['value']} "
                f"{segment['digits']} "
                f"{segment['generator']} "
                f"{segment['signature']}"
            )

        if len(matched_segments) > args.max_matches:
            print(f"... truncated_matches = {len(matched_segments) - args.max_matches}")

        print()
        print("claim = shape-aware visible segment projection only; this does not reconstruct PET(N)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
