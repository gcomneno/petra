"""Explore shape(k^n) with struct/destruct (T01)."""

from __future__ import annotations

import argparse

from resolver import int_to_shape
from resolver.notation import to_mother_notation
from resolver.struct_destruct import destruct, struct


def esplora(k: int, n: int) -> None:
    kn = k ** n
    s = int_to_shape(kn)
    print(f"k = {k}, n = {n}, k^n = {kn}")
    print(f"shape(k)     = {to_mother_notation(int_to_shape(k))}")
    print(f"shape(k^n)   = {to_mother_notation(s)}")
    print()

    triples = destruct(s)
    print(f"destruct restituisce {len(triples)} casi:")
    for piece, rest, kind in sorted(triples, key=lambda t: (t[2], to_mother_notation(t[1]))):
        print(f"   [{kind}]")
        print(f"      piece: {to_mother_notation(piece)}")
        print(f"      rest : {to_mother_notation(rest)}")
        # verifica struct inversa
        ricomposto = struct(rest, piece)
        ok = s in ricomposto
        print(f"      struct(rest, piece) contiene shape(k^n)? {ok}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs", nargs="+", default=["12,3", "30,2", "30,3", "6,4"])
    args = parser.parse_args()
    for pair in args.pairs:
        k, n = pair.split(",")
        esplora(int(k), int(n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
