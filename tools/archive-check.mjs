#!/usr/bin/env node
/**
 * Archive check.
 *
 * The legacy/ folder holds several frozen editions of this project. They are not
 * part of the current build and are not held to its design rules, but they are
 * published, so their internal links must still resolve. An archive full of dead
 * links is not a record of anything.
 *
 * Checks every internal href/src inside legacy/ resolves to a file that exists.
 * External links are skipped: checking those needs the network, and a dead
 * outbound link in a frozen 2026 archive is not a build failure.
 */
import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, dirname, relative, normalize } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const ARCHIVE = join(ROOT, "legacy");

if (!existsSync(ARCHIVE)) {
  console.log("\nArchive check — no legacy/ folder, nothing to verify\n");
  process.exit(0);
}

function walk(dir, acc = []) {
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) walk(full, acc);
    else if (full.endsWith(".html")) acc.push(full);
  }
  return acc;
}

const pages = walk(ARCHIVE);
const broken = [];
let checked = 0;

for (const f of pages) {
  const html = readFileSync(f, "utf8");
  const from = dirname(f);
  const refs = [...html.matchAll(/(?:href|src)="([^"]+)"/g)].map((m) => m[1]);

  for (const ref of refs) {
    if (/^(?:https?:)?\/\//.test(ref) || ref.startsWith("#") || /^(?:mailto|data|tel|javascript):/.test(ref)) continue;
    const clean = ref.split("#")[0].split("?")[0];
    if (!clean) continue;
    checked++;

    let target = normalize(join(from, clean));
    if (clean.endsWith("/") || existsSync(target) && statSync(target).isDirectory()) {
      target = join(target, "index.html");
    }
    if (!existsSync(target)) {
      broken.push(`${relative(ROOT, f)} -> ${ref}`);
    }
  }
}

console.log(`\nArchive check — ${pages.length} archived pages, ${checked} internal refs\n`);

if (broken.length) {
  for (const b of broken.slice(0, 30)) console.log(`  FAIL  ${b}`);
  if (broken.length > 30) console.log(`  ...and ${broken.length - 30} more`);
  console.log(`\n  ${broken.length} broken archive link(s).\n`);
  process.exit(1);
}

console.log("  PASS  every internal link in the archive resolves\n");
