# PET hybrid workflow (end-to-end)

## Goal

Run the current hybrid PET pipeline from a difficult target integer to a forward executable candidate plan.

This workflow does **not** recover the exact PET of the target in general.

It does this instead:

1. probe partial certified structure from the target
2. translate the probe into bridge constraints
3. synthesize and rank PET-compatible candidates
4. materialize a forward constructive plan for a selected candidate
5. execute that plan and verify the resulting candidate generator

## Core tools

- `tools/partial_signature_probe.py`
- `tools/pet_hybrid_bridge.py`
- `tools/pet_hybrid_synthesize.py`
- `tools/pet_candidate_plan.py`
- `tools/pet_constructive_plan.py`

Auxiliary research tool:

- `tools/find_probe_status_examples.py`

## Minimal end-to-end sequence

Example target:

- `N = 212262408`

### 1. Probe the target

```bash
python tools/partial_signature_probe.py 212262408 --schedule 10 --json > /tmp/pet-probe-212262408.json
```

This extracts:

- certified known factors
- residual classification
- root lower bounds
- exact root anatomy only if the probe closes it

### 2. Build bridge constraints

```bash
python tools/pet_hybrid_bridge.py /tmp/pet-probe-212262408.json --json > /tmp/pet-bridge-212262408.json
```

This converts probe output into:

- hard constraints
- soft uncertainty
- synthesis hints

### 3. Synthesize and rank candidates

```bash
python tools/pet_hybrid_synthesize.py /tmp/pet-bridge-212262408.json --json > /tmp/pet-synth-212262408.json
```

This produces:

- one or more candidate PET explanations
- ranking
- status-aware behavior where supported

### 4. Build a forward plan for the selected candidate

```bash
python tools/pet_candidate_plan.py /tmp/pet-synth-212262408.json --rank 1 --json > /tmp/pet-candidate-plan-212262408.json
```

This produces:

- root primes
- root exponents
- forward steps
- `constructive_plan` payload

### 5. Execute the constructive plan

```bash
jq '.constructive_plan' /tmp/pet-candidate-plan-212262408.json > /tmp/pet-exec-plan-212262408.json
python tools/pet_constructive_plan.py /tmp/pet-exec-plan-212262408.json --json
```

This executes the plan and reports:

- final integer
- generator
- final signature
- local step history

## What to check at the end

The most important consistency checks are:

- candidate planner output:
  - `matches_candidate_root_generator = true`
- constructive execution output:
  - `already_minimal = true`
  - `generator = final_n`

When those hold, the ranked candidate has been successfully materialized as a valid forward constructive PET history.

## Residual status interpretation

Current practical reading:

- `prime-power-by-sympy`
  - often already yields `exact_root_anatomy = true`
  - usually does not require dedicated synthesis logic

- `perfect-power-composite-base`
  - currently the best open structured residual for status-aware synthesis
  - supported by a dedicated candidate/ranking behavior

- `composite-non-prime-power`
  - still open research territory
  - currently handled by generic strategies

## Non-claim

This workflow is **not** a replacement for integer factorization.

It is a constrained structural reconstruction workflow under explicit uncertainty.
