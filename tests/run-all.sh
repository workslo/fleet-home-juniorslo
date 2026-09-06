#!/usr/bin/env bash
# Run every memory-lint test in one command.
# No network, no live-corpus dependency — all fixtures are temp dirs.
# Usage: bash tests/run-all.sh   (exit 0 = all green)
set -uo pipefail
cd "$(dirname "$0")/.."

fail=0
for t in tests/test-*.py; do
  echo "== $t"
  if ! python3 "$t"; then
    fail=1
    echo "   FAILED: $t"
  fi
  echo
done

if [ "$fail" -eq 0 ]; then
  echo "All memory-lint tests passed."
else
  echo "FAILURES — see above."
fi
exit "$fail"
