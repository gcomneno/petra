#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from typing import Any

from pet.guarded_redirect import build_row


def positive_int(raw: str) -> int:
    value = int(raw)

    if value < 1:
        raise argparse.ArgumentTypeError("value must be >= 1")

    return value


def print_text(rows: list[dict[str, Any]]) -> None:
    for index, row in enumerate(rows):
        if index:
            print()

        print("PET GUARDED REDIRECT EXECUTION PROBE")
        print()
        print(f"N = {row['n']}")
        print()
        print("current:")
        print(f"current_status = {row['current_status']}")
        print(f"current_anchor = {row['current_anchor']}")
        print(f"current_residual = {row['current_residual']}")
        print(f"current_chain = {row['current_chain']}")
        print(f"current_terminal_residual = {row['current_terminal_residual']}")
        print()
        print("guard:")
        print(f"guard_decision = {row['guard_decision']}")
        print(f"guard_reason = {row['guard_reason']}")
        print(f"structural_prefix = {row['structural_prefix']}")
        print(f"current_signal = {row['current_signal']}")
        print(f"shadow_signal = {row['shadow_signal']}")
        print(f"shadow_anchor = {row['shadow_anchor']}")
        print(f"shadow_residual = {row['shadow_residual']}")
        print()
        print("redirect:")
        print(f"redirect_status = {row['redirect_status']}")
        print(f"redirect_residual_chain = {row['redirect_residual_chain']}")
        print(f"redirect_chain = {row['redirect_chain']}")
        print(f"redirect_terminal_residual = {row['redirect_terminal_residual']}")
        print(f"execution_delta = {row['execution_delta']}")
        print()
        print("redirect_expanded:")
        print(f"redirect_flat_k_status = {row['redirect_flat_k_status']}")
        print(f"redirect_flat_k_chain = {row['redirect_flat_k_chain']}")
        print(
            f"redirect_flat_k_terminal_residual = "
            f"{row['redirect_flat_k_terminal_residual']}"
        )
        print(f"redirect_shape_family_status = {row['redirect_shape_family_status']}")
        print(f"redirect_shape_family_chain = {row['redirect_shape_family_chain']}")
        print(
            f"redirect_shape_family_terminal_residual = "
            f"{row['redirect_shape_family_terminal_residual']}"
        )
        print(f"expanded_execution_delta = {row['expanded_execution_delta']}")
        print()
        certificate_names = [
            "current",
            "current_flat_k",
            "current_shape_family",
            "redirect",
            "redirect_flat_k",
            "redirect_shape_family",
        ]

        print("factor_chain_certificates:")
        certificates = row["factor_chain_certificates"]
        for name in certificate_names:
            certificate = certificates[name]
            print(f"{name}_factor_chain_status = {certificate['status']}")
            print(
                f"{name}_factor_chain_verified_product = "
                f"{str(certificate['verified_product']).lower()}"
            )

        print()
        print("operator_path_certificates:")
        operator_certificates = row["operator_path_certificates"]
        for name in certificate_names:
            certificate = operator_certificates[name]
            print(f"{name}_operator_path_status = {certificate['status']}")
            print(f"{name}_operator_path_reason = {certificate['reason']}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Research-only execution probe for guarded structural prefix "
            "trap redirects."
        ),
    )
    parser.add_argument("n", type=positive_int, nargs="+")
    parser.add_argument("--max-depth", type=int, default=4)

    parser.add_argument(
        "--skip-expanded-execution",
        action="store_true",
        help=("skip expanded redirect execution scans (flat-k and shape-family)"),
    )

    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.max_depth < 0:
        raise SystemExit("--max-depth must be >= 0")

    rows = [
        build_row(
            n,
            args.max_depth,
            skip_expanded_execution=(args.skip_expanded_execution),
        )
        for n in args.n
    ]

    if args.json:
        print(
            json.dumps(
                {
                    "schema": "pet.guarded_redirect_execution_probe.v0",
                    "profile": {
                        "max_depth": args.max_depth,
                    },
                    "rows": rows,
                    "claim": (
                        "Research-only guarded redirect execution probe; "
                        "does not change PET routing or real anchor selection."
                    ),
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print_text(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
