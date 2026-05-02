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
