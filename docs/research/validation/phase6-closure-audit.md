# PETRA Phase 6 — closure audit

Status: **COMPLETE** for issue #311 under programme #276.

This note records the final consistency check for Phase 6 External Mathematical Validation. It introduces no new theorem and performs no normative promotion.

## 1. Closure criterion

Phase 6 requires substantial Phase 1–5 results to have an explicit provenance state relative to external mathematics. It does **not** require every mathematical question to be solved.

Allowed terminal states include:

- `KNOWN`;
- `SPECIALIZED`;
- `PETRA-INTERNAL`;
- `OPEN`;
- `BOUNDED`.

A remaining `TO-VERIFY` row would indicate unfinished validation work.

## 2. Matrix audit

At closure, the validation matrix contains:

```text
KNOWN             11
SPECIALIZED       15
PETRA-INTERNAL    18
OPEN               2
BOUNDED            0
TO-VERIFY          0
```

The two explicit `OPEN` rows are mathematical questions, not provenance gaps:

- global triviality/classification of `Aut(E_P)`;
- completeness of inverse cancellation + independent commutation for witnessed paths.

They remain open by design.

## 3. Previously unresolved Phase-6 comparisons

The closure audit confirms that the major comparison questions raised during Phase 6 now have explicit outcomes:

- residual-system membership: negative for the current witnessed-edge quotient;
- one-step target-orbit converses: specialized from classical tree-similarity results after the PETRA root-preserving bridge;
- rooted lower-neighbour set reconstruction: false by a size-3 counterexample;
- exact common-REMOVE-reduct distance formula: PETRA-INTERNAL after targeted metric comparison;
- maximum-common-reduct `REMOVE*ADD*` geodesic theorem: PETRA-INTERNAL after targeted comparison.

None of these outcomes implies novelty.

## 4. Provenance boundary

The frozen Phase-6 interpretation is:

```text
KNOWN
    = external mathematics directly matches the audited statement

SPECIALIZED
    = established mathematics specialized/reformulated for PETRA

PETRA-INTERNAL
    = proved internally, but no operation-/convention-exact
      external identification was established

OPEN
    = unresolved mathematical question
```

In particular:

```text
PETRA-INTERNAL != NOVEL
OPEN           != PHASE-6 FAILURE
```

## 5. Non-blocking future research

The following may still be studied later without reopening Phase 6:

- global edit-graph rigidity;
- stronger joint-witness residual semantics;
- witnessed-path completeness;
- finer external classification of PETRA-specific edit/statistic/congruence theorems;
- candidate-specific novelty review before any explicit novelty claim.

## 6. Closure result

All Phase-6 validation rows now have explicit terminal classifications, no unintended `TO-VERIFY` row remains, and the source register no longer lists resolved questions as closure blockers.

Therefore:

```text
PHASE_6_EXTERNAL_MATHEMATICAL_VALIDATION = COMPLETE
```

Phase 7 may begin separately. This closure does not modify the normative PETRA SPEC or runtime.
