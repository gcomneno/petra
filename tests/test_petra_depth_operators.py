"""Contract tests for PETRA GRAFT and PRUNE depth rewrites."""

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
    ResolvedSlot,
    ResolvedTerm,
    Root,
    SuccessfulResult,
    Term,
    apply_graft,
    apply_prune,
    resolve_address,
    to_canonical_data,
    validate_shape,
)


Shape = Leaf | Container
Target = DefaultTarget | ExplicitTarget
DepthOperator = Callable[
    [Shape, Target],
    SuccessfulResult | FailedResult,
]


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
    before_shape: Shape,
    invocation_target: Target,
    target_address: Address,
    witness_address: Address,
    expected_after: Shape,
) -> SuccessfulResult:
    assert isinstance(result, SuccessfulResult)
    assert result.schema == "petra.operator-result.v1"
    assert result.status == "ok"
    assert result.operator is Operator.GRAFT
    assert result.reason == "graft-applied"

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
    before_shape: Shape,
    invocation_target: Target,
    reason: str,
) -> FailedResult:
    assert isinstance(result, FailedResult)
    assert result.schema == "petra.operator-result.v1"
    assert result.status == "failed"
    assert result.operator is Operator.GRAFT
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


def test_graft_function_is_public() -> None:
    assert callable(apply_graft)


def test_graft_materializes_explicit_latent_slot() -> None:
    before = container(
        container(Leaf()),
        Leaf(),
    )
    invocation_target = ExplicitTarget(
        address=Address(
            indices=(0, 0),
            is_slot=True,
        )
    )
    snapshot = to_canonical_data(before)

    result = apply_graft(
        before,
        invocation_target,
    )

    success = assert_success(
        result,
        before_shape=before,
        invocation_target=invocation_target,
        target_address=Address(
            indices=(0, 0),
            is_slot=True,
        ),
        witness_address=Address(
            indices=(0, 0, 0),
        ),
        expected_after=container(
            container(
                container(Leaf()),
            ),
            Leaf(),
        ),
    )

    assert isinstance(success.resolved_target, ResolvedSlot)
    assert isinstance(success.resolved_target.target, Leaf)
    assert isinstance(
        resolve_address(
            success.after_shape,
            success.address_effects.witness_address,
        ),
        ResolvedTerm,
    )
    assert to_canonical_data(before) == snapshot


def test_graft_default_selects_deepest_last_latent_slot() -> None:
    before = container(
        container(
            Leaf(),
            container(Leaf()),
        ),
        container(
            Leaf(),
            container(Leaf()),
        ),
    )
    invocation_target = DefaultTarget()

    result = apply_graft(
        before,
        invocation_target,
    )

    assert_success(
        result,
        before_shape=before,
        invocation_target=invocation_target,
        target_address=Address(
            indices=(1, 1, 0),
            is_slot=True,
        ),
        witness_address=Address(
            indices=(1, 1, 0, 0),
        ),
        expected_after=container(
            container(
                Leaf(),
                container(Leaf()),
            ),
            container(
                Leaf(),
                container(
                    container(Leaf()),
                ),
            ),
        ),
    )


@pytest.mark.parametrize(
    "address",
    [
        Address(),
        Address(indices=(0,)),
    ],
)
def test_graft_rejects_non_slot_explicit_targets(
    address: Address,
) -> None:
    before = container(Leaf())
    invocation_target = ExplicitTarget(address=address)

    result = apply_graft(
        before,
        invocation_target,
    )

    assert_failure(
        result,
        before_shape=before,
        invocation_target=invocation_target,
        reason="graft-target-not-slot",
    )


def test_graft_rejects_materialized_slot() -> None:
    before = container(
        container(Leaf()),
    )
    invocation_target = ExplicitTarget(
        address=Address(
            indices=(0,),
            is_slot=True,
        )
    )

    result = apply_graft(
        before,
        invocation_target,
    )

    assert_failure(
        result,
        before_shape=before,
        invocation_target=invocation_target,
        reason="graft-slot-already-materialized",
    )


@pytest.mark.parametrize(
    ("address", "reason"),
    [
        (
            Address(
                indices=(9,),
                is_slot=True,
            ),
            "address-out-of-range",
        ),
        (
            Address(
                indices=(0, 0),
                is_slot=True,
            ),
            "address-crosses-leaf",
        ),
    ],
)
def test_graft_preserves_explicit_traversal_failures(
    address: Address,
    reason: str,
) -> None:
    before = container(Leaf())
    invocation_target = ExplicitTarget(address=address)

    result = apply_graft(
        before,
        invocation_target,
    )

    assert_failure(
        result,
        before_shape=before,
        invocation_target=invocation_target,
        reason=reason,
    )


