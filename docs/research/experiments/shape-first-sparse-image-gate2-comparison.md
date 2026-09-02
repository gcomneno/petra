# Shape-first sparse image artifact — Gate 2 comparison

> [!IMPORTANT]
> Research-only evidence for #205 / #208. This document is not normative PETRA semantics, not a PETRA roadmap commitment, and not a bmaptool/Yocto integration proposal.

## Question

Does a PETRA-inspired logical-first artifact model provide a measurable engineering advantage over a current bmaptool-style separation between:

- a logical image;
- a bmap-like logical mapped-range description with SHA-256 checksums;
- a separately compressed full-image transport stream?

The comparison reuses the exact Gate 1 logical fixture and data extents.

## Baseline correction before execution

The baseline was deliberately strengthened after checking current bmaptool documentation.

Current bmaptool already:

- stores SHA-256 checksums for mapped areas in the bmap;
- verifies mapped image data while copying;
- supports compressed images by decompressing them on-the-fly;
- writes only mapped areas to the destination.

Reference:

- <https://github.com/yoctoproject/bmaptool/blob/main/README.md>

Therefore this gate does **not** claim that PETRA-inspired chunk hashes invent mapped-range verification.

## Frozen fixture

Logical image size:

```text
1,048,576 bytes
```

Mapped/data bytes:

```text
196,608 bytes
```

Layout:

```text
0 KiB                                                         1024 KiB

[ DATA A: 64 KiB ][ HOLE ][ DATA B: 128 KiB ][      HOLE      ]
```

Source SHA-256:

```text
371a7de9d856146287ec1de0598228223d2ab0b5fbbf75563b43b2ef32a72c7d
```

## Compared models

### A — bmaptool-style baseline

The full logical image is compressed as one zlib stream.

A separate logical map contains:

- logical image size;
- mapped-data byte count;
- ordered mapped ranges;
- logical offset and length for each range;
- SHA-256 of each mapped range.

The consumer sequentially decompresses the complete logical image, discards bytes belonging to holes, verifies each complete mapped range, and only then materializes that range.

The prototype intentionally gives the baseline a stronger failure-locality contract than is required for this experiment: an entire mapped range is buffered and verified before it is written.

### B — PETRA-inspired

A canonical logical manifest contains:

- logical image size;
- ordered logical data chunks;
- logical offset and length for each chunk;
- SHA-256 of each logical chunk.

Only logical data chunks are independently compressed and framed in the payload stream. Uncovered logical intervals are sparse regions and therefore do not appear in the compressed payload.

Each chunk is decompressed, verified against its logical digest, and only then materialized at its logical offset.

## Measurements

| Measurement | bmaptool-style | PETRA-inspired |
|---|---:|---:|
| Logical image bytes | 1,048,576 | 1,048,576 |
| Logical data bytes | 196,608 | 196,608 |
| Manifest bytes | 367 | 352 |
| zlib level 1 payload bytes | 4,602 | 912 |
| zlib level 9 payload bytes | 1,046 | 244 |
| Bytes emitted by decompression, level 9 | 1,048,576 | 196,608 |
| Bytes materialized | 196,608 | 196,608 |
| Reconstruction equals source | yes | yes |

The manifest-size difference is small and is not treated as a material result. The useful distinction is that the bmaptool-style compressed stream still projects the complete logical image, including sparse zero regions, whereas the PETRA-inspired stream projects only declared logical data chunks.

At zlib level 9, the PETRA-inspired payload is 244 bytes versus 1,046 bytes for the full-image stream. More importantly for this synthetic fixture, its decompressor emits only 196,608 logical data bytes instead of all 1,048,576 logical bytes.

## Corruption test

The second mapped data region/chunk was modified while the expected logical SHA-256 remained unchanged.

bmaptool-style result:

```text
mapped-range-verification-failed:chunk-1
```

PETRA-inspired result:

```text
chunk-verification-failed:chunk-1
```

Both models reject the corrupted logical region before accepting/materializing it in this prototype.

Therefore verification granularity and failure locality are classified as equivalent in Gate 2.

## Frozen-axis classification

| Axis | PETRA-inspired classification | Evidence / qualification |
|---|---|---|
| Logical/physical coupling | `BETTER` | Logical chunks are primary and compressed frames are projections; physical compressed offsets do not define identity. |
| Metadata coordination | `BETTER` | One logical chunk record directly drives verification and materialization; the baseline coordinates a separate full-image transport with its logical range map. The byte-size difference itself is not material. |
| Verification granularity | `EQUIVALENT` | Both models have per-logical-range SHA-256 evidence. |
| Failure locality | `EQUIVALENT` | Both prototypes reject the corrupted second logical range before materialization. |
| Logical identity across physical encodings | `EQUIVALENT` | Both logical manifests remain independent from zlib level 1 vs level 9 encoding. |
| Streamability | `EQUIVALENT` | Both can be consumed sequentially without requiring the complete compressed payload in memory. |
| Stored compressed payload | `BETTER` | 912 vs 4,602 bytes at level 1; 244 vs 1,046 bytes at level 9. |
| Bytes emitted by decompression | `BETTER` | 196,608 vs 1,048,576 bytes. Sparse holes never enter the PETRA-inspired decompressed stream. |
| Bytes materialized | `EQUIVALENT` | Both write 196,608 logical data bytes. |
| Reconstruction determinism | `EQUIVALENT` | Both reconstruct the exact same source SHA-256. |

No frozen axis is classified `WORSE` in this synthetic gate.

## Result

```text
SUPPORTED
```

The support is **specific and bounded**.

Gate 2 provides evidence that a PETRA-inspired logical-chunk-first representation can improve the transport/decompression projection of a sparse logical image while retaining mapped-range verification, streaming consumption, sparse-aware materialization, deterministic reconstruction, and encoding-independent logical identity.

The strongest observed advantage is not a new checksum feature. bmaptool already has logical mapped-range checksums. The advantage is that sparse absence becomes structural before compression, so bytes belonging to holes are absent from the compressed/decompressed data projection instead of merely compressing well and being skipped at write time.

## Non-claims

This gate does **not** establish that:

- the prototype is a production image format;
- the synthetic payload ratios generalize to real Yocto images;
- PETRA runtime objects or operators should be used for disk images;
- bmaptool should be replaced;
- the prototype is faster on real hardware;
- independent chunk compression always beats whole-stream compression for every image topology;
- metadata coordination is materially simpler at real-world scale;
- a new upstream proposal is justified yet.

Those questions require later gates with realistic image topology, compressor choices, chunk-boundary costs, memory/CPU measurement, and eventually real bmaptool behavior.

## Reproduction

```text
python tools/research/shape_first_sparse_image_gate2.py
```

Expected overall result:

```text
"overall": "SUPPORTED"
```

The script exits zero only when both reconstructions are exact, both corruption checks fire at the expected logical range, materialized-byte counts match, the PETRA-inspired decompressor emits only mapped logical bytes, and no frozen comparison axis is classified `WORSE`.

## Next research question

Gate 2 is enough to justify continuing, but not enough to call this a production use-case.

The next falsification pressure should use a more realistic sparse-image topology and ask whether the observed advantage survives:

- many small mapped ranges;
- poorly compressible mapped data;
- chunk framing overhead;
- compressors used in real image distribution;
- CPU and memory accounting;
- realistic bmaptool mapped-range behavior.

Issue #205 therefore remains open.
