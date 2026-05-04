#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import re
import sys
from itertools import combinations, product
from typing import Iterable, List, Tuple


def factor_exponents(n: int) -> List[int]:
    exponents: List[int] = []
    m = n
    count = 0
    while m % 2 == 0:
        count += 1
        m //= 2
    if count:
        exponents.append(count)
    p = 3
    while p * p <= m:
        count = 0
        while m % p == 0:
            count += 1
            m //= p
        if count:
            exponents.append(count)
        p += 2
    if m > 1:
        exponents.append(1)
    exponents.sort(reverse=True)
    return exponents


def pet_profile(n: int) -> Tuple[int, ...]:
    exponents = factor_exponents(n)
    if not exponents:
        return tuple()
    h = exponents[0]
    profile = []
    for level in range(1, h + 1):
        profile.append(sum(1 for e in exponents if e >= level))
    return tuple(profile)


_PROFILE_RE = re.compile(r"\d+")


def parse_profile(raw: str) -> Tuple[int, ...]:
    values = [int(x) for x in _PROFILE_RE.findall(raw)]
    if not values:
        raise argparse.ArgumentTypeError(
            f"Profilo PET non valido: {raw!r}. Esempi validi: '[2,1]' oppure '2,1'"
        )
    return tuple(values)


def members_in_family(start: int, end: int, profile: Tuple[int, ...]) -> List[int]:
    return [n for n in range(start, end + 1) if pet_profile(n) == profile]


def unique_cross_pairs(left: Iterable[int], right: Iterable[int]) -> List[Tuple[int, int]]:
    seen = set()
    pairs: List[Tuple[int, int]] = []
    for a, b in product(left, right):
        if a == b:
            continue
        pair = (a, b) if a < b else (b, a)
        if pair not in seen:
            seen.add(pair)
            pairs.append(pair)
    pairs.sort()
    return pairs


def same_family_pairs(values: List[int]) -> List[Tuple[int, int]]:
    return list(combinations(values, 2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Calcola tutte le combinazioni senza ripetizione tra i membri di due famiglie PET "
            "in un intervallo dato."
        )
    )
    parser.add_argument("start", type=int, help="Inizio intervallo (incluso)")
    parser.add_argument("end", type=int, help="Fine intervallo (incluso)")
    parser.add_argument("--family-a", required=True, type=parse_profile, help="Primo profilo PET")
    parser.add_argument("--family-b", required=True, type=parse_profile, help="Secondo profilo PET")
    parser.add_argument(
        "--count-only",
        action="store_true",
        help="Stampa solo il numero totale di combinazioni",
    )
    parser.add_argument(
        "--show-members",
        action="store_true",
        help="Mostra anche i membri delle due famiglie su stderr",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.start < 2 or args.end < 2:
        print("Errore: l'intervallo deve partire da almeno 2.", file=sys.stderr)
        return 2
    if args.start > args.end:
        print("Errore: start non può essere maggiore di end.", file=sys.stderr)
        return 2

    family_a = members_in_family(args.start, args.end, args.family_a)
    family_b = members_in_family(args.start, args.end, args.family_b)

    if args.family_a == args.family_b:
        pairs = same_family_pairs(family_a)
    else:
        pairs = unique_cross_pairs(family_a, family_b)

    if args.show_members:
        print(f"Famiglia A {list(args.family_a)} -> {family_a}", file=sys.stderr)
        print(f"Famiglia B {list(args.family_b)} -> {family_b}", file=sys.stderr)

    if args.count_only:
        print(len(pairs))
        return 0

    for a, b in pairs:
        print(f"[{a}, {b}]")

    print(f"\nTotale combinazioni: {len(pairs)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
