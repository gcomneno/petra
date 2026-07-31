# Legacy Operator Occurrence Inventory — Phase 1

> **Audit record, not operator semantics.** The tokens `NEW`, `DROP`, `INC`,
> and `DEC` in this inventory identify legacy material only. Their use here
> does not define active PET semantics.

## Scope and method

This Phase 1 inventory was taken from commit
`25be76443f7724b9f96b6464d9e16066142b6f5e` before the documentation-boundary
edits for issue #165. It inventories exact whole-word uppercase occurrences in
Markdown and text documentation with:

```bash
rg -n -w -o -e 'NEW' -e 'DROP' -e 'INC' -e 'DEC' docs ROADMAP.md
```

The search found 553 occurrences: 549 under `docs/` and 4 in `ROADMAP.md`.
Counts are occurrences, not claims: a generated example can contain several
tokens on one line.

To reproduce the per-file counts in the table, run this from the repository
root (the recorded commit is the pre-change baseline):

```bash
baseline=25be76443f7724b9f96b6464d9e16066142b6f5e
git ls-tree -r --name-only "$baseline" -- docs ROADMAP.md \
  | rg -P '\.(?:md|txt)$' \
  | sort \
  | while read -r file; do
      count=$(git show "$baseline:$file" | rg -o -P '\b(?:NEW|DROP|INC|DEC)\b' | wc -l)
      if [ "$count" -gt 0 ]; then
        printf '%4d %s\n' "$count" "$file"
      fi
    done
```

## Classification and Phase 1 decision

Each pre-change file is assigned one primary, reproducible treatment for all
of its occurrences. No directory inherits a classification:

- **A — active semantic guidance/navigation:** remove the legacy vocabulary.
- **S — supersession/compatibility evidence:** retain only in the object-native
  contract, where it records what that contract supersedes.
- **H — historical or superseded research evidence:** retain with an explicit
  legacy/supersession boundary.
- **C — current executable legacy compatibility:** retain as an accurate record
  of the implemented value-level behavior, with an explicit non-canonical
  boundary.
- **G — generated provenance:** retain unchanged; regeneration is out of scope.

| Class | File | Pre-change occurrences |
| --- | --- | ---: |
| A | `ROADMAP.md` | 4 |
| A | `docs/VISION.md` | 4 |
| A | `docs/foundations/README.md` | 4 |
| A | `docs/reference/CLI.md` | 4 |
| A | `docs/reference/SPEC.md` | 4 |
| A | `docs/reports/STATUS.md` | 4 |
| S | `docs/foundations/../reference/SPEC.md` | 24 |
| H | `docs/foundations/operator-addresses.md` | 40 |
| H | `docs/foundations/operator-algebra.md` | 8 |
| H | `docs/foundations/path-history.md` | 3 |
| H | `docs/foundations/pet-core-v0.md` | 14 |
| C | `docs/foundations/operator-semantics-snapshot.md` | 37 |
| C | `docs/foundations/pet-first-principles-implementation-audit.md` | 4 |
| C | `docs/foundations/pet-module-stability-classification.md` | 4 |
| C | `docs/foundations/pet-peg-2.0-baseline.md` | 11 |
| C | `docs/foundations/pet-peg-2.0-core-pillars.md` | 4 |
| C | `docs/foundations/pet-peg-2.0-graph-path-traversal.md` | 21 |
| C | `docs/foundations/pet-peg-2.0-operator-semantics-promotion-policy.md` | 4 |
| C | `docs/foundations/pet-peg-2.0-operator-semantics.md` | 41 |
| C | `docs/foundations/pet-peg-2.0-traces-certificates.md` | 2 |
| C | `docs/notes/pet-lens-transition.md` | 8 |
| C | `docs/notes/pet-local-probe-proposal.md` | 53 |
| C | `docs/reports/process/canonical-workflow.md` | 2 |
| C | `docs/reports/process/pet-backbone-atlas-research-notes.md` | 22 |
| C | `docs/reports/process/tooling-classification.md` | 2 |
| G | `docs/reports/generated/rewrite-1-30-overscan-90.md` | 29 |
| G | `docs/reports/generated/rewrite-demo-1-10-overscan-40.md` | 57 |
| H | `docs/research/PET_BACKBONE_LANDMARK_PROJECTION.md` | 4 |
| C | `docs/research/README.md` | 6 |
| H | `docs/research/archive/pet-shape-algebra-v0.md` | 18 |
| C | `docs/research/notes/PET-METICA.md` | 38 |
| H | `docs/research/notes/pet_metica_plus_candidate_examples.md` | 1 |
| H | `docs/research/notes/pet_metica_plus_case_2_6_30.md` | 7 |
| C | `docs/research/notes/pet-grammar-note.md` | 37 |
| C | `docs/research/notes/pet_metica_claims_snapshot.md` | 7 |
| C | `docs/research/notes/pet_metica_minimal_definitions.md` | 8 |
| C | `docs/research/notes/pet_metica_operational_semantics.md` | 5 |
| H | `docs/research/pet_syntax_tree.md` | 8 |

| Class | Files | Pre-change occurrences |
| --- | ---: | ---: |
| A — active semantic guidance/navigation | 6 | 24 |
| S — object-native supersession/compatibility evidence | 1 | 24 |
| H — historical or superseded research evidence | 9 | 103 |
| C — current executable legacy compatibility | 20 | 316 |
| G — generated provenance | 2 | 86 |
| **Total** | **38** | **553** |

The table is a primary-treatment classification, not a mechanical rename: a
current compatibility document can also preserve historical evidence. The
listed class determines its Phase 1 boundary and makes each retained file
independently auditable.

## Retained evidence with direct semantic relevance

The following foundation records are retained because they explain the
superseded prime-label/value-level model or its migration boundary. They must
not be used as a normative operator reference:

- `../foundations/pet-peg-2.0-operator-semantics.md`
- `../foundations/operator-semantics-snapshot.md`
- `../foundations/pet-peg-2.0-baseline.md`
- `../foundations/operator-addresses.md`
- `../foundations/pet-peg-2.0-operator-semantics-promotion-policy.md`

The object-native contract itself intentionally retains its 24 occurrences as
supersession and implementation-compatibility evidence. Those mentions are
historical comparators, not invocations or current rules.

## Acceptance rule

After Phase 1, an occurrence of a legacy token is acceptable only when its
document role is generated provenance, historical/archive evidence, or an
explicit implementation-compatibility reference. No active navigation,
specification, vision, roadmap, status claim, or public CLI description may
present it as current PET semantics. The normative reference is
[`../reference/SPEC.md`](../reference/SPEC.md).

## Deferred to Phase 2

Runtime/operator APIs, CLI labels and behavior, graph/rewrite behavior,
research tools, fixtures, snapshots, tests, and generated reports are outside
this documentation-only phase. Their future disposition requires a separate
runtime and generated-artifact migration decision.
