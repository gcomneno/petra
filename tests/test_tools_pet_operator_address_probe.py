from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def test_empty_address_selects_current_pet_object() -> None:
    from tools.research.pet_operator_address_probe import build_payload

    payload = build_payload(60, [])
    resolution = payload["resolution"]

    assert payload["schema"] == "pet.operator_address_probe.v0"
    assert resolution["valid"] is True
    assert resolution["address"] == []
    assert resolution["depth"] == 0
    assert resolution["selected_root"] is None
    assert resolution["selected_exponent_object"] is None
    assert resolution["selected_exponent_kind"] is None
    assert resolution["baseline_index_path"] == []
    assert resolution["terminal_baseline"] == [2, 3, 5]
    assert resolution["reason"] is None


def test_top_level_address_selects_root_and_exponent_object() -> None:
    from tools.research.pet_operator_address_probe import build_payload

    payload = build_payload(60, [2])
    resolution = payload["resolution"]

    assert resolution["valid"] is True
    assert resolution["depth"] == 1
    assert resolution["selected_root"] == 2
    assert resolution["selected_exponent_kind"] == "pet"
    assert resolution["selected_exponent_object"] == [{"p": 2, "e": None}]
    assert resolution["baseline_index_path"] == [0]
    assert resolution["terminal_baseline"] == [2, 3, 5]
    assert resolution["reason"] is None


def test_recursive_address_enters_selected_exponent_object() -> None:
    from tools.research.pet_operator_address_probe import build_payload

    payload = build_payload(60, [2, 2])
    resolution = payload["resolution"]

    assert resolution["valid"] is True
    assert resolution["depth"] == 2
    assert resolution["selected_root"] == 2
    assert resolution["selected_exponent_kind"] == "leaf"
    assert resolution["selected_exponent_object"] is None
    assert resolution["baseline_index_path"] == [0, 0]
    assert resolution["terminal_baseline"] == [2]
    assert resolution["reason"] is None
    assert resolution["trace"] == [
        {
            "depth": 1,
            "root": 2,
            "baseline": [2, 3, 5],
            "baseline_index": 0,
            "exponent_kind": "pet",
        },
        {
            "depth": 2,
            "root": 2,
            "baseline": [2],
            "baseline_index": 0,
            "exponent_kind": "leaf",
        },
    ]


def test_missing_root_is_invalid() -> None:
    from tools.research.pet_operator_address_probe import build_payload

    payload = build_payload(60, [7])
    resolution = payload["resolution"]

    assert resolution["valid"] is False
    assert resolution["depth"] == 0
    assert resolution["selected_root"] is None
    assert resolution["baseline_index_path"] == []
    assert resolution["terminal_baseline"] == [2, 3, 5]
    assert resolution["reason"] == "root-not-in-current-baseline"
    assert resolution["missing_root"] == 7


def test_cannot_descend_through_leaf_exponent() -> None:
    from tools.research.pet_operator_address_probe import build_payload

    payload = build_payload(60, [3, 2])
    resolution = payload["resolution"]

    assert resolution["valid"] is False
    assert resolution["depth"] == 1
    assert resolution["selected_root"] == 3
    assert resolution["selected_exponent_kind"] == "leaf"
    assert resolution["baseline_index_path"] == [1]
    assert resolution["terminal_baseline"] == [2, 3, 5]
    assert resolution["reason"] == "selected-root-has-leaf-exponent"
    assert resolution["blocked_root"] == 3


def test_address_probe_json_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_address_probe.py",
            "60",
            "--address",
            "[2,2]",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    resolution = payload["resolution"]

    assert payload["schema"] == "pet.operator_address_probe.v0"
    assert payload["n"] == 60
    assert resolution["valid"] is True
    assert resolution["address"] == [2, 2]
    assert resolution["baseline_index_path"] == [0, 0]


def test_address_probe_text_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_address_probe.py",
            "60",
            "--address",
            "[7]",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    out = result.stdout

    assert "schema = pet.operator_address_probe.v0" in out
    assert "address = [7]" in out
    assert "valid = false" in out
    assert "baseline_index_path = []" in out
    assert "reason = root-not-in-current-baseline" in out
