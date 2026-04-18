import json

from pet.cli import main


def test_irsr_auto_seed_report_prints_text_report(tmp_path, capsys):
    rc = main([
        "pet",
        "irsr-auto-seed-report",
        "10403",
        "--sqrt-radii",
        "1",
        "--sqrt-radii",
        "4",
        "--max-steps",
        "5",
        "--artifacts-dir",
        str(tmp_path / "artifacts"),
    ])

    captured = capsys.readouterr()

    assert rc == 0
    assert captured.err == ""
    assert "Selection: manual" in captured.out
    assert "Radii specs: [[1], [4]]" in captured.out
    assert "IRSR auto-seed comparison for n=10403" in captured.out
    assert "Best run: sqrt-auto-r1" in captured.out
    assert "Final status: built-exact-match" in captured.out
    assert "- sqrt-auto-r1 | radii=[1] | status=built-exact-match | payloads=1 | built=1 | exact=1" in captured.out
    assert "- sqrt-auto-r4 | radii=[4] | status=payloads-nonexact | payloads=1 | built=0 | exact=0" in captured.out





def test_irsr_auto_seed_report_accepts_explicit_standard_preset(tmp_path, capsys):
    rc = main([
        "pet",
        "irsr-auto-seed-report",
        "10403",
        "--preset",
        "standard",
        "--max-steps",
        "5",
        "--artifacts-dir",
        str(tmp_path / "artifacts-preset"),
    ])

    captured = capsys.readouterr()

    assert rc == 0
    assert captured.err == ""
    assert "Selection: preset=standard" in captured.out
    assert "Radii specs: [[1], [4]]" in captured.out
    assert "IRSR auto-seed comparison for n=10403" in captured.out
    assert "Best run: sqrt-auto-r1" in captured.out
    assert "- sqrt-auto-r1 | radii=[1] | status=built-exact-match | payloads=1 | built=1 | exact=1" in captured.out
    assert "- sqrt-auto-r4 | radii=[4] | status=payloads-nonexact | payloads=1 | built=0 | exact=0" in captured.out


def test_irsr_auto_seed_report_uses_default_ladders_when_not_provided(tmp_path, capsys):
    rc = main([
        "pet",
        "irsr-auto-seed-report",
        "10403",
        "--max-steps",
        "5",
        "--artifacts-dir",
        str(tmp_path / "artifacts-default"),
    ])

    captured = capsys.readouterr()

    assert rc == 0
    assert captured.err == ""
    assert "Selection: preset=standard" in captured.out
    assert "Radii specs: [[1], [4]]" in captured.out
    assert "IRSR auto-seed comparison for n=10403" in captured.out
    assert "Best run: sqrt-auto-r1" in captured.out
    assert "- sqrt-auto-r1 | radii=[1] | status=built-exact-match | payloads=1 | built=1 | exact=1" in captured.out
    assert "- sqrt-auto-r4 | radii=[4] | status=payloads-nonexact | payloads=1 | built=0 | exact=0" in captured.out

def test_irsr_auto_seed_report_emits_json_payload(tmp_path, capsys):
    rc = main([
        "pet",
        "irsr-auto-seed-report",
        "10403",
        "--sqrt-radii",
        "1",
        "--sqrt-radii",
        "4",
        "--max-steps",
        "5",
        "--artifacts-dir",
        str(tmp_path / "artifacts-json"),
        "--json",
    ])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert rc == 0
    assert captured.err == ""
    assert payload["input"] == {
        "n": "10403",
        "kind": "hostile-semiprime",
    }
    assert payload["selection"] == {
        "mode": "manual",
        "preset": None,
        "sqrt_radii_specs": [[1], [4]],
    }
    assert [run["name"] for run in payload["runs"]] == [
        "sqrt-auto-r1",
        "sqrt-auto-r4",
    ]
    assert payload["summary"] == {
        "input": {
            "n": "10403",
            "kind": "hostile-semiprime",
        },
        "run_count": 2,
        "best_run_name": "sqrt-auto-r1",
        "best_final_status": "built-exact-match",
        "status_counts": {
            "built-exact-match": 1,
            "payloads-nonexact": 1,
        },
    }
    assert "IRSR auto-seed comparison for n=10403" in payload["report"]

def test_irsr_auto_seed_report_accepts_explicit_wide_preset(tmp_path, capsys):
    rc = main([
        "pet",
        "irsr-auto-seed-report",
        "11413",
        "--preset",
        "wide",
        "--max-steps",
        "5",
        "--artifacts-dir",
        str(tmp_path / "artifacts-wide"),
    ])

    captured = capsys.readouterr()

    assert rc == 0
    assert captured.err == ""
    assert "Selection: preset=wide" in captured.out
    assert "Radii specs: [[1], [2, 4]]" in captured.out
    assert "IRSR auto-seed comparison for n=11413" in captured.out
    assert "Best run: sqrt-auto-r2-r4" in captured.out
    assert "Final status: payloads-nonexact" in captured.out
    assert "- sqrt-auto-r1 | radii=[1] | status=no-payload-candidates" in captured.out
    assert "- sqrt-auto-r2-r4 | radii=[2, 4] | status=payloads-nonexact" in captured.out

def test_irsr_auto_seed_report_json_includes_preset_selection(tmp_path, capsys):
    rc = main([
        "pet",
        "irsr-auto-seed-report",
        "11413",
        "--preset",
        "wide",
        "--max-steps",
        "5",
        "--artifacts-dir",
        str(tmp_path / "artifacts-wide-json"),
        "--json",
    ])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert rc == 0
    assert captured.err == ""
    assert payload["selection"] == {
        "mode": "preset",
        "preset": "wide",
        "sqrt_radii_specs": [[1], [2, 4]],
    }
    assert payload["best_run"]["name"] == "sqrt-auto-r2-r4"
    assert payload["best_run"]["final_status"] == "payloads-nonexact"

def test_irsr_auto_seed_report_manual_radii_override_preset(tmp_path, capsys):
    rc = main([
        "pet",
        "irsr-auto-seed-report",
        "10403",
        "--preset",
        "wide",
        "--sqrt-radii",
        "1",
        "--sqrt-radii",
        "4",
        "--max-steps",
        "5",
        "--artifacts-dir",
        str(tmp_path / "artifacts-manual-overrides-preset"),
        "--json",
    ])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert rc == 0
    assert captured.err == ""
    assert payload["selection"] == {
        "mode": "manual",
        "preset": None,
        "sqrt_radii_specs": [[1], [4]],
    }
    assert [run["name"] for run in payload["runs"]] == [
        "sqrt-auto-r1",
        "sqrt-auto-r4",
    ]
    assert payload["best_run"]["name"] == "sqrt-auto-r1"
    assert payload["best_run"]["final_status"] == "built-exact-match"

def test_irsr_auto_seed_report_rejects_non_integer_radii(capsys):
    rc = main([
        "pet",
        "irsr-auto-seed-report",
        "10403",
        "--sqrt-radii",
        "1,x",
    ])

    captured = capsys.readouterr()

    assert rc == 2
    assert captured.out == ""
    assert "ERROR: --sqrt-radii must contain only integers" in captured.err


def test_irsr_auto_seed_report_rejects_negative_radii(capsys):
    rc = main([
        "pet",
        "irsr-auto-seed-report",
        "10403",
        "--sqrt-radii",
        "-1",
    ])

    captured = capsys.readouterr()

    assert rc == 2
    assert captured.out == ""
    assert "ERROR: --sqrt-radii values must be >= 0" in captured.err

