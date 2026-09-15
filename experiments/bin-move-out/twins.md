# bin/ move-out — A0 twin verification receipts

The three already-repo-side tools, `cmp`-verified byte-identical against the live `/workspace/bin/` copies at move time (Sep 15, 2026, ~2:15 PM MDT). Pre-verified Sep 14 (plan inventory); re-verified per the plan's A0 rule — any drift would have been a STOP with both bytes preserved. No drift found.

| Tool | Repo home | Live copy | cmp result |
|---|---|---|---|
| gh-app-token.mjs | `bin/gh-app-token.mjs` | `/workspace/bin/gh-app-token.mjs` (6,716 B) | **identical** |
| rm-guard | `bin/rm-guard/rm` (830 B) | `/workspace/bin/rm-guard/rm` (830 B) | **identical** |
| memory-lint | `checks/memory-lint` | `/workspace/bin/memory-lint` (30,023 B) | **identical** |

Per the stated constraint (parent spec Open Q2, not mandated): memory-lint's repo home stays `checks/` — no consolidation rides along with this move.

Their bytes never leave the repo; these receipts are the verify-only disposition for tools #5, #6, #9 of the 13.
