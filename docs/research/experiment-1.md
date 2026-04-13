# Experiment 1 — family separability benchmark

## Goal

Test whether selected classical integer families exhibit measurable and partially distinguishable structural signatures under PET.

This experiment is descriptive, bounded, and reproducible.

It does not aim to prove universal separability.
It aims to measure where PET captures real structural differences, where overlap remains, and where shape alone is insufficient.

## Families

This experiment uses these four classical families:

- Perfect
- Primorials
- Hamming (5-smooth)
- HighlyComposite

Samples should be disjoint before comparison, using the established family-priority rule already adopted in the benchmark workflow.

## Core question

Do disjoint samples from these four families show partially distinguishable PET signatures under canonical PET metrics and PET-based distances?

## Primary metrics

Use these canonical PET metrics as the main basis for comparison:

- node_count
- leaf_count
- height
- max_branching
- branch_profile
- recursive_mass
- average_leaf_depth
- leaf_depth_variance

## Secondary diagnostics

Use these as supporting diagnostics, not as the primary foundation:

- distance
- structural_distance
- shape predicates and simple family-facing classifications when useful

## What to measure

For each family:

- intra-family compactness
- metric spread
- structural-distance spread

Between families:

- pairwise distance summaries
- pairwise structural-distance summaries
- visible overlaps
- strongest and weakest separations

## Success criteria

Experiment 1 is considered successful if:

1. at least one family is structurally tighter than others in a clear and reproducible way
2. at least one pair of families shows meaningful average separation
3. the result survives bounded reproducible reruns
4. the conclusions can be stated without claiming hard or universal separation

## Failure criteria

Experiment 1 is considered weak or inconclusive if:

1. all families appear structurally mixed with no readable contrast
2. any observed contrast is trivial, unstable, or overly dependent on arbitrary thresholds
3. the results require exaggerated interpretation to sound interesting

## Deliverable

The final deliverable for Experiment 1 is a bounded benchmark report that states:

- what was compared
- how the samples were made disjoint
- which PET metrics were used
- what separation signals were observed
- where overlaps remained
- what PET can and cannot claim from this benchmark

A compact decision companion may also be maintained in [docs/experiment-1-scorecard.md](docs/experiment-1-scorecard.md).

## Interpretation rule

A partial result is still a valid result.

This experiment is not about forcing PET to classify everything perfectly.
It is about measuring how far PET can go before overlap and ambiguity become the dominant reality.
