#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from io import StringIO
from pathlib import Path


CLAIM = "backbone closure shadow matrix only; this does not factor N and does not reconstruct PET(N)"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def parse_csv_ints(raw: str) -> tuple[int, ...]:
    values: list[int] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        value = int(item)
        if value < 1:
            raise argparse.ArgumentTypeError("orders must be positive integers")
        values.append(value)

    if not values:
        raise argparse.ArgumentTypeError("expected at least one positive integer")

    return tuple(sorted(set(values)))


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


def parse_tsv_single_row(output: str) -> dict[str, str]:
    reader = csv.DictReader(StringIO(output), delimiter="\t")
    rows = list(reader)
    if len(rows) != 1:
        raise RuntimeError(f"expected exactly one TSV row, got {len(rows)}")
    return dict(rows[0])


def recursive_chunk_root_diagnosis(n_text: str) -> dict[str, str]:
    output = run_command(
        [
            sys.executable,
            "tools/research/pet_recursive_shape_chunk_study.py",
            n_text,
            "--max-depth",
            "1",
        ]
    )
    reader = csv.DictReader(StringIO(output), delimiter="\t")
    for row in reader:
        if row.get("path") == "root":
            return dict(row)
    raise RuntimeError(f"expected root chunk diagnosis for {n_text}")


def shape_summary(
    n_text: str,
    order: int,
    depth: int,
    scale_rules: str,
) -> dict[str, str]:
    output = run_command(
        [
            sys.executable,
            "tools/research/pet_shape_scale_compare_study.py",
            n_text,
            "--scale-rules",
            scale_rules,
            "--target-basis-source",
            "backbone-closure",
            "--backbone-orders",
            str(order),
            "--backbone-depth",
            str(depth),
            "--format",
            "summary-by-n",
        ]
    )
    return parse_tsv_single_row(output)


def overlap_summary(
    n_text: str,
    order: int,
    depth: int,
    scale_rules: str,
) -> dict[str, str]:
    output = run_command(
        [
            sys.executable,
            "tools/research/pet_shape_overlap_projection_study.py",
            n_text,
            "--scale-rules",
            scale_rules,
            "--target-basis-source",
            "backbone-closure",
            "--backbone-orders",
            str(order),
            "--backbone-depth",
            str(depth),
            "--format",
            "summary-by-n",
        ]
    )
    return parse_tsv_single_row(output)


def matrix_row(
    n_text: str,
    order: int,
    depth: int,
    scale_rules: str,
) -> dict[str, str]:
    shape = shape_summary(
        n_text=n_text,
        order=order,
        depth=depth,
        scale_rules=scale_rules,
    )
    overlap = overlap_summary(
        n_text=n_text,
        order=order,
        depth=depth,
        scale_rules=scale_rules,
    )

    row = {
        "N": n_text,
        "digits": str(len(n_text)),
        "backbone_order": str(order),
        "backbone_depth": str(depth),
        "field_class": shape["field_class"],
        "lowest_noise_scale": shape["lowest_noise_scale"],
        "lowest_noise_score": shape["lowest_noise_score"],
        "highest_dominant_scale": shape["highest_dominant_scale"],
        "highest_dominant_ratio": shape["highest_dominant_ratio"],
        "best_overlap_scale": overlap["best_overlap_scale"],
        "best_overlap_hint": overlap["best_overlap_hint"],
        "support_status": "",
        "position_coverage_ratio": overlap["best_position_coverage_ratio"],
        "position_agreement_ratio": overlap["best_position_agreement_ratio"],
        "dominant_position_generator": overlap["best_dominant_position_generator"],
        "dominant_position_ratio": overlap["best_dominant_position_ratio"],
        "average_position_entropy": overlap["best_average_position_entropy"],
        "pi_effective_scale_alias": shape["pi_effective_scale_alias"],
        "claim": CLAIM,
    }
    row["support_status"] = support_status(row)
    return row


def support_status(row: dict[str, str]) -> str:
    overlap_hint = row["best_overlap_hint"]
    dominant_ratio = float(row["dominant_position_ratio"])
    agreement_ratio = float(row["position_agreement_ratio"])
    entropy = float(row["average_position_entropy"])

    if (
        overlap_hint == "coherent-single-generator-overlap"
        and dominant_ratio >= 0.90
        and agreement_ratio >= 0.90
        and entropy <= 0.10
    ):
        return "coherent-support"

    if (
        overlap_hint == "coherent-dominant-overlap"
        and dominant_ratio >= 0.60
        and agreement_ratio >= 0.70
        and entropy <= 0.50
    ):
        return "coherent-support"

    if overlap_hint == "mixed-overlap-field":
        return "weak-or-noisy-support"

    return "none"

