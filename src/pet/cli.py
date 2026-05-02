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
