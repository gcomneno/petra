#!/usr/bin/env python3
from __future__ import annotations

import argparse
import multiprocessing as mp
import time
from collections import Counter
from typing import Any

from pet.core import shape_signature_dict


def compute_signature(n: int) -> dict[str, Any]:
    return shape_signature_dict(n)


def run_signature_with_timeout(
    n: int,
    timeout_seconds: float,
) -> tuple[str, float, dict[str, Any] | None]:
    start = time.monotonic()

    if n < 2:
        return "unit-or-empty", time.monotonic() - start, None

    with mp.Pool(processes=1) as pool:
        result = pool.apply_async(compute_signature, (n,))
        try:
            signature = result.get(timeout=timeout_seconds)
        except mp.TimeoutError:
            pool.terminate()
            pool.join()
            return "timeout", time.monotonic() - start, None

    return "ok", time.monotonic() - start, signature


def split_decimal_blocks(n: int, block_width: int) -> list[str]:
    digits = str(n)
    blocks: list[str] = []

    while digits:
        blocks.append(digits[-block_width:])
        digits = digits[:-block_width]

    return list(reversed(blocks))


def block_transition_kind(left: str, right: str) -> str:
    if set(left) == {"9"} and set(right) == {"0"}:
        return "saturated-to-empty"
    if set(left) == {"0"} and set(right) == {"9"}:
        return "empty-to-saturated"
    if set(right) == {"0"}:
        return "to-empty"
    if set(left) == {"0"}:
        return "from-empty"
    if set(left) == {"9"}:
        return "from-saturated"
    if set(right) == {"9"}:
        return "to-saturated"
    return "ordinary"


def format_generator(signature: dict[str, Any] | None) -> str:
    if signature is None:
        return "1"
    return str(signature.get("generator", "unknown"))


def summarize_width(
    n: int,
    width: int,
    full_generator: str,
    timeout_seconds: float,
) -> dict[str, str]:
    blocks = split_decimal_blocks(n, width)
    local_generators: list[str] = []
    unit_or_empty_count = 0

    for block in blocks:
        value = int(block)
        status, _elapsed, signature = run_signature_with_timeout(value, timeout_seconds)
        if status == "unit-or-empty":
            unit_or_empty_count += 1
            continue
        local_generators.append(format_generator(signature))

    generator_counts = Counter(local_generators)
    if generator_counts:
        dominant_generator = sorted(
            generator_counts.items(),
            key=lambda item: (-item[1], int(item[0])),
        )[0][0]
    else:
        dominant_generator = "1"

    local_generator_set = sorted(set(local_generators), key=lambda value: int(value))
    full_generator_in_local_set = full_generator in local_generator_set

    transition_kinds = [
        block_transition_kind(left, right)
        for left, right in zip(blocks, blocks[1:])
    ]

    has_empty_edge = any("empty" in kind for kind in transition_kinds)
    has_saturated_edge = any("saturated" in kind for kind in transition_kinds)

    if len(blocks) == 1:
        coupling_hint = "identity-single-block"
        candidate_generator = full_generator
    elif has_saturated_edge:
        coupling_hint = "saturated-edge-coupled"
        candidate_generator = dominant_generator
    elif has_empty_edge:
        coupling_hint = "empty-edge-coupled"
        candidate_generator = dominant_generator
    elif full_generator_in_local_set:
        coupling_hint = "local-generator-hit"
        candidate_generator = full_generator
    else:
        coupling_hint = "positional-coupling-created-generator"
        candidate_generator = dominant_generator

    return {
        "width": str(width),
        "block_count": str(len(blocks)),
        "informative_block_count": str(len(local_generators)),
        "unit_or_empty_block_count": str(unit_or_empty_count),
        "local_generator_set": ",".join(local_generator_set) if local_generator_set else "none",
        "dominant_local_generator": dominant_generator,
        "full_generator_in_local_set": "yes" if full_generator_in_local_set else "no",
        "candidate_shadow_generator": candidate_generator,
        "shadow_coupling_hint": coupling_hint,
    }


