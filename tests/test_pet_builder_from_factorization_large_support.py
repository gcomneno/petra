from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

from pet.builder_from_factorization import (
    build_cli_payload_from_factorization_file,
    build_from_factorization_pipeline,
)


def test_build_cli_payload_from_factorization_large_known_support_is_fast_enough(tmp_path: Path) -> None:
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"factors": [[1000000007, 1], [1000000009, 1]]}), encoding="utf-8")

    t0 = perf_counter()
    payload = build_cli_payload_from_factorization_file(spec)
    t1 = perf_counter()

    assert payload["schema"] == "pet-support-realization-input-v0"
    assert payload["input_n"] == 1000000007 * 1000000009
    assert payload["target_generator"] == 6
    assert payload["shape_signature"] is None
    assert (t1 - t0) < 2.0


def test_build_from_factorization_pipeline_large_known_support_smoke(tmp_path: Path) -> None:
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"factors": [[1000000007, 1], [1000000009, 1]]}), encoding="utf-8")

    report = build_from_factorization_pipeline(spec, tmp_path / "out")

    assert report["schema"] == "pet-builder-from-factorization-v0"
    assert report["input_n"] == 1000000007 * 1000000009
    assert report["final_build_output"]["build_status"] == "built"
    assert report["support_report"]["exact_target_match"] is True
