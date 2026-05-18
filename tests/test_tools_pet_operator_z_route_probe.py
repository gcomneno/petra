from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


HISTORY = [
    "NEW(parent_address=[],q=7)",
    "INC(address=[7])",
]


def test_redirect_validates_history_prefix_and_candidate_target() -> None:
    from tools.research.pet_operator_z_route_probe import build_payload

    payload = build_payload(
        op="REDIRECT",
        history=HISTORY,
        prefix=["NEW(parent_address=[],q=7)"],
        candidates=["INC(address=[7])", "INC(address=[7,2])"],
        from_next="INC(address=[7])",
        to_next="INC(address=[7,2])",
    )
    operation = payload["operation"]

    assert payload["schema"] == "pet.operator_z_route_probe.v0"
    assert operation == {
        "op": "REDIRECT",
        "valid": True,
        "reason": None,
        "prefix": ["NEW(parent_address=[],q=7)"],
        "next_index": 1,
        "from_next": "INC(address=[7])",
        "to_next": "INC(address=[7,2])",
        "candidates": ["INC(address=[7])", "INC(address=[7,2])"],
    }


def test_redirect_rejects_invalid_history_prefix() -> None:
    from tools.research.pet_operator_z_route_probe import build_payload

    payload = build_payload(
        op="REDIRECT",
        history=HISTORY,
        prefix=["INC(address=[7])"],
        candidates=["INC(address=[7,2])"],
        from_next="INC(address=[7])",
        to_next="INC(address=[7,2])",
    )
    operation = payload["operation"]

    assert operation["valid"] is False
    assert operation["reason"] == "invalid-history-prefix"
    assert operation["prefix_reason"] == "prefix-does-not-match-history"


def test_redirect_rejects_wrong_from_next() -> None:
    from tools.research.pet_operator_z_route_probe import build_payload

    payload = build_payload(
        op="REDIRECT",
        history=HISTORY,
        prefix=["NEW(parent_address=[],q=7)"],
        candidates=["INC(address=[7,2])"],
        from_next="DROP(parent_address=[],p=5)",
        to_next="INC(address=[7,2])",
    )
    operation = payload["operation"]

    assert operation["valid"] is False
    assert operation["reason"] == "from-next-does-not-match-history-next"
    assert operation["expected_next"] == "INC(address=[7])"


def test_redirect_rejects_unknown_target_candidate() -> None:
    from tools.research.pet_operator_z_route_probe import build_payload

    payload = build_payload(
        op="REDIRECT",
        history=HISTORY,
        prefix=["NEW(parent_address=[],q=7)"],
        candidates=["INC(address=[7])"],
        from_next="INC(address=[7])",
        to_next="INC(address=[7,2])",
    )
    operation = payload["operation"]

    assert operation["valid"] is False
    assert operation["reason"] == "to-next-not-in-candidate-set"


def test_redirect_rejects_noop_redirect() -> None:
    from tools.research.pet_operator_z_route_probe import build_payload

    payload = build_payload(
        op="REDIRECT",
        history=HISTORY,
        prefix=["NEW(parent_address=[],q=7)"],
        candidates=["INC(address=[7])"],
        from_next="INC(address=[7])",
        to_next="INC(address=[7])",
    )
    operation = payload["operation"]

    assert operation["valid"] is False
    assert operation["reason"] == "redirect-target-equals-source"


def test_shadow_select_validates_candidate_selection() -> None:
    from tools.research.pet_operator_z_route_probe import build_payload

    payload = build_payload(
        op="SHADOW_SELECT",
        history=["NEW(parent_address=[],q=7)"],
        prefix=["NEW(parent_address=[],q=7)"],
        candidates=["INC(address=[7])", "DROP(parent_address=[],p=5)"],
        selected_next="INC(address=[7])",
    )
    operation = payload["operation"]

    assert operation == {
        "op": "SHADOW_SELECT",
        "valid": True,
        "reason": None,
        "prefix": ["NEW(parent_address=[],q=7)"],
        "next_index": 1,
        "expected_next": None,
        "selected_next": "INC(address=[7])",
        "candidates": ["INC(address=[7])", "DROP(parent_address=[],p=5)"],
    }


def test_shadow_select_rejects_unknown_candidate() -> None:
    from tools.research.pet_operator_z_route_probe import build_payload

    payload = build_payload(
        op="SHADOW_SELECT",
        history=["NEW(parent_address=[],q=7)"],
        prefix=["NEW(parent_address=[],q=7)"],
        candidates=["DROP(parent_address=[],p=5)"],
        selected_next="INC(address=[7])",
    )
    operation = payload["operation"]

    assert operation["valid"] is False
    assert operation["reason"] == "selected-next-not-in-candidate-set"


def test_prefix_longer_than_history_is_invalid() -> None:
    from tools.research.pet_operator_z_route_probe import build_payload

    payload = build_payload(
        op="SHADOW_SELECT",
        history=["NEW(parent_address=[],q=7)"],
        prefix=["NEW(parent_address=[],q=7)", "INC(address=[7])"],
        candidates=["INC(address=[7])"],
        selected_next="INC(address=[7])",
    )
    operation = payload["operation"]

    assert operation["valid"] is False
    assert operation["reason"] == "invalid-history-prefix"
    assert operation["prefix_reason"] == "prefix-longer-than-history"


def test_z_route_probe_json_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_z_route_probe.py",
            "REDIRECT",
            "--history",
            '["NEW(parent_address=[],q=7)","INC(address=[7])"]',
            "--prefix",
            '["NEW(parent_address=[],q=7)"]',
            "--candidates",
            '["INC(address=[7])","INC(address=[7,2])"]',
            "--from-next",
            "INC(address=[7])",
            "--to-next",
            "INC(address=[7,2])",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    assert payload["schema"] == "pet.operator_z_route_probe.v0"
    assert payload["operation"]["op"] == "REDIRECT"
    assert payload["operation"]["valid"] is True
    assert payload["operation"]["to_next"] == "INC(address=[7,2])"


def test_z_route_probe_text_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_z_route_probe.py",
            "SHADOW_SELECT",
            "--history",
            '["NEW(parent_address=[],q=7)"]',
            "--prefix",
            '["NEW(parent_address=[],q=7)"]',
            "--candidates",
            '["INC(address=[7])","DROP(parent_address=[],p=5)"]',
            "--selected-next",
            "INC(address=[7])",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    out = result.stdout

    assert "schema = pet.operator_z_route_probe.v0" in out
    assert "op = SHADOW_SELECT" in out
    assert "operation_valid = true" in out
    assert "selected_next = INC(address=[7])" in out
