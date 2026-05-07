#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from io import StringIO
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_command(args: list[str]) -> str:
    result = subprocess.run(
        args,
        cwd=repo_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "command failed: "
            + " ".join(args)
            + "\nstdout:\n"
            + result.stdout
            + "\nstderr:\n"
            + result.stderr
        )

    return result.stdout


def parse_rows(output: str) -> list[dict[str, str]]:
    return list(csv.DictReader(StringIO(output), delimiter="\t"))


def decimal_morphology(n_text: str) -> str:
    digits = n_text.strip()
    unique = set(digits)

    if len(unique) <= 2 and "0" in unique and "9" in unique:
        return "saturated-9-0"

    if len(unique) <= 2 and "0" in unique:
        return "sparse-zero"

    if len(digits) >= 4:
        for period in range(1, min(6, len(digits) // 2 + 1)):
            pattern = digits[:period]
            if pattern * (len(digits) // period) + pattern[: len(digits) % period] == digits:
                return "periodic"

    if len(unique) >= max(4, len(digits) // 2):
        return "digit-mixed"

    return "structured-decimal"


def route_decision(row: dict[str, str]) -> tuple[str, str, str]:
    morphology = decimal_morphology(row["N"])
    sigma_status = row["sigma_stability_status"]
    chunk_failure = row.get("chunk_failure_mode", "-")
    chunk_lcm_matches = row.get("chunk_lcm_matches_parent", "-")

    if sigma_status == "stable-coherent-support" and chunk_failure == "local-preservation-success":
        if chunk_lcm_matches == "True":
            return (
                "local-preserved-shadow-coherent",
                "sigma-plus-lambda",
                "high",
            )
        return (
            "local-preserved-sigma-floor-risk",
            "prefer-lambda-diagnostic-over-sigma-generator",
            "medium",
        )

    if sigma_status == "stable-coherent-support" and chunk_failure == "emergent-global-generator":
        return (
            "deceptive-stable-sigma",
            "do-not-trust-sigma-generator",
            "high",
        )

    if sigma_status == "stable-coherent-support" and chunk_failure == "skipped-large-input":
        if morphology == "saturated-9-0":
            return (
                "saturated-shadow-coherent",
                "use-sigma-backbone",
                "high",
            )
        return (
            "sigma-coherent-large-field",
            "use-sigma-as-global-diagnostic",
            "medium",
        )

    if sigma_status == "fragile-depth-support":
        return (
            "fragile-shadow-field",
            "depth-sensitive-review",
            "medium",
        )

    if sigma_status in {"stable-weakening-support", "weak-stable-support", "fragile-weak-support"}:
        return (
            "weak-or-unstable-shadow-field",
            "review-sigma-as-diagnostic-only",
            "medium",
        )

    if sigma_status == "none":
        if morphology == "digit-mixed":
            return (
                "diffuse-digit-mixed-field",
                "handoff-to-new-operator",
                "medium",
            )
        return (
            "diffuse-field",
            "handoff-or-new-operator",
            "medium",
        )

    return (
        "unclassified-monster",
        "manual-review",
        "low",
    )


def shadow_rows(
    numbers: list[str],
    orders: str,
    depth: int,
    scale_rules: str,
    include_chunk: bool,
) -> list[dict[str, str]]:
    command = [
        sys.executable,
        "tools/research/pet_backbone_closure_shadow_matrix.py",
        *numbers,
        "--orders",
        orders,
        "--depth",
        str(depth),
        "--scale-rules",
        scale_rules,
        "--format",
        "stability-by-n",
    ]

    if include_chunk:
        command.append("--include-recursive-chunk-diagnosis")

    output = run_command(command)
    return parse_rows(output)


def skipped_chunk_fields() -> dict[str, str]:
    return {
        "chunk_failure_mode": "skipped-large-input",
        "chunk_split_status": "-",
        "chunk_best_merge_generator": "-",
        "chunk_lcm_matches_parent": "-",
    }


def digit_run_lengths(digits: str, target: str) -> list[int]:
    runs: list[int] = []
    current = 0
    for ch in digits:
        if ch == target:
            current += 1
        elif current:
            runs.append(current)
            current = 0
    if current:
        runs.append(current)
    return runs


def border_non_90_tail_length(digits: str) -> int:
    index = len(digits) - 1
    while index >= 0 and digits[index] not in {"0", "9"}:
        index -= 1
    return len(digits) - 1 - index


def fast_pre_route(n_text: str) -> dict[str, str] | None:
    digits = n_text.strip()
    digit_len = len(digits)
    morphology = decimal_morphology(digits)

    zero_runs = digit_run_lengths(digits, "0")
    nine_runs = digit_run_lengths(digits, "9")
    longest_zero = max(zero_runs, default=0)
    longest_nine = max(nine_runs, default=0)
    non_zero_count = sum(1 for ch in digits if ch != "0")
    non_zero_ratio = non_zero_count / digit_len if digit_len else 0.0
    border_tail = border_non_90_tail_length(digits)

    if (
        digit_len >= 24
        and longest_zero >= 8
        and longest_nine >= 8
        and border_tail <= 4
    ):
        return {
            "N": n_text,
            "digits": str(digit_len),
            "decimal_morphology": "saturated-border-field",
            "sigma_stability_status": "shortcut-skipped",
            "depth_generator": "-",
            "chunk_failure_mode": "shortcut-morphology",
            "chunk_split_status": "-",
            "chunk_best_merge_generator": "-",
            "chunk_lcm_matches_parent": "-",
            "monster_class": "saturated-border-field",
            "recommended_strategy": "use-sigma-shortcut-border-diagnostic",
            "route_confidence": "medium",
            "router_claim": "routing is diagnostic only; not PET(N)",
        }

    if (
        digit_len >= 20
        and longest_zero >= 10
        and non_zero_ratio <= 0.20
    ):
        return {
            "N": n_text,
            "digits": str(digit_len),
            "decimal_morphology": "sparse-zero-border-field",
            "sigma_stability_status": "shortcut-skipped",
            "depth_generator": "-",
            "chunk_failure_mode": "shortcut-morphology",
            "chunk_split_status": "-",
            "chunk_best_merge_generator": "-",
            "chunk_lcm_matches_parent": "-",
            "monster_class": "sparse-zero-border-field",
            "recommended_strategy": "use-sigma-shortcut-sparse-zero-diagnostic",
            "route_confidence": "medium",
            "router_claim": "routing is diagnostic only; not PET(N)",
        }

    if morphology == "periodic" and digit_len >= 20:
        return {
            "N": n_text,
            "digits": str(digit_len),
            "decimal_morphology": "obvious-periodic-field",
            "sigma_stability_status": "shortcut-skipped",
            "depth_generator": "-",
            "chunk_failure_mode": "shortcut-morphology",
            "chunk_split_status": "-",
            "chunk_best_merge_generator": "-",
            "chunk_lcm_matches_parent": "-",
            "monster_class": "obvious-periodic-field",
            "recommended_strategy": "use-sigma-shortcut-periodic-diagnostic",
            "route_confidence": "medium",
            "router_claim": "routing is diagnostic only; not PET(N)",
        }

    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Route PET shadow/chunk diagnostics into monster classes and recommended strategies."
    )
    parser.add_argument("numbers", nargs="+")
    parser.add_argument("--orders", default="1,2,3,4,5")
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument(
        "--scale-rules",
        default="half,quarter,sqrt-digits,log2-digits",
    )
    parser.add_argument(
        "--max-chunk-digits",
        type=int,
        default=8,
        help="Run Λ_chunk only for inputs with at most this many digits. Default: 8.",
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Print per-number progress messages to stderr.",
    )
    args = parser.parse_args()

    columns = (
        "N",
        "digits",
        "decimal_morphology",
        "sigma_stability_status",
        "sigma_depth_generator",
        "chunk_failure_mode",
        "chunk_split_status",
        "chunk_best_merge_generator",
        "chunk_lcm_matches_parent",
        "monster_class",
        "recommended_strategy",
        "route_confidence",
        "router_claim",
    )

    print("\t".join(columns))

    rows: list[dict[str, str]] = []

    for index, n_text in enumerate(args.numbers, start=1):
        if args.progress:
            print(
                f"[router] processing {index}/{len(args.numbers)}: {n_text}",
                file=sys.stderr,
                flush=True,
            )

        shortcut = fast_pre_route(n_text)
        if shortcut is not None:
            rows.append(shortcut)
            continue

        include_chunk = len(n_text) <= args.max_chunk_digits
        row = shadow_rows(
            [n_text],
            args.orders,
            args.depth,
            args.scale_rules,
            include_chunk=include_chunk,
        )[0]

        if not include_chunk:
            row.update(skipped_chunk_fields())

        rows.append(row)

    rows_by_n = {row["N"]: row for row in rows}

    for n_text in args.numbers:
        row = rows_by_n[n_text]
        if row["sigma_stability_status"] == "shortcut-skipped":
            monster_class = row["monster_class"]
            strategy = row["recommended_strategy"]
            confidence = row["route_confidence"]
        else:
            monster_class, strategy, confidence = route_decision(row)
        out = {
            "N": row["N"],
            "digits": row["digits"],
            "decimal_morphology": decimal_morphology(row["N"]),
            "sigma_stability_status": row["sigma_stability_status"],
            "sigma_depth_generator": row["depth_generator"],
            "chunk_failure_mode": row.get("chunk_failure_mode", "-"),
            "chunk_split_status": row.get("chunk_split_status", "-"),
            "chunk_best_merge_generator": row.get("chunk_best_merge_generator", "-"),
            "chunk_lcm_matches_parent": row.get("chunk_lcm_matches_parent", "-"),
            "monster_class": monster_class,
            "recommended_strategy": strategy,
            "route_confidence": confidence,
            "router_claim": "routing is diagnostic only; not PET(N)",
        }
        print("\t".join(out[column] for column in columns))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
