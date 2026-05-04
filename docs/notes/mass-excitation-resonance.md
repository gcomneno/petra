> Historical note.
> This note refers to legacy/research tooling. The current implementation lives
> under `tools/research/`; root-level `tools/*.sh` wrappers remain available for
> compatibility.

# PET mass excitation resonance notes

Status: experimental note.

This note records empirical observations about PET mass excitation sweeps.

The current mass-response lens is a balanced-k mass model. It does not directly infer the true number of factors. It observes how mass-center bands react when the move-span stimulus changes.

## Vocabulary

### Resonance

A mass excitation resonance is present when opaque-mass-response produces a multi-threshold magnetic band under move-span sweep.

This is not a factorization claim.

### Onset

The first move span where a multi-threshold band appears.

Tracked fields:

- onset_span
- onset_k_range
- onset_width

### Saturation

The first stable wider response after onset, where increasing the move span no longer changes the main multi-threshold k-range.

Tracked fields:

- saturation_span
- saturation_k_range
- saturation_width

### Extinction

A resonance extinction occurs when a known peel changes the resonance status from present to none.

Example:

- N resonance: present
- N / known_factor resonance: none

This does not prove factor discovery. It indicates that the removed component was structurally important for the observed resonance.

## Current empirical interpretation

The resonance appears to track coarse mass scale and resonance-driving mass components.

Small factors can perturb the full number too little to affect the resonance signature. In those cases, the low backbone may be better handled by cheap bounded peeling, while PET excitation should focus on components that actually change the resonance.

In short:

PET should be more like a lightsaber than a rake.

## Observed cases

### T3-nasty

N = 3027009081 = 3 * 1009 * 1000003

Full resonance:

- status = present
- onset_span = 3
- onset_k_range = 4..4
- onset_width = 1
- saturation_span = 5
- saturation_k_range = 2..6
- saturation_width = 5

Removing the small factor:

N / 3 = 1009003027 = 1009 * 1000003

The resonance signature remains unchanged.

Interpretation: the factor 3 does not drive the observed mass resonance.

Removing the medium factor:

N / 1009 = 3000009 = 3 * 1000003

The resonance remains present but changes:

- onset_span = 2
- onset_k_range = 3..3
- saturation_span = 3
- saturation_k_range = 2..4

Interpretation: the medium factor modulates the resonance.

Removing the large factor:

N / 1000003 = 3027 = 3 * 1009

The resonance becomes none.

Interpretation: the large component appears to drive the observed coarse mass resonance.

### N10 balanced semiprime

N = 6345405191 = 70139 * 90469

Full resonance:

- status = present
- onset_span = 3
- onset_k_range = 4..4
- onset_width = 1
- saturation_span = 5
- saturation_k_range = 2..6
- saturation_width = 5

Removing either factor:

- N / 70139 = 90469
- N / 90469 = 70139

Both variants produce no resonance.

Interpretation: this is a candidate co-dependent balanced-mass pattern. The full resonance depends on the paired masses; removing either side collapses the resonance.

### S2-unbalanced

N = 9081007063 = 1009 * 9000007

Full resonance:

- status = present
- onset_span = 3
- onset_k_range = 4..4
- onset_width = 1
- saturation_span = 5
- saturation_k_range = 2..6
- saturation_width = 5

Removing the small factor:

N / 1009 = 9000007

The resonance remains present but changes:

- onset_span = 2
- onset_k_range = 3..3
- saturation_span = 3
- saturation_k_range = 2..4

Removing the large factor:

N / 9000007 = 1009

The resonance becomes none.

Interpretation: this is a candidate dominant-large-mass pattern.

## Delta dependency classes

The delta helper currently reports a simple empirical dependency class.

### unchanged

Pattern:

- changed = no
- extinction = no

Candidate meaning: the peel does not affect the observed resonance signature. This usually marks a non-driving component, a small perturbation, or a component below the current excitation sensitivity.

### modulator

Pattern:

- changed = yes
- extinction = no

Candidate meaning: the peel changes the resonance signature but does not destroy it. The removed component modulates the coarse mass resonance, while the peeled residual still supports a resonance.

### extinction-driver

Pattern:

- changed = yes
- extinction = yes

Candidate meaning: removing the component collapses the resonance. This marks a candidate resonance-driving component or a peel that leaves a residual too small/simple to sustain the observed resonance.

This is still diagnostic only. It does not discover or prove factors.

## Candidate resonance dependency profiles

### Co-dependent balanced masses

Pattern:

- N: present
- N / p: none
- N / q: none

Candidate meaning: both masses are comparably important to the resonance.

Observed example:

70139 * 90469

### Dominant-large-mass driven

Pattern:

- N: present
- N / small_factor: present but reduced or shifted
- N / large_factor: none

Candidate meaning: the large component drives the coarse mass resonance.

Observed example:

1009 * 9000007

### Large-driven with medium modulation

Pattern:

- N: present
- N / tiny_factor: unchanged
- N / medium_factor: changed or reduced
- N / large_factor: none

Candidate meaning: the large component drives the resonance, while the medium component modulates it.

Observed example:

3 * 1009 * 1000003

## Important cautions

This is empirical and diagnostic.

A resonance is not a factor.

A resonance extinction is not factor discovery unless the removed factor was independently verified.

Current sweeps use the balanced-k mass-response model. Skew-aware mass excitation is not implemented yet.

## Next experiments

Test more known cases:

- balanced semiprimes at 10, 12, and 15 digits
- unbalanced semiprimes
- 3-factor products with one tiny, one medium, one large factor
- products where removing the largest component does not fully extinguish resonance
- negative controls such as N50B and RSA-like cases

Desired future helper:

tools/mass_excitation_delta.sh FULL FACTOR

It should compare FULL and FULL / FACTOR and report:

- baseline resonance status
- peeled resonance status
- onset delta
- saturation delta
- extinction yes/no
