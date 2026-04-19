from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from pet.builder_from_int import build_from_int_pipeline
from pet.builder_from_irsr import build_from_irsr_pipeline


_ALLOWED_MODES = {"auto", "direct", "irsr"}


def _attempt(mode: str, status: str, detail: str | None = None) -> dict[str, Any]:
    return {
        "mode": mode,
        "status": status,
        "detail": detail,
    }


def _derive_terminal_state(builder_report: dict[str, Any] | None) -> tuple[str, dict[str, Any]]:
    if not builder_report:
        return "blocked", {
            "terminal_status": "blocked",
            "block_reason": "direct-no-viable-path",
        }

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
        "block_reason": "direct-no-viable-path",
    }


def _derive_terminal_state_from_irsr_report(irsr_report: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    terminal = irsr_report.get("terminal_state") or {}
    if terminal.get("status") == "built":
        return "built", {
            "terminal_status": "built",
            "build_status": terminal.get("build_status"),
            "assembly_status": terminal.get("assembly_status"),
        }

    return "blocked", {
        "terminal_status": "blocked",
        "block_reason": "irsr-no-viable-payload",
    }


def _run_direct_builder_with_timeout(
    n: int,
    output_dir: str | Path,
    *,
    timeout_seconds: float,
) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    src_path = str(repo_root / "src")

    env = os.environ.copy()
    env["PYTHONPATH"] = src_path + (":" + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")

    cmd = [
        sys.executable,
        str(repo_root / "tools" / "pet_builder_from_int.py"),
        str(n),
        "--output-dir",
        str(output_dir),
    ]

    try:
        proc = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "detail": "direct factoring budget exceeded",
            "builder_report": None,
        }

    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"direct builder exited with status {proc.returncode}"
        return {
            "status": "error",
            "detail": detail,
            "builder_report": None,
        }

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "detail": f"invalid JSON from direct builder: {exc}",
            "builder_report": None,
        }

    return {
        "status": "ok",
        "detail": None,
        "builder_report": payload,
    }


def build_from_bytes_pipeline(
    path: str | Path,
    output_dir: str | Path,
    *,
    byteorder: str = "big",
    signed: bool = False,
    mode: str = "auto",
    irsr_slot_candidates: dict[str, list[int]] | None = None,
    irsr_max_steps: int = 5,
    direct_timeout_seconds: float = 1.0,
) -> dict[str, Any]:
    if mode not in _ALLOWED_MODES:
        raise ValueError(f"unsupported mode: {mode}")

    file_path = Path(path)
    data = file_path.read_bytes()
    input_n = int.from_bytes(data, byteorder=byteorder, signed=signed) if data else 0

    report: dict[str, Any] = {
        "schema": "pet-builder-from-bytes-v1",
        "file": str(file_path),
        "byteorder": byteorder,
        "signed": signed,
        "byte_count": len(data),
        "hex": data.hex(),
        "input_n": input_n,
        "requested_mode": mode,
        "effective_mode": "none",
        "attempts": [],
        "builder_report": None,
        "terminal_outcome": "blocked",
        "terminal_state": {
            "terminal_status": "blocked",
            "block_reason": "internal-error",
        },
    }

    if len(data) == 0:
        report["terminal_state"] = {
            "terminal_status": "blocked",
            "block_reason": "empty-input",
        }
        return report

    if input_n < 2:
        report["terminal_state"] = {
            "terminal_status": "blocked",
            "block_reason": "input-too-small",
        }
        return report

    if mode == "irsr":
        report["effective_mode"] = "irsr"

        if not irsr_slot_candidates:
            report["attempts"].append(
                _attempt(
                    "irsr",
                    "no-viable-payload",
                    "no irsr seed candidates provided",
                )
            )
            report["terminal_state"] = {
                "terminal_status": "blocked",
                "block_reason": "irsr-no-viable-payload",
            }
            return report

        try:
            irsr_report = build_from_irsr_pipeline(
                input_n,
                output_dir,
                slot_candidates=irsr_slot_candidates,
                max_steps=irsr_max_steps,
            )
        except Exception as exc:
            report["attempts"].append(_attempt("irsr", "error", str(exc)))
            report["terminal_state"] = {
                "terminal_status": "blocked",
                "block_reason": "irsr-no-viable-payload",
            }
            return report

        terminal_outcome, terminal_state = _derive_terminal_state_from_irsr_report(irsr_report)
        report["attempts"].append(
            _attempt("irsr", terminal_outcome, None if terminal_outcome != "blocked" else irsr_report.get("irsr_final_status"))
        )
        report["builder_report"] = irsr_report.get("builder_report")
        report["terminal_outcome"] = terminal_outcome
        report["terminal_state"] = terminal_state
        return report

    if mode == "auto":
        direct = _run_direct_builder_with_timeout(
            input_n,
            output_dir,
            timeout_seconds=direct_timeout_seconds,
        )

        if direct["status"] == "ok":
            builder_report = direct["builder_report"]
            terminal_outcome, terminal_state = _derive_terminal_state(builder_report)
            report["effective_mode"] = "direct"
            report["attempts"].append(_attempt("direct", terminal_outcome, None))
            report["builder_report"] = builder_report
            report["terminal_outcome"] = terminal_outcome
            report["terminal_state"] = terminal_state
            return report

        if direct["status"] == "timeout":
            report["attempts"].append(_attempt("direct", "timeout", direct["detail"]))

            if not irsr_slot_candidates:
                report["effective_mode"] = "direct"
                report["terminal_state"] = {
                    "terminal_status": "blocked",
                    "block_reason": "direct-timeout",
                }
                return report

            try:
                irsr_report = build_from_irsr_pipeline(
                    input_n,
                    output_dir,
                    slot_candidates=irsr_slot_candidates,
                    max_steps=irsr_max_steps,
                )
            except Exception as exc:
                report["effective_mode"] = "irsr"
                report["attempts"].append(_attempt("irsr", "error", str(exc)))
                report["terminal_state"] = {
                    "terminal_status": "blocked",
                    "block_reason": "irsr-no-viable-payload",
                }
                return report

            terminal_outcome, terminal_state = _derive_terminal_state_from_irsr_report(irsr_report)
            report["effective_mode"] = "irsr"
            report["attempts"].append(
                _attempt("irsr", terminal_outcome, None if terminal_outcome != "blocked" else irsr_report.get("irsr_final_status"))
            )
            report["builder_report"] = irsr_report.get("builder_report")
            report["terminal_outcome"] = terminal_outcome
            report["terminal_state"] = terminal_state
            return report

        report["effective_mode"] = "direct"
        report["attempts"].append(_attempt("direct", "error", direct["detail"]))
        report["terminal_state"] = {
            "terminal_status": "blocked",
            "block_reason": "direct-no-viable-path",
        }
        return report

    try:
        builder_report = build_from_int_pipeline(input_n, output_dir)
    except Exception as exc:
        report["effective_mode"] = "direct"
        report["attempts"].append(_attempt("direct", "error", str(exc)))
        report["terminal_state"] = {
            "terminal_status": "blocked",
            "block_reason": "direct-no-viable-path",
        }
        return report

    terminal_outcome, terminal_state = _derive_terminal_state(builder_report)

    report["effective_mode"] = "direct"
    report["attempts"].append(_attempt("direct", terminal_outcome, None))
    report["builder_report"] = builder_report
    report["terminal_outcome"] = terminal_outcome
    report["terminal_state"] = terminal_state
    return report
