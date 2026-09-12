# Bug report: memory worker stamps buffer entries in container-local (UTC) time, ignoring workspace timezone

**Discovered:** Sep 8, 2026 (first systematic catch). **Root-caused to source:** Sep 10, ~10:30 AM MDT.
**Live recurrence:** 11+ catch-events, every one git-anchored and re-stamped by hand.

## Symptom

Every entry the memory-consolidation worker files into `memory/buffer.md` and `memory/archive/<date>.md`
carries a timestamp ~6 hours in the future (workspace timezone: `America/Denver`, container clock: UTC).
Example, from a heartbeat that ran at 12:54 AM MDT on Sep 10:

```
- [Sep 10, 6:54 AM] ...   ← raw UTC, read as local; true time was 12:54 AM MDT
```

Downstream, `bin/memory-lint --stamps` (the workspace's own checker) flags these as
`STAMP IN FUTURE`. The workspace has been hand-repairing every instance from git anchors since Sep 8.

## Root cause (source-verified in the deployed image)

`src/plugins/defaults/memory/buffer-format.ts`, `formatBufferTimestamp()` (line ~83):

```ts
const month = now.toLocaleString("en-US", { month: "short" });
const day = now.getDate();
const hours = now.getHours();   // ← container-local = UTC inside the sandbox
```

`getHours()` / `getDate()` / the no-`timeZone` `toLocaleString` all use the **container's** local
timezone. The container runs UTC. The workspace's configured timezone
(`config.json → "timezone": "America/Denver"`) is honored by the **scheduler**
(`src/schedule/plugin-schedule-reconciler.ts:337` — heartbeats fire at correct local times), but the
**memory worker's stamp formatting never reads it**.

Callers:
- `buffer-format.ts:121` — `formatRememberEntry()` (remember()-filed facts)
- `substrate/consolidation-job.ts:398` — consolidation cutoff string

Both shape every buffer/archive entry, so both classes of filing are affected.

## Fix (backward compatible)

Add an optional `timeZone` parameter; when present, derive the parts via `Intl.DateTimeFormat`:

```ts
export function formatBufferTimestamp(now: Date, timeZone?: string): string {
  if (timeZone) {
    const parts = new Intl.DateTimeFormat("en-US", {
      timeZone, month: "short", day: "numeric",
      hour: "numeric", minute: "2-digit", hour12: true,
    }).formatToParts(now);
    const get = (t: string) => parts.find(p => p.type === t)?.value ?? "";
    const hours = Number(get("hour"));
    const displayHour = hours % 12 || 12;
    return `${get("month")} ${get("day")}, ${displayHour}:${get("minute").padStart(2, "0")} ${get("dayPeriod")}`;
  }
  // existing local-time behavior, unchanged
  ...
}
```

Thread `timeZone` through `formatRememberEntry()` and the `consolidation-job.ts` cutoff call site,
passing the workspace timezone from config at both call sites.

## Verification (logic-level, run in the container against the exact instants from the live catches)

```
UTC-instant, no tz (current bug): Sep 10, 6:54 AM    ← reproduces the bug exactly
UTC-instant, Denver (fixed):     Sep 10, 12:54 AM    ← true time of that run
Turn instant, Denver (fixed):    Sep 10, 10:16 AM    ← true time of the root-causing session
Turn instant, no tz (unchanged): Sep 10, 4:16 PM     ← no-timezone path byte-identical (backward compat)
```

**Not verified:** the full wiring inside the platform's own test suite (no test-runner access to the
deployed image's workspace from the agent sandbox; the patch is offered for the platform side to drop
into their checkout and CI).

## Interim mitigation (shipped Sep 10, agent-side)

Agent convention: remember()-filed facts embed the true local time in the fact text (anchored via
`bin/now`), so each filing is self-anchoring even while the worker's stamp is off. This makes the bug
cosmetic but does not fix it — the platform fix above is still the real repair.

## Workaround available at the platform layer

Running the daemon processes with `TZ=America/Denver` in the container environment would also fix
every local-time read platform-wide (one env var, no code change). Trade-off: it changes the meaning
of "local" for all other code in the container, which may or may not be desired — the code fix is the
precise instrument.
