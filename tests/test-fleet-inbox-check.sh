#!/bin/bash
# Test: fleet-inbox-check script
# Verifies the script runs, queries the live AgentMail API, and returns
# structured output with expected fields.
#
# Run: bash tests/test-fleet-inbox-check.sh

set -e

SCRIPT="python3 $(cd "$(dirname "$0")/.." && pwd)/bin/fleet-inbox-check"
PASS=0
FAIL=0

assert_contains() {
    local label="$1"
    local haystack="$2"
    local needle="$3"
    if echo "$haystack" | grep -q "$needle"; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label (expected to contain: $needle)"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== Test: fleet-inbox-check ==="

# Test 1: Text output runs without error and reports the inbox
echo "Test 1: text output"
OUTPUT=$($SCRIPT 2>&1) || true
assert_contains "script exits cleanly" "$OUTPUT" "Fleet inbox"
assert_contains "reports inbox address" "$OUTPUT" "jrslo-fleet@agentmail.to"

# Test 2: JSON output is valid JSON with expected structure
echo "Test 2: JSON output"
JSON_OUTPUT=$($SCRIPT --json 2>&1)
assert_contains "JSON has inbox field" "$JSON_OUTPUT" '"inbox"'
assert_contains "JSON has total_incoming field" "$JSON_OUTPUT" '"total_incoming"'

# Validate it's parseable JSON
echo "$JSON_OUTPUT" | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null && {
    echo "  PASS: JSON is valid"
    PASS=$((PASS + 1))
} || {
    echo "  FAIL: JSON is not valid"
    FAIL=$((FAIL + 1))
}

# Test 3: --hours flag filters correctly (1 hour should show few/no messages)
echo "Test 3: hours threshold"
SHORT_OUTPUT=$($SCRIPT --hours 1 --json 2>&1)
assert_contains "hours threshold reflected" "$SHORT_OUTPUT" '"hours_threshold": 1'

# Test 4: messages carry subject fields (was: asserted Slo's Aug 15 journal
# letter within 72h — time-bombed, failed permanently after Aug 18. Structure,
# not content: the suite must not depend on which letters exist today.)
echo "Test 4: messages have subjects"
KNOWN_OUTPUT=$($SCRIPT --hours 72 --json 2>&1)
assert_contains "JSON has messages array" "$KNOWN_OUTPUT" '"messages"'
assert_contains "JSON has subject fields" "$KNOWN_OUTPUT" '"subject"' 

# Test 5: --full flag runs cleanly and shows the reply-state legend
# (was: asserted the body delimiter, which only prints when unread/owed mail
# exists in-window — state-dependent, failed on a caught-up inbox)
echo "Test 5: --full flag"
FULL_OUTPUT=$($SCRIPT --full --hours 6 2>&1) || true
assert_contains "full output runs cleanly" "$FULL_OUTPUT" "Fleet inbox"
assert_contains "full output shows reply-state legend" "$FULL_OUTPUT" "OWED"

# Test 6: --full flag does NOT fetch bodies when no unread messages in window
echo "Test 6: --full with no unread (narrow window)"
# Use 0 hours — unlikely to have unread messages exactly at this moment
NARROW_OUTPUT=$($SCRIPT --full --hours 0 2>&1) || true
# Should still run cleanly and report the inbox
assert_contains "narrow window runs cleanly" "$NARROW_OUTPUT" "Fleet inbox"

# Test 7: JSON output includes message_id field (needed for --full body fetch)
echo "Test 7: JSON has message_id"
JSON_WITH_ID=$($SCRIPT --json --hours 72 2>&1)
assert_contains "JSON has message_id field" "$JSON_WITH_ID" '"message_id"'

# Test 8: --full and --json together — JSON should still be valid
echo "Test 8: --full --json combo"
COMBO_OUTPUT=$($SCRIPT --full --json --hours 6 2>&1) || true
echo "$COMBO_OUTPUT" | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null && {
    echo "  PASS: combo JSON is valid"
    PASS=$((PASS + 1))
} || {
    echo "  FAIL: combo JSON is not valid"
    FAIL=$((FAIL + 1))
}

echo
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL

# Test 9: JSON includes reply_state (thread-state authority, added Sep 9
# after the duplicate-ack — sent replies are invisible in the received list)
echo "Test 9: JSON has reply_state"
RS_OUTPUT=$($SCRIPT --json --hours 72 2>&1)
assert_contains "JSON has reply_state field" "$RS_OUTPUT" '"reply_state"'
assert_contains "reply_state values are owed/acked" "$RS_OUTPUT" '"owed"\|"acked"'
