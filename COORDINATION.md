# Shared task board

Coordination file for parallel Arena sessions. Each session works only on its own branch and edits only files in its claimed scope. Log requests for files owned by another session here instead of editing them.

## Sessions and claims

| Session / branch | Status | Owner | File scope |
|---|---|---|---|
| `arena/772f3220-affil3` (this session) | in progress | `arena/772f3220-affil3` | `docs/` (GitHub Pages output, served from `main:/docs`), `register/` (source register, product-intent record, campaign ledger, guides, suggestions, questions, flags — data), `scripts/` (stdlib build + link/QA checks), `COORDINATION.md` (append-only log) |
| `arena/114f47c4-affil3` (other session, seen on `origin`) | in progress (its claim, commit `ce8e459`) | `arena/114f47c4-affil3` | `COORDINATION.md`, `README.md`, `index.html`, `assets/`, `guides/`, `flagged-review.html`, `editorial.html`, `methodology.html`, `data/`, `sitemap.xml`, `feed.xml`, `robots.txt`, `.github/workflows/` |

### Overlap and handling

- **Root-level site files.** The other session plans a root-level site (`index.html`, `guides/`, `sitemap.xml`, `feed.xml`, `robots.txt`, `data/`). This session publishes from `docs/` instead, so the two output trees do not share files. Pages source for this session is `main:/docs`. If both sites are later published, the Pages source must be chosen once by the integration step (see Decisions in the Questions page).
- **`COORDINATION.md`** is claimed by both sessions. This session appends only. Any merge conflict will be resolved by keeping both entries and logged here.
- **`README.md`** is in the other session's scope. This session does not edit it. Request logged below.
- **Branch naming.** The task text asks for `session-<id>/<task>` branches. The agent instructions for this session fix the work to the single current branch `arena/772f3220-affil3`. No other branches are created. This is logged as a deviation.

## Task board

| Task | Status | Owner | Files | Sources / verification |
|---|---|---|---|---|
| T-REPO Repo review and irregularities | in progress | `arena/772f3220-affil3` | `register/repo-review.json` | See Flagged for Review |
| T-SRC Source register (official sources only) | in progress | `arena/772f3220-affil3` | `register/sources.json` | Links are listed on the Sources page |
| T-INTENT Product-intent confirmation record | in progress | `arena/772f3220-affil3` | `register/products.json` | Amazon listing pages fetched; see Products page |
| T-LINK Validated Special Links (Associates workflow test) | blocked: needs owner's Associates login | — | — | Not run. No credentials used; logged as flag FLG-003 follow-up |
| T-MEAS Click and conversion measurement | in progress | `arena/772f3220-affil3` | `docs/assets/measure.js`, `register/measurement.json` | Endpoint not deployed; see Flagged for Review |
| T-COMP Disclosure and policy gate | in progress | `arena/772f3220-affil3` | `register/compliance.json`, `scripts/checks.py` | Operating Agreement and FTC sources linked |
| T-EDIT Question-shaped guides | in progress | `arena/772f3220-affil3` | `register/guides/` | Working titles only; not factual claims |
| T-SUGG Suggestions and questions | in progress | `arena/772f3220-affil3` | `register/suggestions.json`, `register/questions.json` | No changes implemented before choice |
| T-LEDGER Campaign ledger (empty) | done (empty by design) | `arena/772f3220-affil3` | `register/ledger.json` | No first-party reports supplied |
| T-SITE Site build, sitemap, feed, Pages | in progress | `arena/772f3220-affil3` | `docs/`, `scripts/build.py` | Built locally; link check in `scripts/checks.py` |
| T-EXEC Executive summary | in progress | `arena/772f3220-affil3` | `docs/executive-summary.html` | Generated from register |
| T-INT Integration, PR, merge, Pages deploy | not started | `arena/772f3220-affil3` | — | To run after all tasks |

## Handoff / coordination log

- 2026-11-20 — `arena/772f3220-affil3`: Read the repo. It contains only `README.md` (`# Affil3`) and one commit `847ae37`. No COORDINATION.md existed on this branch or `main`. Found the other session's claim on `origin/arena/114f47c4-affil3` (commit `ce8e459`) and recorded the overlap above. Claimed this scope and pushed the claim to this branch only.
- Request logged for the other session: the README and root-level site files are theirs. This session does not touch them. If the integration session wants a single site, it should choose between `main:/docs` (this session) and root (their plan).

## 2026-11-20 update from `arena/772f3220-affil3`

- **Overlap with `main` (FLG-R21).** `origin/main` now serves an integrated site from the repository root, built by session `6249757a` (PRs #1, #4, #6 merged; Pages source `main:/`). Open PRs from other sessions also cover this task (#2, #3, #5). This branch's `docs/` output would be served under `/docs/` on the live host and would duplicate that site. **No PR was opened from this branch to `main`, and no `docs/` output is committed.** The branch keeps the register, the checker and the audit as its contribution.
- **Scope kept.** This session's files are `register/`, `scripts/` and this log. `docs/` stays untracked. No file owned by another session was edited.
- **Audit of `origin/main` (read-only export).** Their `tools/verify.mjs` passes (1,266 checks). The site's disclosure sentence is present on 23 of 34 HTML files (`As an Amazon Associate I earn from qualifying purchases.`), and every Amazon anchor carries `rel="sponsored noopener"`. Requests for the integration owner:
  1. **P-04 mapping conflict (FLG-R19, high).** Re-fetched 2026-11-20: `link.amazon/B00hJ57DV` → `/dp/B08DKYBTPH`; `link.amazon/B0c8moW59` → checkpoint page. The `origin/main` log and its P04 link say the reverse. Correct it or leave P-04 unresolved.
  2. **Outbound link form (FLG-R20, high).** Main links are hand-tagged `/dp/<ASIN>?tag=shopnow047c-20`, not the supplied short links and not validated Special Links. Decide after T-LINK.
  3. **Legacy pages (`legacy/arena-83a43a96/`).** 11 pages lack a canonical link and are not in `sitemap.xml`. Either add them or state that the legacy tree is intentionally unindexed.
  4. **External allowlist.** `www.fsis.usda.gov` and `www.ecfr.gov` are cited but not on the checker's allowlist. Both are official government sources. Add them if the site keeps those citations.
  5. **Base-path links.** Main uses `/Affil3/…` project-root links. These are correct for the Pages project URL. Any checker that resolves links against the export root will report false "broken" links.
- **T-LINK (Special Link testing): still blocked.** No enrolled Associates session is available to this session. No credentials were used. FLG-R18 stays open.
- **Re-verification 2026-11-20.** Re-fetched: product titles and breadcrumbs for P-01, P-02, P-03 and P-05 (match the register); `Updated: October 15, 2025` and the §5 wording on the Operating Agreement (match the site). SRC-01 and SRC-12 to SRC-15 notes are updated in `register/sources.json`. Price and rating are still not recorded.
- **Compliance gate.** `scripts/checks.py` passes on this branch's build (exit 0). C-01 to C-05, C-08 and C-13 cite that run, and each has a negative test (tamper copies: missing `rel="sponsored"`, altered disclosure, broken link, `$` price). The checker is written for this branch's markup and is not a general validator for `main`.
- **Integration owner.** Pages stays on `main:/`. The `docs/` source change was refused by the integration step earlier (FLG-020 on `main`), so no further Pages change is requested from this branch.
