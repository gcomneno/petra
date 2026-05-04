#!/usr/bin/env python3
"""Stampa i numeri in un intervallo e il loro profilo PET.

Comportamento:
- con --profile: filtra i numeri che hanno quel profilo PET
- senza --profile: stampa tutti i numeri del range con il rispettivo profilo
- con --family-counts: stampa tutte le famiglie/profili presenti nel range con il loro conteggio
- con --family-members: stampa tutte le famiglie/profili presenti nel range con conteggio e membri

Definizione usata:
- se n = prod p_i^e_i
- profilo PET = [#{e_i >= 1}, #{e_i >= 2}, ...]

Esempi:
    python3 pet_profile_range_v4.py 2 90 --profile '[2]'
    python3 pet_profile_range_v4.py 2 20
    python3 pet_profile_range_v4.py 2 90 --family-counts
    python3 pet_profile_range_v4.py 2 90 --family-members
    python3 pet_profile_range_v4.py --start 2 --end 90 --count-only
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from typing import DefaultDict, Dict, List, Optional, Tuple


Profile = Tuple[int, ...]


def factorize(n: int) -> Dict[int, int]:
    """Ritorna la fattorizzazione prima di n come {primo: esponente}."""
    factors: Dict[int, int] = {}
    x = n

    while x % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        x //= 2

    d = 3
    while d * d <= x:
        while x % d == 0:
            factors[d] = factors.get(d, 0) + 1
            x //= d
        d += 2

    if x > 1:
        factors[x] = factors.get(x, 0) + 1

    return factors


def pet_profile(n: int) -> Profile:
    """Calcola il profilo PET di n."""
    exponents = sorted(factorize(n).values(), reverse=True)
    if not exponents:
        return tuple()

    h = max(exponents)
    return tuple(sum(1 for e in exponents if e >= level) for level in range(1, h + 1))


def parse_profile(text: str) -> Profile:
    """Accetta sia '[2,1]' sia '2,1'."""
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("profilo vuoto")

    parts = [p for p in re.split(r"[\[\],\s]+", cleaned) if p]
    if not parts:
        raise ValueError(f"profilo non valido: {text!r}")

    values = tuple(int(p) for p in parts)
    if any(v <= 0 for v in values):
        raise ValueError("il profilo deve contenere solo interi positivi")
    if list(values) != sorted(values, reverse=True):
        raise ValueError("il profilo deve essere non crescente, ad esempio [2,1]")
    return values


def format_profile(profile: Profile) -> str:
    return "[" + ", ".join(str(v) for v in profile) + "]"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Elenca i numeri in un intervallo con un dato profilo PET, "
            "oppure tutti i numeri del range con il rispettivo profilo."
        )
    )
    parser.add_argument("start_pos", nargs="?", type=int, help="inizio intervallo")
    parser.add_argument("end_pos", nargs="?", type=int, help="fine intervallo")
    parser.add_argument("--start", dest="start_opt", type=int, help="inizio intervallo")
    parser.add_argument("--end", dest="end_opt", type=int, help="fine intervallo")
    parser.add_argument(
        "--profile",
        default=None,
        help="profilo PET da cercare, es. '[2]' oppure '2,1'; se omesso mostra tutti i profili",
    )
    parser.add_argument(
        "--count-only",
        action="store_true",
        help="stampa solo il conteggio dei numeri emessi; in modalità famiglie stampa il numero di famiglie",
    )
    parser.add_argument(
        "--family-counts",
        action="store_true",
        help="stampa tutte le famiglie/profili presenti nel range con il loro conteggio",
    )
    parser.add_argument(
        "--family-members",
        action="store_true",
        help="stampa tutte le famiglie/profili presenti nel range con conteggio e lista dei membri",
    )
    return parser


def resolve_range(args: argparse.Namespace) -> Tuple[int, int]:
    start = args.start_opt if args.start_opt is not None else args.start_pos
    end = args.end_opt if args.end_opt is not None else args.end_pos

    if start is None or end is None:
        raise ValueError("devi indicare sia start sia end")
    if start > end:
        raise ValueError("start non può essere maggiore di end")
    if start < 2:
        raise ValueError("l'intervallo deve partire da almeno 2")

    return start, end


def sort_profiles_key(profile: Profile) -> Tuple[int, Profile]:
    """Ordina prima per lunghezza del profilo, poi lessicograficamente."""
    return (len(profile), profile)



def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    mode_count = int(bool(args.family_counts)) + int(bool(args.family_members))
    if mode_count > 1:
        parser.error("--family-counts e --family-members non possono essere usati insieme")
    if (args.family_counts or args.family_members) and args.profile is not None:
        parser.error("--family-counts/--family-members e --profile non possono essere usati insieme")

    try:
        start, end = resolve_range(args)
        wanted: Optional[Profile] = None
        if args.profile is not None:
            wanted = parse_profile(args.profile)
    except ValueError as exc:
        parser.error(str(exc))

    rows: List[Tuple[int, Profile]] = []
    for n in range(start, end + 1):
        profile = pet_profile(n)
        if wanted is None or profile == wanted:
            rows.append((n, profile))

    if args.family_counts or args.family_members:
        counts = Counter(profile for _n, profile in rows)
        members: DefaultDict[Profile, List[int]] = defaultdict(list)
        for n, profile in rows:
            members[profile].append(n)
        ordered_profiles = sorted(counts, key=sort_profiles_key)

        if args.count_only:
            print(len(ordered_profiles))
            return 0

        for profile in ordered_profiles:
            if args.family_members:
                numbers = ", ".join(str(n) for n in members[profile])
                print(f"{format_profile(profile)} -> {counts[profile]} :: {numbers}")
            else:
                print(f"{format_profile(profile)} -> {counts[profile]}")
        print(f"\nFamiglie: {len(ordered_profiles)}", file=sys.stderr)
        print(f"Numeri nel range: {len(rows)}", file=sys.stderr)
        return 0

    if args.count_only:
        print(len(rows))
        return 0

    if wanted is None:
        for n, profile in rows:
            print(f"{n} -> {format_profile(profile)}")
    else:
        print(", ".join(str(n) for n, _profile in rows))

    print(f"\nTotale: {len(rows)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
