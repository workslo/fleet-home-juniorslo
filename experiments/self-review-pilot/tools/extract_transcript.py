#!/usr/bin/env python3
"""Extract a clean conversation transcript from a messages.jsonl record.

Phase-2 construction requirements addressed (from Codex's pair-4 review):
- Actor labels accurate: human turns are labeled SHANE (provenance guardian),
  assistant turns JUNIORSLO. Harness toolResult carriers are NOT labeled as
  human speech (pair-4 bug: human turns labeled System/Scheduler).
- Credentials stripped: known secret patterns redacted before writing.
- Paths normalized: /workspace and home prefixes abbreviated.
- Timestamps in both UTC and MDT.

Usage: extract_transcript.py <conversation_dir> [--digest-only]
Writes transcript to stdout. Digest mode emits a short session summary.
"""
import json
import sys
import re
from datetime import datetime, timedelta, timezone

MDT = timezone(timedelta(hours=-6))

SECRET_PATTERNS = [
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"), "<REDACTED_GITHUB_TOKEN>"),
    (re.compile(r"sk-[A-Za-z0-9\-_]{20,}"), "<REDACTED_API_KEY>"),
    (re.compile(r"Bearer [A-Za-z0-9\-._~+/]{20,}"), "Bearer <REDACTED>"),
    (re.compile(r"AIza[A-Za-z0-9\-_]{30,}"), "<REDACTED_GOOGLE_KEY>"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9\-]+"), "<REDACTED_SLACK_TOKEN>"),
]

def scrub(text):
    for pat, repl in SECRET_PATTERNS:
        text = pat.sub(repl, text)
    return text

def norm_path(text):
    text = re.sub(r"/workspace/conversations/[^\s'\"]+", "<conversation-record>", text)
    text = text.replace("/workspace", "~")
    text = text.replace("/Users/shaneslosar", "~host")
    return text

def fmt_ts(ts):
    if not ts:
        return "??"
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return ts
    mdt = dt.astimezone(MDT)
    return f"{dt.strftime('%H:%M:%S')}Z ({mdt.strftime('%H:%M:%S')} MDT)"

def extract(dirpath, digest_only=False):
    turns = []  # (ts, actor, text)
    tool_events = []
    last_tool_ts = None
    for line in open(f"{dirpath}/messages.jsonl"):
        try:
            m = json.loads(line)
        except json.JSONDecodeError:
            continue
        role = m.get("role")
        ts = m.get("ts", "")
        if role == "assistant":
            content = m.get("content") or ""
            if isinstance(content, str) and content.strip():
                turns.append((ts, "JUNIORSLO", scrub(norm_path(content))))
            for tc in (m.get("toolCalls") or []):
                name = tc.get("function", {}).get("name", tc.get("name", "?"))
                tool_events.append((ts, name))
        elif role == "user":
            if isinstance(m.get("content"), str) and m["content"].strip():
                meta = m.get("metadata") or {}
                prov = (meta.get("provenanceTrustClass") == "guardian"
                        or meta.get("userMessageChannel"))
                actor = "SHANE" if prov else "USER(UNVERIFIED)"
                turns.append((ts, actor, scrub(norm_path(m["content"]))))
            elif "toolResults" in m:
                for tr in m.get("toolResults", []):
                    inner = tr.get("content", "")
                    if isinstance(inner, str) and ("Error" in inner[:200] or "error" in inner[:100]):
                        tool_events.append((ts, "toolResult(error)"))

    if digest_only:
        n_shane = sum(1 for _, a, _ in turns if a == "SHANE")
        n_jr = sum(1 for _, a, _ in turns if a == "JUNIORSLO")
        first = turns[0][2][:200] if turns else "(no conversational turns)"
        print(f"- {len(turns)} conversational turns ({n_shane} Shane, {n_jr} JuniorSLO), {len(tool_events)} tool events")
        print(f"- Opening turn: {first}")
        return

    for ts, actor, text in turns:
        print(f"\n[{fmt_ts(ts)}] {actor}:")
        print(text)

def main():
    dirpath = sys.argv[1]
    digest = "--digest-only" in sys.argv
    extract(dirpath, digest)

if __name__ == "__main__":
    main()
