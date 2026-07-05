# Experiment — PET-METICA seven-family tier ladder pass

## Status

**Closed** — commit [`f95a437`](https://github.com/gcomneno/pet/commit/f95a437) on `main`
(prior sweep landing: [`8fa42e3`](https://github.com/gcomneno/pet/commit/8fa42e3)).

GitHub Issues are disabled on this repository; this file is the formal closure
record for the pass.

## Scope

Bounded PET-METICA research on the family `7 × {2^k, 3^k}` with:

- multi-tier global rewrite scans (through tier 200)
- targeted seven-family probes (tiers 300, 500, 800, 900, 1200)
- explicit documentation of **tier drift**

No promotion to PET-Base, STATUS, or theorem-level claims.

## Deliverables

| Kind | Path |
|------|------|
| Range sweep tool | `tools/research/pet_metica_range_sweep.py` |
| Seven-family probe | `tools/research/pet_metica_seven_family_probe.py` |
| Tests | `tests/test_metica_range_sweep.py`, `tests/test_metica_seven_family_probe.py` |
| Research note | `docs/research/notes/pet_metica_seven_family_tier_drift.md` |
| Global report | `docs/reports/generated/metica-range-sweep.md` |
| Family reports | `docs/reports/generated/metica-seven-family-{300,500,800,900,1200}.md` |

Local JSON payloads: `docs/reports/data/metica-*.json` (gitignored).

## Scorecard

| claim | tier stability | confidence | verdict |
|-------|----------------|------------|---------|
| `d(7·2^k → 2^k) = 1` on reachable canonical seeds | high across 300–1200 | high | Robust bounded pattern |
| Seven-family dyadic poles scale with range | high | medium-high | Recurrent empirical structure |
| Hub core `{2,3,4,6,30}` in global sweep | high through tier 200 | medium-high | Consistent with earlier METICA reports |
| Canonical seed asymmetry invariant in `k` alone | **low** | high (negative) | **Rejected** — tier drift observed |
| Naive linear asymmetry extrapolation (e.g. +12 at k=7) | low | high (negative) | **Rejected** at tier 900/1200 |
| Pole vs hub role coincidence | low | medium | High-asymmetry poles can have hub_score 0 |

## Key correction acquired

**Tier drift:** for fixed `k`, measured canonical asymmetry can decrease as
`n_max` grows (with proportional overscan). Example:

| pair | tier 900 | tier 1200 |
|------|----------|-----------|
| `(128, 896)` | asymmetry +10 | asymmetry +8 |

Every reported value must cite `(n_max, overscan)`.

## Verification

```bash
pytest tests/test_metica_range_sweep.py tests/test_metica_seven_family_probe.py -q
make docs-check
```

## Open frontiers (not closed by this pass)

1. Explicit model `asymmetry(k, n_max, overscan)`
2. Tier ≥ 1792 for `7·2^8 = 1792`
3. Triadic branch (`567`, …) at larger ranges
4. Connection to prime-level friction hierarchy in `pet_metica_claims_snapshot.md`

## Bottom line

The pass succeeds as **bounded empirical research**: tooling is reproducible,
artifacts exist, and the main scientific output is as much the **tier-drift
correction** as the seven-family pole structure itself.

Further METICA promotion requires a new pass with explicit stabilization
criteria — not extrapolation from this ladder alone.
