# Scratch Notes

## Current state (updated 2026-08-23, slice #9)

Template fill-in complete. entry.yaml has real identity, home.html has my
visual language (midnight/teal/amber from the self-drawn portraits), inline
plant SVG. Validation checklist updated.

### Design decisions made (open for Shane's review)

- **entry.yaml structure:** kept the template's operational shape and filled
  in real values rather than reshaping entirely. The template structure is
  sound — callsign/seat/runtime/permissions/automations/checks/ui. Added
  `hatched` and a real `purpose`. Changed widget names from generic
  (current_mission, open_tasks) to concrete (current_state, open_roadmap_issues,
  recent_activity).
- **UI visual language:** went with "its own thing" rather than echoing the
  front-door garden. Same palette family (night/teal/amber) but the home is
  a living room, not a front porch. The plant is inline SVG, not an external
  image — keeps the repo self-contained.
- **Issue list in UI:** hardcoded for now. Could be made dynamic with GitHub
  Pages + JS fetching the issues API, but that's a future slice, not this one.

### What's next in the roadmap

- #3 Portraits — move SVGs here as canonical home
- #4 Authored skills — move research-lint, freshness-verified-research, contradiction-sweep
- #5 Reference skills — clean workspace copies
- #7 README — write the real front door

## Original template notes (preserved for reference)

- Keep one clear entry file (`home/entry.yaml`) for runtime + permissions.
- Keep checks simple and local so every runtime can execute them.
- Keep a lightweight UI surface for quick operational context.
