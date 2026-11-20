# Archived: integrated root edition (2026-11-20)

This directory preserves the integrated root edition built by `tools/build.mjs`
from `data/*.json` (sessions `6249757a`, `f761b123`, `4578ad4b`, with data
corrections from `166bf329`). It was the live root site until the
`arena/0a90f62c-affil3` integration pass moved it here to keep the repository's
"nothing deleted; every session's output kept and reachable" convention while
making Crisp & Counter the root publication.

Nothing was edited inside the snapshot except one mechanical rewrite: absolute
self-links of the form `/Affil3/...` now point at
`/Affil3/legacy/arena-4578ad4b/...` so the archive is self-contained. Links to
`/editorial/` and `/legacy/` were left pointing at their real locations.

- The archive's own sitemap and feed are `sitemap.xml` and `feed.xml` in this
  directory.
- Its registers remain at `data/` and `data/register/` in the repository root,
  unchanged.
- To regenerate this edition: `node tools/build.mjs` — but note it writes to the
  repository root and would overwrite the live site; coordinate in
  `COORDINATION.md` first.
