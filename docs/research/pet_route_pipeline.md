# PET route pipeline

Status: completed, tested, documented.

This document describes the current PET route pipeline as an operational research pipeline.

PET does not directly claim to factor integers by itself. PET acts as a structural sensor:

- it detects structural shape families;
- it diagnoses whether PET candidates have arithmetic grip;
- it selects an escalation route;
- it hands off to classic verification or same-shape support scan;
- it promotes verified factors only after classic arithmetic checks.

## Pipeline

```text
N
→ PET structural diagnosis
→ PET grip diagnostic
→ route escalation policy
→ route suggestion
→ route execution
→ PET candidate verification / same-shape support scan
→ factor promotion
→ route_final_status
→ PET route execution summary
```

## Core route states

### PET grip status

```text
has-arithmetic-grip
structural-match-no-grip
no-structural-grip
```

### Route escalation policy

```text
has-arithmetic-grip       → verify-pet-candidates
structural-match-no-grip → same-shape-scan
no-structural-grip       → stop-no-pet-anchor
```

### Route execution status

```text
candidate-verification
same-shape-scan-required
same-shape-scan-running
same-shape-scan-skipped
stopped
```

### Final route status

```text
solved-by-pet-candidate
partial-factorization-by-pet-candidate
solved-by-same-shape-scan
partial-factorization-by-same-shape-scan
same-shape-scan-required
classic-route-suggested-only
stopped-no-pet-anchor
unresolved-no-grip
```

## Canonical examples

### 10403

```text
N = 10403
factorization = 101 * 103
pet_grip_status = structural-match-no-grip
route_escalation_policy = same-shape-scan
route_execution_status = same-shape-scan-running
auto_factor_promotion_status = complete-factorization
summary_route_final_status = solved-by-same-shape-scan
```

Interpretation:

PET detects the semiprime-like shape family but has no direct arithmetic grip. The same-shape support scan finds repeated GCD hits, promotes the verified factors, and closes the route.

### 24680

```text
N = 24680
pet_grip_status = has-arithmetic-grip
route_escalation_policy = verify-pet-candidates
route_execution_status = candidate-verification
candidate_verify_status = verified-factor
summary_route_final_status = partial-factorization-by-pet-candidate
```

Interpretation:

PET candidates have arithmetic grip. Candidate verification finds real divisors, but the candidate set does not close a complete factorization pair, so the route is partial.

### 2147483647

```text
N = 2147483647
pet_grip_status = structural-match-no-grip
route_escalation_policy = same-shape-scan
same_shape_scan_support = unsupported-shape
route_execution_status = same-shape-scan-skipped
summary_route_final_status = classic-route-suggested-only
```

Interpretation:

PET detects structural compatibility, but the current same-shape scan supports only the semiprime-like shape. The scan is skipped explicitly and the route remains a classic suggestion.

## Same-shape support scan

The current same-shape scan supports:

```text
[[], []]
```

The scan is intentionally classic arithmetic work guided by PET shape selection. It reports:

```text
hit_count
unique_factor_hit_count
factor_N
factor_N_hit_frequency
factor_N_first_support
factor_N_first_support_value
best_factor
```

PET selects the structural family. Classic GCD verification confirms whether any support actually exposes a divisor.

## Prime-limit control

Automatic same-shape scans are controlled by:

```text
--same-shape-prime-limit
```

Default:

```text
200
```

This prevents the route from silently baking in an unchangeable scan bound.

## Operational claim

The PET route pipeline is complete as a tested text-output pipeline:

```text
PET route pipeline: completed, tested, documented.
```

The current claim is intentionally limited:

- PET is a structural routing and diagnostic layer;
- factor claims are accepted only after classic arithmetic verification;
- unsupported shapes are reported explicitly;
- final route status is always surfaced in the route execution summary.




## Shape-family support routing

The handoff route reports an explicit shape-family classification and support route.

The classifier is structural. It does not try to enumerate every possible exact
PET shape by hand.

Current families:

    [[]]              -> atomic-leaf
    [[], []]          -> semiprime-flat / same-shape-flat
    [[], [], ...]     -> flat-k-leaf
    [[], [[]]]        -> one-deep-tail
    [[], [], [[]]]    -> one-deep-tail
    [[[]]]            -> narrow-deep-chain
    [[], [[], []]]    -> branchy-shape
    mixed deep shapes -> mixed-depth

