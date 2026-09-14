"""Tests for the Resolver path verifier."""

from __future__ import annotations

import pytest

from petra import DefaultTarget, ExplicitTarget, Operator, parse_shape
from resolver import (
    VerifyError,
    VerifyStep,
    verify_path,
)


# ---------------------------------------------------------------------------
# Valid and minimal
# ---------------------------------------------------------------------------


def test_leaf_to_singleton_one_step() -> None:
    result = verify_path(
        "1",
        "C(r0^1)",
        [{"operator": "SPROUT", "target": {"mode": "default"}}],
    )
    assert result.valid is True
    assert result.minimal is True
    assert result.expected_length == 1
    assert result.reason == "valid-and-minimal"


def test_two_step_tower_path() -> None:
    steps = [
        {"operator": "SPROUT", "target": {"mode": "default"}},
        {"operator": "GRAFT", "target": {"mode": "default"}},
    ]
    result = verify_path("1", "C(r0^C(r0^1))", steps)
    assert result.valid is True
    assert result.minimal is True
    assert result.expected_length == 2


def test_explicit_target_step() -> None:
    steps = [
        {
            "operator": "GRAFT",
            "target": {"mode": "explicit", "address": "@/0/^"},
        }
    ]
    result = verify_path(
        "C(r0^1,r1^C(r0^1))",
        "C(r0^C(r0^1),r1^C(r0^1))",
        steps,
    )
    assert result.valid is True
    assert result.minimal is True
    assert result.expected_length == 1


def test_verify_accepts_verify_step_objects() -> None:
    steps = [
        VerifyStep(
            operator=Operator.SPROUT,
            invocation_target=DefaultTarget(),
        )
    ]
    result = verify_path("1", "C(r0^1)", steps)
    assert result.valid is True


def test_verify_step_with_explicit_address_object() -> None:
    from petra import parse_address

    steps = [
        VerifyStep(
            operator=Operator.GRAFT,
            invocation_target=ExplicitTarget(
                parse_address("@/0/^")
            ),
        )
    ]
    result = verify_path("C(r0^1)", "C(r0^C(r0^1))", steps)
    assert result.valid is True
    assert result.minimal is True


# ---------------------------------------------------------------------------
# Valid but suboptimal
# ---------------------------------------------------------------------------


def test_suboptimal_roundtrip() -> None:
    steps = [
        {"operator": "SPROUT", "target": {"mode": "default"}},
        {"operator": "SPROUT", "target": {"mode": "default"}},
        {"operator": "SHED", "target": {"mode": "default"}},
    ]
    result = verify_path("1", "C(r0^1)", steps)
    assert result.valid is True
    assert result.minimal is False
    assert result.expected_length == 1
    assert result.reason == "valid-but-suboptimal"


def test_skip_minimal_check() -> None:
    steps = [
        {"operator": "SPROUT", "target": {"mode": "default"}},
    ]
    result = verify_path(
        "1",
        "C(r0^1)",
        steps,
        check_minimal=False,
    )
    assert result.valid is True
    assert result.minimal is None
    assert result.expected_length is None
    assert result.reason == "valid"


def test_precomputed_min_distance() -> None:
    steps = [
        {"operator": "SPROUT", "target": {"mode": "default"}},
    ]
    result = verify_path(
        "1",
        "C(r0^1)",
        steps,
        min_distance=1,
    )
    assert result.valid is True
    assert result.minimal is True
    assert result.expected_length == 1


# ---------------------------------------------------------------------------
# Invalid steps
# ---------------------------------------------------------------------------


def test_illegal_first_step() -> None:
    steps = [
        {"operator": "GRAFT", "target": {"mode": "default"}},
    ]
    result = verify_path("1", "C(r0^1,r1^1)", steps)
    assert result.valid is False
    assert result.reason == "invalid-step"
    assert result.failed_step is not None
    assert result.failed_step.index == 0
    assert result.failed_step.operator is Operator.GRAFT


def test_illegal_second_step() -> None:
    steps = [
        {"operator": "SPROUT", "target": {"mode": "default"}},
        {"operator": "GRAFT", "target": {"mode": "explicit", "address": "@/9/^"}},
    ]
    result = verify_path("1", "C(r0^1,r1^1)", steps)
    assert result.valid is False
    assert result.reason == "invalid-step"
    assert result.failed_step is not None
    assert result.failed_step.index == 1


def test_repeated_operator_when_shape_cannot_support() -> None:
    steps = [
        {"operator": "GRAFT", "target": {"mode": "default"}},
        {"operator": "GRAFT", "target": {"mode": "default"}},
    ]
    result = verify_path("1", "C(r0^C(r0^C(r0^1)))", steps)
    assert result.valid is False
    assert result.reason == "invalid-step"
    assert result.failed_step is not None
    assert result.failed_step.index == 0


# ---------------------------------------------------------------------------
# Target not reached
# ---------------------------------------------------------------------------


def test_target_not_reached() -> None:
    steps = [
        {"operator": "SPROUT", "target": {"mode": "default"}},
    ]
    result = verify_path("1", "C(r0^1,r1^1,r2^1)", steps)
    assert result.valid is False
    assert result.reason == "target-not-reached"
    assert result.final_shape == parse_shape("C(r0^1)")
    assert result.failed_step is None


def test_empty_steps_different_shapes() -> None:
    result = verify_path("1", "C(r0^1)", [])
    assert result.valid is False
    assert result.reason == "target-not-reached"


def test_empty_steps_identical_shapes() -> None:
    result = verify_path("C(r0^1)", "C(r0^1)", [])
    assert result.valid is True
    assert result.minimal is True
    assert result.expected_length == 0


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


def test_invalid_operator_name() -> None:
    with pytest.raises(VerifyError):
        verify_path(
            "1",
            "C(r0^1)",
            [{"operator": "INVALID", "target": {"mode": "default"}}],
        )


def test_missing_target_key() -> None:
    with pytest.raises(VerifyError):
        verify_path(
            "1",
            "C(r0^1)",
            [{"operator": "SPROUT"}],
        )


def test_unknown_target_mode() -> None:
    with pytest.raises(VerifyError):
        verify_path(
            "1",
            "C(r0^1)",
            [{"operator": "SPROUT", "target": {"mode": "weird"}}],
        )


def test_missing_explicit_address() -> None:
    with pytest.raises(VerifyError):
        verify_path(
            "1",
            "C(r0^1)",
            [{"operator": "SPROUT", "target": {"mode": "explicit"}}],
        )


def test_invalid_explicit_address() -> None:
    with pytest.raises(VerifyError):
        verify_path(
            "1",
            "C(r0^1)",
            [
                {
                    "operator": "SPROUT",
                    "target": {"mode": "explicit", "address": "garbage"},
                }
            ],
        )


def test_step_must_be_dict_or_verify_step() -> None:
    with pytest.raises(VerifyError):
        verify_path("1", "C(r0^1)", ["not a step"])  # type: ignore[list-item]
