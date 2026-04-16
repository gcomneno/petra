from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "pet_support_realization.py"


def _run_json_file_command(tool: Path, payload: dict) -> dict:
    fh = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False)
    try:
        json.dump(payload, fh)
        fh.flush()
        path = fh.name
    finally:
        fh.close()

    try:
        proc = subprocess.run(
            [sys.executable, str(tool), path, "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(proc.stdout)
    finally:
        Path(path).unlink(missing_ok=True)


def _run_partial_build_payload(n: int) -> dict:
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "build-from-int",
            str(n),
            "--allow-non-canonical-support",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def test_support_realization_reconstructs_exact_target_from_block_products() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 1234567890,
        "target_generator": 4620,
        "shape_signature": [[], [], [], [], [[]]],
        "slot_count": 5,
        "exponent_multiset": [2, 1, 1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "exp2-slot",
                "slot_exp": 2,
                "slot_multiplicity": 1,
                "target_product": 3,
                "constraints": {"prime_only": True, "count": 1},
            },
            {
                "block_id": "exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 4,
                "target_product": 137174210,
                "constraints": {"prime_only": True, "count": 4},
            },
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["source_schema"] == "pet-support-realization-input-v0"
    assert report["resolved_product"] == 1
    assert report["unresolved_product"] == 1234567890
    assert report["resolved_fraction"] == "1/1234567890"
    assert report["resolved_exponent_mass"] == 0
    assert report["unresolved_exponent_mass"] == 6
    assert report["total_exponent_mass"] == 6
    assert report["reconstructed_target_n"] == 1234567890
    assert report["exact_target_match"] is True
    assert report["realization_status"] == "exact-from-block-products"


def test_support_realization_derives_blocks_from_partial_build_payload() -> None:
    payload = _run_partial_build_payload(1234567890)
    report = _run_json_file_command(TOOL, payload)

    assert report["source_schema"] == "pet-build-from-int-v2"
    assert report["target_generator"] == 4620
    assert report["exponent_multiset"] == [2, 1, 1, 1, 1]
    assert report["phase2"]["status"] == "derived-from-factorization"
    assert report["unknown_block_count"] == 2
    assert report["resolved_product"] == 1
    assert report["unresolved_product"] == 1234567890
    assert report["resolved_fraction"] == "1/1234567890"
    assert report["resolved_exponent_mass"] == 0
    assert report["unresolved_exponent_mass"] == 6
    assert report["total_exponent_mass"] == 6
    assert report["reconstructed_target_n"] == 1234567890
    assert report["exact_target_match"] is True
    assert report["realization_status"] == "exact-from-derived-block-products"

    blocks = {block["block_id"]: block for block in report["unknown_blocks"]}
    assert blocks["exp2-slot"]["target_product"] == 3
    assert blocks["exp1-slots"]["target_product"] == 137174210


def test_support_realization_detects_block_product_mismatch() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 1234567890,
        "target_generator": 4620,
        "shape_signature": [[], [], [], [], [[]]],
        "slot_count": 5,
        "exponent_multiset": [2, 1, 1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "exp2-slot",
                "slot_exp": 2,
                "slot_multiplicity": 1,
                "target_product": 3,
                "constraints": {"prime_only": True, "count": 1},
            },
            {
                "block_id": "exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 4,
                "target_product": 137174211,
                "constraints": {"prime_only": True, "count": 4},
            },
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["resolved_product"] == 1
    assert report["unresolved_product"] != 1234567890
    assert report["resolved_fraction"] == "1/1234567890"
    assert report["resolved_exponent_mass"] == 0
    assert report["unresolved_exponent_mass"] == 6
    assert report["total_exponent_mass"] == 6
    assert report["reconstructed_target_n"] != 1234567890
    assert report["exact_target_match"] is False
    assert report["realization_status"] == "block-product-mismatch"


def test_support_realization_reports_known_unknown_split_fraction() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 1234567890123,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [
            {
                "block_id": "known-exp1-slot",
                "slot_exp": 1,
                "slot_multiplicity": 1,
                "target_product": 3,
                "constraints": {"prime_only": True, "count": 1},
            }
        ],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 2,
                "target_product": 411522630041,
                "constraints": {"prime_only": True, "count": 2},
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["resolved_product"] == 3
    assert report["unresolved_product"] == 411522630041
    assert report["resolved_fraction"] == "3/1234567890123"
    assert report["resolved_exponent_mass"] == 1
    assert report["unresolved_exponent_mass"] == 2
    assert report["total_exponent_mass"] == 3
    assert report["reconstructed_target_n"] == 1234567890123
    assert report["exact_target_match"] is True
    assert report["realization_status"] == "exact-from-block-products"


def test_support_realization_validates_supported_constraints_ok() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 1234567890123,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [
            {
                "block_id": "known-exp1-slot",
                "slot_exp": 1,
                "slot_multiplicity": 1,
                "target_product": 3,
                "constraints": {
                    "prime_only": True,
                    "count": 1,
                    "bit_length_min": 2,
                    "bit_length_max": 2,
                    "known_divisors": [3],
                    "forbidden_divisors": [5]
                },
            }
        ],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 2,
                "target_product": 411522630041,
                "constraints": {
                    "count": 2,
                    "bit_length_min": 39,
                    "bit_length_max": 39
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["constraint_status"] == "ok"
    known = report["known_blocks"][0]
    unknown = report["unknown_blocks"][0]
    assert known["constraint_checks"]["bit_length_min"] is True
    assert known["constraint_checks"]["bit_length_max"] is True
    assert known["constraint_checks"]["known_divisors"] is True
    assert known["constraint_checks"]["forbidden_divisors"] is True
    assert unknown["constraint_checks"]["bit_length_min"] is True
    assert unknown["constraint_checks"]["bit_length_max"] is True


def test_support_realization_validates_supported_constraints_failed() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 1234567890123,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [
            {
                "block_id": "known-exp1-slot",
                "slot_exp": 1,
                "slot_multiplicity": 1,
                "target_product": 3,
                "constraints": {
                    "forbidden_divisors": [3]
                },
            }
        ],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 2,
                "target_product": 411522630041,
                "constraints": {
                    "bit_length_max": 10
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["constraint_status"] == "failed"
    assert report["known_blocks"][0]["constraint_checks"]["forbidden_divisors"] is False
    assert report["unknown_blocks"][0]["constraint_checks"]["bit_length_max"] is False


def test_support_realization_peels_known_divisors_from_unknown_block() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 30,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 3,
                "target_product": 30,
                "constraints": {
                    "known_divisors": [2]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["known_block_count"] == 1
    assert report["unknown_block_count"] == 1
    assert report["resolved_product"] == 2
    assert report["unresolved_product"] == 15
    assert report["resolved_exponent_mass"] == 1
    assert report["unresolved_exponent_mass"] == 2
    assert report["reconstructed_target_n"] == 30
    assert report["exact_target_match"] is True

    known = report["known_blocks"][0]
    unknown = report["unknown_blocks"][0]

    assert known["target_product"] == 2
    assert known["slot_exp"] == 1
    assert known["slot_multiplicity"] == 1

    assert unknown["target_product"] == 15
    assert unknown["slot_exp"] == 1
    assert unknown["slot_multiplicity"] == 2


def test_support_realization_does_not_peel_if_last_slot_would_leave_nontrivial_residue() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 6,
        "target_generator": 6,
        "shape_signature": [[], []],
        "slot_count": 2,
        "exponent_multiset": [1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slot",
                "slot_exp": 1,
                "slot_multiplicity": 1,
                "target_product": 6,
                "constraints": {
                    "known_divisors": [2]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["known_block_count"] == 0
    assert report["unknown_block_count"] == 1
    assert report["resolved_product"] == 1
    assert report["unresolved_product"] == 6
    assert report["resolved_exponent_mass"] == 0
    assert report["unresolved_exponent_mass"] == 1
    assert report["exact_target_match"] is True

    unknown = report["unknown_blocks"][0]
    assert unknown["target_product"] == 6
    assert unknown["slot_multiplicity"] == 1


def test_support_realization_peels_multiple_known_divisors_from_single_unknown_block() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 210,
        "target_generator": 210,
        "shape_signature": [[], [], [], []],
        "slot_count": 4,
        "exponent_multiset": [1, 1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 4,
                "target_product": 210,
                "constraints": {
                    "known_divisors": [2, 3]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["known_block_count"] == 2
    assert report["unknown_block_count"] == 1
    assert report["resolved_product"] == 6
    assert report["unresolved_product"] == 35
    assert report["resolved_exponent_mass"] == 2
    assert report["unresolved_exponent_mass"] == 2
    assert report["reconstructed_target_n"] == 210
    assert report["exact_target_match"] is True

    known_products = sorted(block["target_product"] for block in report["known_blocks"])
    assert known_products == [2, 3]

    unknown = report["unknown_blocks"][0]
    assert unknown["target_product"] == 35
    assert unknown["slot_exp"] == 1
    assert unknown["slot_multiplicity"] == 2


def test_support_realization_peels_multiple_known_divisors_and_fully_resolves_block() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 6,
        "target_generator": 6,
        "shape_signature": [[], []],
        "slot_count": 2,
        "exponent_multiset": [1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 2,
                "target_product": 6,
                "constraints": {
                    "known_divisors": [2, 3]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["known_block_count"] == 2
    assert report["unknown_block_count"] == 0
    assert report["resolved_product"] == 6
    assert report["unresolved_product"] == 1
    assert report["resolved_exponent_mass"] == 2
    assert report["unresolved_exponent_mass"] == 0
    assert report["reconstructed_target_n"] == 6
    assert report["exact_target_match"] is True

    known_products = sorted(block["target_product"] for block in report["known_blocks"])
    assert known_products == [2, 3]


def test_support_realization_does_not_peel_when_known_divisors_include_unit_or_nonpositive() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 30,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 3,
                "target_product": 30,
                "constraints": {
                    "known_divisors": [1, 2]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["known_block_count"] == 0
    assert report["unknown_block_count"] == 1
    assert report["resolved_product"] == 1
    assert report["unresolved_product"] == 30
    assert report["resolved_exponent_mass"] == 0
    assert report["unresolved_exponent_mass"] == 3
    assert report["exact_target_match"] is True


def test_support_realization_does_not_peel_when_known_divisor_count_exceeds_slot_multiplicity() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 6,
        "target_generator": 6,
        "shape_signature": [[]],
        "slot_count": 1,
        "exponent_multiset": [1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slot",
                "slot_exp": 1,
                "slot_multiplicity": 1,
                "target_product": 6,
                "constraints": {
                    "known_divisors": [2, 3]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["known_block_count"] == 0
    assert report["unknown_block_count"] == 1
    assert report["resolved_product"] == 1
    assert report["unresolved_product"] == 6
    assert report["resolved_exponent_mass"] == 0
    assert report["unresolved_exponent_mass"] == 1
    assert report["exact_target_match"] is True


def test_support_realization_does_not_peel_when_known_divisor_product_overconsumes_target_product() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 12,
        "target_generator": 6,
        "shape_signature": [[], []],
        "slot_count": 2,
        "exponent_multiset": [1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 2,
                "target_product": 12,
                "constraints": {
                    "known_divisors": [4, 6]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["known_block_count"] == 0
    assert report["unknown_block_count"] == 1
    assert report["resolved_product"] == 1
    assert report["unresolved_product"] == 12
    assert report["resolved_exponent_mass"] == 0
    assert report["unresolved_exponent_mass"] == 2
    assert report["exact_target_match"] is True


def test_support_realization_reports_zero_peeling_summary_when_no_peeling_occurs() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 1234567890123,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [
            {
                "block_id": "known-exp1-slot",
                "slot_exp": 1,
                "slot_multiplicity": 1,
                "target_product": 3,
                "constraints": {"prime_only": True, "count": 1},
            }
        ],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 2,
                "target_product": 411522630041,
                "constraints": {"prime_only": True, "count": 2},
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["peeling_summary"] == {
        "peeled_block_count": 0,
        "peeled_divisor_count": 0,
        "peeled_known_block_ids": [],
        "fully_resolved_unknown_blocks": 0,
        "fully_peeled_block_ids": [],
        "blocked_unknown_blocks": 0,
        "blocked_block_ids": [],
        "not_attempted_unknown_blocks": 1,
        "not_attempted_block_ids": ["unknown-exp1-slots"],
        "partially_peeled_unknown_blocks": 0,
        "partially_peeled_block_ids": [],
        "pre_known_block_ids": ["known-exp1-slot"],
    }


def test_support_realization_reports_peeling_summary_for_partial_resolution() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 30,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 3,
                "target_product": 30,
                "constraints": {
                    "known_divisors": [2]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["peeling_summary"] == {
        "peeled_block_count": 1,
        "peeled_divisor_count": 1,
        "peeled_known_block_ids": ["unknown-exp1-slots::known-divisor-1"],
        "fully_resolved_unknown_blocks": 0,
        "fully_peeled_block_ids": [],
        "blocked_unknown_blocks": 0,
        "blocked_block_ids": [],
        "not_attempted_unknown_blocks": 0,
        "not_attempted_block_ids": [],
        "partially_peeled_unknown_blocks": 1,
        "partially_peeled_block_ids": ["unknown-exp1-slots"],
        "pre_known_block_ids": [],
    }


def test_support_realization_reports_peeling_summary_for_full_resolution() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 6,
        "target_generator": 6,
        "shape_signature": [[], []],
        "slot_count": 2,
        "exponent_multiset": [1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 2,
                "target_product": 6,
                "constraints": {
                    "known_divisors": [2, 3]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["peeling_summary"] == {
        "peeled_block_count": 2,
        "peeled_divisor_count": 2,
        "peeled_known_block_ids": [
            "unknown-exp1-slots::known-divisor-1",
            "unknown-exp1-slots::known-divisor-2",
        ],
        "fully_resolved_unknown_blocks": 1,
        "fully_peeled_block_ids": ["unknown-exp1-slots"],
        "blocked_unknown_blocks": 0,
        "blocked_block_ids": [],
        "not_attempted_unknown_blocks": 0,
        "not_attempted_block_ids": [],
        "partially_peeled_unknown_blocks": 0,
        "partially_peeled_block_ids": [],
        "pre_known_block_ids": [],
    }


def test_support_realization_reports_partial_peeling_status_on_residual_unknown_block() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 30,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 3,
                "target_product": 30,
                "constraints": {
                    "known_divisors": [2]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    unknown = report["unknown_blocks"][0]
    assert unknown["peeling_status"] == {
        "status": "partially-peeled",
        "reason": "peeled-known-divisors",
    }


def test_support_realization_blocks_peeling_on_known_forbidden_divisor_conflict() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 30,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 3,
                "target_product": 30,
                "constraints": {
                    "known_divisors": [2],
                    "forbidden_divisors": [2]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["known_block_count"] == 0
    assert report["unknown_block_count"] == 1
    assert report["resolved_product"] == 1
    assert report["unresolved_product"] == 30

    unknown = report["unknown_blocks"][0]
    assert unknown["peeling_status"] == {
        "status": "blocked",
        "reason": "known-divisors-conflict-with-forbidden-divisors",
    }



def _assert_mapping_contains(actual: dict, expected: dict) -> None:
    for key, value in expected.items():
        assert actual.get(key) == value, (
            f"unexpected value for {key!r}: "
            f"expected {value!r}, got {actual.get(key)!r}"
        )


def test_support_realization_reports_extended_peeling_summary_for_not_attempted_block() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 1234567890123,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [
            {
                "block_id": "known-exp1-slot",
                "slot_exp": 1,
                "slot_multiplicity": 1,
                "target_product": 3,
                "constraints": {"prime_only": True, "count": 1},
            }
        ],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 2,
                "target_product": 411522630041,
                "constraints": {"prime_only": True, "count": 2},
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    _assert_mapping_contains(report["peeling_summary"], {
        "peeled_block_count": 0,
        "peeled_divisor_count": 0,
        "peeled_known_block_ids": [],
        "fully_resolved_unknown_blocks": 0,
        "fully_peeled_block_ids": [],
        "blocked_unknown_blocks": 0,
        "blocked_block_ids": [],
        "not_attempted_unknown_blocks": 1,
        "not_attempted_block_ids": ["unknown-exp1-slots"],
        "partially_peeled_unknown_blocks": 0,
        "partially_peeled_block_ids": [],
        "pre_known_block_ids": ["known-exp1-slot"],
    })


def test_support_realization_reports_extended_peeling_summary_for_partial_resolution() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 30,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 3,
                "target_product": 30,
                "constraints": {
                    "known_divisors": [2]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    _assert_mapping_contains(report["peeling_summary"], {
        "peeled_block_count": 1,
        "peeled_divisor_count": 1,
        "peeled_known_block_ids": ["unknown-exp1-slots::known-divisor-1"],
        "fully_resolved_unknown_blocks": 0,
        "fully_peeled_block_ids": [],
        "blocked_unknown_blocks": 0,
        "blocked_block_ids": [],
        "not_attempted_unknown_blocks": 0,
        "not_attempted_block_ids": [],
        "partially_peeled_unknown_blocks": 1,
        "partially_peeled_block_ids": ["unknown-exp1-slots"],
        "pre_known_block_ids": [],
    })


def test_support_realization_reports_extended_peeling_summary_for_blocked_resolution() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 30,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 3,
                "target_product": 30,
                "constraints": {
                    "known_divisors": [2],
                    "forbidden_divisors": [2]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    _assert_mapping_contains(report["peeling_summary"], {
        "peeled_block_count": 0,
        "peeled_divisor_count": 0,
        "peeled_known_block_ids": [],
        "fully_resolved_unknown_blocks": 0,
        "fully_peeled_block_ids": [],
        "blocked_unknown_blocks": 1,
        "blocked_block_ids": ["unknown-exp1-slots"],
        "not_attempted_unknown_blocks": 0,
        "not_attempted_block_ids": [],
        "partially_peeled_unknown_blocks": 0,
        "partially_peeled_block_ids": [],
        "pre_known_block_ids": [],
    })


def test_support_realization_reports_extended_peeling_summary_for_full_resolution() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 6,
        "target_generator": 6,
        "shape_signature": [[], []],
        "slot_count": 2,
        "exponent_multiset": [1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 2,
                "target_product": 6,
                "constraints": {
                    "known_divisors": [2, 3]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    _assert_mapping_contains(report["peeling_summary"], {
        "peeled_block_count": 2,
        "peeled_divisor_count": 2,
        "peeled_known_block_ids": [
            "unknown-exp1-slots::known-divisor-1",
            "unknown-exp1-slots::known-divisor-2",
        ],
        "fully_resolved_unknown_blocks": 1,
        "fully_peeled_block_ids": ["unknown-exp1-slots"],
        "blocked_unknown_blocks": 0,
        "blocked_block_ids": [],
        "not_attempted_unknown_blocks": 0,
        "not_attempted_block_ids": [],
        "partially_peeled_unknown_blocks": 0,
        "partially_peeled_block_ids": [],
        "pre_known_block_ids": [],
    })


def test_support_realization_exposes_stable_peeling_status_vocabulary() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 6,
        "target_generator": 6,
        "shape_signature": [[], []],
        "slot_count": 2,
        "exponent_multiset": [1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 2,
                "target_product": 6,
                "constraints": {
                    "known_divisors": [2, 3]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["peeling_status_vocabulary"] == [
        "not-attempted",
        "blocked",
        "partially-peeled",
        "fully-peeled",
    ]


def test_support_realization_reports_fully_peeled_block_ids() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 6,
        "target_generator": 6,
        "shape_signature": [[], []],
        "slot_count": 2,
        "exponent_multiset": [1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 2,
                "target_product": 6,
                "constraints": {
                    "known_divisors": [2, 3]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["peeling_summary"]["fully_peeled_block_ids"] == ["unknown-exp1-slots"]


def test_support_realization_reports_blocked_block_ids() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 30,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 3,
                "target_product": 30,
                "constraints": {
                    "known_divisors": [2],
                    "forbidden_divisors": [2]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["peeling_summary"]["blocked_block_ids"] == ["unknown-exp1-slots"]


def test_support_realization_reports_not_attempted_block_ids() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 1234567890123,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 2,
                "target_product": 411522630041,
                "constraints": {"prime_only": True, "count": 2},
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["peeling_summary"]["not_attempted_block_ids"] == ["unknown-exp1-slots"]


def test_support_realization_reports_partially_peeled_block_ids() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 30,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 3,
                "target_product": 30,
                "constraints": {
                    "known_divisors": [2]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["peeling_summary"]["partially_peeled_block_ids"] == ["unknown-exp1-slots"]


def test_support_realization_reports_pre_known_block_ids() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 1234567890123,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [
            {
                "block_id": "known-exp1-slot",
                "slot_exp": 1,
                "slot_multiplicity": 1,
                "target_product": 3,
                "constraints": {"prime_only": True, "count": 1},
            }
        ],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 2,
                "target_product": 411522630041,
                "constraints": {"prime_only": True, "count": 2},
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["peeling_summary"]["pre_known_block_ids"] == ["known-exp1-slot"]


def test_support_realization_reports_peeled_known_block_ids() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 210,
        "target_generator": 210,
        "shape_signature": [[], [], [], []],
        "slot_count": 4,
        "exponent_multiset": [1, 1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 4,
                "target_product": 210,
                "constraints": {
                    "known_divisors": [2, 3]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["peeling_summary"]["peeled_known_block_ids"] == [
        "unknown-exp1-slots::known-divisor-1",
        "unknown-exp1-slots::known-divisor-2",
    ]


def test_support_realization_reports_builder_readiness_not_ready() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 1234567890123,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [
            {
                "block_id": "known-exp1-slot",
                "slot_exp": 1,
                "slot_multiplicity": 1,
                "target_product": 3,
                "constraints": {"prime_only": True, "count": 1},
            }
        ],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 2,
                "target_product": 411522630041,
                "constraints": {"prime_only": True, "count": 2},
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["builder_readiness"] == "not-ready"
    assert report["builder_ready_block_ids"] == []
    assert report["builder_missing_unknown_block_ids"] == ["unknown-exp1-slots"]


def test_support_realization_reports_builder_readiness_ready() -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 6,
        "target_generator": 6,
        "shape_signature": [[], []],
        "slot_count": 2,
        "exponent_multiset": [1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 2,
                "target_product": 6,
                "constraints": {
                    "known_divisors": [2, 3]
                },
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["builder_readiness"] == "ready"
    assert report["builder_ready_block_ids"] == [
        "unknown-exp1-slots::known-divisor-1",
        "unknown-exp1-slots::known-divisor-2",
    ]
    assert report["builder_missing_unknown_block_ids"] == []
