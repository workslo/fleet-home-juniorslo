#!/bin/bash
# Characterization: bin/now — dual-zone output format (offline).
#
# now prints one line: "<Denver datetime>  (<UTC datetime> UTC)".
# This pins the FORMAT (both zones, one line, trailing UTC tag) and the
# INVARIANT (UTC is 6 or 7 hours ahead of Denver — MDT/MST respectively).
# It does not pin the values — time moves.
#
# No network, no fixtures.
# Run: bash tests/test-now.sh

set -u
SCRIPT="$(cd "$(dirname "$0")/.." && pwd)/bin/now"
PASS=0
FAIL=0

echo "=== Test: now (format pin) ==="

OUT=$("$SCRIPT")
RC=$?

echo "Test 1: exits 0"
if [ "$RC" -eq 0 ]; then
    echo "  PASS: exit 0"
    PASS=$((PASS + 1))
else
    echo "  FAIL: exit $RC"
    FAIL=$((FAIL + 1))
fi

echo "Test 2: single line, Denver segment format"
if echo "$OUT" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2} [AP]M (MDT|MST)  \([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2} UTC\)$'; then
    echo "  PASS: full-line format matches"
    PASS=$((PASS + 1))
else
    echo "  FAIL: format mismatch: $OUT"
    FAIL=$((FAIL + 1))
fi

echo "Test 3: Denver and UTC segments are the same moment (6 or 7 h apart)"
DELTA=$(echo "$OUT" | python3 -c "
import sys, re
from datetime import datetime
line = sys.stdin.read().strip()
m = re.match(r'^([0-9-]+ [0-9:]+ [AP]M) (MDT|MST)  \(([0-9-]+) ([0-9:]+) UTC\)$', line)
if not m:
    print('nomatch'); sys.exit(0)
den = datetime.strptime(m.group(1), '%Y-%m-%d %I:%M %p')
utc = datetime.strptime(m.group(3) + ' ' + m.group(4), '%Y-%m-%d %H:%M')
off = 6 if m.group(2) == 'MDT' else 7
delta = (utc - den).total_seconds() / 3600
print(int(delta) if delta == off else 'mismatch')
")
if [ "$DELTA" = "6" ] || [ "$DELTA" = "7" ]; then
    echo "  PASS: offset consistent with zone label ($DELTA h)"
    PASS=$((PASS + 1))
else
    echo "  FAIL: delta=$DELTA (line: $OUT)"
    FAIL=$((FAIL + 1))
fi

echo
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
