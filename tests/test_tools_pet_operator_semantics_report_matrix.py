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
    assert rows[60]["top_level_width"] == 3
    assert rows[60]["has_leaf_address"] is True
    assert rows[60]["has_recursive_address"] is True
    assert rows[60]["first_recursive_address"] == [2, 2]
    assert rows[60]["leaf_blocked_observed"] is True
    assert rows[60]["support_removed_observed"] is True

    assert rows[72]["sample_address_count"] == 4
    assert rows[72]["top_level_width"] == 2
    assert rows[72]["has_leaf_address"] is True
    assert rows[72]["has_recursive_address"] is True
    assert rows[72]["first_recursive_address"] == [2, 3]
    assert rows[72]["leaf_blocked_observed"] is False
    assert rows[72]["support_removed_observed"] is True

    for row in rows.values():
        assert row["axis_invariants_passed"] == 6
        assert row["axis_invariants_failed"] == 0
        assert row["xy_relations"] == [
            "commutes",
            "support-created-y-target",
            "support-removed-y-target",
        ]
        assert row["xy_signature"] == EXPECTED_XY_SIGNATURE
        assert row["boundary"] == "experimental"

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
            "pattern_class": "multi-support-recursive-leaf-blocked",
            "xy_signature": EXPECTED_XY_SIGNATURE,
            "address_stability_signature": EXPECTED_STABILITY_WITH_LEAF_BLOCKED,
            "axis_invariants_failed": 0,
            "numbers": [12, 18, 60],
            "count": 3,
            "example_numbers": [12, 18, 60],
            "width_values": [2, 3],
            "has_leaf_address_count": 3,
            "has_recursive_address_count": 3,
            "leaf_blocked_count": 3,
            "support_removed_count": 3,
        },
        {
            "combined_pattern_signature": EXPECTED_PATTERN_WITHOUT_LEAF_BLOCKED,
            "pattern_class": "multi-support-stable-removal",
            "xy_signature": EXPECTED_XY_SIGNATURE,
            "address_stability_signature": EXPECTED_STABILITY_WITHOUT_LEAF_BLOCKED,
            "axis_invariants_failed": 0,
            "numbers": [72],
            "count": 1,
            "example_numbers": [72],
            "width_values": [2],
            "has_leaf_address_count": 1,
            "has_recursive_address_count": 1,
            "leaf_blocked_count": 0,
            "support_removed_count": 1,
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
    assert payload["rows"][2]["top_level_width"] == 3
    assert payload["rows"][2]["has_recursive_address"] is True
    assert payload["rows"][2]["leaf_blocked_observed"] is True
    assert payload["rows"][2]["combined_pattern_signature"] == EXPECTED_PATTERN_WITH_LEAF_BLOCKED
    assert payload["rows"][3]["combined_pattern_signature"] == EXPECTED_PATTERN_WITHOUT_LEAF_BLOCKED
    assert payload["rows"][3]["has_leaf_address"] is True
    assert payload["rows"][3]["leaf_blocked_observed"] is False


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
    assert "n=60 baseline=[2, 3, 5] width=3" in out
    assert "n=72 baseline=[2, 3] width=2" in out
    assert "leaf_blocked=True" in out
    assert "leaf_blocked=False" in out
    assert "pattern_groups:" in out
    assert "numbers=[12, 18, 60]" in out
    assert "examples=[12, 18, 60]" in out
    assert "widths=[2, 3]" in out
    assert "leaf_blocked_count=3" in out
    assert "numbers=[72]" in out
    assert "leaf_blocked_count=0" in out
    assert f"signature={EXPECTED_PATTERN_WITHOUT_LEAF_BLOCKED}" in out


def test_operator_semantics_report_matrix_collects_ranges_and_dedupes() -> None:
    from tools.research.pet_operator_semantics_report_matrix import collect_numbers

    assert collect_numbers([60], [[12, 14], [14, 16]]) == [60, 12, 13, 14, 15, 16]


def test_operator_semantics_report_matrix_rejects_empty_input() -> None:
    from tools.research.pet_operator_semantics_report_matrix import collect_numbers

    try:
        collect_numbers([], None)
    except ValueError as exc:
        assert "at least one N" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("empty matrix input should be rejected")


def test_operator_semantics_report_matrix_rejects_reversed_range() -> None:
    from tools.research.pet_operator_semantics_report_matrix import collect_numbers

    try:
        collect_numbers([], [[18, 12]])
    except ValueError as exc:
        assert "START <= END" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("reversed range should be rejected")


def test_operator_semantics_report_matrix_range_json_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_semantics_report_matrix.py",
            "--range",
            "12",
            "18",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    assert payload["schema"] == "pet.operator_semantics_report_matrix.v0"
    assert payload["numbers"] == [12, 13, 14, 15, 16, 17, 18]
    assert payload["summary"]["checked"] == 7
    assert payload["summary"]["axis_invariant_failures"] == 0
    assert payload["summary"]["pattern_count"] >= 1
    assert [row["n"] for row in payload["rows"]] == [12, 13, 14, 15, 16, 17, 18]
    assert all(row["combined_pattern_signature"] for row in payload["rows"])


def test_operator_semantics_report_matrix_mixed_input_text_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_semantics_report_matrix.py",
            "60",
            "--range",
            "12",
            "14",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    out = result.stdout

    assert "schema = pet.operator_semantics_report_matrix.v0" in out
    assert "numbers = [60, 12, 13, 14]" in out
    assert "pattern_groups:" in out


def test_operator_semantics_report_matrix_anatomy_for_prime_and_prime_power() -> None:
    from tools.research.pet_operator_semantics_report_matrix import build_payload

    payload = build_payload([13, 16])
    rows = {row["n"]: row for row in payload["rows"]}

    assert rows[13]["top_level_baseline"] == [13]
    assert rows[13]["top_level_width"] == 1
    assert rows[13]["has_leaf_address"] is True
    assert rows[13]["has_recursive_address"] is False
    assert rows[13]["first_recursive_address"] is None
    assert rows[13]["leaf_blocked_observed"] is False
    assert rows[13]["support_removed_observed"] is False

    assert rows[16]["top_level_baseline"] == [2]
    assert rows[16]["top_level_width"] == 1
    assert rows[16]["has_leaf_address"] is False
    assert rows[16]["has_recursive_address"] is True
    assert rows[16]["first_recursive_address"] == [2, 2]
    assert rows[16]["leaf_blocked_observed"] is False
    assert rows[16]["support_removed_observed"] is False


def test_operator_semantics_report_matrix_pattern_group_anatomy_for_range() -> None:
    from tools.research.pet_operator_semantics_report_matrix import build_payload

    payload = build_payload(list(range(12, 19)))

    assert payload["summary"]["pattern_count"] == 4

    groups = {
        tuple(group["numbers"]): group
        for group in payload["pattern_groups"]
    }

    assert groups[(12, 18)]["width_values"] == [2]
    assert groups[(12, 18)]["has_leaf_address_count"] == 2
    assert groups[(12, 18)]["has_recursive_address_count"] == 2
    assert groups[(12, 18)]["leaf_blocked_count"] == 2
    assert groups[(12, 18)]["support_removed_count"] == 2
    assert groups[(12, 18)]["example_numbers"] == [12, 18]

    assert groups[(13, 17)]["width_values"] == [1]
    assert groups[(13, 17)]["has_leaf_address_count"] == 2
    assert groups[(13, 17)]["has_recursive_address_count"] == 0
    assert groups[(13, 17)]["leaf_blocked_count"] == 0
    assert groups[(13, 17)]["support_removed_count"] == 0

    assert groups[(14, 15)]["width_values"] == [2]
    assert groups[(14, 15)]["leaf_blocked_count"] == 0
    assert groups[(14, 15)]["support_removed_count"] == 2

    assert groups[(16,)]["width_values"] == [1]
    assert groups[(16,)]["has_leaf_address_count"] == 0
    assert groups[(16,)]["has_recursive_address_count"] == 1
    assert groups[(16,)]["leaf_blocked_count"] == 0
    assert groups[(16,)]["support_removed_count"] == 0


def test_operator_semantics_report_matrix_filters_pattern_groups_by_min_count() -> None:
    from tools.research.pet_operator_semantics_report_matrix import build_payload

    payload = build_payload(list(range(12, 19)), min_count=2)

    assert payload["summary"]["pattern_count"] == 4
    assert payload["summary"]["emitted_pattern_count"] == 3
    assert payload["summary"]["pattern_group_filter_active"] is True
    assert [group["numbers"] for group in payload["pattern_groups"]] == [
        [12, 18],
        [13, 17],
        [14, 15],
    ]
    assert payload["pattern_group_filters"]["min_count"] == 2


def test_operator_semantics_report_matrix_filters_pattern_groups_by_signature_text() -> None:
    from tools.research.pet_operator_semantics_report_matrix import build_payload

    payload = build_payload([12, 18, 60, 72], pattern="leaf-blocked")

    assert payload["summary"]["pattern_count"] == 2
    assert payload["summary"]["emitted_pattern_count"] == 1
    assert payload["summary"]["numbers_by_pattern"] == {
        EXPECTED_PATTERN_WITH_LEAF_BLOCKED: [12, 18, 60],
        EXPECTED_PATTERN_WITHOUT_LEAF_BLOCKED: [72],
    }
    assert [group["numbers"] for group in payload["pattern_groups"]] == [
        [12, 18, 60],
    ]
    assert "leaf-blocked" in payload["pattern_groups"][0]["combined_pattern_signature"]


def test_operator_semantics_report_matrix_limits_top_patterns_by_frequency() -> None:
    from tools.research.pet_operator_semantics_report_matrix import build_payload

    payload = build_payload(list(range(2, 101)), top_patterns=3)

    assert payload["summary"]["checked"] == 99
    assert payload["summary"]["pattern_count"] == 10
    assert payload["summary"]["emitted_pattern_count"] == 3
    assert [group["count"] for group in payload["pattern_groups"]] == [34, 24, 14]


def test_operator_semantics_report_matrix_can_omit_rows() -> None:
    from tools.research.pet_operator_semantics_report_matrix import build_payload

    payload = build_payload([12, 18, 60, 72], include_rows=False)

    assert payload["summary"]["checked"] == 4
    assert payload["summary"]["pattern_count"] == 2
    assert payload["summary"]["emitted_pattern_count"] == 2
    assert payload["pattern_group_filters"]["include_rows"] is False
    assert "rows" not in payload


def test_operator_semantics_report_matrix_filter_json_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_semantics_report_matrix.py",
            "--range",
            "12",
            "18",
            "--min-count",
            "2",
            "--pattern",
            "leaf-blocked",
            "--no-rows",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    assert payload["schema"] == "pet.operator_semantics_report_matrix.v0"
    assert payload["summary"]["checked"] == 7
    assert payload["summary"]["pattern_count"] == 4
    assert payload["summary"]["emitted_pattern_count"] == 1
    assert payload["pattern_group_filters"]["active"] is True
    assert payload["pattern_group_filters"]["include_rows"] is False
    assert "rows" not in payload
    assert [group["numbers"] for group in payload["pattern_groups"]] == [[12, 18]]


def test_operator_semantics_report_matrix_no_rows_text_cli_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_semantics_report_matrix.py",
            "--range",
            "12",
            "18",
            "--min-count",
            "2",
            "--no-rows",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    out = result.stdout

    assert "schema = pet.operator_semantics_report_matrix.v0" in out
    assert "pattern_group_filters =" in out
    assert "'emitted_pattern_count': 3" in out
    assert "rows:" not in out
    assert "pattern_groups:" in out


def test_operator_semantics_report_matrix_rejects_invalid_group_filters() -> None:
    from tools.research.pet_operator_semantics_report_matrix import build_payload

    for kwargs, expected in [
        ({"top_patterns": 0}, "--top-patterns"),
        ({"min_count": 0}, "--min-count"),
    ]:
        try:
            build_payload([12], **kwargs)
        except ValueError as exc:
            assert expected in str(exc)
        else:  # pragma: no cover - defensive assertion
            raise AssertionError(f"invalid filter should be rejected: {kwargs}")


def test_operator_semantics_report_matrix_declares_experimental_status() -> None:
    from tools.research.pet_operator_semantics_report_matrix import build_payload

    payload = build_payload([12, 18, 60, 72])

    assert payload["tooling_status"] == "experimental documented tooling"
    assert payload["stable_cli_contract"] is False
    assert "experimental documented tooling" in payload["boundaries"]


def test_operator_semantics_report_matrix_classifies_range_patterns() -> None:
    from tools.research.pet_operator_semantics_report_matrix import build_payload

    payload = build_payload(list(range(2, 101)))

    assert payload["summary"]["pattern_count"] == 10
    assert payload["summary"]["pattern_class_count"] == {
        "single-support-root-stable": 1,
        "single-support-leaf": 24,
        "single-support-leaf-blocked": 1,
        "multi-support-stable-removal": 10,
        "single-support-recursive-chain": 4,
        "single-support-leaf-blocked-retarget": 3,
        "multi-support-removal": 34,
        "multi-support-recursive-leaf-blocked": 6,
        "multi-support-leaf-blocked-removal": 14,
        "single-support-power-destroyed": 2,
    }

    groups = {
        tuple(group["example_numbers"]): group["pattern_class"]
        for group in payload["pattern_groups"]
    }

    assert groups[(2,)] == "single-support-root-stable"
    assert groups[(3, 5, 7, 11, 13)] == "single-support-leaf"
    assert groups[(4,)] == "single-support-leaf-blocked"
    assert groups[(6, 24, 30, 42, 48)] == "multi-support-stable-removal"
    assert groups[(8, 16, 32, 64)] == "single-support-recursive-chain"
    assert groups[(9, 25, 49)] == "single-support-leaf-blocked-retarget"
    assert groups[(10, 14, 15, 21, 22)] == "multi-support-removal"
    assert groups[(12, 18, 36, 60, 84)] == "multi-support-recursive-leaf-blocked"
    assert groups[(20, 28, 44, 45, 50)] == "multi-support-leaf-blocked-removal"
    assert groups[(27, 81)] == "single-support-power-destroyed"


def test_operator_semantics_report_matrix_text_includes_pattern_class() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_semantics_report_matrix.py",
            "--range",
            "2",
            "20",
            "--no-rows",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    out = result.stdout

    assert "pattern_class_count" in out
    assert "class=single-support-leaf" in out
    assert "class=multi-support-removal" in out
    assert "class=multi-support-recursive-leaf-blocked" in out


def test_operator_semantics_report_matrix_progress_goes_to_stderr() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_operator_semantics_report_matrix.py",
            "--range",
            "2",
            "11",
            "--no-rows",
            "--progress",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    assert payload["summary"]["checked"] == 10
    assert "progress: checked 1/10 (10%)" in result.stderr
    assert "progress: checked 10/10 (100%)" in result.stderr
