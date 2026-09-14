from __future__ import annotations

import json

import pytest

from petra import (
    Address,
    DefaultTarget,
    ExplicitTarget,
    FailedResult,
    InvocationSyntaxError,
    Leaf,
    Operator,
    apply_graft,
    apply_shed,
    apply_sprout,
    parse_invocation_json,
    serialize_invocation,
    serialize_result,
)


@pytest.mark.parametrize("operator", list(Operator))
def test_default_invocation_round_trips_canonically(operator: Operator) -> None:
    target = DefaultTarget()

    text = serialize_invocation(operator, target)

    assert text == (
        f'{{"operator":"{operator.value}","schema":"petra.operator-invocation.v1",'
        '"target":{"mode":"default"}}'
    )
    assert parse_invocation_json(text) == (operator, target)


@pytest.mark.parametrize(
    ("operator", "address"),
    [
        (Operator.SPROUT, Address()),
        (Operator.SHED, Address((0,))),
        (Operator.GRAFT, Address((0, 0), is_slot=True)),
        (Operator.PRUNE, Address((0, 0))),
    ],
)
def test_explicit_invocation_round_trips_canonically(
    operator: Operator,
    address: Address,
) -> None:
    target = ExplicitTarget(address)

    text = serialize_invocation(operator, target)

    parsed = json.loads(text)
    assert parsed == {
        "schema": "petra.operator-invocation.v1",
        "operator": operator.value,
        "target": {
            "mode": "explicit",
            "address": str(address),
        },
    }
    assert parse_invocation_json(text) == (operator, target)


@pytest.mark.parametrize(
    "text",
    [
        "not-json",
        "[]",
        "{}",
        '{"schema":"wrong","operator":"SPROUT","target":{"mode":"default"}}',
        '{"schema":"petra.operator-invocation.v1","operator":"NEW","target":{"mode":"default"}}',
        '{"schema":"petra.operator-invocation.v1","operator":"SPROUT"}',
        '{"schema":"petra.operator-invocation.v1","operator":"SPROUT","target":{"mode":"default","address":"@/"}}',
        '{"schema":"petra.operator-invocation.v1","operator":"SPROUT","target":{"mode":"explicit"}}',
        '{"schema":"petra.operator-invocation.v1","operator":"SPROUT","target":{"mode":"other"}}',
        '{"schema":"petra.operator-invocation.v1","operator":"SPROUT","target":{"mode":"default"},"extra":true}',
        '{"schema":"petra.operator-invocation.v1","schema":"petra.operator-invocation.v1","operator":"SPROUT","target":{"mode":"default"}}',
        '{"schema":"petra.operator-invocation.v1","operator":"SPROUT","target":{"mode":"default","mode":"default"}}',
        '{"schema":"petra.operator-invocation.v1","operator":"SPROUT","target":{"mode":"default"},"x":NaN}',
    ],
)
def test_invalid_invocation_envelope_has_stable_reason(text: str) -> None:
    with pytest.raises(InvocationSyntaxError) as captured:
        parse_invocation_json(text)

    assert captured.value.reason == "invocation-invalid"


@pytest.mark.parametrize("value", [None, 1, {}, [], b"{}"])
def test_non_text_invocation_is_invalid(value: object) -> None:
    with pytest.raises(InvocationSyntaxError) as captured:
        parse_invocation_json(value)

    assert captured.value.reason == "invocation-invalid"


def test_malformed_explicit_address_has_address_reason_after_envelope_validation() -> None:
    text = (
        '{"schema":"petra.operator-invocation.v1","operator":"GRAFT",'
        '"target":{"mode":"explicit","address":"@/00/^"}}'
    )

    with pytest.raises(InvocationSyntaxError) as captured:
        parse_invocation_json(text)

    assert captured.value.reason == "address-malformed"


def test_invocation_serializer_rejects_non_typed_values() -> None:
    with pytest.raises(TypeError, match="operator must be an Operator"):
        serialize_invocation("SPROUT", DefaultTarget())  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="invocation_target must be a normalized target"):
        serialize_invocation(Operator.SPROUT, object())  # type: ignore[arg-type]


