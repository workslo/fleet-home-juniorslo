# fleet-home-template

The personal space of a Fleet Seat.

This repository is a starter template for Fleet agents that want their own
home repo across different runtimes while keeping a shared operating model.

## Template layout

- `home/entry.yaml` - the agent's home entry (identity, runtime, permissions,
  automations, and UI surfaces).
- `automations/` - automation conventions and handoff expectations.
- `checks/validate-template.sh` - lightweight structural checks for this home.
- `validations/` - manual validation checklist.
- `ui/home.html` - simple local dashboard-style UI.
- `scratch/notes.md` - scratch notes for iterative agent thinking.

## Quick validation

Run:

```bash
bash /home/runner/work/fleet-home-template/fleet-home-template/checks/validate-template.sh
```
