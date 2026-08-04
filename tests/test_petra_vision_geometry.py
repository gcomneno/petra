from __future__ import annotations

import ast
import copy
import inspect
from dataclasses import fields
from functools import lru_cache
from itertools import product

import pytest

from petra.vision import (
    GEOMETRY_MALFORMED,
    GeometrySyntaxError,
    OrderedGroup,
    OrthogonalGeometry,
    Terminal,
    VisionShape,
    decode_geometry,
    encode_geometry,
    geometry_extent,
    normalize_geometry,
)


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
                shapes.add(
                    OrderedGroup(children=children)
                )

    return tuple(sorted(shapes, key=repr))


def _bounded_phase_1_corpus() -> tuple[VisionShape, ...]:
    shapes: set[VisionShape] = set()

    for node_count in range(1, 8):
        shapes.update(
            _shapes_with_exact_nodes(
                node_count,
                maximum_depth=3,
            )
        )

    return tuple(sorted(shapes, key=repr))


PHASE_1_CORPUS = _bounded_phase_1_corpus()


def _geometry_from_cells(
    cells: set[tuple[int, int]],
) -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=tuple(sorted(cells)),
    )


def _frame_cells(
    width: int,
    height: int,
) -> set[tuple[int, int]]:
    return (
        {(x, 0) for x in range(width)}
        | {(x, height - 1) for x in range(width)}
        | {(0, y) for y in range(height)}
        | {(width - 1, y) for y in range(height)}
    )


def test_geometry_record_contains_only_canonical_cells() -> None:
    assert tuple(
        field.name
        for field in fields(OrthogonalGeometry)
    ) == ("cells",)

    geometry = OrthogonalGeometry(
        cells=((0, 0), (1, 0)),
    )

    assert geometry.cells == ((0, 0), (1, 0))


def test_geometry_record_rejects_malformed_cell_data() -> None:
    with pytest.raises(TypeError, match="must be a tuple"):
        OrthogonalGeometry(  # type: ignore[arg-type]
            cells=[(0, 0)]
        )

    with pytest.raises(ValueError, match="non-empty"):
        OrthogonalGeometry(cells=())

    with pytest.raises(TypeError, match="exact integers"):
        OrthogonalGeometry(cells=((0, True),))

    with pytest.raises(ValueError, match="canonical coordinate order"):
        OrthogonalGeometry(
            cells=((1, 0), (0, 0))
        )

    with pytest.raises(ValueError, match="duplicates"):
        OrthogonalGeometry(
            cells=((0, 0), (0, 0))
        )


def test_terminal_is_one_solid_unit_cell_at_the_origin() -> None:
    geometry = encode_geometry(Terminal())

    assert geometry == OrthogonalGeometry(
        cells=((0, 0),)
    )
    assert geometry_extent(geometry) == (1, 1)
    assert decode_geometry(geometry) == Terminal()


def test_unary_terminal_group_has_the_minimal_five_by_five_frame() -> None:
    shape = OrderedGroup(
        children=(Terminal(),)
    )

    geometry = encode_geometry(shape)

    expected_cells = _frame_cells(5, 5)
    expected_cells.add((2, 2))

    assert geometry_extent(geometry) == (5, 5)
    assert set(geometry.cells) == expected_cells
    assert decode_geometry(geometry) == shape


def test_two_terminal_children_share_one_complete_separator() -> None:
    shape = OrderedGroup(
        children=(Terminal(), Terminal())
    )

    geometry = encode_geometry(shape)

    expected_cells = _frame_cells(9, 5)
    expected_cells.update(
        (4, y)
        for y in range(5)
    )
    expected_cells.update(
        {
            (2, 2),
            (6, 2),
        }
    )

    assert geometry_extent(geometry) == (9, 5)
    assert set(geometry.cells) == expected_cells
    assert decode_geometry(geometry) == shape


def test_children_with_different_heights_share_the_canonical_top() -> None:
    shape = OrderedGroup(
        children=(
            Terminal(),
            OrderedGroup(children=(Terminal(),)),
        )
    )

    geometry = encode_geometry(shape)

    assert geometry_extent(geometry) == (13, 9)

    first_bay_child = {
        (x, y)
        for x, y in geometry.cells
        if 0 < x < 4 and 0 < y < 8
    }
    second_bay_child = {
        (x, y)
        for x, y in geometry.cells
        if 4 < x < 12 and 0 < y < 8
    }

    assert first_bay_child == {(2, 6)}
    assert max(y for _, y in first_bay_child) == 6
    assert max(y for _, y in second_bay_child) == 6


