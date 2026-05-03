# PET local probe proposal

The PET local probe proposal is an experimental diagnostic step that connects a PET lens transition to a local inspection window.

It combines:

- the PET lens transition;
- the source generator;
- the target generator;
- the representative target;
- the magnetic mass-response bands.

It does not factor `N`.

## Chain

    N opaque
    -> surface/lens hint
    -> structural candidate
    -> PET transition
    -> local probe proposal

## Operational claim

The local probe proposal does not identify factors.

It selects a structurally coherent inspection window by combining the PET lens transition with magnetic mass-response bands.

In PET terms:

    Non trova il pesce.
    Indica dove l’acqua si muove strano.

## Example: 3027009081

    transition = DROP
    source_generator = 30
    target_generator = 6
    representative_target = 15

    primary_band = multi-threshold NEW,DROP k[2..6]
    transition_side = DROP
    proposal_status = strong
    reason = transition-coherent magnetic band selected
    suggested_probe_role = inspect DROP side / lower structural release
    candidate_window = k[2..6]
    side_band = recovery DROP k[7..11]
    side_window = k[7..11]

Interpretation:

- the PET transition says that the structural movement is `DROP`;
- the mass-response bands expose a critical multi-threshold region;
- the proposal selects the `DROP` side of that region as the next inspection window;
- the side band keeps track of the adjacent `DROP` recovery region.

This does not mean that `15` divides `N`.

The representative target is structural, not arithmetical.

## Weak transition case: 49

    transition = unknown
    source_generator = 4
    target_generator = 2
    representative_target = unknown

    primary_band = pressure-entry NEW k[1..1]
    transition_side = fallback
    proposal_status = weak
    reason = no direct PET lens transition available
    suggested_probe_role = inspect unresolved transition neighborhood
    candidate_window = k[1..1]
    side_band = unknown
    side_window = unknown

Interpretation:

- no direct PET lens transition is available;
- the proposal falls back to the strongest visible band;
- the result is explicitly marked as weak.

This is important because non-flat / power-like cases may require a different transition family, such as a future `DEC` or flattening-aware proposal.

## Current selection rule

The first conservative rule is:

1. read the PET transition;
2. read the magnetic bands;
3. prefer bands whose `move` contains the transition;
4. rank candidate bands by:
   - higher `focus_score`;
   - lower `min_trigger_span`;
   - wider `band_width`;
5. if no transition-coherent band exists, fall back to a multi-threshold band;
6. otherwise fall back to the strongest visible band and mark the proposal as weak;
7. when another transition-coherent band exists, report it as `side_band`;
8. if no side band exists, report `side_band = unknown`.

## Status

This helper is diagnostic.

It is useful for deciding where PET should inspect next, not for claiming a factorization.
