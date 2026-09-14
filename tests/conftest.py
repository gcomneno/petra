"""Pytest configuration for the PETRA test suite.

During Phase 10, the working tree still contains the historical PET
runtime (`src/pet/`) and the PET-era tools (`tools/pet_*`). Tests that
exercise that residue are marked `legacy` here so the canonical PETRA
gate can run in isolation.

Two rules apply, in order:

1. Filename pattern: any test module whose name starts with ``test_pet``
   or ``test_tools_pet_`` is legacy.
2. Explicit allowlist: test modules that import the historical ``pet``
   package are legacy even if their filename does not advertise it.

The marker is applied at collection time; test bodies are not modified.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest


_TESTS_DIR = Path(__file__).parent

# Modules that import the historical `pet` package but do not carry a
# `pet`-prefixed filename. Detected via AST and kept explicit so the
# list is reviewable and stable.
_LEGACY_IMPORT_MODULES: frozenset[str] = frozenset({
    "test_algebra.py",
    "test_cli_backbone_prime_candidates.py",
    "test_cli_opaque_residual_status.py",
    "test_cli_small_number_planner.py",
    "test_distance.py",
    "test_extended_metrics.py",
    "test_graph.py",
    "test_guarded_redirect.py",
    "test_invalid_pet.py",
    "test_metrics.py",
    "test_object_legacy_bridge.py",
    "test_object_metrics.py",
    "test_object_model.py",
    "test_operators.py",
    "test_prime_fast.py",
    "test_root_base.py",
    "test_traces.py",
})


def _module_imports_pet(path: Path) -> bool:
    """Return True if the module imports the historical `pet` package."""

    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError):
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module == "pet" or node.module.startswith("pet."):
                return True
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "pet" or alias.name.startswith("pet."):
                    return True
    return False


def _is_legacy(path: Path) -> bool:
    name = path.name
    if name == "test_pet.py" or name.startswith("test_pet_") or name.startswith("test_tools_pet_"):
        return True
    if name in _LEGACY_IMPORT_MODULES:
        return True
    return _module_imports_pet(path)


def pytest_collection_modifyitems(config, items):
    for item in items:
        path = Path(str(item.fspath))
        try:
            path.relative_to(_TESTS_DIR)
        except ValueError:
            continue
        if _is_legacy(path):
            item.add_marker(pytest.mark.legacy)