def test_bay_widths_and_container_height_derive_from_children() -> None:
    shallow = Terminal()
    deep = OrderedGroup(
        children=(Terminal(),)
    )
    shape = OrderedGroup(
        children=(shallow, deep)
    )

    shallow_geometry = encode_geometry(shallow)
    deep_geometry = encode_geometry(deep)
    geometry = encode_geometry(shape)

    shallow_width, shallow_height = geometry_extent(
        shallow_geometry
    )
    deep_width, deep_height = geometry_extent(deep_geometry)

    expected_width = (
        1
        + shallow_width
        + 3
        + deep_width
        + 3
    )
    expected_height = max(
        shallow_height,
        deep_height,
    ) + 4

    assert geometry_extent(geometry) == (
        expected_width,
        expected_height,
    )


@pytest.mark.parametrize(
    "shape",
    PHASE_1_CORPUS,
)
def test_every_phase_1_shape_roundtrips_through_geometry(
    shape: VisionShape,
) -> None:
    geometry = encode_geometry(shape)
    decoded = decode_geometry(geometry)

    assert min(x for x, _ in geometry.cells) == 0
    assert min(y for _, y in geometry.cells) == 0
    assert decoded == shape
    assert encode_geometry(decoded) == geometry


@pytest.mark.parametrize(
    "shape",
    PHASE_1_CORPUS,
)
def test_geometry_is_deterministic_across_equal_allocations(
    shape: VisionShape,
) -> None:
    independent = copy.deepcopy(shape)

    assert independent == shape
    assert encode_geometry(independent) == encode_geometry(shape)


def test_phase_1_geometry_is_injective_over_the_bounded_corpus() -> None:
    geometries = {
        encode_geometry(shape)
        for shape in PHASE_1_CORPUS
    }

    assert len(PHASE_1_CORPUS) == 110
    assert len(geometries) == len(PHASE_1_CORPUS)


def test_child_order_is_carried_only_by_bay_position() -> None:
    terminal = Terminal()
    nested = OrderedGroup(
        children=(Terminal(),)
    )

    left = OrderedGroup(
        children=(terminal, nested)
    )
    right = OrderedGroup(
        children=(nested, terminal)
    )

    left_geometry = encode_geometry(left)
    right_geometry = encode_geometry(right)

    assert left_geometry != right_geometry
    assert len({left_geometry, right_geometry}) == 2
    assert decode_geometry(left_geometry) == left
    assert decode_geometry(right_geometry) == right


def test_global_translation_is_the_only_normalised_transform() -> None:
    shape = OrderedGroup(
        children=(
            Terminal(),
            OrderedGroup(children=(Terminal(),)),
        )
    )
    canonical = encode_geometry(shape)

    translated = OrthogonalGeometry(
        cells=tuple(
            sorted(
                (x + 17, y - 11)
                for x, y in canonical.cells
            )
        )
    )

    assert translated != canonical
    assert normalize_geometry(translated) == canonical
    assert decode_geometry(translated) == shape


def test_decoder_rejects_incomplete_outer_frame() -> None:
    cells = set(
        encode_geometry(
            OrderedGroup(children=(Terminal(),))
        ).cells
    )
    cells.remove((2, 0))

    with pytest.raises(
        GeometrySyntaxError,
        match=GEOMETRY_MALFORMED,
    ):
        decode_geometry(_geometry_from_cells(cells))


def test_decoder_rejects_incomplete_separator() -> None:
    cells = set(
        encode_geometry(
            OrderedGroup(
                children=(Terminal(), Terminal())
            )
        ).cells
    )
    cells.remove((4, 2))

    with pytest.raises(
        GeometrySyntaxError,
        match=GEOMETRY_MALFORMED,
    ):
        decode_geometry(_geometry_from_cells(cells))


def test_decoder_rejects_empty_bay() -> None:
    cells = set(
        encode_geometry(
            OrderedGroup(children=(Terminal(),))
        ).cells
    )
    cells.remove((2, 2))

    with pytest.raises(
        GeometrySyntaxError,
        match=GEOMETRY_MALFORMED,
    ):
        decode_geometry(_geometry_from_cells(cells))


def test_decoder_rejects_child_inside_clearance_region() -> None:
    cells = set(
        encode_geometry(
            OrderedGroup(children=(Terminal(),))
        ).cells
    )
    cells.remove((2, 2))
    cells.add((1, 2))

    with pytest.raises(
        GeometrySyntaxError,
        match=GEOMETRY_MALFORMED,
    ):
        decode_geometry(_geometry_from_cells(cells))


def test_decoder_rejects_primitive_outside_the_canonical_frame() -> None:
    cells = set(
        encode_geometry(
            OrderedGroup(children=(Terminal(),))
        ).cells
    )
    cells.add((5, 2))

    with pytest.raises(
        GeometrySyntaxError,
        match=GEOMETRY_MALFORMED,
    ):
        decode_geometry(_geometry_from_cells(cells))


