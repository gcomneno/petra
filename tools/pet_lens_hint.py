#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys


def run_tool(*args: str) -> str:
    result = subprocess.run(
        [sys.executable, *args],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr)
    return result.stdout


def extract_value(text: str, key: str) -> str:
    prefix = f"{key} = "
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix):]
    return "unknown"


def lens_name(leaf_count: int) -> str:
    if leaf_count == 1:
        return "one-leaf"
    if leaf_count == 2:
        return "two-leaf"
    if leaf_count == 3:
        return "three-leaf"
    if leaf_count == 4:
        return "four-leaf"
    if leaf_count == 5:
        return "five-leaf"
    if leaf_count == 6:
        return "six-leaf"
    return f"{leaf_count}-leaf"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Combine PET surface and stencil-lens diagnostics."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument("--schedule-limit", type=int, default=8)
    parser.add_argument("--max-leaves", type=int, default=8)
    parser.add_argument(
        "--flatten",
        action="store_true",
        help="pass --flatten to stencil_lens_probe",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="emit a compact operational hint",
    )
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("pet_lens_hint expects integers >= 1")

    surface = run_tool(
        "tools/surface_signature.py",
        str(args.n),
        "--schedule-limit",
        str(args.schedule_limit),
    )

    stencil_args = [
        "tools/stencil_lens_probe.py",
        str(args.n),
        "--max-leaves",
        str(args.max_leaves),
    ]
    if args.flatten:
        stencil_args.append("--flatten")

    stencil = run_tool(*stencil_args)

    digits = extract_value(surface, "digits")
    bit_length = extract_value(surface, "bit_length")
    digit_sum = extract_value(surface, "digit_sum")
    decimal_density = extract_value(surface, "decimal_surface_density")
    binary_density = extract_value(surface, "binary_surface_density")
    blade_index = extract_value(surface, "blade_index")
    blade = extract_value(surface, "blade")

    original_source_size = extract_value(stencil, "original_source_size")
    original_source_height = extract_value(stencil, "original_source_height")
    flattening_steps = extract_value(stencil, "flattening_steps")
    flattening_recommended = extract_value(stencil, "flattening_recommended")
    flatten_applied = extract_value(stencil, "flatten_applied")
    source_size = extract_value(stencil, "source_size")
    source_height = extract_value(stencil, "source_height")
    recommended_lens = extract_value(stencil, "recommended_lens")
    recommended_leaf_count = extract_value(stencil, "recommended_leaf_count")
    recommended_stencil_usage = extract_value(stencil, "recommended_stencil_usage")

    source_leaf_count = max(1, int(source_size) - 1) if source_size != "unknown" else 0
    source_lens = lens_name(source_leaf_count) if source_leaf_count else "unknown"

    if not source_leaf_count:
        target_lens = "unknown"
        target_leaf_count = "unknown"
    elif source_leaf_count == 1:
        target_lens = "none"
        target_leaf_count = "0"
    else:
        target_leaf_count_int = source_leaf_count - 1
        target_lens = lens_name(target_leaf_count_int)
        target_leaf_count = str(target_leaf_count_int)

    if args.summary:
        print("PET LENS HINT SUMMARY")
        print(f"N = {args.n}")
        print(f"blade_index = {blade_index}")
        print(f"source_lens = {source_lens}")
        print(f"source_leaf_count = {target_leaf_count}")
        print(f"target_lens = {target_lens}")
        print(f"target_leaf_count = {target_leaf_count}")
        print("target_role = full-mass lens")
        print(f"stencil_recommended_lens = {recommended_lens}")
        print(f"stencil_recommended_leaf_count = {recommended_leaf_count}")
        print(f"flatten_first = {flattening_recommended}")
        print("claim = PET lens hint only; this does not factor N")
        return 0

    print("PET LENS HINT")
    print()
    print(f"N = {args.n}")

    print()
    print("Surface")
    print(f"  digits = {digits}")
    print(f"  bit_length = {bit_length}")
    print(f"  digit_sum = {digit_sum}")
    print(f"  decimal_surface_density = {decimal_density}")
    print(f"  binary_surface_density = {binary_density}")
    print(f"  blade_index = {blade_index}")
    print(f"  blade = {blade}")

    print()
    print("Shape stencil")
    print(f"  original_source_size = {original_source_size}")
    print(f"  original_source_height = {original_source_height}")
    print(f"  flattening_steps = {flattening_steps}")
    print(f"  flattening_recommended = {flattening_recommended}")
    print(f"  flatten_applied = {flatten_applied}")
    print(f"  source_size = {source_size}")
    print(f"  source_height = {source_height}")
    print(f"  source_lens = {source_lens}")
    print(f"  source_leaf_count = {target_leaf_count}")
    print(f"  target_lens = {target_lens}")
    print(f"  target_leaf_count = {target_leaf_count}")
    print("  target_role = full-mass lens")
    print(f"  recommended_lens = {recommended_lens}")
    print(f"  recommended_leaf_count = {recommended_leaf_count}")
    print(f"  recommended_stencil_usage = {recommended_stencil_usage}")

    print()
    print("Operational hint")
    print(f"  blade_index = {blade_index}")
    print(f"  source_lens = {source_lens}")
    print(f"  source_leaf_count = {target_leaf_count}")
    print(f"  target_lens = {target_lens}")
    print(f"  target_leaf_count = {target_leaf_count}")
    print("  target_role = full-mass lens")
    print(f"  stencil_recommended_lens = {recommended_lens}")
    print(f"  stencil_recommended_leaf_count = {recommended_leaf_count}")
    print(f"  flatten_first = {flattening_recommended}")

    print()
    print("claim = PET lens hint only; this does not factor N")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
