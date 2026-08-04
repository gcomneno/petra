from __future__ import annotations

import ast
import inspect
from functools import lru_cache
from itertools import product

import pytest

from petra import (
    Address,
    AddressError,
    Container,
    Leaf,
    ResolvedAnchor,
    ResolvedSlot,
    ResolvedTerm,
    Root,
    Term,
    render_address,
    resolve_address,
    serialize_shape,
    validate_shape,
)
from petra.vision import (
    OrderedGroup,
    Terminal,
    VisionShape,
    adapt_petra_shape,
    decode_geometry,
    encode_geometry,
    restore_petra_shape,
    validate_vision_shape,
    VISION_SHAPE_OUT_OF_BOUNDS,
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


def _kernel_shape_at_path(
    shape: VisionShape,
    path: tuple[int, ...],
) -> VisionShape:
    current = shape

    for index in path:
        if isinstance(current, Terminal):
            raise IndexError("cannot traverse beyond a terminal")

        current = current.children[index]

    return current


def _kernel_child_occurrences(
    shape: VisionShape,
) -> tuple[tuple[tuple[int, ...], VisionShape], ...]:
    occurrences: list[tuple[tuple[int, ...], VisionShape]] = []
    pending: list[tuple[tuple[int, ...], VisionShape]] = [((), shape)]

    while pending:
        path, current = pending.pop()

        if isinstance(current, Terminal):
            continue

        for index in reversed(range(len(current.children))):
            child = current.children[index]
            child_path = (*path, index)
            occurrences.append((child_path, child))
            pending.append((child_path, child))

    return tuple(occurrences)


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


def test_every_bounded_geometry_path_matches_native_address_projection() -> None:
    anchors = 0
    child_paths = 0
    term_resolutions = 0
    slot_resolutions = 0

    for vision_shape in PHASE_1_CORPUS:
        decoded = decode_geometry(encode_geometry(vision_shape))

        assert decoded == vision_shape

        restored = restore_petra_shape(decoded)
        anchor = resolve_address(restored, "@/")

        assert type(anchor) is ResolvedAnchor
        assert anchor.shape is restored
        assert adapt_petra_shape(anchor.shape) == decoded
        anchors += 1

        for path, enumerated_child in _kernel_child_occurrences(decoded):
            expected_child = _kernel_shape_at_path(decoded, path)
            term_text = render_address(Address(indices=path))
            slot_text = render_address(
                Address(indices=path, is_slot=True)
            )
            term = resolve_address(restored, term_text)
            slot = resolve_address(restored, slot_text)

            assert expected_child == enumerated_child
            assert type(term) is ResolvedTerm
            assert type(slot) is ResolvedSlot
            assert term.address.indices == path
            assert slot.address.indices == path
            assert term.term.root.rank == path[-1]
            assert slot.owner is term.term
            assert slot.target is slot.owner.exponent
            assert adapt_petra_shape(slot.target) == expected_child
            child_paths += 1
            term_resolutions += 1
            slot_resolutions += 1

    assert anchors == 110
    assert child_paths == 574
    assert term_resolutions == 574
    assert slot_resolutions == 574
    assert anchors + term_resolutions + slot_resolutions == 1_258


@pytest.mark.parametrize(
    ("vision_shape", "path", "reason"),
    [
        (Terminal(), (0,), "address-out-of-range"),
        (
            OrderedGroup(children=(Terminal(),)),
            (0, 0),
            "address-crosses-leaf",
        ),
        (
            OrderedGroup(children=(Terminal(), Terminal())),
            (2,),
            "address-out-of-range",
        ),
    ],
)
def test_kernel_path_failures_match_native_address_failures(
    vision_shape: VisionShape,
    path: tuple[int, ...],
    reason: str,
) -> None:
    with pytest.raises(IndexError):
        _kernel_shape_at_path(vision_shape, path)

    address = render_address(Address(indices=path))

    with pytest.raises(AddressError) as error:
        resolve_address(restore_petra_shape(vision_shape), address)

    assert error.value.reason == reason


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


def test_adapter_accepts_exact_native_leaf_and_container_records() -> None:
    leaf = Leaf()
    container = Container(
        terms=(Term(root=Root(0), exponent=leaf),)
    )

    assert adapt_petra_shape(leaf) == Terminal()
    assert adapt_petra_shape(container) == OrderedGroup(
        children=(Terminal(),)
    )


@pytest.mark.parametrize(
    "malformed",
    [
        type("LeafSubclass", (Leaf,), {})(),
        type(
            "ContainerSubclass",
            (Container,),
            {},
        )(
            terms=(Term(root=Root(0), exponent=Leaf()),)
        ),
        Container(
            terms=(
                type("TermSubclass", (Term,), {})(
                    root=Root(0),
                    exponent=Leaf(),
                ),
            )
        ),
        Container(
            terms=(
                Term(
                    root=type("RootSubclass", (Root,), {})(0),
                    exponent=Leaf(),
                ),
            )
        ),
    ],
)
def test_adapter_rejects_native_runtime_subclasses(
    malformed: object,
) -> None:
    with pytest.raises(TypeError):
        adapt_petra_shape(malformed)  # type: ignore[arg-type]


def test_adapter_rejects_post_construction_container_terms_list() -> None:
    corrupted = Container(
        terms=(Term(root=Root(0), exponent=Leaf()),)
    )
    object.__setattr__(corrupted, "terms", [corrupted.terms[0]])

    with pytest.raises(TypeError, match="exact tuple"):
        adapt_petra_shape(corrupted)


@pytest.mark.parametrize(
    "corrupt",
    [
        lambda term: object.__setattr__(term, "root", object()),
        lambda term: object.__setattr__(term.root, "rank", True),
        lambda term: object.__setattr__(term.root, "rank", -1),
        lambda term: object.__setattr__(term, "exponent", object()),
    ],
)
def test_adapter_rejects_corrupted_term_roots_and_exponents(
    corrupt: object,
) -> None:
    term = Term(root=Root(0), exponent=Leaf())
    native = Container(terms=(term,))

    corrupt(term)  # type: ignore[operator]

    with pytest.raises((TypeError, ValueError)):
        adapt_petra_shape(native)


def test_adapter_rejects_a_manually_injected_native_cycle() -> None:
    term = Term(root=Root(0), exponent=Leaf())
    cyclic = Container(terms=(term,))
    object.__setattr__(term, "exponent", cyclic)

    with pytest.raises(ValueError, match="must be acyclic"):
        adapt_petra_shape(cyclic)


def test_adapter_rejects_out_of_bounds_native_shape_before_validation() -> None:
    deep: Leaf | Container = Leaf()
    for _ in range(1_100):
        deep = Container(terms=(Term(root=Root(0), exponent=deep),))

    with pytest.raises(ValueError, match=VISION_SHAPE_OUT_OF_BOUNDS):
        adapt_petra_shape(deep)


def test_adapter_gives_bounds_first_precedence_to_malformed_width_four() -> None:
    corrupted = Container(terms=(Term(root=Root(0), exponent=Leaf()),))
    object.__setattr__(
        corrupted,
        "terms",
        (
            object(),
            Term(root=Root(1), exponent=Leaf()),
            Term(root=Root(2), exponent=Leaf()),
            Term(root=Root(3), exponent=Leaf()),
        ),
    )

    with pytest.raises(ValueError, match=VISION_SHAPE_OUT_OF_BOUNDS):
        adapt_petra_shape(corrupted)


def test_adapter_counts_shared_native_children_by_occurrence() -> None:
    shared = Container(
        terms=(
            Term(root=Root(0), exponent=Leaf()),
            Term(root=Root(1), exponent=Leaf()),
        )
    )
    eight_occurrences = Container(
        terms=(
            Term(root=Root(0), exponent=shared),
            Term(root=Root(1), exponent=shared),
            Term(root=Root(2), exponent=Leaf()),
        )
    )

    with pytest.raises(ValueError, match=VISION_SHAPE_OUT_OF_BOUNDS):
        adapt_petra_shape(eight_occurrences)


def test_restore_and_encoding_reject_deep_hostile_kernel_chain() -> None:
    deep: Terminal | OrderedGroup = Terminal()
    for _ in range(1_100):
        deep = OrderedGroup(children=(deep,))

    with pytest.raises(ValueError, match=VISION_SHAPE_OUT_OF_BOUNDS):
        restore_petra_shape(deep)

    with pytest.raises(ValueError, match=VISION_SHAPE_OUT_OF_BOUNDS):
        encode_geometry(deep)


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
