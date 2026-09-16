# T01 — Canonicalizer for exponential sequences

Status: in progress
Type: index of results, tools, and open questions
References: see individual notes for details

## Statement

Extract `(inner_sequence, structural_class(base))` from a sequence
`k^n` and operate on the pair instead of the full sequence.

Minimal example: `12^n` and `20^n` share the same shape
`C(r0^C(r0^1), r1^1)`. The canonicalizer should produce the same
representative for both.

## Results

1. **Exact identity.** For `k = p1^e1 * ... * pr^er`,
   `shape(k^n) = C(r0^shape(e1*n), ..., r_{r-1}^shape(er*n))`.
   The prime values disappear; only the exponent multiset survives.
   Recorded in `notes/exponential-base-structural-class.md`.

2. **Duplication lemma.** The multiset `{a, a, ..., a}` has the same
   empirical fingerprint as `{a}`. Follows from the linearity of
   `node_count` on same-exponent containers. Recorded in the same note.

3. **Two falsifications.**
   - "The presence of 1 forces a class": false for N >= 500.
   - "The fingerprint is a class invariant": false at fixed window
     size; the same multiset oscillates by up to ~7 percentage points
     across disjoint windows.
   Recorded in the same note.

4. **Form / strada / value boundary.** Three distinct levels:
   - form: `shape(n)`, the canonical shape;
   - strada: a sequence of canonical operators between two forms, not
     unique;
   - value: `n`, the integer, external to the form.
   The signature of a transition is the pair of forms, not the strada,
   not the value.
   Recorded in `notes/form-road-value-boundary.md`.

5. **Recursive reconstruction.** Every canonical shape can be built
   from the mother (bare leaf) in a single chain of `struct`
   applications, using only two elementary pieces (the bare leaf and
   the one-father container with a leaf father), in height-first order.
   The chain is one strada, not a canonical invariant.
   Recorded in `notes/recursive-reconstruction-t01.md`.

## Tools

Runtime:
- `resolver/src/resolver/struct_destruct.py` — `struct` and `destruct`,
  one-level composition and decomposition of forms.
- `resolver/src/resolver/notation.py` — mother notation for shapes.

Research:
- `tools/research/rebuild_shape.py` — BFS search for the shortest chain
  of `struct` applications reaching a target; supports `--pieces
  minimal|all`.
- `tools/research/rebuild_recursive.py` — DFS height-first single-chain
  reconstruction; prints recursion tree and flat steps.

## Open questions

- **Convergence of the cumulative fingerprint.** Does `F(1, N)` have a
  limit as `N` grows? Moved to T16.
- **Canonicity of the reconstruction chain.** The current chain is
  unique under the chosen order (height-first, left-to-right). Other
  orders give other chains. Is any of them canonical, or are they all
  equally arbitrary?
- **Using struct/destruct on `shape(k^n)`.** The exact identity is
  proven, but the tools have not yet been used to explore the
  exponential case `k^n` through composition and decomposition.
- **Asymmetry of structural distance.** Noted in T17, related but
  separate.

## Forward

- **T16** — convergence of the cumulative fingerprint.
- **T17** — asymmetry of `structural_distance_numbers`.
- Possible new threads: canonical chain, exponential case via
  struct/destruct.

## Status

Consolidation of the T01 line after the second session. Three notes,
four tools. The identity and the reconstruction are the solid results.
Classification and convergence remain open.
