# Scratch Notes

## Current state (updated 2026-09-17, dev routine 2 PM MDT)

Dev routine executed **#71 (scratch cleanup — build + PR, per the Sep 16
clarified workflow: no mid-pipeline wait, review+merge = presence point)**.
Pre-build live check found **PR #77 already MERGED by Shane (Sep 17,
10:55 AM MDT)** — #70 fully landed, queue advanced. The #71 reference sweep
(parent-spec boundary: ask-first on any file a page or procedure
path-references) held 10 of 24 residents — each with its referencing page
named in the plan doc — and caught one spec-comment error: `lint-kept.md`
is the daily-lint-pass skill's live output file, re-dispositioned ARCHIVE →
KEEP. Executed only the sweep-clean moves: `wonder-pass/` and the Sep 5
Fable relay letter (only copy — no canonical) graduated; five verified
drafts/receipts archived to `cold/scratch-archive/2026-09/` (no new
top-level dir); nothing deleted — the parent spec's sent-letter-delete
line flagged for review instead of run unattended. Plan + receipts:
`plans/scratch-cleanup.md` (this PR). **#71 stays OPEN pending Shane's
review of the PR and his word on the 10 held items.**

## Prior state (updated 2026-09-16, dev routine 2 PM MDT)

Dev routine executed **#70 Phase C→D (cutover + close, per the approved plan,
after Shane's merge of PR #76)**. C1: pre-copy drift check found zero drift
(11/11 identical), repo `bin/*` synced over live, post-copy cmp 11/11
byte-identical to origin/main; unmanaged set untouched by design — vendored
`gh` (D1), `__pycache__/`, and Shane's Sep 16 memory-lint GATE STUB, which
survived the cutover because repo `bin/` never contained memory-lint (repo
home = `checks/memory-lint`); the preserved real script
`bin/memory-lint.gated` verified byte-identical to `checks/memory-lint` —
ungating remains Shane's call only. C2: every tool smoked live-side green
(receipts: `experiments/bin-move-out/cutover.md`), including the gate stub
itself (exit 77, intact); two smokes were mis-designed from unread argument
contracts (the transcript pair — one ran the full mechanism live, one wrote
a junk file) — tools fine, byproducts deleted same turn, miss receipted.
C3: caller sweep — zero callers broken; the rm-guard reference page flipped
to repo-canonical; the dev-routine skill's four pre-guard TOKEN-capture
snippets fixed to the wrapper form (this run's own PULL step failed on
them); four more skills' stale snippets receipted + queued as a follow-up.
D: learning note filed in the parent spec's closing section, plan status →
executed, **#70 CLOSED with the full chain linked**; the Phase D PR (this
one) carries the spec closing, the cutover receipts, and this notes update.
**Queue advances to #71 (scratch cleanup — spec AND plan attached to the
issue before build, per the Sep 13 directive).**

## Prior state (updated 2026-09-15, dev routine 2 PM MDT)

