#!/usr/bin/env bun
/**
 * gh-app-token.mjs — GitHub App installation token helper (JuniorSLO seat)
 *
 * Reads app_id, installation_id, and pem_b64 (base64-encoded private key)
 * from the assistant credential vault, decodes the key, signs a JWT,
 * exchanges it for a 1-hour installation token, and runs <command> with that
 * token in its environment.
 *
 * The vault holds the key base64-encoded (field `pem_b64`) because the
 * single-line form survives secure-prompt entry and shell handling without
 * ever printing the raw PEM. This script is the sole decode site.
 *
 * Based on the fleet-github-bot-setup-guide (PR #23, merged Aug 14 2026).
 * Adapted from AgentSlo's helper for JuniorSLO's seat.
 *
 * Usage:
 *   bun /workspace/bin/gh-app-token.mjs -- gh api /installation/repositories
 *   bun /workspace/bin/gh-app-token.mjs -- sh -c 'curl -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/installation/repositories'
 *   bun /workspace/bin/gh-app-token.mjs -- git push   # works once `gh auth setup-git` has been run: gh's
 *                                                     # credential helper returns x-access-token + GH_TOKEN
 *
 * The token is placed in GH_TOKEN / GITHUB_TOKEN for <command> only. It is
 * never written to this script's stdout, and the child's output is scrubbed
 * for it. There is no --print mode on purpose: inside an agent's tool call
 * stdout is a pipe either way, so the script cannot tell `$(...)` from a bare
 * run that lands the token in the transcript.
 *
 * Tokens are 1-hour installation tokens — regenerate per session, never store.
 */

import { createSign } from "node:crypto";
import { writeSync } from "node:fs";

const NEVER_EXEC = new Set(["env", "printenv"]); // the two commonest "let me just look" leaks

// --- argv: the command to run with the token. Checked before touching the vault. ---
function parseArgs() {
  const argv = process.argv.slice(2);
  if (argv[0] === "--") argv.shift();
  if (argv.length === 0) {
    process.stderr.write(
      "usage: gh-app-token.mjs -- <command> [args...]\n" +
      "The token is placed in GH_TOKEN / GITHUB_TOKEN for <command> and is never printed.\n"
    );
    // A stale `TOKEN=$(...)` caller gets a broken token, not an empty one —
    // gh treats an empty GH_TOKEN as unset and would fall back to whatever
    // auth the sandbox has.
    writeSync(1, "gh-app-token-refused-see-stderr");
    process.exit(2);
  }
  if (NEVER_EXEC.has(argv[0].split("/").pop())) {
    throw new Error(`refusing to run ${argv[0]}: it would print the token`);
  }
  return argv;
}

// --- credential vault read ---
function readCredential(service, field) {
  const proc = Bun.spawnSync([
    "assistant", "credentials", "reveal",
    "--service", service,
    "--field", field,
  ], { stdout: "pipe", stderr: "pipe" });
  if (proc.exitCode !== 0) {
    const err = new TextDecoder().decode(proc.stderr);
    throw new Error(`Failed to read credential ${service}/${field}: ${err.trim()}`);
  }
  const val = new TextDecoder().decode(proc.stdout).trim();
  if (!val) {
    throw new Error(`Credential ${service}/${field} is empty`);
  }
  return val;
}

// --- JWT creation ---
function createJWT(appId, pemKey) {
  const now = Math.floor(Date.now() / 1000);
  const payload = {
    iat: now - 60,          // 60s clock skew tolerance
    exp: now + 600,         // 10 min max lifetime for app JWT
    iss: String(appId),     // GitHub App ID
  };

  // Minimal JWT: base64url(header).base64url(payload).signature
  const header = { alg: "RS256", typ: "JWT" };

  const b64url = (obj) =>
    Buffer.from(JSON.stringify(obj))
      .toString("base64")
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");

  const signingInput = `${b64url(header)}.${b64url(payload)}`;

  const sign = createSign("RSA-SHA256");
  sign.update(signingInput);
  sign.end();

  const signature = sign.sign(pemKey);
  const sigB64url = signature
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");

  return `${signingInput}.${sigB64url}`;
}

// --- installation token exchange ---
async function getInstallationToken(jwt, installationId) {
  const resp = await fetch(
    `https://api.github.com/app/installations/${installationId}/access_tokens`,
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${jwt}`,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
      },
    }
  );

  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`Token exchange failed (${resp.status}): ${body}`);
  }

  const data = await resp.json();
  return data.token;
}

// --- key decode (sole decode site) ---
function decodePem(pemB64) {
  const pem = Buffer.from(pemB64.trim(), "base64").toString("utf8");
  if (!pem.includes("BEGIN") || !pem.includes("PRIVATE KEY")) {
    throw new Error("Decoded pem_b64 does not look like a private key");
  }
  return pem;
}

// --- run the command with the token in its environment (never on stdout) ---

// Replace the token wherever it appears in the child's output. Holds back the
// last token.length-1 chars of each chunk so a token split across two chunks
// is still caught.
async function scrub(source, sink, token) {
  const decoder = new TextDecoder();
  const keep = token.length - 1;
  let carry = "";
  for await (const chunk of source) {
    const text = (carry + decoder.decode(chunk, { stream: true })).replaceAll(token, "***REDACTED***");
    carry = text.slice(-keep);
    sink.write(text.slice(0, -keep));
  }
  sink.write((carry + decoder.decode()).replaceAll(token, "***REDACTED***"));
}

async function runWithToken(token, argv) {
  const proc = Bun.spawn(argv, {
    env: { ...process.env, GH_TOKEN: token, GITHUB_TOKEN: token },
    stdin: "inherit",
    stdout: "pipe",
    stderr: "pipe",
  });
  await Promise.all([
    scrub(proc.stdout, process.stdout, token),
    scrub(proc.stderr, process.stderr, token),
  ]);
  // exitCode, not exit(): a piped stdout can be async and exit() would truncate it.
  process.exitCode = await proc.exited;
}

// --- main ---
async function main() {
  const argv = parseArgs();

  const appId = readCredential("github-app", "app_id");
  const installationId = readCredential("github-app", "installation_id");
  const pem = decodePem(readCredential("github-app", "pem_b64"));

  const jwt = createJWT(appId, pem);
  const token = await getInstallationToken(jwt, installationId);

  await runWithToken(token, argv);
}

export { createJWT, decodePem };

if (import.meta.main) {
  main().catch((err) => {
    process.stderr.write(`Error: ${err.message}\n`);
    process.exit(1);
  });
}
