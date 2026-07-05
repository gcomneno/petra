# PET-METICA seven-family probe (tier 300)

Targeted bounded scan for the family `7 × {2^k, 3^k}` within `1..n_max`.

## Scope

- generated at (UTC): `2026-07-05T12:21:19.275347+00:00`
- n_max: `300`
- overscan: `900`
- min |asymmetry| for partner table: `6`
- dyadic family members: `[7, 14, 28, 56, 112, 224]`
- triadic family members: `[7, 21, 63, 189]`
- reproduction command:

    tools/research/pet_metica_seven_family_probe.py \
      --output-json docs/reports/data/metica-seven-family-300.json \
      --output-md docs/reports/generated/metica-seven-family-300.md

## Observations

### Family hub scores

| node | hub_score |
|---|---|
| 7 | 1312 |
| 14 | 2011 |
| 21 | 745 |
| 28 | 717 |
| 56 | 786 |
| 63 | 385 |
| 112 | 368 |
| 189 | 0 |
| 224 | 0 |

### Canonical seed pairs `(2^k, 7·2^k)`

| k | base | target | d(base→target) | d(target→base) | asymmetry |
|---|---|---|---|---|---|
| 1 | 2 | 14 | 5 | 1 | 4 |
| 2 | 4 | 28 | 5 | 1 | 4 |
| 3 | 8 | 56 | 5 | 1 | 4 |
| 4 | 16 | 112 | 7 | 1 | 6 |
| 5 | 32 | 224 | 9 | 1 | 8 |

### Canonical seed pairs `(3^k, 7·3^k)`

| k | base | target | d(base→target) | d(target→base) | asymmetry |
|---|---|---|---|---|---|
| 1 | 3 | 21 | 5 | 1 | 4 |
| 2 | 9 | 63 | 5 | 1 | 4 |
| 3 | 27 | 189 | 7 | 1 | 6 |

### Strong family-involved asymmetric pairs

| family_member | partner | d_ab | d_ba | asymmetry |
|---|---|---|---|---|
| 224 | 32 | 9 | 1 | 8 |
| 224 | 64 | 10 | 2 | 8 |
| 224 | 128 | 11 | 3 | 8 |
| 224 | 256 | 4 | 12 | -8 |
| 112 | 16 | 7 | 1 | 6 |
| 224 | 16 | 8 | 2 | 6 |
| 189 | 27 | 7 | 1 | 6 |
| 112 | 32 | 8 | 2 | 6 |
| 112 | 64 | 9 | 3 | 6 |
| 189 | 81 | 8 | 2 | 6 |
| 224 | 96 | 8 | 2 | 6 |
| 224 | 192 | 9 | 3 | 6 |
| 112 | 128 | 4 | 10 | -6 |
| 112 | 256 | 5 | 11 | -6 |
| 189 | 243 | 3 | 9 | -6 |
| 224 | 288 | 3 | 9 | -6 |

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
