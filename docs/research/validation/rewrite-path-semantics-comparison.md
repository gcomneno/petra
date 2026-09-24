# PETRA Phase 6 — rewrite and path semantics comparison

Status: **Phase 6 external-validation note** for issue #299 under programme #276.

This note compares PETRA's witnessed-path presentation with standard free categories, free groupoids, and trace / partial-commutation theory. It does not modify PETRA's normative specification.

## 1. Witnessed paths as a free category

Let `W_P` be the directed witnessed edit graph. The standard free category on a directed graph has graph vertices as objects, finite composable edge paths as morphisms, empty paths as identities, and concatenation as composition.

PETRA witnessed edit paths use exactly this construction.

### Phase-6 classification

`witnessed edit paths form free category` — **SPECIALIZED**.

The categorical construction is standard; PETRA specializes it by supplying its own witnessed edit graph.

## 2. Reverse edges and inverse cancellation

PETRA equips every witnessed elementary edit with a designated reverse witnessed edge. Freely adjoining inverses to graph edges and quotienting path words by immediate inverse cancellation gives the standard free groupoid on the graph.

PETRA's `≡inv` quotient is therefore the generic free-groupoid construction at this level.

### Phase-6 classification

`inverse-cancellation quotient is a groupoid` — **SPECIALIZED**.

This classification stops before PETRA's independent-edit commutation relations are added.

## 3. Partial commutation and trace theory

Mazurkiewicz trace theory starts from an alphabet `Sigma` and a symmetric irreflexive independence relation `I subseteq Sigma x Sigma`. Words are quotiented by swapping adjacent independent letters: `u a b v ~= u b a v` when `(a,b) in I`.

This validates the generic mathematical pattern behind quotienting action sequences by commutation of independent actions.

## 4. Why PETRA is not yet a trace monoid

PETRA does not currently fit the fixed-alphabet trace-monoid definition literally. A witnessed edit contains source-sensitive information such as target occurrence. After executing one edit, the witness for the other edit may need to be transported / residualized in the successor state.

Thus PETRA uses state-typed witnesses and residual witnesses, whereas classical trace theory uses fixed letters and a fixed independence relation.

Therefore `PETRA local commutation quotient == trace monoid` is **not established**.

## 5. Independent-edit theorem

PETRA internally proves a concrete criterion under which two witnessed edits produce a commuting square. External trace theory establishes the general idea that independent actions may commute, but it does not establish PETRA's exact criterion because that criterion depends on PETRA occurrence geometry and witness transport.

### Phase-6 classification

- generic independent-action commutation: **KNOWN**;
- PETRA exact independence criterion: **PETRA-INTERNAL**.

No novelty claim follows from the second classification.

## 6. Free groupoid versus local quotient

Two quotients must remain distinct. Paths modulo inverse cancellation give the free groupoid. PETRA may then additionally quotient by commuting squares. The second quotient is therefore a presented groupoid/category with additional relations, not merely the free groupoid on the graph.

## 7. Reduced paths and geodesics

Standard free-groupoid reduction removes immediate inverse pairs. That is an algebraic normal-form operation, not a metric shortest-path theorem. PETRA's internally proved fact that a reduced path need not be geodesic is therefore compatible with the standard free-groupoid picture.

## 8. Completeness remains open

The Phase-5 question whether inverse cancellation plus independent commutation is complete for all equal witnessed path effects is **not** answered by free-category, free-groupoid, or classical trace-monoid theory.

The state-dependent witness / residual structure is precisely the remaining mismatch. Hence completeness of `≡loc` remains **OPEN**.

## 9. Phase-6 result

This slice resolves two previous `TO-VERIFY` rows: witnessed paths as free category and inverse-cancellation quotient as groupoid are now **SPECIALIZED**.

It also sharpens the commutation boundary: generic partial commutation is **KNOWN**; PETRA's exact commuting criterion remains **PETRA-INTERNAL**; literal trace-monoid identification is not established; completeness remains **OPEN**.

The remaining external question is narrower: find a rewriting/concurrency framework with state-dependent residuals and commuting squares close enough to PETRA to classify the exact independence criterion more strongly.

No Phase-7 promotion follows from this note.
