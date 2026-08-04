# PETRA VISION Phase 1 results and limitations

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

## Status

This record concerns the implementation and evidence head validated at
`ee88cec361b673e4a7b9f17de9300344d5c87d06`. Any documentation commit made
afterward is not the tested implementation revision.

Implementation, bounded evidence, independent repair review, and final
consolidated PETRA validation are complete. The complete dossier and exact
pull-request state at `e45f34859d5111317d8847248e55bca71c2b344a` then received
the final independent read-only completion audit, which ended with
`READY TO RECORD PHASE 1 COMPLETION`. Phase 1 is formally complete for the
declared bounded static contract only. The audit found no blocking findings
and no bounded Phase 1 production defect; it confirmed internal consistency
of the implementation, tests, generated evidence, dossier, revision
attribution, and exact remote PR/CI state. It independently recomputed the
110-shape corpus, deterministic records, digests, injectivity, and roundtrips,
and confirmed sound segregation of the abstract grammar, raw-cell traversal,
production codec, and native address resolver. This completion audit did not
rerun the consolidated 1,006-test implementation validation on the later
documentation revision.

## Validated execution evidence

- The dedicated independent evidence-oracle suite passed: 7 passed.
- The focused PETRA VISION suite, after the oracle repair, passed: 566 passed.
- The consolidated canonical PETRA-only suite comprised 12
  `tests/test_petra_*.py` files and passed with 1,006 passed, zero failures,
  in 3.48 seconds.
- Push and pull-request CI both passed on the exact head
  `ee88cec361b673e4a7b9f17de9300344d5c87d06`.
- The repository remained unchanged after the PETRA-only validation.

The recorded duration is execution evidence only. Timing evidence is
diagnostic only and establishes no performance or complexity guarantee.

## Bounded-domain evidence

The exhaustive independently derived corpus contains 110 unique ordered
shapes. Its exact structural-node-occurrence distribution, for counts one
through seven, is `1, 1, 2, 5, 12, 28, 61`. The bounded domain has maximum
width 3, maximum depth 3, and maximum node count 7. The largest observed
canonical geometry has 181 occupied cells and extent 25 × 13.

The direct occupied-cell oracle recorded 574 non-root paths, 110 root
anchors, 574 native term resolutions, 574 native exponent-slot resolutions,
and 1,258 positive native-address resolutions, together with the three
required negative correspondence categories.

The evidence sources have segregated roles:

- The abstract grammar oracle independently enumerates the bounded ordered
  shapes and their structural relations.
- The raw-cell oracle derives path and containment correspondence directly
  from occupied geometry cells, without using production decoding helpers.
- The production encoder is the implementation under test; it produces the
  canonical geometry subjected to roundtrip, determinism, injectivity, and
  malformed-input evidence.
- The native address resolver is an independent compatibility oracle for the
  PETRA adapter boundary; it is not a production geometry dependency.

These results establish the bounded static contract only.

That contract is limited to the 110 ordered-shape kernel domain, maximum
width 3, maximum depth 3, maximum structural-node count 7, the declared
canonical static geometry, the native PETRA adapter subset, and the recorded
malformed-input, dependency, correspondence, complexity, and validation
evidence.

## Repository-wide validation observations

These observations are separate from the PETRA VISION Phase 1 result.

1. A source-path whole-repository run produced 1,809 passed, 1 skipped, and
   1 failed. The failure was the installed legacy `pet` CLI integration test:
   that transient environment contained pytest but not the installed console
   script.
2. A clean installed-package whole-repository run produced 1,759 passed,
   1 skipped, and 51 failed. The failures clustered around the historical
   `pet` import namespace, `python -m pet.cli`, research tools importing
   `pet`, and shell scripts relying on a bare `python`.

These observations expose the already documented incomplete PET-to-PETRA
runtime replacement. They are not evidence of PETRA VISION regressions. The
repository-wide migration must be repaired in a separate prerequisite branch
or workstream. It is not a PETRA VISION Phase 1 requirement, and this record
does not propose permanently installing both namespaces. The final audit
treated this incomplete historical migration as a non-blocking observation,
not a Phase 1 requirement or regression.

## Limitations and non-claims

Phase 1 proves only the bounded static contract. It does not establish:

- correctness outside the 110-shape bounded domain;
- an unbounded or generalized geometric grammar;
- robustness under noise, damage, rotation, scaling, rasterization, physical
  media, or imperfect sensing;
- error correction or recovery guarantees;
- performance or complexity guarantees from timing measurements;
- security, authentication, confidentiality, or cryptographic properties;
- novelty, patentability, freedom to operate, or prior-art clearance;
- physical causation or propagation behavior;
- dynamic fingerprint injectivity or collision freedom;
- production readiness; or
- completion of the repository-wide PET-to-PETRA migration.

The dynamical geometry hypothesis remains unproven, outside the Phase 1
completion gate, and future research. It is collision-tolerant: dynamic
signatures are not assumed to be injective. It is not a security, robustness,
physical-media, or novelty claim.
