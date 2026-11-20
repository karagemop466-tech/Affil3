# Release review — independent pass (session `arena/d19dff2c-affil3`)

**Date:** 2026-11-20 · **Branch:** `arena/d19dff2c-affil3` (cut from `main`, continuously rebased onto `origin/main`; state reviewed: `c0bee1e`)
**Scope of this document:** independent verification of the live root publication and its release state,
first-hand re-fetches of the official sources behind the site's compliance claims, a list of
irregularities found (each handed to the owning session as a request — this session edited no files
outside this document and `COORDINATION.md`), the questions that must be answered before decisions can
be made, and suggestions for the owner to choose from.

---

## Executive summary

1. **The site is live and the machinery is green.** GitHub Pages serves `main` at `/` with HTTPS
   enforced. On the reviewed commit: root build → 40 pages, 13 feed items, 39 sitemap URLs;
   publishing gate → **4,642 checks passed, 0 failed**; editorial gate → 21 pages PASS;
   disclosure check → 102 published pages PASS; archive check → 100 pages / 3,152 internal
   references PASS; docs-site checks → 18 sitemap pages OK, 593 internal links, none broken.
   The disclosure strip renders above `<main>` on every checked page, every rendered retail Amazon
   link carries `tag=shopnow047c-20` and `rel="sponsored"`, and no price or rating is published.
2. **The compliance spine re-verified first-hand.** This session re-fetched nine official sources
   (Amazon Associates Operating Agreement, Amazon Associates Program Policies, FTC Endorsement Guides
   FAQ, Google outbound-link guidance, Google robots.txt guidance, Amazon's own ASIN page, USDA FSIS
   temperature chart) and confirmed every core claim the site rests on — see §3. Nothing was
   recalled from memory; each row below was read from the fetched page today.
3. **Seven irregularities found (RR-01…RR-07), none block publication.** They are documentation and
   consistency defects: stale counts on the front page and in three flags, four source citations on
   the live Flagged page that point at the wrong register entry, one flag that contradicts both the
   docs and a page fetched today, one failing optional integrity check, one malformed feed in an
   archived edition. Each has a named owner request logged in `COORDINATION.md`.
4. **Two earlier flags are corroborated, not duplicated.** FLG-037 (same-day short-link
   observations conflict) and FLG-038 + S-20 (robots.txt at a project path is not read by search
   engines; the competing editions are not all noindexed) match this session's independent counts
   exactly — this session independently re-counted noindex coverage per edition and re-fetched
   Google's robots.txt location rule (§3, rows 15–16).
5. **Five owner-only gates still block every revenue decision:** tracking-ID confirmation in
   Associates Central, intended-ASIN confirmation for the five submitted links, gate G-02 (one
   Special Link per product tested in the enrolled workflow), an analytics host for the collector,
   and a Search Console property. Until they close, "which topic next", "which product leads", and
   any optimization claim rest on instinct, which is exactly what the brief says to avoid. They are
   tabbed in §5 with how to close each one.
6. **Suggestions for the owner are in §6** — twenty-three reviewable suggestions (R-S01…R-S23) in
   five groups, written to feed the next design/prompt pass. Nothing in §6 is implemented; the
   project's own rule is that suggestions are chosen first on `/suggestions/` (existing items
   S-01…S-20), and §6 adds QA-derived items in the same spirit.

---

## 1. Method and limits

**What this session did**

- Read the repository registers (`data/*.json`), generators (`tools/build.mjs`,
  `tools/verify.mjs`), gates, workflows, and the generated pages; ran every local gate listed in §2.
- Re-fetched the official sources in §3 from the live web (all fetches 2026-11-20, this session).
- Spot-checked the deployed site at `https://karagemop466-tech.github.io/Affil3/` (front page,
  `/flagged/`, `/suggestions/`, `robots.txt`, `sitemap.xml`, `feed.xml`) and the GitHub Pages API.
- Cross-checked open pull requests only to avoid file-scope collisions; no other session's branch
  was modified.

**What this session did not do (and why)**

