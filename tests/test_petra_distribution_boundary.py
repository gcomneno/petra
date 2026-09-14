from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _pyproject_value(section: str, key: str) -> object:
    lines = (ROOT / "pyproject.toml").read_text(encoding="utf-8").splitlines()
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
    lines = (ROOT / "pyproject.toml").read_text(encoding="utf-8").splitlines()
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


def test_distribution_configuration_exposes_only_petra() -> None:
    assert _pyproject_value("project", "name") == "petra"
    assert _pyproject_scripts() == {"petra": "petra.cli:main"}
    assert _pyproject_value("tool.setuptools.packages.find", "where") == ["src"]
    assert _pyproject_value("tool.setuptools.packages.find", "include") == ["petra"]


def test_distribution_source_boundary_keeps_legacy_out_of_package_discovery() -> None:
    assert (ROOT / "src" / "petra" / "__init__.py").is_file()

    if not (ROOT / "src" / "pet").is_dir():
        pytest.skip(
            "Phase 10 complete: historical PET source has been removed; "
            "the legacy-exclusion contract is vacuously satisfied"
        )

    assert _pyproject_value("tool.setuptools.packages.find", "include") == ["petra"]


def test_petra_source_has_no_legacy_pet_imports() -> None:
    violations: list[tuple[str, int, str]] = []

    for path in sorted((ROOT / "src" / "petra").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "pet" or alias.name.startswith("pet."):
                        violations.append((str(path), node.lineno, alias.name))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module == "pet" or module.startswith("pet."):
                    violations.append((str(path), node.lineno, module))

    assert violations == []


def test_historical_pet_source_remains_available_for_later_phase_10_deletion() -> None:
    if not (ROOT / "src" / "pet").is_dir():
        pytest.skip(
            "Phase 10 complete: historical PET source has been removed"
        )
    assert (ROOT / "src" / "pet").is_dir()
