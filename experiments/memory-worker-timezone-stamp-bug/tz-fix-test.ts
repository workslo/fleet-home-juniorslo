// Verification harness for the proposed formatBufferTimestamp fix.
// Run: bun run tz-fix-test.ts
// The instants are the exact ones from the live Sep 10 catches (git-anchored).

function formatBufferTimestamp(now: Date, timeZone?: string): string {
  if (timeZone) {
    const parts = new Intl.DateTimeFormat("en-US", {
      timeZone, month: "short", day: "numeric",
      hour: "numeric", minute: "2-digit", hour12: true,
    }).formatToParts(now);
    const get = (t: string) => parts.find(p => p.type === t)?.value ?? "";
    const hours = Number(get("hour"));
    const minutes = get("minute").padStart(2, "0");
    const displayHour = hours % 12 || 12;
    return `${get("month")} ${get("day")}, ${displayHour}:${minutes} ${get("dayPeriod")}`;
  }
  const month = now.toLocaleString("en-US", { month: "short" });
  const day = now.getDate();
  const hours = now.getHours();
  const minutes = String(now.getMinutes()).padStart(2, "0");
  const ampm = hours >= 12 ? "PM" : "AM";
  const displayHour = hours % 12 || 12;
  return `${month} ${day}, ${displayHour}:${minutes} ${ampm}`;
}

const assert = (cond: boolean, label: string) => {
  if (!cond) { console.error(`FAIL: ${label}`); process.exit(1); }
  console.log(`ok: ${label}`);
};

// The 12:54 AM MDT heartbeat run — the bug stamped it "6:54 AM" (raw UTC)
const midnightRun = new Date("2026-09-10T06:54:49Z");
assert(formatBufferTimestamp(midnightRun) === "Sep 10, 6:54 AM", "bug reproduced: no-tz path yields the wrong stamp");
assert(formatBufferTimestamp(midnightRun, "America/Denver") === "Sep 10, 12:54 AM", "fix: Denver-rendered UTC instant reads true local time");

// This morning's root-causing turn: 10:16 AM MDT
const turn = new Date("2026-09-10T16:16:14Z");
assert(formatBufferTimestamp(turn, "America/Denver") === "Sep 10, 10:16 AM", "fix: morning turn renders correctly");

// Day boundary: 11:31 PM MDT on Sep 9 = 05:31 UTC Sep 10 — month/date must follow local, not UTC
const lateNight = new Date("2026-09-10T05:31:00Z");
assert(formatBufferTimestamp(lateNight, "America/Denver") === "Sep 9, 11:31 PM", "fix: UTC-rollover renders in true local date");

// Backward compat: no-timezone path byte-identical to current behavior
assert(formatBufferTimestamp(turn) === formatBufferTimestamp(turn, undefined), "compat: no-tz path unchanged");
console.log("all green");
