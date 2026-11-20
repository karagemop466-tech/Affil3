# Affil3

An Amazon Associates publication built from a sourced product register. Tracking ID `shopnow047c-20`. This repository does not yet connect an AI provider, product-data API, query data source, analytics endpoint, or Associates reporting feed; see the executive summary and S-13/Q-14 on the site. No autonomous research or publishing claims are made.

**Live:** https://karagemop466-tech.github.io/Affil3/

GitHub Pages serves `main` at `/`. The root publication is the only search-index surface. The earlier editorial build remains reachable at `/editorial/` as a `noindex` archive so its separate register stays reviewable without presenting a second publication to search engines.

## What is published

| Path | Owner | What it is |
|---|---|---|
| `/` | root site (`tools/build.mjs`) | Integrated publication: shop, categories, guides, sources, questions, suggestions, flagged, ledger, measurement, compliance |
| `/editorial/` | `tools/build.py` | Noindex archive of the independent editorial register and its review pages; not in the root sitemap or robots sitemap declarations |
| `/docs/` | retired | The earlier third publication was removed for showing prices and ratings it could not keep accurate; a single noindex redirect page remains at `/docs/index.html` (FLG-043; history in FLG-039) |
| `/counterwise/` | session `arena/c7a56e3d-affil3` | A fourth, independently generated publication: 5 question-shaped guides, 4 verified listings with product-intent records, comparison table, source register with retrieval grades, gate report, suggestions board, open questions, flagged-for-review, executive summary. Built and policed by `counterwise/tools/build.py` + `gate.py` (12 rules), 31 tests, self-hosted event collector shipped unarmed |
| `/counter-desk/` | session `arena/3b45b513-affil3` | A reader-facing publication generated from its own register: front page, 5 product pages with withheld-value reasoning, 3 clusters, 7 question-led guides, an interactive counter-space & fit finder, an RSS feed and a sitemap. Gated by `tools/3b45b513/gate.mjs` (4,330 checks, 0 failed) with 19 gate tests; CI in `.github/workflows/counter-desk.yml` |
| `/editorial/` | `tools/build.py` | A second, independently generated publication: front page, 3 category pages, 5 product pages, 4 guides, source register, flagged-for-review, open questions, suggestions queue, dashboard, disclosure and method |
| `/docs/` | session `arena/c46310a7-affil3` | A third, independently generated publication: shop front, product register with the product-intent confirmation record, 4 buyer guides, comparisons, analytics, suggestions, decision questions, flagged items, compliance, executive summary. Verified with `scripts/` (sitemap, feed, link checker, intake validator, source verifier) and a self-hosted analytics endpoint in `server/` |
| `/kitchen-edit/` | `tools/build_kitchen_edit.py` (session `arena/0a417943-affil3`) | A fourth, reader-facing publication: shop-first front page, 4 question-shaped guides with FAQ JSON-LD, 5 product profiles carrying full intent/observation records, source register, flagged-for-review, decision-readiness questions, suggestion review board, compliance gate, analytics/ledger, working dashboard. Outbound CTAs follow the canonical register's tagged `/dp/<observed-ASIN>?tag=shopnow047c-20` destinations; submitted short links appear as evidence only. Its own gates (`tools/validate_kitchen_edit.py`, G-A1..G-A7) run via `.github/workflows/kitchen-edit-gates.yml`, scoped to its subtree |
| `/legacy/arena-83a43a96/` | preserved | The first session's site, kept unchanged |

`/editorial/` remains reachable because its build uses a separate data model and captures an independent
verification pass. It is explicitly `noindex`; the root publication is canonical for discovery and
sitemap submission. Historical surfaces under `/legacy/`, `/crisp-index/`, `/counter/` and `/counterwise/`
are linked but out of search: crawlers are allowed to fetch them so each page's `noindex` directive can
be read.

## Read these first

