from __future__ import annotations

from dataclasses import FrozenInstanceError, fields

import pytest

from petra.vision import (
    OrderedGroup,
    Terminal,
    VISION_SHAPE_OUT_OF_BOUNDS,
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


def test_ordered_group_snapshots_a_tuple_subclass_at_its_boundary() -> None:
    class MutableTuple(tuple):
        changed = False

        def __iter__(self):
            if type(self).changed:
                return iter((object(),))
            return tuple.__iter__(self)

    source = MutableTuple((Terminal(),))
    group = OrderedGroup(children=source)
    MutableTuple.changed = True

    assert type(group.children) is tuple
    assert group.children == (Terminal(),)
    assert validate_vision_shape(group) is None


def test_validation_rejects_width_four_with_the_stable_bounds_error() -> None:
    wide = OrderedGroup(
        children=(Terminal(), Terminal(), Terminal())
    )
    object.__setattr__(
        wide,
        "children",
        (*wide.children, Terminal()),
    )

    with pytest.raises(ValueError, match=VISION_SHAPE_OUT_OF_BOUNDS):
        validate_vision_shape(wide)


def test_validation_gives_bounds_first_precedence_to_malformed_width_four() -> None:
    corrupted = OrderedGroup(children=(Terminal(),))
    object.__setattr__(
        corrupted,
        "children",
        (object(), Terminal(), Terminal(), Terminal()),
    )

    with pytest.raises(ValueError, match=VISION_SHAPE_OUT_OF_BOUNDS):
        validate_vision_shape(corrupted)


def test_validation_rejects_depth_four_with_the_stable_bounds_error() -> None:
    deep: Terminal | OrderedGroup = Terminal()
    for _ in range(4):
        deep = OrderedGroup(children=(deep,))

    with pytest.raises(ValueError, match=VISION_SHAPE_OUT_OF_BOUNDS):
        validate_vision_shape(deep)


def test_validation_rejects_eight_structural_node_occurrences() -> None:
    eight_nodes = OrderedGroup(
        children=(
            OrderedGroup(
                children=(Terminal(), Terminal(), Terminal())
            ),
            OrderedGroup(children=(Terminal(), Terminal())),
        )
    )

    with pytest.raises(ValueError, match=VISION_SHAPE_OUT_OF_BOUNDS):
        validate_vision_shape(eight_nodes)


def test_shared_acyclic_children_count_at_every_structural_position() -> None:
    shared = OrderedGroup(children=(Terminal(), Terminal()))
    eight_occurrences = OrderedGroup(
        children=(shared, shared, Terminal())
    )

    with pytest.raises(ValueError, match=VISION_SHAPE_OUT_OF_BOUNDS):
        validate_vision_shape(eight_occurrences)


def test_deep_hostile_chain_fails_bounded_validation_not_recursion() -> None:
    deep: Terminal | OrderedGroup = Terminal()
    for _ in range(1_100):
        deep = OrderedGroup(children=(deep,))

    with pytest.raises(ValueError, match=VISION_SHAPE_OUT_OF_BOUNDS):
        validate_vision_shape(deep)


def test_kernel_runtime_types_contain_only_contract_fields() -> None:
    assert tuple(field.name for field in fields(Terminal)) == ()
    assert tuple(field.name for field in fields(OrderedGroup)) == (
        "children",
    )
