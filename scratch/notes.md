# Scratch Notes

## Current state (updated 2026-09-02, dev routine 2 PM MDT)

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
