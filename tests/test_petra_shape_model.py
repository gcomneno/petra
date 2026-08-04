from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from itertools import product

import pytest

from petra import (
    Container,
    Leaf,
    Root,
    Term,
    normalize_shape,
    parse_shape,
    serialize_shape,
    to_canonical_data,
    validate_shape,
)


def leaf_term(rank: int) -> Term:
    return Term(root=Root(rank), exponent=Leaf())


def single_leaf_container(rank: int = 0) -> Container:
    return Container(terms=(leaf_term(rank),))


def deep_unary_shape(
    depth: int,
    terminal_width: int = 1,
) -> Container:
    shape: Leaf | Container = Leaf()
    for level in range(depth):
        if level == 0:
            shape = Container(
                terms=tuple(
                    Term(root=Root(rank), exponent=Leaf())
                    for rank in range(terminal_width)
                )
            )
        else:
            shape = Container(
                terms=(Term(root=Root(0), exponent=shape),)
            )
    assert isinstance(shape, Container)
    return shape


def test_leaf_is_the_unique_terminal_shape_value() -> None:
    first = Leaf()
    second = Leaf()

    assert first == second
    assert first is not second
    assert first != single_leaf_container()


def test_leaf_is_immutable() -> None:
    leaf = Leaf()

    with pytest.raises(FrozenInstanceError):
        leaf.unexpected = "mutation"  # type: ignore[attr-defined]


def test_root_exposes_only_its_canonical_rank_name() -> None:
    root = Root(2)

    assert root.rank == 2
    assert root.name == "r2"


def test_root_rejects_int_subclasses_before_they_can_format() -> None:
    class HostileInt(int):
        def __format__(self, format_spec: str) -> str:
            raise AssertionError("hostile formatting must not run")

    with pytest.raises(TypeError, match="root rank must be an int"):
        Root(HostileInt(0))


@pytest.mark.parametrize("rank", [-1, True, 1.5, "1"])
def test_root_rejects_invalid_ranks(rank: object) -> None:
    expected_error = ValueError if rank == -1 else TypeError

    with pytest.raises(expected_error):
        Root(rank)  # type: ignore[arg-type]


def test_root_is_immutable() -> None:
    root = Root(0)

    with pytest.raises(FrozenInstanceError):
        root.rank = 1  # type: ignore[misc]


def test_term_owns_one_root_and_one_complete_exponent_shape() -> None:
    exponent = single_leaf_container()
    term = Term(root=Root(0), exponent=exponent)

    assert term.root == Root(0)
    assert term.exponent == exponent


@pytest.mark.parametrize(
    ("root", "exponent"),
    [
        ("r0", Leaf()),
        (Root(0), None),
        (Root(0), 1),
        (Root(0), ()),
    ],
)
def test_term_rejects_malformed_relations(
    root: object,
    exponent: object,
) -> None:
    with pytest.raises(TypeError):
        Term(  # type: ignore[arg-type]
            root=root,
            exponent=exponent,
        )


def test_term_is_immutable() -> None:
    term = leaf_term(0)

    with pytest.raises(FrozenInstanceError):
        term.exponent = single_leaf_container()  # type: ignore[misc]


def test_container_requires_an_ordered_non_empty_term_tuple() -> None:
    first = leaf_term(0)
    second = leaf_term(1)
    container = Container(terms=(first, second))

    assert container.terms == (first, second)
    assert isinstance(container.terms, tuple)


def test_container_rejects_empty_or_malformed_term_sequences() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        Container(terms=())

    with pytest.raises(TypeError):
        Container(terms=[leaf_term(0)])  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        Container(terms=(Leaf(),))  # type: ignore[arg-type]


def test_container_is_deeply_immutable_through_its_public_shape() -> None:
    container = single_leaf_container()

    with pytest.raises(FrozenInstanceError):
        container.terms = ()  # type: ignore[misc]

    with pytest.raises(TypeError):
        container.terms[0] = leaf_term(0)  # type: ignore[index]


def test_validation_accepts_recursive_canonical_shapes() -> None:
    inner = single_leaf_container()
    shape = Container(
        terms=(
            Term(root=Root(0), exponent=inner),
            leaf_term(1),
        )
    )

    assert validate_shape(shape) is None


