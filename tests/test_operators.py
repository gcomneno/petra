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


def test_pet_one_is_generative_empty_root() -> None:
    obj = pet_object_from_int(1)

    assert obj.value == 1
    assert obj.is_root is True
    assert obj.is_composite is True
    assert obj.children == ()
    assert obj.structural_signature() == ()


def test_new_target_accepts_fresh_prime_at_empty_unit_root() -> None:
    from pet import apply_operator_by_value

    obj = pet_object_from_int(1)

    target = new_target(obj, (), 2)
    result = apply_operator_by_value(obj, "NEW", (), 2)

    assert target.valid is True
    assert target.reason == "new-target-valid"
    assert target.target_object is obj

    assert result.valid is True
    assert result.reason == "new-applied-by-value"
    assert result.before_value == 1
    assert result.after_value == 2
    assert result.after_object is not None
    assert result.after_object.value == 2


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


def test_apply_operator_by_value_applies_root_new_and_drop() -> None:
    from pet import apply_operator_by_value

    obj = pet_object_from_int(60)

    new_result = apply_operator_by_value(obj, "NEW", (), 7)
    drop_result = apply_operator_by_value(obj, "DROP", (), 5)

    assert new_result.valid is True
    assert new_result.reason == "new-applied-by-value"
    assert new_result.before_value == 60
    assert new_result.after_value == 420
    assert new_result.after_object is not None
    assert new_result.after_object.value == 420

    assert drop_result.valid is True
    assert drop_result.reason == "drop-applied-by-value"
    assert drop_result.before_value == 60
    assert drop_result.after_value == 12
    assert drop_result.after_object is not None
    assert drop_result.after_object.value == 12


def test_apply_operator_by_value_applies_top_level_inc_and_dec() -> None:
    from pet import apply_operator_by_value

    obj = pet_object_from_int(60)

    inc_result = apply_operator_by_value(obj, "INC", (2,))
    dec_result = apply_operator_by_value(obj, "DEC", (2,))

    assert inc_result.valid is True
    assert inc_result.reason == "inc-applied-by-value"
    assert inc_result.after_value == 120
    assert inc_result.after_object is not None
    assert inc_result.after_object.value == 120

    assert dec_result.valid is True
    assert dec_result.reason == "dec-applied-by-value"
    assert dec_result.after_value == 30
    assert dec_result.after_object is not None
    assert dec_result.after_object.value == 30


def test_apply_operator_by_value_applies_nested_inc_and_dec() -> None:
    from pet import apply_operator_by_value

    obj = pet_object_from_int(60)

    inc_result = apply_operator_by_value(obj, "INC", (2, 2))

    assert inc_result.valid is True
    assert inc_result.after_value == 240
    assert inc_result.after_object is not None
    assert inc_result.after_object.at((2,)).value == 16

    dec_result = apply_operator_by_value(inc_result.after_object, "DEC", (2, 2))

    assert dec_result.valid is True
    assert dec_result.after_value == 60
    assert dec_result.after_object is not None
    assert dec_result.after_object.value == 60


def test_apply_operator_by_value_applies_nested_new_and_drop() -> None:
    from pet import apply_operator_by_value

    obj = pet_object_from_int(60)

    new_result = apply_operator_by_value(obj, "NEW", (2,), 3)

    assert new_result.valid is True
    assert new_result.after_value == 960
    assert new_result.after_object is not None
    assert new_result.after_object.at((2,)).value == 64

    drop_result = apply_operator_by_value(new_result.after_object, "DROP", (2,), 3)

    assert drop_result.valid is True
    assert drop_result.after_value == 60
    assert drop_result.after_object is not None
    assert drop_result.after_object.value == 60


def test_apply_operator_by_value_returns_invalid_result_without_mutation() -> None:
    from pet import apply_operator_by_value

    obj = pet_object_from_int(60)

    result = apply_operator_by_value(obj, "DROP", (), 7)

    assert result.valid is False
    assert result.reason == "p-not-in-target-baseline"
    assert result.before_value == 60
    assert result.after_value is None
    assert result.after_object is None


def test_operator_application_serializes() -> None:
    from pet import apply_operator_by_value

    payload = apply_operator_by_value(pet_object_from_int(60), "NEW", (), 7).to_dict()

    assert payload["op"] == "NEW"
    assert payload["address"] == []
    assert payload["argument"] == 7
    assert payload["valid"] is True
    assert payload["reason"] == "new-applied-by-value"
    assert payload["before_value"] == 60
    assert payload["after_value"] == 420
    assert payload["target"]["reason"] == "new-target-valid"
    assert payload["before_object"]["value"] == 60
    assert payload["after_object"]["value"] == 420
