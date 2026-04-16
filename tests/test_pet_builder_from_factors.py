from __future__ import annotations

import json
from pathlib import Path

from pet.builder_from_factors import build_from_factors_pipeline


def _write_factor_file(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "factors.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_pet_builder_from_factors_runs_smoke_case_for_30(tmp_path: Path) -> None:
    path = _write_factor_file(tmp_path, {"factors": [[2, 1], [3, 1], [5, 1]]})

    report = build_from_factors_pipeline(path, tmp_path / "artifacts")

    assert report["schema"] == "pet-builder-from-factors-v0"
    assert report["input_n"] == 30
    assert report["support_report"]["builder_readiness"] == "ready"
    assert report["support_report"]["exact_target_match"] is True
    assert report["final_build_output"]["build_status"] == "built"
    assert report["final_build_output"]["built_pet_object"]["artifact_count"] == 3


def test_pet_builder_from_factors_runs_large_power_case(tmp_path: Path) -> None:
    n = 2**200
    path = _write_factor_file(tmp_path, {"factors": [[2, 200]]})

    report = build_from_factors_pipeline(path, tmp_path / "artifacts")

    assert report["schema"] == "pet-builder-from-factors-v0"
    assert report["input_n"] == n
    assert report["support_report"]["builder_readiness"] == "ready"
    assert report["support_report"]["exact_target_match"] is True
    assert report["final_build_output"]["build_status"] == "built"
    assert report["final_build_output"]["built_pet_object"]["artifact_count"] == 1


def test_pet_builder_from_factors_runs_large_wide_support_case(tmp_path: Path) -> None:
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
    n = 1
    for p in primes:
        n *= p
    path = _write_factor_file(tmp_path, {"factors": [[p, 1] for p in primes]})

    report = build_from_factors_pipeline(path, tmp_path / "artifacts")

    assert report["schema"] == "pet-builder-from-factors-v0"
    assert report["input_n"] == n
    assert report["support_report"]["builder_readiness"] == "ready"
    assert report["support_report"]["exact_target_match"] is True
    assert report["final_build_output"]["build_status"] == "built"
    assert report["final_build_output"]["built_pet_object"]["artifact_count"] == 14
