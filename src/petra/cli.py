"""Minimal PETRA command-line adapter."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from typing import TextIO

from .operators import (
    apply_graft,
    apply_prune,
    apply_shed,
    apply_sprout,
)
from .model import PetraShape
from .results import (
    FailedResult,
    InvocationTarget,
    Operator,
    OperatorResult,
)
from .serialization import (
    InvocationSyntaxError,
    ShapeSyntaxError,
    parse_invocation_json,
    parse_shape,
    serialize_result,
)


_APPLY_OPERATOR: dict[
    Operator,
    Callable[[PetraShape, InvocationTarget], OperatorResult],
] = {
    Operator.SPROUT: apply_sprout,
    Operator.SHED: apply_shed,
    Operator.GRAFT: apply_graft,
    Operator.PRUNE: apply_prune,
}


def main(argv: Sequence[str] | None = None) -> int:
    """Run one PETRA operator invocation from canonical transport text."""

    return _main(
        sys.argv[1:] if argv is None else argv,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


def _main(
    argv: Sequence[str],
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    parser = argparse.ArgumentParser(
        prog="petra",
        description=(
            "Apply one canonical PETRA operator invocation to one "
            "canonical PETRA shape."
        ),
    )
    parser.add_argument("shape_text")
    parser.add_argument("invocation_json")
    args = parser.parse_args(argv)

    try:
        shape = parse_shape(args.shape_text)
    except ShapeSyntaxError as error:
        print(f"petra: {error.reason}", file=stderr)
        return 2
    except ValueError:
        print("petra: shape-invalid", file=stderr)
        return 2

    try:
        operator, target = parse_invocation_json(args.invocation_json)
    except InvocationSyntaxError as error:
        result = FailedResult(
            operator=error.operator,
            invocation_target=None,
            before_shape=shape,
            reason=error.reason,
        )
        print(serialize_result(result), file=stdout)
        return 1

    result = _APPLY_OPERATOR[operator](shape, target)
    print(serialize_result(result), file=stdout)
    return 0 if result.status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
