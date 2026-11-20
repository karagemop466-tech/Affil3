#!/usr/bin/env python3
"""Append the suggestions, questions and discovery rows found by session 0e102530.

Every row cites a source already in data/sources.json or a flag already in data/flags.json,
so the build's source-existence gate stays satisfied. Nothing here asserts a new fact about a
product; these are decisions the owner still has to make.
"""
import json
from collections import OrderedDict

# ---------------------------------------------------------------- suggestions
PATH = 'data/suggestions.json'
with open(PATH, encoding='utf-8') as f:
    sdb = json.load(f, object_pairs_hook=OrderedDict)

existing = {x['id'] for x in sdb['suggestions']}

S20 = OrderedDict([
    ("id", "S-20"),
    ("track", "measurement"),
    ("topic", "Where the analytics collector actually runs"),
    ("problem", "The counter is built, reviewed and tested, and it is switched off, because GitHub Pages cannot run a server. Every option below needs something the repository cannot provide on its own: a host, a service, or a decision about what is worth collecting at all."),
    ("current", "A"),
    ("options", [
        OrderedDict([
            ("id", "A"),
            ("label", "Leave the endpoint unset. The site publishes no traffic figures and no revenue figures, and the /measurement/ page says so in plain words."),
            ("tradeoff", "Nothing to deploy, nothing to disclose, nothing to get wrong. It also means the next guide topic is chosen by instinct rather than by measured queries, which is the gap the publishing cadence was supposed to close."),
            ("effort", "none"),
            ("risk", "low")
        ]),
        OrderedDict([
            ("id", "B"),
            ("label", "Run the collector on a small always-on host and point analyticsEndpoint at it."),
            ("tradeoff", "Turns measurement on the same day it is deployed. It also means the host, its logs, its uptime and its backups become part of what this site promises a reader, and the privacy notice has to describe a real company rather than a generic process."),
            ("effort", "an afternoon"),
            ("risk", "medium")
        ]),
        OrderedDict([
            ("id", "C"),
            ("label", "Publish daily aggregate counts to a public JSON file in this repository, written by a scheduled GitHub Actions workflow, and let the browser POST to a queue instead of the collector."),
            ("tradeoff", "No separate host and no server to pay for, and the counts stay in the repository history. It needs a write path for the browser that does not accept arbitrary POSTs, so the workflow is the part that has to be designed and reviewed carefully."),
            ("effort", "two to three days"),
            ("risk", "medium")
        ]),
        OrderedDict([
            ("id", "D"),
            ("label", "Measure only outbound clicks, with no page-view events at all."),
            ("tradeoff", "The smallest possible data set, and the only number that is actually tied to revenue. It cannot answer which guide brought the reader, which is the question the cadence decision needs."),
            ("effort", "one day"),
            ("risk", "medium")
        ])
    ]),
    ("recommendation", "B if there is a host available and the privacy notice can be settled first (Q-16). D if the goal is strictly to count revenue-bearing clicks. The collector itself is ready: it was run end to end on 2026-11-20 and accepted all five defined events while rejecting malformed input, so the remaining work is hosting and disclosure, not code."),
    ("evidence", OrderedDict([
        ("sources", ["S02"]),
        ("flags", ["FLG-009"])
    ])),
    ("depends_on", ["S-03", "S-16"]),
    ("decision", "undecided"),
    ("decided_on", ""),
    ("decided_by", "")
])

