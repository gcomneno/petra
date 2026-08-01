"""Atomic operator invocation targets, results, and witnesses for PETRA."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

try:
    from enum import StrEnum as _StrEnum
except ImportError:
    from enum import Enum

    class _StrEnum(str, Enum):
        """Python 3.10-compatible subset of enum.StrEnum."""

        def __str__(self) -> str:
            return str(self.value)

        def __format__(self, format_spec: str) -> str:
            return format(self.value, format_spec)

from .addresses import (
    Address,
    AddressError,
    ResolvedAnchor,
    ResolvedSlot,
    ResolvedTerm,
    resolve_address,
)
from .model import PetraShape, validate_shape


class Operator(_StrEnum):
    """One canonical PETRA structural operator."""

    SPROUT = "SPROUT"
    SHED = "SHED"
    GRAFT = "GRAFT"
    PRUNE = "PRUNE"


@dataclass(frozen=True)
class DefaultTarget:
    """A normalized invocation using default target selection."""

    @property
    def mode(self) -> str:
        return "default"


@dataclass(frozen=True)
class ExplicitTarget:
    """A normalized invocation containing one canonical address."""

    address: Address

    def __post_init__(self) -> None:
        if not isinstance(self.address, Address):
            raise TypeError(
                "explicit target address must be an Address"
            )

    @property
    def mode(self) -> str:
        return "explicit"


InvocationTarget: TypeAlias = DefaultTarget | ExplicitTarget


@dataclass(frozen=True)
class AddressEffects:
    """The resolved pre-rewrite address and one result witness."""

    target_address: Address
    witness_address: Address

    def __post_init__(self) -> None:
        if not isinstance(self.target_address, Address):
            raise TypeError(
                "target_address must be an Address"
            )

        if not isinstance(self.witness_address, Address):
            raise TypeError(
                "witness_address must be an Address"
            )


ResolvedTarget: TypeAlias = (
    ResolvedAnchor | ResolvedTerm | ResolvedSlot
)


_SUCCESS_REASONS = {
    Operator.SPROUT: "sprout-applied",
    Operator.SHED: "shed-applied",
    Operator.GRAFT: "graft-applied",
    Operator.PRUNE: "prune-applied",
}

_ADDRESS_TRAVERSAL_REASONS = frozenset(
    {
        "address-out-of-range",
        "address-crosses-leaf",
    }
)

_EXPLICIT_FAILURE_REASONS = {
    Operator.SPROUT: frozenset(
        {
            "sprout-target-not-container",
        }
    ),
    Operator.SHED: frozenset(
        {
            "shed-target-not-leaf",
        }
    ),
    Operator.GRAFT: frozenset(
        {
            "graft-target-not-slot",
            "graft-slot-already-materialized",
        }
    ),
    Operator.PRUNE: frozenset(
        {
            "prune-target-not-terminal-leaf",
            "prune-target-has-no-parent-relation",
            "prune-parent-not-singleton-exponent",
        }
    ),
}

_DEFAULT_FAILURE_REASONS = {
    Operator.SPROUT: frozenset(),
    Operator.SHED: frozenset(
        {
            "shed-no-eligible-top-level-leaf",
        }
    ),
    Operator.GRAFT: frozenset(
        {
            "graft-no-eligible-latent-slot",
        }
    ),
    Operator.PRUNE: frozenset(
        {
            "prune-no-eligible-terminal-leaf",
        }
    ),
}

_ALL_FAILURE_REASONS = frozenset(
    {
        "invocation-invalid",
        "address-malformed",
        *_ADDRESS_TRAVERSAL_REASONS,
        *(
            reason
            for reasons in _EXPLICIT_FAILURE_REASONS.values()
            for reason in reasons
        ),
        *(
            reason
            for reasons in _DEFAULT_FAILURE_REASONS.values()
            for reason in reasons
        ),
    }
)


def _require_operator(
    value: object,
    *,
    allow_none: bool,
) -> Operator | None:
    if value is None and allow_none:
        return None

    if not isinstance(value, Operator):
        raise TypeError("operator must be an Operator")

    return value


def _require_invocation_target(
    value: object,
    *,
    allow_none: bool,
) -> InvocationTarget | None:
    if value is None and allow_none:
        return None

    if not isinstance(
        value,
        (DefaultTarget, ExplicitTarget),
    ):
        raise TypeError(
            "invocation_target must be a normalized target"
        )

    return value


def _require_resolved_target(
    value: object,
) -> ResolvedTarget:
    if not isinstance(
        value,
        (ResolvedAnchor, ResolvedTerm, ResolvedSlot),
    ):
        raise TypeError(
            "resolved_target must be a PETRA resolution record"
        )

    return value


@dataclass(frozen=True)
class SuccessfulResult:
    """One atomic and internally consistent successful result."""

    operator: Operator
    invocation_target: InvocationTarget
    resolved_target: ResolvedTarget
    before_shape: PetraShape
    after_shape: PetraShape
    address_effects: AddressEffects

    def __post_init__(self) -> None:
        operator = _require_operator(
            self.operator,
            allow_none=False,
        )
        invocation_target = _require_invocation_target(
            self.invocation_target,
            allow_none=False,
        )
        resolved_target = _require_resolved_target(
            self.resolved_target
        )

        if operator is None:
            raise AssertionError(
                "successful result operator cannot be None"
            )

        if invocation_target is None:
            raise AssertionError(
                "successful result target cannot be None"
            )

        validate_shape(self.before_shape)
        validate_shape(self.after_shape)

        if not isinstance(self.address_effects, AddressEffects):
            raise TypeError(
                "address_effects must be AddressEffects"
            )

        target_address = resolved_target.address

        if (
            self.address_effects.target_address
            != target_address
        ):
            raise ValueError(
                "address effects target does not match "
                "the resolved target"
            )

        if (
            isinstance(invocation_target, ExplicitTarget)
            and invocation_target.address != target_address
        ):
            raise ValueError(
                "explicit target does not match "
                "the resolved target"
            )

        try:
            expected_target = resolve_address(
                self.before_shape,
                target_address,
            )
        except AddressError as error:
            raise ValueError(
                "resolved target does not resolve "
                "in before_shape"
            ) from error

        if expected_target != resolved_target:
            raise ValueError(
                "resolved target does not belong "
                "to before_shape"
            )

        try:
            resolve_address(
                self.after_shape,
                self.address_effects.witness_address,
            )
        except AddressError as error:
            raise ValueError(
                "witness address does not resolve "
                "in after_shape"
            ) from error

    @property
    def schema(self) -> str:
        return "petra.operator-result.v1"

    @property
    def status(self) -> str:
        return "ok"

    @property
    def reason(self) -> str:
        return _SUCCESS_REASONS[self.operator]


@dataclass(frozen=True)
class FailedResult:
    """One failed invocation with no post-rewrite state."""

    operator: Operator | None
    invocation_target: InvocationTarget | None
    before_shape: PetraShape
    reason: str

    def __post_init__(self) -> None:
        operator = _require_operator(
            self.operator,
            allow_none=True,
        )
        invocation_target = _require_invocation_target(
            self.invocation_target,
            allow_none=True,
        )

        validate_shape(self.before_shape)

        if not isinstance(self.reason, str):
            raise TypeError(
                "failure reason must be a str"
            )

        if self.reason not in _ALL_FAILURE_REASONS:
            raise ValueError(
                f"unknown PETRA failure reason: {self.reason}"
            )

        if self.reason == "invocation-invalid":
            return

        if operator is None:
            raise ValueError(
                "this failure reason requires "
                "a normalized operator"
            )

        if self.reason == "address-malformed":
            if invocation_target is not None:
                raise ValueError(
                    "address-malformed cannot contain "
                    "a normalized invocation target"
                )
            return

        if self.reason in _ADDRESS_TRAVERSAL_REASONS:
            if not isinstance(
                invocation_target,
                ExplicitTarget,
            ):
                raise ValueError(
                    "address traversal failures require "
                    "an explicit target"
                )
            return

        if self.reason in _EXPLICIT_FAILURE_REASONS[operator]:
            if not isinstance(
                invocation_target,
                ExplicitTarget,
            ):
                raise ValueError(
                    "this operator failure requires "
                    "an explicit target"
                )
            return

        if self.reason in _DEFAULT_FAILURE_REASONS[operator]:
            if not isinstance(
                invocation_target,
                DefaultTarget,
            ):
                raise ValueError(
                    "this no-eligible failure requires "
                    "the default target"
                )
            return

        raise ValueError(
            "failure reason does not belong "
            "to the normalized operator"
        )

    @property
    def schema(self) -> str:
        return "petra.operator-result.v1"

    @property
    def status(self) -> str:
        return "failed"


OperatorResult: TypeAlias = SuccessfulResult | FailedResult


__all__ = [
    "AddressEffects",
    "DefaultTarget",
    "ExplicitTarget",
    "FailedResult",
    "InvocationTarget",
    "Operator",
    "OperatorResult",
    "SuccessfulResult",
]
