"""Reduction profile of 3n+k maps in PETRA shape space (P2)."""

from __future__ import annotations

import argparse

from petra import node_count
from resolver import int_to_shape


def step(n: int, k: int) -> int:
    """One shortcut step of 3n+k (k odd): halve if even, else 3n+k."""
    if n % 2 == 0:
        return n // 2
    return 3 * n + k


def trajectory(n0: int, k: int, bound: int) -> list[int]:
    """Trajectory until a cycle is reached or bound is exhausted."""
    seen: set[int] = {n0}
    out: list[int] = [n0]
    n = n0
    for _ in range(bound):
        n = step(n, k)
        if n in seen:
            out.append(n)
            break
        seen.add(n)
        out.append(n)
    return out


def profile(n0: int, k: int, bound: int) -> dict[str, float]:
    traj = trajectory(n0, k, bound)
    red = exp = stab = 0
    for a, b in zip(traj, traj[1:]):
        na = node_count(int_to_shape(a))
        nb = node_count(int_to_shape(b))
        if nb < na:
            red += 1
        elif nb > na:
            exp += 1
        else:
            stab += 1
    total = red + exp + stab
    if total == 0:
        return {"steps": 0, "red": 0.0, "exp": 0.0, "stab": 0.0}
    return {
        "steps": total,
        "red": 100 * red / total,
        "exp": 100 * exp / total,
        "stab": 100 * stab / total,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ks", type=int, nargs="+", default=[1, 3, 5, 7, 9, 11])
    parser.add_argument("--starts", type=int, nargs="+", default=[27, 97, 871])
    parser.add_argument("--bound", type=int, default=2000)
    args = parser.parse_args()

    print(f"{'k':>3} {'n0':>8} {'steps':>6} {'red%':>7} {'exp%':>7} {'stab%':>7}")
    print("-" * 45)
    for k in args.ks:
        for n0 in args.starts:
            p = profile(n0, k, args.bound)
            print(
                f"{k:>3} {n0:>8} {p['steps']:>6.0f} "
                f"{p['red']:>7.1f} {p['exp']:>7.1f} {p['stab']:>7.1f}"
            )
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
