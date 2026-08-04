from __future__ import annotations

from dataclasses import FrozenInstanceError, fields

import pytest

from petra.vision import (
    OrderedGroup,
    Terminal,
    validate_vision_shape,
)


def test_terminal_is_the_unique_kernel_terminal_value() -> None:
    first = Terminal()
    second = Terminal()

    assert first == second
    assert first is not second
    assert first != OrderedGroup(children=(Terminal(),))


def test_terminal_is_immutable_and_has_no_fields() -> None:
    terminal = Terminal()

    assert tuple(field.name for field in fields(Terminal)) == ()

    with pytest.raises(FrozenInstanceError):
        terminal.payload = "hidden"  # type: ignore[attr-defined]


def test_ordered_group_requires_a_non_empty_child_tuple() -> None:
    first = Terminal()
    second = OrderedGroup(children=(Terminal(),))
    group = OrderedGroup(children=(first, second))

    assert group.children == (first, second)
    assert isinstance(group.children, tuple)

    with pytest.raises(ValueError, match="non-empty"):
        OrderedGroup(children=())

    with pytest.raises(TypeError, match="must be a tuple"):
        OrderedGroup(  # type: ignore[arg-type]
            children=[Terminal()]
        )


@pytest.mark.parametrize(
    "children",
    [
        (object(),),
        (Terminal(), object()),
        (None,),
    ],
)
def test_ordered_group_rejects_non_kernel_children(
    children: tuple[object, ...],
) -> None:
    with pytest.raises(TypeError, match="Terminal or OrderedGroup"):
        OrderedGroup(  # type: ignore[arg-type]
            children=children
        )


def test_ordered_group_is_deeply_immutable() -> None:
    group = OrderedGroup(children=(Terminal(),))

    with pytest.raises(FrozenInstanceError):
        group.children = ()  # type: ignore[misc]

    with pytest.raises(TypeError):
        group.children[0] = Terminal()  # type: ignore[index]


def test_child_order_is_structurally_significant() -> None:
    terminal = Terminal()
    nested = OrderedGroup(children=(Terminal(),))

    left = OrderedGroup(children=(terminal, nested))
    right = OrderedGroup(children=(nested, terminal))

    assert left != right
    assert len({left, right}) == 2

    mapping = {
        left: "left",
        right: "right",
    }

    assert mapping[left] == "left"
    assert mapping[right] == "right"


def test_validation_accepts_recursive_kernel_shapes() -> None:
    shape = OrderedGroup(
        children=(
            Terminal(),
            OrderedGroup(children=(Terminal(),)),
        )
    )

    assert validate_vision_shape(shape) is None


@pytest.mark.parametrize(
    "malformed",
    [
        None,
        1,
        (),
        object(),
    ],
)
def test_validation_rejects_non_kernel_values(
    malformed: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="expected a VISION Terminal or OrderedGroup",
    ):
        validate_vision_shape(  # type: ignore[arg-type]
            malformed
        )


def test_validation_rejects_a_manually_injected_cycle() -> None:
    cyclic = OrderedGroup(children=(Terminal(),))

    object.__setattr__(
        cyclic,
        "children",
        (cyclic,),
    )

    with pytest.raises(ValueError, match="must be acyclic"):
        validate_vision_shape(cyclic)


def test_validation_rechecks_a_manually_corrupted_child_container() -> None:
    corrupted = OrderedGroup(children=(Terminal(),))

    object.__setattr__(
        corrupted,
        "children",
        [Terminal()],
    )

    with pytest.raises(TypeError, match="must be a tuple"):
        validate_vision_shape(corrupted)


def test_kernel_runtime_types_contain_only_contract_fields() -> None:
    assert tuple(field.name for field in fields(Terminal)) == ()
    assert tuple(field.name for field in fields(OrderedGroup)) == (
        "children",
    )
