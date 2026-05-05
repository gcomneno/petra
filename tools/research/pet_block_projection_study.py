#!/usr/bin/env python3
from __future__ import annotations

import argparse
import multiprocessing as mp
import time
from typing import Any

from pet.core import shape_signature_dict
from pet_decimal_boundary_study import decimal_boundary_profile


def compute_signature(n: int) -> dict[str, Any]:
    return shape_signature_dict(n)


def run_signature_with_timeout(n: int, timeout_seconds: float) -> tuple[str, float, dict[str, Any] | None]:
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


def format_signature(signature: dict[str, Any] | None) -> str:
    if signature is None:
        return "[]"
    return str(signature.get("signature", "unknown"))


def format_generator(signature: dict[str, Any] | None) -> str:
    if signature is None:
        return "1"
    return str(signature.get("generator", "unknown"))

def compact_signature(signature: dict[str, Any] | None) -> str:
    return format_signature(signature)


def summarize_projection(
    blocks: list[str],
    full_signature: dict[str, Any] | None,
    block_records: list[dict[str, Any]],
    transition_kinds: list[str],
) -> dict[str, str]:
    informative_records = [
        record
        for record in block_records
        if record["signature_status"] != "unit-or-empty"
    ]
    unit_or_empty_count = len(block_records) - len(informative_records)

    local_generators = [
        str(record["generator"])
        for record in informative_records
        if str(record["generator"]) != "unknown"
    ]
    local_generator_set = sorted(set(local_generators), key=lambda value: int(value))

    local_signature_set = sorted(
        {
            str(record["signature"])
            for record in informative_records
            if str(record["signature"]) != "unknown"
        }
    )

    generator_counts: dict[str, int] = {}
    for generator in local_generators:
        generator_counts[generator] = generator_counts.get(generator, 0) + 1

    if generator_counts:
        dominant_local_generator = sorted(
            generator_counts.items(),
            key=lambda item: (-item[1], int(item[0])),
        )[0][0]
    else:
        dominant_local_generator = "1"

    full_generator = format_generator(full_signature)
    full_generator_in_local_set = (
        "yes" if full_generator in local_generator_set else "no"
    )

    transition_kind_set = sorted(set(transition_kinds)) if transition_kinds else []

    has_empty_edge = any("empty" in kind for kind in transition_kinds)
    has_saturated_edge = any("saturated" in kind for kind in transition_kinds)

    if len(blocks) == 1:
        shadow_coupling_hint = "identity-single-block"
        candidate_shadow_generator = full_generator
        candidate_shadow_basis = "single block equals whole input"
    elif has_saturated_edge:
        shadow_coupling_hint = "saturated-edge-coupled"
        candidate_shadow_generator = dominant_local_generator
        candidate_shadow_basis = "dominant local generator with saturated positional edge"
    elif has_empty_edge:
        shadow_coupling_hint = "empty-edge-coupled"
        candidate_shadow_generator = dominant_local_generator
        candidate_shadow_basis = "dominant local generator with empty positional edge"
    elif full_generator_in_local_set == "yes":
        shadow_coupling_hint = "local-generator-hit"
        candidate_shadow_generator = full_generator
        candidate_shadow_basis = "full generator appears among local block generators"
    else:
        shadow_coupling_hint = "positional-coupling-created-generator"
        candidate_shadow_generator = dominant_local_generator
        candidate_shadow_basis = "dominant local generator only; global generator not locally present"

    return {
        "informative_block_count": str(len(informative_records)),
        "unit_or_empty_block_count": str(unit_or_empty_count),
        "local_generator_set": ",".join(local_generator_set) if local_generator_set else "none",
        "dominant_local_generator": dominant_local_generator,
        "full_generator_in_local_set": full_generator_in_local_set,
        "local_signature_family_count": str(len(local_signature_set)),
        "transition_kinds": ",".join(transition_kind_set) if transition_kind_set else "none",
        "shadow_coupling_hint": shadow_coupling_hint,
        "candidate_shadow_generator": candidate_shadow_generator,
        "candidate_shadow_basis": candidate_shadow_basis,
        "candidate_shadow_claim": "local projection only; not PET(N)",
    }


def format_float(value: float) -> str:
    return f"{value:.3f}"


def print_block_projection(n: int, block_width: int, timeout_seconds: float) -> None:
    blocks = split_decimal_blocks(n, block_width)
    full_status, full_elapsed, full_signature = run_signature_with_timeout(n, timeout_seconds)

    print("PET BLOCK PROJECTION STUDY")
    print()
    print(f"N = {n}")
    print(f"N_digits = {len(str(n))}")
    print(f"block_width = {block_width}")
    print(f"block_count = {len(blocks)}")
    print(f"full_signature_status = {full_status}")
    print(f"full_signature_elapsed_seconds = {full_elapsed:.2f}")
    print(f"full_generator = {format_generator(full_signature)}")
    print(f"full_signature = {format_signature(full_signature)}")
    print()
    print("Block projections")
    print(
        "block_index block_text block_value block_digits "
        "signature_status signature_elapsed_seconds generator signature "
        "decimal_rigid_border_score decimal_rigid_border_hint"
    )

    block_records: list[dict[str, Any]] = []
    for index, block_text in enumerate(blocks):
        block_value = int(block_text)
        profile = decimal_boundary_profile(block_value)
        status, elapsed, signature = run_signature_with_timeout(block_value, timeout_seconds)
        generator = format_generator(signature)
        signature_text = format_signature(signature)

        record = {
            "block_index": index,
            "block_text": block_text,
            "block_value": block_value,
            "block_digits": len(block_text),
            "signature_status": status,
            "signature_elapsed_seconds": elapsed,
            "generator": generator,
            "signature": signature_text,
            "decimal_rigid_border_score": format_float(
                float(profile["decimal_rigid_border_score"])
            ),
            "decimal_rigid_border_hint": profile["decimal_rigid_border_hint"],
        }
        block_records.append(record)

        print(
            f"{record['block_index']} "
            f"{record['block_text']} "
            f"{record['block_value']} "
            f"{record['block_digits']} "
            f"{record['signature_status']} "
            f"{record['signature_elapsed_seconds']:.2f} "
            f"{record['generator']} "
            f"{record['signature']} "
            f"{record['decimal_rigid_border_score']} "
            f"{record['decimal_rigid_border_hint']}"
        )

    print()
    print("Block transitions")
    print("left_index right_index left_text right_text transition_kind")
    transition_kinds: list[str] = []
    for index, (left, right) in enumerate(zip(blocks, blocks[1:])):
        transition_kind = block_transition_kind(left, right)
        transition_kinds.append(transition_kind)
        print(
            f"{index} "
            f"{index + 1} "
            f"{left} "
            f"{right} "
            f"{transition_kind}"
        )

    summary = summarize_projection(blocks, full_signature, block_records, transition_kinds)

    print()
    print("Packed shadow summary")
    for key, value in summary.items():
        print(f"{key} = {value}")

    print()
    print("claim = block projection only; this does not reconstruct PET(N)")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Study fixed-width decimal block projections against full PET signatures."
    )
    parser.add_argument("numbers", nargs="+", type=int, metavar="N")
    parser.add_argument("--block-width", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=2.0)
    args = parser.parse_args()

    if args.block_width < 1:
        raise SystemExit("--block-width expects integers >= 1")

    for index, n in enumerate(args.numbers):
        if index:
            print()
            print("=" * 64)
            print()

        print_block_projection(n, args.block_width, args.timeout)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
