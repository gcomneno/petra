"""Dependency-boundary evidence for the PETRA VISION Phase 1 prototype."""

from __future__ import annotations

import ast
import os
from functools import lru_cache
from itertools import product
from pathlib import Path
import subprocess
import sys
from typing import TypeAlias

import petra
import pytest
from petra.vision import (
    OrderedGroup,
    Terminal,
    VisionShape,
    adapt_petra_shape,
    decode_geometry,
    encode_geometry,
    restore_petra_shape,
)


ImportStatement: TypeAlias = tuple[str, int, str | None, tuple[str, ...]]

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_VISION_SOURCE_DIRECTORY = _REPOSITORY_ROOT / "src" / "petra" / "vision"

_EXPECTED_IMPORTS: dict[str, tuple[ImportStatement, ...]] = {
    "kernel.py": (
        ("from", 0, "__future__", ("annotations",)),
        ("from", 0, "dataclasses", ("dataclass",)),
        ("from", 0, "typing", ("TypeAlias",)),
    ),
    "geometry.py": (
        ("from", 0, "__future__", ("annotations",)),
        ("from", 0, "collections.abc", ("Iterable",)),
        ("from", 0, "dataclasses", ("dataclass",)),
        ("from", 0, "typing", ("NoReturn", "TypeAlias")),
        (
            "from",
            1,
            "kernel",
            (
                "OrderedGroup",
                "Terminal",
                "VisionShape",
                "validate_vision_shape",
            ),
        ),
    ),
    "adapter.py": (
        ("from", 0, "__future__", ("annotations",)),
        (
            "from",
            2,
            "model",
            (
                "Container",
                "Leaf",
                "PetraShape",
                "Root",
                "Term",
                "validate_shape",
            ),
        ),
        (
            "from",
            1,
            "kernel",
            (
                "OrderedGroup",
                "PHASE_1_MAX_ORDERED_GROUP_WIDTH",
                "PHASE_1_MAX_STRUCTURAL_DEPTH",
                "PHASE_1_MAX_TOTAL_NODES",
                "Terminal",
                "VisionShape",
                "VISION_SHAPE_OUT_OF_BOUNDS",
                "validate_vision_shape",
            ),
        ),
    ),
    "__init__.py": (
        (
            "from",
            1,
            "adapter",
            ("adapt_petra_shape", "restore_petra_shape"),
        ),
        (
            "from",
            1,
            "geometry",
            (
                "Cell",
                "GEOMETRY_MALFORMED",
                "GeometrySyntaxError",
                "OrthogonalGeometry",
                "PHASE_1_MAX_COORDINATE_MAGNITUDE",
                "PHASE_1_MAX_GEOMETRY_CELLS",
                "PHASE_1_MAX_GEOMETRY_HEIGHT",
                "PHASE_1_MAX_GEOMETRY_WIDTH",
                "decode_geometry",
                "encode_geometry",
                "geometry_extent",
                "normalize_geometry",
            ),
        ),
        (
            "from",
            1,
            "kernel",
            (
                "OrderedGroup",
                "PHASE_1_MAX_ORDERED_GROUP_WIDTH",
                "PHASE_1_MAX_STRUCTURAL_DEPTH",
                "PHASE_1_MAX_TOTAL_NODES",
                "Terminal",
                "VisionShape",
                "VISION_SHAPE_OUT_OF_BOUNDS",
                "validate_vision_shape",
            ),
        ),
    ),
}

_EXPECTED_FACADE_EXPORTS = (
    "Cell",
    "GEOMETRY_MALFORMED",
    "GeometrySyntaxError",
    "OrderedGroup",
    "OrthogonalGeometry",
    "PHASE_1_MAX_COORDINATE_MAGNITUDE",
    "PHASE_1_MAX_GEOMETRY_CELLS",
    "PHASE_1_MAX_GEOMETRY_HEIGHT",
    "PHASE_1_MAX_GEOMETRY_WIDTH",
    "PHASE_1_MAX_ORDERED_GROUP_WIDTH",
    "PHASE_1_MAX_STRUCTURAL_DEPTH",
    "PHASE_1_MAX_TOTAL_NODES",
    "Terminal",
    "VisionShape",
    "VISION_SHAPE_OUT_OF_BOUNDS",
    "adapt_petra_shape",
    "decode_geometry",
    "encode_geometry",
    "geometry_extent",
    "normalize_geometry",
    "restore_petra_shape",
    "validate_vision_shape",
)


