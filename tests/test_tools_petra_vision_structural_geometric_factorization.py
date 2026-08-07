"""Gate 1B contract tests for native Structural Geometric Factorization."""

from __future__ import annotations

from functools import lru_cache
import importlib.util
from itertools import product
from pathlib import Path
from types import ModuleType

import pytest

from petra.vision import (
    OrderedGroup,
    OrthogonalGeometry,
    Terminal,
    VisionShape,
    encode_geometry,
)


_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_NATIVE_MODULE_PATH = (
    _REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_structural_geometric_factorization.py"
)


def _load_native_module() -> ModuleType:
    if not _NATIVE_MODULE_PATH.is_file():
        pytest.fail(
            "native FGS research module is not implemented yet",
            pytrace=False,
        )

    spec = importlib.util.spec_from_file_location(
        "_petra_vision_structural_geometric_factorization",
        _NATIVE_MODULE_PATH,
    )
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _positive_compositions(
    total: int,
    length: int,
) -> tuple[tuple[int, ...], ...]:
    if length == 1:
        return ((total,),) if total >= 1 else ()

    compositions: list[tuple[int, ...]] = []

    for first in range(1, total - length + 2):
        for tail in _positive_compositions(
            total - first,
            length - 1,
        ):
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

    child_budget = node_count - 1

    for width in range(1, 4):
        for partition in _positive_compositions(
            child_budget,
            width,
        ):
            child_domains = tuple(
                _shapes_with_exact_nodes(
                    child_nodes,
                    maximum_depth - 1,
                )
                for child_nodes in partition
            )

            if any(not domain for domain in child_domains):
                continue

            for children in product(*child_domains):
                shapes.add(OrderedGroup(children=children))

    return tuple(sorted(shapes, key=repr))


def _phase_1_corpus() -> tuple[VisionShape, ...]:
    shapes: set[VisionShape] = set()

    for node_count in range(1, 8):
        shapes.update(
            _shapes_with_exact_nodes(
                node_count,
                maximum_depth=3,
            )
        )

    return tuple(sorted(shapes, key=repr))


def _expected_immediate_factors(
    shape: VisionShape,
) -> tuple[OrthogonalGeometry, ...]:
    if isinstance(shape, Terminal):
        return ()

    return tuple(
        encode_geometry(child)
        for child in shape.children
    )


def test_native_fgs_matches_phase_1_immediate_factor_contract() -> None:
    module = _load_native_module()

    native_fgs = getattr(module, "native_fgs", None)
    recompose_fgs = getattr(module, "recompose_fgs", None)

    assert callable(native_fgs), "native_fgs must be callable"
    assert callable(recompose_fgs), "recompose_fgs must be callable"

    corpus = _phase_1_corpus()

    assert len(corpus) == 110
    assert len(set(corpus)) == 110

    terminal_count = 0
    nonterminal_count = 0
    factor_occurrences = 0

    for shape in corpus:
        source = encode_geometry(shape)
        expected = _expected_immediate_factors(shape)

        factors = native_fgs(source)
        replay = native_fgs(source)

        assert type(factors) is tuple
        assert factors == replay

        assert all(
            type(factor) is OrthogonalGeometry
            for factor in factors
        )

        assert factors == expected
        assert recompose_fgs(factors) == source

        if isinstance(shape, Terminal):
            terminal_count += 1
            assert factors == ()
        else:
            nonterminal_count += 1
            factor_occurrences += len(factors)
            assert factors

    assert terminal_count == 1
    assert nonterminal_count == 109
    assert factor_occurrences > 0


def test_native_fgs_preserves_order_and_multiplicity_explicitly() -> None:
    module = _load_native_module()
    native_fgs = getattr(module, "native_fgs", None)

    assert callable(native_fgs), "native_fgs must be callable"

    terminal = Terminal()
    nested = OrderedGroup(children=(Terminal(),))

    source_shape = OrderedGroup(
        children=(
            terminal,
            nested,
            terminal,
        )
    )

    source = encode_geometry(source_shape)
    expected = (
        encode_geometry(terminal),
        encode_geometry(nested),
        encode_geometry(terminal),
    )

    factors = native_fgs(source)

    assert factors == expected
    assert factors[0] == factors[2]
    assert factors[1] != factors[0]



def _expected_recursive_structure(
    shape: VisionShape,
) -> tuple[object, ...]:
    if isinstance(shape, Terminal):
        return ()

    return tuple(
        _expected_recursive_structure(child)
        for child in shape.children
    )


