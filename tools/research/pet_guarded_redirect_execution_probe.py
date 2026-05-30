#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
PROBE_TOOL = ROOT_DIR / "tools" / "research" / "pet_completion_aware_residual_probe.py"
ROUTE_TOOL = ROOT_DIR / "tools" / "core" / "pet_residual_descent_route.py"

KEY_VALUE_RE = re.compile(r"^([A-Za-z0-9_]+)\s*=\s*(.*)$")

INACTIVE_SIGNALS = {
    "inactive-flat-k-required",
    "inactive-shape-family-required",
}


def positive_int(raw: str) -> int:
    value = int(raw)

    if value < 1:
        raise argparse.ArgumentTypeError("value must be >= 1")

    return value


def parse_key_values(text: str) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}

    for line in text.splitlines():
        match = KEY_VALUE_RE.match(line.strip())

        if not match:
            continue

        key, value = match.groups()
        values.setdefault(key, []).append(value.strip())

    return values


def latest(values: dict[str, list[str]], key: str, default: str = "-") -> str:
    found = values.get(key)

    if not found:
        return default

    return found[-1]


def run_probe(n: int, max_depth: int) -> dict[str, Any]:
    result = subprocess.run(
        [
            sys.executable,
            str(PROBE_TOOL),
            str(n),
            "--max-depth",
            str(max_depth),
            "--compare-ranking-policy",
            "--json",
        ],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"probe failed for {n}: {detail}")

    return json.loads(result.stdout)


def run_route(
    n: int,
    max_depth: int,
    *,
    auto_flat_k_scan: bool = False,
    auto_shape_family_scan: bool = False,
) -> dict[str, str]:
    command = [
        sys.executable,
        str(ROUTE_TOOL),
        str(n),
        "--max-depth",
        str(max_depth),
    ]

    if auto_flat_k_scan:
        command.append("--auto-flat-k-scan")

    if auto_shape_family_scan:
        command.append("--auto-shape-family-scan")

    result = subprocess.run(
        command,
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"route failed for {n}: {detail}")

    values = parse_key_values(result.stdout)

    return {
        "status": latest(values, "residual_descent_status"),
        "residual_reduction_chain": latest(values, "residual_reduction_chain"),
        "terminal_residual": latest(values, "terminal_residual"),
    }


def is_positive_int_text(raw: str) -> bool:
    return raw.isdigit() and int(raw) > 0


def candidate_by_anchor(
    probe: dict[str, Any],
    anchor: str,
) -> dict[str, Any] | None:
    for row in probe["candidates"]:
        if row["anchor"] == anchor:
            return row

    return None


def evaluate_guard(probe: dict[str, Any]) -> dict[str, str]:
    ranking = probe["ranking_policy_comparison"]

    current_anchor = ranking["current_selected_anchor"]
    shadow_anchor = ranking["suggested_anchor"]

    current_row = candidate_by_anchor(probe, current_anchor)
    shadow_row = candidate_by_anchor(probe, shadow_anchor)

    current_signal = "-"
    shadow_signal = "-"

    if current_row is not None:
        current_signal = current_row.get("active_completion_signal", "-")

    if shadow_row is not None:
        shadow_signal = shadow_row.get("active_completion_signal", "-")

    guard = {
        "structural_prefix": "-",
        "current_signal": current_signal,
        "shadow_signal": shadow_signal,
        "guard_decision": "keep-current",
        "guard_reason": "not-evaluated",
    }

    if probe["status"] != "blocked-no-verified-anchor":
        guard["guard_reason"] = "not-blocked-status"
        return guard

    if not ranking["changed_selection"]:
        guard["guard_reason"] = "shadow-ranking-does-not-change-selection"
        return guard

    if not (
        is_positive_int_text(current_anchor)
        and is_positive_int_text(shadow_anchor)
    ):
        guard["guard_reason"] = "non-positive-integer-anchor"
        return guard

    current_anchor_int = int(current_anchor)
    shadow_anchor_int = int(shadow_anchor)

    if current_anchor_int % shadow_anchor_int != 0:
        guard["guard_reason"] = "current-anchor-not-divisible-by-shadow-anchor"
        return guard

    structural_prefix = current_anchor_int // shadow_anchor_int
    guard["structural_prefix"] = str(structural_prefix)

    if structural_prefix <= 1:
        guard["guard_reason"] = "no-structural-prefix"
        return guard

    if current_row is None or shadow_row is None:
        guard["guard_reason"] = "candidate-details-missing"
        return guard

    if shadow_signal != "active-partial-expandable":
        guard["guard_reason"] = "shadow-not-active-partial-expandable"
        return guard

    if current_signal not in INACTIVE_SIGNALS:
        guard["guard_reason"] = "current-not-inactive"
        return guard

    guard["guard_decision"] = "would-redirect-to-shadow-anchor"
    guard["guard_reason"] = "structural-prefix-trap-active-shadow"

    return guard


