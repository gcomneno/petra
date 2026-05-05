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

    for index, block_text in enumerate(blocks):
        block_value = int(block_text)
        profile = decimal_boundary_profile(block_value)
        status, elapsed, signature = run_signature_with_timeout(block_value, timeout_seconds)

        print(
            f"{index} "
            f"{block_text} "
            f"{block_value} "
            f"{len(block_text)} "
            f"{status} "
            f"{elapsed:.2f} "
            f"{format_generator(signature)} "
            f"{format_signature(signature)} "
            f"{format_float(float(profile['decimal_rigid_border_score']))} "
            f"{profile['decimal_rigid_border_hint']}"
        )

    print()
    print("Block transitions")
    print("left_index right_index left_text right_text transition_kind")
    for index, (left, right) in enumerate(zip(blocks, blocks[1:])):
        print(
            f"{index} "
            f"{index + 1} "
            f"{left} "
            f"{right} "
            f"{block_transition_kind(left, right)}"
        )

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
