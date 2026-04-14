# PET local generator rewrite laws

## Scope

This note records bounded observations about local rewrite behavior on canonical PET generators.

It is research-facing only.
Claims below are empirical unless explicitly proved elsewhere.

## Setup

For a canonical PET node with child generators

`g_1 >= g_2 >= ... >= g_k >= 1`

the local constructor is

`Ω(g_1, ..., g_k) = product_i p_i ^ g_i`

with `p_i` the `i`-th prime.

A local rewrite changes one or more child generators while preserving canonical order.

## Bounded results recorded

### 1. Forest aggregation law for disjoint rewrites

For pairwise disjoint rewrites, the resulting root generator is predicted correctly by bottom-up aggregation:

- first aggregate updated child generators at the deepest touched parents
- then propagate those updated parent generators upward
- continue until the root

Bounded checker:
- tool: `tools/forest_rewrite_check.py`
- verified with:
  - `--limit 1000000`
  - `--max-k 3`

Observed summary:
- canonical generators checked: `78`
- checked `k=1`: `252`
- checked `k=2`: `269`
- checked `k=3`: `113`
- mismatches: `0`

Interpretation:
disjoint rewrites behave like a bottom-up forest calculation, not like a naive flat product of independent global effects.

### 2. Prune absorption law

Consider a nested pair where the ancestor rewrite prunes a child by sending its generator to `1`.

Observed behavior:
- descendant then ancestor: valid
- ancestor then descendant: invalid
- descendant then ancestor gives the same result as the ancestor rewrite alone

Bounded checker:
- tool: `tools/prune_absorption_check.py`
- verified with:
  - `--limit 1000000`
  - `--max-pairs 200`

Observed summary:
- canonical generators checked: `78`
- sampled prune pairs: `48`
- descendant then ancestor valid: `48`
- ancestor then descendant invalid: `48`
- absorbed pairs: `48`
- mismatches: `0`

Interpretation:
a pruning rewrite absorbs any rewrite strictly below the pruned branch.

### 3. Admissible nested constructive substitution

For nested constructive rewrites:
- first apply an ancestor rewrite `A`
- then apply a descendant rewrite `B` inside the newly created or enlarged subtree
- let `final_g` be the final generator of that child after `A ; B`

Empirical rule:
`A ; B` behaves like a direct ancestor rewrite replacing that child by `final_g`
only when `final_g` is still admissible among the original siblings of the parent.

So the direct substitution works only under the original local order bounds.

### 4. Order obstruction witness

Small clean obstruction witness observed: `4096`

Local situation:
- root child generators: `[12]`
- at path `(0,)`: parent child generators `[2, 1]`

Constructive nested sequence:
- `A`: at path `(0,)`, slot `1`, rewrite `1 -> 2`
- this creates a new subtree of generator `2`
- `B`: inside that new subtree, rewrite `1 -> 2`
- final generator of that child becomes `4`

But in the original parent `[2, 1]`, slot `1` had upper bound `2`.

So:
- direct substitution would require replacing the second child by `4`
- but `4 > 2`
- therefore the one-step substitution is not canonically admissible in the original parent

Interpretation:
the failure is local and structural.
It is not a mysterious failure of the algebra; it is an order obstruction in the original sibling context.

### 5. Local ceiling law for nested constructive rewrites

Additional targeted probes suggest a sharper local admissibility rule.

In this section, slots are indexed from `0`.

Let the original parent have child generators

`g_0 >= g_1 >= ... >= g_{k-1}`

and let a nested constructive chain act entirely inside slot `j`,
producing a final child generator `final_h` for that same slot.

Empirical local rule observed so far:

- if `j = 0`, there is no local upper ceiling from the left
- if `j > 0`, direct substitution into the original parent appears to be canonically admissible exactly when

`final_h <= g_{j-1}`

and when it is admissible, the direct substitution agrees with the nested constructive result.

Equivalently:
- `final_h > g_{j-1}` gives a local order obstruction
- `final_h <= g_{j-1}` allows the one-step substitution at the original parent

#### Targeted evidence

##### Threshold behavior for slot `1` in parents of the form `[u, 1]`

Using the same nested constructive pattern, with final child generator `final_h = 4`:

- `[2, 1]` -> blocked
- `[3, 1]` -> blocked
- `[4, 1]` -> admissible
- `[5, 1]` -> admissible
- `[6, 1]` -> admissible
- `[8, 1]` -> admissible

So the observed threshold is exactly `u = 4`.

Using a deeper nested constructive pattern, with final child generator `final_h = 16`:

- `[4, 1]` -> blocked
- `[8, 1]` -> blocked
- `[12, 1]` -> blocked
- `[15, 1]` -> blocked
- `[16, 1]` -> admissible
- `[20, 1]` -> admissible

So the observed threshold is exactly `u = 16`.

##### Slot-local ceiling in parents of the form `[20, m, 1]`

