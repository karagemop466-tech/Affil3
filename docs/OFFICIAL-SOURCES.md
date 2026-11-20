# Official sources, retrieved 2026-11-20 — for manual review

Every rule this project publishes a decision on is listed here with the exact page to check and the
date it was fetched. Nothing in this file paraphrases: the "quoted" blocks are verbatim, and where
something could not be confirmed it says so instead of filling the gap.

## A. Documents retrieved and quoted (Amazon, official)

| # | Source | URL | Document version | Retrieved | Used for |
|---|---|---|---|---|---|
| A1 | Associates Program Operating Agreement | https://affiliate-program.amazon.com/help/operating/agreement | Updated **October 15, 2025** | 2026-11-20 | §1 Special Links definition, Program Content definition; §2 compliance and cease-payment clause |
| A2 | Associates Program Policies (Commission Income Statement; Participation Requirements) | https://affiliate-program.amazon.com/help/operating/policies | Updated **April 14, 2026** | 2026-11-20 | §1 session/attribution windows; §2(b) link requirements, price display, product lists, promotions expiry, sub-tag prohibition; §6 payment terms and minimums; Participation Requirements §1 enrolment and suitability |

Quoted in full in this session's register `evidence/43565031/claims.json` (rows `CLM-01`…`CLM-17`);
the six rules that changed a design decision are folded into `data/register/compliance.json` as
`R13`–`R18` so they render on the published site.

## B. Documents retrieved and quoted (US Government, official)

| # | Source | URL | Retrieved | Used for |
|---|---|---|---|---|
| B1 | FTC's Endorsement Guides: What People Are Asking | https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking | 2026-11-20 | material-connection disclosure standard; 2023 revision adding a definition of "clearly and conspicuously"; explicit statement that staff guidance is not a safe harbour (CLM-16) |
| B2 | 16 CFR Part 255 (Endorsement Guides) — the Guides B1 refers to | https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255 | **not fetched in this session** | cited only because B1 links to it; not relied on for any wording |

## C. Live evidence about the submitted links

Retrieved by this session with the workspace fetch tool, anonymous, no cookies, no Associates
credentials. Full records with timestamps in [`evidence/43565031/link-verification.json`](../evidence/43565031/link-verification.json),
summarised on the published site at `/flagged/` (`FLG-023`…`FLG-029`) and `/questions/`.

| # | Request | What came back | Review link |
|---|---|---|---|
| C1 | `https://link.amazon/B04G1MEwY` | product page for ASIN **B0CDY277D3**, `plpRedirect=mhFallback`, node 17659096011 (Air Fryers) | https://www.amazon.com/dp/B0CDY277D3 |
| C2 | `https://link.amazon/B02NbDxp3` | product page for ASIN **B09B7SB46R**, same fallback marker, same node | https://www.amazon.com/dp/B09B7SB46R |
| C3 | `https://link.amazon/B00hJ57DV` | product page for ASIN **B08DKYBTPH**, same fallback marker, same node | https://www.amazon.com/dp/B08DKYBTPH |
| C4 | `https://link.amazon/B0c8moW59` | Amazon **"Continue shopping" checkpoint** page; no product | https://link.amazon/B0c8moW59 |
| C5 | `https://link.amazon/B0f3GKalj` | product page for ASIN **B0DZFD6R9Z**, same fallback marker, `channelId=500`, node 289810 (Meat thermometers) | https://www.amazon.com/dp/B0DZFD6R9Z |
| C6 | control: `https://www.amazon.com/dp/B00hJ57DV` | no product page returned (non-success) | — |
| C7 | control: `https://link.amazon/ZZ9ZZ9ZZZ9` | no page the client could read (non-success) | — |
| C8 | control: repeat of C1 | byte-identical response, identical session id ⇒ **served from cache**; does not test redirect stability | — |

Recorded as observed. No claim is made that the submitted links are invalid; that determination is
Amazon's. See UNV-05 in the claims ledger.

## D. Attempted and **not** verified — do not treat as settled

| # | Question | Status | Where it must be settled |
|---|---|---|---|
| D1 | Is an ASIN defined as exactly 10 characters by an Amazon-authored page? | **Not officially cited.** Corroborated by Amazon's catalogue glossary as quoted on a customer Q&A page and by direct observation (every ASIN reached in C1–C5 is 10 chars, every submitted token is 9). Seller Central's reference page needs a login. | Seller Central help, "ASIN" |
| D2 | Do you need 3 qualifying sales within 180 days, and does PA-API access depend on it? | **Not found** in A1 or A2 as fetched. Repeated widely by third-party blogs. Not used anywhere on the site. | Associates Central, in-account notices |
| D3 | Commission rate for Home & Kitchen / small appliances | **Not retrieved.** Rate card sits behind the login. No percentage appears on the site. | Associates Central, Commission Income Statement rate card |
| D4 | Is `link.amazon` an Amazon-owned, authorised short-link domain? | **Unconfirmed.** Requests are handed to amazon.com, which demonstrates routing, not ownership or authorisation. No registrar data obtainable here. | Amazon's documentation of approved link tools |
| D5 | Does tracking ID `shopnow047c-20` exist, is it enrolled, and is it this site's tag? | **Unconfirmed.** No account access. The `XXXXX-##` shape in §2(b) is consistent with tag `shopnow047c-20`; the retrieved text does not say a tracking ID and a tag suffix are the same string, so the value is recorded unsplit rather than parsed. | Associates Central, Account settings → Tracking IDs |
| D6 | Are the submitted short links compliant? | **Deliberately not answered.** Verified facts only: no tag parameter present, destination ≠ submitted token. | Test one tagged link per product in the enrolled workflow; confirm destination and tracking report |
| D7 | Do the four observed listings match what the owner intended to promote? | **Unknown**, and the central open question (Q-03). The fallback marker in C1–C5 is a reason for doubt, not proof of mismatch intent. | Owner's source document for the links |

## E. Notes on method, so the evidence can be reproduced

- One request per URL, anonymous, no session reuse. Each control test is reported with its
  limitation, including where it was inconclusive (C8).
- Prices and star counts visible inside the fetched page chunks were **not** used, because in those
  chunks they belonged to "customers who viewed this item also viewed" carousels rather than to the
  landing listing. Publishing them would have misattributed a number — and §2(b) of A2 forbids
  displaying prices the site did not receive from Amazon or a licensed API.
- No scraping infrastructure was built. A2's bonus-event exclusions disqualify events generated with
  "bots or automated software", so automation here is confined to registers, rendering, and checks.
- This environment has no Amazon credentials, so nothing requiring an account was attempted or
  claimed.
