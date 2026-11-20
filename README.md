# Counter Tested — Amazon Associates shelf, publishing machinery

Live site: **<https://karagemop466-tech.github.io/Affil3/>** · Deployed by GitHub Actions from `site/`.

A five-listing affiliate shelf with the paperwork attached: pages are generated from `data/`, a build gate
refuses to publish anything that breaks the Amazon Associates licence or the site's own honesty rules, and
every value that could not be confirmed from an official source is blank and flagged rather than guessed.

> **Read this first:** [Executive summary](EXECUTIVE_SUMMARY.md) ·
> [COORDINATION.md](COORDINATION.md) (task board, for parallel sessions) ·
> [docs/COMPLIANCE.md](docs/COMPLIANCE.md) (what the licence forbids, and what this repo therefore does not do)

## Two minutes to understand the state

| Question | Answer |
| --- | --- |
| Is the site live? | Yes — published from `main` via Pages, with the gate running in CI. |
| Are the product links clickable? | **No, deliberately.** Five listing links were supplied as `https://link.amazon/<9-char id>`; the destination could not be resolved from this environment, so each card is gated. [Why, on the site](https://karagemop466-tech.github.io/Affil3/product-status.html). |
| What makes them clickable? | One human, ~5 minutes per link, in the enrolled account: [docs/LINK_TEST_PROTOCOL.md](docs/LINK_TEST_PROTOCOL.md). |
| What is verified? | Every programme rule the site relies on, fetched from Amazon's own pages on 2026-11-20 — 28 rows in [`data/sources.json`](data/sources.json), each with URL, section and verification depth. |
| What is not verified? | Everything about the five products. Name, brand, category, price, availability, rating, commission are all `null`, and the tools refuse to fill them. |
| Is there any traffic data? | No. The campaign ledger ships empty by design; the collector exists but Pages cannot host a process (see `data/program.json → measurement.endpoint`). |

## Layout

```
data/            the registers: program, products (product-intent records), sources (evidence),
                 suggestions, questions, flags, events.schema, clusters, editorial-calendar,
                 layout, people, ledger/campaign.jsonl (empty on purpose)
src/content/     guide + page prose (markdown), src/assets/ (stylesheet, event script, illustrations)
tools/           build_site.py · check_site.py (the 13-check publish gate) · product_intake.py ·
                 campaign_ledger.py · events.py · collect_server.py · new_guide.py
site/            generated output, committed so Pages can serve it; CI fails on drift
docs/           COMPLIANCE · DATA_CONTRACTS · EDITORIAL · LINK_TEST_PROTOCOL · MEASUREMENT · DECISIONS
.github/workflows/deploy.yml   build → drift check → register checks → gate → Pages deploy
COORDINATION.md                shared task board for parallel agent sessions
```

## Commands

```bash
python3 tools/build_site.py              # rebuild site/ from data/ + src/
python3 tools/check_site.py              # run the publish gate (13 checks)
python3 tools/build_site.py --check      # prove site/ is not hand-edited
python3 tools/product_intake.py scan     # validate the product-intent register
python3 tools/campaign_ledger.py show    # print the ledger as the site sees it
python3 tools/events.py report           # summarise the local event stream
python3 tools/new_guide.py --title '…' --cluster air-fryers --week 3   # scaffold + calendar row
```

Python 3.11, standard library only. No `npm`, no `pip install`, no external services.

## The rules the machinery enforces

These are not house style; each one traces to a clause in the fetched primary sources, and each has a
numbered check in `tools/check_site.py` that fails the deploy. Full table with citations:
[docs/COMPLIANCE.md](docs/COMPLIANCE.md).

1. **CHK-01** no module may open a network route to Amazon, or ingest Program Content for analysis or model training.
2. **CHK-02** the required associate statement and the disclosure strip are present on every page.
3. **CHK-03** no unsupported superlatives, scores or "we tested" claims without a provenance id.
4. **CHK-04** every outbound Amazon link carries the registered tag, in the `XXXXX-##` form, matching the account's Associates ID.
5. **CHK-05** affiliate links are marked `rel="sponsored"`; citations are not.
6. **CHK-06** no shortener/intermediate host and no non-product URL is published as a product link.
7. **CHK-07** no price or rating is rendered without an authorised source.
8. **CHK-08** Amazon-sourced wording carries the required content disclaimer.
9. **CHK-09** no price-alert or price-tracking feature.
10. **CHK-10** no expired seasonal/promotional sentence lingers.
11. **CHK-11** every guide carries the "what we did not test" block.
12. **CHK-12** sitemap, feed, editorial calendar and built pages all agree.
13. **CHK-13** titles, descriptions, self-canonicals under one host, and every internal link and asset resolves.

## Working rules for any session (agent or human)

1. Read and update [COORDINATION.md](COORDINATION.md) first. Claim a task with your session ID and file
   scope before editing; never edit a file another session claimed; `git pull --rebase` before every push.
2. Work in `data/` and `src/`, never in `site/`. Rebuild, run the gate, commit.
3. Never fill a blank with an inference. A sourced blank is worth more than a plausible number, and the
   gate will punish the guess anyway.
4. Do not add a scraper, a price cache, a review corpus, or a model trained on Program Content. If a task
   seems to require one, it is a written-approval question for Amazon, not a code question (D-004).
5. Do not manufacture traffic, clicks, impressions or test purchases — prohibited, and it would poison the
   only evidence this project has.

## License / attribution note

All product identifiers, prices and availability belong to their respective owners and are not reproduced
here. Disclosure strings are quoted from Amazon's Associates Program Operating Agreement and Program
Policies as fetched on 2026-11-20; advertising-guidance references are to the U.S. FTC's Endorsement
Guides (16 CFR Part 255). Illustrations in `src/assets/img/` are original artwork created for this site —
they are not product photography, by design (see `docs/COMPLIANCE.md` §images).
