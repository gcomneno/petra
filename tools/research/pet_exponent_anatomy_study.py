#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib
import subprocess
import sys
from pathlib import Path
from typing import Callable


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=repo_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def dynamic_symbol(module_names: list[str], symbol_name: str):
    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue

        if hasattr(module, symbol_name):
            return getattr(module, symbol_name)

    raise RuntimeError(f"Could not import {symbol_name}")


shape_signature_dict: Callable[[int], dict] = dynamic_symbol(
    ["pet.core", "src.pet.core"],
    "shape_signature_dict",
)


def factor_exponents(value: int) -> list[int]:
    exponents: list[int] = []

    divisor = 2
    remaining = value

    while divisor * divisor <= remaining:
        exponent = 0

        while remaining % divisor == 0:
            remaining //= divisor
            exponent += 1

        if exponent:
            exponents.append(exponent)

        divisor += 1 if divisor == 2 else 2

    if remaining > 1:
        exponents.append(1)

    return exponents


def signature_of_exponent(exponent: int) -> str:
    if exponent <= 1:
        return "[]"

    return str(shape_signature_dict(exponent)["signature"])


def extract_key(text: str, key: str) -> str:
    prefix = f"{key} = "

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith(prefix):
            return stripped[len(prefix):]

    return "unknown"


def read_transition_rows(n_text: str) -> list[dict[str, str]]:
    result = run(
        [
            sys.executable,
            "tools/research/pet_operator_bridge_study.py",
            n_text,
        ]
    )

    if result.returncode != 0:
        return []

    return list(
        csv.DictReader(
            result.stdout.splitlines(),
            delimiter="\t",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Study whether exponent anatomy correlates with PET candidate hits."
    )
    parser.add_argument("numbers", nargs="+")
    args = parser.parse_args()

    print(
        "\t".join(
            [
                "N",
                "candidate_value",
                "candidate_source",
                "candidate_kind",
                "candidate_is_base",
                "candidate_exponents",
                "candidate_exponent_signatures",
                "max_exponent",
                "composite_exponent_count",
                "nontrivial_exponent_signature_count",
                "gcd_class",
                "hit_rank",
            ]
        )
    )

    for n_text in args.numbers:
        for row in read_transition_rows(n_text):
            value = int(row["candidate_value"])
            exponents = factor_exponents(value)
            exponent_signatures = [
                signature_of_exponent(exponent)
                for exponent in exponents
            ]

            composite_count = sum(
                1
                for exponent in exponents
                if exponent > 1
            )

            nontrivial_signature_count = sum(
                1
                for signature in exponent_signatures
                if signature != "[]"
            )

            print(
                "\t".join(
                    [
                        n_text,
                        row["candidate_value"],
                        row["candidate_source"],
                        row["candidate_kind"],
                        row["candidate_is_base"],
                        str(exponents),
                        str(exponent_signatures),
                        str(max(exponents) if exponents else 0),
                        str(composite_count),
                        str(nontrivial_signature_count),
                        row["gcd_class"],
                        row["hit_rank"],
                    ]
                )
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
