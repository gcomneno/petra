# PET status boundary notes

## Scope

These notes summarize the current observed status boundaries for the hybrid PET reconstruction pipeline after adding batch evaluation, exploratory scans, and focused boundary scans.

## Established pipeline status

The following end-to-end path is now exercised by a dedicated evaluation harness:

1. `partial_signature_probe.py`
2. `pet_hybrid_bridge.py`
3. `pet_hybrid_synthesize.py`
4. `pet_candidate_plan.py`
5. `pet_constructive_plan.py`

The harness records per-case outcomes and aggregate summaries by family and by observed status.

## Main observed outcomes

### 1. The end-to-end hybrid pipeline is stable on controlled and exploratory batches

Controlled and exploratory batches both validated successfully end-to-end, with no observed:
- `no_candidate`
- `mismatch`
- `planner_failed`
- `executor_failed`

This confirms that the current research-facing reconstruction loop is operational rather than a single worked example.

### 2. `perfect-power-composite-base` is real but rare

The status `perfect-power-composite-base` is observed and useful, but it appears only on a narrow subset of cases.

In those cases:
- `exact_root_anatomy = false`
- the dedicated candidate `composite-power-base-completion` rises to rank 1
- the candidate planning and constructive execution loop validates successfully

This supports keeping the dedicated status-aware handling already introduced, but does not support treating this status as common.

### 3. `prime-power-by-sympy` is frequent when the residual closes semantically as a prime power

For scans of the form `2*p^2` with tight probe budget:
- many cases close as `prime-power-by-sympy`
- those cases typically have `exact_root_anatomy = true`
- the top candidate is usually `exact-root-anatomy`

This means the status is informative, but does not currently justify a separate synthesis strategy.

### 4. `composite-non-prime-power` is the dominant difficult-status basin

Across boundary scans and exploratory scans, many difficult cases collapse into:
- `composite-non-prime-power`

This basin absorbs cases from multiple nominal families:
- composite-square-like constructions
- prime-power-edge constructions
- rough composite products
- distinct-prime products beyond simple closures

Within this basin, the observed top-ranked candidate is stably:
- `grouped-leaf-completion`

This is the strongest current empirical regularity in the difficult-case region.


### 5. Probe threshold law inside `composite-non-prime-power`

A stronger empirical regularity now appears inside the `composite-non-prime-power` basin.

Across the currently checked cases, if a target remains `composite-non-prime-power` at schedule `s`
and then first closes to `unit` at schedule `t`, the observed law is:

- `t = smallest_prime_factor(penultimate_residual)`

where `penultimate_residual` means the residual seen at schedule `t - 1`.

Observed scope so far:
- checked on varied `composite-non-prime-power` cases from the repo scans and additional fresh scans
- includes semiprime penultimate residuals and multiplicity-heavy penultimate residuals
- no counterexample observed in the current checked set

Interpretation discipline:
- this is currently an empirical law of the bounded probe behavior
- it should **not** yet be stated as a general PET theorem
- it is still useful as a strong predictive rule for the current probe/status boundary behavior

## Negative results / non-rules

The scans also ruled out several naive explanations.

### 1. Nominal family does not determine observed status

The same apparent family shape can yield different observed statuses depending on arithmetic structure and probe behavior.

### 2. Prime-count alone does not determine the boundary

Distinct-prime product scans showed that the transition into `composite-non-prime-power` is not explained purely by the number of distinct primes.

### 3. Presence of factor `2` alone does not explain the boundary

A/B scans with and without `2` did not support a general rule that the factor `2` alone determines whether a case stays closed or falls into `composite-non-prime-power`.

## Current interpretation

The main discriminator is not the nominal formula of the target but the arithmetic structure of the residual that remains after bounded probe progress.

That is:
- some cases close exactly
- some cases close semantically as prime powers
- some rare cases close semantically as composite-base perfect powers
- many difficult cases remain in the broader `composite-non-prime-power` basin

## Budget-drain observation inside `composite-non-prime-power`

A further empirical observation is that the observed `composite-non-prime-power` basin drains rapidly as the probe schedule increases.

On the tracked difficult-case set used for focused follow-up:

- schedule `10`  -> `19/19` cases still in `composite-non-prime-power`
- schedule `13`  -> `10/19`
- schedule `17`  -> `5/19`
- schedule `19`  -> `3/19`
- schedule `23`  -> `2/19`
- schedule `89`  -> `1/19`
- schedule `191` -> `0/19`

Operational reading:

- the basin is real and important at tight bounded budgets
- but much of it is drained by additional arithmetic progress in the probe
- so the current dominance of `grouped-leaf-completion` should be read mainly as a strong low-budget reconstruction regularity, not yet as evidence for a separate mature synthesis regime

This further supports *not* adding a dedicated `composite-non-prime-power` synthesis strategy yet.

## Stable-before-closure window inside the CNPP ladder

A second empirical observation appears on the focused 16-case CNPP ladder followed across schedules
`10, 13, 17, 19, 23, 89, 191`.

For every target in that ladder that ever appears as `composite-non-prime-power`, the top-1 synthesis
candidate eventually becomes stable *before* exact closure.

Operationally, this means:

- `probe -> partial PET decomposition` may remain open for several schedules
- `synth -> PET reconstruction candidate` can already stop changing earlier
- exact closure can still happen later

This should be read as a pipeline-level empirical regularity, not as a general PET theorem.

Inside the current 16-case ladder:

- `11/11` targets that enter `composite-non-prime-power` show a non-empty stable-before-closure window
- in `9/11` cases the stable window is only one observed CNPP schedule point
- the persistent cases are currently:
  - `3928638`, with stable top-1 root generator `420` from schedule `10` through `23`, before exact closure at `89`
  - `20086291530`, with stable top-1 root generator `1260` from schedule `10` through `89`, before exact closure at `191`

So the strongest current reading is not that there is a broad new persistent CNPP regime, but that:

- stable-before-closure appears ubiquitous in the observed CNPP ladder
- long persistent stable windows are real but rare

A useful early discriminant also appears on the current CNPP ladder already by comparing schedules `10` and `13`.

Within the observed ladder:

- if a case is already `unit` at schedule `13`, it falls in the quick-closure regime
- if a case is still `composite-non-prime-power` at schedule `13` and the top-1 root generator changed from schedule `10`, it falls in the mobile-before-closure regime
- if a case is still `composite-non-prime-power` at schedule `13` and the top-1 root generator stayed unchanged from schedule `10`, it falls in the persistent-stable-before-closure regime

This is a useful empirical discriminant for the current ladder, not yet a general rule.

## Current recommendation

Do **not** add a dedicated synthesis strategy for `composite-non-prime-power` yet.

Current evidence supports:
- keeping the existing special handling for `perfect-power-composite-base`
- keeping generic strategies for the broad `composite-non-prime-power` basin
- treating the current phase as a completed validation/mapping phase rather than a strategy-expansion phase

## Next research target

The next promising line is to further characterize internal substructure inside the `composite-non-prime-power` basin before attempting any new status-specific synthesis rule.
