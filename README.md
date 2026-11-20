# Affil3

Amazon Associates publications built from a verified source register. Tracking ID `shopnow047c-20`.

**Live:** https://karagemop466-tech.github.io/Affil3/

GitHub Pages serves `main` at `/`, so the repository contains more than one published surface.
Nothing was deleted to make room; each session's output is kept and reachable.

## What is published

| Path | Owner | What it is |
|---|---|---|
| `/` | root site (`tools/build.mjs`) | Integrated publication: shop, categories, guides, sources, questions, suggestions, flagged, ledger, measurement, compliance |
| `/editorial/` | `tools/build.py` | A second, independently generated publication: front page, 3 category pages, 5 product pages, 4 guides, source register, flagged-for-review, open questions, suggestions queue, dashboard, disclosure and method |
| `/docs/` | session `arena/c46310a7-affil3` | **Not in the tree at `1f65f70`** (no `docs/` path is tracked; see FLG-039). Described as: a third, independently generated publication: shop front, product register with the product-intent confirmation record, 4 buyer guides, comparisons, analytics, suggestions, decision questions, flagged items, compliance, executive summary. Verified with `scripts/` (sitemap, feed, link checker, intake validator, source verifier) and a self-hosted analytics endpoint in `server/` |
| `/counterwise/` | session `arena/c7a56e3d-affil3` | A fourth, independently generated publication: 5 question-shaped guides, 4 verified listings with product-intent records, comparison table, source register with retrieval grades, gate report, suggestions board, open questions, flagged-for-review, executive summary. Built and policed by `counterwise/tools/build.py` + `gate.py` (12 rules), 31 tests, self-hosted event collector shipped unarmed |
| `/counter-desk/` | session `arena/3b45b513-affil3` | A reader-facing publication generated from its own register: front page, 5 product pages with withheld-value reasoning, 3 clusters, 7 question-led guides, an interactive counter-space & fit finder, an RSS feed and a sitemap. Gated by `tools/3b45b513/gate.mjs` (4,330 checks, 0 failed) with 19 gate tests; CI in `.github/workflows/counter-desk.yml` |
| `/legacy/arena-83a43a96/` | preserved | The first session's site, kept unchanged |

`/editorial/` and `/docs/` exist because their builds were written against different data models and
each verification pass found things the other register did not. Keeping all builds preserves every
verification pass rather than merging them into one file whose provenance nobody can reconstruct.

## Read these first

