# Spec: Deep-History Sidebar Rename Sweep

Status: DRAFT — awaiting Shane's review. Merge = approval.
Locked parameters (Shane, Sep 12 ~6:50 PM MDT): cutoff = created-before-the-Sep-7-sweeps (principle, not age); rename + filing both, on separate slices; slicing at JuniorSLO's judgment.

## Objective

The sidebar is Shane's triage surface: 7 agents, a job, 3-second scans. The Sep 7–8 sweeps titled and filed recent history, but ~40–50 conversations predating the title standard remain unrenamed/unfiled — they don't answer "what domain, what happened, do I care" at a glance. Done means: every conversation created before the Sep 7 sweeps carries a standard title, group placement applied where it clearly fits, with a receipt proving it and nothing out of scope touched.

## Population

**In scope:** conversations created before 2026-09-07 (sweep-1's date — the standard's birth), excluding anything already conforming to the title standard.

**Excluded:**
- Auto-titled sessions (`Heartbeat`, `Schedule: *`) — names regenerate; renaming them is painting a river.
- Heartbeats landing loose in Recents — accepted design (Shane, Sep 8). No schedule-job groupId edits.
- Anything already titled to standard, even if pre-cutoff (sweeps 1–4 output).

**Enumeration (two passes, at slice time):**
1. `assistant conversations list --include-archived` → candidates = rows with last-update ≥6 days old, minus auto-titled. Sep 12 scan: **49 candidates**.
2. Per candidate: `assistant conversations export <id>` — read the **Created line** to confirm pre-Sep-7 creation. The list's stamp is last-updated, not created; export is the authority.

**Known blind spot (named, accepted):** conversations created pre-cutoff but updated within the last 6 days are invisible to pass 1. They were mostly covered by sweeps 1–4 (which touched then-recent history). The receipt carries the denominator so coverage is auditable; stragglers get caught by the next touch rather than by an speculative scan.

## Process (per conversation)

Composes the existing standard — this spec does not redefine it:
- Title standard + failure modes → `conversation-title-audit` skill; taxonomy + GREATER rule → `conversation-sidebar-pass` skill; full rules → `memory/reference/infra/conversation-sidebar.md`.
- Read head AND tail AND the Created line before proposing. Head/tail disagreement → retrieval wins.
- Hook budget: 1 primary hook + 1 parenthetical. N ≥ 3 record-worthy topics → the title carries the most-likely-searched hook; the record fans out the rest.

## Slices

Two slice types, **not mixed** (locked):

1. **Rename slices** (~2, ~25 conversations each): propose + apply titles per standard. Skipped-with-reason rows allowed (e.g. created post-cutoff on second read).
2. **Filing slice** (1, after renames complete): group placement per GREATER for conversations that clearly fit the four groups or Automated runs. One-off lookups stay loose by design.

Receipt written at each slice close before the next begins: `id → old title → new title → group | skipped-reason`.

## Commands

```
assistant conversations list --include-archived
assistant conversations export <id>          # Created line + head/tail read
assistant conversations rename <id> "<title>"
```

No batch move route exists — one move per call (gotcha, Sep 8).

## Boundaries

- **Always:** read-before-rename (head + tail + Created); receipt every slice; re-list after applying to confirm.
- **Ask first:** any new group (taxonomy is Shane's); re-titling anything already conforming; any conversation whose Created line reads post-cutoff.
- **Never:** touch auto-titled sessions; attempt batch moves; delete or archive anything; alter heartbeat landing behavior.

## Verification

After each slice: re-list, confirm applied titles render; cross-check receipt count = in-scope count − skipped count; spot-check a sample against the standard. Coverage claims carry their denominator.

## Success Criteria

1. Every enumerated in-scope conversation renamed to standard (or receipted as skipped-with-reason).
2. Filing slice applied per GREATER; taxonomy unchanged.
3. Receipts exist for all slices.
4. `conversation-sidebar.md` updated (current line + counts).
5. Zero touches outside scope — especially zero auto-titled sessions.

## Open Questions

None — parameters locked Sep 12. Execution itself is a separate approval.
