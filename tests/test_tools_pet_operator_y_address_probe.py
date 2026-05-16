from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def test_inc_selects_pet_exponent_target() -> None:
    from tools.research.pet_operator_y_address_probe import build_payload

    payload = build_payload(60, [2], "INC")
    target = payload["target_resolution"]
    operation = payload["operation"]

    assert payload["schema"] == "pet.operator_y_address_probe.v0"
    assert target["valid"] is True
    assert target["address"] == [2]
    assert target["depth"] == 1
    assert target["selected_root"] == 2
    assert target["selected_exponent_kind"] == "pet"
    assert target["selected_exponent_object"] == [{"p": 2, "e": None}]
    assert target["parent_baseline"] == [2, 3, 5]
    assert target["baseline_index_path"] == [0]
    assert operation == {
        "op": "INC",
        "valid": True,
        "reason": None,
        "selected_root": 2,
        "selected_exponent_kind": "pet",
    }


def test_inc_selects_leaf_exponent_target() -> None:
    from tools.research.pet_operator_y_address_probe import build_payload

    payload = build_payload(60, [3], "INC")
    target = payload["target_resolution"]
    operation = payload["operation"]

    assert target["valid"] is True
    assert target["selected_root"] == 3
    assert target["selected_exponent_kind"] == "leaf"
    assert target["selected_exponent_object"] is None
    assert target["parent_baseline"] == [2, 3, 5]
    assert target["baseline_index_path"] == [1]
    assert operation["valid"] is True
    assert operation["op"] == "INC"


def test_inc_selects_recursive_leaf_target() -> None:
    from tools.research.pet_operator_y_address_probe import build_payload

    payload = build_payload(60, [2, 2], "INC")
    target = payload["target_resolution"]
    operation = payload["operation"]

    assert target["valid"] is True
    assert target["address"] == [2, 2]
    assert target["depth"] == 2
    assert target["selected_root"] == 2
    assert target["selected_exponent_kind"] == "leaf"
    assert target["parent_baseline"] == [2]
    assert target["baseline_index_path"] == [0, 0]
    assert operation["valid"] is True
    assert operation["selected_root"] == 2
    assert operation["selected_exponent_kind"] == "leaf"


def test_dec_accepts_pet_exponent_target() -> None:
    from tools.research.pet_operator_y_address_probe import build_payload

    payload = build_payload(60, [2], "DEC")
    target = payload["target_resolution"]
    operation = payload["operation"]

    assert target["valid"] is True
    assert target["selected_root"] == 2
    assert target["selected_exponent_kind"] == "pet"
    assert operation == {
        "op": "DEC",
        "valid": True,
        "reason": None,
        "selected_root": 2,
        "selected_exponent_kind": "pet",
    }


def test_dec_rejects_leaf_exponent_target() -> None:
    from tools.research.pet_operator_y_address_probe import build_payload

    payload = build_payload(60, [3], "DEC")
    target = payload["target_resolution"]
    operation = payload["operation"]

    assert target["valid"] is True
    assert target["selected_root"] == 3
    assert target["selected_exponent_kind"] == "leaf"
    assert operation["valid"] is False
    assert operation["reason"] == "selected-exponent-has-no-defined-predecessor"


def test_dec_rejects_recursive_leaf_exponent_target() -> None:
    from tools.research.pet_operator_y_address_probe import build_payload

    payload = build_payload(60, [2, 2], "DEC")
    target = payload["target_resolution"]
    operation = payload["operation"]

    assert target["valid"] is True
    assert target["selected_root"] == 2
    assert target["selected_exponent_kind"] == "leaf"
    assert target["parent_baseline"] == [2]
    assert target["baseline_index_path"] == [0, 0]
    assert operation["valid"] is False
    assert operation["reason"] == "selected-exponent-has-no-defined-predecessor"


def test_empty_address_does_not_select_y_target() -> None:
    from tools.research.pet_operator_y_address_probe import build_payload

    payload = build_payload(60, [], "INC")
    target = payload["target_resolution"]
    operation = payload["operation"]

    assert target["valid"] is False
    assert target["address"] == []
    assert target["reason"] == "empty-address-does-not-select-root"
    assert target["parent_baseline"] == [2, 3, 5]
    assert operation["valid"] is False
    assert operation["reason"] == "invalid-address"
    assert operation["target_reason"] == "empty-address-does-not-select-root"


def test_missing_root_is_invalid() -> None:
    from tools.research.pet_operator_y_address_probe import build_payload

    payload = build_payload(60, [7], "INC")
    target = payload["target_resolution"]
    operation = payload["operation"]

    assert target["valid"] is False
    assert target["reason"] == "root-not-in-current-baseline"
    assert target["missing_root"] == 7
    assert target["parent_baseline"] == [2, 3, 5]
    assert operation["valid"] is False
    assert operation["reason"] == "invalid-address"
    assert operation["target_reason"] == "root-not-in-current-baseline"


def test_cannot_descend_through_leaf_exponent() -> None:
    from tools.research.pet_operator_y_address_probe import build_payload

    payload = build_payload(60, [3, 2], "INC")
    target = payload["target_resolution"]
    operation = payload["operation"]

    assert target["valid"] is False
    assert target["reason"] == "selected-root-has-leaf-exponent"
    assert target["blocked_root"] == 3
    assert target["selected_root"] == 3
    assert target["selected_exponent_kind"] == "leaf"
    assert target["baseline_index_path"] == [1]
    assert operation["valid"] is False
    assert operation["target_reason"] == "selected-root-has-leaf-exponent"


def test_y_address_probe_json_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_y_address_probe.py",
            "60",
            "DEC",
            "--address",
            "[2]",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    assert payload["schema"] == "pet.operator_y_address_probe.v0"
    assert payload["n"] == 60
    assert payload["target_resolution"]["valid"] is True
    assert payload["target_resolution"]["address"] == [2]
    assert payload["target_resolution"]["selected_exponent_kind"] == "pet"
    assert payload["operation"]["valid"] is True
    assert payload["operation"]["op"] == "DEC"


def test_y_address_probe_text_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_y_address_probe.py",
            "60",
            "DEC",
            "--address",
            "[3]",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    out = result.stdout

    assert "schema = pet.operator_y_address_probe.v0" in out
    assert "op = DEC" in out
    assert "address = [3]" in out
    assert "target_valid = true" in out
    assert "selected_exponent_kind = leaf" in out
    assert "operation_valid = false" in out
    assert "operation_reason = selected-exponent-has-no-defined-predecessor" in out