| File | What it is |
|---|---|
| [`EXECUTIVE-SUMMARY-478e6577.md`](EXECUTIVE-SUMMARY-478e6577.md) | **The current summary (2026-11-20, session `478e6577`)**: what this pass re-checked, what changed, the open conflicts (FLG-037, FLG-038), and the decisions waiting |
| [`EXECUTIVE_SUMMARY-4c8c7811.md`](EXECUTIVE_SUMMARY-4c8c7811.md) | Session 4c8c7811: sitemap gate fix (FLG-040), dated short-link re-check, what is still open |
| [`EXECUTIVE-SUMMARY-c252594d.md`](EXECUTIVE-SUMMARY-c252594d.md) | The previous session's summary: the five products, what was corrected on 2026-11-20, what is verified and from where, what is still open, and the decisions waiting |
| [`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md) | The first session's summary, kept for the record (describes an earlier, smaller shape of the site) |
| [`EXECUTIVE_SUMMARY-6249757a.md`](EXECUTIVE_SUMMARY-6249757a.md) | The root site's earlier summary |
| [`QA-BRIEF.md`](QA-BRIEF.md) | 30 questions: answered, unanswered, and what closes each one |
| [`EXECUTIVE_SUMMARY-3b45b513.md`](EXECUTIVE_SUMMARY-3b45b513.md) | The Counter Desk edition: what is verified, what is withheld and why, and the two corrections it made to earlier findings |
| [`VERIFICATION-3b45b513.md`](VERIFICATION-3b45b513.md) | Line-by-line verification log for that edition, with every official URL |
| [`COORDINATION.md`](COORDINATION.md) | All session boards, claims, verification logs, merge logs |
| [`data/`](data/) | Register for the root site |
| [`data/c46310a7-affil3/`](data/c46310a7-affil3/) | Register for the `/docs/` site (session-scoped copy; identical content to the session's committed records) |
| [`data/register/`](data/register/) | Register for `/editorial/` |

## Build

**Root site** (Node, no dependencies):

```bash
node tools/build.mjs     # data/*.json  -> repository root
node tools/verify.mjs    # gates
```

**Counter Desk edition** (Node, no dependencies):

```bash
node tools/3b45b513/build.mjs      # data/3b45b513/*.json -> counter-desk/
node tools/3b45b513/gate.mjs       # 4,330 publishing checks
node --test tools/3b45b513/gate.test.mjs   # 19 tests, 7 of which break a page on purpose
```

**Editorial site** (Python, no dependencies):

```bash
python3 tools/build.py       # data/register/*.json -> editorial/
python3 tools/check_site.py  # gates
```

**Docs site** (Python, standard library only):

```bash
python3 scripts/build_sitemap.py --check   # docs/sitemap.xml covers every live page
python3 scripts/check_links.py            # no broken internal links in docs/
python3 scripts/build_feed.py             # keep docs/rss.xml in sync
python3 scripts/amazon_intake.py --link 'https://link.amazon/B04G1MEwY' --validate-only
python3 scripts/verify_sources.py         # re-check recorded official listing URLs
python3 server/analytics_server.py --port 8080   # self-hosted analytics endpoint (no IPs stored)
```

All builds are deterministic. CI rebuilds the root and editorial sites and fails if the committed
output differs; the docs-site workflow (`.github/workflows/check.yml`) runs the docs-site gates.

## What the root gate refuses to let through

`node tools/verify.mjs` prints its own tally; at this commit it runs **7,990 checks** over the published root
pages (the figure grew because the gate's page list was synced with the build's, which had been skipping
`compare/`, `workflow/`, `privacy/` and `design-brief/`, and because of the citation rules below). It stops the build on:

- a page without the Associates statement, the disclosure strip above `<main>`, or the footer repeat;
- an Amazon retail link without `tag=shopnow047c-20`, or without `rel="sponsored"`;
- a `link.amazon` short link published as a clickable link (it cannot carry the tag, so it renders as text);
- a currency amount anywhere in the HTML, a star rating or a review count;
- an image that is missing, remote, or without `alt` text;
- a page without a canonical URL, with more than one `h1`, or with a title longer than 90 characters;
- a broken internal link, a missing anchor, or a page missing from the sitemap;
- a source ID that does not exist, or a spec row citing one;
- a cross-reference in a register or a rendered page that does not resolve to a row — every `S01`-style source id, `FLG-nnn`,
  `S-nn`, `Q-nn`, `K-nn` and `D-nn` (added 2026-11-20 after a first batch of stale references shipped; FLG-042);
- an inline citation in a guide that the guide does not declare in its own source list, and a sentence carrying a measurement
  (`1700 W`, `450 °F`, `8 qt`, `25 presets`) that cites a policy, disclosure or developer page instead of a maker, retailer or
  food-safety source — the rule that caught four guides citing the FTC page for Chefman wattage figures (S-29, FLG-042).

The link rules are enforced by the build itself (`linkPolicy` in `tools/build.mjs`), so a new template
cannot bypass them, and by the gate, so a hand-edited page cannot either.

## One indexable site

The root sitemap offers one publication: the root site. `robots.txt` disallows `/editorial/`, `/legacy/`,
`/crisp-index/`, `/counter/`, `/counterwise/` and `/counter-desk/` (widened 2026-11-20), and every
`/editorial/` page carries `<meta name="robots" content="noindex,nofollow">`.

Read that as crawl management, not de-indexing, because two things are true and the README used to imply
neither. Google reads `robots.txt` from the host root, not from a project path, so `Affil3/robots.txt` is
not consulted for these URLs at all (**FLG-038**). And even where it is read, Google states that
`robots.txt` "is not a mechanism for keeping a web page out of Google", that a disallowed URL can still
appear in results without a description, and that `noindex` cannot be declared in `robots.txt` — while a
page that *is* disallowed cannot have its `noindex` tag seen (sources S24, S25, S26; **FLG-041**). Only one
of the secondary editions ships a `noindex` tag today. What actually de-indexes an edition is a
`<meta name="robots" content="noindex,follow">` in that edition's own generator, without a Disallow line,
or moving it under `/legacy/` — options **B** and **C** of **S-20**, which is an owner decision because each
edition is built by a different session's tooling. The other surfaces stay online and reachable for the
people who need their evidence.

## What the editorial gate refuses to let through

- A price. No currency amount may appear in the HTML at all.
- A star rating or review count.
- A product call-to-action without `tag=shopnow047c-20`.
- An Amazon citation not marked `rel="nofollow"`.
- A page without the required Associates statement.
- A spec row citing a source ID that does not exist.
- A link that escapes the published subtree.
- A page missing from that subtree's sitemap.

This is why **no buy button renders on `/editorial/`**: the submitted links carry no tracking tag.
See `FLG-003` on the [flagged page](https://karagemop466-tech.github.io/Affil3/editorial/flagged/).

## The tag rule, and the short-link conflict

Amazon's Program Policies, Participation Requirements §2(b), require the Associates ID as a URL parameter on every link placed on a site. The buy buttons on this site are `/dp/<ASIN>` URLs that carry `tag=shopnow047c-20`. The submitted short links (`link.amazon/…`) carry no tag of their own, so the site does not publish them as clickable links.

What the short links resolve to is **not settled**. On 2026-11-20, three sandbox rounds recorded product pages and two recorded the Amazon home page for the same five links (FLG-037). None of the five is called valid or invalid here. The owner's signed-in check and gate G-02 are the way to settle it.

## Disclosure

This site participates in the Amazon Associates Program and earns from qualifying purchases.
Every outbound product link is marked as sponsored. Sources:

- [Associates Program Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement)
- [Associates Program Policies](https://affiliate-program.amazon.com/help/operating/policies)
- [FTC endorsements guidance](https://www.ftc.gov/business-guidance/advertising-marketing/endorsements-influencers-reviews)
- [Google rel="sponsored" guidance](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links)

## Licence and attribution

Product names and trademarks belong to their owners. Specification values are quoted from the
publisher's own pages and cited by source ID. Neither publication is endorsed by or affiliated with
Amazon.com, Inc. beyond participation in the Amazon Associates program.

As an Amazon Associate I earn from qualifying purchases.

---

## Session `93cee724` addition (integrated 2026-11-20; nothing above changed)

| Path | Owner | What it is |
|---|---|---|
| `/crisp-index/` | `tools/build_site.py` (Python, stdlib) | A third publication surface: shop front page, 5 question-shaped guides (incl. seasonal), compare hub, test queue with verbatim listing quotes, about/methodology, disclosure, and a Workshop group (product register with intended-vs-observed separation, flagged-for-review, suggestions & decisions queue, open questions, campaign ledger & analytics gates) |

Also added at root: [`VERIFICATION.md`](VERIFICATION.md) (line-by-line verification log,
sources S-01…S-15 with links for manual review) and
[`EXECUTIVE_SUMMARY-93cee724.md`](EXECUTIVE_SUMMARY-93cee724.md). This session's register is
[`data/93cee724/`](data/93cee724/) (its own namespace — `data/*.json` above are untouched).

**Build & gates (this surface):**

```bash
python3 tools/build_site.py   # data/93cee724/*.json -> crisp-index/
python3 tools/validate.py     # data + compliance gates
python3 tools/check_links.py  # internal links + anchors
```

**Find worth knowing:** the Amazon-owned ASIN definition that FLG-012 (board) recorded as
"not located" exists at https://sell.amazon.com/blog/what-is-an-asin (10-character format;
ASIN appears after `/dp/`). Cited as S-03 in `VERIFICATION.md`.

Fourth sync (2026-11-20): merged PRs #31/#37/#25 — outbound link-policy enforcement
(short links shown as non-clickable code; auto-tagging of retail Amazon links), robots
policy for parallel publications, and the committed thermometer product image now carried
in the ShopNow Kitchen build. Gate: 3212 checks passed, 0 failed.


## Crisp & Counter — session edition at `/counter/` (`arena/0a90f62c-affil3`)

A shop-shaped kitchen-gear publication with its research desk in the open: question-first
buying guides, a verified product register with an official source on every findings row,
a product-intent record (intended ASIN fields kept strictly separate from observed redirect
targets), a suggestion board with options to review before anything is implemented, an
empty-but-defined campaign ledger, and a compliance gate page. Published at
`/counter/` following the `crisp-index/` namespace convention; its design rules differ
from the root pipeline's (it publishes date-stamped observed prices and ratings with the
listing linked as source of truth), so `tools/disclosure-check.mjs` skips it the same way
it skips `crisp-index/` and it is gated by its own workflow instead.

```bash
python3 scripts/build_site.py        # render the edition into counter/ (stdlib only)
python3 tools/verify_site.py         # release gate: build drift, disclosures, sources, links
```

Data of record: `data/products-0a90f62c.json` and `data/registers.json` (sources S01–S13,
flags FLG-001…010, questions Q-01…10, suggestions SG-01…12, the five defined events, and
the campaign-ledger schema). `server/collect.js` is the edition's self-hosted
privacy-preserving analytics collector (GitHub Pages cannot host it — FLG-006).

See `docs/EXECUTIVE-SUMMARY.md` — not in the tree, like the rest of that session's `/docs/` output
(FLG-039) — and `counter/desk/coordination/`, which is published.
