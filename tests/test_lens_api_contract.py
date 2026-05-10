from __future__ import annotations

import json

from pet.lens_api import API_VERSION, LENS_ID, analyze


def test_lens_api_reports_stable_identity() -> None:
    result = analyze({})

    assert result["lens_id"] == LENS_ID
    assert result["api_version"] == API_VERSION
    assert result["lens_id"] == "pet"
    assert result["api_version"] == "pet.lens.v1"


def test_lens_api_empty_context_returns_valid_fallback() -> None:
    result = analyze({})

    assert result == {
        "lens_id": "pet",
        "api_version": "pet.lens.v1",
        "target": "unknown",
        "hints": [],
        "candidate_plans": [],
        "resources": [],
        "confidence": "none",
        "reason": "insufficient context for PET advisory",
    }


def test_lens_api_preserves_string_target_in_fallback() -> None:
    result = analyze({"target": "bucket:00"})

    assert result["target"] == "bucket:00"
    assert result["candidate_plans"] == []
    assert result["reason"] == "insufficient context for PET advisory"


def test_lens_api_invalid_context_returns_explicit_fallback() -> None:
    result = analyze(None)

    assert result["target"] == "unknown"
    assert result["candidate_plans"] == []
    assert result["confidence"] == "none"
    assert result["reason"] == "invalid context for PET advisory"


def test_lens_api_output_is_json_serializable() -> None:
    result = analyze({"target": "bucket:00"})

    encoded = json.dumps(result, sort_keys=True)

    assert "pet.lens.v1" in encoded


def test_lens_api_is_deterministic() -> None:
    context = {"target": "bucket:00"}

    assert analyze(context) == analyze(context)
