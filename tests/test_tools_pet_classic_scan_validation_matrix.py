from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


CASES_PATH = Path("tests/fixtures/pet_classic_scan_validation_cases.json")


def run_json_tool(args: list[str]) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, *args, "--json"],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def load_cases() -> list[dict[str, Any]]:
    return json.loads(CASES_PATH.read_text())


def test_classic_scan_validation_matrix_expected_divisors_and_policy() -> None:
    for case in load_cases():
        n = case["n"]

        summary = run_json_tool(["tools/pet_classic_scan_summary.py", str(n)])
        actual_divisors = [
            record["divisor"]
            for record in summary["verified_divisors"]
        ]
        actual_role_hints = {
            str(record["divisor"]): record["role_hint"]
            for record in summary["verified_divisors"]
        }

        assert actual_divisors == case["expected_verified_divisors"], case["label"]
        assert actual_role_hints == case["expected_role_hints"], case["label"]

        policy = run_json_tool(["tools/pet_classic_scan_policy.py", str(n)])
        expected_policy = case["expected_policy"]

        assert policy["baseline_sources"] == expected_policy["baseline_sources"], case["label"]
        assert policy["recommended_sources"] == expected_policy["recommended_sources"], case["label"]
        assert policy["caution_sources"] == expected_policy["caution_sources"], case["label"]
        assert policy["unavailable_sources"] == expected_policy["unavailable_sources"], case["label"]
        assert policy["decision"] == case["expected_decision"], case["label"]

        limitation = case.get("limitation", "")
        assert limitation, case["label"]
        assert any(
            marker in limitation
            for marker in [
                "exhaustive-like",
                "baseline",
                "unavailable",
                "diagnostic",
            ]
        ), case["label"]

        limitation = case.get("limitation", "")
        assert limitation, case["label"]
        assert any(
            marker in limitation
            for marker in [
                "exhaustive-like",
                "baseline",
                "unavailable",
                "diagnostic",
            ]
        ), case["label"]
