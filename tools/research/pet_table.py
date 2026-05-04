#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import difflib
import os
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class PetRow:
    n: int
    freq: int
    factorization: str
    profile: List[int]
    height: int
    branching: int
    rmass: int
    structural_class: str


class DatasetPathError(FileNotFoundError):
    """Raised when the dataset path cannot be resolved helpfully."""


VALID_SORT_FIELDS = ("n", "freq", "h", "b", "rm", "profile", "class")


def factorize(n: int) -> Dict[int, int]:
    if n <= 1:
        raise ValueError(f"PET is defined here only for integers >= 2; got {n}")

    factors: Dict[int, int] = {}
    x = n

    count = 0
    while x % 2 == 0:
        x //= 2
        count += 1
    if count:
        factors[2] = count

    p = 3
    while p * p <= x:
        count = 0
        while x % p == 0:
            x //= p
            count += 1
        if count:
            factors[p] = count
        p += 2

    if x > 1:
        factors[x] = factors.get(x, 0) + 1

    return factors


def pet_profile(exponents: Sequence[int]) -> List[int]:
    h = max(exponents)
    return [sum(1 for e in exponents if e >= level) for level in range(1, h + 1)]


def format_factorization(factors: Dict[int, int]) -> str:
    parts = []
    for p in sorted(factors):
        e = factors[p]
        parts.append(str(p) if e == 1 else f"{p}^{e}")
    return "·".join(parts)


def classify_structure(factors: Dict[int, int]) -> str:
    exps = sorted(factors.values(), reverse=True)
    b = len(exps)

    if b == 1:
        e = exps[0]
        return "primo" if e == 1 else f"p^{e}"

    if all(e == 1 for e in exps):
        if b == 2:
            return "p·q"
        if b == 3:
            return "p·q·r"
        return "squarefree"

    counts = Counter(exps)
    if b == 2 and counts == Counter({2: 1, 1: 1}):
        return "p^2·q"
    if b == 2 and counts == Counter({3: 1, 1: 1}):
        return "p^3·q"
    if b == 2 and counts == Counter({4: 1, 1: 1}):
        return "p^4·q"
    if b == 2 and counts == Counter({2: 2}):
        return "p^2·q^2"
    if b == 3 and counts == Counter({2: 1, 1: 2}):
        return "p^2·q·r"

    parts = []
    for e, c in sorted(counts.items(), reverse=True):
        token = "p" if e == 1 else f"p^{e}"
        parts.extend([token] * c)
    return "·".join(parts)


def compute_row(n: int, freq: int) -> PetRow:
    factors = factorize(n)
    exponents = list(factors.values())
    profile = pet_profile(exponents)
    return PetRow(
        n=n,
        freq=freq,
        factorization=format_factorization(factors),
        profile=profile,
        height=max(exponents),
        branching=len(exponents),
        rmass=sum(e - 1 for e in exponents),
        structural_class=classify_structure(factors),
    )


def read_dataset_text(text: str) -> List[int]:
    normalized = text.replace(",", " ").replace(";", " ")
    values: List[int] = []

    for token in normalized.split():
        try:
            values.append(int(token))
        except ValueError as exc:
            raise ValueError(f"Token non intero trovato nel dataset: {token!r}") from exc

    if not values:
        raise ValueError("Il dataset non contiene interi leggibili.")

    bad = [x for x in values if x < 2]
    if bad:
        raise ValueError(
            "Questo script assume PET solo per interi >= 2. "
            f"Trovati valori non validi: {bad}"
        )

    return values


def read_dataset_from_path(path: Path) -> List[int]:
    return read_dataset_text(path.read_text(encoding="utf-8"))


def build_rows(values: Sequence[int]) -> List[PetRow]:
    freqs = Counter(values)
    return [compute_row(n, freqs[n]) for n in sorted(freqs)]


def rows_to_markdown(rows: Sequence[PetRow]) -> str:
    headers = ["n", "freq", "fattorizzazione", "profilo PET", "h", "b", "rm", "classe strutturale"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "|---:|---:|---|---|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r.n} | {r.freq} | {r.factorization} | {r.profile} | "
            f"{r.height} | {r.branching} | {r.rmass} | {r.structural_class} |"
        )
    return "\n".join(lines)


def write_csv(rows: Sequence[PetRow], path: Path) -> None:
    ensure_parent_dir(path)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["n", "freq", "fattorizzazione", "profilo_PET", "h", "b", "rm", "classe_strutturale"])
        for r in rows:
            writer.writerow([r.n, r.freq, r.factorization, str(r.profile), r.height, r.branching, r.rmass, r.structural_class])


