# PET Backbone Atlas — Research Notes

Status: draft research note  
Scope: PET-METICA / ATLAS / routing overhead  
Mode: docs-only, claim-safe  
Baseline: PET v0.1.5

---

## 1. Executive summary

Recent CLI exploration showed a stable distinction between two rewrite views:

- **canonical rewrite** measures routed structural friction through the PET canonical geography;
- **target-aware rewrite** measures direct structural edits between source and target;
- **optimization_gap** exposes the overhead paid by canonical routing compared to the direct target-aware edit path.

Working formula:

```text
optimization_gap = canonical_cost - target_aware_cost
```

Interpretation:

```text
optimization_gap = structural toll of canonical routing
```

In PET-METICA terms:

```text
canonical rewrite = routed PET geography
target-aware rewrite = direct support/exponent edit
gap = backbone routing overhead
```

---

## 2. Claim-safe boundary

This note does **not** claim that PET:

- solves integer factorization;
- solves primality testing;
- breaks semiprimes;
- replaces PET-Base;
- provides a final mathematical theory.

This note describes observed, bounded, CLI-tested behavior of PET-METICA rewrite paths.

PET-METICA remains an operational, bounded, research-facing layer.

---

## 3. Current stable baseline

Relevant release timeline:

| tag | meaning |
|---|---|
| `v0.1.3` | target-aware rewrite explain |
| `v0.1.4` | fix `NEW_TARGET + INC` for new target primes with exponent > 1 |
| `v0.1.5` | fix `DEC + DROP` for removed source primes with exponent > 1 |

After `v0.1.5`, target-aware rewrite handles:

```text
missing target prime:
  NEW_TARGET(p)
  then INC(p,e=...) until target exponent

removed source prime:
  DEC(p,e=...) down to exponent 1
  then DROP(p)

shared prime:
  INC/DEC unit steps as needed
```

---

## 4. Core distinction

### Canonical rewrite

Canonical rewrite follows the PET canonical graph.

It tends to route through primorial-like backbone supports:

```text
2 -> 6 -> 30 -> 210 -> 2310 -> 30030 -> ...
```

This can introduce temporary primes that are not present in the final target.

### Target-aware rewrite

Target-aware rewrite uses the target support explicitly.

It performs direct structural edits:

```text
DROP extra source primes
NEW_TARGET missing target primes
INC/DEC exponent differences
```

It does not replace canonical distance. It exposes a second, target-informed explanation.

---

## 5. Backbone hypothesis

Observed canonical paths strongly suggest a primorial backbone:

```text
2, 6, 30, 210, 2310, 30030, ...
```

These behave like structural hubs.

Example:

```text
2 -> 210
canonical_cost = 3
target_aware_cost = 3
optimization_gap = 0
```

Path:

```text
2 -> 6 -> 30 -> 210
```

When the target is aligned with the backbone prefix, canonical and target-aware often coincide.

---

## 6. Non-prefix target supports

When the target support is a non-prefix subset of the backbone, canonical tends to climb to a larger backbone hub and then drop extra primes.

Example:

```text
2 -> 70
70 = 2 · 5 · 7
```

Canonical:

```text
2 -> 6 -> 30 -> 210 -> 70
```

Target-aware:

```text
2 -> 10 -> 70
```

Observed:

```text
canonical_cost = 4
target_aware_cost = 2
optimization_gap = 2
```

Interpretation:

```text
extra backbone prime = 3
gap = NEW(3) + DROP(3) = 2
```

---

## 7. Backbone routing overhead

Working term:

```text
backbone routing overhead
```

Definition candidate:

```text
backbone_routing_overhead(src, dst) =
  canonical_cost(src, dst) - target_aware_cost(src, dst)
```

when both costs are available.

If canonical is not reachable inside the bounded graph, then the gap is undefined:

```text
canonical_cost = None
optimization_gap = None
```

This case can be treated separately as a bounded reachability lift.

---

## 8. Directional structural friction

Canonical rewrite is directional.

Example:

```text
22 -> 3718
3718 -> 22
```

where:

```text
22   = 2 · 11
3718 = 2 · 11 · 13²
```

Observed:

| direction | canonical | target-aware | gap |
|---|---:|---:|---:|
| `22 -> 3718` | `8` | `2` | `6` |
| `3718 -> 22` | `2` | `2` | `0` |

Interpretation:

- adding high target prime `13` requires canonical backbone routing;
- removing high prime `13` is direct.

Working term:

```text
directional structural friction
```

Candidate metric:

```text
canonical_asymmetry(a, b) =
  canonical_cost(a -> b) - canonical_cost(b -> a)
```

or:

```text
gap_asymmetry(a, b) =
  gap(a -> b) - gap(b -> a)
```

---

## 9. Exponent-only axis

Pure exponent changes are gap-free.

Example:

```text
2 -> 4096
4096 -> 2
```

where:

```text
4096 = 2¹²
```

Observed:

| direction | canonical | target-aware | gap |
|---|---:|---:|---:|
| `2 -> 4096` | `11` | `11` | `0` |
| `4096 -> 2` | `11` | `11` | `0` |

Interpretation:

```text
INC/DEC unit exponent steps are already local and direct.
```

So exponent distance alone does not create routing overhead.

---

## 10. Temporary exponent normalization

Some canonical paths temporarily lower an exponent that is already correct in both source and target, then restore it after backbone traversal.

Example:

```text
24 -> 4056
24   = 2³ · 3
4056 = 2³ · 3 · 13²
```

Observed:

```text
canonical_cost = 12
target_aware_cost = 2
optimization_gap = 10
```

Canonical includes:

```text
DEC(p=2,e=3): 24 -> 12
DEC(p=2,e=2): 12 -> 6
...
INC(p=2,e=1)
INC(p=2,e=2)
```

