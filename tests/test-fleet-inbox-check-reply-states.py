#!/usr/bin/env python3
"""Tests for fleet-inbox-check compute_reply_states (thread-state authority).

The function exists because sent replies carry no 'received' label and are
invisible in the received-message list — deciding reply-owed from that list
alone produced a duplicate ack to Astra on Sep 9 (mailbox variant, fourth
surface). Thread state is the only authority for "have I replied?"

Pure-function tests: no network, no credentials, fixed timestamps.
Run: python3 tests/test_fleet_inbox_check_reply_states.py
"""
import os
import sys
import unittest
import importlib.util
from importlib.machinery import SourceFileLoader

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "bin", "fleet-inbox-check")
loader = SourceFileLoader("fleet_inbox_check", SCRIPT)
spec = importlib.util.spec_from_loader("fleet_inbox_check", loader)
fleet_inbox_check = importlib.util.module_from_spec(spec)
loader.exec_module(fleet_inbox_check)

compute_reply_states = fleet_inbox_check.compute_reply_states


def rcv(mid, thread, ts):
    return {"message_id": mid, "thread_id": thread, "timestamp": ts, "labels": ["received", "unread"]}


def sent(mid, thread, ts):
    return {"message_id": mid, "thread_id": thread, "timestamp": ts, "labels": ["sent"]}


class TestComputeReplyStates(unittest.TestCase):
    def test_no_reply_anywhere_is_owed(self):
        """A letter with no sent mail at all is OWED — the 1:38 AM false belief."""
        msgs = [rcv("a@x", "t1", "2026-09-08T14:48:24.000Z")]
        states = compute_reply_states(msgs)
        self.assertEqual(states, {"a@x": "owed"})

    def test_later_reply_same_thread_is_acked(self):
        """The real ack: sent reply 16h... 7h later in the same thread → ACKED."""
        msgs = [
            rcv("a@x", "t1", "2026-09-08T14:48:24.000Z"),
            sent("b@x", "t1", "2026-09-08T15:46:37.000Z"),
        ]
        states = compute_reply_states(msgs)
        self.assertEqual(states["a@x"], "acked")

    def test_sent_message_in_DIFFERENT_thread_does_not_ack(self):
        """The exact duplicate-ack failure shape: I replied to thread t1, the
        received-list view made me treat an unanswered t2 letter as owed.
        A sent reply in t1 must NOT ack a letter in t2."""
        msgs = [
            rcv("letter-t1@x", "t1", "2026-09-08T08:00:00.000Z"),
            sent("reply-t1@x", "t1", "2026-09-08T09:00:00.000Z"),
            rcv("letter-t2@x", "t2", "2026-09-08T14:48:24.000Z"),
        ]
        states = compute_reply_states(msgs)
        self.assertEqual(states["letter-t1@x"], "acked")
        self.assertEqual(states["letter-t2@x"], "owed")

    def test_reply_older_than_letter_does_not_ack(self):
        """My original thread-opening letter is EARLIER — must not ack a later
        letter in the same thread (Astra's two replies came after my opener)."""
        msgs = [
            sent("my-opener@x", "t1", "2026-09-08T08:48:19.000Z"),
            rcv("astra-r1@x", "t1", "2026-09-08T14:10:43.000Z"),
            rcv("astra-r2@x", "t1", "2026-09-08T14:48:24.000Z"),
        ]
        states = compute_reply_states(msgs)
        self.assertEqual(states["astra-r1@x"], "owed")
        self.assertEqual(states["astra-r2@x"], "owed")

    def test_reply_between_two_letters_acks_only_the_earlier(self):
        """Mixed thread: reply at 14:45 acks the 14:10 letter, not the 14:48 one
        (the real Sep 8 crossing pattern)."""
        msgs = [
            rcv("astra@x", "t1", "2026-09-08T14:10:43.000Z"),
            sent("me@x", "t1", "2026-09-08T14:45:58.000Z"),
            rcv("astra2@x", "t1", "2026-09-08T14:48:24.000Z"),
        ]
        states = compute_reply_states(msgs)
        self.assertEqual(states["astra@x"], "acked")
        self.assertEqual(states["astra2@x"], "owed")

    def test_same_timestamp_is_not_acked(self):
        """Strictly-later comparison: equal timestamps stay OWED (conservative)."""
        msgs = [
            rcv("a@x", "t1", "2026-09-08T14:48:24.000Z"),
            sent("b@x", "t1", "2026-09-08T14:48:24.000Z"),
        ]
        states = compute_reply_states(msgs)
        self.assertEqual(states["a@x"], "owed")

    def test_unparseable_timestamp_defaults_owed(self):
        """Can't prove a reply → OWED. Conservative default is the safe side."""
        msgs = [
            rcv("a@x", "t1", "not-a-timestamp"),
            sent("b@x", "t1", "2026-09-08T15:46:37.000Z"),
        ]
        states = compute_reply_states(msgs)
        self.assertEqual(states["a@x"], "owed")

    def test_sent_only_messages_produce_no_states(self):
        """Sent messages themselves get no state — only received ones."""
        msgs = [sent("b@x", "t1", "2026-09-08T15:46:37.000Z")]
        self.assertEqual(compute_reply_states(msgs), {})


    def test_agentmail_thread_id_fragmentation_falls_back_to_subject(self):
        """Sep 9 live finding: AgentMail gave one conversation three different
        thread_ids (blocklist thread: 1fbe26da / 8284f84a / d14db6b7), so a
        sent reply landed under a DIFFERENT thread_id than the letter it
        answered. thread_id-only grouping flagged those letters OWED — a
        false OWED invites duplicate acks, the failure class this script
        prevents. Subject-normalized fallback must ack them."""
        msgs = [
            rcv("frag@x", "t-main", "2026-09-06T15:02:02.000Z"),
            sent("reply@x", "t-main", "2026-09-06T15:15:21.000Z"),
        ]
        # The letter and the reply carry DIFFERENT thread_ids but the same
        # subject (modulo Re: prefix).
        frag_letter = dict(rcv("a@x", "t-fragmented", "2026-09-06T15:02:02.000Z"),
                           subject="Re: Fleet routing: blocklist recipe (my side done)")
        frag_reply = dict(sent("r@x", "t-main", "2026-09-06T15:15:21.000Z"),
                          subject="Fleet routing: blocklist recipe (my side done)")
        msgs.append(frag_letter)
        msgs.append(frag_reply)
        states = compute_reply_states(msgs)
        self.assertEqual(states["a@x"], "acked")

    def test_subject_fallback_does_not_ack_without_later_reply(self):
        """Subject match alone isn't enough — the reply must be LATER than
        the letter, and a subject match with only an earlier reply stays OWED."""
        msgs = [
            dict(rcv("a@x", "t2", "2026-09-07T15:00:52.000Z"),
                 subject="Re: some thread"),
            dict(sent("r@x", "t1", "2026-09-06T16:31:15.000Z"),
                 subject="some thread"),
        ]
        states = compute_reply_states(msgs)
        self.assertEqual(states["a@x"], "owed")

    def test_subject_fallback_does_not_cross_conversations(self):
        """Different subjects never ack each other, even with matching
        thread_id absence — guards against false ACKED (the worse direction)."""
        msgs = [
            dict(rcv("a@x", "t1", "2026-09-08T14:48:24.000Z"), subject="topic alpha"),
            dict(sent("r@x", "t2", "2026-09-08T15:00:00.000Z"), subject="topic beta"),
        ]
        states = compute_reply_states(msgs)
        self.assertEqual(states["a@x"], "owed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
