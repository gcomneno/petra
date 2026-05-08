#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


KEY_VALUE_RE = re.compile(r"^([A-Za-z0-9_]+)\s*=\s*(.*)$")


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


SUPPORTED_RESIDUAL_SHAPES = {
    "[[], []]",
}


def normalized_signature(raw: str) -> str:
    try:
        return str(ast.literal_eval(raw))
    except (SyntaxError, ValueError):
        return raw


def signature_complexity(raw: str) -> tuple[int, int]:
    signature = normalized_signature(raw)

    return (
        signature.count("["),
        len(signature),
    )


def residual_shape_rank(raw_signature: str) -> tuple[int, int, int]:
    signature = normalized_signature(raw_signature)
    supported_rank = 0 if signature in SUPPORTED_RESIDUAL_SHAPES else 1
    bracket_count, text_length = signature_complexity(signature)

    return (
        supported_rank,
        bracket_count,
        text_length,
    )




def verified_factorization_terms(raw: str) -> list[int]:
    if raw in {"", "-", "none", "unknown"}:
        return []

    terms: list[int] = []

    for part in raw.split("*"):
        part = part.strip()

        if not part:
            return []

        try:
            value = int(part)
        except ValueError:
            return []

        if value < 2:
            return []

        terms.append(value)

    return terms


def verified_factorization_product(terms: list[int]) -> int:
    product = 1

    for term in terms:
        product *= term

    return product

def verified_anchor_factors(
    *,
    n: int,
    values: dict[str, list[str]],
) -> list[int]:
    factors: set[int] = set()

    for key, records in values.items():
        if not (
            re.fullmatch(r"candidate_verified_factor_\d+", key)
            or re.fullmatch(r"promoted_factor_\d+", key)
        ):
            continue

        for raw in records:
            try:
                factor = int(raw)
            except ValueError:
                continue

            if 1 < factor < n and n % factor == 0:
                factors.add(factor)

    return sorted(factors)


def run_handoff(
    n: int,
    *,
    include_monster_route: bool,
    auto_same_shape_scan: bool,
    same_shape_prime_limit: int,
    auto_flat_k_scan: bool,
    flat_k_prime_limit: int,
    flat_k_max_supports: int,
    flat_k_max_factor_lines: int,
    auto_shape_family_scan: bool,
    shape_family_support_limit: int,
    shape_family_max_supports: int,
    shape_family_max_factor_lines: int,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        "tools/core/pet_classic_handoff_route.py",
        str(n),
    ]

    if include_monster_route:
        command.append("--include-monster-route")

    if auto_same_shape_scan:
        command.append("--auto-same-shape-scan")

    if auto_flat_k_scan:
        command.append("--auto-flat-k-scan")

    if auto_shape_family_scan:
        command.append("--auto-shape-family-scan")

    command.extend(
        [
            "--same-shape-prime-limit",
            str(same_shape_prime_limit),
            "--flat-k-prime-limit",
            str(flat_k_prime_limit),
            "--flat-k-max-supports",
            str(flat_k_max_supports),
            "--flat-k-max-factor-lines",
            str(flat_k_max_factor_lines),
            "--shape-family-support-limit",
            str(shape_family_support_limit),
            "--shape-family-max-supports",
            str(shape_family_max_supports),
            "--shape-family-max-factor-lines",
            str(shape_family_max_factor_lines),
        ]
    )

    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )


