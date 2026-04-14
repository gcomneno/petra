# PET family benchmark report (disjoint classical families)

## Scope

This report summarizes a bounded PET family benchmark using disjoint samples from four classical integer families:

- Perfect
- Primorials
- Hamming (5-smooth)
- Highly composite

The goal is descriptive: measure where PET captures structural differences, where it overlaps, and where it does not yield strong separation.

## Method

The benchmark uses `pet families benchmark-disjoint`, which removes overlaps by priority:

`Perfect > Primorials > Hamming > HighlyComposite`

This avoids trivial zero-distance overlaps caused by the same integer appearing in multiple families.

## Disjoint samples

- Perfect: 4 kept
- Primorials: 6 kept
- Hamming: 28 kept
- HighlyComposite: 26 kept

## Intra-family summaries

| family | distance diam | distance mean | structural_distance diam | structural_distance mean |
|---|---:|---:|---:|---:|
| Perfect | 4.00 | 3.50 | 2.00 | 1.33 |
| Primorials | 6.00 | 2.67 | 6.00 | 2.67 |
| Hamming | 7.00 | 3.60 | 6.00 | 2.49 |
| HighlyComposite | 7.00 | 3.78 | 9.00 | 3.33 |

## Inter-family summaries

### distance

| family A | family B | min | mean | max |
|---|---|---:|---:|---:|
| Perfect | Primorials | 1.00 | 4.83 | 9.00 |
| Perfect | Hamming | 1.00 | 3.75 | 8.00 |
| Perfect | HighlyComposite | 3.00 | 6.15 | 10.00 |
| Primorials | Hamming | 1.00 | 4.31 | 8.00 |
| Primorials | HighlyComposite | 1.00 | 4.40 | 8.00 |
| Hamming | HighlyComposite | 1.00 | 5.59 | 9.00 |

### structural_distance

| family A | family B | min | mean | max |
|---|---|---:|---:|---:|
| Perfect | Primorials | 1.00 | 3.67 | 7.00 |
| Perfect | Hamming | 0.00 | 2.31 | 5.00 |
| Perfect | HighlyComposite | 2.00 | 5.81 | 9.00 |
| Primorials | Hamming | 1.00 | 4.21 | 8.00 |
| Primorials | HighlyComposite | 1.00 | 4.28 | 8.00 |
| Hamming | HighlyComposite | 0.00 | 6.26 | 10.00 |

## Observations

1. PET does not produce hard separation for these four families under the strict gap test.
2. Perfect numbers are the tightest family morphologically (`structural_distance` diameter `2.00`).
3. Highly composite numbers are the widest and most internally varied family in this bounded benchmark.
4. The strongest average separation appears between Perfect and HighlyComposite numbers.
5. Hamming and HighlyComposite still overlap structurally in bounded samples, even after disjoint filtering.
6. Perfect and Hamming also reach structural distance `0.00` in at least one pair, so PET does not uniquely isolate either family by shape alone.

## Limits

This report is bounded and descriptive.

It does not claim universal family separation, complete coverage of each family, or asymptotic conclusions from finite samples alone.
