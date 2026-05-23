#!/usr/bin/env python3
import json
import subprocess
import sys


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pet.cli", *args],
        check=True,
        capture_output=True,
        text=True,
    )


def _run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        check=True,
        capture_output=True,
        text=True,
    )


def test_cli_experimental_operator_semantics_report_json_delegates_to_tool() -> None:
    cli_result = _run_cli(
        "experimental",
        "operator-semantics",
        "report",
        "60",
        "--json",
    )
    tool_result = _run_tool(
        "tools/research/pet_operator_semantics_report.py",
        "60",
        "--json",
    )

    assert json.loads(cli_result.stdout) == json.loads(tool_result.stdout)


def test_cli_experimental_operator_semantics_matrix_json_delegates_to_tool() -> None:
    cli_result = _run_cli(
        "experimental",
        "operator-semantics",
        "matrix",
        "--range",
        "12",
        "18",
        "--min-count",
        "2",
        "--pattern",
        "leaf-blocked",
        "--no-rows",
        "--json",
    )
    tool_result = _run_tool(
        "tools/research/pet_operator_semantics_report_matrix.py",
        "--range",
        "12",
        "18",
        "--min-count",
        "2",
        "--pattern",
        "leaf-blocked",
        "--no-rows",
        "--json",
    )

    assert json.loads(cli_result.stdout) == json.loads(tool_result.stdout)


def test_cli_experimental_operator_semantics_matrix_text_contract() -> None:
    result = _run_cli(
        "experimental",
        "operator-semantics",
        "matrix",
        "--range",
        "12",
        "18",
        "--top-patterns",
        "1",
        "--no-rows",
    )

    assert "schema = pet.operator_semantics_report_matrix.v0" in result.stdout
    assert "pattern_group_filters =" in result.stdout
    assert "'emitted_pattern_count': 1" in result.stdout
    assert "rows:" not in result.stdout
    assert "pattern_groups:" in result.stdout


def test_cli_experimental_help_declares_opt_in_boundary() -> None:
    result = _run_cli("experimental", "--help")

    assert "opt-in experimental PET tooling" in result.stdout
    assert "not part of the stable PET CLI contract" in result.stdout
    assert "operator-semantics" in result.stdout


def test_cli_experimental_operator_semantics_help_declares_boundary() -> None:
    result = _run_cli("experimental", "operator-semantics", "--help")

    assert "opt-in experimental PET/PEG 2.0 operator semantics reports" in result.stdout
    assert "not part of the stable PET CLI contract" in result.stdout
    assert "report" in result.stdout
    assert "matrix" in result.stdout


def test_cli_experimental_operator_semantics_report_help_contract() -> None:
    result = _run_cli("experimental", "operator-semantics", "report", "--help")

    assert "single-number operator semantics report" in result.stdout
    assert "not part of the stable PET CLI contract" in result.stdout
    assert "integer N >= 2" in result.stdout
    assert "--json" in result.stdout
    assert "emit JSON output" in result.stdout


def test_cli_experimental_operator_semantics_matrix_help_contract() -> None:
    result = _run_cli("experimental", "operator-semantics", "matrix", "--help")

    assert "multi-number operator semantics matrix report" in result.stdout
    assert "not part of the stable PET CLI contract" in result.stdout
    assert "integer N >= 2" in result.stdout
    assert "--top-patterns" in result.stdout
    assert "--min-count" in result.stdout
    assert "--pattern" in result.stdout
    assert "--no-rows" in result.stdout
    assert "--json" in result.stdout
    assert "emit JSON output" in result.stdout


def test_cli_experimental_operator_semantics_report_json_status_fields() -> None:
    result = _run_cli(
        "experimental",
        "operator-semantics",
        "report",
        "60",
        "--json",
    )

    payload = json.loads(result.stdout)

    assert payload["tooling_status"] == "experimental documented tooling"
    assert payload["stable_cli_contract"] is False


def test_cli_experimental_operator_semantics_matrix_json_status_fields() -> None:
    result = _run_cli(
        "experimental",
        "operator-semantics",
        "matrix",
        "--range",
        "12",
        "18",
        "--json",
    )

    payload = json.loads(result.stdout)

    assert payload["tooling_status"] == "experimental documented tooling"
    assert payload["stable_cli_contract"] is False
