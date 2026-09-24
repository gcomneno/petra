# PETRA Phase 6 — residual-system axiom audit

Status: **Phase 6 formal validation audit** for issue #303 under programme #276.

This note audits the current PETRA witnessed-edit semantics against the abstract residual-system definition used by Bruggink (2003), while retaining the broader Melliès / deterministic-residual-structure context. It does not change the normative PETRA SPEC.

## 1. External audit target

Bruggink's Definition 2.4 treats a residual system as an abstract rewriting system equipped with identities and a projection operator `/` defined for **every pair of coinitial steps**. Besides source/target compatibility, the projection satisfies:

```text
1 / phi = 1
phi / 1 = phi
phi / phi = 1
(phi/psi)/(chi/psi) = (phi/chi)/(psi/chi)
```

The final equation is the residual cube law. Residual systems with composition satisfy additional projection/composition laws.

This is a stronger requirement than merely having some commuting squares.

## 2. PETRA levels that must not be conflated

PETRA currently has three relevant levels:

1. concrete realization occurrences;
2. individual witnessed-edit classes, where a target occurrence is quotiented by witness-respecting rooted-tree isomorphism;
3. unpointed form-level edges.

The Phase-5 independent-edit theorem is proved at level 1 and then yields equal endpoint forms. A residual-system operator, however, must be a well-defined operation on whatever set of steps is chosen for the abstract rewriting system.

## 3. Audit summary

| Audit item | Result | Reason |
| --- | --- | --- |
| A1 coinitiality / residual domain | **PARTIAL** | PETRA residual transport is defined only for realization-level independent pairs, not every coinitial pair. |
| A2 residual existence | **PARTIAL** | All four ADD/REMOVE pair types have residuals under PETRA's independence criterion; conflicting pairs need not have an elementary residual square. |
| A3 residual uniqueness | **FAIL** on current `W_P` quotient | Automorphism-quotiented edge classes can represent either the same occurrence or distinct symmetric occurrences, so pairwise residual behaviour is not determined by the two edge classes alone. |
| A4 self residual | **FAIL** on current `W_P` quotient | The standard `phi/phi = 1` law conflicts with the possibility that two distinct symmetric realization-level edits collapse to the same witnessed edge class. |
| A5 erasure / conflict | **PASS** as a classification, **FAIL** for totality | Same-target ADD/REMOVE is a genuine conflict: one order destroys removability and the other destroys the ADD target. Current partial residual semantics leaves such pairs outside its domain. |
| A6 duplication | **PASS** at realization level | ADD/REMOVE never copies an existing occurrence. They may create new redex opportunities, but do not duplicate an existing witnessed target. |
| A7 iterated residual coherence | **PARTIAL** | The cube law holds for triples of pairwise compatible distinct original targets by order-independence; it is not established on all coinitial witnessed-edge classes. |
| A8 DRS / SDRS membership | **FAIL** for current `W_P` | A total well-defined residual relation is already missing, so stronger deterministic/stable residual-structure labels are not justified. |
| A9 permutation equivalence | **PARTIAL** | PETRA `≡comm` matches the residual-style swap generator on the verified independent realization-level fragment only. |
| A10 local-presentation completeness | **OPEN** | Nothing in this audit proves completeness of cancellation + commutation for equal endpoint effects. |

## 4. A1 — coinitiality domain

For an abstract rewriting system, two steps are coinitial when they have the same source object.

For PETRA realization-level edits on one concrete realization `T`, the current independence domain is narrower:

- ADD/ADD: distinct existing target occurrences;
- REMOVE/REMOVE: distinct removable leaf occurrences;
- ADD/REMOVE: the ADD target is not the leaf being removed;
- REMOVE/ADD: symmetric condition.

Phase 5 proves residual-style transport only on this domain.

Therefore the PETRA residual operator is presently **partial with respect to ordinary coinitiality**.

## 5. A2 — residual existence by pair type

### ADD / ADD

For distinct existing targets, each target survives the other ADD. The second ADD transports uniquely at realization level. **PASS on the independent domain.**

Two ADDs at the same existing occurrence also have an obvious realization-level two-leaf completion, but PETRA intentionally does not classify that pair as independent, so it is outside the current `≡comm` generator set.

### REMOVE / REMOVE

For distinct leaf occurrences, removing either leaves the other removable. **PASS on the independent domain.**

For the same concrete leaf, the standard residual-system convention would require self-residual `= identity`; PETRA has not defined that as part of its elementary residual transport.

### ADD / REMOVE

If the ADD target differs from the removed leaf, both targets survive appropriately and the square exists. **PASS on the independent domain.**

If the ADD targets the very leaf removed by the other step, there is no elementary commuting square: ADD first makes that original leaf non-removable, while REMOVE first destroys the ADD target. This is a genuine conflict for the current elementary-step system.

