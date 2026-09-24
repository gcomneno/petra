# PETRA Phase 6 — state-dependent residuals and commuting squares

Status: **Phase 6 external-validation note** for issue #301 under programme #276.

This note compares PETRA's state-dependent witnessed-edit transport with residual theory from rewriting. It does not modify the normative PETRA specification.

## 1. Motivation

Trace theory models partial commutation with a fixed action alphabet and a fixed independence relation. PETRA witnessed edits are state-typed, so the second step in a commuting square is generally not literally the same witness after the first step.

Residual theory is closer because it explicitly studies what remains of one coinitial rewrite step after another has been performed.

## 2. PETRA square and residual notation

PETRA's independent-edit theorem has the shape:

```text
P --e1--> P1
|          |
e2         e2/e1
v          v
P2 --e1/e2-> Q
```

The notation `e2/e1` and `e1/e2` is residual-theoretic in spirit: the second witnessed edit is transported into the state produced by the first.

## 3. External prior art

Melliès' axiomatic residual theory treats residuals and permutation equivalence between rewriting paths as part of a general algebraic theory of conflict-free rewriting.

Bruggink constructs residual machinery for a concrete higher-order rewriting formalism using witnessed reductions / proof terms.

Glauert and Khasidashvili define deterministic residual structures as abstract reduction systems equipped with axiomatized residual relations.

Therefore coinitial steps, residuals, commuting completion diagrams, and permutation equivalence of reductions are established prior art.

## 4. Operation-level comparison

| Concept | Residual theory | PETRA |
| --- | --- | --- |
| state | rewrite object / term | rooted unordered PETRA form |
| step | redex contraction | witnessed ADD/REMOVE |
| coinitial steps | two reductions from same object | two witnessed edits from same form |
| residual | transformed remaining redex after a step | transported second witness after first edit |
| square | residual/confluence diagram | independent-edit commuting square |
| path equivalence | permutation equivalence | PETRA `≡comm` candidate relation |
| conflicts | framework-dependent | PETRA non-independent edits |
| persistent identity | not required in general | explicitly absent from carrier |

The analogy is strong at the diagrammatic level.

## 5. Axiom audit status

PETRA is **not yet classified** as a Stable Deterministic Residual Structure or any other named residual-system class.

The current definitions/proofs establish selected commuting squares, but the full residual-system package has not been checked: residual existence, uniqueness versus multiplicity, self-residual behaviour, erasure/duplication, coherence of iterated residuals, stability/conflict-freedom hypotheses, and the exact permutation-equivalence theorem.

Thus PETRA witnessed residual transport as an instance of a standard residual system remains **TO-VERIFY**.

## 6. What is already safe to classify

```text
generic residual transport                 KNOWN
generic permutation equivalence            KNOWN
PETRA residual-shaped commuting square     PETRA-INTERNAL theorem with known analogue
PETRA exact independence criterion         PETRA-INTERNAL
PETRA residual-system membership           TO-VERIFY
```

No item labelled PETRA-INTERNAL is a novelty claim.

## 7. Multiplicity and occurrence witnesses

PETRA may contain repeated isomorphic child subtrees. Unpointed edit effects can therefore collapse distinct occurrence-level actions.

Residual theory requires enough information to track what becomes of a particular step after another step. PETRA's occurrence-sensitive witnesses are therefore the correct level for this comparison.

The absence of persistent identity in the carrier is not itself a blocker, but well-definedness under rooted-tree isomorphism must be part of any future residual-system proof.

## 8. Relation to trace theory

Trace theory and residual theory remain distinct in the validation matrix: trace theory uses fixed actions plus fixed independence and swaps; residual theory uses state-sensitive steps plus residual transport and permutation equivalence.

PETRA is currently closer to the second pattern.

## 9. Completeness remains open

The internal question whether inverse cancellation plus independent commutation is complete for equal witnessed path effects is still **OPEN**.

Residual-theory completeness/permutation-equivalence results require specific axioms and conflict assumptions that have not been established for PETRA as a whole.

## 10. Phase-6 result

```text
free category                              SPECIALIZED
free groupoid under inverse cancellation   SPECIALIZED
generic trace commutation                   KNOWN
generic residual theory                     KNOWN
PETRA residual-system membership            TO-VERIFY
PETRA exact independence criterion          PETRA-INTERNAL
local-presentation completeness             OPEN
```

The next step is a formal residual-system axiom audit against PETRA's witnessed edit definitions. No Phase-7 promotion follows automatically.