def support_score(row: dict[str, str]) -> tuple[int, float, float, float, float]:
    status_rank = {
        "coherent-support": 3,
        "weak-or-noisy-support": 1,
        "none": 0,
    }

    field_rank = {
        "has-single-generator-scale": 4,
        "has-strong-scale": 3,
        "has-weak-scale": 2,
        "diffuse-all-scales": 1,
        "no-visible-target-shape": 0,
    }

    return (
        status_rank.get(row["support_status"], -1),
        field_rank.get(row["field_class"], -1),
        float(row["dominant_position_ratio"]),
        float(row["position_agreement_ratio"]),
        -float(row["average_position_entropy"]),
    )


def print_tsv(rows: list[dict[str, str]]) -> None:
    columns = (
        "N",
        "digits",
        "backbone_order",
        "backbone_depth",
        "field_class",
        "lowest_noise_scale",
        "lowest_noise_score",
        "highest_dominant_scale",
        "highest_dominant_ratio",
        "best_overlap_scale",
        "best_overlap_hint",
        "support_status",
        "position_coverage_ratio",
        "position_agreement_ratio",
        "dominant_position_generator",
        "dominant_position_ratio",
        "average_position_entropy",
        "pi_effective_scale_alias",
        "claim",
    )

    print("\t".join(columns))
    for row in rows:
        print("\t".join(row[column] for column in columns))


def group_rows_by_n(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["N"], []).append(row)
    return grouped


def selected_support_row(group: list[dict[str, str]]) -> dict[str, str] | None:
    usable = [row for row in group if row["support_status"] != "none"]
    if not usable:
        return None
    return max(usable, key=support_score)


def stability_status(
    depth_row: dict[str, str] | None,
    next_depth_row: dict[str, str] | None,
) -> str:
    depth_status = "none" if depth_row is None else depth_row["support_status"]
    next_status = "none" if next_depth_row is None else next_depth_row["support_status"]

    if depth_status == "coherent-support" and next_status == "coherent-support":
        return "stable-coherent-support"

    if depth_status == "coherent-support" and next_status == "weak-or-noisy-support":
        return "stable-weakening-support"

    if depth_status == "coherent-support" and next_status == "none":
        return "fragile-depth-support"

    if depth_status == "weak-or-noisy-support" and next_status in {
        "coherent-support",
        "weak-or-noisy-support",
    }:
        return "weak-stable-support"

    if depth_status == "weak-or-noisy-support" and next_status == "none":
        return "fragile-weak-support"

    if depth_status == "none" and next_status == "none":
        return "none"

    return f"{depth_status}->{next_status}"


def print_summary_by_n(rows: list[dict[str, str]]) -> None:
    columns = (
        "N",
        "digits",
        "selected_backbone_order",
        "backbone_depth",
        "selected_field_class",
        "selected_overlap_hint",
        "selected_support_status",
        "selected_lowest_noise_score",
        "selected_dominant_position_generator",
        "selected_dominant_position_ratio",
        "selected_average_position_entropy",
        "support_selection_claim",
    )

    if include_recursive_chunk_diagnosis:
        columns = columns + (
            "chunk_failure_mode",
            "chunk_split_status",
            "chunk_best_merge_generator",
            "chunk_lcm_matches_parent",
        )

    print("\t".join(columns))

    grouped = group_rows_by_n(rows)

    for n_text, group in grouped.items():
        selected = selected_support_row(group)
        if selected is None:
            first = group[0]
            print(
                "\t".join(
                    (
                        n_text,
                        first["digits"],
                        "none",
                        first["backbone_depth"],
                        "diffuse-all-scales",
                        "diffuse-overlap-field",
                        "none",
                        "-",
                        "-",
                        "-",
                        "-",
                        "no coherent backbone support selected; not PET(N)",
                    )
                )
            )
            continue

        print(
            "\t".join(
                (
                    n_text,
                    selected["digits"],
                    selected["backbone_order"],
                    selected["backbone_depth"],
                    selected["field_class"],
                    selected["best_overlap_hint"],
                    selected["support_status"],
                    selected["lowest_noise_score"],
                    selected["dominant_position_generator"],
                    selected["dominant_position_ratio"],
                    selected["average_position_entropy"],
                    "selected support is diagnostic only; not PET(N)",
                )
            )
        )


