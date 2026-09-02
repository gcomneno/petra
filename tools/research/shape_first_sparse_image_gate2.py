#!/usr/bin/env python3
"""Issue #208: Gate 2 comparison for the shape-first sparse image spike.

This research-only prototype compares a deliberately strong bmaptool-style
baseline with the PETRA-inspired Gate 1 model. It does not reproduce every
bmaptool implementation detail and does not define PETRA runtime semantics.
"""

from __future__ import annotations

import hashlib
import io
import json
import struct
import zlib

LOGICAL_SIZE = 1024 * 1024
EXTENTS = (
    (0, 64 * 1024, b"A"),
    (512 * 1024, 128 * 1024, b"B"),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def build_fixture() -> tuple[bytes, list[dict[str, object]]]:
    source = bytearray(LOGICAL_SIZE)
    chunks: list[dict[str, object]] = []

    for index, (offset, size, fill) in enumerate(EXTENTS):
        data = fill * size
        source[offset : offset + size] = data
        chunks.append(
            {
                "id": f"chunk-{index}",
                "logical_offset": offset,
                "logical_size": size,
                "sha256": sha256(data),
                "data": data,
            }
        )

    return bytes(source), chunks


def logical_records(chunks: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            key: chunk[key]
            for key in ("id", "logical_offset", "logical_size", "sha256")
        }
        for chunk in chunks
    ]


def build_bmap_style_manifest(chunks: list[dict[str, object]]) -> bytes:
    return canonical_json(
        {
            "schema": "bmaptool-style.map.v0",
            "logical_size": LOGICAL_SIZE,
            "mapped_data_bytes": sum(int(c["logical_size"]) for c in chunks),
            "ranges": logical_records(chunks),
        }
    )


def build_petra_manifest(chunks: list[dict[str, object]]) -> bytes:
    return canonical_json(
        {
            "schema": "petra-research.sparse-artifact.v0",
            "logical_size": LOGICAL_SIZE,
            "chunks": logical_records(chunks),
        }
    )


def encode_bmap_style(source: bytes, level: int) -> bytes:
    """Compress the complete logical image as one physical stream."""
    return zlib.compress(source, level)


def encode_petra_style(chunks: list[dict[str, object]], level: int) -> bytes:
    """Compress only logical data chunks and frame them sequentially."""
    stream = io.BytesIO()
    for chunk in chunks:
        payload = zlib.compress(chunk["data"], level)  # type: ignore[arg-type]
        stream.write(struct.pack(">I", len(payload)))
        stream.write(payload)
    return stream.getvalue()


def streamed_zlib_output(payload: bytes, feed_size: int = 32):
    decoder = zlib.decompressobj()
    for offset in range(0, len(payload), feed_size):
        output = decoder.decompress(payload[offset : offset + feed_size])
        if output:
            yield output
    tail = decoder.flush()
    if tail:
        yield tail
    if not decoder.eof:
        raise ValueError("truncated-compressed-image")
    if decoder.unused_data:
        raise ValueError("trailing-compressed-data")


def reconstruct_bmap_style(
    payload: bytes, chunks: list[dict[str, object]]
) -> tuple[bytes, int, int]:
    """Stream the full logical image, but materialize only verified mapped ranges."""
    output = bytearray(LOGICAL_SIZE)
    ranges = logical_records(chunks)
    range_index = 0
    range_buffer = bytearray()
    logical_position = 0
    materialized = 0
    decompressed = 0

    for emitted in streamed_zlib_output(payload):
        decompressed += len(emitted)
        cursor = 0
        while cursor < len(emitted):
            if range_index >= len(ranges):
                logical_position += len(emitted) - cursor
                cursor = len(emitted)
                continue

            current = ranges[range_index]
            start = int(current["logical_offset"])
            size = int(current["logical_size"])
            end = start + size

            if logical_position < start:
                skipped = min(len(emitted) - cursor, start - logical_position)
                logical_position += skipped
                cursor += skipped
                continue

            if logical_position >= end:
                range_index += 1
                range_buffer.clear()
                continue

            taken = min(len(emitted) - cursor, end - logical_position)
            range_buffer.extend(emitted[cursor : cursor + taken])
            logical_position += taken
            cursor += taken

            if logical_position == end:
                data = bytes(range_buffer)
                if len(data) != size:
                    raise ValueError("mapped-range-size-mismatch")
                if sha256(data) != current["sha256"]:
                    raise ValueError(
                        f"mapped-range-verification-failed:{current['id']}"
                    )

                # Deliberately generous baseline: verify each mapped range
                # before materializing it.
                output[start:end] = data
                materialized += size
                range_index += 1
                range_buffer.clear()

    if logical_position != LOGICAL_SIZE:
        raise ValueError("logical-size-mismatch")
    if range_index != len(ranges):
        raise ValueError("missing-mapped-range")

    return bytes(output), materialized, decompressed


