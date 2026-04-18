import json

from pet.cli import main


def _build_batch_fixture(tmp_path, capsys):
    standard_path = tmp_path / "standard.jsonl"
    wide_path = tmp_path / "wide.jsonl"
    combined_path = tmp_path / "combined.jsonl"

    rc = main([
        "pet",
        "irsr-auto-seed-batch",
        "10403",
        "10403",
        "--jsonl",
        str(standard_path),
    ])
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out == ""
    assert captured.err == ""

    rc = main([
        "pet",
        "irsr-auto-seed-batch",
        "11413",
        "11413",
        "--preset",
        "wide",
        "--jsonl",
        str(wide_path),
    ])
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out == ""
    assert captured.err == ""

    combined_path.write_text(
        standard_path.read_text() + wide_path.read_text(),
        encoding="utf-8",
    )
    return combined_path


def test_irsr_auto_seed_batch_summary_reports_counts_and_matches(tmp_path, capsys):
    combined_path = _build_batch_fixture(tmp_path, capsys)

    rc = main([
        "pet",
        "irsr-auto-seed-batch-summary",
        str(combined_path),
    ])

    captured = capsys.readouterr()

    assert rc == 0
    assert captured.err == ""
    assert f"File: {combined_path}" in captured.out
    assert "Total records: 2" in captured.out
    assert "Best status counts: built-exact-match=1, payloads-nonexact=1" in captured.out
    assert "Best run counts: sqrt-auto-r1=1, sqrt-auto-r2-r4=1" in captured.out
    assert "Matching records: 2" in captured.out
    assert "- n=10403 | best_run=sqrt-auto-r1 | best_status=built-exact-match" in captured.out
    assert "- n=11413 | best_run=sqrt-auto-r2-r4 | best_status=payloads-nonexact" in captured.out


def test_irsr_auto_seed_batch_summary_can_filter_by_status_in_json(tmp_path, capsys):
    combined_path = _build_batch_fixture(tmp_path, capsys)

    rc = main([
        "pet",
        "irsr-auto-seed-batch-summary",
        str(combined_path),
        "--status",
        "payloads-nonexact",
        "--json",
    ])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert rc == 0
    assert captured.err == ""
    assert payload["schema"] == "irsr-auto-seed-batch-summary-v1"
    assert payload["selected_statuses"] == ["payloads-nonexact"]
    assert payload["total_records"] == 2
    assert payload["matching_count"] == 1
    assert payload["matches"] == [
        {
            "n": "11413",
            "best_run_name": "sqrt-auto-r2-r4",
            "best_final_status": "payloads-nonexact",
            "selection_mode": "preset",
            "selection_preset": "wide",
            "sqrt_radii_specs": [[1], [2, 4]],
        }
    ]


def test_irsr_auto_seed_batch_summary_rejects_limit_below_1(tmp_path, capsys):
    combined_path = _build_batch_fixture(tmp_path, capsys)

    rc = main([
        "pet",
        "irsr-auto-seed-batch-summary",
        str(combined_path),
        "--limit",
        "0",
    ])

    captured = capsys.readouterr()

    assert rc == 2
    assert captured.out == ""
    assert "ERROR: --limit must be >= 1" in captured.err
