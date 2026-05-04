from __future__ import annotations

import json
import subprocess
import sys


def run_tool(*args: str) -> str:
    result = subprocess.run(
        [sys.executable, "tools/research/pet_composite_probe.py", *args],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def test_composite_probe_reports_pet_unit_and_self_unmerge() -> None:
    output = run_tool("55")

    assert "PET COMPOSITE PROBE" in output
    assert "N = 55" in output
    assert "n_generator = 6" in output
    assert "n_signature = [[], []]" in output
    assert "pet_unit = 1" in output
    assert "pet_unit_signature = []" in output
    assert "unit_merge_left = 6" in output
    assert "unit_merge_right = 6" in output
    assert "self_unmerge_available = yes" in output
    assert "self_unmerge_result = 1" in output
    assert "self_unmerge_signature = []" in output
    assert "flat_generator = yes" in output
    assert "flat_leaf_count = 2" in output
    assert "claim = PET composite probe only; this does not factor N" in output


def test_composite_probe_compares_canonical_generators() -> None:
    output = run_tool("30030", "--other", "55")

    assert "Composite comparison" in output
    assert "left_n = 30030" in output
    assert "right_n = 55" in output
    assert "left_generator = 30030" in output
    assert "right_generator = 6" in output

    assert "PET-MERGE" in output
    assert "merge_result = 180180" in output
    assert "merge_result_generator = 180180" in output
    assert "merge_result_signature = [[], [], [], [], [[]], [[]]]" in output

    assert "PET-UNMERGE" in output
    assert "unmerge_available = yes" in output
    assert "unmerge_result = 5005" in output
    assert "unmerge_result_generator = 210" in output
    assert "unmerge_result_signature = [[], [], [], []]" in output


def test_composite_probe_json_output() -> None:
    output = run_tool("30030", "--other", "55", "--json")
    payload = json.loads(output)

    assert payload["self_probe"]["n"] == 30030
    assert payload["self_probe"]["n_generator"] == 30030
    assert payload["self_probe"]["pet_unit"] == 1
    assert payload["self_probe"]["self_unmerge_result"] == 1

    comparison = payload["comparison"]
    assert comparison["left_generator"] == 30030
    assert comparison["right_generator"] == 6
    assert comparison["merge_result"] == 180180
    assert comparison["merge_result_signature"] == [[], [], [], [], [[]], [[]]]
    assert comparison["unmerge_available"] is True
    assert comparison["unmerge_result"] == 5005
    assert comparison["unmerge_result_generator"] == 210
    assert comparison["unmerge_result_signature"] == [[], [], [], []]
