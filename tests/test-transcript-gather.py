#!/usr/bin/env python3
"""Characterization: bin/transcript-gather.py — arg handling + output shape (offline).

Pins the interface, not live transcript reads: a date with no conversations
(1999-01-01 — before this workspace existed) against a TEMP WORKSPACE
(the tool's WORKSPACE env override), so no live corpus is touched and the
only writes land in the temp dir. Structure, not content: the suite must
not depend on which conversations exist today.

No network; temp-dir fixtures only.
Run: python3 tests/test-transcript-gather.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "bin", "transcript-gather.py")
EMPTY_DATE = "1999-01-01"


def run_gather(extra_args, workspace):
    env = dict(os.environ, WORKSPACE=workspace)
    # Strip variables that could leak a live workspace in
    env.pop("GH_TOKEN", None)
    return subprocess.run(
        [sys.executable, SCRIPT, EMPTY_DATE, *extra_args],
        capture_output=True, text=True, env=env, timeout=60,
    )


class TestTranscriptGather(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="tg-char-")
        # conversations dir the tool will glob (empty — no matches for any date)
        os.makedirs(os.path.join(self.tmp, "conversations"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_text_mode_summary_shape(self):
        r = run_gather([], self.tmp)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn(f"Gathered {EMPTY_DATE}: 0 conversations", r.stdout)
        self.assertIn("Journal entry found:", r.stdout)

    def test_json_mode_structure(self):
        r = run_gather(["--json"], self.tmp)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual(data["date"], EMPTY_DATE)
        self.assertEqual(data["conversations"], 0)
        self.assertEqual(data["excluded"], 0)
        self.assertEqual(data["messages"], 0)
        self.assertIsInstance(data["journal_found"], bool)
        # journal does not exist in the temp workspace → False
        self.assertFalse(data["journal_found"])
        self.assertTrue(data["output_path"].endswith(f"{EMPTY_DATE}-input.md"))

    def test_output_file_written_into_temp_workspace(self):
        r = run_gather(["--json"], self.tmp)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        out = json.loads(r.stdout)["output_path"]
        self.assertTrue(out.startswith(self.tmp), msg=out)
        self.assertTrue(os.path.exists(out))

    def test_interactive_only_flag_accepted(self):
        r = run_gather(["--json", "--interactive-only"], self.tmp)
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual(data["conversations"], 0)
        self.assertEqual(data["excluded"], 0)

    def test_default_date_is_today_when_no_positional(self):
        # No date arg → defaults to today's UTC date; still 0 conversations
        # against the empty temp workspace, and the report names a real date.
        env = dict(os.environ, WORKSPACE=self.tmp)
        r = subprocess.run(
            [sys.executable, SCRIPT, "--json"],
            capture_output=True, text=True, env=env, timeout=60,
        )
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        data = json.loads(r.stdout)
        self.assertRegex(data["date"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(data["conversations"], 0)


if __name__ == "__main__":
    unittest.main()
