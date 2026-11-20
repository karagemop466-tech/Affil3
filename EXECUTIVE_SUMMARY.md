# Affil3 — executive summary

**Updated:** 2026-11-20 by session `arena-43565031-affil3`
**Live site:** https://karagemop466-tech.github.io/Affil3/ (GitHub Pages, source `main` /, build status `built`)
**Repo at base commit:** one file, `README.md`, containing the text `# Affil3`. There was no pre-existing
source register, no product data, and no configuration to inherit. Everything below is new work across
merged PR #1 and this branch.
**Every source used:** [`docs/OFFICIAL-SOURCES.md`](docs/OFFICIAL-SOURCES.md)

---

## 1. The headline finding

**The five product links supplied for this project do not currently identify five products.**

Requested on 2026-11-20, anonymously:

| Submitted | Result |
|---|---|
| `link.amazon/B04G1MEwY` | opened ASIN **B0CDY277D3** (Chefman 6 Qt dual-basket air fryer oven) — not B04G1MEwY |
| `link.amazon/B02NbDxp3` | opened ASIN **B09B7SB46R** (Emeril Lagasse 26QT French-door oven) — not B02NbDxp3 |
| `link.amazon/B00hJ57DV` | opened ASIN **B08DKYBTPH** (Chefman 8 Qt TurboFry) — not B00hJ57DV |
| `link.amazon/B0c8moW59` | opened an Amazon **checkpoint page**. No product at all |
| `link.amazon/B0f3GKalj` | opened ASIN **B0DZFD6R9Z** (CHEF iQ Sense meat thermometer) — a **different category** |

Three things follow, and all three are checkable by hand in a minute:

1. Every token is **9 characters**; every real ASIN reached in the same session is **10**. The most
   likely explanation is a dropped character during a copy-paste, not a dead campaign.
2. Every destination URL carried `plpRedirect=mhFallback` — a fallback marker, not a resolved deep link.
3. Four destinations split across **two Amazon browse nodes** (Air Fryers `17659096011` ×3, Meat
   thermometers `289810` ×1), so the submitted set is not one merchandisable category.

