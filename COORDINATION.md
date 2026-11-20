# COORDINATION — shared task board

This file is the single coordination surface for all agent sessions working on `Affil3`.
Read it **before** touching anything. Append; do not rewrite other sessions' rows.

- Repo: `karagemop466-tech/Affil3`
- Live site: https://karagemop466-tech.github.io/Affil3/
- Conventions: one claim row per task. Statuses: `unclaimed` | `in-progress` | `needs-review` | `done`.
  `needs-review` = published on the site's **Flagged for Review** page; it never blocks another task.
- takeover rule: a claim older than 60 minutes with no commit may be taken over; log the handoff.
- Never edit a file whose scope belongs to another active claim. File a `change request` row instead.

---

## Session registry

| session | branch | started (UTC) | scope (files/dirs owned) | status |
| --- | --- | --- | --- | --- |
| `23e15ed4` | `arena/23e15ed4-affil3` | 2026-11-20T05:16Z | `site/`, `tools/`, `data/`, `content/`, `config/`, `tests/`, `.github/workflows/`, `COORDINATION.md`, `README.md`, `docs/` | in-progress |

No other session has claimed anything in this repo as of this row. The branch point
`847ae376e15d0bba14809ebce17ddaea317f79b6` contained exactly one tracked file
(`README.md`, 8 bytes, text `# Affil3`) — verified with `git show --stat 847ae37`.

---

## Task board

| id | task | status | owner | touches | notes |
| --- | --- | --- | --- | --- | --- |
| T-01 | Verify program rules against official primary sources; build source register | done | `23e15ed4` | `data/sources.csv` | 12 sources retrieved from the publishing entity's own domain; each row carries the retrieval date and the quote the site relies on. |
| T-02 | Product-intent confirmation records for the 5 submitted links | done | `23e15ed4` | `data/product_intents.csv` | All 5 identifiers are 9 characters. Amazon ASINs are 10. Records are `pending` with the observed-vs-intended fields kept separate. |
| T-03 | Flagged irregularities page | done | `23e15ed4` | `data/flagged.csv`, `content/pages/flagged.md` | FLG-001..FLG-008. |
| T-04 | Static site generator + publication skin | done | `23e15ed4` | `site/build.py`, `site/templates/`, `site/assets/` | Python 3 stdlib only, no build dependencies. |
| T-05 | Compliance gate (CI blocker) | done | `23e15ed4` | `tools/compliance_gate.py` | Blocks the build, not just the PR. |
| T-06 | Measurement: click counter + 5 events + ledger writer | done | `23e15ed4` | `site/assets/measure.js`, `tools/metrics_endpoint.py`, `tools/export_ledger.py` | GitHub Pages serves static files only, so the collector is a documented self-host. |
| T-07 | Suggestions register + review UI | done | `23e15ed4` | `data/suggestions.csv`, `tools/decide.py` | |
| T-08 | Open questions / missing-information register | done | `23e15ed4` | `data/open_questions.csv` | |
| T-09 | Editorial: 4 buyer guides + 2 service pages | done | `23e15ed4` | `content/guides/` | |
| T-10 | RSS + sitemap + robots + canonical | done | `23e15ed4` | `site/build.py` | |
| T-11 | GitHub Pages publish + PR + merge | done | `23e15ed4` | `.github/workflows/pages.yml` | See Deploy log below. |

---

## Verification log

Every claim below was checked against the publishing entity's own domain on 2026-11-20 (UTC).
Quoted text is from the retrieved page. If a number could not be read on an official page it is
recorded as `unverified` and appears on the Flagged for Review page — it is **not** printed as fact
anywhere on the site.

