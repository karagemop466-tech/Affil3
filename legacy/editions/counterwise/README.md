# Affil3 — Counterwise

An Amazon-Associates affiliate publication for countertop cooking gear, plus the register and the
build gate that decide what it is allowed to claim.

- **Live site:** https://karagemop466-tech.github.io/Affil3/
- **Tracking ID:** `shopnow047c-20` (present on every outbound link; existence in-account is
  tracked as FLG-009)
- **Repository of record for decisions:** [`COORDINATION.md`](COORDINATION.md)
- **Operating procedures:** [`RUNBOOK.md`](RUNBOOK.md)

## What is here

```
data/            the register — sources, links, product-intent records, flags, suggestions,
                 questions, events, the campaign ledger. This is where facts are written.
content/guides/  guide bodies as markdown, one file per guide
tools/           build.py · gate.py · special_links.py · collector.py · ledger.py · resolve_links.py
tests/           unittest suite: mostly "prove the gate still catches a wrong claim"
docs/            GENERATED static site, published by GitHub Pages from /docs. Never hand-edit.
assets-src/      stylesheet, beacon, illustration sources (copied into docs/assets by the build)
```

## Commands

```bash
python3 counterwise/tools/build.py                       # regenerate docs/ from data/ + content/, then run the gate
python3 counterwise/tools/gate.py                        # audit only; exit 1 means the site may not ship
python3 counterwise/tools/gate.py --explain              # every rule and why it exists
python3 -m unittest discover -s counterwise/tests -v     # the anti-hallucination tests
python3 counterwise/tools/special_links.py check         # prove every product row yields a tagged Special Link
python3 counterwise/tools/ledger.py status               # campaign ledger state
python3 counterwise/tools/collector.py serve --port 8099 # the event sink (not deployed; see FLG-010)
```

Python 3.11 standard library only. No dependencies to install, nothing in the build path that can
drift. `markdown`, `pyyaml` and `pytest` are deliberately absent — the renderer is in
`tools/site_common.py` and the tests use `unittest`.

## The rule this repository is built around

A fact may appear on a page only if it exists in `data/` with a source and a date, and the gate
refuses the build otherwise. Blanks stay blank and get flagged rather than being filled by an
inference: `intent.*` fields (what the program owner meant to promote) can only be written inside
the enrolled Associates account, and `observation.*` fields (what a link actually did when it was
followed) are recorded separately and never merged into them.

See [`data/README.md`](data/README.md) for the register contract and
[`counterwise/transparency/method/`](https://karagemop466-tech.github.io/Affil3/transparency/method/) for
the rules as they run.

## Deliberate absences

No prices, no star ratings, no conversion score, no revenue forecast, no Product or Review
structured data, no cookies, no third-party assets. Each of those is explained on the site as a
decision with a flag or a suggestion row behind it, not as an oversight.
