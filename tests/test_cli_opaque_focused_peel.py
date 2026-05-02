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


def test_opaque_focused_peel_lift_exposes_visible_pet_form() -> None:
    data = _run_json(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--lift",
    )

    assert data["cut"] is True
    assert data["peel_step"] is True
    assert data["slice"] is True
    assert data["lift"] is True

    lift = data["peel_lift"]
    assert lift["lift_available"] is True
    assert lift["lift_target"]["name"] == "boundary-informative-side"
    assert lift["lifted_against"]["name"] == "pressured-side"

    profile = lift["lift_profile"]
    assert profile["selected_width"] == 2
    assert profile["separated_width"] == 2
    assert profile["local_shape"] == "thin-ramp"
    assert profile["emergent_form"] == "pre-pressure-edge"
    assert profile["edge_k"] == 2
    assert profile["slice_boundary"] == "2/3"

    visible = lift["visible_pet_form"]
    assert visible["form"] == "pre-pressure-edge"
    assert visible["shape"] == "thin-ramp"
    assert visible["edge_k"] == 2
    assert visible["boundary"] == "2/3"


def test_opaque_focused_peel_lift_text_is_monkey_friendly() -> None:
    result = _run_cli(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--lift",
    )

    assert result.returncode == 0, result.stderr
    assert "Focused peel cut" in result.stdout
    assert "Focused peel step" in result.stdout
    assert "Focused peel slice" in result.stdout
    assert "Focused peel lift" in result.stdout
    assert "Visible PET form" in result.stdout
    assert "emergent_form = pre-pressure-edge" in result.stdout
    assert "local_shape = thin-ramp" in result.stdout


def test_opaque_focused_peel_decode_translates_visible_form() -> None:
    data = _run_json(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--decode",
    )

    assert data["cut"] is True
    assert data["peel_step"] is True
    assert data["slice"] is True
    assert data["lift"] is True
    assert data["decode"] is True

    decode = data["pet_decode"]
    assert decode["decode_available"] is True
    assert decode["input_form"] == "pre-pressure-edge"
    assert decode["input_shape"] == "thin-ramp"
    assert decode["edge_k"] == 2
    assert decode["boundary"] == "2/3"
    assert "does not factor N" in decode["claim"]

    constraints = decode["decoded_constraints"]
    assert constraints["support_count_region"]["k_range"] == "1..2"
    assert constraints["separated_region"]["k_range"] == "3..4"
    assert constraints["local_edge_hypothesis"]["k"] == 2
    assert constraints["local_edge_hypothesis"]["form"] == "pre-pressure-edge"
    assert constraints["local_edge_hypothesis"]["shape"] == "thin-ramp"
    assert constraints["transition"] == "boundary-informative-side -> pressured-side"
    assert constraints["decode_strength"] == "sharp"
    assert constraints["recommended_next_lens"] == "preserve-edge-k"

    projected = constraints["projected_center_pet_form"]
    assert projected["expression"] == "N^(1/2)"
    assert round(projected["estimate"], 6) == 101.995098
    assert projected["nearest_integer"] == 102
    assert projected["nearest_integer_digits"] == 3
    assert projected["nearest_integer_bits"] == 7
    assert projected["pet_shape_text"] == "((), (), ())"
    assert projected["pet_signature"] == [[], [], []]
    assert projected["pet_generator"] == 30
    assert projected["pet_child_generators"] == [1, 1, 1]
    assert projected["center_role"] == "local edge projection"


def test_opaque_focused_peel_decode_text_is_monkey_friendly() -> None:
    result = _run_cli(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--decode",
    )

    assert result.returncode == 0, result.stderr
    assert "Focused peel lift" in result.stdout
    assert "PET visible-form decode" in result.stdout
    assert "input_form = pre-pressure-edge" in result.stdout
    assert "input_shape = thin-ramp" in result.stdout
    assert "local_edge_hypothesis = k=2" in result.stdout
    assert "recommended_next_lens = preserve-edge-k" in result.stdout
    assert "Projected center PET form" in result.stdout
    assert "expression = N^(1/2)" in result.stdout
    assert "nearest_integer = 102" in result.stdout
    assert "pet_shape = ((), (), ())" in result.stdout
    assert "pet_signature = [[], [], []]" in result.stdout
    assert "pet_generator = 30" in result.stdout


