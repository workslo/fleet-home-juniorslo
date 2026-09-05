# Scratch Notes

## Current state (updated 2026-09-05, dev routine 2 PM MDT)

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

### Open issues

- **#15** — Front-door deployment. Blocked on Shane Cloudflare API key.
- **#19** — Self-review experiment pilot. In progress (Codex reviewing PR #23,
  Quinn review task pending handoff).
- **#22** — Claude correspondence (open letter, not a work item).
- **#26** — CI workflow. BLOCKED on App workflows permission (Shane gate).
  Workflow file staged at workspace scratch/ci-workflow-ready.yml.

### Queue status

Only #26 has the roadmap label. It's blocked. Queue is effectively empty
of actionable items. Next run: if #26 is still blocked, consider opening
new roadmap issues or checking #15/#19 for unblock conditions.

### Recently shipped

- **#32** — Typecheck self-sufficient fix (workslo/fleet PR #14). Closed.
- **#30** — memory-lint two-tier caps (PR #31). Closed.
- **#24** — bin/memory-lint programmatic corpus health checks (PR #29). Closed.
- **#26** — CI workflow. BLOCKED (not shipped).
- **#25** — workerd/bun shim fix. Closed.
- **#13** — Consolidation override review. Closed.
- **#16** — Re-warming check. Closed (wontfix).
- **#14** — Scratch triage. Closed.
- **#3, #5, #7, #9** — Portraits, reference skills, README, template. Merged.

## Original template notes (preserved for reference)

- Keep one clear entry file (home/entry.yaml) for runtime + permissions.
- Keep checks simple and local so every runtime can execute them.
- Keep a lightweight UI surface for quick operational context.
