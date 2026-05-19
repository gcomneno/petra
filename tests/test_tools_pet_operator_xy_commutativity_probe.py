from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def test_xy_distinct_top_level_targets_commute() -> None:
    from tools.research.pet_operator_xy_commutativity_probe import build_payload

    payload = build_payload(60, [], "NEW", 7, [3], "INC")

    assert payload["schema"] == "pet.operator_xy_commutativity_probe.v0"
    assert payload["relation"] == "commutes"
    assert payload["left"]["valid"] is True
    assert payload["right"]["valid"] is True
    assert payload["left"]["final_value"] == 1260
    assert payload["right"]["final_value"] == 1260


def test_xy_new_can_create_y_target_asymmetrically() -> None:
    from tools.research.pet_operator_xy_commutativity_probe import build_payload

    payload = build_payload(60, [], "NEW", 7, [7], "INC")

    assert payload["relation"] == "support-created-y-target"
    assert payload["left"]["valid"] is True
    assert payload["left"]["final_value"] == 2940
    assert payload["right"]["valid"] is False
    assert payload["right"]["invalid_axis"] == "Y"
    assert payload["right"]["invalid_reason"] == "invalid-address"


def test_xy_drop_can_remove_y_target_asymmetrically() -> None:
    from tools.research.pet_operator_xy_commutativity_probe import build_payload

    payload = build_payload(60, [], "DROP", 2, [2], "INC")

    assert payload["relation"] == "support-removed-y-target"
    assert payload["left"]["valid"] is False
    assert payload["left"]["invalid_axis"] == "Y"
    assert payload["left"]["invalid_reason"] == "invalid-address"
    assert payload["right"]["valid"] is True
    assert payload["right"]["final_value"] == 15


def test_xy_recursive_x_parent_and_y_same_outer_root_do_not_commute() -> None:
    from tools.research.pet_operator_xy_commutativity_probe import build_payload

    payload = build_payload(60, [2], "NEW", 5, [2], "INC")

    assert payload["relation"] == "non-commutes"
    assert payload["left"]["valid"] is True
    assert payload["right"]["valid"] is True
    assert payload["left"]["final_value"] == 30720
    assert payload["right"]["final_value"] == 491520


def test_xy_both_orderings_can_be_invalid() -> None:
    from tools.research.pet_operator_xy_commutativity_probe import build_payload

    payload = build_payload(60, [], "DROP", 2, [3], "DEC")

    assert payload["relation"] == "both-invalid"
    assert payload["left"]["valid"] is False
    assert payload["right"]["valid"] is False
    assert payload["left"]["invalid_axis"] == "Y"
    assert payload["right"]["invalid_axis"] == "Y"


def test_xy_commutativity_probe_json_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_xy_commutativity_probe.py",
            "60",
            "--x-op",
            "NEW",
            "--x-root",
            "5",
            "--x-parent-address",
            "[2]",
            "--y-op",
            "INC",
            "--y-address",
            "[2]",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    assert payload["schema"] == "pet.operator_xy_commutativity_probe.v0"
    assert payload["relation"] == "non-commutes"
    assert payload["left_order"] == "X_THEN_Y"
    assert payload["right_order"] == "Y_THEN_X"
    assert payload["left"]["final_value"] == 30720
    assert payload["right"]["final_value"] == 491520


def test_xy_commutativity_probe_text_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_xy_commutativity_probe.py",
            "60",
            "--x-op",
            "DROP",
            "--x-root",
            "2",
            "--y-op",
            "INC",
            "--y-address",
            "[2]",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    out = result.stdout

    assert "schema = pet.operator_xy_commutativity_probe.v0" in out
    assert "left_order = X_THEN_Y" in out
    assert "left_valid = false" in out
    assert "right_order = Y_THEN_X" in out
    assert "right_valid = true" in out
    assert "relation = support-removed-y-target" in out
