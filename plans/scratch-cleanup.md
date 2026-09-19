---
status: in-review
date: 2026-09-17
links:
  spec: specs/pipeline-artifact-layout.md (PR #64, merged — Migrations §2)
  issue: 71
---

# Plan: scratch/ Cleanup — 24 Residents, Dispositioned Live

Implements Migrations §2 of the parent spec. The parent-spec boundary governs every move: **ask first on any migration that moves a file another page or procedure references — reference sweep before each move.** The sweep ran Sep 17 across `memory/` (all pages), `skills/`, `bin/`, `HEARTBEAT.md`, `NOW.md`, `build-queue.md`, `cold/`, and the repo's own `specs/`+`plans/`.

Workflow note (per the Sep 16 clarification): spec → plan → build → PR with no mid-pipeline wait; Shane's review + merge of this PR is the presence point. Moves below were executed this pass **only where the sweep came back clean**; every path-referenced item is HELD for his word at review. Nothing was deleted — the parent spec's "sent-letter drafts → deleted" line is flagged below rather than executed unattended.

## Inventory — 24 residents, dispositioned (live listing Sep 17, 2 PM MDT)

| # | Resident | Disposition | Evidence / reason |
|---|---|---|---|
| 1 | `audit.json` | **KEEP** | active — harness-audit output feeding #58 |
| 2 | `audit2.json` | **KEEP** | active — same run |
| 3 | `blind-sort/` | **HOLD** | path-referenced: sealed ground-truth key + phase1 working files + pre-registration (`substrate-independent-voice.md`, two sent-to-Slo letters); live cold-shelf protocol with Slo |
| 4 | `ci-workflow-ready.yml` | **HOLD** | staged artifact per `github-app-onboarding.md` — "ready to push when unblocked" (awaits `workflows` permission) |
| 5 | `garden-render-report.md` | **KEEP** | needed for the garden seeing report; graduates to `repos/front-door/` at garden build time |
| 6 | `garden-shots/` | **KEEP** | same |
| 7 | `glm-5.3-sports-car-review.md` | **HOLD** | path-referenced by 3 pages: `jrslo-runtime.md`, `jrslo-runtime-history.md`, `model-landscape-2026-09.md` |
| 8 | `intelligence-vs-cost-2026-09-04.svg` | **HOLD** | path-referenced by `model-landscape-2026-09.md`, `shane-how-he-engages.md` |
| 9 | `letter-claude-phase2-receipt-2026-09-05.md` | **MOVE → archive** | draft/receipt; canonical verified identical (headers aside): `memory/letters/letter-to-claude-phase2-pairs-delivery-2026-09-05.md` |
| 10 | `letter-littlebird-reply-2026-09-05.md` | **MOVE → archive** | draft; canonical verified: `memory/letters/reply-littlebird-2026-09-05-seeing.md` |
| 11 | `letter-to-fable-2026-09-05.md` | **MOVE → `memory/letters/`** | **only copy** (no canonical found) — the Sep 5 reply to Fable via Claude's relay address; graduates as correspondence record |
| 12 | `lint-kept.md` | **KEEP** | **re-dispositioned from ARCHIVE**: it is the `daily-lint-pass` skill's live output file (procedure writes to this path every run) |
| 13 | `model-comparison-2026-09-04.md` | **HOLD** | path-referenced by `model-landscape-2026-09.md`, `shane-how-he-engages.md` |
| 14 | `reply-fleet-v2.md` | **MOVE → archive** | draft of the sent v2-announcement reply; canonical = the announcement thread |
| 15 | `reply-routing-ack.md` | **MOVE → archive** | draft of a sent ack; canonical = the routing thread |
| 16 | `rename-process-test.md` | **HOLD** | path-referenced by `conversation-sidebar.md` ("receipt + full process: …") |
| 17 | `return-lines-spec-prep.md` | **KEEP** | feeds the open return-lines item (spec drafted, awaiting review); graduates when that item lands |
| 18 | `scratch-cleanup-spec` (`2026-09-16-scratch-cleanup-spec.md`) | **MOVE → archive** | this slice's spec draft; canonical = the #71 spec comment |
| 19 | `seeds/` | **HOLD** | procedure output location (`concept-seed-prospect` skill writes `scratch/seeds/week-N.md`) + the flagged judgment call (record vs cold storage) |
| 20 | `stamp-fix.bundle` | **HOLD** | parent-spec explicit: "remains until the upstream PR (vellum-assistant) merges, then deleted" — upstream branch still awaits the fork grant (verified Sep 16) |
| 21 | `stamp-normalize.py` | **HOLD** | path-referenced by `gotchas.md` (the Sep 8 repair record) |
| 22 | `transcript-diff-reports/` | **KEEP** | active dig artifacts (touched Sep 16) |
| 23 | `wonder-pass/` | **MOVE → `memory/archive/wonder-pass/`** | topic-references only (`hand-coded-svg.md` cites the series by name/date, no path); the one path-form hit is my own build-queue pointer, updated in-run |
| 24 | `write-time-verification-brief.md` | **HOLD** | live pointer from `write-time-verification.md` — the brief is the artifact of a parked spec-first item ("discussion-ready") |

**Totals: 7 KEEP · 10 HOLD · 7 MOVE · 0 DELETE.**

## Moves executed (workspace-side, this pass)

- `wonder-pass/` → `memory/archive/wonder-pass/` (graduate — artifacts of a named practice)
- `letter-to-fable-2026-09-05.md` → `memory/letters/to-fable-via-claude-relay-2026-09-05.md` (graduate — only copy)
- 5 drafts/receipts → `cold/scratch-archive/2026-09/` (claude receipt, littlebird reply, v2 reply, routing ack, spec draft)

Archive location rationale: `cold/` is the existing cold-storage convention (finished, on-touch revival) — no new workspace top-level directory (guardrail honored). All moves plain `mv`, verified after by listing both ends; `build-queue.md`'s wonder-pass pointer updated to the new path.

## Deviations from the attached spec comment (flagged for review)

1. **lint-kept.md: ARCHIVE → KEEP.** The sweep caught what the spec comment missed — it's a live procedure's output file, regenerated by every daily-lint run.
2. **stamp-fix.bundle: ARCHIVE → HOLD.** The parent spec's own line ("remains until the upstream PR merges") governs over the spec comment's archive disposition.
3. **Letters: archived, not deleted.** The parent spec says "sent-letter drafts → deleted"; canonicals verified for two of three, but deletion is irreversible and this ran unattended — the delete completes on one word at review. The fable-relay letter was NOT deleted-eligible at all (only copy — graduated instead).
4. **Archive home: `cold/scratch-archive/2026-09/`**, not a new top-level `scratch-archive/` — no-new-top-level-directories guardrail.

## What one word from Shane clears (the HOLD list, ask-first per parent spec)

Each held item moves the moment he says so, with its referencing pages' pointers updated in the same pass. Options at review: (a) move named items + fix pointers, (b) leave named items in scratch as permanent residents, (c) blanket call for all 10. The `seeds/` judgment call (memory/archive vs cold) rides the same word.

---

## Execution receipt — Sep 18, ~7:00 PM MDT (blanket call + delete, Shane's word)

**Held list: blanket call executed.** All 10 moved, pointers fixed same-pass (11 live pointers across memory/reference/, skills/, 0 residue on re-scan):

| Item | Destination |
|---|---|
| `blind-sort/` (registration; phase1/1b already lived there) | `cold/blind-sort/` |
| `seeds/` | `cold/seeds/` |
| `ci-workflow-ready.yml` | `cold/scratch-archive/2026-09/` |
| `stamp-fix.bundle` | `cold/scratch-archive/2026-09/` (intact — parent-spec delete still gated on upstream merge) |
| `write-time-verification-brief.md` | `cold/scratch-archive/2026-09/` |
| `glm-5.3-sports-car-review.md`, `model-comparison-2026-09-04.md`, `intelligence-vs-cost-2026-09-04.svg`, `rename-process-test.md`, `stamp-normalize.py` | `memory/archive/` |

**Sent-letter duplicates: 5 deleted, each re-verified before deletion.** Two corrections to this plan's record, caught at execution:

1. **Canonical paths were wrong.** This plan says `memory/letters/` — no such directory exists. The letters' real home is workspace-root `letters/`. Both file-canonicals (littlebird reply, phase2 delivery) verified there, bodies identical headers-aside.
2. **The claude canonical was mispaired.** `letter-claude-phase2-receipt-2026-09-05.md` is not a copy of the phase2 *delivery* letter — it is my own receipt-*ack* back to Claude. Its canonical is the sent thread (eb7d4a7d), text confirmed in the Sep 6 conversation transcript. Deleted on that basis, not on the plan's claim.

Also verified before deletion: spec draft carried verbatim in the #71 comment; v2 reply + routing ack confirmed in conversation transcripts. `scratch/` now 13 residents (11 KEEP + 2 renders), all active.