def combine_chain(anchor: str, residual_chain: str) -> str:
    if anchor == "-" or residual_chain == "-":
        return "-"

    return f"{anchor} * {residual_chain}"


FACTOR_CHAIN_CERTIFICATE_CLAIM = (
    "factor-chain product verification only; "
    "not a PET operator-path certificate"
)


def parse_factor_chain(chain: str) -> tuple[int, ...] | None:
    if chain == "-":
        return None

    parts = [part.strip() for part in chain.split("*")]

    if not parts:
        return None

    factors: list[int] = []

    for part in parts:
        if not is_positive_int_text(part):
            return None

        factors.append(int(part))

    return tuple(factors)


def factor_chain_product(factors: tuple[int, ...]) -> int:
    product = 1

    for factor in factors:
        product *= factor

    return product


def factor_chain_certificate(
    *,
    n: int,
    chain: str,
    source: str,
) -> dict[str, Any]:
    factors = parse_factor_chain(chain)

    if factors is None:
        status = "unavailable" if chain == "-" else "invalid-chain"
        return {
            "kind": "factor-chain",
            "source": source,
            "n": n,
            "chain": chain,
            "factors": [],
            "factor_count": 0,
            "product": None,
            "verified_product": False,
            "status": status,
            "claim": FACTOR_CHAIN_CERTIFICATE_CLAIM,
        }

    product = factor_chain_product(factors)
    verified_product = product == n

    return {
        "kind": "factor-chain",
        "source": source,
        "n": n,
        "chain": chain,
        "factors": list(factors),
        "factor_count": len(factors),
        "product": product,
        "verified_product": verified_product,
        "status": (
            "verified-product" if verified_product else "product-mismatch"
        ),
        "claim": FACTOR_CHAIN_CERTIFICATE_CLAIM,
    }


def route_completed(route: dict[str, str]) -> bool:
    return (
        route.get("status") == "complete"
        and route.get("terminal_residual") == "1"
    )


def empty_route() -> dict[str, str]:
    return {
        "status": "-",
        "residual_reduction_chain": "-",
        "terminal_residual": "-",
    }


def classify_execution_delta(
    *,
    guard_decision: str,
    shadow_residual: str,
    redirect_status: str,
    redirect_chain: str,
    redirect_terminal_residual: str,
) -> str:
    if guard_decision != "would-redirect-to-shadow-anchor":
        return "guard-not-triggered"

    if redirect_status == "complete" and redirect_terminal_residual == "1":
        return "redirect-completes"

    if (
        redirect_chain != "-"
        and shadow_residual.isdigit()
        and redirect_terminal_residual != shadow_residual
    ):
        return "redirect-expands-route"

    return "redirect-remains-blocked"


def classify_expanded_execution_delta(
    *,
    guard_decision: str,
    redirect_flat_k: dict[str, str],
    redirect_shape_family: dict[str, str],
) -> str:
    if guard_decision != "would-redirect-to-shadow-anchor":
        return "guard-not-triggered"

    if route_completed(redirect_flat_k):
        return "redirect-completes-with-flat-k"

    if route_completed(redirect_shape_family):
        return "redirect-completes-with-shape-family"

    return "redirect-still-blocked"


