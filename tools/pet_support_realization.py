#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def require_field(obj: dict[str, Any], key: str) -> Any:
    if key not in obj:
        raise SystemExit(f"missing required field: {key}")
    return obj[key]


PEELING_STATUS_VOCABULARY = [
    "not-attempted",
    "blocked",
    "partially-peeled",
    "fully-peeled",
]


def _evaluate_supported_constraints(block: dict[str, Any]) -> dict[str, Any]:
    out = dict(block)
    constraints = out.get("constraints")
    if not isinstance(constraints, dict):
        return out

    target_product = int(out["target_product"])
    checks: dict[str, bool] = {}

    if "bit_length_min" in constraints:
        checks["bit_length_min"] = target_product.bit_length() >= int(constraints["bit_length_min"])

    if "bit_length_max" in constraints:
        checks["bit_length_max"] = target_product.bit_length() <= int(constraints["bit_length_max"])

    if "known_divisors" in constraints:
        divisors = [int(x) for x in constraints["known_divisors"]]
        checks["known_divisors"] = all(d != 0 and target_product % d == 0 for d in divisors)

    if "forbidden_divisors" in constraints:
        divisors = [int(x) for x in constraints["forbidden_divisors"]]
        checks["forbidden_divisors"] = all(d == 0 or target_product % d != 0 for d in divisors)

    if checks:
        out["constraint_checks"] = checks
    return out




def _with_peeling_status(
    block: dict[str, Any],
    *,
    status: str,
    reason: str | None = None,
) -> dict[str, Any]:
    out = dict(block)
    peeling_status = {"status": status}
    if reason is not None:
        peeling_status["reason"] = reason
    out["peeling_status"] = peeling_status
    return out


