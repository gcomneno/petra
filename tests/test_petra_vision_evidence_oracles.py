"""Independent Phase 1 corpus, raw-cell path, and address evidence."""

from __future__ import annotations

from functools import lru_cache
import importlib.util
from itertools import product
from pathlib import Path
from types import ModuleType
from typing import TypeAlias

import pytest

from petra import (
    Address,
    AddressError,
    ResolvedAnchor,
    ResolvedSlot,
    ResolvedTerm,
    render_address,
    resolve_address,
)
from petra.addresses import ADDRESS_CROSSES_LEAF, ADDRESS_OUT_OF_RANGE
from petra.vision import (
    OrderedGroup,
    Terminal,
    VisionShape,
    adapt_petra_shape,
    encode_geometry,
    restore_petra_shape,
)


AbstractShape: TypeAlias = tuple[object, ...]
Cell: TypeAlias = tuple[int, int]

_TERMINAL: AbstractShape = ("T",)
_EXPECTED_COUNTS = {1: 1, 2: 1, 3: 2, 4: 5, 5: 12, 6: 28, 7: 61}
_TEST_DIRECTORY = Path(__file__).resolve().parent


def _abstract_encoding(shape: AbstractShape) -> str:
    if shape == _TERMINAL:
        return "T"

    tag, children = shape
    assert tag == "G"
    assert isinstance(children, tuple)
    return "G[" + ",".join(
        _abstract_encoding(child)
        for child in children
    ) + "]"


def _positive_compositions(
    total: int,
    parts: int,
) -> tuple[tuple[int, ...], ...]:
    if parts == 1:
        return ((total,),) if total >= 1 else ()

    compositions: list[tuple[int, ...]] = []
    for first in range(1, total - parts + 2):
        for suffix in _positive_compositions(total - first, parts - 1):
            compositions.append((first, *suffix))
    return tuple(compositions)


@lru_cache(maxsize=None)
def _abstract_shapes_with_exact_nodes(
    node_count: int,
    remaining_depth: int,
) -> tuple[AbstractShape, ...]:
    shapes: set[AbstractShape] = {_TERMINAL} if node_count == 1 else set()

    if remaining_depth == 0 or node_count == 1:
        return tuple(sorted(shapes, key=_abstract_encoding))

    for width in range(1, min(3, node_count - 1) + 1):
        for child_counts in _positive_compositions(node_count - 1, width):
            child_domains = tuple(
                _abstract_shapes_with_exact_nodes(
                    child_count,
                    remaining_depth - 1,
                )
                for child_count in child_counts
            )
            if any(not domain for domain in child_domains):
                continue
            for children in product(*child_domains):
                shapes.add(("G", children))

    return tuple(sorted(shapes, key=_abstract_encoding))


def _abstract_corpus() -> tuple[AbstractShape, ...]:
    return tuple(sorted(
        (
            shape
            for node_count in range(1, 8)
            for shape in _abstract_shapes_with_exact_nodes(
                node_count,
                remaining_depth=3,
            )
        ),
        key=_abstract_encoding,
    ))


def _abstract_node_count(shape: AbstractShape) -> int:
    if shape == _TERMINAL:
        return 1
    children = shape[1]
    assert isinstance(children, tuple)
    return 1 + sum(_abstract_node_count(child) for child in children)


def _kernel_from_abstract(shape: AbstractShape) -> VisionShape:
    if shape == _TERMINAL:
        return Terminal()
    children = shape[1]
    assert isinstance(children, tuple)
    return OrderedGroup(
        children=tuple(_kernel_from_abstract(child) for child in children)
    )


def _abstract_from_kernel(shape: VisionShape) -> AbstractShape:
    if isinstance(shape, Terminal):
        return _TERMINAL
    assert isinstance(shape, OrderedGroup)
    return ("G", tuple(_abstract_from_kernel(child) for child in shape.children))


def _load_test_module(filename: str) -> ModuleType:
    path = _TEST_DIRECTORY / filename
    module_name = "_petra_vision_evidence_" + path.stem
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _project_existing_corpus(
    filename: str,
    corpus_name: str,
) -> tuple[AbstractShape, ...]:
    module = _load_test_module(filename)
    candidate = getattr(module, corpus_name)
    corpus = candidate() if callable(candidate) else candidate
    return tuple(_abstract_from_kernel(shape) for shape in corpus)


@pytest.mark.parametrize(
    ("filename", "corpus_name"),
    (
        ("test_petra_vision_geometry.py", "PHASE_1_CORPUS"),
        ("test_petra_vision_adapter.py", "PHASE_1_CORPUS"),
        ("test_petra_vision_dependencies.py", "_bounded_phase_1_corpus"),
    ),
)
def test_existing_core_corpora_match_the_independent_abstract_grammar(
    filename: str,
    corpus_name: str,
) -> None:
    projected = _project_existing_corpus(filename, corpus_name)
    reloaded_projected = _project_existing_corpus(filename, corpus_name)
    expected = _abstract_corpus()

    assert {
        node_count: len(_abstract_shapes_with_exact_nodes(node_count, 3))
        for node_count in range(1, 8)
    } == _EXPECTED_COUNTS
    assert len(expected) == 110
    assert len(set(expected)) == 110
    assert len(set(projected)) == 110
    assert tuple(
        sorted(projected, key=_abstract_encoding)
    ) == expected
    assert projected == reloaded_projected
    assert {
        node_count: sum(
            _abstract_node_count(shape) == node_count
            for shape in projected
        )
        for node_count in range(1, 8)
    } == _EXPECTED_COUNTS


