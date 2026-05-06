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

    print("\t".join(columns))

    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["N"], []).append(row)

    for n_text, group in grouped.items():
        usable = [row for row in group if row["support_status"] != "none"]
        if not usable:
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

        selected = max(usable, key=support_score)
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
        choices=("tsv", "summary-by-n"),
        default="tsv",
    )
    args = parser.parse_args()

    if args.depth < 0:
        raise SystemExit("--depth must be >= 0")

    rows: list[dict[str, str]] = []
    for n_text in args.numbers:
        for order in parse_csv_ints(args.orders):
            rows.append(
                matrix_row(
                    n_text=n_text,
                    order=order,
                    depth=args.depth,
                    scale_rules=args.scale_rules,
                )
            )

    if args.format == "summary-by-n":
        print_summary_by_n(rows)
    else:
        print_tsv(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
