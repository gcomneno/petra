"""Contract tests for the Resolver."""

from __future__ import annotations

import json

import pytest
from petra import DefaultTarget, ExplicitTarget, parse_shape

from resolver import (
    PrimeKey,
    ProjectionError,
    ResolverError,
    project,
    resolve,
)
from resolver.cli import main as cli_main

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def tower_shape(depth: int) -> str:
    """Return the canonical text of a pure tower of the given depth."""

    text = "1"
    for _ in range(depth):
        text = f"C(r0^{text})"
    return text


def tower_key(depth: int) -> PrimeKey:
    """Return a PrimeKey assigning prime 2 to every level of a tower."""

    assignments: dict[tuple[int, ...], int] = {}
    address: tuple[int, ...] = ()
    for _ in range(depth):
        address = (*address, 0)
        assignments[address] = 2
    return PrimeKey(assignments)


def wide_shape(width: int) -> str:
    """Return the canonical text of a flat container of the given width."""

    terms = ",".join(f"r{i}^1" for i in range(width))
    return f"C({terms})"


# ---------------------------------------------------------------------------
# Minimal paths
# ---------------------------------------------------------------------------


def test_identity_returns_empty_path() -> None:
    path = resolve("C(r0^1)", "C(r0^1)")

    assert path.length == 0
    assert path.steps == ()
    assert path.source == parse_shape("C(r0^1)")
    assert path.target == parse_shape("C(r0^1)")


def test_single_sprout() -> None:
    path = resolve("C(r0^1)", "C(r0^1,r1^1)")

    assert path.length == 1
    assert path.steps[0].operator.value == "SPROUT"
    assert path.steps[0].after_shape == parse_shape("C(r0^1,r1^1)")


def test_leaf_to_singleton_container() -> None:
    path = resolve("1", "C(r0^1)")

    assert path.length == 1
    assert path.steps[0].operator.value == "SPROUT"


def test_leaf_to_two_level_tower() -> None:
    path = resolve("1", "C(r0^C(r0^1))")

    assert path.length == 2
    assert path.steps[0].operator.value == "SPROUT"
    assert path.steps[1].operator.value == "GRAFT"


def test_wide_target_uses_sprout() -> None:
    path = resolve("1", wide_shape(4))

    assert path.length == 4
    assert all(step.operator.value == "SPROUT" for step in path.steps)


def test_tower_target_uses_graft() -> None:
    path = resolve("1", tower_shape(4))

    assert path.length == 4
    assert path.steps[0].operator.value == "SPROUT"
    assert all(step.operator.value == "GRAFT" for step in path.steps[1:])


@pytest.mark.parametrize("depth", [1, 2, 3, 5, 8])
def test_tower_path_length_matches_depth(depth: int) -> None:
    path = resolve(
        "1",
        tower_shape(depth),
        max_depth=depth + 4,
        max_nodes=2 * depth + 10,
    )

    assert path.length == depth


@pytest.mark.parametrize("width", [1, 2, 3, 5, 8])
def test_wide_path_length_matches_width(width: int) -> None:
    path = resolve(
        "1",
        wide_shape(width),
        max_depth=width + 4,
        max_nodes=2 * width + 10,
    )

    assert path.length == width


# ---------------------------------------------------------------------------
# Step structure
# ---------------------------------------------------------------------------


def test_first_step_target_is_default() -> None:
    path = resolve("C(r0^1)", "C(r0^1,r1^1)")
    step = path.steps[0]

    assert isinstance(step.invocation_target, DefaultTarget)
    assert step.before_shape == parse_shape("C(r0^1)")
    assert step.after_shape == parse_shape("C(r0^1,r1^1)")


def test_path_is_connected() -> None:
    path = resolve("1", tower_shape(4), max_depth=8, max_nodes=20)

    assert path.steps[0].before_shape == path.source
    for previous, current in zip(path.steps, path.steps[1:], strict=False):
        assert previous.after_shape == current.before_shape
    assert path.steps[-1].after_shape == path.target


def test_explicit_target_used_when_default_would_miss() -> None:
    # The default GRAFT targets the deepest latent slot, which here is
    # @/1/0/^, but the target requires @/0/^.
    path = resolve(
        "C(r0^1,r1^C(r0^1))",
        "C(r0^C(r0^1),r1^C(r0^1))",
    )

    assert path.length == 1
    step = path.steps[0]
    assert step.operator.value == "GRAFT"
    assert isinstance(step.invocation_target, ExplicitTarget)
    assert str(step.invocation_target.address) == "@/0/^"


# ---------------------------------------------------------------------------
# Heuristic signature
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("depth", [3, 5, 8])
def test_explored_equals_length_plus_one_on_towers(depth: int) -> None:
    path = resolve(
        "1",
        tower_shape(depth),
        max_depth=depth + 4,
        max_nodes=2 * depth + 10,
    )

    assert path.explored == path.length + 1


@pytest.mark.parametrize("width", [3, 5, 8])
def test_explored_equals_length_plus_one_on_wide_shapes(width: int) -> None:
    path = resolve(
        "1",
        wide_shape(width),
        max_depth=width + 4,
        max_nodes=2 * width + 10,
    )

    assert path.explored == path.length + 1


# ---------------------------------------------------------------------------
# Bounds and failures
# ---------------------------------------------------------------------------


def test_max_depth_insufficient_raises() -> None:
    with pytest.raises(ResolverError):
        resolve("1", wide_shape(5), max_depth=3)