| File | What it is |
|---|---|
| [`EXECUTIVE-SUMMARY.md`](EXECUTIVE-SUMMARY.md) | Integrated summary: observed product register, the G-02 purchase-link hold, verification standard, and what is still missing |
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

**Kitchen-edit site** (Python, no dependencies):

```bash
python3 tools/build_kitchen_edit.py      # kitchen-edit/src/*.html -> kitchen-edit/
python3 tools/validate_kitchen_edit.py   # gates G-A1..G-A7 (scoped to kitchen-edit/)
```

All builds are deterministic. CI rebuilds the root and editorial sites and fails if the committed
output differs; the docs-site workflow (`.github/workflows/check.yml`) runs the docs-site gates;
the kitchen-edit workflow (`.github/workflows/kitchen-edit-gates.yml`) runs its gates, scoped to
its subtree.

## What the root gate refuses to let through

`node tools/verify.mjs` runs **8,831 checks** at this commit over the 55 published root pages (FLG-039, FLG-043 and FLG-044 corrected stale figures; the count is whatever the run prints, and a merge that adds a page or a guide changes it, so treat the number as a log line rather than a claim). `tools/build.mjs` and `tools/verify.mjs` both import their page list from `tools/site-scope.mjs`, so the gate cannot walk a shorter list than the builder writes (FLG-043). It stops the build on:
`node tools/verify.mjs` prints its own tally; at this commit it runs **8,831 checks** over the published root
pages (the figure grew because the gate's page list was synced with the build's, which had been skipping
`compare/`, `workflow/`, `privacy/` and `design-brief/`, and because of the citation rules below). It stops the build on:

- a page without the Associates statement, the disclosure strip above `<main>`, or the footer repeat;
- an Amazon retail link without `tag=shopnow047c-20`, or without `rel="sponsored"`;
- a `link.amazon` short link published as a clickable link (it cannot carry the tag, so it renders as text);
- a currency amount anywhere in the HTML, a star rating or a review count;
- an image that is missing, remote, or without `alt` text;
- a page without a canonical URL, with more than one `h1`, or with a title longer than 90 characters;
- a broken internal link, a missing anchor, or a page missing from the sitemap;
- a source ID that does not exist, or a spec row citing one.
- a superseded edition or a root-level session record that the generated `robots.txt` does not exclude (FLG-047);
- an unrendered count token such as `{guide}`, which means prose was hand-typed instead of computed;
- a JSON-LD block that does not parse, or a breadcrumb trail that points at its own page.
- a source ID that does not exist, or a spec row citing one;
- a cross-reference in a register or a rendered page that does not resolve to a row — every `S01`-style source id, `FLG-nnn`,
  `S-nn`, `Q-nn`, `K-nn` and `D-nn` (added 2026-11-20 after a first batch of stale references shipped; FLG-044);
- an inline citation in a guide that the guide does not declare in its own source list, and a sentence carrying a measurement
  (`1700 W`, `450 °F`, `8 qt`, `25 presets`) that cites a policy, disclosure or developer page instead of a maker, retailer or
  food-safety source — the rule that caught five guides citing the FTC page for Chefman wattage figures (S-35, FLG-044).

The link rules are enforced by the build itself (`linkPolicy` in `tools/build.mjs`), so a new template
cannot bypass them, and by the gate, so a hand-edited page cannot either.

## One indexable site

`robots.txt` allows crawlers everywhere so each archived page can be read as `noindex`, and every `/editorial/` page also
carries `<meta name="robots" content="noindex,nofollow">`. The root publication is the one site offered
to search engines; the other surfaces stay online and reachable for the people who need their evidence.
The root sitemap offers one publication: the root site. `robots.txt` disallows `/editorial/`, `/legacy/`,
`/crisp-index/`, `/counter/`, `/counterwise/` and `/counter-desk/` (widened 2026-11-20), and every
`/editorial/` page carries `<meta name="robots" content="noindex,nofollow">`.

