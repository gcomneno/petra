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
