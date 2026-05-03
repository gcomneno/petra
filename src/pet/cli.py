from __future__ import annotations

import argparse
from functools import lru_cache
import ast
import json
import math
import heapq
import pathlib
import subprocess
import sys
import time
from collections import Counter, deque

from .atlas import atlas, draw_shape, extract_shape, print_atlas
from .algebra import distance, structural_distance
from .core import (
    decode,
    encode,
    is_prime,
    metrics_dict,
    minimal_shape_representative,
    prime_factorization,
    shape_generator,
    shape_generator_from_factorization,
    shape_signature_dict,
    validate,
)
from .io import load_json_file, render, to_json
from .metrics import extended_metrics
from .families import register_subparser as register_families_subparser, run_args as run_families
from .query import register_subparser as register_query_subparser, run_args as run_query
from .metrics import (
    is_expanding,
    is_level_uniform,
    is_linear,
    is_squarefree,
    leaf_ratio,
    profile_shape,
)




def _hide_subparser(subparsers, name: str) -> None:
    subparsers._choices_actions = [
        action for action in subparsers._choices_actions
        if getattr(action, "dest", None) != name
    ]


def _shape_to_jsonable(shape):
    if shape is None:
        return None
    return [_shape_to_jsonable(child) for child in shape]


def _jsonable_value(value):
    if isinstance(value, tuple):
        return [_jsonable_value(child) for child in value]
    if isinstance(value, list):
        return [_jsonable_value(child) for child in value]
    if isinstance(value, dict):
        return {key: _jsonable_value(val) for key, val in value.items()}
    return value


def _parse_partial_shape_arg(raw: str):
    try:
        value = ast.literal_eval(raw)
    except (SyntaxError, ValueError) as exc:
        raise ValueError(f"invalid partial shape literal: {raw}") from exc

    def _convert(obj):
        if obj is None:
            return None
        if isinstance(obj, tuple):
            return tuple(_convert(child) for child in obj)
        if isinstance(obj, list):
            return tuple(_convert(child) for child in obj)
        raise ValueError("partial shape must use only tuple/list nesting and None")

    return _convert(value)


def _format_factorization(factors):
    if not factors:
        return "1"

    parts = []
    for prime, exp in factors:
        if exp == 1:
            parts.append(str(prime))
        else:
            parts.append(f"{prime}^{exp}")
    return " * ".join(parts)


_OPAQUE_RESIDUAL_BACKBONE_LOOKUP_LIMIT = 10_000_000
_BACKBONE_PRIME_CACHE_KIND = "pet-backbone-prime-cache"


def _backbone_cache_dir() -> pathlib.Path:
    return pathlib.Path(".pet-cache")


def _backbone_cache_path(limit: int) -> pathlib.Path:
    return _backbone_cache_dir() / f"backbone-primes-up-to-{limit}.json"


