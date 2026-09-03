from __future__ import annotations

import ast
import configparser
import os
import subprocess
import sys
import venv
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_project() -> configparser.ConfigParser:
    project = configparser.ConfigParser()
    loaded = project.read(ROOT / "pyproject.toml", encoding="utf-8")
    assert loaded == [str(ROOT / "pyproject.toml")]
    return project


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _venv_script(venv_dir: Path, name: str) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / f"{name}.exe"
    return venv_dir / "bin" / name


def test_distribution_configuration_exposes_only_petra() -> None:
    project = _load_project()

    assert ast.literal_eval(project["project"]["name"]) == "petra"
    scripts = {
        key: ast.literal_eval(value)
        for key, value in project["project.scripts"].items()
    }
    assert scripts == {"petra": "petra.cli:main"}

    package_find = project["tool.setuptools.packages.find"]
    assert ast.literal_eval(package_find["where"]) == ["src"]
    assert ast.literal_eval(package_find["include"]) == ["petra"]


def test_built_and_installed_distribution_contains_only_petra(
    tmp_path: Path,
) -> None:
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()

    build = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--no-build-isolation",
            "--wheel-dir",
            str(wheelhouse),
            str(ROOT),
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert build.returncode == 0, build.stderr

    wheels = sorted(wheelhouse.glob("petra-*.whl"))
    assert len(wheels) == 1
    wheel = wheels[0]

    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        entry_point_files = sorted(
            name
            for name in names
            if name.endswith(".dist-info/entry_points.txt")
        )
        assert len(entry_point_files) == 1
        entry_points = archive.read(entry_point_files[0]).decode("utf-8")

    assert any(name.startswith("petra/") for name in names)
    assert not any(name.startswith("pet/") for name in names)
    assert "petra = petra.cli:main" in entry_points
    assert "\npet =" not in entry_points

    venv_dir = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True).create(venv_dir)
    python = _venv_python(venv_dir)

    install = subprocess.run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--no-deps",
            str(wheel),
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert install.returncode == 0, install.stderr

    outside = tmp_path / "outside"
    outside.mkdir()

    import_petra = subprocess.run(
        [str(python), "-c", "import petra"],
        cwd=outside,
        check=False,
        capture_output=True,
        text=True,
    )
    assert import_petra.returncode == 0, import_petra.stderr

    import_pet = subprocess.run(
        [str(python), "-c", "import pet"],
        cwd=outside,
        check=False,
        capture_output=True,
        text=True,
    )
    assert import_pet.returncode != 0

    petra_script = _venv_script(venv_dir, "petra")
    pet_script = _venv_script(venv_dir, "pet")
    assert petra_script.exists()
    assert not pet_script.exists()

    invocation = (
        '{"schema":"petra.operator-invocation.v1",'
        '"operator":"SPROUT",'
        '"target":{"mode":"default"}}'
    )
    smoke = subprocess.run(
        [str(petra_script), "1", invocation],
        cwd=outside,
        check=False,
        capture_output=True,
        text=True,
    )
    assert smoke.returncode == 0, smoke.stderr
    assert '"schema":"petra.operator-result.v1"' in smoke.stdout
    assert '"operator":"SPROUT"' in smoke.stdout
    assert '"status":"ok"' in smoke.stdout


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


def test_historical_pet_source_is_not_a_distribution_requirement() -> None:
    assert (ROOT / "src" / "pet").is_dir()
