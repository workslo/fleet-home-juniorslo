---
title: "Artifact Pipeline — Where Specs, Plans, and Files Live"
status: in-review
date: 2026-09-11
author: JuniorSLO (drafted in conversation with Shane)
links:
  - "Ratified in conversation, Sep 11, 2026, ~6:20–7:40 PM MDT"
  - "Prior art: repos/agent-skills — spec-driven-development, adoption-guide.md (Path B)"
  - "Sibling: home-remote sketch (workslo/home-jr) — separate spec, not this one"
---

# Artifact Pipeline — Where Specs, Plans, and Files Live

## Assumptions I'm making

1. `specs/` and `plans/` are NEW directories in this repo (nothing by these names exists yet — verified against the working tree).
2. "Workspace" means `/workspace` in the assistant container; "repo" means this repository, which is the source of truth for workspace work.
3. The corpus (`memory/`) is knowledge, not a pipeline artifact — it has its own gates and is out of scope except where it links in.

## Objective

Every deliverable — project work, workspace tooling, memory-system changes — flows through one visible chain: **Spec → Plan → Build → Review → Ship → Learning**. This spec defines the *folders and files* each stage's artifact lives in, the links that make the chain walkable, and the gates between stages. Success looks like: any deliverable's position in the pipeline is visible from the filesystem alone, and nothing sits in an "open bucket" without a spec path pointing at it.

Prior art governs the vocabulary: this repo adopts the `agent-skills` lifecycle (`/spec → /plan → /build → /review → /ship`) and its gated phase structure (each phase ends, human reviews, then the next begins). Nothing here invents a sibling of an existing tool.

## Ratified decisions (Shane, Sep 11, 2026)

1. **Spec-first is universal.** Every deliverable gets a written spec before execution. Small things get small specs, never no specs — with the pack's own floor: single-line fixes, typo corrections, and changes where requirements are unambiguous and self-contained may proceed without a spec file.
2. **Plans are separate artifacts**, not sections inside specs. Spec and plan link to each other; each ends before the next stage starts.
3. **Specs and plans live repo-side**, in this repo — the workspace's source of truth — because it is reviewable: issues can be opened against it and PRs link to both.
4. **Code-change gate.** Any write that affects *code* (as opposed to artifacts) requires a spec AND a plan, linked to the implementation slice (the "build").
5. **Scratch is for disposables only** — write the script, run it, delete it. The directory must be empty-able at any moment with zero information loss.

## Project structure — where things live

```
fleet-home-juniorslo/          ← SOURCE OF TRUTH (this repo)
  specs/<topic>.md             ← one spec per deliverable
  plans/<topic>.md             ← one plan per spec, linked
  bin/                         ← tool source (repo-first; PR #56 convention)
  tests/                       ← tests live next to what they test
  experiments/                 ← experiment data (diff reports, pilot materials)
  home/ portraits/ ui/         ← shipped artifacts (existing, unchanged)
  automations/ validations/    ← existing, unchanged

/workspace/                    ← RUNTIME (deployed from the repo)
  bin/                         ← deployed copies, synced ONLY from origin/main
  tests/                       ← deployed copies, same rule
  scratch/                     ← disposables ONLY (write, run, delete)
  memory/                      ← the corpus — knowledge tier, NOT pipeline artifacts
  tasks/                       ← RETIRED by this spec (contents: two stale Aug 4 files)
```

### Spec files — `specs/<topic>.md`

Frontmatter (required): `status`, `date`, `links` (issue #, plan path). Body follows the pack's six-area template, adapted:

1. **Objective** — what and why; who reviews it; what done looks like.
2. **Assumptions** — surfaced up front, numbered, correctable ("→ Correct me now or I'll proceed").
3. **Structure** — the files this work creates, moves, or retires, with paths.
4. **Testing strategy** — how each step's result gets verified.
5. **Boundaries** — always do / ask first / never do.
6. **Plan link** — points at `plans/<topic>.md` (created only after this spec is approved).

### Plan files — `plans/<topic>.md`

Frontmatter: `status`, `links` (spec path, issue #). Body: numbered steps, **each step naming its verification** ("how I'll know this step worked"). A plan exists only after its spec is approved; the plan ends (no edits) before implementation begins.

### The links that make the chain walkable

- Issue → spec path (in the issue body). Spec → issue #, plan path. Plan → spec path. PR → plan and spec. A reader can start anywhere and walk the whole chain.
- A threads.md item **without a spec path is, by definition, unspec'd work** — its next action is "write the spec."

## Lifecycle — statuses and gates

**Spec:** `draft → in-review → approved → (work) → shipped | retired`
**Plan:** `drafted → in-review → approved → executed` (only after spec approval)

| Gate | Rule | Where it lives |
|---|---|---|
| Spec approval | Explicit Shane approval in the thread; spec ends first | review habit, per spec |
| Plan-end | Plan completes and ENDS before implementation (Shane, Sep 11) | Authorization Gates |
| Code-change | Code writes need spec + plan linked to the slice | this spec, decision 4 |
| Merge | PR + CI green + Shane's review before merge | repo convention |
| Learning | Nothing retires without the learning note filed | spec closing section |

## Testing strategy

- The layout itself is verified by this checklist, per merge: every spec in `specs/` has a status; every approved spec has a plan link; every open PR touches its plan's steps or states a gap.
- Tool migrations under this spec (bin/ move-out) follow the pack's brownfield rule: **characterization tests BEFORE the move** — no test, no refactor.
- `memory-lint` gains no new checks from this spec; layout hygiene is review-visible by construction (the files and links are the check). A separate layout lint is a future spec only if a real failure occurs — per the stop-rule on speculative checkers.

## Boundaries

- **Always do:** run the prior-art sweep (own memory → agent-skills pack → web) before writing a spec's design section. Link every artifact both directions.
- **Ask first:** any migration that moves files another page or procedure references (wikilink sweep required); any change to the corpus tier.
- **Never do:** start a build without an approved spec + ended plan; keep accumulables in `scratch/`; sync live copies from anything but `origin/main`.

## Migrations (each its own plan, this spec's first children)

1. **bin/ move-out** — all 13 tools into `bin/` here, characterization tests first; live `/workspace/bin/` becomes deployment.
2. **scratch cleanup** — ~20 non-disposable residents get homes (experiment data → `experiments/`, artwork → `portraits/`, spec-preps → `specs/`, sent-letter drafts → deleted); `stamp-fix.bundle` remains until the upstream PR merges, then deleted.
3. **tasks/ retirement** — two Aug 4 files; archive to cold, delete after verification.

## Open questions

1. **`conversations/` scope** — belongs to the home-remote spec (workslo/home-jr sketch), not this one. Carried there.
2. **`checks/` vs `bin/` consolidation** — both hold tool sources today (PR #56 made checks/memory-lint byte-identical). Consolidation is a future plan; not mandated here.
3. **Repo name for the home-remote** — Shane's call, separate spec.
