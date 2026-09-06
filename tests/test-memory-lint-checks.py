#!/usr/bin/env python3
"""Test: memory-lint remaining checks (issue #35).

test-memory-lint-two-tier.py covers check 1 (two-tier size caps). This file
covers the rest — each check gets at least one positive test (a known-bad
fixture fires the finding) and one negative test (a clean corpus stays clean):

  - Check 2: orphaned references — [[wikilinks]] to slugs that don't exist
  - Check 3: NOW.md freshness — mtime vs warn/flag thresholds
  - Check 4: buffer age — entries older than the stated consolidation cutoff
  - Check 5: critical files tracked — journal/buffer/NOW/SOUL must be in git

Run: bash tests/run-all.sh   (or: python3 tests/test-memory-lint-checks.py)

No network, no live-corpus dependency — every fixture is a temp directory.
"""
import sys
import os
import time
import tempfile
import shutil
import subprocess
from datetime import datetime, timezone, timedelta

# Import the lint module dynamically — 'memory-lint' has a hyphen,
# which isn't a valid Python module name, so we load it via importlib.
import importlib.util

def load_lint_module(path):
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("memory_lint", path)
    spec = importlib.util.spec_from_loader("memory_lint", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod

LINT_PATH = os.path.join(os.path.dirname(__file__), '..', 'checks', 'memory-lint')
lint = load_lint_module(LINT_PATH)

PASS = 0
FAIL = 0

def check(label, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✓ {label}")
    else:
        FAIL += 1
        print(f"  ✗ {label}")

def make_fake_workspace():
    """Temp workspace with the minimal structure the checks expect."""
    ws = tempfile.mkdtemp(prefix='lint-test-')
    os.makedirs(os.path.join(ws, 'memory/concepts'))
    os.makedirs(os.path.join(ws, 'memory/reference/people'))
    os.makedirs(os.path.join(ws, 'memory/journal'))
    with open(os.path.join(ws, 'NOW.md'), 'w') as f:
        f.write("# test\n")
    return ws

# --- Check 2: orphaned references --------------------------------------

def test_orphaned_link_flags():
    """A wikilink to a slug that exists nowhere → flagged with source page."""
    ws = make_fake_workspace()
    try:
        with open(os.path.join(ws, 'memory/concepts/a.md'), 'w') as f:
            f.write("---\nslug: alpha\n---\nSee [[gamma]] for context.\n")
        issues, warnings = lint.check_orphaned_references(ws)
        check("orphaned: [[gamma]] flagged", len(issues) == 1)
        check("orphaned: names the missing slug", 'gamma' in issues[0])
        check("orphaned: names the source page", 'a.md' in issues[0])
    finally:
        shutil.rmtree(ws)

def test_valid_links_clean():
    """Links to a frontmatter slug, a filename stem, and pipe-display form → clean."""
    ws = make_fake_workspace()
    try:
        with open(os.path.join(ws, 'memory/concepts/a.md'), 'w') as f:
            f.write("---\nslug: alpha\n---\nSee [[alpha]] and [[beta]] and [[beta|the beta page]].\n")
        with open(os.path.join(ws, 'memory/concepts/beta.md'), 'w') as f:
            f.write("beta page, no frontmatter\n")
        issues, warnings = lint.check_orphaned_references(ws)
        check("valid links (slug, stem, pipe-display) all clean", len(issues) == 0)
    finally:
        shutil.rmtree(ws)

def test_reference_only_target_still_flags():
    """A slug that exists only under reference/ is not in the concept slug set → flagged.

    This pins the check's actual contract: valid slugs come from concept pages
    (frontmatter slug + filename stem). Reference pages are recall-only and not
    link targets for the injection pool.
    """
    ws = make_fake_workspace()
    try:
        with open(os.path.join(ws, 'memory/concepts/a.md'), 'w') as f:
            f.write("See [[people-slo]].\n")
        with open(os.path.join(ws, 'memory/reference/people/people-slo.md'), 'w') as f:
            f.write("reference page\n")
        issues, warnings = lint.check_orphaned_references(ws)
        check("reference-only target flagged (concept slug set only)", len(issues) == 1)
    finally:
        shutil.rmtree(ws)

# --- Check 3: NOW.md freshness ------------------------------------------

def set_mtime(path, hours_ago):
    """Set a file's mtime N hours in the past."""
    ts = time.time() - hours_ago * 3600
    os.utime(path, (ts, ts))

def test_now_fresh_clean():
    """NOW.md modified just now → clean, no warnings."""
    ws = make_fake_workspace()
    try:
        issues, warnings = lint.check_now_freshness(ws)
        check("NOW.md fresh: clean", len(issues) == 0 and len(warnings) == 0)
    finally:
        shutil.rmtree(ws)

def test_now_aging_warns():
    """NOW.md ~30h old → warning only (between 24h warn and 48h flag)."""
    ws = make_fake_workspace()
    try:
        set_mtime(os.path.join(ws, 'NOW.md'), 30)
        issues, warnings = lint.check_now_freshness(ws)
        check("NOW.md 30h: warning, not issue", len(issues) == 0 and len(warnings) == 1)
    finally:
        shutil.rmtree(ws)

def test_now_stale_flags():
    """NOW.md ~72h old → issue (past the 48h flag threshold)."""
    ws = make_fake_workspace()
    try:
        set_mtime(os.path.join(ws, 'NOW.md'), 72)
        issues, warnings = lint.check_now_freshness(ws)
        check("NOW.md 72h: flagged stale", len(issues) == 1 and 'STALE' in issues[0])
    finally:
        shutil.rmtree(ws)

def test_now_missing_flags():
    """No NOW.md at all → MISSING issue."""
    ws = make_fake_workspace()
    try:
        os.remove(os.path.join(ws, 'NOW.md'))
        issues, warnings = lint.check_now_freshness(ws)
        check("NOW.md missing: flagged", len(issues) == 1 and 'MISSING' in issues[0])
    finally:
        shutil.rmtree(ws)

# --- Check 4: buffer age -------------------------------------------------

def test_stale_buffer_entry_flags():
    """An entry older than the stated cutoff → STALE ENTRY issue."""
    ws = make_fake_workspace()
    try:
        with open(os.path.join(ws, 'memory/buffer.md'), 'w') as f:
            f.write("# Buffer\n\nCutoff: Sep 2, 1:39 PM.\n\n"
                    "- [Sep 1, 5:00 PM] old entry, past cutoff\n"
                    "- [Sep 3, 10:00 AM] new entry, after cutoff\n")
        issues, warnings = lint.check_buffer_age(ws)
        check("buffer: stale entry flagged", len(issues) == 1 and 'STALE ENTRY' in issues[0])
        check("buffer: new entry not flagged", 'Sep 3' not in issues[0])
    finally:
        shutil.rmtree(ws)

def test_fresh_buffer_clean():
    """All entries after the cutoff → clean."""
    ws = make_fake_workspace()
    try:
        with open(os.path.join(ws, 'memory/buffer.md'), 'w') as f:
            f.write("# Buffer\n\nCutoff: Sep 1, 9:00 AM.\n\n"
                    "- [Sep 2, 8:00 PM] recent one\n"
                    "- [Sep 3, 10:00 AM] recent two\n")
        issues, warnings = lint.check_buffer_age(ws)
        check("buffer: all-fresh entries clean", len(issues) == 0)
    finally:
        shutil.rmtree(ws)

def test_unparseable_cutoff_warns_not_flags():
    """A cutoff the parser can't read → warning note, no false flags."""
    ws = make_fake_workspace()
    try:
        with open(os.path.join(ws, 'memory/buffer.md'), 'w') as f:
            f.write("# Buffer\n\nCutoff: someday soon.\n\n- [Sep 1, 5:00 PM] entry\n")
        issues, warnings = lint.check_buffer_age(ws)
        check("buffer: unparseable cutoff → warning, no issues",
              len(issues) == 0 and len(warnings) == 1 and 'cutoff' in warnings[0])
    finally:
        shutil.rmtree(ws)

def test_missing_buffer_warns():
    """No buffer.md → warning note (skip), not an issue."""
    ws = make_fake_workspace()
    try:
        issues, warnings = lint.check_buffer_age(ws)
        check("buffer: missing file → warning note", len(issues) == 0 and len(warnings) == 1)
    finally:
        shutil.rmtree(ws)

# --- Check 5: critical files tracked in git ------------------------------

def git(ws, *args):
    return subprocess.run(["git", "-C", ws, *args], capture_output=True, text=True)

def write_critical_files(ws):
    """Create the four critical content files on disk."""
    with open(os.path.join(ws, 'memory/journal/journal.md'), 'w') as f:
        f.write("# journal\n")
    with open(os.path.join(ws, 'memory/buffer.md'), 'w') as f:
        f.write("# buffer\n")
    # NOW.md already written by make_fake_workspace
    with open(os.path.join(ws, 'SOUL.md'), 'w') as f:
        f.write("# soul\n")

def test_untracked_critical_files_flag():
    """Critical files on disk but not git-added → UNTRACKED issues (the journal.md class)."""
    ws = make_fake_workspace()
    try:
        write_critical_files(ws)
        git(ws, "init", "-q")
        issues, warnings = lint.check_tracked_critical_files(ws)
        check("tracked: untracked critical files flagged", len(issues) == 4)
        check("tracked: message names the file", all('UNTRACKED' in i for i in issues))
    finally:
        shutil.rmtree(ws)

def test_tracked_critical_files_clean():
    """Critical files git-added → clean."""
    ws = make_fake_workspace()
    try:
        write_critical_files(ws)
        git(ws, "init", "-q")
        git(ws, "add", "memory/journal/journal.md", "memory/buffer.md", "NOW.md", "SOUL.md")
        issues, warnings = lint.check_tracked_critical_files(ws)
        check("tracked: git-added critical files clean", len(issues) == 0 and len(warnings) == 0)
    finally:
        shutil.rmtree(ws)

def test_missing_critical_file_warns():
    """A critical file absent from disk → warning (MISSING ON DISK), not an issue."""
    ws = make_fake_workspace()
    try:
        write_critical_files(ws)
        os.remove(os.path.join(ws, 'SOUL.md'))
        git(ws, "init", "-q")
        git(ws, "add", "memory/journal/journal.md", "memory/buffer.md", "NOW.md")
        issues, warnings = lint.check_tracked_critical_files(ws)
        check("tracked: missing-on-disk → warning", len(issues) == 0
              and len(warnings) == 1 and 'SOUL.md' in warnings[0])
    finally:
        shutil.rmtree(ws)

# --- Main ----------------------------------------------------------------

if __name__ == '__main__':
    print("test-memory-lint-checks — issue #35: coverage for checks 2-5")
    print()

    print("Check 2 — orphaned references:")
    test_orphaned_link_flags()
    test_valid_links_clean()
    test_reference_only_target_still_flags()
    print()

    print("Check 3 — NOW.md freshness:")
    test_now_fresh_clean()
    test_now_aging_warns()
    test_now_stale_flags()
    test_now_missing_flags()
    print()

    print("Check 4 — buffer age:")
    test_stale_buffer_entry_flags()
    test_fresh_buffer_clean()
    test_unparseable_cutoff_warns_not_flags()
    test_missing_buffer_warns()
    print()

    print("Check 5 — critical files tracked in git:")
    test_untracked_critical_files_flag()
    test_tracked_critical_files_clean()
    test_missing_critical_file_warns()
    print()

    print(f"  {PASS} passed, {FAIL} failed")
    sys.exit(0 if FAIL == 0 else 1)
