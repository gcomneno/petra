import json
import subprocess
import sys

import pytest


def _run_cli(*args: str) -> str:
    return subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )


def test_cli_build_from_int_smoke():
    out = _run_cli("build-from-int", "360")

    assert "input_n = 360" in out
    assert "factors = 2^3 * 3^2 * 5" in out
    assert "target_n = 360" in out
    assert "steps = 5" in out
    assert "2 --INC(p=2,e=1)--> 4" in out
    assert "72 --NEW(p=5)--> 360" in out


def test_cli_build_from_int_json_smoke():
    out = _run_cli("build-from-int", "240", "--json")
    payload = json.loads(out)

    assert payload["input_n"] == 240
    assert payload["factors"] == [[2, 4], [3, 1], [5, 1]]
    assert payload["target_n"] == 240
    assert payload["steps"] == 5
    assert payload["path"][0]["source_n"] == 2
    assert payload["path"][-1]["target_n"] == 240


def test_cli_build_from_int_rejects_noncanonical_support():
    proc = subprocess.run(
        [sys.executable, "-m", "pet.cli", "build-from-int", "28"],
        text=True,
        capture_output=True,
    )
    assert proc.returncode != 0
    assert "NEW-canonical" in proc.stderr

def test_cli_build_from_int_json_partial_noncanonical_support():
    out = _run_cli("build-from-int", "1234567890", "--allow-non-canonical-support", "--json")
    payload = json.loads(out)

    assert payload["schema"] == "pet-build-from-int-v2"
    assert payload["input_n"] == 1234567890
    assert payload["target_generator"] == 4620
    assert payload["mode"] == "canonical-build+support-realization"
    assert payload["build_status"] == "partial"

    assert payload["phase1"]["status"] == "ok"
    assert payload["phase1"]["target_n"] == 4620
    assert payload["phase1"]["target_generator"] == 4620
    assert payload["phase1"]["steps"] == 5
    assert payload["phase1"]["path"][0]["source_n"] == 2
    assert payload["phase1"]["path"][-1]["target_n"] == 4620

    assert payload["phase2"]["status"] == "pending"
    assert payload["phase2"]["same_pet_shape"] is True
    assert payload["phase2"]["reached_target"] is False
    assert "not yet implemented" in payload["phase2"]["message"]


def test_cli_build_from_int_flag_keeps_canonical_case_normal():
    out = _run_cli("build-from-int", "4620", "--allow-non-canonical-support", "--json")
    payload = json.loads(out)

    assert payload["input_n"] == 4620
    assert payload["factors"] == [[2, 2], [3, 1], [5, 1], [7, 1], [11, 1]]
    assert payload["target_n"] == 4620
    assert payload["target_generator"] == 4620
    assert payload["steps"] == 5
    assert "build_status" not in payload
    assert "phase1" not in payload
    assert "phase2" not in payload


def test_cli_build_from_int_json_partial_noncanonical_support_for_18():
    out = _run_cli("build-from-int", "18", "--allow-non-canonical-support", "--json")
    payload = json.loads(out)

    assert payload["schema"] == "pet-build-from-int-v2"
    assert payload["input_n"] == 18
    assert payload["target_generator"] == 12
    assert payload["mode"] == "canonical-build+support-realization"
    assert payload["build_status"] == "partial"
    assert payload["phase1"]["status"] == "ok"
    assert payload["phase1"]["target_n"] == 12
    assert payload["phase1"]["target_generator"] == 12
    assert payload["phase2"]["status"] == "pending"
    assert payload["phase2"]["same_pet_shape"] is True
    assert payload["phase2"]["reached_target"] is False


def test_cli_builder_from_int_json_for_30():
    out = _run_cli("builder-from-int", "30", "--json")
    payload = json.loads(out)

    assert payload["schema"] == "pet-builder-from-int-v0"
    assert payload["input_n"] == 30
    assert payload["builder_execution"]["execution_status"] == "executed"
    assert payload["final_build_output"]["build_status"] == "built"
    assert payload["final_build_output"]["built_pet_object"]["assembly_status"] == "assembled"
    assert payload["final_build_output"]["built_pet_object"]["component_count"] == 3


def test_cli_builder_from_int_json_for_18():
    out = _run_cli("builder-from-int", "18", "--json")
    payload = json.loads(out)

    assert payload["schema"] == "pet-builder-from-int-v0"
    assert payload["input_n"] == 18
    assert payload["builder_execution"]["execution_status"] == "executed"
    assert payload["final_build_output"]["build_status"] == "built"
    assert payload["final_build_output"]["built_pet_object"]["assembly_status"] == "assembled"
    assert payload["final_build_output"]["built_pet_object"]["component_count"] == 2
