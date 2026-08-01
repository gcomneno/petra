"""Contract tests for PETRA atomic operator results and witnesses."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
import subprocess
import sys
import textwrap
from typing import get_args

import pytest

from petra import (
    Address,
    AddressEffects,
    Container,
    DefaultTarget,
    ExplicitTarget,
    FailedResult,
    InvocationTarget,
    Leaf,
    Operator,
    OperatorResult,
    ResolvedAnchor,
    ResolvedSlot,
    ResolvedTerm,
    Root,
    SuccessfulResult,
    Term,
    resolve_address,
    to_canonical_data,
)


def term(rank: int, exponent: Leaf | Container) -> Term:
    return Term(root=Root(rank), exponent=exponent)


def container(*exponents: Leaf | Container) -> Container:
    return Container(
        terms=tuple(
            term(rank, exponent)
            for rank, exponent in enumerate(exponents)
        )
    )


def success_components(
    operator: Operator,
) -> tuple[
    Leaf | Container,
    Leaf | Container,
    Address,
    Address,
]:
    if operator is Operator.SPROUT:
        return (
            container(Leaf()),
            container(Leaf(), Leaf()),
            Address(),
            Address(indices=(1,)),
        )

    if operator is Operator.SHED:
        return (
            container(Leaf(), Leaf()),
            container(Leaf()),
            Address(indices=(1,)),
            Address(),
        )

    if operator is Operator.GRAFT:
        return (
            container(Leaf()),
            container(container(Leaf())),
            Address(indices=(0,), is_slot=True),
            Address(indices=(0, 0)),
        )

    if operator is Operator.PRUNE:
        return (
            container(container(Leaf())),
            container(Leaf()),
            Address(indices=(0, 0)),
            Address(indices=(0,), is_slot=True),
        )

    raise AssertionError(f"unsupported test operator: {operator}")


def make_success(
    operator: Operator,
    *,
    explicit: bool,
) -> SuccessfulResult:
    before_shape, after_shape, target_address, witness_address = (
        success_components(operator)
    )

    invocation_target: DefaultTarget | ExplicitTarget

    if explicit:
        invocation_target = ExplicitTarget(
            address=target_address,
        )
    else:
        invocation_target = DefaultTarget()

    resolved_target = resolve_address(
        before_shape,
        target_address,
    )

    return SuccessfulResult(
        operator=operator,
        invocation_target=invocation_target,
        resolved_target=resolved_target,
        before_shape=before_shape,
        after_shape=after_shape,
        address_effects=AddressEffects(
            target_address=target_address,
            witness_address=witness_address,
        ),
    )


def test_operator_identity_is_closed_and_canonical() -> None:
    assert tuple(Operator) == (
        Operator.SPROUT,
        Operator.SHED,
        Operator.GRAFT,
        Operator.PRUNE,
    )

    assert [operator.value for operator in Operator] == [
        "SPROUT",
        "SHED",
        "GRAFT",
        "PRUNE",
    ]

    assert [str(operator) for operator in Operator] == [
        "SPROUT",
        "SHED",
        "GRAFT",
        "PRUNE",
    ]

    for value in (
        "SPROUT",
        "SHED",
        "GRAFT",
        "PRUNE",
    ):
        assert Operator(value).value == value


@pytest.mark.parametrize(
    "value",
    [
        "",
        "sprout",
        "Sprout",
        "DELETE",
        0,
        None,
    ],
)
def test_operator_identity_rejects_unknown_values(
    value: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        Operator(value)


def test_invocation_target_variants_are_minimal() -> None:
    assert [field.name for field in fields(DefaultTarget)] == []
    assert [field.name for field in fields(ExplicitTarget)] == [
        "address",
    ]

    default = DefaultTarget()
    explicit = ExplicitTarget(
        address=Address(indices=(0,)),
    )

    assert default.mode == "default"
    assert explicit.mode == "explicit"
    assert explicit.address == Address(indices=(0,))

    assert set(get_args(InvocationTarget)) == {
        DefaultTarget,
        ExplicitTarget,
    }


def test_invocation_target_variants_are_immutable() -> None:
    default = DefaultTarget()
    explicit = ExplicitTarget(
        address=Address(indices=(0,)),
    )

    with pytest.raises(FrozenInstanceError):
        default.mode = "explicit"

    with pytest.raises(FrozenInstanceError):
        explicit.address = Address(indices=(1,))


@pytest.mark.parametrize(
    "value",
    [
        "@/0",
        None,
        0,
        object(),
    ],
)
def test_explicit_target_requires_canonical_address(
    value: object,
) -> None:
    with pytest.raises(TypeError):
        ExplicitTarget(address=value)


def test_address_effects_are_minimal_and_immutable() -> None:
    effects = AddressEffects(
        target_address=Address(indices=(0,)),
        witness_address=Address(indices=(1,)),
    )

    assert [field.name for field in fields(AddressEffects)] == [
        "target_address",
        "witness_address",
    ]

    assert effects.target_address == Address(indices=(0,))
    assert effects.witness_address == Address(indices=(1,))

    with pytest.raises(FrozenInstanceError):
        effects.target_address = Address()


@pytest.mark.parametrize(
    ("target_address", "witness_address"),
    [
        ("@/0", Address()),
        (Address(), "@/0"),
        (None, Address()),
        (Address(), None),
    ],
)
def test_address_effects_require_address_values(
    target_address: object,
    witness_address: object,
) -> None:
    with pytest.raises(TypeError):
        AddressEffects(
            target_address=target_address,
            witness_address=witness_address,
        )


def test_result_variants_have_disjoint_minimal_fields() -> None:
    assert [field.name for field in fields(SuccessfulResult)] == [
        "operator",
        "invocation_target",
        "resolved_target",
        "before_shape",
        "after_shape",
        "address_effects",
    ]

    assert [field.name for field in fields(FailedResult)] == [
        "operator",
        "invocation_target",
        "before_shape",
        "reason",
    ]

    assert set(get_args(OperatorResult)) == {
        SuccessfulResult,
        FailedResult,
    }


@pytest.mark.parametrize(
    "operator",
    list(Operator),
)
@pytest.mark.parametrize(
    "explicit",
    [False, True],
    ids=["default", "explicit"],
)
def test_success_results_cover_all_operators_and_target_modes(
    operator: Operator,
    explicit: bool,
) -> None:
    result = make_success(
        operator,
        explicit=explicit,
    )

    assert result.schema == "petra.operator-result.v1"
    assert result.status == "ok"
    assert result.operator is operator
    assert result.reason == (
        f"{operator.value.lower()}-applied"
    )

    if explicit:
        assert isinstance(
            result.invocation_target,
            ExplicitTarget,
        )
        assert (
            result.invocation_target.address
            == result.resolved_target.address
        )
    else:
        assert isinstance(
            result.invocation_target,
            DefaultTarget,
        )

    assert result.address_effects.target_address == (
        result.resolved_target.address
    )

    assert resolve_address(
        result.after_shape,
        result.address_effects.witness_address,
    ).address == result.address_effects.witness_address


@pytest.mark.parametrize(
    ("operator", "resolved_type", "witness_type"),
    [
        (
            Operator.SPROUT,
            ResolvedAnchor,
            ResolvedTerm,
        ),
        (
            Operator.SHED,
            ResolvedTerm,
            ResolvedAnchor,
        ),
        (
            Operator.GRAFT,
            ResolvedSlot,
            ResolvedTerm,
        ),
        (
            Operator.PRUNE,
            ResolvedTerm,
            ResolvedSlot,
        ),
    ],
)
def test_success_records_preserve_target_and_witness_kinds(
    operator: Operator,
    resolved_type: type[
        ResolvedAnchor | ResolvedTerm | ResolvedSlot
    ],
    witness_type: type[
        ResolvedAnchor | ResolvedTerm | ResolvedSlot
    ],
) -> None:
    result = make_success(
        operator,
        explicit=True,
    )

    assert isinstance(result.resolved_target, resolved_type)

    witness = resolve_address(
        result.after_shape,
        result.address_effects.witness_address,
    )

    assert isinstance(witness, witness_type)


def test_success_result_is_immutable() -> None:
    result = make_success(
        Operator.SPROUT,
        explicit=False,
    )

    with pytest.raises(FrozenInstanceError):
        result.operator = Operator.SHED

    with pytest.raises(FrozenInstanceError):
        result.after_shape = Leaf()

    with pytest.raises(FrozenInstanceError):
        result.address_effects = AddressEffects(
            target_address=Address(),
            witness_address=Address(),
        )


def test_success_preserves_exact_shape_references() -> None:
    before_shape, after_shape, target_address, witness_address = (
        success_components(Operator.GRAFT)
    )

    result = SuccessfulResult(
        operator=Operator.GRAFT,
        invocation_target=ExplicitTarget(
            address=target_address,
        ),
        resolved_target=resolve_address(
            before_shape,
            target_address,
        ),
        before_shape=before_shape,
        after_shape=after_shape,
        address_effects=AddressEffects(
            target_address=target_address,
            witness_address=witness_address,
        ),
    )

    assert result.before_shape is before_shape
    assert result.after_shape is after_shape


def test_success_construction_never_mutates_shapes() -> None:
    before_shape, after_shape, target_address, witness_address = (
        success_components(Operator.PRUNE)
    )

    before_data = to_canonical_data(before_shape)
    after_data = to_canonical_data(after_shape)

    SuccessfulResult(
        operator=Operator.PRUNE,
        invocation_target=ExplicitTarget(
            address=target_address,
        ),
        resolved_target=resolve_address(
            before_shape,
            target_address,
        ),
        before_shape=before_shape,
        after_shape=after_shape,
        address_effects=AddressEffects(
            target_address=target_address,
            witness_address=witness_address,
        ),
    )

    assert to_canonical_data(before_shape) == before_data
    assert to_canonical_data(after_shape) == after_data


@pytest.mark.parametrize(
    "field_name",
    [
        "operator",
        "invocation_target",
        "resolved_target",
        "before_shape",
        "after_shape",
        "address_effects",
    ],
)
def test_success_rejects_wrong_runtime_types(
    field_name: str,
) -> None:
    before_shape, after_shape, target_address, witness_address = (
        success_components(Operator.SPROUT)
    )

    values: dict[str, object] = {
        "operator": Operator.SPROUT,
        "invocation_target": DefaultTarget(),
        "resolved_target": resolve_address(
            before_shape,
            target_address,
        ),
        "before_shape": before_shape,
        "after_shape": after_shape,
        "address_effects": AddressEffects(
            target_address=target_address,
            witness_address=witness_address,
        ),
    }

    values[field_name] = object()

    with pytest.raises(TypeError):
        SuccessfulResult(**values)


def test_success_rejects_explicit_target_mismatch() -> None:
    before_shape = container(Leaf(), Leaf())
    after_shape = container(Leaf(), Leaf(), Leaf())

    with pytest.raises(ValueError):
        SuccessfulResult(
            operator=Operator.SPROUT,
            invocation_target=ExplicitTarget(
                address=Address(indices=(1,)),
            ),
            resolved_target=resolve_address(
                before_shape,
                Address(indices=(0,)),
            ),
            before_shape=before_shape,
            after_shape=after_shape,
            address_effects=AddressEffects(
                target_address=Address(indices=(0,)),
                witness_address=Address(indices=(2,)),
            ),
        )


def test_success_rejects_effect_target_mismatch() -> None:
    before_shape = container(Leaf(), Leaf())
    after_shape = container(Leaf())

    with pytest.raises(ValueError):
        SuccessfulResult(
            operator=Operator.SHED,
            invocation_target=ExplicitTarget(
                address=Address(indices=(1,)),
            ),
            resolved_target=resolve_address(
                before_shape,
                Address(indices=(1,)),
            ),
            before_shape=before_shape,
            after_shape=after_shape,
            address_effects=AddressEffects(
                target_address=Address(indices=(0,)),
                witness_address=Address(),
            ),
        )


def test_success_rejects_target_from_different_before_shape() -> None:
    before_shape = container(Leaf())
    foreign_shape = container(container(Leaf()))
    after_shape = container(Leaf(), Leaf())

    foreign_target = resolve_address(
        foreign_shape,
        Address(indices=(0,)),
    )

    with pytest.raises(ValueError):
        SuccessfulResult(
            operator=Operator.SPROUT,
            invocation_target=ExplicitTarget(
                address=Address(indices=(0,)),
            ),
            resolved_target=foreign_target,
            before_shape=before_shape,
            after_shape=after_shape,
            address_effects=AddressEffects(
                target_address=Address(indices=(0,)),
                witness_address=Address(indices=(1,)),
            ),
        )


@pytest.mark.parametrize(
    "witness_address",
    [
        Address(indices=(1,)),
        Address(indices=(0, 0)),
    ],
)
def test_success_rejects_unresolvable_witness(
    witness_address: Address,
) -> None:
    before_shape = container(Leaf())
    after_shape = container(Leaf())

    with pytest.raises(ValueError):
        SuccessfulResult(
            operator=Operator.SPROUT,
            invocation_target=DefaultTarget(),
            resolved_target=resolve_address(
                before_shape,
                Address(),
            ),
            before_shape=before_shape,
            after_shape=after_shape,
            address_effects=AddressEffects(
                target_address=Address(),
                witness_address=witness_address,
            ),
        )


def test_success_accepts_equivalent_independent_shapes() -> None:
    before_a = container(container(Leaf()))
    after_a = container(Leaf())

    before_b = container(container(Leaf()))
    after_b = container(Leaf())

    address = Address(indices=(0, 0))
    witness = Address(indices=(0,), is_slot=True)

    result_a = SuccessfulResult(
        operator=Operator.PRUNE,
        invocation_target=ExplicitTarget(address=address),
        resolved_target=resolve_address(before_a, address),
        before_shape=before_a,
        after_shape=after_a,
        address_effects=AddressEffects(
            target_address=address,
            witness_address=witness,
        ),
    )

    result_b = SuccessfulResult(
        operator=Operator.PRUNE,
        invocation_target=ExplicitTarget(address=address),
        resolved_target=resolve_address(before_b, address),
        before_shape=before_b,
        after_shape=after_b,
        address_effects=AddressEffects(
            target_address=address,
            witness_address=witness,
        ),
    )

    assert result_a == result_b


VALID_FAILURES = [
    (
        Operator.SPROUT,
        None,
        "address-malformed",
    ),
    (
        Operator.SHED,
        None,
        "address-malformed",
    ),
    (
        Operator.GRAFT,
        None,
        "address-malformed",
    ),
    (
        Operator.PRUNE,
        None,
        "address-malformed",
    ),
    *[
        (
            operator,
            ExplicitTarget(address=Address(indices=(99,))),
            reason,
        )
        for operator in Operator
        for reason in (
            "address-out-of-range",
            "address-crosses-leaf",
        )
    ],
    (
        Operator.SPROUT,
        ExplicitTarget(address=Address(indices=(0,))),
        "sprout-target-not-container",
    ),
    (
        Operator.SHED,
        ExplicitTarget(address=Address()),
        "shed-target-not-leaf",
    ),
    (
        Operator.SHED,
        DefaultTarget(),
        "shed-no-eligible-top-level-leaf",
    ),
    (
        Operator.GRAFT,
        ExplicitTarget(address=Address()),
        "graft-target-not-slot",
    ),
    (
        Operator.GRAFT,
        ExplicitTarget(
            address=Address(indices=(0,), is_slot=True),
        ),
        "graft-slot-already-materialized",
    ),
    (
        Operator.GRAFT,
        DefaultTarget(),
        "graft-no-eligible-latent-slot",
    ),
    (
        Operator.PRUNE,
        ExplicitTarget(address=Address()),
        "prune-target-not-terminal-leaf",
    ),
    (
        Operator.PRUNE,
        ExplicitTarget(address=Address(indices=(0,))),
        "prune-target-has-no-parent-relation",
    ),
    (
        Operator.PRUNE,
        ExplicitTarget(address=Address(indices=(0, 0))),
        "prune-parent-not-singleton-exponent",
    ),
    (
        Operator.PRUNE,
        DefaultTarget(),
        "prune-no-eligible-terminal-leaf",
    ),
]


@pytest.mark.parametrize(
    ("operator", "invocation_target", "reason"),
    VALID_FAILURES,
)
def test_failed_results_accept_normative_reason_matrix(
    operator: Operator,
    invocation_target: DefaultTarget | ExplicitTarget | None,
    reason: str,
) -> None:
    before_shape = container(Leaf())

    result = FailedResult(
        operator=operator,
        invocation_target=invocation_target,
        before_shape=before_shape,
        reason=reason,
    )

    assert result.schema == "petra.operator-result.v1"
    assert result.status == "failed"
    assert result.operator is operator
    assert result.invocation_target == invocation_target
    assert result.before_shape is before_shape
    assert result.reason == reason

    assert not hasattr(result, "after_shape")
    assert not hasattr(result, "resolved_target")
    assert not hasattr(result, "address_effects")


@pytest.mark.parametrize(
    ("operator", "invocation_target"),
    [
        (None, None),
        (Operator.SPROUT, None),
        (None, DefaultTarget()),
        (
            None,
            ExplicitTarget(
                address=Address(indices=(0,)),
            ),
        ),
        (Operator.SHED, DefaultTarget()),
        (
            Operator.GRAFT,
            ExplicitTarget(
                address=Address(
                    indices=(0,),
                    is_slot=True,
                )
            ),
        ),
    ],
)
def test_invocation_invalid_preserves_available_normalized_state(
    operator: Operator | None,
    invocation_target: DefaultTarget | ExplicitTarget | None,
) -> None:
    before_shape = Leaf()

    result = FailedResult(
        operator=operator,
        invocation_target=invocation_target,
        before_shape=before_shape,
        reason="invocation-invalid",
    )

    assert result.operator is operator
    assert result.invocation_target == invocation_target
    assert result.before_shape is before_shape
    assert result.reason == "invocation-invalid"


def test_failed_result_is_immutable() -> None:
    result = FailedResult(
        operator=Operator.SHED,
        invocation_target=DefaultTarget(),
        before_shape=Leaf(),
        reason="shed-no-eligible-top-level-leaf",
    )

    with pytest.raises(FrozenInstanceError):
        result.reason = "invocation-invalid"

    with pytest.raises(FrozenInstanceError):
        result.operator = None


@pytest.mark.parametrize(
    "reason",
    [
        "",
        "unknown",
        "address-kind-mismatch",
        "slot-not-latent",
        "sprout-no-eligible-container",
        "shed-target-not-direct-child",
        None,
        0,
    ],
)
def test_failed_result_rejects_unknown_reason(
    reason: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        FailedResult(
            operator=Operator.SPROUT,
            invocation_target=DefaultTarget(),
            before_shape=Leaf(),
            reason=reason,
        )


@pytest.mark.parametrize(
    ("operator", "reason"),
    [
        (
            Operator.SHED,
            "sprout-target-not-container",
        ),
        (
            Operator.GRAFT,
            "shed-target-not-leaf",
        ),
        (
            Operator.PRUNE,
            "graft-target-not-slot",
        ),
        (
            Operator.SPROUT,
            "prune-target-not-terminal-leaf",
        ),
    ],
)
def test_failed_result_rejects_reason_for_other_operator(
    operator: Operator,
    reason: str,
) -> None:
    with pytest.raises(ValueError):
        FailedResult(
            operator=operator,
            invocation_target=ExplicitTarget(
                address=Address(indices=(0,)),
            ),
            before_shape=container(Leaf()),
            reason=reason,
        )


@pytest.mark.parametrize(
    "reason",
    [
        "address-out-of-range",
        "address-crosses-leaf",
    ],
)
def test_traversal_failures_require_explicit_target(
    reason: str,
) -> None:
    with pytest.raises(ValueError):
        FailedResult(
            operator=Operator.SPROUT,
            invocation_target=DefaultTarget(),
            before_shape=Leaf(),
            reason=reason,
        )

    with pytest.raises(ValueError):
        FailedResult(
            operator=Operator.SPROUT,
            invocation_target=None,
            before_shape=Leaf(),
            reason=reason,
        )


def test_address_malformed_requires_operator_and_no_target() -> None:
    with pytest.raises(ValueError):
        FailedResult(
            operator=None,
            invocation_target=None,
            before_shape=Leaf(),
            reason="address-malformed",
        )

    with pytest.raises(ValueError):
        FailedResult(
            operator=Operator.GRAFT,
            invocation_target=ExplicitTarget(
                address=Address(indices=(0,)),
            ),
            before_shape=Leaf(),
            reason="address-malformed",
        )

    with pytest.raises(ValueError):
        FailedResult(
            operator=Operator.GRAFT,
            invocation_target=DefaultTarget(),
            before_shape=Leaf(),
            reason="address-malformed",
        )


@pytest.mark.parametrize(
    ("operator", "reason"),
    [
        (
            Operator.SHED,
            "shed-no-eligible-top-level-leaf",
        ),
        (
            Operator.GRAFT,
            "graft-no-eligible-latent-slot",
        ),
        (
            Operator.PRUNE,
            "prune-no-eligible-terminal-leaf",
        ),
    ],
)
def test_no_eligible_reasons_require_default_target(
    operator: Operator,
    reason: str,
) -> None:
    with pytest.raises(ValueError):
        FailedResult(
            operator=operator,
            invocation_target=ExplicitTarget(
                address=Address(indices=(0,)),
            ),
            before_shape=Leaf(),
            reason=reason,
        )


@pytest.mark.parametrize(
    ("operator", "reason"),
    [
        (
            Operator.SPROUT,
            "sprout-target-not-container",
        ),
        (
            Operator.SHED,
            "shed-target-not-leaf",
        ),
        (
            Operator.GRAFT,
            "graft-target-not-slot",
        ),
        (
            Operator.GRAFT,
            "graft-slot-already-materialized",
        ),
        (
            Operator.PRUNE,
            "prune-target-not-terminal-leaf",
        ),
        (
            Operator.PRUNE,
            "prune-target-has-no-parent-relation",
        ),
        (
            Operator.PRUNE,
            "prune-parent-not-singleton-exponent",
        ),
    ],
)
def test_explicit_target_reasons_reject_default_mode(
    operator: Operator,
    reason: str,
) -> None:
    with pytest.raises(ValueError):
        FailedResult(
            operator=operator,
            invocation_target=DefaultTarget(),
            before_shape=Leaf(),
            reason=reason,
        )


@pytest.mark.parametrize(
    ("field_name", "bad_value"),
    [
        ("operator", "SPROUT"),
        ("invocation_target", {"mode": "default"}),
        ("before_shape", object()),
    ],
)
def test_failed_result_rejects_wrong_runtime_types(
    field_name: str,
    bad_value: object,
) -> None:
    values: dict[str, object] = {
        "operator": Operator.SPROUT,
        "invocation_target": DefaultTarget(),
        "before_shape": Leaf(),
        "reason": "invocation-invalid",
    }

    values[field_name] = bad_value

    with pytest.raises(TypeError):
        FailedResult(**values)


def test_failed_result_never_normalizes_or_mutates_before_shape() -> None:
    before_shape = container(container(Leaf()), Leaf())
    before_data = to_canonical_data(before_shape)

    result = FailedResult(
        operator=Operator.GRAFT,
        invocation_target=DefaultTarget(),
        before_shape=before_shape,
        reason="graft-no-eligible-latent-slot",
    )

    assert result.before_shape is before_shape
    assert to_canonical_data(before_shape) == before_data


def test_equivalent_failures_compare_equal() -> None:
    result_a = FailedResult(
        operator=Operator.SHED,
        invocation_target=DefaultTarget(),
        before_shape=container(Leaf()),
        reason="shed-no-eligible-top-level-leaf",
    )

    result_b = FailedResult(
        operator=Operator.SHED,
        invocation_target=DefaultTarget(),
        before_shape=container(Leaf()),
        reason="shed-no-eligible-top-level-leaf",
    )

    assert result_a == result_b


def test_operator_identity_falls_back_without_native_strenum() -> None:
    """The Python 3.10 compatibility path preserves string-enum behavior."""

    script = textwrap.dedent(
        """
        import enum
        import json
        import sys

        if hasattr(enum, "StrEnum"):
            delattr(enum, "StrEnum")

        for module_name in tuple(sys.modules):
            if (
                module_name == "petra"
                or module_name.startswith("petra.")
            ):
                del sys.modules[module_name]

        import petra

        operator = petra.Operator.SPROUT

        assert isinstance(operator, str)
        assert operator == "SPROUT"
        assert operator.value == "SPROUT"
        assert str(operator) == "SPROUT"
        assert format(operator) == "SPROUT"
        assert f"{operator:>8}" == "  SPROUT"
        assert json.dumps(
            {"operator": operator}
        ) == '{"operator": "SPROUT"}'

        assert tuple(
            member.value
            for member in petra.Operator
        ) == (
            "SPROUT",
            "SHED",
            "GRAFT",
            "PRUNE",
        )
        """
    )

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
