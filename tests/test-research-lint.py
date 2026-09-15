#!/usr/bin/env python3
"""Tests for bin/research-lint.

Creates synthetic markdown files with known dates (stale and fresh),
runs the script, and checks exit codes and output.
Run: python3 /workspace/tests/test_research_lint.py
"""
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone, timedelta

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "bin", "research-lint")
SCRIPT = os.path.normpath(SCRIPT)

now = datetime.now(timezone.utc)


def make_test_file(content):
    """Write content to a temp file and return the path."""
    fd, path = tempfile.mkstemp(suffix=".md", prefix="research-lint-test-")
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


def run_lint(path, window_days=None):
    """Run research-lint on path, return (exit_code, stdout)."""
    cmd = [SCRIPT, path]
    if window_days:
        cmd += ["--window-days", str(window_days)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


def test_fresh_dates_only():
    """All dates within window → exit 0, no stale warning."""
    fresh = now - timedelta(days=30)
    content = f"""# Test Doc

Some claim from {fresh.strftime('%B %d, %Y')}.

## Sources
- [Example](https://example.com) — {fresh.strftime('%Y-%m-%d')}
"""
    path = make_test_file(content)
    try:
        code, out = run_lint(path, window_days=180)
        assert code == 0, f"Expected exit 0, got {code}. Output:\n{out}"
        assert "STALE" not in out, f"Should not flag fresh dates as stale:\n{out}"
        assert "OK:" in out, f"Should report OK for fresh dates:\n{out}"
        print("PASS: test_fresh_dates_only")
    finally:
        os.unlink(path)


def test_stale_dates_flagged():
    """Dates outside window → exit 1, stale warning."""
    stale = now - timedelta(days=400)
    content = f"""# Test Doc

A claim from {stale.strftime('%B %d, %Y')} that is old.

## Sources
- [Old Source](https://example.com) — {stale.strftime('%Y-%m-%d')}
"""
    path = make_test_file(content)
    try:
        code, out = run_lint(path, window_days=180)
        assert code == 1, f"Expected exit 1, got {code}. Output:\n{out}"
        assert "STALE" in out, f"Should flag stale dates:\n{out}"
        print("PASS: test_stale_dates_flagged")
    finally:
        os.unlink(path)


def test_mixed_dates():
    """Some fresh, some stale → exit 1, only stale flagged."""
    fresh = now - timedelta(days=10)
    stale = now - timedelta(days=365)
    content = f"""# Test Doc

Fresh: {fresh.strftime('%Y-%m-%d')}
Stale: {stale.strftime('%Y-%m-%d')}

## Sources
- [Fresh](https://fresh.com) — {fresh.strftime('%B %d, %Y')}
- [Stale](https://stale.com) — {stale.strftime('%B %d, %Y')}
"""
    path = make_test_file(content)
    try:
        code, out = run_lint(path, window_days=180)
        assert code == 1, f"Expected exit 1, got {code}. Output:\n{out}"
        assert "STALE" in out, f"Should flag stale dates:\n{out}"
        print("PASS: test_mixed_dates")
    finally:
        os.unlink(path)


def test_no_sources_section():
    """No Sources section → warning."""
    fresh = now - timedelta(days=5)
    content = f"""# Test Doc

Just some text with a date {fresh.strftime('%Y-%m-%d')}.
No sources section here.
"""
    path = make_test_file(content)
    try:
        code, out = run_lint(path, window_days=180)
        assert "No 'Sources'" in out or "No 'References'" in out, \
            f"Should warn about missing Sources section:\n{out}"
        print("PASS: test_no_sources_section")
    finally:
        os.unlink(path)


def test_no_urls():
    """No URLs → warning."""
    fresh = now - timedelta(days=5)
    content = f"""# Test Doc

Text with date {fresh.strftime('%B %d, %Y')}.

## Sources
No URLs here.
"""
    path = make_test_file(content)
    try:
        code, out = run_lint(path, window_days=180)
        assert "No URLs" in out, f"Should warn about no URLs:\n{out}"
        print("PASS: test_no_urls")
    finally:
        os.unlink(path)


def test_iso_date_format():
    """ISO dates (2026-08-23) parsed correctly."""
    stale_iso = (now - timedelta(days=300)).strftime('%Y-%m-%d')
    fresh_iso = (now - timedelta(days=5)).strftime('%Y-%m-%d')
    content = f"""# Test

Stale: {stale_iso}
Fresh: {fresh_iso}

## Sources
- [A](https://a.com) — {fresh_iso}
"""
    path = make_test_file(content)
    try:
        code, out = run_lint(path, window_days=180)
        assert code == 1, f"Expected exit 1 for mixed ISO dates, got {code}:\n{out}"
        assert "STALE" in out, f"Should flag stale ISO date:\n{out}"
        print("PASS: test_iso_date_format")
    finally:
        os.unlink(path)


def test_month_year_format():
    """Month Year format (July 2026) parsed correctly."""
    stale_my = (now - timedelta(days=400)).strftime('%B %Y')
    content = f"""# Test

Published {stale_my}.

## Sources
- [A](https://a.com) — {stale_my}
"""
    path = make_test_file(content)
    try:
        code, out = run_lint(path, window_days=180)
        assert code == 1, f"Expected exit 1 for stale month-year, got {code}:\n{out}"
        assert "STALE" in out, f"Should flag stale month-year:\n{out}"
        print("PASS: test_month_year_format")
    finally:
        os.unlink(path)


def test_custom_window():
    """Custom window-days works."""
    fresh = now - timedelta(days=10)
    content = f"""# Test

Date: {fresh.strftime('%Y-%m-%d')}

## Sources
- [A](https://a.com) — {fresh.strftime('%Y-%m-%d')}
"""
    path = make_test_file(content)
    try:
        # 10 days ago with a 5-day window should be stale
        code, out = run_lint(path, window_days=5)
        assert code == 1, f"Expected exit 1 with tight window, got {code}:\n{out}"
        assert "STALE" in out, f"Should flag as stale with tight window:\n{out}"

        # 10 days ago with a 30-day window should be clean
        code, out = run_lint(path, window_days=30)
        assert code == 0, f"Expected exit 0 with loose window, got {code}:\n{out}"
        print("PASS: test_custom_window")
    finally:
        os.unlink(path)


def test_missing_file():
    """Missing file → exit 2."""
    code, out = run_lint("/nonexistent/path/file.md")
    assert code == 2, f"Expected exit 2 for missing file, got {code}"
    assert "not found" in out.lower() or "no file" in out.lower(), \
        f"Should report file not found:\n{out}"
    print("PASS: test_missing_file")


def test_no_args():
    """No args → exit 2."""
    code, out = run_lint(None)
    # When path is None, we pass it as a literal "None" — but actually
    # run_lint builds [SCRIPT, None] which is wrong. Let's handle this.
    # Actually the function will pass None as an arg. Let's just call directly.
    result = subprocess.run([SCRIPT], capture_output=True, text=True)
    assert result.returncode == 2, f"Expected exit 2 for no args, got {result.returncode}"
    print("PASS: test_no_args")


def run_lint(path, window_days=None):
    """Run research-lint on path, return (exit_code, stdout+stderr)."""
    if path is None:
        result = subprocess.run([SCRIPT], capture_output=True, text=True)
        return result.returncode, result.stdout + result.stderr
    cmd = [SCRIPT, path]
    if window_days:
        cmd += ["--window-days", str(window_days)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


if __name__ == "__main__":
    tests = [
        test_fresh_dates_only,
        test_stale_dates_flagged,
        test_mixed_dates,
        test_no_sources_section,
        test_no_urls,
        test_iso_date_format,
        test_month_year_format,
        test_custom_window,
        test_missing_file,
        test_no_args,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except (AssertionError, Exception) as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1

    print(f"\n=== {passed} passed, {failed} failed ===")
    sys.exit(1 if failed > 0 else 0)
