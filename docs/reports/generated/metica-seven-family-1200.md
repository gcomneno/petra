# PET-METICA seven-family probe (tier 1200)

Targeted bounded scan for the family `7 × {2^k, 3^k}` within `1..n_max`.

## Scope

- generated at (UTC): `2026-07-05T12:47:20.083639+00:00`
- n_max: `1200`
- overscan: `3600`
- min |asymmetry| for partner table: `6`
- dyadic family members: `[7, 14, 28, 56, 112, 224, 448, 896]`
- triadic family members: `[7, 21, 63, 189, 567]`
- reproduction command:

    tools/research/pet_metica_seven_family_probe.py \
      --n-max 1200 --overscan 3600 \
      --output-json docs/reports/data/metica-seven-family-1200.json \
      --output-md docs/reports/generated/metica-seven-family-1200.md

## Observations

### Family hub scores

| node | hub_score |
|---|---|
| 7 | 12135 |
| 14 | 18574 |
| 21 | 6760 |
| 28 | 5004 |
| 56 | 3678 |
| 63 | 2276 |
| 112 | 2707 |
| 189 | 1516 |
| 224 | 2995 |
| 448 | 1395 |
| 567 | 31 |
| 896 | 0 |

### Canonical seed pairs `(2^k, 7·2^k)`

| k | base | target | d(base→target) | d(target→base) | asymmetry |
|---|---|---|---|---|---|
| 1 | 2 | 14 | 5 | 1 | 4 |
| 2 | 4 | 28 | 5 | 1 | 4 |
| 3 | 8 | 56 | 5 | 1 | 4 |
| 4 | 16 | 112 | 5 | 1 | 4 |
| 5 | 32 | 224 | 5 | 1 | 4 |
| 6 | 64 | 448 | 7 | 1 | 6 |
| 7 | 128 | 896 | 9 | 1 | 8 |

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
| 56 | 616 | 9 | 1 | 8 |
| 112 | 616 | 10 | 2 | 8 |
| 896 | 128 | 9 | 1 | 8 |
| 224 | 352 | 14 | 6 | 8 |
| 224 | 616 | 11 | 3 | 8 |
| 224 | 704 | 15 | 7 | 8 |
| 224 | 1056 | 13 | 5 | 8 |
| 896 | 256 | 10 | 2 | 8 |
| 448 | 616 | 12 | 4 | 8 |
| 448 | 704 | 16 | 8 | 8 |
| 448 | 1056 | 14 | 6 | 8 |
| 896 | 512 | 11 | 3 | 8 |
| 896 | 1056 | 15 | 7 | 8 |
| 448 | 352 | 7 | 15 | -8 |
| 896 | 352 | 8 | 16 | -8 |
| 896 | 616 | 5 | 13 | -8 |
| 896 | 704 | 9 | 17 | -8 |
| 896 | 1024 | 4 | 12 | -8 |
| 7 | 77 | 7 | 1 | 6 |
| 7 | 539 | 8 | 2 | 6 |

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
