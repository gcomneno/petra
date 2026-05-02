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


def test_opaque_focused_peel_selects_highest_focus_band() -> None:
    data = _run_json(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
    )

    assert data["digits"] == 5
    assert data["bit_length"] == 14

    band = data["selected_band"]
    assert band["kind"] == "pressure-entry"
    assert band["move"] == "NEW"
    assert band["k_range"] == "1..2"
    assert band["boundary"] == "2/3"
    assert band["focus_score"] == 4
    assert band["signal"] == "critical"

    lens = data["peel_lens"]
    assert lens["k_start"] == 1
    assert lens["k_end"] == 2
    assert lens["closest_k"] == 2
    assert lens["min_trigger_span"] == 1
    assert lens["local_hotspot_count"] == 2

    assert "claim" in data
    assert "does not factor N" in data["claim"]


def test_opaque_focused_peel_can_filter_kind_and_move() -> None:
    data = _run_json(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--kind",
        "recovery",
        "--move",
        "DROP",
    )

    band = data["selected_band"]
    assert band["kind"] == "recovery"
    assert band["move"] == "DROP"
    assert band["k_range"] == "3..4"
    assert band["boundary"] == "3/2"
    assert band["signal"] == "strong"


def test_opaque_focused_peel_text_is_monkey_friendly() -> None:
    result = _run_cli(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
    )

    assert result.returncode == 0, result.stderr
    assert "PET OPAQUE FOCUSED PEEL" in result.stdout
    assert "Selected magnetic band" in result.stdout
    assert "Peel lens" in result.stdout
    assert "Local hotspots" in result.stdout
    assert "claim = PET focused peel lens only; this does not factor N" in result.stdout


def test_opaque_focused_peel_rejects_non_positive_integer() -> None:
    result = _run_cli(
        "opaque-focused-peel",
        "0",
        "--excluded-support-limit",
        "16",
    )

    assert result.returncode != 0
    assert "opaque-focused-peel expects integers >= 1" in result.stderr


def test_opaque_focused_peel_errors_when_no_band_matches() -> None:
    result = _run_cli(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--kind",
        "visibility-entry",
    )

    assert result.returncode != 0
    assert "opaque-focused-peel found no matching magnetic bands" in result.stderr


def test_opaque_focused_peel_cut_reports_layers() -> None:
    data = _run_json(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--cut",
    )

    assert data["cut"] is True
    cut = data["peel_cut"]
    assert cut["cut_available"] is True
    assert cut["cut_window"] == "k[1,2]"
    assert cut["edge_k"] == 2
    assert cut["boundary"] == "2/3"
    assert cut["cut_kind"] == "pressure-entry"
    assert cut["cut_move"] == "NEW"
    assert cut["layer_count"] == 2

    layers = {layer["k"]: layer for layer in cut["layers"]}
    assert layers[1]["layer"] == "outer-layer"
    assert layers[2]["layer"] == "edge-layer"

    assert cut["side_layers"]
    assert cut["side_layers"][0]["side"] == "pressured-side"
    assert cut["side_layers"][0]["k_start"] == 3


def test_opaque_focused_peel_cut_text_is_monkey_friendly() -> None:
    result = _run_cli(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--cut",
    )

    assert result.returncode == 0, result.stderr
    assert "Focused peel cut" in result.stdout
    assert "Layers" in result.stdout
    assert "outer-layer" in result.stdout
    assert "edge-layer" in result.stdout
    assert "Side layers" in result.stdout
    assert "pressured-side" in result.stdout


def test_opaque_focused_peel_step_selects_edge_layer() -> None:
    data = _run_json(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--cut",
        "--peel-step",
    )

    assert data["peel_step"] is True
    step = data["peel_step_result"]
    assert step["step_available"] is True
    assert step["selected_action"] == "peel-edge"
    assert step["target_layer"] == "edge-layer"
    assert step["target_k"] == 2
    assert step["target_boundary"] == "2/3"
    assert step["target_kind"] == "pressure-entry"
    assert step["target_move"] == "NEW"
    assert step["target_minimal_trigger_span"] == 1
    assert step["next_side"] == "pressured-side"
    assert step["next_side_k_start"] == 3

    decisions = {row["k"]: row for row in step["layer_decisions"]}
    assert decisions[1]["decision"] == "keep-as-ramp-context"
    assert decisions[2]["decision"] == "next-peel-target"


def test_opaque_focused_peel_step_text_is_monkey_friendly() -> None:
    result = _run_cli(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--cut",
        "--peel-step",
    )

    assert result.returncode == 0, result.stderr
    assert "Focused peel step" in result.stdout
    assert "selected_action = peel-edge" in result.stdout
    assert "target_layer = edge-layer" in result.stdout
    assert "target_k = 2" in result.stdout
    assert "Layer decisions" in result.stdout
    assert "next-peel-target" in result.stdout


def test_opaque_focused_peel_slice_partitions_shape_space() -> None:
    data = _run_json(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--slice",
    )

    assert data["cut"] is True
    assert data["peel_step"] is True
    assert data["slice"] is True

    slice_data = data["peel_slice"]
    assert slice_data["slice_available"] is True
    assert slice_data["slice_boundary"] == "2/3"
    assert slice_data["edge_k"] == 2
    assert slice_data["target_kind"] == "pressure-entry"
    assert slice_data["target_move"] == "NEW"

    selected = slice_data["selected_partition"]
    assert selected["name"] == "boundary-informative-side"
    assert selected["k_start"] == 1
    assert selected["k_end"] == 2
    assert selected["k_range"] == "1..2"
    assert selected["role"] == "retained-peel-side"

    separated = slice_data["separated_partition"]
    assert separated["name"] == "pressured-side"
    assert separated["k_start"] == 3
    assert separated["k_end"] == 4
    assert separated["k_range"] == "3..4"
    assert separated["role"] == "separated-side"

    decision = slice_data["slice_decision"]
    assert decision["keep"] == "selected_partition"
    assert decision["separate"] == "separated_partition"
    assert decision["next_action"] == "inspect edge stability before pressured transition"


def test_opaque_focused_peel_slice_text_is_monkey_friendly() -> None:
    result = _run_cli(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--slice",
    )

    assert result.returncode == 0, result.stderr
    assert "Focused peel cut" in result.stdout
    assert "Focused peel step" in result.stdout
    assert "Focused peel slice" in result.stdout
    assert "Selected partition" in result.stdout
    assert "Separated partition" in result.stdout
    assert "boundary-informative-side" in result.stdout
    assert "pressured-side" in result.stdout