def profile_counters(rows: Sequence[PetRow]) -> Tuple[Counter[str], Counter[str]]:
    by_occurrences: Counter[str] = Counter()
    by_distinct: Counter[str] = Counter()
    for r in rows:
        profile = str(r.profile)
        by_occurrences[profile] += r.freq
        by_distinct[profile] += 1
    return by_occurrences, by_distinct


def dominant_profiles(counter: Counter[str]) -> Tuple[List[Tuple[str, int]], int]:
    if not counter:
        return [], 0
    best = max(counter.values())
    winners = [(profile, value) for profile, value in sorted(counter.items()) if value == best]
    return winners, best


def format_dominant_line(
    title: str,
    winners: Sequence[Tuple[str, int]],
    total: int,
    noun: str,
) -> str:
    if not winners or total <= 0:
        return f"- {title}: **nessuna**"

    profiles = ", ".join(profile for profile, _ in winners)
    value = winners[0][1]
    pct = 100.0 * value / total
    if len(winners) == 1:
        return f"- {title}: **{profiles}** con **{value} {noun}** ({pct:.2f}%)"
    return f"- {title}: **pari merito tra {profiles}** con **{value} {noun}** ciascuna ({pct:.2f}%)"


def write_summary(rows: Sequence[PetRow], total_count: int, path: Path) -> None:
    ensure_parent_dir(path)
    by_occurrences, by_distinct = profile_counters(rows)
    distinct_total = len(rows)
    occ_winners, _ = dominant_profiles(by_occurrences)
    distinct_winners, _ = dominant_profiles(by_distinct)

    with path.open("w", encoding="utf-8") as f:
        f.write("# Sintesi PET\n\n")
        f.write(f"- osservazioni totali: **{total_count}**\n")
        f.write(f"- valori distinti: **{distinct_total}**\n\n")
        f.write("## Classi dominanti\n\n")
        f.write(format_dominant_line("classe dominante (occorrenze)", occ_winners, total_count, "occorrenze") + "\n")
        f.write(format_dominant_line("classe dominante (distinti)", distinct_winners, distinct_total, "valori distinti") + "\n\n")
        f.write("## Frequenze per profilo PET (occorrenze)\n\n")
        for profile, freq in sorted(by_occurrences.items(), key=lambda x: (-x[1], x[0])):
            pct = 100.0 * freq / total_count if total_count else 0.0
            f.write(f"- {profile}: {freq} ({pct:.2f}%)\n")
        f.write("\n## Frequenze per profilo PET (valori distinti)\n\n")
        for profile, count in sorted(by_distinct.items(), key=lambda x: (-x[1], x[0])):
            pct = 100.0 * count / distinct_total if distinct_total else 0.0
            f.write(f"- {profile}: {count} ({pct:.2f}%)\n")


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Genera una tabella PET da un dataset di interi. "
            "Input da file o da stdin usando '-'."
        )
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="-",
        help="File di input con interi, oppure '-' per leggere da stdin.",
    )
    parser.add_argument(
        "--markdown-out",
        type=Path,
        help="Salva la tabella in formato Markdown.",
    )
    parser.add_argument(
        "--csv-out",
        type=Path,
        help="Salva la tabella in formato CSV.",
    )
    parser.add_argument(
        "--summary-out",
        type=Path,
        help="Salva una sintesi per profilo PET.",
    )
    parser.add_argument(
        "--sort-by",
        choices=VALID_SORT_FIELDS,
        default="n",
        help="Ordina le righe per uno dei campi disponibili.",
    )
    parser.add_argument(
        "--min-freq",
        type=int,
        default=1,
        help="Mostra solo valori con frequenza >= N.",
    )
    parser.add_argument(
        "--only-profile",
        type=str,
        help="Mostra solo il profilo PET indicato, per esempio '[2,1]' oppure '2,1'.",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        dest="print_markdown",
        help="Stampa la tabella Markdown su stdout.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Non stampare il riepilogo finale dei file scritti.",
    )
    args = parser.parse_args(list(argv))

    if args.min_freq < 1:
        parser.error("--min-freq deve essere >= 1")

    return args


def search_roots(script_dir: Path, cwd: Path) -> List[Path]:
    roots = [cwd, script_dir]
    for extra in (cwd / "tools", script_dir.parent):
        if extra.exists() and extra not in roots:
            roots.append(extra)
    return roots


