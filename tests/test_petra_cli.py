from __future__ import annotations

import ast
import subprocess
import sys
import sysconfig
from pathlib import Path

from petra import (
    FailedResult,
    Operator,
    apply_graft,
    apply_shed,
    apply_sprout,
    parse_invocation_json,
    parse_shape,
    serialize_result,
)


def _run_petra_cli(
    shape_text: str,
    invocation_json: str,
) -> subprocess.CompletedProcess[str]:
    return _run_petra_cli_args([shape_text, invocation_json])


def _run_petra_cli_args(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "petra.cli",
            *args,
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def _petra_console_script_path() -> Path:
    scripts_dir = Path(sysconfig.get_path("scripts"))
    candidates = [scripts_dir / "petra", scripts_dir / "petra.exe"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise AssertionError(f"petra console script not found in {scripts_dir}")


def _pyproject_value(section: str, key: str) -> object:
    lines = Path("pyproject.toml").read_text(encoding="utf-8").splitlines()
    current_section: str | None = None

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1]
            continue
        if current_section != section or not stripped.startswith(f"{key} ="):
            continue

        value = stripped.split("=", 1)[1].strip()
        while value.count("[") > value.count("]"):
            index += 1
            value += " " + lines[index].strip()
        return ast.literal_eval(value)

    raise AssertionError(f"missing pyproject assignment: [{section}] {key}")


def _pyproject_scripts() -> dict[str, str]:
    lines = Path("pyproject.toml").read_text(encoding="utf-8").splitlines()
    scripts: dict[str, str] = {}
    current_section: str | None = None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1]
            continue
        if current_section != "project.scripts" or not stripped:
            continue
        key, raw_value = stripped.split("=", 1)
        scripts[key.strip()] = ast.literal_eval(raw_value.strip())

    return scripts


def _default_invocation(operator: str) -> str:
    return (
        '{"schema":"petra.operator-invocation.v1",'
        f'"operator":"{operator}",'
        '"target":{"mode":"default"}}'
    )


def _explicit_invocation(operator: str, address: str) -> str:
    return (
        '{"schema":"petra.operator-invocation.v1",'
        f'"operator":"{operator}",'
        '"target":{"mode":"explicit",'
        f'"address":"{address}"'
        "}}"
    )


def test_petra_console_script_entry_point_is_declared() -> None:
    assert _pyproject_value("project", "name") == "petra"
    assert _pyproject_scripts() == {"petra": "petra.cli:main"}
    assert _pyproject_value("tool.setuptools.packages.find", "where") == ["src"]
    assert _pyproject_value("tool.setuptools.packages.find", "include") == ["petra"]