def build_row(
    n: int,
    max_depth: int,
    *,
    skip_expanded_execution: bool = False,
) -> dict[str, Any]:
    probe = run_probe(n, max_depth)
    ranking = probe["ranking_policy_comparison"]
    guard = evaluate_guard(probe)

    shadow_anchor = ranking["suggested_anchor"]
    shadow_residual = ranking["suggested_residual"]

    redirect = empty_route()
    redirect_flat_k = empty_route()
    redirect_shape_family = empty_route()

    redirect_chain = "-"
    redirect_flat_k_chain = "-"
    redirect_shape_family_chain = "-"

    if (
        guard["guard_decision"] == "would-redirect-to-shadow-anchor"
        and is_positive_int_text(shadow_residual)
    ):
        shadow_residual_int = int(shadow_residual)

        redirect = run_route(shadow_residual_int, max_depth)

        if not skip_expanded_execution:
            redirect_flat_k = run_route(
                shadow_residual_int,
                max_depth,
                auto_flat_k_scan=True,
            )
            redirect_shape_family = run_route(
                shadow_residual_int,
                max_depth,
                auto_shape_family_scan=True,
            )

        redirect_chain = combine_chain(
            shadow_anchor,
            redirect["residual_reduction_chain"],
        )
        redirect_flat_k_chain = combine_chain(
            shadow_anchor,
            redirect_flat_k["residual_reduction_chain"],
        )
        redirect_shape_family_chain = combine_chain(
            shadow_anchor,
            redirect_shape_family["residual_reduction_chain"],
        )

    execution_delta = classify_execution_delta(
        guard_decision=guard["guard_decision"],
        shadow_residual=shadow_residual,
        redirect_status=redirect["status"],
        redirect_chain=redirect_chain,
        redirect_terminal_residual=redirect["terminal_residual"],
    )
    if skip_expanded_execution:
        expanded_execution_delta = "skipped"
    else:
        expanded_execution_delta = (
            classify_expanded_execution_delta(
                guard_decision=guard["guard_decision"],
                redirect_flat_k=redirect_flat_k,
                redirect_shape_family=redirect_shape_family,
            )
        )

    factor_chain_certificates = {
        "current": factor_chain_certificate(
            n=n,
            chain=probe["residual_reduction_chain"],
            source="current",
        ),
        "redirect": factor_chain_certificate(
            n=n,
            chain=redirect_chain,
            source="guarded-redirect-conservative",
        ),
        "redirect_flat_k": factor_chain_certificate(
            n=n,
            chain=redirect_flat_k_chain,
            source="guarded-redirect-flat-k",
        ),
        "redirect_shape_family": factor_chain_certificate(
            n=n,
            chain=redirect_shape_family_chain,
            source="guarded-redirect-shape-family",
        ),
    }

    return {
        "n": n,
        "current_status": probe["status"],
        "current_anchor": ranking["current_selected_anchor"],
        "current_residual": ranking["current_selected_residual"],
        "current_chain": probe["residual_reduction_chain"],
        "current_terminal_residual": probe["terminal_residual"],
        "guard_decision": guard["guard_decision"],
        "guard_reason": guard["guard_reason"],
        "structural_prefix": guard["structural_prefix"],
        "current_signal": guard["current_signal"],
        "shadow_signal": guard["shadow_signal"],
        "shadow_anchor": shadow_anchor,
        "shadow_residual": shadow_residual,
        "redirect_status": redirect["status"],
        "redirect_residual_chain": redirect["residual_reduction_chain"],
        "redirect_chain": redirect_chain,
        "redirect_terminal_residual": redirect["terminal_residual"],
        "redirect_flat_k_status": redirect_flat_k["status"],
        "redirect_flat_k_residual_chain": redirect_flat_k[
            "residual_reduction_chain"
        ],
        "redirect_flat_k_chain": redirect_flat_k_chain,
        "redirect_flat_k_terminal_residual": redirect_flat_k[
            "terminal_residual"
        ],
        "redirect_shape_family_status": redirect_shape_family["status"],
        "redirect_shape_family_residual_chain": redirect_shape_family[
            "residual_reduction_chain"
        ],
        "redirect_shape_family_chain": redirect_shape_family_chain,
        "redirect_shape_family_terminal_residual": redirect_shape_family[
            "terminal_residual"
        ],
        "execution_delta": execution_delta,
        "expanded_execution_delta": expanded_execution_delta,
        "factor_chain_certificates": factor_chain_certificates,
    }


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
        print(
            f"redirect_shape_family_status = "
            f"{row['redirect_shape_family_status']}"
        )
        print(
            f"redirect_shape_family_chain = "
            f"{row['redirect_shape_family_chain']}"
        )
        print(
            f"redirect_shape_family_terminal_residual = "
            f"{row['redirect_shape_family_terminal_residual']}"
        )
        print(f"expanded_execution_delta = {row['expanded_execution_delta']}")
        print()
        print("factor_chain_certificates:")
        certificates = row["factor_chain_certificates"]
        for name in [
            "current",
            "redirect",
            "redirect_flat_k",
            "redirect_shape_family",
        ]:
            certificate = certificates[name]
            print(
                f"{name}_factor_chain_status = "
                f"{certificate['status']}"
            )
            print(
                f"{name}_factor_chain_verified_product = "
                f"{str(certificate['verified_product']).lower()}"
            )


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
        help=(
            "skip expanded redirect execution scans "
            "(flat-k and shape-family)"
        ),
    )

    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.max_depth < 0:
        raise SystemExit("--max-depth must be >= 0")

    rows = [
        build_row(
            n,
            args.max_depth,
            skip_expanded_execution=(
                args.skip_expanded_execution
            ),
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
