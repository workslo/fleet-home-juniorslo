#!/usr/bin/env python3
"""Test: memory-lint link graveyard check (issue #34).

Consolidation passes move pages to archive/ and rename them, but links in
surviving pages rot silently — nothing fails loud when a target disappears.
Check 7 is the structural version. Resolution follows the settled resolver
model (Sep 9, three falsifications): frontmatter `links:` entries and body
wikilinks resolve ONLY against memory/concepts/; anything else routes via
body prose paths, which resolve against the filesystem (explicit archive/
paths are valid redirects, not dead links — issue #34 done-when).

Pinned behaviors:
  - valid concepts frontmatter link / wikilink / body path → clean
  - dead frontmatter link → DEAD LINK with source page + line
  - archived target (frontmatter or wikilink) → ROTTED with archive location
  - reference-tier frontmatter target → UNREACHABLE FORM (route via prose)
  - dead body path (reference/, archive/, concepts/) → DEAD PATH with line
  - .md-suffixed and memory/-prefixed body paths resolve
  - reference-tier pages are NOT scanned as sources
  - blank lines inside the links: list don't break parsing (the-fleet shape)

Run: bash tests/run-all.sh   (or: python3 tests/test-memory-lint-links.py)

No network, no live-corpus dependency — every fixture is a temp directory.
"""
import sys
import os
import tempfile
import shutil

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

def make_ws():
    """Temp workspace with the directory shapes the corpus uses."""
    ws = tempfile.mkdtemp(prefix='links-test-')
    for d in ('memory/concepts', 'memory/concepts/arcs',
              'memory/reference/people', 'memory/reference/projects',
              'memory/archive/concepts-2026-08', 'memory/archive/arcs'):
        os.makedirs(os.path.join(ws, d), exist_ok=True)
    with open(os.path.join(ws, 'NOW.md'), 'w') as f:
        f.write('# test\n')
    return ws

def write(path, content=''):
    with open(path, 'w') as f:
        f.write(content)

def seed(ws):
    """Target fixtures — what source-page links will aim at (or miss)."""
    write(os.path.join(ws, 'memory/concepts/valid-concept.md'), '# valid\n')
    write(os.path.join(ws, 'memory/reference/people/slo.md'), '# slo\n')
    write(os.path.join(ws, 'memory/reference/people/littlebird.md'), '# littlebird\n')
    write(os.path.join(ws, 'memory/archive/concepts-2026-08/moved-page.md'), '# moved\n')
    write(os.path.join(ws, 'memory/archive/concepts-2026-08/old-friend.md'), '# old\n')

# A source page carrying every link form. 1-based line numbers:
#   frontmatter link entries at lines 7-10, body paths at 14-15, wikilinks at 16.
SRC = '''---
title: Source
slug: source-page
tags: [test]
main: source-page
links:
  - "valid-concept — a live concepts target"
  - "moved-page - a target that was archived"
  - "ghost-slug — a target that never existed"
  - "people/slo - an INDEX-form reference-tier target"
---
# Source

Prose paths: `reference/people/slo` plus `archive/concepts-2026-08/old-friend`
and `concepts/valid-concept` but also `reference/projects/ghost-project`.
Wikilinks: [[valid-concept]] and [[moved-page]].
'''

def run(ws):
    return lint.check_link_graveyard(ws)

def test_valid_corpus_clean():
    """Every target resolves → zero issues (the settled forms all pass)."""
    ws = make_ws()
    try:
        seed(ws)
        write(os.path.join(ws, 'memory/concepts/clean-page.md'), '''---
title: Clean
slug: clean-page
links:
  - "valid-concept — live target"
---
Body [[valid-concept]] plus `reference/people/slo` and `archive/concepts-2026-08/old-friend` and `concepts/valid-concept`.
''')
        issues, warnings = run(ws)
        check("all-valid page is clean", len(issues) == 0 and len(warnings) == 0)
    finally:
        shutil.rmtree(ws)

def test_full_page_findings():
    """The SRC page: exactly 5 issues — one per dead/rotted/unreachable form."""
    ws = make_ws()
    try:
        seed(ws)
        write(os.path.join(ws, 'memory/concepts/source-page.md'), SRC)
        issues, warnings = run(ws)
        check("full page: exactly 5 issues", len(issues) == 5)
        check("full page: UNREACHABLE FORM at frontmatter line 10",
              any('UNREACHABLE FORM' in i and 'line 10' in i and 'people/slo' in i for i in issues))
        check("full page: ROTTED frontmatter link at line 8 names the archive location",
              any('ROTTED LINK' in i and 'line 8' in i and 'moved-page' in i
                  and 'archive/concepts-2026-08/moved-page.md' in i for i in issues))
        check("full page: DEAD frontmatter link at line 9",
              any('DEAD LINK' in i and 'line 9' in i and 'ghost-slug' in i for i in issues))
        check("full page: DEAD body path at line 15",
              any('DEAD PATH' in i and 'line 15' in i and 'reference/projects/ghost-project' in i for i in issues))
        check("full page: ROTTED wikilink at line 16",
              any('ROTTED LINK' in i and 'line 16' in i and 'moved-page' in i for i in issues))
        check("full page: no false flag on valid forms",
              not any('valid-concept' in i or 'people/slo"' in i and 'DEAD' in i
                      or 'old-friend' in i for i in issues))
    finally:
        shutil.rmtree(ws)

