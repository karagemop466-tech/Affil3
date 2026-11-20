#!/usr/bin/env node
/*
 * Guide scaffold for the publishing cadence (SG-08).
 *
 * The cadence claim is only real if adding a guide is one command and one commit, and if the new
 * page cannot skip the parts that make the rest of the site defensible. So the template arrives
 * pre-filled with the byline, the no-testing note, and a sources section that says "no external
 * source was required" rather than leaving it blank - a blank is what gets skipped under deadline.
 *
 *   node scripts/new-guide.mjs "Question-shaped title here" --cluster air-fryers --days 2
 */
import fs from "node:fs";
import path from "node:path";
import url from "node:url";

const ROOT = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2).filter(Boolean);
const title = args.find((a) => !a.startsWith("--"));
const opt = (k, d) => { const i = args.indexOf("--" + k); return i === -1 ? d : args[i + 1]; };
if (!title) {
  console.error('usage: node scripts/new-guide.mjs "A question a buyer actually asks" --cluster air-fryers --days 2');
  process.exit(1);
}
const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 60);
const cluster = opt("cluster", "air-fryers");
const days = Number(opt("days", 0));
const d = new Date(Date.now() + days * 86400000).toISOString().slice(0, 10);
const dest = path.join(ROOT, "content/guides", slug + ".md");
if (fs.existsSync(dest)) { console.error(`exists: ${path.relative(ROOT, dest)}`); process.exit(1); }

const body = `---
title: "${title.replace(/"/g, "'")}"
slug: ${slug}
date: ${d}
cluster: ${cluster}
description: One sentence a search result would be proud of: the question this answers and who it is for. Under 155 characters.
reading_time: 5
tags: [${cluster.replace(/-/g, " ")}, buying guide]
---

## The question worth answering

Open with the decision the reader is actually stuck on, in their words. Then answer it with things
they can check for themselves - a measurement, a physical constraint, a line of the listing.

## What to look for

1. **The concrete check.** Name the thing, and where on the page or in the manual it lives.
2. **The trade-off it reveals.** What choosing this way costs, stated as a cost, not as a flaw.
3. **The one number that matters.** If we cannot verify the number ourselves, say what to read.

## What this does not tell you

No product linked from this site has been tested by us, and nothing here is a ranking. Prices,
ratings and availability are not published because they cannot be refreshed from an authorised
source - see /methodology/. Edit this section into a sentence that fits the piece; do not delete it.

## Sources

- No external source was required for the guidance above, which is general how-to-judge-it advice.
- If you add a figure, a standard, or a claim, it needs a row in register/sources.json with the
  official URL and an access date, or the build will not be able to say where it came from.
`;

fs.writeFileSync(dest, body);
console.log(`created ${path.relative(ROOT, dest)}`);
console.log(`next: fill it in, then 'node scripts/build.mjs' - the sitemap, the feed, the guides index,`);
console.log(`      the home-page rack and the search index all pick it up automatically, and`);
console.log(`      'node scripts/checks.mjs' will refuse the build if the disclosure or the wording fails.`);
