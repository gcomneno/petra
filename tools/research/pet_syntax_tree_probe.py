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
KEY_VALUE_RE = re.compile(r"^([A-Za-z0-9_]+)\s*=\s*(.*)$")
DEPTH_INPUT_RE = re.compile(r"^depth_(\d+)_input\s*=\s*(\d+)\s*$")


def parse_key_values(text: str) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}

    for line in text.splitlines():
        match = KEY_VALUE_RE.match(line.strip())

        if not match:
            continue

        key, value = match.groups()
        values.setdefault(key, []).append(value.strip())

    return values


def latest(
    values: dict[str, list[str]],
    key: str,
    default: str = "unknown",
) -> str:
    found = values.get(key)

    if not found:
        return default

    return found[-1]


def depth_value(
    values: dict[str, list[str]],
    depth: int,
    suffix: str,
    default: str = "unknown",
) -> str:
    return latest(values, f"depth_{depth}_{suffix}", default)


def parse_depth_inputs(output: str) -> list[tuple[int, int]]:
    depths: list[tuple[int, int]] = []

    for line in output.splitlines():
        match = DEPTH_INPUT_RE.match(line.strip())

        if not match:
            continue

        depth, value = match.groups()
        depths.append((int(depth), int(value)))

    return depths


def parse_factorization(raw: str) -> list[int]:
    if raw in {"", "-", "unknown"}:
        return []

    factors: list[int] = []

    for item in raw.split("*"):
        item = item.strip()

        if not item:
            continue

        try:
            factors.append(int(item))
        except ValueError:
            return []

    return factors


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT_DIR,
        check=False,
        capture_output=True,
        text=True,
    )


def residual_command(args: argparse.Namespace) -> list[str]:
    command = [
        sys.executable,
        "tools/core/pet_residual_descent_route.py",
        str(args.n),
        "--max-depth",
        str(args.max_depth),
        "--flat-k-prime-limit",
        str(args.flat_k_prime_limit),
        "--flat-k-max-supports",
        str(args.flat_k_max_supports),
        "--flat-k-max-factor-lines",
        str(args.flat_k_max_factor_lines),
        "--shape-family-support-limit",
        str(args.shape_family_support_limit),
        "--shape-family-max-supports",
        str(args.shape_family_max_supports),
        "--shape-family-max-factor-lines",
        str(args.shape_family_max_factor_lines),
    ]

    if args.auto_flat_k_scan:
        command.append("--auto-flat-k-scan")

    if args.auto_shape_family_scan:
        command.append("--auto-shape-family-scan")

    return command


def handoff_command(
    value: int,
    args: argparse.Namespace,
) -> list[str]:
    command = [
        sys.executable,
        "tools/core/pet_classic_handoff_route.py",
        str(value),
        "--include-monster-route",
        "--same-shape-prime-limit",
        str(args.same_shape_prime_limit),
        "--flat-k-prime-limit",
        str(args.flat_k_prime_limit),
        "--flat-k-max-supports",
        str(args.flat_k_max_supports),
        "--flat-k-max-factor-lines",
        str(args.flat_k_max_factor_lines),
        "--shape-family-support-limit",
        str(args.shape_family_support_limit),
        "--shape-family-max-supports",
        str(args.shape_family_max_supports),
        "--shape-family-max-factor-lines",
        str(args.shape_family_max_factor_lines),
    ]

    if args.auto_same_shape_scan:
        command.append("--auto-same-shape-scan")

    if args.auto_flat_k_scan:
        command.append("--auto-flat-k-scan")

    if args.auto_shape_family_scan:
        command.append("--auto-shape-family-scan")

    return command


def handoff_metadata(
    value: int,
    args: argparse.Namespace,
) -> dict[str, str]:
    result = run_command(handoff_command(value, args))

    if result.returncode != 0:
        return {
            "target_signature": "handoff-error",
            "shape_family_class": "handoff-error",
            "pet_grip_status": "handoff-error",
            "summary_route_escalation_policy": "handoff-error",
            "summary_route_execution_status": "handoff-error",
            "summary_route_final_status": "handoff-error",
        }

    values = parse_key_values(result.stdout)

    return {
        "target_signature": latest(values, "target_signature"),
        "shape_family_class": latest(values, "shape_family_class"),
        "pet_grip_status": latest(values, "pet_grip_status"),
        "summary_route_escalation_policy": latest(
            values,
            "summary_route_escalation_policy",
        ),
        "summary_route_execution_status": latest(
            values,
            "summary_route_execution_status",
        ),
        "summary_route_final_status": latest(
            values,
            "summary_route_final_status",
        ),
    }


