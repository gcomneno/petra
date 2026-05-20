from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def test_address_stays_stable_when_unrelated_support_is_added() -> None:
    from tools.research.pet_operator_address_stability_probe import build_payload

    payload = build_payload(60, [3], "NEW", root=7)

    assert payload["schema"] == "pet.operator_address_stability_probe.v0"
    assert payload["stability"] == "stable"
    assert payload["before"]["valid"] is True
    assert payload["after"]["valid"] is True
    assert payload["operator"]["mutated_value"] == 420


def test_address_can_be_created_by_new_support_root() -> None:
    from tools.research.pet_operator_address_stability_probe import build_payload

    payload = build_payload(60, [7], "NEW", root=7)

    assert payload["stability"] == "created"
    assert payload["before"]["valid"] is False
    assert payload["before"]["reason"] == "root-not-in-current-baseline"
    assert payload["after"]["valid"] is True
    assert payload["operator"]["mutated_value"] == 420


def test_address_can_be_destroyed_by_drop_support_root() -> None:
    from tools.research.pet_operator_address_stability_probe import build_payload

    payload = build_payload(60, [2], "DROP", root=2)

    assert payload["stability"] == "destroyed"
    assert payload["before"]["valid"] is True
    assert payload["after"]["valid"] is False
    assert payload["after"]["reason"] == "root-not-in-current-baseline"
    assert payload["operator"]["mutated_value"] == 15


def test_address_can_survive_while_target_changes() -> None:
    from tools.research.pet_operator_address_stability_probe import build_payload

    payload = build_payload(60, [2], "INC", operator_address=[2])

    assert payload["stability"] == "retargeted"
    assert payload["before"]["valid"] is True
    assert payload["after"]["valid"] is True
    assert payload["before"]["selected_exponent_kind"] == "pet"
    assert payload["after"]["selected_exponent_kind"] == "pet"
    assert payload["operator"]["mutated_value"] == 120


def test_recursive_address_can_become_leaf_blocked() -> None:
    from tools.research.pet_operator_address_stability_probe import build_payload

    payload = build_payload(60, [2, 2], "DEC", operator_address=[2])

    assert payload["stability"] == "leaf-blocked"
    assert payload["before"]["valid"] is True
    assert payload["after"]["valid"] is False
    assert payload["after"]["reason"] == "selected-root-has-leaf-exponent"
    assert payload["operator"]["mutated_value"] == 30


def test_invalid_operator_blocks_after_resolution() -> None:
    from tools.research.pet_operator_address_stability_probe import build_payload

    payload = build_payload(60, [3], "DROP", root=7)

    assert payload["stability"] == "operator-invalid"
    assert payload["operator"]["valid"] is False
    assert payload["operator"]["reason"] == "p-not-in-target-baseline"
    assert payload["before"]["valid"] is True
    assert payload["after"] is None


def test_still_invalid_address_remains_invalid_after_unrelated_operation() -> None:
    from tools.research.pet_operator_address_stability_probe import build_payload

    payload = build_payload(60, [11], "NEW", root=7)

    assert payload["stability"] == "still-invalid"
    assert payload["before"]["valid"] is False
    assert payload["after"]["valid"] is False
    assert payload["before"]["reason"] == "root-not-in-current-baseline"
    assert payload["after"]["reason"] == "root-not-in-current-baseline"


def test_address_stability_probe_json_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_address_stability_probe.py",
            "60",
            "--tracked-address",
            "[2]",
            "--op",
            "INC",
            "--operator-address",
            "[2]",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    assert payload["schema"] == "pet.operator_address_stability_probe.v0"
    assert payload["tracked_address"] == [2]
    assert payload["operator"]["op"] == "INC"
    assert payload["operator"]["mutated_value"] == 120
    assert payload["stability"] == "retargeted"


def test_address_stability_probe_text_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_address_stability_probe.py",
            "60",
            "--tracked-address",
            "[2,2]",
            "--op",
            "DEC",
            "--operator-address",
            "[2]",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    out = result.stdout

    assert "schema = pet.operator_address_stability_probe.v0" in out
    assert "tracked_address = [2, 2]" in out
    assert "op = DEC" in out
    assert "operator_valid = true" in out
    assert "after_reason = selected-root-has-leaf-exponent" in out
    assert "stability = leaf-blocked" in out
