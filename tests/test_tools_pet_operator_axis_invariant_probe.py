from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def test_operator_axis_probe_default_cases_pass() -> None:
    from tools.research.pet_operator_axis_invariant_probe import build_payload

    payload = build_payload()

    assert payload["schema"] == "pet.operator_axis_invariant_probe.v0"
    assert payload["summary"] == {
        "checked": 6,
        "passed": 6,
        "failed": 0,
        "failed_cases": [],
    }

    rows = {row["case"]: row for row in payload["rows"]}

    assert rows["new-expands-root-support"]["axis"] == "X"
    assert rows["new-expands-root-support"]["support_delta"] == 1
    assert rows["new-expands-root-support"]["invariant_holds"] is True

    assert rows["drop-contracts-root-support"]["axis"] == "X"
    assert rows["drop-contracts-root-support"]["support_delta"] == -1
    assert rows["drop-contracts-root-support"]["invariant_holds"] is True

    assert rows["inc-preserves-root-support"]["axis"] == "Y"
    assert rows["inc-preserves-root-support"]["support_delta"] == 0
    assert rows["inc-preserves-root-support"]["invariant_holds"] is True

    assert rows["dec-preserves-root-support"]["axis"] == "Y"
    assert rows["dec-preserves-root-support"]["support_delta"] == 0
    assert rows["dec-preserves-root-support"]["invariant_holds"] is True

    assert rows["redirect-is-connectivity-only"]["axis"] == "Z"
    assert rows["redirect-is-connectivity-only"]["direct_shape_mutation"] is False
    assert rows["redirect-is-connectivity-only"]["applied_shape_operator"] is False
    assert rows["redirect-is-connectivity-only"]["support_delta"] == 0
    assert rows["redirect-is-connectivity-only"]["invariant_holds"] is True

    assert rows["shadow-select-is-connectivity-only"]["axis"] == "Z"
    assert rows["shadow-select-is-connectivity-only"]["direct_shape_mutation"] is False
    assert rows["shadow-select-is-connectivity-only"]["applied_shape_operator"] is False
    assert rows["shadow-select-is-connectivity-only"]["support_delta"] == 0
    assert rows["shadow-select-is-connectivity-only"]["invariant_holds"] is True


def test_operator_axis_probe_json_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_axis_invariant_probe.py",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    assert payload["schema"] == "pet.operator_axis_invariant_probe.v0"
    assert payload["summary"]["checked"] == 6
    assert payload["summary"]["failed"] == 0
    assert {row["op"] for row in payload["rows"]} == {
        "NEW",
        "DROP",
        "INC",
        "DEC",
        "REDIRECT",
        "SHADOW_SELECT",
    }


def test_operator_axis_probe_text_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_axis_invariant_probe.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    out = result.stdout

    assert "schema = pet.operator_axis_invariant_probe.v0" in out
    assert "case = new-expands-root-support" in out
    assert "op = REDIRECT" in out
    assert "axis = Z" in out
    assert "summary = checked:6 passed:6 failed:0" in out
