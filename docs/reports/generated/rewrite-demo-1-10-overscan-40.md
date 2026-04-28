# PET-METICA canonical demo: 1..10 with overscan 40

This document is the canonical small PET-METICA demo.

It is intentionally small, reproducible, and bounded. It demonstrates the
operational PET-METICA workflow without claiming general theory beyond the
explicit commands shown here.

## Scope

- local-neighbor example: `12`
- rewrite explanation example: `12 -> 9`
- bounded scan range: `1..10`
- overscan domain: `1..40`
- report limit: `3`

## Demo commands

    pet branch-neighbors 12
    pet rewrite explain 12 9 --overscan 120
    pet rewrite friction --n-max 10 --overscan 40 --limit 3
    pet rewrite scan --n-max 10 --overscan 40 --limit 3

## 1. Local rewrite neighborhood

Command:

    pet branch-neighbors 12

Output:

    N = 12
    count = 5
    ---
    12 --NEW(p=5)--> 60
    12 --DROP(p=3)--> 4
    12 --INC(p=2,e=2)--> 24
    12 --INC(p=3,e=1)--> 36
    12 --DEC(p=2,e=2)--> 6

This shows the immediate PET-METICA moves available from `12`.

## 2. Rewrite explanation

Command:

    pet rewrite explain 12 9 --overscan 120

Output:

    source = 12
    target = 9
    reachable = True
    cost = 3
    
    path:
      1. DEC(p=2,e=2): 12 -> 6
         meaning: decrease the exponent structure at p=2,e=2
      2. DROP(p=2): 6 -> 3
         meaning: remove p=2 from the support
      3. INC(p=3,e=1): 3 -> 9
         meaning: increase the exponent structure at p=3,e=1

This demonstrates PET-METICA as a rewrite debugger: the transition `12 -> 9`
is explained as a minimal path of local structural moves, not as ordinary
numeric subtraction.

## 3. Rewrite friction

Command:

    pet rewrite friction --n-max 10 --overscan 40 --limit 3

Output:

    n_max = 10
    overscan = 40
    
    by_label:
      DEC(p=2,e=2): count=1 min=1 max=1 avg=1.0
      DEC(p=2,e=3): count=1 min=1 max=1 avg=1.0
      DEC(p=3,e=2): count=1 min=1 max=1 avg=1.0
      DROP(p=2): count=2 min=1 max=1 avg=1.0
      INC(p=2,e=1): count=1 min=1 max=1 avg=1.0
      INC(p=2,e=2): count=1 min=1 max=1 avg=1.0
      INC(p=3,e=1): count=1 min=1 max=1 avg=1.0
      NEW(x2): count=2 min=1 max=1 avg=1.0
      NEW(x3): count=1 min=3 max=3 avg=3.0
    
    by_prime:
      p=2: count=8 min=1 max=1 avg=1.0
      p=3: count=3 min=1 max=3 avg=1.667
    
    hardest_returns:
      2 --NEW(x3)--> 6: return_cost=3
      5 --NEW(x2)--> 10: return_cost=1
      3 --NEW(x2)--> 6: return_cost=1

This demonstrates local reversibility analysis. The key point is that a one-step
forward move may require a longer return path.

## 4. Bounded rewrite scan

Command:

    pet rewrite scan --n-max 10 --overscan 40 --limit 3

