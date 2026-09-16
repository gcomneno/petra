# Fingerprint asymptotics: reduction to the arithmetic function g(n) (T16)

Status: research note (bounded empirical)
Scope: asymptotic behaviour of the transition fingerprint of `k^n`
Stability: one reduction verified exhaustively, one empirical asymptotics with unresolved limit
Thread: T16 (`open-threads.md`), downstream of T01

## Context

T16 asks whether the cumulative fingerprint `F(1, N)` of `k^n`
converges as `N -> infinity`, and at what rate. The earlier note
`exponential-base-structural-class.md` established that the window
fingerprint `(red, exp, stab)` is window-dependent and therefore not a
class invariant. This note pushes the analysis past the window and
identifies the exact underlying signal.

## Result 1: the transition signal is an arithmetic difference

Let `shape(k^n)` be the canonical PETRA shape of the integer `k^n`
(SEC 1), and let `transition(a, b)` be the classification of consecutive
`node_count` (SEC 8): `red`, `exp`, or `stab`. Define

    g(n) = node_count(shape(n))

For `k = 2` the shape identity `shape(2^n) = C(r0^shape(n))` holds for
every `n >= 1`, and therefore

    node_count(shape(2^n)) = 2 + g(n)

(the outer container contributes 1, its single term contributes 1, and
its exponent `shape(n)` contributes `g(n)`).

Consequently:

    transition(shape(2^n), shape(2^(n+1))) = sign( g(n+1) - g(n) )

where `sign` maps negative differences to `red`, positive differences to
`exp`, and zero to `stab`.

Verified against the direct definition for `n = 2..80`: 79/79 matches,
zero mismatches.

The analogous identity holds for every base `k`, replacing `2` by `k`
and the single exponent by the exponent multiset of `k`. The underlying
signal is therefore the same for all bases, shifted by the factorisation
of `k`.

## Result 2: the exact arithmetic recurrence for g

The function `g` satisfies a purely arithmetic recurrence:

    g(1) = 1
    g(n) = 1 + sum over e in Exp(n) of (1 + g(e))

where `Exp(n)` is the multiset of exponents in the prime factorisation
of `n`. The `1 +` outside the sum is the outer container; each `1 + g(e)`
inside is one term plus its exponent subtree.

This recurrence is exact and does not require building any PETRA shape.

Verified against `node_count(shape(n))` for `n = 1..200`: 200/200
matches, zero mismatches.

The recurrence is also a genuine recursion into the exponents
themselves: the argument of `g` on the right-hand side is `e`, an
exponent of `n`, and `e < n` for every `n > 1`. It terminates.

This addresses the open question 4 of
`exponential-base-structural-class.md` for the metric `node_count`:
the decomposition does recurse into the exponents, and the recurrence
is closed on the integers.

## Result 3: the cumulative fingerprint of g

Define `d(n) = sign(g(n+1) - g(n))`, and let

    F_g(N) = (red_pct(N), exp_pct(N), stab_pct(N))

be the percentages of `red`, `exp`, `stab` over `n = 1..N-1`, computed
by a linear sieve to `10^7` and `10^8` (no PETRA shape is constructed;
only the recurrence of Result 2 is used).

Checkpoints:

| N | red | exp | stab | red - exp | stab * log N |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10^2 | 38.38 | 41.41 | 20.20 | -3.03 | 93.03 |
| 10^3 | 41.14 | 41.14 | 17.72 | 0.00 | 122.39 |
| 10^4 | 41.44 | 41.48 | 17.07 | -0.04 | 157.24 |
| 10^5 | 41.79 | 41.85 | 16.36 | -0.05 | 188.34 |
| 10^6 | 42.06 | 42.06 | 15.88 | -0.01 | 219.37 |
| 10^7 | 42.25 | 42.25 | 15.50 | 0.00 | 249.88 |
| 10^8 | 42.40 | 42.40 | 15.20 | 0.00 | 280.02 |

Two clear facts:

- `red - exp` collapses to numerical zero by `N = 10^3` and stays there.
  The two directional transitions are asymptotically equiprobable.
- `stab(N)` decreases monotonically from `20.2%` to `15.2%` across six
  decades, and has not visibly stabilised at `N = 10^8`.

## Result 4: unresolved form of stab(N)

Two candidate asymptotics remain indistinguishable at `N = 10^8`:

    (A)  stab(N) = a + b / log N       with a ~ 13 and b > 0
    (B)  stab(N) = c / (log N)^alpha   with alpha ~ 0.15

Local slope of `stab * log N` versus `log N`:

| interval | slope |
| --- | ---: |
| 10^2 -> 10^3 | 12.75 |
| 10^3 -> 10^4 | 15.14 |
| 10^4 -> 10^5 | 13.50 |
| 10^5 -> 10^6 | 13.47 |
| 10^6 -> 10^7 | 13.25 |
| 10^7 -> 10^8 | 13.09 |

The slope decreases monotonically over the last four decades, from
13.50 to 13.09. Under (A) it should stabilise at `a`; under (B) it
should continue to decrease indefinitely. The data at `10^8` do not
decide between the two.

Under (B), `stab` decays so slowly that it would still be near `13%`
at `N = 10^100`, which is why the two scenarios are practically
indistinguishable at accessible scales.

## Consequences for T01

- The fingerprint of `k^n` is a property of the integer sequence
  `n -> g(n)`, not of the base `k`. It is therefore neither a class
  invariant in the sense of T01, nor a base invariant. It is a
  universal arithmetic signal.
- The window-dependence documented in
  `exponential-base-structural-class.md` is a projection loss: the
  transition sequence `d(n)` is deterministic and slowly varying, and
  any finite window under-resolves it.
- The true asymptotic question of T16 is the density of
  `{ n : g(n+1) = g(n) }`. This is an arithmetic problem on the
  exponent multisets of consecutive integers, not a PETRA structural
  problem.

## Method and reproducibility

- `g` computed by linear sieve `spf` up to `N`, then the recurrence of
  Result 2 with memoisation on `g`.
- `N = 10^7`: sieve ~ 4 s, `g` ~ 11 s, scan ~ 3 s (Python 3, CPython).
- `N = 10^8`: sieve ~ 40 s, `g` ~ 132 s, scan ~ 38 s; peak memory
  ~ 800 MB with two `array('i')` of length `N+1`.
- No PETRA shape is constructed at any point in the computation of
  `F_g`.

## Boundary

This note does not claim:

- convergence of `stab(N)` to a positive constant, nor to zero;
- a proof of the recurrence of Result 2 beyond `n = 200`;
- that the linear sieve to `10^8` is the practical limit, only that
  `10^8` is the largest scale attempted here;
- that `node_count` is the only admissible metric (SEC 8 leaves this
  open for future admission);
- any statement about bases `k` other than through the exact reduction
  to `g`.

## Status

Second structural result of the T16 line, downstream of the T01 exact
identity. The reduction (Results 1 and 2) is exact and verified
exhaustively at small scales. The asymptotics (Results 3 and 4) is
empirical and unresolved at the level of the constant `a` or the
exponent `alpha`. A dedicated thread is warranted to decide between
(A) and (B) analytically, if possible.
