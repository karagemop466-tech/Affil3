#!/usr/bin/env node
/**
 * Structural check. Separate from the publication gate so a failure here reads
 * as "the markup is wrong" rather than "the compliance rules are broken".
 *
 *   - balanced tags
 *   - exactly one <h1> per page
 *   - no heading level skips (h2 -> h4)
 *   - exactly one <main> landmark
 *   - every <img> has alt text (there are none, but the rule stays)
 */
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, dirname, relative } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const VOID = new Set(["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"]);

function walk(dir, acc = []) {
  for (const name of readdirSync(dir)) {
    if ([".git", "node_modules", "tools"].includes(name)) continue;
    const full = join(dir, name);
    if (statSync(full).isDirectory()) walk(full, acc);
    else if (full.endsWith(".html")) acc.push(full);
  }
  return acc;
}

const problems = [];
const files = walk(ROOT);

for (const f of files) {
  const page = relative(ROOT, f);
  const html = readFileSync(f, "utf8");
  const stack = [];
  const headings = [];
  let main = 0;

  const re = /<(\/?)([a-zA-Z][a-zA-Z0-9]*)\b([^>]*)>/g;
  let m;
  while ((m = re.exec(html))) {
    const closing = m[1] === "/";
    const tag = m[2].toLowerCase();
    if (tag === "main") main += closing ? 0 : 1;
    if (/^h[1-4]$/.test(tag) && !closing) headings.push(Number(tag[1]));
    if (VOID.has(tag)) continue;
    if (closing) {
      for (let i = stack.length - 1; i >= 0; i--) {
        if (stack[i] === tag) {
          if (i !== stack.length - 1) problems.push(`${page}: </${tag}> while ${stack.slice(i + 1).join(",")} still open`);
          stack.length = i;
          break;
        }
      }
      if (!stack.includes(tag) && stack.length === 0) { /* closed */ }
    } else {
      stack.push(tag);
    }
  }

  const leftover = stack.filter((t) => t !== "html" && t !== "body");
  if (leftover.length) problems.push(`${page}: unclosed tags ${[...new Set(leftover)].join(",")}`);
  if (headings.filter((h) => h === 1).length !== 1) problems.push(`${page}: ${headings.filter((h) => h === 1).length} <h1> elements`);
  let prev = 0;
  for (const h of headings) {
    if (prev && h - prev > 1) { problems.push(`${page}: heading skip h${prev} -> h${h}`); break; }
    prev = h;
  }
  if (main !== 1) problems.push(`${page}: ${main} <main> landmarks`);
  const imgs = [...html.matchAll(/<img\b[^>]*>/g)];
  for (const img of imgs) if (!/alt=/.test(img[0])) problems.push(`${page}: <img> without alt`);
}

console.log(`\nStructure check — ${files.length} pages\n`);
if (!problems.length) {
  console.log("  PASS  tags balanced, one h1, no heading skips, one main\n");
  process.exit(0);
}
for (const p of problems) console.log("  " + p);
console.log(`\n  ${problems.length} problem(s)\n`);
process.exit(1);
