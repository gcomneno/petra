from __future__ import annotations
import json

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _run_cli(*args: str) -> str:
    result = subprocess.run(
        [sys.executable, "-m", "pet.cli", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def test_cli_shape_of_smoke():
    out = _run_cli("shape-of", "12")

    assert "N = 12" in out
    assert "shape = ((), ((),))" in out
    assert "shape tree:" in out


def test_cli_partial_shape_match_smoke():
    out = _run_cli("partial-shape-match", "12", "((), None)")

    assert "N = 12" in out
    assert "partial = (None, ())" in out
    assert "shape = ((), ((),))" in out
    assert "match = yes" in out


def test_cli_partial_shape_witness_smoke():
    out = _run_cli("partial-shape-witness", "((), None)")

    assert "partial = (None, ())" in out
    assert "target_shape = ((), ())" in out
    assert "target_gamma = 6" in out
    assert '"p": 2' in out
    assert '"p": 3' in out


def test_cli_partial_shape_completions_smoke():
    out = _run_cli("partial-shape-completions", "((), None)", "--max-mass", "3")

    assert "partial = (None, ())" in out
    assert "max_mass = 3" in out
    assert "count = 2" in out
    assert "  ((), ())" in out
    assert "  ((), ((),))" in out
    assert "exact_gammas (preview=20) = (6, 12)" in out


def test_cli_partial_shape_forced_core_smoke():
    out = _run_cli("partial-shape-forced-core", "((), None)", "--max-mass", "3")

    assert "partial = (None, ())" in out
    assert "max_mass = 3" in out
    assert "completion_count = 2" in out
    assert "forced_core = (None, ())" in out
    assert "forced_core_kind = partially-structured" in out
    assert "forced_hole_count = 1" in out
    assert "is_exact = False" in out


def test_cli_partial_shape_forced_core_trace_smoke():
    out = _run_cli("partial-shape-forced-core", "((), None)", "--max-mass", "4", "--trace")

    assert "partial = (None, ())" in out
    assert "max_mass = 4" in out
    assert "change_masses = (1, 2, 3)" in out
    assert "trace:" in out
    assert "Δ[start] max_mass=1 completion_count=0 prev=None forced_core=None" in out
    assert "Δ[strengthen] max_mass=2 completion_count=1 prev=None forced_core=((), ())" in out
    assert "Δ[relax] max_mass=3 completion_count=2 prev=((), ()) forced_core=(None, ())" in out
    assert "=[same] max_mass=4 completion_count=4 prev=(None, ()) forced_core=(None, ())" in out
    assert "stabilization_mass (inspected suffix) = 3" in out


def test_cli_partial_shape_forced_core_window_smoke():
    out = _run_cli("partial-shape-forced-core", "((), None)", "--max-mass", "4", "--window", "2")

    assert "stable_window = 2" in out
    assert "fixed_window = 2" in out
    assert "meets_window = yes" in out


def test_cli_partial_shape_forced_core_auto_window_smoke():
    out = _run_cli(
        "partial-shape-forced-core",
        "((), None)",
        "--auto-window",
        "2",
        "--max-mass-cap",
        "6",
    )

    assert "effective_max_mass = 4" in out
    assert "stable_window = 2" in out
    assert "auto_window = 2" in out
    assert "max_mass_cap = 6" in out
    assert "auto_window_met = yes" in out


def test_cli_partial_shape_forced_core_kind_examples():
    out1 = _run_cli("partial-shape-forced-core", "None", "--max-mass", "2")
    out2 = _run_cli("partial-shape-forced-core", "(None, (None,))", "--max-mass", "5")
    out3 = _run_cli("partial-shape-forced-core", "((None,), (None,))", "--max-mass", "6")

    assert "forced_core_kind = empty" in out1
    assert "forced_core_kind = root-arity-only" in out2
    assert "forced_core_kind = partially-structured" in out3


def test_cli_partial_shape_residual_smoke():
    out = _run_cli("partial-shape-residual", "((), None)", "--auto-window", "3", "--max-mass-cap", "12")

    assert "partial = (None, ())" in out
    assert "effective_max_mass = 5" in out
    assert "forced_core = (None, ())" in out
    assert "forced_core_kind = partially-structured" in out
    assert "free_paths = ((0,),)" in out
    assert "free_path_count = 1" in out


def test_cli_partial_shape_residual_kind_examples():
    out1 = _run_cli("partial-shape-residual", "None", "--max-mass", "2")
    out2 = _run_cli("partial-shape-residual", "(None, (None,))", "--max-mass", "5")
    out3 = _run_cli("partial-shape-residual", "((None,), (None,))", "--max-mass", "6")

    assert "forced_core_kind = empty" in out1
    assert "free_paths = ((),)" in out1

    assert "forced_core_kind = root-arity-only" in out2
    assert "free_paths = ((0,), (1,))" in out2

    assert "forced_core_kind = partially-structured" in out3
    assert "free_paths = ((0, 0), (1, 0))" in out3


def test_cli_partial_shape_residual_profile_smoke():
    out = _run_cli("partial-shape-residual-profile", "((), None)", "--max-mass", "5")

    assert "partial = (None, ())" in out
    assert "effective_max_mass = 5" in out
    assert "forced_core = (None, ())" in out
    assert "forced_core_kind = partially-structured" in out
    assert "free_paths = ((0,),)" in out
    assert "per_path:" in out
    assert "  path = (0,)" in out
    assert "    local_forced_core = None" in out
    assert "    local_forced_core_kind = empty" in out
    assert "    preview_local_gammas = (1, 2, 6, 12, 30)" in out


def test_cli_partial_shape_residual_summary_smoke():
    out = _run_cli("partial-shape-residual-summary", "((), None)", "--max-mass", "5")

    assert "partial = (None, ())" in out
    assert "forced_core = (None, ())" in out
    assert "forced_core_kind = partially-structured" in out
    assert "free_paths = ((0,),)" in out
    assert "per_path_summary:" in out
    assert "  path = (0,)" in out
    assert "    local_forced_core = None" in out
    assert "    local_forced_core_kind = empty" in out
    assert "    observed_local_gammas = (1, 2, 6, 12, 30)" in out


def test_cli_help_exposes_only_core_shape_commands():
    out = _run_cli("-h")

    assert "shape-of" in out
    assert "partial-shape-match" in out
    assert "partial-shape-forced-core" in out
    assert "partial-shape-residual-summary" in out

    assert "partial-shape-report" not in out
    assert "partial-shape-witness" not in out
    assert "partial-shape-completions" not in out
    assert "partial-shape-residual " not in out
    assert "partial-shape-residual-profile" not in out


def test_cli_partial_shape_target_smoke():
    out = _run_cli("partial-shape-target", "((), None)", "--max-mass", "5")

    assert "partial = (None, ())" in out
    assert "observed_core = (None, ())" in out
    assert "observed_core_kind = partially-structured" in out
    assert "residual_free_paths = ((0,),)" in out
    assert "residual_local_profiles:" in out
    assert "  path = (0,)" in out


def test_cli_shape_of_prime_power_wraps_exponent_shape():
    import ast
    import re

    cache = {}

    def shape_of(n: int):
        if n in cache:
            return cache[n]
        out = _run_cli("shape-of", str(n))
        m = re.search(r"^shape = (.+)$", out, re.M)
        assert m is not None, f"shape line non trovata per n={n}\n{out}"
        value = ast.literal_eval(m.group(1))
        cache[n] = value
        return value

    for p in (2, 3, 5, 7):
        for k in range(1, 21):
            if k == 1:
                predicted = ((),)
            else:
                predicted = (shape_of(k),)
            actual = shape_of(p ** k)
            assert actual == predicted, (
                f"shape({p}^{k}) mismatch: predicted={predicted!r} actual={actual!r}"
            )


def test_cli_shape_of_prime_power_towers_wraps_recursively():
    import ast
    import re

    def shape_of(n: int):
        out = _run_cli("shape-of", str(n))
        m = re.search(r"^shape = (.+)$", out, re.M)
        assert m is not None, f"shape line non trovata per n={n}\n{out}"
        return ast.literal_eval(m.group(1))

    cases = [
        (2, 3, 2),   # 2^(3^2)
        (3, 2, 3),   # 3^(2^3)
        (5, 2, 4),   # 5^(2^4)
        (2, 5, 2),   # 2^(5^2)
    ]

    for p, q, m in cases:
        k = q ** m
        actual = shape_of(p ** k)
        predicted = (shape_of(k),)
        assert actual == predicted, (
            f"shape({p}^({q}^{m})) mismatch: predicted={predicted!r} actual={actual!r}"
        )


def test_cli_partial_shape_target_warns_on_weak_stabilization():
    out = _run_cli("partial-shape-target", "(None, ((None,),))", "--max-mass", "7")
    assert "stable_window = 1" in out
    assert "warning = weak-stabilization" in out


def test_cli_partial_shape_target_no_warning_when_stable():
    out = _run_cli("partial-shape-target", "(None, (None, None))", "--max-mass", "7")
    assert "warning = weak-stabilization" not in out


def test_cli_shape_enumerate_text_smoke_without_gamma():
    out = _run_cli("shape-enumerate", "--max-mass", "5", "--limit", "5")
    assert "shape 1" in out
    assert "mass:" in out
    assert "height:" in out
    assert "root_width:" in out
    assert "shape:" in out
    assert "gamma:" not in out


def test_cli_shape_enumerate_json_orders_height_first_then_root_width():
    out = _run_cli("shape-enumerate", "--max-mass", "5", "--limit", "10", "--json")
    rows = json.loads(out)

    assert len(rows) == 10

    got = [(row["mass"], row["height"], row["root_width"], row["shape"]) for row in rows[:6]]
    expected = [
        (5, 5, 1, [[[[[[]]]]]]),
        (4, 4, 1, [[[[[]]]]]),
        (5, 4, 1, [[[[[], []]]]]),
        (5, 4, 1, [[[[], [[]]]]]),
        (5, 4, 1, [[[], [[[]]]]]),
        (5, 4, 2, [[], [[[[]]]]]),
    ]
    assert got == expected


def test_cli_shape_enumerate_json_with_pet_includes_pet_but_not_gamma():
    out = _run_cli("shape-enumerate", "--max-mass", "5", "--limit", "3", "--json", "--with-pet")
    rows = json.loads(out)

    assert len(rows) == 3
    assert all("pet" in row for row in rows)
    assert all("gamma" not in row for row in rows)

    first = rows[0]
    assert first["mass"] == 5
    assert first["height"] == 5
    assert first["root_width"] == 1
    assert first["pet"] == [{"p": 2, "e": [{"p": 2, "e": [{"p": 2, "e": [{"p": 2, "e": [{"p": 2, "e": None}]}]}]}]}]


def test_cli_shape_enumerate_with_gamma_small_case():
    out = _run_cli("shape-enumerate", "--max-mass", "3", "--limit", "10", "--with-gamma")

    assert "gamma: 16" in out
    assert "gamma: 4" in out
    assert "gamma: 64" in out
    assert "gamma: 12" in out
    assert "gamma: 2" in out
    assert "gamma: 6" in out
    assert "gamma: 30" in out

    gamma_lines = [line.strip() for line in out.splitlines() if line.strip().startswith("gamma: ")]
    assert gamma_lines == [
        "gamma: 16",
        "gamma: 4",
        "gamma: 64",
        "gamma: 12",
        "gamma: 2",
        "gamma: 6",
        "gamma: 30",
    ]
