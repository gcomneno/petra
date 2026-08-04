from __future__ import annotations

import ast
import inspect
from functools import lru_cache
from itertools import product

import pytest

from petra import (
    Container,
    Leaf,
    Root,
    Term,
    serialize_shape,
    validate_shape,
)
from petra.vision import (
    OrderedGroup,
    Terminal,
    VisionShape,
    adapt_petra_shape,
    restore_petra_shape,
    validate_vision_shape,
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
        return tuple(
            sorted(shapes, key=repr)
        )

    child_node_budget = node_count - 1

    for width in range(1, 4):
        for partition in _positive_compositions(
            child_node_budget,
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

    return tuple(
        sorted(shapes, key=repr)
    )


def bounded_phase_1_corpus() -> tuple[VisionShape, ...]:
    shapes: set[VisionShape] = set()

    for node_count in range(1, 8):
        shapes.update(
            _shapes_with_exact_nodes(
                node_count,
                maximum_depth=3,
            )
        )

    return tuple(
        sorted(shapes, key=repr)
    )


PHASE_1_CORPUS = bounded_phase_1_corpus()


def _shape_metrics(
    shape: VisionShape,
) -> tuple[int, int, int]:
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

        maximum_width = max(
            maximum_width,
            len(current.children),
        )

        for child in current.children:
            pending.append((child, depth + 1))

    return (
        node_count,
        maximum_depth,
        maximum_width,
    )


def test_phase_1_corpus_has_expected_exhaustive_size() -> None:
    assert len(PHASE_1_CORPUS) == 110
    assert len(set(PHASE_1_CORPUS)) == 110


def test_phase_1_corpus_respects_all_normative_bounds() -> None:
    for shape in PHASE_1_CORPUS:
        node_count, depth, width = _shape_metrics(shape)

        assert node_count <= 7
        assert depth <= 3
        assert width <= 3


@pytest.mark.parametrize(
    "vision_shape",
    PHASE_1_CORPUS,
)
def test_every_bounded_kernel_shape_roundtrips_through_petra(
    vision_shape: VisionShape,
) -> None:
    validate_vision_shape(vision_shape)

    petra_shape = restore_petra_shape(vision_shape)

    assert validate_shape(petra_shape) is None
    assert adapt_petra_shape(petra_shape) == vision_shape


@pytest.mark.parametrize(
    "vision_shape",
    PHASE_1_CORPUS,
)
def test_every_mirrored_petra_shape_roundtrips_through_kernel(
    vision_shape: VisionShape,
) -> None:
    petra_shape = restore_petra_shape(vision_shape)
    restored = restore_petra_shape(
        adapt_petra_shape(petra_shape)
    )

    assert restored == petra_shape
    assert serialize_shape(restored) == serialize_shape(petra_shape)


def test_adapter_projects_native_petra_structure_only() -> None:
    native = Container(
        terms=(
            Term(root=Root(0), exponent=Leaf()),
            Term(
                root=Root(1),
                exponent=Container(
                    terms=(
                        Term(
                            root=Root(0),
                            exponent=Leaf(),
                        ),
                    )
                ),
            ),
        )
    )

    assert adapt_petra_shape(native) == OrderedGroup(
        children=(
            Terminal(),
            OrderedGroup(children=(Terminal(),)),
        )
    )


def test_restore_derives_canonical_root_ranks_from_child_order() -> None:
    vision = OrderedGroup(
        children=(
            Terminal(),
            OrderedGroup(children=(Terminal(),)),
            Terminal(),
        )
    )

    native = restore_petra_shape(vision)

    assert isinstance(native, Container)
    assert tuple(
        term.root.rank
        for term in native.terms
    ) == (0, 1, 2)
    assert validate_shape(native) is None


def test_adapter_rejects_noncanonical_native_root_ranks() -> None:
    noncanonical = Container(
        terms=(
            Term(root=Root(4), exponent=Leaf()),
        )
    )

    with pytest.raises(ValueError, match="expected r0"):
        adapt_petra_shape(noncanonical)


@pytest.mark.parametrize(
    "malformed",
    [
        None,
        1,
        (),
        object(),
    ],
)
def test_adapter_rejects_non_petra_values(
    malformed: object,
) -> None:
    with pytest.raises(TypeError):
        adapt_petra_shape(  # type: ignore[arg-type]
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
def test_restore_rejects_non_kernel_values(
    malformed: object,
) -> None:
    with pytest.raises(TypeError):
        restore_petra_shape(  # type: ignore[arg-type]
            malformed
        )


def test_adapter_does_not_mutate_native_input() -> None:
    native = Container(
        terms=(
            Term(root=Root(0), exponent=Leaf()),
            Term(root=Root(1), exponent=Leaf()),
        )
    )
    before = serialize_shape(native)

    projected = adapt_petra_shape(native)

    assert projected == OrderedGroup(
        children=(Terminal(), Terminal())
    )
    assert serialize_shape(native) == before


def test_restore_does_not_mutate_kernel_input() -> None:
    vision = OrderedGroup(
        children=(
            Terminal(),
            OrderedGroup(children=(Terminal(),)),
        )
    )
    before = repr(vision)

    restored = restore_petra_shape(vision)

    assert validate_shape(restored) is None
    assert repr(vision) == before


def test_adapter_output_is_independent_of_python_allocation() -> None:
    first = Container(
        terms=(
            Term(root=Root(0), exponent=Leaf()),
        )
    )
    second = Container(
        terms=(
            Term(root=Root(0), exponent=Leaf()),
        )
    )

    assert first is not second
    assert adapt_petra_shape(first) == adapt_petra_shape(second)


def test_adapter_module_has_no_forbidden_runtime_dependencies() -> None:
    import petra.vision.adapter as adapter

    names = set(vars(adapter))

    assert "serialize_shape" not in names
    assert "parse_shape" not in names
    assert "resolve_address" not in names
    assert "apply_sprout" not in names
    assert "apply_shed" not in names
    assert "apply_graft" not in names
    assert "apply_prune" not in names

    tree = ast.parse(inspect.getsource(adapter))

    absolute_imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }

    relative_imports = {
        (node.level, node.module)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }

    assert absolute_imports == set()
    assert relative_imports == {
        (0, "__future__"),
        (2, "model"),
        (1, "kernel"),
    }
