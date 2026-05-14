from __future__ import annotations

import json
import subprocess
import sys
from typing import Any


def run_probe(n: int) -> dict[str, Any]:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_syntax_tree_probe.py",
            str(n),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return json.loads(result.stdout)


def test_pet_syntax_tree_probe_emits_json_tree_for_one_deep_tail() -> None:
    tree = run_probe(245)

    assert tree["schema"] == "pet.syntax_tree.v0"
    assert tree["n"] == 245
    assert tree["root"] == "depth_0_input"
    assert tree["summary"]["status"] == "complete"
    assert tree["summary"]["terminal_residual"] == "1"
    assert "classic-bounded" in tree["claim"]

    root = next(node for node in tree["nodes"] if node["id"] == tree["root"])

    assert root["role"] == "root"
    assert root["value"] == 245
    assert root["shape_signature"] == "[[], [[]]]"
    assert root["shape_family_class"] == "one-deep-tail"

    edge_kinds = {edge["edge_kind"] for edge in tree["edges"]}

    assert "has_anchor" in edge_kinds
    assert "has_residual" in edge_kinds


def test_pet_syntax_tree_probe_records_residual_descent_chain() -> None:
    tree = run_probe(24680)

    assert tree["schema"] == "pet.syntax_tree.v0"
    assert tree["summary"]["status"] == "complete"
    assert tree["summary"]["terminal_residual"] == "1"
    assert tree["summary"]["residual_reduction_chain"] == "20 * 2 * 617"

    values_by_role = {
        (node["role"], node["value"])
        for node in tree["nodes"]
    }

    assert ("root", 24680) in values_by_role
    assert ("anchor", 20) in values_by_role
    assert ("anchor", 2) in values_by_role
    assert ("residual", 1234) in values_by_role
    assert ("residual", 617) in values_by_role

    residual_edges = [
        edge
        for edge in tree["edges"]
        if edge["edge_kind"] == "has_residual"
    ]

    assert any(edge["reason"] == "24680 / 20" for edge in residual_edges)
    assert any(edge["reason"] == "1234 / 2" for edge in residual_edges)


def test_pet_syntax_tree_probe_output_is_deterministic() -> None:
    first = run_probe(1001)
    second = run_probe(1001)

    assert first == second


def test_pet_syntax_tree_probe_represents_terminal_prime_leaf() -> None:
    tree = run_probe(24680)

    prime_leaf_nodes = [
        node
        for node in tree["nodes"]
        if node["role"] == "prime_leaf"
    ]

    assert prime_leaf_nodes == [
        {
            "id": "depth_2_prime_leaf",
            "role": "prime_leaf",
            "value": 617,
            "shape_signature": None,
            "shape_family_class": None,
            "pet_grip_status": None,
            "route_policy": None,
            "route_status": None,
            "terminal_status": "classic-verified",
            "metadata": {
                "depth": 2,
                "verification_status": "classic-verified",
            },
        }
    ]

    assert {
        "source": "depth_2_input",
        "target": "depth_2_prime_leaf",
        "edge_kind": "terminal_prime_leaf",
        "move": "VERIFY",
        "verification_status": "classic-verified",
        "reason": "terminal prime leaf verified by leaf-primality-route",
    } in tree["edges"]