Output:

    stats:
      overscan = 40
      node_count = 40
      active_node_count = 35
      edge_count = 61
      distinct_label_count = 21
      out_of_domain_edges_seen_after_filter = 0
    
    label_counts:
      DEC(p=2,e=2): 5
      DEC(p=2,e=3): 3
      DEC(p=2,e=4): 1
      DEC(p=2,e=5): 1
      DEC(p=3,e=2): 2
      DEC(p=3,e=3): 1
      DEC(p=5,e=2): 1
      DROP(p=2): 9
      DROP(p=3): 6
      DROP(p=5): 3
      DROP(p=7): 1
      INC(p=2,e=1): 5
      INC(p=2,e=2): 3
      INC(p=2,e=3): 1
      INC(p=2,e=4): 1
      INC(p=3,e=1): 2
      INC(p=3,e=2): 1
      INC(p=5,e=1): 1
      NEW(x2): 9
      NEW(x3): 4
      NEW(x5): 1
    
    top_hubs:
      n=6 hub_score=30
      n=4 hub_score=30
      n=2 hub_score=21
    
    largest_positive_gap:
      7 -> 10: pet=9 num=3 gap=6
      7 -> 5: pet=8 num=2 gap=6
      8 -> 10: pet=7 num=2 gap=5
    
    largest_negative_gap:
      3 -> 9: pet=1 num=6 gap=-5
      9 -> 3: pet=1 num=6 gap=-5
      10 -> 2: pet=3 num=8 gap=-5
    
    top_asymmetries:
      4 <-> 10: d(4,10)=6 d(10,4)=2 delta=4
      8 <-> 10: d(8,10)=7 d(10,8)=3 delta=4
      2 <-> 10: d(2,10)=5 d(10,2)=3 delta=2
    
    top_attractors:
      n=4: avg_in=2.375 avg_out=3.143 score=0.768 in=8 out=7
      n=8: avg_in=3.25 avg_out=4.0 score=0.75 in=8 out=7
      n=5: avg_in=4.5 avg_out=4.286 score=-0.214 in=8 out=7
    
    family_report:
      p=2:
        n=2 (2^1): avg_in=3.25 avg_out=2.571 score=-0.679 in=8 out=7
        n=4 (2^2): avg_in=2.375 avg_out=3.143 score=0.768 in=8 out=7
        n=8 (2^3): avg_in=3.25 avg_out=4.0 score=0.75 in=8 out=7
      p=3:
        n=3 (3^1): avg_in=3.5 avg_out=3.143 score=-0.357 in=8 out=7
        n=9 (3^2): avg_in=4.375 avg_out=4.0 score=-0.375 in=8 out=7
      p=5:
        n=5 (5^1): avg_in=4.5 avg_out=4.286 score=-0.214 in=8 out=7
      p=7:
        n=7 (7^1): avg_in=None avg_out=5.75 score=None in=0 out=8
    
    dyadic_trend:
      n=2: score=-0.679 delta_from_prev=None avg_in=3.25 avg_out=2.571
      n=4: score=0.768 delta_from_prev=1.447 avg_in=2.375 avg_out=3.143
      n=8: score=0.75 delta_from_prev=-0.018 avg_in=3.25 avg_out=4.0
    
    one_step_return_costs.by_label:
      DEC(p=2,e=2): count=1 min=1 max=1 avg=1.0
      DEC(p=2,e=3): count=1 min=1 max=1 avg=1.0
      DEC(p=3,e=2): count=1 min=1 max=1 avg=1.0
      DROP(p=2): count=2 min=1 max=1 avg=1.0
      INC(p=2,e=1): count=1 min=1 max=1 avg=1.0
      INC(p=2,e=2): count=1 min=1 max=1 avg=1.0
      INC(p=3,e=1): count=1 min=1 max=1 avg=1.0
      NEW(x2): count=2 min=1 max=1 avg=1.0
      NEW(x3): count=1 min=3 max=3 avg=3.0
    
    one_step_return_costs.by_prime:
      p=2: count=8 min=1 max=1 avg=1.0
      p=3: count=3 min=1 max=3 avg=1.667
    
    one_step_return_costs.hardest_returns:
      2 --NEW(x3)--> 6: return_cost=3
      5 --NEW(x2)--> 10: return_cost=1
      3 --NEW(x2)--> 6: return_cost=1
    
    sample_unreachable:
      1 -> 2
      1 -> 3
      1 -> 4

This demonstrates the bounded scan view: graph stats, hubs, asymmetries,
attractors, family behavior, and one-step return costs.

## Demo conclusions

1. PET-METICA exposes local moves through `NEW`, `DROP`, `INC`, and `DEC`.
2. `12 -> 9` has a readable minimal rewrite explanation.
3. In the bounded `1..10` scan, hubs such as `6`, `4`, and `2` appear.
4. Rewrite transport is directional: some paths are cheaper one way than back.
5. Rewrite friction gives a concrete way to measure local reversibility.

## Non-claims

This demo does not claim:

- global hub rankings
- asymptotic behavior
- general theorems about rewrite distance
- stability beyond the explicit bounded parameters
- completeness of PET-METICA geometry

Its purpose is to provide a small canonical demonstration of the current
PET-METICA operational core.
