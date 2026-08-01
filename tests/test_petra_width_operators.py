"""Contract tests for PETRA SPROUT and SHED width rewrites."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from petra import (
    Address,
    Container,
    DefaultTarget,
    ExplicitTarget,
    FailedResult,
    Leaf,
    Operator,
    ResolvedAnchor,
    ResolvedSlot,
    ResolvedTerm,
    Root,
    SuccessfulResult,
    Term,
    apply_shed,
    apply_sprout,
    resolve_address,
    to_canonical_data,
    validate_shape,
)


Shape = Leaf | Container
Target = DefaultTarget | ExplicitTarget
WidthOperator = Callable[[Shape, Target], SuccessfulResult | FailedResult]


def term(rank: int, exponent: Shape) -> Term:
    return Term(
        root=Root(rank),
        exponent=exponent,
    )


def container(*exponents: Shape) -> Container:
    return Container(
        terms=tuple(
            term(rank, exponent)
            for rank, exponent in enumerate(exponents)
        )
    )


def assert_success(
    result: SuccessfulResult | FailedResult,
    *,
    operator: Operator,
    before_shape: Shape,
    invocation_target: Target,
    target_address: Address,
    witness_address: Address,
    expected_after: Shape,
) -> SuccessfulResult:
    assert isinstance(result, SuccessfulResult)
    assert result.schema == "petra.operator-result.v1"
    assert result.status == "ok"
    assert result.operator is operator
    assert result.reason == f"{operator.value.lower()}-applied"

    assert result.invocation_target is invocation_target
    assert result.before_shape is before_shape
    assert result.after_shape == expected_after

    assert result.address_effects.target_address == target_address
    assert result.address_effects.witness_address == witness_address

    assert result.resolved_target == resolve_address(
        before_shape,
        target_address,
    )

    validate_shape(result.after_shape)
    resolve_address(
        result.after_shape,
        witness_address,
    )

    return result


def assert_failure(
    result: SuccessfulResult | FailedResult,
    *,
    operator: Operator,
    before_shape: Shape,
    invocation_target: Target,
    reason: str,
) -> FailedResult:
    assert isinstance(result, FailedResult)
    assert result.schema == "petra.operator-result.v1"
    assert result.status == "failed"
    assert result.operator is operator
    assert result.invocation_target is invocation_target
    assert result.before_shape is before_shape
    assert result.reason == reason

    for success_only_field in (
        "after_shape",
        "resolved_target",
        "address_effects",
    ):
        assert not hasattr(result, success_only_field)

    return result


def test_width_operator_functions_are_public() -> None:
    assert callable(apply_sprout)
    assert callable(apply_shed)


@pytest.mark.parametrize(
    "invocation_target",
    [
        DefaultTarget(),
        ExplicitTarget(address=Address()),
    ],
)
def test_sprout_materializes_root_leaf(
    invocation_target: Target,
) -> None:
    before = Leaf()
    snapshot = to_canonical_data(before)

    result = apply_sprout(
        before,
        invocation_target,
    )

    success = assert_success(
        result,
        operator=Operator.SPROUT,
        before_shape=before,
        invocation_target=invocation_target,
        target_address=Address(),
        witness_address=Address(indices=(0,)),
        expected_after=container(Leaf()),
    )

    assert isinstance(success.resolved_target, ResolvedAnchor)
    assert to_canonical_data(before) == snapshot


@pytest.mark.parametrize(
    "invocation_target",
    [
        DefaultTarget(),
        ExplicitTarget(address=Address()),
    ],
)
def test_sprout_appends_to_root_container(
    invocation_target: Target,
) -> None:
    nested = container(Leaf())
    before = container(
        nested,
        Leaf(),
    )
    snapshot = to_canonical_data(before)

    result = apply_sprout(
        before,
        invocation_target,
    )

    success = assert_success(
        result,
        operator=Operator.SPROUT,
        before_shape=before,
        invocation_target=invocation_target,
        target_address=Address(),
        witness_address=Address(indices=(2,)),
        expected_after=container(
            nested,
            Leaf(),
            Leaf(),
        ),
    )

    assert isinstance(success.resolved_target, ResolvedAnchor)
    assert success.after_shape.terms[0].exponent is nested
    assert to_canonical_data(before) == snapshot


def test_sprout_appends_to_explicit_nested_container() -> None:
    inner = container(Leaf())
    before = container(
        inner,
        Leaf(),
    )
    invocation_target = ExplicitTarget(
        address=Address(indices=(0,)),
    )

    result = apply_sprout(
        before,
        invocation_target,
    )

    success = assert_success(
        result,
        operator=Operator.SPROUT,
        before_shape=before,
        invocation_target=invocation_target,
        target_address=Address(indices=(0,)),
        witness_address=Address(indices=(0, 1)),
        expected_after=container(
            container(
                Leaf(),
                Leaf(),
            ),
            Leaf(),
        ),
    )

    assert isinstance(success.resolved_target, ResolvedTerm)


@pytest.mark.parametrize(
    "address",
    [
        Address(indices=(1,)),
        Address(indices=(0,), is_slot=True),
    ],
)
def test_sprout_rejects_leaf_terms_and_slots(
    address: Address,
) -> None:
    before = container(
        container(Leaf()),
        Leaf(),
    )
    invocation_target = ExplicitTarget(address=address)

    result = apply_sprout(
        before,
        invocation_target,
    )

    assert_failure(
        result,
        operator=Operator.SPROUT,
        before_shape=before,
        invocation_target=invocation_target,
        reason="sprout-target-not-container",
    )


@pytest.mark.parametrize(
    ("address", "reason"),
    [
        (
            Address(indices=(9,)),
            "address-out-of-range",
        ),
        (
            Address(indices=(1, 0)),
            "address-crosses-leaf",
        ),
    ],
)
def test_sprout_preserves_explicit_traversal_failures(
    address: Address,
    reason: str,
) -> None:
    before = container(
        container(Leaf()),
        Leaf(),
    )
    invocation_target = ExplicitTarget(address=address)

    result = apply_sprout(
        before,
        invocation_target,
    )

    assert_failure(
        result,
        operator=Operator.SPROUT,
        before_shape=before,
        invocation_target=invocation_target,
        reason=reason,
    )


def test_shed_default_selects_last_direct_top_level_leaf() -> None:
    first_nested = container(Leaf())
    second_nested = container(Leaf())
    before = container(
        Leaf(),
        first_nested,
        Leaf(),
        second_nested,
    )
    invocation_target = DefaultTarget()
    snapshot = to_canonical_data(before)

    result = apply_shed(
        before,
        invocation_target,
    )

    success = assert_success(
        result,
        operator=Operator.SHED,
        before_shape=before,
        invocation_target=invocation_target,
        target_address=Address(indices=(2,)),
        witness_address=Address(),
        expected_after=container(
            Leaf(),
            first_nested,
            second_nested,
        ),
    )

    assert isinstance(success.resolved_target, ResolvedTerm)
    assert success.after_shape.terms[1].exponent is first_nested
    assert success.after_shape.terms[2].exponent is second_nested
    assert to_canonical_data(before) == snapshot


@pytest.mark.parametrize(
    "before",
    [
        Leaf(),
        container(
            container(Leaf()),
            container(Leaf()),
        ),
    ],
)
def test_shed_default_reports_no_eligible_top_level_leaf(
    before: Shape,
) -> None:
    invocation_target = DefaultTarget()

    result = apply_shed(
        before,
        invocation_target,
    )

    assert_failure(
        result,
        operator=Operator.SHED,
        before_shape=before,
        invocation_target=invocation_target,
        reason="shed-no-eligible-top-level-leaf",
    )


@pytest.mark.parametrize(
    "removed_index",
    [0, 1, 2],
)
def test_shed_closes_root_sibling_ranks(
    removed_index: int,
) -> None:
    before = container(
        Leaf(),
        Leaf(),
        Leaf(),
    )
    invocation_target = ExplicitTarget(
        address=Address(indices=(removed_index,)),
    )

    result = apply_shed(
        before,
        invocation_target,
    )

    success = assert_success(
        result,
        operator=Operator.SHED,
        before_shape=before,
        invocation_target=invocation_target,
        target_address=Address(indices=(removed_index,)),
        witness_address=Address(),
        expected_after=container(
            Leaf(),
            Leaf(),
        ),
    )

    assert [
        current.root.rank
        for current in success.after_shape.terms
    ] == [0, 1]


@pytest.mark.parametrize(
    "invocation_target",
    [
        DefaultTarget(),
        ExplicitTarget(
            address=Address(indices=(0,)),
        ),
    ],
)
def test_shed_collapses_singleton_root_container(
    invocation_target: Target,
) -> None:
    before = container(Leaf())

    result = apply_shed(
        before,
        invocation_target,
    )

    assert_success(
        result,
        operator=Operator.SHED,
        before_shape=before,
        invocation_target=invocation_target,
        target_address=Address(indices=(0,)),
        witness_address=Address(),
        expected_after=Leaf(),
    )


def test_shed_nested_parent_survives_with_owner_term_witness() -> None:
    before = container(
        container(
            Leaf(),
            Leaf(),
        ),
        Leaf(),
    )
    invocation_target = ExplicitTarget(
        address=Address(indices=(0, 0)),
    )

    result = apply_shed(
        before,
        invocation_target,
    )

    success = assert_success(
        result,
        operator=Operator.SHED,
        before_shape=before,
        invocation_target=invocation_target,
        target_address=Address(indices=(0, 0)),
        witness_address=Address(indices=(0,)),
        expected_after=container(
            container(Leaf()),
            Leaf(),
        ),
    )

    assert isinstance(
        resolve_address(
            success.after_shape,
            success.address_effects.witness_address,
        ),
        ResolvedTerm,
    )


def test_shed_nested_parent_collapse_returns_latent_slot() -> None:
    before = container(
        container(Leaf()),
        Leaf(),
    )
    invocation_target = ExplicitTarget(
        address=Address(indices=(0, 0)),
    )

    result = apply_shed(
        before,
        invocation_target,
    )

    success = assert_success(
        result,
        operator=Operator.SHED,
        before_shape=before,
        invocation_target=invocation_target,
        target_address=Address(indices=(0, 0)),
        witness_address=Address(
            indices=(0,),
            is_slot=True,
        ),
        expected_after=container(
            Leaf(),
            Leaf(),
        ),
    )

    resolved_witness = resolve_address(
        success.after_shape,
        success.address_effects.witness_address,
    )

    assert isinstance(resolved_witness, ResolvedSlot)
    assert isinstance(resolved_witness.target, Leaf)


@pytest.mark.parametrize(
    "address",
    [
        Address(),
        Address(indices=(0,), is_slot=True),
        Address(indices=(0,)),
    ],
)
def test_shed_rejects_non_leaf_explicit_targets(
    address: Address,
) -> None:
    before = container(
        container(Leaf()),
        Leaf(),
    )
    invocation_target = ExplicitTarget(address=address)

    result = apply_shed(
        before,
        invocation_target,
    )

    assert_failure(
        result,
        operator=Operator.SHED,
        before_shape=before,
        invocation_target=invocation_target,
        reason="shed-target-not-leaf",
    )


@pytest.mark.parametrize(
    ("address", "reason"),
    [
        (
            Address(indices=(9,)),
            "address-out-of-range",
        ),
        (
            Address(indices=(1, 0)),
            "address-crosses-leaf",
        ),
    ],
)
def test_shed_preserves_explicit_traversal_failures(
    address: Address,
    reason: str,
) -> None:
    before = container(
        container(Leaf()),
        Leaf(),
    )
    invocation_target = ExplicitTarget(address=address)

    result = apply_shed(
        before,
        invocation_target,
    )

    assert_failure(
        result,
        operator=Operator.SHED,
        before_shape=before,
        invocation_target=invocation_target,
        reason=reason,
    )


@pytest.mark.parametrize(
    "operator",
    [
        apply_sprout,
        apply_shed,
    ],
)
@pytest.mark.parametrize(
    "invalid_target",
    [
        None,
        Address(),
        "default",
        object(),
    ],
)
def test_width_operators_reject_non_normalized_targets(
    operator: WidthOperator,
    invalid_target: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="invocation_target",
    ):
        operator(
            container(Leaf()),
            invalid_target,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "operator",
    [
        apply_sprout,
        apply_shed,
    ],
)
def test_width_operators_validate_shape_before_selection(
    operator: WidthOperator,
) -> None:
    non_canonical = Container(
        terms=(
            term(1, Leaf()),
        )
    )

    with pytest.raises(
        ValueError,
        match="non-canonical root rank",
    ):
        operator(
            non_canonical,
            DefaultTarget(),
        )


@pytest.mark.parametrize(
    "operator",
    [
        apply_sprout,
        apply_shed,
    ],
)
def test_width_operators_reject_non_shape_objects(
    operator: WidthOperator,
) -> None:
    with pytest.raises(
        TypeError,
        match="PETRA",
    ):
        operator(
            object(),  # type: ignore[arg-type]
            DefaultTarget(),
        )


@pytest.mark.parametrize(
    (
        "before",
        "sprout_target",
    ),
    [
        (
            container(
                Leaf(),
                container(Leaf()),
            ),
            DefaultTarget(),
        ),
        (
            container(
                container(Leaf()),
                Leaf(),
            ),
            ExplicitTarget(
                address=Address(indices=(0,)),
            ),
        ),
    ],
)
def test_explicit_shed_of_sprout_witness_restores_shape(
    before: Container,
    sprout_target: Target,
) -> None:
    sprout_result = apply_sprout(
        before,
        sprout_target,
    )

    assert isinstance(
        sprout_result,
        SuccessfulResult,
    )

    shed_target = ExplicitTarget(
        address=sprout_result.address_effects.witness_address,
    )

    shed_result = apply_shed(
        sprout_result.after_shape,
        shed_target,
    )

    assert isinstance(
        shed_result,
        SuccessfulResult,
    )
    assert shed_result.after_shape == before


def test_root_leaf_sprout_then_shed_restores_leaf() -> None:
    before = Leaf()

    sprout_result = apply_sprout(
        before,
        DefaultTarget(),
    )

    assert isinstance(
        sprout_result,
        SuccessfulResult,
    )

    shed_result = apply_shed(
        sprout_result.after_shape,
        ExplicitTarget(
            address=sprout_result.address_effects.witness_address,
        ),
    )

    assert isinstance(
        shed_result,
        SuccessfulResult,
    )
    assert shed_result.after_shape == before


def test_nested_shed_collapse_witness_is_not_a_sprout_target() -> None:
    before = container(
        container(Leaf()),
        Leaf(),
    )

    shed_result = apply_shed(
        before,
        ExplicitTarget(
            address=Address(indices=(0, 0)),
        ),
    )

    assert isinstance(
        shed_result,
        SuccessfulResult,
    )

    witness = shed_result.address_effects.witness_address

    assert witness == Address(
        indices=(0,),
        is_slot=True,
    )
    assert isinstance(
        resolve_address(
            shed_result.after_shape,
            witness,
        ),
        ResolvedSlot,
    )

    sprout_result = apply_sprout(
        shed_result.after_shape,
        ExplicitTarget(address=witness),
    )

    assert isinstance(
        sprout_result,
        FailedResult,
    )
    assert sprout_result.reason == "sprout-target-not-container"
    assert sprout_result.before_shape is shed_result.after_shape
