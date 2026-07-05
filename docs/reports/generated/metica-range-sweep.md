# PET-METICA multi-range sweep

This report compares bounded PET-METICA rewrite scans across several
 `(n_max, overscan)` tiers. Findings are descriptive and bounded.

## Scope

- generated at (UTC): `2026-07-05T12:17:41.992523+00:00`
- report limit: `10`
- scan tiers: `[{'n_max': 30, 'overscan': 90}, {'n_max': 50, 'overscan': 150}, {'n_max': 75, 'overscan': 225}, {'n_max': 100, 'overscan': 300}, {'n_max': 150, 'overscan': 450}, {'n_max': 200, 'overscan': 600}]`
- extended friction tier: `n_max=50`, `overscan=50000`
- reproduction command:

    tools/research/pet_metica_range_sweep.py \
      --output-json docs/reports/data/metica-range-sweep.json \
      --output-md docs/reports/generated/metica-range-sweep.md

## Observations

### Tier `30-90` (`1..30`, overscan `90`)

- active nodes: `79` / `90`
- edges: `199`
- distinct rewrite labels: `37`

Top hubs:

| node | hub_score |
|---|---|
| 2 | 259 |
| 6 | 233 |
| 4 | 120 |
| 30 | 96 |
| 3 | 90 |
| 8 | 59 |
| 15 | 51 |
| 5 | 48 |
| 10 | 48 |
| 9 | 45 |

Rewrite friction by prime:

| prime | count | min | max | avg_back_cost |
|---|---|---|---|---|
| 2 | 28 | 1 | 1 | 1.0 |
| 3 | 16 | 1 | 3 | 1.25 |
| 5 | 7 | 1 | 3 | 1.857 |

Top asymmetries:

| a | b | d_ab | d_ba | asymmetry |
|---|---|---|---|---|
| 2 | 5 | 4 | 2 | 2 |
| 2 | 10 | 3 | 1 | 2 |
| 2 | 20 | 4 | 2 | 2 |
| 2 | 25 | 5 | 3 | 2 |
| 3 | 15 | 3 | 1 | 2 |

### Tier `50-150` (`1..50`, overscan `150`)

- active nodes: `135` / `150`
- edges: `355`
- distinct rewrite labels: `50`

Top hubs:

| node | hub_score |
|---|---|
| 2 | 613 |
| 6 | 491 |
| 4 | 332 |
| 8 | 211 |
| 30 | 209 |
| 3 | 185 |
| 10 | 148 |
| 12 | 144 |
| 15 | 108 |
| 16 | 99 |

Rewrite friction by prime:

| prime | count | min | max | avg_back_cost |
|---|---|---|---|---|
| 2 | 48 | 1 | 1 | 1.0 |
| 3 | 26 | 1 | 3 | 1.308 |
| 5 | 11 | 1 | 3 | 1.909 |
| 7 | 2 | 1 | 1 | 1.0 |

Top asymmetries:

| a | b | d_ab | d_ba | asymmetry |
|---|---|---|---|---|
| 2 | 5 | 4 | 2 | 2 |
| 2 | 10 | 3 | 1 | 2 |
| 2 | 20 | 4 | 2 | 2 |
| 2 | 25 | 5 | 3 | 2 |
| 2 | 40 | 5 | 3 | 2 |

### Tier `75-225` (`1..75`, overscan `225`)

- active nodes: `205` / `225`
- edges: `557`
- distinct rewrite labels: `61`

Top hubs:

| node | hub_score |
|---|---|
| 2 | 1461 |
| 6 | 1398 |
| 30 | 1021 |
| 4 | 687 |
| 8 | 476 |
| 3 | 418 |
| 10 | 322 |
| 14 | 310 |
| 12 | 293 |
| 15 | 265 |

Rewrite friction by prime:

| prime | count | min | max | avg_back_cost |
|---|---|---|---|---|
| 2 | 72 | 1 | 1 | 1.0 |
| 3 | 40 | 1 | 3 | 1.4 |
| 5 | 17 | 1 | 5 | 1.941 |
| 7 | 10 | 1 | 9 | 4.6 |