def make_pet_state_node(
    *,
    node_id: str,
    role: str,
    value: int,
    depth: int,
    descent_values: dict[str, list[str]],
    handoff: dict[str, str],
) -> dict[str, Any]:
    depth_status = depth_value(descent_values, depth, "status", "non-terminal")

    return {
        "id": node_id,
        "role": role,
        "value": value,
        "shape_signature": handoff["target_signature"],
        "shape_family_class": handoff["shape_family_class"],
        "pet_grip_status": handoff["pet_grip_status"],
        "route_policy": depth_value(
            descent_values,
            depth,
            "route_escalation_policy",
            handoff["summary_route_escalation_policy"],
        ),
        "route_status": depth_value(
            descent_values,
            depth,
            "route_final_status",
            handoff["summary_route_final_status"],
        ),
        "terminal_status": depth_status,
        "metadata": {
            "depth": depth,
            "route_execution_status": depth_value(
                descent_values,
                depth,
                "route_execution_status",
                handoff["summary_route_execution_status"],
            ),
        },
    }


def make_anchor_node(
    *,
    node_id: str,
    value: int,
    depth: int,
) -> dict[str, Any]:
    return {
        "id": node_id,
        "role": "anchor",
        "value": value,
        "shape_signature": None,
        "shape_family_class": None,
        "pet_grip_status": None,
        "route_policy": None,
        "route_status": None,
        "terminal_status": "classic-verified",
        "metadata": {
            "depth": depth,
            "verification_status": "classic-verified",
        },
    }


def make_factor_node(
    *,
    node_id: str,
    value: int,
    depth: int,
) -> dict[str, Any]:
    return {
        "id": node_id,
        "role": "factor",
        "value": value,
        "shape_signature": None,
        "shape_family_class": None,
        "pet_grip_status": None,
        "route_policy": None,
        "route_status": None,
        "terminal_status": "classic-verified",
        "metadata": {
            "depth": depth,
            "verification_status": "classic-verified",
        },
    }


def make_prime_leaf_node(
    *,
    node_id: str,
    value: int,
    depth: int,
) -> dict[str, Any]:
    return {
        "id": node_id,
        "role": "prime_leaf",
        "value": value,
        "shape_signature": None,
        "shape_family_class": None,
        "pet_grip_status": None,
        "route_policy": None,
        "route_status": None,
        "terminal_status": "classic-verified",
        "metadata": {
            "depth": depth,
            "verification_status": "classic-verified",
        },
    }


