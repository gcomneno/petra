import json
import subprocess
import sys


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pet.cli", *args],
        check=False,
        text=True,
        capture_output=True,
    )


def _run_json(*args: str) -> dict:
    result = _run_cli(*args, "--json")
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_opaque_recursive_lens_json_reports_minimal_window_for_patata() -> None:
    data = _run_json(
        "opaque-recursive-lens",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--depth",
        "3",
    )

    assert data["digits"] == 5
    assert data["bit_length"] == 14
    assert data["depth"] == 3

    recurrence = data["recurrence"]
    assert recurrence["status"] == "minimal-window"
    assert recurrence["level_count"] == 1
    assert recurrence["available_level_count"] == 1
    assert recurrence["center_shape_sequence"] == ["((), (), ())"]
    assert recurrence["center_generator_sequence"] == [30]
    assert recurrence["edge_sequence"] == [2]

    level = data["levels"][0]
    assert level["available"] is True
    assert level["visible_form"] == "pre-pressure-edge"
    assert level["visible_shape"] == "thin-ramp"
    assert level["edge_k"] == 2
    assert level["boundary"] == "2/3"
    assert level["center_lens"]["lens_kind"] == "flat-three-leaf-center"
    assert level["center_lens"]["suggested_window"]["k_range"] == "1..2"


def test_opaque_recursive_lens_text_is_monkey_friendly() -> None:
    result = _run_cli(
        "opaque-recursive-lens",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--depth",
        "3",
    )

    assert result.returncode == 0, result.stderr
    assert "PET OPAQUE RECURSIVE LENS" in result.stdout
    assert "Recursive zoom levels" in result.stdout
    assert "level 0" in result.stdout
    assert "center_lens_kind = flat-three-leaf-center" in result.stdout
    assert "suggested_window = k[1,2]" in result.stdout
    assert "Recurrence" in result.stdout
    assert "status = minimal-window" in result.stdout
    assert "claim = PET recursive zoom lens only; this does not factor N" in result.stdout


def test_opaque_recursive_lens_rejects_non_positive_depth() -> None:
    result = _run_cli(
        "opaque-recursive-lens",
        "10403",
        "--excluded-support-limit",
        "16",
        "--depth",
        "0",
    )

    assert result.returncode != 0
    assert "--depth expects integers >= 1" in result.stderr


def test_opaque_recursive_lens_keeps_zoom_inside_suggested_window() -> None:
    rsa250 = (
        "2140324650240744961264423072839333563008614715144755017797754920881418023447140136643345519095804679610992851872470914587687396261921557363047454770520805119056493106687691590019759405693457452230589325976697471681738069364894699871578494975937497937"
    )

    data = _run_json(
        "opaque-recursive-lens",
        rsa250,
        "--max-generator-count",
        "40",
        "--excluded-support-limit",
        "100000000",
        "--max-move-span",
        "5",
        "--depth",
        "2",
    )

    assert data["levels"][0]["center_lens"]["suggested_window"]["k_range"] == "28..30"

    if len(data["levels"]) > 1 and data["levels"][1]["available"]:
        level1 = data["levels"][1]
        assert level1["input_window"]["k_range"] == "28..30"
        selected_start, selected_end = [
            int(part)
            for part in level1["selected_band"]["k_range"].split("..")
        ]
        assert selected_start <= 30
        assert selected_end >= 28
        assert level1["window_filter"] == "overlap"
    else:
        assert data["recurrence"]["status"] == "terminal-window"
        assert data["levels"][1]["available"] is False
        assert data["levels"][1]["reason"] == "no magnetic band overlaps active window"

def test_opaque_recursive_lens_terminal_reduction_proposes_semiprime_projection() -> None:
    rsa250 = (
        "2140324650240744961264423072839333563008614715144755017797754920881418023447140136643345519095804679610992851872470914587687396261921557363047454770520805119056493106687691590019759405693457452230589325976697471681738069364894699871578494975937497937"
    )

    data = _run_json(
        "opaque-recursive-lens",
        rsa250,
        "--max-generator-count",
        "40",
        "--excluded-support-limit",
        "100000000",
        "--max-move-span",
        "5",
        "--depth",
        "2",
        "--terminal-reduction",
    )

    reduction = data["terminal_reduction"]
    assert reduction["available"] is True
    assert reduction["status"] == "proposal"
    assert reduction["source_status"] == "terminal-window"
    assert reduction["source_edge_k"] == 30
    assert reduction["source_window"]["k_range"] == "28..30"
    assert reduction["source_visible_form"] == "pre-pressure-edge"
    assert reduction["source_visible_shape"] == "ramp-band"
    assert reduction["target_edge_k"] == 2
    assert reduction["reduction_kind"] == "semiprime-projection"
    assert reduction["recommended_classic_handoff"] is False
    assert "does not factor N" in reduction["claim"]


