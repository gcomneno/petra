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
    assert "IRSR auto-seed comparison for n=10403" in captured.out
    assert "Best run: sqrt-auto-r1" in captured.out
    assert "Final status: built-exact-match" in captured.out
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
