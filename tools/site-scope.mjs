// The single definition of what the root publication owns, shared by the builder and the gate.
// Before it existed, tools/build.mjs and tools/verify.mjs each kept their own list and they had
// quietly drifted: the builder was writing /compare/, /workflow/, /privacy/, /design-brief/ and
// /find/ while the gate was only walking the shorter list, so several published pages were never
// checked at all (recorded as FLG-038). One list, imported by both, cannot drift.
import fs from 'node:fs';
import path from 'node:path';

// Paths the root build writes. Anything at the repository root outside this list belongs to another
// edition or to the repository itself and is left untouched.
export const OWNED = [
  'index.html', 'shop', 'search', 'compare', 'find', 'products', 'categories', 'guides', 'articles', 'decisions', 'how-we-choose',
  'executive-summary', 'sources', 'questions', 'suggestions', 'flagged', 'ledger', 'measurement',
  'compliance', 'about', 'workflow', 'privacy', 'design-brief', '404.html',
  'feed.xml', 'sitemap.xml', 'robots.txt',
  'assets/style.css', 'assets/analytics.js', 'assets/img', '.nojekyll',
];

// Directories at the root of the repository that publish a page of their own and are not written by
// this build: the superseded editions kept for provenance. Sorted so the output is deterministic.
export function extraEditions(root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..')) {
  return fs.readdirSync(root, { withFileTypes: true })
    .filter((d) => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
    .map((d) => d.name)
    .filter((n) => !OWNED.includes(n) && fs.existsSync(path.join(root, n, 'index.html')))
    .sort();
}

// Markdown kept at the repository root for the record. The repository is also the web root (Pages
// publishes main at /), so with .nojekyll each of those files is served as plain text at a guessable
// URL. They are excluded from the index by the same generated robots.txt, and never moved or edited
// here: they are another session's record, and the relocation is a decision for the owner (S-22).
export function rootMarkdown(root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..')) {
  return fs.readdirSync(root, { withFileTypes: true })
    .filter((d) => d.isFile() && d.name.endsWith('.md'))
    .map((d) => d.name)
    .sort();
}