def _direct_imports(path: Path) -> tuple[ImportStatement, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    statements: list[ImportStatement] = []

    for node in tree.body:
        if isinstance(node, ast.Import):
            statements.append(
                ("import", 0, None, tuple(alias.name for alias in node.names))
            )
        elif isinstance(node, ast.ImportFrom):
            statements.append(
                (
                    "from",
                    node.level,
                    node.module,
                    tuple(alias.name for alias in node.names),
                )
            )

    return tuple(statements)


def test_vision_production_files_have_the_exact_direct_import_graph() -> None:
    for filename, expected in _EXPECTED_IMPORTS.items():
        assert _direct_imports(_VISION_SOURCE_DIRECTORY / filename) == expected


def _has_dynamic_loading_bypass(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "__import__":
                return True
            if (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "importlib"
            ):
                return True

        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "sys"
            and node.attr == "modules"
        ):
            return True

    return False


def test_vision_production_code_has_no_dynamic_loading_bypass() -> None:
    for filename in ("kernel.py", "geometry.py", "adapter.py"):
        path = _VISION_SOURCE_DIRECTORY / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        assert not _has_dynamic_loading_bypass(tree)


def test_vision_facade_has_the_exact_eager_public_exports() -> None:
    import petra.vision

    assert tuple(petra.vision.__all__) == _EXPECTED_FACADE_EXPORTS
    assert len(petra.vision.__all__) == len(set(petra.vision.__all__))
    assert all(hasattr(petra.vision, name) for name in petra.vision.__all__)


def test_importing_geometry_performs_documented_eager_package_loading() -> None:
    expected_modules = {
        "petra",
        "petra.vision",
        "petra.vision.kernel",
        "petra.vision.geometry",
        "petra.vision.adapter",
        "petra.model",
        "petra.addresses",
        "petra.serialization",
        "petra.results",
        "petra.operators",
    }
    script = (
        "import sys\n"
        "import petra.vision.geometry\n"
        f"expected = {expected_modules!r}\n"
        "missing = expected.difference(sys.modules)\n"
        "assert not missing, sorted(missing)\n"
    )
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = "src"

    completed = subprocess.run(
        [sys.executable, "-B", "-c", script],
        cwd=_REPOSITORY_ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr


def _positive_compositions(
    total: int,
    length: int,
) -> tuple[tuple[int, ...], ...]:
    if length == 1:
        return ((total,),) if total >= 1 else ()

    compositions: list[tuple[int, ...]] = []
    for first in range(1, total - length + 2):
        for tail in _positive_compositions(total - first, length - 1):
            compositions.append((first, *tail))
    return tuple(compositions)


@lru_cache(maxsize=None)
def _shapes_with_exact_nodes(
    node_count: int,
    maximum_depth: int,
) -> tuple[VisionShape, ...]:
    shapes: set[VisionShape] = set()
    if node_count == 1:
        shapes.add(Terminal())

    if maximum_depth <= 0 or node_count <= 1:
        return tuple(sorted(shapes, key=repr))

    for width in range(1, 4):
        for partition in _positive_compositions(node_count - 1, width):
            child_domains = tuple(
                _shapes_with_exact_nodes(child_nodes, maximum_depth - 1)
                for child_nodes in partition
            )
            if any(not domain for domain in child_domains):
                continue
            for children in product(*child_domains):
                shapes.add(OrderedGroup(children=children))

    return tuple(sorted(shapes, key=repr))


def _bounded_phase_1_corpus() -> tuple[VisionShape, ...]:
    shapes: set[VisionShape] = set()
    for node_count in range(1, 8):
        shapes.update(_shapes_with_exact_nodes(node_count, maximum_depth=3))
    return tuple(sorted(shapes, key=repr))


def _shape_metrics(shape: VisionShape) -> tuple[int, int, int]:
    node_count = 0
    maximum_depth = 0
    maximum_width = 0
    pending: list[tuple[VisionShape, int]] = [(shape, 0)]

    while pending:
        current, depth = pending.pop()
        node_count += 1
        maximum_depth = max(maximum_depth, depth)
        if isinstance(current, Terminal):
            continue

        maximum_width = max(maximum_width, len(current.children))
        pending.extend((child, depth + 1) for child in current.children)

    return node_count, maximum_depth, maximum_width


def _forbidden_entry_point(*_args: object, **_kwargs: object) -> None:
    raise AssertionError("VISION path called a forbidden compatibility entry point")


def _patch_forbidden_entry_points(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[str, ...]:
    import petra.addresses
    import petra.model
    import petra.operators
    import petra.serialization

    modules_and_names: tuple[tuple[object, tuple[str, ...]], ...] = (
        (
            petra.addresses,
            ("parse_address", "render_address", "resolve_address"),
        ),
        (petra.serialization, ("parse_shape", "serialize_shape")),
        (petra.model, ("normalize_shape", "to_canonical_data")),
        (
            petra.operators,
            ("apply_graft", "apply_prune", "apply_shed", "apply_sprout"),
        ),
    )
    patched: list[str] = []

    for module, names in modules_and_names:
        for name in names:
            monkeypatch.setattr(module, name, _forbidden_entry_point)
            monkeypatch.setattr(petra, name, _forbidden_entry_point)
            patched.append(name)

    return tuple(patched)


def test_all_bounded_vision_paths_fail_fast_on_unrelated_apis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    corpus = _bounded_phase_1_corpus()
    assert len(corpus) == 110
    assert len(set(corpus)) == 110
    assert all(
        node_count <= 7 and depth <= 3 and width <= 3
        for node_count, depth, width in map(_shape_metrics, corpus)
    )

    patched = _patch_forbidden_entry_points(monkeypatch)
    assert patched == (
        "parse_address",
        "render_address",
        "resolve_address",
        "parse_shape",
        "serialize_shape",
        "normalize_shape",
        "to_canonical_data",
        "apply_graft",
        "apply_prune",
        "apply_shed",
        "apply_sprout",
    )

    for shape in corpus:
        geometry = encode_geometry(shape)
        assert decode_geometry(geometry) == shape

        native = restore_petra_shape(shape)
        assert adapt_petra_shape(native) == shape
        assert restore_petra_shape(decode_geometry(geometry)) == native