**What this does *not* say.** It does not say the short links are invalid or non-compliant, and the site
nowhere claims that. Compliance is Amazon's determination. The register records only what was observed,
with the URL to reproduce it. (Owner's standing instruction, kept.)

**Why it is the headline:** product identity is upstream of everything else — the niche, the article
list, the images you may lawfully use, and whether a click earns anything. Prior sessions recorded these
fields as permanently blank because the links "could not be dereferenced from the sandbox." That was
wrong; they can be, and the evidence is now published on the site with dates and links.

---

## 2. What is live on the site now

| Surface | Purpose |
|---|---|
| `index.html` | Publication front page. Leads with the shelf (four named listings, dated), one plain-English caveat block instead of a disclaimer on every card, the guide rail, and a "how this shop works" section |
| `shop.html` | The shelf plus five editorial clusters and the topic queue for each |
| `products.html` | The five links exactly as submitted (unchanged, from PR #1) |
| `verification.html` | **Link evidence register** — intended fields and observed fields in separate columns, with control tests and their limitations |
| `suggestions.html` | **Decision room** — 16 ranked suggestions, 3 paths, and the verbatim policy text each suggestion rests on |
| `questions.html` | **Open questions** — 15 questions, each with what is known, what is missing, how to go find it, who must answer, and what it blocks |
| `guides/` | Four question-shaped buyer guides |
| `flagged.html` | Flagged-for-review register: prior FLG-001…007 plus FLG-43565031-01…08, each with a source link |
| `disclosure.html`, `privacy.html`, `about.html`, `sitemap.xml`, `feed.xml` | Reader trust pages and discoverability, from PR #1 |
| `scripts/`, `data/`, `.github/workflows/ci.yml` | The machinery — see §4 |

Disclosure sits under the masthead on every page and repeats in the footer. Every outbound product link
carries `rel="sponsored nofollow"`. Tracking ID `shopnow047c-20` is displayed as submitted and explicitly
marked unconfirmed.

## 3. Design decisions the policy text settles outright

Read from the Operating Agreement (updated 2025-10-15) and Program Policies (updated 2026-04-14). These
are not stylistic preferences; each one closes an open question:

| Rule (verbatim in the claims ledger) | Decision it forces |
|---|---|
| A site "may only show prices and availability" if Amazon serves the link or the data comes from Creators/PA API — §2(b) | **No hardcoded prices or star ratings anywhere.** Buttons say "Check current price on Amazon". This also removes the staleness burden |
| "you must include your Associates ID or 'tag' (appearing as XXXXX-## …) as a parameter in the URL of each link" — §2(b) | Live links must be rebuilt as tagged links; the submitted short links stay as evidence only |
| "When linking to pages with Product lists you must have additional original content … relevant to the Special Link" — §2(b) | Category hubs must carry real decision content. A grid of links is not allowed to be the product |
| "Your Site(s) must contain original content … must contain significant commentary, analysis, or transformation" — Participation Requirements §1 | The anti-slop requirement is an **eligibility** rule, not a taste preference |
| "Under no circumstances may you associate any sub-tag … with a specific end user" — §2(b) | Measurement is aggregate-only. Rules out per-visitor sub-tag A/B schemes |
| "You must remove … any links and related references to limited time promotions as soon as that promotion … ends" — §2(b) | Any seasonal/deal content needs an expiry date enforced at build time |
| Session = 24 hours from click; cart path = **89 days**; ship-and-pay within 180 days — Commission Income Statement §1 | The attribution definition for the campaign ledger. Note 89, not the 90 days repeated across the internet |
| Payment ≈60 days after month end; 10 USD minimum for direct deposit; 2,000 USD gift-card ceiling; 100 USD check with 15 USD fee — §6 | Revenue cannot be judged weekly, which changes how the project schedule should be read |
| Violation → Amazon may "permanently cease payment of … any and all commission income … without notice" — §2 | The reason publishing stays gated rather than reviewed later |
| FTC: a material connection "should be disclosed clearly and conspicuously"; staff guidance "doesn't provide a safe harbor" | Disclosure sits in the page next to the first product link, not only in a footer |

## 4. Machinery: what is automated, and what is deliberately not

**Automated.** `data/*.json` are the source of truth (link verification, claims, suggestions, open
questions, topics). `scripts/build_registers.py` renders four pages from them and refuses, in `--check`
mode, to let a generated page be hand-edited. `scripts/validate_site.py` fails the build on: a register
row without its required fields (R02), a blank that is not a genuine blank or a blank copied from the
observed column (R03), a missing disclosure above the fold or in the footer (R04), a product link
without `sponsored` (R05), a displayed price (R06), an unsupported superlative, with mentions inside
quoted or negated sentences exempted (R07), an unsourced policy sentence (R08), an internal link to a
missing file (R10), a stale generated page (R11), a sitemap row pointing at nothing (R12), a dead
in-page anchor (R13), and unbalanced markup (`check_markup.py`). All of it runs in CI on every push and PR.

**Not automated, on purpose.** Product identity confirmation, disclosure approval, and any publish of an
unverified field stay human. Automated access to Amazon pages was not built: the Commission Income
Statement disqualifies events produced with "bots or automated software," so a scraper would be the wrong
answer to "make the machinery trustworthy." Real product data is expected to arrive through Creators/PA
API once an account exists (Q-04).

**Still missing, and blocked by nothing but a decision:** a receiver for the five instrumented events
(GitHub Pages is static, so clicks are counted nowhere today), Search Console, and the campaign ledger,
which stays empty until rows can be transcribed from an authorized report.

## 5. What is unverified, and stays blank

`3 qualifying sales in 180 days` — not found in the retrieved policy text; not used anywhere.
Commission rates — behind a login; **no percentage appears on the site**.
The 10-character ASIN definition — corroborated by Amazon's own glossary quoted on a Q&A page, not
formally cited. `link.amazon` domain ownership — unknown. Whether tracking ID `shopnow047c-20` is
enrolled — unknown. Whether the four observed listings are the products the owner meant — unknown.
Each is published as a row on the flagged page and as a question with a lookup path, per the rule that a
value you cannot confirm is left blank and flagged rather than filled in.

## 6. Recommended path

**Take Path B ("Publication that earns the click"), with two Path-A items pulled forward: SUG-01 and
SUG-02.** The reasoning is narrow and evidence-based:

- Traffic cannot fix an identity problem. Writing four guides about products you have not confirmed is
  how a site ends up either generic (the slop outcome being objected to) or wrong (the account risk).
- The two blockers are minutes of owner input, not weeks of engineering: ten characters per product
  (Q-03), and one tagged link generated inside the enrolled workflow and checked in the tracking report
  (SUG-02, Q-01).
- Path C's automation has no data source until API access exists, and Amazon's own rules cap what
  automation may do to product pages and to events. Building the pipeline first buys the least.

If no product confirmation arrives, the honest fallback is Path B with a self-chosen niche, which is
`SUG-01` option three — and it should be a decision, not a silent default.

## 7. One structural risk outside the site

Twelve branches are in flight. `main` holds PR #1's build; PR #2 holds a differently-named build of the
same site with its own homepage, analytics receiver and data files; another branch claims repo-wide
integration. Two published shapes on one origin is the fastest way to lose the indexation the brief asks
for. This branch deliberately added **new** pages and used an idempotent script for nav and sitemap so
integration stays a merge rather than a rewrite; requests to other sessions' scopes are logged in
`COORDINATION.md` rather than edited. Integration decision needed: keep `main`'s site, cherry-pick PR
#2's analytics receiver and site checker, close the duplicate build (Q-15).

## 8. Where to look to check any of this

- Retrieved policy text and the exact quotes relied on → [`docs/OFFICIAL-SOURCES.md`](docs/OFFICIAL-SOURCES.md) §A/§B
- Dated link evidence, controls, and reproduction links → [`docs/OFFICIAL-SOURCES.md`](docs/OFFICIAL-SOURCES.md) §C and `verification.html`
- Unverified items → `docs/OFFICIAL-SOURCES.md` §D, `flagged.html`, and `questions.html`
- Session claims, contested files, and handoffs → `COORDINATION.md`