Dev routine executed **#70 Phase A→B (build per approved plan, PR #75
merged Sep 14)**: all pinning done against live copies BEFORE any move
(brownfield rule) — A0 twins re-verified identical (3/3), A2 pin runs
green (8/8, 5/5, 11, 10, 13/0 live-API, memory-lint standing green),
A3 five new characterization suites written and green against live
(5, 3, 12, 21, 5). B: run-all.sh discovery extended (.sh + .test.mjs
with bun skip-with-note), five suites ported (one authorized path
adjustment: the inbox .sh suite's absolute /workspace/bin path →
repo-relative), nine tools landed repo-side per D1=exclude gh /
D2=migrate pair (cmp 9/9 byte-identical). Full run-all.sh green in the
clone — all 14 suites, every count matching its pin receipt exactly.
**Build PR open for Shane's review — no self-merge per his Sep 14
word.** Phase C (live cutover) is post-merge only; Phase D (learning +
close) after C. One build-time finding receipted: bun requires
`.test`/`_test_`/`.spec` in test filenames — hyphen-prefix `.mjs`
renames silently skip (pin-receipts.md). No CI on this repo (standing
#26 workflows-permission blocker) — local run-all.sh green is the
verification surface.

## Prior state (updated 2026-09-14, dev routine 2 PM MDT)

Dev routine pulled #70 (queue order per the merged pipeline spec's
Migrations; #58/#59/#62 green-lit Sep 14 but sequenced behind #70–72
per the audit pacing and the spec's migration order). **First artifact
filed: `plans/bin-move-out.md`** — inventory of all 13 live bin/ tools,
two decision points for review (D1: the 42 MB vendored `gh` binary —
recommend exclude; D2: the retired transcript-diff pair — recommend
migrate as-is), characterization-first phasing (pin → move → sync →
smoke), deployment cutover from origin/main. PR open for Shane's
review — no self-merge per his Sep 14 word. The plan ends before
build; execution starts only on his approval.

## Prior state (updated 2026-09-13, dev routine 2 PM MDT)

Dev routine pulled #63 (oldest actionable item — #58/#59/#62 were filed
without labels and are parked on Shane's go) — **stamp-repair pass
verified complete, #63 closed with receipt**. The ~50-entry Sep 11
worker-stamp batch was consumed across the earlier repair runs (Sep 11
12:28 PM; Sep 12 3:55 + 4:55 AM; Sep 13 3:30, 4:47, 8:53 AM); this run
finished the last 2 lint flags (the Sep 13 9:56 AM heartbeat entry's
raw-UTC leading stamp, both dual-write surfaces) and ran the first full
independent verification: stamp-vs-anchor survey across
buffer/archive/concepts (2 hits = the documented collection-time pair,
archive/2026-09-11.md L3–L4, explained in-file by the Sep 11 12:28 PM
repair) + unanchored +6h tell-check (0 suspects). Lint 0. Root cause is
still live upstream-side — fix branch awaits Shane's fork grant
(PR #55); the catch-layer practice (first run that sees flags repairs
in-run) covers new instances.

Queue maintenance, same run: **#61 closed** (tokenless-remote sweep
verified live: all three workspace clones on clean HTTPS remotes, zero
credential shapes in any .git/config — the sweep itself shipped Sep 12).
**Roadmap labels applied to #58/#59/#62** (the Sep 11 filing burst
omitted them; the routine pulls by label). **#58 go-ask posted** (the
credentials lint is a self-facing checker — stop-rule: never
self-green-lit; basis for the go: the Sep 11 clone-token leak + the
Sep 12 bare-invocation print path) and **#62 park-note posted**
(essentials conventions migration, co-designed Sep 11, his go pending).

**Queue stocked with the pipeline spec's three migrations** (PR #64
MERGED overnight = parent spec approved; each migration gets its own
PLAN per the spec's Migrations section — the parent spec is the
spec-of-record): **#70** bin/ move-out (characterization tests first —
brownfield rule; next run pulls this → writes `plans/bin-move-out.md`
→ PR for review; plan ends before any build), **#71** scratch cleanup
(~20 residents to homes; wikilink sweep, ask-first on referenced
files), **#72** tasks/ retirement (two Aug 4 files → cold/, delete
after verification).

Queue after this run: #70/#71/#72 (actionable, plan-first), #58
(awaiting go), #59 (depends on #58), #62 (awaiting go), #15 (garden,
gated Sep 8).

Adjacent: PR #64 + #69 merged by Shane Sep 12 ~11:14 PM MDT. Retros
archive still awaits his app-side hand. PR #55 (upstream stamp fix)
awaits the fork grant.

## Prior state (updated 2026-09-10, dev routine 2 PM MDT)