def build_tree(args: argparse.Namespace) -> dict[str, Any]:
    residual_result = run_command(residual_command(args))

    if residual_result.returncode != 0:
        return {
            "schema": "pet.syntax_tree.v0",
            "n": args.n,
            "root": None,
            "nodes": [],
            "edges": [],
            "summary": {
                "status": "residual-descent-error",
                "terminal_residual": None,
                "residual_reduction_chain": None,
                "returncode": residual_result.returncode,
                "stderr": residual_result.stderr.strip(),
            },
            "claim": (
                "PET syntax tree is explanatory only; arithmetic verification "
                "remains classic-bounded"
            ),
        }

    descent_values = parse_key_values(residual_result.stdout)
    depths = parse_depth_inputs(residual_result.stdout)

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    existing_node_ids: set[str] = set()

    for depth, value in depths:
        node_id = f"depth_{depth}_input"
        role = "root" if depth == 0 else "residual"
        handoff = handoff_metadata(value, args)

        nodes.append(
            make_pet_state_node(
                node_id=node_id,
                role=role,
                value=value,
                depth=depth,
                descent_values=descent_values,
                handoff=handoff,
            )
        )
        existing_node_ids.add(node_id)

    for depth, value in depths:
        source_id = f"depth_{depth}_input"
        anchor_raw = depth_value(descent_values, depth, "anchor_factor", "-")
        residual_raw = depth_value(descent_values, depth, "residual", "-")

        if anchor_raw not in {"-", "unknown"}:
            anchor_value = int(anchor_raw)
            anchor_id = f"depth_{depth}_anchor"

            nodes.append(
                make_anchor_node(
                    node_id=anchor_id,
                    value=anchor_value,
                    depth=depth,
                )
            )

            edges.append(
                {
                    "source": source_id,
                    "target": anchor_id,
                    "edge_kind": "has_anchor",
                    "move": "ANCHOR",
                    "verification_status": "classic-verified",
                    "reason": depth_value(
                        descent_values,
                        depth,
                        "selected_anchor_reason",
                        "verified anchor selected by residual descent",
                    ),
                }
            )

            if residual_raw not in {"-", "unknown"}:
                residual_value = int(residual_raw)
                next_depth_id = f"depth_{depth + 1}_input"
                residual_id = (
                    next_depth_id
                    if next_depth_id in existing_node_ids
                    else f"depth_{depth}_residual"
                )

                if residual_id not in existing_node_ids:
                    handoff = handoff_metadata(residual_value, args)
                    nodes.append(
                        make_pet_state_node(
                            node_id=residual_id,
                            role="residual",
                            value=residual_value,
                            depth=depth + 1,
                            descent_values=descent_values,
                            handoff=handoff,
                        )
                    )
                    existing_node_ids.add(residual_id)

                edges.append(
                    {
                        "source": source_id,
                        "target": residual_id,
                        "edge_kind": "has_residual",
                        "move": "RESIDUAL",
                        "verification_status": "classic-verified",
                        "reason": f"{value} / {anchor_value}",
                    }
                )

        verified_factorization = depth_value(
            descent_values,
            depth,
            "verified_factorization",
            "-",
        )
        factors = parse_factorization(verified_factorization)

        for factor_index, factor in enumerate(factors, start=1):
            factor_id = f"depth_{depth}_factor_{factor_index}"

            nodes.append(
                make_factor_node(
                    node_id=factor_id,
                    value=factor,
                    depth=depth,
                )
            )

            edges.append(
                {
                    "source": source_id,
                    "target": factor_id,
                    "edge_kind": "classic_verified_factor",
                    "move": "VERIFY",
                    "verification_status": "classic-verified",
                    "reason": f"verified_factorization = {verified_factorization}",
                }
            )

        if depth_value(descent_values, depth, "status", "") == "complete-prime-leaf":
            prime_leaf_id = f"depth_{depth}_prime_leaf"

            nodes.append(
                make_prime_leaf_node(
                    node_id=prime_leaf_id,
                    value=value,
                    depth=depth,
                )
            )

            edges.append(
                {
                    "source": source_id,
                    "target": prime_leaf_id,
                    "edge_kind": "terminal_prime_leaf",
                    "move": "VERIFY",
                    "verification_status": "classic-verified",
                    "reason": "terminal prime leaf verified by leaf-primality-route",
                }
            )

    return {
        "schema": "pet.syntax_tree.v0",
        "n": args.n,
        "root": "depth_0_input" if depths else None,
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "status": latest(descent_values, "residual_descent_status"),
            "terminal_residual": latest(descent_values, "terminal_residual"),
            "residual_reduction_chain": latest(
                descent_values,
                "residual_reduction_chain",
            ),
        },
        "claim": (
            "PET syntax tree is explanatory only; arithmetic verification "
            "remains classic-bounded"
        ),
    }


def positive_int(raw: str) -> int:
    value = int(raw)

    if value < 1:
        raise argparse.ArgumentTypeError("value must be >= 1")

    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit a research-only PET syntax tree JSON explanation.",
    )
    parser.add_argument("n", type=positive_int)
    parser.add_argument("--max-depth", type=int, default=10)
    parser.add_argument("--same-shape-prime-limit", type=int, default=200)
    parser.add_argument("--auto-same-shape-scan", action="store_true")
    parser.add_argument(
        "--auto-flat-k-scan",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--flat-k-prime-limit", type=int, default=50)
    parser.add_argument("--flat-k-max-supports", type=int, default=5000)
    parser.add_argument("--flat-k-max-factor-lines", type=int, default=25)
    parser.add_argument(
        "--auto-shape-family-scan",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--shape-family-support-limit", type=int, default=5000)
    parser.add_argument("--shape-family-max-supports", type=int, default=1000)
    parser.add_argument("--shape-family-max-factor-lines", type=int, default=25)

    args = parser.parse_args()

    if args.max_depth < 0:
        raise SystemExit("--max-depth must be >= 0")

    tree = build_tree(args)
    print(json.dumps(tree, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