def test_decoder_rejects_an_extra_full_height_separator() -> None:
    cells = set(
        encode_geometry(
            OrderedGroup(children=(Terminal(),))
        ).cells
    )
    cells.update(
        (3, y)
        for y in range(1, 4)
    )

    with pytest.raises(
        GeometrySyntaxError,
        match=GEOMETRY_MALFORMED,
    ):
        decode_geometry(_geometry_from_cells(cells))


def test_decoder_rejects_two_disconnected_children_in_one_bay() -> None:
    cells = _frame_cells(7, 5)
    cells.update(
        {
            (2, 2),
            (4, 2),
        }
    )

    with pytest.raises(
        GeometrySyntaxError,
        match=GEOMETRY_MALFORMED,
    ):
        decode_geometry(_geometry_from_cells(cells))


def test_decoder_rejects_a_nonterminal_solid_block() -> None:
    solid = _geometry_from_cells(
        {
            (x, y)
            for x in range(5)
            for y in range(5)
        }
    )

    with pytest.raises(
        GeometrySyntaxError,
        match=GEOMETRY_MALFORMED,
    ):
        decode_geometry(solid)


def test_decoder_rejects_small_hollow_object_as_a_container() -> None:
    hollow = _geometry_from_cells(
        _frame_cells(3, 3)
    )

    with pytest.raises(
        GeometrySyntaxError,
        match=GEOMETRY_MALFORMED,
    ):
        decode_geometry(hollow)


def test_horizontal_reflection_is_a_different_valid_message() -> None:
    left = OrderedGroup(
        children=(
            Terminal(),
            OrderedGroup(children=(Terminal(),)),
        )
    )
    left_geometry = encode_geometry(left)
    width, _ = geometry_extent(left_geometry)

    reflected = OrthogonalGeometry(
        cells=tuple(
            sorted(
                (width - 1 - x, y)
                for x, y in left_geometry.cells
            )
        )
    )

    right = OrderedGroup(
        children=(
            OrderedGroup(children=(Terminal(),)),
            Terminal(),
        )
    )

    assert reflected != left_geometry
    assert decode_geometry(reflected) == right
    assert encode_geometry(right) == reflected


def test_half_turn_is_not_a_normalised_equivalent_transform() -> None:
    shape = OrderedGroup(
        children=(
            Terminal(),
            OrderedGroup(children=(Terminal(),)),
        )
    )
    geometry = encode_geometry(shape)
    width, height = geometry_extent(geometry)

    rotated = OrthogonalGeometry(
        cells=tuple(
            sorted(
                (
                    width - 1 - x,
                    height - 1 - y,
                )
                for x, y in geometry.cells
            )
        )
    )

    with pytest.raises(
        GeometrySyntaxError,
        match=GEOMETRY_MALFORMED,
    ):
        decode_geometry(rotated)


def test_encoder_rejects_a_manually_injected_kernel_cycle() -> None:
    cyclic = OrderedGroup(children=(Terminal(),))

    object.__setattr__(
        cyclic,
        "children",
        (cyclic,),
    )

    with pytest.raises(ValueError, match="must be acyclic"):
        encode_geometry(cyclic)


@pytest.mark.parametrize(
    "malformed",
    [
        None,
        1,
        (),
        object(),
    ],
)
def test_encoder_rejects_non_kernel_values(
    malformed: object,
) -> None:
    with pytest.raises(TypeError):
        encode_geometry(  # type: ignore[arg-type]
            malformed
        )


@pytest.mark.parametrize(
    "malformed",
    [
        None,
        1,
        (),
        object(),
    ],
)
def test_decoder_rejects_non_geometry_values(
    malformed: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="expected an OrthogonalGeometry",
    ):
        decode_geometry(  # type: ignore[arg-type]
            malformed
        )


def test_geometry_module_has_no_petra_or_hidden_channel_dependency() -> None:
    import petra.vision.geometry as geometry

    names = set(vars(geometry))

    forbidden_names = {
        "Container",
        "Leaf",
        "Root",
        "Term",
        "adapt_petra_shape",
        "parse_shape",
        "resolve_address",
        "serialize_shape",
        "to_canonical_data",
    }

    assert names.isdisjoint(forbidden_names)

    tree = ast.parse(inspect.getsource(geometry))

    imported_modules = {
        (node.level, node.module)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }

    assert imported_modules == {
        (0, "__future__"),
        (0, "collections.abc"),
        (0, "dataclasses"),
        (0, "typing"),
        (1, "kernel"),
    }

    assert not any(
        isinstance(node, ast.Import)
        for node in ast.walk(tree)
    )
