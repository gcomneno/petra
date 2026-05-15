from __future__ import annotations

import json
import subprocess
import sys


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pet.cli", *args],
        capture_output=True,
        text=True,
        check=True,
    )


def test_cli_structural_factorization_reports_stable_summary() -> None:
    result = _run_cli(
        "structural-factorization",
        "24680",
        "--max-depth",
        "4",
    )

    assert result.stdout.strip().splitlines() == [
        "PET STRUCTURAL FACTORIZATION",
        "",
        "N = 24680",
        "status = complete",
        "residual_reduction_chain = 20 * 2 * 617",
        "terminal_residual = 1",
        (
            "claim = PET performs structural factorization of the PET shape; "
            "classic verification confirms arithmetic factors"
        ),
    ]


def test_cli_structural_factorization_writes_optional_pest_json(tmp_path) -> None:
    pest_json = tmp_path / "pest.json"

    result = _run_cli(
        "structural-factorization",
        "24680",
        "--max-depth",
        "4",
        "--pest-json",
        str(pest_json),
    )

    assert "PET STRUCTURAL FACTORIZATION" in result.stdout

    tree = json.loads(pest_json.read_text())

    assert tree["schema"] == "pet.syntax_tree.v0"
    assert tree["summary"]["status"] == "complete"
    assert tree["summary"]["terminal_residual"] == "1"
    assert tree["summary"]["residual_reduction_chain"] == "20 * 2 * 617"


def test_cli_structural_factorization_guarded_redirect_completes() -> None:
    result = _run_cli(
        "structural-factorization",
        "357357",
        "--max-depth",
        "4",
        "--guarded-redirect",
    )

    assert result.stdout.strip().splitlines() == [
        "PET STRUCTURAL FACTORIZATION",
        "",
        "N = 357357",
        "status = complete",
        "residual_reduction_chain = 3 * 7 * 7 * 17 * 11 * 13",
        "terminal_residual = 1",
        "guarded_redirect = applied",
        "guarded_redirect_mode = flat-k",
        "guarded_redirect_current_anchor = 231",
        "guarded_redirect_redirect_anchor = 3",
        "guarded_redirect_structural_prefix = 77",
        (
            "guarded_redirect_execution_delta = "
            "redirect-completes-with-flat-k"
        ),
        (
            "claim = PET performs structural factorization of the PET shape; "
            "classic verification confirms arithmetic factors"
        ),
    ]


def test_cli_structural_factorization_guarded_redirect_positive_control() -> None:
    result = _run_cli(
        "structural-factorization",
        "30030",
        "--max-depth",
        "4",
        "--guarded-redirect",
    )

    lines = result.stdout.strip().splitlines()

    assert "status = complete" in lines
    assert "residual_reduction_chain = 5005 * 2 * 3" in lines
    assert "terminal_residual = 1" in lines
    assert "guarded_redirect = not-applied" in lines
    assert "guarded_redirect_guard_reason = not-blocked-status" in lines
