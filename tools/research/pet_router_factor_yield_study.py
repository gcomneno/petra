#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from io import StringIO
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=repo_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def extract_key(text: str, key: str) -> str:
    prefix = f"{key} = "
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix):]
    return "unknown"


def extract_suggested_command(text: str) -> list[str] | None:
    raw = extract_key(text, "suggested_command")
    if raw == "unknown":
        return None
    return raw.split()


def extract_suggested_verifier_command(text: str) -> list[str] | None:
    raw = extract_key(text, "suggested_verifier_command")
    if raw == "unknown":
        return None
    return raw.split()


def run_pipeline(n_text: str) -> str:
    result = run_command(
        [
            "tools/core/pet_triage_pipeline.sh",
            n_text,
            "--route-only",
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"pipeline failed for {n_text}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result.stdout


def extract_factor_candidates(text: str) -> list[str]:
    patterns = [
        r"\bfactor\s*=\s*([^\s]+)",
        r"\bdivisor\s*=\s*([^\s]+)",
        r"\bfound_factor\s*=\s*([^\s]+)",
        r"\bfound_divisor\s*=\s*([^\s]+)",
        r"\bnontrivial_divisor\s*=\s*([^\s]+)",
    ]
    found: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            value = match.group(1).strip().rstrip(",")
            if value not in found:
                found.append(value)
    return found


def factor_found_status(text: str) -> tuple[str, str]:
    known_factorization = extract_key(text, "known_factorization")
    if known_factorization != "unknown" and known_factorization not in {"-", "", "none"}:
        return "yes", known_factorization

    best_factor = extract_key(text, "best_factor")
    if best_factor != "unknown" and best_factor not in {"-", "", "1"}:
        return "yes", best_factor

    candidates = extract_factor_candidates(text)
    if candidates:
        return "yes", ",".join(candidates)

    lowered = text.lower()
    weak_positive_markers = [
        "found factor",
        "found divisor",
        "nontrivial divisor",
        "verified-factor",
    ]
    if any(marker in lowered for marker in weak_positive_markers):
        return "maybe", "unparsed"

    return "no", "-"


def run_suggested_command(parts: list[str] | None) -> tuple[str, str, str, str]:
    if parts is None:
        return "unavailable", "-", "no-command", "-"

    result = run_command(parts)
    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    found_status, found_value = factor_found_status(combined)

    if result.returncode != 0:
        return "failed", found_status, found_value, combined.strip().splitlines()[0] if combined.strip() else "-"

    return "ok", found_status, found_value, "-"


def run_suggested_verifier(parts: list[str] | None) -> tuple[str, str, str, str, str]:
    if parts is None:
        return "unavailable", "-", "-", "no-command", "-"

    result = run_command(parts)
    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    usable_factor_count = extract_key(combined, "usable_factor_count")
    best_factor = extract_key(combined, "best_factor")
    found_status, found_value = factor_found_status(combined)

    if result.returncode != 0:
        return (
            "failed",
            usable_factor_count if usable_factor_count != "unknown" else "-",
            best_factor if best_factor != "unknown" else "-",
            found_status,
            combined.strip().splitlines()[0] if combined.strip() else "-",
        )

    return (
        "ok",
        usable_factor_count if usable_factor_count != "unknown" else "-",
        best_factor if best_factor != "unknown" else "-",
        found_status,
        "-",
    )


def router_row(n_text: str) -> dict[str, str]:
    result = run_command(
        [
            "tools/research/pet_shadow_monster_router.py",
            n_text,
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"router failed for {n_text}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    rows = list(csv.DictReader(StringIO(result.stdout), delimiter="\t"))
    if len(rows) != 1:
        raise RuntimeError(f"expected 1 router row for {n_text}, got {len(rows)}")
    return dict(rows[0])


def study_row(n_text: str) -> dict[str, str]:
    pipeline_output = run_pipeline(n_text)
    router = router_row(n_text)

    suggested_parts = extract_suggested_command(pipeline_output)
    suggested_verifier_parts = extract_suggested_verifier_command(pipeline_output)
    suggested_command = "-" if suggested_parts is None else " ".join(suggested_parts)
    suggested_verifier_command = "-" if suggested_verifier_parts is None else " ".join(suggested_verifier_parts)

    route_kind = extract_key(pipeline_output, "route_kind")
    route_trial_limit_hint = extract_key(pipeline_output, "route_trial_limit_hint")
    triage_router_monster_class = extract_key(pipeline_output, "triage_router_monster_class")

    command_status, factor_found, factor_value, command_error = run_suggested_command(suggested_parts)
    verifier_status, usable_factor_count, best_factor, verifier_factor_found, verifier_error = run_suggested_verifier(suggested_verifier_parts)

    return {
        "N": n_text,
        "monster_class": router.get("monster_class", "-"),
        "recommended_strategy": router.get("recommended_strategy", "-"),
        "route_confidence": router.get("route_confidence", "-"),
        "route_kind": route_kind,
        "route_trial_limit_hint": route_trial_limit_hint,
        "triage_router_monster_class": triage_router_monster_class,
        "suggested_command": suggested_command,
        "command_status": command_status,
        "factor_found": factor_found,
        "factor_value": factor_value,
        "command_error": command_error,
        "suggested_verifier_command": suggested_verifier_command,
        "verifier_status": verifier_status,
        "verifier_factor_found": verifier_factor_found,
        "usable_factor_count": usable_factor_count,
        "best_factor": best_factor,
        "verifier_error": verifier_error,
        "claim": "study only; classic and verifier factor detection is heuristic",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure whether PET router/pipeline suggested classic commands yield concrete factors."
    )
    parser.add_argument("numbers", nargs="+")
    args = parser.parse_args()

    columns = (
        "N",
        "monster_class",
        "recommended_strategy",
        "route_confidence",
        "route_kind",
        "route_trial_limit_hint",
        "triage_router_monster_class",
        "suggested_command",
        "command_status",
        "factor_found",
        "factor_value",
        "command_error",
        "suggested_verifier_command",
        "verifier_status",
        "verifier_factor_found",
        "usable_factor_count",
        "best_factor",
        "verifier_error",
        "claim",
    )

    print("\t".join(columns))
    for n_text in args.numbers:
        row = study_row(n_text)
        print("\t".join(row[column] for column in columns))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
