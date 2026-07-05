# PET-METICA seven-family probe (tier 900)

Targeted bounded scan for the family `7 × {2^k, 3^k}` within `1..n_max`.

## Scope

- generated at (UTC): `2026-07-05T12:36:57.773192+00:00`
- n_max: `900`
- overscan: `2700`
- min |asymmetry| for partner table: `6`
- dyadic family members: `[7, 14, 28, 56, 112, 224, 448, 896]`
- triadic family members: `[7, 21, 63, 189, 567]`
- reproduction command:

    tools/research/pet_metica_seven_family_probe.py \
      --n-max 900 --overscan 2700 \
      --output-json docs/reports/data/metica-seven-family-900.json \
      --output-md docs/reports/generated/metica-seven-family-900.md

## Observations

### Family hub scores

| node | hub_score |
|---|---|
| 7 | 8036 |
| 14 | 12651 |
| 21 | 3830 |
| 28 | 3596 |
| 56 | 2615 |
| 63 | 1650 |
| 112 | 4264 |
| 189 | 1115 |
| 224 | 2220 |
| 448 | 1072 |
| 567 | 0 |
| 896 | 0 |

### Canonical seed pairs `(2^k, 7·2^k)`

| k | base | target | d(base→target) | d(target→base) | asymmetry |
|---|---|---|---|---|---|
| 1 | 2 | 14 | 5 | 1 | 4 |
| 2 | 4 | 28 | 5 | 1 | 4 |
| 3 | 8 | 56 | 5 | 1 | 4 |
| 4 | 16 | 112 | 5 | 1 | 4 |
| 5 | 32 | 224 | 7 | 1 | 6 |
| 6 | 64 | 448 | 9 | 1 | 8 |
| 7 | 128 | 896 | 11 | 1 | 10 |

### Canonical seed pairs `(3^k, 7·3^k)`

| k | base | target | d(base→target) | d(target→base) | asymmetry |
|---|---|---|---|---|---|
| 1 | 3 | 21 | 5 | 1 | 4 |
| 2 | 9 | 63 | 5 | 1 | 4 |
| 3 | 27 | 189 | 5 | 1 | 4 |
| 4 | 81 | 567 | 7 | 1 | 6 |

### Strong family-involved asymmetric pairs

| family_member | partner | d_ab | d_ba | asymmetry |
|---|---|---|---|---|
| 896 | 128 | 11 | 1 | 10 |
| 896 | 256 | 12 | 2 | 10 |
| 896 | 512 | 13 | 3 | 10 |
| 56 | 616 | 9 | 1 | 8 |
| 448 | 64 | 9 | 1 | 8 |
| 896 | 64 | 10 | 2 | 8 |
| 112 | 616 | 10 | 2 | 8 |
| 448 | 128 | 10 | 2 | 8 |
| 224 | 616 | 11 | 3 | 8 |
| 448 | 256 | 11 | 3 | 8 |
| 896 | 384 | 10 | 2 | 8 |
| 448 | 616 | 12 | 4 | 8 |
| 896 | 768 | 11 | 3 | 8 |
| 448 | 512 | 4 | 12 | -8 |
| 896 | 616 | 5 | 13 | -8 |
| 7 | 77 | 7 | 1 | 6 |
| 7 | 539 | 8 | 2 | 6 |
| 7 | 847 | 8 | 2 | 6 |
| 28 | 308 | 7 | 1 | 6 |
| 28 | 616 | 8 | 2 | 6 |

## Interpretation and limits

1. Family members and seed pairs are defined algebraically inside the
   bounded window `1..n_max`; this is not an infinite-family theorem.
2. Canonical seeds test the `(base, 7·base)` pattern for bases `2^k` and
   `3^k` separately.
3. Partner tables list strong asymmetries where at least one endpoint is
   a family member.

## Non-claims

This probe does not claim global asymmetry laws for all multiples of 7,
asymptotic hub rank for the family, or invariance under overscan choice.
