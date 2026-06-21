from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]

MARKDOWN_FILES = [ROOT / "README.md"]
MARKDOWN_FILES.extend(sorted((ROOT / "docs").rglob("*.md")))

MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SRC_PY_REF_RE = re.compile(r"(src/pet(?:/[A-Za-z0-9_./-]+|_[A-Za-z0-9_./-]+)\.py)")


def _is_external_link(target: str) -> bool:
    lowered = target.lower()
    return lowered.startswith(
        (
            "http://",
            "https://",
            "mailto:",
            "tel:",
        )
    )


def _local_link_path(raw_target: str) -> str:
    target = raw_target.strip()

    if not target:
        return ""

    if _is_external_link(target):
        return ""

    if target.startswith("#"):
        return ""

    if " " in target:
        target = target.split(" ", 1)[0]

    target = target.strip("<>")
    target = target.split("#", 1)[0]
    target = target.split("?", 1)[0]
    target = unquote(target)

    return target


def _check_markdown_links(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    rel_path = path.relative_to(ROOT)

    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in MARKDOWN_LINK_RE.finditer(line):
            target = _local_link_path(match.group(1))

            if not target:
                continue

            if target.startswith("/"):
                candidate = ROOT / target.lstrip("/")
            else:
                candidate = path.parent / target

            if not candidate.exists():
                errors.append(
                    f"{rel_path}:{line_no}: broken local markdown link: {match.group(1)}"
                )

    return errors


def _check_src_python_refs(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    rel_path = path.relative_to(ROOT)

    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in SRC_PY_REF_RE.finditer(line):
            ref = match.group(1)
            candidate = ROOT / ref

            if not candidate.exists():
                errors.append(
                    f"{rel_path}:{line_no}: stale Python source reference: {ref}"
                )

    return errors


def main() -> int:
    errors: list[str] = []

    for path in MARKDOWN_FILES:
        errors.extend(_check_markdown_links(path))
        errors.extend(_check_src_python_refs(path))

    if errors:
        print("Documentation consistency check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Documentation consistency check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
