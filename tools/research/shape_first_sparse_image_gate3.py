#!/usr/bin/env python3
"""Issue #213: adversarial pressure test for shape-first sparse artifacts.

Research-only. This probe compares a bmaptool-style full-image compressed stream
plus mapped-range metadata with a PETRA-inspired logical-chunk representation.
It does not define PETRA runtime semantics or benchmark production bmaptool.
"""

from __future__ import annotations

import hashlib
import json
import lzma
import random
import statistics
import struct
import time
import tracemalloc
import zlib

LOGICAL_SIZE = 4 * 1024 * 1024
CODECS = ("zlib", "xz")
WORKLOADS = (
    "dense-compressible",
    "dense-incompressible",
    "sparse-few-large-compressible",
    "sparse-few-large-incompressible",
    "sparse-many-small-compressible",
    "sparse-many-small-incompressible",
    "extreme-fragmentation",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def deterministic_bytes(size: int, seed: int) -> bytes:
    return random.Random(seed).randbytes(size)


def build_fixture(kind: str) -> tuple[bytes, list[tuple[int, int, bytes]]]:
    source = bytearray(LOGICAL_SIZE)
    extents: list[tuple[int, int, bytes]] = []

    def add(offset: int, size: int, data: bytes) -> None:
        source[offset : offset + size] = data
        extents.append((offset, size, data))

    if kind == "dense-compressible":
        add(0, LOGICAL_SIZE, b"ABCD" * (LOGICAL_SIZE // 4))
    elif kind == "dense-incompressible":
        add(0, LOGICAL_SIZE, deterministic_bytes(LOGICAL_SIZE, 1))
    elif kind == "sparse-few-large-compressible":
        for offset, size, fill in (
            (0, 512 * 1024, b"A"),
            (1536 * 1024, 512 * 1024, b"B"),
            (3 * 1024 * 1024, 256 * 1024, b"C"),
        ):
            add(offset, size, fill * size)
    elif kind == "sparse-few-large-incompressible":
        for index, (offset, size) in enumerate(
            (
                (0, 512 * 1024),
                (1536 * 1024, 512 * 1024),
                (3 * 1024 * 1024, 256 * 1024),
            )
        ):
            add(offset, size, deterministic_bytes(size, 10 + index))
    elif kind == "sparse-many-small-compressible":
        for index in range(256):
            size = 4096
            offset = index * 16384
            add(offset, size, bytes([65 + (index % 26)]) * size)
    elif kind == "sparse-many-small-incompressible":
        for index in range(256):
            size = 4096
            offset = index * 16384
            add(offset, size, deterministic_bytes(size, 1000 + index))
    elif kind == "extreme-fragmentation":
        for index in range(1024):
            size = 512
            offset = index * 4096
            add(offset, size, deterministic_bytes(size, 5000 + index))
    else:
        raise ValueError(f"unknown workload: {kind}")

    return bytes(source), extents


def compress(data: bytes, codec: str) -> bytes:
    if codec == "zlib":
        return zlib.compress(data, 9)
    if codec == "xz":
        return lzma.compress(data, format=lzma.FORMAT_XZ, preset=6)
    raise ValueError(codec)


def decompress(data: bytes, codec: str) -> bytes:
    if codec == "zlib":
        return zlib.decompress(data)
    if codec == "xz":
        return lzma.decompress(data, format=lzma.FORMAT_XZ)
    raise ValueError(codec)


def canonical_json(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("ascii")


def baseline_manifest(extents: list[tuple[int, int, bytes]]) -> tuple[bytes, dict]:
    obj = {
        "schema": "bmap-style.v0",
        "logical_size": LOGICAL_SIZE,
        "ranges": [
            {"offset": offset, "size": size, "sha256": sha256(data)}
            for offset, size, data in extents
        ],
    }
    return canonical_json(obj), obj


def petra_manifest(extents: list[tuple[int, int, bytes]]) -> tuple[bytes, dict]:
    obj = {
        "schema": "petra-research.sparse-artifact.v0",
        "logical_size": LOGICAL_SIZE,
        "chunks": [
            {
                "id": f"chunk-{index}",
                "logical_offset": offset,
                "logical_size": size,
                "sha256": sha256(data),
            }
            for index, (offset, size, data) in enumerate(extents)
        ],
    }
    return canonical_json(obj), obj


def timed_peak(callable_, repeats: int = 3):
    durations = []
    peaks = []
    result = None
    for _ in range(repeats):
        tracemalloc.start()
        started = time.perf_counter()
        result = callable_()
        durations.append(time.perf_counter() - started)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peaks.append(peak)
    return result, statistics.median(durations), max(peaks)


def encode_baseline(source: bytes, codec: str) -> bytes:
    return compress(source, codec)


def encode_petra(extents: list[tuple[int, int, bytes]], codec: str):
    stream = bytearray()
    payload_bytes = 0
    framing_bytes = 0
    for _, _, data in extents:
        payload = compress(data, codec)
        stream.extend(struct.pack(">I", len(payload)))
        stream.extend(payload)
        framing_bytes += 4
        payload_bytes += len(payload)
    return bytes(stream), payload_bytes, framing_bytes


def decode_baseline(payload: bytes, manifest: dict, codec: str):
    logical = decompress(payload, codec)
    if len(logical) != LOGICAL_SIZE:
        raise ValueError("logical-size-mismatch")
    output = bytearray(LOGICAL_SIZE)
    materialized = 0
    for index, entry in enumerate(manifest["ranges"]):
        offset = int(entry["offset"])
        size = int(entry["size"])
        data = logical[offset : offset + size]
        if sha256(data) != entry["sha256"]:
            raise ValueError(f"range-verification-failed:{index}")
        output[offset : offset + size] = data
        materialized += size
    return bytes(output), len(logical), materialized


def decode_petra(stream: bytes, manifest: dict, codec: str):
    view = memoryview(stream)
    position = 0
    output = bytearray(LOGICAL_SIZE)
    emitted = 0
    materialized = 0
    for entry in manifest["chunks"]:
        if position + 4 > len(view):
            raise ValueError("truncated-frame")
        payload_size = struct.unpack(">I", view[position : position + 4])[0]
        position += 4
        payload = bytes(view[position : position + payload_size])
        position += payload_size
        if len(payload) != payload_size:
            raise ValueError("truncated-payload")
        data = decompress(payload, codec)
        emitted += len(data)
        logical_size = int(entry["logical_size"])
        if len(data) != logical_size or sha256(data) != entry["sha256"]:
            raise ValueError(f"chunk-verification-failed:{entry['id']}")
        offset = int(entry["logical_offset"])
        output[offset : offset + logical_size] = data
        materialized += logical_size
    if position != len(view):
        raise ValueError("trailing-data")
    return bytes(output), emitted, materialized


def corruption_checks(source: bytes, extents, baseline_obj: dict, petra_obj: dict, codec: str):
    if len(extents) < 2:
        return {"baseline": "not-applicable", "petra": "not-applicable"}

    corrupted = bytearray(source)
    offset, _, _ = extents[1]
    corrupted[offset] ^= 0x01
    baseline_result = "not-rejected"
    try:
        decode_baseline(compress(bytes(corrupted), codec), baseline_obj, codec)
    except ValueError as error:
        baseline_result = str(error)

    corrupted_extents = list(extents)
    offset, size, data = corrupted_extents[1]
    changed = bytearray(data)
    changed[0] ^= 0x01
    corrupted_extents[1] = (offset, size, bytes(changed))
    stream, _, _ = encode_petra(corrupted_extents, codec)
    petra_result = "not-rejected"
    try:
        decode_petra(stream, petra_obj, codec)
    except ValueError as error:
        petra_result = str(error)

    return {"baseline": baseline_result, "petra": petra_result}


def run_row(workload: str, codec: str) -> dict:
    source, extents = build_fixture(workload)
    baseline_meta, baseline_obj = baseline_manifest(extents)
    petra_meta, petra_obj = petra_manifest(extents)

    baseline_payload, baseline_encode_seconds, baseline_encode_peak = timed_peak(
        lambda: encode_baseline(source, codec)
    )
    petra_encoded, petra_encode_seconds, petra_encode_peak = timed_peak(
        lambda: encode_petra(extents, codec)
    )
    petra_stream, petra_payload_bytes, petra_framing_bytes = petra_encoded

    baseline_decoded, baseline_decode_seconds, baseline_decode_peak = timed_peak(
        lambda: decode_baseline(baseline_payload, baseline_obj, codec)
    )
    petra_decoded, petra_decode_seconds, petra_decode_peak = timed_peak(
        lambda: decode_petra(petra_stream, petra_obj, codec)
    )
    baseline_output, baseline_emitted, baseline_materialized = baseline_decoded
    petra_output, petra_emitted, petra_materialized = petra_decoded

    if baseline_output != source or petra_output != source:
        raise AssertionError("reconstruction mismatch")

    return {
        "workload": workload,
        "codec": codec,
        "logical_bytes": LOGICAL_SIZE,
        "mapped_bytes": sum(size for _, size, _ in extents),
        "mapped_ranges": len(extents),
        "baseline_payload_bytes": len(baseline_payload),
        "petra_payload_bytes": petra_payload_bytes,
        "petra_framing_bytes": petra_framing_bytes,
        "baseline_manifest_bytes": len(baseline_meta),
        "petra_manifest_bytes": len(petra_meta),
        "baseline_transport_bytes": len(baseline_payload) + len(baseline_meta),
        "petra_transport_bytes": petra_payload_bytes + petra_framing_bytes + len(petra_meta),
        "baseline_decompressor_output_bytes": baseline_emitted,
        "petra_decompressor_output_bytes": petra_emitted,
        "baseline_materialized_bytes": baseline_materialized,
        "petra_materialized_bytes": petra_materialized,
        "baseline_encode_seconds": baseline_encode_seconds,
        "petra_encode_seconds": petra_encode_seconds,
        "baseline_decode_seconds": baseline_decode_seconds,
        "petra_decode_seconds": petra_decode_seconds,
        "baseline_encode_peak_bytes": baseline_encode_peak,
        "petra_encode_peak_bytes": petra_encode_peak,
        "baseline_decode_peak_bytes": baseline_decode_peak,
        "petra_decode_peak_bytes": petra_decode_peak,
        "source_sha256": sha256(source),
        "corruption": corruption_checks(source, extents, baseline_obj, petra_obj, codec),
    }


def main() -> int:
    rows = [run_row(workload, codec) for workload in WORKLOADS for codec in CODECS]
    print(json.dumps(rows, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
