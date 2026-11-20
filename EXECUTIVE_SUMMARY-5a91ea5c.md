# Executive summary — session `arena/5a91ea5c-affil3`

**Prepared:** 2026-11-20 · **Tracking ID:** `shopnow047c-20` · **Site:** https://karagemop466-tech.github.io/Affil3/
**Branch:** `arena/5a91ea5c-affil3` (cut from `main` @ `16ee89f`; integrated with `main` through PR #87 before this PR)

---

## The one-paragraph version

Five Amazon links were supplied; all five have resolved to real products in one coherent niche —
countertop cooking appliances for kitchens with limited counter space — and the site publishes a
product-led shop over them: 18 question-shaped guides, a seven-piece Journal of timely articles,
5 product pages, a comparison table, three category clusters, a source register, and three decision
surfaces (suggestions, questions, flagged). Every page carries the Associates disclosure above the
fold, every retail link carries `rel="sponsored"` and `tag=shopnow047c-20`, and a build gate enforces
all of it — the merged tree passes **55 pages, 8,890 checks, 0 failed**. What still blocks revenue is
not build work: as observed, no supplied link carries the tracking ID, no Special Link has been
tested in Associates Central, and the decision log is still empty. This session's contribution is the
growth half of that decision board, a line-by-line pass that fixed copy and cross-references which
had drifted from the data, and this summary.

## What the five links are (observed, 2026-11-20, this session's round)

| Supplied token | Resolves to (this session's round) | Product |
|---|---|---|
| `B04G1MEwY` | `amazon.com/dp/B0CDY277D3` | CHEFMAN 6 Qt Dual Basket air fryer |
| `B02NbDxp3` | `amazon.com/dp/B09B7SB46R` | Emeril Lagasse 26 QT French door air fryer oven |
| `B00hJ57DV` | Amazon home page this round (intermittent; register: `B08DKYBTPH`) | CHEFMAN TurboFry 8 Qt |
| `B0c8moW59` | Amazon home page this round (intermittent; register: `B0DHZTCNR5`) | ThermoMaven 1 Sec instant-read thermometer |
| `B0f3GKalj` | `amazon.com/dp/B0DZFD6R9Z` | CHEF iQ Sense smart wireless thermometer, 3 probes |

Three of five reached the expected product pages on this round; two returned Amazon's home page —
the same session-sensitive behaviour recorded across every prior round (FLG-031), never evidence a
link is dead. **No destination carried `tag=`**, which is the finding that matters: as observed,
these links would not attribute a sale (FLG-003 unresolved, not invalid; the fix is one tested
Special Link per product in Associates Central — gate G-02, suggestion S-02). Intended ASINs remain
blank for all five rows; observed and intended fields are never merged (FLG-001, FLG-002).
Full round recorded in `data/observations/2026-11-20-5a91ea5c-recheck.json`.

## What is built and enforced

- **One indexed publication** at the repository root (robots.txt excludes the archived editions);
  products lead on the front page, dashboards live in one footer group, and a Journal band surfaces
  the seven timely articles alongside the 18 evergreen guides.
- **The gate** (`tools/verify.mjs`): disclosure above the fold on every page, `sponsored` + tag on
  every retail link, no prices or ratings anywhere, every source ID real, every internal link
  resolving, sitemap/feed coverage, and (new on main) citation integrity — every FLG/S/Q reference
  in the registers must resolve to a real row, which caught this session's own prose twice. Current
  state: **55 pages, 8,890 checks, 0 failed**; the disclosure check, archive check, counter-desk
  gate, counterwise gate and link checkers all pass on the merged tree.
- **Measurement** is built but inert: the click counter ships unarmed until an owner sets an
  analytics endpoint (FLG-009), and the five events are proposed, not confirmed (FLG-008).

## What this session changed (all reversible, all logged)

1. **Growth suggestions on the decision board** — a new track *7. Organic traffic and editorial
   growth* with six rows after two merge-time renumbers: **S-42** (which of the two assembled
   design prompts — `/design-brief/` or `/decisions/` — binds the next redesign), **S-43**
   (cluster pillars and related-guide linking, PB-9), **S-44** (reader-shaped titles + a length
   gate, PB-10), **S-45** (a fifteen-minute weekly decision-review cadence so the log stops
   staying empty), **S-46** (seasonality expiry machinery, PB-8), plus **S-47** in the trust
   track (footer gloss, PB-6). Each has options, trade-offs, effort, risk and a recommendation;
   nothing is implemented until an option is chosen. Its original S-20/S-31/S-32 were dropped or
   renumbered at merge: S-31 (seasonal lane) and S-32 (topics from measured queries) were dropped
   because main already carries S-23 and S-21 on those exact topics; the survivors were
   renumbered twice (to S-28/S-33–S-37, then to S-42–S-47) as main's own waves took those ids.
2. **Discovery questions** — **Q-29** (which acquisition channels the owner will run, closed by
   **D-27** against Participation Requirements 6(e)–(g) and Operating Agreement §4) and **D-28**
   (how to confirm the name already shipping, closing main's Q-18). Its original Q-25 was dropped
   as a duplicate of main's Q-18; D-13/D-14 and then Q-24/D-19/D-20 were renumbered as main took
   those ids. Registers now: 30 known, 29 open, 28 discovery paths.
3. **Stale copy and stale cross-references fixed where they had drifted from the data** —
   "All five guides" above the published guides, "five question-led guides" in the executive summary,
   "five original guides — below the 10-post rule" in the workflow page, decision IDs pointing at
   renumbered rows in the workflow copy, the design brief's sequence/prescriptions/prompt, and five
   flags' manual steps (FLG-007, FLG-008, FLG-014, FLG-015, FLG-016). Recorded as **FLG-054**
   (resolved; renumbered twice at merge — main had taken FLG-043/FLG-044 and documents 046–048 as
   gaps); counts are now derived from the registers. Main had independently fixed the
   workflow page's counts in commit `ad43826`; both fixes are kept, and this session's remaining
   Q-04/SG-29 references were replaced with Q-02/Q-12.
4. **FLG-055 raised** (renumbered from FLG-044 at merge): session c252594d's merged PR #54 shipped its guides but not the decision
   boards, register corrections or gate changes its work log claims; its scripts, if run now, would
   collide with IDs already taken. Owner/session action, published on `/flagged/`.
5. **Q-18 corrected**: the name row still claimed a placeholder "Affil3" wordmark; the site ships
   "ShopNow Kitchen" (config.json and the rendered `<title>`). Corrected with evidence, keeping
   main's row and closure path.

## What is blocked, and on whom (nothing here is build work)

| Blocked | Owner step | Closes |
|---|---|---|
| Revenue, entirely | Test one Special Link per product in Associates Central; confirm the click appears in the report | S-02, FLG-005, Q-02 |
| Attribution of the supplied links | Re-issue links with `shopnow047c-20` or confirm the short links were generated under it | FLG-003, Q-03 |
| Intended products | Open each short link signed-in and name the product | Q-01, FLG-002 |
| Any measurement | Choose the collector option (S-03) and set the endpoint | FLG-009, Q-04 |
| Topic selection from data | Verify the site in Search Console, submit the sitemap | S-21, FLG-013, Q-12 |
| Reader trust polish | Name an editor (S-08, Q-06); confirm the name already shipping (Q-18) | FLG-014 |
| Content-depth flag | Amazon's own judgement at application review; the count sits at 18 guides (S19) | FLG-007 (stays open) |
| Decisions, generally | Fifteen minutes a week on the board: reply one ID + letter (S-45) | decision_log |

## The honest position on revenue and traffic

The site earns nothing today and will earn nothing until a tagged link exists and has been tested
once. There is no traffic, conversion or revenue figure anywhere in this repository, because none
exists; no title claims popularity or search demand; the campaign ledger is empty by design. The
growth suggestions above are the plan for earning attention honestly — measured topics, cluster
linking, seasonal lanes with takedown dates — and every one of them waits on the same short list of
owner steps.

## Read next

- `/suggestions/` — 46 options with trade-offs; reply `S-xx <letter>` to choose (start: S-45 B).
- `/decisions/` — main's assembled decision board and design prompt.
- `/questions/` — 30 known, 29 open, 28 discovery paths, each with the step that closes it.
- `/flagged/` — 52 irregularities with sources (41 open, 11 resolved); none block publication.
- `/design-brief/` — the design prompt of record candidate (S-42); references remapped this session.
- `COORDINATION.md` — this session's claim, verification log, merge resolution and completion record.
