#!/usr/bin/env python3
"""Recursive construction of a target shape, single chain, height-first.

The current shape is transformed in place. Every step is a real struct
application to the current shape; there are no restarts.

Strategy: depth-first. At each container, process fathers one at a
time, from left to right. For each father:

1. append a new leaf father;
2. if the target father has a non-leaf exponent, recursively fill it
   completely before moving to the next father.

Only two elementary pieces are used: ○ and ○^(A).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field

from petra import Container, Leaf, PetraShape, Root, Term
from resolver import int_to_shape
from resolver.notation import to_mother_notation


# ---------------------------------------------------------------------------
# in-place transformations on a specific path
# ---------------------------------------------------------------------------


def _append_father_at(
    shape: PetraShape,
    path: tuple[int, ...],
    exponent: PetraShape,
) -> PetraShape:
    """Append a new father with `exponent` to the container at `path`."""

    if not path:
        if isinstance(shape, Leaf):
            return Container(
                terms=(Term(root=Root(0), exponent=exponent),)
            )
        assert isinstance(shape, Container)
        terms = list(shape.terms) + [
            Term(root=Root(0), exponent=exponent)
        ]
        rebuilt = tuple(
            Term(root=Root(i), exponent=t.exponent)
            for i, t in enumerate(terms)
        )
        return Container(terms=rebuilt)

    head, *rest = path
    assert isinstance(shape, Container)
    term = shape.terms[head]
    new_exponent = _append_father_at(term.exponent, tuple(rest), exponent)
    new_terms = tuple(
        Term(root=t.root, exponent=(new_exponent if i == head else t.exponent))
        for i, t in enumerate(shape.terms)
    )
    return Container(terms=new_terms)


# ---------------------------------------------------------------------------
# trace
# ---------------------------------------------------------------------------


@dataclass
class Trace:
    steps: list[tuple[str, PetraShape]] = field(default_factory=list)

    def add(self, label: str, shape: PetraShape) -> None:
        self.steps.append((label, shape))


# ---------------------------------------------------------------------------
# recursive builder: height-first
# ---------------------------------------------------------------------------


def fill(
    current: PetraShape,
    path: tuple[int, ...],
    target: PetraShape,
    trace: Trace,
    *,
    indent: int = 0,
    show_tree: bool = True,
    prefix: str = "",
) -> PetraShape:
    """Fill the leaf at `path` in `current` with content matching `target`.

    Height-first: each father is appended and completed before moving on
    to the next father.
    """

    pad = "  " * indent

    if isinstance(target, Leaf):
        if show_tree:
            print(f"{pad}{prefix}leaf ○")
        return current

    assert isinstance(target, Container)
    if show_tree:
        print(
            f"{pad}{prefix}container {to_mother_notation(target)} "
            f"with {len(target.terms)} father(s)"
        )

    for i, term in enumerate(target.terms):
        # 1. append a new leaf father at `path`
        current = _append_father_at(current, path, Leaf())
        label = f"append ○ at {'root' if not path else path}->{i}"
        trace.add(label, current)
        if show_tree:
            print(f"{pad}  father {i}: appended leaf")

        # 2. if the target father has a non-leaf exponent, fill it
        #    completely before moving to the next father
        if not isinstance(term.exponent, Leaf):
            current = fill(
                current,
                (*path, i),
                term.exponent,
                trace,
                indent=indent + 2,
                show_tree=show_tree,
                prefix=f"father {i}: ",
            )

    return current


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Recursive construction, single chain, height-first."
    )
    parser.add_argument("target_n", type=int)
    args = parser.parse_args(argv)

    target = int_to_shape(args.target_n)
    print(f"=== target: {to_mother_notation(target)} ===")
    print()

    print("--- recursion tree ---")
    trace = Trace()
    current = Leaf()
    trace.add("start", current)
    built = fill(current, (), target, trace)
    print()

    print("--- flat steps ---")
    for i, (label, shape) in enumerate(trace.steps):
        print(f"  step {i:>2}: {label:<30}  -> {to_mother_notation(shape)}")
    print()

    print(f"built:  {to_mother_notation(built)}")
    print(f"equals target? {built == target}")
    return 0 if built == target else 1


if __name__ == "__main__":
    sys.exit(main())
