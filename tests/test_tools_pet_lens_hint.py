import subprocess
import sys


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=False,
        text=True,
        capture_output=True,
    )


def test_pet_lens_hint_reports_two_leaf_for_three_mass_case() -> None:
    result = run("tools/pet_lens_hint.py", "385")

    assert result.returncode == 0, result.stderr
    assert "blade_index = 3" in result.stdout
    assert "target_lens = two-leaf" in result.stdout
    assert "target_leaf_count = 2" in result.stdout
    assert "flatten_first = no" in result.stdout


def test_pet_lens_hint_reports_one_leaf_for_balanced_semiprime() -> None:
    result = run("tools/pet_lens_hint.py", "6345405191")

    assert result.returncode == 0, result.stderr
    assert "blade_index = 10" in result.stdout
    assert "target_lens = one-leaf" in result.stdout
    assert "target_leaf_count = 1" in result.stdout
    assert "flatten_first = no" in result.stdout


def test_pet_lens_hint_reports_flatten_hint_for_power_like_case() -> None:
    result = run("tools/pet_lens_hint.py", "49")

    assert result.returncode == 0, result.stderr
    assert "flattening_recommended = yes" in result.stdout
    assert "flatten_first = yes" in result.stdout


def test_pet_lens_hint_flatten_projection_reaches_flat_core() -> None:
    result = run("tools/pet_lens_hint.py", "49", "--flatten")

    assert result.returncode == 0, result.stderr
    assert "flatten_applied = yes" in result.stdout
    assert "source_height = 2" in result.stdout
    assert "target_lens = none" in result.stdout


def test_peelator_wrapper_runs_pet_triage_pipeline_with_legacy_lens_hint() -> None:
    result = run(
        "tools/peelator.sh",
        "385",
        "--max-generator-count",
        "8",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "3",
        "--depth",
        "1",
        "--no-fork",
        "--no-fork-follow",
        "--no-recursive",
    )

    assert result.returncode == 0, result.stderr
    assert "PET STRUCTURAL FACTORIZATION PIPELINE" in result.stdout
    assert "0. PET race diagnostic" in result.stdout
    assert "1. PET classic handoff policy" in result.stdout
    assert "4. Legacy lens hint" in result.stdout
    assert "PET LENS HINT" in result.stdout
    assert "target_lens = two-leaf" in result.stdout
    assert "7. Legacy mass response" in result.stdout
