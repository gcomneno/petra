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


def _normalize_help(output: str) -> str:
    return " ".join(output.split())


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
    help_text = _normalize_help(result.stdout)

    assert "opt-in experimental PET tooling" in help_text
    assert "not part of the stable PET CLI contract" in help_text
    assert "operator-semantics" in result.stdout


def test_cli_experimental_operator_semantics_help_declares_boundary() -> None:
    result = _run_cli("experimental", "operator-semantics", "--help")
    help_text = _normalize_help(result.stdout)

    assert "opt-in experimental PET/PEG 2.0 operator semantics reports" in help_text
    assert "not part of the stable PET CLI contract" in help_text
    assert "report" in result.stdout
    assert "matrix" in result.stdout


def test_cli_experimental_operator_semantics_report_help_contract() -> None:
    result = _run_cli("experimental", "operator-semantics", "report", "--help")
    help_text = _normalize_help(result.stdout)

    assert "single-number operator semantics report" in help_text
    assert "not part of the stable PET CLI contract" in help_text
    assert "integer N >= 2" in help_text
    assert "--json" in result.stdout
    assert "emit JSON output" in help_text


def test_cli_experimental_operator_semantics_matrix_help_contract() -> None:
    result = _run_cli("experimental", "operator-semantics", "matrix", "--help")
    help_text = _normalize_help(result.stdout)

    assert "multi-number operator semantics matrix report" in help_text
    assert "not part of the stable PET CLI contract" in help_text
    assert "integer N >= 2" in help_text
    assert "--top-patterns" in result.stdout
    assert "--min-count" in result.stdout
    assert "--pattern" in result.stdout
    assert "--no-rows" in result.stdout
    assert "--anatomy" in result.stdout
    assert "--check-rules" in result.stdout
    assert "--progress" in result.stdout
    assert "--compact-text" in result.stdout
    assert "--json" in result.stdout
    assert "emit JSON output" in help_text


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


def test_cli_experimental_operator_semantics_matrix_progress_stderr_contract() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "experimental",
            "operator-semantics",
            "matrix",
            "--range",
            "2",
            "11",
            "--no-rows",
            "--progress",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    assert payload["summary"]["checked"] == 10
    assert "progress: checked 1/10 (10%)" in result.stderr
    assert "progress: checked 10/10 (100%)" in result.stderr


def test_cli_experimental_operator_semantics_matrix_anatomy_json_contract() -> None:
    result = _run_cli(
        "experimental",
        "operator-semantics",
        "matrix",
        "--range",
        "2",
        "20",
        "--no-rows",
        "--anatomy",
        "--json",
    )

    payload = json.loads(result.stdout)

    assert payload["summary"]["anatomy_enabled"] is True
    assert "rows" not in payload
    assert all("arithmetic_anatomy" in group for group in payload["pattern_groups"])


def test_cli_experimental_operator_semantics_matrix_check_rules_json_contract() -> None:
    result = _run_cli(
        "experimental",
        "operator-semantics",
        "matrix",
        "--range",
        "2",
        "200",
        "--no-rows",
        "--anatomy",
        "--check-rules",
        "--json",
    )

    payload = json.loads(result.stdout)
    check = payload["rule_checks"]["multi_support_nonflat_rule"]

    assert check["status"] == "passed"
    assert check["mismatch_count"] == 0
    assert check["checked"] > 0


def test_cli_experimental_operator_semantics_matrix_compact_text_contract() -> None:
    result = _run_cli(
        "experimental",
        "operator-semantics",
        "matrix",
        "--range",
        "2",
        "200",
        "--no-rows",
        "--check-rules",
        "--compact-text",
    )

    assert "summary = checked=199 pattern_count=10 emitted_pattern_count=10" in result.stdout
    assert "rule_checks:" in result.stdout
    assert "- multi_support_nonflat_rule status=passed checked=139 mismatches=0" in result.stdout
    assert "numbers = [" not in result.stdout
    assert "numbers_by_pattern" not in result.stdout
