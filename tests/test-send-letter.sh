#!/bin/bash
# Characterization: bin/send-letter.sh — --dry-run paths ONLY (offline).
#
# Pins: usage refusal on missing args, letter-file existence gate, empty
# body gate, frontmatter/plain-body parsing (mode + thread detection),
# and the dry-run previews for both SEND and REPLY modes. The dry-run
# branch exits before any HTTP call — never a live send from this suite.
# No real recipients anywhere in fixtures.
#
# No network (dry-run only); temp-dir fixtures only.
# Run: bash tests/test-send-letter.sh

set -u
SCRIPT="$(cd "$(dirname "$0")/.." && pwd)/bin/send-letter.sh"
PASS=0
FAIL=0
T=$(mktemp -d)

check() {
    # check <label> <expected-substring> <haystack>
    if echo "$3" | grep -q "$2"; then
        echo "  PASS: $1"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $1 (expected: $2)"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== Test: send-letter.sh (dry-run paths) ==="

echo "Test 1: no args → usage, exit 1"
out=$(bash "$SCRIPT" 2>&1); rc=$?
[ "$rc" -eq 1 ] && { echo "  PASS: exit 1"; PASS=$((PASS + 1)); } || { echo "  FAIL: rc=$rc"; FAIL=$((FAIL + 1)); }
check "usage printed" "Usage: send-letter.sh" "$out"

echo "Test 2: missing letter file → error, exit 1"
out=$(bash "$SCRIPT" test@example.invalid "s" "$T/no-such-file.md" 2>&1); rc=$?
[ "$rc" -eq 1 ] && { echo "  PASS: exit 1"; PASS=$((PASS + 1)); } || { echo "  FAIL: rc=$rc"; FAIL=$((FAIL + 1)); }
check "file-not-found error" "Letter file not found" "$out"

echo "Test 3: empty body gate → error, exit 1"
printf -- '---\n---\n' > "$T/empty.md"
out=$(bash "$SCRIPT" test@example.invalid "s" "$T/empty.md" --dry-run 2>&1); rc=$?
[ "$rc" -eq 1 ] && { echo "  PASS: exit 1"; PASS=$((PASS + 1)); } || { echo "  FAIL: rc=$rc"; FAIL=$((FAIL + 1)); }
check "empty-body refusal" "extracted body is empty" "$out"

echo "Test 4: plain body, SEND mode dry-run → preview, exit 0"
printf 'Hello Fleet,\n\nA body for the preview.\n' > "$T/plain.md"
out=$(bash "$SCRIPT" test@example.invalid "Test subject" "$T/plain.md" --dry-run 2>&1); rc=$?
[ "$rc" -eq 0 ] && { echo "  PASS: exit 0"; PASS=$((PASS + 1)); } || { echo "  FAIL: rc=$rc (out: $out)"; FAIL=$((FAIL + 1)); }
check "SEND mode" "Mode: SEND (new thread)" "$out"
check "endpoint previewed" "Endpoint:" "$out"
check "dry-run marker" "DRY RUN — not sending." "$out"
check "body length reported" "Body: " "$out"

echo "Test 5: --thread arg → REPLY mode dry-run, exit 0"
out=$(bash "$SCRIPT" test@example.invalid "Re: something" "$T/plain.md" --thread abc-123 --dry-run 2>&1); rc=$?
[ "$rc" -eq 0 ] && { echo "  PASS: exit 0"; PASS=$((PASS + 1)); } || { echo "  FAIL: rc=$rc (out: $out)"; FAIL=$((FAIL + 1)); }
check "REPLY mode" "Mode: REPLY (continuing thread abc-123)" "$out"
check "would-reply preview" "Would fetch thread" "$out"
check "dry-run marker" "DRY RUN — not sending." "$out"

echo "Test 6: frontmatter thread_id auto-detected (no --thread arg)"
printf -- '---\nthread_id: fm-thread-9\n---\nBody after frontmatter.\n' > "$T/fm.md"
out=$(bash "$SCRIPT" test@example.invalid "s" "$T/fm.md" --dry-run 2>&1); rc=$?
[ "$rc" -eq 0 ] && { echo "  PASS: exit 0"; PASS=$((PASS + 1)); } || { echo "  FAIL: rc=$rc (out: $out)"; FAIL=$((FAIL + 1)); }
check "frontmatter thread used" "continuing thread fm-thread-9" "$out"

echo "Test 7: --thread overrides frontmatter thread_id"
out=$(bash "$SCRIPT" test@example.invalid "s" "$T/fm.md" --thread cli-wins --dry-run 2>&1); rc=$?
[ "$rc" -eq 0 ] && { echo "  PASS: exit 0"; PASS=$((PASS + 1)); } || { echo "  FAIL: rc=$rc"; FAIL=$((FAIL + 1)); }
check "CLI thread wins" "continuing thread cli-wins" "$out"

echo "Test 8: archived-letter shape (no leading ---, separator mid-file)"
printf 'Some header prose.\n---\nThe actual letter body.\n' > "$T/arch.md"
out=$(bash "$SCRIPT" test@example.invalid "s" "$T/arch.md" --dry-run 2>&1); rc=$?
[ "$rc" -eq 0 ] && { echo "  PASS: exit 0"; PASS=$((PASS + 1)); } || { echo "  FAIL: rc=$rc (out: $out)"; FAIL=$((FAIL + 1)); }
check "body after separator" "The actual letter body" "$out"

rm -r "$T" 2>/dev/null || true

echo
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
