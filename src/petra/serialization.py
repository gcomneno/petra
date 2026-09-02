"""Canonical serialization boundaries for PETRA."""

from __future__ import annotations

import json
from typing import Any

from .addresses import AddressError, parse_address, render_address
from .model import (
    Container,
    Leaf,
    PetraShape,
    Root,
    Term,
)
from .results import (
    AddressEffects,
    DefaultTarget,
    ExplicitTarget,
    FailedResult,
    InvocationTarget,
    Operator,
    OperatorResult,
    SuccessfulResult,
)


SHAPE_TEXT_MALFORMED = "shape-text-malformed"
INVOCATION_INVALID = "invocation-invalid"
ADDRESS_MALFORMED = "address-malformed"

_ASCII_WHITESPACE = frozenset(" \t\n\r\f\v")

# These fixed limits are normative; see docs/reference/SPEC.md section 1.5.
_MAX_INPUT_TEXT_LENGTH = 65_536
_MAX_NESTING_DEPTH = 2_048
_MAX_TOTAL_NODES = 10_001
_MAX_TERMS_PER_CONTAINER = 1_024
_MAX_ROOT_RANK_DIGITS = 4

_SHAPE_SERIALIZATION_LIMIT_EXCEEDED = (
    "shape-serialization-limit-exceeded"
)
_INVOCATION_SCHEMA = "petra.operator-invocation.v1"


class ShapeSyntaxError(ValueError):
    """A deterministic PETRA shape-text grammar failure."""

    def __init__(self, reason: str) -> None:
        if not isinstance(reason, str):
            raise TypeError("shape syntax reason must be a str")

        if reason != SHAPE_TEXT_MALFORMED:
            raise ValueError(
                f"unknown shape syntax reason: {reason}"
            )

        self.reason = reason
        super().__init__(reason)


class InvocationSyntaxError(ValueError):
    """A deterministic raw PETRA invocation boundary failure."""

    def __init__(
        self,
        reason: str,
        *,
        operator: Operator | None = None,
    ) -> None:
        if not isinstance(reason, str):
            raise TypeError("invocation syntax reason must be a str")
        if reason not in {INVOCATION_INVALID, ADDRESS_MALFORMED}:
            raise ValueError(
                f"unknown invocation syntax reason: {reason}"
            )
        if operator is not None and not isinstance(operator, Operator):
            raise TypeError("operator must be an Operator or None")
        if reason == INVOCATION_INVALID and operator is not None:
            raise ValueError(
                "invocation-invalid cannot carry a normalized operator"
            )

        self.reason = reason
        self.operator = operator
        super().__init__(reason)


class _InvalidJson(ValueError):
    """Internal strict-JSON rejection marker."""


class _ContainerFrame:
    """The partially parsed state of one open textual container."""

    __slots__ = ("terms", "pending_root")

    def __init__(self) -> None:
        self.terms: list[Term] = []
        self.pending_root: Root | None = None


