---
status: complete
date: 2026-09-16
links:
  issue: 70
  plan: plans/bin-move-out.md
  build-pr: 76
---

# Phase C cutover receipts — live bin/ → deployment of origin/main

Executed by the dev routine Sep 16, 2 PM MDT slot, immediately after Shane's merge of PR #76 (28d0d15).

## C1 — sync + cmp

Pre-copy drift check (clobber rule): **zero drift — 11/11 identical before any copy.** The Sep 15 build's byte-fidelity held overnight.

Copy: repo `bin/*` (origin/main @ 28d0d15) → live `/workspace/bin/`. Post-copy cmp: **11/11 byte-identical to origin/main** — fleet-inbox-check, fleet-issue-check, gh-api, gh-app-token.mjs, now, research-lint, rm-guard/rm, send-letter.sh, transcript-diff-prompt.md, transcript-diff.py, transcript-gather.py.

Unmanaged by design (untouched):

- `gh` (42 MB vendored binary — D1, excluded; deployment story = the documented download-and-relink procedure)
- `__pycache__/` (regenerated deployment artifact)
- `memory-lint` — **gate stub** (Shane, Sep 16 ~9:12 AM MDT): prints the gated box, exits 77. Survived the cutover untouched because repo `bin/` never contained memory-lint (its repo home is `checks/memory-lint` per the plan's stated constraint). Ungating remains Shane's call only.
- `memory-lint.gated` — the preserved real script, verified **byte-identical to `checks/memory-lint`** at cutover: the gate destroyed nothing; the canonical lives repo-side.

## C2 — smokes (live-side)

| Tool | Path smoked | Receipt |
|---|---|---|
| now | direct | dual-zone one-liner (MDT + UTC), exit 0 |
| gh-app-token.mjs | bare | usage + refusal, no token printed, exit 2 (pinned refusal class) |
| gh-api | `rate_limit` via wrapper | live JSON (core limit 5050), exit 0 — leading-slash form 404s; documented form is slash-free (already on reference/infra/gh-app-token) |
| fleet-inbox-check | direct | live AgentMail report (21 incoming / 13 in 72h), exit 0 |
| fleet-issue-check | bare | pinned no-token refusal, exit 1, wrapper instruction |
| fleet-issue-check | via wrapper | live scan report (21 comments / 6 repos), exit 0 |
| memory-lint (stub) | direct | **gate box printed, exit 77 — the gate is intact post-cutover** |
| research-lint | bare | usage, exit 2 (pinned) |
| rm-guard/rm | `--version` | pass-through to GNU rm 9.7, exit 0 |
| send-letter.sh | `--dry-run` | full preview + "DRY RUN — not sending.", exit 0 (pinned; fixture created + deleted same turn) |
| transcript-diff.py | bare (mis-designed) | **full mechanism ran live**: gathered today (2 conversations), MiniMax M3 inference, diff report written, exit 0 — tool fully functional; unintended live run, byproducts deleted |
| transcript-gather.py | `--help` (mis-designed) | no argparse — `--help` treated as a date arg, wrote junk `--help-input.md`, exit 0; junk deleted |

**Smoke-design miss, receipted:** both transcript smokes were designed from the assumption "bare = usage path" without reading the entry points' argument handling first. The tools work (the accidental full run is the stronger receipt), but the miss produced three unwanted files in `scratch/transcript-diff-reports/` (`--help-input.md`, `2026-09-16-input.md`, `2026-09-16-diff.md`) — all deleted same turn. Practice: read the arg contract before choosing a smoke invocation.

## C3 — caller sweep

Surfaces grepped: HEARTBEAT.md, skills/ (25 files reference bin/), memory/reference/ (15 pages). Letters and archives are frozen correspondence — not sweep targets.

- **Zero callers broken** — paths unchanged live-side (deployment, same location); every invocation smoke green.
- **HEARTBEAT.md**: invocation paths only; zero memory-lint references remain (the Sep 16 stamp-lint removal held).
- **reference/infra/gh-app-token.md**: already says repo = source of truth (verified; no change needed).
- **reference/procedures/rm-guard.md**: UPDATED — canonical flipped from live `/workspace/bin/rm-guard/rm` to repo `bin/rm-guard/rm` (origin/main); live copy marked deployment, byte-identical; noted check 8 fires only when memory-lint runs (the lint is gated).
- **skills/fleet-home-dev-routine/SKILL.md**: UPDATED — all four snippets used the pre-Sep-12-guard `TOKEN=$(node bin/gh-app-token.mjs)` capture (impossible since the guard removed stdout delivery; this run's own PULL step failed on it and re-derived the wrapper form) plus a token-in-URL clone (removed pattern, #61). All four now use the wrapper form; the clone is plain HTTPS through the wrapper.
- **Stale-snippet findings — filed, not fixed** (adjacent rot; follow-up queue item): four more skills carry pre-guard capture patterns — fleet-plugin-install (`TOKEN=$(bin/gh-api --token)` bare), fleet-coordinated-slice-start/references/gotchas.md, fleet-shared-repo-fix/scripts/poll-open-issues.sh (usage comment), vellum-github-app-setup (setup-guide era).

## Phase D

Learning note filed in the parent spec's closing section; plan status → executed; issue #70 closed with the full chain linked. This file is the Phase C receipt set.
