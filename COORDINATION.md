# COORDINATION — shared task board for `Affil3`

Read this before you touch anything. Write to it before you start, and again when you stop.
This file is the only coordination surface for parallel Arena sessions.

**Session ID:** `59aebafb` · **Branch:** `arena/59aebafb-affil3`

Rules that keep parallel sessions from destroying each other's work:

1. **Claim first.** Session ID + file scope in the board, commit, push, *then* edit.
2. **Never edit outside your scope.** Need a file another session owns? Open a `REQUESTS`
   entry below instead of editing it.
3. **Branch per task** is the intent of the brief, but Arena fixes each session to one working
   branch. Sessions therefore isolate by **directory scope**, not by branch. This is logged as a
   deliberate deviation (see LOG).
4. **Small commits, `git pull --rebase` before every push.** Resolve conflicts keeping both sides;
   record the conflict here.
5. **Shared outputs** — `docs/` (published site), `docs/sitemap.xml`, `docs/feed.xml`, site nav —
   are generated from `register/*.json` by `scripts/build.mjs`. Nobody hand-edits `docs/`; edit the
   register and rebuild. Merge conflicts in generated files are resolved by re-running the build.
6. **Stale-claim takeover:** no commits for > 60 minutes ⇒ any session may take the task over and
   must note the handoff in LOG.
7. **Verification is a gate, not a vibe.** Nothing is marked `verified` unless it was checked
   against an official source, with source URL + access date recorded in `register/sources.json`.
   Values that cannot be confirmed are left **blank** and flagged on the Flagged for Review page.
   `needs review` never blocks a merge; a **broken build does**.

---

## My scope (claimed by `59aebafb`)

| Path | Contents |
|---|---|
| `register/` | Source of truth: source register, product-intent records, suggestions, flags, questions, ledger, event schema |
| `content/` | Authored editorial (guide markdown + site copy) consumed by the builder |
| `scripts/` | `build.mjs`, `checks.mjs` (compliance gate), `collect.mjs` (self-hosted event endpoint) |
| `docs/` | Generated GitHub Pages output (served from `main:/docs`) |
| `docs/EXECUTIVE-SUMMARY.md` etc. | Repo-level exec summary + decision brief |
| `.github/workflows/ci.yml` | CI gate: build + checks |
| `README.md` | Repo entry point |
| `COORDINATION.md` | This board — append-only in LOG/REQUESTS for other sessions |

## Board