class _Parser:
    """One bounded, iterative parse of PETRA shape text."""

    def __init__(self, text: str) -> None:
        self._text = text
        self._position = 0
        self._node_count = 0

    def parse(self) -> PetraShape:
        frames: list[_ContainerFrame] = []
        action = "shape"
        result: PetraShape | None = None

        while True:
            self._skip_whitespace()

            if action == "shape":
                current = self._current()
                if current == "1":
                    self._position += 1
                    self._reserve_node()
                    action, result = self._complete_shape(
                        Leaf(), frames, result
                    )
                    continue

                if current != "C":
                    self._malformed()

                self._position += 1
                self._skip_whitespace()
                if self._current() != "(":
                    self._malformed()
                self._position += 1

                if len(frames) >= _MAX_NESTING_DEPTH:
                    self._malformed()
                self._reserve_node()
                frames.append(_ContainerFrame())
                action = "term"
                continue

            if action == "term":
                if not frames:
                    self._malformed()
                frame = frames[-1]
                if len(frame.terms) >= _MAX_TERMS_PER_CONTAINER:
                    self._malformed()

                if self._current() != "r":
                    self._malformed()
                self._position += 1
                rank = self._parse_rank()

                self._skip_whitespace()
                if self._current() != "^":
                    self._malformed()
                self._position += 1
                # A term necessarily follows this complete root token. Reserve
                # its budget before allocating an arbitrarily nested exponent.
                self._reserve_node()
                frame.pending_root = Root(rank)
                action = "shape"
                continue

            if action == "delimiter":
                if not frames:
                    self._malformed()
                current = self._current()
                if current == ",":
                    self._position += 1
                    action = "term"
                    continue
                if current != ")":
                    self._malformed()

                self._position += 1
                frame = frames.pop()
                # A frame reaches this state only after a complete term.
                action, result = self._complete_shape(
                    Container(terms=tuple(frame.terms)), frames, result
                )
                continue

            if action == "done":
                if not self._at_end or result is None:
                    self._malformed()
                _validate_shape_for_serialization(result)
                return result

            self._malformed()

    @property
    def _at_end(self) -> bool:
        return self._position >= len(self._text)

    def _current(self) -> str | None:
        if self._at_end:
            return None
        return self._text[self._position]

    def _skip_whitespace(self) -> None:
        while (
            not self._at_end
            and self._text[self._position] in _ASCII_WHITESPACE
        ):
            self._position += 1

    def _parse_rank(self) -> int:
        current = self._current()

        if current is None or current < "0" or current > "9":
            self._malformed()

        rank = 0
        digit_count = 0
        leading_zero = current == "0"
        while current is not None and "0" <= current <= "9":
            if digit_count >= _MAX_ROOT_RANK_DIGITS:
                self._malformed()
            if leading_zero and digit_count:
                self._malformed()
            rank = (rank * 10) + (ord(current) - ord("0"))
            digit_count += 1
            self._position += 1
            current = self._current()

        return rank

    def _reserve_node(self) -> None:
        if self._node_count >= _MAX_TOTAL_NODES:
            self._malformed()
        self._node_count += 1

    def _complete_shape(
        self,
        shape: PetraShape,
        frames: list[_ContainerFrame],
        result: PetraShape | None,
    ) -> tuple[str, PetraShape | None]:
        if not frames:
            if result is not None:
                self._malformed()
            return "done", shape

        frame = frames[-1]
        if frame.pending_root is None:
            self._malformed()
        frame.terms.append(
            Term(root=frame.pending_root, exponent=shape)
        )
        frame.pending_root = None
        return "delimiter", result

    def _malformed(self) -> None:
        raise ShapeSyntaxError(SHAPE_TEXT_MALFORMED)


def parse_shape(value: object) -> PetraShape:
    """Parse one supported PETRA textual shape."""

    if not isinstance(value, str):
        raise ShapeSyntaxError(SHAPE_TEXT_MALFORMED)
    if str.__len__(value) > _MAX_INPUT_TEXT_LENGTH:
        raise ShapeSyntaxError(SHAPE_TEXT_MALFORMED)

    # Call the built-in implementation directly so a str subclass cannot
    # influence grammar recognition through an overridden string method.
    text = value if type(value) is str else str.__str__(value)
    if type(text) is not str:
        raise ShapeSyntaxError(SHAPE_TEXT_MALFORMED)

    return _Parser(text).parse()


def serialize_shape(shape: PetraShape) -> str:
    """Render one valid typed shape in canonical textual form."""

    _validate_shape_for_serialization(shape)

    chunks: list[str] = []
    stack: list[tuple[str, object, int]] = [("shape", shape, 0)]
    while stack:
        action, value, index = stack.pop()
        if action == "shape":
            if isinstance(value, Leaf):
                chunks.append("1")
                continue
            stack.append(("container", value, 0))
            continue

        container = value
        assert isinstance(container, Container)
        if index == len(container.terms):
            chunks.append(")")
            continue
        if index == 0:
            chunks.append("C(")
        else:
            chunks.append(",")
        term = container.terms[index]
        chunks.append(f"r{term.root.rank}^")
        stack.append(("container", container, index + 1))
        stack.append(("shape", term.exponent, 0))

    return "".join(chunks)


