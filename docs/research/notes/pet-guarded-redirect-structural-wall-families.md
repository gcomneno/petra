# PET guarded redirect structural wall families

This note records a structural observation from the guarded redirect factor-chain
matrix.

In the studied guarded-redirect cases, the current selected anchor has the form:

```text
current_anchor = shadow_anchor * structural_prefix
```

and the original value reconstructs as:

N = shadow_anchor * structural_prefix * current_terminal_residual

The guarded redirect keeps the smaller active shadow_anchor and avoids carrying
the structural prefix inside the selected anchor.

Observed structural prefixes

The observed structural prefixes are:

77    = 7 * 11
1001  = 7 * 11 * 13
17017 = 7 * 11 * 13 * 17

These behave like structural walls consumed by the current route.

Confirmed trigger cases
238238    : 154   = 2 * 77
357357    : 231   = 3 * 77
374374    : 154   = 2 * 77
442442    : 154   = 2 * 77
561561    : 231   = 3 * 77
935935    : 385   = 5 * 77

4526522   : 2002  = 2 * 1001
6789783   : 3003  = 3 * 1001

104110006 : 34034 = 2 * 17017
156165009 : 51051 = 3 * 17017

For every trigger case above:

current_anchor = shadow_anchor * structural_prefix
N = shadow_anchor * structural_prefix * current_terminal_residual
Completion families

The observed redirected completion families split into:

flat-k:
  238238
  357357
  4526522
  6789783
  104110006
  156165009

shape-family:
  374374
  442442
  561561
  935935

In all trigger cases, conservative guarded redirect expands the route first.
Completion requires an expanded scan mode.

Positive controls

The positive controls do not trigger guarded redirect:

30030
9699690

This supports the interpretation that the guard is detecting a structural-prefix
trap rather than blindly redirecting.

Interpretation

The current route appears to overconsume a structural wall into the selected
anchor.

The guarded redirect keeps the smaller active anchor and exposes a residual route
that can complete under flat-k or shape-family expansion.

This is a structural route observation only.

It does not promote default routing, anchor selection, or factorization behavior.

## Larger structural wall seed

A larger 10-digit seed confirms the next observed structural wall:

```text
3019190174 = 2 * 323323 * 4669
323323 = 7 * 11 * 13 * 17 * 19
4669 = 7 * 23 * 29
```

Observed guarded redirect result:

current_anchor = 646646
shadow_anchor = 2
structural_prefix = 323323

646646 = 2 * 323323

Current chain:

646646 * 4669

Conservative guarded redirect chain:

2 * 17017 * 7 * 12673

Expanded flat-k chain:

2 * 17017 * 7 * 29 * 19 * 23

The expanded result completes with flat-k:

expanded_execution_delta = redirect-completes-with-flat-k

Shape-family does not complete this seed and leaves terminal residual:

12673 = 19 * 23 * 29

This extends the observed structural wall sequence:

77     = 7 * 11
1001   = 7 * 11 * 13
17017  = 7 * 11 * 13 * 17
323323 = 7 * 11 * 13 * 17 * 19

Boundary remains unchanged: this is a structural route observation, not a
default routing change or a factorization-performance claim.

## Recursive wall peel observation

A larger 11-digit seed shows that full-wall redirect is not always the right
structural move.

Seed:

```text
69441374002 = 2 * 7436429 * 4669
7436429 = 7 * 11 * 13 * 17 * 19 * 23
4669 = 7 * 23 * 29
```

The guarded redirect probe does not trigger full-wall redirect:

guard_decision = keep-current
guard_reason = shadow-ranking-does-not-change-selection

The current route selects:

current_anchor = 646646
646646 = 2 * 323323
323323 = 7 * 11 * 13 * 17 * 19

So the route does not consume the full wall 7436429; it peels it back to the
previous wall 323323.

Plain and flat-k execution remain blocked:

646646 * 107387
terminal_residual = 107387

But shape-family execution completes:

residual_reduction_chain = 646646 * 667 * 7 * 23
terminal_residual = 1

with:

107387 = 667 * 7 * 23
667 = 23 * 29

Interpretation:

full redirect to shadow_anchor = 2 is too aggressive for this seed.
partial-wall peel to 2 * 323323 leaves a shape-family-completable residual.

This introduces a distinct observed category:

partial-wall peel with shape-family residual completion

Boundary remains unchanged: this is a research-only structural route observation,
not a routing-policy promotion or factorization-performance claim.