Read that as crawl management, not de-indexing, because two things are true and the README used to imply
neither. Google reads `robots.txt` from the host root, not from a project path, so `Affil3/robots.txt` is
not consulted for these URLs at all (**FLG-038**). And even where it is read, Google states that
`robots.txt` "is not a mechanism for keeping a web page out of Google", that a disallowed URL can still
appear in results without a description, and that `noindex` cannot be declared in `robots.txt` — while a
page that *is* disallowed cannot have its `noindex` tag seen (sources S24, S25, S26; **FLG-043**). Only one
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
in the ShopNow Kitchen build. Gate: the run before this line was written reported 3,212 checks passed, 0 failed; the current figure is the one above.


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

See [`docs/EXECUTIVE-SUMMARY.md`](docs/EXECUTIVE-SUMMARY.md) and
`counter/desk/coordination/` on the live site.
## Session `59aebafb` addition (integrated 2026-11-20; nothing above changed)

| Path | Owner | What it is |
|---|---|---|
| `/shopnow/` | `scripts/build.mjs` (Node, stdlib only) | A fourth independent publication: publication front page, 6 question-shaped buyer guides, 4 product records with the intended-vs-observed ASIN split, 4 decision-shape clusters, a 7-row shape comparison, methodology / about / disclosure / privacy, and the full review board — 22 suggestions with paths and trade-offs, 22 open questions with the step that closes each, 10 flagged items, source register, dashboard, executive summary. Client-side search over a static index; RSS, sitemap, robots, humans; JSON-LD on every page |

**Why `/shopnow/` and not `/shop/`.** `/shop/` is another session's hub page (`shop/index.html`). The
first relocation attempt here overwrote it during a local rebuild; the file was restored
byte-for-byte (`diff` against `origin/main:shop/index.html` → identical) and this surface moved to a
free path. The rule that prevents a repeat: **check `git ls-tree origin/main -- <path>` before choosing
a mount point, and treat any non-empty result as claimed.** This checker walks only `shopnow/`, so a
rebuild cannot reach into a neighbour's tree.

**Build and gate** (npm-namespaced so `build` / `verify` / `check` keep meaning the root site):

```bash
npm run shop:build       # register/*.json + shopnow/content/*.md -> shopnow/
npm run shop:check       # 11 gates; exit 1 blocks the merge
npm run shop:verify      # build + gate
npm run shop:links       # derive Special Links from the register; refuses a 9-char ASIN
npm run shop:new-guide   # scaffold the next guide in the cadence
npm run shop:serve       # http://localhost:8080/Affil3/shopnow/
npm run shop:collect     # optional self-hosted event collector on :8788
```

The 11 gates: the Associates sentence above the fold *and* in the footer of every page; `tag=` plus
`rel="sponsored nofollow"` on every Amazon anchor; **no currency figure anywhere**; no testing or
superlative language on any buyer-facing page; no Amazon CDN asset and no third-party script; a
source row behind every published value; intended and observed identifiers kept in separate fields;
no broken internal link; sitemap/feed parity; no orphan page. Authored assets live in
`shopnow/content/assets/` and are copied into the output, because a hand-written file inside a generated
directory is one clean step from destruction — which is how this session lost them once.

**Where this session differs from the others, deliberately.** `/shopnow/` publishes no
specifications at all: a listing title is an observation, not a verified spec, and `/editorial/`
quotes listing-sourced capacity and wattage under its own `S06`. Both readings are dated and
attributed; neither was averaged into the other. Also unlike `/editorial/`, this surface *does*
render buy buttons, built as tagged `?tag=shopnow047c-20` Special Links derived from the resolved
ASINs rather than from the supplied short links.

**Cross-verification, and an adopted correction.** `data/register/products.json` and
`register/products.json` independently recorded the same resolved ASIN set
(`B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH`, `B0DZFD6R9Z`), the same `redirect_had_tag: false`, and the
same blank *intended* ASIN on every row. This session also adopted a correction from this board: a
checkpoint interstitial is not evidence a link is dead. `B0c8moW59` was therefore retried to **six**
attempts across two windows (3 checkpoint, 3 transport) before the negative was recorded — it held,
and that row stays off the shop floor as UNRESOLVED rather than guessed.