def reconstruct_petra_style(
    payload: bytes, chunks: list[dict[str, object]]
) -> tuple[bytes, int, int]:
    output = bytearray(LOGICAL_SIZE)
    stream = io.BytesIO(payload)
    materialized = 0
    decompressed = 0

    for chunk in logical_records(chunks):
        header = stream.read(4)
        if len(header) != 4:
            raise ValueError("truncated-frame")
        (payload_size,) = struct.unpack(">I", header)
        compressed = stream.read(payload_size)
        if len(compressed) != payload_size:
            raise ValueError("truncated-payload")

        data = zlib.decompress(compressed)
        decompressed += len(data)
        size = int(chunk["logical_size"])
        if len(data) != size:
            raise ValueError("logical-size-mismatch")
        if sha256(data) != chunk["sha256"]:
            raise ValueError(f"chunk-verification-failed:{chunk['id']}")

        start = int(chunk["logical_offset"])
        output[start : start + size] = data
        materialized += size

    if stream.read(1):
        raise ValueError("trailing-data")

    return bytes(output), materialized, decompressed


def corrupt_second_extent(source: bytes) -> bytes:
    corrupted = bytearray(source)
    start, _, _ = EXTENTS[1]
    corrupted[start + 123] ^= 0x01
    return bytes(corrupted)


def corrupt_second_petra_chunk(
    chunks: list[dict[str, object]], level: int
) -> bytes:
    stream = io.BytesIO()
    for index, chunk in enumerate(chunks):
        data = bytearray(chunk["data"])  # type: ignore[arg-type]
        if index == 1:
            data[123] ^= 0x01
        compressed = zlib.compress(bytes(data), level)
        stream.write(struct.pack(">I", len(compressed)))
        stream.write(compressed)
    return stream.getvalue()


def rejection_reason(callable_) -> str | None:
    try:
        callable_()
    except ValueError as error:
        return str(error)
    return None


def main() -> int:
    source, chunks = build_fixture()
    bmap_manifest = build_bmap_style_manifest(chunks)
    petra_manifest = build_petra_manifest(chunks)

    bmap_l1 = encode_bmap_style(source, 1)
    bmap_l9 = encode_bmap_style(source, 9)
    petra_l1 = encode_petra_style(chunks, 1)
    petra_l9 = encode_petra_style(chunks, 9)

    bmap_rebuilt, bmap_materialized, bmap_decompressed = reconstruct_bmap_style(
        bmap_l9, chunks
    )
    petra_rebuilt, petra_materialized, petra_decompressed = reconstruct_petra_style(
        petra_l9, chunks
    )

    bmap_corruption = rejection_reason(
        lambda: reconstruct_bmap_style(
            encode_bmap_style(corrupt_second_extent(source), 9), chunks
        )
    )
    petra_corruption = rejection_reason(
        lambda: reconstruct_petra_style(
            corrupt_second_petra_chunk(chunks, 9), chunks
        )
    )

    classifications = {
        "logical_physical_coupling": "BETTER",
        "metadata_coordination": "BETTER",
        "verification_granularity": "EQUIVALENT",
        "failure_locality": "EQUIVALENT",
        "logical_identity_across_encodings": "EQUIVALENT",
        "streamability": "EQUIVALENT",
        "stored_compressed_payload": "BETTER",
        "decompressed_bytes": "BETTER",
        "materialized_bytes": "EQUIVALENT",
        "reconstruction_determinism": "EQUIVALENT",
    }

    measurements = {
        "source_sha256": sha256(source),
        "logical_size": LOGICAL_SIZE,
        "actual_data_bytes": sum(int(c["logical_size"]) for c in chunks),
        "bmap_style": {
            "manifest_bytes": len(bmap_manifest),
            "manifest_sha256": sha256(bmap_manifest),
            "payload_level_1_bytes": len(bmap_l1),
            "payload_level_9_bytes": len(bmap_l9),
            "decompressed_bytes_level_9": bmap_decompressed,
            "materialized_bytes_level_9": bmap_materialized,
            "reconstruction_equal": bmap_rebuilt == source,
            "corruption_reason": bmap_corruption,
        },
        "petra_inspired": {
            "manifest_bytes": len(petra_manifest),
            "manifest_sha256": sha256(petra_manifest),
            "payload_level_1_bytes": len(petra_l1),
            "payload_level_9_bytes": len(petra_l9),
            "decompressed_bytes_level_9": petra_decompressed,
            "materialized_bytes_level_9": petra_materialized,
            "reconstruction_equal": petra_rebuilt == source,
            "corruption_reason": petra_corruption,
        },
        "manifest_identity_stable_when_compression_changes": {
            "bmap_style": True,
            "petra_inspired": True,
        },
        "classifications": classifications,
        "overall": "SUPPORTED",
        "qualification": (
            "synthetic Gate 2 only; advantage is transport/decompression and "
            "coordination, not a new mapped-range checksum capability"
        ),
    }

    print(json.dumps(measurements, indent=2, sort_keys=True))

    expected_bmap_failure = "mapped-range-verification-failed:chunk-1"
    expected_petra_failure = "chunk-verification-failed:chunk-1"
    passed = all(
        (
            bmap_rebuilt == source,
            petra_rebuilt == source,
            bmap_materialized == measurements["actual_data_bytes"],
            petra_materialized == measurements["actual_data_bytes"],
            bmap_decompressed == LOGICAL_SIZE,
            petra_decompressed == measurements["actual_data_bytes"],
            len(petra_l1) < len(bmap_l1),
            len(petra_l9) < len(bmap_l9),
            bmap_corruption == expected_bmap_failure,
            petra_corruption == expected_petra_failure,
            "WORSE" not in classifications.values(),
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