### REMOVE / ADD

Symmetric to ADD/REMOVE. **PASS on the independent domain; conflicting at the same target leaf.**

## 6. A3/A4 — decisive witness-quotient obstruction

Consider

```text
P = Node({Z, Z}).
```

The two leaf children are exchanged by an automorphism of `P`. Therefore removing the left leaf and removing the right leaf define the **same witnessed REMOVE edge class** in `W_P`; call it `r`.

At realization level there are nevertheless two different situations:

1. residualizing one concrete removal against itself should erase it, corresponding to `r/r = identity`;
2. removing the two distinct symmetric leaves is an independent pair, and after the first removal the residual of the other is another REMOVE step, not an identity.

Both situations collapse to the same ordered pair of witnessed edge classes `(r,r)`. Hence a binary residual operator on current `W_P` edge classes cannot recover which case occurred.

This is not merely a missing proof. It is a concrete information-loss obstruction caused by quotienting **individual** witnesses by automorphism before retaining their joint incidence relation.

### Consequence

```text
current W_P witnessed-edge quotient
    is not, as it stands, a Bruggink residual system.
```

A future residual semantics would need richer joint witness data — for example a simultaneous realization with distinguished occurrences, or another representation preserving relative occurrence information — without turning persistent identity into carrier structure.

## 7. A5 — erasure and conflict

PETRA has explicit conflict cases. The simplest is ADD versus REMOVE at the same original leaf.

Current semantics treats this by **absence from the independence/residual domain**, not by a total projection returning an elementary step.

That is perfectly coherent for PETRA's local commutation theorem, but it fails the total-projection requirement of the audited residual-system definition.

## 8. A6 — no duplication of existing redex occurrences

Elementary PETRA edits never copy an existing occurrence:

- ADD preserves every old occurrence and adds one fresh leaf;
- REMOVE deletes exactly one old leaf and preserves every other old occurrence.

Therefore an existing coinitial target can be preserved or erased, but not duplicated into two residual copies.

New edit opportunities can be **created**: an ADD creates a fresh removable leaf, and a REMOVE can make its parent become a leaf. Creation is not duplication of an existing coinitial witness.

Thus non-duplication of existing targets is **PASS at realization level**.

## 9. A7 — cube coherence on the independent fragment

Take three realization-level elementary edits whose original target occurrences are pairwise distinct and whose ADD/REMOVE choices satisfy the same survival conditions used by Theorem 3.

Each edit changes only its own local incidence: it either adds one fresh leaf below its target or deletes its own target leaf. The other original targets are untouched. Consequently all six execution orders are valid and lead, up to rooted-tree isomorphism fixing surviving original occurrences, to the same final realization.

Residualizing one edit after either order of the other two therefore transports it to the same surviving original target. On this restricted domain the residual cube equation holds.

This gives **PARTIAL**, not full, residual-system coherence because conflicts and quotient-level ambiguity remain.

## 10. A8 — deterministic / stable residual structures

Stronger labels such as DRS or SDRS presuppose a residual relation satisfying their own axiom packages. PETRA currently fails an earlier prerequisite: a total well-defined residual projection on the chosen witnessed-step quotient.

Therefore:

```text
PETRA current W_P is a DRS/SDRS    FAIL
```

This does not rule out a future enriched witness system satisfying such axioms.

## 11. A9 — permutation equivalence

On the realization-level independent fragment, PETRA's generator

```text
a ; (b/a)  ≡comm  b ; (a/b)
```

is exactly the residual-theoretic shape of swapping two coinitial independent steps through their residuals.

Therefore the **local generator shape is SPECIALIZED prior art**.

However PETRA `≡comm` is not yet the full permutation equivalence of a standard residual system because the residual operator is partial and not well-defined on current automorphism-quotiented edge classes.

Result: **PARTIAL**.

## 12. A10 — completeness remains open

The audit does not prove

```text
inverse cancellation + independent commutation
is complete for all equal witnessed path effects.
```

In fact, the witness-quotient obstruction strengthens the reason for caution: endpoint equality and local commutation may lose pairwise occurrence information under symmetry.

Classification remains **OPEN**.

## 13. Phase-6 consequence

The previous `TO-VERIFY` question is now resolved more sharply:

```text
generic residual theory                         KNOWN
independent realization-level residual square   SPECIALIZED shape / PETRA-INTERNAL criterion
current W_P as full residual system              FAIL
current W_P as DRS / SDRS                        FAIL
permutation-equivalence match                    PARTIAL
local-presentation completeness                  OPEN
```

The negative result concerns the **current witness quotient**, not the mathematical possibility of a richer PETRA residual semantics.

No Phase-7 promotion follows from this audit.
