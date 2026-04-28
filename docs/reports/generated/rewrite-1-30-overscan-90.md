# PET-METICA rewrite report: 1..30 with overscan 90

This report summarizes a bounded PET-METICA rewrite scan.

The report is descriptive and bounded. It does not claim asymptotic behavior,
global hub structure, or general theorems beyond the explicit scan parameters.

## Scope

- source range: `1..30`
- overscan domain: `1..90`
- report limit: `10`
- command:

    pet rewrite scan --n-max 30 --overscan 90 --limit 10 --json

## Graph stats

- node count: `90`
- active node count: `79`
- edge count: `155`
- distinct label count: `31`
- out-of-domain edges after filter: `0`

## Top hubs

These nodes occur most often as internal nodes of canonical shortest rewrite
paths among pairs in the bounded source range.

| node | hub_score |
|---|---|
| 4 | 239 |
| 6 | 156 |
| 2 | 98 |
| 12 | 93 |
| 30 | 75 |
| 3 | 60 |
| 20 | 60 |
| 15 | 58 |
| 8 | 58 |
| 9 | 55 |

## Top asymmetries

These pairs show the largest directional difference between `d(a,b)` and
`d(b,a)` in the bounded scan.

| a | b | d_ab | d_ba | asymmetry | abs_asymmetry |
|---|---|---|---|---|---|
| 6 | 30 | 1 | 5 | -4 | 4 |
| 2 | 10 | 5 | 3 | 2 | 2 |
| 2 | 20 | 4 | 2 | 2 | 2 |
| 4 | 5 | 5 | 3 | 2 | 2 |
| 4 | 10 | 4 | 2 | 2 | 2 |
| 4 | 20 | 3 | 1 | 2 | 2 |
| 4 | 25 | 6 | 4 | 2 | 2 |
| 5 | 6 | 5 | 3 | 2 | 2 |
| 5 | 15 | 3 | 1 | 2 | 2 |
| 5 | 18 | 6 | 4 | 2 | 2 |

## Top attractors

Attractor score compares average outgoing and incoming rewrite distances in
the bounded pair scan.

| node | avg_in | avg_out | attractor_score | incoming_count | outgoing_count |
|---|---|---|---|---|---|
| 4 | 2.577 | 3.062 | 0.486 | 26 | 16 |
| 8 | 3.385 | 3.75 | 0.365 | 26 | 16 |
| 16 | 4.346 | 4.688 | 0.341 | 26 | 16 |
| 30 | 3.615 | 3.5 | -0.115 | 26 | 16 |
| 9 | 4.269 | 3.812 | -0.457 | 26 | 16 |
| 27 | 5.231 | 4.75 | -0.481 | 26 | 16 |
| 2 | 3.538 | 3.0 | -0.538 | 26 | 16 |
| 12 | 3.077 | 2.5 | -0.577 | 26 | 16 |
| 24 | 3.885 | 3.188 | -0.697 | 26 | 16 |
| 6 | 3.5 | 2.562 | -0.938 | 26 | 16 |

## Rewrite friction by prime

Rewrite friction is measured as the shortest return cost after a one-step local
rewrite. These values are bounded observations over the scan parameters.

| prime | count | min_back_cost | max_back_cost | avg_back_cost |
|---|---|---|---|---|
| 2 | 28 | 1 | 1 | 1.0 |
| 3 | 13 | 1 | 3 | 1.769 |
| 5 | 4 | 1 | 5 | 2.5 |

## Hardest one-step returns

These are the highest return-cost one-step rewrites observed in this bounded
scan.

| src | forward_label | dst | back_cost |
|---|---|---|---|
| 6 | NEW(x5) | 30 | 5 |
| 10 | NEW(x3) | 30 | 3 |
| 2 | NEW(x3) | 6 | 3 |
| 20 | DROP(p=5) | 4 | 3 |
| 21 | DROP(p=3) | 7 | 3 |
| 15 | DROP(p=3) | 5 | 3 |
| 18 | DEC(p=3,e=2) | 6 | 3 |
| 8 | NEW(x3) | 24 | 1 |
| 4 | NEW(x3) | 12 | 1 |
| 15 | NEW(x2) | 30 | 1 |

## Label-level friction highlights

| label | count | min_back_cost | max_back_cost | avg_back_cost |
|---|---|---|---|---|
| DEC(p=2,e=2) | 4 | 1 | 1 | 1.0 |
| DEC(p=2,e=3) | 2 | 1 | 1 | 1.0 |
| DEC(p=2,e=4) | 1 | 1 | 1 | 1.0 |
| DEC(p=3,e=2) | 2 | 1 | 3 | 2.0 |
| DEC(p=3,e=3) | 1 | 1 | 1 | 1.0 |
| DEC(p=5,e=2) | 1 | 1 | 1 | 1.0 |
| DROP(p=2) | 7 | 1 | 1 | 1.0 |
| DROP(p=3) | 4 | 1 | 3 | 2.0 |
| DROP(p=5) | 1 | 3 | 3 | 3.0 |
| INC(p=2,e=1) | 4 | 1 | 1 | 1.0 |
| INC(p=2,e=2) | 2 | 1 | 1 | 1.0 |
| INC(p=2,e=3) | 1 | 1 | 1 | 1.0 |
| INC(p=3,e=1) | 1 | 1 | 1 | 1.0 |
| INC(p=3,e=2) | 1 | 1 | 1 | 1.0 |
| INC(p=5,e=1) | 1 | 1 | 1 | 1.0 |
| NEW(x2) | 7 | 1 | 1 | 1.0 |
| NEW(x3) | 4 | 1 | 3 | 2.0 |
| NEW(x5) | 1 | 5 | 5 | 5.0 |

## Bounded conclusions

1. The strongest hubs in this scan are `4`, `6`, `2`, `12`, and `30`.
2. Rewrite distance is visibly directional. For example, `6 -> 30` has cost `1`,
   while `30 -> 6` has cost `5`.
3. The hardest observed one-step return is `6 --NEW(x5)--> 30`, with return
   cost `5`.
4. Prime-level friction is not uniform in this bounded scan. Larger involved
   primes can produce higher return costs, but this remains a bounded
   empirical observation.

## Non-claims

This report does not claim:

- global hub rankings beyond `1..30`
- asymptotic behavior
- a theorem about friction growth by prime
- completeness of PET-METICA geometry
- stability under all overscan choices

The purpose of this report is to provide a reproducible bounded artifact for
PET-METICA development.
