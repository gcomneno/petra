#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from io import StringIO
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tools.research.pet_operator_bridge_study import (
    prefix_match_count,
    shape_signature_dict,
    signature_depth_sum,
    suffix_match_count,
)


def apply_new(signature: list[object]) -> list[object]:
    return [*signature, []]


def apply_inc(signature: list[object]) -> list[object]:
    if not signature:
        return [[[]]]

    updated = list(signature)
    updated[-1] = [updated[-1]]
    return updated


def apply_branch_at(
    signature: list[object],
    index: int,
) -> list[object]:
    updated = list(signature)

    if not 0 <= index < len(updated):
        return updated

    if updated[index] != []:
        return updated

    updated[index] = [[], []]
    return updated


def simulate_transition_path(
    candidate_signature: list[object],
    *,
    target_signature: list[object],
) -> tuple[list[str], bool]:
    current = list(candidate_signature)

    steps = [str(current)]

    max_iterations = 16

    for _ in range(max_iterations):
        if current == target_signature:
            return steps, True

        current_width = len(current)
        target_width = len(target_signature)

        current_depth = signature_depth_sum(current)
        target_depth = signature_depth_sum(target_signature)

        if current_width < target_width:
            current = apply_new(current)
            steps.append(f"NEW -> {current}")
            continue

        branched = False

        for index, (current_item, target_item) in enumerate(
            zip(current, target_signature)
        ):
            if current_item == [] and target_item == [[], []]:
                current = apply_branch_at(current, index)
                steps.append(f"BRANCH_AT({index}) -> {current}")
                branched = True
                break

        if branched:
            continue

        if current_depth < target_depth:
            current = apply_inc(current)
            steps.append(f"INC -> {current}")
            continue

        break

    return steps, current == target_signature



