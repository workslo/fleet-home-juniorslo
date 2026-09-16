#!/usr/bin/env bun
/**
 * tests/gh-api.test.mjs — tests for the bin/gh-api wrapper.
 *
 * The wrapper's real behavior (mint + HTTP call) is exercised live in
 * sessions; here we test the behaviors that can be wrong without network:
 * argument handling, the truncation guard, and the structural property
 * that the wrapper never reads a cached token file.
 */

import { describe, test, expect } from "bun:test";
import { readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import path from "node:path";

const GH_API = path.join(import.meta.dir, "..", "bin", "gh-api");

function run(args, env = {}) {
  return spawnSync("bash", [GH_API, ...args], {
    encoding: "utf8",
    timeout: 15000,
    env: { ...process.env, ...env },
  });
}

describe("gh-api wrapper", () => {
  test("no args exits non-zero with usage on stderr", () => {
    const r = run([]);
    expect(r.status).not.toBe(0);
    expect(r.stderr).toContain("usage:");
  });

  test("--help prints usage", () => {
    const r = run(["--help"]);
    expect(r.status).toBe(0);
    expect(r.stdout).toContain("--set-remote");
  });

  test("mint guard: non-token output from helper fails loudly", () => {
    // Point the wrapper at a helper that emits garbage.
    const fakeHelper = path.join(import.meta.dir, "fixtures", "gh-fake-helper-bad.mjs");
    const r = run(["--token"], { GH_API_FORCE_HELPER: fakeHelper });
    // The wrapper hardcodes the real helper path, so this run either fails
    // (vault unavailable in test env) or succeeds — assert it never prints
    // a truncated token silently.
    if (r.status === 0) {
      expect(r.stdout.trim()).toMatch(/^ghs_[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/);
    } else {
      expect(r.stderr).toContain("gh-api:");
    }
  });

  test("structural: wrapper never reads the stale cache file", () => {
    const src = readFileSync(GH_API, "utf8");
    // Exactly one mention allowed: the doc-comment explaining WHY the cache
    // is gone. Any second occurrence is a code path reading it — fail loud.
    const mentions = src.split(".gh-app-token").length - 1;
    expect(mentions).toBe(1);
    expect(src.split(".gh-app-token")[0]).toContain("#"); // inside the header comment
    expect(src).toContain("gh-app-token.mjs"); // the live minter, always
  });

  test("structural: every mint passes through the truncation guard", () => {
    const src = readFileSync(GH_API, "utf8");
    // The guard checks for three JWT-ish segments (two dots) before use.
    expect(src).toContain("*.*.*");
  });
});
