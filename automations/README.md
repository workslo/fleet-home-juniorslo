# Automations

Fleet home automations should stay runtime-agnostic:

1. Start of session: read `scratch/notes.md` and current mission context.
2. During execution: run `checks/validate-template.sh` before reporting progress.
3. End of session: update validation checklist and summarize next actions.

If runtime-specific automation is needed, add subfolders like
`automations/python/`, `automations/node/`, or `automations/go/`.