def select_pet_residual_anchor(
    *,
    n: int,
    anchors: list[int],
    depth: int,
    include_monster_route: bool,
    auto_same_shape_scan: bool,
    same_shape_prime_limit: int,
    auto_flat_k_scan: bool,
    flat_k_prime_limit: int,
    flat_k_max_supports: int,
    flat_k_max_factor_lines: int,
    auto_shape_family_scan: bool,
    shape_family_support_limit: int,
    shape_family_max_supports: int,
    shape_family_max_factor_lines: int,
) -> int:
    ranked: list[tuple[tuple[int, int, int, int], int]] = []

    for index, anchor in enumerate(anchors, start=1):
        residual = n // anchor

        result = run_handoff(
            residual,
            include_monster_route=include_monster_route,
            auto_same_shape_scan=auto_same_shape_scan,
            same_shape_prime_limit=same_shape_prime_limit,
            auto_flat_k_scan=auto_flat_k_scan,
            flat_k_prime_limit=flat_k_prime_limit,
            flat_k_max_supports=flat_k_max_supports,
            flat_k_max_factor_lines=flat_k_max_factor_lines,
            auto_shape_family_scan=auto_shape_family_scan,
            shape_family_support_limit=shape_family_support_limit,
            shape_family_max_supports=shape_family_max_supports,
            shape_family_max_factor_lines=shape_family_max_factor_lines,
        )

        if result.returncode != 0:
            residual_signature = "handoff-error"
            residual_policy = "handoff-error"
            residual_execution = "handoff-error"
            residual_final = "handoff-error"
            score = (9, 9, 9999, -anchor)
        else:
            values = parse_key_values(result.stdout)
            residual_signature = normalized_signature(
                latest(values, "target_signature")
            )
            residual_policy = latest(values, "summary_route_escalation_policy")
            residual_execution = latest(values, "summary_route_execution_status")
            residual_final = latest(values, "summary_route_final_status")
            shape_score = residual_shape_rank(residual_signature)

            score = (
                shape_score[0],
                shape_score[1],
                shape_score[2],
                -anchor,
            )

        print(f"depth_{depth}_anchor_candidate_{index} = {anchor}")
        print(f"depth_{depth}_anchor_candidate_{index}_residual = {residual}")
        print(
            f"depth_{depth}_anchor_candidate_{index}_residual_signature = "
            f"{residual_signature}"
        )
        print(
            f"depth_{depth}_anchor_candidate_{index}_residual_policy = "
            f"{residual_policy}"
        )
        print(
            f"depth_{depth}_anchor_candidate_{index}_residual_execution = "
            f"{residual_execution}"
        )
        print(
            f"depth_{depth}_anchor_candidate_{index}_residual_final_status = "
            f"{residual_final}"
        )
        print(
            f"depth_{depth}_anchor_candidate_{index}_selection_score = "
            f"{score[0]},{score[1]},{score[2]},{score[3]}"
        )

        ranked.append((score, anchor))

    ranked.sort()
    selected_anchor = ranked[0][1]

    print(f"depth_{depth}_selected_anchor_factor = {selected_anchor}")
    print(
        "depth_"
        f"{depth}_selected_anchor_reason = best-pet-residual-shape-descent"
    )

    return selected_anchor


def print_handoff_output(depth: int, output: str) -> None:
    print(f"depth_{depth}_handoff_output_start")

    for line in output.strip().splitlines():
        print(line)

    print(f"depth_{depth}_handoff_output_end")


