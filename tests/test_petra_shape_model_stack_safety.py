from __future__ import annotations

import pytest

from petra import (
    Container,
    Leaf,
    Root,
    Term,
    normalize_shape,
    to_canonical_data,
    validate_shape,
)


def deep_unary_shape(
    depth: int,
    *,
    rank: int = 0,
    terminal_rank: int | None = None,
    terminal_width: int = 1,
) -> Container:
    shape: Leaf | Container = Leaf()

    for level in range(depth):
        current_rank = (
            terminal_rank
            if level == 0 and terminal_rank is not None
            else rank
        )
        if level == 0:
            shape = Container(
                terms=tuple(
                    Term(
                        root=Root(current_rank + offset),
                        exponent=Leaf(),
                    )
                    for offset in range(terminal_width)
                )
            )
        else:
            shape = Container(
                terms=(Term(root=Root(rank), exponent=shape),)
            )

    assert isinstance(shape, Container)
    return shape


@pytest.mark.parametrize("depth", [1_200, 2_048])
def test_validate_shape_is_stack_safe_at_supported_depth(depth: int) -> None:
    assert validate_shape(deep_unary_shape(depth)) is None


def test_validate_shape_reports_deep_noncanonical_rank_deterministically() -> None:
    malformed = deep_unary_shape(2_048, terminal_rank=7)

    with pytest.raises(
        ValueError,
        match=r"non-canonical root rank: expected r0, got r7",
    ):
        validate_shape(malformed)


def test_validate_shape_preserves_depth_first_first_error_contract() -> None:
    nested_bad = Container(
        terms=(Term(root=Root(9), exponent=Leaf()),)
    )
    shape = Container(
        terms=(
            Term(root=Root(0), exponent=nested_bad),
            Term(root=Root(8), exponent=Leaf()),
        )
    )

    with pytest.raises(
        ValueError,
        match=r"non-canonical root rank: expected r0, got r9",
    ):
        validate_shape(shape)


@pytest.mark.parametrize("depth", [1_200, 2_048])
def test_normalize_shape_is_stack_safe_and_idempotent(depth: int) -> None:
    original = deep_unary_shape(depth, rank=7)

    normalized = normalize_shape(original)

    assert validate_shape(normalized) is None
    assert normalize_shape(normalized) == normalized
    assert original.terms[0].root == Root(7)


def test_normalize_shape_preserves_sibling_order() -> None:
    left = Container(terms=(Term(root=Root(4), exponent=Leaf()),))
    right = Container(
        terms=(
            Term(root=Root(5), exponent=Leaf()),
            Term(root=Root(6), exponent=Leaf()),
        )
    )
    shape = Container(
        terms=(
            Term(root=Root(9), exponent=left),
            Term(root=Root(3), exponent=right),
        )
    )

    normalized = normalize_shape(shape)

    first = normalized.terms[0].exponent
    second = normalized.terms[1].exponent
    assert isinstance(first, Container)
    assert isinstance(second, Container)
    assert len(first.terms) == 1
    assert len(second.terms) == 2
    assert [term.root for term in normalized.terms] == [Root(0), Root(1)]


def test_normalize_shape_reuses_shared_immutable_subshapes() -> None:
    shared = Container(
        terms=(Term(root=Root(5), exponent=Leaf()),)
    )
    shape = Container(
        terms=(
            Term(root=Root(8), exponent=shared),
            Term(root=Root(3), exponent=shared),
        )
    )

    normalized = normalize_shape(shape)

    assert normalized.terms[0].exponent is normalized.terms[1].exponent


@pytest.mark.parametrize("depth", [1_200, 2_048])
def test_to_canonical_data_is_stack_safe_at_supported_depth(depth: int) -> None:
    data = to_canonical_data(deep_unary_shape(depth))

    assert data[0] == "container"


def test_canonical_data_matches_for_independently_allocated_deep_shapes() -> None:
    left = deep_unary_shape(2_048)
    right = deep_unary_shape(2_048)

    assert to_canonical_data(left) == to_canonical_data(right)


def test_stack_safe_utilities_retain_non_petra_input_errors() -> None:
    for operation in (validate_shape, normalize_shape, to_canonical_data):
        with pytest.raises(TypeError, match="expected a PETRA Leaf or Container"):
            operation(object())  # type: ignore[arg-type]