def limited_walk_files(root: Path, *, max_depth: int = 3, max_files: int = 2000) -> Iterable[Path]:
    if not root.exists() or not root.is_dir():
        return

    root = root.resolve()
    yielded = 0
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        rel_parts = current.relative_to(root).parts
        depth = len(rel_parts)
        if depth >= max_depth:
            dirnames[:] = []

        dirnames[:] = sorted(
            d for d in dirnames
            if not d.startswith(".") and d not in {".git", "__pycache__", ".venv", "venv", "node_modules"}
        )

        for filename in sorted(filenames):
            if filename.startswith("."):
                continue
            yield current / filename
            yielded += 1
            if yielded >= max_files:
                return


def find_exact_filename_matches(name: str, roots: Sequence[Path], limit: int = 8) -> List[Path]:
    matches: List[Path] = []
    seen = set()
    for root in roots:
        for candidate in limited_walk_files(root):
            if candidate.name != name:
                continue
            resolved = candidate.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            matches.append(candidate)
            if len(matches) >= limit:
                return matches
    return matches


def collect_filename_candidates(roots: Sequence[Path], limit: int = 200) -> List[str]:
    names: List[str] = []
    seen = set()
    for root in roots:
        for candidate in limited_walk_files(root):
            name = candidate.name
            if name in seen:
                continue
            seen.add(name)
            names.append(name)
            if len(names) >= limit:
                return names
    return names


def format_paths_for_user(paths: Sequence[Path], cwd: Path) -> List[str]:
    formatted = []
    cwd_resolved = cwd.resolve()
    for path in paths:
        resolved = path.resolve()
        try:
            formatted.append(str(resolved.relative_to(cwd_resolved)))
        except ValueError:
            formatted.append(str(resolved))
    return formatted


def resolve_input_path(raw_input: str, cwd: Path, script_dir: Path) -> Optional[Path]:
    if raw_input == "-":
        return None

    requested = Path(raw_input).expanduser()
    if requested.is_absolute() and requested.exists():
        return requested

    direct = (cwd / requested) if not requested.is_absolute() else requested
    if direct.exists():
        return direct

    if not requested.is_absolute():
        relative_to_script = script_dir / requested
        if relative_to_script.exists():
            return relative_to_script

        basename_matches = find_exact_filename_matches(requested.name, search_roots(script_dir, cwd), limit=2)
        if len(basename_matches) == 1:
            return basename_matches[0]

    roots = search_roots(script_dir, cwd)
    suggestions: List[str] = []

    if not requested.is_absolute():
        exact_matches = find_exact_filename_matches(requested.name, roots, limit=5)
        suggestions.extend(format_paths_for_user(exact_matches, cwd))

        candidate_names = collect_filename_candidates(roots)
        for name in difflib.get_close_matches(requested.name, candidate_names, n=5, cutoff=0.55):
            for match in find_exact_filename_matches(name, roots, limit=2):
                pretty = format_paths_for_user([match], cwd)[0]
                if pretty not in suggestions:
                    suggestions.append(pretty)

    attempted = [str(direct)]
    if not requested.is_absolute():
        attempted.append(str(script_dir / requested))
    attempted_text = "\n  - " + "\n  - ".join(attempted)

    message = [
        f"File di input non trovato: {raw_input!r}",
        f"Path provati:{attempted_text}",
    ]
    if suggestions:
        message.append("Forse intendevi uno di questi?\n  - " + "\n  - ".join(suggestions[:5]))
    else:
        message.append("Suggerimento: usa un path relativo alla directory corrente, oppure '-' per leggere da stdin.")

    raise DatasetPathError("\n".join(message))


def load_values(input_arg: str) -> Tuple[List[int], str]:
    cwd = Path.cwd()
    script_dir = Path(__file__).resolve().parent

    if input_arg == "-":
        text = sys.stdin.read()
        if not text.strip():
            raise ValueError(
                "stdin è vuoto. Passa un file oppure usa una pipe, per esempio: cat dataset.txt | python3 pet_table_v4.py -"
            )
        return read_dataset_text(text), "stdin"

    resolved = resolve_input_path(input_arg, cwd=cwd, script_dir=script_dir)
    assert resolved is not None
    return read_dataset_from_path(resolved), str(resolved)