def _generate_backbone_prime_tuple(limit: int) -> tuple[int, ...]:
    if limit < 2:
        return ()

    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"

    candidate = 2
    while candidate * candidate <= limit:
        if sieve[candidate]:
            start = candidate * candidate
            sieve[start : limit + 1 : candidate] = b"\x00" * (
                ((limit - start) // candidate) + 1
            )
        candidate += 1

    return tuple(candidate for candidate in range(2, limit + 1) if sieve[candidate])


def _read_backbone_prime_cache(limit: int) -> tuple[int, tuple[int, ...], pathlib.Path] | None:
    cache_dir = _backbone_cache_dir()
    if not cache_dir.exists():
        return None

    best: tuple[int, tuple[int, ...], pathlib.Path] | None = None

    for path in cache_dir.glob("backbone-primes-up-to-*.json"):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue

        if data.get("kind") != _BACKBONE_PRIME_CACHE_KIND:
            continue

        cache_limit = int(data.get("limit", -1))
        if cache_limit < limit:
            continue

        primes = tuple(int(prime) for prime in data.get("primes", []))
        if not primes and limit >= 2:
            continue

        if best is None or cache_limit < best[0]:
            best = (cache_limit, primes, path)

    if best is None:
        return None

    cache_limit, primes, path = best
    if cache_limit != limit:
        primes = tuple(prime for prime in primes if prime <= limit)

    return cache_limit, primes, path


def _write_backbone_prime_cache(limit: int, primes: tuple[int, ...]) -> pathlib.Path:
    cache_dir = _backbone_cache_dir()
    cache_dir.mkdir(exist_ok=True)

    path = _backbone_cache_path(limit)
    data = {
        "kind": _BACKBONE_PRIME_CACHE_KIND,
        "limit": limit,
        "prime_count": len(primes),
        "first_prime": primes[0] if primes else None,
        "last_prime": primes[-1] if primes else None,
        "primes": list(primes),
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return path


def _build_backbone_prime_cache(limit: int) -> dict:
    if limit < 2:
        raise ValueError("--limit must be >= 2")

    primes = _generate_backbone_prime_tuple(limit)
    path = _write_backbone_prime_cache(limit, primes)
    _backbone_prime_cache.cache_clear()

    return {
        "cache_path": str(path),
        "limit": limit,
        "prime_count": len(primes),
        "first_prime": primes[0] if primes else None,
        "last_prime": primes[-1] if primes else None,
    }


def _inspect_backbone_prime_cache(limit: int) -> dict:
    if limit < 2:
        raise ValueError("--limit must be >= 2")

    cached = _read_backbone_prime_cache(limit)
    if cached is None:
        return {
            "cache_exists": False,
            "requested_limit": limit,
            "cache_path": None,
            "cache_limit": None,
            "prime_count": 0,
            "first_prime": None,
            "last_prime": None,
        }

    cache_limit, primes, path = cached
    return {
        "cache_exists": True,
        "requested_limit": limit,
        "cache_path": str(path),
        "cache_limit": cache_limit,
        "prime_count": len(primes),
        "first_prime": primes[0] if primes else None,
        "last_prime": primes[-1] if primes else None,
    }


@lru_cache(maxsize=32)
def _backbone_prime_cache(limit: int) -> tuple[tuple[int, ...], frozenset[int]]:
    """Return PET backbone prime generators up to ``limit`` and a lookup set."""
    cached = _read_backbone_prime_cache(limit)
    if cached is not None:
        _, primes, _ = cached
    else:
        primes = _generate_backbone_prime_tuple(limit)

    return primes, frozenset(primes)


def _iter_backbone_prime_candidates(limit: int):
    """Yield prime candidates that extend the PET backbone up to ``limit``."""
    primes, _ = _backbone_prime_cache(limit)
    yield from primes


def _iter_backbone_prime_window_candidates(start: int, end: int):
    """Yield PET backbone prime generators in the inclusive window [start, end]."""
    if end < start or end < 2:
        return

    start = max(2, start)
    primes, _ = _backbone_prime_cache(end)

    for candidate in primes:
        if candidate < start:
            continue
        yield candidate


def _iter_scanned_prime_window_candidates(start: int, end: int):
    """Yield prime candidates by scanning only the inclusive window [start, end]."""
    if end < start or end < 2:
        return

    candidate = max(2, start)
    while candidate <= end:
        if is_prime(candidate):
            yield candidate
        candidate += 1


def _iter_prime_window_candidates(start: int, end: int, *, strategy: str):
    if strategy == "backbone":
        yield from _iter_backbone_prime_window_candidates(start, end)
    elif strategy == "scan":
        yield from _iter_scanned_prime_window_candidates(start, end)
    else:
        raise ValueError("unsupported prime window candidate strategy")


def _opaque_residual_status(residual: int, *, backbone_limit: int) -> str:
    if residual == 1:
        return "one"

    if residual <= _OPAQUE_RESIDUAL_BACKBONE_LOOKUP_LIMIT:
        lookup_limit = max(backbone_limit, residual)
    else:
        lookup_limit = backbone_limit

    if residual <= lookup_limit:
        _, prime_lookup = _backbone_prime_cache(lookup_limit)
        if residual in prime_lookup:
            return "probable_prime"

    return "composite_or_unknown"


def _trial_division_partial(n: int, *, trial_limit: int) -> dict:
    if n < 1:
        raise ValueError("opaque-probe expects integers >= 1")
    if trial_limit < 2:
        raise ValueError("--trial-limit must be >= 2")

    original = n
    residual = n
    known_factors: list[dict[str, int]] = []

    for candidate in _iter_backbone_prime_candidates(trial_limit):
        if residual == 1:
            break

        exponent = 0
        while residual % candidate == 0:
            residual //= candidate
            exponent += 1

        if exponent:
            known_factors.append({"prime": candidate, "exponent": exponent})

    residual_status = _opaque_residual_status(
        residual,
        backbone_limit=trial_limit,
    )

    return {
        "n": original,
        "digits": len(str(original)),
        "bit_length": original.bit_length(),
        "trial_limit": trial_limit,
        "known_factors": known_factors,
        "known_factorization": _format_factorization(
            [(row["prime"], row["exponent"]) for row in known_factors]
        ),
        "opaque_residual": residual,
        "opaque_residual_digits": len(str(residual)),
        "opaque_residual_bit_length": residual.bit_length(),
        "opaque_residual_status": residual_status,
        "fully_factored": residual == 1,
        "claim": "partial factor peeling only; this does not solve general factorization",
    }


_OPAQUE_RESUME_STATE_KIND = "pet-opaque-resume-state"


def _opaque_resume_peel(
    *,
    n: int,
    residual: int,
    known_factors: list[dict[str, int]],
    checked_until: int,
    trial_limit: int,
) -> dict:
    if n < 1:
        raise ValueError("opaque-resume expects integers >= 1")
    if trial_limit < 2:
        raise ValueError("--trial-limit must be >= 2")
    if trial_limit < checked_until:
        raise ValueError("--trial-limit must be >= checked_until")

    for candidate in _iter_backbone_prime_window_candidates(
        checked_until + 1,
        trial_limit,
    ):
        if residual == 1:
            break

        exponent = 0
        while residual % candidate == 0:
            residual //= candidate
            exponent += 1

        if exponent:
            known_factors.append({"prime": candidate, "exponent": exponent})

    residual_status = _opaque_residual_status(
        residual,
        backbone_limit=trial_limit,
    )

    return {
        "kind": _OPAQUE_RESUME_STATE_KIND,
        "n": n,
        "digits": len(str(n)),
        "bit_length": n.bit_length(),
        "checked_until": trial_limit,
        "known_factors": known_factors,
        "known_factorization": _format_factorization(
            [(row["prime"], row["exponent"]) for row in known_factors]
        ),
        "opaque_residual": residual,
        "opaque_residual_digits": len(str(residual)),
        "opaque_residual_bit_length": residual.bit_length(),
        "opaque_residual_status": residual_status,
        "fully_factored": residual == 1,
        "claim": "resumable bounded factor peeling only; this does not solve general factorization",
    }


def _write_opaque_resume_state(path: pathlib.Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def _read_opaque_resume_state(path: pathlib.Path) -> dict:
    data = json.loads(path.read_text())
    if data.get("kind") != _OPAQUE_RESUME_STATE_KIND:
        raise ValueError("invalid opaque-resume state file")
    return data


def _opaque_resume_start(n: int, *, trial_limit: int, state_path: pathlib.Path) -> dict:
    data = _opaque_resume_peel(
        n=n,
        residual=n,
        known_factors=[],
        checked_until=1,
        trial_limit=trial_limit,
    )
    _write_opaque_resume_state(state_path, data)
    return data


def _opaque_resume_continue(*, trial_limit: int, state_path: pathlib.Path) -> dict:
    state = _read_opaque_resume_state(state_path)
    data = _opaque_resume_peel(
        n=int(state["n"]),
        residual=int(state["opaque_residual"]),
        known_factors=[
            {"prime": int(row["prime"]), "exponent": int(row["exponent"])}
            for row in state["known_factors"]
        ],
        checked_until=int(state["checked_until"]),
        trial_limit=trial_limit,
    )
    _write_opaque_resume_state(state_path, data)
    return data


def _print_opaque_resume_state(data: dict) -> None:
    print(f"N = {data['n']}")
    print(f"digits = {data['digits']}")
    print(f"bit_length = {data['bit_length']}")
    print(f"checked_until = {data['checked_until']}")
    print(f"known_factorization = {data['known_factorization']}")
    print(f"opaque_residual = {data['opaque_residual']}")
    print(f"opaque_residual_digits = {data['opaque_residual_digits']}")
    print(f"opaque_residual_bit_length = {data['opaque_residual_bit_length']}")
    print(f"opaque_residual_status = {data['opaque_residual_status']}")
    print(f"fully_factored = {'yes' if data['fully_factored'] else 'no'}")
    print(f"claim = {data['claim']}")


def _print_opaque_summary(data: dict, *, include_window: bool = False) -> None:
    print(f"digits = {data['digits']}")
    print(f"bit_length = {data['bit_length']}")

    if "trial_limit" in data:
        print(f"trial_limit = {data['trial_limit']}")
    if "checked_until" in data:
        print(f"checked_until = {data['checked_until']}")
    if include_window:
        print(f"window_start = {data['window_start']}")
        print(f"window_end = {data['window_end']}")
        print(f"tested_prime_count = {data['tested_prime_count']}")

    print(f"known_factorization = {data['known_factorization']}")
    print(f"opaque_residual_digits = {data['opaque_residual_digits']}")
    print(f"opaque_residual_bit_length = {data['opaque_residual_bit_length']}")
    print(f"opaque_residual_status = {data['opaque_residual_status']}")
    print(f"fully_factored = {'yes' if data['fully_factored'] else 'no'}")
    print(f"claim = {data['claim']}")


def _opaque_benchmark_probe(n: int, *, trial_limit: int) -> dict:
    started = time.perf_counter()
    data = _trial_division_partial(n, trial_limit=trial_limit)
    elapsed = time.perf_counter() - started

    return {
        "mode": "probe",
        "elapsed_seconds": elapsed,
        "digits": data["digits"],
        "bit_length": data["bit_length"],
        "trial_limit": data["trial_limit"],
        "known_factorization": data["known_factorization"],
        "opaque_residual_digits": data["opaque_residual_digits"],
        "opaque_residual_bit_length": data["opaque_residual_bit_length"],
        "opaque_residual_status": data["opaque_residual_status"],
        "fully_factored": data["fully_factored"],
        "claim": "opaque benchmark only; this does not solve general factorization",
    }


def _opaque_benchmark_resume(*, trial_limit: int, state_path: pathlib.Path) -> dict:
    state = _read_opaque_resume_state(state_path)
    previous_checked_until = int(state["checked_until"])

    started = time.perf_counter()
    data = _opaque_resume_continue(
        trial_limit=trial_limit,
        state_path=state_path,
    )
    elapsed = time.perf_counter() - started

    return {
        "mode": "resume",
        "elapsed_seconds": elapsed,
        "previous_checked_until": previous_checked_until,
        "checked_until": data["checked_until"],
        "digits": data["digits"],
        "bit_length": data["bit_length"],
        "known_factorization": data["known_factorization"],
        "opaque_residual_digits": data["opaque_residual_digits"],
        "opaque_residual_bit_length": data["opaque_residual_bit_length"],
        "opaque_residual_status": data["opaque_residual_status"],
        "fully_factored": data["fully_factored"],
        "claim": "opaque benchmark only; this does not solve general factorization",
    }


def _print_opaque_benchmark(data: dict) -> None:
    print(f"mode = {data['mode']}")
    print(f"elapsed_seconds = {data['elapsed_seconds']:.6f}")
    print(f"digits = {data['digits']}")
    print(f"bit_length = {data['bit_length']}")
    if "trial_limit" in data:
        print(f"trial_limit = {data['trial_limit']}")
    if "previous_checked_until" in data:
        print(f"previous_checked_until = {data['previous_checked_until']}")
    if "checked_until" in data:
        print(f"checked_until = {data['checked_until']}")
    print(f"known_factorization = {data['known_factorization']}")
    print(f"opaque_residual_digits = {data['opaque_residual_digits']}")
    print(f"opaque_residual_bit_length = {data['opaque_residual_bit_length']}")
    print(f"opaque_residual_status = {data['opaque_residual_status']}")
    print(f"fully_factored = {'yes' if data['fully_factored'] else 'no'}")
    print(f"claim = {data['claim']}")


def _parse_trial_limits(raw: str) -> list[int]:
    limits: list[int] = []

    for chunk in raw.split(","):
        value = chunk.strip()
        if not value:
            continue

        limit = int(value)
        if limit < 2:
            raise ValueError("--limits values must be >= 2")

        limits.append(limit)

    if not limits:
        raise ValueError("--limits must contain at least one integer >= 2")

    return limits


def _opaque_profile(n: int, *, limits: list[int]) -> dict:
    if n < 1:
        raise ValueError("opaque-profile expects integers >= 1")

    checkpoint_limits = sorted(set(limits))
    max_limit = checkpoint_limits[-1]

    residual = n
    known_factors: list[dict[str, int]] = []
    rows_by_limit: dict[int, dict] = {}

    def make_row(limit: int) -> dict:
        residual_status = _opaque_residual_status(
            residual,
            backbone_limit=max_limit,
        )

        return {
            "trial_limit": limit,
            "known_count": len(known_factors),
            "opaque_residual_digits": len(str(residual)),
            "opaque_residual_bit_length": residual.bit_length(),
            "opaque_residual_status": residual_status,
            "fully_factored": residual == 1,
        }

    checkpoint_index = 0

    for candidate in _iter_backbone_prime_candidates(max_limit):
        while (
            checkpoint_index < len(checkpoint_limits)
            and candidate > checkpoint_limits[checkpoint_index]
        ):
            rows_by_limit[checkpoint_limits[checkpoint_index]] = make_row(
                checkpoint_limits[checkpoint_index]
            )
            checkpoint_index += 1

        if residual == 1:
            break

        exponent = 0
        while residual % candidate == 0:
            residual //= candidate
            exponent += 1

        if exponent:
            known_factors.append({"prime": candidate, "exponent": exponent})

    while checkpoint_index < len(checkpoint_limits):
        rows_by_limit[checkpoint_limits[checkpoint_index]] = make_row(
            checkpoint_limits[checkpoint_index]
        )
        checkpoint_index += 1

    rows = [rows_by_limit[limit] for limit in limits]

    return {
        "n": n,
        "digits": len(str(n)),
        "bit_length": n.bit_length(),
        "limits": limits,
        "rows": rows,
        "claim": "bounded opaque residual profiling only; this does not solve general factorization",
    }


def _opaque_window_plan(n: int, *, policy: str) -> dict:
    if n < 1:
        raise ValueError("opaque-window-plan expects integers >= 1")
    if policy != "balanced-semiprime":
        raise ValueError("unsupported opaque-window-plan policy")

    digits = len(str(n))
    low_digits = (digits + 1) // 2
    high_digits = low_digits + 1

    return {
        "n": n,
        "digits": digits,
        "bit_length": n.bit_length(),
        "policy": policy,
        "candidate_factor_digits": low_digits,
        "low_digits": low_digits,
        "high_digits": high_digits,
        "decimal_window_low_power": low_digits - 1,
        "decimal_window_high_power": low_digits,
        "decimal_window_low": f"10^{low_digits - 1}",
        "decimal_window_high": f"10^{low_digits}",
        "secondary_decimal_window_low": f"10^{low_digits - 1}",
        "secondary_decimal_window_high": f"10^{high_digits}",
        "claim": "structural candidate window only; this does not factor N",
    }


def _opaque_window_probe(
    n: int,
    *,
    start: int,
    end: int,
    candidate_strategy: str = "backbone",
) -> dict:
    if n < 1:
        raise ValueError("opaque-window-probe expects integers >= 1")
    if start < 2:
        raise ValueError("--start must be >= 2")
    if end < start:
        raise ValueError("--end must be >= --start")
    # Window is already resolved by the CLI layer.

    residual = n
    known_factors: list[dict[str, int]] = []
    tested_prime_count = 0

    for candidate in _iter_prime_window_candidates(
        start,
        end,
        strategy=candidate_strategy,
    ):
        tested_prime_count += 1

        if residual == 1:
            break

        exponent = 0
        while residual % candidate == 0:
            residual //= candidate
            exponent += 1

        if exponent:
            known_factors.append({"prime": candidate, "exponent": exponent})

    residual_status = _opaque_residual_status(
        residual,
        backbone_limit=end,
    )

    return {
        "n": n,
        "digits": len(str(n)),
        "bit_length": n.bit_length(),
        "window_start": start,
        "window_end": end,
        "candidate_strategy": candidate_strategy,
        "tested_prime_count": tested_prime_count,
        "known_factors": known_factors,
        "known_factorization": _format_factorization(
            [(row["prime"], row["exponent"]) for row in known_factors]
        ),
        "opaque_residual": residual,
        "opaque_residual_digits": len(str(residual)),
        "opaque_residual_bit_length": residual.bit_length(),
        "opaque_residual_status": residual_status,
        "fully_factored": residual == 1,
        "claim": "bounded backbone-window probing only; this does not solve general factorization",
    }


_OPAQUE_WINDOW_RESUME_STATE_KIND = "pet-opaque-window-resume-state"


def _opaque_window_resume_probe(
    *,
    n: int,
    residual: int,
    known_factors: list[dict[str, int]],
    checked_ranges: list[dict[str, int]],
    start: int,
    end: int,
) -> dict:
    if n < 1:
        raise ValueError("opaque-window-resume expects integers >= 1")
    if start < 2:
        raise ValueError("--start must be >= 2")
    if end < start:
        raise ValueError("--end must be >= --start")

    tested_prime_count = 0

    for candidate in _iter_backbone_prime_window_candidates(start, end):
        tested_prime_count += 1

        if residual == 1:
            break

        exponent = 0
        while residual % candidate == 0:
            residual //= candidate
            exponent += 1

        if exponent:
            known_factors.append({"prime": candidate, "exponent": exponent})

    checked_ranges = [
        *checked_ranges,
        {"kind": "window", "start": start, "end": end},
    ]

    residual_status = _opaque_residual_status(
        residual,
        backbone_limit=end,
    )

    return {
        "kind": _OPAQUE_WINDOW_RESUME_STATE_KIND,
        "n": n,
        "digits": len(str(n)),
        "bit_length": n.bit_length(),
        "window_start": start,
        "window_end": end,
        "tested_prime_count": tested_prime_count,
        "checked_ranges": checked_ranges,
        "known_factors": known_factors,
        "known_factorization": _format_factorization(
            [(row["prime"], row["exponent"]) for row in known_factors]
        ),
        "opaque_residual": residual,
        "opaque_residual_digits": len(str(residual)),
        "opaque_residual_bit_length": residual.bit_length(),
        "opaque_residual_status": residual_status,
        "fully_factored": residual == 1,
        "claim": "resumable bounded backbone-window probing only; this does not solve general factorization",
    }


def _write_opaque_window_resume_state(path: pathlib.Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def _read_opaque_window_resume_state(path: pathlib.Path) -> dict:
    data = json.loads(path.read_text())
    if data.get("kind") != _OPAQUE_WINDOW_RESUME_STATE_KIND:
        raise ValueError("invalid opaque-window-resume state file")
    return data


def _opaque_window_resume_start(
    n: int,
    *,
    start: int,
    end: int,
    state_path: pathlib.Path,
) -> dict:
    data = _opaque_window_resume_probe(
        n=n,
        residual=n,
        known_factors=[],
        checked_ranges=[],
        start=start,
        end=end,
    )
    _write_opaque_window_resume_state(state_path, data)
    return data


def _opaque_window_resume_continue(
    *,
    end: int,
    state_path: pathlib.Path,
) -> dict:
    state = _read_opaque_window_resume_state(state_path)
    previous_end = int(state["window_end"])
    start = previous_end + 1

    data = _opaque_window_resume_probe(
        n=int(state["n"]),
        residual=int(state["opaque_residual"]),
        known_factors=[
            {"prime": int(row["prime"]), "exponent": int(row["exponent"])}
            for row in state["known_factors"]
        ],
        checked_ranges=[
            {
                "kind": str(row["kind"]),
                "start": int(row["start"]),
                "end": int(row["end"]),
            }
            for row in state["checked_ranges"]
        ],
        start=start,
        end=end,
    )
    _write_opaque_window_resume_state(state_path, data)
    return data


def _print_opaque_window_resume_state(data: dict) -> None:
    print(f"N = {data['n']}")
    print(f"digits = {data['digits']}")
    print(f"bit_length = {data['bit_length']}")
    print(f"window_start = {data['window_start']}")
    print(f"window_end = {data['window_end']}")
    print(f"tested_prime_count = {data['tested_prime_count']}")
    print(f"checked_range_count = {len(data['checked_ranges'])}")
    print(f"known_factorization = {data['known_factorization']}")
    print(f"opaque_residual = {data['opaque_residual']}")
    print(f"opaque_residual_digits = {data['opaque_residual_digits']}")
    print(f"opaque_residual_bit_length = {data['opaque_residual_bit_length']}")
    print(f"opaque_residual_status = {data['opaque_residual_status']}")
    print(f"fully_factored = {'yes' if data['fully_factored'] else 'no'}")
    print(f"claim = {data['claim']}")


def _opaque_state_summary(path: pathlib.Path) -> dict:
    data = json.loads(path.read_text())
    kind = data.get("kind")

    if kind == _OPAQUE_RESUME_STATE_KIND:
        checked_ranges = [
            {
                "kind": "low-peel",
                "start": 2,
                "end": int(data["checked_until"]),
            }
        ]
    elif kind == _OPAQUE_WINDOW_RESUME_STATE_KIND:
        checked_ranges = [
            {
                "kind": str(row["kind"]),
                "start": int(row["start"]),
                "end": int(row["end"]),
            }
            for row in data["checked_ranges"]
        ]
    else:
        raise ValueError("unsupported opaque state file")

    return {
        "kind": kind,
        "state_path": str(path),
        "n": int(data["n"]),
        "digits": int(data["digits"]),
        "bit_length": int(data["bit_length"]),
        "known_factors": data["known_factors"],
        "known_factorization": data["known_factorization"],
        "opaque_residual": int(data["opaque_residual"]),
        "opaque_residual_digits": int(data["opaque_residual_digits"]),
        "opaque_residual_bit_length": int(data["opaque_residual_bit_length"]),
        "opaque_residual_status": data["opaque_residual_status"],
        "fully_factored": bool(data["fully_factored"]),
        "checked_ranges": checked_ranges,
        "checked_range_count": len(checked_ranges),
        "claim": "unified opaque state summary only; this does not solve general factorization",
    }


def _print_opaque_state_summary(data: dict) -> None:
    print(f"kind = {data['kind']}")
    print(f"state_path = {data['state_path']}")
    print(f"digits = {data['digits']}")
    print(f"bit_length = {data['bit_length']}")
    print(f"known_factorization = {data['known_factorization']}")
    print(f"opaque_residual_digits = {data['opaque_residual_digits']}")
    print(f"opaque_residual_bit_length = {data['opaque_residual_bit_length']}")
    print(f"opaque_residual_status = {data['opaque_residual_status']}")
    print(f"fully_factored = {'yes' if data['fully_factored'] else 'no'}")
    print(f"checked_range_count = {data['checked_range_count']}")
    for index, row in enumerate(data["checked_ranges"], start=1):
        print(
            f"checked_range_{index} = "
            f"{row['kind']}[{row['start']},{row['end']}]"
        )
    print(f"claim = {data['claim']}")


def _opaque_report(
    n: int,
    *,
    trial_limit: int | None,
    window_start: int | None,
    window_end: int | None,
) -> dict:
    if n < 1:
        raise ValueError("opaque-report expects integers >= 1")

    low_peel = None
    window_probe = None

    if trial_limit is not None:
        low_peel = _trial_division_partial(n, trial_limit=trial_limit)

    if window_start is not None or window_end is not None:
        if window_start is None or window_end is None:
            raise ValueError("--window-start and --window-end must be used together")
        window_probe = _opaque_window_probe(n, start=window_start, end=window_end)

    if low_peel is None and window_probe is None:
        raise ValueError("opaque-report needs --trial-limit and/or --window-start/--window-end")

    found_low = low_peel is not None and low_peel["known_factorization"] != "1"
    found_window = window_probe is not None and window_probe["known_factorization"] != "1"
    fully_low = low_peel is not None and low_peel["fully_factored"]
    fully_window = window_probe is not None and window_probe["fully_factored"]

    if fully_low or fully_window:
        verdict = "fully peeled under the selected bounded analysis"
    elif found_low or found_window:
        verdict = "partially peeled; an opaque residual remains"
    else:
        verdict = "no factors found under the selected bounded analysis"

    return {
        "n": n,
        "digits": len(str(n)),
        "bit_length": n.bit_length(),
        "low_peel": low_peel,
        "window_probe": window_probe,
        "verdict": verdict,
        "claim": "monkey-friendly bounded opaque report only; this does not solve general factorization",
    }


def _print_opaque_report(data: dict) -> None:
    print("PET OPAQUE REPORT")
    print()
    print("N")
    print(f"  digits = {data['digits']}")
    print(f"  bit_length = {data['bit_length']}")

    low = data["low_peel"]
    if low is not None:
        print()
        print("1) Low peel")
        print(f"  checked backbone primes up to = {low['trial_limit']}")
        print(f"  known PET part = {low['known_factorization']}")
        print(f"  opaque residual digits = {low['opaque_residual_digits']}")
        print(f"  opaque residual status = {low['opaque_residual_status']}")
        print(f"  fully factored = {'yes' if low['fully_factored'] else 'no'}")

    window = data["window_probe"]
    if window is not None:
        print()
        print("2) Window probe")
        print(f"  window = [{window['window_start']}, {window['window_end']}]")
        print(f"  tested prime candidates = {window['tested_prime_count']}")
        print(f"  window factors found = {window['known_factorization']}")
        print(f"  opaque residual digits = {window['opaque_residual_digits']}")
        print(f"  opaque residual status = {window['opaque_residual_status']}")
        print(f"  fully factored = {'yes' if window['fully_factored'] else 'no'}")

    print()
    print("Verdict")
    print(f"  {data['verdict']}")
    print()
    print(f"claim = {data['claim']}")


def _opaque_shape_families(
    n: int,
    *,
    max_generator_count: int,
    max_exponent: int,
    excluded_support_limit: int | None = None,
) -> dict:
    if n < 1:
        raise ValueError("opaque-shape-families expects integers >= 1")
    if max_generator_count < 1:
        raise ValueError("--max-generator-count expects integers >= 1")
    if max_exponent < 2:
        raise ValueError("--max-exponent expects integers >= 2")

    digits = len(str(n))
    bit_length = n.bit_length()
    mass_bits = bit_length

    balanced_families = [
        {
            "family": f"balanced-{k}-generator",
            "k": k,
            "mass_bits_per_generator": mass_bits / k,
            "digits_per_generator": digits / k,
        }
        for k in range(1, max_generator_count + 1)
    ]

    prime_power_families = [
        {
            "family": "prime-power-like",
            "exponent": exponent,
            "base_mass_bits": mass_bits / exponent,
            "base_digits": digits / exponent,
        }
        for exponent in range(2, max_exponent + 1)
    ]

    if excluded_support_limit is None:
        excluded_backbone_support = None
    else:
        if excluded_support_limit < 1:
            raise ValueError("--excluded-support-limit expects integers >= 1")
        excluded_backbone_support = excluded_support_limit

    return {
        "n": n,
        "digits": digits,
        "bit_length": bit_length,
        "mass_bits": mass_bits,
        "balanced_families": balanced_families,
        "prime_power_families": prime_power_families,
        "known_constraints": {
            "known_body": "1",
            "excluded_backbone_support": excluded_backbone_support,
            "low_visible_support": [],
        },
        "interpretation": [
            "The projection is compatible with many shape families.",
            "Current PET-visible body is empty.",
            "Any compatible shape must hide its support beyond the observed low backbone range, or belong to a family not visible under current PET lenses.",
        ],
        "claim": "PET shape-family constraints only; this does not factor N",
    }


def _print_opaque_shape_families(data: dict) -> None:
    print("PET OPAQUE SHAPE FAMILIES")
    print()
    print("Observed projection")
    print(f"  digits = {data['digits']}")
    print(f"  bit_length = {data['bit_length']}")
    print(f"  mass_bits = {data['mass_bits']}")

    print()
    print("Balanced generator families")
    print("  k | mass_bits_per_generator | digits_per_generator")
    for row in data["balanced_families"]:
        print(
            f"  {row['k']} | "
            f"{row['mass_bits_per_generator']:.2f}                  | "
            f"{row['digits_per_generator']:.2f}"
        )

    print()
    print("Prime-power-like families")
    print("  exponent | base_mass_bits | base_digits")
    for row in data["prime_power_families"]:
        print(
            f"  {row['exponent']}        | "
            f"{row['base_mass_bits']:.2f}         | "
            f"{row['base_digits']:.2f}"
        )

    constraints = data["known_constraints"]
    excluded = constraints["excluded_backbone_support"]
    if excluded is None:
        excluded_text = "unknown"
    else:
        excluded_text = f"<= {excluded}"

    low_visible = constraints["low_visible_support"]
    if low_visible:
        low_visible_text = ", ".join(str(item) for item in low_visible)
    else:
        low_visible_text = "none"

    print()
    print("Known PET constraints")
    print(f"  known_body = {constraints['known_body']}")
    print(f"  excluded_backbone_support = {excluded_text}")
    print(f"  low visible support = {low_visible_text}")

    if data.get("fork"):
        fork = data["peel_fork"]
        print()
        print("PET multi-threshold fork")
        if not fork or not fork["fork_available"]:
            reason = "unknown" if not fork else fork["reason"]
            print(f"  unavailable = {reason}")
        else:
            source = fork["source_band"]
            print(
                "  source_band = "
                f"{source['kind']} {source['move']} k[{source['k_range']}]"
            )
            print(f"  boundary = {source['boundary']}")
            print(f"  branch_count = {fork['branch_count']}")

            print()
            print("  Branches")
            for branch in fork["branches"]:
                retained = branch["retained_window"]
                side = branch["side_window"]
                print(f"    {branch['name']}")
                print(f"      move = {branch['move']}")
                print(f"      direction = {branch['direction']}")
                print(
                    "      retained_window = "
                    f"k[{retained['k_start']},{retained['k_end']}]"
                )
                print(
                    "      side_window = "
                    f"k[{side['k_start']},{side['k_end']}] "
                    f"({side['source_kind']} {side['source_move']})"
                )
                print(f"      side_role = {branch['side_role']}")
                print(f"      next_action = {branch['next_action']}")
                print(f"      reason = {branch['reason']}")

            print(f"  claim = {fork['claim']}")

    if data.get("fork_follow"):
        followup = data["peel_fork_followup"]
        print()
        print("PET fork follow-up lens")
        if not followup or not followup["available"]:
            reason = "unknown" if not followup else followup["reason"]
            print("  available = no")
            print(f"  reason = {reason}")
        else:
            source_window = followup["source_window"]
            retained_window = followup["retained_window"]
            print("  available = yes")
            print(f"  status = {followup['status']}")
            print(f"  requested_branch = {followup['requested_branch']}")
            print(f"  source_branch = {followup['source_branch']}")
            print(f"  source_move = {followup['source_move']}")
            print(f"  source_direction = {followup['source_direction']}")
            print(f"  source_role = {followup['source_role']}")
            print(
                "  retained_window = "
                f"k[{retained_window['k_start']},{retained_window['k_end']}]"
            )
            print(
                "  source_window = "
                f"k[{source_window['k_start']},{source_window['k_end']}]"
            )
            print(f"  target_edge_hint = {followup['target_edge_hint']}")
            print(f"  reduction_kind = {followup['reduction_kind']}")
            print(f"  recommended_next_lens = {followup['recommended_next_lens']}")
            print(f"  next_action = {followup['next_action']}")
            print(f"  reason = {followup['reason']}")
            print(f"  claim = {followup['claim']}")

    print()
    print("PET interpretation")
    for line in data["interpretation"]:
        print(f"  {line}")

    print()
    print(f"claim = {data['claim']}")


def _opaque_shape_opacity(margin_bits: float) -> str:
    if margin_bits >= 64:
        return "high"
    if margin_bits >= 16:
        return "medium"
    if margin_bits >= 0:
        return "low"
    return "pressured"


def _opaque_shape_rank(
    n: int,
    *,
    max_generator_count: int,
    excluded_support_limit: int,
) -> dict:
    if n < 1:
        raise ValueError("opaque-shape-rank expects integers >= 1")
    if max_generator_count < 1:
        raise ValueError("--max-generator-count expects integers >= 1")
    if excluded_support_limit < 1:
        raise ValueError("--excluded-support-limit expects integers >= 1")

    digits = len(str(n))
    bit_length = n.bit_length()
    mass_bits = bit_length
    excluded_support_bits = excluded_support_limit.bit_length()
    excluded_support_digits = len(str(excluded_support_limit))

    families = []
    for k in range(1, max_generator_count + 1):
        avg_generator_bits = mass_bits / k
        avg_generator_digits = digits / k
        margin_bits = avg_generator_bits - excluded_support_bits
        families.append(
            {
                "family": f"balanced-{k}-generator",
                "k": k,
                "avg_generator_bits": avg_generator_bits,
                "avg_generator_digits": avg_generator_digits,
                "excluded_support_bits": excluded_support_bits,
                "excluded_support_digits": excluded_support_digits,
                "margin_bits": margin_bits,
                "opacity": _opaque_shape_opacity(margin_bits),
            }
        )

    return {
        "n": n,
        "digits": digits,
        "bit_length": bit_length,
        "mass_bits": mass_bits,
        "excluded_support_limit": excluded_support_limit,
        "excluded_support_bits": excluded_support_bits,
        "excluded_support_digits": excluded_support_digits,
        "ranked_families": families,
        "interpretation": [
            "Families with average generator size far above the excluded low backbone remain more opaque.",
            "Families whose expected generators approach the excluded support range become less opaque.",
            "PET still does not identify the support; it ranks shape hypotheses only.",
        ],
        "claim": "PET shape-family ranking only; this does not factor N",
    }


def _print_opaque_shape_rank(data: dict) -> None:
    print("PET OPAQUE SHAPE RANK")
    print()
    print("Observed projection")
    print(f"  digits = {data['digits']}")
    print(f"  bit_length = {data['bit_length']}")
    print(f"  mass_bits = {data['mass_bits']}")
    print(f"  excluded_backbone_support = <= {data['excluded_support_limit']}")
    print(f"  excluded_support_bits = {data['excluded_support_bits']}")

    print()
    print("Ranked compatible families")
    print("  family                  | avg_bits | avg_digits | margin_bits | opacity")
    for row in data["ranked_families"]:
        print(
            f"  {row['family']:<23} | "
            f"{row['avg_generator_bits']:>8.2f} | "
            f"{row['avg_generator_digits']:>10.2f} | "
            f"{row['margin_bits']:>11.2f} | "
            f"{row['opacity']}"
        )

    print()
    print("PET interpretation")
    for line in data["interpretation"]:
        print(f"  {line}")

    print()
    print(f"claim = {data['claim']}")


def _opaque_mass_center_zone(margin_bits: float) -> str:
    if margin_bits < 0:
        return "pressured"
    if margin_bits < 16:
        return "boundary-informative"
    if margin_bits < 64:
        return "informative"
    return "deep-opaque"


def _opaque_mass_center_signal(margin_bits: float) -> str:
    if margin_bits < 0:
        return "critical"
    if margin_bits < 16:
        return "strong"
    if margin_bits < 64:
        return "medium"
    return "weak"


def _opaque_mass_center_information_weight(margin_bits: float) -> float:
    distance_from_boundary = abs(margin_bits)
    return 1.0 / (1.0 + distance_from_boundary)


def _opaque_mass_response_hotspot_kind(from_zone: str, to_zone: str) -> str:
    transition = (from_zone, to_zone)
    kinds = {
        ("deep-opaque", "informative"): "visibility-entry",
        ("informative", "deep-opaque"): "fog-return",
        ("informative", "boundary-informative"): "boundary-entry",
        ("boundary-informative", "informative"): "decompression",
        ("boundary-informative", "pressured"): "pressure-entry",
        ("pressured", "boundary-informative"): "recovery",
    }
    return kinds.get(transition, "zone-transition")


def _opaque_mass_response_focus_score(kind: str) -> int:
    scores = {
        "visibility-entry": 1,
        "fog-return": 1,
        "decompression": 2,
        "boundary-entry": 3,
        "recovery": 3,
        "pressure-entry": 4,
        "zone-transition": 1,
    }
    return scores[kind]


def _opaque_mass_response_signal(focus_score: int) -> str:
    if focus_score >= 4:
        return "critical"
    if focus_score >= 3:
        return "strong"
    if focus_score >= 2:
        return "medium"
    return "weak"


def _opaque_mass_response_bands(hotspots: list[dict]) -> list[dict]:
    bands = []
    current_rows: list[dict] = []

    def close_current() -> None:
        if not current_rows:
            return

        first = current_rows[0]
        last = current_rows[-1]
        trigger_spans = [
            int(row["minimal_trigger_span"])
            for row in current_rows
        ]
        closest = min(
            current_rows,
            key=lambda row: (
                int(row["minimal_trigger_span"]),
                int(row["k"]),
            ),
        )

        if closest["response"] == "NEW":
            boundary = f"{closest['k']}/{closest['new_k']}"
        elif closest["response"] == "DROP":
            boundary = f"{closest['k']}/{closest['drop_k']}"
        else:
            boundary = "multi"

        bands.append(
            {
                "kind": first["hotspot_kind"],
                "move": first["response"],
                "k_start": first["k"],
                "k_end": last["k"],
                "k_range": f"{first['k']}..{last['k']}",
                "band_width": last["k"] - first["k"] + 1,
                "min_trigger_span": min(trigger_spans),
                "max_trigger_span": max(trigger_spans),
                "span_range": (
                    f"{first['minimal_trigger_span']}.."
                    f"{last['minimal_trigger_span']}"
                ),
                "closest_k": closest["k"],
                "boundary": boundary,
                "focus_score": first["focus_score"],
                "signal": _opaque_mass_response_signal(first["focus_score"]),
            }
        )

        current_rows.clear()

    previous = None
    for row in hotspots:
        if previous is None:
            current_rows.append(row)
            previous = row
            continue

        same_band = (
            row["k"] == previous["k"] + 1
            and row["hotspot_kind"] == previous["hotspot_kind"]
            and row["response"] == previous["response"]
            and row["focus_score"] == previous["focus_score"]
        )

        if same_band:
            current_rows.append(row)
        else:
            close_current()
            current_rows.append(row)

        previous = row

    close_current()
    return bands


def _opaque_mass_centers(
    n: int,
    *,
    max_generator_count: int,
    excluded_support_limit: int,
) -> dict:
    if n < 1:
        raise ValueError("opaque-mass-centers expects integers >= 1")
    if max_generator_count < 1:
        raise ValueError("--max-generator-count expects integers >= 1")
    if excluded_support_limit < 1:
        raise ValueError("--excluded-support-limit expects integers >= 1")

    digits = len(str(n))
    bit_length = n.bit_length()
    mass_bits = bit_length
    excluded_support_bits = excluded_support_limit.bit_length()
    excluded_support_digits = len(str(excluded_support_limit))

    centers = []
    for k in range(1, max_generator_count + 1):
        center_bits = mass_bits / k
        center_digits = digits / k
        margin_bits = center_bits - excluded_support_bits
        centers.append(
            {
                "family": f"balanced-{k}-generator",
                "k": k,
                "center_bits": center_bits,
                "center_digits": center_digits,
                "excluded_support_bits": excluded_support_bits,
                "excluded_support_digits": excluded_support_digits,
                "margin_bits": margin_bits,
                "zone": _opaque_mass_center_zone(margin_bits),
                "signal": _opaque_mass_center_signal(margin_bits),
                "information_weight": _opaque_mass_center_information_weight(
                    margin_bits
                ),
            }
        )

    return {
        "n": n,
        "digits": digits,
        "bit_length": bit_length,
        "mass_bits": mass_bits,
        "excluded_support_limit": excluded_support_limit,
        "excluded_support_bits": excluded_support_bits,
        "excluded_support_digits": excluded_support_digits,
        "mass_centers": centers,
        "interpretation": [
            "Deep opaque centers are compatible but weakly discriminating.",
            "Boundary centers are informative because they sit near the excluded backbone.",
            "Pressured centers are critical because their average mass falls inside or below the excluded low-support range.",
            "PET does not identify the true support here; it marks which mass centers deserve attention.",
        ],
        "claim": "PET mass-center analysis only; this does not factor N",
    }


def _print_opaque_mass_centers(data: dict) -> None:
    print("PET OPAQUE MASS CENTERS")
    print()
    print("Observed projection")
    print(f"  digits = {data['digits']}")
    print(f"  bit_length = {data['bit_length']}")
    print(f"  mass_bits = {data['mass_bits']}")
    print(f"  excluded_backbone_support = <= {data['excluded_support_limit']}")
    print(f"  excluded_support_bits = {data['excluded_support_bits']}")

    print()
    print("Mass centers")
    print(
        "  family                  | center_bits | center_digits | "
        "margin_bits | zone                 | signal   | info_weight"
    )
    for row in data["mass_centers"]:
        print(
            f"  {row['family']:<23} | "
            f"{row['center_bits']:>11.2f} | "
            f"{row['center_digits']:>13.2f} | "
            f"{row['margin_bits']:>11.2f} | "
            f"{row['zone']:<20} | "
            f"{row['signal']:<8} | "
            f"{row['information_weight']:.4f}"
        )

    print()
    print("PET interpretation")
    for line in data["interpretation"]:
        print(f"  {line}")

    print()
    print(f"claim = {data['claim']}")


def _opaque_mass_response(
    n: int,
    *,
    max_generator_count: int,
    excluded_support_limit: int,
    max_move_span: int = 1,
    include_bands: bool = False,
) -> dict:
    if n < 1:
        raise ValueError("opaque-mass-response expects integers >= 1")
    if max_generator_count < 2:
        raise ValueError("--max-generator-count expects integers >= 2")
    if excluded_support_limit < 1:
        raise ValueError("--excluded-support-limit expects integers >= 1")
    if max_move_span < 1:
        raise ValueError("--max-move-span expects integers >= 1")

    digits = len(str(n))
    bit_length = n.bit_length()
    mass_bits = bit_length
    excluded_support_bits = excluded_support_limit.bit_length()
    excluded_support_digits = len(str(excluded_support_limit))

    def center_for(k: int) -> dict:
        center_bits = mass_bits / k
        center_digits = digits / k
        margin_bits = center_bits - excluded_support_bits
        return {
            "k": k,
            "center_bits": center_bits,
            "center_digits": center_digits,
            "margin_bits": margin_bits,
            "zone": _opaque_mass_center_zone(margin_bits),
        }

    hotspots = []
    for k in range(1, max_generator_count + 1):
        current = center_for(k)

        response_moves = []
        threshold_crossings = []
        hotspot_kinds = []
        focus_scores = []
        trigger_spans = []
        new_trigger = None
        drop_trigger = None

        for span in range(1, max_move_span + 1):
            new_k = k + span
            if new_k <= max_generator_count:
                new_center = center_for(new_k)
                if new_center["zone"] != current["zone"]:
                    kind = _opaque_mass_response_hotspot_kind(
                        current["zone"],
                        new_center["zone"],
                    )
                    new_trigger = {
                        "move": "NEW",
                        "span": span,
                        "target_k": new_k,
                        "target_zone": new_center["zone"],
                        "threshold_crossing": (
                            f"NEW({span}):"
                            f"{current['zone']}->{new_center['zone']}"
                        ),
                        "hotspot_kind": kind,
                        "focus_score": _opaque_mass_response_focus_score(kind),
                    }
                    break

        for span in range(1, max_move_span + 1):
            drop_k = k - span
            if drop_k >= 1:
                drop_center = center_for(drop_k)
                if drop_center["zone"] != current["zone"]:
                    kind = _opaque_mass_response_hotspot_kind(
                        current["zone"],
                        drop_center["zone"],
                    )
                    drop_trigger = {
                        "move": "DROP",
                        "span": span,
                        "target_k": drop_k,
                        "target_zone": drop_center["zone"],
                        "threshold_crossing": (
                            f"DROP({span}):"
                            f"{current['zone']}->{drop_center['zone']}"
                        ),
                        "hotspot_kind": kind,
                        "focus_score": _opaque_mass_response_focus_score(kind),
                    }
                    break

        for trigger in (new_trigger, drop_trigger):
            if trigger is None:
                continue
            response_moves.append(trigger["move"])
            threshold_crossings.append(trigger["threshold_crossing"])
            hotspot_kinds.append(trigger["hotspot_kind"])
            focus_scores.append(trigger["focus_score"])
            trigger_spans.append(trigger["span"])

        if not response_moves:
            continue

        focus_score = max(focus_scores)
        minimal_trigger_span = min(trigger_spans)

        hotspots.append(
            {
                "family": f"balanced-{k}-generator",
                "k": k,
                "center_bits": current["center_bits"],
                "center_digits": current["center_digits"],
                "margin_bits": current["margin_bits"],
                "zone": current["zone"],
                "new_k": None if new_trigger is None else new_trigger["target_k"],
                "new_zone": None
                if new_trigger is None
                else new_trigger["target_zone"],
                "new_trigger_span": None
                if new_trigger is None
                else new_trigger["span"],
                "drop_k": None
                if drop_trigger is None
                else drop_trigger["target_k"],
                "drop_zone": None
                if drop_trigger is None
                else drop_trigger["target_zone"],
                "drop_trigger_span": None
                if drop_trigger is None
                else drop_trigger["span"],
                "minimal_trigger_span": minimal_trigger_span,
                "response_moves": response_moves,
                "response": ",".join(response_moves),
                "threshold_crossings": threshold_crossings,
                "hotspot_kinds": hotspot_kinds,
                "hotspot_kind": hotspot_kinds[0]
                if len(hotspot_kinds) == 1
                else "multi-threshold",
                "focus_score": focus_score,
            }
        )

    magnetic_bands = _opaque_mass_response_bands(hotspots)

    return {
        "n": n,
        "digits": digits,
        "bit_length": bit_length,
        "mass_bits": mass_bits,
        "excluded_support_limit": excluded_support_limit,
        "excluded_support_bits": excluded_support_bits,
        "excluded_support_digits": excluded_support_digits,
        "max_generator_count": max_generator_count,
        "max_move_span": max_move_span,
        "include_bands": include_bands,
        "hotspots": hotspots,
        "hotspot_count": len(hotspots),
        "magnetic_bands": magnetic_bands,
        "magnetic_band_count": len(magnetic_bands),
        "interpretation": [
            "Hotspots are mass centers where symbolic PET NEW/DROP moves change the information zone.",
            "Move span is the symbolic stimulus strength applied to the support-count hypothesis.",
            "Minimal trigger span is the smallest NEW/DROP stimulus that crosses a representation-scale threshold.",
            "Magnetic bands group consecutive hotspots that share the same response kind and move.",
            "Focus score is a PET heuristic for prioritizing reactive frontiers, not a probability.",
            "PET still does not identify the true support; it marks reactive mass-center boundaries.",
        ],
        "claim": "PET mass-response analysis only; this does not factor N",
    }


def _print_opaque_mass_response(data: dict) -> None:
    print("PET OPAQUE MASS RESPONSE")
    print()
    print("Observed projection")
    print(f"  digits = {data['digits']}")
    print(f"  bit_length = {data['bit_length']}")
    print(f"  mass_bits = {data['mass_bits']}")
    print(f"  excluded_backbone_support = <= {data['excluded_support_limit']}")
    print(f"  excluded_support_bits = {data['excluded_support_bits']}")
    print(f"  max_generator_count = {data['max_generator_count']}")
    print(f"  max_move_span = {data['max_move_span']}")

    print()
    print("Response hotspots")
    if not data["hotspots"]:
        print("  none")
    else:
        print(
            "  k | center_bits | margin_bits | zone                 | "
            "response | min_span | kind             | focus | threshold"
        )
        for row in data["hotspots"]:
            thresholds = ";".join(row["threshold_crossings"])
            print(
                f"  {row['k']:>2} | "
                f"{row['center_bits']:>11.2f} | "
                f"{row['margin_bits']:>11.2f} | "
                f"{row['zone']:<20} | "
                f"{row['response']:<8} | "
                f"{row['minimal_trigger_span']:>8} | "
                f"{row['hotspot_kind']:<16} | "
                f"{row['focus_score']:>5} | "
                f"{thresholds}"
            )

    if data.get("include_bands"):
        print()
        print("Magnetic bands")
        if not data["magnetic_bands"]:
            print("  none")
        else:
            print(
                "  kind             | move     | k_range | span_range | "
                "boundary | focus | signal"
            )
            for band in data["magnetic_bands"]:
                print(
                    f"  {band['kind']:<16} | "
                    f"{band['move']:<8} | "
                    f"{band['k_range']:<7} | "
                    f"{band['span_range']:<10} | "
                    f"{band['boundary']:<8} | "
                    f"{band['focus_score']:>5} | "
                    f"{band['signal']}"
                )

    print()
    print("PET interpretation")
    for line in data["interpretation"]:
        print(f"  {line}")

    print()
    print(f"claim = {data['claim']}")


def _opaque_focused_peel_cut(selected_band: dict, local_hotspots: list[dict]) -> dict:
    if not local_hotspots:
        return {
            "cut_available": False,
            "reason": "selected band has no local hotspots",
            "layers": [],
        }

    ordered = sorted(local_hotspots, key=lambda row: int(row["k"]))
    closest_k = int(selected_band["closest_k"])
    boundary = str(selected_band["boundary"])
    move = str(selected_band["move"])
    kind = str(selected_band["kind"])

    layers = []
    for row in ordered:
        k = int(row["k"])
        trigger_span = int(row["minimal_trigger_span"])

        if k == closest_k:
            layer = "edge-layer"
        elif trigger_span == int(selected_band["max_trigger_span"]):
            layer = "outer-layer"
        else:
            layer = "middle-layer"

        layers.append(
            {
                "layer": layer,
                "k": k,
                "center_bits": row["center_bits"],
                "margin_bits": row["margin_bits"],
                "response": row["response"],
                "minimal_trigger_span": trigger_span,
                "hotspot_kind": row["hotspot_kind"],
                "threshold_crossings": row["threshold_crossings"],
            }
        )

    side_layers = []
    if "/" in boundary:
        left_text, right_text = boundary.split("/", maxsplit=1)
        try:
            left_k = int(left_text)
            right_k = int(right_text)
        except ValueError:
            left_k = None
            right_k = None

        if left_k is not None and right_k is not None:
            if kind == "pressure-entry" and move == "NEW":
                side_layers.append(
                    {
                        "side": "pressured-side",
                        "k_start": right_k,
                        "description": "symbolic NEW crosses from boundary-informative into pressured",
                    }
                )
            elif kind == "recovery" and move == "DROP":
                side_layers.append(
                    {
                        "side": "boundary-side",
                        "k_start": right_k,
                        "description": "symbolic DROP crosses from pressured back into boundary-informative",
                    }
                )
            elif kind == "boundary-entry" and move == "NEW":
                side_layers.append(
                    {
                        "side": "boundary-side",
                        "k_start": right_k,
                        "description": "symbolic NEW crosses from informative into boundary-informative",
                    }
                )
            elif kind == "decompression" and move == "DROP":
                side_layers.append(
                    {
                        "side": "informative-side",
                        "k_start": right_k,
                        "description": "symbolic DROP crosses from boundary-informative back into informative",
                    }
                )
            elif kind == "visibility-entry" and move == "NEW":
                side_layers.append(
                    {
                        "side": "informative-side",
                        "k_start": right_k,
                        "description": "symbolic NEW crosses from deep-opaque into informative",
                    }
                )
            elif kind == "fog-return" and move == "DROP":
                side_layers.append(
                    {
                        "side": "deep-opaque-side",
                        "k_start": right_k,
                        "description": "symbolic DROP crosses from informative back into deep-opaque",
                    }
                )

    return {
        "cut_available": True,
        "cut_kind": kind,
        "cut_move": move,
        "cut_window": f"k[{selected_band['k_start']},{selected_band['k_end']}]",
        "edge_k": closest_k,
        "boundary": boundary,
        "layer_count": len(layers),
        "layers": layers,
        "side_layers": side_layers,
        "interpretation": [
            "The cut separates the selected magnetic band into PET layers.",
            "The edge layer is the closest hotspot to the representation-scale boundary.",
            "Side layers describe the symbolic regime beyond the selected boundary.",
            "This cut is structural: it does not inspect value divisibility.",
        ],
    }


def _opaque_focused_peel_step(peel_cut: dict | None) -> dict:
    if not peel_cut or not peel_cut.get("cut_available"):
        return {
            "step_available": False,
            "reason": "focused peel cut is not available",
        }

    layers = peel_cut["layers"]
    if not layers:
        return {
            "step_available": False,
            "reason": "focused peel cut has no layers",
        }

    edge_layers = [
        layer for layer in layers
        if layer["layer"] == "edge-layer"
    ]
    if edge_layers:
        target = edge_layers[0]
        target_reason = "edge layer has the minimal trigger span at the selected boundary"
    else:
        target = min(
            layers,
            key=lambda layer: (
                int(layer["minimal_trigger_span"]),
                int(layer["k"]),
            ),
        )
        target_reason = "layer has the smallest available trigger span"

    side_layers = peel_cut.get("side_layers", [])
    if side_layers:
        next_side = side_layers[0]
        side_name = next_side["side"]
        side_start = next_side["k_start"]
    else:
        side_name = None
        side_start = None

    return {
        "step_available": True,
        "selected_action": "peel-edge",
        "target_layer": target["layer"],
        "target_k": target["k"],
        "target_boundary": peel_cut["boundary"],
        "target_kind": peel_cut["cut_kind"],
        "target_move": peel_cut["cut_move"],
        "target_minimal_trigger_span": target["minimal_trigger_span"],
        "target_center_bits": target["center_bits"],
        "target_margin_bits": target["margin_bits"],
        "target_threshold_crossings": target["threshold_crossings"],
        "next_side": side_name,
        "next_side_k_start": side_start,
        "target_reason": target_reason,
        "layer_decisions": [
            {
                "layer": layer["layer"],
                "k": layer["k"],
                "decision": (
                    "next-peel-target"
                    if layer["k"] == target["k"]
                    else "keep-as-ramp-context"
                ),
            }
            for layer in layers
        ],
        "interpretation": [
            "The peel step selects the next structural layer inside the focused cut.",
            "The selected layer is a PET-local target, not a value-level divisor.",
            "This advances from where to cut to which layer to peel next.",
        ],
    }


def _opaque_focused_peel_slice(
    *,
    selected_band: dict,
    peel_step_result: dict | None,
    max_generator_count: int,
) -> dict:
    if not peel_step_result or not peel_step_result.get("step_available"):
        return {
            "slice_available": False,
            "reason": "focused peel step is not available",
        }

    boundary = str(peel_step_result["target_boundary"])
    edge_k = int(peel_step_result["target_k"])
    next_side = peel_step_result["next_side"]
    next_side_k_start = peel_step_result["next_side_k_start"]
    kind = str(peel_step_result["target_kind"])
    move = str(peel_step_result["target_move"])

    if next_side is None or next_side_k_start is None:
        return {
            "slice_available": False,
            "reason": "focused peel step has no next side",
        }

    if kind == "pressure-entry" and move == "NEW":
        selected_name = "boundary-informative-side"
        separated_name = "pressured-side"
        selected_role = "retained-peel-side"
        separated_role = "separated-side"
        next_action = "inspect edge stability before pressured transition"
        reason = "symbolic NEW crosses from boundary-informative into pressured"
    elif kind == "boundary-entry" and move == "NEW":
        selected_name = "informative-side"
        separated_name = "boundary-informative-side"
        selected_role = "retained-context-side"
        separated_role = "selected-boundary-side"
        next_action = "inspect boundary entry stability"
        reason = "symbolic NEW crosses from informative into boundary-informative"
    elif kind == "recovery" and move == "DROP":
        selected_name = "pressured-side"
        separated_name = "boundary-informative-side"
        selected_role = "retained-recovery-side"
        separated_role = "recovered-side"
        next_action = "inspect recovery edge stability"
        reason = "symbolic DROP crosses from pressured back into boundary-informative"
    elif kind == "decompression" and move == "DROP":
        selected_name = "boundary-informative-side"
        separated_name = "informative-side"
        selected_role = "retained-boundary-side"
        separated_role = "decompressed-side"
        next_action = "inspect decompression edge stability"
        reason = "symbolic DROP crosses from boundary-informative back into informative"
    else:
        selected_name = f"{kind}-source-side"
        separated_name = str(next_side)
        selected_role = "retained-side"
        separated_role = "separated-side"
        next_action = "inspect edge stability"
        reason = f"symbolic {move} crosses the selected representation-scale boundary"

    selected_partition = {
        "name": selected_name,
        "k_start": int(selected_band["k_start"]),
        "k_end": edge_k,
        "k_range": f"{selected_band['k_start']}..{edge_k}",
        "role": selected_role,
    }

    separated_partition = {
        "name": separated_name,
        "k_start": int(next_side_k_start),
        "k_end": max_generator_count,
        "k_range": f"{next_side_k_start}..{max_generator_count}",
        "role": separated_role,
    }

    return {
        "slice_available": True,
        "slice_boundary": boundary,
        "edge_k": edge_k,
        "target_kind": kind,
        "target_move": move,
        "selected_partition": selected_partition,
        "separated_partition": separated_partition,
        "slice_decision": {
            "keep": "selected_partition",
            "separate": "separated_partition",
            "next_action": next_action,
            "reason": reason,
        },
        "interpretation": [
            "The slice partitions local PET shape-space across the selected representation-scale boundary.",
            "The retained side remains the local peel side; the separated side is structurally beyond the boundary.",
            "This is a structural PET slice, not a value-level operation.",
        ],
    }


def _opaque_focused_peel_lift(peel_slice: dict | None) -> dict:
    if not peel_slice or not peel_slice.get("slice_available"):
        return {
            "lift_available": False,
            "reason": "focused peel slice is not available",
        }

    selected = peel_slice["selected_partition"]
    separated = peel_slice["separated_partition"]
    decision = peel_slice["slice_decision"]

    selected_width = int(selected["k_end"]) - int(selected["k_start"]) + 1
    separated_width = int(separated["k_end"]) - int(separated["k_start"]) + 1

    if selected_width == 1:
        local_shape = "edge-point"
    elif selected_width <= 3:
        local_shape = "thin-ramp"
    else:
        local_shape = "ramp-band"

    if peel_slice["target_kind"] == "pressure-entry":
        emergent_form = "pre-pressure-edge"
    elif peel_slice["target_kind"] == "boundary-entry":
        emergent_form = "boundary-entry-ramp"
    elif peel_slice["target_kind"] == "recovery":
        emergent_form = "recovery-edge"
    elif peel_slice["target_kind"] == "decompression":
        emergent_form = "decompression-edge"
    else:
        emergent_form = "scale-transition-edge"

    lift_profile = {
        "selected_width": selected_width,
        "separated_width": separated_width,
        "local_shape": local_shape,
        "emergent_form": emergent_form,
        "edge_k": peel_slice["edge_k"],
        "slice_boundary": peel_slice["slice_boundary"],
        "retained_side": selected["name"],
        "separated_side": separated["name"],
        "next_action": decision["next_action"],
    }

    return {
        "lift_available": True,
        "lift_target": selected,
        "lifted_against": separated,
        "lift_profile": lift_profile,
        "visible_pet_form": {
            "form": emergent_form,
            "shape": local_shape,
            "edge_k": peel_slice["edge_k"],
            "boundary": peel_slice["slice_boundary"],
            "description": (
                f"{local_shape} on {selected['name']} ending at edge "
                f"k={peel_slice['edge_k']} before {separated['name']}"
            ),
        },
        "interpretation": [
            "The lift inspects the retained local shape-space partition after the slice.",
            "The visible PET form is a structural profile of the lifted side.",
            "This lift does not identify hidden support; it exposes the local PET shape of the cut.",
        ],
    }


def _opaque_projected_center_pet_form(n: int, edge_k: int) -> dict:
    if edge_k < 1:
        raise ValueError("projected center edge_k expects integers >= 1")

    center_estimate = n ** (1.0 / edge_k)
    nearest_integer = max(1, int(round(center_estimate)))
    nearest_tree = encode(nearest_integer)

    try:
        from tools.pet_shape_algebra import pet_to_shape

        pet_shape = pet_to_shape(nearest_tree)
    except Exception:
        pet_shape = None

    signature_data = shape_signature_dict(nearest_integer)

    return {
        "expression": f"N^(1/{edge_k})",
        "estimate": center_estimate,
        "nearest_integer": nearest_integer,
        "nearest_integer_digits": len(str(nearest_integer)),
        "nearest_integer_bits": nearest_integer.bit_length(),
        "pet_shape": None if pet_shape is None else _jsonable_value(pet_shape),
        "pet_shape_text": None if pet_shape is None else str(pet_shape),
        "pet_signature": signature_data["signature"],
        "pet_generator": signature_data["generator"],
        "pet_already_minimal": signature_data["already_minimal"],
        "pet_child_generators": signature_data["child_generators"],
        "center_role": "local edge projection",
    }



def _opaque_focused_peel_decode(n: int, peel_lift: dict | None) -> dict:
    if not peel_lift or not peel_lift.get("lift_available"):
        return {
            "decode_available": False,
            "reason": "focused peel lift is not available",
        }

    visible = peel_lift["visible_pet_form"]
    profile = peel_lift["lift_profile"]
    retained = peel_lift["lift_target"]
    separated = peel_lift["lifted_against"]

    edge_k = int(visible["edge_k"])
    support_region = {
        "name": retained["name"],
        "k_start": int(retained["k_start"]),
        "k_end": int(retained["k_end"]),
        "k_range": retained["k_range"],
    }
    separated_region = {
        "name": separated["name"],
        "k_start": int(separated["k_start"]),
        "k_end": int(separated["k_end"]),
        "k_range": separated["k_range"],
    }

    if visible["shape"] == "thin-ramp":
        recommended_next_lens = "preserve-edge-k"
        decode_strength = "sharp"
    elif visible["shape"] == "ramp-band":
        recommended_next_lens = "preserve-edge-k-and-rescan-local-band"
        decode_strength = "banded"
    elif visible["shape"] == "edge-point":
        recommended_next_lens = "preserve-single-edge"
        decode_strength = "point"
    else:
        recommended_next_lens = "preserve-visible-form"
        decode_strength = "generic"

    projected_center = _opaque_projected_center_pet_form(n, edge_k)

    decoded_constraints = {
        "support_count_region": support_region,
        "separated_region": separated_region,
        "local_edge_hypothesis": {
            "k": edge_k,
            "boundary": visible["boundary"],
            "form": visible["form"],
            "shape": visible["shape"],
        },
        "projected_center_pet_form": projected_center,
        "transition": (
            f"{profile['retained_side']} -> {profile['separated_side']}"
        ),
        "decode_strength": decode_strength,
        "recommended_next_lens": recommended_next_lens,
    }

    return {
        "decode_available": True,
        "input_form": visible["form"],
        "input_shape": visible["shape"],
        "edge_k": edge_k,
        "boundary": visible["boundary"],
        "decoded_constraints": decoded_constraints,
        "interpretation": [
            "The decode translates the lifted PET form into local structural constraints.",
            "The local edge hypothesis preserves the visible edge without inspecting value divisibility.",
            "The recommended next lens describes how to continue PET-local analysis.",
        ],
        "claim": "PET visible-form decode only; this does not factor N",
    }


def _opaque_focused_peel_center_lens(pet_decode: dict | None) -> dict:
    if not pet_decode or not pet_decode.get("decode_available"):
        return {
            "center_lens_available": False,
            "reason": "focused peel decode is not available",
        }

    constraints = pet_decode["decoded_constraints"]
    projected = constraints["projected_center_pet_form"]
    edge = constraints["local_edge_hypothesis"]

    edge_k = int(edge["k"])
    center_shape_text = projected["pet_shape_text"]
    center_signature = projected["pet_signature"]
    center_generator = int(projected["pet_generator"])

    if center_signature == [[], [], []]:
        lens_kind = "flat-three-leaf-center"
        next_focus = "edge stability with preserved flat three-leaf center"
    elif center_signature == [[], []]:
        lens_kind = "flat-two-leaf-center"
        next_focus = "edge stability with preserved flat two-leaf center"
    elif center_signature == [[]]:
        lens_kind = "single-leaf-center"
        next_focus = "edge stability with preserved single-leaf center"
    else:
        lens_kind = "projected-center-shape"
        next_focus = "edge stability with preserved projected center shape"

    suggested_start = max(1, edge_k - 2)
    suggested_end = edge_k

    return {
        "center_lens_available": True,
        "source": "projected_center_pet_form",
        "lens_kind": lens_kind,
        "edge_k": edge_k,
        "boundary": edge["boundary"],
        "preserve_edge_k": True,
        "preserve_center_shape": True,
        "center_nearest_integer": projected["nearest_integer"],
        "center_shape": center_shape_text,
        "center_signature": center_signature,
        "center_generator": center_generator,
        "center_child_generators": projected["pet_child_generators"],
        "center_bits": projected["nearest_integer_bits"],
        "center_digits": projected["nearest_integer_digits"],
        "suggested_window": {
            "k_start": suggested_start,
            "k_end": suggested_end,
            "k_range": f"{suggested_start}..{suggested_end}",
        },
        "next_focus": next_focus,
        "recommended_next_lens": (
            "rescan-suggested-window-preserving-edge-and-center-shape"
        ),
        "interpretation": [
            "The center lens uses the projected center PET form as a guide for the next local scan.",
            "It preserves the decoded edge and center shape instead of treating the center as a value-level factor.",
            "The suggested window is a PET-local refinement around the decoded edge.",
        ],
        "claim": "PET decoded-center lens only; this does not factor N",
    }



def _opaque_focused_peel_realization(pet_decode: dict | None) -> dict:
    if not pet_decode or not pet_decode.get("decode_available"):
        return {
            "realization_available": False,
            "reason": "focused peel decode is not available",
        }

    constraints = pet_decode["decoded_constraints"]
    projected = constraints["projected_center_pet_form"]
    edge = constraints["local_edge_hypothesis"]

    nearest_integer = int(projected["nearest_integer"])
    encoded_pet = encode(nearest_integer)
    decoded_back = decode(encoded_pet)
    roundtrip_ok = decoded_back == nearest_integer

    return {
        "realization_available": True,
        "source": "projected-center",
        "source_form": f"{pet_decode['input_form']}:{pet_decode['input_shape']}",
        "edge_k": edge["k"],
        "boundary": edge["boundary"],
        "nearest_integer": nearest_integer,
        "encode_decode": {
            "encoded_pet": _jsonable_value(encoded_pet),
            "decoded_back": decoded_back,
            "roundtrip_ok": roundtrip_ok,
        },
        "realized_shape": {
            "shape": projected["pet_shape"],
            "shape_text": projected["pet_shape_text"],
            "signature": projected["pet_signature"],
            "generator": projected["pet_generator"],
            "already_minimal": projected["pet_already_minimal"],
            "child_generators": projected["pet_child_generators"],
        },
        "role": "local edge projection realization",
        "interpretation": [
            "The realization payload materializes the projected center with the canonical PET encode/decode pipeline.",
            "The roundtrip check verifies that the projected center can re-enter the original PET world.",
            "This bridges focused peel decode to PET shape, signature, generator, and algebra tools.",
        ],
        "claim": "PET realization payload only; this does not factor N",
    }



def _opaque_focused_peel_classic_handoff(
    n: int,
    pet_realization: dict | None,
    *,
    radius: int,
) -> dict:
    if radius < 0:
        raise ValueError("--handoff-radius expects integers >= 0")

    if not pet_realization or not pet_realization.get("realization_available"):
        return {
            "handoff_available": False,
            "reason": "PET realization payload is not available",
        }

    edge_k = int(pet_realization["edge_k"])
    center = int(pet_realization["nearest_integer"])

    if edge_k == 1:
        scan_limit = int(n**0.5)
        candidates_checked = []
        divisor_found = None
        cofactor = None

        for candidate in range(2, scan_limit + 1):
            candidates_checked.append(candidate)
            if n % candidate == 0:
                divisor_found = candidate
                cofactor = n // candidate
                break

        verified = (
            divisor_found is not None
            and cofactor is not None
            and divisor_found * cofactor == n
        )

        return {
            "handoff_available": True,
            "source": "PET realization payload",
            "method": "classic-small-n-trial-division",
            "recommended": True,
            "reason": (
                "edge_k=1 center is N itself; using classic bounded "
                "trial division fallback"
            ),
            "edge_k": edge_k,
            "center": center,
            "radius": radius,
            "scan_limit": scan_limit,
            "candidates_checked": candidates_checked,
            "divisor_found": divisor_found,
            "cofactor": cofactor,
            "verified": verified,
            "claim": (
                "PET-guided classic handoff only; classic small-N fallback "
                "performed"
            ),
        }

    if edge_k != 2:
        return {
            "handoff_available": True,
            "source": "PET realization payload",
            "method": "local-divisibility-scan",
            "recommended": False,
            "reason": "direct divisor handoff is only recommended for edge_k=1 or edge_k=2",
            "edge_k": edge_k,
            "center": center,
            "radius": radius,
            "candidates_checked": [],
            "divisor_found": None,
            "cofactor": None,
            "verified": False,
            "claim": "PET-guided classic handoff only; skipped direct divisor search",
        }

    start = max(2, center - radius)
    end = max(start, center + radius)

    candidates_checked = []
    divisor_found = None
    cofactor = None

    for candidate in range(start, end + 1):
        candidates_checked.append(candidate)
        if candidate > 1 and n % candidate == 0:
            divisor_found = candidate
            cofactor = n // candidate
            break

    verified = (
        divisor_found is not None
        and cofactor is not None
        and divisor_found * cofactor == n
    )

    return {
        "handoff_available": True,
        "source": "PET realization payload",
        "method": "local-divisibility-scan",
        "recommended": True,
        "reason": "edge_k=2 supports local divisor scan around realized center",
        "edge_k": edge_k,
        "center": center,
        "radius": radius,
        "scan_start": start,
        "scan_end": end,
        "candidates_checked": candidates_checked,
        "divisor_found": divisor_found,
        "cofactor": cofactor,
        "verified": verified,
        "claim": "PET-guided classic handoff only; classic divisibility check performed",
    }



def _opaque_focused_peel_multi_fork(peel_cut: dict | None, response_data: dict) -> dict:
    if not peel_cut or not peel_cut.get("cut_available"):
        return {
            "fork_available": False,
            "reason": "focused peel cut is not available",
        }

    if peel_cut["cut_move"] != "NEW,DROP":
        return {
            "fork_available": False,
            "reason": "focused peel band is not multi-threshold",
        }

    cut_window_text = peel_cut["cut_window"]
    k_start_text, k_end_text = (
        cut_window_text.removeprefix("k[")
        .removesuffix("]")
        .split(",", 1)
    )
    k_start = int(k_start_text)
    k_end = int(k_end_text)
    max_k = int(response_data["max_generator_count"])

    lower_bands = [
        band
        for band in response_data["magnetic_bands"]
        if int(band["k_end"]) < k_start
    ]
    upper_bands = [
        band
        for band in response_data["magnetic_bands"]
        if int(band["k_start"]) > k_end
    ]

    lower_band = lower_bands[-1] if lower_bands else None
    upper_band = upper_bands[0] if upper_bands else None

    drop_side_window = (
        {
            "k_start": int(lower_band["k_start"]),
            "k_end": int(lower_band["k_end"]),
            "k_range": lower_band["k_range"],
            "source_kind": lower_band["kind"],
            "source_move": lower_band["move"],
        }
        if lower_band
        else {
            "k_start": 1,
            "k_end": max(1, k_start - 1),
            "k_range": f"1..{max(1, k_start - 1)}",
            "source_kind": "implicit-lower-side",
            "source_move": "DROP",
        }
    )

    new_side_window = (
        {
            "k_start": int(upper_band["k_start"]),
            "k_end": int(upper_band["k_end"]),
            "k_range": upper_band["k_range"],
            "source_kind": upper_band["kind"],
            "source_move": upper_band["move"],
        }
        if upper_band
        else {
            "k_start": min(max_k, k_end + 1),
            "k_end": max_k,
            "k_range": f"{min(max_k, k_end + 1)}..{max_k}",
            "source_kind": "implicit-upper-side",
            "source_move": "NEW",
        }
    )

    retained_window = {
        "k_start": k_start,
        "k_end": k_end,
        "k_range": f"{k_start}..{k_end}",
        "kind": peel_cut["cut_kind"],
        "move": peel_cut["cut_move"],
        "boundary": peel_cut["boundary"],
    }

    branches = [
        {
            "name": "NEW-side",
            "move": "NEW",
            "direction": "upward",
            "retained_window": retained_window,
            "side_window": new_side_window,
            "side_role": "pressured-side",
            "next_action": "inspect pressured-side recovery edge",
            "reason": "NEW threshold exits the multi band toward higher-k pressure",
        },
        {
            "name": "DROP-side",
            "move": "DROP",
            "direction": "downward",
            "retained_window": retained_window,
            "side_window": drop_side_window,
            "side_role": "informative-side",
            "next_action": "inspect informative-side boundary edge",
            "reason": "DROP threshold exits the multi band toward lower-k decompression",
        },
    ]

    return {
        "fork_available": True,
        "source_band": retained_window,
        "branch_count": len(branches),
        "branches": branches,
        "interpretation": [
            "The multi-threshold fork opens a NEW,DROP band into two explicit structural branches.",
            "The NEW-side follows the higher-k pressure transition.",
            "The DROP-side follows the lower-k decompression transition.",
            "This fork does not factor N; it separates ambiguous PET peel directions.",
        ],
        "claim": "PET multi-threshold fork only; this does not factor N",
    }



def _opaque_focused_peel_fork_followup(
    peel_fork: dict | None,
    fork_follow: str | None,
) -> dict | None:
    if fork_follow is None:
        return None

    claim = "PET fork follow-up lens only; this does not factor N"

    if not peel_fork or not peel_fork.get("fork_available"):
        return {
            "available": False,
            "reason": "multi-threshold fork is not available",
            "requested_branch": fork_follow,
            "claim": claim,
        }

    branch_name = f"{fork_follow}-side"
    branch = next(
        (
            branch
            for branch in peel_fork["branches"]
            if branch["name"] == branch_name
        ),
        None,
    )

    if branch is None:
        return {
            "available": False,
            "reason": f"branch {branch_name} is not available",
            "requested_branch": fork_follow,
            "claim": claim,
        }

    side_window = branch["side_window"]
    k_start = int(side_window["k_start"])
    k_end = int(side_window["k_end"])
    target_edge_hint = 2 if k_start <= 2 <= k_end else k_start

    return {
        "available": True,
        "status": "proposal",
        "requested_branch": fork_follow,
        "source_branch": branch["name"],
        "source_move": branch["move"],
        "source_direction": branch["direction"],
        "source_role": branch["side_role"],
        "source_window": side_window,
        "retained_window": branch["retained_window"],
        "target_edge_hint": target_edge_hint,
        "reduction_kind": "branch-window-collapse",
        "recommended_next_lens": "rescan-branch-window",
        "next_action": branch["next_action"],
        "reason": branch["reason"],
        "claim": claim,
    }


def _opaque_focused_peel(
    n: int,
    *,
    max_generator_count: int,
    excluded_support_limit: int,
    max_move_span: int,
    kind: str | None = None,
    move: str | None = None,
    cut: bool = False,
    peel_step: bool = False,
    slice_: bool = False,
    lift: bool = False,
    decode: bool = False,
    center_lens: bool = False,
    realize: bool = False,
    classic_handoff: bool = False,
    handoff_radius: int = 5,
    fork: bool = False,
    fork_follow: str | None = None,
) -> dict:
    if n < 1:
        raise ValueError("opaque-focused-peel expects integers >= 1")
    if max_generator_count < 2:
        raise ValueError("--max-generator-count expects integers >= 2")
    if excluded_support_limit < 1:
        raise ValueError("--excluded-support-limit expects integers >= 1")
    if max_move_span < 1:
        raise ValueError("--max-move-span expects integers >= 1")
    if handoff_radius < 0:
        raise ValueError("--handoff-radius expects integers >= 0")

    if classic_handoff:
        realize = True
    if fork:
        cut = True
        peel_step = True
    if realize:
        center_lens = True
    if center_lens:
        decode = True
    if decode:
        lift = True
    if lift:
        slice_ = True
    if slice_:
        cut = True
        peel_step = True

    requested_move = None if move is None else move.upper()

    response = _opaque_mass_response(
        n,
        max_generator_count=max_generator_count,
        excluded_support_limit=excluded_support_limit,
        max_move_span=max_move_span,
        include_bands=True,
    )

    bands = response["magnetic_bands"]
    if kind is not None:
        bands = [band for band in bands if band["kind"] == kind]
    if requested_move is not None:
        bands = [band for band in bands if band["move"] == requested_move]

    if not bands:
        raise ValueError("opaque-focused-peel found no matching magnetic bands")

    selected = sorted(
        bands,
        key=lambda band: (
            -int(band["focus_score"]),
            int(band["min_trigger_span"]),
            -int(band["band_width"]),
            int(band["k_start"]),
        ),
    )[0]

    local_hotspots = [
        row
        for row in response["hotspots"]
        if selected["k_start"] <= row["k"] <= selected["k_end"]
        and row["hotspot_kind"] == selected["kind"]
        and row["response"] == selected["move"]
    ]

    peel_lens = {
        "kind": selected["kind"],
        "move": selected["move"],
        "signal": selected["signal"],
        "focus_score": selected["focus_score"],
        "k_start": selected["k_start"],
        "k_end": selected["k_end"],
        "k_range": selected["k_range"],
        "band_width": selected["band_width"],
        "closest_k": selected["closest_k"],
        "boundary": selected["boundary"],
        "min_trigger_span": selected["min_trigger_span"],
        "max_trigger_span": selected["max_trigger_span"],
        "span_range": selected["span_range"],
        "local_hotspot_count": len(local_hotspots),
        "local_hotspots": local_hotspots,
    }

    peel_cut = _opaque_focused_peel_cut(selected, local_hotspots) if cut else None
    peel_step_result = _opaque_focused_peel_step(peel_cut) if peel_step else None
    peel_slice = (
        _opaque_focused_peel_slice(
            selected_band=selected,
            peel_step_result=peel_step_result,
            max_generator_count=max_generator_count,
        )
        if slice_
        else None
    )
    peel_lift = _opaque_focused_peel_lift(peel_slice) if lift else None
    pet_decode = _opaque_focused_peel_decode(n, peel_lift) if decode else None
    decoded_center_lens = (
        _opaque_focused_peel_center_lens(pet_decode)
        if center_lens
        else None
    )
    pet_realization = (
        _opaque_focused_peel_realization(pet_decode)
        if realize
        else None
    )
    pet_classic_handoff = (
        _opaque_focused_peel_classic_handoff(
            n,
            pet_realization,
            radius=handoff_radius,
        )
        if classic_handoff
        else None
    )
    effective_fork = fork or fork_follow is not None
    if effective_fork and peel_cut is None:
        peel_cut = _opaque_focused_peel_cut(selected, local_hotspots)

    peel_fork = (
        _opaque_focused_peel_multi_fork(peel_cut, response)
        if effective_fork
        else None
    )
    peel_fork_followup = _opaque_focused_peel_fork_followup(
        peel_fork,
        fork_follow,
    )

    return {
        "n": n,
        "digits": response["digits"],
        "bit_length": response["bit_length"],
        "mass_bits": response["mass_bits"],
        "excluded_support_limit": excluded_support_limit,
        "excluded_support_bits": response["excluded_support_bits"],
        "max_generator_count": max_generator_count,
        "max_move_span": max_move_span,
        "requested_kind": kind,
        "requested_move": requested_move,
        "cut": cut,
        "peel_step": peel_step,
        "slice": slice_,
        "lift": lift,
        "decode": decode,
        "center_lens": center_lens,
        "realize": realize,
        "classic_handoff": classic_handoff,
        "handoff_radius": handoff_radius,
        "fork": effective_fork,
        "fork_follow": fork_follow,
        "selected_band": selected,
        "peel_lens": peel_lens,
        "peel_cut": peel_cut,
        "peel_step_result": peel_step_result,
        "peel_slice": peel_slice,
        "peel_lift": peel_lift,
        "pet_decode": pet_decode,
        "decoded_center_lens": decoded_center_lens,
        "pet_realization": pet_realization,
        "pet_classic_handoff": pet_classic_handoff,
        "peel_fork": peel_fork,
        "peel_fork_followup": peel_fork_followup,
        "interpretation": [
            "The focused peel lens is selected from magnetic bands, not from raw value probing.",
            "The selected band is the highest-focus matching reactive frontier under the current PET lens.",
            "When enabled, the cut separates the focused band into local PET layers.",
            "When enabled, the peel step selects the next structural layer to lift.",
            "When enabled, the slice partitions local PET shape-space across the selected boundary.",
            "When enabled, the lift exposes the visible PET form of the retained partition.",
            "When enabled, the decode translates the visible PET form into local structural constraints.",
            "When enabled, the center lens builds the next PET-local lens from the projected center shape.",
            "When enabled, the realization payload bridges the projected center back to PET encode/decode.",
            "When enabled, the classic handoff uses the realized center as an explicit external divisibility anchor.",
            "When enabled, the fork opens multi-threshold bands into explicit NEW/DROP branches.",
            "This is a local PET peeling target: it identifies where to focus next, not what the hidden support is.",
        ],
        "claim": "PET focused peel lens only; this does not factor N",
    }


def _print_opaque_focused_peel(data: dict) -> None:
    print("PET OPAQUE FOCUSED PEEL")
    print()
    print("Observed projection")
    print(f"  digits = {data['digits']}")
    print(f"  bit_length = {data['bit_length']}")
    print(f"  mass_bits = {data['mass_bits']}")
    print(f"  excluded_backbone_support = <= {data['excluded_support_limit']}")
    print(f"  excluded_support_bits = {data['excluded_support_bits']}")
    print(f"  max_generator_count = {data['max_generator_count']}")
    print(f"  max_move_span = {data['max_move_span']}")

    band = data["selected_band"]
    print()
    print("Selected magnetic band")
    print(f"  kind = {band['kind']}")
    print(f"  move = {band['move']}")
    print(f"  k_range = {band['k_range']}")
    print(f"  boundary = {band['boundary']}")
    print(f"  span_range = {band['span_range']}")
    print(f"  focus_score = {band['focus_score']}")
    print(f"  signal = {band['signal']}")

    lens = data["peel_lens"]
    print()
    print("Peel lens")
    print(f"  peel_window = k[{lens['k_start']},{lens['k_end']}]")
    print(f"  closest_k = {lens['closest_k']}")
    print(f"  boundary = {lens['boundary']}")
    print(f"  minimal_trigger_span = {lens['min_trigger_span']}")
    print(f"  local_hotspot_count = {lens['local_hotspot_count']}")

    print()
    print("Local hotspots")
    for row in lens["local_hotspots"]:
        thresholds = ";".join(row["threshold_crossings"])
        print(
            f"  k={row['k']} "
            f"center_bits={row['center_bits']:.2f} "
            f"margin_bits={row['margin_bits']:.2f} "
            f"response={row['response']} "
            f"min_span={row['minimal_trigger_span']} "
            f"kind={row['hotspot_kind']} "
            f"threshold={thresholds}"
        )

    if data.get("cut"):
        cut = data["peel_cut"]
        print()
        print("Focused peel cut")
        if not cut or not cut["cut_available"]:
            reason = "unknown" if not cut else cut["reason"]
            print(f"  unavailable = {reason}")
        else:
            print(f"  cut_window = {cut['cut_window']}")
            print(f"  edge_k = {cut['edge_k']}")
            print(f"  boundary = {cut['boundary']}")
            print(f"  cut_kind = {cut['cut_kind']}")
            print(f"  cut_move = {cut['cut_move']}")
            print()
            print("  Layers")
            for layer in cut["layers"]:
                print(
                    f"    {layer['layer']}: "
                    f"k={layer['k']} "
                    f"center_bits={layer['center_bits']:.2f} "
                    f"margin_bits={layer['margin_bits']:.2f} "
                    f"min_span={layer['minimal_trigger_span']}"
                )

            if cut["side_layers"]:
                print()
                print("  Side layers")
                for side in cut["side_layers"]:
                    print(
                        f"    {side['side']}: "
                        f"k_start={side['k_start']} "
                        f"{side['description']}"
                    )

    if data.get("peel_step"):
        step = data["peel_step_result"]
        print()
        print("Focused peel step")
        if not step or not step["step_available"]:
            reason = "unknown" if not step else step["reason"]
            print(f"  unavailable = {reason}")
        else:
            print(f"  selected_action = {step['selected_action']}")
            print(f"  target_layer = {step['target_layer']}")
            print(f"  target_k = {step['target_k']}")
            print(f"  target_boundary = {step['target_boundary']}")
            print(f"  target_kind = {step['target_kind']}")
            print(f"  target_move = {step['target_move']}")
            print(
                "  target_minimal_trigger_span = "
                f"{step['target_minimal_trigger_span']}"
            )
            print(f"  next_side = {step['next_side']}")
            print(f"  next_side_k_start = {step['next_side_k_start']}")
            print(f"  target_reason = {step['target_reason']}")

            print()
            print("  Layer decisions")
            for decision in step["layer_decisions"]:
                print(
                    f"    {decision['layer']}: "
                    f"k={decision['k']} "
                    f"{decision['decision']}"
                )

    if data.get("slice"):
        slice_data = data["peel_slice"]
        print()
        print("Focused peel slice")
        if not slice_data or not slice_data["slice_available"]:
            reason = "unknown" if not slice_data else slice_data["reason"]
            print(f"  unavailable = {reason}")
        else:
            print(f"  slice_boundary = {slice_data['slice_boundary']}")
            print(f"  edge_k = {slice_data['edge_k']}")
            print(f"  target_kind = {slice_data['target_kind']}")
            print(f"  target_move = {slice_data['target_move']}")

            selected_partition = slice_data["selected_partition"]
            separated_partition = slice_data["separated_partition"]
            print()
            print("  Selected partition")
            print(f"    name = {selected_partition['name']}")
            print(f"    k_range = {selected_partition['k_range']}")
            print(f"    role = {selected_partition['role']}")
            print()
            print("  Separated partition")
            print(f"    name = {separated_partition['name']}")
            print(f"    k_range = {separated_partition['k_range']}")
            print(f"    role = {separated_partition['role']}")

            decision = slice_data["slice_decision"]
            print()
            print("  Slice decision")
            print(f"    keep = {decision['keep']}")
            print(f"    separate = {decision['separate']}")
            print(f"    next_action = {decision['next_action']}")
            print(f"    reason = {decision['reason']}")

    if data.get("lift"):
        lift_data = data["peel_lift"]
        print()
        print("Focused peel lift")
        if not lift_data or not lift_data["lift_available"]:
            reason = "unknown" if not lift_data else lift_data["reason"]
            print(f"  unavailable = {reason}")
        else:
            profile = lift_data["lift_profile"]
            visible = lift_data["visible_pet_form"]
            print(f"  lift_target = {lift_data['lift_target']['name']}")
            print(f"  lifted_against = {lift_data['lifted_against']['name']}")
            print(f"  selected_width = {profile['selected_width']}")
            print(f"  separated_width = {profile['separated_width']}")
            print(f"  local_shape = {profile['local_shape']}")
            print(f"  emergent_form = {profile['emergent_form']}")
            print(f"  edge_k = {profile['edge_k']}")
            print(f"  slice_boundary = {profile['slice_boundary']}")
            print()
            print("  Visible PET form")
            print(f"    form = {visible['form']}")
            print(f"    shape = {visible['shape']}")
            print(f"    boundary = {visible['boundary']}")
            print(f"    description = {visible['description']}")

    if data.get("decode"):
        decode_data = data["pet_decode"]
        print()
        print("PET visible-form decode")
        if not decode_data or not decode_data["decode_available"]:
            reason = "unknown" if not decode_data else decode_data["reason"]
            print(f"  unavailable = {reason}")
        else:
            constraints = decode_data["decoded_constraints"]
            support = constraints["support_count_region"]
            separated = constraints["separated_region"]
            edge = constraints["local_edge_hypothesis"]
            print(f"  input_form = {decode_data['input_form']}")
            print(f"  input_shape = {decode_data['input_shape']}")
            print(f"  edge_k = {decode_data['edge_k']}")
            print(f"  boundary = {decode_data['boundary']}")

            print()
            print("  Decoded constraints")
            print(f"    support_count_region = k[{support['k_start']},{support['k_end']}]")
            print(f"    separated_region = k[{separated['k_start']},{separated['k_end']}]")
            print(f"    local_edge_hypothesis = k={edge['k']}")
            print(f"    transition = {constraints['transition']}")
            print(f"    decode_strength = {constraints['decode_strength']}")
            print(
                "    recommended_next_lens = "
                f"{constraints['recommended_next_lens']}"
            )

            projected = constraints["projected_center_pet_form"]
            print()
            print("  Projected center PET form")
            print(f"    expression = {projected['expression']}")
            print(f"    estimate = {projected['estimate']:.12f}")
            print(f"    nearest_integer = {projected['nearest_integer']}")
            print(
                "    nearest_integer_digits = "
                f"{projected['nearest_integer_digits']}"
            )
            print(
                "    nearest_integer_bits = "
                f"{projected['nearest_integer_bits']}"
            )
            print(f"    pet_shape = {projected['pet_shape_text']}")
            print(f"    pet_signature = {projected['pet_signature']}")
            print(f"    pet_generator = {projected['pet_generator']}")
            print(
                "    pet_child_generators = "
                f"{projected['pet_child_generators']}"
            )
            print(f"    center_role = {projected['center_role']}")
            print(f"    claim = {decode_data['claim']}")

    if data.get("center_lens"):
        lens = data["decoded_center_lens"]
        print()
        print("PET decoded-center lens")
        if not lens or not lens["center_lens_available"]:
            reason = "unknown" if not lens else lens["reason"]
            print(f"  unavailable = {reason}")
        else:
            window = lens["suggested_window"]
            print(f"  source = {lens['source']}")
            print(f"  lens_kind = {lens['lens_kind']}")
            print(f"  edge_k = {lens['edge_k']}")
            print(f"  boundary = {lens['boundary']}")
            print(f"  preserve_edge_k = {'yes' if lens['preserve_edge_k'] else 'no'}")
            print(
                "  preserve_center_shape = "
                f"{'yes' if lens['preserve_center_shape'] else 'no'}"
            )
            print(f"  center_nearest_integer = {lens['center_nearest_integer']}")
            print(f"  center_shape = {lens['center_shape']}")
            print(f"  center_signature = {lens['center_signature']}")
            print(f"  center_generator = {lens['center_generator']}")
            print(f"  center_child_generators = {lens['center_child_generators']}")
            print(f"  center_bits = {lens['center_bits']}")
            print(f"  center_digits = {lens['center_digits']}")
            print(f"  suggested_window = k[{window['k_start']},{window['k_end']}]")
            print(f"  next_focus = {lens['next_focus']}")
            print(f"  recommended_next_lens = {lens['recommended_next_lens']}")
            print(f"  claim = {lens['claim']}")

    if data.get("realize"):
        realization = data["pet_realization"]
        print()
        print("PET realization payload")
        if not realization or not realization["realization_available"]:
            reason = "unknown" if not realization else realization["reason"]
            print(f"  unavailable = {reason}")
        else:
            encode_decode = realization["encode_decode"]
            realized_shape = realization["realized_shape"]
            print(f"  source = {realization['source']}")
            print(f"  source_form = {realization['source_form']}")
            print(f"  edge_k = {realization['edge_k']}")
            print(f"  boundary = {realization['boundary']}")
            print(f"  nearest_integer = {realization['nearest_integer']}")

            print()
            print("  Encode/decode")
            print(f"    encoded_pet = {encode_decode['encoded_pet']}")
            print(f"    decoded_back = {encode_decode['decoded_back']}")
            print(
                "    roundtrip_ok = "
                f"{'yes' if encode_decode['roundtrip_ok'] else 'no'}"
            )

            print()
            print("  Realized shape")
            print(f"    shape = {realized_shape['shape_text']}")
            print(f"    signature = {realized_shape['signature']}")
            print(f"    generator = {realized_shape['generator']}")
            print(f"    already_minimal = {realized_shape['already_minimal']}")
            print(f"    child_generators = {realized_shape['child_generators']}")
            print(f"    role = {realization['role']}")
            print(f"    claim = {realization['claim']}")

    if data.get("classic_handoff"):
        handoff = data["pet_classic_handoff"]
        print()
        print("PET classic handoff")
        if not handoff or not handoff["handoff_available"]:
            reason = "unknown" if not handoff else handoff["reason"]
            print(f"  unavailable = {reason}")
        else:
            print(f"  source = {handoff['source']}")
            print(f"  method = {handoff['method']}")
            print(f"  recommended = {'yes' if handoff['recommended'] else 'no'}")
            print(f"  reason = {handoff['reason']}")
            print(f"  edge_k = {handoff['edge_k']}")
            print(f"  center = {handoff['center']}")
            print(f"  radius = {handoff['radius']}")
            if handoff.get("scan_start") is not None:
                print(f"  scan_window = [{handoff['scan_start']},{handoff['scan_end']}]")
            if handoff.get("scan_limit") is not None:
                print(f"  scan_limit = {handoff['scan_limit']}")
            print(f"  candidates_checked = {handoff['candidates_checked']}")
            print(f"  divisor_found = {handoff['divisor_found']}")
            print(f"  cofactor = {handoff['cofactor']}")
            print(f"  verified = {'yes' if handoff['verified'] else 'no'}")
            print(f"  claim = {handoff['claim']}")

    if data.get("fork"):
        fork = data["peel_fork"]
        print()
        print("PET multi-threshold fork")
        if not fork or not fork["fork_available"]:
            reason = "unknown" if not fork else fork["reason"]
            print(f"  unavailable = {reason}")
        else:
            source = fork["source_band"]
            print(
                "  source_band = "
                f"{source['kind']} {source['move']} k[{source['k_range']}]"
            )
            print(f"  boundary = {source['boundary']}")
            print(f"  branch_count = {fork['branch_count']}")

            print()
            print("  Branches")
            for branch in fork["branches"]:
                retained = branch["retained_window"]
                side = branch["side_window"]
                print(f"    {branch['name']}")
                print(f"      move = {branch['move']}")
                print(f"      direction = {branch['direction']}")
                print(
                    "      retained_window = "
                    f"k[{retained['k_start']},{retained['k_end']}]"
                )
                print(
                    "      side_window = "
                    f"k[{side['k_start']},{side['k_end']}] "
                    f"({side['source_kind']} {side['source_move']})"
                )
                print(f"      side_role = {branch['side_role']}")
                print(f"      next_action = {branch['next_action']}")
                print(f"      reason = {branch['reason']}")

            print(f"  claim = {fork['claim']}")

    if data.get("fork_follow"):
        followup = data["peel_fork_followup"]
        print()
        print("PET fork follow-up lens")
        if not followup or not followup["available"]:
            reason = "unknown" if not followup else followup["reason"]
            print("  available = no")
            print(f"  reason = {reason}")
        else:
            source_window = followup["source_window"]
            retained_window = followup["retained_window"]
            print("  available = yes")
            print(f"  status = {followup['status']}")
            print(f"  requested_branch = {followup['requested_branch']}")
            print(f"  source_branch = {followup['source_branch']}")
            print(f"  source_move = {followup['source_move']}")
            print(f"  source_direction = {followup['source_direction']}")
            print(f"  source_role = {followup['source_role']}")
            print(
                "  retained_window = "
                f"k[{retained_window['k_start']},{retained_window['k_end']}]"
            )
            print(
                "  source_window = "
                f"k[{source_window['k_start']},{source_window['k_end']}]"
            )
            print(f"  target_edge_hint = {followup['target_edge_hint']}")
            print(f"  reduction_kind = {followup['reduction_kind']}")
            print(f"  recommended_next_lens = {followup['recommended_next_lens']}")
            print(f"  next_action = {followup['next_action']}")
            print(f"  reason = {followup['reason']}")
            print(f"  claim = {followup['claim']}")

    print()
    print("PET interpretation")
    for line in data["interpretation"]:
        print(f"  {line}")

    print()
    print(f"claim = {data['claim']}")


def _same_k_window(left: dict | None, right: dict | None) -> bool:
    if left is None or right is None:
        return False
    return (
        int(left["k_start"]) == int(right["k_start"])
        and int(left["k_end"]) == int(right["k_end"])
    )


def _parse_k_range(k_range: str) -> tuple[int, int]:
    start_text, end_text = k_range.split("..", 1)
    return int(start_text), int(end_text)


def _k_range_overlaps_window(k_range: str, window: dict | None) -> bool:
    if window is None:
        return True

    start, end = _parse_k_range(k_range)
    window_start = int(window["k_start"])
    window_end = int(window["k_end"])
    return start <= window_end and end >= window_start


def _k_range_inside_window(k_range: str, window: dict | None) -> bool:
    if window is None:
        return True

    start, end = _parse_k_range(k_range)
    window_start = int(window["k_start"])
    window_end = int(window["k_end"])
    return start >= window_start and end <= window_end


def _select_windowed_recursive_peel(
    n: int,
    *,
    active_window: dict | None,
    excluded_support_limit: int,
    max_generator_count: int,
    max_move_span: int,
) -> dict:
    effective_max_generator_count = max_generator_count
    if active_window is not None:
        effective_max_generator_count = min(
            max_generator_count,
            int(active_window["k_end"]),
        )

    peel = _opaque_focused_peel(
        n,
        max_generator_count=effective_max_generator_count,
        excluded_support_limit=excluded_support_limit,
        max_move_span=max_move_span,
        center_lens=True,
    )

    if active_window is None:
        return {
            "peel": peel,
            "effective_max_generator_count": effective_max_generator_count,
            "window_filter": "full",
            "window_match": True,
        }

    selected_range = peel["selected_band"]["k_range"]
    if _k_range_overlaps_window(selected_range, active_window):
        return {
            "peel": peel,
            "effective_max_generator_count": effective_max_generator_count,
            "window_filter": "overlap",
            "window_match": True,
        }

    response = _opaque_mass_response(
        n,
        max_generator_count=effective_max_generator_count,
        excluded_support_limit=excluded_support_limit,
        max_move_span=max_move_span,
        include_bands=True,
    )

    matching_bands = [
        band
        for band in response["magnetic_bands"]
        if _k_range_overlaps_window(band["k_range"], active_window)
    ]
    if not matching_bands:
        return {
            "peel": peel,
            "effective_max_generator_count": effective_max_generator_count,
            "window_filter": "overlap",
            "window_match": False,
            "reason": "no magnetic band overlaps active window",
        }

    best = sorted(
        matching_bands,
        key=lambda band: (
            -int(band["focus_score"]),
            int(band["min_trigger_span"]),
            abs(int(band["closest_k"]) - int(active_window["k_end"])),
        ),
    )[0]

    windowed_peel = _opaque_focused_peel(
        n,
        max_generator_count=effective_max_generator_count,
        excluded_support_limit=excluded_support_limit,
        max_move_span=max_move_span,
        kind=best["kind"],
        move=best["move"],
        center_lens=True,
    )

    return {
        "peel": windowed_peel,
        "effective_max_generator_count": effective_max_generator_count,
        "window_filter": "overlap",
        "window_match": True,
        "forced_band": {
            "kind": best["kind"],
            "move": best["move"],
            "k_range": best["k_range"],
        },
    }



def _small_factorization_payload(value: int) -> dict:
    factors = prime_factorization(value)
    flat = []
    for prime, exponent in factors:
        flat.extend([prime] * exponent)

    return {
        "value": value,
        "factors": [
            {"prime": prime, "exponent": exponent}
            for prime, exponent in factors
        ],
        "flat_factors": flat,
        "text": " * ".join(str(part) for part in flat) if flat else str(value),
    }


def _opaque_recursive_lens_composite_edge_peel(levels: list[dict]) -> dict:
    claim = "PET composite-edge peel only; this does not factor N"

    available_levels = [
        level
        for level in levels
        if level.get("available")
        and "center_lens" in level
        and int(level.get("edge_k", 0)) > 2
    ]

    if not available_levels:
        return {
            "available": False,
            "reason": "no recursive center lens with composite edge_k > 2 is available",
            "claim": claim,
        }

    candidate_level = None
    for level in reversed(available_levels):
        edge_k = int(level["edge_k"])
        edge_factors = prime_factorization(edge_k)
        if len(edge_factors) > 1 or edge_factors[0][1] > 1:
            candidate_level = level
            break

    if candidate_level is None:
        return {
            "available": False,
            "reason": "recursive edge_k values are prime or non-composite",
            "claim": claim,
        }

    edge_k = int(candidate_level["edge_k"])
    lens = candidate_level["center_lens"]
    center_generator = int(lens["center_generator"])

    edge_payload = _small_factorization_payload(edge_k)
    generator_payload = _small_factorization_payload(center_generator)

    edge_factor_set = set(edge_payload["flat_factors"])
    generator_factor_set = set(generator_payload["flat_factors"])
    shared = sorted(edge_factor_set & generator_factor_set)

    subedge_lenses = [
        {
            "edge_k": factor,
            "role": (
                "shared-form-subedge"
                if factor in shared
                else "edge-only-subedge"
            ),
            "next_action": "inspect symbolic subedge as PET form, not as N divisor",
        }
        for factor in sorted(edge_factor_set)
    ]

    return {
        "available": True,
        "source_level": candidate_level["level"],
        "source_form": (
            f"{candidate_level['visible_form']}:"
            f"{candidate_level['visible_shape']}"
        ),
        "source_band": {
            "kind": candidate_level["selected_band"]["kind"],
            "move": candidate_level["selected_band"]["move"],
            "k_range": candidate_level["selected_band"]["k_range"],
            "signal": candidate_level["selected_band"]["signal"],
            "focus_score": candidate_level["selected_band"]["focus_score"],
        },
        "source_edge_k": edge_k,
        "edge_factorization": edge_payload,
        "center_lens_kind": lens["lens_kind"],
        "center_shape": lens["center_shape"],
        "center_generator": center_generator,
        "center_generator_factorization": generator_payload,
        "shared_form_factors": shared,
        "subedge_lenses": subedge_lenses,
        "classic_bridge_recommendation": "not-recommended",
        "reason": (
            "stable composite edge exposes symbolic subedges; "
            "this is PET-form analysis, not a divisor anchor"
        ),
        "claim": claim,
    }


def _opaque_recursive_lens_anchor_field(levels: list[dict]) -> dict:
    claim = "PET anchor-field analysis only; this does not factor N"

    candidate_level = None
    for level in reversed(levels):
        if not level.get("available"):
            continue
        if "center_lens" not in level:
            continue
        if int(level.get("edge_k", -1)) != 2:
            continue
        candidate_level = level
        break

    if candidate_level is None:
        return {
            "available": False,
            "reason": "no recursive center lens with edge_k=2 is available",
            "claim": claim,
        }

    lens = candidate_level["center_lens"]
    band = candidate_level["selected_band"]
    visible_shape = candidate_level["visible_shape"]
    lens_kind = lens["lens_kind"]
    center_generator = int(lens["center_generator"])
    signal = band["signal"]

    if (
        visible_shape == "thin-ramp"
        and lens_kind == "flat-three-leaf-center"
        and center_generator <= 30
    ):
        anchor_status = "strong"
        binding_strength = "high"
        classic_bridge_recommendation = "recommended"
        reason = "thin-ramp flat center forms a local divisor anchor"
    elif (
        visible_shape == "edge-point"
        and lens_kind == "projected-center-shape"
        and center_generator > 30
    ):
        anchor_status = "weak"
        binding_strength = "low"
        classic_bridge_recommendation = "not-recommended"
        reason = "edge-point projected center is structurally geometric, not a local divisor anchor"
    else:
        anchor_status = "unresolved"
        binding_strength = "unknown"
        classic_bridge_recommendation = "inspect-only"
        reason = "recursive edge form does not match a known anchor-field class"

    return {
        "available": True,
        "source_level": candidate_level["level"],
        "source_band": {
            "kind": band["kind"],
            "move": band["move"],
            "k_range": band["k_range"],
            "signal": signal,
            "focus_score": band["focus_score"],
        },
        "source_form": f"{candidate_level['visible_form']}:{visible_shape}",
        "edge_k": candidate_level["edge_k"],
        "center_lens_kind": lens_kind,
        "center_shape": lens["center_shape"],
        "center_generator": center_generator,
        "center_nearest_integer": lens["center_nearest_integer"],
        "anchor_status": anchor_status,
        "binding_strength": binding_strength,
        "classic_bridge_recommendation": classic_bridge_recommendation,
        "reason": reason,
        "claim": claim,
    }


def _opaque_recursive_lens_classic_handoff(
    n: int,
    levels: list[dict],
    *,
    radius: int,
) -> dict:
    if radius < 0:
        raise ValueError("--handoff-radius expects integers >= 0")

    candidate_level = None
    for level in reversed(levels):
        if not level.get("available"):
            continue
        if int(level.get("edge_k", -1)) != 2:
            continue
        if "center_lens" not in level:
            continue
        candidate_level = level
        break

    if candidate_level is None:
        return {
            "handoff_available": False,
            "reason": "no recursive center lens with edge_k=2 is available",
        }

    lens = candidate_level["center_lens"]
    pet_realization = {
        "realization_available": True,
        "source": "recursive-center-lens",
        "source_form": (
            f"{candidate_level['visible_form']}:"
            f"{candidate_level['visible_shape']}"
        ),
        "edge_k": candidate_level["edge_k"],
        "boundary": candidate_level["boundary"],
        "nearest_integer": lens["center_nearest_integer"],
    }

    handoff = _opaque_focused_peel_classic_handoff(
        n,
        pet_realization,
        radius=radius,
    )
    handoff["source"] = "recursive-center-lens"
    handoff["level"] = candidate_level["level"]
    handoff["anchor_useful"] = bool(handoff.get("verified"))
    handoff["claim"] = (
        "PET-guided recursive classic handoff only; "
        "classic divisibility check performed"
    )
    return handoff


def _opaque_recursive_lens_subedge_recursion(
    n: int,
    composite_edge_peel_payload: dict | None,
    *,
    excluded_support_limit: int,
    max_generator_count: int,
    max_move_span: int,
) -> dict:
    claim = "PET composite-subedge recursion only; this does not factor N"

    if (
        not composite_edge_peel_payload
        or not composite_edge_peel_payload.get("available")
    ):
        return {
            "available": False,
            "reason": "composite-edge peel is not available",
            "claim": claim,
        }

    subedge_results = []
    for subedge in composite_edge_peel_payload["subedge_lenses"]:
        subedge_k = int(subedge["edge_k"])
        target_window = {
            "k_start": subedge_k,
            "k_end": subedge_k,
            "k_range": f"{subedge_k}..{subedge_k}",
            "source": "composite-subedge",
        }

        try:
            selection = _select_windowed_recursive_peel(
                n,
                active_window=target_window,
                max_generator_count=max_generator_count,
                excluded_support_limit=excluded_support_limit,
                max_move_span=max_move_span,
            )
        except ValueError as exc:
            subedge_results.append(
                {
                    "subedge_k": subedge_k,
                    "target_window": target_window,
                    "available": False,
                    "reason": str(exc),
                    "source_role": subedge["role"],
                }
            )
            continue

        if not selection["window_match"]:
            subedge_results.append(
                {
                    "subedge_k": subedge_k,
                    "target_window": target_window,
                    "available": False,
                    "reason": selection["reason"],
                    "source_role": subedge["role"],
                    "window_filter": selection.get("window_filter"),
                }
            )
            continue

        peel = selection["peel"]
        center_lens = peel.get("decoded_center_lens")
        selected_band = peel["selected_band"]
        visible = peel.get("peel_lift", {}).get("visible_pet_form")

        center_lens_available = bool(
            center_lens and center_lens.get("center_lens_available")
        )

        subedge_results.append(
            {
                "subedge_k": subedge_k,
                "target_window": target_window,
                "available": True,
                "source_role": subedge["role"],
                "window_filter": selection.get("window_filter"),
                "forced_band": selection.get("forced_band"),
                "effective_max_generator_count": selection[
                    "effective_max_generator_count"
                ],
                "selected_band": {
                    "kind": selected_band["kind"],
                    "move": selected_band["move"],
                    "k_range": selected_band["k_range"],
                    "focus_score": selected_band["focus_score"],
                    "signal": selected_band["signal"],
                },
                "visible_form": None if not visible else visible["form"],
                "visible_shape": None if not visible else visible["shape"],
                "edge_k": None if not center_lens_available else center_lens["edge_k"],
                "center_lens_available": center_lens_available,
                "center_lens_kind": (
                    None if not center_lens_available else center_lens["lens_kind"]
                ),
                "center_generator": (
                    None
                    if not center_lens_available
                    else center_lens["center_generator"]
                ),
                "center_nearest_integer": (
                    None
                    if not center_lens_available
                    else center_lens["center_nearest_integer"]
                ),
                "center_shape": (
                    None
                    if not center_lens_available
                    else center_lens["center_shape"]
                ),
                "center_signature": (
                    None
                    if not center_lens_available
                    else center_lens["center_signature"]
                ),
                "suggested_window": (
                    None
                    if not center_lens_available
                    else center_lens["suggested_window"]
                ),
                "next_action": (
                    "inspect subedge visible form for thin-ramp or anchor-field"
                ),
            }
        )

    available_results = [
        result for result in subedge_results if result.get("available")
    ]

    convergence_groups: dict[tuple[int | None, int | None], list[dict]] = {}
    for result in available_results:
        key = (result.get("edge_k"), result.get("center_generator"))
        convergence_groups.setdefault(key, []).append(result)

    converged_groups = [
        group
        for key, group in convergence_groups.items()
        if key[0] is not None and key[1] is not None and len(group) > 1
    ]

    if converged_groups:
        best_group = sorted(
            converged_groups,
            key=lambda group: (-len(group), int(group[0]["edge_k"])),
        )[0]
        convergence = {
            "available": True,
            "kind": "twin-subedge-convergence",
            "converged_subedges": [
                result["subedge_k"] for result in best_group
            ],
            "converged_edge_k": best_group[0]["edge_k"],
            "converged_center_generator": best_group[0]["center_generator"],
            "converged_visible_shape": best_group[0]["visible_shape"],
            "converged_center_lens_kind": best_group[0]["center_lens_kind"],
            "reason": (
                "multiple symbolic subedges re-enter the same PET field"
            ),
        }
    else:
        convergence = {
            "available": False,
            "reason": "no repeated subedge PET field was detected",
        }

    if convergence["available"]:
        converged_subedges = set(convergence["converged_subedges"])
        converged_results = [
            result
            for result in available_results
            if result["subedge_k"] in converged_subedges
        ]
        centers = sorted(
            {
                result["center_nearest_integer"]
                for result in converged_results
                if result.get("center_nearest_integer") is not None
            }
        )

        visible_shape = convergence["converged_visible_shape"]
        converged_edge_k = int(convergence["converged_edge_k"])

        if (
            converged_edge_k == 2
            and visible_shape == "thin-ramp"
            and len(centers) == 1
        ):
            anchor_status = "strong"
            binding_strength = "high"
            classic_bridge_recommendation = "recommended"
            reason = (
                "twin subedges converge to a thin-ramp edge_k=2 field with "
                "a single realized center"
            )
        elif converged_edge_k == 2 and len(centers) == 1:
            anchor_status = "weak"
            binding_strength = "low"
            classic_bridge_recommendation = "not-recommended"
            reason = (
                "twin subedges converge to edge_k=2 with a single center, "
                "but visible shape is not anchor-like"
            )
        elif converged_edge_k == 2:
            anchor_status = "unresolved"
            binding_strength = "unknown"
            classic_bridge_recommendation = "not-recommended"
            reason = (
                "twin subedges converge to edge_k=2 but do not agree on a "
                "single realized center"
            )
        else:
            anchor_status = "structural-only"
            binding_strength = "medium"
            classic_bridge_recommendation = "not-recommended"
            reason = (
                "subedge convergence is structural but not classic-anchor compatible"
            )

        refined_anchor_candidate = {
            "available": True,
            "source": "twin-subedge-convergence",
            "base_centers": centers,
            "candidate_count": len(centers),
            "anchor_status": anchor_status,
            "binding_strength": binding_strength,
            "classic_bridge_recommendation": classic_bridge_recommendation,
            "converged_subedges": convergence["converged_subedges"],
            "converged_edge_k": convergence["converged_edge_k"],
            "converged_visible_shape": convergence["converged_visible_shape"],
            "converged_center_generator": convergence[
                "converged_center_generator"
            ],
            "reason": reason,
            "claim": (
                "PET convergence-refined anchor candidate only; "
                "this does not factor N"
            ),
        }
    else:
        refined_anchor_candidate = {
            "available": False,
            "reason": "subedge convergence is not available",
            "claim": (
                "PET convergence-refined anchor candidate only; "
                "this does not factor N"
            ),
        }

    single_anchor_candidates = [
        result
        for result in available_results
        if result.get("subedge_k") == 2
        and result.get("edge_k") == 2
        and result.get("center_lens_available")
        and result.get("center_lens_kind") in {
            "flat-two-leaf-center",
            "flat-three-leaf-center",
        }
    ]

    if single_anchor_candidates:
        best_single = sorted(
            single_anchor_candidates,
            key=lambda result: (
                0 if result["center_lens_kind"] == "flat-two-leaf-center" else 1,
                int(result["center_generator"]),
            ),
        )[0]
        single_subedge_anchor_candidate = {
            "available": True,
            "source": "single-subedge-recursion",
            "subedge_k": best_single["subedge_k"],
            "target_window": best_single["target_window"],
            "selected_band": best_single["selected_band"],
            "visible_form": best_single["visible_form"],
            "visible_shape": best_single["visible_shape"],
            "edge_k": best_single["edge_k"],
            "center_lens_kind": best_single["center_lens_kind"],
            "center_generator": best_single["center_generator"],
            "center_nearest_integer": best_single["center_nearest_integer"],
            "center_shape": best_single["center_shape"],
            "anchor_status": "unresolved",
            "binding_strength": "medium",
            "classic_bridge_recommendation": "diagnostic-only",
            "classic_bridge_kind": "small-range-verification",
            "reason": (
                "single k=2 subedge exposes a flat local center, "
                "but no subedge convergence confirms it"
            ),
            "claim": (
                "PET single-subedge anchor candidate only; "
                "this does not factor N"
            ),
        }
    else:
        single_subedge_anchor_candidate = {
            "available": False,
            "reason": "no single k=2 flat local subedge anchor candidate is available",
            "claim": (
                "PET single-subedge anchor candidate only; "
                "this does not factor N"
            ),
        }

    return {
        "available": bool(subedge_results),
        "source": "composite-edge-peel",
        "source_edge_k": composite_edge_peel_payload["source_edge_k"],
        "source_level": composite_edge_peel_payload["source_level"],
        "subedge_count": len(subedge_results),
        "available_subedge_count": len(available_results),
        "subedge_results": subedge_results,
        "convergence": convergence,
        "refined_anchor_candidate": refined_anchor_candidate,
        "single_subedge_anchor_candidate": single_subedge_anchor_candidate,
        "claim": claim,
    }


def _opaque_recursive_lens_branch_verdict(
    levels: list[dict],
    *,
    anchor_field_payload: dict | None,
    composite_edge_peel_payload: dict | None,
    subedge_recursion_payload: dict | None,
) -> dict:
    claim = "PET branch verdict only; this does not factor N"

    if (
        subedge_recursion_payload
        and subedge_recursion_payload.get("available")
    ):
        refined = subedge_recursion_payload.get("refined_anchor_candidate")
        if refined and refined.get("available"):
            classic_ready = (
                refined["classic_bridge_recommendation"] == "recommended"
                and refined["anchor_status"] == "strong"
            )
            if refined["anchor_status"] == "weak":
                best_signal = "twin-subedge-convergence"
            elif refined["anchor_status"] == "strong":
                best_signal = "strong-convergence-anchor"
            else:
                best_signal = f"{refined['anchor_status']}-subedge-convergence"

            return {
                "available": True,
                "classic_ready": classic_ready,
                "best_signal": best_signal,
                "anchor_status": refined["anchor_status"],
                "binding_strength": refined["binding_strength"],
                "classic_bridge_recommendation": refined[
                    "classic_bridge_recommendation"
                ],
                "source": refined["source"],
                "reason": refined["reason"],
                "claim": claim,
            }

        convergence = subedge_recursion_payload.get("convergence")
        if convergence and convergence.get("available"):
            return {
                "available": True,
                "classic_ready": False,
                "best_signal": convergence["kind"],
                "anchor_status": "weak",
                "binding_strength": "low",
                "classic_bridge_recommendation": "not-recommended",
                "source": "subedge-convergence",
                "reason": convergence["reason"],
                "claim": claim,
            }

        single_anchor = subedge_recursion_payload.get(
            "single_subedge_anchor_candidate"
        )
        if single_anchor and single_anchor.get("available"):
            return {
                "available": True,
                "classic_ready": False,
                "best_signal": "single-subedge-anchor-candidate",
                "anchor_status": single_anchor["anchor_status"],
                "binding_strength": single_anchor["binding_strength"],
                "classic_bridge_recommendation": single_anchor[
                    "classic_bridge_recommendation"
                ],
                "source": single_anchor["source"],
                "reason": single_anchor["reason"],
                "claim": claim,
            }

        if subedge_recursion_payload.get("subedge_count", 0) > 0:
            return {
                "available": True,
                "classic_ready": False,
                "best_signal": "composite-edge-with-dead-subedge",
                "anchor_status": "no",
                "binding_strength": "none",
                "classic_bridge_recommendation": "not-recommended",
                "source": "subedge-recursion",
                "reason": (
                    "composite edge produced subedges, but no subedge produced "
                    "a repeated PET field or single-subedge anchor candidate"
                ),
                "claim": claim,
            }

    if (
        composite_edge_peel_payload
        and composite_edge_peel_payload.get("available")
    ):
        return {
            "available": True,
            "classic_ready": False,
            "best_signal": "composite-edge",
            "anchor_status": "structural-only",
            "binding_strength": "medium",
            "classic_bridge_recommendation": "not-recommended",
            "source": "composite-edge-peel",
            "reason": composite_edge_peel_payload["reason"],
            "claim": claim,
        }

    if anchor_field_payload and anchor_field_payload.get("available"):
        classic_ready = (
            anchor_field_payload["classic_bridge_recommendation"]
            == "recommended"
            and anchor_field_payload["anchor_status"] == "strong"
        )
        return {
            "available": True,
            "classic_ready": classic_ready,
            "best_signal": f"{anchor_field_payload['anchor_status']}-anchor-field",
            "anchor_status": anchor_field_payload["anchor_status"],
            "binding_strength": anchor_field_payload["binding_strength"],
            "classic_bridge_recommendation": anchor_field_payload[
                "classic_bridge_recommendation"
            ],
            "source": "anchor-field",
            "reason": anchor_field_payload["reason"],
            "claim": claim,
        }

    available_levels = [level for level in levels if level.get("available")]
    if available_levels:
        last = available_levels[-1]
        edge_k = last.get("edge_k")
        center_lens = last.get("center_lens")
        if edge_k is not None and center_lens is not None:
            return {
                "available": True,
                "classic_ready": False,
                "best_signal": "stable-prime-or-unsplit-edge",
                "anchor_status": "structural-only",
                "binding_strength": "low",
                "classic_bridge_recommendation": "not-recommended",
                "source": "recursive-levels",
                "reason": (
                    "recursive branch produced a PET edge, but no composite "
                    "subedge or anchor field is available"
                ),
                "claim": claim,
            }

    return {
        "available": False,
        "classic_ready": False,
        "reason": "no usable recursive PET signal is available",
        "claim": claim,
    }


def _opaque_recursive_lens_shape_handoff_verdict(
    branch_verdict: dict,
    subedge_recursion_payload: dict | None,
) -> dict:
    claim = "PET shape handoff verdict only; this does not factor N"

    if not branch_verdict or not branch_verdict.get("available"):
        return {
            "available": False,
            "mode": "unavailable",
            "classic_ready": False,
            "diagnostic_classic_allowed": False,
            "recommended_method": None,
            "reason": "no usable PET branch verdict is available",
            "claim": claim,
        }

    single = None
    if subedge_recursion_payload and subedge_recursion_payload.get("available"):
        single = subedge_recursion_payload.get("single_subedge_anchor_candidate")

    if single and single.get("available"):
        diagnostic_allowed = (
            single["classic_bridge_recommendation"] == "diagnostic-only"
        )
        center_lens_kind = single.get("center_lens_kind")
        if diagnostic_allowed and center_lens_kind == "flat-two-leaf-center":
            recommended_method = "fermat-center-scan"
            anchor_kind = "fermat-center"
        elif diagnostic_allowed:
            recommended_method = "local-divisibility-scan"
            anchor_kind = "local-divisor-window"
        else:
            recommended_method = None
            anchor_kind = "none"

        return {
            "available": True,
            "mode": "diagnostic-only" if diagnostic_allowed else "structural-only",
            "best_signal": branch_verdict["best_signal"],
            "anchor_source": "single-subedge-anchor-candidate",
            "anchor_kind": anchor_kind,
            "anchor_status": single["anchor_status"],
            "classic_ready": False,
            "diagnostic_classic_allowed": diagnostic_allowed,
            "recommended_method": recommended_method,
            "center": single.get("center_nearest_integer"),
            "center_lens_kind": center_lens_kind,
            "binding_strength": single["binding_strength"],
            "risk": "no twin-subedge convergence",
            "reason": single["reason"],
            "claim": claim,
        }

    if branch_verdict.get("classic_ready"):
        return {
            "available": True,
            "mode": "classic-ready",
            "best_signal": branch_verdict["best_signal"],
            "anchor_source": branch_verdict["source"],
            "anchor_kind": "classic-anchor",
            "anchor_status": branch_verdict["anchor_status"],
            "classic_ready": True,
            "diagnostic_classic_allowed": False,
            "recommended_method": None,
            "center": None,
            "center_lens_kind": None,
            "binding_strength": branch_verdict["binding_strength"],
            "risk": "requires explicit classic handoff verification",
            "reason": branch_verdict["reason"],
            "claim": claim,
        }

    return {
        "available": True,
        "mode": (
            "weak"
            if branch_verdict.get("anchor_status") == "weak"
            else "structural-only"
        ),
        "best_signal": branch_verdict.get("best_signal"),
        "anchor_source": branch_verdict.get("source"),
        "anchor_kind": "none",
        "anchor_status": branch_verdict.get("anchor_status"),
        "classic_ready": False,
        "diagnostic_classic_allowed": False,
        "recommended_method": None,
        "center": None,
        "center_lens_kind": None,
        "binding_strength": branch_verdict.get("binding_strength"),
        "risk": "no PET anchor authorized for classic probing",
        "reason": branch_verdict.get("reason"),
        "claim": claim,
    }


def _opaque_recursive_lens_diagnostic_classic_probe(
    n: int,
    subedge_recursion_payload: dict | None,
    shape_handoff_verdict: dict | None,
    *,
    radius: int,
) -> dict:
    claim = "PET diagnostic classic probe only; this does not factor N unless verified"

    if radius < 0:
        raise ValueError("--handoff-radius expects integers >= 0")

    if (
        not shape_handoff_verdict
        or not shape_handoff_verdict.get("available")
        or not shape_handoff_verdict.get("diagnostic_classic_allowed")
    ):
        return {
            "available": False,
            "reason": "shape handoff verdict does not allow diagnostic classic probing",
            "claim": claim,
        }

    if (
        not subedge_recursion_payload
        or not subedge_recursion_payload.get("available")
    ):
        return {
            "available": False,
            "reason": "subedge recursion is not available",
            "claim": claim,
        }

    single = subedge_recursion_payload.get("single_subedge_anchor_candidate")
    if not single or not single.get("available"):
        return {
            "available": False,
            "reason": "single-subedge anchor candidate is not available",
            "claim": claim,
        }

    if single["classic_bridge_recommendation"] != "diagnostic-only":
        return {
            "available": False,
            "reason": "single-subedge anchor candidate is not diagnostic-only",
            "claim": claim,
        }

    method = shape_handoff_verdict.get("recommended_method")
    center = shape_handoff_verdict.get("center")
    if method not in {"fermat-center-scan", "local-divisibility-scan"}:
        return {
            "available": False,
            "reason": "shape handoff verdict does not recommend a supported diagnostic classic method",
            "claim": claim,
        }
    if center is None:
        return {
            "available": False,
            "reason": "shape handoff verdict does not provide a diagnostic center",
            "claim": claim,
        }

    center = int(center)
    start = max(2, center - radius)
    end = max(start, center + radius)

    candidates_checked = []
    divisor_found = None
    cofactor = None
    verified = False

    if method == "fermat-center-scan":
        for candidate_center in range(start, end + 1):
            candidates_checked.append(candidate_center)
            delta_square = candidate_center * candidate_center - n
            if delta_square < 0:
                continue

            delta = math.isqrt(delta_square)
            if delta * delta != delta_square:
                continue

            left = candidate_center - delta
            right = candidate_center + delta
            if left > 1 and right > 1 and left * right == n:
                divisor_found = left
                cofactor = right
                verified = True
                break
    elif method == "local-divisibility-scan":
        for candidate in range(start, end + 1):
            candidates_checked.append(candidate)
            if n % candidate == 0:
                divisor_found = candidate
                cofactor = n // candidate
                break

        verified = (
            divisor_found is not None
            and cofactor is not None
            and divisor_found * cofactor == n
        )

    return {
        "available": True,
        "source": "single-subedge-anchor-candidate",
        "probe_kind": "diagnostic-only-small-range",
        "method": method,
        "center": center,
        "radius": radius,
        "scan_start": start,
        "scan_end": end,
        "candidates_checked": candidates_checked,
        "candidates_checked_count": len(candidates_checked),
        "divisor_found": divisor_found,
        "cofactor": cofactor,
        "verified": verified,
        "anchor_status": single["anchor_status"],
        "classic_bridge_recommendation": single[
            "classic_bridge_recommendation"
        ],
        "reason": (
            "single-subedge anchor candidate allows a bounded diagnostic "
            "classic probe"
        ),
        "claim": claim,
    }


def _opaque_recursive_lens(
    n: int,
    *,
    excluded_support_limit: int,
    max_generator_count: int,
    max_move_span: int,
    depth: int,
    terminal_reduction: bool = False,
    branch_recursion: str | None = None,
    classic_handoff: bool = False,
    handoff_radius: int = 5,
    anchor_field: bool = False,
    composite_edge_peel: bool = False,
    diagnostic_classic_probe: bool = False,
) -> dict:
    if n < 1:
        raise ValueError("opaque-recursive-lens expects integers >= 1")
    if excluded_support_limit < 1:
        raise ValueError("--excluded-support-limit expects integers >= 1")
    if max_generator_count < 2:
        raise ValueError("--max-generator-count expects integers >= 2")
    if max_move_span < 1:
        raise ValueError("--max-move-span expects integers >= 1")
    if depth < 1:
        raise ValueError("--depth expects integers >= 1")

    levels = []
    active_window = None
    stop_reason = "depth-limit"

    for level_index in range(depth):
        effective_max_generator_count = max_generator_count
        if active_window is not None:
            effective_max_generator_count = min(
                max_generator_count,
                int(active_window["k_end"]),
            )

        if effective_max_generator_count < 2:
            stop_reason = "minimal-window"
            break

        try:
            selection = _select_windowed_recursive_peel(
                n,
                active_window=active_window,
                max_generator_count=max_generator_count,
                excluded_support_limit=excluded_support_limit,
                max_move_span=max_move_span,
            )
            effective_max_generator_count = selection["effective_max_generator_count"]

            if not selection["window_match"]:
                levels.append(
                    {
                        "level": level_index,
                        "input_window": active_window,
                        "effective_max_generator_count": effective_max_generator_count,
                        "available": False,
                        "reason": selection["reason"],
                    }
                )
                stop_reason = "terminal-window"
                break

            peel = selection["peel"]
        except ValueError as exc:
            levels.append(
                {
                    "level": level_index,
                    "input_window": active_window,
                    "effective_max_generator_count": effective_max_generator_count,
                    "available": False,
                    "reason": str(exc),
                }
            )
            stop_reason = "collapsed"
            break

        center_lens = peel["decoded_center_lens"]
        if not center_lens or not center_lens["center_lens_available"]:
            if branch_recursion is not None:
                branch_peel = _opaque_focused_peel(
                    n,
                    max_generator_count=effective_max_generator_count,
                    excluded_support_limit=excluded_support_limit,
                    max_move_span=max_move_span,
                    kind=peel["selected_band"]["kind"],
                    move=peel["selected_band"]["move"],
                    fork_follow=branch_recursion,
                )
                branch_followup = branch_peel["peel_fork_followup"]

                if branch_followup and branch_followup["available"]:
                    branch_window = branch_followup["source_window"]
                    levels.append(
                        {
                            "level": level_index,
                            "input_window": active_window,
                            "effective_max_generator_count": effective_max_generator_count,
                            "available": True,
                            "recursion_source": "fork-follow",
                            "window_filter": selection.get("window_filter"),
                            "forced_band": selection.get("forced_band"),
                            "selected_band": {
                                "kind": peel["selected_band"]["kind"],
                                "move": peel["selected_band"]["move"],
                                "k_range": peel["selected_band"]["k_range"],
                                "focus_score": peel["selected_band"]["focus_score"],
                                "signal": peel["selected_band"]["signal"],
                            },
                            "branch_followup": branch_followup,
                            "branch_window": branch_window,
                            "edge_k": branch_followup["target_edge_hint"],
                            "visible_form": "fork-follow",
                            "visible_shape": branch_followup["reduction_kind"],
                        }
                    )
                    active_window = branch_window
                    continue

            levels.append(
                {
                    "level": level_index,
                    "input_window": active_window,
                    "effective_max_generator_count": effective_max_generator_count,
                    "available": False,
                    "reason": (
                        "center lens unavailable"
                        if not center_lens
                        else center_lens["reason"]
                    ),
                }
            )
            stop_reason = "collapsed"
            break

        selected_band = peel["selected_band"]
        visible = peel["peel_lift"]["visible_pet_form"]
        decode = peel["pet_decode"]
        projected = decode["decoded_constraints"]["projected_center_pet_form"]
        suggested_window = center_lens["suggested_window"]

        level = {
            "level": level_index,
            "input_window": active_window,
            "effective_max_generator_count": effective_max_generator_count,
            "available": True,
            "window_filter": selection.get("window_filter"),
            "forced_band": selection.get("forced_band"),
            "visible_form": visible["form"],
            "visible_shape": visible["shape"],
            "edge_k": center_lens["edge_k"],
            "boundary": center_lens["boundary"],
            "selected_band": {
                "kind": selected_band["kind"],
                "move": selected_band["move"],
                "k_range": selected_band["k_range"],
                "focus_score": selected_band["focus_score"],
                "signal": selected_band["signal"],
            },
            "center_lens": {
                "lens_kind": center_lens["lens_kind"],
                "center_shape": center_lens["center_shape"],
                "center_signature": center_lens["center_signature"],
                "center_generator": center_lens["center_generator"],
                "center_nearest_integer": center_lens["center_nearest_integer"],
                "center_bits": center_lens["center_bits"],
                "center_digits": center_lens["center_digits"],
                "suggested_window": suggested_window,
                "recommended_next_lens": center_lens["recommended_next_lens"],
            },
            "projected_center": {
                "expression": projected["expression"],
                "nearest_integer": projected["nearest_integer"],
                "pet_shape_text": projected["pet_shape_text"],
                "pet_signature": projected["pet_signature"],
                "pet_generator": projected["pet_generator"],
            },
        }
        levels.append(level)

        if _same_k_window(active_window, suggested_window):
            stop_reason = "stable-window"
            break

        if (
            int(suggested_window["k_start"]) == 1
            and int(suggested_window["k_end"]) <= 2
        ):
            if (
                level["visible_shape"] == "edge-point"
                and int(level["edge_k"]) == 2
                and int(suggested_window["k_start"]) == 1
                and int(suggested_window["k_end"]) == 2
                and level_index + 1 < depth
            ):
                level["rampification"] = {
                    "attempted": True,
                    "source_level": level_index,
                    "source_window": active_window,
                    "target_window": suggested_window,
                    "reason": (
                        "edge-point requires PET-side rampification before "
                        "treating the minimal window as terminal"
                    ),
                    "claim": (
                        "PET edge-point rampification only; this does not factor N"
                    ),
                }
                active_window = suggested_window
                continue

            active_window = suggested_window
            stop_reason = "minimal-window"
            break

        active_window = suggested_window

    center_shapes = [
        level["center_lens"]["center_shape"]
        for level in levels
        if level.get("available") and "center_lens" in level
    ]
    center_generators = [
        level["center_lens"]["center_generator"]
        for level in levels
        if level.get("available") and "center_lens" in level
    ]
    edges = [
        level["edge_k"]
        for level in levels
        if level.get("available")
    ]
    visible_forms = [
        f"{level['visible_form']}:{level['visible_shape']}"
        for level in levels
        if level.get("available")
    ]

    recurrence = {
        "level_count": len(levels),
        "available_level_count": sum(1 for level in levels if level.get("available")),
        "center_shape_sequence": center_shapes,
        "center_generator_sequence": center_generators,
        "edge_sequence": edges,
        "visible_form_sequence": visible_forms,
        "stable_center_shape": (
            len(center_shapes) > 1 and len(set(center_shapes)) == 1
        ),
        "stable_center_generator": (
            len(center_generators) > 1 and len(set(center_generators)) == 1
        ),
        "stable_edge": len(edges) > 1 and len(set(edges)) == 1,
        "status": stop_reason,
    }

    recursive_classic_handoff = (
        _opaque_recursive_lens_classic_handoff(
            n,
            levels,
            radius=handoff_radius,
        )
        if classic_handoff
        else None
    )
    anchor_field_payload = (
        _opaque_recursive_lens_anchor_field(levels)
        if anchor_field
        else None
    )
    composite_edge_peel_payload = (
        _opaque_recursive_lens_composite_edge_peel(levels)
        if composite_edge_peel
        else None
    )
    subedge_recursion_payload = (
        _opaque_recursive_lens_subedge_recursion(
            n,
            composite_edge_peel_payload,
            excluded_support_limit=excluded_support_limit,
            max_generator_count=max_generator_count,
            max_move_span=max_move_span,
        )
        if composite_edge_peel
        else None
    )
    branch_verdict = _opaque_recursive_lens_branch_verdict(
        levels,
        anchor_field_payload=anchor_field_payload,
        composite_edge_peel_payload=composite_edge_peel_payload,
        subedge_recursion_payload=subedge_recursion_payload,
    )
    shape_handoff_verdict = _opaque_recursive_lens_shape_handoff_verdict(
        branch_verdict,
        subedge_recursion_payload,
    )

    diagnostic_classic_probe_payload = (
        _opaque_recursive_lens_diagnostic_classic_probe(
            n,
            subedge_recursion_payload,
            shape_handoff_verdict,
            radius=handoff_radius,
        )
        if diagnostic_classic_probe
        else None
    )

    data = {
        "n": n,
        "digits": len(str(n)),
        "bit_length": n.bit_length(),
        "excluded_support_limit": excluded_support_limit,
        "excluded_support_bits": excluded_support_limit.bit_length(),
        "max_generator_count": max_generator_count,
        "max_move_span": max_move_span,
        "depth": depth,
        "classic_handoff": classic_handoff,
        "handoff_radius": handoff_radius,
        "anchor_field": anchor_field,
        "composite_edge_peel": composite_edge_peel,
        "subedge_recursion": composite_edge_peel,
        "levels": levels,
        "anchor_field_payload": anchor_field_payload,
        "composite_edge_peel_payload": composite_edge_peel_payload,
        "subedge_recursion_payload": subedge_recursion_payload,
        "branch_verdict": branch_verdict,
        "shape_handoff_verdict": shape_handoff_verdict,
        "diagnostic_classic_probe": diagnostic_classic_probe,
        "diagnostic_classic_probe_payload": diagnostic_classic_probe_payload,
        "recursive_classic_handoff": recursive_classic_handoff,
        "recurrence": recurrence,
        "interpretation": [
            "The recursive lens re-enters PET-local windows suggested by decoded center lenses.",
            "Each level preserves the decoded edge and projected center shape from the previous visible form.",
            "Recurrence tracks whether center shapes, generators, or edges stabilize across zoom levels.",
            "This is a recursive PET zoom lens; it does not inspect value divisibility.",
        ],
        "claim": "PET recursive zoom lens only; this does not factor N",
    }

    if terminal_reduction:
        available_levels = [level for level in levels if level.get("available")]
        last_available = available_levels[-1] if available_levels else None
        terminal_reduction_payload = {
            "available": False,
            "reason": "recursive lens did not stop at a terminal window",
            "claim": "PET reduction lens only; this does not factor N",
        }

        if recurrence["status"] == "terminal-window" and last_available is not None:
            suggested = last_available["center_lens"]["suggested_window"]
            terminal_reduction_payload = {
                "available": True,
                "status": "proposal",
                "claim": "PET reduction lens only; this does not factor N",
                "source_status": "terminal-window",
                "source_edge_k": last_available["edge_k"],
                "source_window": suggested,
                "source_visible_form": last_available["visible_form"],
                "source_visible_shape": last_available["visible_shape"],
                "source_center_shape": last_available["center_lens"]["center_shape"],
                "source_center_generator": last_available["center_lens"]["center_generator"],
                "target_edge_k": 2,
                "reduction_kind": "semiprime-projection",
                "recommended_classic_handoff": False,
            }

        data["terminal_reduction"] = terminal_reduction_payload

    return data


def _print_opaque_recursive_lens(data: dict) -> None:
    print("PET OPAQUE RECURSIVE LENS")
    print()
    print("Observed projection")
    print(f"  digits = {data['digits']}")
    print(f"  bit_length = {data['bit_length']}")
    print(f"  excluded_backbone_support = <= {data['excluded_support_limit']}")
    print(f"  excluded_support_bits = {data['excluded_support_bits']}")
    print(f"  max_generator_count = {data['max_generator_count']}")
    print(f"  max_move_span = {data['max_move_span']}")
    print(f"  depth = {data['depth']}")

    print()
    print("Recursive zoom levels")
    if not data["levels"]:
        print("  none")
    else:
        for level in data["levels"]:
            print()
            print(f"  level {level['level']}")
            if level["input_window"] is None:
                print("    input_window = full")
            else:
                window = level["input_window"]
                print(f"    input_window = k[{window['k_start']},{window['k_end']}]")
            print(
                "    effective_max_generator_count = "
                f"{level['effective_max_generator_count']}"
            )

            if not level["available"]:
                print(f"    unavailable = {level['reason']}")
                continue

            band = level["selected_band"]
            print(f"    window_filter = {level.get('window_filter')}")

            if level.get("recursion_source") == "fork-follow":
                followup = level["branch_followup"]
                branch_window = level["branch_window"]
                print(f"    visible_form = {level['visible_form']}")
                print(f"    visible_shape = {level['visible_shape']}")
                print(f"    edge_k = {level['edge_k']}")
                print(f"    recursion_source = {level['recursion_source']}")
                print(f"    source_branch = {followup['source_branch']}")
                print(
                    "    branch_window = "
                    f"k[{branch_window['k_start']},{branch_window['k_end']}]"
                )
                print(f"    recommended_next_lens = {followup['recommended_next_lens']}")
                print(
                    "    selected_band = "
                    f"{band['kind']} {band['move']} k[{band['k_range']}]"
                )
                continue

            lens = level["center_lens"]
            suggested = lens["suggested_window"]
            if level.get("forced_band"):
                forced = level["forced_band"]
                print(
                    "    forced_band = "
                    f"{forced['kind']} {forced['move']} k[{forced['k_range']}]"
                )
            print(f"    visible_form = {level['visible_form']}")
            print(f"    visible_shape = {level['visible_shape']}")
            print(f"    edge_k = {level['edge_k']}")
            print(f"    boundary = {level['boundary']}")
            print(
                "    selected_band = "
                f"{band['kind']} {band['move']} k[{band['k_range']}]"
            )
            print(f"    center_lens_kind = {lens['lens_kind']}")
            print(f"    center_shape = {lens['center_shape']}")
            print(f"    center_generator = {lens['center_generator']}")
            print(f"    center_nearest_integer = {lens['center_nearest_integer']}")
            print(
                "    suggested_window = "
                f"k[{suggested['k_start']},{suggested['k_end']}]"
            )
            print(
                "    recommended_next_lens = "
                f"{lens['recommended_next_lens']}"
            )
            if level.get("rampification"):
                ramp = level["rampification"]
                target = ramp["target_window"]
                print("    rampification = attempted")
                print(
                    "    rampification_target_window = "
                    f"k[{target['k_start']},{target['k_end']}]"
                )
                print(f"    rampification_reason = {ramp['reason']}")

    recurrence = data["recurrence"]
    print()
    print("Recurrence")
    print(f"  status = {recurrence['status']}")
    print(f"  level_count = {recurrence['level_count']}")
    print(f"  available_level_count = {recurrence['available_level_count']}")
    print(f"  center_shape_sequence = {recurrence['center_shape_sequence']}")
    print(f"  center_generator_sequence = {recurrence['center_generator_sequence']}")
    print(f"  edge_sequence = {recurrence['edge_sequence']}")
    print(f"  visible_form_sequence = {recurrence['visible_form_sequence']}")
    print(
        "  stable_center_shape = "
        f"{'yes' if recurrence['stable_center_shape'] else 'no'}"
    )
    print(
        "  stable_center_generator = "
        f"{'yes' if recurrence['stable_center_generator'] else 'no'}"
    )
    print(f"  stable_edge = {'yes' if recurrence['stable_edge'] else 'no'}")

    if "terminal_reduction" in data:
        reduction = data["terminal_reduction"]
        print()
        print("PET terminal reduction lens")
        print(f"  available = {'yes' if reduction['available'] else 'no'}")
        if not reduction["available"]:
            print(f"  reason = {reduction['reason']}")
        else:
            source_window = reduction["source_window"]
            print(f"  status = {reduction['status']}")
            print(f"  source_status = {reduction['source_status']}")
            print(f"  source_edge_k = {reduction['source_edge_k']}")
            print(
                "  source_window = "
                f"k[{source_window['k_start']},{source_window['k_end']}]"
            )
            print(f"  source_visible_form = {reduction['source_visible_form']}")
            print(f"  source_visible_shape = {reduction['source_visible_shape']}")
            print(f"  source_center_shape = {reduction['source_center_shape']}")
            print(f"  source_center_generator = {reduction['source_center_generator']}")
            print(f"  target_edge_k = {reduction['target_edge_k']}")
            print(f"  reduction_kind = {reduction['reduction_kind']}")
            print(
                "  recommended_classic_handoff = "
                f"{'yes' if reduction['recommended_classic_handoff'] else 'no'}"
            )
        print(f"  claim = {reduction['claim']}")

    if data.get("composite_edge_peel"):
        peel = data["composite_edge_peel_payload"]
        print()
        print("PET composite-edge peel")
        if not peel or not peel["available"]:
            reason = "unknown" if not peel else peel["reason"]
            print(f"  unavailable = {reason}")
        else:
            band = peel["source_band"]
            print(f"  source_level = {peel['source_level']}")
            print(
                "  source_band = "
                f"{band['kind']} {band['move']} k[{band['k_range']}]"
            )
            print(f"  source_signal = {band['signal']}")
            print(f"  source_form = {peel['source_form']}")
            print(f"  source_edge_k = {peel['source_edge_k']}")
            print(
                "  edge_factorization = "
                f"{peel['edge_factorization']['text']}"
            )
            print(f"  center_lens_kind = {peel['center_lens_kind']}")
            print(f"  center_shape = {peel['center_shape']}")
            print(f"  center_generator = {peel['center_generator']}")
            print(
                "  center_generator_factorization = "
                f"{peel['center_generator_factorization']['text']}"
            )
            print(f"  shared_form_factors = {peel['shared_form_factors']}")
            print("  subedge_lenses")
            for lens in peel["subedge_lenses"]:
                print(
                    f"    k={lens['edge_k']} "
                    f"role={lens['role']}"
                )
            print(
                "  classic_bridge_recommendation = "
                f"{peel['classic_bridge_recommendation']}"
            )
            print(f"  reason = {peel['reason']}")
            print(f"  claim = {peel['claim']}")

    if data.get("subedge_recursion"):
        recursion = data["subedge_recursion_payload"]
        print()
        print("PET composite-subedge recursion")
        if not recursion or not recursion["available"]:
            reason = "unknown" if not recursion else recursion["reason"]
            print(f"  unavailable = {reason}")
        else:
            print(f"  source = {recursion['source']}")
            print(f"  source_level = {recursion['source_level']}")
            print(f"  source_edge_k = {recursion['source_edge_k']}")
            print(f"  subedge_count = {recursion['subedge_count']}")
            print(
                "  available_subedge_count = "
                f"{recursion['available_subedge_count']}"
            )

            print()
            print("  Subedge results")
            for result in recursion["subedge_results"]:
                target = result["target_window"]
                print(f"    subedge_k = {result['subedge_k']}")
                print(
                    "      target_window = "
                    f"k[{target['k_start']},{target['k_end']}]"
                )
                print(f"      source_role = {result['source_role']}")
                if not result["available"]:
                    print(f"      unavailable = {result['reason']}")
                    continue

                band = result["selected_band"]
                print(f"      window_filter = {result.get('window_filter')}")
                print(
                    "      selected_band = "
                    f"{band['kind']} {band['move']} k[{band['k_range']}]"
                )
                print(f"      visible_form = {result['visible_form']}")
                print(f"      visible_shape = {result['visible_shape']}")
                print(f"      edge_k = {result['edge_k']}")
                print(
                    "      center_lens_available = "
                    f"{'yes' if result['center_lens_available'] else 'no'}"
                )
                print(f"      center_lens_kind = {result['center_lens_kind']}")
                print(f"      center_generator = {result['center_generator']}")

                suggested = result["suggested_window"]
                if suggested is not None:
                    print(
                        "      suggested_window = "
                        f"k[{suggested['k_start']},{suggested['k_end']}]"
                    )
                print(f"      next_action = {result['next_action']}")

            convergence = recursion["convergence"]
            print()
            print("  Subedge convergence")
            if not convergence["available"]:
                print("    available = no")
                print(f"    reason = {convergence['reason']}")
            else:
                print("    available = yes")
                print(f"    kind = {convergence['kind']}")
                print(
                    "    converged_subedges = "
                    f"{convergence['converged_subedges']}"
                )
                print(
                    "    converged_edge_k = "
                    f"{convergence['converged_edge_k']}"
                )
                print(
                    "    converged_center_generator = "
                    f"{convergence['converged_center_generator']}"
                )
                print(
                    "    converged_visible_shape = "
                    f"{convergence['converged_visible_shape']}"
                )
                print(
                    "    converged_center_lens_kind = "
                    f"{convergence['converged_center_lens_kind']}"
                )
                print(f"    reason = {convergence['reason']}")

            refined = recursion["refined_anchor_candidate"]
            print()
            print("  Convergence-refined anchor candidate")
            if not refined["available"]:
                print("    available = no")
                print(f"    reason = {refined['reason']}")
            else:
                print("    available = yes")
                print(f"    source = {refined['source']}")
                print(f"    base_centers = {refined['base_centers']}")
                print(f"    candidate_count = {refined['candidate_count']}")
                print(f"    anchor_status = {refined['anchor_status']}")
                print(f"    binding_strength = {refined['binding_strength']}")
                print(
                    "    classic_bridge_recommendation = "
                    f"{refined['classic_bridge_recommendation']}"
                )
                print(
                    "    converged_subedges = "
                    f"{refined['converged_subedges']}"
                )
                print(
                    "    converged_edge_k = "
                    f"{refined['converged_edge_k']}"
                )
                print(
                    "    converged_visible_shape = "
                    f"{refined['converged_visible_shape']}"
                )
                print(
                    "    converged_center_generator = "
                    f"{refined['converged_center_generator']}"
                )
                print(f"    reason = {refined['reason']}")
                print(f"    claim = {refined['claim']}")

            single = recursion["single_subedge_anchor_candidate"]
            print()
            print("  Single-subedge anchor candidate")
            if not single["available"]:
                print("    available = no")
                print(f"    reason = {single['reason']}")
            else:
                target = single["target_window"]
                band = single["selected_band"]
                print("    available = yes")
                print(f"    source = {single['source']}")
                print(f"    subedge_k = {single['subedge_k']}")
                print(
                    "    target_window = "
                    f"k[{target['k_start']},{target['k_end']}]"
                )
                print(
                    "    selected_band = "
                    f"{band['kind']} {band['move']} k[{band['k_range']}]"
                )
                print(f"    visible_form = {single['visible_form']}")
                print(f"    visible_shape = {single['visible_shape']}")
                print(f"    edge_k = {single['edge_k']}")
                print(f"    center_lens_kind = {single['center_lens_kind']}")
                print(f"    center_generator = {single['center_generator']}")
                print(
                    "    center_nearest_integer = "
                    f"{single['center_nearest_integer']}"
                )
                print(f"    center_shape = {single['center_shape']}")
                print(f"    anchor_status = {single['anchor_status']}")
                print(f"    binding_strength = {single['binding_strength']}")
                print(
                    "    classic_bridge_recommendation = "
                    f"{single['classic_bridge_recommendation']}"
                )
                print(
                    "    classic_bridge_kind = "
                    f"{single['classic_bridge_kind']}"
                )
                print(f"    reason = {single['reason']}")
                print(f"    claim = {single['claim']}")

            print(f"  claim = {recursion['claim']}")

    if data.get("anchor_field"):
        field = data["anchor_field_payload"]
        print()
        print("PET anchor field")
        if not field or not field["available"]:
            reason = "unknown" if not field else field["reason"]
            print(f"  unavailable = {reason}")
        else:
            band = field["source_band"]
            print(f"  source_level = {field['source_level']}")
            print(
                "  source_band = "
                f"{band['kind']} {band['move']} k[{band['k_range']}]"
            )
            print(f"  source_signal = {band['signal']}")
            print(f"  source_form = {field['source_form']}")
            print(f"  edge_k = {field['edge_k']}")
            print(f"  center_lens_kind = {field['center_lens_kind']}")
            print(f"  center_shape = {field['center_shape']}")
            print(f"  center_generator = {field['center_generator']}")
            print(f"  center_nearest_integer = {field['center_nearest_integer']}")
            print(f"  anchor_status = {field['anchor_status']}")
            print(f"  binding_strength = {field['binding_strength']}")
            print(
                "  classic_bridge_recommendation = "
                f"{field['classic_bridge_recommendation']}"
            )
            print(f"  reason = {field['reason']}")
            print(f"  claim = {field['claim']}")

    if data.get("classic_handoff"):
        handoff = data["recursive_classic_handoff"]
        print()
        print("PET recursive classic handoff")
        if not handoff or not handoff["handoff_available"]:
            reason = "unknown" if not handoff else handoff["reason"]
            print(f"  unavailable = {reason}")
        else:
            print(f"  source = {handoff['source']}")
            print(f"  level = {handoff.get('level')}")
            print(f"  method = {handoff['method']}")
            print(f"  recommended = {'yes' if handoff['recommended'] else 'no'}")
            print(f"  reason = {handoff['reason']}")
            print(f"  edge_k = {handoff['edge_k']}")
            print(f"  center = {handoff['center']}")
            print(f"  radius = {handoff['radius']}")
            if handoff.get("scan_start") is not None:
                print(f"  scan_window = [{handoff['scan_start']},{handoff['scan_end']}]")
            print(f"  candidates_checked = {handoff['candidates_checked']}")
            print(f"  divisor_found = {handoff['divisor_found']}")
            print(f"  cofactor = {handoff['cofactor']}")
            print(f"  verified = {'yes' if handoff['verified'] else 'no'}")
            print(f"  anchor_useful = {'yes' if handoff['anchor_useful'] else 'no'}")
            print(f"  claim = {handoff['claim']}")

    verdict = data.get("branch_verdict")
    if verdict is not None:
        print()
        print("PET branch verdict")
        if not verdict["available"]:
            print("  available = no")
            print(f"  classic_ready = {'yes' if verdict['classic_ready'] else 'no'}")
            print(f"  reason = {verdict['reason']}")
        else:
            print("  available = yes")
            print(f"  classic_ready = {'yes' if verdict['classic_ready'] else 'no'}")
            print(f"  best_signal = {verdict['best_signal']}")
            print(f"  anchor_status = {verdict['anchor_status']}")
            print(f"  binding_strength = {verdict['binding_strength']}")
            print(
                "  classic_bridge_recommendation = "
                f"{verdict['classic_bridge_recommendation']}"
            )
            print(f"  source = {verdict['source']}")
            print(f"  reason = {verdict['reason']}")
        print(f"  claim = {verdict['claim']}")

    if data.get("diagnostic_classic_probe"):
        probe = data["diagnostic_classic_probe_payload"]
        print()
        print("PET diagnostic classic probe")
        if not probe or not probe["available"]:
            reason = "unknown" if not probe else probe["reason"]
            print(f"  unavailable = {reason}")
        else:
            print(f"  source = {probe['source']}")
            print(f"  probe_kind = {probe['probe_kind']}")
            print(f"  method = {probe.get('method', 'unknown')}")
            print(f"  anchor_status = {probe['anchor_status']}")
            print(
                "  classic_bridge_recommendation = "
                f"{probe['classic_bridge_recommendation']}"
            )
            print(f"  center = {probe['center']}")
            print(f"  radius = {probe['radius']}")
            print(f"  scan_window = [{probe['scan_start']},{probe['scan_end']}]")
            print(
                "  candidates_checked_count = "
                f"{probe.get('candidates_checked_count', len(probe['candidates_checked']))}"
            )
            print(f"  divisor_found = {probe['divisor_found']}")
            print(f"  cofactor = {probe['cofactor']}")
            print(f"  verified = {'yes' if probe['verified'] else 'no'}")
            print(f"  reason = {probe['reason']}")
            print(f"  claim = {probe['claim']}")

    print()
    print("PET interpretation")
    for line in data["interpretation"]:
        print(f"  {line}")

    print()
    print(f"claim = {data['claim']}")


def _next_prime_at_or_after(n: int) -> int:
    candidate = max(2, n)

    while not is_prime(candidate):
        candidate += 1

    return candidate


def _ensure_int_string_digit_capacity(required_digits: int) -> None:
    if not hasattr(sys, "set_int_max_str_digits"):
        return

    current_limit = sys.get_int_max_str_digits()
    if current_limit == 0 or current_limit >= required_digits:
        return

    sys.set_int_max_str_digits(required_digits)


def _opaque_synthetic_profile(
    *,
    target_digits: int,
    start_prime: int,
    base: int,
    full_fry: bool = False,
) -> dict:
    if target_digits < 1:
        raise ValueError("--target-digits must be >= 1")

    _ensure_int_string_digit_capacity(target_digits + 1000)
    if start_prime < 2:
        raise ValueError("--start-prime must be >= 2")
    if base < 1:
        raise ValueError("--base must be >= 1")

    primes: list[int] = []
    n = base
    candidate = start_prime

    while len(str(n)) < target_digits:
        prime = _next_prime_at_or_after(candidate)
        primes.append(prime)
        n *= prime
        candidate = prime + 1

    if full_fry:
        limits = [100_000, start_prime]
        limits.extend(primes)
        limits = list(dict.fromkeys(limits))
    else:
        checkpoint_indexes = sorted(
            {
                index
                for index in [
                    0,
                    1,
                    9,
                    24,
                    49,
                    99,
                    len(primes) // 2,
                    len(primes) - 2,
                    len(primes) - 1,
                ]
                if 0 <= index < len(primes)
            }
        )

        limits = [100_000, start_prime]
        limits.extend(primes[index] for index in checkpoint_indexes)
        limits = list(dict.fromkeys(limits))

    profile = _opaque_profile(n, limits=limits)

    return {
        "base": base,
        "target_digits": target_digits,
        "start_prime": start_prime,
        "full_fry": full_fry,
        "prime_count": len(primes),
        "first_prime": primes[0] if primes else None,
        "last_prime": primes[-1] if primes else None,
        "n": n,
        "n_digits": len(str(n)),
        "n_bit_length": n.bit_length(),
        "limits": limits,
        "rows": profile["rows"],
        "claim": "synthetic bounded opaque residual profiling only; this does not solve general factorization",
    }


def _next_new_prime(support: set[int]) -> int:
    candidate = 2
    while True:
        if candidate not in support and is_prime(candidate):
            return candidate
        candidate += 1


def _explain_moves(n: int, *, include_generators: bool = True) -> dict:
    factors = prime_factorization(n)
    support = {p for p, _ in factors}

    by_exp: dict[int, list[int]] = {}
    for prime, exp in factors:
        by_exp.setdefault(exp, []).append(prime)

    q = _next_new_prime(support)
    new_n = n * q
    target_generator_for = (lambda value: shape_signature_dict(value)['generator']) if include_generators else (lambda value: None)

    moves = {
        "new": {
            "prime": q,
            "target_n": new_n,
            "target_generator": target_generator_for(new_n),
        },
        "drop": None,
        "inc": [],
        "dec": [],
    }

    for exp in sorted(by_exp):
        primes = sorted(by_exp[exp])
        rep = primes[0]

        inc_n = n * rep
        moves["inc"].append(
            {
                "exponent": exp,
                "count": len(primes),
                "primes": primes,
                "representative_prime": rep,
                "target_n": inc_n,
                "target_generator": target_generator_for(inc_n),
            }
        )

        if exp >= 2:
            dec_n = n // rep
            moves["dec"].append(
                {
                    "exponent": exp,
                    "count": len(primes),
                    "primes": primes,
                    "representative_prime": rep,
                    "target_n": dec_n,
                    "target_generator": target_generator_for(dec_n),
                }
            )

    if 1 in by_exp:
        primes = sorted(by_exp[1])
        rep = primes[0]
        drop_n = n // rep
        if drop_n >= 2:
            moves["drop"] = {
                "count": len(primes),
                "primes": primes,
                "representative_prime": rep,
                "target_n": drop_n,
                "target_generator": target_generator_for(drop_n),
            }

    return moves


def _pathwise_edges_for_number(n: int) -> list[dict]:
    moves = _explain_moves(n, include_generators=False)
    edges: list[dict] = []

    new_move = moves["new"]
    edges.append(
        {
            "label": f"NEW(x{new_move['prime']})",
            "target_n": new_move["target_n"],
            "target_generator": new_move["target_generator"],
        }
    )

    drop_move = moves["drop"]
    if drop_move is not None:
        for prime in drop_move["primes"]:
            target_n = n // prime
            if target_n >= 2:
                edges.append(
                    {
                        "label": f"DROP(p={prime})",
                        "target_n": target_n,
                        "target_generator": None,
                    }
                )

    for row in moves["inc"]:
        exponent = row["exponent"]
        for prime in row["primes"]:
            target_n = n * prime
            edges.append(
                {
                    "label": f"INC(p={prime},e={exponent})",
                    "target_n": target_n,
                    "target_generator": None,
                }
            )

    for row in moves["dec"]:
        exponent = row["exponent"]
        for prime in row["primes"]:
            target_n = n // prime
            if target_n >= 2:
                edges.append(
                    {
                        "label": f"DEC(p={prime},e={exponent})",
                        "target_n": target_n,
                        "target_generator": None,
                    }
                )

    return edges


def _pathwise_neighborhood(
    n: int,
    depth: int,
    max_nodes: int | None = None,
) -> dict:
    if depth <= 1:
        return {"levels": [], "truncated": False}

    frontier = {n: {"path": []}}
    levels: list[dict] = []
    seen_nodes = {n}
    truncated = False

    for level in range(1, depth + 1):
        next_targets: dict[int, dict] = {}

        for source_n, meta in sorted(frontier.items()):
            source_generator = shape_signature_dict(source_n)["generator"]

            for edge in _pathwise_edges_for_number(source_n):
                target_n = edge["target_n"]
                target_generator = edge["target_generator"]

                if target_n not in seen_nodes:
                    if max_nodes is not None and len(seen_nodes) >= max_nodes:
                        truncated = True
                        continue
                    seen_nodes.add(target_n)

                row = next_targets.setdefault(
                    target_n,
                    {
                        "n": target_n,
                        "generator": target_generator,
                        "from_numbers": set(),
                        "from_generators": set(),
                        "last_step_labels": set(),
                        "path": meta["path"] + [edge["label"]],
                    },
                )
                row["from_numbers"].add(source_n)
                row["from_generators"].add(source_generator)
                row["last_step_labels"].add(edge["label"])

        if not next_targets:
            break

        rows = []
        for target_n in sorted(next_targets):
            row = next_targets[target_n]
            rows.append(
                {
                    "n": row["n"],
                    "generator": row["generator"],
                    "from_numbers": sorted(row["from_numbers"]),
                    "from_generators": sorted(row["from_generators"]),
                    "last_step_labels": sorted(row["last_step_labels"]),
                    "path": row["path"],
                }
            )

        levels.append({"depth": level, "targets": rows})
        frontier = {row["n"]: {"path": row["path"]} for row in rows}

    return {"levels": levels, "truncated": truncated}


def _dot_quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\"')


def _pathwise_dot(n: int, depth: int, max_nodes: int | None = None) -> str:
    nodes: dict[int, int] = {n: shape_signature_dict(n)["generator"]}
    edge_labels: dict[tuple[int, int], set[str]] = {}
    frontier = {n}
    seen_nodes = {n}
    truncated = False

    if depth > 1:
        for _level in range(1, depth + 1):
            next_frontier: set[int] = set()

            for source_n in sorted(frontier):
                for edge in _pathwise_edges_for_number(source_n):
                    target_n = edge["target_n"]
                    target_g = edge["target_generator"]
                    label = edge["label"]

                    if target_n not in seen_nodes:
                        if max_nodes is not None and len(seen_nodes) >= max_nodes:
                            truncated = True
                            continue
                        seen_nodes.add(target_n)
                        nodes[target_n] = target_g

                    if target_n in nodes:
                        edge_labels.setdefault((source_n, target_n), set()).add(label)
                        next_frontier.add(target_n)

            if not next_frontier:
                break

            frontier = next_frontier

    lines = [
        "digraph pet_explain {",
        "  rankdir=LR;",
        '  node [shape=box];',
    ]

    if truncated:
        lines.append('  truncated_note [shape=note,label="truncated by --max-nodes"];')

    for node_n in sorted(nodes):
        node_id = f"n_{node_n}"
        node_label = f"N={node_n}\\ng={nodes[node_n]}"
        extra = " style=bold" if node_n == n else ""
        lines.append(f'  {node_id} [label="{_dot_quote(node_label)}"{extra}];')

    for (src, dst) in sorted(edge_labels):
        labels = sorted(edge_labels[(src, dst)])
        edge_label = " / ".join(labels)
        lines.append(
            f'  n_{src} -> n_{dst} [label="{_dot_quote(edge_label)}"];'
        )

    lines.append("}")
    return "\n".join(lines)



def _explain_data(
    n: int,
    pathwise_depth: int = 1,
    max_nodes: int | None = None,
) -> dict:
    tree = encode(n)
    factors = prime_factorization(n)
    signature = shape_signature_dict(n)
    metrics = metrics_dict(tree)

    return {
        "n": n,
        "pathwise_depth": pathwise_depth,
        "factorization": [{"prime": p, "exponent": e} for p, e in factors],
        "factorization_str": _format_factorization(factors),
        "generator": signature["generator"],
        "already_minimal": signature["already_minimal"],
        "child_generators": signature["child_generators"],
        "signature": signature["signature"],
        "metrics": metrics,
        "moves": _explain_moves(n),
        "max_nodes": max_nodes,
        "pathwise_neighborhood": _pathwise_neighborhood(
            n,
            pathwise_depth,
            max_nodes=max_nodes,
        ),
    }


def _factor_exp(n: int, prime: int) -> int:
    for p, exp in prime_factorization(n):
        if p == prime:
            return exp
    return 0


def _read_int_from_bytes_file(path_str: str, *, byteorder: str, signed: bool) -> dict:
    data = pathlib.Path(path_str).read_bytes()
    value = int.from_bytes(data, byteorder=byteorder, signed=signed)
    return {
        "file": path_str,
        "byteorder": byteorder,
        "signed": signed,
        "byte_count": len(data),
        "hex": data.hex(),
        "int": value,
    }


def _factor_exp_map(n: int) -> dict[int, int]:
    return dict(prime_factorization(n))




def _branch_move_rows(n: int, *, include_generators: bool = True) -> list[dict]:
    factors = prime_factorization(n)
    factor_map = dict(factors)

    def target_generator_for(value: int):
        return shape_signature_dict(value)["generator"] if include_generators else None

    rows: list[dict] = []

    new_prime = _next_new_prime(set(factor_map))
    new_n = n * new_prime
    rows.append(
        {
            "label": f"NEW(p={new_prime})",
            "source_n": n,
            "target_n": new_n,
            "target_generator": target_generator_for(new_n),
            "prime": new_prime,
            "kind": "NEW",
        }
    )

    for prime, exp in factors:
        inc_n = n * prime
        rows.append(
            {
                "label": f"INC(p={prime},e={exp})",
                "source_n": n,
                "target_n": inc_n,
                "target_generator": target_generator_for(inc_n),
                "representative_prime": prime,
                "exponent": exp,
                "kind": "INC",
            }
        )

        if exp > 1:
            dec_n = n // prime
            rows.append(
                {
                    "label": f"DEC(p={prime},e={exp})",
                    "source_n": n,
                    "target_n": dec_n,
                    "target_generator": target_generator_for(dec_n),
                    "representative_prime": prime,
                    "exponent": exp,
                    "kind": "DEC",
                }
            )

    leaf_primes = [prime for prime, exp in factors if exp == 1]
    if len(factors) > 1 and leaf_primes:
        drop_prime = min(leaf_primes)
        drop_n = n // drop_prime
        rows.append(
            {
                "label": f"DROP(p={drop_prime})",
                "source_n": n,
                "target_n": drop_n,
                "target_generator": target_generator_for(drop_n),
                "representative_prime": drop_prime,
                "kind": "DROP",
            }
        )

    return rows

def _plan_move_rank(label: str) -> tuple[int, str]:
    if label.startswith("NEW("):
        return (0, label)
    if label.startswith("DROP("):
        return (1, label)
    if label.startswith("INC("):
        return (2, label)
    if label.startswith("DEC("):
        return (3, label)
    return (4, label)


def _sorted_plan_neighbors(n: int) -> list[dict]:
    rows = _branch_move_rows(n, include_generators=False)
    return sorted(
        rows,
        key=lambda row: (_plan_move_rank(row["label"]), row["target_n"], row["label"]),
    )


def _plan_neighbors(n: int) -> list[dict]:
    return _sorted_plan_neighbors(n)

def _load_shape_algebra_module():
    import importlib
    import importlib.util
    import sys
    from pathlib import Path

    try:
        return importlib.import_module("pet_shape_algebra")
    except Exception:
        pass

    path = Path(__file__).resolve().parents[2] / "tools" / "pet_shape_algebra.py"
    if not path.exists():
        raise RuntimeError(f"cannot locate pet_shape_algebra module at {path}")
    spec = importlib.util.spec_from_file_location("pet_shape_algebra", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load pet_shape_algebra module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("pet_shape_algebra", module)
    spec.loader.exec_module(module)
    return module


def _shape_to_json_payload(shape):
    return [_shape_to_json_payload(child) for child in shape]


def _pet_tree_to_json_payload(tree):
    return [{"p": int(p), "e": None if exp is None else _pet_tree_to_json_payload(exp)} for p, exp in tree]


def _shape_height_local(shape) -> int:
    if not shape:
        return 0
    return 1 + max((_shape_height_local(child) for child in shape), default=0)


def _shape_key_local(shape):
    return (len(shape), tuple((_shape_key_local(child) for child in shape)))


def _run_shape_enumerate(args: argparse.Namespace) -> int:
    import json

    if args.max_mass < 1:
        raise SystemExit("--max-mass must be >= 1")
    if args.limit is not None and args.limit < 1:
        raise SystemExit("--limit must be >= 1")

    mod = _load_shape_algebra_module()
    shapes = tuple(mod.partial_shape_completion_frontier(None, args.max_mass))
    shapes = tuple(sorted(shapes, key=lambda s: (-_shape_height_local(s), len(s), _shape_key_local(s))))
    if args.limit is not None:
        shapes = shapes[: args.limit]

    if args.json:
        rows = []
        for shape in shapes:
            row = {
                "mass": mod.shape_mass(shape),
                "height": _shape_height_local(shape),
                "root_width": len(shape),
                "shape": _shape_to_json_payload(shape),
            }
            if args.with_gamma:
                row["gamma"] = mod.shape_gamma(shape)
            if args.with_pet:
                row["pet"] = _pet_tree_to_json_payload(mod.shape_to_pet(shape))
            rows.append(row)
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0

    for i, shape in enumerate(shapes, start=1):
        print(f"shape {i}")
        print(f"mass: {mod.shape_mass(shape)}")
        print(f"height: {_shape_height_local(shape)}")
        print(f"root_width: {len(shape)}")
        if args.with_gamma:
            print(f"gamma: {mod.shape_gamma(shape)}")
        print(f"shape: {json.dumps(_shape_to_json_payload(shape), ensure_ascii=False)}")
        if args.with_pet:
            print(f"pet: {json.dumps(_pet_tree_to_json_payload(mod.shape_to_pet(shape)), ensure_ascii=False)}")
        if i != len(shapes):
            print()
    return 0


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        prog="pet",
        description="PET — Prime Exponent Tree encoder/decoder",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    # encode
    p_encode = subparsers.add_parser("encode", help="encode N as PET")
    p_encode.add_argument("n", type=int, metavar="N")
    p_encode.add_argument("--json", action="store_true")

    # decode
    p_decode = subparsers.add_parser("decode", help="decode a PET JSON file back to N")
    p_decode.add_argument("file", metavar="FILE.json")

    # render
    p_render = subparsers.add_parser("render", help="render a PET JSON file as tree")
    p_render.add_argument("file", metavar="FILE.json")

    # validate
    p_validate = subparsers.add_parser("validate", help="validate a PET JSON file")
    p_validate.add_argument("file", metavar="FILE.json")

    # generator
    p_generator = subparsers.add_parser(
        "generator",
        help="print the smallest integer having the same PET structural shape as N",
    )
    p_generator.add_argument("n", type=int, metavar="N")

    # backbone-cache
    p_backbone_cache = subparsers.add_parser(
        "backbone-cache",
        help="build or inspect persistent PET backbone prime cache",
    )
    backbone_cache_subparsers = p_backbone_cache.add_subparsers(
        dest="backbone_cache_command",
        metavar="COMMAND",
    )
    backbone_cache_subparsers.required = True

    p_backbone_cache_build = backbone_cache_subparsers.add_parser(
        "build",
        help="build persistent PET backbone prime cache up to a limit",
    )
    p_backbone_cache_build.add_argument("--limit", type=int, required=True)
    p_backbone_cache_build.add_argument("--json", action="store_true")

    p_backbone_cache_inspect = backbone_cache_subparsers.add_parser(
        "inspect",
        help="inspect persistent PET backbone prime cache for a requested limit",
    )
    p_backbone_cache_inspect.add_argument("--limit", type=int, required=True)
    p_backbone_cache_inspect.add_argument("--json", action="store_true")

    # opaque-probe
    p_opaque_probe = subparsers.add_parser(
        "opaque-probe",
        help="extract small known factors and report an opaque residual",
    )
    p_opaque_probe.add_argument("n", type=int, metavar="N")
    p_opaque_probe.add_argument("--trial-limit", type=int, default=1000)
    p_opaque_probe.add_argument("--json", action="store_true")
    p_opaque_probe.add_argument("--summary", action="store_true")

    # opaque-resume
    p_opaque_resume = subparsers.add_parser(
        "opaque-resume",
        help="start or continue resumable bounded factor peeling",
    )
    opaque_resume_subparsers = p_opaque_resume.add_subparsers(
        dest="opaque_resume_command",
        metavar="COMMAND",
    )
    opaque_resume_subparsers.required = True

    p_opaque_resume_start = opaque_resume_subparsers.add_parser(
        "start",
        help="start a resumable opaque peeling state",
    )
    p_opaque_resume_start.add_argument("n", type=int, metavar="N")
    p_opaque_resume_start.add_argument("--trial-limit", type=int, required=True)
    p_opaque_resume_start.add_argument("--state", required=True)
    p_opaque_resume_start.add_argument("--json", action="store_true")
    p_opaque_resume_start.add_argument("--summary", action="store_true")

    p_opaque_resume_continue = opaque_resume_subparsers.add_parser(
        "continue",
        help="continue a resumable opaque peeling state",
    )
    p_opaque_resume_continue.add_argument("--trial-limit", type=int, required=True)
    p_opaque_resume_continue.add_argument("--state", required=True)
    p_opaque_resume_continue.add_argument("--json", action="store_true")
    p_opaque_resume_continue.add_argument("--summary", action="store_true")

    # opaque-profile
    p_opaque_profile = subparsers.add_parser(
        "opaque-profile",
        help="profile opaque residuals across multiple trial limits",
    )
    p_opaque_profile.add_argument("n", type=int, metavar="N")
    p_opaque_profile.add_argument("--limits", required=True)
    p_opaque_profile.add_argument("--json", action="store_true")

    # opaque-window-plan
    p_opaque_window_plan = subparsers.add_parser(
        "opaque-window-plan",
        help="plan a structural candidate factor window for an opaque N",
    )
    p_opaque_window_plan.add_argument("n", type=int, metavar="N")
    p_opaque_window_plan.add_argument(
        "--policy",
        choices=["balanced-semiprime"],
        default="balanced-semiprime",
    )
    p_opaque_window_plan.add_argument("--json", action="store_true")

    # opaque-window-probe
    p_opaque_window_probe = subparsers.add_parser(
        "opaque-window-probe",
        help="probe an opaque N using backbone prime candidates inside a bounded window",
    )
    p_opaque_window_probe.add_argument("n", type=int, metavar="N")
    p_opaque_window_probe.add_argument("--start", type=int)
    p_opaque_window_probe.add_argument("--end", type=int)
    p_opaque_window_probe.add_argument(
        "--around-sqrt",
        action="store_true",
        help="probe a bounded window centered around floor(sqrt(N))",
    )
    p_opaque_window_probe.add_argument("--radius", type=int, default=1000)
    p_opaque_window_probe.add_argument(
        "--candidate-strategy",
        choices=["backbone", "scan"],
        default="backbone",
    )
    p_opaque_window_probe.add_argument("--json", action="store_true")
    p_opaque_window_probe.add_argument("--summary", action="store_true")

    # opaque-window-resume
    p_opaque_window_resume = subparsers.add_parser(
        "opaque-window-resume",
        help="start or continue resumable bounded backbone-window probing",
    )
    opaque_window_resume_subparsers = p_opaque_window_resume.add_subparsers(
        dest="opaque_window_resume_command",
        metavar="COMMAND",
    )
    opaque_window_resume_subparsers.required = True

    p_opaque_window_resume_start = opaque_window_resume_subparsers.add_parser(
        "start",
        help="start a resumable opaque window probing state",
    )
    p_opaque_window_resume_start.add_argument("n", type=int, metavar="N")
    p_opaque_window_resume_start.add_argument("--start", type=int, required=True)
    p_opaque_window_resume_start.add_argument("--end", type=int, required=True)
    p_opaque_window_resume_start.add_argument("--state", required=True)
    p_opaque_window_resume_start.add_argument("--json", action="store_true")

    p_opaque_window_resume_continue = opaque_window_resume_subparsers.add_parser(
        "continue",
        help="continue a resumable opaque window probing state",
    )
    p_opaque_window_resume_continue.add_argument("--end", type=int, required=True)
    p_opaque_window_resume_continue.add_argument("--state", required=True)
    p_opaque_window_resume_continue.add_argument("--json", action="store_true")

    # opaque-state
    p_opaque_state = subparsers.add_parser(
        "opaque-state",
        help="summarize opaque analysis state files",
    )
    opaque_state_subparsers = p_opaque_state.add_subparsers(
        dest="opaque_state_command",
        metavar="COMMAND",
    )
    opaque_state_subparsers.required = True

    p_opaque_state_summarize = opaque_state_subparsers.add_parser(
        "summarize",
        help="summarize an opaque analysis state file",
    )
    p_opaque_state_summarize.add_argument("state", metavar="STATE.json")
    p_opaque_state_summarize.add_argument("--json", action="store_true")

    # opaque-report
    p_opaque_report = subparsers.add_parser(
        "opaque-report",
        help="print a monkey-friendly bounded opaque analysis report",
    )
    p_opaque_report.add_argument("n", type=int, metavar="N")
    p_opaque_report.add_argument("--trial-limit", type=int)
    p_opaque_report.add_argument("--window-start", type=int)
    p_opaque_report.add_argument("--window-end", type=int)
    p_opaque_report.add_argument("--json", action="store_true")

    # opaque-shape-families
    p_opaque_shape_families = subparsers.add_parser(
        "opaque-shape-families",
        help="describe PET shape-family constraints for an opaque projection",
    )
    p_opaque_shape_families.add_argument("n", type=int, metavar="N")
    p_opaque_shape_families.add_argument(
        "--max-generator-count",
        type=int,
        default=20,
    )
    p_opaque_shape_families.add_argument(
        "--max-exponent",
        type=int,
        default=20,
    )
    p_opaque_shape_families.add_argument(
        "--excluded-support-limit",
        type=int,
    )
    p_opaque_shape_families.add_argument("--json", action="store_true")


    # opaque-shape-rank
    p_opaque_shape_rank = subparsers.add_parser(
        "opaque-shape-rank",
        help="rank PET shape-family hypotheses against an excluded backbone range",
    )
    p_opaque_shape_rank.add_argument("n", type=int, metavar="N")
    p_opaque_shape_rank.add_argument(
        "--max-generator-count",
        type=int,
        default=20,
    )
    p_opaque_shape_rank.add_argument(
        "--excluded-support-limit",
        type=int,
        required=True,
    )
    p_opaque_shape_rank.add_argument("--json", action="store_true")

    # opaque-mass-centers
    p_opaque_mass_centers = subparsers.add_parser(
        "opaque-mass-centers",
        help="analyze informative PET mass centers against an excluded backbone range",
    )
    p_opaque_mass_centers.add_argument("n", type=int, metavar="N")
    p_opaque_mass_centers.add_argument(
        "--max-generator-count",
        type=int,
        default=20,
    )
    p_opaque_mass_centers.add_argument(
        "--excluded-support-limit",
        type=int,
        required=True,
    )
    p_opaque_mass_centers.add_argument("--json", action="store_true")

    # opaque-mass-response
    p_opaque_mass_response = subparsers.add_parser(
        "opaque-mass-response",
        help="find reactive PET mass-center frontiers under symbolic NEW/DROP moves",
    )
    p_opaque_mass_response.add_argument("n", type=int, metavar="N")
    p_opaque_mass_response.add_argument(
        "--max-generator-count",
        type=int,
        default=30,
    )
    p_opaque_mass_response.add_argument(
        "--excluded-support-limit",
        type=int,
        required=True,
    )
    p_opaque_mass_response.add_argument(
        "--max-move-span",
        type=int,
        default=1,
    )
    p_opaque_mass_response.add_argument(
        "--bands",
        action="store_true",
        help="print grouped magnetic bands for response hotspots",
    )
    p_opaque_mass_response.add_argument("--json", action="store_true")


    # opaque-focused-peel
    p_opaque_focused_peel = subparsers.add_parser(
        "opaque-focused-peel",
        help="select a focused PET peel lens from opaque mass-response magnetic bands",
    )
    p_opaque_focused_peel.add_argument("n", type=int, metavar="N")
    p_opaque_focused_peel.add_argument(
        "--max-generator-count",
        type=int,
        default=40,
    )
    p_opaque_focused_peel.add_argument(
        "--excluded-support-limit",
        type=int,
        required=True,
    )
    p_opaque_focused_peel.add_argument(
        "--max-move-span",
        type=int,
        default=5,
    )
    p_opaque_focused_peel.add_argument("--kind")
    p_opaque_focused_peel.add_argument(
        "--move",
        choices=["NEW", "DROP", "new", "drop"],
    )
    p_opaque_focused_peel.add_argument(
        "--cut",
        action="store_true",
        help="incise the selected magnetic band into local PET peel layers",
    )
    p_opaque_focused_peel.add_argument(
        "--peel-step",
        action="store_true",
        help="select the next PET structural layer to peel from the focused cut",
    )
    p_opaque_focused_peel.add_argument(
        "--slice",
        action="store_true",
        help="partition local PET shape-space across the selected peel boundary",
    )
    p_opaque_focused_peel.add_argument(
        "--lift",
        action="store_true",
        help="lift the retained partition and expose its visible PET form",
    )
    p_opaque_focused_peel.add_argument(
        "--decode",
        action="store_true",
        help="decode the lifted visible PET form into local structural constraints",
    )
    p_opaque_focused_peel.add_argument(
        "--center-lens",
        action="store_true",
        help="build the next PET-local lens from the decoded projected center shape",
    )
    p_opaque_focused_peel.add_argument(
        "--realize",
        action="store_true",
        help="materialize the projected center through canonical PET encode/decode",
    )
    p_opaque_focused_peel.add_argument(
        "--classic-handoff",
        action="store_true",
        help="use the realized PET center as an explicit classic divisibility anchor",
    )
    p_opaque_focused_peel.add_argument(
        "--fork",
        action="store_true",
        help="open multi-threshold bands into explicit NEW/DROP peel branches",
    )
    p_opaque_focused_peel.add_argument(
        "--fork-follow",
        choices=["NEW", "DROP"],
        help="propose a follow-up lens for a selected multi-threshold fork branch",
    )
    p_opaque_focused_peel.add_argument(
        "--handoff-radius",
        type=int,
        default=5,
        help="radius around the realized center for classic handoff scans",
    )
    p_opaque_focused_peel.add_argument("--json", action="store_true")

    # opaque-recursive-lens
    p_opaque_recursive_lens = subparsers.add_parser(
        "opaque-recursive-lens",
        help="recursively zoom into PET-local lenses suggested by decoded center forms",
    )
    p_opaque_recursive_lens.add_argument("n", type=int, metavar="N")
    p_opaque_recursive_lens.add_argument(
        "--excluded-support-limit",
        type=int,
        required=True,
    )
    p_opaque_recursive_lens.add_argument(
        "--max-generator-count",
        type=int,
        default=40,
    )
    p_opaque_recursive_lens.add_argument(
        "--max-move-span",
        type=int,
        default=5,
    )
    p_opaque_recursive_lens.add_argument(
        "--depth",
        type=int,
        default=3,
    )
    p_opaque_recursive_lens.add_argument(
        "--terminal-reduction",
        action="store_true",
    )
    p_opaque_recursive_lens.add_argument(
        "--branch-recursion",
        choices=["NEW", "DROP"],
        help="continue recursive zoom through a selected fork-follow branch when center lens is unavailable",
    )
    p_opaque_recursive_lens.add_argument(
        "--anchor-field",
        action="store_true",
        help="evaluate whether the recursive edge_k=2 form creates a PET-side anchor field",
    )
    p_opaque_recursive_lens.add_argument(
        "--composite-edge-peel",
        action="store_true",
        help="decompose stable composite recursive edge_k values as PET-side symbolic subedges",
    )
    p_opaque_recursive_lens.add_argument(
        "--diagnostic-classic-probe",
        action="store_true",
        help="run a bounded diagnostic classic probe from PET diagnostic-only anchors",
    )
    p_opaque_recursive_lens.add_argument(
        "--classic-handoff",
        action="store_true",
        help="use the recursive center lens as a classic divisibility anchor",
    )
    p_opaque_recursive_lens.add_argument(
        "--handoff-radius",
        type=int,
        default=5,
        help="radius around the recursive center for classic handoff scans",
    )
    p_opaque_recursive_lens.add_argument("--json", action="store_true")

    # opaque-benchmark
    p_opaque_benchmark = subparsers.add_parser(
        "opaque-benchmark",
        help="benchmark bounded opaque analysis commands",
    )
    opaque_benchmark_subparsers = p_opaque_benchmark.add_subparsers(
        dest="opaque_benchmark_command",
        metavar="COMMAND",
    )
    opaque_benchmark_subparsers.required = True

    p_opaque_benchmark_probe = opaque_benchmark_subparsers.add_parser(
        "probe",
        help="benchmark opaque-probe",
    )
    p_opaque_benchmark_probe.add_argument("n", type=int, metavar="N")
    p_opaque_benchmark_probe.add_argument("--trial-limit", type=int, required=True)
    p_opaque_benchmark_probe.add_argument("--json", action="store_true")

    p_opaque_benchmark_resume = opaque_benchmark_subparsers.add_parser(
        "resume",
        help="benchmark opaque-resume continue",
    )
    p_opaque_benchmark_resume.add_argument("--trial-limit", type=int, required=True)
    p_opaque_benchmark_resume.add_argument("--state", required=True)
    p_opaque_benchmark_resume.add_argument("--json", action="store_true")

    # opaque-synthetic-profile
    p_opaque_synthetic_profile = subparsers.add_parser(
        "opaque-synthetic-profile",
        help="generate a synthetic opaque N and profile bounded residual peeling",
    )
    p_opaque_synthetic_profile.add_argument("--target-digits", type=int, required=True)
    p_opaque_synthetic_profile.add_argument("--start-prime", type=int, default=1_000_000)
    p_opaque_synthetic_profile.add_argument("--base", type=int, default=72)
    p_opaque_synthetic_profile.add_argument("--full-fry", action="store_true")
    p_opaque_synthetic_profile.add_argument("--json", action="store_true")

    # signature
    p_signature = subparsers.add_parser(
        "signature",
        help="print the canonical structural signature of the PET shape class of N",
    )
    p_signature.add_argument("n", type=int, metavar="N")
    p_signature.add_argument("--json", action="store_true")

    # compare
    p_compare = subparsers.add_parser(
        "compare",
        help="compare two integers via PET distance and structural distance",
    )
    p_compare.add_argument("n1", type=int, metavar="N1")
    p_compare.add_argument("n2", type=int, metavar="N2")
    p_compare.add_argument("--json", action="store_true")

    # classify
    p_classify = subparsers.add_parser(
        "classify",
        help="classify one integer via PET-derived structural predicates",
    )
    p_classify.add_argument("n", type=int, metavar="N")
    p_classify.add_argument("--json", action="store_true")

    # metrics
    p_metrics = subparsers.add_parser("metrics", help="print structural metrics for N")
    p_metrics.add_argument("n", type=int, metavar="N")
    p_metrics.add_argument("--json", action="store_true")

    # extended metrics
    p_xmetrics = subparsers.add_parser(
        "xmetrics",
        help="print extended/research metrics for N",
    )
    p_xmetrics.add_argument("n", type=int, metavar="N")
    p_xmetrics.add_argument("--json", action="store_true")

    # explain
    p_explain = subparsers.add_parser(
        "explain",
        help="explain N as PET building blocks and immediate rewrite moves",
    )
    p_explain.add_argument("n", type=int, metavar="N")
    p_explain.add_argument(
        "--pathwise-depth",
        type=int,
        default=1,
        help="pathwise neighborhood depth (default: 1)",
    )
    p_explain.add_argument(
        "--depth",
        dest="pathwise_depth",
        type=int,
        help=argparse.SUPPRESS,
    )
    p_explain.add_argument(
        "--dot",
        action="store_true",
        help="print the pathwise neighborhood as Graphviz DOT",
    )
    p_explain.add_argument(
        "--max-nodes",
        type=int,
        default=None,
        help="cap the total number of pathwise neighborhood nodes",
    )
    p_explain.add_argument("--json", action="store_true")

    # scan
    p_scan = subparsers.add_parser("scan", help="scan range and output JSONL dataset")
    p_scan.add_argument("start", type=int)
    p_scan.add_argument("end", type=int)
    p_scan.add_argument("--jsonl", required=True)

    # atlas
    p_atlas = subparsers.add_parser(
        "atlas",
        help="compute atlas statistics for a PET dataset",
    )
    p_atlas.add_argument("file", metavar="DATASET.jsonl")

    # shape generators
    p_generators = subparsers.add_parser(
        "shape-generators",
        help="print the first integer generating each PET structural shape",
    )
    p_generators.add_argument("file", metavar="DATASET.jsonl")
    p_generators.add_argument("--metrics", action="store_true")


    # shape-of
    p_shape_of = subparsers.add_parser(
        "shape-of",
        help="print the canonical PET shape of N",
    )
    p_shape_of.add_argument("n", type=int, metavar="N")
    p_shape_of.add_argument("--json", action="store_true")

    # shape-enumerate
    p_shape_enumerate = subparsers.add_parser(
        "shape-enumerate",
        help="enumerate exact shapes in canonical shape-first order",
    )
    p_shape_enumerate.add_argument(
        "--max-mass",
        type=int,
        required=True,
        help="maximum structural mass to enumerate",
    )
    p_shape_enumerate.add_argument(
        "--limit",
        type=int,
        help="limit number of emitted shapes after canonical sorting",
    )
    p_shape_enumerate.add_argument(
        "--json",
        action="store_true",
        help="emit JSON array instead of text output",
    )
    p_shape_enumerate.add_argument(
        "--with-pet",
        action="store_true",
        help="include the minimal PET witness for each shape",
    )
    p_shape_enumerate.add_argument(
        "--with-gamma",
        action="store_true",
        help="include gamma (can grow extremely fast for height-first shapes)",
    )

    # partial-shape-report
    p_partial_shape_report = subparsers.add_parser(
        "partial-shape-report",
        help=argparse.SUPPRESS,
    )
    p_partial_shape_report.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_report.add_argument(
        "--max-mass",
        type=int,
        default=3,
        help="maximum structural mass for bounded completion frontier (default: 3)",
    )
    p_partial_shape_report.add_argument(
        "--preview",
        type=int,
        default=5,
        help="how many exact completions to preview (default: 5)",
    )
    p_partial_shape_report.add_argument("--json", action="store_true")
    _hide_subparser(subparsers, "partial-shape-report")


    # partial-shape-match
    p_partial_shape_match = subparsers.add_parser(
        "partial-shape-match",
        help="check whether N matches a given partial PET shape",
    )
    p_partial_shape_match.add_argument("n", type=int, metavar="N")
    p_partial_shape_match.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_match.add_argument("--json", action="store_true")


    # partial-shape-witness
    p_partial_shape_witness = subparsers.add_parser(
        "partial-shape-witness",
        help=argparse.SUPPRESS,
    )
    p_partial_shape_witness.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_witness.add_argument("--json", action="store_true")
    _hide_subparser(subparsers, "partial-shape-witness")


    # partial-shape-completions
    p_partial_shape_completions = subparsers.add_parser(
        "partial-shape-completions",
        help=argparse.SUPPRESS,
    )
    p_partial_shape_completions.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_completions.add_argument(
        "--max-mass",
        type=int,
        default=3,
        help="maximum structural mass for bounded completion frontier (default: 3)",
    )
    p_partial_shape_completions.add_argument(
        "--preview",
        type=int,
        default=20,
        help="how many completions to print (default: 20)",
    )
    p_partial_shape_completions.add_argument("--json", action="store_true")
    _hide_subparser(subparsers, "partial-shape-completions")


    # partial-shape-forced-core
    p_partial_shape_forced_core = subparsers.add_parser(
        "partial-shape-forced-core",
        help="compute the bounded forced core shared by exact completions of a partial PET shape",
    )
    p_partial_shape_forced_core.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_forced_core.add_argument(
        "--max-mass",
        type=int,
        default=3,
        help="maximum structural mass for bounded completion frontier (default: 3)",
    )
    p_partial_shape_forced_core.add_argument(
        "--trace",
        action="store_true",
        help="show the cumulative forced-core trace for each bound up to --max-mass",
    )
    p_partial_shape_forced_core.add_argument(
        "--window",
        type=int,
        default=1,
        help="require an observed stabilization window of at least this many masses (default: 1)",
    )
    p_partial_shape_forced_core.add_argument(
        "--auto-window",
        type=int,
        default=None,
        help="auto-increase the inspected bound until the observed stable window reaches this size",
    )
    p_partial_shape_forced_core.add_argument(
        "--max-mass-cap",
        type=int,
        default=12,
        help="upper cap used together with --auto-window (default: 12)",
    )
    p_partial_shape_forced_core.add_argument("--json", action="store_true")


    # partial-shape-residual
    p_partial_shape_residual = subparsers.add_parser(
        "partial-shape-residual",
        help=argparse.SUPPRESS,
    )
    p_partial_shape_residual.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_residual.add_argument(
        "--max-mass",
        type=int,
        default=3,
        help="maximum structural mass for bounded forced-core analysis (default: 3)",
    )
    p_partial_shape_residual.add_argument(
        "--auto-window",
        type=int,
        default=None,
        help="auto-increase the inspected bound until the observed stable window reaches this size",
    )
    p_partial_shape_residual.add_argument(
        "--max-mass-cap",
        type=int,
        default=12,
        help="upper cap used together with --auto-window (default: 12)",
    )
    p_partial_shape_residual.add_argument("--json", action="store_true")
    _hide_subparser(subparsers, "partial-shape-residual")


    # partial-shape-residual-profile
    p_partial_shape_residual_profile = subparsers.add_parser(
        "partial-shape-residual-profile",
        help=argparse.SUPPRESS,
    )
    p_partial_shape_residual_profile.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_residual_profile.add_argument(
        "--max-mass",
        type=int,
        default=3,
        help="maximum structural mass for bounded residual profiling (default: 3)",
    )
    p_partial_shape_residual_profile.add_argument(
        "--preview",
        type=int,
        default=5,
        help="how many local shapes/gammas to preview per free path (default: 5)",
    )
    p_partial_shape_residual_profile.add_argument(
        "--auto-window",
        type=int,
        default=None,
        help="auto-increase the inspected bound until the observed stable window reaches this size",
    )
    p_partial_shape_residual_profile.add_argument(
        "--max-mass-cap",
        type=int,
        default=12,
        help="upper cap used together with --auto-window (default: 12)",
    )
    p_partial_shape_residual_profile.add_argument("--json", action="store_true")
    _hide_subparser(subparsers, "partial-shape-residual-profile")


    # partial-shape-residual-summary
    p_partial_shape_residual_summary = subparsers.add_parser(
        "partial-shape-residual-summary",
        help="print a compact canonical summary of forced core vs residual freedom",
    )
    p_partial_shape_residual_summary.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_residual_summary.add_argument(
        "--max-mass",
        type=int,
        default=3,
        help="maximum structural mass for bounded residual summary (default: 3)",
    )
    p_partial_shape_residual_summary.add_argument(
        "--preview",
        type=int,
        default=5,
        help="how many local shapes/gammas to preview per free path (default: 5)",
    )
    p_partial_shape_residual_summary.add_argument(
        "--fast-preview",
        action="store_true",
        help="skip expensive exact local-forced-core computation and only show preview shapes/gammas",
    )
    p_partial_shape_residual_summary.add_argument(
        "--auto-window",
        type=int,
        default=None,
        help="auto-increase the inspected bound until the observed stable window reaches this size",
    )
    p_partial_shape_residual_summary.add_argument(
        "--max-mass-cap",
        type=int,
        default=12,
        help="upper cap used together with --auto-window (default: 12)",
    )
    p_partial_shape_residual_summary.add_argument("--json", action="store_true")


    # partial-shape-target
    p_partial_shape_target = subparsers.add_parser(
        "partial-shape-target",
        help="print the observed compatible decomposition: core + residual freedom",
    )
    p_partial_shape_target.add_argument("partial", metavar="PARTIAL_SHAPE")
    p_partial_shape_target.add_argument(
        "--max-mass",
        type=int,
        default=3,
        help="maximum structural mass for bounded observed decomposition (default: 3)",
    )
    p_partial_shape_target.add_argument(
        "--preview",
        type=int,
        default=5,
        help="how many local shapes/gammas to preview per free path (default: 5)",
    )
    p_partial_shape_target.add_argument(
        "--auto-window",
        type=int,
        default=None,
        help="auto-increase the inspected bound until the observed stable window reaches this size",
    )
    p_partial_shape_target.add_argument(
        "--max-mass-cap",
        type=int,
        default=12,
        help="upper cap used together with --auto-window (default: 12)",
    )
    p_partial_shape_target.add_argument(
        "--fast-preview",
        action="store_true",
        help="skip expensive exact local-forced-core computation and only show preview shapes/gammas",
    )
    p_partial_shape_target.add_argument("--json", action="store_true")


    # int-from-bytes
    p_int_from_bytes = subparsers.add_parser(
        "int-from-bytes",
        help="read a byte stream file and interpret it as an integer",
    )
    p_int_from_bytes.add_argument("file", metavar="BYTES.bin")
    p_int_from_bytes.add_argument(
        "--byteorder",
        choices=("big", "little"),
        default="big",
        help="byte order used to decode the integer (default: big)",
    )
    p_int_from_bytes.add_argument(
        "--signed",
        action="store_true",
        help="interpret the byte stream as a signed integer",
    )
    p_int_from_bytes.add_argument("--json", action="store_true")


    # branch-neighbors
    p_branch_neighbors = subparsers.add_parser(
        "branch-neighbors",
        help="show canonical deterministic PET branch moves from N",
    )
    p_branch_neighbors.add_argument("n", type=int, metavar="N")
    p_branch_neighbors.add_argument("--json", action="store_true")

    # rewrite
    p_rewrite = subparsers.add_parser(
        "rewrite",
        help="PET-METICA rewrite distance, scans, and pairwise matrices",
    )
    rewrite_subparsers = p_rewrite.add_subparsers(
        dest="rewrite_command",
        metavar="REWRITE_COMMAND",
    )
    rewrite_subparsers.required = True

    p_rewrite_pair = rewrite_subparsers.add_parser(
        "pair",
        help="compute canonical rewrite difference between two numbers",
    )
    p_rewrite_pair.add_argument("src", type=int, metavar="SRC")
    p_rewrite_pair.add_argument("dst", type=int, metavar="DST")
    p_rewrite_pair.add_argument("--overscan", type=int, default=90)
    p_rewrite_pair.add_argument("--json", action="store_true")
    p_rewrite_pair.add_argument("--explain", action="store_true")

    p_rewrite_explain = rewrite_subparsers.add_parser(
        "explain",
        help="explain a PET-METICA rewrite path between two numbers",
    )
    p_rewrite_explain.add_argument("src", type=int, metavar="SRC")
    p_rewrite_explain.add_argument("dst", type=int, metavar="DST")
    p_rewrite_explain.add_argument("--overscan", type=int, default=90)
    p_rewrite_explain.add_argument(
        "--target-aware",
        action="store_true",
        help="compute an explicit target-aware structural explanation",
    )
    p_rewrite_explain.add_argument("--json", action="store_true")

    p_rewrite_friction = rewrite_subparsers.add_parser(
        "friction",
        help="summarize one-step PET-METICA rewrite return costs",
    )
    p_rewrite_friction.add_argument("--n-max", type=int, default=30)
    p_rewrite_friction.add_argument("--overscan", type=int, default=90)
    p_rewrite_friction.add_argument("--limit", type=int, default=10)
    p_rewrite_friction.add_argument("--json", action="store_true")

    p_rewrite_scan = rewrite_subparsers.add_parser(
        "scan",
        help="global PET-METICA scan over 1..N with overscan",
    )
    p_rewrite_scan.add_argument("--n-max", type=int, default=30)
    p_rewrite_scan.add_argument("--overscan", type=int, default=90)
    p_rewrite_scan.add_argument("--limit", type=int, default=10)
    p_rewrite_scan.add_argument("--json", action="store_true")

    p_rewrite_matrix = rewrite_subparsers.add_parser(
        "matrix",
        help="emit all pair rewrite distances as JSON",
    )
    p_rewrite_matrix.add_argument("--n-max", type=int, default=30)
    p_rewrite_matrix.add_argument("--overscan", type=int, default=90)
    p_rewrite_matrix.add_argument("--json", action="store_true")

    # query / families
    register_query_subparser(subparsers)
    register_families_subparser(subparsers)

    args = parser.parse_args(argv[1:])

    try:
        if args.command == "encode":
            tree = encode(args.n)
            if args.json:
                print(to_json(tree))
            else:
                back = decode(tree)
                print(f"N = {args.n}")
                print(to_json(tree))
                print(f"decoded = {back}")

        elif args.command == "shape-enumerate":
            return _run_shape_enumerate(args)

        elif args.command == "decode":
            tree = load_json_file(args.file)
            print(decode(tree))

        elif args.command == "render":
            tree = load_json_file(args.file)
            print(render(tree))

        elif args.command == "validate":
            tree = load_json_file(args.file)
            validate(tree)
            print("OK")

        elif args.command == "generator":
            print(shape_generator(args.n))

        elif args.command == "backbone-cache":
            if args.backbone_cache_command == "build":
                data = _build_backbone_prime_cache(args.limit)
            elif args.backbone_cache_command == "inspect":
                data = _inspect_backbone_prime_cache(args.limit)
            else:
                raise ValueError("unsupported backbone-cache command")

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                if args.backbone_cache_command == "build":
                    print(f"cache_path = {data['cache_path']}")
                    print(f"limit = {data['limit']}")
                    print(f"prime_count = {data['prime_count']}")
                    print(f"first_prime = {data['first_prime']}")
                    print(f"last_prime = {data['last_prime']}")
                else:
                    print(f"cache_exists = {'yes' if data['cache_exists'] else 'no'}")
                    print(f"requested_limit = {data['requested_limit']}")
                    print(f"cache_path = {data['cache_path']}")
                    print(f"cache_limit = {data['cache_limit']}")
                    print(f"prime_count = {data['prime_count']}")
                    print(f"first_prime = {data['first_prime']}")
                    print(f"last_prime = {data['last_prime']}")

        elif args.command == "opaque-probe":
            data = _trial_division_partial(args.n, trial_limit=args.trial_limit)

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            elif args.summary:
                _print_opaque_summary(data)
            else:
                print(f"N = {data['n']}")
                print(f"digits = {data['digits']}")
                print(f"bit_length = {data['bit_length']}")
                print(f"trial_limit = {data['trial_limit']}")
                print(f"known_factorization = {data['known_factorization']}")
                print(f"opaque_residual = {data['opaque_residual']}")
                print(f"opaque_residual_digits = {data['opaque_residual_digits']}")
                print(f"opaque_residual_bit_length = {data['opaque_residual_bit_length']}")
                print(f"opaque_residual_status = {data['opaque_residual_status']}")
                print(f"fully_factored = {'yes' if data['fully_factored'] else 'no'}")
                print(f"claim = {data['claim']}")

        elif args.command == "opaque-resume":
            state_path = pathlib.Path(args.state)
            if args.opaque_resume_command == "start":
                data = _opaque_resume_start(
                    args.n,
                    trial_limit=args.trial_limit,
                    state_path=state_path,
                )
            elif args.opaque_resume_command == "continue":
                data = _opaque_resume_continue(
                    trial_limit=args.trial_limit,
                    state_path=state_path,
                )
            else:
                raise ValueError("unsupported opaque-resume command")

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            elif args.summary:
                _print_opaque_summary(data)
            else:
                _print_opaque_resume_state(data)

        elif args.command == "opaque-profile":
            limits = _parse_trial_limits(args.limits)
            data = _opaque_profile(args.n, limits=limits)

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N = {data['n']}")
                print(f"digits = {data['digits']}")
                print(f"bit_length = {data['bit_length']}")
                print("limit | known_count | residual_digits | residual_bits | status | fully")
                for row in data["rows"]:
                    print(
                        f"{row['trial_limit']} | "
                        f"{row['known_count']} | "
                        f"{row['opaque_residual_digits']} | "
                        f"{row['opaque_residual_bit_length']} | "
                        f"{row['opaque_residual_status']} | "
                        f"{str(row['fully_factored']).lower()}"
                    )
                print(f"claim = {data['claim']}")

        elif args.command == "opaque-window-plan":
            data = _opaque_window_plan(args.n, policy=args.policy)

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N = {data['n']}")
                print(f"digits = {data['digits']}")
                print(f"bit_length = {data['bit_length']}")
                print(f"policy = {data['policy']}")
                print(
                    "balanced_semiprime_candidate_factor_digits = "
                    f"{data['candidate_factor_digits']}"
                )
                print(
                    "decimal_window = "
                    f"[{data['decimal_window_low']}, {data['decimal_window_high']})"
                )
                print(
                    "secondary_decimal_window = "
                    f"[{data['secondary_decimal_window_low']}, "
                    f"{data['secondary_decimal_window_high']})"
                )
                print(f"claim = {data['claim']}")

        elif args.command == "opaque-window-probe":
            if args.around_sqrt:
                if args.radius < 0:
                    raise ValueError("--radius must be >= 0")
                center = math.isqrt(args.n)
                start = max(2, center - args.radius)
                end = center + args.radius
            else:
                if args.start is None or args.end is None:
                    raise ValueError("--start and --end are required unless --around-sqrt is used")
                start = args.start
                end = args.end

            data = _opaque_window_probe(
                args.n,
                start=start,
                end=end,
                candidate_strategy=args.candidate_strategy,
            )

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            elif args.summary:
                _print_opaque_summary(data, include_window=True)
            else:
                print(f"N = {data['n']}")
                print(f"digits = {data['digits']}")
                print(f"bit_length = {data['bit_length']}")
                print(f"window_start = {data['window_start']}")
                print(f"window_end = {data['window_end']}")
                print(f"candidate_strategy = {data['candidate_strategy']}")
                print(f"tested_prime_count = {data['tested_prime_count']}")
                print(f"known_factorization = {data['known_factorization']}")
                print(f"opaque_residual = {data['opaque_residual']}")
                print(f"opaque_residual_digits = {data['opaque_residual_digits']}")
                print(f"opaque_residual_bit_length = {data['opaque_residual_bit_length']}")
                print(f"opaque_residual_status = {data['opaque_residual_status']}")
                print(f"fully_factored = {'yes' if data['fully_factored'] else 'no'}")
                print(f"claim = {data['claim']}")

        elif args.command == "opaque-window-resume":
            state_path = pathlib.Path(args.state)
            if args.opaque_window_resume_command == "start":
                data = _opaque_window_resume_start(
                    args.n,
                    start=args.start,
                    end=args.end,
                    state_path=state_path,
                )
            elif args.opaque_window_resume_command == "continue":
                data = _opaque_window_resume_continue(
                    end=args.end,
                    state_path=state_path,
                )
            else:
                raise ValueError("unsupported opaque-window-resume command")

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                _print_opaque_window_resume_state(data)

        elif args.command == "opaque-state":
            if args.opaque_state_command == "summarize":
                data = _opaque_state_summary(pathlib.Path(args.state))
            else:
                raise ValueError("unsupported opaque-state command")

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                _print_opaque_state_summary(data)

        elif args.command == "opaque-report":
            data = _opaque_report(
                args.n,
                trial_limit=args.trial_limit,
                window_start=args.window_start,
                window_end=args.window_end,
            )

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                _print_opaque_report(data)

        elif args.command == "opaque-shape-families":
            data = _opaque_shape_families(
                args.n,
                max_generator_count=args.max_generator_count,
                max_exponent=args.max_exponent,
                excluded_support_limit=args.excluded_support_limit,
            )

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                _print_opaque_shape_families(data)


        elif args.command == "opaque-shape-rank":
            data = _opaque_shape_rank(
                args.n,
                max_generator_count=args.max_generator_count,
                excluded_support_limit=args.excluded_support_limit,
            )

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                _print_opaque_shape_rank(data)

        elif args.command == "opaque-mass-centers":
            data = _opaque_mass_centers(
                args.n,
                max_generator_count=args.max_generator_count,
                excluded_support_limit=args.excluded_support_limit,
            )

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                _print_opaque_mass_centers(data)

        elif args.command == "opaque-mass-response":
            data = _opaque_mass_response(
                args.n,
                max_generator_count=args.max_generator_count,
                excluded_support_limit=args.excluded_support_limit,
                max_move_span=args.max_move_span,
                include_bands=args.bands,
            )

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                _print_opaque_mass_response(data)


        elif args.command == "opaque-focused-peel":
            data = _opaque_focused_peel(
                args.n,
                max_generator_count=args.max_generator_count,
                excluded_support_limit=args.excluded_support_limit,
                max_move_span=args.max_move_span,
                kind=args.kind,
                move=args.move,
                cut=args.cut,
                peel_step=args.peel_step,
                slice_=args.slice,
                lift=args.lift,
                decode=args.decode,
                center_lens=args.center_lens,
                realize=args.realize,
                classic_handoff=args.classic_handoff,
                handoff_radius=args.handoff_radius,
                fork=args.fork,
                fork_follow=args.fork_follow,
            )

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                _print_opaque_focused_peel(data)

        elif args.command == "opaque-recursive-lens":
            data = _opaque_recursive_lens(
                args.n,
                excluded_support_limit=args.excluded_support_limit,
                max_generator_count=args.max_generator_count,
                max_move_span=args.max_move_span,
                depth=args.depth,
                terminal_reduction=args.terminal_reduction,
                branch_recursion=args.branch_recursion,
                classic_handoff=args.classic_handoff,
                handoff_radius=args.handoff_radius,
                anchor_field=args.anchor_field,
                composite_edge_peel=args.composite_edge_peel,
                diagnostic_classic_probe=args.diagnostic_classic_probe,
            )

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                _print_opaque_recursive_lens(data)

        elif args.command == "opaque-benchmark":
            if args.opaque_benchmark_command == "probe":
                data = _opaque_benchmark_probe(
                    args.n,
                    trial_limit=args.trial_limit,
                )
            elif args.opaque_benchmark_command == "resume":
                data = _opaque_benchmark_resume(
                    trial_limit=args.trial_limit,
                    state_path=pathlib.Path(args.state),
                )
            else:
                raise ValueError("unsupported opaque-benchmark command")

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                _print_opaque_benchmark(data)

        elif args.command == "opaque-synthetic-profile":
            data = _opaque_synthetic_profile(
                target_digits=args.target_digits,
                start_prime=args.start_prime,
                base=args.base,
                full_fry=args.full_fry,
            )

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"base = {data['base']}")
                print(f"target_digits = {data['target_digits']}")
                print(f"start_prime = {data['start_prime']}")
                print(f"full_fry = {'yes' if data['full_fry'] else 'no'}")
                print(f"prime_count = {data['prime_count']}")
                print(f"first_prime = {data['first_prime']}")
                print(f"last_prime = {data['last_prime']}")
                print(f"N_digits = {data['n_digits']}")
                print(f"N_bit_length = {data['n_bit_length']}")
                print("limits = " + ",".join(str(limit) for limit in data["limits"]))
                print()
                print("limit | known_count | residual_digits | residual_bits | status | fully")
                for row in data["rows"]:
                    print(
                        f"{row['trial_limit']} | "
                        f"{row['known_count']} | "
                        f"{row['opaque_residual_digits']} | "
                        f"{row['opaque_residual_bit_length']} | "
                        f"{row['opaque_residual_status']} | "
                        f"{str(row['fully_factored']).lower()}"
                    )
                print(f"claim = {data['claim']}")

        elif args.command == "signature":
            data = shape_signature_dict(args.n)

            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                print(f"generator = {data['generator']}")
                print(f"already_minimal = {data['already_minimal']}")
                print(f"child_generators = {data['child_generators']}")
                print(f"signature = {data['signature']}")

                def _list_to_tuple_shape(obj):
                    if isinstance(obj, list):
                        return tuple(_list_to_tuple_shape(child) for child in obj)
                    return obj

                print("shape:")
                shape = _list_to_tuple_shape(data["signature"])
                lines = draw_shape(shape, lines=[])
                for line in lines:
                    print(line)

        elif args.command == "compare":
            tree1 = encode(args.n1)
            tree2 = encode(args.n2)
            data = {
                "n1": args.n1,
                "n2": args.n2,
                "distance": distance(tree1, tree2),
                "structural_distance": structural_distance(tree1, tree2),
                "same_shape": structural_distance(tree1, tree2) == 0,
            }
            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N1 = {args.n1}")
                print(f"N2 = {args.n2}")
                for key, value in data.items():
                    if key in {"n1", "n2"}:
                        continue
                    print(f"{key} = {value}")

        elif args.command == "classify":
            tree = encode(args.n)
            data = {
                "n": args.n,
                "is_linear": is_linear(tree),
                "is_level_uniform": is_level_uniform(tree),
                "is_expanding": is_expanding(tree),
                "is_squarefree": is_squarefree(tree),
                "leaf_ratio": str(leaf_ratio(tree)),
                "profile_shape": profile_shape(tree),
            }
            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                for key, value in data.items():
                    if key == "n":
                        continue
                    print(f"{key} = {value}")

        elif args.command == "metrics":
            tree = encode(args.n)
            if args.json:
                print(json.dumps(metrics_dict(tree), indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                for key, value in metrics_dict(tree).items():
                    print(f"{key} = {value}")

        elif args.command == "xmetrics":
            tree = encode(args.n)
            data = extended_metrics(tree)
            if args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                for key, value in data.items():
                    print(f"{key} = {value}")

        elif args.command == "explain":
            if args.pathwise_depth < 1:
                raise ValueError("--pathwise-depth must be >= 1")
            if args.max_nodes is not None and args.max_nodes < 1:
                raise ValueError("--max-nodes must be >= 1")
            if args.json and args.dot:
                raise ValueError("--json and --dot cannot be used together")

            data = _explain_data(
                args.n,
                pathwise_depth=args.pathwise_depth,
                max_nodes=args.max_nodes,
            )

            if args.dot:
                print(_pathwise_dot(args.n, args.pathwise_depth, max_nodes=args.max_nodes))
            elif args.json:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"N = {data['n']}")
                print(f"factorization = {data['factorization_str']}")
                print(f"generator = {data['generator']}")
                print(f"already_minimal = {data['already_minimal']}")
                print(f"child_generators = {data['child_generators']}")
                print(
                    "metrics =",
                    f"nodes={data['metrics']['node_count']}",
                    f"height={data['metrics']['height']}",
                    f"max_branching={data['metrics']['max_branching']}",
                    f"recursive_mass={data['metrics']['recursive_mass']}",
                )

                print("moves:")
                new_move = data["moves"]["new"]
                print(
                    "  NEW:",
                    f"x{new_move['prime']}",
                    f"-> N'={new_move['target_n']}",
                    f"generator={new_move['target_generator']}",
                )

                drop_move = data["moves"]["drop"]
                if drop_move is None:
                    print("  DROP: unavailable")
                else:
                    print(
                        "  DROP:",
                        f"primes={drop_move['primes']}",
                        f"representative={drop_move['representative_prime']}",
                        f"-> N'={drop_move['target_n']}",
                        f"generator={drop_move['target_generator']}",
                    )

                if data["moves"]["inc"]:
                    print("  INC:")
                    for row in data["moves"]["inc"]:
                        print(
                            "   ",
                            f"e={row['exponent']}",
                            f"primes={row['primes']}",
                            f"representative={row['representative_prime']}",
                            f"-> N'={row['target_n']}",
                            f"generator={row['target_generator']}",
                        )

                if data["moves"]["dec"]:
                    print("  DEC:")
                    for row in data["moves"]["dec"]:
                        print(
                            "   ",
                            f"e={row['exponent']}",
                            f"primes={row['primes']}",
                            f"representative={row['representative_prime']}",
                            f"-> N'={row['target_n']}",
                            f"generator={row['target_generator']}",
                        )
                else:
                    print("  DEC: unavailable")

                neighborhood = data["pathwise_neighborhood"]
                if neighborhood["levels"]:
                    cap = ""
                    if data["max_nodes"] is not None:
                        cap = f", max_nodes={data['max_nodes']}"
                    print(f"pathwise neighborhood (depth={data['pathwise_depth']}{cap}):")
                    for level in neighborhood["levels"]:
                        print(f"  depth {level['depth']}:")
                        for row in level["targets"]:
                            print(
                                "   ",
                                f"n={row['n']}",
                                f"g={row['generator']}",
                                f"from_n={row['from_numbers']}",
                                f"from_g={row['from_generators']}",
                                f"via={row['last_step_labels']}",
                                f"path={' -> '.join(row['path'])}",
                            )
                    if neighborhood["truncated"]:
                        print("  [truncated by --max-nodes]")

        elif args.command == "scan":
            from .scan import scan_range, write_jsonl

            if args.start < 2:
                raise ValueError("start must be >= 2")

            if args.end < args.start:
                raise ValueError("end must be >= start")

            records = scan_range(args.start, args.end)
            write_jsonl(records, args.jsonl)

        elif args.command == "atlas":
            stats = atlas(args.file)
            print_atlas(stats)

        elif args.command == "shape-generators":
            seen = set()
            index = 0
            generators = []

            with open(args.file, "r", encoding="utf-8") as f:
                for line in f:
                    rec = json.loads(line)

                    n = rec["n"]
                    tree = rec["pet"]
                    metrics = rec["metrics"]

                    shape = extract_shape(tree)

                    if shape not in seen:
                        seen.add(shape)
                        index += 1
                        generators.append(n)

                        print()
                        print(f"shape {index}")
                        print(f"generator: {n}")

                        if args.metrics:
                            print(
                                "metrics:",
                                f"nodes={metrics['node_count']}",
                                f"height={metrics['height']}",
                                f"max_branching={metrics['max_branching']}",
                                f"recursive_mass={metrics['recursive_mass']}",
                            )

                        lines = draw_shape(shape, lines=[])

                        for line in lines:
                            print(line)

            print()
            print("generator sequence G(k):")
            print(generators)








        elif args.command == "int-from-bytes":
            report = _read_int_from_bytes_file(
                args.file,
                byteorder=args.byteorder,
                signed=args.signed,
            )

            if args.json:
                print(json.dumps(report, indent=2, ensure_ascii=False))
            else:
                print(f"file = {report['file']}")
                print(f"byteorder = {report['byteorder']}")
                print(f"signed = {'yes' if report['signed'] else 'no'}")
                print(f"byte_count = {report['byte_count']}")
                print(f"hex = {report['hex']}")
                print(f"int = {report['int']}")

        elif args.command == "branch-neighbors":
            if args.n < 2:
                raise ValueError("branch-neighbors expects integers >= 2")

            rows = _sorted_plan_neighbors(args.n)

            if args.json:
                print(json.dumps({
                    "n": args.n,
                    "count": len(rows),
                    "path": _jsonable_value(rows),
                }, indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                print(f"count = {len(rows)}")
                print("---")
                for row in rows:
                    print(f"{row['source_n']} --{row['label']}--> {row['target_n']}")

        elif args.command == "shape-of":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import pet_to_shape

            shape = pet_to_shape(encode(args.n))

            if args.json:
                print(json.dumps({
                    "n": args.n,
                    "shape": _shape_to_jsonable(shape),
                }, indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                print(f"shape = {shape}")
                print("shape tree:")
                lines = draw_shape(shape, lines=[])
                for line in lines:
                    print(line)

        elif args.command == "partial-shape-report":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                normalize_partial_shape,
                partial_shape_completion_report,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))
            report = partial_shape_completion_report(
                partial,
                max_mass=args.max_mass,
                preview=args.preview,
            )

            if args.json:
                print(json.dumps(_jsonable_value(report), indent=2, ensure_ascii=False))
            else:
                print(f"partial = {report['partial']}")
                print(f"is_exact = {report['is_exact']}")
                print(f"hole_count = {report['hole_count']}")
                print(f"fill_min = {report['fill_min']}")
                print(f"min_target_shape = {report['min_target_shape']}")
                print(f"min_target_gamma = {report['min_target_gamma']}")
                print(f"completion_count = {report['completion_count']}")
                print(f"per_mass_count = {report['per_mass_count']}")
                print(f"cumulative_count = {report['cumulative_count']}")
                print(f"per_mass_min_gamma = {report['per_mass_min_gamma']}")
                print(f"preview_exact_shapes = {report['preview_exact_shapes']}")
                print(f"preview_exact_gammas = {report['preview_exact_gammas']}")


        elif args.command == "partial-shape-match":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                n_matches_partial_shape,
                normalize_partial_shape,
                pet_to_shape,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))
            shape = pet_to_shape(encode(args.n))
            match = n_matches_partial_shape(args.n, partial)

            if args.json:
                print(json.dumps({
                    "n": args.n,
                    "partial": _jsonable_value(partial),
                    "shape": _shape_to_jsonable(shape),
                    "match": match,
                }, indent=2, ensure_ascii=False))
            else:
                print(f"N = {args.n}")
                print(f"partial = {partial}")
                print(f"shape = {shape}")
                print(f"match = {'yes' if match else 'no'}")


        elif args.command == "partial-shape-witness":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                normalize_partial_shape,
                partial_shape_shortest_completion_gamma,
                partial_shape_shortest_completion_pet,
                partial_shape_shortest_completion_target,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))
            target_shape = partial_shape_shortest_completion_target(partial)
            target_gamma = partial_shape_shortest_completion_gamma(partial)
            target_pet = partial_shape_shortest_completion_pet(partial)

            if args.json:
                print(json.dumps({
                    "partial": _jsonable_value(partial),
                    "target_shape": _jsonable_value(target_shape),
                    "target_gamma": target_gamma,
                    "target_pet": _jsonable_value(to_jsonable(target_pet)),
                }, indent=2, ensure_ascii=False))
            else:
                print(f"partial = {partial}")
                print(f"target_shape = {target_shape}")
                print(f"target_gamma = {target_gamma}")
                print("target_pet:")
                print(to_json(target_pet))


        elif args.command == "partial-shape-completions":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                normalize_partial_shape,
                partial_shape_completion_frontier,
                partial_shape_completion_gamma_frontier,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))
            shapes = partial_shape_completion_frontier(partial, args.max_mass)
            gammas = partial_shape_completion_gamma_frontier(partial, args.max_mass)

            if args.json:
                print(json.dumps({
                    "partial": _jsonable_value(partial),
                    "max_mass": args.max_mass,
                    "count": len(shapes),
                    "exact_shapes": _jsonable_value(shapes[:args.preview]),
                    "exact_gammas": gammas[:args.preview],
                }, indent=2, ensure_ascii=False))
            else:
                print(f"partial = {partial}")
                print(f"max_mass = {args.max_mass}")
                print(f"count = {len(shapes)}")
                print(f"exact_shapes (preview={args.preview}):")
                for shape in shapes[:args.preview]:
                    print(f"  {shape}")
                print(f"exact_gammas (preview={args.preview}) = {gammas[:args.preview]}")



        elif args.command == "partial-shape-forced-core":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                normalize_partial_shape,
                partial_shape_forced_core_change_masses,
                partial_shape_forced_core_meets_window,
                partial_shape_forced_core_report,
                partial_shape_forced_core_stabilization_mass,
                partial_shape_forced_core_stable_window,
                partial_shape_forced_core_trace,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))

            if args.window < 1:
                raise ValueError("--window must be >= 1")
            if args.auto_window is not None and args.auto_window < 1:
                raise ValueError("--auto-window must be >= 1")
            if args.max_mass_cap < 1:
                raise ValueError("--max-mass-cap must be >= 1")

            effective_max_mass = args.max_mass
            auto_window = args.auto_window

            if auto_window is not None:
                chosen = None
                for bound in range(1, args.max_mass_cap + 1):
                    if partial_shape_forced_core_meets_window(partial, bound, auto_window):
                        chosen = bound
                        break
                effective_max_mass = args.max_mass_cap if chosen is None else chosen

            report = partial_shape_forced_core_report(partial, effective_max_mass)
            trace = partial_shape_forced_core_trace(partial, effective_max_mass) if args.trace else ()
            change_masses = partial_shape_forced_core_change_masses(partial, effective_max_mass)
            stabilization_mass = partial_shape_forced_core_stabilization_mass(partial, effective_max_mass)
            stable_window = partial_shape_forced_core_stable_window(partial, effective_max_mass)
            meets_window = partial_shape_forced_core_meets_window(partial, effective_max_mass, args.window)
            auto_window_met = (
                partial_shape_forced_core_meets_window(partial, effective_max_mass, auto_window)
                if auto_window is not None else None
            )

            if args.json:
                payload = dict(report)
                if args.trace:
                    payload["trace"] = trace
                payload["change_masses"] = change_masses
                payload["stabilization_mass"] = stabilization_mass
                payload["stable_window"] = stable_window
                payload["fixed_window"] = args.window
                payload["meets_window"] = meets_window
                payload["effective_max_mass"] = effective_max_mass
                payload["auto_window"] = auto_window
                payload["max_mass_cap"] = args.max_mass_cap
                payload["auto_window_met"] = auto_window_met
                print(json.dumps(_jsonable_value(payload), indent=2, ensure_ascii=False))
            else:
                print(f"partial = {report['partial']}")
                print(f"max_mass = {report['max_mass']}")
                print(f"effective_max_mass = {effective_max_mass}")
                print(f"completion_count = {report['completion_count']}")
                print(f"forced_core = {report['forced_core']}")
                print(f"forced_core_kind = {report['forced_core_kind']}")
                print(f"reported_in_canonical_coordinates = {'yes' if report['reported_in_canonical_coordinates'] else 'no'}")
                print(f"forced_hole_count = {report['forced_hole_count']}")
                print(f"fast_preview = {'yes' if report['fast_preview'] else 'no'}")
                print(f"is_exact = {report['is_exact']}")
                print(f"change_masses = {change_masses}")
                print(f"stable_window = {stable_window}")
                if stable_window < 2:
                    print("warning = weak-stabilization")
                print(f"fixed_window = {args.window}")
                print(f"meets_window = {'yes' if meets_window else 'no'}")
                if auto_window is not None:
                    print(f"auto_window = {auto_window}")
                    print(f"max_mass_cap = {args.max_mass_cap}")
                    print(f"auto_window_met = {'yes' if auto_window_met else 'no'}")
                if args.trace:
                    print("trace:")
                    for row in trace:
                        delta = "Δ" if row["changed"] else "="
                        print(
                            "  ",
                            f"{delta}[{row['change_kind']}]",
                            f"max_mass={row['max_mass']}",
                            f"completion_count={row['completion_count']}",
                            f"prev={row['prev_forced_core']}",
                            f"forced_core={row['forced_core']}",
                        )
                    if stabilization_mass is None:
                        print("stabilization_mass (inspected suffix) = none")
                    else:
                        print(f"stabilization_mass (inspected suffix) = {stabilization_mass}")


        elif args.command == "partial-shape-residual":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                normalize_partial_shape,
                partial_shape_forced_core_meets_window,
                partial_shape_residual,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))

            if args.auto_window is not None and args.auto_window < 1:
                raise ValueError("--auto-window must be >= 1")
            if args.max_mass_cap < 1:
                raise ValueError("--max-mass-cap must be >= 1")

            effective_max_mass = args.max_mass
            auto_window = args.auto_window

            if auto_window is not None:
                chosen = None
                for bound in range(1, args.max_mass_cap + 1):
                    if partial_shape_forced_core_meets_window(partial, bound, auto_window):
                        chosen = bound
                        break
                effective_max_mass = args.max_mass_cap if chosen is None else chosen

            report = partial_shape_residual(partial, effective_max_mass)

            if args.json:
                payload = dict(report)
                payload["effective_max_mass"] = effective_max_mass
                payload["auto_window"] = auto_window
                payload["max_mass_cap"] = args.max_mass_cap
                print(json.dumps(_jsonable_value(payload), indent=2, ensure_ascii=False))
            else:
                print(f"partial = {report['partial']}")
                print(f"max_mass = {report['max_mass']}")
                print(f"effective_max_mass = {effective_max_mass}")
                print(f"forced_core = {report['forced_core']}")
                print(f"forced_core_kind = {report['forced_core_kind']}")
                print(f"reported_in_canonical_coordinates = {'yes' if report['reported_in_canonical_coordinates'] else 'no'}")
                print(f"free_paths = {report['free_paths']}")
                print(f"free_path_count = {report['free_path_count']}")
                print(f"forced_hole_count = {report['forced_hole_count']}")
                print(f"fast_preview = {'yes' if report['fast_preview'] else 'no'}")
                print(f"stable_window = {report['stable_window']}")
                print(f"stabilization_mass = {report['stabilization_mass']}")
                if report["stable_window"] < 2:
                    print("warning = weak-stabilization")
                if auto_window is not None:
                    print(f"auto_window = {auto_window}")
                    print(f"max_mass_cap = {args.max_mass_cap}")


        elif args.command == "partial-shape-residual-profile":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                normalize_partial_shape,
                partial_shape_forced_core_meets_window,
                partial_shape_residual_profile,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))

            if args.preview < 0:
                raise ValueError("--preview must be >= 0")
            if args.auto_window is not None and args.auto_window < 1:
                raise ValueError("--auto-window must be >= 1")
            if args.max_mass_cap < 1:
                raise ValueError("--max-mass-cap must be >= 1")

            effective_max_mass = args.max_mass
            auto_window = args.auto_window

            if auto_window is not None:
                chosen = None
                for bound in range(1, args.max_mass_cap + 1):
                    if partial_shape_forced_core_meets_window(partial, bound, auto_window):
                        chosen = bound
                        break
                effective_max_mass = args.max_mass_cap if chosen is None else chosen

            report = partial_shape_residual_profile(partial, effective_max_mass, preview=args.preview)

            if args.json:
                payload = dict(report)
                payload["effective_max_mass"] = effective_max_mass
                payload["auto_window"] = auto_window
                payload["max_mass_cap"] = args.max_mass_cap
                print(json.dumps(_jsonable_value(payload), indent=2, ensure_ascii=False))
            else:
                print(f"partial = {report['partial']}")
                print(f"max_mass = {report['max_mass']}")
                print(f"effective_max_mass = {effective_max_mass}")
                print(f"forced_core = {report['forced_core']}")
                print(f"forced_core_kind = {report['forced_core_kind']}")
                print(f"reported_in_canonical_coordinates = {'yes' if report['reported_in_canonical_coordinates'] else 'no'}")
                print(f"free_paths = {report['free_paths']}")
                print(f"free_path_count = {report['free_path_count']}")
                if auto_window is not None:
                    print(f"auto_window = {auto_window}")
                    print(f"max_mass_cap = {args.max_mass_cap}")
                print("per_path:")
                for path, row in report["per_path"].items():
                    print(f"  path = {path}")
                    print(f"    count = {row['count']}")
                    print(f"    local_forced_core = {row['local_forced_core']}")
                    print(f"    local_forced_core_kind = {row['local_forced_core_kind']}")
                    print(f"    preview_shapes = {row['preview_shapes']}")
                    print(f"    preview_local_gammas = {row['preview_local_gammas']}")


        elif args.command == "partial-shape-residual-summary":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                normalize_partial_shape,
                partial_shape_forced_core_meets_window,
                partial_shape_residual_summary,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))

            if args.preview < 0:
                raise ValueError("--preview must be >= 0")
            if args.auto_window is not None and args.auto_window < 1:
                raise ValueError("--auto-window must be >= 1")
            if args.max_mass_cap < 1:
                raise ValueError("--max-mass-cap must be >= 1")

            effective_max_mass = args.max_mass
            auto_window = args.auto_window

            if auto_window is not None:
                chosen = None
                for bound in range(1, args.max_mass_cap + 1):
                    if partial_shape_forced_core_meets_window(partial, bound, auto_window):
                        chosen = bound
                        break
                effective_max_mass = args.max_mass_cap if chosen is None else chosen

            report = partial_shape_residual_summary(
                partial,
                effective_max_mass,
                preview=args.preview,
                fast_preview=args.fast_preview,
            )

            if args.json:
                payload = dict(report)
                payload["effective_max_mass"] = effective_max_mass
                payload["auto_window"] = auto_window
                payload["max_mass_cap"] = args.max_mass_cap
                print(json.dumps(_jsonable_value(payload), indent=2, ensure_ascii=False))
            else:
                print(f"partial = {report['partial']}")
                print(f"max_mass = {report['max_mass']}")
                print(f"effective_max_mass = {effective_max_mass}")
                print(f"forced_core = {report['forced_core']}")
                print(f"forced_core_kind = {report['forced_core_kind']}")
                print(f"reported_in_canonical_coordinates = {'yes' if report['reported_in_canonical_coordinates'] else 'no'}")
                print(f"free_paths = {report['free_paths']}")
                print(f"free_path_count = {report['free_path_count']}")
                print(f"forced_hole_count = {report['forced_hole_count']}")
                print(f"fast_preview = {'yes' if report['fast_preview'] else 'no'}")
                print(f"stable_window = {report['stable_window']}")
                print(f"stabilization_mass = {report['stabilization_mass']}")
                if report["stable_window"] < 2:
                    print("warning = weak-stabilization")
                if auto_window is not None:
                    print(f"auto_window = {auto_window}")
                    print(f"max_mass_cap = {args.max_mass_cap}")
                print("per_path_summary:")
                for path, row in report["per_path_summary"].items():
                    print(f"  path = {path}")
                    print(f"    local_forced_core = {row['local_forced_core']}")
                    print(f"    local_forced_core_kind = {row['local_forced_core_kind']}")
                    print(f"    observed_local_count = {row['observed_local_count']}")
                    print(f"    observed_local_shapes = {row['observed_local_shapes']}")
                    print(f"    observed_local_gammas = {row['observed_local_gammas']}")


        elif args.command == "partial-shape-target":
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))

            from tools.pet_shape_algebra import (
                normalize_partial_shape,
                partial_shape_forced_core_meets_window,
                partial_shape_observed_decomposition,
            )

            partial = normalize_partial_shape(_parse_partial_shape_arg(args.partial))

            if args.preview < 0:
                raise ValueError("--preview must be >= 0")
            if args.auto_window is not None and args.auto_window < 1:
                raise ValueError("--auto-window must be >= 1")
            if args.max_mass_cap < 1:
                raise ValueError("--max-mass-cap must be >= 1")

            effective_max_mass = args.max_mass
            auto_window = args.auto_window

            if auto_window is not None:
                chosen = None
                for bound in range(1, args.max_mass_cap + 1):
                    if partial_shape_forced_core_meets_window(partial, bound, auto_window):
                        chosen = bound
                        break
                effective_max_mass = args.max_mass_cap if chosen is None else chosen

            report = partial_shape_observed_decomposition(
                partial,
                max_mass=effective_max_mass,
                preview=args.preview,
                fast_preview=args.fast_preview,
            )

            if args.json:
                payload = dict(report)
                payload["effective_max_mass"] = effective_max_mass
                payload["auto_window"] = auto_window
                payload["max_mass_cap"] = args.max_mass_cap
                print(json.dumps(_jsonable_value(payload), indent=2, ensure_ascii=False))
            else:
                print(f"partial = {report['partial']}")
                print(f"observed_core = {report['observed_core']}")
                print(f"observed_core_kind = {report['observed_core_kind']}")
                print(f"reported_in_canonical_coordinates = {'yes' if report['reported_in_canonical_coordinates'] else 'no'}")
                print(f"residual_free_paths = {report['residual_free_paths']}")
                print(f"residual_free_path_count = {report['residual_free_path_count']}")
                print("evidence:")
                print(f"  max_mass = {report['evidence']['max_mass']}")
                print(f"  stable_window = {report['evidence']['stable_window']}")
                print(f"  stabilization_mass = {report['evidence']['stabilization_mass']}")
                if report["evidence"]["stable_window"] < 2:
                    print("  warning = weak-stabilization")
                print(f"  forced_hole_count = {report['evidence']['forced_hole_count']}")
                print(f"  fast_preview = {'yes' if report['evidence']['fast_preview'] else 'no'}")
                if auto_window is not None:
                    print(f"  auto_window = {auto_window}")
                    print(f"  max_mass_cap = {args.max_mass_cap}")
                    print(f"  effective_max_mass = {effective_max_mass}")
                print("residual_local_profiles:")
                for path, row in report["residual_local_profiles"].items():
                    print(f"  path = {path}")
                    print(f"    local_forced_core = {row['local_forced_core']}")
                    print(f"    local_forced_core_kind = {row['local_forced_core_kind']}")
                    print(f"    observed_local_count = {row['observed_local_count']}")
                    print(f"    observed_local_shapes = {row['observed_local_shapes']}")
                    print(f"    observed_local_gammas = {row['observed_local_gammas']}")

        elif args.command == "rewrite":
            from pet import rewrite_metric as _rewrite_metric

            if args.rewrite_command == "pair":
                return _rewrite_metric.cmd_pair(args)
            elif args.rewrite_command == "explain":
                return _rewrite_metric.cmd_explain(args)
            elif args.rewrite_command == "friction":
                return _rewrite_metric.cmd_friction(args)
            elif args.rewrite_command == "scan":
                return _rewrite_metric.cmd_scan(args)
            elif args.rewrite_command == "matrix":
                return _rewrite_metric.cmd_matrix(args)
            raise ValueError(f"unknown rewrite command: {args.rewrite_command}")

        elif args.command == "query":
            return run_query(args)

        elif args.command == "families":
            return run_families(args)

        else:
            parser.print_help()
            return 1

        return 0

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


def cli() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    cli()
