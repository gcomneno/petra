# Shape-plus-context: no bounded k (P3)

Status: research note (bounded empirical + argument)
Scope: whether a fixed context size k determines the Collatz
       successor's shape
Stability: negative result, with a Dirichlet-based argument
Thread: P3

## Context

T09 observed that the shape of `n` does not determine the shape of
`Collatz(n)`, but shape plus `n mod 2^k` might. The question was
whether a finite `k` suffices, and if so, whether it is constant or
grows with `n`.

## Argument

For every `k`, by Dirichlet's theorem there are infinitely many primes
in every residue class `mod 2^k` coprime to `2^k`. Choose two distinct
primes `p, q` in the same class. Then:

- `shape(p) = shape(q) = ○^(A)`, since both are prime;
- `p mod 2^k = q mod 2^k`, by choice;
- `3p + 1 ≠ 3q + 1`, since `p ≠ q`.

The shapes `shape(3p+1)` and `shape(3q+1)` are not in general equal.
Hence for every fixed `k`, there exist pairs of integers with the same
shape and the same residue mod `2^k`, but different successor shapes.

Therefore no finite `k` is universal. The context required grows with
`n`.

## Smallest explicit counterexample

For `k = 3`, primes congruent to `5 mod 8`:

| p | p mod 8 | shape(p) | 3p+1 | shape(3p+1) |
| ---: | ---: | --- | ---: | --- |
| 5 | 5 | ○^(A) | 16 | ○^(A^(A^(A))) |
| 13 | 5 | ○^(A) | 40 | ○^(A^(A) × B) |
| 29 | 5 | ○^(A) | 88 | ○^(A^(A) × B) |
| 37 | 5 | ○^(A) | 112 | ○^(A^(A^(A)) × B) |
| 101 | 5 | ○^(A) | 304 | ○^(A^(A^(A)) × B) |

Same shape, same residue, different successor shapes.

## Boundary

This note does not claim:

- that no context suffices (the full value of `n` always suffices);
- that the growth rate of the minimal `k` is known (untested);
- that the argument extends to maps other than Collatz;
- that the counterexamples are the smallest possible for each `k`.

## Reproducibility

Small check with `sympy.primerange`, `resolver.int_to_shape`,
`resolver.notation.to_mother_notation`. Full script not committed.

## Status

P3 closed. Negative result: no bounded universal context.