def normalize_profile_text(raw: str) -> str:
    text = raw.strip()
    if not text:
        raise ValueError("Profilo PET vuoto passato a --only-profile")

    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1].strip()

    if not text:
        raise ValueError("Profilo PET vuoto passato a --only-profile")

    parts = [part.strip() for part in text.split(",")]
    if any(not part for part in parts):
        raise ValueError(f"Profilo PET non valido: {raw!r}")

    try:
        values = [int(part) for part in parts]
    except ValueError as exc:
        raise ValueError(f"Profilo PET non valido: {raw!r}") from exc

    if any(v <= 0 for v in values):
        raise ValueError(f"Profilo PET non valido: {raw!r}")

    return str(values)


def apply_filters(rows: Sequence[PetRow], min_freq: int, only_profile: Optional[str]) -> List[PetRow]:
    filtered = [row for row in rows if row.freq >= min_freq]
    if only_profile is not None:
        normalized = normalize_profile_text(only_profile)
        filtered = [row for row in filtered if str(row.profile) == normalized]
    return filtered


def sort_rows(rows: Sequence[PetRow], sort_by: str) -> List[PetRow]:
    if sort_by == "n":
        return sorted(rows, key=lambda r: (r.n,))
    if sort_by == "freq":
        return sorted(rows, key=lambda r: (-r.freq, r.n))
    if sort_by == "h":
        return sorted(rows, key=lambda r: (-r.height, r.n))
    if sort_by == "b":
        return sorted(rows, key=lambda r: (-r.branching, r.n))
    if sort_by == "rm":
        return sorted(rows, key=lambda r: (-r.rmass, r.n))
    if sort_by == "profile":
        return sorted(rows, key=lambda r: (tuple([-x for x in r.profile]), len(r.profile), r.n))
    if sort_by == "class":
        return sorted(rows, key=lambda r: (r.structural_class, r.n))
    raise ValueError(f"Campo di ordinamento non supportato: {sort_by!r}")


def maybe_write_markdown(rows: Sequence[PetRow], path: Path) -> None:
    ensure_parent_dir(path)
    path.write_text(rows_to_markdown(rows), encoding="utf-8")


def print_output_report(source_label: str, args: argparse.Namespace, rows: Sequence[PetRow], total_count: int) -> None:
    if args.quiet:
        return
    outputs = []
    if args.markdown_out:
        outputs.append(f"Markdown: {args.markdown_out}")
    if args.csv_out:
        outputs.append(f"CSV: {args.csv_out}")
    if args.summary_out:
        outputs.append(f"Sintesi: {args.summary_out}")

    by_occurrences, by_distinct = profile_counters(rows)
    distinct_total = len(rows)
    occ_winners, _ = dominant_profiles(by_occurrences)
    distinct_winners, _ = dominant_profiles(by_distinct)

    print(f"[pet-table] sorgente: {source_label}", file=sys.stderr)
    print(f"[pet-table] righe emesse: {len(rows)}", file=sys.stderr)
    print(f"[pet-table] osservazioni emesse: {total_count}", file=sys.stderr)
    if args.min_freq > 1:
        print(f"[pet-table] filtro: freq >= {args.min_freq}", file=sys.stderr)
    if args.only_profile:
        print(f"[pet-table] filtro: profilo = {normalize_profile_text(args.only_profile)}", file=sys.stderr)
    if args.sort_by != "n":
        print(f"[pet-table] ordinamento: {args.sort_by}", file=sys.stderr)
    print(
        f"[pet-table] {format_dominant_line('classe dominante (occorrenze)', occ_winners, total_count, 'occorrenze')[2:]}",
        file=sys.stderr,
    )
    print(
        f"[pet-table] {format_dominant_line('classe dominante (distinti)', distinct_winners, distinct_total, 'valori distinti')[2:]}",
        file=sys.stderr,
    )
    for line in outputs:
        print(f"[pet-table] scritto -> {line}", file=sys.stderr)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)

    try:
        values, source_label = load_values(args.input_file)
        rows = build_rows(values)
        rows = apply_filters(rows, min_freq=args.min_freq, only_profile=args.only_profile)
        rows = sort_rows(rows, sort_by=args.sort_by)
    except Exception as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        return 1

    total_count = sum(row.freq for row in rows)

    should_print = args.print_markdown or (
        not args.markdown_out and not args.csv_out and not args.summary_out
    )
    if should_print:
        print(rows_to_markdown(rows))

    if args.markdown_out:
        maybe_write_markdown(rows, args.markdown_out)
    if args.csv_out:
        write_csv(rows, args.csv_out)
    if args.summary_out:
        write_summary(rows, total_count, args.summary_out)

    print_output_report(source_label, args, rows, total_count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