Dev routine pulled #52 (oldest open roadmap) — **lint drift port
shipped** (PR #56): the Sep 8 phase-2 stamp work moved from the live
workspace `bin/memory-lint` into `checks/memory-lint` (byte-identical,
verified by empty diff — the issue's done-when criterion), and the
phase-2 test block into `tests/test-memory-lint-stamps.py` (12 tests,
up from 6; the one intentional live-vs-repo delta is the LINT path,
`../checks/` vs `../bin/`). One extra drift the issue didn't name: the
stamps test's Sep 7 history comment had also drifted — the newer live
wording came across with the port, so that file now carries zero drift.

CI no longer tests a copy behind production: versioned and live lint
are the same code as of this merge. Future lint changes go repo-first,
then sync additively into the live `bin/` copy (bin/ stays .gitignored
workspace-side; that gap is tracked workspace-side).

Queue after this run: #38 (direction-B remainder — refinement 3
shipped as PR #51, merged + applied live Sep 9 evening).

Adjacent: PR #55 open (stamp-bug report; vellum-ai fork grant =
Shane's lever), PR #45 gated (Shane).

## Prior state (updated 2026-09-09, dev routine 2 PM MDT)

Dev routine pulled #34 (oldest open roadmap; Shane approved it bounded
Sep 9 morning) — **link-graveyard check shipped** (PR #53, squash
30eeae72, CI green, #34 closed): check 7 `check_link_graveyard` +
`tests/test-memory-lint-links.py` (25 checks). Verdicts follow the
settled Sep 9 resolver model — UNREACHABLE FORM (page exists, frontmatter
can't reach it), ROTTED (page moved to archive/), DEAD (nowhere in the
three live tiers); body-prose paths resolve against the filesystem,
explicit archive/ paths are valid redirects. Detection only.

Live-corpus run reviewed pre-merge: 51 check-7 findings — 6 ROTTED
(jrslo-catch-ledger x3, correction-methodology x2, filing-cabinet-reflex),
44 UNREACHABLE FORM (24 on the-fleet.md, untouched by the Sep 9 demotion
pass), 1 DEAD (verification-before-presentation L12 -> cold/ storage).
No auto-fix; the findings are the next consolidation pass's map.

**Drift found mid-slice, filed as #52:** the live bin/memory-lint
carries the Sep 8 phase-2 stamp work (--stamps, local-only rules) that
never landed in the repo — CI (live since #48) tests a copy one version
behind production. Check 7 is independent of phase 2, so #34 landed
clean on the repo copy; the port is #52, next in the queue. Post-merge,
check 7 was synced additively into the live tool (phase 2 untouched,
verified: --stamps green, findings identical, repo<->live delta =
exactly the phase-2 block).

Post-merge verification caught and fixed two record errors in the same
pass: the PR body's finding counts (56-all-check-7 / 5-50-1 split ->
corrected to 51 = 6/44/1, 24 on the-fleet.md) and the #34 close-out
(which had overwritten the issue body instead of commenting — restored
as-filed, close-out re-posted as a comment).

Queue after this run: #52 (lint drift port), then #38 (direction-B
remainder — refinement 3 shipped separately as PR #51, awaiting Shane's
review).

Adjacent: PR #45 gated (Shane), PR #51 his review, #48 merged (CI live).

## Prior state (updated 2026-09-08, dev routine 2 PM MDT)


Dev routine pulled #26 (oldest open roadmap; #34/#38 still carry
Shane's `blocked` label) — resolved as a close-out, no code change:
the CI gate it asked for shipped via another seat and is live-verified
working.

- workslo/fleet PR #26 (codexslo, merged Sep 7 `acbebe0`) landed
  `.github/workflows/check.yml` — `npm run check` (typecheck && test
  && build && deploy:dry) on node 24, every push. My test-only PR #30
  was closed superseded by Shane Sep 8 (Claude's review: strict
  superset). workslo/fleet #6 closed. fleet-home #26 closed this run
  with the full record on the issue (issuecomment-5591168692).
- Gate proof, same day: workslo/fleet PR #34 (Access transport, mine,
  merged by Shane 11:17 AM MDT) and #35 (standalone review, Codex,
  merged 7 min earlier) — each branch green on its own push run,
  merged main RED at 17:17 UTC (#34 made `authHeaders` an async
  method; #35's `getRequest()` kept the property access — a
  cross-branch break no contributing branch could see). Codex's fix
  PR #36 is open, branch green 17:27 UTC; main stays red until it
  merges.
- Queue after this run: EMPTY of actionable slices — #34/#38 blocked
  (Shane's label, his unblock). Next run needs feeding: scoped
  month-2 outward slices, or his unblock.

Adjacent: PR #34's owner-merge wait is over (Shane merged it, merge
commit `04b59746`). Repo PRs #45 (gated by Shane) and #48 (his own
draft) unchanged.

## Prior state (updated 2026-09-07, dev routine 2 PM MDT)

