"""Minimal command-line interface for the Resolver."""

from __future__ import annotations

import argparse
import json
import sys

from petra import (
    DefaultTarget,
    ExplicitTarget,
    ShapeSyntaxError,
    serialize_shape,
)

from .projection import PrimeKey
from .search import Path, ResolverError, Step, resolve


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resolver",
        description=(
            "Find a bounded shortest edit path between two "
            "canonical PETRA shapes."
        ),
    )
    parser.add_argument("source", help="source PETRA shape text")
    parser.add_argument("target", help="target PETRA shape text")
    parser.add_argument(
        "--max-depth",
        type=int,
        default=10,
        help="maximum number of steps (default: 10)",
    )
    parser.add_argument(
        "--max-nodes",
        type=int,
        default=20,
        help="maximum node count per shape (default: 20)",
    )
    parser.add_argument(
        "--max-visited",
        type=int,
        default=1000,
        help="maximum distinct shapes explored (default: 1000)",
    )
    parser.add_argument(
        "--key-json",
        default=None,
        help=(
            "optional JSON object mapping addresses to primes, "
            'e.g. \'{"@/0":2,"@/1":3}\''
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit a single compact JSON document",
    )
    return parser


def _parse_key_json(text: str) -> PrimeKey:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise ResolverError(f"key-json is not valid JSON: {error}") from None

    if not isinstance(data, dict):
        raise ResolverError("key-json must be a JSON object")

    assignments: dict[tuple[int, ...], int] = {}
    for address_text, prime in data.items():
        address = _parse_key_address(address_text)
        assignments[address] = prime

    return PrimeKey(assignments)


def _parse_key_address(text: str) -> tuple[int, ...]:
    if text in {"@/", "@"}:
        return ()
    if not text.startswith("@/"):
        raise ResolverError(f"invalid key address: {text}")
    parts = text[2:].split("/")
    try:
        return tuple(int(part) for part in parts)
    except ValueError:
        raise ResolverError(f"invalid key address: {text}") from None


def _target_data(
    target: DefaultTarget | ExplicitTarget,
) -> dict[str, str]:
    if isinstance(target, DefaultTarget):
        return {"mode": "default"}
    return {
        "mode": "explicit",
        "address": str(target.address),
    }


def _step_data(step: Step) -> dict[str, object]:
    return {
        "operator": step.operator.value,
        "invocation_target": _target_data(step.invocation_target),
        "before_shape": serialize_shape(step.before_shape),
        "after_shape": serialize_shape(step.after_shape),
        "value_before": step.value_before,
        "value_after": step.value_after,
    }


def _path_data(path: Path) -> dict[str, object]:
    return {
        "schema": "resolver.path.v1",
        "source": serialize_shape(path.source),
        "target": serialize_shape(path.target),
        "length": path.length,
        "value_source": path.value_source,
        "value_target": path.value_target,
        "steps": [_step_data(step) for step in path.steps],
    }


def _path_has_values(path: Path) -> bool:
    if path.value_source is not None or path.value_target is not None:
        return True
    return any(
        step.value_before is not None or step.value_after is not None
        for step in path.steps
    )


def _format_value(value: int | None) -> str:
    if value is None:
        return "?"
    try:
        return str(value)
    except ValueError:
        return "<too-large>"


def _print_human(path: Path) -> None:
    has_values = _path_has_values(path)

    def annotated(shape_text: str, value: int | None) -> str:
        if not has_values:
            return shape_text
        return f"{shape_text} [{_format_value(value)}]"

    print(
        f"source = {annotated(serialize_shape(path.source), path.value_source)}"
    )
    print(
        f"target = {annotated(serialize_shape(path.target), path.value_target)}"
    )
    print(f"length = {path.length}")

    for index, step in enumerate(path.steps, start=1):
        target = step.invocation_target
        address = "default" if isinstance(target, DefaultTarget) else str(target.address)

        line = (
            f"{index}. {step.operator.value} {address}"
            f" -> {serialize_shape(step.after_shape)}"
        )
        if has_values:
            line += (
                f"  [{_format_value(step.value_before)}"
                f" -> {_format_value(step.value_after)}]"
            )
        print(line)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        key = _parse_key_json(args.key_json) if args.key_json is not None else None
        path = resolve(
            args.source,
            args.target,
            max_depth=args.max_depth,
            max_nodes=args.max_nodes,
            max_visited=args.max_visited,
            key=key,
        )
    except (ResolverError, ShapeSyntaxError) as error:
        print(f"resolver: {error}", file=sys.stderr)
        return 1

    if args.json:
        print(
            json.dumps(
                _path_data(path),
                sort_keys=True,
                separators=(",", ":"),
            )
        )
    else:
        _print_human(path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
