#!/usr/bin/env python3
"""Tests for memory-lint check 6: dual-zone stamp consistency.

The check exists because consolidation passes hand-compose stamps and got
the zone wrong three times (Sep 1, Sep 5, Sep 6) — e.g. "9:39 PM MDT
(21:39 UTC)" reads 24h UTC as a PM local time; 21:39 UTC is 3:39 PM MDT.
Check 6 makes the next instance fail loud within 24h.

Stamps in these tests are derived from the real clock (now − 1h) so they
stay valid whenever the suite runs, across DST boundaries and years.
"""
import os
import sys
import tempfile
import unittest
import importlib.util
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader

LINT = os.path.join(os.path.dirname(__file__), "..", "checks", "memory-lint")
loader = SourceFileLoader("memory_lint", LINT)
spec = importlib.util.spec_from_loader("memory_lint", loader)
memory_lint = importlib.util.module_from_spec(spec)
loader.exec_module(memory_lint)

DENVER = ZoneInfo("America/Denver")


def fmt_12h(dt):
    return dt.strftime("%I:%M %p").lstrip("0")


def make_stamps(offset_hours=-1):
    """Return (local_line_fragment, utc_24h, utc_12h) for now + offset."""
    utc = datetime.now(timezone.utc) + timedelta(hours=offset_hours)
    local = utc.astimezone(DENVER)
    date_part = local.strftime("%b %-d,")
    local_part = f"{date_part} {fmt_12h(local)} {local.strftime('%Z')}"
    return local_part, utc.strftime("%H:%M"), f"{fmt_12h(utc)}"


def flip_ampm(time12):
    """'3:39 PM' -> '3:39 AM' and vice versa."""
    return time12.replace("AM", "**").replace("PM", "AM").replace("**", "PM")


def make_ws(now_line, recent_line, cutoff_line):
    ws = tempfile.mkdtemp()
    with open(os.path.join(ws, "NOW.md"), "w") as f:
        f.write(now_line + "\n")
    os.makedirs(os.path.join(ws, "memory"), exist_ok=True)
    with open(os.path.join(ws, "memory", "recent.md"), "w") as f:
        f.write(recent_line + "\n")
    with open(os.path.join(ws, "memory", "buffer.md"), "w") as f:
        f.write("# Buffer\n\nCutoff: " + cutoff_line + ".\n")
    return ws


