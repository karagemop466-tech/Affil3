#!/usr/bin/env python3
"""Session c252594d — extend the decision boards.

The brief asks for a section where someone can review suggestions and choose a path before
anything is implemented, and for a clear list of the questions and the missing information that
have to be answered first. Both boards live in data/ and are rendered as-is by tools/build.mjs,
so this script only adds entries; it implements nothing.
"""
import json
import pathlib

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def save(name, obj):
    (DATA / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote data/{name}")


# ------------------------------------------------------------------ suggestions
doc = load("suggestions.json")
new = [
    {
        "id": "S-11",
        "topic": "Design direction for the site",
        "current": "A",
        "options": [
            {
                "id": "A",
                "label": "Keep the warm editorial system as it stands: cream paper, terracotta accent, serif headlines, illustration-led cards, one navigation group.",
                "tradeoff": "It is the only direction that has actually been built and checked against the publishing gate, so it is the cheapest to keep and the safest to keep shipping.",
            },
            {
                "id": "B",
                "label": "Push it toward a shop: bigger product photography, price-shaped cards, a persistent comparison bar, and the guides demoted below the fold.",
                "tradeoff": "Closer to how a store reads, and further from why people trust the site. It also collides with the price and availability rule, which only allows prices that come from Amazon's own feeds.",
            },
            {
                "id": "C",
                "label": "Push it toward a reference work: dense specification tables, numbered source citations on every claim, and the front page replaced by an index.",
                "tradeoff": "Maximum authority and minimum charm. It reads like a database and converts like one.",
            },
            {
                "id": "D",
                "label": "Seasonal campaign layers: the same system with a monthly theme - roast season, grill season, small-kitchen season - carried by the hero band and the guide covers.",
                "tradeoff": "Gives the front page a reason to change and gives search engines a freshness signal, at the cost of a design change every month and the risk of looking like a banner ad.",
            },
        ],
        "recommendation": (
            "A as the base, with D layered on in the way the front page already hints at. The current "
            "system passes the publishing gate, reads like a publication, and carries the disclosure "
            "without shouting. If one thing changes, make it D: a seasonal band is the cheapest way to "
            "keep a buying guide looking alive without inventing facts."
        ),
    },
    {
        "id": "S-12",
        "topic": "Which product leads the front page",
        "current": "A",
        "options": [
            {
                "id": "A",
                "label": "Lead with the shelf in register order: the dual-basket fryer, the french-door oven, the 8 qt fryer, the two thermometers (current).",
                "tradeoff": "Neutral and predictable. It also leads with the product whose listing and maker page disagree most, because that row is first for historical reasons.",
            },
            {
                "id": "B",
                "label": "Lead with the unit that has the most complete, least contradictory record.",
                "tradeoff": "The most defensible page becomes the most boring page, and the two units with the most interesting caveats get buried.",
            },
            {
                "id": "C",
                "label": "Lead with the seasonal unit and rotate the lead with the season.",
                "tradeoff": "Matches what people are actually shopping for at the time, and makes the front page change without anything false being claimed.",
            },
        ],
        "recommendation": (
            "C, with the caveat that the seasonal choice is a judgement about what people are buying, "
            "not a claim about what sells. No conversion data exists yet, so a rotation decided by "
            "preference and revisited when the click counter is live is the honest version."
        ),
    },
    {
        "id": "S-13",
        "topic": "How opinionated the guides should be",
        "current": "A",
        "options": [
            {
                "id": "A",
                "label": "Stay descriptive and sourced: explain what each shape does, what the maker states, and what could not be confirmed (current).",
                "tradeoff": "Safe and durable, but it reads more like a well-organised manual than a magazine, and it leaves the reader to do the final comparison.",
            },
            {
                "id": "B",
                "label": "Take a position in each guide - say which type suits which household - while keeping every factual sentence sourced.",
                "tradeoff": "Better for the reader and better for search, at the cost of a stated opinion that has to be defensible without ever crossing into an unqualified product claim.",
            },
            {
                "id": "C",
                "label": "Add a clear recommendation per guide: one product we would buy, with the reason.",
                "tradeoff": "The strongest commercial move and the hardest to keep honest, because the site has never used a product. A recommendation without hands-on use is a recommendation from a specification sheet.",
            },
        ],
        "recommendation": (
            "B. Position is the one thing a specification sheet cannot supply, and every position in "
            "these guides is about suitability for a household rather than a claim about a product. "
            "C is not available yet: the site states plainly that it is not a test kitchen, and "
            "publishing a pick would contradict that in the same sentence."
        ),
    },
    {
        "id": "S-14",
        "topic": "Article length and shape",
        "current": "A",
        "options": [
            {
                "id": "A",
                "label": "Medium guides of roughly 700 to 1,000 words, one question each, with a comparison table and a short reader-questions section (current).",
                "tradeoff": "Enough to be useful, short enough to be finished, and each one has to earn its place with a source.",
            },
            {
                "id": "B",
                "label": "Long-form guides of 1,500 words or more, with history, science and technique, as a magazine would run.",
                "tradeoff": "Stronger search performance and a real reason to subscribe, and a much larger surface for an error to hide in.",
            },
            {
                "id": "C",
                "label": "Short answer pieces of 300 words, designed to be skimmed and shared.",
                "tradeoff": "Fast to produce and easy to read, and unlikely to rank for the questions that actually matter.",
            },
        ],
        "recommendation": (
            "A for the running rhythm, with one B-length flagship per quarter. Depth is what a "
            "question-shaped guide earns by answering the whole question, not by hitting a word "
            "count; the current guides already show the shape works."
        ),
    },
    {
        "id": "S-15",
        "topic": "Whether the shelf grows past five products",
        "current": "A",
        "options": [
            {
                "id": "A",
                "label": "Stay at the five products the owner supplied, and go deeper on them (current).",
                "tradeoff": "Nothing is published that nobody checked, and the shelf stays too thin to rank for most category queries.",
            },
            {
                "id": "B",
                "label": "Add a second shelf of products from the same three categories, each with the same product-intent and observed-redirect discipline.",
                "tradeoff": "Doubles the pages that can rank, and doubles the verification load, including the link-intake work that is currently the bottleneck.",
            },
            {
                "id": "C",
                "label": "Add a 'considered alternatives' section naming types and models without linking them.",
                "tradeoff": "Cheap, and it cannot earn a commission, so it only pays if the guide itself earns the click.",
            },
        ],
        "recommendation": (
            "B, but only after Q-01 and Q-02 are closed. More products do not fix an unresolved link "
            "test; they multiply it. Until a Special Link is confirmed to credit a sale, a larger "
            "shelf is a larger untested surface."
        ),
    },
    {
        "id": "S-16",
        "topic": "How the guides earn their traffic",
        "current": "A",
        "options": [
            {
                "id": "A",
                "label": "Question-shaped titles that read like a buyer asked them, each with the comparison table near the top (current).",
                "tradeoff": "Matches how people search and how they read, and it will never be as dense with keywords as a title written for a crawler.",
            },
            {
                "id": "B",
                "label": "Keyword-shaped titles with the question as a subtitle.",
                "tradeoff": "Usually more search volume, at the price of the tone that makes the site feel like it was written for someone rather than for a robot.",
            },
            {
                "id": "C",
                "label": "Keep question-shaped titles and add an internal 'questions we answer' index page that groups every guide by the question it answers.",
                "tradeoff": "One more page to maintain, and it gives a crawler a second, denser route through the same material.",
            },
        ],
        "recommendation": (
            "A with C. The titles are the reason the guides read like advice rather than filler, and "
            "an index page by question is a small addition that helps a reader and a crawler at once."
        ),
    },
    {
        "id": "S-17",
        "topic": "Whether the evidence surfaces move up from the footer",
        "current": "A",
        "options": [
            {
                "id": "A",
                "label": "Keep the source register, questions, suggestions and flags in the footer and behind one 'Research desk' group in the navigation (current).",
                "tradeoff": "The reading experience stays clean, and a reader who never looks for the evidence never finds it.",
            },
            {
                "id": "B",
                "label": "Add a visible 'How we check' link in the masthead next to the navigation.",
                "tradeoff": "One more item in the top bar, and a stronger trust signal for the people who are checking.",
            },
            {
                "id": "C",
                "label": "Surface a short 'what we could not verify' line on every product card, not only on the product page.",
                "tradeoff": "More honesty in the place where the decision is made, and a busier card that some readers will read as a problem.",
            },
        ],
        "recommendation": (
            "B, and C for the two rows that have real caveats. The evidence pages exist and are "
            "well made; the only thing missing is a signpost that costs one item in the masthead."
        ),
    },
    {
        "id": "S-18",
        "topic": "Distribution beyond the site itself",
        "current": "A",
        "options": [
            {
                "id": "A",
                "label": "Publish and wait: the sitemap, the feed and Search Console, and nothing else (current).",
                "tradeoff": "Cheapest, and the slowest possible route to traffic.",
            },
            {
                "id": "B",
                "label": "Republish each guide as one social post in a single channel, with the link back to the guide.",
                "tradeoff": "Real distribution, and a channel that may not be the one the reader is on.",
            },
            {
                "id": "C",
                "label": "Hold distribution until the click counter is live, so that distribution and measurement are switched on together.",
                "tradeoff": "Delays traffic by as long as the collector takes to deploy, and avoids sending people to pages whose performance cannot be read.",
            },
        ],
        "recommendation": (
            "C, then B. The measurement question is the one the brief puts first, and there is no "
            "point driving traffic to a page whose clicks cannot be counted. Once the collector is "
            "deployed, one channel is enough to test the guides; two channels at once would make it "
            "impossible to tell which one worked."
        ),
    },
]
existing = {s["id"] for s in doc["suggestions"]}
for s in new:
    if s["id"] not in existing:
        doc["suggestions"].append(s)
save("suggestions.json", doc)

# ------------------------------------------------------------------ questions
q = load("questions.json")

known = {k["id"]: k for k in q["known"]}
known["K-10"]["statement"] = (
    "All five tracked products now have a manufacturer specification page that states at least some "
    "of capacity, temperature, power or dimensions. The ThermoMaven page was located on 2026-11-20, "
    "which closed FLG-025."
)
known["K-10"]["sources"] = ["S11", "S12", "S13", "S14", "S21", "S22"]

q["known"].extend([
    {
        "id": "K-13",
        "statement": "Amazon defines the ASIN itself: an ASIN is 'a unique combination of 10 letters and numbers that Amazon assigns to a product', on Amazon's own advertising site. The 10-character rule the register relies on is therefore Amazon's, not a third party's.",
        "sources": ["S23"],
    },
    {
        "id": "K-14",
        "statement": "The ThermoMaven F1 Ace page states an instant read in one second on a thermocouple sensor, a stated accuracy of plus or minus 0.5 °F, a bright auto-rotating display, a 100% waterproof design, a built-in magnet, and a lifetime warranty activated within 30 days of purchase.",
        "sources": ["S21"],
    },
    {
        "id": "K-15",
        "statement": "The CHEF iQ Sense page states an internal temperature range of 32 to 212 °F and an ambient temperature range of 32 to 1,000 °F, with heat resistance to 1,000 °F. The 1,000 °F figure is the ambient and heat-resistance limit, not the range the probe measures in food.",
        "sources": ["S14"],
    },
    {
        "id": "K-16",
        "statement": "Chefman publishes two different 8 qt air fryers: RJ38-8T-BLACK, stated at 450 °F on Hi-Fry, and RJ38-SQSS-8T, stated at 200 to 400 °F. The Amazon listing for the tracked 8 qt unit names RJ38-SQSS-8T in its own copy, and its title advertises the 450 °F Hi-Fry figure that belongs to the other machine.",
        "sources": ["S12", "S22", "S16"],
    },
    {
        "id": "K-17",
        "statement": "The submitted short link for the ThermoMaven row, link.amazon/B0c8moW59, has resolved to the observed ThermoMaven listing across two dated fetches by two independent sessions, so that row now carries a tagged outbound link like the other four.",
        "sources": ["S05", "S04"],
    },
])

q["unknown"].extend([
    {
        "id": "Q-14",
        "question": "Is the observed ThermoMaven listing the F1 Ace, and is the maker's F1 Ace page the right page to publish specifications against it?",
        "why_it_matters": "The maker's page and the listing carry different model names. The features match, so the two are consistent, but the maker does not publish the marketplace identifier, so the P04 specification row rests on a very likely rather than a confirmed match.",
        "how_to_close": "Ask ThermoMaven, through the contact form on its own product page, whether the 1 Sec Professional listing is the F1 Ace. One reply closes Q-14 and Q-16 together.",
        "sources": ["S21", "S04"],
        "blocking": False,
    },
    {
        "id": "Q-15",
        "question": "Which ThermoMaven variant did the owner mean when the link was supplied, and is it the one the link now lands on?",
        "why_it_matters": "The maker sells a 1-second model and a 0.5-second model, and the marketplace carries several near-identical listings with the same accuracy and certification wording. Publishing a spec sheet for the wrong sibling model would be a confident wrong answer.",
        "how_to_close": "Open the supplied link in a signed-in Amazon session and name the product and the model number, the same one-line check that closes Q-01 for the other four rows.",
        "sources": ["S05", "S21", "S04"],
        "blocking": True,
    },
    {
        "id": "Q-16",
        "question": "Does the owner's Amazon account actually credit a sale when a tagged link on this site is clicked?",
        "why_it_matters": "Every outbound link on this site carries the tracking ID, but a tagged link has never been clicked from this site and confirmed to appear in the account's reports. Until that happens, the earning side of the whole plan is an assumption.",
        "how_to_close": "Open one Special Link in Associates Central, click it from this site, and confirm the click appears in the reports. This is the same manual step as D-02, and it is the single highest-value thing the owner can do.",
        "sources": ["S01", "S02"],
        "blocking": True,
    },
    {
        "id": "Q-17",
        "question": "Has any appliance on this shelf actually been used by a person?",
        "why_it_matters": "The site says plainly that it is not a test kitchen and that nothing is hands-on measurement. That is honest and it is also the main limit on what the guides can claim. It is also the difference between a specification-led guide and a recommendation.",
        "how_to_close": "Either cook with one of the tracked units and record what happened, or state permanently that the site is specification-led. Both answers are publishable; leaving it ambiguous is not.",
        "sources": [],
        "blocking": False,
    },
])

q["discovery"].extend([
    {
        "id": "D-09",
        "suggestion": "Ask ThermoMaven whether the 1 Sec Professional listing is the F1 Ace, and whether the unit carries NSF certification and an IP67 rating, then keep the written reply with the source register.",
        "closes": ["Q-14", "Q-01"],
    },
    {
        "id": "D-10",
        "suggestion": "Read the manufacturer user-guide PDF linked from each product page for the values the web page omits, such as overall dimensions, power draw, temperature limits and probe care instructions.",
        "closes": [],
    },
    {
        "id": "D-11",
        "suggestion": "Save a dated, readable copy of each product listing's 'About this item' block, so that when a listing's copy changes, the change is visible rather than merely suspected.",
        "closes": ["Q-01"],
    },
    {
        "id": "D-12",
        "suggestion": "Write down the commercial goal for the next ninety days - clicks, clicks toward one product, or a declared-site approval - so the campaign ledger has a definition of success to record against.",
        "closes": ["Q-09"],
    },
])

save("questions.json", q)
print("done")
