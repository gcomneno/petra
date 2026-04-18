from pet.irsr_state import (
    format_hostile_semiprime_auto_seed_comparison_report,
    summarize_hostile_semiprime_auto_seed_comparison,
)


def _comparison_result():
    return {
        "input": {
            "n": "10403",
            "kind": "hostile-semiprime",
        },
        "runs": [
            {
                "name": "sqrt-auto-r1",
                "sqrt_radii": [1],
                "final_status": "built-exact-match",
                "payload_summary": {"payload_count": 1},
                "build_summary": {"built_count": 1, "exact_match_count": 1},
                "run": {
                    "telemetry": {
                        "portfolio_family_refine_counts": {"sqrt-auto": 2},
                    }
                },
            },
            {
                "name": "sqrt-auto-r4",
                "sqrt_radii": [4],
                "final_status": "payloads-nonexact",
                "payload_summary": {"payload_count": 1},
                "build_summary": {"built_count": 0, "exact_match_count": 0},
                "run": {
                    "telemetry": {
                        "portfolio_family_refine_counts": {"sqrt-auto": 2},
                    }
                },
            },
        ],
        "best_run": {
            "name": "sqrt-auto-r1",
            "sqrt_radii": [1],
            "final_status": "built-exact-match",
            "payload_summary": {"payload_count": 1},
            "build_summary": {"built_count": 1, "exact_match_count": 1},
            "run": {
                "telemetry": {
                    "portfolio_family_refine_counts": {"sqrt-auto": 2},
                }
            },
        },
    }


def test_summarize_hostile_semiprime_auto_seed_comparison_reports_operational_summary():
    summary = summarize_hostile_semiprime_auto_seed_comparison(_comparison_result())

    assert summary == {
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


def test_format_hostile_semiprime_auto_seed_comparison_report_emits_readable_multiline_text():
    report = format_hostile_semiprime_auto_seed_comparison_report(_comparison_result())

    assert "IRSR auto-seed comparison for n=10403" in report
    assert "Best run: sqrt-auto-r1" in report
    assert "Final status: built-exact-match" in report
    assert "- sqrt-auto-r1 | radii=[1] | status=built-exact-match | payloads=1 | built=1 | exact=1" in report
    assert "- sqrt-auto-r4 | radii=[4] | status=payloads-nonexact | payloads=1 | built=0 | exact=0" in report


def test_format_hostile_semiprime_auto_seed_comparison_report_handles_empty_run_list():
    result = {
        "input": {
            "n": "11413",
            "kind": "hostile-semiprime",
        },
        "runs": [],
        "best_run": None,
    }

    report = format_hostile_semiprime_auto_seed_comparison_report(result)

    assert "IRSR auto-seed comparison for n=11413" in report
    assert "No runs available." in report
