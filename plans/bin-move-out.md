---
status: in-review
date: 2026-09-14
links:
  spec: specs/pipeline-artifact-layout.md (PR #64, merged — Migrations §1)
  issue: 70
---

# Plan: bin/ Move-Out — All 13 Tools Repo-Side

Implements Migrations §1 of the parent spec. The brownfield rule governs the whole plan: **characterization tests BEFORE the move — no test, no refactor.** Workspace `bin/` is gitignored with zero git history, so the live copies are the only record until they land here. This plan ends (no edits) before implementation begins; execution starts only on Shane's approval of this plan.

After the move, live `/workspace/bin/` is deployment — synced ONLY from `origin/main` (parent spec, structure + boundaries). Tool paths do not change live-side; callers keep working.

## Inventory — the 13, enumerated live (Sep 14, 2 PM MDT)

| # | Tool | Live | Repo home today | Tests today | Action |
|---|---|---|---|---|---|
| 1 | fleet-inbox-check | 13,125 B | — | 2 suites workspace-side (`test-fleet-inbox-check.sh`, `test_fleet_inbox_check_reply_states.py`) | move + port suites |
| 2 | fleet-issue-check | 5,294 B | — | none | move + characterize |
| 3 | gh | 42 MB binary | — | n/a | **decision D1** |
| 4 | gh-api | 3,539 B | — | `gh-api.test.mjs` (bun) | move + port suite |
| 5 | gh-app-token.mjs | 6,716 B | `bin/` (PR #68) — cmp identical Sep 14 | `gh-app-token.test.mjs`, 8/8 (bun), workspace-side | verify-only + port suite |
| 6 | memory-lint | 30,023 B | `checks/` (PR #56 canon) — cmp identical Sep 14 | 4 suites, already repo-side | verify-only (home stays `checks/` — spec Open Q2) |
| 7 | now | 212 B | — | none | move + characterize |
| 8 | research-lint | 5,536 B | — | `test_research_lint.py` workspace-side | move + port suite |
| 9 | rm-guard/ | 1 file (`rm`) | `bin/rm-guard/` — cmp identical Sep 14 | none | verify-only + characterize |
| 10 | send-letter.sh | 7,292 B | — | none (has `--dry-run`) | move + characterize (dry-run paths only) |
| 11 | transcript-diff-prompt.md | 6,003 B | — | n/a (prompt file) | **decision D2** |
| 12 | transcript-diff.py | 5,435 B | — | none | **decision D2** |
| 13 | transcript-gather.py | 12,533 B | — (skill twin identical: `skills/transcript-diff-gather/scripts/`) | none | move + characterize |

Excluded, not tools: `__pycache__/` (regenerated deployment artifact).

New moves if D1 = exclude and D2 = migrate: **9 tools** (#1, 2, 4, 7, 8, 10, 11, 12, 13), plus **5 test suites** ported workspace→repo. The three already-repo-side tools (#5, 6, 9) get verification receipts only — their bytes never leave the repo.

## Decision points (the review's asks)

**D1 — `gh` (42 MB vendored binary).** Third-party gh CLI 2.100.0, installed Sep 12 — a dependency, not authored tooling. Options: (a) exclude from migration — its deployment story is the documented download-and-relink procedure already on `reference/infra/gh-app-token`; (b) commit raw — +42 MB in every clone, forever; (c) git LFS — not set up in this repo. **Recommendation: (a) exclude.** It is the only one of the 13 I didn't write.

**D2 — transcript-diff pair (retired purpose).** `transcript-diff.py` + `transcript-diff-prompt.md` were the journal diff tracker; the schedule is retired (verified live Sep 14 — no transcript-diff schedule exists) and the files sit untouched since Sep 1. Options: (a) migrate as-is — the spec's "all 13" was ratified the same evening as the retirement, so it counted these eyes-open; bytes preserved, git history begins, no schedule re-attaches; (b) archive to `cold/` as retired tooling. **Recommendation: (a) migrate as-is.** If the journal ever wants a tracker again, that is a new spec either way.

**Stated constraint (not a decision):** memory-lint's repo home stays `checks/memory-lint` — consolidation is the parent spec's Open Question 2, explicitly not mandated there, so not changed here.

## Phase A — Pin (characterization; no tool moves)

**A0 — Twin verification receipts.** cmp the three already-repo-side tools against live (`gh-app-token.mjs`, `rm-guard/rm`, `checks/memory-lint`); receipt in `experiments/bin-move-out/twins.md`. Pre-verified Sep 14 (all three identical); re-verify at move time — any drift = STOP and surface, never overwrite either side (the clobber rule).
*Verify:* receipts exist; any drift halts the phase with both bytes preserved.

**A1 — Test inventory reconciliation.** One row per migrating tool: existing suites (workspace + repo), runner format (`.py` / `.sh` / `.mjs`-bun), gap flag. Output: `experiments/bin-move-out/test-inventory.md`.
*Verify:* every one of the 13 maps to exactly one row; the gap list matches the inventory table above.

**A2 — Pin runs (existing suites, live copies).** Run each workspace-side suite against its live `/workspace/bin/` copy and receipt the output (counts, key assertions): gh-app-token (8/8), gh-api, fleet-inbox-check ×2, research-lint. memory-lint's pin is the standing repo CI green on main (its suites already live repo-side against the cmp-identical canonical) — receipt the latest run.
*Verify:* each pin receipt shows its known-good count; zero red results unreceipted.

**A3 — Gap suites (tools with no tests anywhere).** Write characterization suites for fleet-issue-check, now, rm-guard, send-letter.sh, transcript-gather.py. Offline paths only (run-all.sh constraints: no network, temp-dir fixtures): argument validation and usage output; refusal/guard behaviors (fleet-issue-check's bare-run refusal class, rm-guard's blocklist); `now`'s output format; send-letter.sh via `--dry-run` only — never a live send; transcript-gather pins argparse/usage paths, not live transcript reads. Characterization documents what IS: a failing pin means a real bug surfaced — pin it anyway with the failure receipted and an issue filed; no fix rides along.
*Verify:* each gap suite green against the live copy (or green-with-receipted-known-failure); suites run clean under run-all.sh conventions.

## Phase B — Move (build; starts only on plan approval)

**B1 — run-all.sh discovery extension.** Add `tests/test-*.sh` (bash) and `tests/test-*.mjs` (bun when present — both `.mjs` suites are `bun:test` format, verified Sep 14). If bun is absent in CI, `.mjs` suites skip-with-note and their pin receipts carry the coverage — bun-in-CI is a future infra question, not this slice.
*Verify:* `bash tests/run-all.sh` locally executes every discovered suite; the discovery globs receipted in the PR body.

**B2 — Port the five workspace suites repo-side.** gh-app-token, gh-api, fleet-inbox-check ×2, research-lint → `tests/` under the discovery naming convention (hyphens), path references adjusted from `/workspace/bin/...` to repo-relative. Content otherwise ported faithful — no behavior edits during a port.
*Verify:* each ported suite passes against the repo copy; counts match the A2 pin receipts exactly.

**B3 — Land the nine tools.** Copy the nine live tools into repo `bin/` (per D1/D2 outcomes — nine if gh is excluded and the diff pair migrates). Live `/workspace/bin/` is untouched in this phase — the first and only write to live happens in Phase C.
*Verify:* `cmp` each landed copy against its live pin copy — byte-identical, all nine; `git status` shows only expected paths.

**B4 — PR.** One PR: landed tools + ported suites + run-all.sh extension. Body links spec, plan, issue; carries the D1/D2 resolutions, pin receipts, and twin receipts. CI green required.
*Verify:* CI green; PR open for Shane's review — **no self-merge** (his Sep 14 word).

## Phase C — Deployment cutover (post-merge only)

**C1 — Sync live from origin/main.** Clean clone of main → copy repo `bin/*` over live `/workspace/bin/` → cmp verify each. `gh` and `__pycache__/` untouched (unmanaged per D1). Before this sync, live was the source; after it, `origin/main` is.
*Verify:* cmp live vs origin/main for every managed tool, zero diffs.

**C2 — Smoke.** Each tool invoked once live-side — the heartbeat itself smokes fleet-inbox-check, fleet-issue-check, now, gh-api, gh-app-token; manual smokes: memory-lint, research-lint, rm-guard, send-letter `--dry-run`, the transcript pair's usage paths.
*Verify:* smoke receipts; zero behavior change vs pin.

**C3 — Caller sweep + page updates.** Paths are unchanged live-side (same location, new source), so callers keep working — confirm by grepping procedures/skills for `/workspace/bin/` references; update owning reference pages that still call live `bin/` the source of truth (the gh-app-token page already says repo — verify each owner).
*Verify:* zero callers broken; pages updated; sweep receipted.

## Phase D — Learning + close

Learning note per the parent spec's Learning gate — what the first full Migrations execution taught about the pipeline layout itself. Issue #70 close-out comment with the full chain linked; `notes.md` updated; queue advances to #71.
*Verify:* learning note filed; issue closed with PR link; plan status → `executed` in the merge.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Live↔repo drift discovered at move time (clobber class) | A0 re-verify at B3; any drift = STOP + surface, both bytes preserved, neither overwritten |
| Characterization pin fails (real bug surfaces) | Pin what IS; failure receipted + issue filed; no fix rides along |
| send-letter.sh sends real mail from a test | `--dry-run` paths only; no real recipients anywhere in fixtures |
| CI lacks bun → `.mjs` suites can't run there | Skip-with-note in run-all.sh; pin receipts carry coverage; bun-in-CI = future question |
| Token expiry mid-push | Re-run through the wrapper; token never in the remote (tokenless push pattern, Sep 13) |
| Destructive cleanup reflex | No `rm -rf` anywhere; `rm -r` only inside the scratch clone, only after the push receipt |
| A caller references bin/ by a path that changes | Paths don't change (deployment, same location); C3 sweep confirms |
| Scope creep into checks/-consolidation or skills-side copies | Both explicitly out of scope (Open Q2; skills are their own domain) — named so the boundary is visible |

## Definition of done

All 13 dispositioned: three verified twins, nine landed repo-side (or per D1/D2 outcomes), one excluded-by-decision with receipt. Every migrating tool: pinned → moved → cmp-identical → synced → smoked. run-all.sh green with all ported suites. Live `bin/` deployment-only, synced from `origin/main`. Learning note filed; issue #70 closed with the full chain (spec → plan → PR) linked.