def test_validation_rejects_noncanonical_root_ranks() -> None:
    shape = Container(
        terms=(
            leaf_term(4),
            leaf_term(9),
        )
    )

    with pytest.raises(ValueError, match="expected r0"):
        validate_shape(shape)


def test_validation_rejects_nested_noncanonical_root_ranks() -> None:
    inner = single_leaf_container(rank=7)
    shape = Container(
        terms=(
            Term(root=Root(0), exponent=inner),
        )
    )

    with pytest.raises(ValueError, match="expected r0"):
        validate_shape(shape)


def test_normalization_reassigns_ranks_without_reordering_terms() -> None:
    shallow = Leaf()
    deep = single_leaf_container(rank=8)
    shape = Container(
        terms=(
            Term(root=Root(6), exponent=shallow),
            Term(root=Root(2), exponent=deep),
        )
    )

    normalized = normalize_shape(shape)

    assert [term.root.name for term in normalized.terms] == ["r0", "r1"]
    assert normalized.terms[0].exponent == shallow
    assert normalized.terms[1].exponent == single_leaf_container()
    assert validate_shape(normalized) is None


def test_normalization_is_recursive_deterministic_and_idempotent() -> None:
    inner = Container(
        terms=(
            leaf_term(9),
            leaf_term(3),
        )
    )
    shape = Container(
        terms=(
            Term(root=Root(5), exponent=inner),
        )
    )

    first = normalize_shape(shape)
    second = normalize_shape(shape)
    third = normalize_shape(first)

    assert first == second
    assert third == first
    assert validate_shape(first) is None


@pytest.mark.parametrize("malformed", [None, 1, (), (Leaf(),)])
def test_normalization_rejects_non_petra_input(malformed: object) -> None:
    with pytest.raises(TypeError):
        normalize_shape(malformed)  # type: ignore[arg-type]


def test_independently_allocated_canonical_shapes_compare_equal() -> None:
    left = Container(
        terms=(
            leaf_term(0),
            Term(root=Root(1), exponent=single_leaf_container()),
        )
    )
    right = Container(
        terms=(
            leaf_term(0),
            Term(root=Root(1), exponent=single_leaf_container()),
        )
    )

    assert left == right
    assert left is not right
    assert left.terms[0] is not right.terms[0]


def test_deep_shape_equality_hashing_and_round_trip_are_stack_safe() -> None:
    depth = 1_200
    left = deep_unary_shape(depth)
    right = deep_unary_shape(depth)

    assert left == right
    assert hash(left) == hash(right)
    assert {left, right} == {left}
    assert {left: "value"}[right] == "value"
    assert parse_shape(serialize_shape(left)) == left


def test_deep_shape_difference_near_terminal_region_is_detected() -> None:
    left = deep_unary_shape(1_200)
    right = deep_unary_shape(1_200, terminal_width=2)

    assert left != right


def test_deep_term_hashing_is_stack_safe_and_preserves_root_rank() -> None:
    left = Term(root=Root(0), exponent=deep_unary_shape(1_200))
    right = Term(root=Root(0), exponent=deep_unary_shape(1_200))

    assert left == right
    assert hash(left) == hash(right)
    assert left != Term(root=Root(1), exponent=right.exponent)
    assert left != object()
    assert left.exponent != object()


def test_order_is_structurally_significant() -> None:
    shallow = Leaf()
    deep = single_leaf_container()

    left = Container(
        terms=(
            Term(root=Root(0), exponent=shallow),
            Term(root=Root(1), exponent=deep),
        )
    )
    right = Container(
        terms=(
            Term(root=Root(0), exponent=deep),
            Term(root=Root(1), exponent=shallow),
        )
    )

    assert validate_shape(left) is None
    assert validate_shape(right) is None
    assert left != right


def test_multiple_leaf_terms_remain_distinct_by_position() -> None:
    shape = Container(
        terms=(
            leaf_term(0),
            leaf_term(1),
        )
    )

    assert shape.terms[0].exponent == shape.terms[1].exponent
    assert shape.terms[0].root != shape.terms[1].root
    assert shape.terms[0] != shape.terms[1]
    assert validate_shape(shape) is None