def test_opaque_recursive_lens_terminal_reduction_reports_unavailable_when_not_terminal() -> None:
    data = _run_json(
        "opaque-recursive-lens",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--depth",
        "3",
        "--terminal-reduction",
    )

    reduction = data["terminal_reduction"]
    assert reduction["available"] is False
    assert reduction["reason"] == "recursive lens did not stop at a terminal window"
    assert "does not factor N" in reduction["claim"]


def test_opaque_recursive_lens_terminal_reduction_text_is_explicitly_non_factorizing() -> None:
    rsa250 = (
        "2140324650240744961264423072839333563008614715144755017797754920881418023447140136643345519095804679610992851872470914587687396261921557363047454770520805119056493106687691590019759405693457452230589325976697471681738069364894699871578494975937497937"
    )

    result = _run_cli(
        "opaque-recursive-lens",
        rsa250,
        "--max-generator-count",
        "40",
        "--excluded-support-limit",
        "100000000",
        "--max-move-span",
        "5",
        "--depth",
        "2",
        "--terminal-reduction",
    )

    assert result.returncode == 0, result.stderr
    assert "PET terminal reduction lens" in result.stdout
    assert "available = yes" in result.stdout
    assert "status = proposal" in result.stdout
    assert "source_edge_k = 30" in result.stdout
    assert "source_window = k[28,30]" in result.stdout
    assert "target_edge_k = 2" in result.stdout
    assert "reduction_kind = semiprime-projection" in result.stdout
    assert "recommended_classic_handoff = no" in result.stdout
    assert "claim = PET reduction lens only; this does not factor N" in result.stdout

def test_opaque_recursive_lens_branch_recursion_reuses_fork_follow_window() -> None:
    n50b = "2000000000900146713649308342226750098973706617969"

    data = _run_json(
        "opaque-recursive-lens",
        n50b,
        "--max-generator-count",
        "40",
        "--excluded-support-limit",
        "100000000",
        "--max-move-span",
        "5",
        "--depth",
        "3",
        "--branch-recursion",
        "DROP",
    )

    level0 = data["levels"][0]
    assert level0["available"] is True
    assert level0["recursion_source"] == "fork-follow"
    assert level0["branch_followup"]["source_branch"] == "DROP-side"
    assert level0["branch_window"]["k_range"] == "2..3"
    assert level0["edge_k"] == 2
    assert level0["visible_form"] == "fork-follow"
    assert level0["visible_shape"] == "branch-window-collapse"

    level1 = data["levels"][1]
    assert level1["available"] is True
    assert level1["input_window"]["k_range"] == "2..3"
    assert level1["edge_k"] == 2
    assert level1["selected_band"]["k_range"] == "2..3"
    assert level1["center_lens"]["lens_kind"] == "projected-center-shape"

    assert data["recurrence"]["status"] == "minimal-window"
    assert data["recurrence"]["edge_sequence"] == [2, 2, 1]


def test_opaque_recursive_lens_branch_recursion_text_is_monkey_friendly() -> None:
    n50b = "2000000000900146713649308342226750098973706617969"

    result = _run_cli(
        "opaque-recursive-lens",
        n50b,
        "--max-generator-count",
        "40",
        "--excluded-support-limit",
        "100000000",
        "--max-move-span",
        "5",
        "--depth",
        "3",
        "--branch-recursion",
        "DROP",
    )

    assert result.returncode == 0, result.stderr
    assert "recursion_source = fork-follow" in result.stdout
    assert "source_branch = DROP-side" in result.stdout
    assert "branch_window = k[2,3]" in result.stdout
    assert "input_window = k[2,3]" in result.stdout
    assert "visible_shape = edge-point" in result.stdout
    assert "edge_k = 2" in result.stdout
    assert "selected_band = fog-return DROP k[2..3]" in result.stdout
    assert "status = minimal-window" in result.stdout

def test_opaque_recursive_lens_anchor_field_marks_thin_ramp_as_strong() -> None:
    data = _run_json(
        "opaque-recursive-lens",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--depth",
        "3",
        "--anchor-field",
    )

    field = data["anchor_field_payload"]
    assert field["available"] is True
    assert field["source_level"] == 0
    assert field["source_band"]["kind"] == "pressure-entry"
    assert field["source_band"]["move"] == "NEW"
    assert field["source_band"]["k_range"] == "1..2"
    assert field["source_form"] == "pre-pressure-edge:thin-ramp"
    assert field["edge_k"] == 2
    assert field["center_lens_kind"] == "flat-three-leaf-center"
    assert field["center_generator"] == 30
    assert field["anchor_status"] == "strong"
    assert field["binding_strength"] == "high"
    assert field["classic_bridge_recommendation"] == "recommended"
    assert "does not factor N" in field["claim"]