def print_stability_by_n(
    depth_rows: list[dict[str, str]],
    next_depth_rows: list[dict[str, str]],
    include_recursive_chunk_diagnosis: bool = False,
) -> None:
    columns = (
        "N",
        "digits",
        "depth",
        "depth_order",
        "depth_status",
        "depth_generator",
        "next_depth",
        "next_depth_order",
        "next_depth_status",
        "next_depth_generator",
        "sigma_stability_status",
        "support_selection_claim",
    )

    print("\t".join(columns))

    grouped_depth = group_rows_by_n(depth_rows)
    grouped_next = group_rows_by_n(next_depth_rows)

    for n_text, depth_group in grouped_depth.items():
        next_group = grouped_next.get(n_text, [])
        depth_selected = selected_support_row(depth_group)
        next_selected = selected_support_row(next_group) if next_group else None

        first = depth_group[0]
        next_first = next_group[0] if next_group else None

        depth_order = "none" if depth_selected is None else depth_selected["backbone_order"]
        depth_status = "none" if depth_selected is None else depth_selected["support_status"]
        depth_generator = (
            "-"
            if depth_selected is None
            else depth_selected["dominant_position_generator"]
        )

        next_depth = (
            "-"
            if next_first is None
            else next_first["backbone_depth"]
        )
        next_depth_order = (
            "none" if next_selected is None else next_selected["backbone_order"]
        )
        next_depth_status = (
            "none" if next_selected is None else next_selected["support_status"]
        )
        next_depth_generator = (
            "-"
            if next_selected is None
            else next_selected["dominant_position_generator"]
        )

        status = stability_status(depth_selected, next_selected)
        chunk_diagnosis = (
            recursive_chunk_root_diagnosis(n_text)
            if include_recursive_chunk_diagnosis
            else {}
        )

        print(
            "\t".join(
                (
                    n_text,
                    first["digits"],
                    first["backbone_depth"],
                    depth_order,
                    depth_status,
                    depth_generator,
                    next_depth,
                    next_depth_order,
                    next_depth_status,
                    next_depth_generator,
                    status,
                    "support stability is diagnostic only; not PET(N)",
                )
                + (
                    (
                        chunk_diagnosis["failure_mode"],
                        chunk_diagnosis["split_status"],
                        chunk_diagnosis["best_merge_generator"],
                        chunk_diagnosis["lcm_matches_parent"],
                    )
                    if include_recursive_chunk_diagnosis
                    else ()
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
        description="Print a compact N x backbone-order PET-shadow matrix using backbone-closure target bases."
    )
    parser.add_argument("numbers", nargs="+", type=positive_integer_text)
    parser.add_argument(
        "--orders",
        default="1,2,3,4",
        help="Comma-separated flat backbone orders. Default: 1,2,3,4",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=2,
        help="Backbone closure depth. Default: 2",
    )
    parser.add_argument(
        "--scale-rules",
        default="pi,third,half,quarter,sqrt-digits,log2-digits",
    )
    parser.add_argument(
        "--format",
        choices=("tsv", "summary-by-n", "stability-by-n"),
        default="tsv",
    )
    parser.add_argument(
        "--include-recursive-chunk-diagnosis",
        action="store_true",
        help="Append root-level Λ_chunk diagnostics to stability-by-n output.",
    )
    args = parser.parse_args()

    if args.depth < 0:
        raise SystemExit("--depth must be >= 0")

    orders = parse_csv_ints(args.orders)

    rows: list[dict[str, str]] = []
    for n_text in args.numbers:
        for order in orders:
            rows.append(
                matrix_row(
                    n_text=n_text,
                    order=order,
                    depth=args.depth,
                    scale_rules=args.scale_rules,
                )
            )

    if args.format == "stability-by-n":
        next_rows: list[dict[str, str]] = []
        for n_text in args.numbers:
            for order in orders:
                next_rows.append(
                    matrix_row(
                        n_text=n_text,
                        order=order,
                        depth=args.depth + 1,
                        scale_rules=args.scale_rules,
                    )
                )
        print_stability_by_n(
            rows,
            next_rows,
            include_recursive_chunk_diagnosis=args.include_recursive_chunk_diagnosis,
        )
    elif args.format == "summary-by-n":
        print_summary_by_n(rows)
    else:
        print_tsv(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
