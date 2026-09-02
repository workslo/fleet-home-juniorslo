#!/usr/bin/env python3
"""Test: memory-lint two-tier caps (issue #30).

The lint tool had a category error — it applied a 5K cap designed for
injection-weight (concepts/) to reference pages that cost zero tokens
per conversation. This test verifies the two-tier fix:

  - concept pages > 5K chars → flagged (injection pool, real cost)
  - reference pages > 5K but < 25K → NOT flagged (recall-only, zero cost)
  - reference pages > 25K → flagged (genuinely too large for recall)
  - concept pages < 5K → clean

Run: python3 tests/test-memory-lint-two-tier.py
"""
import sys
import os
import tempfile
import shutil

# Import the lint module dynamically — 'memory-lint' has a hyphen,
# which isn't a valid Python module name, so we load it via importlib.
import importlib.util

def load_lint_module(path):
    # spec_from_file_location returns None for files without .py extension,
    # so we use an explicit SourceFileLoader.
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
    """Create a temp workspace with the minimal directory structure."""
    ws = tempfile.mkdtemp(prefix='lint-test-')
    os.makedirs(os.path.join(ws, 'memory/concepts'))
    os.makedirs(os.path.join(ws, 'memory/reference/people'))
    os.makedirs(os.path.join(ws, 'memory/reference/projects'))
    # NOW.md and buffer.md so those checks don't error
    with open(os.path.join(ws, 'NOW.md'), 'w') as f:
        f.write("# test\n")
    return ws

def write_page(path, size_chars):
    """Write a .md file of approximately size_chars bytes."""
    content = '#' + ('x' * (size_chars - 1))
    with open(path, 'w') as f:
        f.write(content[:size_chars])

def test_concept_over_cap_flags():
    """A concept page > 5K should be flagged."""
    ws = make_fake_workspace()
    try:
        write_page(os.path.join(ws, 'memory/concepts/big.md'), 6000)
        issues, warnings = lint.check_page_sizes(ws)
        check("concept page >5K is flagged", len(issues) == 1 and 'big.md' in issues[0])
    finally:
        shutil.rmtree(ws)

def test_concept_under_cap_clean():
    """A concept page < 5K should be clean."""
    ws = make_fake_workspace()
    try:
        write_page(os.path.join(ws, 'memory/concepts/small.md'), 3000)
        issues, warnings = lint.check_page_sizes(ws)
        check("concept page <5K is clean", len(issues) == 0)
    finally:
        shutil.rmtree(ws)

def test_reference_over_old_cap_under_new_cap_clean():
    """A reference page at 10K should NOT be flagged (under 25K reference cap).

    This is the core fix — the old single 5K cap would have flagged this.
    The two-tier model recognizes that reference/ costs zero per-conversation.
    """
    ws = make_fake_workspace()
    try:
        write_page(os.path.join(ws, 'memory/reference/people/slo.md'), 10000)
        issues, warnings = lint.check_page_sizes(ws)
        check("reference page at 10K is NOT flagged (under 25K ref cap)", len(issues) == 0)
    finally:
        shutil.rmtree(ws)

def test_reference_people_over_new_cap_flags():
    """A people page > 25K should be flagged."""
    ws = make_fake_workspace()
    try:
        write_page(os.path.join(ws, 'memory/reference/people/huge.md'), 26000)
        issues, warnings = lint.check_page_sizes(ws)
        check("reference people page >25K is flagged", len(issues) == 1 and 'huge.md' in issues[0])
    finally:
        shutil.rmtree(ws)

def test_reference_projects_scanned():
    """A projects page > 25K should also be flagged (scan covers all reference/)."""
    ws = make_fake_workspace()
    try:
        write_page(os.path.join(ws, 'memory/reference/projects/big.md'), 26000)
        issues, warnings = lint.check_page_sizes(ws)
        check("reference projects page >25K is flagged (recursive scan)", len(issues) == 1 and 'big.md' in issues[0])
    finally:
        shutil.rmtree(ws)

def test_reference_projects_under_cap_clean():
    """A projects page at 15K should be clean (under 25K, was never scanned before)."""
    ws = make_fake_workspace()
    try:
        write_page(os.path.join(ws, 'memory/reference/projects/medium.md'), 15000)
        issues, warnings = lint.check_page_sizes(ws)
        check("reference projects page at 15K is clean", len(issues) == 0)
    finally:
        shutil.rmtree(ws)

def test_mixed_scenario():
    """Realistic mix: one concept over cap, one reference over old-cap-under-new-cap,
    one reference over new cap. Only concept + huge reference should flag."""
    ws = make_fake_workspace()
    try:
        write_page(os.path.join(ws, 'memory/concepts/core.md'), 6000)        # flags (concept >5K)
        write_page(os.path.join(ws, 'memory/concepts/lean.md'), 4000)        # clean
        write_page(os.path.join(ws, 'memory/reference/people/slo.md'), 18000) # clean (ref <25K)
        write_page(os.path.join(ws, 'memory/reference/projects/big.md'), 26000) # flags (ref >25K)
        issues, warnings = lint.check_page_sizes(ws)
        check("mixed: exactly 2 issues flagged", len(issues) == 2)
        check("mixed: concept core.md flagged", any('core.md' in i for i in issues))
        check("mixed: reference big.md flagged", any('big.md' in i for i in issues))
        check("mixed: reference slo.md NOT flagged", not any('slo.md' in i for i in issues))
    finally:
        shutil.rmtree(ws)


if __name__ == '__main__':
    print("test-memory-lint-two-tier — issue #30: two-tier caps")
    print()

    test_concept_over_cap_flags()
    test_concept_under_cap_clean()
    test_reference_over_old_cap_under_new_cap_clean()
    test_reference_people_over_new_cap_flags()
    test_reference_projects_scanned()
    test_reference_projects_under_cap_clean()
    test_mixed_scenario()

    print()
    print(f"  {PASS} passed, {FAIL} failed")
    sys.exit(0 if FAIL == 0 else 1)