def test_opaque_focused_peel_center_lens_builds_next_lens() -> None:
    data = _run_json(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--center-lens",
    )

    assert data["cut"] is True
    assert data["peel_step"] is True
    assert data["slice"] is True
    assert data["lift"] is True
    assert data["decode"] is True
    assert data["center_lens"] is True

    lens = data["decoded_center_lens"]
    assert lens["center_lens_available"] is True
    assert lens["source"] == "projected_center_pet_form"
    assert lens["lens_kind"] == "flat-three-leaf-center"
    assert lens["edge_k"] == 2
    assert lens["boundary"] == "2/3"
    assert lens["preserve_edge_k"] is True
    assert lens["preserve_center_shape"] is True
    assert lens["center_nearest_integer"] == 102
    assert lens["center_shape"] == "((), (), ())"
    assert lens["center_signature"] == [[], [], []]
    assert lens["center_generator"] == 30
    assert lens["center_child_generators"] == [1, 1, 1]
    assert lens["suggested_window"]["k_range"] == "1..2"
    assert lens["recommended_next_lens"] == (
        "rescan-suggested-window-preserving-edge-and-center-shape"
    )
    assert "does not factor N" in lens["claim"]


def test_opaque_focused_peel_center_lens_text_is_monkey_friendly() -> None:
    result = _run_cli(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--center-lens",
    )

    assert result.returncode == 0, result.stderr
    assert "PET visible-form decode" in result.stdout
    assert "PET decoded-center lens" in result.stdout
    assert "lens_kind = flat-three-leaf-center" in result.stdout
    assert "preserve_edge_k = yes" in result.stdout
    assert "preserve_center_shape = yes" in result.stdout
    assert "center_shape = ((), (), ())" in result.stdout
    assert "suggested_window = k[1,2]" in result.stdout


def test_opaque_focused_peel_realize_bridges_to_pet_encode_decode() -> None:
    data = _run_json(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--realize",
    )

    assert data["cut"] is True
    assert data["peel_step"] is True
    assert data["slice"] is True
    assert data["lift"] is True
    assert data["decode"] is True
    assert data["center_lens"] is True
    assert data["realize"] is True

    realization = data["pet_realization"]
    assert realization["realization_available"] is True
    assert realization["source"] == "projected-center"
    assert realization["source_form"] == "pre-pressure-edge:thin-ramp"
    assert realization["edge_k"] == 2
    assert realization["boundary"] == "2/3"
    assert realization["nearest_integer"] == 102

    encode_decode = realization["encode_decode"]
    assert encode_decode["decoded_back"] == 102
    assert encode_decode["roundtrip_ok"] is True
    assert encode_decode["encoded_pet"] == [
        [2, None],
        [3, None],
        [17, None],
    ]

    realized_shape = realization["realized_shape"]
    assert realized_shape["shape_text"] == "((), (), ())"
    assert realized_shape["signature"] == [[], [], []]
    assert realized_shape["generator"] == 30
    assert realized_shape["already_minimal"] is False
    assert realized_shape["child_generators"] == [1, 1, 1]
    assert realization["role"] == "local edge projection realization"
    assert "does not factor N" in realization["claim"]


def test_opaque_focused_peel_realize_text_is_monkey_friendly() -> None:
    result = _run_cli(
        "opaque-focused-peel",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--realize",
    )

    assert result.returncode == 0, result.stderr
    assert "PET visible-form decode" in result.stdout
    assert "PET decoded-center lens" in result.stdout
    assert "PET realization payload" in result.stdout
    assert "source = projected-center" in result.stdout
    assert "nearest_integer = 102" in result.stdout
    assert "Encode/decode" in result.stdout
    assert "decoded_back = 102" in result.stdout
    assert "roundtrip_ok = yes" in result.stdout
    assert "Realized shape" in result.stdout
    assert "shape = ((), (), ())" in result.stdout
    assert "generator = 30" in result.stdout
