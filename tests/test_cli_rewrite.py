#!/usr/bin/env python3
import json
import subprocess
import sys


def _run_json(*args):
    result = subprocess.run(
        [sys.executable, "-m", "pet.cli", *args, "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_cli_rewrite_pair_json_contract():
    data = _run_json("rewrite", "pair", "12", "9", "--overscan", "120")

    assert set(data.keys()) == {"src", "dst", "reachable", "cost", "path"}
    assert data["src"] == 12
    assert data["dst"] == 9
    assert data["reachable"] is True
    assert data["cost"] == 3
    assert data["path"] == [
        {"src": 12, "dst": 6, "label": "DEC(p=2,e=2)"},
        {"src": 6, "dst": 3, "label": "DROP(p=2)"},
        {"src": 3, "dst": 9, "label": "INC(p=3,e=1)"},
    ]


def test_cli_rewrite_scan_json_contract():
    data = _run_json(
        "rewrite",
        "scan",
        "--n-max",
        "10",
        "--overscan",
        "40",
        "--limit",
        "3",
    )

    expected_keys = {
        "n_max",
        "overscan",
        "stats",
        "surprises",
        "top_hubs",
        "top_asymmetries",
        "top_attractors",
        "family_report",
        "one_step_return_costs",
    }

    assert set(data.keys()) == expected_keys
    assert data["n_max"] == 10
    assert data["overscan"] == 40

    stats = data["stats"]
    assert stats["overscan"] == 40
    assert stats["node_count"] == 40
    assert stats["out_of_domain_edges_seen_after_filter"] == 0
    assert "label_counts" in stats

    assert set(data["surprises"].keys()) == {
        "largest_positive_gap",
        "largest_negative_gap",
        "sample_unreachable",
    }
    assert len(data["top_hubs"]) <= 3
    assert len(data["top_asymmetries"]) <= 3
    assert len(data["top_attractors"]) <= 3

    assert {"by_label", "by_prime", "hardest_returns"} <= set(
        data["one_step_return_costs"].keys()
    )


def test_cli_rewrite_matrix_json_contract():
    data = _run_json(
        "rewrite",
        "matrix",
        "--n-max",
        "5",
        "--overscan",
        "30",
    )

    assert set(data.keys()) == {"n_max", "overscan", "stats", "distances"}
    assert data["n_max"] == 5
    assert data["overscan"] == 30

    assert data["stats"]["overscan"] == 30
    assert data["stats"]["node_count"] == 30
    assert len(data["distances"]) == 25

    first = data["distances"][0]
    assert set(first.keys()) == {
        "src",
        "dst",
        "reachable",
        "pet_distance",
        "numeric_distance",
        "distance_gap",
    }
    assert first == {
        "src": 1,
        "dst": 1,
        "reachable": True,
        "pet_distance": 0,
        "numeric_distance": 0,
        "distance_gap": 0,
    }


def test_cli_rewrite_pair_explain_output():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "rewrite",
            "pair",
            "12",
            "9",
            "--overscan",
            "120",
            "--explain",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    out = result.stdout
    assert "12 --DEC(p=2,e=2)--> 6" in out
    assert "meaning: decrease the exponent structure at p=2,e=2" in out
    assert "6 --DROP(p=2)--> 3" in out
    assert "meaning: remove p=2 from the support" in out
    assert "3 --INC(p=3,e=1)--> 9" in out
    assert "meaning: increase the exponent structure at p=3,e=1" in out


def test_cli_rewrite_explain_uses_complete_branch_inc_edges():
    data = _run_json("rewrite", "explain", "30", "90", "--overscan", "200")

    assert data["reachable"] is True
    assert data["cost"] == 1
    assert data["path"] == [
        {"src": 30, "dst": 90, "label": "INC(p=3,e=1)"},
    ]
    assert data["structural_delta"] == {
        "removed_primes": [],
        "introduced_primes": [],
        "strengthened_branches": ["p=3,e=1"],
        "weakened_branches": [],
    }


def test_cli_rewrite_explain_target_aware_optimizes_missing_support_prime():
    data = _run_json(
        "rewrite",
        "explain",
        "2",
        "10",
        "--overscan",
        "120",
        "--target-aware",
    )

    assert data["mode"] == "target-aware"
    assert data["canonical_reachable"] is True
    assert data["canonical_cost"] == 3
    assert data["target_aware_reachable"] is True
    assert data["target_aware_cost"] == 1
    assert data["optimization_gap"] == 2
    assert data["target_used"] is True
    assert data["factorization_used"] is True
    assert data["path"] == [
        {"src": 2, "dst": 10, "label": "NEW_TARGET(p=5)"},
    ]
    assert data["structural_delta"] == {
        "removed_primes": [],
        "introduced_primes": ["5"],
        "strengthened_branches": [],
        "weakened_branches": [],
    }


def test_cli_rewrite_explain_target_aware_handles_canonical_unreachable():
    data = _run_json(
        "rewrite",
        "explain",
        "2",
        "14",
        "--overscan",
        "200",
        "--target-aware",
    )

    assert data["mode"] == "target-aware"
    assert data["canonical_reachable"] is False
    assert data["canonical_cost"] is None
    assert data["target_aware_reachable"] is True
    assert data["target_aware_cost"] == 1
    assert data["optimization_gap"] is None
    assert data["path"] == [
        {"src": 2, "dst": 14, "label": "NEW_TARGET(p=7)"},
    ]
    assert data["structural_delta"]["introduced_primes"] == ["7"]


def test_cli_rewrite_explain_target_aware_keeps_unit_exponent_steps():
    data = _run_json(
        "rewrite",
        "explain",
        "2",
        "16",
        "--overscan",
        "200",
        "--target-aware",
    )

    assert data["mode"] == "target-aware"
    assert data["canonical_cost"] == 3
    assert data["target_aware_cost"] == 3
    assert data["optimization_gap"] == 0
    assert data["path"] == [
        {"src": 2, "dst": 4, "label": "INC(p=2,e=1)"},
        {"src": 4, "dst": 8, "label": "INC(p=2,e=2)"},
        {"src": 8, "dst": 16, "label": "INC(p=2,e=3)"},
    ]
    assert data["structural_delta"] == {
        "removed_primes": [],
        "introduced_primes": [],
        "strengthened_branches": ["p=2,e=1", "p=2,e=2", "p=2,e=3"],
        "weakened_branches": [],
    }


def test_cli_rewrite_explain_target_aware_human_output():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "rewrite",
            "explain",
            "2",
            "10",
            "--overscan",
            "120",
            "--target-aware",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    out = result.stdout
    assert "mode = target-aware" in out
    assert "canonical_cost = 3" in out
    assert "target_aware_cost = 1" in out
    assert "optimization_gap = 2" in out
    assert "introduced_primes = ['5']" in out
    assert "1. NEW_TARGET(p=5): 2 -> 10" in out
    assert "meaning: introduce target prime 5 into the support" in out


def test_cli_rewrite_explain_human_output():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "rewrite",
            "explain",
            "12",
            "9",
            "--overscan",
            "120",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    out = result.stdout
    assert "source = 12" in out
    assert "target = 9" in out
    assert "cost = 3" in out
    assert "structural_delta:" in out
    assert "removed_primes = ['p=2']" in out
    assert "introduced_primes = []" in out
    assert "strengthened_branches = ['p=3,e=1']" in out
    assert "weakened_branches = ['p=2,e=2']" in out
    assert "1. DEC(p=2,e=2): 12 -> 6" in out
    assert "meaning: decrease the exponent structure at p=2,e=2" in out
    assert "2. DROP(p=2): 6 -> 3" in out
    assert "meaning: remove p=2 from the support" in out
    assert "3. INC(p=3,e=1): 3 -> 9" in out
    assert "meaning: increase the exponent structure at p=3,e=1" in out


def test_cli_rewrite_explain_json_contract():
    data = _run_json("rewrite", "explain", "12", "9", "--overscan", "120")

    assert set(data.keys()) == {
        "src",
        "dst",
        "reachable",
        "cost",
        "path",
        "explanations",
        "structural_delta",
    }

    assert data["src"] == 12
    assert data["dst"] == 9
    assert data["reachable"] is True
    assert data["cost"] == 3
    assert data["structural_delta"] == {
        "removed_primes": ["p=2"],
        "introduced_primes": [],
        "strengthened_branches": ["p=3,e=1"],
        "weakened_branches": ["p=2,e=2"],
    }

    assert data["explanations"] == [
        {
            "src": 12,
            "dst": 6,
            "label": "DEC(p=2,e=2)",
            "meaning": "decrease the exponent structure at p=2,e=2",
        },
        {
            "src": 6,
            "dst": 3,
            "label": "DROP(p=2)",
            "meaning": "remove p=2 from the support",
        },
        {
            "src": 3,
            "dst": 9,
            "label": "INC(p=3,e=1)",
            "meaning": "increase the exponent structure at p=3,e=1",
        },
    ]


def test_cli_rewrite_friction_human_output():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "rewrite",
            "friction",
            "--n-max",
            "10",
            "--overscan",
            "40",
            "--limit",
            "3",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    out = result.stdout
    assert "n_max = 10" in out
    assert "overscan = 40" in out
    assert "by_label:" in out
    assert "NEW(x3): count=1 min=1 max=1 avg=1.0" in out
    assert "by_prime:" in out
    assert "p=3: count=4 min=1 max=1 avg=1.0" in out
    assert "hardest_returns:" in out
    assert "10 --DROP(p=5)--> 2: return_cost=3" in out


def test_cli_rewrite_friction_json_contract():
    data = _run_json(
        "rewrite",
        "friction",
        "--n-max",
        "10",
        "--overscan",
        "40",
        "--limit",
        "3",
    )

    assert set(data.keys()) == {"n_max", "overscan", "one_step_return_costs"}
    assert data["n_max"] == 10
    assert data["overscan"] == 40

    costs = data["one_step_return_costs"]
    assert set(costs.keys()) == {"hardest_returns", "by_label", "by_prime"}

    by_label = {row["label"]: row for row in costs["by_label"]}
    assert by_label["NEW(x3)"] == {
        "label": "NEW(x3)",
        "count": 1,
        "min_back_cost": 1,
        "max_back_cost": 1,
        "avg_back_cost": 1.0,
    }

    by_prime = {row["prime"]: row for row in costs["by_prime"]}
    assert by_prime[3] == {
        "prime": 3,
        "count": 4,
        "min_back_cost": 1,
        "max_back_cost": 1,
        "avg_back_cost": 1.0,
    }

    hardest = costs["hardest_returns"][0]
    assert hardest["src"] == 10
    assert hardest["dst"] == 2
    assert hardest["forward_label"] == "DROP(p=5)"
    assert hardest["back_cost"] == 3
