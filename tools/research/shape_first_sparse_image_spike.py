#!/usr/bin/env python3
"""Issue #205: minimal shape-first sparse image research spike.

This is a research-only prototype. It does not define PETRA runtime semantics or
an image format. The experiment tests whether one canonical logical layout can
remain stable while physical compression changes, and whether chunks can be
verified before materialization.
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


def build_fixture() -> tuple[bytes, list[dict[str, object]], bytes]:
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

    manifest_object = {
        "schema": "petra-research.sparse-artifact.v0",
        "logical_size": LOGICAL_SIZE,
        "chunks": [
            {
                key: chunk[key]
                for key in ("id", "logical_offset", "logical_size", "sha256")
            }
            for chunk in chunks
        ],
    }
    manifest = json.dumps(
        manifest_object, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return bytes(source), chunks, manifest


def encode(chunks: list[dict[str, object]], level: int) -> bytes:
    stream = io.BytesIO()
    for chunk in chunks:
        payload = zlib.compress(chunk["data"], level)  # type: ignore[arg-type]
        stream.write(struct.pack(">I", len(payload)))
        stream.write(payload)
    return stream.getvalue()


def reconstruct(
    stream_bytes: bytes,
    chunks: list[dict[str, object]],
) -> tuple[bytes, int]:
    output = bytearray(LOGICAL_SIZE)
    stream = io.BytesIO(stream_bytes)
    materialized = 0

    for chunk in chunks:
        header = stream.read(4)
        if len(header) != 4:
            raise ValueError("truncated-frame")

        (payload_size,) = struct.unpack(">I", header)
        payload = stream.read(payload_size)
        if len(payload) != payload_size:
            raise ValueError("truncated-payload")

        data = zlib.decompress(payload)
        logical_size = int(chunk["logical_size"])
        if len(data) != logical_size:
            raise ValueError("logical-size-mismatch")
        if sha256(data) != chunk["sha256"]:
            raise ValueError(f"chunk-verification-failed:{chunk['id']}")

        # Materialization happens only after logical-content verification.
        offset = int(chunk["logical_offset"])
        output[offset : offset + logical_size] = data
        materialized += logical_size

    if stream.read(1):
        raise ValueError("trailing-data")

    return bytes(output), materialized


def encode_corrupted_second_chunk(
    chunks: list[dict[str, object]], level: int
) -> bytes:
    stream = io.BytesIO()
    for index, chunk in enumerate(chunks):
        data = bytearray(chunk["data"])  # type: ignore[arg-type]
        if index == 1:
            data[123] ^= 0x01
        payload = zlib.compress(bytes(data), level)
        stream.write(struct.pack(">I", len(payload)))
        stream.write(payload)
    return stream.getvalue()


def main() -> int:
    source, chunks, manifest = build_fixture()
    payload_level_1 = encode(chunks, 1)
    payload_level_9 = encode(chunks, 9)

    reconstructed_1, materialized_1 = reconstruct(payload_level_1, chunks)
    reconstructed_9, materialized_9 = reconstruct(payload_level_9, chunks)

    corruption_rejected = False
    corruption_reason = None
    try:
        reconstruct(encode_corrupted_second_chunk(chunks, 9), chunks)
    except ValueError as error:
        corruption_reason = str(error)
        corruption_rejected = corruption_reason == "chunk-verification-failed:chunk-1"

    measurements = {
        "logical_size": LOGICAL_SIZE,
        "actual_data_bytes": sum(int(chunk["logical_size"]) for chunk in chunks),
        "manifest_bytes": len(manifest),
        "manifest_sha256": sha256(manifest),
        "payload_level_1_bytes": len(payload_level_1),
        "payload_level_9_bytes": len(payload_level_9),
        "physical_encodings_differ": payload_level_1 != payload_level_9,
        "source_sha256": sha256(source),
        "reconstructed_level_1_sha256": sha256(reconstructed_1),
        "reconstructed_level_9_sha256": sha256(reconstructed_9),
        "reconstruction_level_1_equal": reconstructed_1 == source,
        "reconstruction_level_9_equal": reconstructed_9 == source,
        "materialized_bytes_level_1": materialized_1,
        "materialized_bytes_level_9": materialized_9,
        "corruption_rejected_before_materialization": corruption_rejected,
        "corruption_reason": corruption_reason,
    }

    print(json.dumps(measurements, indent=2, sort_keys=True))

    passed = all(
        (
            measurements["physical_encodings_differ"],
            measurements["reconstruction_level_1_equal"],
            measurements["reconstruction_level_9_equal"],
            measurements["corruption_rejected_before_materialization"],
            materialized_1 == measurements["actual_data_bytes"],
            materialized_9 == measurements["actual_data_bytes"],
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
