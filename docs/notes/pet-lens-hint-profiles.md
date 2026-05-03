# PET lens hint profiles

Status: experimental note.

This note records empirical profiles produced by combining three diagnostic layers:

- surface signature
- shape stencil lens hint
- mass excitation delta

## Operating model

Surface selects blade scale.

Stencil selects cut shape.

Delta classifies response role.

In short:

- surface answers: how long should the blade be?
- stencil answers: what shape should the next cut have?
- delta answers: how did a known peel affect the resonance?

This does not factor N.

This does not prove primality.

It is a PET diagnostic profile.

## Dependency classes

The current delta helper reports:

- unchanged
- modulator
- extinction-driver

### unchanged

The peel does not affect the observed resonance signature.

Candidate interpretation:

The removed component is structurally non-driving under the current excitation setup.

### modulator

The peel changes the resonance signature but does not collapse it.

Candidate interpretation:

The removed component influences the resonance, but the residual still supports a coherent response.

### extinction-driver

The peel collapses the resonance.

Candidate interpretation:

The removed component was necessary for the observed resonance, or the residual is too small/simple to sustain it.

## Profile 1: tiny crumb, modulator, driver

N = 3027009081

Classic view:

3027009081 = 3 * 1009 * 1000003

Lens hint:

- blade_index = 10
- target_lens = two-leaf
- flatten_first = no

Delta profile:

- peel 3 -> unchanged
- peel 1009 -> modulator
- peel 1000003 -> extinction-driver

PET interpretation:

The tiny factor 3 is real arithmetically, but structurally non-driving.

The 1009 component modulates the resonance.

The 1000003 component drives the observed resonance.

Operationally, the dominant PET cut is two-leaf.

## Profile 2: unbalanced driver-dominant semiprime

N = 9081007063

Classic view:

9081007063 = 1009 * 9000007

Lens hint:

- blade_index = 10
- target_lens = two-leaf
- flatten_first = no

Delta profile:

- peel 1009 -> modulator
- peel 9000007 -> extinction-driver

PET interpretation:

The smaller component behaves as a modulator.

The larger component behaves as the resonance driver.

The two-leaf lens does not mean equal mass. It means the next structural cut has a two-leaf form.

## Profile 3: balanced co-dependent semiprime

N = 6345405191

Classic view:

6345405191 = 70139 * 90469

Lens hint:

- blade_index = 10
- target_lens = one-leaf
- flatten_first = no

Delta profile:

- peel 70139 -> extinction-driver
- peel 90469 -> extinction-driver

PET interpretation:

Both components are co-dependent resonance drivers.

Removing either side collapses the observed resonance.

This differs from the unbalanced case, where one component modulates and the other drives.

## Current distinction

PET structural mass is not the same as classical prime factor count.

Small arithmetic factors may be real but structurally non-driving.

Non tutte le briciole meritano la spada laser.

## Practical reading

A PET lens hint should be read as follows:

- blade_index gives the surface-scale blade length
- target_lens gives the structural form of the next cut
- flatten_first indicates whether non-flat depth should be projected before using flat lenses
- dependency class describes how a known peel affects resonance

## Current limitations

These profiles use known factors to compute deltas.

Therefore they are diagnostic and empirical.

They do not yet solve candidate discovery.

The next open problem is to replace known-factor delta probes with PET-generated candidate cuts.
