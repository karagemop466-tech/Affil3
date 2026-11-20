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