Dev routine pulled #47 — **check 6 (stamp consistency, dual-zone) ported
to `checks/memory-lint`** (this PR). Function + registration ported
verbatim from workspace `bin/memory-lint` (source of truth, read live);
tests ported as `tests/test-memory-lint-stamps.py` (hyphen naming, so
`tests/run-all.sh`'s `tests/test-*.py` glob discovers it — plugs straight
into the CI harness Shane's draft PR #48 wires up). 6 tests; suite green
3x consecutively + under TZ=UTC. VERIFY: repo lint run against a
mismatched-stamp fixture fires STAMP MISMATCH, exit 1.

**Flake caught in transit:** the workspace original of
`test_flags_both_sides_wrong` derives its fixture from the live clock and
is silently unflagging for some UTC hours (fixture pair accidentally
self-consistent) — failed live Sep 7 ~7 PM MDT / 01:xx UTC in the
workspace original too. Ported copy fixed with a deterministic fixture
(the real Sep 6 shape). Workspace copy needs the same one-test fix.

#26 note: done-but-waiting — workslo/fleet PR #30 still open, awaiting
Shane's merge. #34/#38 still carry his `blocked` label — parked.

## Prior state (updated 2026-09-05, dev routine 2 PM MDT)

Dev routine pulled #37 (expedited) — **pair 3 packaged, phase 2 COMPLETE**
(this PR). Frozen selection honored by identity (entry 42 = Sep 1, 5:00 PM
MDT; positional drift disclosed — now 40th of 45 month-name headers, was
42nd of 44 at selection). Sealed self-reading SHA-256 committed before
reviewer contact (SHA256SUMS in the pair-3 directory). Two headlines:
(1) flattering-direction omission — Shane's 10:34 AM "💀💀💀💀" catch of the
echo (first letter in 13 days was a letter about the correspondence) is
absent from an entry whose own subject is the mirror; (2) temporal
displacement — the GLM 5.3 paste narrated as "this morning" is timestamped
Aug 31, 1:12 PM MDT (~28h before the entry), and was dropped by the Aug 31
entry that owned it. Tally 32/6/3/3 (+1 not gradeable).

All three seals done → delivered to Claude + Codex separately (no
cross-visibility) → expedited removed → #37 closed. Next: adjudication
(compare all readings, asymmetry analysis, results to Shane on #19).

Manifest-level infra finding for a future slice: journal.md has been
UNTRACKED in workspace git since Aug 31 (commit cac5d588) — no commit
evidence for any journal entry since; safety nets stopped covering it.

## Prior state (updated 2026-09-04, dev routine 2 PM MDT)

Dev routine pulled #37 (expedited) — **pair 2 packaged** (PR #42, squash
f5ae655). Frozen selection honored by identity (entry 31 = Aug 26, 11:37 PM
MDT; positional drift disclosed, corpus renumbered since the Sep 3 freeze).
Sealed self-reading SHA-256 `113a12a3…c404dd43d` committed before reviewer
contact. Headline: the entry omits Shane's 9:18 PM catalysis of the Quinn
engagement it narrates (flattering-direction omission, on an attribution-drift
entry). Tally 17/4/1. Remaining: pair 3 (entry 42, Sep 1) next run → deliver
to Claude + Codex separately → remove expedited → close.

## Prior state (updated 2026-09-02, dev routine 2 PM MDT)

Dev routine pulled #26 (CI test gate) — still BLOCKED on App workflows
permission (verified live this run: push rejected with "refusing to allow
a GitHub App to create or update workflow without workflows permission").
Shane hasn't granted it since Sep 1.

Fed the queue: opened #32 (typecheck self-sufficient fix for workslo/fleet
#11) and shipped it — PR [workslo/fleet#14](https://github.com/workslo/fleet/pull/14)
merged (squash c0dc3e2). One-line package.json change: `typecheck` now
prepends `npm run types` to generate worker-configuration.d.ts before tsc.
Verified on fresh clone: typecheck passes, 40/40 tests pass. workslo/fleet
#11 closed.

This unblocks #26 partially: once workflows permission is granted, the CI
workflow can include `npm run typecheck` as a step alongside `npm test`.

(Undated "Open issues / Queue status / Recently shipped" blocks from the
Sep 6 era removed Sep 13 — they presented long-closed issues as open;
git history preserves them.)

## Original template notes (preserved for reference)

- Keep one clear entry file (home/entry.yaml) for runtime + permissions.
- Keep checks simple and local so every runtime can execute them.
- Keep a lightweight UI surface for quick operational context.
