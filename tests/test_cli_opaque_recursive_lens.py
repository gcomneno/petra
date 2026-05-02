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
    assert data["recurrence"]["edge_sequence"] == [2, 2]


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