These fields are reported:

    shape_family_class
    shape_family_support_status
    shape_family_route
    shape_family_route_reason

The classifier does not factor by itself. It records which operational route is
currently known, routed, recognized, or missing for a PET shape family.



## Branchy and mixed-depth support scan

`branchy-shape` and `mixed-depth` families are recognized structurally.

When they have arithmetic grip, the route remains:

    verify-pet-candidates

When they have structural match but no arithmetic grip, the route is:

    shape-family-support-scan

The scan is bounded:

    --shape-family-support-limit
    --shape-family-max-supports
    --shape-family-max-factor-lines

The scan reports verified factor hits, but factor selection is deferred:

    factor_selection_policy = deferred-to-residual-descent

Anchor selection remains PET-style through residual descent.

## Flat-k support scan

`flat-k-leaf` families are recognized structurally.

When a flat-k family has arithmetic grip, the normal route remains:

    verify-pet-candidates

When a flat-k family has structural match but no arithmetic grip, the route is:

    flat-k-support-scan

The flat-k support scan is bounded:

    --flat-k-prime-limit
    --flat-k-max-supports
    --flat-k-max-factor-lines

The scan reports verified factor hits, but factor selection is deferred:

    factor_selection_policy = deferred-to-residual-descent

This prevents the scan from selecting anchors by numeric order. Anchor selection
remains PET-style through residual descent.

## Atomic leaf route

The atomic PET shape is:

    [[]]

This shape is treated as a terminal leaf route, not as an unsupported
same-shape scan.

When an input or residual reaches this shape with structural match but no
arithmetic grip, the route reports:

    shape_family_route = atomic-leaf
    route_escalation_policy = leaf-primality-route
    route_execution_status = leaf-route-suggested
    route_final_status = stopped-at-atomic-leaf

In residual descent this becomes:

    depth_N_status = stopped-at-leaf
    residual_descent_status = stopped-at-leaf

This does not claim that the terminal residual is prime. It only records that
PET reached an atomic leaf and that any primality decision belongs to the
classic route.

## Residual descent

The residual descent route recursively reuses the PET route pipeline on residuals.

When a route produces verified anchor factors but does not close a full factorization,
the residual descent driver computes:

- `anchor_factor`
- `residual = current / anchor_factor`
- a new PET route on the residual

The driver does not factor residuals by magic. Each new anchor must come from verified
route output.

### Residual anchor selection

Anchor selection is PET-style:

- prefer the verified anchor that transforms the residual into the simplest supported PET shape;
- prefer supported residual shapes over unsupported ones;
- prefer lower residual shape complexity;
- use numeric anchor size only as a final tie-breaker.

Operational reason:

    best-pet-residual-shape-descent

For example, with `24680`, the verified anchors are `2`, `10`, and `20`.

Their residual shapes are:

    24680 / 2  = 12340  -> [[], [], [[]]]
    24680 / 10 = 2468   -> [[], [[]]]
    24680 / 20 = 1234   -> [[], []]

The selected anchor is `20`, not because it is numerically largest, but because it
transforms the residual into the simplest supported PET shape.

This gives the verified residual reduction chain:

    20 * 2 * 617

The terminal residual is not automatically claimed to be prime.

## Non-goals for this milestone

The following are future optional features, not required for this completed milestone:

```text
JSON output
adaptive prime-limit
support entropy
support clustering
large benchmark matrix
advanced scan pruning
full mathematical equivalence theorem
```

## Small-number residual descent milestone

The PET-guided residual descent pipeline has been validated on the full range:

    2..99

Validation result:

    ok = 98
    bad = 0

This means every integer in `2..99` reached:

    residual_descent_status = complete
    terminal_residual = 1

Operational interpretation:

    PET classifies the structure.
    PET chooses the route.
    PET proposes anchors or support families.
    Classic bounded checks verify arithmetic factors.
    Residual descent restarts from PET-routing on each verified residual.

This is not a claim that PET performs pure arithmetic factorization by itself.
It is a PET-guided indirect factorization pipeline with bounded classic
verification.

The final missing cases in the sweep were:

    52 = 2 * 2 * 13
    75 = 5 * 3 * 5

They were closed by routing `one-deep-tail` shapes with `no-structural-grip`
through the bounded shape-family support scan.
