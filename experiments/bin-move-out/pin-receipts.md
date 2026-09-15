# bin/ move-out — pin receipts (A2 existing suites + A3 gap suites)

All runs against the LIVE `/workspace/bin/` copies, Sep 15, 2026 (~2:05–2:20 PM MDT), before any tool moved (brownfield rule: pin before move). These receipts carry the coverage: any post-move count that differs from these is a regression, not a test flake.

## A2 — existing suites, live copies

| Suite | Runner | Pin result |
|---|---|---|
| `gh-app-token.test.mjs` | bun 3.11 | **8 pass / 0 fail** (15 expect calls) — matches plan expectation 8/8 |
| `gh-api.test.mjs` | bun 3.11 | **5 pass / 0 fail** (9 expect calls) |
| `test_fleet_inbox_check_reply_states.py` | python3 | **11 tests OK** (pure-function, no network) |
| `test_research_lint.py` | python3 | **10 passed / 0 failed** |
| `test-fleet-inbox-check.sh` | bash | **13 passed / 0 failed** — live AgentMail API (network + vault credential required at run time) |
| memory-lint canon | `bash tests/run-all.sh` on main `e39d3dc9` | **all green** (4 suites) — repo-side already; this run is the standing-green receipt |

Notes pinned as-is:
- `test-fleet-inbox-check.sh` Test 9 (`reply_state` asserts) is **unreachable code** — it sits after `exit $FAIL` and never executes. Documented, not fixed (characterization pins what IS; no fix rides along). The reply-state behavior itself IS covered — by the reply-states pure-function suite (11 tests).
- The `.sh` inbox suite is the one ported suite with a live-API dependency; its pin receipt above carries that coverage for environments without network (same pattern as bun-absent `.mjs` skips in run-all.sh).

## A3 — gap suites (new this run), live copies

| Suite | Pins | Pin result |
|---|---|---|
| `test-fleet-issue-check.sh` | bare-run refusal class: no-token gate fires before any network, exit 1 + wrapper instruction on stderr; flags don't bypass; empty-string token = absent | **5 passed / 0 failed** |
| `test-now.sh` | dual-zone one-line format; exit 0; Denver/UTC offset consistent with zone label (6 h MDT / 7 h MST) | **3 passed / 0 failed** |
| `test-rm-guard.sh` | blocklist: `-rf`, `-r -f`, `-fr`, `-R -f` all refused (exit 1, "rm-guard: refused", target survives); `-r`/`-f`/plain pass through and really delete temp fixtures | **12 passed / 0 failed** |
| `test-send-letter.sh` | dry-run paths ONLY: usage/missing-file/empty-body gates (exit 1); SEND + REPLY dry-run previews (exit 0, "DRY RUN — not sending."); frontmatter thread detection; `--thread` override; archived-letter body extraction | **21 passed / 0 failed** |
| `test-transcript-gather.py` | arg/output shape against a TEMP WORKSPACE (env override): text + JSON summaries, 0-conversation date, output file lands in temp, `--interactive-only` accepted, default-date shape | **5 tests OK** |

No red results anywhere; no known-failure receipts needed (no real bugs surfaced during pinning).

## Build-time finding (B1/B2, receipted)

bun refuses to run test files whose filename lacks `.test`/`_test_`/`.spec` — a hyphen-prefix rename (`test-gh-api.mjs`) made `bun test` skip the suite with only a note, which fail'd run-all.sh without a single red assert. The port therefore keeps the bun-native `.test.mjs` names for both `.mjs` suites, and run-all.sh's `.mjs` glob is `tests/*.test.mjs` (documented in the runner's header). Naming conventions are runner contracts: the discovery glob and the runner's filename requirements have to agree, or suites vanish silently.
