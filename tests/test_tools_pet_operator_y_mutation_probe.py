from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def test_inc_leaf_exponent_mutates_value() -> None:
    from tools.research.pet_operator_y_mutation_probe import build_payload

    payload = build_payload(60, [3], "INC")
    operation = payload["operation"]

    assert payload["schema"] == "pet.operator_y_mutation_probe.v0"
    assert payload["original_value"] == 60
    assert operation["valid"] is True
    assert operation["selected_root"] == 3
    assert operation["selected_exponent_kind"] == "leaf"
    assert operation["old_exponent_value"] == 1
    assert operation["new_exponent_value"] == 2
    assert operation["mutated_value"] == 180
    assert operation["reason"] is None


def test_inc_pet_exponent_mutates_value() -> None:
    from tools.research.pet_operator_y_mutation_probe import build_payload

    payload = build_payload(60, [2], "INC")
    operation = payload["operation"]

    assert operation["valid"] is True
    assert operation["selected_root"] == 2
    assert operation["selected_exponent_kind"] == "pet"
    assert operation["old_exponent_value"] == 2
    assert operation["new_exponent_value"] == 3
    assert operation["mutated_value"] == 120


def test_dec_pet_exponent_mutates_value() -> None:
    from tools.research.pet_operator_y_mutation_probe import build_payload

    payload = build_payload(60, [2], "DEC")
    operation = payload["operation"]

    assert operation["valid"] is True
    assert operation["selected_root"] == 2
    assert operation["selected_exponent_kind"] == "pet"
    assert operation["old_exponent_value"] == 2
    assert operation["new_exponent_value"] == 1
    assert operation["mutated_value"] == 30


def test_dec_leaf_exponent_is_invalid() -> None:
    from tools.research.pet_operator_y_mutation_probe import build_payload

    payload = build_payload(60, [3], "DEC")
    operation = payload["operation"]

    assert operation["valid"] is False
    assert operation["selected_root"] == 3
    assert operation["selected_exponent_kind"] == "leaf"
    assert operation["old_exponent_value"] == 1
    assert operation["new_exponent_value"] is None
    assert operation["mutated_pet"] is None
    assert operation["mutated_value"] is None
    assert operation["reason"] == "selected-exponent-has-no-defined-predecessor"


def test_inc_recursive_leaf_exponent_mutates_value() -> None:
    from tools.research.pet_operator_y_mutation_probe import build_payload

    payload = build_payload(60, [2, 2], "INC")
    target = payload["target_resolution"]
    operation = payload["operation"]

    assert target["valid"] is True
    assert target["address"] == [2, 2]
    assert target["parent_baseline"] == [2]
    assert target["baseline_index_path"] == [0, 0]
    assert operation["valid"] is True
    assert operation["selected_root"] == 2
    assert operation["selected_exponent_kind"] == "leaf"
    assert operation["old_exponent_value"] == 1
    assert operation["new_exponent_value"] == 2
    assert operation["mutated_value"] == 240


def test_missing_root_blocks_mutation() -> None:
    from tools.research.pet_operator_y_mutation_probe import build_payload

    payload = build_payload(60, [7], "INC")
    target = payload["target_resolution"]
    operation = payload["operation"]

    assert target["valid"] is False
    assert target["reason"] == "root-not-in-current-baseline"
    assert operation["valid"] is False
    assert operation["reason"] == "invalid-address"
    assert operation["target_reason"] == "root-not-in-current-baseline"
    assert operation["mutated_pet"] is None
    assert operation["mutated_value"] is None


def test_empty_address_blocks_mutation() -> None:
    from tools.research.pet_operator_y_mutation_probe import build_payload

    payload = build_payload(60, [], "INC")
    target = payload["target_resolution"]
    operation = payload["operation"]

    assert target["valid"] is False
    assert target["reason"] == "empty-address-does-not-select-root"
    assert operation["valid"] is False
    assert operation["reason"] == "invalid-address"
    assert operation["target_reason"] == "empty-address-does-not-select-root"


def test_y_mutation_probe_json_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_y_mutation_probe.py",
            "60",
            "INC",
            "--address",
            "[2,2]",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    assert payload["schema"] == "pet.operator_y_mutation_probe.v0"
    assert payload["n"] == 60
    assert payload["original_value"] == 60
    assert payload["target_resolution"]["valid"] is True
    assert payload["target_resolution"]["address"] == [2, 2]
    assert payload["operation"]["valid"] is True
    assert payload["operation"]["op"] == "INC"
    assert payload["operation"]["mutated_value"] == 240


def test_y_mutation_probe_text_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_y_mutation_probe.py",
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

    assert "schema = pet.operator_y_mutation_probe.v0" in out
    assert "op = DEC" in out
    assert "address = [3]" in out
    assert "selected_exponent_kind = leaf" in out
    assert "operation_valid = false" in out
    assert "operation_reason = selected-exponent-has-no-defined-predecessor" in out
    assert "mutated_value = None" in out
