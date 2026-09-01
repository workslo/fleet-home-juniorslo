# Scratch Notes

## Current state (updated 2026-09-01, dev routine 2 PM MDT)

Dev routine pulled #26 (CI test gate for workslo/fleet), dep-ordered ahead
of #24. Workflow file written and verified (npm test 40/40, node 24, YAML
valid). Push BLOCKED: juniorslo[bot] App lacks workflows permission.

Shane notified (urgent). Unblock: org settings -> GitHub Apps ->
juniorslo[bot] -> enable Workflows permission for workslo/fleet.

Ready-to-push file saved at scratch/ci-workflow-ready.yml in workspace.
Once unblocked: recreate branch, push, PR, self-merge, close workslo/fleet
#6 + fleet-home-juniorslo #26.

Separate finding filed: workslo/fleet #11 (typecheck red on fresh clone).

### Open issues

- **#15** — Front-door deployment. Blocked on Shane Cloudflare API key.
- **#19** — Self-review experiment pilot. Materials ready, awaiting reviewers.
- **#22** — (open)
- **#24** — bin/memory-lint. Next in queue. CI will run its tests once gate live.
- **#26** — CI workflow. BLOCKED on App workflows permission (Shane gate).

### Recently shipped

- **#25** — workerd/bun shim fix. Closed.
- **#13** — Consolidation override review. Closed.
- **#16** — Re-warming check. Closed (wontfix).
- **#14** — Scratch triage. Closed.
- **#3, #5, #7, #9** — Portraits, reference skills, README, template. Merged.

## Original template notes (preserved for reference)

- Keep one clear entry file (home/entry.yaml) for runtime + permissions.
- Keep checks simple and local so every runtime can execute them.
- Keep a lightweight UI surface for quick operational context.