def test_opaque_recursive_lens_anchor_field_marks_edge_point_as_weak() -> None:
    n50b = "2000000000900146713649308342226750098973706617969"

    data = _run_json(
        "opaque-recursive-lens",
        n50b,
        "--max-generator-count",
        "40",
        "--excluded-support-limit",
        "100000000",
        "--max-move-span",
        "5",
        "--depth",
        "3",
        "--branch-recursion",
        "DROP",
        "--anchor-field",
    )

    field = data["anchor_field_payload"]
    assert field["available"] is True
    assert field["source_level"] == 1
    assert field["source_band"]["kind"] == "fog-return"
    assert field["source_band"]["move"] == "DROP"
    assert field["source_band"]["k_range"] == "2..3"
    assert field["source_form"] == "scale-transition-edge:edge-point"
    assert field["edge_k"] == 2
    assert field["center_lens_kind"] == "projected-center-shape"
    assert field["center_generator"] == 430080
    assert field["anchor_status"] == "weak"
    assert field["binding_strength"] == "low"
    assert field["classic_bridge_recommendation"] == "not-recommended"
    assert "does not factor N" in field["claim"]


def test_opaque_recursive_lens_anchor_field_text_is_monkey_friendly() -> None:
    result = _run_cli(
        "opaque-recursive-lens",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--depth",
        "3",
        "--anchor-field",
    )

    assert result.returncode == 0, result.stderr
    assert "PET anchor field" in result.stdout
    assert "source_form = pre-pressure-edge:thin-ramp" in result.stdout
    assert "center_lens_kind = flat-three-leaf-center" in result.stdout
    assert "anchor_status = strong" in result.stdout
    assert "binding_strength = high" in result.stdout
    assert "classic_bridge_recommendation = recommended" in result.stdout
    assert "claim = PET anchor-field analysis only; this does not factor N" in result.stdout

def test_opaque_recursive_lens_auto_rampifies_edge_point_minimal_window() -> None:
    n50b = "2000000000900146713649308342226750098973706617969"

    data = _run_json(
        "opaque-recursive-lens",
        n50b,
        "--max-generator-count",
        "40",
        "--excluded-support-limit",
        "100000000",
        "--max-move-span",
        "5",
        "--depth",
        "4",
        "--branch-recursion",
        "DROP",
    )

    assert data["recurrence"]["status"] == "minimal-window"
    assert len(data["levels"]) == 3

    level1 = data["levels"][1]
    assert level1["visible_shape"] == "edge-point"
    assert level1["edge_k"] == 2
    assert level1["rampification"]["attempted"] is True
    assert level1["rampification"]["target_window"]["k_range"] == "1..2"

    level2 = data["levels"][2]
    assert level2["input_window"]["k_range"] == "1..2"
    assert level2["visible_shape"] == "edge-point"
    assert level2["edge_k"] == 1
    assert level2["selected_band"]["kind"] == "visibility-entry"
    assert "rampification" not in level2


def test_opaque_recursive_lens_auto_rampification_text_is_monkey_friendly() -> None:
    n50b = "2000000000900146713649308342226750098973706617969"

    result = _run_cli(
        "opaque-recursive-lens",
        n50b,
        "--max-generator-count",
        "40",
        "--excluded-support-limit",
        "100000000",
        "--max-move-span",
        "5",
        "--depth",
        "4",
        "--branch-recursion",
        "DROP",
    )

    assert result.returncode == 0, result.stderr
    assert "rampification = attempted" in result.stdout
    assert "rampification_target_window = k[1,2]" in result.stdout
    assert "input_window = k[1,2]" in result.stdout
    assert "selected_band = visibility-entry NEW k[1..1]" in result.stdout

def test_opaque_recursive_lens_composite_edge_peel_opens_stable_new_branch_edge() -> None:
    n50b = "2000000000900146713649308342226750098973706617969"

    data = _run_json(
        "opaque-recursive-lens",
        n50b,
        "--max-generator-count",
        "40",
        "--excluded-support-limit",
        "100000000",
        "--max-move-span",
        "5",
        "--depth",
        "6",
        "--branch-recursion",
        "NEW",
        "--composite-edge-peel",
    )

    peel = data["composite_edge_peel_payload"]
    assert peel["available"] is True
    assert peel["source_edge_k"] == 6
    assert peel["edge_factorization"]["flat_factors"] == [2, 3]
    assert peel["center_generator"] == 210
    assert peel["center_generator_factorization"]["flat_factors"] == [2, 3, 5, 7]
    assert peel["shared_form_factors"] == [2, 3]
    assert [lens["edge_k"] for lens in peel["subedge_lenses"]] == [2, 3]
    assert all(lens["role"] == "shared-form-subedge" for lens in peel["subedge_lenses"])
    assert peel["classic_bridge_recommendation"] == "not-recommended"
    assert "does not factor N" in peel["claim"]


