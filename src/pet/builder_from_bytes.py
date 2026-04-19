from __future__ import annotations

from pathlib import Path
from typing import Any

from pet.builder_from_int import build_from_int_pipeline


def _derive_terminal_state(builder_report: dict[str, Any] | None) -> tuple[str, dict[str, Any]]:
    if not builder_report:
        return "blocked", {"terminal_status": "blocked", "block_reason": "missing-builder-report"}

    final_build_output = builder_report.get("final_build_output") or {}
    built_pet_object = final_build_output.get("built_pet_object") or {}

    build_status = final_build_output.get("build_status")
    assembly_status = built_pet_object.get("assembly_status")

    if build_status == "built":
        return "built", {
            "terminal_status": "built",
            "build_status": build_status,
            "assembly_status": assembly_status,
        }

    if assembly_status == "assembled":
        return "assembled", {
            "terminal_status": "assembled",
            "build_status": build_status,
            "assembly_status": assembly_status,
        }

    return "blocked", {
        "terminal_status": "blocked",
        "build_status": build_status,
        "assembly_status": assembly_status,
    }


def build_from_bytes_pipeline(
    path: str | Path,
    output_dir: str | Path,
    *,
    byteorder: str = "big",
    signed: bool = False,
) -> dict[str, Any]:
    file_path = Path(path)
    data = file_path.read_bytes()
    input_n = int.from_bytes(data, byteorder=byteorder, signed=signed) if data else 0

    report: dict[str, Any] = {
        "schema": "pet-builder-from-bytes-v0",
        "file": str(file_path),
        "byteorder": byteorder,
        "signed": signed,
        "byte_count": len(data),
        "hex": data.hex(),
        "input_n": input_n,
        "builder_report": None,
        "terminal_state": None,
    }

    if len(data) == 0:
        report["terminal_outcome"] = "blocked"
        report["terminal_state"] = {
            "terminal_status": "blocked",
            "block_reason": "empty-input",
        }
        return report

    if input_n < 2:
        report["terminal_outcome"] = "blocked"
        report["terminal_state"] = {
            "terminal_status": "blocked",
            "block_reason": "input-too-small",
        }
        return report

    builder_report = build_from_int_pipeline(input_n, output_dir)
    terminal_outcome, terminal_state = _derive_terminal_state(builder_report)

    report["builder_report"] = builder_report
    report["terminal_outcome"] = terminal_outcome
    report["terminal_state"] = terminal_state
    return report
