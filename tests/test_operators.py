import pytest

from pet import (
    PETOperatorTarget,
    dec_target,
    drop_target,
    inc_target,
    new_target,
    pet_object_from_int,
    resolve_operator_target,
)


def test_new_target_accepts_fresh_prime_at_root_parent() -> None:
    obj = pet_object_from_int(60)

    target = new_target(obj, (), 7)

    assert isinstance(target, PETOperatorTarget)
    assert target.op == "NEW"
    assert target.axis == "X"
    assert target.target_kind == "parent-support"
    assert target.valid is True
    assert target.reason == "new-target-valid"
    assert target.address_resolution == "valid"
    assert target.target_object is obj


def test_new_target_rejects_existing_or_nonprime_root() -> None:
    obj = pet_object_from_int(60)

    existing = new_target(obj, (), 3)
    nonprime = new_target(obj, (), 9)

    assert existing.valid is False
    assert existing.reason == "q-already-in-target-baseline"

    assert nonprime.valid is False
    assert nonprime.reason == "argument-not-prime"


def test_new_target_rejects_atomic_parent_address() -> None:
    obj = pet_object_from_int(60)

    target = new_target(obj, (3,), 7)

    assert target.valid is False
    assert target.reason == "parent-address-selects-atomic-leaf"
    assert target.target_object is not None
    assert target.target_object.value == 3


def test_drop_target_accepts_existing_prime_at_root_parent() -> None:
    obj = pet_object_from_int(60)

    target = drop_target(obj, (), 5)

    assert target.op == "DROP"
    assert target.axis == "X"
    assert target.valid is True
    assert target.reason == "drop-target-valid"
    assert target.target_object is obj


def test_drop_target_rejects_missing_or_nonprime_root() -> None:
    obj = pet_object_from_int(60)

    missing = drop_target(obj, (), 7)
    nonprime = drop_target(obj, (), 9)

    assert missing.valid is False
    assert missing.reason == "p-not-in-target-baseline"

    assert nonprime.valid is False
    assert nonprime.reason == "argument-not-prime"


def test_inc_target_accepts_composite_and_atomic_selected_roots() -> None:
    obj = pet_object_from_int(60)

    composite = inc_target(obj, (2,))
    atomic = inc_target(obj, (3,))

    assert composite.valid is True
    assert composite.reason == "inc-target-valid"
    assert composite.target_object is not None
    assert composite.target_object.value == 4

    assert atomic.valid is True
    assert atomic.reason == "inc-target-valid"
    assert atomic.target_object is not None
    assert atomic.target_object.value == 3


def test_inc_target_rejects_empty_missing_and_blocked_leaf_addresses() -> None:
    obj = pet_object_from_int(60)

    empty = inc_target(obj, ())
    missing = inc_target(obj, (7,))
    blocked = inc_target(obj, (3, 2))

    assert empty.valid is False
    assert empty.reason == "empty-address-does-not-select-root"

    assert missing.valid is False
    assert missing.reason == "address-missing"

    assert blocked.valid is False
    assert blocked.reason == "address-blocked-at-leaf"


def test_dec_target_accepts_composite_selected_root_and_rejects_atomic_leaf() -> None:
    obj = pet_object_from_int(60)

    composite = dec_target(obj, (2,))
    atomic = dec_target(obj, (3,))

    assert composite.valid is True
    assert composite.reason == "dec-target-valid"
    assert composite.target_object is not None
    assert composite.target_object.value == 4

    assert atomic.valid is False
    assert atomic.reason == "selected-object-is-atomic-leaf"
    assert atomic.target_object is not None
    assert atomic.target_object.value == 3


def test_resolve_operator_target_dispatches_all_operators() -> None:
    obj = pet_object_from_int(60)

    assert resolve_operator_target(obj, "NEW", (), 7).reason == "new-target-valid"
    assert resolve_operator_target(obj, "DROP", (), 5).reason == "drop-target-valid"
    assert resolve_operator_target(obj, "INC", (2,)).reason == "inc-target-valid"
    assert resolve_operator_target(obj, "DEC", (2,)).reason == "dec-target-valid"


def test_resolve_operator_target_rejects_bad_argument_shape() -> None:
    obj = pet_object_from_int(60)

    with pytest.raises(ValueError, match="NEW requires argument q"):
        resolve_operator_target(obj, "NEW", ())

    with pytest.raises(ValueError, match="DROP requires argument p"):
        resolve_operator_target(obj, "DROP", ())

    with pytest.raises(ValueError, match="INC does not accept an argument"):
        resolve_operator_target(obj, "INC", (2,), 7)

    with pytest.raises(ValueError, match="DEC does not accept an argument"):
        resolve_operator_target(obj, "DEC", (2,), 7)


def test_operator_target_serializes_selected_object() -> None:
    obj = pet_object_from_int(60)

    payload = new_target(obj, (), 7).to_dict()

    assert payload["op"] == "NEW"
    assert payload["axis"] == "X"
    assert payload["target_kind"] == "parent-support"
    assert payload["address"] == []
    assert payload["argument"] == 7
    assert payload["valid"] is True
    assert payload["reason"] == "new-target-valid"
    assert payload["address_resolution"] == "valid"
    assert payload["target_object"]["value"] == 60
