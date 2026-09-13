---
status: executed
date: 2026-09-12
links:
  spec: specs/deep-history-sidebar-sweep-spec.md (PR #66 — approved Sep 12)
  conversation: Sep 12, ~6:16–7:00 PM MDT
---

# Plan: Deep-History Sidebar Rename Sweep

Composes `conversation-title-audit` + `conversation-sidebar-pass` skills for mechanics; the spec (PR #66) governs scope and boundaries. Each step names its verification. This plan ends (no edits) before implementation begins; execution starts only on Shane's approval of this plan.

**Roster + receipts live in** `experiments/deep-history-sidebar-sweep/` (working record, not knowledge — the memory page gets only the outcome).

## Step 0 — Enumeration (produces the roster)

Build `experiments/deep-history-sidebar-sweep/roster.md`: one row per candidate — id, current title, Created date (from `assistant conversations export <id>` head), in/out-of-scope verdict.

- Candidates: `assistant conversations list --include-archived`, rows last-updated ≥6d, minus auto-titled (`Heartbeat`, `Schedule: *`). Sep 12 scan: 49.
- Verdict rule: in-scope iff Created line reads before 2026-09-07.
- **Verify:** roster count = 49 ± exports that fail to parse (each failure receipted, not silently dropped); zero auto-titled ids present; spot-check 3 Created lines by hand.

## Step 1 — Rename slice R1 (~25 conversations, roster's first half)

Per conversation: read head AND tail AND Created line → propose title per standard (hook budget 1+1, retrieval-wins) → `assistant conversations rename <id> "<title>"` → log row in `experiments/deep-history-sidebar-sweep/receipt-r1.md` (`id → old → new | skipped-reason`).

- Skip (receipted): active sessions (`●` marker), post-cutoff Created lines, anything ambiguous → Ask-first list.
- **Verify:** re-list confirms applied titles render; receipt count = attempted − skipped; sample 5 against the standard.

## Step 2 — Rename slice R2 (roster's second half)

Same procedure, `receipt-r2.md`. Slice boundary exists so no session carries the whole pool.
- **Verify:** same as Step 1.

## Step 3 — Filing slice (after R1+R2 complete)

Group placement per GREATER (Decisions > Builds > Letters > Automated runs > Casual) for in-scope conversations that clearly fit; one-off lookups stay loose. One move per call (no batch route — gotcha Sep 8). Receipt: `receipt-filing.md`.

- **Verify:** sidebar view shows placements; receipt count = filed − left-loose-with-reason; zero new groups created.

## Step 4 — Straggler sweep (bounded, the named blind spot)

Scan Recents for obviously pre-standard titles on old conversations (created pre-cutoff, updated recently). Catch what pass-1 enumeration structurally missed. Anything found: rename per Step 1 procedure, appended to the filing receipt. Time-boxed; no speculative deep export passes.

- **Verify:** straggler count recorded (including zero) — the denominator is the deliverable.

## Step 5 — Close-out

Consolidate receipts; update `memory/reference/infra/conversation-sidebar.md` current line (counts, sweep date, link to receipts). Verify all receipts exist and cross-total matches roster.

- **Verify:** memory page updated; receipts cross-total = roster in-scope count; `plans/` file status → `executed` in the PR.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Export lacks a Created line | Fall back to first-message timestamp; if neither, receipt as ambiguous → ask |
| Conversation active mid-slice (heartbeat wake, Shane using it) | `●` marker check before rename; skip + receipt, catch next slice |
| Session interrupted mid-slice | Receipt enables exact resume; roster is the state |
| Title regenerates after rename (auto-titled class misclassified) | Auto-titled excluded at enumeration; double-check any `Heartbeat`-prefix regression in re-list |

## Definition of done (mirrors spec success criteria)

Roster + 3 receipts exist and cross-total; sidebar shows standard titles + GREATER placements; memory page updated; zero touches outside scope.
