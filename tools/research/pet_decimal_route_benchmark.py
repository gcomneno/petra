#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import time

from pet_decimal_boundary_study import decimal_boundary_profile

def coerce_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value


def run_pipeline(n: int, timeout_seconds: float) -> tuple[str, str, float]:
    command = [
        "bash",
        "tools/pet_triage_pipeline.sh",
        str(n),
        "--operator-depth",
        "0",
        "--blade-window",
        "active",
        "--route-only",
        "--decimal-rigid-shallow-route",
    ]

    start = time.monotonic()
    try:
        result = subprocess.run(
            command,
            check=False,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - start
        output = coerce_output(exc.stdout) + coerce_output(exc.stderr)
        return "timeout", output, elapsed

    elapsed = time.monotonic() - start
    output = result.stdout + result.stderr

    if result.returncode != 0:
        return f"error:{result.returncode}", output, elapsed

    return "ok", output, elapsed


def extract_value(text: str, key: str) -> str:
    prefix = f"{key} = "
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix):]
    return "unknown"


def route_mode(output: str, status: str) -> str:
    if status == "timeout":
        return "timeout"
    if status.startswith("error:"):
        return status
    if "shallow_route_status = available" in output:
        return "shallow"
    if "route_kind = " in output:
        return "race"
    return "unknown"


def route_kind(output: str, mode: str) -> str:
    if mode == "shallow":
        return extract_value(output, "shallow_route_kind")
    if mode == "race":
        return extract_value(output, "route_kind")
    if mode == "timeout":
        return "timeout-before-route"
    return "unknown"


def format_float(value: float) -> str:
    return f"{value:.3f}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark PET decimal-rigid shallow route behavior."
    )
    parser.add_argument("numbers", nargs="+", type=int, metavar="N")
    parser.add_argument("--timeout", type=float, default=45.0)
    args = parser.parse_args()

    fields = [
        "N",
        "digits",
        "decimal_rigid_border_score",
        "decimal_rigid_border_hint",
        "mode",
        "route_kind",
        "elapsed_seconds",
    ]

    print(" ".join(fields))

    for n in args.numbers:
        profile = decimal_boundary_profile(n)
        status, output, elapsed = run_pipeline(n, args.timeout)
        mode = route_mode(output, status)

        row = {
            "N": str(n),
            "digits": str(profile["digits"]),
            "decimal_rigid_border_score": format_float(
                float(profile["decimal_rigid_border_score"])
            ),
            "decimal_rigid_border_hint": str(profile["decimal_rigid_border_hint"]),
            "mode": mode,
            "route_kind": route_kind(output, mode),
            "elapsed_seconds": f"{elapsed:.2f}",
        }

        print(" ".join(row[field] for field in fields))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