| Task | Status | Owner | Files touched |
|---|---|---|---|
| T-REPO — repo review, irregularities | done | `59aebafb` | `register/repo_review.json` |
| T-SRC — official source register | done | `59aebafb` | `register/sources.json` |
| T-INTENT — product-intent confirmation records | done | `59aebafb` | `register/products.json` |
| T-LINK — Special Link generation (test one, then scale) | needs review (gated on owner's Associates Central) | `59aebafb` | `register/links.json`, `scripts/build.mjs` |
| T-COMP — disclosure + policy gate in build | done | `59aebafb` | `scripts/checks.mjs`, `register/compliance.json` |
| T-EDIT — question-shaped guides | done | `59aebafb` | `content/guides/*.md` |
| T-SUGG — suggestions register (review before implementing) | done | `59aebafb` | `register/suggestions.json` |
| T-QUEST — open questions / missing-information gate | done | `59aebafb` | `register/questions.json` |
| T-MEAS — click + conversion measurement | done (endpoint local, not deployed) | `59aebafb` | `docs/assets/track.js`, `scripts/collect.mjs`, `register/measurement.json` |
| T-LEDGER — campaign ledger (empty by design) | done | `59aebafb` | `register/ledger.json` |
| T-SITE — Pages site, sitemap, RSS, search | done | `59aebafb` | `docs/`, `scripts/build.mjs` |
| T-EXEC — executive summary + decision brief | done | `59aebafb` | `docs/EXECUTIVE-SUMMARY.md`, `docs/DECISION-BRIEF.md` |
| T-INT — integration, PR → main, Pages deploy | in progress | `59aebafb` | — |

## Requests

- `59aebafb` → any sibling session: `main` currently has no COORDINATION.md. Whoever integrates
  first should land a board that includes other sessions' scopes rather than replacing this one.

## LOG

- 2026-11-20T05:09Z `59aebafb` — Read the repo. It contains exactly one file, `README.md`
  (8 bytes, `# Affil3`), and one commit `847ae37`. **No COORDINATION.md, no site, no register, and
  none of the artifacts referenced in the task brief exist in this repo** (no source register, no
  `SG-27..SG-30`, no `FLG-003`, no `S01/S07/S24` rows). The brief is written as a continuation of
  prior work; that work is not present here. Recorded rather than silently re-created.
- 2026-11-20T05:14Z `59aebafb` — Enumerated `origin`: 9 sibling `arena/*-affil3` branches, each
  with a COORDINATION.md claim committed 05:09–05:13Z, each containing only `README.md` +
  `COORDINATION.md` (+ `.gitignore`). **No sibling session has produced site content.** Observed
  overlapping scopes: `114f47c4` claims root-level site files (`index.html`, `guides/`, `data/`);
  `772f3220` claims `docs/` + `register/` (overlaps this session's plan; see DEVIATION below).
  This session proceeded because `main` is empty and no task was completed elsewhere.
- 2026-11-20T05:14Z `59aebafb` — **DEVIATION / conflict risk:** `772f3220` claims `docs/` and
  `register/`, the same paths this session claims. Neither board exists on `main`, so there is no
  ordering mechanism. Resolution chosen: this session keeps working its own branch; if both PRs
  land, integration should keep one output tree and regenerate the other. Logged, not resolved
  unilaterally.
- 2026-11-20T05:15Z `59aebafb` — **IRREGULARITY (repo-level, pre-build):** the five "product
  links" in the brief are `https://link.amazon/<9-char token>`. Amazon ASINs are 10 characters, so
  the five strings (`B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV`, `B0c8moW59`, `B0f3GKalj`) are **not
  ASINs**; they are redirector tokens. Verified by resolution: `link.amazon` does resolve and does
  redirect to real `amazon.com/dp/…` listings whose ASINs differ from the submitted tokens. See
  `register/products.json`: submitted token and observed target ASIN are stored in **separate
  fields**, never merged, per the brief's product-intent requirement.
- 2026-11-20T05:20Z `59aebafb` — Resolution outcomes (accessed 2026-11-20, via HTTPS fetch, final
  URL + page `<title>` recorded): `B04G1MEwY`→`B0CDY277D3`; `B02NbDxp3`→`B09B7SB46R`;
  `B00hJ57DV`→`B08DKYBTPH`; `B0f3GKalj`→`B0DZFD6R9Z`; `B0c8moW59`→**unresolved** (3 attempts,
  Amazon `checkpoint/continue` interstitial). Flagged FLG-004. No product identity, price, rating,
  or spec was inferred for it.
- 2026-11-20T05:22Z `59aebafb` — **Compliance consequence adopted site-wide:** observed redirects
  carried **no `tag=` parameter** in the final URL. Do not claim the short links are invalid
  (compliance status unresolved, FLG-003 as briefed); do publish Special Links built in the
  documented tagged format with the site's tracking ID instead.
- 2026-11-20T05:25Z `59aebafb` — **Price suppression decision:** no prices, availability, star
  ratings, or review counts are published. Rationale: Associates Program Policies permit price/
  availability only when served by Amazon's own link/tools or pulled from the Creators/PA API
  (24-hour refresh ceiling), and this project has no API credentials. `scripts/checks.mjs` fails
  the build if any `$` price pattern reaches `docs/`.
- 2026-11-20T05:26Z `59aebafb` — Claim pushed to `arena/59aebafb-affil3`. Work begins on
  `register/`.
