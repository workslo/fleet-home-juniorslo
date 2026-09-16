# bin/ move-out — A1 test inventory reconciliation

One row per tool of the 13. "WS" = workspace-side suite (`/workspace/tests/`), "repo" = suite already in this repo pre-move. Gap flag = no suite anywhere at pin time. Counts are the A2/A3 pin receipts (Sep 15, 2026 — see `pin-receipts.md`).

| # | Tool | Suites at pin time | Runner | Gap | Disposition |
|---|---|---|---|---|---|
| 1 | fleet-inbox-check | WS: `test-fleet-inbox-check.sh` (13, live-API) + `test_fleet_inbox_check_reply_states.py` (11) | sh + py | no | move + port both (`.sh` path adjusted to repo-relative; reply-states ports as-is) |
| 2 | fleet-issue-check | none | — | **GAP** | move + new suite `test-fleet-issue-check.sh` (5) — refusal class |
| 3 | gh | n/a (vendored binary) | n/a | n/a | **D1: excluded** — dependency, not authored tooling |
| 4 | gh-api | WS: `gh-api.test.mjs` (5) | bun | no | move + port → `gh-api.test.mjs` (bun-native name kept — bun requires `.test` in the filename; hyphen-prefix would silently skip) |
| 5 | gh-app-token.mjs | WS: `gh-app-token.test.mjs` (8); repo twin verified | bun | no | verify-only + port → `gh-app-token.test.mjs` (same bun naming rule) |
| 6 | memory-lint | repo canon: 4 suites, run-all green on main (WS copies of 3 are legacy — repo canon is ahead; nothing to port) | py | no | verify-only; home stays `checks/` |
| 7 | now | none | — | **GAP** | move + new suite `test-now.sh` (3) — format pin |
| 8 | research-lint | WS: `test_research_lint.py` (10) | py | no | move + port → `test-research-lint.py` |
| 9 | rm-guard/ | none (repo twin verified) | — | **GAP** | verify-only + new suite `test-rm-guard.sh` (12) — blocklist |
| 10 | send-letter.sh | none (has `--dry-run`) | — | **GAP** | move + new suite `test-send-letter.sh` (21) — dry-run paths only |
| 11 | transcript-diff-prompt.md | n/a (prompt file) | n/a | n/a | **D2: migrate as-is** — no suite (not executable) |
| 12 | transcript-diff.py | none | — | none (by plan) | **D2: migrate as-is, no suite** — retired tooling, eyes-open per plan A3 list; no schedule re-attaches |
| 13 | transcript-gather.py | none (skill twin identical, own domain) | — | **GAP** | move + new suite `test-transcript-gather.py` (5) — arg/output shape, temp WORKSPACE |

Reconciliation: 13 rows for 13 tools. Gap list at pin time — fleet-issue-check, now, rm-guard, send-letter.sh, transcript-gather.py — matches the plan's A3 list exactly. transcript-diff.py carries no suite by explicit plan decision (retired, D2); recorded here so the eyes-open choice is visible, not accidental.

Ported-suite naming follows the repo's existing hyphen convention (`test-<tool>.<ext>`), which is also the run-all.sh discovery shape (B1).
