# Completion-aware residual descent and structural lateral doors

Status: research note
Issue: #88
Scope: exploratory observation, no default behavior change

## Summary

Structural factorization currently follows a conservative route:

    PET decomposes the PET-visible shape route.
    Classic verification confirms arithmetic factors.
    PEST can explain the path.

During structural factorization experiments, we observed that some numbers behave
like structural walls under the conservative route, but become traversable when
embedded in a richer multiplicative context.

Working metaphor:

    Per attraversare il muro, PET non lo sfonda:
    gli costruisce attorno una geometria in cui compare una porta.

This note records the seed observations behind a possible future
completion-aware residual descent policy.

## Vocabulary

### Structural wall

A structural wall is a number or residual that the conservative structural
factorization route cannot currently cross.

Example:

    N = 1001
    status = blocked-no-verified-anchor
    residual_reduction_chain = 1001
    terminal_residual = 1001

This does not mean that the number has no classical factorization.

It means that the active PET route did not produce a verified anchor that lets
the conservative residual descent complete.

### Structural lateral door

A structural lateral door is an anchor exposed by a richer multiplicative
context that avoids attacking a wall directly and instead leaves a residual
that the active route can close.

Example:

    30030 = 1001 * 30

Conservative structural factorization:

    N = 30030
    status = complete
    residual_reduction_chain = 5005 * 2 * 3
    terminal_residual = 1

The important point is that PET does not attack 1001 directly.

Instead, it finds a different route:

    30030 -> 5005 * 6
    6 -> 2 * 3

The multiplicative context exposes a lateral door.

### Structural trap-door

A structural trap-door is an apparently good structural reduction that leaves
a residual blocked under the active profile.

Example:

    21021 = 1001 * 21

Conservative structural factorization:

    N = 21021
    status = blocked-no-verified-anchor
    residual_reduction_chain = 21 * 1001
    terminal_residual = 1001

The route reduces the number, but it leaves the known wall 1001 as the terminal
residual.

With flat-k enabled, the same case can complete:

    21021 -> 21 * 13 * 7 * 11

This shows that the default route was not mathematically impossible; it was
blocked by the active profile.

### Trap-context

A trap-context is a multiplicative context that repeatedly induces a
non-closing route under the current shape-descent-first policy.

Seed trap-context candidate:

    k = 21

Observed cases:

    1001 * 21   = 21021   -> 21 * 1001      -> blocked
    17017 * 21  = 357357  -> 231 * 1547     -> blocked
    323323 * 21 = 6789783 -> 3003 * 2261    -> blocked

This suggests a possible future route-pattern classifier, not a precomputed lookup table of known walls.

## Seed walls

The initial wall family used for observation was:

    1001   = 7 * 11 * 13
    17017  = 7 * 11 * 13 * 17
    323323 = 7 * 11 * 13 * 17 * 19

Conservative structural factorization:

    1001   -> blocked
    17017  -> blocked, chain = 7 * 2431
    323323 -> blocked, chain = 77 * 4199

With flat-k enabled:

    1001   -> 13 * 7 * 11
    17017  -> 7 * 17 * 11 * 13
    323323 -> 77 * 19 * 13 * 17

Interpretation:

- these are not impossible cases
- they are blocked by the conservative active profile
- additional scan modes can open the wall
- richer multiplicative contexts can sometimes expose lateral doors even under
  the conservative CLI route

## Multiplicative context observations

Many tested contexts turn the wall into a complete route under the conservative
structural-factorization CLI.

Examples:

    1001 * 30   -> 5005 * 2 * 3
    17017 * 30  -> 6 * 85085
    323323 * 30 -> 1616615 * 2 * 3

This supports the central observation:

    A wall can become traversable when embedded in a multiplicative context
    that exposes a completion-friendly anchor.

However, not every context helps.

Trap-like examples:

    1001 * 21   -> 21 * 1001      -> blocked
    17017 * 21  -> 231 * 1547     -> blocked
    323323 * 21 -> 3003 * 2261    -> blocked

So the useful distinction is not simply:

    wall alone vs wall multiplied

The useful distinction is:

    lateral-door context vs trap-context

## Current policy limitation

The current residual descent policy is shape-descent-first.

Informally:

    prefer the structurally simpler residual

The experiments show that:

    shape-simple is not always completion-friendly

A residual may have a simpler PET shape and still be blocked under the active
profile.

