## Observed patterns in the ranges `1..24` and `24..48`

Using `tools/exponent_shape_trace.py`, the first two windows already suggest that exponent-shape traces are not merely irregular, but are structured around a small set of recurring local shape classes.

### 1. Plateaus are real but sparse

For `1..24`, the summary is:

- transition count: `23`
- unchanged transitions: `4`

For `24..48`, the summary is:

- transition count: `24`
- unchanged transitions: `4`

So plateau transitions clearly exist, but they remain a minority.
Most consecutive exponent transitions still change both signature and generator.

### 2. Small generators recur very frequently

Even as exponents grow, many values still fall back into PET shape classes with very small generators, especially:

- `2`
- `4`
- `6`
- `12`

This reinforces the earlier observation that arithmetic size and PET shape complexity are strongly decoupled.
Exponent growth does not imply monotone growth of PET shape complexity.

### 3. Constant runs can be longer than length 2

In `1..24`, unchanged transitions appear only as isolated pairs such as:

- `2 -> 3`
- `8 -> 9`
- `14 -> 15`
- `21 -> 22`

But in `24..48`, a longer constant run appears:

- `33`
- `34`
- `35`

All three share:

- `generator = 6`
- `signature = [[], []]`

So plateau behaviour is not limited to isolated consecutive pairs.
Short constant runs of length greater than 2 already appear in small ranges.

### 4. Large upward jumps remain abrupt

The trace also exhibits sharp jumps from very small generators to much larger ones.
Examples in `24..48` include:

- `29 -> 30`: `2 -> 30`
- `35 -> 36`: `6 -> 36`
- `41 -> 42`: `2 -> 30`
- `47 -> 48`: `2 -> 48`

So the exponent-shape trace is not just non-monotone.
It appears to alternate between:

- frequent returns to a few small recurring classes
- short plateau segments
- abrupt jumps toward structurally richer classes

## Provisional interpretation

A reasonable empirical reading of the current data is:

> The exponent-shape trace appears to be dominated by frequent returns to a small set of low-generator PET shape classes, interrupted by short plateaus and abrupt jumps to richer shape classes.

This suggests a dynamics with local recurring attractors rather than smooth structural growth.
