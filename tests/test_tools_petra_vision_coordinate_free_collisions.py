from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from math import factorial
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPOSITORY_ROOT / "tools" / "research" / "petra_vision_coordinate_free_collisions.py"
EXPECTED_CODES = ["G(G(G(T)),G(T,T))", "G(G(T,T),G(G(T)))"]
READERS = ("global_multiset", "component_multiset")


def _load_tool_module():
    spec = importlib.util.spec_from_file_location(
        "petra_vision_coordinate_free_collisions", TOOL_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load collision-semantics tool")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tool = _load_tool_module()


def test_frozen_v1_regression_and_exact_coordinate_free_collision() -> None:
    report = tool.analyze_experiment()
    phase_1 = report["corpora"]["phase_1"]

    for reader in READERS:
        result = phase_1["readers"][reader]
        assert result["distinct_signatures"] == 109
        assert len(result["collisions"]) == 1
        collision = result["collisions"][0]
        assert collision["positions"] == [23, 41]
        assert collision["corpus_indices"] == [23, 41]
        assert collision["phase_1_indices"] == [23, 41]
        assert collision["shape_codes"] == EXPECTED_CODES

    assert tool.v1.analyze_experiment()["readers"]["global_multiset"]["collision_groups"] == [[23, 41]]
    assert tool.v1.analyze_experiment()["readers"]["component_multiset"]["collision_groups"] == [[23, 41]]


def test_frozen_protocol_constants_and_reader_definitions() -> None:
    report = tool.analyze_experiment()
    assert tool.v1.EULER_DENOMINATOR == 8
    assert tool.v1.SAMPLE_STEPS == (1, 2, 4, 8, 16, 32)
    assert report["protocol"]["euler_denominator"] == 8
    assert report["protocol"]["sample_steps"] == [1, 2, 4, 8, 16, 32]
    for reader in READERS:
        assert "exactly when" in report["corpora"]["phase_1"]["readers"][reader]["equivalence_definition"]


def test_translation_reflection_and_component_reordering_results() -> None:
    report = tool.analyze_experiment()
    transforms = report["derived_transformations"]
    geometries, _annotations = tool._corpus_entries("phase_1")
    expected_candidates = sum(
        len(tool.component_permutation_geometries(geometry))
        for geometry in geometries
    )
    expected_raw_specifications = sum(
        factorial(len(tool.normalized_component_shapes(geometry)))
        for geometry in geometries
    )

    counts = transforms["counts"]
    assert counts["source_geometries"] == len(geometries)
    assert counts["translation_cases"] == len(geometries) * len(tool.FIXED_TRANSLATIONS)
    assert counts["reflection_cases"] == len(geometries)
    assert counts["raw_labelled_permutation_specifications"] == expected_raw_specifications
    assert counts["candidate_cases"] == expected_candidates == 22917
    assert counts["valid_reconstructed_geometries"] == expected_candidates
    assert counts["invalid_or_rejected_cases"] == 0
    assert counts["duplicate_generated_geometries"] == 0
    assert counts["unique_valid_generated_geometries"] == expected_candidates
    assert counts["dynamically_evaluated_cases"] == expected_candidates
    assert counts["duplicate_labelled_permutation_specifications"] == (
        expected_raw_specifications - expected_candidates
    )
    assert transforms["rejection_reasons"] == {}
    assert all(
        value == counts["translation_cases"]
        for value in transforms["translation_matches"].values()
    )
    assert transforms["reflection_matches"]["global_multiset"] == 26
    assert transforms["reflection_matches"]["component_multiset"] == 26
    assert all(
        transforms["per_reader_signature_matches"][reader] == expected_candidates
        for reader in READERS
    )
    # The #23 family is selected after the general replay, not as its scope.
    source_23 = transforms["per_source"][23]
    assert source_23["valid_reconstructed_geometries"] == 840
    assert all(
        source_23["per_reader_signature_matches"][reader] == 840
        for reader in READERS
    )


def test_component_permutation_generator_is_deterministic_and_valid() -> None:
    geometries, _annotations = tool._corpus_entries("phase_1")
    source = geometries[23]
    first = tool.component_permutation_geometries(source)
    second = tool.component_permutation_geometries(source)

    assert first == second
    assert len(first) == tool.component_permutation_count(source) == 840
    original_shapes = sorted(tool.normalized_component_shapes(source))
    assert all(sorted(tool.normalized_component_shapes(item)) == original_shapes for item in first)


def test_transformations_reject_malformed_inputs() -> None:
    geometries, _annotations = tool._corpus_entries("phase_1")
    components = tool.normalized_component_shapes(geometries[23])

    with pytest.raises(ValueError, match="permutation"):
        tool.reconstruct_component_geometry(components, (0,))
    with pytest.raises(TypeError, match="displacement"):
        tool.translate_geometry(geometries[23], (1, "bad"))
    with pytest.raises(ValueError, match="overlap"):
        tool.reconstruct_component_geometry(
            components,
            tuple(range(len(components))),
            tuple((0, 0) for _component in components),
        )
    with pytest.raises(ValueError, match="normalized"):
        tool.reconstruct_component_geometry(
            (((1, 0),),),
            (0,),
        )


def test_collision_classification_retains_indices_codes_and_all_collisions() -> None:
    report = tool.analyze_experiment()
    classifications = report["collision_classification"]

    assert len(classifications["phase_1"]) == 2
    for item in classifications["phase_1"]:
        assert item["corpus_indices"] == [23, 41]
        assert item["shape_codes"] == EXPECTED_CODES
        assert item["classification"] == "structural"
        assert item["explicit_invariants"]
        assert item["is_known_phase_1_23_41_class"] is True
    for corpus_name, corpus in report["corpora"].items():
        all_non_singleton = [
            collision
            for reader in READERS
            for collision in corpus["readers"][reader]["collisions"]
        ]
        assert len(classifications[corpus_name]) == len(all_non_singleton)
        assert report["additional_collisions"][corpus_name] == [
            item for item in classifications[corpus_name]
            if not item["is_known_phase_1_23_41_class"]
        ]
    # A new collision changes the derived empty result rather than disappearing.
    assert report["additional_collisions"]["phase_1"] == []
    synthetic_extra = {"is_known_phase_1_23_41_class": False, "classification": "unclassified"}
    assert tool._derive_additional_collisions([
        {"is_known_phase_1_23_41_class": True}, synthetic_extra,
    ]) == [synthetic_extra]


def test_extended_classification_uses_phase_1_transform_sources() -> None:
    report = tool.analyze_experiment()
    transforms = dict(report["derived_transformations"])
    per_source = [dict(item) for item in transforms["per_source"]]
    transforms["per_source"] = per_source

    for position, item in enumerate(per_source):
        if item["source_position"] not in {23, 41}:
            continue
        changed = dict(item)
        matches = dict(changed["per_reader_signature_matches"])
        matches["global_multiset"] -= 1
        changed["per_reader_signature_matches"] = matches
        per_source[position] = changed

    for source_position in (25, 45):
        untouched = next(
            item for item in per_source
            if item["source_position"] == source_position
        )
        assert (
            untouched["per_reader_signature_matches"]["global_multiset"]
            == untouched["valid_reconstructed_geometries"]
        )

    geometries, _annotations = tool._corpus_entries("extended")
    classifications = tool._classify_collisions(
        "extended",
        report["corpora"]["extended"],
        geometries,
        transforms,
    )
    result = next(
        item for item in classifications
        if item["reader"] == "global_multiset"
    )

    assert result["positions"] == [25, 45]
    assert result["phase_1_indices"] == [23, 41]
    assert result["transformation_source_phase_1_indices"] == [23, 41]
    assert result["classification"] == "unclassified"


def test_phase_held_out_extended_and_controls_are_reported_separately() -> None:
    report = tool.analyze_experiment()
    expected = {"phase_1": (110, 109), "held_out": (27, 27), "extended": (137, 136)}
    for corpus, (size, distinct) in expected.items():
        result = report["corpora"][corpus]
        assert result["size"] == size
        assert all(result["readers"][reader]["distinct_signatures"] == distinct for reader in READERS)
        assert result["controls"]["oriented"]["role"].startswith("control only")
        assert result["controls"]["null_oriented"]["role"].startswith("control only")
    assert report["corpora"]["held_out"]["readers"]["global_multiset"]["collisions"] == []
    assert report["corpora"]["extended"]["readers"]["global_multiset"]["collisions"][0]["shape_codes"] == EXPECTED_CODES


def test_replay_identity_audit_and_reporting_metadata_negative_control(monkeypatch) -> None:
    report = tool.analyze_experiment()
    audit = report["identity_channel_audit"]
    assert report["deterministic_replay"] is True
    assert audit["ast_passed"] is True
    assert audit["ast_violations"] == {}
    assert audit["parameter_allow_list"]["coordinate_free_signatures"] == ["geometry"]
    assert audit["parameter_allow_list"]["_equivalence_groups"] == ["records", "reader"]
    assert audit["reporting_join_after_dynamic_records"] is True
    assert audit["coordinate_free_claim_readers"] == list(READERS)
    assert audit["control_readers_excluded_from_coordinate_free_claim"] == ["oriented", "null_oriented"]
    geometries, annotations = tool._corpus_entries("phase_1")
    original = tool.coordinate_free_signatures
    calls = 0

    def counted(geometry):
        nonlocal calls
        calls += 1
        return original(geometry)

    monkeypatch.setattr(tool, "coordinate_free_signatures", counted)
    control = tool.identity_channel_audit(geometries, annotations)["negative_annotation_control"]
    assert calls == 2 * len(geometries)
    assert control == {
        "annotations_changed": True,
        "independent_complete_dynamic_recomputations": 2,
        "signatures_unchanged": True,
        "class_membership_unchanged": True,
        "reporting_output_changed": True,
    }


def test_cli_json_is_reproducible_and_write_json_is_sorted(tmp_path: Path) -> None:
    command = [sys.executable, str(TOOL_PATH), "--json"]
    first = subprocess.run(command, cwd=REPOSITORY_ROOT, check=True, capture_output=True, text=True)
    second = subprocess.run(command, cwd=REPOSITORY_ROOT, check=True, capture_output=True, text=True)
    destination = tmp_path / "evidence.json"
    written = subprocess.run(
        [sys.executable, str(TOOL_PATH), "--write-json", str(destination)],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert first.stdout == second.stdout
    assert first.stderr == second.stderr == written.stderr == ""
    assert first.stdout.endswith("\n")
    assert destination.read_text(encoding="utf-8") == first.stdout
    assert json.loads(first.stdout) == tool.analyze_experiment()


def test_cli_returns_nonzero_when_scientific_invariants_are_falsified(monkeypatch) -> None:
    original = tool.analyze_experiment()
    broken = dict(original)
    broken["deterministic_replay"] = False
    monkeypatch.setattr(tool, "analyze_experiment", lambda: broken)
    assert tool.main([]) == 1
