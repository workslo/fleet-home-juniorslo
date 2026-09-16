#!/usr/bin/env bash
# Run every discovered test suite in tests/ in one command.
# Memory-lint suites: no network, no live-corpus dependency — all fixtures
# are temp dirs. Discovery (bin/ move-out, issue #70):
#   tests/test-*.py  → python3
#   tests/test-*.sh  → bash
#   tests/*.test.mjs → bun when present; skip-with-note otherwise (their
#                      pin receipts carry the coverage — bun-in-CI is a
#                      future infra question, not a suite problem).
#                      .mjs suites keep bun's native `.test.mjs` suffix:
#                      bun REFUSES files without .test/_test_/.spec in the
#                      name (caught live in the #70 build — a hyphen-prefix
#                      rename made bun skip the suite silently).
# Known live-API suite: tests/test-fleet-inbox-check.sh queries the real
# AgentMail inbox (network + vault credential at run time); its behavior
# is additionally pinned in experiments/bin-move-out/pin-receipts.md.
# Usage: bash tests/run-all.sh   (exit 0 = all green)
set -uo pipefail
cd "$(dirname "$0")/.."

fail=0

for t in tests/test-*.py; do
  [ -e "$t" ] || continue
  echo "== $t"
  if ! python3 "$t"; then
    fail=1
    echo "   FAILED: $t"
  fi
  echo
done

for t in tests/test-*.sh; do
  [ -e "$t" ] || continue
  echo "== $t"
  if ! bash "$t"; then
    fail=1
    echo "   FAILED: $t"
  fi
  echo
done

if command -v bun >/dev/null 2>&1; then
  for t in tests/*.test.mjs; do
    [ -e "$t" ] || continue
    echo "== $t"
    if ! bun test "$t"; then
      fail=1
      echo "   FAILED: $t"
    fi
    echo
  done
else
  echo "== tests/*.test.mjs: SKIPPED (bun absent) — coverage carried by pin receipts (experiments/bin-move-out/pin-receipts.md)"
  echo
fi

if [ "$fail" -eq 0 ]; then
  echo "All discovered tests passed."
else
  echo "FAILURES — see above."
fi
exit "$fail"
