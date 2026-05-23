from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def test_operator_semantics_report_for_60_has_expected_shape() -> None:
    from tools.research.pet_operator_semantics_report import build_payload

    payload = build_payload(60)

    assert payload["schema"] == "pet.operator_semantics_report.v0"
    assert payload["n"] == 60
    assert payload["top_level_baseline"] == [2, 3, 5]
    assert payload["axis_invariants"]["summary"] == {
        "checked": 6,
        "passed": 6,
        "failed": 0,
        "failed_cases": [],
    }

    assert [row["address"] for row in payload["sample_addresses"]] == [
        [],
        [2],
        [3],
        [5],
        [2, 2],
    ]

    assert "experimental documented tooling" in payload["boundaries"]
    assert "no stable CLI behavior change" in payload["boundaries"]
    assert "no PEG algebra completeness claim" in payload["boundaries"]


def test_operator_semantics_report_for_60_x_axis_samples() -> None:
    from tools.research.pet_operator_semantics_report import build_payload

    payload = build_payload(60)
    samples = {row["label"]: row for row in payload["x_axis_samples"]}

    assert samples["new-top-level-fresh-root"]["op"] == "NEW"
    assert samples["new-top-level-fresh-root"]["valid"] is True
    assert samples["new-top-level-fresh-root"]["target_baseline"] == [2, 3, 5]

    assert samples["drop-top-level-first-root"]["op"] == "DROP"
    assert samples["drop-top-level-first-root"]["valid"] is True
    assert samples["drop-top-level-first-root"]["target_baseline"] == [2, 3, 5]


def test_operator_semantics_report_for_60_y_axis_samples() -> None:
    from tools.research.pet_operator_semantics_report import build_payload

    payload = build_payload(60)
    samples = {row["label"]: row for row in payload["y_axis_samples"]}

    assert samples["inc-first-root-target"]["op"] == "INC"
    assert samples["inc-first-root-target"]["valid"] is True
    assert samples["inc-first-root-target"]["address"] == [2]
    assert samples["inc-first-root-target"]["mutated_value"] == 120

    assert samples["dec-first-root-target"]["op"] == "DEC"
    assert samples["dec-first-root-target"]["valid"] is True
    assert samples["dec-first-root-target"]["address"] == [2]
    assert samples["dec-first-root-target"]["mutated_value"] == 30

    assert samples["inc-leaf-or-first-root-target"]["op"] == "INC"
    assert samples["inc-leaf-or-first-root-target"]["valid"] is True
    assert samples["inc-leaf-or-first-root-target"]["address"] == [3]
    assert samples["inc-leaf-or-first-root-target"]["selected_exponent_kind"] == "leaf"


def test_operator_semantics_report_for_60_xy_samples() -> None:
    from tools.research.pet_operator_semantics_report import build_payload

    payload = build_payload(60)

    assert [row["relation"] for row in payload["xy_composition_samples"]] == [
        "commutes",
        "support-created-y-target",
        "support-removed-y-target",
    ]


def test_operator_semantics_report_for_60_address_stability_samples() -> None:
    from tools.research.pet_operator_semantics_report import build_payload

    payload = build_payload(60)

    assert [row["stability"] for row in payload["address_stability_samples"]] == [
        "stable",
        "created",
        "destroyed",
        "retargeted",
        "leaf-blocked",
    ]


def test_operator_semantics_report_json_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_semantics_report.py",
            "60",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    assert payload["schema"] == "pet.operator_semantics_report.v0"
    assert payload["n"] == 60
    assert payload["top_level_baseline"] == [2, 3, 5]
    assert payload["xy_composition_samples"][1]["relation"] == "support-created-y-target"
    assert payload["address_stability_samples"][4]["stability"] == "leaf-blocked"


def test_operator_semantics_report_text_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_semantics_report.py",
            "60",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    out = result.stdout

    assert "schema = pet.operator_semantics_report.v0" in out
    assert "top_level_baseline = [2, 3, 5]" in out
    assert "axis_invariant_summary = {'checked': 6, 'passed': 6, 'failed': 0, 'failed_cases': []}" in out
    assert "xy_composition_samples:" in out
    assert "relation=support-created-y-target" in out
    assert "address_stability_samples:" in out
    assert "stability=leaf-blocked" in out


def test_operator_semantics_report_declares_experimental_status() -> None:
    from tools.research.pet_operator_semantics_report import build_payload

    payload = build_payload(60)

    assert payload["tooling_status"] == "experimental documented tooling"
    assert payload["stable_cli_contract"] is False
    assert "experimental documented tooling" in payload["boundaries"]
