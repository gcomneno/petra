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
