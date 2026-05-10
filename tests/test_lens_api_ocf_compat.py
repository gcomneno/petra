from __future__ import annotations

import json
from typing import Any

from pet.lens_api import analyze


RESULT_KEYS = {
    "lens_id",
    "api_version",
    "target",
    "hints",
    "candidate_plans",
    "resources",
    "confidence",
    "reason",
}

CANDIDATE_PLAN_KEYS = {
    "layer_id",
    "codec_text",
    "stream_codecs",
    "note",
}


def numeric_context() -> dict[str, Any]:
    return {
        "target": "bucket:00",
        "scope": "dir-autopick",
        "metrics": {
            "numeric_ratio": 0.75,
            "sample_size": 2048,
        },
        "available_layers": ["TEXT", "NUMS"],
        "available_codecs": ["raw", "num_v1", "num_v2"],
        "constraints": {
            "max_candidates": 3,
        },
    }


def assert_lens_result_shape(result: dict[str, Any]) -> None:
    assert set(result) == RESULT_KEYS
    assert result["lens_id"] == "pet"
    assert result["api_version"] == "pet.lens.v1"
    assert isinstance(result["target"], str)
    assert isinstance(result["hints"], list)
    assert isinstance(result["candidate_plans"], list)
    assert isinstance(result["resources"], list)
    assert isinstance(result["confidence"], str)
    assert isinstance(result["reason"], str)


def assert_candidate_plan_shape(plan: dict[str, Any]) -> None:
    assert set(plan) == CANDIDATE_PLAN_KEYS
    assert isinstance(plan["layer_id"], str)
    assert isinstance(plan["codec_text"], str)
    assert isinstance(plan["stream_codecs"], dict)
    assert isinstance(plan["note"], str)


def test_empty_context_result_is_ocf_lens_result_shaped() -> None:
    result = analyze({})

    assert_lens_result_shape(result)
    assert result["candidate_plans"] == []
    assert result["resources"] == []
    assert result["confidence"] == "none"


def test_numeric_context_result_is_ocf_lens_result_shaped() -> None:
    result = analyze(numeric_context())

    assert_lens_result_shape(result)
    assert len(result["candidate_plans"]) == 1

    plan = result["candidate_plans"][0]

    assert_candidate_plan_shape(plan)


def test_numeric_candidate_plan_is_mappable_to_ocf_lens_candidate_plan() -> None:
    context = numeric_context()
    result = analyze(context)
    plan = result["candidate_plans"][0]

    assert plan["layer_id"] in context["available_layers"]
    assert plan["codec_text"] in context["available_codecs"]
    assert plan["stream_codecs"] == {"NUMS": "num_v2"}

    for layer_id, codec_text in plan["stream_codecs"].items():
        assert layer_id in context["available_layers"]
        assert codec_text in context["available_codecs"]


def test_numeric_candidate_plan_preserves_advisory_boundary_note() -> None:
    result = analyze(numeric_context())
    plan = result["candidate_plans"][0]

    assert "PET advisory only" in plan["note"]
    assert "OCF autopick must measure and verify" in plan["note"]


def test_lens_result_is_json_serializable_for_ocf_transport() -> None:
    fallback = analyze({})
    numeric = analyze(numeric_context())

    json.dumps(fallback, sort_keys=True)
    json.dumps(numeric, sort_keys=True)


def test_lens_result_is_deterministic_for_ocf_caching() -> None:
    context = numeric_context()

    assert analyze(context) == analyze(context)


def test_unavailable_layer_produces_no_candidate_plan() -> None:
    context = numeric_context()
    context["available_layers"] = ["TEXT"]

    result = analyze(context)

    assert_lens_result_shape(result)
    assert result["candidate_plans"] == []
    assert result["resources"] == []
    assert result["confidence"] == "none"


def test_unavailable_codec_produces_no_candidate_plan() -> None:
    context = numeric_context()
    context["available_codecs"] = ["raw", "num_v1"]

    result = analyze(context)

    assert_lens_result_shape(result)
    assert result["candidate_plans"] == []
    assert result["resources"] == []
    assert result["confidence"] == "none"


def test_max_candidates_is_respected_for_ocf_candidate_list() -> None:
    context = numeric_context()
    context["constraints"] = {
        "max_candidates": 0,
    }

    result = analyze(context)

    assert_lens_result_shape(result)
    assert result["candidate_plans"] == []
    assert result["resources"] == []
    assert result["confidence"] == "none"


def test_every_hint_is_json_object_shaped() -> None:
    result = analyze(numeric_context())

    assert result["hints"]

    for hint in result["hints"]:
        assert isinstance(hint, dict)
        assert isinstance(hint["kind"], str)
        assert isinstance(hint["message"], str)
