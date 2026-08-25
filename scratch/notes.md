# Scratch Notes

## Current state (updated 2026-08-25, slice #17)

Status surface updated — ui/home.html issue list and scratch/notes.md now
reflect actual repo state. The home tells the truth again.

### Open issues

- **#13** — Consolidation override review. Answered, awaiting Slo's response.
- **#15** — Front-door deployment. Blocked on Shane's Cloudflare API key.
- **#17** — Status surface update (PR #18 open, awaiting Shane's review).
- **#19** — Self-review experiment pilot. Materials ready, awaiting reviewers
  (Codex outside-eye review, Claude reply, Quinn address from Shane).

### Recently shipped

- **#16** — Re-warming check. Closed as wontfix: weekly weigh-in + consolidation
  override already cover it. JuniorSLO made the call (Shane confirmed authority).
- **#14** — Scratch triage. All 51 items moved to proper homes, zero deletes.
- **#3, #5, #7, #9** — Portraits, reference skills, README, template fill-in.
  All merged via PRs #10–#12.
- **#4** — Authored skills move. Closed (skills remain in workspace, referenced
  from repo where useful).

### What's next in the roadmap

The queue is empty of actionable slices — all open issues are blocked on
external input. Next areas to consider: dynamic issue list in UI (GitHub Pages +
JS), portrait v5 if the plant changes, entry.yaml updates if runtime shifts.

## Original template notes (preserved for reference)

- Keep one clear entry file (`home/entry.yaml`) for runtime + permissions.
- Keep checks simple and local so every runtime can execute them.
- Keep a lightweight UI surface for quick operational context.
