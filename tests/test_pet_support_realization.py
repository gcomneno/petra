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
    assert report["reconstructed_target_n"] == 1234567890
    assert report["exact_target_match"] is True
    assert report["realization_status"] == "exact-from-block-products"


def test_support_realization_keeps_partial_build_payload_pending() -> None:
    payload = _run_partial_build_payload(1234567890)
    report = _run_json_file_command(TOOL, payload)

    assert report["source_schema"] == "pet-build-from-int-v2"
    assert report["target_generator"] == 4620
    assert report["realization_status"] == "pending"
    assert "reconstructed_target_n" not in report
    assert "exact_target_match" not in report


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

    assert report["reconstructed_target_n"] != 1234567890
    assert report["exact_target_match"] is False
    assert report["realization_status"] == "block-product-mismatch"
