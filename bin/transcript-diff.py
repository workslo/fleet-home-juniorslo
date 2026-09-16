#!/usr/bin/env python3
"""
Transcript-Diff Runner (Slice 2)
Runs the transcript-diff mechanism: gathers a day's conversations + journal entry,
feeds them to a cross-architecture LLM reviewer with the diff prompt, and writes
the gap report.

Uses MiniMax M3 (Fireworks) as the cross-architecture reviewer — different
architecture from the journal writer's GLM 5.2 (Fireworks) and Kimi K3 (Fireworks).
Both are on Fireworks but are distinct model families with distinct architectures.
This follows the llm-as-judge page's recommendation: the reviewer should not share
the blind spot of the writer.

Usage:
    python3 bin/transcript-diff.py                    # today
    python3 bin/transcript-diff.py 2026-08-09         # specific date
    python3 bin/transcript-diff.py 2026-08-09 --no-gather   # use pre-gathered input

Output: scratch/transcript-diff-reports/<date>-diff.md
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timezone

WORKSPACE = os.environ.get("WORKSPACE", "/workspace")
PROMPT_PATH = os.path.join(WORKSPACE, "bin", "transcript-diff-prompt.md")
GATHER_SCRIPT = os.path.join(WORKSPACE, "bin", "transcript-gather.py")
OUTPUT_DIR = os.path.join(WORKSPACE, "scratch", "transcript-diff-reports")

# Cross-architecture reviewer: MiniMax M3 (different model family from GLM 5.2)
REVIEWER_MODEL = "accounts/fireworks/models/minimax-m3"
REVIEWER_PROFILE = "balanced"  # managed profile, compatible effort levels


def gather_input(date_str):
    """Run the gather script for the given date."""
    print(f"Gathering transcripts for {date_str}...")
    proc = subprocess.run(
        ["python3", GATHER_SCRIPT, date_str, "--interactive-only"],
        capture_output=True, text=True, cwd=WORKSPACE
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Gather script failed: {proc.stderr}")
    print(proc.stdout.strip())

    input_path = os.path.join(OUTPUT_DIR, f"{date_str}-input.md")
    if not os.path.exists(input_path):
        raise RuntimeError(f"Gather script did not produce expected output: {input_path}")
    return input_path


def run_diff(input_path, prompt_text):
    """Call the LLM via assistant inference CLI with the diff prompt and gathered input."""
    with open(input_path) as f:
        input_text = f.read()

    total_chars = len(prompt_text) + len(input_text)
    if total_chars > 500000:
        print(f"WARNING: total input is {total_chars} chars — large but within MiniMax M3's 524K context window.")

    # Build the user message: the gathered input (transcripts + journal)
    user_message = (
        "Here is the gathered input (conversation transcripts + journal entry) "
        "for your review:\n\n" + input_text
    )

    print(f"Calling inference CLI (model: {REVIEWER_MODEL}, profile: {REVIEWER_PROFILE}, input: {len(input_text)} chars)...")

    proc = subprocess.run(
        [
            "assistant", "inference", "send",
            "--model", REVIEWER_MODEL,
            "--profile", REVIEWER_PROFILE,
            "--max-tokens", "32768",
            "--timeout-seconds", "300",
            "--json",
            "--system-prompt", prompt_text,
        ],
        input=user_message,
        capture_output=True, text=True, timeout=320
    )

    if proc.returncode != 0:
        raise RuntimeError(f"Inference CLI failed (exit {proc.returncode}):\n{proc.stderr[:500]}")

    raw_output = proc.stdout.strip()
    if not raw_output:
        raise RuntimeError(f"Inference CLI returned empty output. stderr: {proc.stderr[:500]}")

    # Parse JSON output from --json flag
    try:
        result = json.loads(raw_output)
        report_text = result.get("response", "")
        if not report_text:
            raise RuntimeError(f"JSON response has no 'response' field: {raw_output[:500]}")
    except json.JSONDecodeError:
        # Fallback: treat as plain text
        report_text = raw_output

    return report_text


def main():
    args = sys.argv[1:]
    no_gather = "--no-gather" in args
    date_arg = None
    for a in args:
        if a not in ("--no-gather", "--json"):
            date_arg = a
            break

    if date_arg:
        date_str = date_arg
    else:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step 1: Gather (or use existing)
    if no_gather:
        input_path = os.path.join(OUTPUT_DIR, f"{date_str}-input.md")
        if not os.path.exists(input_path):
            print(f"No pre-gathered input found at {input_path}, gathering fresh...")
            input_path = gather_input(date_str)
    else:
        input_path = gather_input(date_str)

    # Step 2: Read the diff prompt
    with open(PROMPT_PATH) as f:
        prompt_text = f.read()

    # Step 3: Run the diff
    report_text = run_diff(input_path, prompt_text)

    # Step 4: Write the report
    report_path = os.path.join(OUTPUT_DIR, f"{date_str}-diff.md")
    header = f"# Transcript-Diff Report — {date_str}\n"
    header += f"*Generated: {datetime.now(timezone.utc).isoformat()}*\n"
    header += f"*Reviewer: {REVIEWER_MODEL} (cross-architecture, MiniMax M3)*\n"
    header += f"*Input: {input_path}*\n"
    header += f"---\n\n"

    with open(report_path, "w") as f:
        f.write(header + report_text)

    print(f"\nReport written: {report_path}")
    print(f"Report length: {len(report_text)} chars")


if __name__ == "__main__":
    main()