Top asymmetries:

| a | b | d_ab | d_ba | asymmetry |
|---|---|---|---|---|
| 8 | 56 | 9 | 1 | 8 |
| 16 | 56 | 10 | 2 | 8 |
| 32 | 56 | 11 | 3 | 8 |
| 56 | 64 | 4 | 12 | -8 |
| 4 | 28 | 7 | 1 | 6 |

### Tier `100-300` (`1..100`, overscan `300`)

- active nodes: `272` / `300`
- edges: `763`
- distinct rewrite labels: `73`

Top hubs:

| node | hub_score |
|---|---|
| 2 | 2273 |
| 6 | 2197 |
| 30 | 1566 |
| 4 | 1061 |
| 3 | 745 |
| 8 | 732 |
| 14 | 589 |
| 12 | 541 |
| 10 | 532 |
| 16 | 447 |

Rewrite friction by prime:

| prime | count | min | max | avg_back_cost |
|---|---|---|---|---|
| 2 | 98 | 1 | 1 | 1.0 |
| 3 | 54 | 1 | 3 | 1.37 |
| 5 | 22 | 1 | 5 | 1.818 |
| 7 | 13 | 1 | 9 | 4.077 |

Top asymmetries:

| a | b | d_ab | d_ba | asymmetry |
|---|---|---|---|---|
| 8 | 56 | 9 | 1 | 8 |
| 16 | 56 | 10 | 2 | 8 |
| 32 | 56 | 11 | 3 | 8 |
| 56 | 64 | 4 | 12 | -8 |
| 4 | 28 | 7 | 1 | 6 |

### Tier `150-450` (`1..150`, overscan `450`)

- active nodes: `410` / `450`
- edges: `1184`
- distinct rewrite labels: `90`

Top hubs:

| node | hub_score |
|---|---|
| 2 | 4274 |
| 6 | 3831 |
| 30 | 2694 |
| 4 | 2307 |
| 12 | 1463 |
| 8 | 1433 |
| 3 | 1285 |
| 10 | 954 |
| 16 | 948 |
| 60 | 919 |

Rewrite friction by prime:

| prime | count | min | max | avg_back_cost |
|---|---|---|---|---|
| 2 | 148 | 1 | 1 | 1.0 |
| 3 | 82 | 1 | 3 | 1.39 |
| 5 | 35 | 1 | 5 | 2.029 |
| 7 | 19 | 1 | 9 | 3.632 |
| 11 | 2 | 1 | 1 | 1.0 |

Top asymmetries:

| a | b | d_ab | d_ba | asymmetry |
|---|---|---|---|---|
| 16 | 112 | 9 | 1 | 8 |
| 32 | 112 | 10 | 2 | 8 |
| 64 | 112 | 11 | 3 | 8 |
| 112 | 128 | 4 | 12 | -8 |
| 8 | 56 | 7 | 1 | 6 |

### Tier `200-600` (`1..200`, overscan `600`)

- active nodes: `552` / `600`
- edges: `1616`
- distinct rewrite labels: `108`

Top hubs:

| node | hub_score |
|---|---|
| 2 | 6517 |
| 6 | 5742 |
| 30 | 3948 |
| 4 | 3636 |
| 12 | 2503 |
| 8 | 2217 |
| 3 | 1888 |
| 60 | 1607 |
| 16 | 1471 |
| 10 | 1462 |

Rewrite friction by prime:

| prime | count | min | max | avg_back_cost |
|---|---|---|---|---|
| 2 | 198 | 1 | 1 | 1.0 |
| 3 | 109 | 1 | 3 | 1.385 |
| 5 | 48 | 1 | 5 | 2.125 |
| 7 | 24 | 1 | 9 | 3.833 |
| 11 | 2 | 1 | 1 | 1.0 |
| 13 | 2 | 1 | 1 | 1.0 |

Top asymmetries:

