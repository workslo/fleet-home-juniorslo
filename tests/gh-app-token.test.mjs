/**
 * Tests for bin/gh-app-token.mjs
 *
 * Covers: base64url encoding, JWT payload fields, RSA signing with a
 * real generated key, clock-skew tolerance, pem_b64 decoding (valid +
 * malformed), and JWT verifiability against the public key.
 *
 * The live token exchange (GitHub API) is NOT tested here — it is gated
 * on the App's private key existing in the vault.
 *
 * Run: bun test tests/gh-app-token.test.mjs
 */

import { describe, test, expect } from "bun:test";
import { generateKeyPairSync, createVerify } from "node:crypto";
import { createJWT, decodePem } from "../bin/gh-app-token.mjs";

const { privateKey, publicKey } = generateKeyPairSync("rsa", {
  modulusLength: 2048,
});
const pem = privateKey.export({ type: "pkcs1", format: "pem" });
const pubPem = publicKey.export({ type: "pkcs1", format: "pem" });

function decodeSegment(seg) {
  const b64 = seg.replace(/-/g, "+").replace(/_/g, "/");
  return JSON.parse(Buffer.from(b64, "base64").toString("utf8"));
}

describe("createJWT", () => {
  const jwt = createJWT("4591122", pem);
  const [h, p, s] = jwt.split(".");

  test("has three base64url segments", () => {
    expect(jwt.split(".")).toHaveLength(3);
    for (const seg of [h, p, s]) {
      expect(seg).toMatch(/^[A-Za-z0-9_-]+$/); // no +, /, or = padding
    }
  });

  test("header is RS256 JWT", () => {
    expect(decodeSegment(h)).toEqual({ alg: "RS256", typ: "JWT" });
  });

  test("payload carries iss and skew-tolerant iat/exp", () => {
    const payload = decodeSegment(p);
    const now = Math.floor(Date.now() / 1000);
    expect(payload.iss).toBe("4591122");
    expect(payload.iat).toBeLessThanOrEqual(now - 55); // ~60s skew
    expect(payload.iat).toBeGreaterThan(now - 120);
    expect(payload.exp).toBeGreaterThan(now + 500); // ~10 min lifetime
    expect(payload.exp).toBeLessThanOrEqual(now + 600);
  });

  test("signature verifies against the public key", () => {
    const verify = createVerify("RSA-SHA256");
    verify.update(`${h}.${p}`);
    verify.end();
    const sig = Buffer.from(
      s.replace(/-/g, "+").replace(/_/g, "/"),
      "base64"
    );
    expect(verify.verify(pubPem, sig)).toBe(true);
  });
});

describe("decodePem", () => {
  test("round-trips a base64-encoded PEM", () => {
    const b64 = Buffer.from(pem, "utf8").toString("base64");
    expect(decodePem(b64)).toBe(pem);
  });

  test("tolerates surrounding whitespace", () => {
    const b64 = "  " + Buffer.from(pem, "utf8").toString("base64") + "\n";
    expect(decodePem(b64)).toBe(pem);
  });

  test("rejects malformed input", () => {
    const b64 = Buffer.from("definitely not a key", "utf8").toString("base64");
    expect(() => decodePem(b64)).toThrow(/private key/i);
  });

  test("decoded key signs a verifiable JWT (end-to-end vault path)", () => {
    const b64 = Buffer.from(pem, "utf8").toString("base64");
    const jwt = createJWT("4591122", decodePem(b64));
    const [h, p, s] = jwt.split(".");
    const verify = createVerify("RSA-SHA256");
    verify.update(`${h}.${p}`);
    verify.end();
    expect(
      verify.verify(pubPem, Buffer.from(s.replace(/-/g, "+").replace(/_/g, "/"), "base64"))
    ).toBe(true);
  });
});