def test_petra_console_script_entry_point_executes_in_editable_environment() -> None:
    invocation_json = _default_invocation("SPROUT")
    expected = serialize_result(
        apply_sprout(parse_shape("1"), parse_invocation_json(invocation_json)[1])
    ) + "\n"

    result = subprocess.run(
        [_petra_console_script_path(), "1", invocation_json],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout == expected
    assert result.stderr == ""


def test_cli_missing_required_arguments_use_argparse_exit_2() -> None:
    result = _run_petra_cli_args(["1"])

    assert result.returncode == 2
    assert result.stdout == ""
    assert "usage: petra" in result.stderr
    assert "the following arguments are required: invocation_json" in result.stderr


def test_cli_unexpected_extra_arguments_use_argparse_exit_2() -> None:
    result = _run_petra_cli_args(["1", _default_invocation("SPROUT"), "extra"])

    assert result.returncode == 2
    assert result.stdout == ""
    assert "usage: petra" in result.stderr
    assert "unrecognized arguments: extra" in result.stderr


def test_cli_successful_default_invocation_emits_canonical_result_json() -> None:
    shape_text = "1"
    invocation_json = _default_invocation("SPROUT")
    shape = parse_shape(shape_text)
    operator, target = parse_invocation_json(invocation_json)

    assert operator is Operator.SPROUT
    expected = serialize_result(apply_sprout(shape, target)) + "\n"

    result = _run_petra_cli(shape_text, invocation_json)

    assert result.returncode == 0
    assert result.stdout == expected
    assert result.stderr == ""


def test_cli_successful_explicit_invocation_emits_canonical_result_json() -> None:
    shape_text = "C(r0^1)"
    invocation_json = _explicit_invocation("GRAFT", "@/0/^")
    shape = parse_shape(shape_text)
    operator, target = parse_invocation_json(invocation_json)

    assert operator is Operator.GRAFT
    expected = serialize_result(apply_graft(shape, target)) + "\n"

    result = _run_petra_cli(shape_text, invocation_json)

    assert result.returncode == 0
    assert result.stdout == expected
    assert result.stderr == ""


def test_cli_stdout_adds_only_transport_newline_to_serializer_output() -> None:
    invocation_json = _default_invocation("SPROUT")
    result = _run_petra_cli("1", invocation_json)

    assert result.returncode == 0
    assert result.stdout.endswith("\n")
    assert not result.stdout.endswith("\n\n")
    assert result.stdout[:-1] == serialize_result(
        apply_sprout(parse_shape("1"), parse_invocation_json(invocation_json)[1])
    )


def test_cli_malformed_invocation_preserves_existing_failure_result_reason() -> None:
    shape_text = "C(r0^1)"
    invocation_json = (
        '{"schema":"petra.operator-invocation.v1",'
        '"operator":"SPROUT",'
        '"target":{"mode":"default"},'
        '"legacy":true}'
    )
    expected = serialize_result(
        FailedResult(
            operator=None,
            invocation_target=None,
            before_shape=parse_shape(shape_text),
            reason="invocation-invalid",
        )
    ) + "\n"

    result = _run_petra_cli(shape_text, invocation_json)

    assert result.returncode == 1
    assert result.stdout == expected
    assert result.stderr == ""


def test_cli_malformed_invocation_address_preserves_existing_reason() -> None:
    shape_text = "C(r0^1)"
    invocation_json = _explicit_invocation("GRAFT", "@/00/^")
    expected = serialize_result(
        FailedResult(
            operator=Operator.GRAFT,
            invocation_target=None,
            before_shape=parse_shape(shape_text),
            reason="address-malformed",
        )
    ) + "\n"

    result = _run_petra_cli(shape_text, invocation_json)

    assert result.returncode == 1
    assert result.stdout == expected
    assert result.stderr == ""


def test_cli_operator_failure_preserves_existing_stable_reason() -> None:
    shape_text = "1"
    invocation_json = _default_invocation("SHED")
    shape = parse_shape(shape_text)
    operator, target = parse_invocation_json(invocation_json)

    assert operator is Operator.SHED
    expected = serialize_result(apply_shed(shape, target)) + "\n"

    result = _run_petra_cli(shape_text, invocation_json)

    assert result.returncode == 1
    assert result.stdout == expected
    assert result.stderr == ""


def test_cli_malformed_shape_is_deterministic_transport_error() -> None:
    result = _run_petra_cli("C(r0^)", _default_invocation("SPROUT"))

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == "petra: shape-text-malformed\n"


def test_cli_does_not_accept_legacy_pet_operator_names() -> None:
    shape_text = "1"
    invocation_json = _default_invocation("NEW")
    expected = serialize_result(
        FailedResult(
            operator=None,
            invocation_target=None,
            before_shape=parse_shape(shape_text),
            reason="invocation-invalid",
        )
    ) + "\n"

    result = _run_petra_cli(shape_text, invocation_json)

    assert result.returncode == 1
    assert result.stdout == expected
    assert result.stderr == ""


def test_petra_cli_version_flag_prints_installed_version() -> None:
    from importlib.metadata import version as _pkg_version

    result = _run_petra_cli_args(["--version"])

    assert result.returncode == 0
    assert result.stdout.strip() == f"petra {_pkg_version('petra')}"