def test_max_nodes_insufficient_raises() -> None:
    with pytest.raises(ResolverError):
        resolve("1", wide_shape(20), max_nodes=5)


def test_max_visited_bound_raises() -> None:
    with pytest.raises(ResolverError):
        resolve(
            "1",
            tower_shape(8),
            max_depth=10,
            max_nodes=20,
            max_visited=2,
        )


@pytest.mark.parametrize("value", [-1, -10])
def test_negative_max_depth_is_rejected(value: int) -> None:
    with pytest.raises(ResolverError):
        resolve("1", "C(r0^1)", max_depth=value)


@pytest.mark.parametrize("value", [0, -1])
def test_invalid_max_nodes_is_rejected(value: int) -> None:
    with pytest.raises(ResolverError):
        resolve("1", "C(r0^1)", max_nodes=value)


def test_malformed_source_shape_raises() -> None:
    from petra import ShapeSyntaxError

    with pytest.raises(ShapeSyntaxError):
        resolve("not a shape", "1")


def test_malformed_target_shape_raises() -> None:
    from petra import ShapeSyntaxError

    with pytest.raises(ShapeSyntaxError):
        resolve("1", "C(r0^)")


# ---------------------------------------------------------------------------
# Projection layer
# ---------------------------------------------------------------------------


def test_project_wide_shape() -> None:
    shape = parse_shape("C(r0^1,r1^1)")
    key = PrimeKey({(0,): 2, (1,): 3})

    assert project(shape, key) == 6


def test_project_nested_exponent() -> None:
    # 2^2 * 3^5 = 4 * 243 = 972
    shape = parse_shape("C(r0^C(r0^1),r1^C(r0^1))")
    key = PrimeKey(
        {
            (0,): 2,
            (0, 0): 2,
            (1,): 3,
            (1, 0): 5,
        }
    )

    assert project(shape, key) == 972


def test_project_primorial() -> None:
    shape = parse_shape("C(r0^1,r1^1,r2^1,r3^1,r4^1,r5^1)")
    key = PrimeKey(
        {
            (0,): 2,
            (1,): 3,
            (2,): 5,
            (3,): 7,
            (4,): 11,
            (5,): 13,
        }
    )

    assert project(shape, key) == 30030


def test_project_missing_assignment_raises() -> None:
    shape = parse_shape("C(r0^1,r1^1)")
    key = PrimeKey({(0,): 2})

    with pytest.raises(ProjectionError):
        project(shape, key)


@pytest.mark.parametrize(
    ("assignments", "exception"),
    [
        ({(0,): 1}, ValueError),         # prime must be >= 2
        ({(0,): 0}, ValueError),
        ({(0,): -3}, ValueError),
        ({(0,): 2.5}, TypeError),        # must be int
        ({("a",): 2}, TypeError),        # address must be tuple of ints
        ({(-1,): 2}, ValueError),        # indices must be >= 0
    ],
)
def test_prime_key_rejects_invalid_assignments(
    assignments: dict, exception: type[Exception]
) -> None:
    with pytest.raises(exception):
        PrimeKey(assignments)


def test_resolve_with_key_attaches_values() -> None:
    key = PrimeKey({(0,): 2, (0, 0): 3})
    path = resolve("C(r0^1)", "C(r0^C(r0^1))", key=key)

    assert path.value_source == 2
    assert path.value_target == 8
    assert path.steps[0].value_before == 2
    assert path.steps[0].value_after == 8


def test_resolve_with_partial_key_yields_none() -> None:
    key = PrimeKey({(0,): 2})
    path = resolve("C(r0^1)", "C(r0^C(r0^1))", key=key)

    assert path.value_source == 2
    assert path.value_target is None
    assert path.steps[0].value_before == 2
    assert path.steps[0].value_after is None


def test_resolve_without_key_yields_none() -> None:
    path = resolve("C(r0^1)", "C(r0^1,r1^1)")

    assert path.value_source is None
    assert path.value_target is None
    assert path.steps[0].value_before is None
    assert path.steps[0].value_after is None


def test_projection_limit_yields_none_on_huge_tower() -> None:
    # A tower of depth 6 produces 2^(2^(2^(2^(2^2)))) which exceeds
    # the projection bit bound.
    path = resolve(
        "1",
        tower_shape(6),
        key=tower_key(6),
        max_depth=10,
        max_nodes=20,
    )

    assert path.length == 6
    assert path.value_source == 1
    assert path.value_target is None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_human_output(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli_main(["C(r0^1)", "C(r0^1,r1^1)"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "length = 1" in captured.out
    assert "SPROUT" in captured.out


def test_cli_json_output(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli_main(["C(r0^1)", "C(r0^1,r1^1)", "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)

    assert exit_code == 0
    assert data["schema"] == "resolver.path.v1"
    assert data["length"] == 1
    assert data["steps"][0]["operator"] == "SPROUT"


def test_cli_with_key_attaches_values(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli_main(
        [
            "C(r0^1)",
            "C(r0^C(r0^1))",
            "--key-json",
            '{"@/0":2,"@/0/0":3}',
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "[2 -> 8]" in captured.out


def test_cli_error_on_malformed_shape(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli_main(["garbage", "1"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "shape-text-malformed" in captured.err


def test_cli_error_on_unreachable_target(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli_main(
        ["1", wide_shape(5), "--max-depth", "2"]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "no path found" in captured.err


def test_cli_error_on_invalid_key_json(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli_main(
        [
            "C(r0^1)",
            "C(r0^1,r1^1)",
            "--key-json",
            "not json",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "not valid JSON" in captured.err
