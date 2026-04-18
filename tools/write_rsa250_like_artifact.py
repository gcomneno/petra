from __future__ import annotations

import json
from pathlib import Path

P = 72882784824948594400286627895860428049337066678295002899479215802808504054739834300577632230021345735080173542649178932703573
Q = 94678932273813122340070183534126169636023368296354573716348377451444339454154608297391074856538178520407335789832845238736181


def main() -> int:
    out_dir = Path("artifacts/rsa250_like")
    out_dir.mkdir(parents=True, exist_ok=True)

    factor_spec = {
        "trust_primes": True,
        "factors": [
            [P, 1],
            [Q, 1],
        ],
    }

    n = P * Q
    meta = {
        "schema": "rsa250-like-spec-v0",
        "p_digits": len(str(P)),
        "q_digits": len(str(Q)),
        "n_digits": len(str(n)),
        "factor_count": 2,
        "support_kind": "hostile-semiprime",
        "pet_build_from_factors_compatible": False,
        "note": "Stored as a reproducible hostile specimen, not as a NEW-canonical build-from-factors input.",
    }

    readme = """# rsa250_like

Deterministic semiprime-like specimen with two 125-digit factors.

## Important
This specimen is intentionally hostile for the canonical PET builder front door.

It is **not** compatible with:

    python -m pet.cli build-from-factors ...

because that command requires NEW-canonical support starting at prime 2.

## Regeneration
Regenerate these files with:

    python tools/write_rsa250_like_artifact.py
"""

    (out_dir / "factor_spec.json").write_text(
        json.dumps(factor_spec, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (out_dir / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (out_dir / "README.md").write_text(readme, encoding="utf-8")

    print(f"artifacts_dir = {out_dir}")
    print(f"factor_spec = {out_dir / 'factor_spec.json'}")
    print(f"meta = {out_dir / 'meta.json'}")
    print(f"n_digits = {meta['n_digits']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