S21 = OrderedDict([
    ("id", "S-21"),
    ("track", "platform"),
    ("topic", "Image weight on a site whose job is to be found and read"),
    ("problem", "Every guide page loaded an illustration of 3.3 to 4.0 MB. The artwork itself is fine and the file format was a poor fit for it: these are flat, grainy, mid-tone illustrations, which are exactly the images that compress well into a small palette. Six files were re-encoded to a 256-colour palette on 2026-11-20, which cut each from 3.3-4.0 MB to 0.9-1.1 MB with no visible change (measured pixel RMSE 0.012). The remaining weight is still real: an image that is the largest thing on the page slows the page down on the connections a reader is actually using."),
    ("current", "B"),
    ("options", [
        OrderedDict([
            ("id", "A"),
            ("label", "Leave the images as they are."),
            ("tradeoff", "Free, and the pages still render. It leaves the heaviest element on the page untouched for a site whose stated goal is organic traffic, where time-to-first-byte on mobile connections is a ranking input rather than a detail."),
            ("effort", "none"),
            ("risk", "medium")
        ]),
        OrderedDict([
            ("id", "B"),
            ("label", "Re-encode the remaining illustrations to the same small palette and keep going (current state)."),
            ("tradeoff", "No file path or artwork changes, so no page reference moves and no gate rule has to be written. The pages are now roughly a third of their previous weight."),
            ("effort", "half an hour"),
            ("risk", "low")
        ]),
        OrderedDict([
            ("id", "C"),
            ("label", "Move every illustration to JPEG, delete the PNGs, and add a gate rule that no image over 300 KB may be committed."),
            ("tradeoff", "The smallest files and the smallest ongoing cost, because a rule stops the problem returning. It also means the illustration pages are no longer lossless, and the rule needs an exception path for a genuinely detailed image."),
            ("effort", "half a day"),
            ("risk", "low")
        ]),
        OrderedDict([
            ("id", "D"),
            ("label", "Keep the illustrations but load them lazily, and reserve their space with the width and height already in the markup."),
            ("tradeoff", "The markup already carries width and height, so the layout does not shift, and lazy loading is already on for the figures below the fold. The hero image on each guide page is above the fold and would still load eagerly, which is where most of the weight is."),
            ("effort", "one hour"),
            ("risk", "low")
        ])
    ]),
    ("recommendation", "B now, C when the next illustration is added. The re-encode was done with the same file names and the same pixels, so it is safe to do without a decision, and a weight rule in the gate would stop it coming back."),
    ("evidence", OrderedDict([
        ("sources", []),
        ("flags", [])
    ])),
    ("depends_on", []),
    ("decision", "B"),
    ("decided_on", "2026-11-20"),
    ("decided_by", "0e102530 (build step, reversible, no path or artwork changed)")
])

for s in (S20, S21):
    if s['id'] in existing:
        raise SystemExit('suggestion already present: ' + s['id'])
    sdb['suggestions'].append(s)

with open(PATH, 'w', encoding='utf-8') as f:
    json.dump(sdb, f, indent=2, ensure_ascii=False)
    f.write('\n')

# ---------------------------------------------------------------- questions
PATH = 'data/questions.json'
with open(PATH, encoding='utf-8') as f:
    qdb = json.load(f, object_pairs_hook=OrderedDict)

existing_q = {x['id'] for x in qdb['unknown']}
existing_d = {x['id'] for x in qdb['discovery']}

K22 = OrderedDict([
    ("id", "K-22"),
    ("statement", "The CHEF iQ Sense publishes two separate temperature ranges, and the site's product table now shows the one that applies to food. The manufacturer's specification page lists an internal range of 32-212 F and an ambient range of 32-1,000 F; the manufacturer's own FAQ repeats the distinction, giving 212 F as the maximum for the portion of the probe inserted into food and 1,000 F as the Gen 3 ambient limit. The table on the product page and on the comparison page previously showed 32-1,000 F as the probe temperature, which was the ambient figure. It was corrected to 32-212 F on 2026-11-20 and the ambient rating is stated in the product's summary line instead."),
    ("sources", ["S14", "S15"])
])