def parse_invocation_json(value: object) -> tuple[Operator, InvocationTarget]:
    """Parse one strict PETRA operator invocation JSON document."""

    if type(value) is not str:
        raise InvocationSyntaxError(INVOCATION_INVALID)

    try:
        payload = json.loads(
            value,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_json_constant,
        )
    except (json.JSONDecodeError, _InvalidJson, TypeError, ValueError):
        raise InvocationSyntaxError(INVOCATION_INVALID) from None

    if not isinstance(payload, dict) or set(payload) != {
        "schema",
        "operator",
        "target",
    }:
        raise InvocationSyntaxError(INVOCATION_INVALID)
    if payload["schema"] != _INVOCATION_SCHEMA:
        raise InvocationSyntaxError(INVOCATION_INVALID)

    try:
        operator = Operator(payload["operator"])
    except (TypeError, ValueError):
        raise InvocationSyntaxError(INVOCATION_INVALID) from None

    target = payload["target"]
    if not isinstance(target, dict) or "mode" not in target:
        raise InvocationSyntaxError(INVOCATION_INVALID)

    mode = target["mode"]
    if mode == "default":
        if set(target) != {"mode"}:
            raise InvocationSyntaxError(INVOCATION_INVALID)
        return operator, DefaultTarget()

    if mode != "explicit" or set(target) != {"mode", "address"}:
        raise InvocationSyntaxError(INVOCATION_INVALID)
    if type(target["address"]) is not str:
        raise InvocationSyntaxError(INVOCATION_INVALID)

    try:
        address = parse_address(target["address"])
    except AddressError as error:
        if error.reason == ADDRESS_MALFORMED:
            raise InvocationSyntaxError(
                ADDRESS_MALFORMED,
                operator=operator,
            ) from None
        raise AssertionError(
            "parsing an address must not produce traversal failures"
        ) from error

    return operator, ExplicitTarget(address)


def serialize_invocation(
    operator: Operator,
    invocation_target: InvocationTarget,
) -> str:
    """Serialize one normalized invocation as canonical compact JSON."""

    if not isinstance(operator, Operator):
        raise TypeError("operator must be an Operator")
    if not isinstance(invocation_target, (DefaultTarget, ExplicitTarget)):
        raise TypeError(
            "invocation_target must be a normalized target"
        )

    return _canonical_json(
        {
            "schema": _INVOCATION_SCHEMA,
            "operator": operator.value,
            "target": _invocation_target_data(invocation_target),
        }
    )


def serialize_result(result: OperatorResult) -> str:
    """Serialize one typed operator result as canonical compact JSON."""

    if isinstance(result, SuccessfulResult):
        payload: dict[str, Any] = {
            "schema": result.schema,
            "status": result.status,
            "operator": result.operator.value,
            "invocation_target": _invocation_target_data(
                result.invocation_target
            ),
            "resolved_target": {
                "kind": result.resolved_target.kind,
                "address": render_address(result.resolved_target.address),
            },
            "before_shape": serialize_shape(result.before_shape),
            "after_shape": serialize_shape(result.after_shape),
            "address_effects": _address_effects_data(
                result.address_effects
            ),
            "reason": result.reason,
        }
        return _canonical_json(payload)

    if isinstance(result, FailedResult):
        return _canonical_json(
            {
                "schema": result.schema,
                "status": result.status,
                "operator": (
                    None
                    if result.operator is None
                    else result.operator.value
                ),
                "invocation_target": (
                    None
                    if result.invocation_target is None
                    else _invocation_target_data(
                        result.invocation_target
                    )
                ),
                "before_shape": serialize_shape(result.before_shape),
                "reason": result.reason,
            }
        )

    raise TypeError("expected an OperatorResult")


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _InvalidJson("duplicate object key")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> Any:
    raise _InvalidJson(f"non-standard JSON constant: {value}")


