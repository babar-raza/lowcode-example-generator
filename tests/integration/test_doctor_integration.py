"""Integration tests for the doctor health check system."""

from plugin_examples.health.doctor import (
    check_engineering_hygiene_all,
    format_results_json,
    format_results_text,
    run_all_checks,
)


def test_run_all_checks_returns_minimum_count():
    """run_all_checks must return >= 18 checks (8 core + 10 EHV)."""
    results = run_all_checks()
    assert len(results) >= 18, f"Expected >= 18 checks, got {len(results)}"


def test_ehv_validators_all_present():
    """All EHV-01 through EHV-10 validators must be present in results."""
    results = check_engineering_hygiene_all()
    validator_ids = {r.name for r in results}
    for i in range(1, 11):
        # _ehv_result_to_health_check names: ehv_ehv_XX (validator_id="EHV-XX")
        expected = f"ehv_ehv_{i:02d}"
        assert expected in validator_ids, f"Missing {expected} in doctor results: {validator_ids}"


def test_text_output_contains_markers():
    """Text output must contain status markers for all checks."""
    results = run_all_checks()
    text = format_results_text(results)
    assert "Health Check Results" in text
    assert any(marker in text for marker in ["[OK]", "[!!]", "[XX]", "[--]"])


def test_json_output_is_valid():
    """JSON output must be valid and contain expected fields."""
    import json
    results = run_all_checks()
    json_str = format_results_json(results)
    data = json.loads(json_str)
    # Output may be a dict with "checks" key or a bare list
    checks = data["checks"] if isinstance(data, dict) else data
    assert isinstance(checks, list)
    assert len(checks) >= 18
    for item in checks:
        assert "name" in item
        assert "status" in item
        assert "detail" in item
        assert "required" in item


def test_no_required_checks_fail():
    """No required health check should fail."""
    results = run_all_checks()
    required_failures = [r for r in results if r.required and r.status == "FAIL"]
    assert len(required_failures) == 0, (
        f"Required checks failed: {[(r.name, r.detail) for r in required_failures]}"
    )
