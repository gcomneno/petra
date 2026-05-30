# PET guarded redirect factor-chain certificates

This note records the first PET structural factorization research step after the
PET/PEG 2.0 object, graph, trace, certificate, legacy bridge, and object-native
metrics work.

The guarded redirect execution probe now emits factor-chain certificates.

These certificates verify that a reported factor chain multiplies back to the
original `N`.

They are deliberately not PET/PEG operator-path certificates.

## Boundary

A factor-chain certificate means:

- the chain is parseable as positive integer factors
- the product of the factors equals `N`
- the certificate verifies product consistency only

It does not mean:

- the route is optimal
- the route should be promoted into default routing
- the route is a PET/PEG operator path
- PET solves general integer factorization
- anchor selection should change by default

## Observed seed matrix

### Flat-k completion family

For `238238`:

- guard triggers
- conservative redirect expands the route
- expanded flat-k execution completes

Observed chains:

```text
current         = 154 * 1547
redirect        = 2 * 7 * 7 * 2431
redirect_flat_k = 2 * 7 * 7 * 17 * 11 * 13
```

All reported chains verify product 238238.

For 357357:

guard triggers
conservative redirect expands the route
expanded flat-k execution completes

Observed chains:

current         = 231 * 1547
redirect        = 3 * 7 * 7 * 2431
redirect_flat_k = 3 * 7 * 7 * 17 * 11 * 13

All reported chains verify product 357357.

Shape-family completion family

For 374374:

guard triggers
conservative redirect expands the route
expanded shape-family execution completes

Observed chains:

current               = 154 * 2431
redirect              = 2 * 7 * 26741
redirect_shape_family = 2 * 7 * 187 * 11 * 13

All reported chains verify product 374374.

For 442442:

guard triggers
conservative redirect expands the route
expanded shape-family execution completes

Observed chains:

current               = 154 * 2873
redirect              = 2 * 7 * 31603
redirect_shape_family = 2 * 7 * 221 * 11 * 13

All reported chains verify product 442442.

Positive control

For 30030:

guard does not trigger
redirect certificates are unavailable
current chain still verifies product

Observed chain:

current = 5005 * 2 * 3

The positive control confirms that guarded redirect factor-chain certificates do
not fabricate redirect evidence when the guard does not trigger.

Current interpretation

The observed cases split into at least two structural completion families:

flat-k expanded completion:
  238238
  357357

shape-family expanded completion:
  374374
  442442

guard-not-triggered control:
  30030

The common pattern is:

current route:
  selects a structural-prefix anchor and blocks or under-expands

guarded redirect:
  redirects to the smaller active shadow anchor

conservative redirected execution:
  expands the route but may not complete

expanded redirected execution:
  completes under flat-k or shape-family scan

This remains research-only.

The result supports studying route structure and completion signals, not changing
default PET routing.