def _canonical_json(payload: object) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )


def _invocation_target_data(
    invocation_target: InvocationTarget,
) -> dict[str, str]:
    if isinstance(invocation_target, DefaultTarget):
        return {"mode": "default"}

    assert isinstance(invocation_target, ExplicitTarget)
    return {
        "mode": "explicit",
        "address": render_address(invocation_target.address),
    }


def _address_effects_data(
    address_effects: AddressEffects,
) -> dict[str, str]:
    return {
        "target_address": render_address(address_effects.target_address),
        "witness_address": render_address(address_effects.witness_address),
    }


def _validate_shape_for_serialization(shape: PetraShape) -> None:
    """Validate canonical typed input and the serialization resource budget."""

    node_count = 0
    text_length = 0
    stack: list[tuple[object, int]] = [(shape, 0)]

    while stack:
        current, depth = stack.pop()
        if isinstance(current, Leaf):
            node_count = _next_node_count(node_count)
            text_length = _next_text_length(text_length, 1)
            continue

        if not isinstance(current, Container):
            raise TypeError("expected a PETRA Leaf or Container")
        if depth >= _MAX_NESTING_DEPTH:
            _raise_serialization_limit()
        if not isinstance(current.terms, tuple):
            raise TypeError("container terms must be a tuple")
        if not current.terms:
            raise ValueError("container terms must be non-empty")
        if len(current.terms) > _MAX_TERMS_PER_CONTAINER:
            _raise_serialization_limit()

        node_count = _next_node_count(node_count)
        text_length = _next_text_length(text_length, 3)
        for expected_rank, term in enumerate(current.terms):
            if not isinstance(term, Term):
                raise TypeError("container terms must contain only Term objects")
            if not isinstance(term.root, Root):
                raise TypeError("term root must be a Root")
            if type(term.root.rank) is not int:
                raise TypeError("root rank must be an int")
            if term.root.rank < 0:
                raise ValueError("root rank must be >= 0")

            rank_digits = _decimal_digit_count(term.root.rank)
            if rank_digits > _MAX_ROOT_RANK_DIGITS:
                _raise_serialization_limit()
            if term.root.rank != expected_rank:
                raise ValueError(
                    "non-canonical root rank: "
                    f"expected r{expected_rank}, got r{term.root.rank}"
                )

            node_count = _next_node_count(node_count)
            text_length = _next_text_length(
                text_length,
                rank_digits + 2 + (1 if expected_rank else 0),
            )

        for term in reversed(current.terms):
            stack.append((term.exponent, depth + 1))


def _next_node_count(node_count: int) -> int:
    if node_count >= _MAX_TOTAL_NODES:
        _raise_serialization_limit()
    return node_count + 1


def _next_text_length(text_length: int, addition: int) -> int:
    text_length += addition
    if text_length > _MAX_INPUT_TEXT_LENGTH:
        _raise_serialization_limit()
    return text_length


def _decimal_digit_count(rank: int) -> int:
    if rank == 0:
        return 1
    count = 0
    while rank:
        rank //= 10
        count += 1
    return count


def _raise_serialization_limit() -> None:
    raise ValueError(_SHAPE_SERIALIZATION_LIMIT_EXCEEDED)


__all__ = [
    "ADDRESS_MALFORMED",
    "INVOCATION_INVALID",
    "InvocationSyntaxError",
    "SHAPE_TEXT_MALFORMED",
    "ShapeSyntaxError",
    "parse_invocation_json",
    "parse_shape",
    "serialize_invocation",
    "serialize_result",
    "serialize_shape",
]
