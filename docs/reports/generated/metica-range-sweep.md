# PET-METICA multi-range sweep

This report compares bounded PET-METICA rewrite scans across several
 `(n_max, overscan)` tiers. Findings are descriptive and bounded.

## Scope

- generated at (UTC): `2026-07-04T17:14:02.709142+00:00`
- report limit: `10`
- scan tiers: `[{'n_max': 30, 'overscan': 90}, {'n_max': 50, 'overscan': 150}, {'n_max': 75, 'overscan': 225}, {'n_max': 100, 'overscan': 300}]`
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

## Cross-tier comparison

Baseline hub persistence (baseline top-5 appearing in each tier top-10):

| tier | overlap_count | shared_nodes |
|---|---|---|
| 30-90 | 5 | 2, 3, 4, 6, 30 |
| 50-150 | 5 | 2, 3, 4, 6, 30 |
| 75-225 | 5 | 2, 3, 4, 6, 30 |
| 100-300 | 5 | 2, 3, 4, 6, 30 |

Friction monotonicity check (`avg_back_cost` non-decreasing by prime):

| tier | monotonic |
|---|---|
| 30-90 | True |
| 50-150 | False |
| 75-225 | True |
| 100-300 | True |

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

## Non-claims

This report does not claim:

- global hub rankings beyond the stated tiers
- asymptotic friction growth laws
- completeness of PET-METICA geometry
- invariance under all overscan choices
