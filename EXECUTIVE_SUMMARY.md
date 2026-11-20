# Affil3 — executive summary

**Updated:** 2026-11-20 by session `arena-43565031-affil3` (reconciled with `main`'s generated-site architecture)
**Live site:** https://karagemop466-tech.github.io/Affil3/ — root publication, with `/editorial/` as the register appendix
**Sources, quoted with retrieval dates:** [`docs/OFFICIAL-SOURCES.md`](docs/OFFICIAL-SOURCES.md)

> Two other executive summaries exist in the repo (`EXECUTIVE-SUMMARY.md`, `EXECUTIVE_SUMMARY-6249757a.md`)
> from other sessions. They are left untouched here on purpose; consolidating them into one page is logged
> in `COORDINATION.md` and raised as an open question (`Q-17`) rather than settled unilaterally.

---

## 1. The finding that governs everything else

**The five product links supplied for this project do not identify five products.**

| Submitted | Reached on 2026-11-20 |
|---|---|
| `link.amazon/B04G1MEwY` | ASIN **B0CDY277D3** — not the submitted token |
| `link.amazon/B02NbDxp3` | ASIN **B09B7SB46R** — not the submitted token |
| `link.amazon/B00hJ57DV` | ASIN **B08DKYBTPH** — not the submitted token |
| `link.amazon/B0c8moW59` | Amazon **checkpoint page**, no product |
| `link.amazon/B0f3GKalj` | ASIN **B0DZFD6R9Z**, in a **different browse node** (meat thermometers, not air fryers) |

Three properties of that evidence, each independently checkable:

1. **Every token is 9 characters**; every real ASIN reached in the same session is 10. A dropped
   character during a copy-paste is the simplest explanation, and it is an input error, not a campaign
   failure.
2. **Every resolved URL carried `plpRedirect=mhFallback`** — a router saying *I did not find that item*.
   The register marks these rows `identity_status: resolved` on the strength of title and manufacturer
   agreement, which identifies the page reached but cannot prove it is the page intended. Raised as
   `FLG-023`.
3. **Two sessions got different answers for the same links.** An earlier record has `B00hJ57DV` hitting
   the checkpoint; on this retrieval `B00hJ57DV` resolved and `B0c8moW59` hit the checkpoint. Both stand.
   That is direct evidence the destination varies by session or timing, so re-verification must append
   attempts rather than overwrite rows (`FLG-024`).

What is **not** claimed anywhere: that the short links are invalid or non-compliant. Verified facts only —
no `tag` parameter present, destination ≠ token. Compliance is Amazon's determination, per the standing
instruction in the brief.

## 2. Rules that settle design questions outright

Read verbatim from the Associates Program Operating Agreement (updated 2025-10-15), the Associates
Program Policies (updated 2026-04-14), and the FTC's Endorsement Guides page. Each is now a row in the
compliance register with its quote (`R13`–`R18`) and, where it is unenforced, a flag:

| Rule | Consequence for this site |
|---|---|
| §2(b): a site may show price/availability only if Amazon serves it or Creators/PA API supplies it | **No prices or star ratings anywhere**, enforced by `tools/check_site.py`. "Check current price" links instead |
| §2(b): tag must appear as `XXXXX-##` in every outbound link | Until the account is confirmed, the site publishes **no buy links**; the assertion passes on an empty set and is recorded as `blocked`, not `met` |
| §2(b): product lists require additional original content relevant to the link | A links-only category page is not allowed to be the product; hubs carry editorial body copy |
| §2(b): "Under no circumstances may you associate any sub-tag … with a specific end user" | The shipped collector must stay aggregate. Event fields (path, referrer_host, product_id, destination_host) comply today; the constraint on future joins is flagged (`FLG-025`, `Q-14`) |
| §2(b): remove promotion references as soon as a promotion ends | Currently satisfied by publishing no offers at all. Needs an `expires_on` mechanism before any deal page ships (`R16` open, `S-14`) |
| §1: "no representation … regarding the amount of traffic or commission income you can expect" | The site publishes **no** revenue forecast, conversion score, or rate. The ledger ships empty by design |
| Participation Requirements §1: original content, public at the address in the application, "significant commentary, analysis, or transformation" | Thin aggregation is an **eligibility** failure, not a style preference — the formal answer to "make it not read like AI slop" |
| Statement is Agreement **§5**, and §6 deems its violation a material breach | Citation verified against the text rather than trusted; recorded as a resolved flag (`FLG-029`) |
| Session = 24 hours; cart path = **89 days** | Any attribution figure must use these, not the "90 days" repeated online (`FLG-027`) |

## 3. What this branch changed

- **Folded evidence into the live registers**, not into a parallel site: `data/flags.json` (7 new flags,
  `FLG-023`…`FLG-029`, each with sources, a manual step, and a dated observation),
  `data/questions.json` (+4 known, +4 unknown, +4 discovery routes), `data/suggestions.json`
  (`S-13`…`S-16`), `data/register/compliance.json` (`R13`…`R18` with verbatim quotes).
- **Rebuilt both publications** from that data (`tools/build.mjs` for the root site, `tools/build.py` for
  `/editorial/`), which also corrected a stale generated stylesheet (`editorial/assets/site.css`).
- **`docs/OFFICIAL-SOURCES.md`** — every source with the exact wording relied on, document version dates,
  retrieval dates, the live-evidence table with reproduction links, and a section for what could not be
  verified. This is the manual-review layer the brief asks for.
- **`evidence/43565031/`** — this session's raw registers (link verification with control tests, a claims
  ledger, an open-questions register, an editorial-cluster plan). Kept as evidence and as the source the
  flags trace back to, deliberately outside `data/` so it is never mistaken for build input.
