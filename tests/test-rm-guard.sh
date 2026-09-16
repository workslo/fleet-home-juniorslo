#!/bin/bash
# Characterization: bin/rm-guard/rm — the Sep 11 standing rule (offline).
#
# Pins the blocklist: recursive + force together is REFUSED with a loud
# stderr message and exit 1; each flag alone (and plain rm) passes through
# to /bin/rm and really deletes. Combined short flags (-rf, -fr) are also
# refused. Pass-through cases delete real temp fixtures — that is the
# behavior being pinned.
#
# No network; temp-dir fixtures only.
# Run: bash tests/test-rm-guard.sh

set -u
GUARD="$(cd "$(dirname "$0")/.." && pwd)/bin/rm-guard/rm"
PASS=0
FAIL=0
T=$(mktemp -d)

assert_refused() {
    local label="$1"
    shift
    local out
    local rc=0
    out=$("$GUARD" "$@" 2>&1 1>/dev/null) || rc=$?
    if [ "$rc" -eq 1 ] && echo "$out" | grep -q "rm-guard: refused"; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (rc=$rc, stderr: $out)"
        FAIL=$((FAIL + 1))
    fi
}

assert_deletes() {
    local label="$1"
    local target="$2"
    shift 2
    local rc=0
    "$GUARD" "$@" >/dev/null 2>&1 || rc=$?
    if [ "$rc" -eq 0 ] && [ ! -e "$target" ]; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (rc=$rc, target exists: $([ -e "$target" ] && echo yes || echo no))"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== Test: rm-guard (blocklist) ==="

echo "Test 1: -rf is refused, target survives"
mkdir -p "$T/v1"; touch "$T/v1/f"
assert_refused "-rf refused" -rf "$T/v1"
[ -d "$T/v1" ] && { echo "  PASS: target survived refusal"; PASS=$((PASS + 1)); } || { echo "  FAIL: target vanished on refusal"; FAIL=$((FAIL + 1)); }

echo "Test 2: -r -f split flags refused"
mkdir -p "$T/v2"; touch "$T/v2/f"
assert_refused "-r -f refused" -r -f "$T/v2"
[ -d "$T/v2" ] && { echo "  PASS: target survived refusal"; PASS=$((PASS + 1)); } || { echo "  FAIL: target vanished on refusal"; FAIL=$((FAIL + 1)); }

echo "Test 3: -fr order-independent refused"
mkdir -p "$T/v3"; touch "$T/v3/f"
assert_refused "-fr refused" -fr "$T/v3"
[ -d "$T/v3" ] && { echo "  PASS: target survived refusal"; PASS=$((PASS + 1)); } || { echo "  FAIL: target vanished on refusal"; FAIL=$((FAIL + 1)); }

echo "Test 4: refusal message cites the standing rule"
out=$("$GUARD" -rf "$T/v3" 2>&1 1>/dev/null) || true
echo "$out" | grep -q "standing rule" && { echo "  PASS: message cites the rule"; PASS=$((PASS + 1)); } || { echo "  FAIL: message: $out"; FAIL=$((FAIL + 1)); }

echo "Test 5: -r alone passes through and deletes"
mkdir -p "$T/v5"; touch "$T/v5/f"
assert_deletes "-r deletes" "$T/v5" -r "$T/v5"

echo "Test 6: -f alone passes through and deletes"
touch "$T/f6"
assert_deletes "-f deletes" "$T/f6" -f "$T/f6"

echo "Test 7: plain rm passes through and deletes"
touch "$T/f7"
assert_deletes "plain rm deletes" "$T/f7" "$T/f7"

echo "Test 8: -R (capital) + -f also refused"
mkdir -p "$T/v8"; touch "$T/v8/f"
assert_refused "-R -f refused" -R -f "$T/v8"
[ -d "$T/v8" ] && { echo "  PASS: target survived refusal"; PASS=$((PASS + 1)); } || { echo "  FAIL: target vanished on refusal"; FAIL=$((FAIL + 1)); }

# cleanup (rm -r is allowed; the guard is not on PATH here)
rm -r "$T" 2>/dev/null || true

echo
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
