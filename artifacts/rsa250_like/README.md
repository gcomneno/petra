# rsa250_like

Deterministic semiprime-like specimen with two 125-digit factors.

## Important
This specimen is intentionally hostile for the canonical PET builder front door.

It is **not** compatible with:

    python -m pet.cli build-from-factors ...

because that command requires NEW-canonical support starting at prime 2.

## Regeneration
Regenerate these files with:

    python tools/write_rsa250_like_artifact.py