def test_graft_default_reports_no_eligible_latent_slot() -> None:
    before = Leaf()
    invocation_target = DefaultTarget()

    result = apply_graft(
        before,
        invocation_target,
    )

    assert_failure(
        result,
        before_shape=before,
        invocation_target=invocation_target,
        reason="graft-no-eligible-latent-slot",
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
def test_graft_rejects_non_normalized_targets(
    invalid_target: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="invocation_target",
    ):
        apply_graft(
            container(Leaf()),
            invalid_target,  # type: ignore[arg-type]
        )


def test_prune_function_is_public() -> None:
    assert callable(apply_prune)


def test_prune_removes_explicit_terminal_leaf() -> None:
    before = container(
        container(
            container(Leaf()),
        ),
        Leaf(),
    )
    invocation_target = ExplicitTarget(
        address=Address(indices=(0, 0, 0))
    )
    snapshot = to_canonical_data(before)

    result = apply_prune(
        before,
        invocation_target,
    )

    assert isinstance(result, SuccessfulResult)
    assert result.operator is Operator.PRUNE
    assert result.reason == "prune-applied"
    assert result.invocation_target is invocation_target
    assert result.before_shape is before
    assert result.after_shape == container(
        container(Leaf()),
        Leaf(),
    )

    assert result.address_effects.target_address == Address(
        indices=(0, 0, 0)
    )
    assert result.address_effects.witness_address == Address(
        indices=(0, 0),
        is_slot=True,
    )

    assert isinstance(result.resolved_target, ResolvedTerm)
    assert isinstance(result.resolved_target.term.exponent, Leaf)

    resolved_witness = resolve_address(
        result.after_shape,
        result.address_effects.witness_address,
    )
    assert isinstance(resolved_witness, ResolvedSlot)
    assert isinstance(resolved_witness.target, Leaf)

    assert to_canonical_data(before) == snapshot


def test_prune_default_selects_deepest_last_terminal_leaf() -> None:
    before = container(
        container(
            container(Leaf()),
        ),
        container(
            container(Leaf()),
        ),
    )
    invocation_target = DefaultTarget()

    result = apply_prune(
        before,
        invocation_target,
    )

    assert isinstance(result, SuccessfulResult)
    assert result.operator is Operator.PRUNE
    assert result.address_effects.target_address == Address(
        indices=(1, 0, 0)
    )
    assert result.address_effects.witness_address == Address(
        indices=(1, 0),
        is_slot=True,
    )
    assert result.after_shape == container(
        container(
            container(Leaf()),
        ),
        container(Leaf()),
    )


@pytest.mark.parametrize(
    "address",
    [
        Address(),
        Address(
            indices=(0,),
            is_slot=True,
        ),
        Address(indices=(0,)),
    ],
)
def test_prune_rejects_non_terminal_leaf_targets(
    address: Address,
) -> None:
    before = container(
        container(Leaf()),
    )
    invocation_target = ExplicitTarget(address=address)

    result = apply_prune(
        before,
        invocation_target,
    )

    assert isinstance(result, FailedResult)
    assert result.operator is Operator.PRUNE
    assert result.before_shape is before
    assert result.invocation_target is invocation_target
    assert result.reason == "prune-target-not-terminal-leaf"


def test_prune_rejects_leaf_directly_in_root_container() -> None:
    before = container(Leaf())
    invocation_target = ExplicitTarget(
        address=Address(indices=(0,))
    )

    result = apply_prune(
        before,
        invocation_target,
    )

    assert isinstance(result, FailedResult)
    assert result.operator is Operator.PRUNE
    assert result.reason == "prune-target-has-no-parent-relation"
    assert result.before_shape is before


def test_prune_rejects_leaf_in_non_singleton_exponent_container() -> None:
    before = container(
        container(
            Leaf(),
            Leaf(),
        ),
    )
    invocation_target = ExplicitTarget(
        address=Address(indices=(0, 1))
    )

    result = apply_prune(
        before,
        invocation_target,
    )

    assert isinstance(result, FailedResult)
    assert result.operator is Operator.PRUNE
    assert result.reason == "prune-parent-not-singleton-exponent"
    assert result.before_shape is before


@pytest.mark.parametrize(
    ("address", "reason"),
    [
        (
            Address(indices=(9,)),
            "address-out-of-range",
        ),
        (
            Address(indices=(0, 0)),
            "address-crosses-leaf",
        ),
    ],
)
def test_prune_preserves_explicit_traversal_failures(
    address: Address,
    reason: str,
) -> None:
    before = container(Leaf())
    invocation_target = ExplicitTarget(address=address)

    result = apply_prune(
        before,
        invocation_target,
    )

    assert isinstance(result, FailedResult)
    assert result.operator is Operator.PRUNE
    assert result.reason == reason
    assert result.before_shape is before


@pytest.mark.parametrize(
    "before",
    [
        Leaf(),
        container(Leaf()),
        container(
            container(
                Leaf(),
                Leaf(),
            ),
        ),
    ],
)
def test_prune_default_reports_no_eligible_terminal_leaf(
    before: Shape,
) -> None:
    invocation_target = DefaultTarget()

    result = apply_prune(
        before,
        invocation_target,
    )

    assert isinstance(result, FailedResult)
    assert result.operator is Operator.PRUNE
    assert result.invocation_target is invocation_target
    assert result.before_shape is before
    assert result.reason == "prune-no-eligible-terminal-leaf"


@pytest.mark.parametrize(
    "invalid_target",
    [
        None,
        Address(),
        "default",
        object(),
    ],
)
def test_prune_rejects_non_normalized_targets(
    invalid_target: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="invocation_target",
    ):
        apply_prune(
            container(
                container(Leaf()),
            ),
            invalid_target,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    (
        "before",
        "graft_target",
    ),
    [
        (
            container(Leaf()),
            ExplicitTarget(
                address=Address(
                    indices=(0,),
                    is_slot=True,
                )
            ),
        ),
        (
            container(
                container(Leaf()),
                Leaf(),
            ),
            ExplicitTarget(
                address=Address(
                    indices=(0, 0),
                    is_slot=True,
                )
            ),
        ),
        (
            container(
                container(
                    Leaf(),
                    container(Leaf()),
                ),
                Leaf(),
            ),
            DefaultTarget(),
        ),
    ],
)
def test_explicit_prune_of_graft_witness_restores_shape(
    before: Container,
    graft_target: Target,
) -> None:
    graft_result = apply_graft(
        before,
        graft_target,
    )

    assert isinstance(
        graft_result,
        SuccessfulResult,
    )

    prune_result = apply_prune(
        graft_result.after_shape,
        ExplicitTarget(
            address=graft_result.address_effects.witness_address,
        ),
    )

    assert isinstance(
        prune_result,
        SuccessfulResult,
    )
    assert prune_result.after_shape == before
    assert (
        prune_result.address_effects.witness_address
        == graft_result.address_effects.target_address
    )


@pytest.mark.parametrize(
    (
        "before",
        "prune_target",
    ),
    [
        (
            container(
                container(Leaf()),
            ),
            ExplicitTarget(
                address=Address(indices=(0, 0))
            ),
        ),
        (
            container(
                container(
                    container(Leaf()),
                ),
                Leaf(),
            ),
            ExplicitTarget(
                address=Address(indices=(0, 0, 0))
            ),
        ),
        (
            container(
                container(
                    container(Leaf()),
                ),
                container(
                    container(Leaf()),
                ),
            ),
            DefaultTarget(),
        ),
    ],
)
def test_explicit_graft_of_prune_witness_restores_shape(
    before: Container,
    prune_target: Target,
) -> None:
    prune_result = apply_prune(
        before,
        prune_target,
    )

    assert isinstance(
        prune_result,
        SuccessfulResult,
    )

    graft_result = apply_graft(
        prune_result.after_shape,
        ExplicitTarget(
            address=prune_result.address_effects.witness_address,
        ),
    )

    assert isinstance(
        graft_result,
        SuccessfulResult,
    )
    assert graft_result.after_shape == before
    assert (
        graft_result.address_effects.target_address
        == prune_result.address_effects.witness_address
    )


def test_default_prune_is_not_an_inverse_guarantee() -> None:
    before = container(
        Leaf(),
        Leaf(),
    )

    graft_result = apply_graft(
        before,
        ExplicitTarget(
            address=Address(
                indices=(0,),
                is_slot=True,
            )
        ),
    )

    assert isinstance(
        graft_result,
        SuccessfulResult,
    )

    second_graft = apply_graft(
        graft_result.after_shape,
        ExplicitTarget(
            address=Address(
                indices=(1,),
                is_slot=True,
            )
        ),
    )

    assert isinstance(
        second_graft,
        SuccessfulResult,
    )

    prune_result = apply_prune(
        second_graft.after_shape,
        DefaultTarget(),
    )

    assert isinstance(
        prune_result,
        SuccessfulResult,
    )
    assert (
        prune_result.address_effects.target_address
        == second_graft.address_effects.witness_address
    )
    assert prune_result.after_shape != before


def test_default_graft_is_not_an_inverse_guarantee() -> None:
    before = container(
        container(Leaf()),
        container(
            container(Leaf()),
        ),
    )

    prune_result = apply_prune(
        before,
        ExplicitTarget(
            address=Address(indices=(0, 0))
        ),
    )

    assert isinstance(
        prune_result,
        SuccessfulResult,
    )

    graft_result = apply_graft(
        prune_result.after_shape,
        DefaultTarget(),
    )

    assert isinstance(
        graft_result,
        SuccessfulResult,
    )
    assert (
        graft_result.address_effects.target_address
        != prune_result.address_effects.witness_address
    )
    assert graft_result.after_shape != before


@pytest.mark.parametrize(
    "operator",
    [
        apply_graft,
        apply_prune,
    ],
)
def test_depth_operators_validate_shape_before_selection(
    operator: DepthOperator,
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
        apply_graft,
        apply_prune,
    ],
)
def test_depth_operators_reject_non_shape_objects(
    operator: DepthOperator,
) -> None:
    with pytest.raises(
        TypeError,
        match="PETRA",
    ):
        operator(
            object(),  # type: ignore[arg-type]
            DefaultTarget(),
        )
