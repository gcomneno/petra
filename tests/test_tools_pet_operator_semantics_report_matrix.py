from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


EXPECTED_XY_SIGNATURE = (
    "commutes|support-created-y-target|support-removed-y-target"
)
EXPECTED_STABILITY_WITH_LEAF_BLOCKED = (
    "stable|created|destroyed|retargeted|leaf-blocked"
)
EXPECTED_STABILITY_WITHOUT_LEAF_BLOCKED = (
    "stable|created|destroyed|retargeted"
)
EXPECTED_PATTERN_WITH_LEAF_BLOCKED = (
    f"xy={EXPECTED_XY_SIGNATURE};"
    f"address={EXPECTED_STABILITY_WITH_LEAF_BLOCKED};"
    "axis_failed=0"
)
EXPECTED_PATTERN_WITHOUT_LEAF_BLOCKED = (
    f"xy={EXPECTED_XY_SIGNATURE};"
    f"address={EXPECTED_STABILITY_WITHOUT_LEAF_BLOCKED};"
    "axis_failed=0"
)


def test_operator_semantics_report_matrix_for_initial_seeds() -> None:
    from tools.research.pet_operator_semantics_report_matrix import build_payload

    payload = build_payload([12, 18, 60, 72])

    assert payload["schema"] == "pet.operator_semantics_report_matrix.v0"
    assert payload["numbers"] == [12, 18, 60, 72]
    assert payload["summary"]["checked"] == 4
    assert payload["summary"]["axis_invariant_failures"] == 0
    assert payload["summary"]["numbers_with_axis_invariant_failures"] == []
    assert payload["summary"]["pattern_count"] == 2

    rows = {row["n"]: row for row in payload["rows"]}

    assert rows[12]["top_level_baseline"] == [2, 3]
    assert rows[18]["top_level_baseline"] == [2, 3]
    assert rows[60]["top_level_baseline"] == [2, 3, 5]
    assert rows[72]["top_level_baseline"] == [2, 3]

    assert rows[60]["sample_address_count"] == 5
    assert rows[72]["sample_address_count"] == 4

    for row in rows.values():
        assert row["axis_invariants_passed"] == 6
        assert row["axis_invariants_failed"] == 0
        assert row["xy_relations"] == [
            "commutes",
            "support-created-y-target",
            "support-removed-y-target",
        ]
        assert row["xy_signature"] == EXPECTED_XY_SIGNATURE
        assert row["boundary"] == "research-only"

    assert rows[60]["address_stability_classes"] == [
        "stable",
        "created",
        "destroyed",
        "retargeted",
        "leaf-blocked",
    ]
    assert rows[60]["address_stability_signature"] == EXPECTED_STABILITY_WITH_LEAF_BLOCKED
    assert rows[60]["combined_pattern_signature"] == EXPECTED_PATTERN_WITH_LEAF_BLOCKED

    assert rows[72]["address_stability_classes"] == [
        "stable",
        "created",
        "destroyed",
        "retargeted",
    ]
    assert rows[72]["address_stability_signature"] == EXPECTED_STABILITY_WITHOUT_LEAF_BLOCKED
    assert rows[72]["combined_pattern_signature"] == EXPECTED_PATTERN_WITHOUT_LEAF_BLOCKED


def test_operator_semantics_report_matrix_groups_numbers_by_pattern() -> None:
    from tools.research.pet_operator_semantics_report_matrix import build_payload

    payload = build_payload([12, 18, 60, 72])

    assert payload["summary"]["numbers_by_pattern"] == {
        EXPECTED_PATTERN_WITH_LEAF_BLOCKED: [12, 18, 60],
        EXPECTED_PATTERN_WITHOUT_LEAF_BLOCKED: [72],
    }

    assert payload["pattern_groups"] == [
        {
            "combined_pattern_signature": EXPECTED_PATTERN_WITH_LEAF_BLOCKED,
            "xy_signature": EXPECTED_XY_SIGNATURE,
            "address_stability_signature": EXPECTED_STABILITY_WITH_LEAF_BLOCKED,
            "axis_invariants_failed": 0,
            "numbers": [12, 18, 60],
            "count": 3,
        },
        {
            "combined_pattern_signature": EXPECTED_PATTERN_WITHOUT_LEAF_BLOCKED,
            "xy_signature": EXPECTED_XY_SIGNATURE,
            "address_stability_signature": EXPECTED_STABILITY_WITHOUT_LEAF_BLOCKED,
            "axis_invariants_failed": 0,
            "numbers": [72],
            "count": 1,
        },
    ]


def test_operator_semantics_report_matrix_json_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_semantics_report_matrix.py",
            "12",
            "18",
            "60",
            "72",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    assert payload["schema"] == "pet.operator_semantics_report_matrix.v0"
    assert payload["summary"]["checked"] == 4
    assert payload["summary"]["axis_invariant_failures"] == 0
    assert payload["summary"]["pattern_count"] == 2
    assert [row["n"] for row in payload["rows"]] == [12, 18, 60, 72]
    assert payload["rows"][2]["top_level_baseline"] == [2, 3, 5]
    assert payload["rows"][2]["combined_pattern_signature"] == EXPECTED_PATTERN_WITH_LEAF_BLOCKED
    assert payload["rows"][3]["combined_pattern_signature"] == EXPECTED_PATTERN_WITHOUT_LEAF_BLOCKED


def test_operator_semantics_report_matrix_text_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_semantics_report_matrix.py",
            "12",
            "18",
            "60",
            "72",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    out = result.stdout

    assert "schema = pet.operator_semantics_report_matrix.v0" in out
    assert "numbers = [12, 18, 60, 72]" in out
    assert "'pattern_count': 2" in out
    assert "n=60 baseline=[2, 3, 5]" in out
    assert "n=72 baseline=[2, 3]" in out
    assert "pattern_groups:" in out
    assert "numbers=[12, 18, 60]" in out
    assert "numbers=[72]" in out
    assert f"signature={EXPECTED_PATTERN_WITHOUT_LEAF_BLOCKED}" in out
