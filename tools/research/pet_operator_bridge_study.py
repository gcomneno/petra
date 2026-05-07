#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import subprocess
import sys
from pathlib import Path
from typing import Callable


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=repo_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def extract_key(text: str, key: str) -> str:
    prefix = f"{key} = "
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix):]
    return "unknown"


def dynamic_symbol(module_names: list[str], symbol_name: str):
    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue

        if hasattr(module, symbol_name):
            return getattr(module, symbol_name)

    raise RuntimeError(
        f"Could not import {symbol_name}. "
        f"Adjust module list."
    )


CORE_MODULES = [
    "pet.core",
    "src.pet.core",
]

ALGEBRA_MODULES = [
    "pet.algebra",
    "src.pet.algebra",
]


shape_signature_dict: Callable[[int], dict] = dynamic_symbol(
    CORE_MODULES,
    "shape_signature_dict",
)

encode: Callable[[int], object] = dynamic_symbol(
    CORE_MODULES,
    "encode",
)

structural_distance: Callable[[object, object], int] = dynamic_symbol(
    ALGEBRA_MODULES,
    "structural_distance",
)


def parse_candidate_block(text: str) -> list[dict[str, str]]:
    count_raw = extract_key(text, "candidate_count")

    try:
        count = int(count_raw)
    except ValueError:
        return []

    rows: list[dict[str, str]] = []

    for index in range(1, count + 1):
        rows.append(
            {
                "kind": extract_key(text, f"candidate_{index}_kind"),
                "value": extract_key(text, f"candidate_{index}_value"),
                "source": extract_key(text, f"candidate_{index}_source"),
                "confidence": extract_key(text, f"candidate_{index}_confidence"),
                "note": extract_key(text, f"candidate_{index}_note"),
            }
        )

    return rows


def handoff_output(n_text: str) -> str:
    result = run_command(
        [
            sys.executable,
            "tools/core/pet_classic_handoff_route.py",
            n_text,
            "--include-monster-route",
        ]
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"handoff failed for {n_text}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    return result.stdout


def verify_candidate(
    n_text: str,
    candidate_value: str,
) -> tuple[str, str]:
    result = run_command(
        [
            sys.executable,
            "tools/core/pet_classic_candidate_verify.py",
            n_text,
            "--candidate",
            candidate_value,
        ]
    )

    if result.returncode != 0:
        return "verify-failed", "-"

    hit_kind = extract_key(
        result.stdout,
        "candidate_1_hit_kind",
    )

    if hit_kind == "unknown":
        hit_kind = extract_key(
            result.stdout,
            "candidate_1_status",
        )

    gcd_value = extract_key(
        result.stdout,
        "candidate_1_factor",
    )

    if gcd_value == "unknown":
        gcd_value = extract_key(
            result.stdout,
            "candidate_1_gcd",
        )

    return hit_kind, gcd_value


def tsv_rows(
    n_text: str,
    handoff_text: str,
) -> list[dict[str, str]]:
    n = int(n_text)

    monster_class = extract_key(
        handoff_text,
        "monster_class",
    )

    if monster_class == "unknown":
        monster_class = extract_key(
            handoff_text,
            "triage_router_monster_class",
        )

    n_sig_data = shape_signature_dict(n)

    n_signature = str(n_sig_data["signature"])
    n_generator = str(n_sig_data["generator"])

    rows: list[dict[str, str]] = []

    for candidate in parse_candidate_block(handoff_text):
        value_raw = candidate["value"]

        try:
            candidate_value = int(value_raw)
        except ValueError:
            continue

        candidate_sig_data = shape_signature_dict(candidate_value)

        candidate_signature = str(
            candidate_sig_data["signature"]
        )

        candidate_generator = str(
            candidate_sig_data["generator"]
        )

        distance_to_n = structural_distance(
            encode(candidate_value),
            encode(n),
        )

        hit_kind, gcd_value = verify_candidate(
            n_text,
            str(candidate_value),
        )

        rows.append(
            {
                "N": n_text,
                "monster_class": monster_class,
                "n_signature": n_signature,
                "n_generator": n_generator,
                "candidate_kind": candidate["kind"],
                "candidate_source": candidate["source"],
                "candidate_confidence": candidate["confidence"],
                "candidate_value": str(candidate_value),
                "candidate_signature": candidate_signature,
                "candidate_generator": candidate_generator,
                "distance_to_n": str(distance_to_n),
                "hit_kind": hit_kind,
                "gcd_value": gcd_value,
            }
        )

    return rows


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Observed PET candidate transition study "
            "(no synthetic operators)."
        )
    )

    parser.add_argument(
        "numbers",
        nargs="+",
    )

    args = parser.parse_args()

    columns = (
        "N",
        "monster_class",
        "n_signature",
        "n_generator",
        "candidate_kind",
        "candidate_source",
        "candidate_confidence",
        "candidate_value",
        "candidate_signature",
        "candidate_generator",
        "distance_to_n",
        "hit_kind",
        "gcd_value",
    )

    print("\t".join(columns))

    for n_text in args.numbers:
        handoff_text = handoff_output(n_text)

        for row in tsv_rows(
            n_text,
            handoff_text,
        ):
            print(
                "\t".join(
                    row[column]
                    for column in columns
                )
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
