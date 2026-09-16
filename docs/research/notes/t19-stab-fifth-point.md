# Fifth data point for stab(N) (T19)

Status: research note (bounded empirical, one hypothesis rejected)
Scope: asymptotic behaviour of stab(N) = rho(N) * SumPk2(N)
Stability: one new data point at N = 10^8, one hypothesis excluded
Thread: T19 (downstream of T16)

## Context

`t16-fingerprint-asymptotics.md` (Result 5) decomposes

    stab(N) = rho(N) * SumPk2(N)

and measures four points, `N = 10^4..10^7`. Two candidate asymptotic
forms were already excluded. This note adds the point `N = 10^8`.

## Method

A new tool, `tools/research/t16_asymptotics.py`, computes `g(n)` by
the exact arithmetic recurrence (no PETRA shape is constructed) and
reports `stab`, `SumPk2`, and `rho` at each requested `N`.

Runtime: `N = 10^7` in ~19 s, `N = 10^8` in ~3 min 12 s, peak memory
~800 MB.

Values at `N = 10^6` and `N = 10^7` reproduce the earlier note
exactly, confirming the tool.

## Fifth data point

| N | red% | exp% | stab% | SumPk2 | rho | loglog | SumPk2·sqrt(loglog) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10^4 | -- | -- | 17.07 | 22.48 | 0.7595 | 2.2203 | 33.49 |
| 10^5 | -- | -- | 16.36 | 21.09 | 0.7758 | 2.4435 | 32.96 |
| 10^6 | 42.06 | 42.06 | 15.88 | 20.13 | 0.7888 | 2.6258 | 32.62 |
| 10^7 | 42.25 | 42.25 | 15.50 | 19.42 | 0.7983 | 2.7799 | 32.38 |
| **10^8** | **42.40** | **42.40** | **15.20** | **18.86** | **0.806** | **2.9135** | **32.19** |

## Hypothesis rejected: SumPk2 ~ c / sqrt(log log N)

The quantity `SumPk2 · sqrt(log log N)` decreases monotonically over
five decades:

    33.49, 32.96, 32.62, 32.38, 32.19

The decline is by ~0.2 per decade, regular. It does not stabilise.
Therefore `SumPk2` is not proportional to `1 / sqrt(log log N)`.
Fitting five points gives an exponent slightly larger than 0.5:

    SumPk2 ~ c / (log log N)^alpha,  alpha ~ 0.51, c ~ 33.

The exponent 0.5 is excluded by the data.

## rho continues to increase, slowly

The increments of `rho` per decade:

    0.0163, 0.0130, 0.0095, 0.0077

They shrink, but by a factor of ~0.8 per step, not geometrically fast.
A limit near 0.83-0.85 is compatible with the data but not supported by
it.

## stab continues to decrease, slowly

    stab:  17.07, 16.36, 15.88, 15.50, 15.20
    decrements: 0.71, 0.48, 0.38, 0.30

The decrements shrink but not toward zero fast. `stab` does not show
a plateau at `N = 10^8`.

## Boundary

This note does not claim:

- that `rho` converges, or to which value;
- that the exponent `alpha ~ 0.51` is exact (it is a 5-point fit);
- that `N = 10^9` or `10^10` would give the same trends (untested);
- any analytic argument.

The only new claim is: the hypothesis `SumPk2 ~ c / sqrt(log log N)`
is excluded by the data.

## Reproducibility

`tools/research/t16_asymptotics.py --Ns 10000000 100000000`.

## Status

T19 remains open. One candidate form excluded. Two points remain:
the limit of `rho(N)` and the asymptotic form of `SumPk2(N)`.