Target-aware only does:

```text
NEW_TARGET(p=13)
INC(p=13,e=1)
```

Interpretation:

```text
canonical normalizes 2³ · 3 down to 2 · 3 before ascending the backbone,
then reconstructs the exponent afterward.
```

Working term:

```text
backbone ascent normalization
```

Candidate decomposition:

```text
optimization_gap =
  support backbone detour
  + temporary exponent normalization detour
```

For `24 -> 4056`:

```text
support detour: {5,7,11} = 6 steps
normalization detour: 2³ -> 2 -> 2³ = 4 steps
gap = 10
```

---

## 11. Compact observed table

Representative CLI results:

| pair | canonical | target-aware | gap |
|---|---:|---:|---:|
| `2 -> 4096` | `11` | `11` | `0` |
| `4096 -> 2` | `11` | `11` | `0` |
| `18 -> 2178` | `6` | `2` | `4` |
| `2178 -> 18` | `2` | `2` | `0` |
| `18 -> 3042` | `10` | `2` | `8` |
| `3042 -> 18` | `2` | `2` | `0` |
| `24 -> 4056` | `12` | `2` | `10` |
| `4056 -> 24` | `2` | `2` | `0` |
| `9 -> 169` | `12` | `4` | `8` |
| `169 -> 9` | `6` | `4` | `2` |
| `25 -> 169` | `12` | `4` | `8` |
| `169 -> 25` | `8` | `4` | `4` |
| `49 -> 169` | `12` | `4` | `8` |
| `169 -> 49` | `10` | `4` | `6` |
| `49 -> 121` | `10` | `4` | `6` |
| `121 -> 49` | `10` | `4` | `6` |

---

## 12. Friction scan confirmation

The command:

```bash
python -m pet.cli rewrite friction --n-max 50 --overscan 50000 --limit 20
```

showed increasing friction by prime:

```text
p=2  avg=1.0
p=3  avg=1.308
p=5  avg=2.167
p=7  avg=3.571
p=11 avg=7.0
p=13 avg=9.0
```

This supports the backbone routing interpretation:

```text
higher primes are costlier to reconstruct canonicaly after being dropped.
```

`INC` and `DEC` remained average `1.0`, reinforcing that exponent moves themselves are local.

---

## 13. Bounded reachability lift

Target-aware can explain paths that canonical cannot find within a given `--overscan`.

Example class:

```text
canonical_reachable = False
target_aware_reachable = True
```

This should be treated separately from a numeric gap.

Working term:

```text
reachability lift
```

Research questions:

- Is canonical unreachable only because the needed primorial hub exceeds `--overscan`?
- Can the required overscan be predicted from the largest target prime?
- Can the minimal necessary backbone hub be estimated from support data?

---

## 14. Partial PET / opaque residuals

PET does not solve factorization.

For opaque huge numbers:

```text
N = P · Q
```

where `P` and `Q` are unknown huge primes, PET cannot recover the structure without factoring `N`.

However, PET can still be useful with partial structure:

```text
N = known_factors · R
```

where `R` is an opaque residual.

Candidate representation:

```text
PET partial structure:
  known branches:
    p1^e1
    p2^e2
  opaque residual:
    R
```

Research direction:

```text
PET with opaque residuals
```

Possible operations:

- factor peeling using small primes;
- `gcd(N, known_generator)`;
- divisibility checks;
- partial structural delta;
- target-aware partial explanations;
- explicit unknown/opaque branch accounting.

Claim-safe formulation:

```text
PET can analyze known or partially known multiplicative structure.
PET cannot infer hidden factorization for free.
```

---

## 15. Proposed research tracks

### Track A — PET Backbone Atlas

Goal:

```text
Map the canonical PET geography:
hub nodes, backbone prefixes, side branches, cul-de-sacs, bridge nodes.
```

Candidate outputs:

- atlas tables;
- gap heatmaps;
- hub frequency reports;
- friction summaries by prime/support;
- examples of directional routing.

### Track B — Routing overhead metric

Goal:

```text
Treat optimization_gap as a first-class research metric.
```

Candidate names:

```text
routing_overhead
backbone_routing_overhead
structural_toll
```

Recommended name for now:

```text
backbone_routing_overhead
```

### Track C — Directional friction

Goal:

```text
Study asymmetry in canonical rewrite.
```

Candidate metrics:

```text
canonical_asymmetry(a,b)
gap_asymmetry(a,b)
```

### Track D — Backbone ascent normalization

Goal:

```text
Understand when canonical lowers exponents before backbone traversal.
```

Candidate metric:

```text
normalization_detour_cost
```

### Track E — Opaque residual PET

Goal:

```text
Support partial multiplicative structure without pretending to factor huge semiprimes.
```

Candidate term:

```text
opaque residual
```

---

## 16. Non-goals for now

Do not immediately implement:

- new CLI commands;
- release work;
- refactors;
- PET-Base changes;
- factorization features;
- claims about breaking semiprimes.

Recommended next step is docs-only consolidation.

---

## 17. Possible future docs file

If promoted into the repository later, a reasonable location would be:

```text
docs/reports/pet-backbone-atlas-notes.md
```

Suggested structure:

```text
1. Summary
2. Claim-safe boundaries
3. Canonical vs target-aware rewrite
4. Backbone routing examples
5. Optimization gap
6. Directional friction
7. Exponent normalization
8. Friction scan evidence
9. Opaque residuals
10. Future research tracks
```

---

## 18. One-line takeaway

```text
PET-METICA canonical rewrite measures routed structural friction through the PET backbone;
target-aware rewrite measures direct structural edits;
their gap exposes the structural toll paid by canonical routing.
```