def test_canonical_data_is_deterministic_and_contains_no_numeric_projection() -> None:
    shape = Container(
        terms=(
            leaf_term(0),
            Term(root=Root(1), exponent=single_leaf_container()),
        )
    )

    assert to_canonical_data(shape) == (
        "container",
        (
            ("r0", ("leaf",)),
            (
                "r1",
                (
                    "container",
                    (
                        ("r0", ("leaf",)),
                    ),
                ),
            ),
        ),
    )


def test_canonical_data_requires_a_valid_canonical_shape() -> None:
    noncanonical = single_leaf_container(rank=6)

    with pytest.raises(ValueError, match="expected r0"):
        to_canonical_data(noncanonical)


# PROPERTY_STYLE_CONTRACT
def canonical_shapes(max_depth: int) -> tuple[Leaf | Container, ...]:
    """Enumerate a finite recursive PETRA shape domain."""

    cache: dict[int, tuple[Leaf | Container, ...]] = {}

    def build(depth: int) -> tuple[Leaf | Container, ...]:
        if depth in cache:
            return cache[depth]

        shapes: list[Leaf | Container] = [Leaf()]

        if depth > 0:
            exponent_shapes = build(depth - 1)

            for width in (1, 2):
                for exponents in product(
                    exponent_shapes,
                    repeat=width,
                ):
                    shapes.append(
                        Container(
                            terms=tuple(
                                Term(
                                    root=Root(rank),
                                    exponent=exponent,
                                )
                                for rank, exponent in enumerate(
                                    exponents
                                )
                            )
                        )
                    )

        cache[depth] = tuple(shapes)
        return cache[depth]

    return build(max_depth)


def shift_ranks_recursively(
    shape: Leaf | Container,
    offset: int = 3,
) -> Leaf | Container:
    """Build equivalent valid shape data with noncanonical ranks."""

    if isinstance(shape, Leaf):
        return Leaf()

    return Container(
        terms=tuple(
            Term(
                root=Root(offset + position),
                exponent=shift_ranks_recursively(
                    term.exponent,
                    offset + 1,
                ),
            )
            for position, term in enumerate(shape.terms)
        )
    )


def test_runtime_types_contain_only_required_model_fields() -> None:
    assert tuple(field.name for field in fields(Leaf)) == ()
    assert tuple(field.name for field in fields(Root)) == ("rank",)
    assert tuple(field.name for field in fields(Term)) == (
        "root",
        "exponent",
    )
    assert tuple(field.name for field in fields(Container)) == (
        "terms",
    )


@pytest.mark.parametrize("shape", canonical_shapes(max_depth=2))
def test_generated_canonical_shapes_validate(
    shape: Leaf | Container,
) -> None:
    assert validate_shape(shape) is None


@pytest.mark.parametrize("shape", canonical_shapes(max_depth=2))
def test_recursive_rank_normalization_restores_generated_shape(
    shape: Leaf | Container,
) -> None:
    shifted = shift_ranks_recursively(shape)
    normalized = normalize_shape(shifted)

    assert normalized == shape
    assert validate_shape(normalized) is None


@pytest.mark.parametrize("shape", canonical_shapes(max_depth=2))
def test_normalization_is_idempotent_across_generated_domain(
    shape: Leaf | Container,
) -> None:
    first = normalize_shape(shape)
    second = normalize_shape(first)

    assert first == shape
    assert second == first


@pytest.mark.parametrize("shape", canonical_shapes(max_depth=2))
def test_canonical_data_is_stable_across_generated_domain(
    shape: Leaf | Container,
) -> None:
    first = to_canonical_data(shape)
    second = to_canonical_data(shape)

    assert first == second


def test_different_recursive_nesting_is_not_equal() -> None:
    shallow = Container(
        terms=(
            Term(root=Root(0), exponent=Leaf()),
            Term(root=Root(1), exponent=Leaf()),
        )
    )
    nested = Container(
        terms=(
            Term(
                root=Root(0),
                exponent=Container(
                    terms=(
                        Term(root=Root(0), exponent=Leaf()),
                    )
                ),
            ),
        )
    )

    assert validate_shape(shallow) is None
    assert validate_shape(nested) is None
    assert shallow != nested