| a | b | d_ab | d_ba | asymmetry |
|---|---|---|---|---|
| 16 | 112 | 9 | 1 | 8 |
| 27 | 189 | 9 | 1 | 8 |
| 32 | 112 | 10 | 2 | 8 |
| 64 | 112 | 11 | 3 | 8 |
| 81 | 189 | 10 | 2 | 8 |

## Cross-tier comparison

Baseline hub persistence (baseline top-5 appearing in each tier top-10):

| tier | overlap_count | shared_nodes |
|---|---|---|
| 30-90 | 5 | 2, 3, 4, 6, 30 |
| 50-150 | 5 | 2, 3, 4, 6, 30 |
| 75-225 | 5 | 2, 3, 4, 6, 30 |
| 100-300 | 5 | 2, 3, 4, 6, 30 |
| 150-450 | 5 | 2, 3, 4, 6, 30 |
| 200-600 | 5 | 2, 3, 4, 6, 30 |

Friction monotonicity check (`avg_back_cost` non-decreasing by prime):

| tier | monotonic |
|---|---|
| 30-90 | True |
| 50-150 | False |
| 75-225 | True |
| 100-300 | True |
| 150-450 | False |
| 200-600 | False |

Asymmetry pole evolution (nodes most often in top asymmetric pairs):

| tier | dominant_pole | pole_appearances | strong_pairs_ge_6 |
|---|---|---|---|
| 30-90 | 2 | 4 | 0 |
| 50-150 | 2 | 6 | 0 |
| 75-225 | 56 | 6 | 10 |
| 100-300 | 56 | 6 | 10 |
| 150-450 | 112 | 5 | 10 |
| 200-600 | 112 | 5 | 10 |

Strong asymmetric pairs (`|asymmetry| >= 6`) by tier:

- `75-225`: 8↔56(+8), 16↔56(+8), 32↔56(+8), 56↔64(-8), 4↔28(+6), 4↔56(+6), 8↔28(+6), 9↔63(+6), 16↔28(+6), 24↔56(+6)
- `100-300`: 8↔56(+8), 16↔56(+8), 32↔56(+8), 56↔64(-8), 4↔28(+6), 4↔56(+6), 8↔28(+6), 9↔63(+6), 16↔28(+6), 24↔56(+6)
- `150-450`: 16↔112(+8), 32↔112(+8), 64↔112(+8), 112↔128(-8), 8↔56(+6), 8↔112(+6), 9↔63(+6), 16↔56(+6), 27↔63(+6), 32↔56(+6)
- `200-600`: 16↔112(+8), 27↔189(+8), 32↔112(+8), 64↔112(+8), 81↔189(+8), 112↔128(-8), 8↔56(+6), 8↔112(+6), 9↔63(+6), 9↔189(+6)

### Extended friction tier `50-50000`

High-overscan friction pass (for prime-level return costs only):

| prime | count | min | max | avg_back_cost |
|---|---|---|---|---|
| 2 | 48 | 1 | 1 | 1.0 |
| 3 | 26 | 1 | 3 | 1.308 |
| 5 | 12 | 1 | 5 | 2.167 |
| 7 | 7 | 1 | 5 | 3.571 |
| 11 | 3 | 7 | 7 | 7.0 |
| 13 | 2 | 9 | 9 | 9.0 |

## Interpretation and limits

1. Hub rankings and asymmetry tables are valid only within each tier's
   explicit `(n_max, overscan)` window.
2. Cross-tier overlap measures stability of earlier observations, not
   proof of global structure.
3. Prime-level friction ordering is an empirical pattern in bounded scans;
   it is not a theorem about asymptotic rewrite geometry.
4. Extended friction tiers use large overscan to approximate return paths;
   they are computationally heavier and still bounded.
5. Asymmetry poles can shift with range (e.g. `56` at medium tiers,
   `112` at larger tiers); this is a bounded empirical observation only.

## Non-claims

This report does not claim:

- global hub rankings beyond the stated tiers
- asymptotic friction growth laws
- completeness of PET-METICA geometry
- invariance under all overscan choices