def run_command(args: list[str]) -> str:
    result = subprocess.run(
        args,
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


def branch_for_transition_side(transition_side: str) -> str:
    if "DROP" in transition_side:
        return "DROP"
    if "NEW" in transition_side:
        return "NEW"
    return "unknown"


def command_text(parts: list[str]) -> str:
    return " ".join(parts)


def classic_probe_policy(shape_diagnostic: str) -> str:
    return {
        "atomic-exact": "primality-check-only",
        "narrow-deep": "power-like-local-check",
        "wide-exact": "backbone-wide-structural-check",
        "near-shape": "operator-neighborhood-check",
        "complex-border": "complex-border-route-needed",
    }.get(shape_diagnostic, "route-needed")



def append_candidate(
    candidates: list[dict[str, str]],
    *,
    kind: str,
    value: str,
    source: str,
    confidence: str,
    note: str,
) -> None:
    if value in {"", "-", "unknown", "skipped-by-router", "none"}:
        return
    if any(existing["value"] == value for existing in candidates):
        return
    candidates.append(
        {
            "kind": kind,
            "value": value,
            "source": source,
            "confidence": confidence,
            "note": note,
        }
    )


def candidate_rows(
    *,
    monster_route: dict[str, str],
    selected_backbone_generator: str,
    selected_backbone_order: str,
) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []

    monster_class = monster_route.get("monster_class", "unknown")
    sigma_value = monster_route.get("sigma_depth_generator", "-")
    chunk_value = monster_route.get("chunk_best_merge_generator", "-")

    if monster_class == "local-preserved-shadow-coherent":
        append_candidate(
            candidates,
            kind="local-preserved-generator",
            value=chunk_value,
            source="lambda_chunk",
            confidence="high",
            note="local chunk merge agrees with sigma",
        )
        append_candidate(
            candidates,
            kind="selected-backbone-generator",
            value=selected_backbone_generator,
            source="local_probe",
            confidence="medium",
            note=f"selected backbone order {selected_backbone_order}",
        )
        append_candidate(
            candidates,
            kind="sigma-depth-generator",
            value=sigma_value,
            source="sigma_backbone",
            confidence="medium",
            note="global sigma support",
        )
        return candidates

    if monster_class == "local-preserved-sigma-floor-risk":
        append_candidate(
            candidates,
            kind="local-preserved-generator",
            value=chunk_value,
            source="lambda_chunk",
            confidence="high",
            note="local generator preserved while sigma may be collapsed",
        )
        append_candidate(
            candidates,
            kind="selected-backbone-generator",
            value=selected_backbone_generator,
            source="local_probe",
            confidence="medium",
            note=f"selected backbone order {selected_backbone_order}",
        )
        append_candidate(
            candidates,
            kind="sigma-depth-generator",
            value=sigma_value,
            source="sigma_backbone",
            confidence="low",
            note="sigma floor risk",
        )
        return candidates

    if monster_class == "deceptive-stable-sigma":
        append_candidate(
            candidates,
            kind="selected-backbone-generator",
            value=selected_backbone_generator,
            source="local_probe",
            confidence="medium",
            note=f"selected backbone order {selected_backbone_order}",
        )
        append_candidate(
            candidates,
            kind="chunk-merge-generator",
            value=chunk_value,
            source="lambda_chunk",
            confidence="low",
            note="available but globally emergent case",
        )
        append_candidate(
            candidates,
            kind="sigma-depth-generator",
            value=sigma_value,
            source="sigma_backbone",
            confidence="low",
            note="do not trust directly",
        )
        return candidates

    if monster_class == "fragile-shadow-field":
        append_candidate(
            candidates,
            kind="selected-backbone-generator",
            value=selected_backbone_generator,
            source="local_probe",
            confidence="low",
            note=f"fragile field, backbone order {selected_backbone_order}",
        )
        append_candidate(
            candidates,
            kind="chunk-merge-generator",
            value=chunk_value,
            source="lambda_chunk",
            confidence="low",
            note="fragile field",
        )
        append_candidate(
            candidates,
            kind="sigma-depth-generator",
            value=sigma_value,
            source="sigma_backbone",
            confidence="low",
            note="depth fragile support",
        )
        return candidates

    if monster_class in {
        "diffuse-field",
        "diffuse-digit-mixed-field",
        "saturated-border-field",
        "sparse-zero-border-field",
        "obvious-periodic-field",
        "sigma-coherent-large-field",
    }:
        append_candidate(
            candidates,
            kind="selected-backbone-generator",
            value=selected_backbone_generator,
            source="local_probe",
            confidence="low",
            note="router-classified field; no strong PET candidate",
        )
        return candidates

    append_candidate(
        candidates,
        kind="selected-backbone-generator",
        value=selected_backbone_generator,
        source="local_probe",
        confidence="medium",
        note=f"default candidate from backbone order {selected_backbone_order}",
    )
    append_candidate(
        candidates,
        kind="sigma-depth-generator",
        value=sigma_value,
        source="sigma_backbone",
        confidence="low",
        note="default sigma candidate",
    )
    append_candidate(
        candidates,
        kind="chunk-merge-generator",
        value=chunk_value,
        source="lambda_chunk",
        confidence="low",
        note="default chunk candidate",
    )
    return candidates


def divisors_desc(value: int) -> list[int]:
    divisors: set[int] = set()
    limit = int(value ** 0.5)
    for candidate in range(2, limit + 1):
        if value % candidate == 0:
            divisors.add(candidate)
            divisors.add(value // candidate)
    divisors.add(value)
    return sorted(divisors, reverse=True)


def confidence_rank(confidence: str) -> int:
    return {
        "high": 3,
        "medium": 2,
        "low": 1,
    }.get(confidence, 0)


def append_derived_lcm_merge(
    candidates: list[dict[str, str]],
    *,
    base_count: int,
) -> list[dict[str, str]]:
    derived_values: list[int] = []

    for candidate in candidates[base_count:]:
        try:
            value = int(candidate["value"])
        except ValueError:
            continue

        if value >= 2:
            derived_values.append(value)

    if not derived_values:
        return candidates

    merged_value = math.lcm(*derived_values)
    merged_text = str(merged_value)

    if any(candidate["value"] == merged_text for candidate in candidates):
        return candidates

    return candidates + [
        {
            "kind": "derived-lcm-merge",
            "value": merged_text,
            "source": "candidate_merge",
            "confidence": "high",
            "note": "lcm of derived expansion candidates",
        }
    ]


def candidate_has_verified_factor(
    n: int,
    candidate_value: int,
) -> bool:
    if candidate_value < 2:
        return False

    gcd_value = math.gcd(n, candidate_value)

    return 1 < gcd_value < n


def expand_candidates(
    base_candidates: list[dict[str, str]],
    *,
    target_n: int | None = None,
) -> list[dict[str, str]]:
    expanded: list[dict[str, str]] = []
    seen: set[str] = set()

    def add(kind: str, value: str, source: str, confidence: str, note: str) -> None:
        if value in {"", "-", "unknown", "none", "skipped-by-router"}:
            return
        if value in seen:
            return
        seen.add(value)
        expanded.append(
            {
                "kind": kind,
                "value": value,
                "source": source,
                "confidence": confidence,
                "note": note,
            }
        )

    for candidate in base_candidates:
        add(
            candidate["kind"],
            candidate["value"],
            candidate["source"],
            candidate["confidence"],
            candidate["note"],
        )

    numeric_values: list[int] = []
    for candidate in base_candidates:
        try:
            numeric_values.append(int(candidate["value"]))
        except ValueError:
            continue

    numeric_values = [value for value in numeric_values if value >= 2]
    numeric_values = sorted(set(numeric_values), reverse=True)

    if target_n is not None:
        saturated_values: list[int] = []

        for value in numeric_values:
            if candidate_has_verified_factor(
                target_n,
                value,
            ):
                continue

            saturated_values.append(value)

        numeric_values = saturated_values

    derived_divisors_added = 0
    for root in numeric_values[:2]:
        for divisor in divisors_desc(root):
            if divisor == root or divisor < 4:
                continue
            if derived_divisors_added >= 4:
                break
            add(
                "derived-divisor",
                str(divisor),
                "candidate_expansion",
                "medium",
                f"non-trivial divisor of {root}",
            )
            if str(divisor) in seen:
                derived_divisors_added += 1
        if derived_divisors_added >= 4:
            break

    import math

    pair_values = numeric_values[:3]
    for index, left in enumerate(pair_values):
        for right in pair_values[index + 1 :]:
            gcd_value = math.gcd(left, right)
            if gcd_value >= 4:
                add(
                    "derived-gcd",
                    str(gcd_value),
                    "candidate_expansion",
                    "medium",
                    f"gcd({left},{right})",
                )

    expanded.sort(
        key=lambda candidate: (
            -confidence_rank(candidate["confidence"]),
            -int(candidate["value"]),
            candidate["kind"],
        )
    )

    # Keep base candidates first, then cap derived expansion rows.
    base_values = {candidate["value"] for candidate in base_candidates}
    base_rows = [candidate for candidate in expanded if candidate["value"] in base_values]
    derived_rows = [candidate for candidate in expanded if candidate["value"] not in base_values]

    derived_rows = derived_rows[: max(0, 8 - len(base_rows))]
    return base_rows + derived_rows


def transition_verified_for_candidate(
    *,
    target_n: int,
    candidate_value: int,
) -> bool:
    target_signature = shape_signature_dict(target_n)["signature"]
    candidate_signature = shape_signature_dict(candidate_value)["signature"]

    _, verified = simulate_transition_path(
        candidate_signature,
        target_signature=target_signature,
    )

    return verified


def rank_candidates_by_signature_transition(
    candidates: list[dict[str, str]],
    *,
    target_n: int,
) -> list[dict[str, str]]:
    def key(candidate: dict[str, str]) -> tuple[int, int]:
        try:
            candidate_value = int(candidate["value"])
        except ValueError:
            return (1, 0)

        verified = transition_verified_for_candidate(
            target_n=target_n,
            candidate_value=candidate_value,
        )

        return (
            0 if verified else 1,
            -int(candidate["value"]),
        )

    return sorted(candidates, key=key)



def print_candidates(
    candidates: list[dict[str, str]],
    *,
    base_count: int,
    target_n: int,
) -> None:
    target_sig_data = shape_signature_dict(target_n)
    target_signature_raw = target_sig_data["signature"]
    target_signature = str(target_signature_raw)
    target_width = len(target_signature_raw)
    target_depth_sum = signature_depth_sum(target_signature_raw)

    print("PET candidate forms")
    print(f"candidate_base_count = {base_count}")
    print(f"candidate_count = {len(candidates)}")
    print()

    print("PET signature target")
    print(f"target_n = {target_n}")
    print(f"target_signature = {target_signature}")
    print(f"target_width = {target_width}")
    print(f"target_depth_sum = {target_depth_sum}")
    print()

    for index, candidate in enumerate(candidates, start=1):
        candidate_value = int(candidate["value"])

        candidate_sig_data = shape_signature_dict(candidate_value)
        candidate_signature_raw = candidate_sig_data["signature"]
        candidate_signature = str(candidate_signature_raw)

        candidate_width = len(candidate_signature_raw)
        candidate_depth_sum = signature_depth_sum(
            candidate_signature_raw
        )

        prefix_match = prefix_match_count(
            target_signature_raw,
            candidate_signature_raw,
        )

        suffix_match = suffix_match_count(
            target_signature_raw,
            candidate_signature_raw,
        )

        width_gap = target_width - candidate_width
        depth_gap = target_depth_sum - candidate_depth_sum

        transition_path, transition_verified = (
            simulate_transition_path(
                candidate_signature_raw,
                target_signature=target_signature_raw,
            )
        )

        transition_ops: list[str] = []

        for step in transition_path[1:]:
            transition_ops.append(step.split(" -> ", maxsplit=1)[0])

        if not transition_ops:
            transition_label = "IDENTITY"
        else:
            transition_label = " + ".join(transition_ops)

        if transition_label == "IDENTITY":
            transition_hint = "exact-structural-match"
        elif transition_label.startswith("NEW") and "INC" in transition_ops:
            transition_hint = "width-then-depth-growth"
        elif transition_label.startswith("NEW"):
            transition_hint = "width-growth"
        elif transition_label.startswith("INC"):
            transition_hint = "depth-only-growth"
        else:
            transition_hint = "mixed-growth"

        print(f"candidate_{index}_kind = {candidate['kind']}")
        print(f"candidate_{index}_value = {candidate['value']}")
        print(f"candidate_{index}_source = {candidate['source']}")
        print(f"candidate_{index}_confidence = {candidate['confidence']}")
        print(f"candidate_{index}_note = {candidate['note']}")

        print(f"candidate_{index}_signature = {candidate_signature}")
        print(f"candidate_{index}_width = {candidate_width}")
        print(f"candidate_{index}_depth_sum = {candidate_depth_sum}")

        print(f"candidate_{index}_width_gap = {width_gap}")
        print(f"candidate_{index}_depth_gap = {depth_gap}")

        print(f"candidate_{index}_prefix_match = {prefix_match}")
        print(f"candidate_{index}_suffix_match = {suffix_match}")

        print(
            f"candidate_{index}_estimated_transition = "
            f"{transition_label}"
        )

        print(
            f"candidate_{index}_transition_hint = "
            f"{transition_hint}"
        )

        for step_index, step in enumerate(
            transition_path,
            start=1,
        ):
            print(
                f"candidate_{index}_transition_step_"
                f"{step_index} = {step}"
            )

        print(
            f"candidate_{index}_transition_verified = "
            f"{'yes' if transition_verified else 'no'}"
        )

        print()

    print()


def same_shape_factor_hits_from_output(output: str) -> list[int]:
    factors: list[int] = []

    for line in output.splitlines():
        key, separator, raw_value = line.partition("=")

        if separator == "":
            continue

        key = key.strip()
        raw_value = raw_value.strip()

        if not key.startswith("factor_"):
            continue

        suffix = key.removeprefix("factor_")

        if not suffix.isdigit():
            continue

        try:
            factors.append(int(raw_value))
        except ValueError:
            continue

    return factors


def print_same_shape_factor_promotion(
    *,
    n: int,
    factors: list[int],
) -> None:
    promoted: list[tuple[int, int]] = []

    for factor in sorted(set(factors)):
        if 1 < factor < n and n % factor == 0:
            promoted.append((factor, n // factor))

    if not promoted:
        print("auto_factor_promotion_status = no-factor-promoted")
        print("route_final_status = unresolved-no-grip")
        return

    promoted_factors = {factor for factor, _cofactor in promoted}
    complete_pair: tuple[int, int] | None = None

    for factor, cofactor in promoted:
        if factor * cofactor == n and cofactor in promoted_factors:
            complete_pair = (factor, cofactor)
            break

    if complete_pair is None:
        promotion_status = "partial-factorization"
        final_status = "partial-factorization-by-same-shape-scan"
        verified_factorization = "-"
    else:
        promotion_status = "complete-factorization"
        final_status = "solved-by-same-shape-scan"
        verified_factorization = f"{complete_pair[0]} * {complete_pair[1]}"

    print(f"auto_factor_promotion_status = {promotion_status}")

    for index, (factor, cofactor) in enumerate(promoted, start=1):
        print(f"promoted_factor_{index} = {factor}")
        print(f"promoted_cofactor_{index} = {cofactor}")

    print(f"verified_factorization = {verified_factorization}")
    print(f"route_final_status = {final_status}")


def print_pet_grip_diagnostic(
    *,
    n: int,
    candidates: list[dict[str, str]],
    auto_same_shape_scan: bool = False,
) -> None:
    arithmetic_grip_count = 0
    structural_match_count = 0
    best_gcd = 1

    for candidate in candidates:
        try:
            candidate_value = int(candidate["value"])
        except ValueError:
            continue

        gcd_value = math.gcd(n, candidate_value)
        best_gcd = max(best_gcd, gcd_value)

        if 1 < gcd_value < n:
            arithmetic_grip_count += 1

        if transition_verified_for_candidate(
            target_n=n,
            candidate_value=candidate_value,
        ):
            structural_match_count += 1

    if arithmetic_grip_count > 0:
        grip_status = "has-arithmetic-grip"
        no_grip_hint = "no"
    elif structural_match_count > 0:
        grip_status = "structural-match-no-grip"
        no_grip_hint = "yes"
    else:
        grip_status = "no-structural-grip"
        no_grip_hint = "unknown"

    print("PET grip diagnostic")
    print(f"pet_structural_match_count = {structural_match_count}")
    print(f"pet_arithmetic_grip_count = {arithmetic_grip_count}")
    print(f"pet_best_candidate_gcd = {best_gcd}")
    print(f"pet_grip_status = {grip_status}")
    print(f"pet_no_grip_hint = {no_grip_hint}")

    target_signature = str(shape_signature_dict(n)["signature"])

    if grip_status == "structural-match-no-grip":
        print(
            "suggested_same_shape_support_scan_command = "
            f"{sys.executable} tools/core/pet_same_shape_support_scan.py "
            f"{n} --shape '{target_signature}' --prime-limit 200"
        )

        if (
            auto_same_shape_scan
            and target_signature == "[[], []]"
        ):
            print("auto_same_shape_scan_status = running")

            result = subprocess.run(
                [
                    sys.executable,
                    "tools/core/pet_same_shape_support_scan.py",
                    str(n),
                    "--shape",
                    target_signature,
                    "--prime-limit",
                    "200",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            print("auto_same_shape_scan_output_start")

            for line in result.stdout.strip().splitlines():
                print(line)

            print("auto_same_shape_scan_output_end")

            factor_hits = same_shape_factor_hits_from_output(result.stdout)
            print_same_shape_factor_promotion(
                n=n,
                factors=factor_hits,
            )


    print()



def verifier_command_text(n: int, candidates: list[dict[str, str]]) -> str:
    parts = [
        sys.executable,
        "tools/core/pet_classic_candidate_verify.py",
        str(n),
    ]
    for candidate in candidates:
        parts.extend(["--candidate", candidate["value"]])
    return command_text(parts)



def monster_route_summary(n: int) -> dict[str, str]:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_shadow_monster_router.py",
            str(n),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    if result.returncode != 0:
        message = (result.stderr or result.stdout).strip().splitlines()
        return {
            "monster_route_status": "unavailable",
            "monster_route_error": message[0] if message else "unknown router error",
        }

    rows = list(csv.DictReader(StringIO(result.stdout), delimiter="\t"))
    if len(rows) != 1:
        return {
            "monster_route_status": "unavailable",
            "monster_route_error": f"expected 1 router row, got {len(rows)}",
        }

    row = rows[0]
    return {
        "monster_route_status": "available",
        "monster_class": row.get("monster_class", "-"),
        "recommended_strategy": row.get("recommended_strategy", "-"),
        "route_confidence": row.get("route_confidence", "-"),
        "sigma_stability_status": row.get("sigma_stability_status", "-"),
        "sigma_depth_generator": row.get("sigma_depth_generator", "-"),
        "chunk_failure_mode": row.get("chunk_failure_mode", "-"),
        "chunk_best_merge_generator": row.get("chunk_best_merge_generator", "-"),
    }


def monster_route_summary_from_file(path: Path) -> dict[str, str]:
    rows = list(csv.DictReader(StringIO(path.read_text(encoding="utf-8")), delimiter="\t"))
    if len(rows) != 1:
        return {
            "monster_route_status": "unavailable",
            "monster_route_error": f"expected 1 router row, got {len(rows)}",
        }

    row = rows[0]
    return {
        "monster_route_status": "available",
        "monster_class": row.get("monster_class", "-"),
        "recommended_strategy": row.get("recommended_strategy", "-"),
        "route_confidence": row.get("route_confidence", "-"),
        "sigma_stability_status": row.get("sigma_stability_status", "-"),
        "sigma_depth_generator": row.get("sigma_depth_generator", "-"),
        "chunk_failure_mode": row.get("chunk_failure_mode", "-"),
        "chunk_best_merge_generator": row.get("chunk_best_merge_generator", "-"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a PET-guided route from local probe proposal to classic handoff."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument("--max-leaves", type=int, default=8)
    parser.add_argument("--max-generator-count", type=int, default=20)
    parser.add_argument("--excluded-support-limit", type=int, default=16)
    parser.add_argument("--max-move-span", type=int, default=5)
    parser.add_argument("--handoff-radius", type=int, default=100)
    parser.add_argument("--operator-depth", default="auto")
    parser.add_argument(
        "--blade-window",
        choices=("full", "active"),
        default="full",
        help="Proposal race candidate window policy.",
    )
    parser.add_argument(
        "--proposal-file",
        type=Path,
        help="Reuse a precomputed pet_local_probe_proposal output instead of recomputing it.",
    )
    parser.add_argument(
        "--monster-route-file",
        type=Path,
        help="Reuse a precomputed PET shadow monster router TSV row instead of recomputing it.",
    )
    parser.add_argument(
        "--include-monster-route",
        action="store_true",
        help="Append PET shadow monster router diagnostics to the handoff output.",
    )
    parser.add_argument(
        "--auto-same-shape-scan",
        action="store_true",
        help="Run automatic same-shape support scan for PET no-grip cases.",
    )
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("pet_classic_handoff_route expects integers >= 1")

    if args.include_monster_route:
        monster_route = (
            monster_route_summary_from_file(args.monster_route_file)
            if args.monster_route_file is not None
            else monster_route_summary(args.n)
        )
    else:
        monster_route = {"monster_route_status": "skipped"}
    monster_class = monster_route.get("monster_class", "unknown")

    if (
        args.proposal_file is None
        and monster_route.get("monster_route_status") == "available"
        and monster_class in {
            "diffuse-field",
            "diffuse-digit-mixed-field",
            "saturated-border-field",
            "sparse-zero-border-field",
            "obvious-periodic-field",
            "sigma-coherent-large-field",
        }
    ):
        print("PET CLASSIC HANDOFF ROUTE")
        print()
        print(f"N = {args.n}")
        print(f"proposal_transition = skipped-by-router")
        print(f"proposal_transition_side = skipped-by-router")
        print(f"proposal_status = skipped-by-router")
        print(f"proposal_primary_band = skipped-by-router")
        print(f"proposal_side_band = skipped-by-router")
        print(f"proposal_selected_backbone_order = skipped-by-router")
        print(f"proposal_race_shape_diagnostic = skipped-by-router")
        print(f"proposal_selected_operator_sequence = skipped-by-router")
        print(f"proposal_composite_border_hint = skipped-by-router")
        print(f"proposal_decimal_rigid_border_score = skipped-by-router")
        print(f"proposal_decimal_rigid_border_hint = skipped-by-router")
        print(f"proposal_operator_depth = {args.operator_depth}")
        print(f"proposal_blade_window = {args.blade_window}")
        print("classic_probe_policy = router-preempted")
        print()
        if args.include_monster_route:
            print("PET shadow monster route")
            print(f"monster_route_status = {monster_route['monster_route_status']}")
            print(f"monster_class = {monster_route['monster_class']}")
            print(f"recommended_strategy = {monster_route['recommended_strategy']}")
            print(f"route_confidence = {monster_route['route_confidence']}")
            print(f"sigma_stability_status = {monster_route['sigma_stability_status']}")
            print(f"sigma_depth_generator = {monster_route['sigma_depth_generator']}")
            print(f"chunk_failure_mode = {monster_route['chunk_failure_mode']}")
            print(f"chunk_best_merge_generator = {monster_route['chunk_best_merge_generator']}")
            print()
        router_base_candidates = candidate_rows(
            monster_route=monster_route,
            selected_backbone_generator="skipped-by-router",
            selected_backbone_order="skipped-by-router",
        )
        router_base_count = len(router_base_candidates)
        router_candidates = expand_candidates(
            router_base_candidates,
            target_n=args.n,
        )
        router_candidates = append_derived_lcm_merge(
            router_candidates,
            base_count=router_base_count,
        )
        router_candidates = rank_candidates_by_signature_transition(
            router_candidates,
            target_n=args.n,
        )
        print_candidates(router_candidates, base_count=router_base_count, target_n=args.n)
        print_pet_grip_diagnostic(
            n=args.n,
            candidates=router_candidates,
            auto_same_shape_scan=False,
        )
        print("route_status = unavailable")
        print(f"route_kind = {monster_class}")
        print("reason = router preempted local probe recomputation for a large or diffuse field")
        print(f"suggested_verifier_command = {verifier_command_text(args.n, router_candidates)}")
        print("route_trial_limit_hint = avoid-sigma-expansion")
        print("route_trial_limit_reason = router classified the field before local probe")
        print("route_warning = local probe skipped because router already classified the field as non-local or large-shortcut")
        print()
        print("claim = PET classic handoff route only; classic verification required")
        return 0

    if args.proposal_file is None:
        proposal = run_command(
            [
                sys.executable,
                "tools/pet_local_probe_proposal.py",
                str(args.n),
                "--operator-depth",
                args.operator_depth,
                "--backbone-selection",
                "race",
                "--blade-window",
                args.blade_window,
            ]
        )
    else:
        proposal = args.proposal_file.read_text(encoding="utf-8")

    transition = extract_value(proposal, "transition")
    transition_side = extract_value(proposal, "transition_side")
    proposal_status = extract_value(proposal, "proposal_status")
    primary_band = extract_value(proposal, "primary_band")
    side_band = extract_value(proposal, "side_band")
    selected_backbone_order = extract_value(proposal, "selected_backbone_order")
    selected_backbone_generator = extract_value(proposal, "selected_backbone_generator")
    race_shape_diagnostic = extract_value(proposal, "race_shape_diagnostic")
    selected_operator_sequence = extract_value(proposal, "selected_operator_sequence")
    composite_border_hint = extract_value(proposal, "composite_border_hint")
    decimal_rigid_border_score = extract_value(proposal, "decimal_rigid_border_score")
    decimal_rigid_border_hint = extract_value(proposal, "decimal_rigid_border_hint")
    policy = classic_probe_policy(race_shape_diagnostic)

    print("PET CLASSIC HANDOFF ROUTE")
    print()
    print(f"N = {args.n}")
    print(f"proposal_transition = {transition}")
    print(f"proposal_transition_side = {transition_side}")
    print(f"proposal_status = {proposal_status}")
    print(f"proposal_primary_band = {primary_band}")
    print(f"proposal_side_band = {side_band}")
    print(f"proposal_selected_backbone_order = {selected_backbone_order}")
    print(f"proposal_race_shape_diagnostic = {race_shape_diagnostic}")
    print(f"proposal_selected_operator_sequence = {selected_operator_sequence}")
    print(f"proposal_composite_border_hint = {composite_border_hint}")
    print(f"proposal_decimal_rigid_border_score = {decimal_rigid_border_score}")
    print(f"proposal_decimal_rigid_border_hint = {decimal_rigid_border_hint}")
    print(f"proposal_operator_depth = {args.operator_depth}")
    print(f"proposal_blade_window = {args.blade_window}")
    print(f"classic_probe_policy = {policy}")
    if decimal_rigid_border_hint == "yes":
        print("route_note = decimal rigid border detected; route-only benchmark may be expensive")
    print()
    if args.include_monster_route:
        print("PET shadow monster route")
        print(f"monster_route_status = {monster_route['monster_route_status']}")
        if monster_route["monster_route_status"] == "available":
            print(f"monster_class = {monster_route['monster_class']}")
            print(f"recommended_strategy = {monster_route['recommended_strategy']}")
            print(f"route_confidence = {monster_route['route_confidence']}")
            print(f"sigma_stability_status = {monster_route['sigma_stability_status']}")
            print(f"sigma_depth_generator = {monster_route['sigma_depth_generator']}")
            print(f"chunk_failure_mode = {monster_route['chunk_failure_mode']}")
            print(f"chunk_best_merge_generator = {monster_route['chunk_best_merge_generator']}")
        else:
            print(f"monster_route_error = {monster_route.get('monster_route_error', '-')}")
        print()
    route_warning = None
    route_note = None
    if monster_route.get("monster_route_status") == "available":
        monster_class = monster_route.get("monster_class", "unknown")
        if monster_class == "deceptive-stable-sigma":
            route_warning = (
                "sigma support appears stable but locally deceptive; avoid trusting sigma generator directly"
            )
        elif monster_class == "local-preserved-shadow-coherent":
            route_note = (
                "local lambda preservation detected; sigma and local chunk diagnostics agree"
            )
        elif monster_class == "local-preserved-sigma-floor-risk":
            route_warning = (
                "local PET generator appears preserved, but sigma support may be collapsed to a low floor"
            )
        elif monster_class == "fragile-shadow-field":
            route_warning = (
                "sigma support is depth-fragile; treat route as conservative only"
            )

    route_trial_limit_hint = "none"
    route_trial_limit_reason = "no router-guided trial-limit hint"
    base_candidates = candidate_rows(
        monster_route=monster_route,
        selected_backbone_generator=selected_backbone_generator,
        selected_backbone_order=selected_backbone_order,
    )
    base_count = len(base_candidates)
    candidates = expand_candidates(
        base_candidates,
        target_n=args.n,
    )
    candidates = append_derived_lcm_merge(
        candidates,
        base_count=base_count,
    )
    candidates = rank_candidates_by_signature_transition(
        candidates,
        target_n=args.n,
    )
    print_candidates(candidates, base_count=base_count, target_n=args.n)
    print_pet_grip_diagnostic(
        n=args.n,
        candidates=candidates,
        auto_same_shape_scan=args.auto_same_shape_scan,
    )
    if monster_route.get("monster_route_status") == "available":
        monster_class = monster_route.get("monster_class", "unknown")
        if monster_class == "deceptive-stable-sigma":
            route_trial_limit_hint = "keep-conservative-20"
            route_trial_limit_reason = "stable sigma appears deceptive"
        elif monster_class == "local-preserved-shadow-coherent":
            route_trial_limit_hint = "keep-structural-bound"
            route_trial_limit_reason = "local lambda preservation agrees with sigma"
        elif monster_class == "local-preserved-sigma-floor-risk":
            route_trial_limit_hint = "avoid-low-sigma-floor-shortcut"
            route_trial_limit_reason = "local generator is preserved but sigma may be collapsed to a low floor"
        elif monster_class == "fragile-shadow-field":
            route_trial_limit_hint = "keep-conservative-current-limit"
            route_trial_limit_reason = "sigma support is depth-fragile"
        elif monster_class in {"diffuse-field", "diffuse-digit-mixed-field"}:
            route_trial_limit_hint = "avoid-sigma-expansion"
            route_trial_limit_reason = "no coherent sigma support detected"
        elif monster_class in {"saturated-shadow-coherent", "sigma-coherent-large-field"}:
            route_trial_limit_hint = "keep-sigma-guided-limit"
            route_trial_limit_reason = "coherent large-field sigma support detected"


    if policy == "primality-check-only":
        suggested_parts = [
            "python",
            "-m",
            "pet.cli",
            "opaque-probe",
            str(args.n),
            "--trial-limit",
            "2",
        ]
        print("route_status = available")
        print("route_kind = primality-check-only")
        print("reason = atomic PET shape; run minimal classic residual/primality probe")
        print(f"suggested_command = {command_text(suggested_parts)}")
        print(f"suggested_verifier_command = {verifier_command_text(args.n, candidates)}")
        print(f"route_trial_limit_hint = {route_trial_limit_hint}")
        print(f"route_trial_limit_reason = {route_trial_limit_reason}")
        if route_note is not None:
            print(f"route_note = {route_note}")
        if route_warning is not None:
            print(f"route_warning = {route_warning}")
        print()
        print("claim = PET classic handoff route only; classic verification required")
        return 0

    if policy == "power-like-local-check":
        suggested_parts = [
            "python",
            "-m",
            "pet.cli",
            "opaque-probe",
            str(args.n),
            "--trial-limit",
            "2",
        ]
        print("route_status = available")
        print("route_kind = power-like-local-check")
        print("reason = narrow deep PET shape; run minimal classic check for repeated small factors")
        print(f"suggested_command = {command_text(suggested_parts)}")
        print(f"suggested_verifier_command = {verifier_command_text(args.n, candidates)}")
        print(f"route_trial_limit_hint = {route_trial_limit_hint}")
        print(f"route_trial_limit_reason = {route_trial_limit_reason}")
        if route_note is not None:
            print(f"route_note = {route_note}")
        if route_warning is not None:
            print(f"route_warning = {route_warning}")
        print()
        print("claim = PET classic handoff route only; classic verification required")
        return 0

    if policy == "backbone-wide-structural-check":
        suggested_parts = [
            "python",
            "-m",
            "pet.cli",
            "opaque-probe",
            str(args.n),
            "--trial-limit",
            selected_backbone_order,
        ]
        print("route_status = available")
        print("route_kind = backbone-wide-structural-check")
        print("reason = wide exact PET shape; run classic probe bounded by selected backbone order")
        print(f"suggested_command = {command_text(suggested_parts)}")
        print(f"suggested_verifier_command = {verifier_command_text(args.n, candidates)}")
        print(f"route_trial_limit_hint = {route_trial_limit_hint}")
        print(f"route_trial_limit_reason = {route_trial_limit_reason}")
        if route_note is not None:
            print(f"route_note = {route_note}")
        if route_warning is not None:
            print(f"route_warning = {route_warning}")
        print()
        print("claim = PET classic handoff route only; classic verification required")
        return 0

    if policy == "operator-neighborhood-check":
        suggested_parts = [
            "python",
            "-m",
            "pet.cli",
            "opaque-probe",
            str(args.n),
            "--trial-limit",
            selected_backbone_order,
        ]
        print("route_status = available")
        print("route_kind = operator-neighborhood-check")
        print("reason = near PET shape; run classic probe bounded by selected operator neighborhood")
        print(f"suggested_command = {command_text(suggested_parts)}")
        print(f"suggested_verifier_command = {verifier_command_text(args.n, candidates)}")
        print(f"route_trial_limit_hint = {route_trial_limit_hint}")
        print(f"route_trial_limit_reason = {route_trial_limit_reason}")
        if route_note is not None:
            print(f"route_note = {route_note}")
        if route_warning is not None:
            print(f"route_warning = {route_warning}")
        print()
        print("claim = PET classic handoff route only; classic verification required")
        return 0

    if policy == "complex-border-route-needed":
        lens_transition = run_command(
            [
                sys.executable,
                "tools/pet_lens_transition.py",
                str(args.n),
                "--max-leaves",
                str(args.max_leaves),
            ]
        )
        transition_available = extract_value(lens_transition, "transition_available")
        transition = extract_value(lens_transition, "transition")

        suggested_parts = [
            "python",
            "-m",
            "pet.cli",
            "opaque-probe",
            str(args.n),
            "--trial-limit",
            "20",
        ]
        print("route_status = available")
        if (
            composite_border_hint == "balanced-flat-border"
            and transition_available == "yes"
            and transition == "DROP"
        ):
            print("route_kind = balanced-flat-border-lens-drop-classic-probe")
            print("reason = balanced flat PET border has a DROP lens transition; run conservative classic residual probe")
        elif transition_available == "yes" and transition == "DROP":
            print("route_kind = complex-border-lens-drop-classic-probe")
            print("reason = complex border PET shape has a DROP lens transition; run conservative classic residual probe")
        else:
            print("route_kind = complex-border-classic-probe")
            print("reason = complex border PET shape; run conservative classic residual probe")
        print(f"suggested_command = {command_text(suggested_parts)}")
        print(f"suggested_verifier_command = {verifier_command_text(args.n, candidates)}")
        print(f"route_trial_limit_hint = {route_trial_limit_hint}")
        print(f"route_trial_limit_reason = {route_trial_limit_reason}")
        if route_note is not None:
            print(f"route_note = {route_note}")
        if route_warning is not None:
            print(f"route_warning = {route_warning}")
        print()
        print("claim = PET classic handoff route only; classic verification required")
        return 0

    print("route_status = unavailable")
    print(f"route_kind = {policy}")
    print("reason = classic probe policy route not implemented yet")
    print(f"route_trial_limit_hint = {route_trial_limit_hint}")
    print(f"route_trial_limit_reason = {route_trial_limit_reason}")
    if route_note is not None:
        print(f"route_note = {route_note}")
    if route_warning is not None:
        print(f"route_warning = {route_warning}")
    print()
    print("claim = PET classic handoff route only; classic verification required")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
