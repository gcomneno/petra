#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import multiprocessing as mp
import subprocess
import sys
import time
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

from pet.core import shape_signature_dict


CLAIM = "correlation study only; PET-shadow does not reconstruct PET(N)"


@dataclass(frozen=True)
class DecimalBoundary:
    score: str
    hint: str


@dataclass(frozen=True)
class ShadowSummary:
    lowest_noise_scale: str
    lowest_noise_score: str
    highest_dominant_scale: str
    highest_dominant_ratio: str
    pi_effective_scale_alias: str
    field_class: str


@dataclass(frozen=True)
class SignatureCost:
    status: str
    elapsed_seconds: str
    decimal_rigid_border_score: str
    decimal_rigid_border_hint: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_command(args: list[str], timeout_seconds: float | None = None) -> str:
    result = subprocess.run(
        args,
        cwd=repo_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_seconds,
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


def decimal_boundary(n_text: str) -> DecimalBoundary:
    module_path = repo_root() / "tools" / "research" / "pet_decimal_boundary_study.py"
    spec = importlib.util.spec_from_file_location("pet_decimal_boundary_study", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    profile = module.decimal_boundary_profile(int(n_text))

    return DecimalBoundary(
        score=f"{float(profile['decimal_rigid_border_score']):.3f}",
        hint=str(profile["decimal_rigid_border_hint"]),
    )

def shadow_summary(
    n_text: str,
    scale_rules: str,
    target_generators: str,
) -> ShadowSummary:
    output = run_command(
        [
            sys.executable,
            "tools/research/pet_shape_scale_compare_study.py",
            n_text,
            "--scale-rules",
            scale_rules,
            "--target-generators",
            target_generators,
            "--format",
            "summary-by-n",
        ]
    )
    row = parse_tsv_single_row(output)
    return ShadowSummary(
        lowest_noise_scale=row["lowest_noise_scale"],
        lowest_noise_score=row["lowest_noise_score"],
        highest_dominant_scale=row["highest_dominant_scale"],
        highest_dominant_ratio=row["highest_dominant_ratio"],
        pi_effective_scale_alias=row["pi_effective_scale_alias"],
        field_class=row["field_class"],
    )


def _signature_worker(n_value: int, queue: mp.Queue) -> None:
    try:
        shape_signature_dict(n_value)
    except Exception as exc:
        queue.put(("error", repr(exc)))
    else:
        queue.put(("ok", ""))


def signature_cost(n_text: str, timeout_seconds: float) -> SignatureCost:
    start = time.monotonic()
    queue: mp.Queue = mp.Queue()
    process = mp.Process(
        target=_signature_worker,
        args=(int(n_text), queue),
    )
    process.start()
    process.join(timeout_seconds)

    elapsed = time.monotonic() - start

    if process.is_alive():
        process.terminate()
        process.join()
        return SignatureCost(
            status="timeout",
            elapsed_seconds=f"{elapsed:.3f}",
            decimal_rigid_border_score="-",
            decimal_rigid_border_hint="-",
        )

    if not queue.empty():
        status, _payload = queue.get()
        if status == "ok":
            return SignatureCost(
                status="ok",
                elapsed_seconds=f"{elapsed:.3f}",
                decimal_rigid_border_score="-",
                decimal_rigid_border_hint="-",
            )
        return SignatureCost(
            status="error",
            elapsed_seconds=f"{elapsed:.3f}",
            decimal_rigid_border_score="-",
            decimal_rigid_border_hint="-",
        )

    return SignatureCost(
        status="error",
        elapsed_seconds=f"{elapsed:.3f}",
        decimal_rigid_border_score="-",
        decimal_rigid_border_hint="-",
    )

def route_pressure_hint(
    decimal_hint: str,
    field_class: str,
    signature_status: str,
) -> str:
    if signature_status == "timeout":
        if field_class == "diffuse-all-scales":
            return "shadow-diffuse-timeout"
        if decimal_hint == "yes":
            return "decimal-rigid-timeout"
        return "structured-shadow-timeout"

    if field_class == "diffuse-all-scales":
        return "shadow-diffuse-but-finished"

    if field_class in {
        "has-strong-scale",
        "has-single-generator-scale",
        "has-weak-scale",
    }:
        return "structured-shadow-finished"

    return "unclassified-finished"


def print_tsv(rows: list[dict[str, str]]) -> None:
    columns = (
        "N",
        "digits",
        "decimal_rigid_border_score",
        "decimal_rigid_border_hint",
        "field_class",
        "lowest_noise_scale",
        "lowest_noise_score",
        "highest_dominant_scale",
        "highest_dominant_ratio",
        "pi_effective_scale_alias",
        "signature_status",
        "signature_elapsed_seconds",
        "route_pressure_hint",
        "claim",
    )

    print("\t".join(columns))
    for row in rows:
        print("\t".join(row[column] for column in columns))


def positive_integer_text(raw: str) -> str:
    value = raw.strip()
    if not value.isdigit():
        raise argparse.ArgumentTypeError(f"not a positive integer: {raw!r}")
    if int(value) <= 0:
        raise argparse.ArgumentTypeError(f"not a positive integer: {raw!r}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Correlate PET-shadow field classes with decimal rigidity and signature cost."
    )
    parser.add_argument("numbers", nargs="+", type=positive_integer_text)
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Timeout for full signature cost probe. Default: 5.0",
    )
    parser.add_argument(
        "--scale-rules",
        default="pi,third,half,quarter,sqrt-digits,log2-digits",
    )
    parser.add_argument(
        "--target-generators",
        default="2,4,6,12,30,36,60,210",
    )
    args = parser.parse_args()

    rows: list[dict[str, str]] = []

    for n_text in args.numbers:
        boundary = decimal_boundary(n_text)
        shadow = shadow_summary(
            n_text=n_text,
            scale_rules=args.scale_rules,
            target_generators=args.target_generators,
        )
        cost = signature_cost(n_text=n_text, timeout_seconds=args.timeout)

        rows.append(
            {
                "N": n_text,
                "digits": str(len(n_text)),
                "decimal_rigid_border_score": boundary.score,
                "decimal_rigid_border_hint": boundary.hint,
                "field_class": shadow.field_class,
                "lowest_noise_scale": shadow.lowest_noise_scale,
                "lowest_noise_score": shadow.lowest_noise_score,
                "highest_dominant_scale": shadow.highest_dominant_scale,
                "highest_dominant_ratio": shadow.highest_dominant_ratio,
                "pi_effective_scale_alias": shadow.pi_effective_scale_alias,
                "signature_status": cost.status,
                "signature_elapsed_seconds": cost.elapsed_seconds,
                "route_pressure_hint": route_pressure_hint(
                    decimal_hint=boundary.hint,
                    field_class=shadow.field_class,
                    signature_status=cost.status,
                ),
                "claim": CLAIM,
            }
        )

    print_tsv(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
