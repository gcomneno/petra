#!/usr/bin/env python3
"""Measure SumPk2, rho, stab of g(n) at large N (T16/T19).

Uses only the arithmetic recurrence

    g(1) = 1
    g(n) = 1 + sum over e in Exp(n) of (1 + g(e))

No PETRA shape is constructed. The transition of base 2 reduces to
sign(g(n+1) - g(n)); the same g underlies every base.
"""

from __future__ import annotations

import argparse
import math
from array import array
from collections import Counter


def build_spf(N: int) -> array:
    """Smallest prime factor up to N."""
    spf = array("i", range(N + 1))
    if N >= 1:
        spf[1] = 1
    i = 2
    while i * i <= N:
        if spf[i] == i:
            j = i * i
            while j <= N:
                if spf[j] == j:
                    spf[j] = i
                j += i
        i += 1
    return spf


def compute_g(N: int, spf: array) -> array:
    """g(n) for n in 1..N using the recurrence."""
    g = array("i", [0]) * (N + 1)
    g[1] = 1
    for n in range(2, N + 1):
        m = n
        s = 1
        while m > 1:
            p = spf[m]
            e = 0
            while m % p == 0:
                m //= p
                e += 1
            s += 1 + g[e]
        g[n] = s
    return g


def measure(N: int) -> dict:
    spf = build_spf(N)
    g = compute_g(N, spf)
    counts_g: Counter = Counter()
    counts_d: Counter = Counter()
    for n in range(1, N + 1):
        counts_g[g[n]] += 1
    for n in range(1, N):
        d = g[n + 1] - g[n]
        if d < 0:
            counts_d["red"] += 1
        elif d > 0:
            counts_d["exp"] += 1
        else:
            counts_d["stab"] += 1
    total_d = sum(counts_d.values())
    red = counts_d["red"] / total_d
    exp = counts_d["exp"] / total_d
    stab = counts_d["stab"] / total_d
    sumpk2 = sum((c / N) ** 2 for c in counts_g.values())
    rho = stab / sumpk2 if sumpk2 > 0 else 0.0
    return {
        "N": N,
        "red": round(red * 100, 4),
        "exp": round(exp * 100, 4),
        "stab": round(stab * 100, 4),
        "SumPk2": round(sumpk2 * 100, 4),
        "rho": round(rho, 4),
        "distinct_g": len(counts_g),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--Ns", type=int, nargs="+", default=[10_000_000])
    args = parser.parse_args()
    print(f"{'N':>10} {'red%':>8} {'exp%':>8} {'stab%':>8} {'SumPk2':>8} {'rho':>7} {'loglog':>8} {'SumPk2*sqrt(loglog)':>20}")
    for N in args.Ns:
        r = measure(N)
        ll = math.log(math.log(N)) if N > 1 else 0.0
        prod = r["SumPk2"] * math.sqrt(ll)
        print(f"{r['N']:>10} {r['red']:>8} {r['exp']:>8} {r['stab']:>8} {r['SumPk2']:>8} {r['rho']:>7} {ll:>8.4f} {prod:>20.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