The 21021 case is the seed example:

    3  -> residual 7007 -> shape-family-scan-required
    21 -> residual 1001 -> flat-k-scan-required

The current policy selects 21 because it gives the structurally simpler
residual, but under the conservative profile that residual does not close.

## Completion-aware residual descent

A future completion-aware policy would ask:

    Which candidate residual is more likely to close under the active profile?

Instead of only ranking by residual shape simplicity, it may consider:

- whether the residual route is already solved
- whether the residual requires an inactive scan mode
- whether the residual matches a known wall-like pattern
- whether the context appears in a trap-context catalogue
- whether an alternative anchor leaves a completion-friendly residual

Possible future rule sketch:

    if candidate residual matches a known wall-like residual
    or candidate context matches a known trap-context
    then penalize that route unless the active profile can complete it

This should remain research-only until better understood.

## Research probe

A non-default research probe is available at:

    tools/research/pet_completion_aware_residual_probe.py

The probe observes the current depth-0 residual candidate ranking without
changing PET routing, CLI behavior, or anchor selection.

Example:

    python tools/research/pet_completion_aware_residual_probe.py 21021

Seed output interpretation:

    selected_anchor = 21
    selected_residual = 1001
    candidate_2_classification = selected-trap-door-candidate

The same probe highlights structural lateral doors:

    python tools/research/pet_completion_aware_residual_probe.py 30030

Seed output interpretation:

    selected_anchor = 5005
    selected_residual = 6
    candidate_2_classification = completion-friendly

With flat-k enabled, the 21021 trap-door becomes expandable under the active
profile:

    python tools/research/pet_completion_aware_residual_probe.py 21021 --auto-flat-k-scan

Seed output interpretation:

    selected_anchor = 21
    selected_residual = 1001
    candidate_2_classification = expandable-with-active-mode

This confirms the core research distinction:

    a route can be a trap-door in the conservative profile
    but become expandable when the required scan mode is active

## Route-pattern trap-door detection

A literal trap-context lookup table keyed by known walls or known numbers is not
a good policy foundation.

That would risk turning the research direction into a list of special cases:

    wall = 1001
    context = 21
    avoid this route

This is not the goal.

The useful generalization is route-pattern detection.

A future completion-aware policy should observe the candidate route itself:

    candidate anchor
    candidate residual
    residual route final status
    active profile
    required inactive scan mode
    alternative candidates
    selected candidate classification

The relevant question is not:

    have we seen this exact wall before?

The relevant question is:

    does this candidate leave a residual that the active profile cannot close,
    while another candidate looks more completion-friendly?

This keeps the idea general and PET-native.

Seed classifications remain useful as observations:

    structural-wall
    structural-lateral-door
    structural-trap-door
    trap-context
    completion-friendly-context

But they should be derived from route behavior, not from a precomputed
per-number table.

Potential use:

- compare current shape-descent-first selection with completion-aware ranking
- detect recurring non-closing route patterns
- avoid special-casing known numbers
- provide evidence before changing any policy
- keep the public CLI conservative

## Boundary

This note does not change PET behavior.

Do not change the default CLI route based on this note alone.

Do not claim that PET magically factors integers.

Structural factorization remains a PET-shape route plus classic verification.

PEST remains explanatory-only.

## Next possible research steps

1. Create a small research probe that compares candidate anchors by:
   - current selection score
   - residual route final status
   - whether completion requires inactive modes

2. Collect route-pattern examples from seed walls without hardcoding
   wall values into policy:
   - 1001
   - 17017
   - 323323

3. Compare conservative route vs flat-k-enabled route.

4. Keep all behavior non-default and research-facing.

5. Only consider CLI exposure after the policy is better understood and tested.

### Active-vs-expanded profile comparison

The completion-aware residual probe can optionally compare each depth-0
candidate residual against expanded research profiles:

    python tools/research/pet_completion_aware_residual_probe.py 21021 --compare-expanded-profile --json

This mode is observational only. It does not change:

- stable CLI behavior
- routing
- anchor selection
- residual descent core
- verification

The comparison records whether a candidate residual remains blocked under the
current active profile or opens when an expanded scan mode is enabled.

Initial completion deltas:

- `unchanged-complete`
- `opens-with-flat-k`
- `opens-with-shape-family`
- `remains-blocked`

The purpose is to make active-vs-expanded completion signals visible before
considering any future completion-aware ranking policy.