As an Amazon Associate I earn from qualifying purchases.

> Sources live in `site-src/`, the build output `countertop-notes/` is gitignored, and the root site remains the published GitHub Pages content (this surface never deploys).

## Countertop Notes — kitchen choices, made clearer (source: `site-src/`, build: `countertop-notes/`)

This repo now contains a publication-style Amazon affiliate site plus a source-backed Research desk. The front page leads with practical buyer questions; product identity, link compliance, analytics, and search setup remain visibly gated wherever the available evidence is incomplete.

## Important status

- Five submitted URLs are recorded. Intended ASIN, official intended listing URL, confirmation date, and confirmation source remain blank until confirmed; observed destinations are separate.
- The selected Tracking ID `shopnow047c-20` is owner-provided and has not been verified against Associates Central.
- The exact compliance status of the supplied short links is unresolved in **FLG-003**; this project does not claim they are invalid.
- Price, availability, reviews, competition, commission, trend, conversion, and revenue fields are blank. The campaign ledger is empty.
- A proposed privacy-preserving five-event schema and a self-hosted Node endpoint are included. The request does not define the five-event contract; the built Pages artifact and default preview serve a disabled runtime, and collection must not be enabled until the specification is confirmed.
- Search Console ownership and reader capture are not configured.

See [Executive Summary](EXECUTIVE-SUMMARY.md), [requirements status](site-src/docs/REQUIREMENTS.md), [official source register](site-src/docs/SOURCES.md), and the public **Flagged for Review** page.

## Build and verify

Requires Node.js 20 or newer. There are no third-party package dependencies.

```sh
npm run notes:check
```

The command builds static HTML into ignored `countertop-notes/` and checks local links, disclosures, navigation, product-link `rel="sponsored"`, source links on table rows, blank unverified fields, sitemap/RSS coverage, event schema, and campaign-ledger state.

To build and preview the site:

```sh
npm run notes:build
npm run notes:serve
```

Both the generated Pages artifact and the default preview serve a disabled analytics runtime. The default preview also rejects event and summary requests. The Node endpoint binds to `0.0.0.0:4173`, but analytics can be enabled only through an explicit environment setting; use that only in an isolated local development environment after review, never in the shared Arena preview or a public production process:

```sh
HOST=127.0.0.1 ANALYTICS_ENABLED=true npm run notes:serve
```

When explicitly enabled, the endpoint stores daily aggregate event counts under ignored `.local/`, with 90-day retention by default. It checks Fetch Metadata, requires a matching Origin, and enables no CORS access. If a separately hosted reverse proxy rewrites the request host, configure only its exact public origin with `ANALYTICS_ALLOWED_ORIGINS`; never allow arbitrary origins. Hosting-provider and reverse-proxy logs can have their own retention. GitHub Pages never runs this server. A production runtime must be separately hosted, privacy-reviewed, configured, and verified before measurement is described as active.

## Site map

- `site-src/pages/` — page content fragments
- `site-src/data/` — product-intent register, sources, requirements, flags, suggestions, event schema, and empty campaign ledger
- `site-src/assets/` — original illustration, design system, and browser scripts
- `scripts/build-site.mjs` — creates pages, sitemap, RSS, and robots file
- `scripts/verify-site.mjs` — offline consistency and link checks
- `server/index.mjs` — optional static preview and aggregate-only API
- `.github/workflows/pages.yml` — checked GitHub Pages build/deployment workflow

The current configured Pages URL is `https://karagemop466-tech.github.io/Affil3/`. Deployment and GitHub Pages Actions-source settings must be confirmed after the PR is merged.
See `docs/EXECUTIVE-SUMMARY.md` — not in the tree, like the rest of that session's `/docs/` output
(FLG-039) — and `counter/desk/coordination/`, which is published.