def test_dead_frontmatter_link_minimal():
    """Minimal page, one dead frontmatter link → 1 issue with page + line."""
    ws = make_ws()
    try:
        write(os.path.join(ws, 'memory/concepts/t.md'), '''---
title: T
slug: t
links:
  - "ghost-slug — dead"
---
Body.
''')
        issues, _ = run(ws)
        check("dead frontmatter link flagged once", len(issues) == 1)
        check("message carries source page and line 5",
              'memory/concepts/t.md' in issues[0] and 'line 5' in issues[0])
    finally:
        shutil.rmtree(ws)

def test_archived_target_message_names_location():
    """ROTTED message tells the reader where the target went."""
    ws = make_ws()
    try:
        seed(ws)
        write(os.path.join(ws, 'memory/concepts/t.md'), '''---
title: T
slug: t
links:
  - "moved-page — archived target"
---
Body.
''')
        issues, _ = run(ws)
        check("rotted message names archive path and resolver rule",
              len(issues) == 1 and 'memory/archive/concepts-2026-08/moved-page.md' in issues[0]
              and 'memory/concepts/' in issues[0])
    finally:
        shutil.rmtree(ws)

def test_reference_tier_frontmatter_unreachable():
    """Frontmatter link to an existing reference page → UNREACHABLE FORM
    (settled Sep 9 rule: frontmatter resolves only against concepts/)."""
    ws = make_ws()
    try:
        seed(ws)
        write(os.path.join(ws, 'memory/concepts/t.md'), '''---
title: T
slug: t
links:
  - "people/slo - reference-tier target"
---
Body.
''')
        issues, _ = run(ws)
        check("unreachable-form flagged", len(issues) == 1 and 'UNREACHABLE FORM' in issues[0])
        check("message says route via body prose",
              'body prose' in issues[0] and 'memory/reference/people/slo.md' in issues[0])
    finally:
        shutil.rmtree(ws)

def test_body_reference_path_dead():
    """Body prose path to a missing reference page → DEAD PATH with line."""
    ws = make_ws()
    try:
        seed(ws)
        write(os.path.join(ws, 'memory/concepts/t.md'), '''---
title: T
slug: t
---
See `reference/projects/ghost-project` for details.
''')
        issues, _ = run(ws)
        check("dead body path flagged with line 5",
              len(issues) == 1 and 'DEAD PATH' in issues[0] and 'line 5' in issues[0])
    finally:
        shutil.rmtree(ws)

def test_body_archive_path_valid():
    """Issue #34 done-when: explicit archive paths that exist are redirects,
    not dead links — must NOT be flagged."""
    ws = make_ws()
    try:
        seed(ws)
        write(os.path.join(ws, 'memory/concepts/t.md'), '''---
title: T
slug: t
---
Split from → `archive/concepts-2026-08/old-friend`.
''')
        issues, _ = run(ws)
        check("valid archive path is clean (redirect, not dead)", len(issues) == 0)
    finally:
        shutil.rmtree(ws)

def test_body_archive_path_dead():
    """Body archive path to a vanished page → DEAD PATH."""
    ws = make_ws()
    try:
        seed(ws)
        write(os.path.join(ws, 'memory/concepts/t.md'), '''---
title: T
slug: t
---
Split from → `archive/concepts-2026-08/vanished`.
''')
        issues, _ = run(ws)
        check("dead archive path flagged", len(issues) == 1 and 'DEAD PATH' in issues[0])
    finally:
        shutil.rmtree(ws)

def test_body_concepts_path_both_ways():
    """concepts/ body paths: valid one clean, dead one flagged."""
    ws = make_ws()
    try:
        seed(ws)
        write(os.path.join(ws, 'memory/concepts/t.md'), '''---
title: T
slug: t
---
See `concepts/valid-concept` and `concepts/ghost`.
''')
        issues, _ = run(ws)
        check("dead concepts/ path flagged, valid one clean",
              len(issues) == 1 and 'concepts/ghost' in issues[0] and 'DEAD PATH' in issues[0])
    finally:
        shutil.rmtree(ws)

def test_md_suffix_and_memory_prefix_forms():
    """.md-suffixed and memory/-prefixed path forms resolve like bare ones."""
    ws = make_ws()
    try:
        seed(ws)
        write(os.path.join(ws, 'memory/concepts/t.md'), '''---
title: T
slug: t
---
See memory/reference/people/slo.md and `reference/people/slo.md` but not memory/reference/people/ghost.md.
''')
        issues, _ = run(ws)
        check("suffixed/prefixed valid paths clean, dead one flagged",
              len(issues) == 1 and 'reference/people/ghost' in issues[0])
    finally:
        shutil.rmtree(ws)

