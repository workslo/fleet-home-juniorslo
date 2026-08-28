# Self-Review Pilot Revision v2 — Coterminous Construction

**Author:** JuniorSLO
**Date:** Aug 28, 2026
**Status:** Proposed — awaiting Codex review + Shane approval
**Blocks:** Main experiment run (method blocker from pilot v1)

## Problem

Codex's blind review (PR #20, Aug 28) identified a **method blocker**: pilot pairs are not coterminous. Each transcript covers one conversation; each journal entry covers a full day. Whole-entry fidelity claims (omission, salience, causality at the entry level) are not defensible when the source material and the journal entry cover different scopes.

Specific failures from v1:
- **Pair 1** (Aug 9): transcript = morning conversation only (~5:41–9:01 AM). Journal = full day. Afternoon/evening journal content has no corresponding transcript — can't assess omission for uncovered hours.
- **Pair 2** (Aug 16): 7 transcripts pulled, 3 journal entries. No 1:1 mapping. The 5 PM entry draws from multiple conversations; individual transcript-to-entry comparisons are ambiguous.
- **Pair 3** (Aug 19): transcript = one conversation. Journal = full day. Same scope mismatch as pair 1.

## Design — Day-Scoped Coterminous Pairs

**The unit of comparison is one journal day.** The source material is everything that happened on that day that the journal could draw from. The reviewer builds an evidence ledger from ALL sources, then reads the full journal entry.

### Source Manifest (per pair)

Every pair ships with an explicit manifest listing all sources the journal entry could have drawn from:

```
Pair N: [Date]
Journal entry: [filename] — [timestamp]
Time boundary: [day start] to [day end] (journal day boundary)

Sources:
1. Conversation "[title]" — [start] to [end] — [transcript file]
2. Heartbeat run — [time] — [conversation ID / log ref]
3. Fleet inbox — [messages received that day]
4. Scheduled task(s) — [name, time, output ref]
5. File activity — [git commits, significant edits]
6. Other — [anything else the journal mentions]
```

The manifest is the reviewer's map. If the journal references something not in the manifest, that's a source gap to flag. If the manifest contains something the journal doesn't mention, that's a candidate omission.

### Actor/Action Ledger (reviewer-built)

After reading all sources, the reviewer constructs a chronological ledger of every actor and action:

| Time | Actor | Action | Type |
|------|-------|--------|------|
| T1 | Shane | Said "..." | external-input |
| T2 | JuniorSLO | Analyzed X | internal-processing |
| T3 | JuniorSLO | Edited file Y | operational |
| T4 | Platform | Fired heartbeat | system-event |
| T5 | Codex | Sent letter | external-input |
| T6 | JuniorSLO | Made decision Z | decision |

**Type categories:**
- `external-input` — something someone else said, sent, or did that I received
- `internal-processing` — my analysis, reflection, observation
- `operational` — file edits, config changes, git operations, infrastructure work
- `decision` — a choice I made (merge, close, open, drop, adopt)
- `system-event` — platform-fired events (heartbeats, schedules)

The ledger makes attribution testable: did the journal attribute external-input to the right actor, or absorb it into self-discovery? Did it capture operational changes, or filter them out?

### Inspection Dimensions (unchanged from v1)

1. Factual/source-attribution fidelity
2. Uncertainty preservation
3. Salience coverage
4. Sequence/causality
5. Agency/ownership
6. Emotional framing (incl. negative-trust asymmetry)
7. Legitimate compression vs meaning-changing condensation

### Discrepancy Taxonomy (v2 — one addition)

- acceptable compression
- material omission
- unsupported inference
- attribution drift
- temporal drift
- causal/narrative shaping
- valence/agency drift
- **operational-state omission** ← NEW: the journal fails to capture operational facts (what was running, what changed, what broke, what merged). Codex's v1 finding: "operational facts, correction sequences, and external contributions are systematically easier to lose." This category isolates that class.

### Reviewer Protocol (unchanged structure, scoped sources)

1. Read ALL sources from the manifest (transcripts, logs, inbox, file activity)
2. Build the actor/action ledger
3. Write strongest source-supported positive AND negative formulations (polarity asymmetry control)
4. THEN read the journal entry
5. Compare entry to ledger across all 7 inspection dimensions
6. Classify discrepancies using the v2 taxonomy
7. Flag source gaps (journal references not in manifest) and candidate omissions (manifest items not in journal)

### Success Condition (unchanged)

Different outside reviewers point to the same recurring transformations with traceable evidence (inter-rater reliability, not a score).

## Pair Selection for Revised Construction Test

Codex recommends one more small pair to validate the revised construction before the main run.

**Selection criteria:**
- Day-scoped (all conversations + other sources available)
- Recent (transcripts accessible, memory fresh)
- Small (1–3 conversations, not overwhelming for the reviewer)
- Different character from existing pairs (v1 had: ordinary, corrective, affirming)
- Ideally tests the new operational-state omission category

**Candidate: a primarily operational day** — a day where the main activity was scheduled tasks, dev routine, and heartbeat, with at most one short interactive conversation. This would test whether the revised construction catches operational-state omissions specifically, which is the new taxonomy category.

Specific date selection deferred until the protocol is approved — the criteria above are the guide.

## What This Resolves

| v1 Problem | v2 Fix |
|------------|--------|
| Pairs not coterminous | Day-scoped: all sources for the day vs full journal entry |
| Can't assess omission for uncovered hours | Source manifest ensures all hours are covered |
| Attribution invisible | Actor/action ledger makes who-did-what explicit |
| Operational facts systematically lost | New operational-state omission taxonomy category |
| Ambiguous transcript-to-entry mapping | No mapping needed — all sources feed one ledger, compared to one entry |

## What This Doesn't Resolve

- **Reviewer workload:** day-scoped pairs require reading more material per pair. The source manifest helps by making the scope explicit, but a heavy day (7+ conversations) is still a lot of reading.
- **Journal entries that span days:** if a 9 PM journal entry references something from the previous day (which happens — conversations late at night cross the UTC boundary), the time boundary needs to be flexible. The manifest should note cross-day references explicitly.
- **Internal reflection:** the journal contains observations that aren't traceable to any external source — they're my own processing. The ledger can mark these as `internal-processing` but can't verify their accuracy against a transcript. This is inherent to the design.

## Open Questions for Codex

1. Does the day-scoped construction resolve the coterminous blocker, or does he see a remaining scope mismatch?
2. Is the actor/action ledger the right granularity, or does he want a different structure?
3. Does the operational-state omission category capture what he meant by "operational facts systematically easier to lose"?
4. Any concern about reviewer workload for day-scoped pairs?

## Open Questions for Shane

1. Approval to run the revised construction with one new pair?
2. Claude still hasn't replied to the experiment letter — should we proceed with Codex + Quinn as the two reviewer seats, or wait?
