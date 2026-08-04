"""Contract tests for canonical PETRA textual serialization."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from itertools import product

import pytest

from petra import (
    SHAPE_TEXT_MALFORMED,
    Address,
    Container,
    Leaf,
    Root,
    ShapeSyntaxError,
    Term,
    apply_graft,
    apply_prune,
    apply_shed,
    apply_sprout,
    parse_shape,
    resolve_address,
    serialize_shape,
)
from petra.results import (
    DefaultTarget,
    SuccessfulResult,
)
from petra.serialization import (
    _MAX_INPUT_TEXT_LENGTH,
    _MAX_NESTING_DEPTH,
    _MAX_ROOT_RANK_DIGITS,
    _MAX_TERMS_PER_CONTAINER,
    _MAX_TOTAL_NODES,
)


def nested_text(depth: int) -> str:
    return ("C(r0^" * depth) + "1" + (")" * depth)


def nested_shape(depth: int) -> Leaf | Container:
    shape: Leaf | Container = Leaf()
    for _ in range(depth):
        shape = container(shape)
    return shape


def node_budget_text(chain_depths: tuple[int, ...]) -> str:
    return "C(" + ",".join(
        f"r{rank}^{nested_text(depth)}"
        for rank, depth in enumerate(chain_depths)
    ) + ")"


def node_budget_shape(chain_depths: tuple[int, ...]) -> Container:
    return container(*(nested_shape(depth) for depth in chain_depths))


def container(
    *exponents: Leaf | Container,
) -> Container:
    return Container(
        terms=tuple(
            Term(
                root=Root(rank),
                exponent=exponent,
            )
            for rank, exponent in enumerate(exponents)
        )
    )


def canonical_shapes(
    max_depth: int,
) -> tuple[Leaf | Container, ...]:
    cache: dict[int, tuple[Leaf | Container, ...]] = {}

    def build(
        depth: int,
    ) -> tuple[Leaf | Container, ...]:
        if depth in cache:
            return cache[depth]

        shapes: list[Leaf | Container] = [Leaf()]

        if depth > 0:
            exponents = build(depth - 1)

            for width in (1, 2):
                for selected in product(
                    exponents,
                    repeat=width,
                ):
                    shapes.append(container(*selected))

        cache[depth] = tuple(shapes)
        return cache[depth]

    return build(max_depth)


@pytest.mark.parametrize(
    ("shape", "expected"),
    [
        (Leaf(), "1"),
        (container(Leaf()), "C(r0^1)"),
        (
            container(
                container(Leaf()),
                Leaf(),
            ),
            "C(r0^C(r0^1),r1^1)",
        ),
        (
            container(
                container(
                    container(Leaf()),
                ),
            ),
            "C(r0^C(r0^C(r0^1)))",
        ),
    ],
)
def test_serializer_emits_exact_canonical_text(
    shape: Leaf | Container,
    expected: str,
) -> None:
    assert serialize_shape(shape) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1", Leaf()),
        (" C ( r0 ^ 1 ) ", container(Leaf())),
        (
            "\nC(\tr0^C(r0^1),\r\nr1 ^ 1\f)\v",
            container(
                container(Leaf()),
                Leaf(),
            ),
        ),
    ],
)
def test_parser_accepts_ascii_whitespace_between_tokens(
    text: str,
    expected: Leaf | Container,
) -> None:
    parsed = parse_shape(text)

    assert parsed == expected
    assert serialize_shape(parsed) == serialize_shape(expected)


@pytest.mark.parametrize(
    "text",
    [
        "",
        " ",
        "2",
        "leaf",
        "c(r0^1)",
        "C",
        "C(",
        "C()",
        "C(r0)",
        "C(r0^)",
        "C(^1)",
        "C(r^1)",
        "C(r00^1)",
        "C(r01^1)",
        "C(r-1^1)",
        "C(r+1^1)",
        "C(r 0^1)",
        "C(r0^1,)",
        "C(,r0^1)",
        "C(r0^1 r1^1)",
        "C(r0^^1)",
        "C(r0^1))",
        "1 trailing",
        "C(r0^١)",
        "C(r０^1)",
        "C(r0^１)",
        "\u00a01\u00a0",
    ],
)
def test_malformed_text_uses_stable_reason(
    text: str,
) -> None:
    with pytest.raises(ShapeSyntaxError) as error:
        parse_shape(text)

    assert error.value.reason == SHAPE_TEXT_MALFORMED
    assert str(error.value) == SHAPE_TEXT_MALFORMED
    assert error.value.args == (SHAPE_TEXT_MALFORMED,)


@pytest.mark.parametrize(
    "value",
    [
        None,
        1,
        b"1",
        ["1"],
    ],
)
def test_non_text_input_is_malformed(
    value: object,
) -> None:
    with pytest.raises(ShapeSyntaxError) as error:
        parse_shape(value)

    assert error.value.reason == SHAPE_TEXT_MALFORMED


def test_oversized_rank_token_uses_stable_syntax_failure() -> None:
    text = f"C(r{'9' * 5000}^1)"

    with pytest.raises(ShapeSyntaxError) as error:
        parse_shape(text)

    assert error.value.reason == SHAPE_TEXT_MALFORMED


def test_parser_accepts_text_at_the_input_length_boundary() -> None:
    text = "1" + (" " * (_MAX_INPUT_TEXT_LENGTH - 1))

    assert parse_shape(text) == Leaf()


def test_parser_rejects_text_one_character_over_the_input_limit() -> None:
    text = "1" + (" " * _MAX_INPUT_TEXT_LENGTH)

    with pytest.raises(ShapeSyntaxError) as error:
        parse_shape(text)

    assert error.value.reason == SHAPE_TEXT_MALFORMED


def test_parser_accepts_depth_at_the_documented_boundary() -> None:
    text = nested_text(_MAX_NESTING_DEPTH)

    assert serialize_shape(parse_shape(text)) == text


def test_parser_rejects_depth_one_level_over_the_limit() -> None:
    with pytest.raises(ShapeSyntaxError) as error:
        parse_shape(nested_text(_MAX_NESTING_DEPTH + 1))

    assert error.value.reason == SHAPE_TEXT_MALFORMED


def test_parser_accepts_total_nodes_at_the_documented_boundary() -> None:
    # 1 root container + 4 root terms + 4 * (1,249 containers,
    # terms, and leaves) = 10,001 model nodes.
    text = node_budget_text((1249, 1249, 1249, 1249))
    assert _MAX_TOTAL_NODES == 10_001

    assert serialize_shape(parse_shape(text)) == text


def test_parser_rejects_total_nodes_over_the_limit() -> None:
    text = node_budget_text((1250, 1249, 1249, 1249))

    with pytest.raises(ShapeSyntaxError) as error:
        parse_shape(text)

    assert error.value.reason == SHAPE_TEXT_MALFORMED


def test_parser_accepts_container_width_at_the_documented_boundary() -> None:
    text = "C(" + ",".join(
        f"r{rank}^1" for rank in range(_MAX_TERMS_PER_CONTAINER)
    ) + ")"

    assert "r1023^1" in text
    assert serialize_shape(parse_shape(text)) == text


def test_parser_rejects_container_width_one_term_over_the_limit() -> None:
    text = "C(" + ",".join(
        f"r{rank}^1"
        for rank in range(_MAX_TERMS_PER_CONTAINER + 1)
    ) + ")"

    with pytest.raises(ShapeSyntaxError) as error:
        parse_shape(text)

    assert error.value.reason == SHAPE_TEXT_MALFORMED


def test_rank_token_limit_is_scanned_without_python_integer_conversion() -> None:
    largest_rank = "9" * _MAX_ROOT_RANK_DIGITS

    with pytest.raises(ValueError, match=f"got r{largest_rank}"):
        parse_shape(f"C(r{largest_rank}^1)")

    with pytest.raises(ShapeSyntaxError) as error:
        parse_shape(f"C(r{'9' * (_MAX_ROOT_RANK_DIGITS + 1)}^1)")

    assert error.value.reason == SHAPE_TEXT_MALFORMED


def test_deep_valid_round_trip_does_not_depend_on_python_recursion() -> None:
    depth = 1_200
    text = nested_text(depth)

    assert serialize_shape(parse_shape(text)) == text


def test_equally_deep_truncated_input_is_a_syntax_error() -> None:
    with pytest.raises(ShapeSyntaxError) as error:
        parse_shape(nested_text(1_200)[:-1])

    assert error.value.reason == SHAPE_TEXT_MALFORMED


def test_str_subclass_cannot_override_parser_grammar_recognition() -> None:
    class HostileStr(str):
        def startswith(self, *args: object, **kwargs: object) -> bool:
            return True

    assert parse_shape(HostileStr("C(r0^1)")) == container(Leaf())


def test_syntactic_shape_with_noncanonical_rank_is_not_repaired() -> None:
    with pytest.raises(
        ValueError,
        match="expected r0, got r1",
    ):
        parse_shape("C(r1^1)")


def test_nested_noncanonical_rank_is_not_repaired() -> None:
    with pytest.raises(
        ValueError,
        match="expected r0, got r4",
    ):
        parse_shape("C(r0^C(r4^1))")


def test_serializer_rejects_noncanonical_typed_shape() -> None:
    shape = Container(
        terms=(
            Term(
                root=Root(7),
                exponent=Leaf(),
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match="expected r0, got r7",
    ):
        serialize_shape(shape)


@pytest.mark.parametrize(
    "shape",
    [
        nested_shape(_MAX_NESTING_DEPTH + 1),
        container(
            *(Leaf() for _ in range(_MAX_TERMS_PER_CONTAINER + 1))
        ),
        node_budget_shape((1250, 1249, 1249, 1249)),
        Container(terms=(Term(root=Root(10_000), exponent=Leaf()),)),
    ],
)
def test_serializer_rejects_typed_shapes_over_resource_limits(
    shape: Leaf | Container,
) -> None:
    with pytest.raises(
        ValueError,
        match="^shape-serialization-limit-exceeded$",
    ):
        serialize_shape(shape)


def test_serializer_renders_deep_typed_shape_iteratively() -> None:
    depth = 1_200

    assert serialize_shape(nested_shape(depth)) == nested_text(depth)


@pytest.mark.parametrize(
    "value",
    [
        None,
        1,
        (),
    ],
)
def test_serializer_rejects_non_shape_values(
    value: object,
) -> None:
    with pytest.raises(TypeError):
        serialize_shape(value)


def test_serialization_does_not_mutate_input_shape() -> None:
    shape = container(
        container(Leaf()),
        Leaf(),
    )
    before_terms = shape.terms
    before_inner = shape.terms[0].exponent

    serialize_shape(shape)

    assert shape.terms is before_terms
    assert shape.terms[0].exponent is before_inner

    with pytest.raises(FrozenInstanceError):
        shape.terms = ()


def test_generated_shapes_round_trip_deterministically() -> None:
    for shape in canonical_shapes(max_depth=3):
        text = serialize_shape(shape)

        assert parse_shape(text) == shape
        assert serialize_shape(parse_shape(text)) == text


def test_structural_addresses_resolve_equivalently_after_round_trip() -> None:
    shape = container(
        container(
            Leaf(),
            container(Leaf()),
        ),
        Leaf(),
    )
    restored = parse_shape(serialize_shape(shape))

    addresses = (
        Address(),
        Address(indices=(0,)),
        Address(indices=(0,), is_slot=True),
        Address(indices=(0, 0)),
        Address(indices=(0, 0), is_slot=True),
        Address(indices=(0, 1)),
        Address(indices=(0, 1), is_slot=True),
        Address(indices=(0, 1, 0)),
        Address(indices=(1,)),
    )

    for address in addresses:
        assert (
            resolve_address(shape, address).kind
            == resolve_address(restored, address).kind
        )


@pytest.mark.parametrize(
    "apply_operator",
    [
        apply_sprout,
        apply_shed,
        apply_graft,
        apply_prune,
    ],
)
def test_operator_results_round_trip_through_shape_text(
    apply_operator,
) -> None:
    seed = container(
        container(Leaf()),
        Leaf(),
    )

    if apply_operator is apply_sprout:
        shape = seed
    elif apply_operator is apply_shed:
        shape = seed
    elif apply_operator is apply_graft:
        shape = container(Leaf())
    else:
        shape = container(container(Leaf()))

    result = apply_operator(
        shape,
        DefaultTarget(),
    )

    assert isinstance(result, SuccessfulResult)
    assert (
        parse_shape(serialize_shape(result.after_shape))
        == result.after_shape
    )