class GeometryPathOutOfRange(IndexError):
    """A raw-cell path selected no bay at its current geometry."""


class GeometryPathCrossesTerminal(IndexError):
    """A raw-cell path attempted to continue after a terminal child."""


def _normalize_cells(cells: tuple[Cell, ...]) -> tuple[Cell, ...]:
    minimum_x = min(x for x, _ in cells)
    minimum_y = min(y for _, y in cells)
    return tuple(sorted((x - minimum_x, y - minimum_y) for x, y in cells))


def _raw_cell_child(
    cells: tuple[Cell, ...],
    index: int,
    *,
    continuation: bool,
) -> tuple[Cell, ...]:
    normalized = _normalize_cells(cells)
    occupied = set(normalized)

    if occupied == {(0, 0)}:
        if continuation:
            raise GeometryPathCrossesTerminal()
        raise GeometryPathOutOfRange()

    width = max(x for x, _ in normalized) + 1
    height = max(y for _, y in normalized) + 1
    boundaries = tuple(
        x
        for x in range(width)
        if all((x, y) in occupied for y in range(height))
    )
    bays = tuple(zip(boundaries, boundaries[1:]))

    if index >= len(bays):
        raise GeometryPathOutOfRange()

    left, right = bays[index]
    child_cells = tuple(
        sorted(
            (x, y)
            for x, y in occupied
            if left < x < right and 0 < y < height - 1
        )
    )
    assert child_cells
    return _normalize_cells(child_cells)


def _raw_cell_geometry_at_path(
    cells: tuple[Cell, ...],
    path: tuple[int, ...],
) -> tuple[Cell, ...]:
    current = _normalize_cells(cells)
    for position, index in enumerate(path):
        current = _raw_cell_child(
            current,
            index,
            continuation=position > 0,
        )
    return current


def _abstract_at_path(
    shape: AbstractShape,
    path: tuple[int, ...],
) -> AbstractShape:
    current = shape
    for index in path:
        children = current[1]
        assert isinstance(children, tuple)
        current = children[index]
    return current


def _non_root_paths(
    shape: AbstractShape,
    prefix: tuple[int, ...] = (),
) -> tuple[tuple[int, ...], ...]:
    if shape == _TERMINAL:
        return ()

    children = shape[1]
    assert isinstance(children, tuple)
    paths: list[tuple[int, ...]] = []
    for index, child in enumerate(children):
        path = (*prefix, index)
        paths.append(path)
        paths.extend(_non_root_paths(child, path))
    return tuple(paths)


def test_raw_cell_paths_match_abstract_subshapes_and_native_addresses() -> None:
    anchors = 0
    geometry_paths = 0
    term_resolutions = 0
    exponent_slot_resolutions = 0

    for abstract_shape in _abstract_corpus():
        kernel_shape = _kernel_from_abstract(abstract_shape)
        root_geometry = encode_geometry(kernel_shape)
        restored = restore_petra_shape(kernel_shape)

        anchor = resolve_address(restored, "@/")
        assert type(anchor) is ResolvedAnchor
        assert anchor.shape is restored
        assert adapt_petra_shape(anchor.shape) == kernel_shape
        anchors += 1

        for path in _non_root_paths(abstract_shape):
            expected_abstract = _abstract_at_path(abstract_shape, path)
            expected_kernel = _kernel_from_abstract(expected_abstract)
            extracted_cells = _raw_cell_geometry_at_path(
                root_geometry.cells,
                path,
            )

            assert extracted_cells == encode_geometry(expected_kernel).cells

            term_text = render_address(Address(indices=path))
            slot_text = render_address(Address(indices=path, is_slot=True))
            term = resolve_address(restored, term_text)
            slot = resolve_address(restored, slot_text)

            assert type(term) is ResolvedTerm
            assert type(slot) is ResolvedSlot
            assert term.address.indices == path
            assert slot.address.indices == path
            assert term.term.root.rank == path[-1]
            assert slot.owner is term.term
            assert slot.target is slot.owner.exponent
            assert adapt_petra_shape(slot.target) == expected_kernel
            geometry_paths += 1
            term_resolutions += 1
            exponent_slot_resolutions += 1

    assert anchors == 110
    assert geometry_paths == 574
    assert term_resolutions == 574
    assert exponent_slot_resolutions == 574
    assert anchors + term_resolutions + exponent_slot_resolutions == 1_258


@pytest.mark.parametrize(
    ("abstract_shape", "path", "raw_error", "native_reason"),
    (
        (_TERMINAL, (0,), GeometryPathOutOfRange, ADDRESS_OUT_OF_RANGE),
        (
            ("G", (_TERMINAL,)),
            (0, 0),
            GeometryPathCrossesTerminal,
            ADDRESS_CROSSES_LEAF,
        ),
        (
            ("G", (_TERMINAL, _TERMINAL)),
            (2,),
            GeometryPathOutOfRange,
            ADDRESS_OUT_OF_RANGE,
        ),
    ),
)
def test_raw_cell_path_failures_match_native_address_failures(
    abstract_shape: AbstractShape,
    path: tuple[int, ...],
    raw_error: type[IndexError],
    native_reason: str,
) -> None:
    kernel_shape = _kernel_from_abstract(abstract_shape)

    with pytest.raises(raw_error):
        _raw_cell_geometry_at_path(encode_geometry(kernel_shape).cells, path)

    with pytest.raises(AddressError) as error:
        resolve_address(
            restore_petra_shape(kernel_shape),
            render_address(Address(indices=path)),
        )

    assert error.value.reason == native_reason
