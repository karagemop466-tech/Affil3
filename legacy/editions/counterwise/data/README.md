# `data/` — the register everything else is generated from

`counterwise/` is build output. **Never hand-edit a file under `counterwise/`** — change the row here, run
`python3 counterwise/tools/build.py`, and the site, the sitemap, the feed and the gate report follow.

Zero third-party dependencies: stdlib Python only, so the gate runs in CI, in a sandbox, or on
a laptop with nothing installed.

## Files

| File | Rows | Purpose |
| --- | --- | --- |
| `config.json` | — | Site identity, tracking ID, disclosure text, measurement and capture state, cadence |
| `links.json` | `LNK-*` | The links supplied by the program owner, exactly as given, plus the observed redirect evidence |
| `products.json` | `P-*` | Product-intent confirmation records. Confirmation fields and observation fields are kept apart on purpose |
| `sources.json` | `SG-*` | Source register: what each official page says, how it was read, when |
| `questions.json` | `Q-*` | Open questions: what we have, what is missing, how to find it, what it blocks |
| `suggestions.json` | `S-*` | Decision board: options with cost, payoff, risk, dependency, and a decision field to fill in |
| `flags.json` | `FLG-*` | Irregularities and unverified items. Published on `/review/`, never silently fixed |
| `events.json` | `EV-*` | The five events the measurement layer is allowed to record |
| `guides.json` | `G-*` | Editorial index: title, cluster, summary, dates, body file, sources used |
| `ledger/` | CSV + JSONL | Empty campaign ledger and the collected-event log directory |

## Rules the gate enforces (`python3 counterwise/tools/gate.py`)

1. **Every factual row carries a source.** A row whose `verification` is `confirmed` or
   `verified` must reference at least one `sources.json` ID or an `evidence` URL that this repo
   actually fetched.
2. **No inferred values.** If a field is not confirmed it is `""` or absent, and the row points at
   a `FLG-*`. `tools/gate.py` rejects placeholder text (`TBD`, `n/a`, `unknown`, `Lorem`, `[insert`).
3. **No unregistered citations.** Every external URL used in any published page must be either a
   registered source, a registered observed listing URL, or the marketplace itself with a tag.
4. **Compliance is not optional.** Every page ships the disclosure strip under the masthead *and*
   in the footer; every Amazon-bound link carries `tag=<tracking_id>` and `rel="sponsored nofollow"`.
5. **No unsupported marketing voice.** Banned patterns include invented prices, invented star
   ratings, "we tested/tried", "editor's choice", "best overall", guarantees, health claims, and
   the filler vocabulary that makes sites read like they were generated. See `BANNED_PATTERNS` in
   `tools/gate.py` — each entry has a `why`.
6. **No broken site.** Every internal link resolves to a file that exists; `sitemap.xml` lists
   exactly the pages that exist; `feed.xml` parses; JSON-LD blocks parse; the ledger header matches
   `counterwise/data/ledger/README.md`.
7. **Output is fresh.** `counterwise/manifest.json` stores a hash of `data/` + `content/`; the gate fails
   if the committed HTML was built from different inputs.

## Adding a row

```bash
python3 counterwise/tools/gate.py --explain          # what the rules check, one line each
python3 counterwise/tools/build.py                   # regenerate docs/ from data/ + content/
python3 counterwise/tools/gate.py                    # exit 0 or the site does not ship
python3 -m unittest discover -s counterwise/tests    # proves the gate still catches bad rows
```

## Adding a product the honest way

`data/products.json` separates two things that affiliate sites normally mash together:

* `intent.*` — what the program owner says they meant to promote (intended ASIN, official listing
  URL, confirmation date, who/where it was confirmed). This is a **confirmation record**, and only
  someone inside the Associates account can complete it.
* `observation.*` — what this project actually saw when it followed the supplied link on a given
  date: final URL, page title, breadcrumb.

Do not copy `observation.listing_asin` into `intent.intended_asin` to make a row look complete.
That merge is exactly what the FLG-001 flag exists to prevent.