- **No owner-account actions:** no Associates Central login exists in this environment, so gate
  G-02, tracking-ID confirmation and intended-ASIN confirmation remain owner steps.
- **No edits to shared machinery:** `tools/build.mjs`, `tools/verify.mjs`, `data/*.json`, the root
  generated pages, `robots.txt`, `sitemap.xml`, `feed.xml`, CSS/assets and `README.md` were left
  untouched because open PRs (#51, #53, #40 and others) already own those files. Findings about
  them are logged as requests in `COORDINATION.md`, not fixed here.
- **No prices, ratings or availability were read or recorded**, per the Program Policies price
  clause confirmed in §3 row 5.
- **The five submitted `link.amazon` short links were not dereferenced in this session.** The
  dated observation rounds in `data/observations/` disagree with each other (FLG-037), and this
  session adds no new observation rather than a sixth conflicting one.

---

## 2. Release state (verified 2026-11-20)

| Check | Command / source | Result |
|---|---|---|
| Root build + publishing gate | `node tools/build.mjs && node tools/verify.mjs` | 40 pages, 13 feed items, 39 sitemap URLs; **4,642 checks passed, 0 failed** |
| Editorial build + gate | `python3 tools/build.py && python3 tools/check_site.py` | 21 pages; PASS (internal links, no currency, no ratings, Associates statement, source ids, sitemap/feed parse) |
| Full project check | `npm run check` | all of the above, exit 0 |
| Disclosure placement | `node tools/disclosure-check.mjs` | 102 published pages; PASS — both statements present and above the fold on every page; no price/rating text |
| Archived editions | `node tools/archive-check.mjs` | 100 archived pages, 3,152 internal refs; PASS |
| Docs-site sitemap | `python3 scripts/build_sitemap.py --check` | OK — 18 pages, all present |
| Docs-site links | `python3 scripts/check_links.py --no-external` | 593 links across 18 pages; no broken internal links |
| Register integrity (optional tool added by PR #63) | `node tools/integrity-check.mjs` | **425 passed, 1 failed** → RR-05 |
| GitHub Pages configuration | GitHub API `repos/.../pages` | source `main` at `/`, HTTPS enforced |
| GitHub Pages deploy | GitHub API `.../pages/builds` | built for `a42e974` (06:53:31Z); later main commits re-deploy — re-check at merge time (completion record) |
| Live front page | fetch `https://karagemop466-tech.github.io/Affil3/` | disclosure strip above `<main>`; five product cards, each `View on Amazon` = `…/dp/<ASIN>?tag=shopnow047c-20` with `rel="sponsored noopener"`; decision-helper section live; **“All five guides →” text live → RR-01** |
| Live Flagged page | fetch `…/flagged/` | FLG-001… render with sources; three rows render wrong source links → RR-02 |
| Register counts (HEAD) | `data/*.json` | 5 products · 13 guides · 24 sources · 39 flags (FLG-001…039, 33 open) · 21 known / 17 open / 12 discovery questions · 20 suggestions · 5 defined events · ledger: 0 rows (empty by design) · `analyticsEndpoint` = `""` (inactive) |
| Edition noindex coverage (this session's count) | `grep -rl noindex` per edition | editorial 21/21 · counter 0/23 · counterwise 1/30 · crisp-index 1/18 · legacy 4/100 · counter-desk 1/32 — matches FLG-038 |

---

## 3. Line-by-line verification against official sources

Every row was fetched **by this session on 2026-11-20**. “Confirmed” means the published claim
matches what the official page says; nothing below is recalled from memory.

| # | Claim as published (where) | Official source | What the source actually says (fetched 2026-11-20) | Result |
|---|---|---|---|---|
| 1 | Site must carry “As an Amazon Associate I earn from qualifying purchases.”, clearly and prominently (disclosure strip + footer, every page; register S01) | [Associates Program Operating Agreement §5](https://affiliate-program.amazon.com/help/operating/agreement) | “You must clearly and prominently state the following … ‘As an Amazon Associate I earn from qualifying purchases.’” Page header: “Updated: October 15, 2025” | **Confirmed**, including the header date recorded in S01’s method |
| 2 | Outbound links must use Amazon’s tagged formats (register S01, FLG-005) | [Operating Agreement §1](https://affiliate-program.amazon.com/help/operating/agreement) | “The links must properly use the special ‘tagged’ link formats we provide … (‘Special Links’).” | **Confirmed** |
| 3 | Associates tag must appear as a URL parameter on every link placed on the site (register S02/S03; the reason every buy button carries `?tag=shopnow047c-20`) | [Program Policies, Participation Requirements §2(a)–(b)](https://affiliate-program.amazon.com/help/operating/policies) | “Special Links must use the Associates ID we have assigned to you.” … “you must include your Associates ID or ‘tag’ (appearing as XXXXX-## …) as a parameter in the URL of each link you place on your Site to an Amazon Site.” | **Confirmed** |
| 4 | Same page, updated date recorded in S02’s method as April 14, 2026 | [Program Policies](https://affiliate-program.amazon.com/help/operating/policies) | Header: “Updated: April 14, 2026.” | **Confirmed** |
| 5 | Site shows no prices because prices/availability may only be shown if Amazon serves the link or data comes via Creators API/PA API (register S03; no-price rule in both gates) | [Program Policies §2(b)](https://affiliate-program.amazon.com/help/operating/policies) | “your Site may only show prices and availability if: (a) we serve the link in which that price and availability data are displayed, or (b) you obtain Product pricing and availability data via Creators API or PA API …” | **Confirmed** |
| 6 | Short-link compliance unresolved: policy restricts shorteners that obscure the Amazon destination (FLG-003) | [Program Policies, Participation Requirements (w)](https://affiliate-program.amazon.com/help/operating/policies) | “You will not use a link shortening service, button, hyperlink or other ad placement in a manner that makes it unclear that you are linking to an Amazon Site.” | **Confirmed verbatim** — and FLG-003’s stance (unresolved, not “invalid”) remains the correct reading: nothing fetched determines how `link.amazon` behaves |
| 7 | No redirect-based click counter (register `events.json` → `why_no_redirect`) | [Program Policies, Participation Requirements (v)](https://affiliate-program.amazon.com/help/operating/policies) | “You will not cloak, hide, spoof, or otherwise obscure the URL of your Site containing Special Links (including by use of Redirecting Links) …” | **Confirmed** — browser-side counting with a direct link is the compliant design |
| 8 | No star ratings / review counts anywhere (both gates) | [Program Policies, Participation Requirements (t)](https://affiliate-program.amazon.com/help/operating/policies) | “You will not display or otherwise use any of our customer reviews or star ratings … unless you have obtained [them] through Creators API or PA API …” | **Confirmed** |
| 9 | No price-tracking functionality (implied by the no-price design) | [Program Policies, Participation Requirements (y)](https://affiliate-program.amazon.com/help/operating/policies) | “Unless otherwise agreed by Amazon, your Site must not have price tracking and/or price alerting functionality.” | **Confirmed** |
| 10 | “24-hour session, or up to 89 days if the item is added to the cart first” (register S17, measurement pages) | [Program Policies, Commission Income Statement §1](https://affiliate-program.amazon.com/help/operating/policies) | Session ends at “24 hours elapse from that click”; cart path: purchase “no later than 89 days after their initial click-through” | **Confirmed** |
| 11 | Disclosure wording “I get commissions for purchases made through links in this post.” (config `ftcDisclosure`, every strip) | [FTC Endorsement Guides: What People Are Asking — Affiliate section](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) | “You could say something like, ‘I get commissions for purchases made through links in this post.’” | **Confirmed verbatim** (the site uses the FTC’s own example sentence) |
| 12 | An “affiliate link” label or a buy button alone is not an adequate disclosure (register S22) | [FTC FAQ — “Is ‘affiliate link’ by itself an adequate disclosure?”](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) | “Consumers might not understand that ‘affiliate link’ means that the person placing the link is getting paid … a ‘buy now’ button would not be adequate.” Also: “‘Paid link’ right next to an affiliate link should be an adequate disclosure.” | **Confirmed** |
| 13 | Disclosure must not live only on a separate page; it must be near the endorsement (above-fold strip design, S07/S08/S22) | [FTC FAQ](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) | “a single disclosure on your home page won’t be sufficient…”; “A hyperlinked disclosure like that is easily avoidable … not clear and conspicuous”; “The closer the disclosure is to your recommendation, the better.” | **Confirmed** — the strip-under-masthead design matches this guidance |
| 14 | Every outbound affiliate link carries `rel="sponsored"` (gate-enforced; register S06) | [Google Search Central — Qualify your outbound links](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links) | “Mark links that are advertisements or paid placements (commonly called paid links) with the `sponsored` value.” (page last updated 2025-12-10) | **Confirmed** |
| 15 | robots.txt for this project site is not read by search engines; meta tags are the alternative (FLG-038 / S-20, source S25) | [Google — How to write and submit a robots.txt file](https://developers.google.com/crawling/docs/robots-txt/create-robots-txt) | “The robots.txt file must be located at the root of the site host … It *cannot* be placed in a subdirectory … If you can’t access your site root, use an alternative blocking method such as `meta` tags.” | **Confirmed first-hand by this session** (S25’s quote is accurate) |
| 16 | ASIN = 10-character Amazon-owned identifier, typically `B0…`, appears after `/dp/` (VERIFICATION.md S-03; contradicts open FLG-012 — see RR-03) | [Amazon (sell.amazon.com) — Understanding ASINs](https://sell.amazon.com/blog/what-is-an-asin) | “a unique 10-character alphanumeric code”; “typically starts with ‘B0,’ or in the case of books begins with a number”; “The ASIN appears after ‘/dp/’” | **Confirmed — and it closes the factual question behind FLG-012**: an Amazon-owned definitional page does exist |
| 17 | Doneness temperatures in thermometer guides: beef/pork/veal/lamb 145 °F + 3 min rest; ground meats 160 °F; all poultry & ground poultry 165 °F (register S10) | [USDA FSIS — Safe Minimum Internal Temperature Chart](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart) | “Beef, Pork, Veal and Lamb Steaks, Chops and Roasts — 145 degrees F … rest for at least 3 minutes”; “Ground Meats — 160 degrees F”; “All Poultry … — 165 degrees F”. Page “Last Updated: Apr 14, 2025” | **Confirmed** |

**Not re-fetched in this pass — links provided for manual review; no claim is made about them here:**

- Manufacturer specification pages used for product rows: [Chefman 6 Qt dual-window](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) · [Chefman 8 Qt Hi-Fry (RJ38-8T-BLACK)](https://chefman.com/products/turbofry-8-qt-air-fryer-w-high-fry) · [Chefman RJ38-SQSS-8T](https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1) · [Emeril Lagasse 26 QT](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) · [CHEF iQ Sense](https://chefiq.com/products/iq-sense) · [CHEF iQ FAQ](https://chefiq.com/pages/new-iq-sense-faq) · [ThermoMaven F1 Ace](https://www.thermomaven.com/products/f1-ace)
- Amazon detail pages (identity only; prices/ratings deliberately not recorded): `/dp/B0CDY277D3`, `/dp/B09B7SB46R`, `/dp/B08DKYBTPH`, `/dp/B0DHZTCNR5`, `/dp/B0DZFD6R9Z`
- Associates help pages carried as excerpt-grade sources: [build a simple text link (S18)](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) · [application review process (S19)](https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM) · [USDA food thermometers (S20)](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/food-thermometers) · [FTC full Endorsement Guides (16 CFR 255)](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255) · [Google spam policies (S09)](https://developers.google.com/search/docs/essentials/spam-policies) · [Google outbound links page](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links)

---

## 4. Irregularities found (RR-01 … RR-07)

Non-blocking, published here for review per the brief. Each “request” is logged in
`COORDINATION.md` under this session’s board; **this session edited none of the listed files.**

| ID | Severity | Finding | Evidence | Requested from |
|---|---|---|---|---|
| **RR-01** | medium (reader-visible) | **Stale guide counts.** The front page says “All five guides →” and the workflow page says “the site has five original guides”, but the register and `/guides/` carry **13**. FLG-007 repeats “The site has 5 guides”. The workflow text also draws a conclusion (“below the at-least-10-posts rule of thumb”) that the current count no longer supports. | `tools/build.mjs:372` and `:864` (text sources), `index.html:175` (committed output), `data/flags.json` FLG-007 detail; live fetch of `/` on 2026-11-20 shows the sentence | Owner of `tools/build.mjs` + `data/flags.json` (sessions with open PRs #51/#40 on those files): derive the count from `data/guides.json` and rebuild |
| **RR-02** | high (trust) | **Four Flagged-page rows cite source IDs that point at the wrong pages.** In the current root numbering, S11/S12/S13 are manufacturer pages, but flag texts written under an older numbering resolve them as policy/help pages. Live page renders: FLG-001 lists `[S12] = chefman.com 8 Qt page` beside an ASIN-format claim; FLG-003 lists `[S13] = emerileveryday.com` beside “Amazon’s Associates help (S13)”; FLG-006/FLG-007 list `[S11] = chefman.com 6 Qt page` beside Associates-help claims (the help page exists as S19). FLG-001’s sources array also includes S12 for a claim S12 does not support. (FLG-026’s S12 citation is correct — it deliberately names the wrong-comparison page.) | `data/flags.json` FLG-001/003/006/007 `sources` + detail text; live `/flagged/` render | Owner of `data/flags.json`: re-cite FLG-001→(S04,S05,+ASIN source), FLG-003→(S02,S05, OneLink help), FLG-006/007→(S19) and rebuild |
| **RR-03** | medium (register vs docs contradiction) | **FLG-012 says no Amazon-owned ASIN definition was located — one exists.** `data/flags.json` FLG-012 is open with that text (and FLG-001 repeats it), while `VERIFICATION.md` marks FLG-012 “Closed” citing an Amazon-owned page, and README says the same. This session fetched the page: Amazon’s own “Understanding ASINs” defines the 10-character, typically-`B0`, after-`/dp/` format. The site now publishes two contradictory states about the same question. | `data/flags.json` FLG-012 vs `VERIFICATION.md:112,150` vs `README.md` “Find worth knowing”; fetch result in §3 row 16 | Owner of `data/flags.json`: close FLG-012 with the Amazon-owned URL, fix FLG-001’s sentence (interacts with RR-02) |
| **RR-04** | low | **Stale count inside FLG-003:** “None of the **four** observed product redirects contains a tag parameter” — the register carries five observed rows. | `data/flags.json` FLG-003 detail | Owner of `data/flags.json` (same pass as RR-02) |
| **RR-05** | medium (a red check exists) | **`node tools/integrity-check.mjs` fails 1 of 426:** open flag FLG-030 has an empty `manual_step` (and no resolution/action). The tool (added by PR #63) is not wired into `package.json` or CI, so the failure is latent — but it is a failing check in the tree, and the brief says failing checks get fixed. Session 478e6577 recorded the same finding in its board; the flag itself is still unfixed as of `c0bee1e`. | `node tools/integrity-check.mjs` → “425 passed, 1 failed … FLG-030”; `data/flags.json` FLG-030 | Owner of `data/flags.json` (add manual_step or mark resolved); owner of the tool/CI (add to `npm run check` or a workflow) |
| **RR-06** | low | **Self-contradictory source statuses:** S15, S18, S19, S20 are stored as `status: "verified (excerpt; re-check manually)"` — “verified” and “excerpt” cannot both be the grade. The site’s own note defines three grades (fetched/excerpt/observed). | `data/sources.json` rows S15/S18/S19/S20 | Owner of `data/sources.json`: normalize to `excerpt` (manual re-check still pending) |
| **RR-07** | low (isolated surface) | **`/counter/feed.xml` is not well-formed XML** — unescaped `&` in `<title>Crisp & Counter …</title>` (line 4). Any reader of that edition’s feed gets a parse error. Root `feed.xml` parses (13 items) and is unaffected. | `python3 -c "import xml.etree.ElementTree as E; E.parse('counter/feed.xml')"` → ParseError line 4 col 16 | Owner of the `counter/` edition: escape `&amp;` in the generator and rebuild |

**Corroborated (already flagged by other sessions — no duplicate created):**

- **FLG-037** — same-day short-link rounds disagree (product page vs Amazon home page). This
  session did not add a sixth round; owner signed-in check + G-02 remain the only settlement.
- **FLG-038 / S-20** — robots.txt at `/Affil3/` is not read from a project path, and the
  competing editions are mostly un-noindexed. This session independently re-counted noindex
  coverage (§2 table, matches FLG-038 exactly) and re-fetched Google’s location rule (§3 row 15).
  Decision S-20 is waiting on the owner.

---

## 5. Questions that must be answered before decisions can be reasonably made

Nothing below can be answered from the repository; each needs a person, an account, or a clock.
These are the inputs any revenue/optimization decision is missing.

| # | Question | What the repo already knows | What is missing | How to close it | Decisions it blocks |
|---|---|---|---|---|---|
| DQ-1 | Is `shopnow047c-20` a live tracking ID on the enrolled Associates account, and is this site a declared channel? | The ID is used in every rendered link; gates enforce the string; register marks it **unverified** (FLG-001/006 family) | Associates Central screenshots/status | Sign in → Account Settings → Tracking IDs; check declared site list (10 min) | Any claim that clicks can earn; G-02; scaling links |
| DQ-2 | Which product was *intended* for each submitted short link? | Observed destinations for all five (separate `observed.*` fields, dated rounds, conflicting per FLG-037) | The owner’s intent: `intended_asin`, `official_listing_url`, `confirmation_date`, `confirmation_source` | Owner opens each link signed-in, compares with intended product, fills the four fields (15 min) | Closing FLG-001/002/031/037; product-intent record completion; trusting the shelf |
| DQ-3 | Does one tagged Special Link per product track correctly? | Links follow the policy format confirmed in §3 row 3 | Destination + tracking-report proof from the enrolled workflow | Gate G-02: generate in Associates Central, click, check report, five times | Scaling links; enabling revenue claims; S-02 choice |
| DQ-4 | Where will the analytics collector run, and who reads it? | `tools/collector.mjs` ships; `analyticsEndpoint=""`; five-event schema defined; ledger empty by design | A hosting choice (S-03 options A–D) + owner | Owner picks S-03 option, deploys, sets `data/config.json`, rebuilds | Turning on measurement; “choose next topic from measured queries”; campaign ledger |
| DQ-5 | Is the site verified in Search Console, and is `sitemap.xml` submitted? | Sitemap generated (39 URLs); robots/Sitemap line cannot be discovered at a project path (FLG-038) | Google account + property | URL-prefix property on `/Affil3/`, verify, submit sitemap (30 min) | Query-driven editorial choices; measuring impressions; FLG-013 |
| DQ-6 | Which edition is the one search engines should rank? | Root is the intended single site; six other editions exist; noindex coverage is partial (FLG-038) | One choice on S-20 (A/B/C) | Owner answers “S-20 B” (or A/C) on `/suggestions/` | “Make it findable” goal; duplicate-content risk |
| DQ-7 | Is there a named author/editor willing to take the byline? | Team byline, flagged as a weakness (S-08) | A person + bio + contact | Owner chooses S-08 option B and supplies identity | Trust/E-E-A-T work; outreach; publication depth |
| DQ-8 | What is the confirmed wattage/size for Chefman RJ38-SQSS-8T, and the 450 °F Hi-Fry story? | Maker says 1700 W / 15.4×12.6×13.5 in; listing says 1000 W / 12.75×13.5×10 in; title says 450 °F, bullet+maker say 400 °F (FLG-026/027) | A written answer from Chefman support or the model’s user guide | Email support / read linked manual; record with date | Publishing those cells; “conflict” copy on the P03 page |
| DQ-9 | Which content claim is “the site’s position” on P04’s identity (ThermoMaven listing says “1 Sec Professional”, maker page is “F1 Ace”)? | Family specs published with a stated caveat (FLG-025) | Model field from the listing (signed-in) | Owner reads product details on Amazon; closes FLG-025 | Promoting family figures to confirmed specs |
| DQ-10 | What does the first month of data say? | Nothing yet — no endpoint, no Search Console, ledger has 0 rows by design | Real sessions/clicks/orders from authorized first-party reports | DQ-4 + DQ-5, then ≥30 days | Topic selection, product lead choice, any “optimize the campaign” work |

---

## 6. Suggestions for review (nothing here is implemented)

Additive to the existing decision board at `/suggestions/` (S-01…S-20). Reply format is the same:
pick an ID and an option. These are QA-derived: each answers something §3–§5 exposed.

### A. Read like a shop, not an audit (design / front page)

| ID | Suggestion | Options (tradeoff) | Recommend |
|---|---|---|---|
| R-S01 | Front-page truthfulness pass | **A.** Derive every count from the register (guides, categories, “updated” date) and add a gate check that front-page numbers match `data/*.json` · **B.** Hand-edit the sentence (returns next build) | **A** (fixes RR-01 permanently) |
| R-S02 | Merchandising order on `/` | **A.** current: hero → shortlist → decision helper → guides · **B.** hero → decision helper (“pick by how you cook”) → shortlist → guides · **C.** hero → seasonal block → shortlist | **B**: it answers “which one for me?” before asking for a click |
| R-S03 | Product-card specificity (anti-slop lever) | **A.** keep current ledes · **B.** require each card to carry one measurable constraint (footprint in inches, batch size, probe range) drawn from the spec table | **B** — concrete numbers are the cheapest signal that a human checked something |
| R-S04 | Imagery toward real product | **A.** keep labelled illustrations (current, S-07) · **B.** Amazon-approved image service for hero images only · **C.** photograph owned units | Follow S-07’s recommendation (B for heroes) once links are G-02-tested |

### B. Make it findable (SEO)

| ID | Suggestion | Options | Recommend |
|---|---|---|---|
| R-S05 | Execute S-20 (crawl control) — see §4/FLG-038 | existing options A/B/C on `/suggestions/` | **B** (noindex everywhere non-root) — smallest reversible step that actually controls indexing at a project path |
| R-S06 | Manual sitemap submission the day GSC opens | **A.** submit root sitemap only · **B.** also submit after each ≥5-page batch | **A**, then quarterly |
| R-S07 | Cluster internal linking per category | **A.** keep current related-guide links · **B.** add a “hub” paragraph at the top of each category page linking every guide in that cluster + JSON-LD `BreadcrumbList` | **B** — clusters are named in the brief and half-built already |
| R-S08 | Wire `tools/integrity-check.mjs` into `npm run check` + CI | **A.** wire it (fails on RR-05 until fixed) · **B.** leave optional | **A after** the FLG-030 fix lands, so CI stays green |
| R-S09 | Resolve duplicate feed surfaces | **A.** fix `counter/feed.xml` (RR-07) · **B.** remove feed links from archived editions | **A** (one-line escape fix) |

### C. Measurement before more writing (brief’s ordering)

| ID | Suggestion | Options | Recommend |
|---|---|---|---|
| R-S10 | Choose S-03 (analytics host) this week | existing options A–D on `/suggestions/` | **B** (serverless function running `tools/collector.mjs`); until then every topic choice is a guess (DQ-10) |
| R-S11 | Define the ledger import ritual now | **A.** monthly: pull Associates report → append authorized rows (timestamp, source, channel, sessions, clicks, orders only) · **B.** automate later | **A** — automation before authorized data exists would fabricate the first rows |
| R-S12 | Event → decision mapping page | **A.** document which of the five events answers which open question · **B.** skip until data exists | **A** — cheap now, prevents metric theatre later |
| R-S13 | Publishing cadence = choose S-05 | existing options A–C | **A** (fortnightly), but only after DQ-4/DQ-5 so each issue can be *measured* |

### D. Trust and compliance posture

| ID | Suggestion | Options | Recommend |
|---|---|---|---|
| R-S14 | Fix the four wrong source citations (RR-02) + close FLG-012 (RR-03) | **A.** one data pass by the flags owner · **B.** leave for the next audit | **A** — wrong links on the Flagged page undermine the page whose job is trust |
| R-S15 | Byline (feeds DQ-7 / S-08) | follow S-08 | **B** as soon as a real person agrees |
| R-S16 | House-style gate (feeds the “not AI slop” instruction) | follow S-19 | **B** — turn the design-brief’s do/don’t list into gate rules |
| R-S17 | Disclosure stress-test each quarter | **A.** re-run disclosure gate + re-read FTC/Associates pages after any policy update (policies updated 2026-04-14; agreement 2025-10-15 — both fetched today) · **B.** only when pages change | **A** |

### E. Growth (only after C and D)

| ID | Suggestion | Options | Recommend |
|---|---|---|---|
| R-S18 | Expand shelf per S-09 | follow S-09 (deepen categories with maker-page-verifiable products) | **B**, one category at a time |
| R-S19 | Seasonal hooks | **A.** keep the holiday thermometer block · **B.** add a rotating “occasion” slot driven by calendar + measured queries | **B** once DQ-5 supplies queries |
| R-S20 | Reader capture | follow S-06 | **B** after ≥3 returning guides |
| R-S21 | Distribution before traffic exists | **A.** RSS + one external post per guide · **B.** wait for search | **A** — GSC is not a launch strategy |
| R-S22 | Compare-page as linkable asset | **A.** keep comparison table static · **B.** add “download as CSV/print” affordance + `FAQPage` JSON-LD on guide pages | **B** — zero-risk structured data, real utility |
| R-S23 | Next-prompt feedstock | **A.** brief the next design pass from this document §4–§6 + `/questions/` + `/suggestions/` · **B.** write a fresh brief from scratch | **A** — the open items are already ID’d, owned and sourced |

---

## 7. Source links (manual review index)

**Policy / platform (fetched by this session, 2026-11-20):**
[Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) ·
[Program Policies](https://affiliate-program.amazon.com/help/operating/policies) ·
[FTC Endorsement Guides FAQ](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) ·
[16 CFR Part 255](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255) ·
[Google — qualify outbound links](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links) ·
[Google — robots.txt location rule](https://developers.google.com/crawling/docs/robots-txt/create-robots-txt) ·
[Google — spam policies](https://developers.google.com/search/docs/essentials/spam-policies) ·
[Amazon — Understanding ASINs](https://sell.amazon.com/blog/what-is-an-asin) ·
[Amazon Ads — ASINs introduction](https://advertising.amazon.com/library/guides/asins-introduction)

**Safety data:** [USDA FSIS temperature chart](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart) · [USDA FSIS food thermometers](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/food-thermometers)

**Live site:** [front page](https://karagemop466-tech.github.io/Affil3/) · [flagged](https://karagemop466-tech.github.io/Affil3/flagged/) · [suggestions](https://karagemop466-tech.github.io/Affil3/suggestions/) · [questions](https://karagemop466-tech.github.io/Affil3/questions/) · [sources](https://karagemop466-tech.github.io/Affil3/sources/) · [measurement](https://karagemop466-tech.github.io/Affil3/measurement/) · [sitemap](https://karagemop466-tech.github.io/Affil3/sitemap.xml) · [feed](https://karagemop466-tech.github.io/Affil3/feed.xml)

**Repository evidence:** `data/sources.json`, `data/flags.json`, `data/observations/*`,
`tools/verify.mjs`, `tools/integrity-check.mjs`, `VERIFICATION.md`, `COORDINATION.md`
(session boards for FLG-037/FLG-038, S-19/S-20).

---

*No value in this document was inferred. Where a value could not be confirmed from an official
source in this pass, it is absent from this document or listed under “Not re-fetched”. Flagged
irregularities do not block publication; they are published here and on `/flagged/` for review.*
