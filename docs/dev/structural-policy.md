# PET structural policy

The PET builder-from-bytes IRSR path uses a structural profile policy layer to decide
which generic exponent profiles are attempted by default.

## Default policy

The default structural policy is intentionally conservative.

Enabled exponent profiles:

- `[2]`
- `[2, 1]`
- `[2, 1, 1]`

Enabled squarefree support profiles:

- `[1, 1, 1]`
- `[1, 1, 1, 1]`
- `[1, 1, 1, 1, 1]`

Deferred profiles include:

- `[3, 1]`

The backend may support broader profiles, but they are not automatically enabled
in the default policy.

## Radius

The default generic exponent structural radius is conservative.

For larger structured cases, use the explicit CLI override:

```bash
python -m pet.cli builder-from-bytes FILE.bin \
  --mode irsr \
  --irsr-structural-radius 64 \
  --json
```

Injected policy

Python callers can inject a custom structural policy through:

build_from_bytes_pipeline(
    path,
    output_dir,
    mode="irsr",
    irsr_structural_radius=64,
    irsr_structural_policy=policy,
)

The injected policy flows through:

build_from_bytes_pipeline
→ build_from_irsr_pipeline
→ _run_structural_profile_policy_v0
→ _generate_structural_profile_candidates_v1
→ generic backend

This allows broader policy experiments without changing the default policy.

Probe tool

Use:

python tools/pet_structural_policy_probe.py

The probe currently demonstrates that broader injected policies can build profiles
such as:

[3, 1]
[3, 2]
[2, 1, 1, 1]

These are probe-supported, not necessarily default-enabled.

Design rule

Default policy should remain safe and conservative.
Broader profiles should be tested through injected policies before being promoted.
