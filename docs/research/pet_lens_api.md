# PET lens advisory API for OCF integration

PET exposes a small, deterministic advisory API for optional OCF integration.

The API is intentionally conservative:

- PET suggests candidate plans.
- OCF remains responsible for autopick, measurement, verification, artifact writing, and final plan selection.
- PET does not read or modify OCF artifacts.
- PET does not bypass OCF codecs or layers.

## API version

    pet.lens.v1

## Public entry point

    from pet.lens_api import analyze

    result = analyze(context)

The public function is:

    analyze(context) -> dict

The returned dictionary is shaped so it can be mapped to an OCF LensResult.

## Responsibility boundary

PET is an advisory structural lens.

PET may:

- inspect the provided context;
- emit hints;
- suggest candidate plans;
- explain fallback reasons.

PET must not:

- choose the final OCF plan;
- replace OCF autopick;
- measure compression;
- verify OCF artifact correctness;
- read OCF artifacts directly;
- write OCF artifacts;
- use network access;
- run subprocesses;
- perform hidden side effects.

OCF remains responsible for:

- candidate measurement;
- final plan selection;
- codec execution;
- layer execution;
- verification;
- artifact creation.

## Context shape

OCF passes a controlled context to PET.

Example:

    {
        "target": "bucket:00",
        "scope": "dir-autopick",
        "metrics": {
            "numeric_ratio": 0.75,
            "sample_size": 2048
        },
        "available_layers": ["TEXT", "NUMS"],
        "available_codecs": ["raw", "num_v1", "num_v2"],
        "constraints": {
            "max_candidates": 3
        }
    }

Current recognized fields:

- `target`: target identifier, usually an OCF bucket or planning target.
- `scope`: OCF planning scope.
- `metrics`: controlled metrics supplied by OCF.
- `available_layers`: layer identifiers OCF allows PET to suggest.
- `available_codecs`: codec identifiers OCF allows PET to suggest.
- `constraints`: optional constraints, currently including `max_candidates`.

PET treats missing, invalid, or unsupported context explicitly.

## Result shape

PET always returns:

    {
        "lens_id": "pet",
        "api_version": "pet.lens.v1",
        "target": "...",
        "hints": [],
        "candidate_plans": [],
        "resources": [],
        "confidence": "none|low|medium",
        "reason": "..."
    }

Required fields:

- `lens_id`
- `api_version`
- `target`
- `hints`
- `candidate_plans`
- `resources`
- `confidence`
- `reason`

`resources` is present even when empty.

## Candidate plan shape

Each candidate plan is shaped for OCF mapping:

    {
        "layer_id": "NUMS",
        "codec_text": "num_v2",
        "stream_codecs": {
            "NUMS": "num_v2"
        },
        "note": "PET advisory only; OCF autopick must measure and verify"
    }

Required candidate fields:

- `layer_id`
- `codec_text`
- `stream_codecs`
- `note`

PET must only suggest layers and codecs that are present in the input context.

## Current advisory behavior

The initial `pet.lens.v1` behavior is deliberately narrow.

PET may suggest:

    NUMS:num_v2

only when:

- `metrics.numeric_ratio >= 0.60`;
- `NUMS` is present in `available_layers`;
- `num_v2` is present in `available_codecs`;
- `constraints.max_candidates` is not zero.

Example result:

    {
        "lens_id": "pet",
        "api_version": "pet.lens.v1",
        "target": "bucket:00",
        "hints": [
            {
                "kind": "numeric-heavy",
                "message": "target metrics suggest numeric stream structure"
            }
        ],
        "candidate_plans": [
            {
                "layer_id": "NUMS",
                "codec_text": "num_v2",
                "stream_codecs": {
                    "NUMS": "num_v2"
                },
                "note": "PET advisory only; OCF autopick must measure and verify"
            }
        ],
        "resources": [],
        "confidence": "low",
        "reason": "numeric-heavy metrics and num_v2 available"
    }

PET does not claim this plan is optimal or correct.

OCF must still measure, compare, select, and verify.

## Fallback behavior

PET returns explicit fallback results for missing, invalid, or unsupported context.

Empty context:

    {
        "lens_id": "pet",
        "api_version": "pet.lens.v1",
        "target": "unknown",
        "hints": [],
        "candidate_plans": [],
        "resources": [],
        "confidence": "none",
        "reason": "insufficient context for PET advisory"
    }

Missing target:

    reason = insufficient context for PET advisory: missing target

Missing required field:

    reason = insufficient context for PET advisory: missing metrics
    reason = insufficient context for PET advisory: missing available_layers
    reason = insufficient context for PET advisory: missing available_codecs

Invalid field:

    reason = invalid context for PET advisory: invalid metrics
    reason = invalid context for PET advisory: invalid available_layers
    reason = invalid context for PET advisory: invalid available_codecs
    reason = invalid context for PET advisory: invalid constraints

Unsupported but valid context:

    reason = unsupported context for PET advisory

## Determinism and side effects

`pet.lens.v1` is deterministic for the same input.

The API does not intentionally use:

- network access;
- filesystem access;
- subprocesses;
- random values;
- timestamps;
- hidden mutable external state.

The output is JSON-serializable.

## Integration summary for OCF

The intended integration point is before OCF autopick.

OCF can call:

    analyze(context)

Then OCF may translate the returned `candidate_plans` into its own LensResult /
LensCandidatePlan objects.

PET suggestions are advisory only.

OCF still owns:

- autopick;
- measurement;
- verification;
- final selection;
- artifact writes.
