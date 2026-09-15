#!/bin/bash
# Characterization: fleet-issue-check — bare-run refusal class (offline).
#
# The tool's live path (GitHub API via wrapper-minted token) runs in
# heartbeats and sessions; this suite pins the no-token gate: the tool
# must refuse BEFORE any network call, printing the wrapper instruction
# on stderr and exiting 1. Flags must not bypass the gate.
#
# No network, no credentials, no fixtures.
# Run: bash tests/test-fleet-issue-check.sh

set -u
SCRIPT="$(cd "$(dirname "$0")/.." && pwd)/bin/fleet-issue-check"
PASS=0
FAIL=0

assert_refused() {
    local label="$1"
    shift
    local stderr_out
    local rc=0
    stderr_out=$(env -u GH_TOKEN -u GITHUB_TOKEN "$@" 2>&1 1>/dev/null) || rc=$?
    if [ "$rc" -eq 1 ] && echo "$stderr_out" | grep -q "no GH_TOKEN/GITHUB_TOKEN in env"; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (rc=$rc, stderr: $stderr_out)"
        FAIL=$((FAIL + 1))
    fi
}

assert_mentions_wrapper() {
    local label="$1"
    local stderr_out
    stderr_out=$(env -u GH_TOKEN -u GITHUB_TOKEN python3 "$SCRIPT" 2>&1 1>/dev/null)
    if echo "$stderr_out" | grep -q "gh-app-token.mjs -- python3 bin/fleet-issue-check"; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== Test: fleet-issue-check (refusal class) ==="

echo "Test 1: bare run without token refuses"
assert_refused "exit 1 + refusal message" python3 "$SCRIPT"

echo "Test 2: refusal names the wrapper invocation"
assert_mentions_wrapper "stderr carries the wrapper instruction"

echo "Test 3: flags do not bypass the gate"
assert_refused "--json still refused without token" python3 "$SCRIPT" --json
assert_refused "--hours still refused without token" python3 "$SCRIPT" --hours 5

echo "Test 4: empty-string token is treated as absent"
local_out=$(GH_TOKEN="" GITHUB_TOKEN="" python3 "$SCRIPT" 2>&1 1>/dev/null) || true
if echo "$local_out" | grep -q "no GH_TOKEN/GITHUB_TOKEN in env"; then
    echo "  PASS: empty token refused"
    PASS=$((PASS + 1))
else
    echo "  FAIL: empty token not refused (stderr: $local_out)"
    FAIL=$((FAIL + 1))
fi

echo
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