def test_opaque_recursive_lens_composite_edge_peel_reports_unavailable_on_drop_branch() -> None:
    n50b = "2000000000900146713649308342226750098973706617969"

    data = _run_json(
        "opaque-recursive-lens",
        n50b,
        "--max-generator-count",
        "40",
        "--excluded-support-limit",
        "100000000",
        "--max-move-span",
        "5",
        "--depth",
        "4",
        "--branch-recursion",
        "DROP",
        "--composite-edge-peel",
    )

    peel = data["composite_edge_peel_payload"]
    assert peel["available"] is False
    assert peel["reason"] == "no recursive center lens with composite edge_k > 2 is available"
    assert "does not factor N" in peel["claim"]


def test_opaque_recursive_lens_composite_edge_peel_text_is_monkey_friendly() -> None:
    n50b = "2000000000900146713649308342226750098973706617969"

    result = _run_cli(
        "opaque-recursive-lens",
        n50b,
        "--max-generator-count",
        "40",
        "--excluded-support-limit",
        "100000000",
        "--max-move-span",
        "5",
        "--depth",
        "6",
        "--branch-recursion",
        "NEW",
        "--composite-edge-peel",
    )

    assert result.returncode == 0, result.stderr
    assert "PET composite-edge peel" in result.stdout
    assert "source_edge_k = 6" in result.stdout
    assert "edge_factorization = 2 * 3" in result.stdout
    assert "center_generator = 210" in result.stdout
    assert "center_generator_factorization = 2 * 3 * 5 * 7" in result.stdout
    assert "shared_form_factors = [2, 3]" in result.stdout
    assert "k=2 role=shared-form-subedge" in result.stdout
    assert "k=3 role=shared-form-subedge" in result.stdout
    assert "claim = PET composite-edge peel only; this does not factor N" in result.stdout

def test_opaque_recursive_lens_composite_edge_peel_runs_subedge_recursion() -> None:
    n50b = "2000000000900146713649308342226750098973706617969"

    data = _run_json(
        "opaque-recursive-lens",
        n50b,
        "--max-generator-count",
        "40",
        "--excluded-support-limit",
        "100000000",
        "--max-move-span",
        "5",
        "--depth",
        "6",
        "--branch-recursion",
        "NEW",
        "--composite-edge-peel",
    )

    recursion = data["subedge_recursion_payload"]
    assert data["subedge_recursion"] is True
    assert recursion["available"] is True
    assert recursion["source"] == "composite-edge-peel"
    assert recursion["source_edge_k"] == 6
    assert recursion["subedge_count"] == 2
    assert recursion["available_subedge_count"] == 2

    results = {result["subedge_k"]: result for result in recursion["subedge_results"]}
    assert sorted(results) == [2, 3]

    assert results[2]["target_window"]["k_range"] == "2..2"
    assert results[2]["visible_shape"] == "edge-point"
    assert results[2]["edge_k"] == 2
    assert results[2]["center_generator"] == 430080

    assert results[3]["target_window"]["k_range"] == "3..3"
    assert results[3]["visible_shape"] == "edge-point"
    assert results[3]["edge_k"] == 2
    assert results[3]["center_generator"] == 430080

    convergence = recursion["convergence"]
    assert convergence["available"] is True
    assert convergence["kind"] == "twin-subedge-convergence"
    assert convergence["converged_subedges"] == [2, 3]
    assert convergence["converged_edge_k"] == 2
    assert convergence["converged_center_generator"] == 430080
    assert convergence["converged_visible_shape"] == "edge-point"


def test_opaque_recursive_lens_composite_subedge_recursion_text_is_monkey_friendly() -> None:
    n50b = "2000000000900146713649308342226750098973706617969"

    result = _run_cli(
        "opaque-recursive-lens",
        n50b,
        "--max-generator-count",
        "40",
        "--excluded-support-limit",
        "100000000",
        "--max-move-span",
        "5",
        "--depth",
        "6",
        "--branch-recursion",
        "NEW",
        "--composite-edge-peel",
    )

    assert result.returncode == 0, result.stderr
    assert "PET composite-subedge recursion" in result.stdout
    assert "source_edge_k = 6" in result.stdout
    assert "subedge_count = 2" in result.stdout
    assert "subedge_k = 2" in result.stdout
    assert "target_window = k[2,2]" in result.stdout
    assert "subedge_k = 3" in result.stdout
    assert "target_window = k[3,3]" in result.stdout
    assert "Subedge convergence" in result.stdout
    assert "kind = twin-subedge-convergence" in result.stdout
    assert "converged_subedges = [2, 3]" in result.stdout
    assert "converged_edge_k = 2" in result.stdout
    assert "converged_center_generator = 430080" in result.stdout
    assert "claim = PET composite-subedge recursion only; this does not factor N" in result.stdout
