import json

from pet.cli import main


def test_irsr_auto_seed_batch_writes_compact_jsonl_with_standard_preset(tmp_path, capsys):
    jsonl_path = tmp_path / "batch.jsonl"

    rc = main([
        "pet",
        "irsr-auto-seed-batch",
        "10403",
        "10403",
        "--jsonl",
        str(jsonl_path),
    ])

    captured = capsys.readouterr()
    rows = [json.loads(line) for line in jsonl_path.read_text().splitlines()]

    assert rc == 0
    assert captured.out == ""
    assert captured.err == ""
    assert len(rows) == 1

    row = rows[0]
    assert row["schema"] == "irsr-auto-seed-report-batch-v1"
    assert row["json_mode"] == "compact"
    assert row["selection"] == {
        "mode": "preset",
        "preset": "standard",
        "sqrt_radii_specs": [[1], [4]],
    }
    assert row["summary"] == {
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
    assert "run" not in row["runs"][0]
    assert row["best_run"]["name"] == "sqrt-auto-r1"
    assert row["best_run"]["final_status"] == "built-exact-match"


def test_irsr_auto_seed_batch_writes_compact_jsonl_with_wide_preset(tmp_path, capsys):
    jsonl_path = tmp_path / "batch-wide.jsonl"

    rc = main([
        "pet",
        "irsr-auto-seed-batch",
        "11413",
        "11413",
        "--preset",
        "wide",
        "--jsonl",
        str(jsonl_path),
    ])

    captured = capsys.readouterr()
    rows = [json.loads(line) for line in jsonl_path.read_text().splitlines()]

    assert rc == 0
    assert captured.out == ""
    assert captured.err == ""
    assert len(rows) == 1

    row = rows[0]
    assert row["selection"] == {
        "mode": "preset",
        "preset": "wide",
        "sqrt_radii_specs": [[1], [2, 4]],
    }
    assert "run" not in row["runs"][0]
    assert row["best_run"]["name"] == "sqrt-auto-r2-r4"
    assert row["best_run"]["final_status"] == "payloads-nonexact"


def test_irsr_auto_seed_batch_rejects_start_below_2(capsys):
    rc = main([
        "pet",
        "irsr-auto-seed-batch",
        "1",
        "10",
        "--jsonl",
        "out.jsonl",
    ])

    captured = capsys.readouterr()

    assert rc == 2
    assert captured.out == ""
    assert "ERROR: irsr-auto-seed-batch expects START >= 2" in captured.err


def test_irsr_auto_seed_batch_rejects_end_below_start(capsys):
    rc = main([
        "pet",
        "irsr-auto-seed-batch",
        "10",
        "9",
        "--jsonl",
        "out.jsonl",
    ])

    captured = capsys.readouterr()

    assert rc == 2
    assert captured.out == ""
    assert "ERROR: --end must be >= --start" in captured.err