- **Removed this session's duplicate root pages** (`shop.html`, `suggestions.html`, `questions.html`,
  `verification.html`) and this session's competing validator/builder scripts and CI workflow, because
  `main` already publishes those surfaces. Publishing a second shape of the same site is the one change
  that would actively hurt indexation.

## 4. What is still missing, and only the owner can supply it

1. **Product identity** — ten characters per product, from the listing while signed in (`Q-01`, `Q-15`).
2. **Associates account state** — does `shopnow047c-20` exist, is this Pages URL declared in the
   application, is the account accepted (`Q-01`, `FLG-006`).
3. **API access** — without Creators/PA API, no lawful price, image, or automated product data, which
   caps the "AI-powered platform" half of the brief (`Q-04`).
4. **A measurement receiver** — GitHub Pages is static, so clicks are instrumented and collected nowhere
   today; and one collector rule is a hard constraint, not an option (`Q-14`).
5. **Search Console** — no verification record exists, so topic selection is still unmeasured (`Q-08`).
6. **An integration decision** — two publishers, two exec summaries, twelve session branches. This is the
   structural risk to the site, not a cosmetic one (`Q-17`, `FLG-028`).

## 5. Recommended path

Take **one** verified correction first: resolve the five products and regenerate the tagged links, because
every other improvement inherits its honesty from that step. Then, in order: `S-16` (make the CI assertion
point at `editorial/` so the site cannot silently ship stale output), `S-15` (quote + version date on every
compliance source, so the site remains auditable after Amazon edits a page), `S-13` (assert the aggregate
measurement boundary before a receiver goes live), `S-14` (an `expires_on` field before any deal content).

Deliberately **not** recommended now: scraping product data (the Commission Income Statement disqualifies
events generated by "bots or automated software", and the fallback behaviour observed above shows why
scraped fields rot quietly), and publishing price or rating numbers for the same reason.

## 6. Manual review index

| To check | Where |
|---|---|
| Verbatim policy wording, section numbers, retrieval dates | [`docs/OFFICIAL-SOURCES.md`](docs/OFFICIAL-SOURCES.md) §A–§B |
| The five links, controls, and reproduction URLs | `docs/OFFICIAL-SOURCES.md` §C, then [`/flagged/`](https://karagemop466-tech.github.io/Affil3/flagged/) |
| Rules the site meets, blocks on, or merely avoids | `/editorial/dashboard/` (rule-by-rule status) and `/editorial/disclosure/` (the quotes beside the wording they govern) |
| Every unresolved item with its closing step | [`/questions/`](https://karagemop466-tech.github.io/Affil3/questions/), [`/suggestions/`](https://karagemop466-tech.github.io/Affil3/suggestions/) |
| Session claims, conflicts, handoffs | [`COORDINATION.md`](COORDINATION.md) |
