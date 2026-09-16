# Multiset-of-exponents invariant (T03)

Status: research note (closed)
Scope: what the fingerprint of shape(k^n) depends on
Stability: exact consequence of the identity; verified on small
           examples
Thread: T03

## Statement

The fingerprint of `shape(k^n)` depends only on the **multiset of
exponents** in the prime factorization of `k`. It does not depend on:

- the numeric values of the primes;
- the order of the exponents.

## Argument

The exact identity (`exponential-base-structural-class.md`) gives, for
`k = p1^e1 * ... * pr^er`,

    shape(k^n) = C(r0^shape(e1*n), ..., r_{r-1}^shape(er*n)).

The values `p_i` do not appear. Therefore the shape of `k^n` does not
depend on them.

The `node_count` of a container is the sum of the node counts of its
terms plus one. This sum is invariant under reordering of the terms.
Since the fingerprint is computed from `node_count(shape(k^n))`, and
`node_count` is invariant under reordering, the fingerprint is also
invariant under reordering.

Together: only the multiset `{e1, ..., er}` survives.

## Minimal example

`2^n`, `6^n`, `30^n` all have multiset `{1, 1, ..., 1}` (one 1 per
distinct prime). By the duplication lemma
(`{a, a, ...} ≡ {a}`), they share the same fingerprint.

## Verification

Order-invariance check, `N = 60`:

| base | multiset | fingerprint |
| ---: | --- | --- |
| 12 | {2, 1} | (37.29, 40.68, 22.03) |
| 18 | {1, 2} | (37.29, 40.68, 22.03) |
| 60 | {2, 1, 1} | (37.29, 42.37, 20.34) |
| 90 | {1, 2, 1} | (37.29, 42.37, 20.34) |

Same multiset, different order, same fingerprint.

## Boundary

This note does not claim:

- that the fingerprint depends **only** on the multiset (it depends
  also on `N`, the window; see `exponential-base-structural-class.md`);
- that different multisets always give different fingerprints
  (the "1 wins" conjecture was falsified);
- that the duplication lemma extends beyond the tested range.

## Status

T03 closed. The answer to "does the fingerprint depend only on the
multiset of exponents, not on the number of distinct primes?" is:
yes, exactly, by the identity and the symmetry of `node_count`.