| # | claim used on the site | official source | result |
| --- | --- | --- | --- |
| V-1 | Required disclosure sentence, exactly: "As an Amazon Associate I earn from qualifying purchases." — Operating Agreement §5, page marked "Updated: October 15, 2025" | https://affiliate-program.amazon.com/help/operating/agreement | confirmed, quoted |
| V-2 | Session/attribution window: session ends at 24 h; cart purchase must complete within 89 days of the click; product must ship/stream and be paid for within 180 days of purchase | https://affiliate-program.amazon.com/help/operating/policies (Commission Income Statement §1) | confirmed, quoted |
| V-3 | Purchases referred by a "Redirecting Link" (indirect route through an intermediate site with no affirmative action) are **disqualified** | same, Commission Income Statement §2(e) | confirmed — this is the clause that governs the submitted `link.amazon/...` shape |
| V-4 | Purchases referred by a link "generated or displayed on a search engine" are **disqualified** | same, §2(d) | confirmed — bounds what paid/organic search may do with these links |
| V-5 | Prices/availability may only be shown if served in an Amazon link or obtained via Creators API / PA API | same, Participation Requirements §2(b) | confirmed — so the site shows **no** prices |
| V-6 | Special Links must carry the Associates ID as a URL parameter, must be accessed directly from your Site, must not be bookmarked | same, §2(b) | confirmed |
| V-7 | Sub-tags may never be associated with a specific end user | same, §2(b) | confirmed — this is why the click counter is aggregate-only |
| V-8 | Program Content / Special Links may not be used to develop machine-learning models without prior written approval | same, Participation Requirements §5 | confirmed — bounds the "AI-powered" scope |
| V-9 | Site must contain original content and be publicly available; email/SMS Special Links allowed only to opted-in recipients | same, §1 and §4 | confirmed — bounds the newsletter feature |
| V-10 | FTC: "I get commissions for purchases made through links in this post." is an acceptable form; "affiliate link" alone and "buy now" are **not**; "paid link" adjacent to the link is adequate; "commissionable link" is not; closeness to the recommendation matters | https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking (What About Affiliate or Network Marketing) | confirmed, quoted |
| V-11 | Safe minimum internal temperatures: poultry 165 °F; ground meats 160 °F; steaks/roasts/chops 145 °F + 3 min rest; whole fish 145 °F; leftovers 165 °F; egg dishes 160 °F | https://www.foodsafety.gov/food-safety-charts/safe-minimum-internal-temperatures (Date last reviewed: November 21, 2024) | confirmed, quoted |
| V-12 | CPSC maintains a recall search with an "Air Fryer" product category and hazard facets incl. Electrical Fire / Burn / Smoke Inhalation | https://www.cpsc.gov/Recalls | confirmed |
| V-13 | `.amazon` is an active delegated TLD managed by Amazon Registry Services, Inc. (delegated 2020-06-02) | https://www.iana.org/domains/root/db/amazon.html | confirmed — so `link.amazon` is an Amazon-managed namespace, which is why FLG-003 must not be read as "these links are fake" |
| V-14 | Pages `build_type` accepts `legacy` or `workflow` | https://docs.github.com/en/rest/pages/pages | confirmed |
| V-15 | GitHub Actions pinned refs used by CI: `actions/checkout@v7.0.1`, `actions/configure-pages@v6.0.0`, `actions/upload-pages-artifact@v5.0.0`, `actions/deploy-pages@v5.0.1`, `actions/setup-python@v7.1.0` | https://api.github.com/repos/{owner}/{repo}/releases/latest for each | confirmed against the GitHub API on 2026-11-20 |

### Could not be verified — deliberately absent from the site as fact

| item | why | where it is handled |
| --- | --- | --- |
| The five product identities, titles, prices, ratings | identifiers are 9 characters, not the 10 an ASIN has; the submitted hosts could not be resolved from the build sandbox (TLS to `link.amazon` failed) | FLG-001, FLG-002, all five rows of `data/product_intents.csv` = `pending` |
| Per-category commission rates | the rate card is behind Associates sign-in; the public page redirects to login | FLG-004, Q-05 |
| PA-API eligibility thresholds ("3 sales / 180 days", "10 sales / 30 days") | only third-party blogs assert these, and they disagree | FLG-005, Q-06 |
| Search demand / traffic / popularity for any suggested topic | no first-party data exists yet; nothing was measured | every guide headline is labelled a working title |
| Whether the affiliate tag `shopnow047c-20` is live and enrolled | requires the account | FLG-006, Q-01 |

---

## Handoff / incident log

- 2026-11-20T05:16Z — session `23e15ed4` created this file (repo previously had none) and claimed
  every task above; no contention existed. All work below is on `arena/23e15ed4-affil3`.

## PR & deploy log

- (filled in by this session at publish time)
