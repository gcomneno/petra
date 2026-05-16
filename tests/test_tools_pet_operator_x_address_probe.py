from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def test_new_on_top_level_support_is_valid() -> None:
    from tools.research.pet_operator_x_address_probe import build_payload

    payload = build_payload(60, [], "NEW", 7)
    parent = payload["parent_resolution"]
    operation = payload["operation"]

    assert payload["schema"] == "pet.operator_x_address_probe.v0"
    assert parent["valid"] is True
    assert parent["parent_address"] == []
    assert parent["target_baseline"] == [2, 3, 5]
    assert operation == {
        "op": "NEW",
        "valid": True,
        "q": 7,
        "reason": None,
        "target_baseline": [2, 3, 5],
    }


def test_new_on_recursive_parent_support_is_valid() -> None:
    from tools.research.pet_operator_x_address_probe import build_payload

    payload = build_payload(60, [2], "NEW", 7)
    parent = payload["parent_resolution"]
    operation = payload["operation"]

    assert parent["valid"] is True
    assert parent["parent_address"] == [2]
    assert parent["target_baseline"] == [2]
    assert parent["baseline_index_path"] == [0]
    assert operation["valid"] is True
    assert operation["q"] == 7
    assert operation["target_baseline"] == [2]


def test_new_rejects_existing_root_in_target_baseline() -> None:
    from tools.research.pet_operator_x_address_probe import build_payload

    payload = build_payload(60, [], "NEW", 3)
    operation = payload["operation"]

    assert operation["valid"] is False
    assert operation["reason"] == "q-already-in-target-baseline"
    assert operation["target_baseline"] == [2, 3, 5]


def test_drop_on_top_level_support_is_valid() -> None:
    from tools.research.pet_operator_x_address_probe import build_payload

    payload = build_payload(60, [], "DROP", 3)
    parent = payload["parent_resolution"]
    operation = payload["operation"]

    assert parent["valid"] is True
    assert parent["target_baseline"] == [2, 3, 5]
    assert operation == {
        "op": "DROP",
        "valid": True,
        "p": 3,
        "reason": None,
        "target_baseline": [2, 3, 5],
    }


def test_drop_rejects_missing_root_in_target_baseline() -> None:
    from tools.research.pet_operator_x_address_probe import build_payload

    payload = build_payload(60, [], "DROP", 7)
    operation = payload["operation"]

    assert operation["valid"] is False
    assert operation["reason"] == "p-not-in-target-baseline"
    assert operation["target_baseline"] == [2, 3, 5]


def test_drop_rejects_empty_pet_result() -> None:
    from tools.research.pet_operator_x_address_probe import build_payload

    payload = build_payload(60, [2], "DROP", 2)
    parent = payload["parent_resolution"]
    operation = payload["operation"]

    assert parent["valid"] is True
    assert parent["target_baseline"] == [2]
    assert operation["valid"] is False
    assert operation["reason"] == "drop-would-create-empty-pet"


def test_invalid_parent_address_blocks_operation() -> None:
    from tools.research.pet_operator_x_address_probe import build_payload

    payload = build_payload(60, [3], "NEW", 7)
    parent = payload["parent_resolution"]
    operation = payload["operation"]

    assert parent["valid"] is False
    assert parent["reason"] == "parent-address-selects-leaf-exponent"
    assert parent["blocked_root"] == 3
    assert operation["valid"] is False
    assert operation["reason"] == "invalid-parent-address"
    assert operation["parent_reason"] == "parent-address-selects-leaf-exponent"


def test_non_prime_new_root_is_invalid() -> None:
    from tools.research.pet_operator_x_address_probe import build_payload

    payload = build_payload(60, [], "NEW", 9)
    operation = payload["operation"]

    assert operation["valid"] is False
    assert operation["reason"] == "q-is-not-prime"


def test_non_prime_drop_root_is_invalid() -> None:
    from tools.research.pet_operator_x_address_probe import build_payload

    payload = build_payload(60, [], "DROP", 9)
    operation = payload["operation"]

    assert operation["valid"] is False
    assert operation["reason"] == "p-is-not-prime"


def test_x_address_probe_json_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_x_address_probe.py",
            "60",
            "NEW",
            "7",
            "--parent-address",
            "[2]",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    assert payload["schema"] == "pet.operator_x_address_probe.v0"
    assert payload["parent_resolution"]["valid"] is True
    assert payload["parent_resolution"]["parent_address"] == [2]
    assert payload["parent_resolution"]["target_baseline"] == [2]
    assert payload["operation"]["valid"] is True
    assert payload["operation"]["op"] == "NEW"
    assert payload["operation"]["q"] == 7


def test_x_address_probe_text_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_x_address_probe.py",
            "60",
            "DROP",
            "2",
            "--parent-address",
            "[2]",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    out = result.stdout

    assert "schema = pet.operator_x_address_probe.v0" in out
    assert "op = DROP" in out
    assert "parent_address = [2]" in out
    assert "parent_valid = true" in out
    assert "target_baseline = [2]" in out
    assert "operation_valid = false" in out
    assert "operation_reason = drop-would-create-empty-pet" in out
