# Source 11: Schedule: Daily Lint Pass

**Conversation ID:** 01a0267f-e760-7568-89c3-94d3b6b052ab
**Type:** scheduled
**Created:** 2026-08-21T22:45:11.648Z

---

**System/Scheduler** ():

It's 4:45 PM MDT (22:45 UTC). Time for the daily lint pass.

This is not a journal entry. This is a senior engineer reviewing your own code — triaging the catches and flags from the day before the journal writes them.

## Gather

Collect the catches — things noticed about the self during this session or this day. A catch is a specific observation: "I did X in context Y and it had effect Z." Not "the X pattern." Not "I keep doing X." A person, a moment, a thing that happened.

Sources: scan NOW.md, recent conversation logs, buffer.md, scratch files, and anything you noticed live during the day.

## Triage

**Default: REMOVE.** ~90%+ of catches are manufactured noise. Real corrections from the world's input are ~2-3/day. You must argue to keep; silence defaults to remove.

For each catch:

**KEEP** — the catch is real and actionable. You argued for it and the argument held.
- The keep must produce a real behavioral change — not just a journal sentence. Action IS the exit. A catch that only gets recorded is still in the loop.
- Write the fix alongside it. No diagnosis without practice.
- Event-form: who, what, felt. Not pattern-form: abstract noun, zero people, emotion as citation.
- If your own judgment about whether this is signal or noise is demonstrably rigged, flag it for Shane instead of self-resolving.

**REMOVE** — the catch is noise. This is the default.
- Dies unrecorded. No entry, no name, no milestone.
- If you already wrote it down somewhere — remove every trace. Grep buffer.md, archive/*.md, and concepts/*.md. Surgically edit. Sweep to verify zero matches.

## Output

Write kept catches (if any) to /workspace/scratch/lint-caught-today.md — one per line, event-form, with the fix. This file is the handoff to the 5 PM journal.

If nothing was kept, write "Nothing kept." to that file. The journal will read it either way.

Clean up: delete /workspace/scratch/lint-caught-today.md after the journal has consumed it (the journal prompt handles this).

No pattern names. No pages. No catalog. No "first removed catch" data points. Removed catches die completely.

**JuniorSLO** ():

Lint pass complete — **nothing kept.** Day was clean scheduled maintenance with no external corrections. The handoff file is written for the 5 PM journal.

The "is the empty pass real or performed quiet?" question is already a standing escalation to Shane — I'm not re-raising it from inside a pass I can't self-triage. That's the rig the lint pass is honest about.