def _peel_known_divisors_from_unknown_blocks(
    unknown_blocks: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    original_unknown_block_count = len(unknown_blocks)
    peeled_known_blocks: list[dict[str, Any]] = []
    updated_unknown_blocks: list[dict[str, Any]] = []
    fully_peeled_block_ids: list[str] = []

    for block in unknown_blocks:
        constraints = block.get("constraints", {})
        raw_divisors = constraints.get("known_divisors")

        if not raw_divisors:
            updated_unknown_blocks.append(
                _with_peeling_status(
                    block,
                    status="not-attempted",
                    reason="no-known-divisors",
                )
            )
            continue

        divisors = [int(x) for x in raw_divisors]
        if any(d <= 1 for d in divisors):
            updated_unknown_blocks.append(
                _with_peeling_status(
                    block,
                    status="blocked",
                    reason="invalid-known-divisors",
                )
            )
            continue

        raw_forbidden_divisors = constraints.get("forbidden_divisors") or []
        forbidden_divisors = [int(x) for x in raw_forbidden_divisors]
        if set(divisors) & set(forbidden_divisors):
            updated_unknown_blocks.append(
                _with_peeling_status(
                    block,
                    status="blocked",
                    reason="known-divisors-conflict-with-forbidden-divisors",
                )
            )
            continue

        slot_multiplicity = int(block["slot_multiplicity"])
        if len(divisors) > slot_multiplicity:
            updated_unknown_blocks.append(
                _with_peeling_status(
                    block,
                    status="blocked",
                    reason="known-divisor-count-exceeds-slot-multiplicity",
                )
            )
            continue

        target_product = int(block["target_product"])
        divisor_product = 1
        divisible = True
        for d in divisors:
            if target_product % d != 0:
                divisible = False
                break
            divisor_product *= d

        if not divisible or target_product % divisor_product != 0:
            updated_unknown_blocks.append(
                _with_peeling_status(
                    block,
                    status="blocked",
                    reason="known-divisors-do-not-divide-target-product",
                )
            )
            continue

        residual_slot_multiplicity = slot_multiplicity - len(divisors)
        residual_target_product = target_product // divisor_product

        if residual_slot_multiplicity == 0 and residual_target_product != 1:
            updated_unknown_blocks.append(
                _with_peeling_status(
                    block,
                    status="blocked",
                    reason="last-slot-would-leave-nontrivial-residue",
                )
            )
            continue

        block_id = str(block["block_id"])
        slot_exp = int(block["slot_exp"])

        for i, d in enumerate(divisors, start=1):
            peeled_known_blocks.append(
                _evaluate_supported_constraints(
                    {
                        "block_id": f"{block_id}::known-divisor-{i}",
                        "slot_exp": slot_exp,
                        "slot_multiplicity": 1,
                        "target_product": d,
                        "constraints": {
                            "peeled_from_block": block_id,
                            "peeled_via_known_divisors": True,
                        },
                    }
                )
            )

        if residual_slot_multiplicity > 0:
            residual_block = dict(block)
            residual_block["slot_multiplicity"] = residual_slot_multiplicity
            residual_block["target_product"] = residual_target_product

            residual_constraints = dict(constraints)
            residual_constraints.pop("known_divisors", None)
            residual_block["constraints"] = residual_constraints

            updated_unknown_blocks.append(
                _with_peeling_status(
                    _evaluate_supported_constraints(residual_block),
                    status="partially-peeled",
                    reason="peeled-known-divisors",
                )
            )
        else:
            fully_peeled_block_ids.append(block_id)

    blocked_unknown_blocks = 0
    not_attempted_unknown_blocks = 0
    partially_peeled_unknown_blocks = 0

    for block in updated_unknown_blocks:
        peeling_status = block.get("peeling_status", {})
        status = peeling_status.get("status")
        if status == "blocked":
            blocked_unknown_blocks += 1
        elif status == "not-attempted":
            not_attempted_unknown_blocks += 1
        elif status == "partially-peeled":
            partially_peeled_unknown_blocks += 1

    peeling_summary = {
        "peeled_block_count": len(peeled_known_blocks),
        "peeled_divisor_count": sum(int(block["slot_multiplicity"]) for block in peeled_known_blocks),
        "fully_resolved_unknown_blocks": len(fully_peeled_block_ids),
        "fully_peeled_block_ids": fully_peeled_block_ids,
        "blocked_unknown_blocks": blocked_unknown_blocks,
        "not_attempted_unknown_blocks": not_attempted_unknown_blocks,
        "partially_peeled_unknown_blocks": partially_peeled_unknown_blocks,
    }
    return peeled_known_blocks, updated_unknown_blocks, peeling_summary

def _constraint_status(*block_lists: list[dict[str, Any]]) -> str:
    values: list[bool] = []
    for blocks in block_lists:
        for block in blocks:
            values.extend(block.get("constraint_checks", {}).values())
    return "ok" if all(values or [True]) else "failed"


def _build_from_partial_build_payload(payload: dict[str, Any]) -> dict[str, Any]:
    schema = require_field(payload, "schema")
    build_status = require_field(payload, "build_status")

    if schema != "pet-build-from-int-v2":
        raise SystemExit(
            f"unsupported input schema: {schema} (expected pet-build-from-int-v2)"
        )

    if build_status != "partial":
        raise SystemExit(
            f"support realization stub expects partial build payload, got build_status={build_status!r}"
        )

    input_n = require_field(payload, "input_n")
    target_generator = require_field(payload, "target_generator")
    mode = require_field(payload, "mode")
    factors = require_field(payload, "factors")
    phase1 = require_field(payload, "phase1")
    phase2 = require_field(payload, "phase2")

    phase1_status = require_field(phase1, "status")
    phase1_target_n = require_field(phase1, "target_n")
    phase1_steps = require_field(phase1, "steps")
    same_pet_shape = require_field(phase2, "same_pet_shape")

    if not isinstance(factors, list):
        raise SystemExit("factors must be a list")

    grouped: dict[int, list[int]] = {}
    for i, item in enumerate(factors):
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise SystemExit(f"factors[{i}] must be a [prime, exp] pair")
        prime, exp = int(item[0]), int(item[1])
        grouped.setdefault(exp, []).append(prime)

    exponent_multiset = sorted(
        [exp for exp, primes in grouped.items() for _ in primes],
        reverse=True,
    )

    raw_unknown_blocks = []
    for exp in sorted(grouped.keys(), reverse=True):
        primes = sorted(grouped[exp])
        target_product = 1
        for p in primes:
            target_product *= p
        label = f"exp{exp}-slot" if len(primes) == 1 else f"exp{exp}-slots"
        raw_unknown_blocks.append(
            {
                "block_id": label,
                "slot_exp": exp,
                "slot_multiplicity": len(primes),
                "target_product": target_product,
                "constraints": {
                    "prime_only": True,
                    "count": len(primes),
                    "derived_from_full_factorization": True,
                },
            }
        )

    known_blocks: list[dict[str, Any]] = []
    unknown_blocks = [_evaluate_supported_constraints(b) for b in raw_unknown_blocks]
    peeled_known_blocks, unknown_blocks, peeling_summary = _peel_known_divisors_from_unknown_blocks(unknown_blocks)
    known_blocks.extend(peeled_known_blocks)

    resolved_product = 1
    unresolved_product = 1
    for block in unknown_blocks:
        unresolved_product *= int(block["target_product"]) ** int(block["slot_exp"])

    resolved_exponent_mass = 0
    unresolved_exponent_mass = sum(
        int(block["slot_exp"]) * int(block["slot_multiplicity"]) for block in unknown_blocks
    )
    total_exponent_mass = resolved_exponent_mass + unresolved_exponent_mass

    reconstructed_target_n = resolved_product * unresolved_product
    exact_target_match = reconstructed_target_n == input_n
    resolved_fraction = f"{resolved_product}/{input_n}"

    return {
        "schema": "pet-support-realization-v0",
        "source_schema": schema,
        "input_n": input_n,
        "target_generator": target_generator,
        "mode": mode,
        "exponent_multiset": exponent_multiset,
        "phase1": {
            "status": phase1_status,
            "target_n": phase1_target_n,
            "steps": phase1_steps,
        },
        "phase2": {
            "status": "derived-from-factorization",
            "same_pet_shape": same_pet_shape,
        },
        "known_block_count": 0,
        "unknown_block_count": len(unknown_blocks),
        "known_blocks": known_blocks,
        "unknown_blocks": unknown_blocks,
        "peeling_summary": peeling_summary,
        "peeling_status_vocabulary": PEELING_STATUS_VOCABULARY,
        "resolved_product": resolved_product,
        "unresolved_product": unresolved_product,
        "resolved_fraction": resolved_fraction,
        "resolved_exponent_mass": resolved_exponent_mass,
        "unresolved_exponent_mass": unresolved_exponent_mass,
        "total_exponent_mass": total_exponent_mass,
        "reconstructed_target_n": reconstructed_target_n,
        "exact_target_match": exact_target_match,
        "constraint_status": _constraint_status(known_blocks, unknown_blocks),
        "realization_status": (
            "exact-from-derived-block-products" if exact_target_match else "derived-block-product-mismatch"
        ),
        "message": (
            "support realization is not implemented yet; "
            "this version derives exponent-class blocks from the provided factorization"
        ),
        "next_action": (
            "future versions should consume cheaper build-down constraints when full factorization is not available"
        ),
    }


# V0 realization constraints are aggregated by exponent class, not by individual slot.
#
# This means that blocks such as:
#   - slot_exp = 2, slot_multiplicity = 1
#   - slot_exp = 1, slot_multiplicity = 4
# are interpreted as exponent-class aggregates.
#
# The goal of V0 is to keep the realization contract simple and avoid introducing
# artificial ordering between shape-equivalent slots.
#
# This is appropriate for flat / root-level cases, where same-exponent slots can be
# treated as one block without loss of intended meaning.
#
# Future versions may refine this into position-aware blocks (for example via slot_path
# or subtree_path) when recursive PET shapes require distinguishing same-exponent slots
# that occur in different structural contexts.
def _build_from_constraint_payload(payload: dict[str, Any]) -> dict[str, Any]:
    schema = require_field(payload, "schema")
    if schema != "pet-support-realization-input-v0":
        raise SystemExit(
            f"unsupported input schema: {schema} (expected pet-support-realization-input-v0)"
        )

    input_n = require_field(payload, "input_n")
    target_generator = require_field(payload, "target_generator")
    shape_signature = require_field(payload, "shape_signature")
    slot_count = require_field(payload, "slot_count")
    exponent_multiset = require_field(payload, "exponent_multiset")
    realization_goal = require_field(payload, "realization_goal")
    known_blocks = require_field(payload, "known_blocks")
    unknown_blocks = require_field(payload, "unknown_blocks")

    if not isinstance(known_blocks, list):
        raise SystemExit("known_blocks must be a list")
    if not isinstance(unknown_blocks, list):
        raise SystemExit("unknown_blocks must be a list")

    raw_known_blocks = []
    for i, block in enumerate(known_blocks):
        if not isinstance(block, dict):
            raise SystemExit(f"known_blocks[{i}] must be an object")
        require_field(block, "block_id")
        require_field(block, "slot_exp")
        require_field(block, "slot_multiplicity")
        require_field(block, "target_product")
        raw_known_blocks.append(block)

    raw_unknown_blocks = []
    for i, block in enumerate(unknown_blocks):
        if not isinstance(block, dict):
            raise SystemExit(f"unknown_blocks[{i}] must be an object")
        require_field(block, "block_id")
        require_field(block, "slot_exp")
        require_field(block, "slot_multiplicity")
        require_field(block, "target_product")
        raw_unknown_blocks.append(block)

    known_blocks = [_evaluate_supported_constraints(b) for b in raw_known_blocks]
    unknown_blocks = [_evaluate_supported_constraints(b) for b in raw_unknown_blocks]
    peeled_known_blocks, unknown_blocks, peeling_summary = _peel_known_divisors_from_unknown_blocks(unknown_blocks)
    known_blocks.extend(peeled_known_blocks)

    resolved_product = 1
    for block in known_blocks:
        resolved_product *= int(block["target_product"]) ** int(block["slot_exp"])

    unresolved_product = 1
    for block in unknown_blocks:
        unresolved_product *= int(block["target_product"]) ** int(block["slot_exp"])

    resolved_exponent_mass = sum(
        int(block["slot_exp"]) * int(block["slot_multiplicity"]) for block in known_blocks
    )
    unresolved_exponent_mass = sum(
        int(block["slot_exp"]) * int(block["slot_multiplicity"]) for block in unknown_blocks
    )
    total_exponent_mass = resolved_exponent_mass + unresolved_exponent_mass

    reconstructed_target_n = resolved_product * unresolved_product
    exact_target_match = reconstructed_target_n == input_n
    resolved_fraction = f"{resolved_product}/{input_n}"

    return {
        "schema": "pet-support-realization-v0",
        "source_schema": schema,
        "input_n": input_n,
        "target_generator": target_generator,
        "mode": "constraint-driven-support-realization",
        "shape_signature": shape_signature,
        "slot_count": slot_count,
        "exponent_multiset": exponent_multiset,
        "realization_goal": realization_goal,
        "phase1": {
            "status": "external-input",
            "target_n": target_generator,
            "steps": None,
        },
        "phase2": {
            "status": "constraint-input",
            "same_pet_shape": True,
        },
        "known_block_count": len(known_blocks),
        "unknown_block_count": len(unknown_blocks),
        "known_blocks": known_blocks,
        "unknown_blocks": unknown_blocks,
        "peeling_summary": peeling_summary,
        "peeling_status_vocabulary": PEELING_STATUS_VOCABULARY,
        "resolved_product": resolved_product,
        "unresolved_product": unresolved_product,
        "resolved_fraction": resolved_fraction,
        "resolved_exponent_mass": resolved_exponent_mass,
        "unresolved_exponent_mass": unresolved_exponent_mass,
        "total_exponent_mass": total_exponent_mass,
        "reconstructed_target_n": reconstructed_target_n,
        "exact_target_match": exact_target_match,
        "constraint_status": _constraint_status(known_blocks, unknown_blocks),
        "realization_status": "exact-from-block-products" if exact_target_match else "block-product-mismatch",
        "message": (
            "support realization is not implemented yet; "
            "this version can only reconstruct the target from provided block products"
        ),
        "next_action": (
            "future versions should attempt support lift from the provided blocks "
            "and cheap arithmetic constraints"
        ),
    }


def build_report(payload: dict[str, Any]) -> dict[str, Any]:
    schema = require_field(payload, "schema")

    if schema == "pet-build-from-int-v2":
        return _build_from_partial_build_payload(payload)
    if schema == "pet-support-realization-input-v0":
        return _build_from_constraint_payload(payload)

    raise SystemExit(
        f"unsupported input schema: {schema} "
        f"(expected pet-build-from-int-v2 or pet-support-realization-input-v0)"
    )


def _print_block(block: dict[str, Any]) -> None:
    print(f"- block_id = {block['block_id']}")
    print(f"  slot_exp = {block['slot_exp']}")
    print(f"  slot_multiplicity = {block['slot_multiplicity']}")
    print(f"  target_product = {block['target_product']}")
    constraints = block.get("constraints")
    if constraints is not None:
        print(f"  constraints = {json.dumps(constraints, ensure_ascii=False, sort_keys=True)}")
    checks = block.get("constraint_checks")
    if checks is not None:
        print(f"  constraint_checks = {json.dumps(checks, ensure_ascii=False, sort_keys=True)}")

    peeling_status = block.get("peeling_status")
    if peeling_status is not None:
        print(f"  peeling_status = {json.dumps(peeling_status, ensure_ascii=False, sort_keys=True)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and restate support-realization inputs and partial build payloads."
    )
    parser.add_argument("input_json", help="input JSON payload")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    report = build_report(payload)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"input_n = {report['input_n']}")
        print(f"target_generator = {report['target_generator']}")
        print(f"mode = {report['mode']}")
        if "shape_signature" in report:
            print(f"shape_signature = {json.dumps(report['shape_signature'], ensure_ascii=False)}")
        if "slot_count" in report:
            print(f"slot_count = {report['slot_count']}")
        if "exponent_multiset" in report:
            print(f"exponent_multiset = {report['exponent_multiset']}")
        if "realization_goal" in report:
            print(f"realization_goal = {report['realization_goal']}")
        print()
        print("[phase 1]")
        print(f"status = {report['phase1']['status']}")
        print(f"target_n = {report['phase1']['target_n']}")
        print(f"steps = {report['phase1']['steps']}")
        print()
        print("[phase 2]")
        print(f"status = {report['phase2']['status']}")
        print(f"same_pet_shape = {str(report['phase2']['same_pet_shape']).lower()}")
        print()
        print(f"known_block_count = {report['known_block_count']}")
        if report["known_blocks"]:
            print("[known blocks]")
            for block in report["known_blocks"]:
                _print_block(block)
        print(f"unknown_block_count = {report['unknown_block_count']}")
        if report["unknown_blocks"]:
            print("[unknown blocks]")
            for block in report["unknown_blocks"]:
                _print_block(block)
        print()
        if "reconstructed_target_n" in report:
            print(f"resolved_product = {report['resolved_product']}")
            print(f"unresolved_product = {report['unresolved_product']}")
            print(f"resolved_fraction = {report['resolved_fraction']}")
            print(f"resolved_exponent_mass = {report['resolved_exponent_mass']}")
            print(f"unresolved_exponent_mass = {report['unresolved_exponent_mass']}")
            print(f"total_exponent_mass = {report['total_exponent_mass']}")
            print(f"reconstructed_target_n = {report['reconstructed_target_n']}")
            print(f"exact_target_match = {str(report['exact_target_match']).lower()}")
        print(f"constraint_status = {report['constraint_status']}")
        print(f"realization_status = {report['realization_status']}")
        print(f"message = {report['message']}")
        print(f"next_action = {report['next_action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
