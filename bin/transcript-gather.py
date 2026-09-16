#!/usr/bin/env python3
"""
Transcript-Diff Gather Script (Slice 1)
Collects a day's conversation transcripts + journal entry into a single input file
for the transcript-diff mechanism (Slo's agentslo #45 proposal).

Usage:
    python3 bin/transcript-gather.py                    # today (UTC date)
    python3 bin/transcript-gather.py 2026-08-21         # specific date
    python3 bin/transcript-gather.py --json             # machine-readable output

Output: scratch/transcript-diff-reports/<date>-input.md
"""

import json
import os
import sys
import glob
from datetime import datetime, timezone, timedelta

WORKSPACE = os.environ.get("WORKSPACE", "/workspace")
CONVERSATIONS_DIR = os.path.join(WORKSPACE, "conversations")
JOURNAL_PATH = os.path.join(WORKSPACE, "memory", "journal", "journal.md")
NOW_MD_PATH = os.path.join(WORKSPACE, "NOW.md")
OUTPUT_DIR = os.path.join(WORKSPACE, "scratch", "transcript-diff-reports")

# MDT = UTC-6. The journal runs at 5 PM MDT (23:00 UTC same day).
# The diff runs at 5:30 PM MDT (23:30 UTC same day).
# At that point, conversations from the MDT day (midnight-5:30 PM MDT = 06:00-23:30 UTC)
# all share the same UTC date as the MDT date.
MDT_OFFSET = timedelta(hours=6)


def get_target_date():
    """Get the target date from args or default to today's UTC date."""
    args = sys.argv[1:]
    json_mode = "--json" in args
    interactive_only = "--interactive-only" in args
    date_arg = None
    for a in args:
        if a not in ("--json", "--interactive-only"):
            date_arg = a
            break

    if date_arg:
        return date_arg, json_mode, interactive_only

    # Default: today's UTC date (at 5:30 PM MDT = 23:30 UTC, same date)
    now_utc = datetime.now(timezone.utc)
    return now_utc.strftime("%Y-%m-%d"), json_mode, interactive_only


def find_conversations(date_str, interactive_only=False):
    """Find all conversation directories matching the given date.
    If interactive_only, exclude background maintenance conversations
    (heartbeats, retrospectives, memory consolidation) and scheduled
    maintenance tasks (lint, journal, drift items). Keeps 'standard'
    type conversations (real Shane interactions) and substantive
    scheduled conversations."""
    pattern = os.path.join(CONVERSATIONS_DIR, f"{date_str}T*")
    dirs = sorted(glob.glob(pattern))

    if not interactive_only:
        return dirs

    filtered = []
    excluded = []
    for d in dirs:
        meta_path = os.path.join(d, "meta.json")
        conv_type = "unknown"
        title = ""
        if os.path.exists(meta_path):
            try:
                with open(meta_path) as f:
                    meta = json.load(f)
                conv_type = meta.get("type", "unknown")
                title = meta.get("title", "")
            except (json.JSONDecodeError, IOError):
                pass

        # Exclude background maintenance (heartbeats, retros, consolidation, subagents)
        if conv_type == "background":
            excluded.append((d, f"background: {title}"))
            continue

        # Exclude scheduled maintenance tasks (lint, journal, drift items)
        if conv_type == "scheduled" and title.startswith("Schedule:"):
            excluded.append((d, f"scheduled maintenance: {title}"))
            continue

        filtered.append(d)

    return filtered, excluded