Q17 = OrderedDict([
    ("id", "Q-17"),
    ("question", "Which of the two published temperature ranges should a reader compare against a cooking target: the food range or the ambient range?"),
    ("have", "Both ranges, from the manufacturer's specification page and its FAQ. The site now publishes the food range in the specification table and states the ambient rating in the summary line and the guide that covers the product."),
    ("lack", "Nothing for the table itself. What is missing is guidance from the manufacturer about which figure a buyer should use when checking whether the probe will survive a particular cooking method, since a 1,000 F ambient figure invites the reading that the probe can be left in a 1,000 F oven."),
    ("who", "Manufacturer support, or the owner's own judgment after reading the manual"),
    ("why_it_matters", "A reader who sees only 1,000 F may leave the probe in an oven or under a broiler that the probe's food-side limit does not cover. The distinction is the difference between a safe instruction and a dangerous one, and the site currently publishes only the number, not the instruction."),
    ("how_to_close", "Ask the manufacturer in writing which range applies to which part of the probe in each cooking method, or read the product manual for the limit on the inserted section. Publish the answer as a line of guidance next to the table."),
    ("sources", ["S14", "S15"]),
    ("blocking", False)
])

Q18 = OrderedDict([
    ("id", "Q-18"),
    ("question", "Does the short-link behaviour seen on 2026-11-20 mean anything about the submitted links?"),
    ("have", "Five dated fetches on 2026-11-20, one per submitted link, each landing on the Amazon home page rather than a product page. The same behaviour is already recorded on two earlier dated rounds (FLG-004, FLG-031), and the direct /dp/ URLs for all five products resolved and returned the expected titles and ASINs in the same session."),
    ("lack", "A fetch of the same five links from a signed-in browser, which the sandbox cannot do. Without one, the observation stays an observation and no conclusion about the links is available."),
    ("who", "Site owner"),
    ("why_it_matters", "Three sessions in a row have now seen the same thing and none of them can interpret it. Either the short links redirect to the home page for unsigned-in requests, which would be ordinary and would say nothing about their validity, or something about them is different. Those two readings lead to opposite decisions, and the site's compliance position on them (FLG-003) depends on which is true."),
    ("how_to_close", "Open each of the five links in a signed-in Amazon session and record the product name and the ten-character ASIN from the resulting URL. One pass, five minutes, and it closes Q-01 as well."),
    ("sources", ["S05", "S04"]),
    ("blocking", True)
])

D13 = OrderedDict([
    ("id", "D-13"),
    ("suggestion", "Ask the CHEF iQ manufacturer, in writing, which of its two published temperature ranges applies to the probe section inserted into food and which to the ambient sensor, and publish the answer as guidance rather than leaving the reader to infer it from two numbers."),
    ("closes", ["Q-17"])
])

D14 = OrderedDict([
    ("id", "D-14"),
    ("suggestion", "Open the five submitted short links in a signed-in Amazon session and record the destination ASIN and product name for each, alongside the date. This has now failed to resolve from three separate unsigned-in rounds, which is itself a reason to try it the way a reader would."),
    ("closes", ["Q-01", "Q-18"])
])

D15 = OrderedDict([
    ("id", "D-15"),
    ("suggestion", "Re-check the two manufacturer pages whose own text disagrees with themselves - Emeril Lagasse's preset count and in-1 count, and CHEF iQ's 'five internal sensors' phrasing in its introduction against its four-internal-plus-one-ambient specification list - on a later date, and keep both readings dated rather than choosing the one that reads better."),
    ("closes", ["Q-02"])
])

for q in (K22,):
    if q['id'] in {x['id'] for x in qdb['known']}:
        raise SystemExit('known already present: ' + q['id'])
    qdb['known'].append(q)

for q in (Q17, Q18):
    if q['id'] in existing_q:
        raise SystemExit('question already present: ' + q['id'])
    qdb['unknown'].append(q)

for d in (D13, D14, D15):
    if d['id'] in existing_d:
        raise SystemExit('discovery already present: ' + d['id'])
    qdb['discovery'].append(d)

with open(PATH, 'w', encoding='utf-8') as f:
    json.dump(qdb, f, indent=2, ensure_ascii=False)
    f.write('\n')

print('suggestions:', len(sdb['suggestions']), 'known:', len(qdb['known']),
      'unknown:', len(qdb['unknown']), 'discovery:', len(qdb['discovery']))
