#!/usr/bin/env python3
"""new_guide.py - the publishing workflow for a guide, in one command.

Adds the file AND the calendar row in the same operation, because the two drifting apart is how a
sitemap ends up advertising pages that do not exist (the gate checks this: CHK-12). It then prints
the two things a human still has to do: fill the claims table with real sources, and run the gate.

It cannot write the article. The scaffold's claims table is empty on purpose: an empty table makes
the guide unbuildable rather than publishable, which is the whole difference between a template site
and a publication. See data/sources.json [S16][S27] for why "generate 40 articles" is not a feature.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ROOT / "src" / "content" / "guides"
CALENDAR = ROOT / "data" / "editorial-calendar.json"

TEMPLATE = """---
title: {title}
desc: One sentence: what a reader can decide after reading this, in the time the header promises.
date: {date}
kicker: {kicker}
cluster: {cluster}
author: Counter Tested
status: draft
sources:
---

Write the body here. Rules that keep this publishable, all of them enforced by the gate:

1. No product claim without a source row in `data/sources.json`. If the source does not exist, the
   sentence cannot exist - delete the claim, do not soften it.
2. No price, no star rating, no review quote, no Amazon image. Those are licence-restricted fields
   and the build has no lawful way to obtain them today. [S06] [S07] [S08]
3. No superlatives, no "trending", no "we tested". CHK-03 fails on those strings unless the sentence
   carries a provenance id, and it should stay that way.
4. Say what the reader can check themselves, in the order they can check it. That is the entire
   editorial angle of this site: the questions a listing page can actually answer.
5. End with the state of our evidence. The build appends the standing "what we did not test" block;
   do not duplicate it in prose, and do not contradict it.

## The question, stated plainly

## What to look for, and where

## The trade-off nobody prices in

## What we have not established

:::note
Related: [the shelf](shelf.html) · [how we work](executive-summary.html)
:::

<!-- CLAIMS TABLE - required before this page can be built. One row per factual assertion.
     | Claim (as it will appear) | Value | Source id | Checked |
     | --- | --- | --- | --- |
     | example: the associate sentence is required verbatim | yes | S01 | {date} |
-->
"""


def slugify(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")[:60]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--cluster", default="null")
    ap.add_argument("--kicker", default="Guide")
    ap.add_argument("--slug")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--week", type=int)
    ap.add_argument("--from-query", help="Search Console query this was chosen because of; recorded in the calendar row")
    a = ap.parse_args()

    slug = a.slug or slugify(a.title.split(":")[0])
    path = GUIDES / f"{slug}.md"
    if path.exists():
        raise SystemExit(f"FATAL: {path.relative_to(ROOT)} already exists. Edit it, do not overwrite it.")

    # refuse to create a second guide in the same week-slot without a calendar row (cadence discipline)
    cal = json.loads(CALENDAR.read_text(encoding="utf-8"))
    weeks = {w["week"]: w for w in cal["weeks"]}
    week = a.week or max(weeks) if weeks else 1
    if a.week and a.week not in weeks:
        weeks[a.week] = {"week": a.week, "start": a.date, "planned": []}
        cal["weeks"] = sorted(weeks.values(), key=lambda w: w["week"])
    target_week = weeks[a.week] if a.week in weeks else weeks[week]
    row = {"slug": slug, "title": a.title, "cluster": None if a.cluster == "null" else a.cluster,
           "status": "draft", "note": (f"chosen because of query: {a.from_query}" if a.from_query else "claims table empty until a human fills it")}
    target_week["planned"].append(row)
    CALENDAR.write_text(json.dumps(cal, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    GUIDES.mkdir(parents=True, exist_ok=True)
    path.write_text(TEMPLATE.format(title=a.title, date=a.date, kicker=a.kicker, cluster=a.cluster), encoding="utf-8")

    print(f"created src/content/guides/{slug}.md (status: draft)")
    print(f"calendar row added to week {target_week['week']} as status=draft")
    print("\nBefore this can be published:")
    print(f"  1. fill the CLAIMS TABLE in {slug}.md - one row per factual assertion, each naming a source id")
    print(f"  2. set 'status: published' in the file and in data/editorial-calendar.json for {slug}")
    print("  3. python3 tools/build_site.py && python3 tools/check_site.py")
    print("\nRefusing to do step 1 for you: an auto-filled claims table is the thing this project exists not to be.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
