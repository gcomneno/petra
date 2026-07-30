# PET local probe proposal

> **Legacy implementation-compatibility note.** `NEW`, `DROP`, `INC`, and
> `DEC` below describe retained current probe labels, not canonical PET
> semantics. The sole normative future operator contract is
> [`../foundations/pet-peg-2.0-object-native-operators.md`](../foundations/pet-peg-2.0-object-native-operators.md).

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

    primary_band = recovery DROP k[2..6]
    transition_side = DEC-as-DROP
    proposal_status = partial
    reason = exponent transition mapped to DROP-like release band
    suggested_probe_role = inspect DEC exponent release through DROP-like band
    candidate_window = k[2..6]
    side_band = unknown
    side_window = unknown

Interpretation:

- the direct PET lens transition is now detected as `DEC`;
- `DEC` is not treated as native `DROP`;
- it is projected onto a `DROP`-like release band;
- the result is explicitly marked as partial.

This is important because non-flat / power-like cases require exponent-aware transitions.

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
8. if no side band exists, report `side_band = unknown`;
9. map exponent transitions conservatively:
   - `DEC` -> `DROP`-like release;
   - `INC` -> `NEW`-like pressure;
   - `DEC_PATH` -> `DROP`-like release;
   - `INC_PATH` -> `NEW`-like pressure;
   - `DROP_PATH` -> `DROP`-like release;
   - `NEW_PATH` -> `NEW`-like pressure;
10. mark exponent-projected and path-projected proposals as `partial`, not `strong`.

## Status

This helper is diagnostic.

It is useful for deciding where PET should inspect next, not for claiming a factorization.

## Exponent transition projection

PET transitions can be native or projected.

Native transitions:

    NEW  -> structural pressure
    DROP -> structural release

Exponent transitions:

    INC -> NEW-like pressure
    DEC -> DROP-like release

Transition paths:

    INC_PATH  -> NEW-like pressure
    DEC_PATH  -> DROP-like release
    NEW_PATH  -> NEW-like pressure
    DROP_PATH -> DROP-like release

The projection is conservative.

A `DEC-as-DROP` or `INC-as-NEW` proposal is marked as `partial` because the magnetic bands currently expose `NEW` / `DROP` movement, not native `INC` / `DEC` bands.

This avoids pretending that exponent movement and flat leaf movement are identical.


## Multi-step transition paths

When no immediate transition reaches the target lens generator, PET can use the rewrite explanation path between the source generator and the target generator.

Example:

    N = 16
    source_generator = 16
    target_generator = 2
    transition = DEC_PATH
    transition_path = DEC -> DEC -> DEC
    generator_path = 16 -> 8 -> 4 -> 2

The local probe proposal maps this to:

    primary_band = recovery DROP k[2..6]
    transition_side = DEC_PATH-as-DROP
    proposal_status = partial
    reason = exponent transition path mapped to DROP-like release band

This does not mean that `DEC_PATH` is identical to `DROP`.

It means that, with the current magnetic band vocabulary, a multi-step exponent release is inspected through the closest available DROP-like release band.
