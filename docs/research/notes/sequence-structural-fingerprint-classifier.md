# Sequence structural fingerprint as a classifier (bounded empirical)

Status: research note
Scope: classification of integer sequences by shape-space profile
Stability: bounded empirical observation; not a theorem

This note records a third observation about PETRA shape space as a
setting for analyzing infinite integer sequences. It builds on the two
previous notes (`collatz-structural-signature.md` and
`arithmetic-maps-structural-fingerprint.md`) and asks whether the
profile of a sequence in shape space can act as a classifier.

## Method

For each sequence, the experiment:

1. takes the first N values of the sequence;
2. converts each value to its canonical PETRA shape;
3. computes `node_count` of each shape (number of Leaf, Container, and
   Term nodes);
4. classifies each consecutive transition:
   - reduction if `node_count(b) < node_count(a)`;
   - expansion if `node_count(b) > node_count(a)`;
   - stable if equal;
5. reports the three percentages (red, exp, stab) as the sequence
   fingerprint.

## Observation 1 — Profiles converge

Fingerprint values stabilize as N grows. Tested at N in {100, 150, 200,
250}, the position of each sequence in (red, exp, stab) space moves by
at most 1-2 percentage points after N = 150.

Stable fingerprints at N = 200:

| Sequence | red | exp | stab |
| --- | ---: | ---: | ---: |
| Fibonacci | 46.7 | 46.2 | 7.0 |
| n^2 | 40.2 | 43.7 | 16.1 |
| 2^n | 38.2 | 40.7 | 21.1 |
| n! | 25.6 | 55.3 | 19.1 |
| Catalan | 20.6 | 43.7 | 35.7 |

Every tested family occupies a distinct region of the (red, exp, stab)
space.

## Observation 2 — Exponential bases collide

Sequences `k^n` for different bases k share the same fingerprint:

| Sequence | red | exp | stab |
| --- | ---: | ---: | ---: |
| 2^n | 38.2 | 40.7 | 21.1 |
| 3^n | 38.2 | 40.7 | 21.1 |
| 7^n | 38.2 | 40.7 | 21.1 |

This is not an experimental coincidence. It follows from the shape
projection:

    shape(2^n) = C(r0^shape(n))
    shape(3^n) = C(r0^shape(n))
    shape(k^n) = C(r0^shape(n))    for any prime k

The shape of `k^n` depends only on `shape(n)`, not on `k`. The
transition `n -> n+1` therefore produces the same structural variation
for every base. The collision is a property of the projection, not a
limitation of the classifier.

## Observation 3 — Algebraic variation is distinguished

Two sequences with the same growth rate can have different
fingerprints. Both `n^2` and `n^2 + n` are quadratic, but:

| Sequence | red | exp | stab |
| --- | ---: | ---: | ---: |
| n^2 | 40.2 | 43.7 | 16.1 |
| n^2 + n | 33.7 | 36.7 | 29.6 |
| n^2 + 1000 | 40.7 | 41.2 | 18.1 |

`n^2 + n = n(n+1)` is always even and always factors as a product of
two consecutive integers. The structural fingerprint reflects this
algebraic difference: the stability percentage almost doubles (16.1 to
29.6).

The classifier is therefore finer than growth class alone.

## Observation 4 — Algebraic identities are confirmed

`4^n` and `2^(2n)` are the same sequence under any reasonable
evaluation. Their fingerprints are bit-for-bit identical:

| Sequence | red | exp | stab |
| --- | ---: | ---: | ---: |
| 2^(2n) | 35.7 | 37.7 | 26.6 |
| 4^n | 35.7 | 37.7 | 26.6 |

The classifier respects exact algebraic identities and does not produce
spurious distinctions.

## Granularity

Combining the observations, the classifier operates at three levels:

| Level | Distinguishes | Example |
| --- | --- | --- |
| broad | growth class | polynomial vs exponential |
| medium | algebraic family | n^2 vs n^2 + n |
| narrow | (not reached) | 2^n and 3^n collide |

The medium level is the operational granularity of the method. It does
not distinguish individual sequences that differ only in a
multiplicative constant or a base prime. It does distinguish algebraic
variation that changes the factorization structure of the sequence.

## Interpretation

Two kinds of information are captured by the fingerprint:

1. **Growth-class information**: which transitions dominate, how often
   the shape changes.
2. **Algebraic-structure information**: how the factorization pattern
   of consecutive values varies.

The first kind is shared by families with the same asymptotic growth.
The second kind differentiates sequences within the same growth class.
Together they give a classifier at algebraic-family granularity.

## Boundary

This note does not claim that:

- the fingerprint is a complete invariant of an integer sequence;
- the classifier is exact or has a closed-form definition;
- `node_count` is the only reasonable structural metric;
- the tested families are representative of all integer sequences;
- collision of fingerprints implies any deep equivalence of sequences;
- non-collision implies the sequences are fundamentally different.

The observation is bounded to the tested sequences and ranges.

## Reproducibility

All results were produced with:

- `resolver.int_to_shape` for value-to-shape conversion;
- `petra.parse_shape` and the public shape model for node counting;
- direct evaluation of each sequence.

No precomputed tables or external datasets were used.

## Possible next directions

1. Test collision and distinction on more families:
   - aliquot sequences;
   - sums of two squares in enumeration order;
   - Beatty sequences;
   - random walks with drift.
2. Use a finer structural metric:
   - depth-weighted mass;
   - recursive-mass metric.
3. Investigate whether the fingerprint is invariant under arithmetic
   transformations (shift, scaling, composition).
4. Test whether the classification changes when the same sequence is
   sampled sparsely (every second term, every k-th term).
5. Build a small catalogue of sequence fingerprints for known families
   and check whether novel sequences can be assigned to a family.

Each direction requires a separate bounded experiment.

## Status

This note is a third bounded observation. It should be extended,
refuted, or archived based on further experiments. It does not claim a
general theorem about sequence classification.
