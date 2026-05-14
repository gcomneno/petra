import subprocess


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=False,
        text=True,
        capture_output=True,
    )


def test_pet_lens_transition_reports_drop_for_three_leaf_source() -> None:
    result = run("tools/pet_lens_transition.py", "3027009081")

    assert result.returncode == 0, result.stderr
    assert "source_generator = 30" in result.stdout
    assert "target_generator = 6" in result.stdout
    assert "transition_available = yes" in result.stdout
    assert "transition = DROP" in result.stdout
    assert "transition_path = DROP" in result.stdout
    assert "representative_path = 30 -> 15" in result.stdout
    assert "representative_target = 15" in result.stdout


def test_pet_lens_transition_reports_drop_for_two_leaf_source() -> None:
    result = run("tools/pet_lens_transition.py", "6345405191")

    assert result.returncode == 0, result.stderr
    assert "source_generator = 6" in result.stdout
    assert "target_generator = 2" in result.stdout
    assert "transition_available = yes" in result.stdout
    assert "transition = DROP" in result.stdout
    assert "representative_target = 3" in result.stdout


def test_pet_lens_transition_detects_dec_for_power_like_source() -> None:
    result = run("tools/pet_lens_transition.py", "49")

    assert result.returncode == 0, result.stderr
    assert "source_generator = 4" in result.stdout
    assert "target_generator = 2" in result.stdout
    assert "transition_available = yes" in result.stdout
    assert "transition = DEC" in result.stdout


def test_peelator_wrapper_reports_legacy_lens_transition_section() -> None:
    result = run(
        "tools/peelator.sh",
        "3027009081",
        "--max-generator-count",
        "20",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "5",
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
    assert "6. Legacy lens transition" in result.stdout
    assert "source_generator = 30" in result.stdout
    assert "target_generator = 6" in result.stdout
    assert "transition = DROP" in result.stdout


def test_pet_lens_transition_reports_multistep_dec_path() -> None:
    result = run("tools/pet_lens_transition.py", "16")

    assert result.returncode == 0, result.stderr
    assert "source_generator = 16" in result.stdout
    assert "target_generator = 2" in result.stdout
    assert "transition_available = partial" in result.stdout
    assert "transition = DEC_PATH" in result.stdout
    assert "representative_target = 2" in result.stdout
    assert "transition_path = DEC -> DEC -> DEC" in result.stdout
    assert "generator_path = 16 -> 8 -> 4 -> 2" in result.stdout