For slot `2`, with the same final child generator `final_h = 16`:

- `[20, 12, 1]` -> blocked
- `[20, 15, 1]` -> blocked
- `[20, 16, 1]` -> admissible
- `[20, 18, 1]` -> admissible

This suggests that the relevant ceiling is not a global parent bound,
but specifically the immediate left sibling bound for the rewritten slot,
here `m = g_1`.

##### Head-slot behavior

For slot `0`, no upper ceiling from the left was observed.

In the parent `[1, 1]`, nested constructive growth inside slot `0` remained admissible for:

- `final_h = 2`
- `final_h = 4`
- `final_h = 16`
- `final_h = 65536`

This is consistent with the rule that slot `0` has no local upper ceiling.

##### Fixed-final-child history independence

Additional targeted probes suggest a stronger local invariance principle.

Fix the following local data:
- the original parent
- the original slot
- the original child in that slot
- the final child generator `final_h`

Then the observed admissibility outcome appears to depend only on that local data,
not on the particular constructive chain used inside the slot to produce `final_h`.

In particular, different nested constructive chains that produced the same final child generator
gave the same admissibility result, and whenever direct substitution was admissible,
it agreed with the nested constructive result.

Targeted evidence:
- for parents of the form `[upper, 12]`, slot `1`, multiple distinct constructive chains produced the same `final_h = 144`
- for `upper = 36`, all such chains were blocked
- for `upper = 48`, all such chains were blocked
- for `upper = 144`, all such chains were admissible, and the direct substitution matched the nested result

The same pattern was observed for parents of the form `[200, mid, 12]`, slot `2`:
- for `mid = 36`, all sampled chains with `final_h = 144` were blocked
- for `mid = 48`, all sampled chains with `final_h = 144` were blocked
- for `mid = 144`, all sampled chains with `final_h = 144` were admissible, and the direct substitution matched the nested result

This suggests the following strengthened working hypothesis:

For nested constructive rewrites confined to one original slot,
admissibility and direct-substitution behavior are determined by the original local slot context
together with the final child generator,
and are independent of the internal constructive history that produced that final child.

##### Irrelevance of non-adjacent sibling context

Additional targeted probes suggest that the observed constructive admissibility bound
depends only on the immediate left sibling of the rewritten slot, not on the rest of the sibling context.

Targeted evidence:
- for parents of the form `[upper, 12, right]`, slot `1`, varying the right sibling among
  `1, 2, 4, 12` did not change the outcome for `final_h = 144`
- with `upper = 48`, all such cases were blocked
- with `upper = 144`, all such cases were admissible, and direct substitution matched the nested result

A complementary probe was run for slot `2` in parents of the form `[left, mid, 12]`:
- varying the far-left sibling among `48, 144, 500` did not change the outcome for `final_h = 144`
- with `mid = 48`, all such cases were blocked
- with `mid = 144`, all such cases were admissible, and direct substitution matched the nested result

This suggests that, for the constructive nested cases observed so far,
the relevant upper admissibility constraint is the immediate left sibling bound only.

So the current local picture is:
- the immediate left sibling provides the effective ceiling when `j > 0`
- right siblings appear irrelevant to the obstruction
- siblings further left than the immediate left sibling also appear irrelevant

##### Apparent vacuity of lower-side constraints in the constructive regime

A further targeted probe suggests why right siblings have not produced independent obstructions
in the constructive nested cases observed so far.

In the sampled constructive chains, the final child generator did not decrease below the original child generator.
This was observed both:
- in small sampled cases where the rewritten child initially had generator `1`
- in a targeted probe where the rewritten child initially had generator `12`

In the latter probe:
- original parent form: `[500, 12]`
- rewritten slot: `1`
- sampled constructive chains explored: `18`
- observed violations of `final_h >= initial_h`: `0`

So, in the constructive regime observed so far, the lower-side sibling constraints appear vacuous:
if the original parent is canonical and the rewritten child does not decrease in the sampled constructive regime,
then the final child generator remains above every original sibling to its right in those observed cases.

This does not yet prove global monotonicity for all constructive nested chains.
But it supports the current local picture in which the only nontrivial observed admissibility bound
is the ceiling coming from the immediate left sibling.

#### Interpretation

This strengthens the earlier admissible-substitution picture.

The current working hypothesis is that, for nested constructive rewrites confined to one original slot:

- the obstruction is purely local
- it is determined by the original parent ordering constraints
- for `j > 0`, the only upper admissibility test is whether the final child generator stays below or equal to the immediate left sibling bound
- for `j = 0`, there is no such upper bound

This is still an empirical rule, not yet a general proof.
But it appears to explain the previously observed obstruction witness cleanly.

## Correction / refinement

The observations above about local slot ceilings remain useful, but they are not by themselves sufficient to guarantee global canonicity.

