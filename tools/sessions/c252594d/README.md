# Session `c252594d` — one-shot register migrations

These scripts are **not** part of the build. They are the exact, re-runnable edits this session
made to `data/*.json`, kept so that any later change can be traced back to the dated fetch that
justified it. Each one is idempotent: it skips entries that are already present.

| Script | What it changed | Why |
|---|---|---|
| `apply-verification.py` | `data/sources.json`, `data/products.json`, `data/flags.json` | Applied the primary-source corrections of 2026-11-20 (P03, P04, P05), added sources S21–S23, closed FLG-012 and FLG-025, opened FLG-031 to FLG-033 |
| `add-guides.py` | `data/guides.json` | Added the eight question-shaped guides and corrected the outdated note in the thermometer guide |
| `add-decision-boards.py` | `data/suggestions.json`, `data/questions.json` | Added suggestions S-11–S-18, questions K-13–K-17 / Q-14–Q-17, discovery actions D-09–D-12, and corrected K-07 and K-10 |

The live site is built from the registers, not from these scripts. After changing a register by
hand, run `node tools/build.mjs && node tools/verify.mjs`.
