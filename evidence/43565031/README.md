# Session 43565031 — working registers

Kept as evidence and as the traceable source for `FLG-023`…`FLG-029`, `R13`…`R18`, `S-13`…`S-16` and
`Q-14`…`Q-17` in the live registers. **Deliberately outside `data/`, so no builder reads them and they
cannot be mistaken for site inputs.**

| File | What it is | Where it is used |
|---|---|---|
| `link-verification.json` | The five submitted links: submitted token, intended fields (blank, unconfirmed), observed destination, breadcrumb, flags, plus three control tests each with its limitation | Folded into `data/flags.json` `FLG-023`/`FLG-024` and `data/questions.json` `K-08`/`K-09` |
| `claims.json` | 17 policy claims, each with a verbatim quote, the document's own version date, and a retrieval date; plus 6 claims left explicitly unverified | `data/register/compliance.json` `R13`–`R18`; unverified list echoed as `FLG-026` |
| `open-questions.json` | 15 questions in know / don't-know / how-to-find-out / who-must-answer form | `data/questions.json` `Q-14`–`Q-17` and `D-07`–`D-10`; the rest largely already existed upstream as `Q-01`…`Q-13` |
| `suggestions.json` | 16 ranked suggestions with three bundle paths | `data/suggestions.json` `S-13`–`S-16`; the remainder overlapped existing `S-01`…`S-12` and was dropped rather than duplicated |
| `topics.json` | Five editorial clusters with 18 working titles, each with the angle and the anti-slop requirement | Not folded in: main publishes its own guide set. Kept as the pool the next cadence decision draws on |

## Why these are not generated pages any more

An earlier commit on this branch shipped `shop.html`, `suggestions.html`, `questions.html` and
`verification.html` at the repo root. `main` meanwhile became a generated publication with `/shop/`,
`/suggestions/`, `/questions/` and `/flagged/`, built from `data/*.json` by `tools/build.mjs`, plus
`/editorial/` built from `data/register/*.json` by `tools/build.py`. Root-level duplicates would have
been a second site to index — the exact failure mode the brief's "make it findable" goal is about — so
the pages and this session's competing validator/builder/CI files were removed, and the **content** was
folded into the registers above instead.

## Reproducing the evidence

Each URL in `link-verification.json` was requested once, anonymously, with no Associates credentials.
To re-check any row, open the `review_link` in a private window and read the address bar after the
redirect. The `plpRedirect=mhFallback` parameter and the mismatch between submitted token and reached
ASIN are the two things worth looking at; nothing here requires trusting this file.