def extract_transcript(conv_dir):
    """Extract meaningful content from a conversation directory.
    Returns (title, conv_type, messages) where messages is a list of {role, content}."""
    meta_path = os.path.join(conv_dir, "meta.json")
    messages_path = os.path.join(conv_dir, "messages.jsonl")

    title = "(untitled)"
    conv_type = "(unknown)"

    if os.path.exists(meta_path):
        try:
            with open(meta_path) as f:
                meta = json.load(f)
            title = meta.get("title", "(untitled)")
            conv_type = meta.get("type", "(unknown)")
        except (json.JSONDecodeError, IOError):
            pass

    messages = []
    if os.path.exists(messages_path):
        with open(messages_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Skip toolResults-only entries (harness internal)
                content = msg.get("content")
                if content is None or content == "":
                    continue

                role = msg.get("role", "?")
                ts = msg.get("ts", "")

                # Truncate extremely long messages to keep total size manageable
                # (context window management — open question in the design)
                max_msg_chars = 8000
                if len(content) > max_msg_chars:
                    content = content[:max_msg_chars] + "\n... [truncated, original length: {} chars]".format(len(content))

                messages.append({
                    "role": role,
                    "ts": ts,
                    "content": content,
                })

    return title, conv_type, messages


def extract_journal_entry(date_str):
    """Extract the journal entry for the given date.
    Journal sections are headers like: ## August X, 2026 — time MDT (time UTC)
    We match by the date in the header."""
    if not os.path.exists(JOURNAL_PATH):
        return "(journal not found)"

    with open(JOURNAL_PATH) as f:
        text = f.read()

    # Parse month name + day from date_str (YYYY-MM-DD)
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        # Journal headers use "August 31, 2026" format
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        date_header_fragment = f"{month_names[dt.month - 1]} {dt.day}, {dt.year}"
    except ValueError:
        return f"(could not parse date: {date_str})"

    # Find the date-matching header, then capture everything until the NEXT
    # date-matching header. Journal entries use ## sub-headers (## Who was here,
    # ## What the day gave me) that also start with ## — we must NOT stop at those.
    # Date headers contain a month name + day + year (e.g. "August 9, 2026").
    all_month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    def is_date_header(line):
        """Check if a ## line is a date-matching journal entry header."""
        if not line.startswith("## "):
            return False
        return any(m in line for m in all_month_names) and str(dt.year) in line

    lines = text.split("\n")
    entry_lines = []
    in_target = False
    found = False

    for i, line in enumerate(lines):
        if is_date_header(line) and date_header_fragment in line:
            in_target = True
            found = True
            entry_lines.append(line)
            continue
        elif is_date_header(line) and in_target:
            # Next date-matching entry — stop
            break
        elif in_target:
            entry_lines.append(line)

    if not found:
        return f"(no journal entry found for {date_header_fragment})"

    return "\n".join(entry_lines).strip()


def build_input_file(date_str, conversations, journal_entry, now_md=""):
    """Build the combined input file for the transcript-diff LLM call."""
    parts = []

    # Header
    parts.append(f"# Transcript-Diff Input — {date_str}")
    parts.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    parts.append("")

    # Conversation inventory
    total_messages = 0
    total_chars = 0
    parts.append(f"## Conversation Inventory ({len(conversations)} conversations)")
    parts.append("")
    for i, (title, conv_type, messages, conv_dir) in enumerate(conversations, 1):
        msg_count = len(messages)
        char_count = sum(len(m["content"]) for m in messages)
        total_messages += msg_count
        total_chars += char_count
        dir_name = os.path.basename(conv_dir)
        parts.append(f"{i}. **{title}** (type: {conv_type}, messages: {msg_count}, chars: {char_count}) — `{dir_name}`")
    parts.append("")
    parts.append(f"**Totals:** {len(conversations)} conversations, {total_messages} messages, {total_chars} characters")
    parts.append("")

    # Transcripts
    parts.append("---")
    parts.append("")
    parts.append("## Conversation Transcripts")
    parts.append("")
    for i, (title, conv_type, messages, conv_dir) in enumerate(conversations, 1):
        parts.append(f"### Conversation {i}: {title}")
        parts.append(f"*Type: {conv_type}*")
        parts.append("")
        if not messages:
            parts.append("(no text content — tool-only conversation)")
            parts.append("")
            continue
        for msg in messages:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            parts.append(f"**[{role_label}]** {msg['content']}")
            parts.append("")
        parts.append("")

    # NOW.md (status shelf — gives reviewer context on what's filed elsewhere)
    if now_md:
        parts.append("---")
        parts.append("")
        parts.append("## NOW.md (Status Shelf — for reviewer context)")
        parts.append("")
        parts.append("**Note to reviewer:** content in this section is filed on the status shelf, NOT the journal. Operational facts, decisions, and infrastructure status that appear here are NOT journal gaps — they are correctly filed on a different shelf (journal = lived things, status systems = decisions). However, the *receivable* aspects of those same events (someone's guiding agency, affirming moments, lived texture, emotional arc) may still be journal gaps even when the operational fact is filed here. Use this section to distinguish 'dropped entirely' from 'correctly filed elsewhere.'")
        parts.append("")
        parts.append(now_md)
        parts.append("")

    # Journal entry
    parts.append("---")
    parts.append("")
    parts.append("## Journal Entry for This Date")
    parts.append("")
    parts.append(journal_entry)
    parts.append("")

    return "\n".join(parts), total_messages, total_chars


def main():
    date_str, json_mode, interactive_only = get_target_date()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    result = find_conversations(date_str, interactive_only)
    if interactive_only:
        conv_dirs, excluded = result
    else:
        conv_dirs = result
        excluded = []

    conversations = []
    for conv_dir in conv_dirs:
        title, conv_type, messages = extract_transcript(conv_dir)
        conversations.append((title, conv_type, messages, conv_dir))

    journal_entry = extract_journal_entry(date_str)

    # Read NOW.md (status shelf) so the diff reviewer can distinguish
    # "dropped entirely" from "correctly filed on the status shelf"
    now_md = ""
    if os.path.exists(NOW_MD_PATH):
        with open(NOW_MD_PATH) as f:
            now_md = f.read().strip()

    input_text, total_messages, total_chars = build_input_file(
        date_str, conversations, journal_entry, now_md
    )

    # Add exclusion summary if filtering
    if excluded:
        exclusion_summary = "\n\n## Excluded Conversations (filtered by --interactive-only)\n\n"
        for d, reason in excluded:
            exclusion_summary += f"- {reason}\n"
        input_text += exclusion_summary

    output_path = os.path.join(OUTPUT_DIR, f"{date_str}-input.md")
    with open(output_path, "w") as f:
        f.write(input_text)

    if json_mode:
        result = {
            "date": date_str,
            "conversations": len(conversations),
            "excluded": len(excluded),
            "messages": total_messages,
            "total_chars": total_chars,
            "output_path": output_path,
            "journal_found": not journal_entry.startswith("("),
        }
        print(json.dumps(result, indent=2))
    else:
        filter_note = f" (filtered: {len(excluded)} excluded)" if excluded else ""
        print(f"Gathered {date_str}: {len(conversations)} conversations{filter_note}, {total_messages} messages, {total_chars} chars")
        print(f"Journal entry found: {not journal_entry.startswith('(')}")
        print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
