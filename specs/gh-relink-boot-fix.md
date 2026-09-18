# Spec: gh re-link boot fix

**Status:** draft — awaiting Shane review (spec-first)
**Author:** JuniorSLO, Sep 18 heartbeat
**Evidence:** real caught failure ×2 (both Sep 16; gotchas.md line 62). The symlink
`/usr/local/bin/gh → /workspace/bin/gh` is wiped by every container rebuild because
`/usr/local/bin` lives outside the persistent volume. The 42MB real binary at
`/workspace/bin/gh` survives every rebuild. Currently WORKING (link re-created
Sep 17 03:25 by the last repair) — this spec makes the repair unnecessary.

## Constraints found (live checks, Sep 18)

- `/workspace/bin/gh` — persistent, executable, works (`gh --version` → 2.100.0).
- `/usr/local/bin` is on the default PATH for non-interactive processes; that's
  why the symlink approach was chosen. `.bashrc` PATH edits don't reach
  non-interactive heartbeat scripts (bashrc is interactive-only, verified).
- `~/.profile` same limit; PATH is set by the platform environment.
- `/data/system/bin` IS writable and IS on PATH — but it's host-provided system
  space (bind-mounted, contains host binaries). **Rejected: do not write into
  host system space for a container-convenience link.**
- No boot hook mechanism found under my control (`hooks/` holds only
  reference-transaction; no crontab; nothing runs at container start that I own).

## Options

**A. Self-healing wrapper (RECOMMENDED).** The `gh` call sites that matter all
already run through `bin/gh-app-token.mjs` (the Sep 17 wrapper conversion made
this the canonical path — zero stale-capture callers remain). Add a cheap
self-heal to the wrapper's startup: if `! command -v gh` (or
`[ ! -e /usr/local/bin/gh ]`), attempt `ln -sf /workspace/bin/gh
/usr/local/bin/gh`, and if that link attempt fails (read-only), fall through to
exporting a PATH-prepend of `/workspace/bin` for the child process. Either way
the wrapped `gh` call succeeds. Cost: ~6 lines in one file. Coverage: every
script that goes through the wrapper (which is all of them, post-conversion).
Ad-hoc interactive `gh` calls from a fresh shell after a rebuild still hit the
gap — acceptable, since interactive shells can also run the one-line relink, and
the wrapper heals it on first use anyway.

**B. Boot-time fixup.** Requires a mechanism that runs at container start. None
found in my control. Would need platform-level support (a boot hook or the
schedule worker firing on start) — building on machinery that may itself change
under v2. Rejected for now; revisit if the platform adds boot hooks.

**C. Add `/workspace/bin` to PATH platform-wide.** The env comes from the
platform, not from anything I can set for non-interactive child processes.
Rejected as not in my control.

## Proposed change (Option A)

In `bin/gh-app-token.mjs`, before minting/using the token:

```js
import { existsSync, symlinkSync } from "node:fs";
if (!existsSync("/usr/local/bin/gh")) {
  try { symlinkSync("/workspace/bin/gh", "/usr/local/bin/gh"); }
  catch { /* read-only fs: child PATH prepend below covers us */ }
}
const childEnv = existsSync("/usr/local/bin/gh") ? process.env
  : { ...process.env, PATH: `/workspace/bin:${process.env.PATH}` };
```

…passing `childEnv` to the existing child spawn. Same pattern, no behavior
change when the link is healthy.

## Acceptance

1. `rm /usr/local/bin/gh && node bin/gh-app-token.mjs -- gh api /rate_limit`
   (or equivalent live call) succeeds and the link exists afterward.
2. Normal path unchanged when link present (no double-link attempts in logs).
3. `bin/gh-app-token.mjs` still passes the existing smoke tests
   (`node bin/gh-app-token.mjs -- python3 bin/fleet-issue-check`).

## Out of scope

- The interactive-shell first-use gap (heals via wrapper on first fleet call).
- Any v2-identity overlap: per-agent GitHub identities may replace token minting
  entirely — this fix is deliberately small and disposable if v2 lands first.
