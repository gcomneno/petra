# Shape-first sparse image artifact spike

> [!IMPORTANT]
> **Research-only cross-domain experiment.** This document is not normative for
> PETRA, does not modify [`../../reference/SPEC.md`](../../reference/SPEC.md), and
> does not propose a bmaptool or Yocto change.

Tracking issue: #205.

## Question

Can one canonical logical sparse-image description remain independent from its
physical compressed representation while still supporting deterministic
reconstruction, sparse-aware materialization, and verification of each logical
chunk before that chunk is written?

This spike tests a transfer of one PETRA design principle:

```text
canonical structure first
→ physical projection second
```

It does **not** use the PETRA object model or PETRA operators as an image format.

## Frozen Gate 1 contract

The first experiment is deliberately small:

- logical image size: 1 MiB;
- data extent A: 64 KiB at logical offset 0;
- data extent B: 128 KiB at logical offset 512 KiB;
- every uncovered logical byte is zero/sparse;
- the canonical manifest contains logical size, ordered logical offsets, logical
  sizes, stable chunk identifiers, and SHA-256 of each uncompressed logical
  chunk;
- compressed offsets and compression level do not participate in the logical
  manifest or chunk identity;
- each chunk is independently zlib-compressed;
- a consumer must decompress and verify a chunk before materializing it at its
  logical offset.

The prototype is [`../../../tools/research/shape_first_sparse_image_spike.py`](../../../tools/research/shape_first_sparse_image_spike.py).

## Falsification conditions

Gate 1 fails if any of the following is required:

1. physical compressed offsets must become part of logical chunk identity;
2. the whole physical artifact must be available before a chunk can be
   verified;
3. sparse reconstruction is ambiguous from the logical manifest;
4. changing only the compression encoding changes the logical artifact;
5. corrupted logical content can be materialized before its digest failure is
   detected.

No bmaptool-specific conclusion follows merely from passing this gate.

## Prototype result

A controlled execution of the Gate 1 prototype produced:

| Measurement | Result |
| --- | ---: |
| Logical image size | 1,048,576 bytes |
| Logical data bytes | 196,608 bytes |
| Canonical manifest | 352 bytes |
| zlib level 1 payload | 912 bytes |
| zlib level 9 payload | 244 bytes |
| Materialized bytes | 196,608 bytes |
| Physical encodings differ | yes |
| Level 1 reconstruction equals source | yes |
| Level 9 reconstruction equals source | yes |
| Corrupted second chunk rejected | yes |

Canonical manifest SHA-256:

```text
b5ab363d6457c37bc291e0b5e963b280595674d7101acb5157843d9a33918539
```

Source and both reconstructed-image SHA-256 values:

```text
371a7de9d856146287ec1de0598228223d2ab0b5fbbf75563b43b2ef32a72c7d
```

The deliberately corrupted second logical chunk failed with:

```text
chunk-verification-failed:chunk-1
```

The consumer performs that digest check before the materialization statement,
so the rejected chunk is not accepted into the reconstructed logical image.

## Gate 1 interpretation

**Result: SUPPORTED, narrowly.**

Within this synthetic boundary, the experiment demonstrates that:

- sparse regions need not be serialized as payload;
- one logical manifest can describe two physically different compressed
  encodings;
- logical chunk identity can be based on uncompressed logical content rather
  than compressed byte position;
- independently compressed chunks can be consumed sequentially;
- each chunk can be verified before its logical bytes are materialized;
- both physical encodings reconstruct the same byte-for-byte logical image.

This is evidence for the transferred shape-first principle, not yet evidence
that a PETRA-inspired design improves bmaptool.

## What Gate 1 does not prove

The experiment does not yet test:

- a real sparse file or block device;
- `.bmap` semantics or compatibility;
- Yocto `.wic` images;
- filesystem allocation behavior;
- network streaming;
- signatures or provenance;
- random access;
- resumability;
- chunk-boundary strategy;
- adversarial manifests;
- metadata overhead at realistic scale;
- performance against bmaptool;
- whether this architecture is simpler or better than bmaptool's current
  separation of image, compression, and `.bmap`.

## Next falsifiable gate

The next experiment should compare the same deterministic synthetic image under
**two models**:

```text
current-style model
image + sparse map + compressed transport

PETRA-inspired model
canonical logical artifact
→ sparse/compressed/materialized projections
```

The comparison should measure at least:

- logical-to-physical coupling;
- metadata needed to reconstruct the image;
- verification granularity and failure locality;
- stored bytes and written bytes;
- determinism across physical encodings;
- whether streaming requires whole-artifact knowledge;
- complexity introduced by keeping sparse mapping and compression separate.

Only a demonstrated advantage on one or more of those properties would support
calling this a real-world PETRA paradigm use case rather than a successful
analogy.
