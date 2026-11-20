# Affil3

A buyer's shop for countertop cooking, built as an Amazon Associates affiliate publication, with the
evidence and the decision-making exposed next to the products.

**Live site:** https://karagemop466-tech.github.io/Affil3/

## What is here

| Path | What it is |
|---|---|
| `index.html` | Front page: the shelf, the guides, how the shop works |
| `shop.html` | Shelf plus five editorial clusters and their topic queues |
| `products.html` | The five submitted Amazon links exactly as received |
| `verification.html` | Link evidence register — intended vs observed fields, dated, with control tests |
| `suggestions.html` | Decision room — 16 ranked proposals, 3 paths, each resting on quoted policy text |
| `questions.html` | Open questions — what is known, what is missing, how to go find it, who must answer |
| `flagged.html` | Flagged-for-review register with a source link per row |
| `guides/` | Question-shaped buyer guides |
| `EXECUTIVE_SUMMARY.md` | The summary a decision should start from |
| `docs/OFFICIAL-SOURCES.md` | Every source relied on, quoted, with retrieval dates and what could not be verified |
| `COORDINATION.md` | Shared task board for parallel sessions |

## How it is built

`data/*.json` are the registers and the source of truth. Four of the pages above are **generated** from
them:

```bash
python3 scripts/build_registers.py     # write the pages
python3 scripts/validate_site.py       # the publishing gate
python3 scripts/check_markup.py        # structural check
```

CI (`.github/workflows/ci.yml`) runs all three on every push and pull request. A generated page must
not be edited by hand — change the register and rebuild, or the build fails.

Static HTML, no framework, no external fonts or assets, no build dependencies beyond Python 3.

## House rules the code enforces

- No displayed price or availability figure anywhere: program policy permits a site to show them only
  when Amazon serves them or a licensed API supplies them.
- No unsourced row: anything not confirmed against an official source stays blank and is flagged, and a
  blank is never back-filled from a neighbouring column.
- Every outbound product link carries `rel="sponsored nofollow"`.
- Disclosure sits under the masthead and repeats in the footer on every page.
- No superlative or demand claim ("most popular", "top-rated", "trending") unless it is quoted from a
  source; a phrase inside a sentence that disclaims it is treated as a mention, not a claim.

## Known open items

Product identity for the five submitted links is unresolved, the Associates account and tracking ID are
unconfirmed, and no click or conversion data is collected yet (GitHub Pages cannot receive the beacon).
Each is listed with its lookup path in `questions.html` rather than being answered by guesswork.