def test_sprout_success_serializes_anchor_and_witness_exactly() -> None:
    result = apply_sprout(Leaf(), DefaultTarget())

    payload = json.loads(serialize_result(result))

    assert payload == {
        "schema": "petra.operator-result.v1",
        "status": "ok",
        "operator": "SPROUT",
        "invocation_target": {"mode": "default"},
        "resolved_target": {"kind": "anchor", "address": "@/"},
        "before_shape": "1",
        "after_shape": "C(r0^1)",
        "address_effects": {
            "target_address": "@/",
            "witness_address": "@/0",
        },
        "reason": "sprout-applied",
    }


def test_explicit_shed_success_serializes_term_target() -> None:
    before = apply_sprout(Leaf(), DefaultTarget()).after_shape
    result = apply_shed(before, ExplicitTarget(Address((0,))))

    payload = json.loads(serialize_result(result))

    assert payload["resolved_target"] == {
        "kind": "term",
        "address": "@/0",
    }
    assert payload["invocation_target"] == {
        "mode": "explicit",
        "address": "@/0",
    }
    assert payload["reason"] == "shed-applied"


def test_explicit_graft_success_serializes_slot_target() -> None:
    before = apply_sprout(Leaf(), DefaultTarget()).after_shape
    result = apply_graft(
        before,
        ExplicitTarget(Address((0,), is_slot=True)),
    )

    payload = json.loads(serialize_result(result))

    assert payload["resolved_target"] == {
        "kind": "slot",
        "address": "@/0/^",
    }
    assert payload["reason"] == "graft-applied"


@pytest.mark.parametrize("operator", list(Operator))
def test_success_reason_and_schema_are_serialized_for_every_operator(
    operator: Operator,
) -> None:
    root = apply_sprout(Leaf(), DefaultTarget()).after_shape
    grafted = apply_graft(
        root,
        ExplicitTarget(Address((0,), is_slot=True)),
    ).after_shape

    if operator is Operator.SPROUT:
        result = apply_sprout(root, DefaultTarget())
    elif operator is Operator.SHED:
        result = apply_shed(root, DefaultTarget())
    elif operator is Operator.GRAFT:
        result = apply_graft(
            root,
            ExplicitTarget(Address((0,), is_slot=True)),
        )
    else:
        from petra import apply_prune

        result = apply_prune(
            grafted,
            ExplicitTarget(Address((0, 0))),
        )

    payload = json.loads(serialize_result(result))
    assert payload["schema"] == "petra.operator-result.v1"
    assert payload["status"] == "ok"
    assert payload["operator"] == operator.value
    assert payload["reason"] == f"{operator.value.lower()}-applied"


def test_failure_serialization_has_no_success_only_fields() -> None:
    result = FailedResult(
        operator=Operator.SHED,
        invocation_target=DefaultTarget(),
        before_shape=Leaf(),
        reason="shed-no-eligible-top-level-leaf",
    )

    payload = json.loads(serialize_result(result))

    assert payload == {
        "schema": "petra.operator-result.v1",
        "status": "failed",
        "operator": "SHED",
        "invocation_target": {"mode": "default"},
        "before_shape": "1",
        "reason": "shed-no-eligible-top-level-leaf",
    }
    assert "after_shape" not in payload
    assert "resolved_target" not in payload
    assert "address_effects" not in payload


def test_raw_invocation_failure_can_serialize_null_normalized_state() -> None:
    result = FailedResult(
        operator=None,
        invocation_target=None,
        before_shape=Leaf(),
        reason="invocation-invalid",
    )

    assert json.loads(serialize_result(result)) == {
        "schema": "petra.operator-result.v1",
        "status": "failed",
        "operator": None,
        "invocation_target": None,
        "before_shape": "1",
        "reason": "invocation-invalid",
    }


def test_result_serializer_rejects_non_result_values() -> None:
    with pytest.raises(TypeError, match="expected an OperatorResult"):
        serialize_result(object())  # type: ignore[arg-type]


def test_public_json_serialization_is_compact_sorted_and_has_no_newline() -> None:
    invocation = serialize_invocation(Operator.SPROUT, DefaultTarget())
    result = serialize_result(apply_sprout(Leaf(), DefaultTarget()))

    assert invocation == json.dumps(
        json.loads(invocation),
        sort_keys=True,
        separators=(",", ":"),
    )
    assert result == json.dumps(
        json.loads(result),
        sort_keys=True,
        separators=(",", ":"),
    )
    assert not invocation.endswith("\n")
    assert not result.endswith("\n")