Further targeted witnesses show that a nested constructive chain can remain locally admissible at the rewritten node while still breaking canonicity at a higher ancestor on the path to the root.

So the stronger working hypothesis is no longer a purely local ceiling law at one parent.
Instead, the relevant condition appears to be pathwise:

- along the target path, every ancestor must continue to satisfy its immediate-left-sibling ceiling constraint
- a constructive chain becomes globally non-canonical as soon as one ancestor on that path violates its ceiling

Observed witness split:
- `4096`: the obstruction appears at the local parent of the rewritten slot
- canonical embedding `[2000, 900]`: the first constructive step remains canonical, but a deeper nested step breaks both the local target ceiling and the root-level ancestor ceiling

This suggests a pathwise ceiling law rather than a single-parent ceiling law.

##### Obstruction taxonomy: ancestor-only vs local obstruction

Further targeted witnesses separate two different failure modes for nested constructive chains.

Ancestor-only obstruction:
- the rewritten target node remains locally canonical
- but some higher ancestor on the path violates its ceiling
- so the overall tree becomes globally non-canonical even though the target node itself still respects local order

Observed witness:
- canonical embedding `[4000, 900]`
- after one locally canonical constructive step, the target becomes `[3, 2, 2]` and remains globally canonical
- after a second locally canonical constructive step, the target becomes `[3, 3, 2]`, still locally canonical
- but the root-level child generator becomes `5400`, exceeding the root ceiling `4000`
- so the failure is purely ancestral

Local obstruction:
- the rewritten target node itself becomes locally non-canonical
- global canonicity then fails automatically as well

Observed witness:
- canonical embedding `[20000, 900]`
- after one constructive step, the target becomes `[3, 2, 2]` and remains globally canonical
- after a second constructive step, the target becomes `[3, 4, 2]`
- this already violates the local ceiling at the target node
- global canonicity therefore fails as a consequence

This suggests that pathwise constructive obstruction splits into:
- local obstruction at the rewritten node
- ancestor-only obstruction higher on the path

##### Refinement: first bad ancestor need not be the root

Additional canonical embeddings show that, in one-step ancestor-only obstruction,
the first violated ceiling need not occur at the root.

Observed canonical witnesses:
- minimal standalone witness: `36 -> 324`, via a one-step internal constructive rewrite at path `(1,)`
- embedding `[576, 36]`, with an internal one-step constructive rewrite inside the embedded `36`
- embedding `[10000, 900]`, with an internal one-step constructive rewrite inside the embedded `900`

Important note:
the embedded witness notation above should be read as a targeted canonical embedding description,
not as a claim that the current `encode(h)` dump literally exposes `36` or `900` as an immediately readable subtree label with the current tooling.

Minimal standalone witness details:
- initial root child generators: `[2, 2]`
- rewritten local child generators: `[1] -> [2]`
- resulting root child generators: `[2, 4]`
- the rewritten local node remains locally canonical
- but the full tree becomes globally non-canonical

So local admissibility at the rewritten node is not sufficient for global canonicity.

In the embedded witnesses above:
- the notation is conceptual and describes a targeted canonical embedding scenario
- it should not yet be read as a fully replayed witness under the current tooling
- so these examples motivate the possibility of a non-root first bad ancestor, but do not yet establish it as a reproduced bounded fact

So the more accurate working rule is:

the first failure occurs at the first ancestor on the rewritten path whose ceiling is exceeded.

What is currently verified is the standalone-root case:
- for the minimal witness `36 -> 324`, the rewritten local node remains locally canonical
- the first bad ancestor is the root
- the first violation is the root inversion `[2, 2] -> [2, 4]`
- this is measured directly by the current pathwise classification helpers and tests

More generally, in the bounded root-failure family currently locked in tests:
- the rewritten local node remains locally canonical
- the first bad path is the root
- the first violation is a single local ceiling inversion at the root

What is currently verified about the embedded case is:

- under the current tooling, the current bounded one-step automatic scans have so far exhibited root failures only
- however, an `embedded_ancestor` witness is now reproducible via an explicit canonical embedding construction rather than by the current automatic scan
- in the bounded cases now locked in tests, the same local rewrite shifts from `root` failure to `embedded_ancestor` exactly when the higher ancestor absorbs the growth and the first lower ancestor does not

So the non-root formulation is now a bounded empirical fact with explicit canonical embeddings,
but not yet a settled general law for arbitrary constructive chains.

## Current picture

At this stage the rewrite behavior seems to split into three regimes:

1. disjoint rewrites  
   -> bottom-up forest aggregation

2. nested destructive rewrites  
   -> prune absorption

3. nested constructive rewrites  
   -> global canonicity appears to be controlled by pathwise ceiling constraints along the ancestor chain

## Open direction

A useful next step would be to formulate a local theory of rewrite admissibility / obstruction,
instead of searching immediately for a universal substitution law.