def test_reference_tier_source_not_scanned():
    """Sources are concept pages only — a rotten link inside reference/ is
    known residual debt (gotchas resolver entry), not this check's flag."""
    ws = make_ws()
    try:
        seed(ws)
        write(os.path.join(ws, 'memory/reference/people/rotten.md'),
              'See `reference/projects/ghost-project` and [[ghost-slug]].\n')
        issues, _ = run(ws)
        check("reference-tier source not scanned", len(issues) == 0)
    finally:
        shutil.rmtree(ws)

def test_blank_line_inside_links_list():
    """the-fleet.md shape: blank line between entry groups — parser survives."""
    ws = make_ws()
    try:
        seed(ws)
        write(os.path.join(ws, 'memory/concepts/t.md'), '''---
title: T
slug: t
links:
  - "valid-concept — live"

  - "ghost-slug — dead after the blank line"
---
Body.
''')
        issues, _ = run(ws)
        check("entry after blank line still parsed and flagged",
              len(issues) == 1 and 'ghost-slug' in issues[0] and 'line 7' in issues[0])
    finally:
        shutil.rmtree(ws)

def test_truncated_glob_not_flagged():
    """A truncated glob mention (archive/concepts-*) is ambiguous — skip."""
    ws = make_ws()
    try:
        seed(ws)
        write(os.path.join(ws, 'memory/concepts/t.md'), '''---
title: T
slug: t
---
Old pages live under archive/concepts-* somewhere.
''')
        issues, _ = run(ws)
        check("truncated glob mention not flagged", len(issues) == 0)
    finally:
        shutil.rmtree(ws)

def test_no_concept_pages_warns():
    """Empty concepts dir → NOTE warning, no crash, no issues."""
    ws = make_ws()
    try:
        issues, warnings = run(ws)
        check("no concepts → warning note, zero issues",
              len(issues) == 0 and len(warnings) == 1 and 'no concept pages' in warnings[0])
    finally:
        shutil.rmtree(ws)

def test_bare_slug_reference_link_unreachable():
    """Bare-slug frontmatter link aimed at a reference page (the live
    'littlebird' shape): the page exists — UNREACHABLE FORM naming it,
    not a false DEAD 'no page anywhere' claim."""
    ws = make_ws()
    try:
        seed(ws)
        write(os.path.join(ws, 'memory/concepts/t.md'), '''---
title: T
slug: t
links:
  - "littlebird — painter and messenger"
---
Body.
''')
        issues, _ = run(ws)
        check("bare slug to reference page → UNREACHABLE FORM, not DEAD",
              len(issues) == 1 and 'UNREACHABLE FORM' in issues[0]
              and 'memory/reference/people/littlebird.md' in issues[0])
    finally:
        shutil.rmtree(ws)

def test_explicit_archive_path_in_frontmatter_unreachable():
    """A frontmatter entry that already points into archive/ (the-fleet.md
    line 26 shape): the page is where it says — the problem is the FORM
    (frontmatter resolves only against concepts/). UNREACHABLE FORM, not a
    nonsense 'moved to where it already points' ROTTED."""
    ws = make_ws()
    try:
        seed(ws)
        write(os.path.join(ws, 'memory/concepts/t.md'), '''---
title: T
slug: t
links:
  - "archive/concepts-2026-08/old-friend - already points at archive"
---
Body.
''')
        issues, _ = run(ws)
        check("explicit archive path in frontmatter → UNREACHABLE FORM naming location",
              len(issues) == 1 and 'UNREACHABLE FORM' in issues[0]
              and 'memory/archive/concepts-2026-08/old-friend.md' in issues[0])
    finally:
        shutil.rmtree(ws)

def test_check_wired_into_main():
    """The check must actually run in the default suite (wiring guard)."""
    src = open(LINT_PATH).read()
    check("check 7 registered in main() checks list",
          '("7. Link graveyard (concept-page links)", check_link_graveyard)' in src)


if __name__ == '__main__':
    print("test-memory-lint-links — issue #34: link graveyard check")
    print()

    test_valid_corpus_clean()
    test_full_page_findings()
    test_dead_frontmatter_link_minimal()
    test_archived_target_message_names_location()
    test_reference_tier_frontmatter_unreachable()
    test_body_reference_path_dead()
    test_body_archive_path_valid()
    test_body_archive_path_dead()
    test_body_concepts_path_both_ways()
    test_md_suffix_and_memory_prefix_forms()
    test_reference_tier_source_not_scanned()
    test_blank_line_inside_links_list()
    test_truncated_glob_not_flagged()
    test_no_concept_pages_warns()
    test_bare_slug_reference_link_unreachable()
    test_explicit_archive_path_in_frontmatter_unreachable()
    test_check_wired_into_main()

    print()
    print(f"  {PASS} passed, {FAIL} failed")
    sys.exit(0 if FAIL == 0 else 1)