class CheckStampConsistency(unittest.TestCase):
    def test_clean_24h_utc_form(self):
        local, utc24, _ = make_stamps()
        ws = make_ws(
            f"# {local}.",
            f"# {local} ({utc24} UTC).",
            f"{local} ({utc24} UTC)",
        )
        issues, warnings = memory_lint.check_stamp_consistency(ws)
        self.assertEqual(issues, [])
        self.assertEqual(warnings, [])

    def test_clean_12h_utc_form(self):
        local, _, utc12 = make_stamps()
        ws = make_ws(
            f"# {local}.",
            f"# {local} ({utc12} UTC).",
            f"{local} ({utc12} UTC)",
        )
        issues, warnings = memory_lint.check_stamp_consistency(ws)
        self.assertEqual(issues, [])
        self.assertEqual(warnings, [])

    def test_flags_pm_flip_in_local(self):
        """The Sep 6 class: 21:39 UTC rendered as '9:39 PM' in the MDT slot."""
        local, utc24, _ = make_stamps()
        hh, mm, ap = local.split(" ")[-2], local.split(" ")[-1], None
        # local fragment shape: "Sep 6, 3:39 PM MDT" — flip the AM/PM token
        parts = local.split(" ")
        parts[-2] = flip_ampm(parts[-2])
        flipped = " ".join(parts)
        ws = make_ws(f"# {flipped} ({utc24} UTC).", f"# {local} ({utc24} UTC).", f"{local} ({utc24} UTC)")
        issues, _ = memory_lint.check_stamp_consistency(ws)
        self.assertEqual(len(issues), 1)
        self.assertIn("STAMP MISMATCH", issues[0])
        self.assertIn("NOW.md", issues[0])

    def test_flags_both_sides_wrong(self):
        """The recent.md Sep 6 shape: '9:40 PM MDT (3:40 PM UTC)' for 21:40 UTC.

        Fixed stamps, not clock-derived: the real 21:40 UTC was 3:40 PM MDT,
        hand-composed as '9:40 PM MDT (3:40 PM UTC)'. Stated local 21:40
        Denver = 03:40 UTC, stamp says 15:40 UTC -> flagged. (A clock-derived
        version of this fixture is flaky: for some UTC hours the swapped
        pair is accidentally self-consistent and flags nothing — caught
        live Sep 7 ~7 PM MDT / 01:xx UTC; fixed in the fleet-home port first.)
        """
        local = "Sep 6, 3:40 PM MDT"
        utc12 = "21:40"
        wrong = "Sep 6, 9:40 PM MDT (3:40 PM UTC)"
        ws = make_ws(f"# {local}.", f"# {wrong}.", f"{local} ({utc12} UTC)")
        issues, _ = memory_lint.check_stamp_consistency(ws)
        self.assertEqual(len(issues), 1)
        self.assertIn("STAMP MISMATCH", issues[0])
        self.assertIn("recent.md", issues[0])

    def test_flags_future_stamp(self):
        local, utc24, _ = make_stamps(offset_hours=+2)
        ws = make_ws(f"# {local} ({utc24} UTC).", f"# {local} ({utc24} UTC).", f"{local} ({utc24} UTC)")
        issues, _ = memory_lint.check_stamp_consistency(ws)
        self.assertEqual(len(issues), 3)
        self.assertTrue(all("STAMP IN FUTURE" in i for i in issues))

    def test_skips_local_only_stamp(self):
        local, _, _ = make_stamps()
        ws = make_ws(f"# {local}.", f"# {local}.", local)
        issues, warnings = memory_lint.check_stamp_consistency(ws)
        self.assertEqual(issues, [])
        self.assertEqual(warnings, [])

    # --- Phase 2: local-only stamps (Sep 8, 2026) -------------------------
    # On Sep 8 an entire day of archive/buffer/recent stamps sat ~6h wrong
    # (raw UTC clock read as local) and phase 1 saw none of it — local-only
    # stamps were skipped by design. These tests pin the two new rules.

    def _write_buffer_entry(self, ws, stamp_fragment):
        with open(os.path.join(ws, "memory", "buffer.md"), "a") as f:
            f.write(f"- [{stamp_fragment}] Entry text\n")

    def _write_archive_entry(self, ws, stamp_fragment):
        arch = os.path.join(ws, "memory", "archive")
        os.makedirs(arch, exist_ok=True)
        with open(os.path.join(arch, "2026-09-08.md"), "a") as f:
            f.write(f"- [{stamp_fragment}] Entry text\n")

    def test_flags_local_only_future_recent_header(self):
        """The Sep 8 live shape: recent.md line 1 'Sep 8, ~9:41 PM cutoff'
        written at 3:41 PM MDT — a local-only stamp hours in the future."""
        local, _, _ = make_stamps()
        local_future, _, _ = make_stamps(offset_hours=+2)
        ws = make_ws(f"# {local}.", f"# {local_future} cutoff.", local)
        issues, _ = memory_lint.check_stamp_consistency(ws)
        self.assertEqual(len(issues), 1)
        self.assertIn("LOCAL-ONLY STAMP IN FUTURE", issues[0])
        self.assertIn("recent.md", issues[0])

    def test_flags_local_only_future_buffer_entry(self):
        local, _, _ = make_stamps()
        local_future, _, _ = make_stamps(offset_hours=+2)
        ws = make_ws(f"# {local}.", f"# {local}.", local)
        self._write_buffer_entry(ws, local_future)
        issues, _ = memory_lint.check_stamp_consistency(ws)
        self.assertEqual(len(issues), 1)
        self.assertIn("LOCAL-ONLY STAMP IN FUTURE", issues[0])
        self.assertIn("buffer.md", issues[0])

    def test_flags_local_only_future_archive_entry(self):
        local, _, _ = make_stamps()
        local_future, _, _ = make_stamps(offset_hours=+2)
        ws = make_ws(f"# {local}.", f"# {local}.", local)
        self._write_archive_entry(ws, local_future)
        issues, _ = memory_lint.check_stamp_consistency(ws)
        self.assertEqual(len(issues), 1)
        self.assertIn("LOCAL-ONLY STAMP IN FUTURE", issues[0])
        self.assertIn("archive", issues[0])

    def test_flags_stamp_later_than_last_write(self):
        """The mtime rule: a PAST stamp that still claims a write moment
        after the file's last write (UTC-as-local always claims +6h)."""
        local, _, _ = make_stamps()
        cutoff_old, _, _ = make_stamps(offset_hours=-4)
        local_30m_ago, _, _ = make_stamps(offset_hours=-0.5)
        ws = make_ws(f"# {local}.", f"# {local}.", cutoff_old)
        self._write_buffer_entry(ws, local_30m_ago)
        bpath = os.path.join(ws, "memory", "buffer.md")
        old = datetime.now(timezone.utc) - timedelta(hours=3)
        os.utime(bpath, (old.timestamp(), old.timestamp()))
        issues, _ = memory_lint.check_stamp_consistency(ws)
        self.assertEqual(len(issues), 1)
        self.assertIn("STAMP LATER THAN LAST WRITE", issues[0])
        self.assertIn("buffer.md", issues[0])

    def test_clean_local_only_past_entries_all_surfaces(self):
        """Correct local-only stamps (past, mtime-consistent) stay silent."""
        local, _, _ = make_stamps(offset_hours=-2)
        ws = make_ws(f"# {local}.", f"# {local} cutoff.", local)
        self._write_buffer_entry(ws, local)
        self._write_archive_entry(ws, local)
        issues, warnings = memory_lint.check_stamp_consistency(ws)
        self.assertEqual(issues, [])
        self.assertEqual(warnings, [])

    def test_paired_stamp_not_double_flagged(self):
        """A paired stamp is judged once (phase 1); phase 2 must not re-flag
        the local half of the pair."""
        local, utc24, _ = make_stamps(offset_hours=+2)
        ws = make_ws(f"# {local}.", f"# {local} ({utc24} UTC).", local)
        issues, _ = memory_lint.check_stamp_consistency(ws)
        recent_issues = [i for i in issues if "recent.md" in i]
        self.assertEqual(len(recent_issues), 1)
        self.assertIn("STAMP IN FUTURE", recent_issues[0])


if __name__ == "__main__":
    unittest.main()
