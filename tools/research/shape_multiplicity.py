"""How many integers share a shape (P4)."""

from __future__ import annotations

import argparse
from collections import Counter

from resolver import int_to_shape
from resolver.notation import to_mother_notation


def run(N: int) -> tuple[Counter, int]:
    counter: Counter = Counter()
    for n in range(1, N + 1):
        counter[to_mother_notation(int_to_shape(n))] += 1
    return counter, N


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ns", type=int, nargs="+",
                        default=[100, 1000, 10000, 100000])
    args = parser.parse_args()

    for N in args.ns:
        counter, _ = run(N)
        counts = sorted(counter.values(), reverse=True)
        singletons = sum(1 for c in counter.values() if c == 1)
        max_shape = max(counter, key=counter.get)
        print(f"N = {N}")
        print(f"   distinct shapes: {len(counter)}")
        print(f"   shapes appearing once: {singletons}")
        print(f"   most frequent shape: {max_shape} (count = {counter[max_shape]})")
        print(f"   top 5 counts: {counts[:5]}")
        print(f"   bottom 5 counts: {counts[-5:]}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
