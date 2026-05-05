#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.research.pet_shape_algebra import (
    normalize_shape,
    shape_closure,
    shape_gamma,
)


CLAIM = "backbone closure basis only; this does not factor N and does not reconstruct PET(N)"


@dataclass(frozen=True)
class BasisRow:
    order: int
    depth: int
    backbone_gamma: int
    gamma_count: int
    gamma_basis: tuple[int, ...]


def flat_backbone_shape(order: int):
    return normalize_shape(tuple(() for _ in range(order)))


def closure_gamma_basis(order: int, depth: int) -> BasisRow:
    root = flat_backbone_shape(order)
    backbone_gamma = shape_gamma(root)

    gammas: set[int] = set()
    for shape in shape_closure(root, depth):
        if shape == ():
            continue
        try:
            gammas.add(shape_gamma(shape))
        except ValueError:
            continue

    basis = tuple(sorted(gammas))

    return BasisRow(
        order=order,
        depth=depth,
        backbone_gamma=backbone_gamma,
        gamma_count=len(basis),
        gamma_basis=basis,
    )


def print_tsv(rows: list[BasisRow]) -> None:
    print(
        "\t".join(
            (
                "order",
                "depth",
                "backbone_gamma",
                "gamma_count",
                "gamma_basis",
                "claim",
            )
        )
    )

    for row in rows:
        print(
            "\t".join(
                (
                    str(row.order),
                    str(row.depth),
                    str(row.backbone_gamma),
                    str(row.gamma_count),
                    ",".join(str(gamma) for gamma in row.gamma_basis),
                    CLAIM,
                )
            )
        )


def parse_orders(raw: str) -> tuple[int, ...]:
    orders: list[int] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        order = int(item)
        if order < 1:
            raise argparse.ArgumentTypeError("--orders expects positive integers")
        orders.append(order)

    if not orders:
        raise argparse.ArgumentTypeError("--orders must contain at least one order")

    return tuple(sorted(set(orders)))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate PET-native target bases from shallow flat-backbone shape closures."
    )
    parser.add_argument(
        "--orders",
        default="1,2,3,4,5",
        help="Comma-separated flat backbone orders. Default: 1,2,3,4,5",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=2,
        help="Shape closure depth. Default: 2",
    )
    args = parser.parse_args()

    if args.depth < 0:
        raise SystemExit("--depth must be >= 0")

    rows = [
        closure_gamma_basis(order=order, depth=args.depth)
        for order in parse_orders(args.orders)
    ]
    print_tsv(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