def dominant_value(values: list[str]) -> str:
    if not values:
        return "none"
    counts = Counter(values)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def study_number(n: int, widths: list[int], timeout_seconds: float) -> dict[str, str]:
    full_status, full_elapsed, full_signature = run_signature_with_timeout(
        n,
        timeout_seconds,
    )
    full_generator = format_generator(full_signature)

    width_summaries = [
        summarize_width(n, width, full_generator, timeout_seconds)
        for width in widths
    ]

    candidate_generators = [
        summary["candidate_shadow_generator"]
        for summary in width_summaries
    ]
    coupling_hints = [
        summary["shadow_coupling_hint"]
        for summary in width_summaries
    ]

    non_identity = [
        summary
        for summary in width_summaries
        if summary["shadow_coupling_hint"] != "identity-single-block"
    ]

    non_identity_candidates = [
        summary["candidate_shadow_generator"]
        for summary in non_identity
    ]

    local_hit_count = sum(
        1
        for summary in width_summaries
        if summary["full_generator_in_local_set"] == "yes"
    )

    identity_scale_count = sum(
        1
        for summary in width_summaries
        if summary["shadow_coupling_hint"] == "identity-single-block"
    )

    candidate_unique_count = len(set(candidate_generators))
    candidate_stability = (
        "stable"
        if candidate_unique_count == 1
        else "mixed"
    )

    non_identity_candidate_stability = (
        "none"
        if not non_identity_candidates
        else "stable"
        if len(set(non_identity_candidates)) == 1
        else "mixed"
    )

    return {
        "N": str(n),
        "digits": str(len(str(n))),
        "widths": ",".join(str(width) for width in widths),
        "full_signature_status": full_status,
        "full_signature_elapsed_seconds": f"{full_elapsed:.2f}",
        "full_generator": full_generator,
        "candidate_shadow_generators": ",".join(candidate_generators),
        "candidate_generator_unique_count": str(candidate_unique_count),
        "candidate_generator_stability": candidate_stability,
        "non_identity_candidate_stability": non_identity_candidate_stability,
        "dominant_candidate_shadow_generator": dominant_value(candidate_generators),
        "shadow_coupling_hints": ",".join(coupling_hints),
        "dominant_shadow_coupling_hint": dominant_value(coupling_hints),
        "local_generator_hit_count": str(local_hit_count),
        "identity_scale_count": str(identity_scale_count),
        "scale_sensitivity": "low" if candidate_stability == "stable" else "high",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Study PET block-shadow summaries across multiple decimal block widths."
    )
    parser.add_argument("numbers", nargs="+", type=int, metavar="N")
    parser.add_argument(
        "--widths",
        default="1,2,3,4",
        help="Comma-separated block widths. Default: 1,2,3,4.",
    )
    parser.add_argument("--timeout", type=float, default=2.0)
    args = parser.parse_args()

    widths = [int(part) for part in args.widths.split(",") if part]
    if not widths or any(width < 1 for width in widths):
        raise SystemExit("--widths expects comma-separated integers >= 1")

    fields = [
        "N",
        "digits",
        "widths",
        "full_signature_status",
        "full_signature_elapsed_seconds",
        "full_generator",
        "candidate_shadow_generators",
        "candidate_generator_unique_count",
        "candidate_generator_stability",
        "non_identity_candidate_stability",
        "dominant_candidate_shadow_generator",
        "shadow_coupling_hints",
        "dominant_shadow_coupling_hint",
        "local_generator_hit_count",
        "identity_scale_count",
        "scale_sensitivity",
    ]

    print(" ".join(fields))

    for n in args.numbers:
        row = study_number(n, widths, args.timeout)
        print(" ".join(row[field] for field in fields), flush=True)

    print()
    print("claim = multiscale shadow study only; candidate generators are local projections, not PET(N)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
