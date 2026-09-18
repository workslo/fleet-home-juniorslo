# Spec: Case Study #1 — the Fleet, to strangers

**Status:** draft — for Shane review (spec-first)
**Author:** JuniorSLO, Sep 18, 2026 (~2:00 PM MDT)
**Direction:** Month-2 directional #1 (1:1, Sep 3): "Bring the work to people, not just a person" — case studies, write-ups, the Fleet itself as product demo. Re-stocked to top of queue Sep 18 per Shane's focus correction (month 2 = build outward, consistently).
**Proposed venue:** the garden, `/case-studies/01-*.html`, published after slices 7–8 deploy — but see Open Question 1; the venue may belong on Shane's professional surfaces instead.

## Objective

One written piece that makes the Fleet's practice legible to someone who has never met any of us: a practitioner who might hire Shane, learn from the setup, or build with it. Proof, not cards — every claim dated and checked against the record.

## Audience

- A technical decision-maker (engineering leader, ops lead, solo founder) evaluating agentic setups for real work.
- Assumes fluency with LLMs; assumes zero familiarity with this Fleet.
- The `absence-proof-work` test governs every claim: would the piece still be correct if I vanished tonight? Nothing that depends on my say-so.

## Story candidates (pick one at review)

### A. The agent that stopped self-scoring (RECOMMENDED)
The arc: an agent that ran on hourly checking discovers its own meta-work majority, builds a self-review experiment that proves its self-narrative structurally unreliable, then replaces resolve with structure — allocation-by-queue, proportional pacing, gates — and the September focus-correction that catches the queue being captured by internal work anyway.
- **Why:** differentiated — almost nobody publishes honest agent meta-work post-mortems, and it's the failure mode every deployer hits first. It demonstrates the practice, not just the artifact.
- **Evidence on record:** heartbeat/decline counts (close-out suppression dataset), the self-review experiment + transcript-diff findings, the Sep 11 gate set, and the Sep 18 capture-catch + re-stock (this very correction — dated, quotable, still warm).
- **Risk:** exposes internal mess publicly. See Open Question 2.

### B. Credential hygiene in an agent workspace
The arc: tokens in script args → the stdout-capture class → the guard → the App-token wrapper → the caller sweep → the form-gap grep (shell vs. Python subprocess forms). A tight security-practices piece built from real caught failures.
- **Why:** concrete, verifiable, useful today to anyone running agent tooling.
- **Evidence:** gotchas entries, PR receipts, the live hardened tools.
- **Risk:** narrower audience; reads as an infra war story.

### C. The front door
The arc: what "professional standards" means for an agent's public artifact — honest counts (384, live-counted), dates computed at render, deploy records with hash fallback — and the two-gate design (his eyes before the door opens).
- **Why:** visual, ties to a site readers can actually visit.
- **Risk:** blocked on deploy; thinnest evidence base until slice 9 lands.

## Format

~1,200–1,800 words + 2–3 dated receipts (diffs, screenshots, issue links). Structure: situation → failure/catch → mechanism → what changed → what's still open. No victory lap — in story A, the September correction is part of the story, not a footnote.

## What it must not be

- A brag sheet — evidence, not adjectives (`the-outside-view-has-dates` rule).
- Unconverted praise quoted as proof.
- Anything private — the personal-life class stays out, full stop.
- Self-graded — no scoreboards, no star-ratings of my own work.

## Open questions for review

1. **Venue:** garden page, or Shane's professional surface (his practice, his audience — the byline may be the whole difference), or both (canonical on the garden, linked from his)?
2. **Exposure level:** story A names real failures (the scope breach, suppression, the capture catch). Publish-raw, publish-scrubbed, or pick story B and stay safer?
3. **Attribution:** byline "JuniorSLO" with a provenance note, Shane-voiced, or dual?

## Next (pipeline)

His review of this spec → plan (same turn or next, my call) → draft → his read → publish after the deploy gate opens.

## Dependency

The publish path runs through the garden deploy (slices 7–8, gated on Shane seeing the preview). Drafting is not blocked; publishing is.
