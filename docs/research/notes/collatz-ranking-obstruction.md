# No ranking function on PETRA shapes for Collatz

Status: research note
Scope: formal obstruction for shape-level termination arguments
Stability: negative result; mathematical obstruction, not a theorem about Collatz

This note records a negative observation: no ranking function over
PETRA shapes alone can establish termination of the Collatz map. The
obstruction is formal and does not depend on the specific form of the
ranking function.

The note does not address the Collatz conjecture. It records why one
specific approach, suggested by the classical termination-proof
technique, cannot work in this representation.

## Context

In formal verification, termination of a deterministic loop is often
established by exhibiting a **ranking function** `R`: a total function
from program states to a well-founded set (typically `N`) such that at
every step:

    R(next_state) < R(current_state)

For the Collatz map, the natural candidate is `R(n) = n`. It fails
immediately: `3 -> 10`. No known `R(n)` has been found that decreases
along every Collatz step.

A natural question in the PETRA setting is whether a ranking function
can be found on the **shape** instead of the value:

    R(shape(next_state)) < R(shape(current_state))

for all `n > 1` and for some well-founded `R` on canonical PETRA
shapes.

This note shows that no such `R` exists.

## Formal obstruction

Let `S(n)` denote the canonical PETRA shape of a positive integer `n`.
Suppose there existed a total function

    R : PETRA shapes -> W

where `(W, <)` is a well-founded order, such that for every `n > 1`:

    R(S(C(n))) < R(S(n))

where `C` is the Collatz map.

For the inequality to be well-defined for every `n`, the value of
`R(S(C(n)))` must depend only on `S(n)`. That is, `S(C(n))` must be
determined by `S(n)`:

    S(a) = S(b)  implies  S(C(a)) = S(C(b))    for all a, b > 1.

This implication is false.

Take `a = 6` and `b = 15`. Both have the same shape:

    S(6) = S(15) = C(r0^1, r1^1)

But their Collatz successors differ in shape:

    C(6) = 3      S(3) = C(r0^1)
    C(15) = 46    S(46) = C(r0^1, r1^1)

Therefore `S(C(a)) != S(C(b))` while `S(a) = S(b)`. The implication
fails. Consequently no such `R` exists.

## Experimental confirmation

The obstruction is a direct consequence of the shape projection being
lossy: the shape discards the concrete primes, and the concrete primes
determine the Collatz successor.

To confirm the magnitude of the effect, an experiment was run over all
distinct-prime semiprimes in `[4, 100000)`. For each `n`, one Collatz
step was applied and the shape of the successor was recorded.

The semiprimes split into two classes:

| Class | Count | Successor shape distribution |
| --- | ---: | --- |
| even (`2p`) | 5132 | 100% `C(r0^1)` (prime shape) |
| odd (`p·q`, `p,q` odd) | ~18000 | spread across `C(r0^1,r1^1,r2^1)` (21.7%), `C(r0^C(r0^1),r1^1,r2^1)` (18.0%), `C(r0^1,r1^1)` (13.1%), ... |

Both classes share the same shape `C(r0^1, r1^1)`. Their successor
shapes differ. The shape does not carry the parity information that
determines the next step.

## Interpretation

The reduction-dominance observed in the earlier note
(`arithmetic-maps-structural-fingerprint.md`) is consistent with this
obstruction. The shape-level reduction is a **statistical tendency**,
not a deterministic property. It arises because:

- even semiprimes (`2p`) collapse to a prime in one step;
- odd semiprimes (`p·q`) expand or reshuffle in a way that depends on
  their concrete prime factors;
- the shape projection cannot distinguish the two cases.

No shape-only criterion can therefore separate the reducing steps from
the expanding steps.

## Relationship to the Collatz literature

A recent survey of the Collatz conjecture notes that no global
potential function has been found that decreases along every orbit.
This note does not prove that such a function does not exist on `N`.

What it does prove is narrower: no such function exists on PETRA
**shapes**. The obstruction is specific to the shape projection and
does not transfer to value-level arguments.

The mechanism is general: whenever a projection `p` from a domain `D`
to a smaller codomain fails the implication

    p(a) = p(b)  implies  p(f(a)) = p(f(b))

for a function `f` on `D`, no ranking function on `p(D)` can establish
termination of `f`. The Collatz map on PETRA shapes is one instance.

## Boundary

This note does not claim that:

- Collatz is undecidable, independent, or unprovable;
- no ranking function exists on the integers;
- the Collatz conjecture is affected by this observation;
- shape-space analysis is useless for Collatz;
- the specific experimental counts generalize beyond the tested range.

The result is a **negative structural result**: it establishes the
non-existence of a specific class of proofs in a specific
representation.

## What remains possible

The obstruction does not exclude:

- statistical analyses of shape transitions;
- Lyapunov-like measures that decrease on average;
- shape-plus-context state (for example shape together with `n mod 2^k`)
  where a deterministic successor is recovered at the cost of
  reintroducing value information;
- projections other than PETRA shapes that preserve enough structure.

The obstruction only excludes the pure shape-only ranking approach.

## Reproducibility

The experimental confirmation used:

- `resolver.int_to_shape` for value-to-shape conversion;
- `sympy.factorint` for semiprime detection;
- a direct single-step Collatz application.

The formal obstruction is a proof by counterexample and can be
verified by inspection.

## Status

This note is a negative structural result. It should be cited as a
limitation, not as progress on Collatz.
