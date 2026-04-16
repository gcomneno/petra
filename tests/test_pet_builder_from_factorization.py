from __future__ import annotations

import json
from pathlib import Path

from pet.builder_from_factorization import build_from_factorization_pipeline


def _write_factor_file(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "factors.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_pet_builder_from_factorization_runs_noncanonical_small_case(tmp_path: Path) -> None:
    path = _write_factor_file(tmp_path, {"factors": [[3, 1], [5, 1], [7, 1]]})

    report = build_from_factorization_pipeline(path, tmp_path / "artifacts")

    assert report["schema"] == "pet-builder-from-factorization-v0"
    assert report["input_n"] == 105
    assert report["support_report"]["builder_readiness"] == "ready"
    assert report["support_report"]["exact_target_match"] is True
    assert report["final_build_output"]["build_status"] == "built"
    assert report["final_build_output"]["built_pet_object"]["artifact_count"] == 3


def test_pet_builder_from_factorization_runs_hostile_known_case(tmp_path: Path) -> None:
    p = 100000007
    q = 100000429
    n = p * q
    path = _write_factor_file(tmp_path, {"factors": [[p, 1], [q, 1]]})

    report = build_from_factorization_pipeline(path, tmp_path / "artifacts")

    assert report["schema"] == "pet-builder-from-factorization-v0"
    assert report["input_n"] == n
    assert report["support_report"]["builder_readiness"] == "ready"
    assert report["support_report"]["exact_target_match"] is True
    assert report["final_build_output"]["build_status"] == "built"
    assert report["final_build_output"]["built_pet_object"]["artifact_count"] == 2


def test_pet_builder_from_factorization_runs_canonical_large_power_case(tmp_path: Path) -> None:
    n = 2**200
    path = _write_factor_file(tmp_path, {"factors": [[2, 200]]})

    report = build_from_factorization_pipeline(path, tmp_path / "artifacts")

    assert report["schema"] == "pet-builder-from-factorization-v0"
    assert report["input_n"] == n
    assert report["support_report"]["builder_readiness"] == "ready"
    assert report["support_report"]["exact_target_match"] is True
    assert report["final_build_output"]["build_status"] == "built"
    assert report["final_build_output"]["built_pet_object"]["artifact_count"] == 1
