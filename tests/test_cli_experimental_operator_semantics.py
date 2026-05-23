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