def _native_recursive_structure(
    module: ModuleType,
    geometry: OrthogonalGeometry,
) -> tuple[tuple[object, ...], int]:
    factors = module.native_fgs(geometry)

    assert module.recompose_fgs(factors) == geometry

    children: list[object] = []
    occurrence_count = 0

    for factor in factors:
        child_structure, child_occurrences = (
            _native_recursive_structure(
                module,
                factor,
            )
        )
        children.append(child_structure)
        occurrence_count += 1 + child_occurrences

    return tuple(children), occurrence_count


def _geometry_from_cells(
    cells: set[tuple[int, int]],
) -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=tuple(sorted(cells)),
    )


def test_recursive_native_fgs_matches_all_574_phase_1_child_occurrences() -> None:
    module = _load_native_module()
    corpus = _phase_1_corpus()

    total_occurrences = 0

    for shape in corpus:
        source = encode_geometry(shape)

        actual, occurrence_count = _native_recursive_structure(
            module,
            source,
        )
        expected = _expected_recursive_structure(shape)

        assert actual == expected
        total_occurrences += occurrence_count

    assert len(corpus) == 110
    assert total_occurrences == 574


def test_native_fgs_rejects_noncanonical_translation() -> None:
    module = _load_native_module()

    translated_terminal = OrthogonalGeometry(
        cells=((17, -11),)
    )

    with pytest.raises(
        module.FGSGeometryError,
        match="canonical minimum",
    ):
        module.native_fgs(translated_terminal)


def test_native_fgs_rejects_root_level_malformed_geometries() -> None:
    module = _load_native_module()

    unary = set(
        encode_geometry(
            OrderedGroup(children=(Terminal(),))
        ).cells
    )

    incomplete_outer_frame = set(unary)
    incomplete_outer_frame.remove((2, 0))

    empty_bay = set(unary)
    empty_bay.remove((2, 2))

    horizontal_clearance = set(unary)
    horizontal_clearance.remove((2, 2))
    horizontal_clearance.add((1, 2))

    extra_separator = set(unary)
    extra_separator.update(
        (3, y)
        for y in range(1, 4)
    )

    malformed = (
        _geometry_from_cells(incomplete_outer_frame),
        _geometry_from_cells(empty_bay),
        _geometry_from_cells(horizontal_clearance),
        _geometry_from_cells(extra_separator),
    )

    for geometry in malformed:
        with pytest.raises(module.FGSGeometryError):
            module.native_fgs(geometry)


def test_recursive_native_fgs_rejects_malformed_nested_factor() -> None:
    module = _load_native_module()

    source = encode_geometry(
        OrderedGroup(
            children=(
                OrderedGroup(
                    children=(Terminal(),)
                ),
            )
        )
    )
    cells = set(source.cells)

    # The immediate child occupies x=2..6, y=2..6.
    # Remove one non-corner cell from that child's bottom frame.
    # The root bay itself remains geometrically valid, so native FGS
    # must extract the malformed child successfully and reject it only
    # when recursion reaches that child geometry.
    cells.remove((4, 2))

    malformed_parent = _geometry_from_cells(cells)

    immediate = module.native_fgs(malformed_parent)

    assert len(immediate) == 1
    assert immediate[0].cells != encode_geometry(
        OrderedGroup(children=(Terminal(),))
    ).cells

    with pytest.raises(
        module.FGSGeometryError,
        match="outer frame is incomplete",
    ):
        module.native_fgs(immediate[0])

    with pytest.raises(
        module.FGSGeometryError,
        match="outer frame is incomplete",
    ):
        _native_recursive_structure(
            module,
            malformed_parent,
        )


def test_native_fgs_source_boundary_is_geometry_only() -> None:
    import ast

    source = _NATIVE_MODULE_PATH.read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)

    imported_modules = {
        (node.level, node.module)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }

    assert imported_modules == {
        (0, "__future__"),
        (0, "collections.abc"),
        (0, "petra.vision.geometry"),
    }

    assert not any(
        isinstance(node, ast.Import)
        for node in ast.walk(tree)
    )

    geometry_imports = {
        alias.asname or alias.name
        for node in ast.walk(tree)
        if (
            isinstance(node, ast.ImportFrom)
            and node.level == 0
            and node.module == "petra.vision.geometry"
        )
        for alias in node.names
    }

    assert geometry_imports == {
        "OrthogonalGeometry",
        "geometry_extent",
    }

    forbidden_names = {
        "VisionShape",
        "Terminal",
        "OrderedGroup",
        "decode_geometry",
        "encode_geometry",
        "adapt_petra_shape",
        "restore_petra_shape",
        "shape_code",
        "resolve_address",
        "serialize_shape",
    }

    referenced_names = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
    }

    assert referenced_names.isdisjoint(forbidden_names)