def residual_descent(
    *,
    n: int,
    max_depth: int,
    include_monster_route: bool,
    auto_same_shape_scan: bool,
    same_shape_prime_limit: int,
    auto_flat_k_scan: bool,
    flat_k_prime_limit: int,
    flat_k_max_supports: int,
    flat_k_max_factor_lines: int,
    auto_shape_family_scan: bool,
    shape_family_support_limit: int,
    shape_family_max_supports: int,
    shape_family_max_factor_lines: int,
    show_handoff_output: bool,
) -> int:
    current = n
    chain: list[int] = []
    final_status = "unknown"

    print("PET RESIDUAL DESCENT ROUTE")
    print()
    print(f"N = {n}")
    print(f"max_depth = {max_depth}")
    print(f"include_monster_route = {'yes' if include_monster_route else 'no'}")
    print(f"auto_same_shape_scan = {'yes' if auto_same_shape_scan else 'no'}")
    print(f"same_shape_prime_limit = {same_shape_prime_limit}")
    print(f"auto_flat_k_scan = {'yes' if auto_flat_k_scan else 'no'}")
    print(f"flat_k_prime_limit = {flat_k_prime_limit}")
    print(f"flat_k_max_supports = {flat_k_max_supports}")
    print(f"flat_k_max_factor_lines = {flat_k_max_factor_lines}")
    print(f"auto_shape_family_scan = {'yes' if auto_shape_family_scan else 'no'}")
    print(f"shape_family_support_limit = {shape_family_support_limit}")
    print(f"shape_family_max_supports = {shape_family_max_supports}")
    print(f"shape_family_max_factor_lines = {shape_family_max_factor_lines}")
    print()

    for depth in range(max_depth + 1):
        print(f"Residual depth {depth}")
        print(f"depth_{depth}_input = {current}")

        result = run_handoff(
            current,
            include_monster_route=include_monster_route,
            auto_same_shape_scan=auto_same_shape_scan,
            same_shape_prime_limit=same_shape_prime_limit,
            auto_flat_k_scan=auto_flat_k_scan,
            flat_k_prime_limit=flat_k_prime_limit,
            flat_k_max_supports=flat_k_max_supports,
            flat_k_max_factor_lines=flat_k_max_factor_lines,
            auto_shape_family_scan=auto_shape_family_scan,
            shape_family_support_limit=shape_family_support_limit,
            shape_family_max_supports=shape_family_max_supports,
            shape_family_max_factor_lines=shape_family_max_factor_lines,
        )

        if result.returncode != 0:
            print(f"depth_{depth}_status = handoff-error")
            print(f"depth_{depth}_returncode = {result.returncode}")
            print(f"depth_{depth}_stderr = {(result.stderr or '').strip() or '-'}")
            final_status = "blocked-handoff-error"
            break

        if show_handoff_output:
            print_handoff_output(depth, result.stdout)

        values = parse_key_values(result.stdout)

        route_policy = latest(values, "summary_route_escalation_policy")
        execution_status = latest(values, "summary_route_execution_status")
        route_final_status = latest(values, "summary_route_final_status")

        print(f"depth_{depth}_route_escalation_policy = {route_policy}")
        print(f"depth_{depth}_route_execution_status = {execution_status}")
        print(f"depth_{depth}_route_final_status = {route_final_status}")

        if route_final_status.startswith("solved-by-"):
            verified_factorization = latest(values, "verified_factorization")
            verified_terms = verified_factorization_terms(verified_factorization)

            print(f"depth_{depth}_status = solved")
            print(f"depth_{depth}_verified_factorization = {verified_factorization}")

            if (
                verified_terms
                and verified_factorization_product(verified_terms) == current
            ):
                chain.extend(verified_terms)
                current = 1
                print(f"depth_{depth}_anchor_factor = -")
                print(f"depth_{depth}_residual = 1")
            else:
                print(f"depth_{depth}_anchor_factor = -")
                print(f"depth_{depth}_residual = -")

            final_status = "complete"
            break

        anchors = verified_anchor_factors(n=current, values=values)

        if not anchors:
            if route_final_status == "stopped-at-atomic-leaf":
                depth_status = "stopped-at-leaf"
                final_status = "stopped-at-leaf"
            elif route_final_status == "classic-route-suggested-only":
                depth_status = "stopped-no-verified-anchor"
                final_status = "stopped-at-classic-suggestion"
            else:
                depth_status = "stopped-no-verified-anchor"
                final_status = "blocked-no-verified-anchor"

            print(f"depth_{depth}_status = {depth_status}")
            print(f"depth_{depth}_anchor_factor = -")
            print(f"depth_{depth}_residual = -")

            break

        anchor = select_pet_residual_anchor(
            n=current,
            anchors=anchors,
            depth=depth,
            include_monster_route=include_monster_route,
            auto_same_shape_scan=auto_same_shape_scan,
            same_shape_prime_limit=same_shape_prime_limit,
            auto_flat_k_scan=auto_flat_k_scan,
            flat_k_prime_limit=flat_k_prime_limit,
            flat_k_max_supports=flat_k_max_supports,
            flat_k_max_factor_lines=flat_k_max_factor_lines,
            auto_shape_family_scan=auto_shape_family_scan,
            shape_family_support_limit=shape_family_support_limit,
            shape_family_max_supports=shape_family_max_supports,
            shape_family_max_factor_lines=shape_family_max_factor_lines,
        )
        residual = current // anchor

        print(f"depth_{depth}_status = reduced")
        print(f"depth_{depth}_anchor_factor = {anchor}")
        print(f"depth_{depth}_anchor_selection_policy = best-pet-residual-shape-descent")
        print(f"depth_{depth}_residual = {residual}")

        chain.append(anchor)

        if residual == 1:
            final_status = "complete"
            break

        if residual == current:
            final_status = "blocked-non-decreasing-residual"
            break

        current = residual
        print()
    else:
        final_status = "blocked-max-depth"

    terminal_residual = current

    if final_status != "complete" and terminal_residual > 1:
        chain_with_terminal = [*chain, terminal_residual]
    else:
        chain_with_terminal = chain

    print()
    print("PET residual descent summary")
    print(f"residual_descent_status = {final_status}")
    print(
        "residual_reduction_chain = "
        f"{' * '.join(str(value) for value in chain_with_terminal) if chain_with_terminal else '-'}"
    )
    print(f"terminal_residual = {terminal_residual}")
    print(
        "claim = PET residual descent only; each anchor comes from verified route output, terminal residual is not automatically prime"
    )

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run recursive PET residual descent using the handoff route."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--same-shape-prime-limit", type=int, default=200)
    parser.add_argument("--auto-flat-k-scan", action="store_true")
    parser.add_argument("--flat-k-prime-limit", type=int, default=50)
    parser.add_argument("--flat-k-max-supports", type=int, default=5000)
    parser.add_argument("--flat-k-max-factor-lines", type=int, default=25)
    parser.add_argument("--auto-shape-family-scan", action="store_true")
    parser.add_argument("--shape-family-support-limit", type=int, default=10000)
    parser.add_argument("--shape-family-max-supports", type=int, default=5000)
    parser.add_argument("--shape-family-max-factor-lines", type=int, default=25)
    parser.add_argument("--show-handoff-output", action="store_true")
    parser.add_argument("--no-include-monster-route", action="store_true")
    parser.add_argument("--no-auto-same-shape-scan", action="store_true")
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("pet_residual_descent_route expects integers >= 1")

    if args.max_depth < 0:
        raise SystemExit("--max-depth must be >= 0")

    if args.same_shape_prime_limit < 2:
        raise SystemExit("--same-shape-prime-limit must be >= 2")

    if args.flat_k_prime_limit < 2:
        raise SystemExit("--flat-k-prime-limit must be >= 2")

    if args.flat_k_max_supports < 1:
        raise SystemExit("--flat-k-max-supports must be >= 1")

    if args.flat_k_max_factor_lines < 0:
        raise SystemExit("--flat-k-max-factor-lines must be >= 0")

    if args.shape_family_support_limit < 2:
        raise SystemExit("--shape-family-support-limit must be >= 2")

    if args.shape_family_max_supports < 1:
        raise SystemExit("--shape-family-max-supports must be >= 1")

    if args.shape_family_max_factor_lines < 0:
        raise SystemExit("--shape-family-max-factor-lines must be >= 0")

    return residual_descent(
        n=args.n,
        max_depth=args.max_depth,
        include_monster_route=not args.no_include_monster_route,
        auto_same_shape_scan=not args.no_auto_same_shape_scan,
        same_shape_prime_limit=args.same_shape_prime_limit,
        auto_flat_k_scan=args.auto_flat_k_scan,
        flat_k_prime_limit=args.flat_k_prime_limit,
        flat_k_max_supports=args.flat_k_max_supports,
        flat_k_max_factor_lines=args.flat_k_max_factor_lines,
        auto_shape_family_scan=args.auto_shape_family_scan,
        shape_family_support_limit=args.shape_family_support_limit,
        shape_family_max_supports=args.shape_family_max_supports,
        shape_family_max_factor_lines=args.shape_family_max_factor_lines,
        show_handoff_output=args.show_handoff_output,
    )


if __name__ == "__main__":
    raise SystemExit(main())
