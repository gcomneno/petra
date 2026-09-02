from __future__ import annotations

import json

import pytest

from petra import (
    Address,
    DefaultTarget,
    ExplicitTarget,
    FailedResult,
    Leaf,
    Operator,
    serialize_result,
)


@pytest.mark.parametrize(
    ("operator", "target", "reason"),
    [
        (
            Operator.SPROUT,
            ExplicitTarget(Address((4,))),
            "address-out-of-range",
        ),
        (
            Operator.SHED,
            ExplicitTarget(Address((0, 0))),
            "address-crosses-leaf",
        ),
        (
            Operator.SPROUT,
            ExplicitTarget(Address((0,))),
            "sprout-target-not-container",
        ),
        (
            Operator.SHED,
            ExplicitTarget(Address((0,), is_slot=True)),
            "shed-target-not-leaf",
        ),
        (
            Operator.GRAFT,
            ExplicitTarget(Address((0,))),
            "graft-target-not-slot",
        ),
        (
            Operator.GRAFT,
            ExplicitTarget(Address((0,), is_slot=True)),
            "graft-slot-already-materialized",
        ),
        (
            Operator.PRUNE,
            ExplicitTarget(Address()),
            "prune-target-not-terminal-leaf",
        ),
        (
            Operator.PRUNE,
            ExplicitTarget(Address((0,))),
            "prune-target-has-no-parent-relation",
        ),
        (
            Operator.PRUNE,
            ExplicitTarget(Address((0, 1))),
            "prune-parent-not-singleton-exponent",
        ),
        (
            Operator.SHED,
            DefaultTarget(),
            "shed-no-eligible-top-level-leaf",
        ),
        (
            Operator.GRAFT,
            DefaultTarget(),
            "graft-no-eligible-latent-slot",
        ),
        (
            Operator.PRUNE,
            DefaultTarget(),
            "prune-no-eligible-terminal-leaf",
        ),
    ],
)
def test_failure_reason_families_serialize_without_success_state(
    operator: Operator,
    target: DefaultTarget | ExplicitTarget,
    reason: str,
) -> None:
    result = FailedResult(
        operator=operator,
        invocation_target=target,
        before_shape=Leaf(),
        reason=reason,
    )

    payload = json.loads(serialize_result(result))

    assert payload["schema"] == "petra.operator-result.v1"
    assert payload["status"] == "failed"
    assert payload["operator"] == operator.value
    assert payload["reason"] == reason
    assert payload["before_shape"] == "1"
    assert payload["invocation_target"]["mode"] == target.mode
    assert "after_shape" not in payload
    assert "resolved_target" not in payload
    assert "address_effects" not in payload


def test_address_malformed_failure_serializes_partially_normalized_state() -> None:
    result = FailedResult(
        operator=Operator.GRAFT,
        invocation_target=None,
        before_shape=Leaf(),
        reason="address-malformed",
    )

    assert json.loads(serialize_result(result)) == {
        "schema": "petra.operator-result.v1",
        "status": "failed",
        "operator": "GRAFT",
        "invocation_target": None,
        "before_shape": "1",
        "reason": "address-malformed",
    }
