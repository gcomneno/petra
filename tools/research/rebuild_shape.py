#!/usr/bin/env python3
"""BFS reconstruction of a target shape using struct only.

Given a target shape T and a finite set of elementary pieces X, search
for the shortest sequence of `struct(., X)` operations that produces T,
starting from the bare leaf ○.

Constraints:

- every intermediate shape must have `node_count` at most `max_nodes`;
- every elementary piece X must have `node_count` strictly less than
  `node_count(T)`;
- intermediate shapes are deduplicated; the first time a shape is
  reached, the shortest path to it is recorded.

The tool is analytical. It does not modify PETRA.
"""

from __future__ import annotations

import argparse
import sys
from collections import deque

from petra import Leaf, PetraShape, node_count
from resolver import int_to_shape
from resolver.notation import to_mother_notation
from resolver.struct_destruct import struct


def build_pieces(target_nodes: int, cap: int) -> list[PetraShape]:
    """Elementary pieces with node_count < target_nodes and <= cap."""

    pieces: list[PetraShape] = []
    for n in range(2, 200):
        s = int_to_shape(n)
        nc = node_count(s)
        if nc >= target_nodes:
            continue
        if nc > cap:
            continue
        pieces.append(s)
    # deduplicate by structure
    seen: set[PetraShape] = set()
    unique: list[PetraShape] = []
    for p in pieces:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique


def reconstruct(
    target: PetraShape,
    pieces: list[PetraShape],
    *,
    max_nodes: int,
    max_depth: int,
) -> list[tuple[str, PetraShape]] | None:
    """Return a shortest sequence of struct applications reaching target.

    Each step is `(piece_label, resulting_shape)`. The first element of
    the returned list is the empty step (the starting leaf).
    """

    start = Leaf()
    if start == target:
        return [("<start>", start)]

    # BFS
    queue: deque[PetraShape] = deque([start])
    came_from: dict[PetraShape, tuple[PetraShape, str] | None] = {start: None}
    depth: dict[PetraShape, int] = {start: 0}

    while queue:
        current = queue.popleft()
        d = depth[current]
        if d >= max_depth:
            continue
        for piece in pieces:
            for candidate in struct(current, piece):
                if node_count(candidate) > max_nodes:
                    continue
                if candidate in came_from:
                    continue
                came_from[candidate] = (current, to_mother_notation(piece))
                depth[candidate] = d + 1
                if candidate == target:
                    return _unroll(came_from, target)
                queue.append(candidate)
    return None


def _unroll(
    came_from: dict[PetraShape, tuple[PetraShape, str] | None],
    target: PetraShape,
) -> list[tuple[str, PetraShape]]:
    chain: list[tuple[str, PetraShape]] = []
    node: PetraShape | None = target
    while node is not None:
        entry = came_from[node]
        if entry is None:
            chain.append(("<start>", node))
            break
        parent, label = entry
        chain.append((label, node))
        node = parent
    chain.reverse()
    return chain


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="BFS reconstruction of a target shape using struct only."
    )
    parser.add_argument("target_n", type=int, help="integer whose shape is the target")
    parser.add_argument(
        "--max-nodes",
        type=int,
        default=None,
        help="max node_count for intermediate shapes (default: target nodes + 5)",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=4,
        help="max number of struct steps (default: 4)",
    )
    parser.add_argument(
        "--piece-cap",
        type=int,
        default=None,
        help="max node_count for elementary pieces (default: target nodes - 1)",
    )
    args = parser.parse_args(argv)

    target = int_to_shape(args.target_n)
    target_nodes = node_count(target)
    max_nodes = args.max_nodes if args.max_nodes is not None else target_nodes + 5
    piece_cap = args.piece_cap if args.piece_cap is not None else target_nodes - 1

    pieces = build_pieces(target_nodes, piece_cap)
    print(f"target: {to_mother_notation(target)}  (node_count={target_nodes})")
    print(f"pieces: {len(pieces)} elementary shapes with node_count <= {piece_cap}")
    print(f"max nodes: {max_nodes}   max depth: {args.max_depth}")
    print()

    chain = reconstruct(
        target, pieces, max_nodes=max_nodes, max_depth=args.max_depth
    )
    if chain is None:
        print("(no reconstruction found within the constraints)")
        return 1

    for i, (label, shape) in enumerate(chain):
        prefix = "" if i == 0 else f"struct(_, {label}) -> "
        print(f"  step {i}: {prefix}{to_mother_notation(shape)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
