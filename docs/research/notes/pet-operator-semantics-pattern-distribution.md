# PET/PEG Operator Semantics Pattern Distribution

This note records an experimental observation from the PET/PEG 2.0 operator
semantics matrix report.

The observation is based on the experimental command:

    pet experimental operator-semantics matrix --range START END --no-rows --json

It does not define stable PET semantics. It does not change PET core
factorization, routing, anchor selection, verification, or default operator
semantics.

## Summary

Across the observed ranges:

- 2..100
- 2..1,000
- 2..10,000
- 2..100,000

the matrix produced:

- `pattern_count = 10`
- `unclassified-operator-pattern = none`

This suggests that the current experimental `pattern_class` vocabulary covers
the observed operator-semantics matrix patterns up to 100,000.

The dominant class is consistently:

    multi-support-removal

Its share increases with the scanned range.

## Observed distributions

### Range 2..100

Checked: 99

| Count | Class |
| ---: | --- |
| 34 | `multi-support-removal` |
| 24 | `single-support-leaf` |
| 14 | `multi-support-leaf-blocked-removal` |
| 10 | `multi-support-stable-removal` |
| 6 | `multi-support-recursive-leaf-blocked` |
| 4 | `single-support-recursive-chain` |
| 3 | `single-support-leaf-blocked-retarget` |
| 2 | `single-support-power-destroyed` |
| 1 | `single-support-root-stable` |
| 1 | `single-support-leaf-blocked` |

### Range 2..1,000

Checked: 999

| Count | Class |
| ---: | --- |
| 484 | `multi-support-removal` |
| 167 | `single-support-leaf` |
| 156 | `multi-support-leaf-blocked-removal` |
| 102 | `multi-support-stable-removal` |
| 64 | `multi-support-recursive-leaf-blocked` |
| 10 | `single-support-leaf-blocked-retarget` |
| 7 | `single-support-power-destroyed` |
| 7 | `single-support-recursive-chain` |
| 1 | `single-support-leaf-blocked` |
| 1 | `single-support-root-stable` |

### Range 2..10,000

Checked: 9,999

| Count | Percent | Class |
| ---: | ---: | --- |
| 5,415 | 54.16% | `multi-support-removal` |
| 1,638 | 16.38% | `multi-support-leaf-blocked-removal` |
| 1,228 | 12.28% | `single-support-leaf` |
| 1,024 | 10.24% | `multi-support-stable-removal` |
| 642 | 6.42% | `multi-support-recursive-leaf-blocked` |
| 24 | 0.24% | `single-support-leaf-blocked-retarget` |
| 15 | 0.15% | `single-support-power-destroyed` |
| 11 | 0.11% | `single-support-recursive-chain` |
| 1 | 0.01% | `single-support-leaf-blocked` |
| 1 | 0.01% | `single-support-root-stable` |

### Range 2..100,000

Checked: 99,999

Runtime observed with progress enabled:

    elapsed=4:59.41 user=297.01 sys=0.28

| Count | Percent | Class |
| ---: | ---: | --- |
| 57,042 | 57.04% | `multi-support-removal` |
| 16,591 | 16.59% | `multi-support-leaf-blocked-removal` |
| 10,229 | 10.23% | `multi-support-stable-removal` |
| 9,591 | 9.59% | `single-support-leaf` |
| 6,437 | 6.44% | `multi-support-recursive-leaf-blocked` |
| 64 | 0.06% | `single-support-leaf-blocked-retarget` |
| 29 | 0.03% | `single-support-power-destroyed` |
| 14 | 0.01% | `single-support-recursive-chain` |
| 1 | 0.00% | `single-support-leaf-blocked` |
| 1 | 0.00% | `single-support-root-stable` |

## Singleton classes

Two classes remain singleton observations through 100,000:

| Class | Number |
| --- | ---: |
| `single-support-root-stable` | 2 |
| `single-support-leaf-blocked` | 4 |

Interpretation:

- `2` is the minimal single-support root-stable case.
- `4 = 2^2` is the first single-support case where the sampled address behavior
  observes `leaf-blocked`.

These are special only inside the experimental operator-semantics matrix
classification. This is not a factorization claim.

## Multi-support non-flat rule

A follow-up anatomy check exposed a sharper rule for the multi-support classes.

For a number written as:

    N = p1^e1 * p2^e2 * ...

with primes ordered increasingly, define:

    first_nonflat_exp = first exponent e_i > 1

If all exponents are `1`, then `first_nonflat_exp = none`.

Across the observed range 2..100,000, the multi-support classes follow this
grid with no observed mismatches:

| Support condition | `first_nonflat_exp` | Pattern class |
| --- | --- | --- |
| does not contain `{2, 3}` | `2` | `multi-support-leaf-blocked-removal` |
| does not contain `{2, 3}` | `none` or `>= 3` | `multi-support-removal` |
| contains `{2, 3}` | `2` | `multi-support-recursive-leaf-blocked` |
| contains `{2, 3}` | `none` or `>= 3` | `multi-support-stable-removal` |

This means the observed `leaf-blocked` split is not triggered by the mere
presence of an exponent `2` somewhere in the factorization.

Instead, it is triggered when the first non-flat branch, in prime-support order,
is quadratic.

Examples:

| N | Factorization | Support contains `{2, 3}` | `first_nonflat_exp` | Class |
| ---: | --- | --- | ---: | --- |
| 20 | `2^2 * 5` | no | 2 | `multi-support-leaf-blocked-removal` |
| 200 | `2^3 * 5^2` | no | 3 | `multi-support-removal` |
| 12 | `2^2 * 3` | yes | 2 | `multi-support-recursive-leaf-blocked` |
| 72 | `2^3 * 3^2` | yes | 3 | `multi-support-stable-removal` |
| 108 | `2^2 * 3^3` | yes | 2 | `multi-support-recursive-leaf-blocked` |

The experimental matrix report exposes this discriminator through `--anatomy`
fields:

- `first_nonflat_exp_dist`
- `has_support_2_3_count`
- `has_support_2_3_ratio`

## Working interpretation

The current data suggests that the dominant observed behavior is not the
single-support prime/leaf case.

Instead, the dominant behavior is:

    multi-support removal

The share of `multi-support-removal` increases across the observed ranges:

| Range | Share |
| --- | ---: |
| 2..100 | 34.34% |
| 2..1,000 | 48.45% |
| 2..10,000 | 54.16% |
| 2..100,000 | 57.04% |

The single-support prime/leaf class decreases as the range grows, which is
consistent with prime density decreasing over larger intervals.

## Boundary

This note is an experimental observation.

It does not claim:

- stable PET semantics
- complete PEG algebra
- factorization improvement
- routing improvement
- anchor-selection improvement
- verification change
- default CLI behavior change
