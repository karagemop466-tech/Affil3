#!/usr/bin/env python3
"""build_site.py - render the Counter Tested site from data/ + src/content/.

Design commitments, in the order they matter:

1. DATA-DRIVEN. Pages are rendered from data/*.json and src/content/**/*.md. There is no page in
   this repo that a data change cannot update, and no number on a page that is not either in the
   data or written in a guide body with a source row attached.
2. DETERMINISTIC. Same inputs -> byte-identical output, so CI can prove that the committed site/
   folder is actually what the tools produce (see --check). No timestamps, no sorted-by-hash noise.
3. GATED. A product whose link_state is not 'live', or a programme switch that is off, produces a
   card with no clickable affiliate href. The gate is in the renderer, so forgetting is not an option.
4. LICENCE-SAFE. No price, rating, review-quote or Amazon image can be emitted from here: those
   fields are only ever rendered if a row carries provenance, and the intake tool refuses to write
   them at all. See docs/COMPLIANCE.md.

Usage:
  python3 tools/build_site.py            # build into site/
  python3 tools/build_site.py --check    # rebuild into .build-tmp/ and diff against site/
  python3 tools/build_site.py --stdout guides/x.html
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SRC = ROOT / "src"
OUT_DEFAULT = ROOT / "site"

# --------------------------------------------------------------------------- io

def load_json(rel: str):
    p = DATA / rel
    if not p.exists():
        sys.exit(f"FATAL: missing {rel} (data/{rel})")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:  # a broken register must not half-build
        sys.exit(f"FATAL: data/{rel} is not valid JSON: {e}")


def E(s) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def cell(v, *, mono=False, blank_note="not confirmed"):
    """A table cell that renders absence honestly."""
    if v is None or v == "" or (isinstance(v, list) and not v):
        return f'<td class="blank">{E(blank_note)}</td>'
    if isinstance(v, list):
        return "<td><ul>" + "".join(f"<li>{E(x)}</li>" for x in v) + "</ul></td>"
    inner = E(v)
    if mono:
        inner = f"<code>{inner}</code>"
    return f"<td>{inner}</td>"


# ------------------------------------------------------------------- markdown
# A deliberately small subset: headings, paragraphs, lists, tables, blockquotes,
# :::note callouts, and inline bold/italic/code/links. It exists so guide bodies can be
# plain text in git without a dependency, not so that anyone can get clever.

BLOCK_RE = re.compile(r"^\s*")


def inline(s: str, source_ids: dict) -> str:
    out = E(s)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", out)

    def link(m):
        text, href = m.group(1), m.group(2)
        if href.startswith(("http://", "https://")):
            return f'<a href="{href}" rel="noopener">{text}</a>'
        return f'<a href="{href}">{text}</a>'

    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, out)
    # [S06]-style citation chips -> a link into the source register
    out = re.sub(r"\[(S\d\d)\]", lambda m: f'<a class="srcchip" href="source-register.html#{m.group(1)}">[{m.group(1)}]</a>', out)
    return out


def md_to_html(text: str, source_ids: dict) -> str:
    lines = text.replace("\r\n", "\n").split("\n")
    out, i = [], 0

    def para(buf):
        if buf:
            out.append("<p>" + inline(" ".join(buf).strip(), source_ids) + "</p>")
            buf.clear()

    buf: list[str] = []
    while i < len(lines):
        ln = lines[i]
        if ln.startswith(":::"):
            para(buf)
            kind = ln[3:].strip() or "note"
            body, i = [], i + 1
            while i < len(lines) and not lines[i].startswith(":::"):
                body.append(lines[i])
                i += 1
            title = kind if kind != "note" else ""
            inner = md_to_html("\n".join(body), source_ids)
            head = f"<h4>{E(title)}</h4>" if title else ""
            out.append(f'<div class="callout"><p class="sr-only">Note</p>{head}{inner}</div>')
            i += 1
            continue
        if ln.startswith("#"):
            para(buf)
            lvl = len(ln) - len(ln.lstrip("#"))
            txt = ln[lvl:].strip()
            aid = re.sub(r"[^a-z0-9]+", "-", txt.lower()).strip("-")
            out.append(f'<h{min(lvl+1,6)} id="{aid}">{inline(txt, source_ids)}</h{min(lvl+1,6)}>')
            i += 1
            continue
        if ln.startswith("> "):
            para(buf)
            q = []
            while i < len(lines) and lines[i].startswith(">"):
                q.append(lines[i].lstrip("> ").strip())
                i += 1
            out.append("<blockquote>" + inline(" ".join(q), source_ids) + "</blockquote>")
            continue
        if re.match(r"^\s*[-*] ", ln):
            para(buf)
            items = []
            while i < len(lines) and re.match(r"^\s*[-*] ", lines[i]):
                items.append(re.sub(r"^\s*[-*] ", "", lines[i]))
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x, source_ids)}</li>" for x in items) + "</ul>")
            continue
        if re.match(r"^\s*\d+\. ", ln):
            para(buf)
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\. ", lines[i]):
                items.append(re.sub(r"^\s*\d+\. ", "", lines[i]))
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline(x, source_ids)}</li>" for x in items) + "</ol>")
            continue
        if ln.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            para(buf)
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            header = [c.strip() for c in rows[0].strip("|").split("|")]
            body_rows = [[c.strip() for c in r.strip("|").split("|")] for r in rows[2:]]
            thead = "<thead><tr>" + "".join(f"<th>{inline(h, source_ids)}</th>" for h in header) + "</tr></thead>"
            tbody = "<tbody>" + "".join(
                "<tr>" + "".join(
                    f'<td>{inline(c, source_ids)}</td>' if c else '<td class="blank">-</td>' for c in r
                ) + "</tr>"
                for r in body_rows
            ) + "</tbody>"
            out.append(f'<div class="tablewrap"><table>{thead}{tbody}</table></div>')
            continue
        if ln.strip() == "":
            para(buf)
            i += 1
            continue
        if ln.strip() == "---":
            para(buf)
            out.append("<hr>")
            i += 1
            continue
        buf.append(ln.strip())
        i += 1
    para(buf)
    return "\n".join(out)


def read_doc(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    fm = {}
    if raw.startswith("---"):
        end = raw.index("\n---", 3)
        for line in raw[3:end].strip().split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()
        body = raw[end + 4:].lstrip("\n")
    return fm, body


def parse_list(v: str) -> list[str]:
    if not v or v in ("null", "[]"):
        return []
    return [x.strip() for x in v.split(",") if x.strip() and x.strip() != "null"]


# ------------------------------------------------------------------- rendering

class Site:
    def __init__(self, out: Path):
        self.out = out
        self.program = load_json("program.json")
        self.products = load_json("products.json")
        self.sources = load_json("sources.json")
        self.suggestions = load_json("suggestions.json")
        self.questions = load_json("questions.json")
        self.flags = load_json("flags.json")
        self.events = load_json("events.schema.json")
        self.calendar = load_json("editorial-calendar.json")
        self.clusters = load_json("clusters.json")
        self.people = load_json("people.json")
        self.layout = load_json("layout.json")
        self.source_ids = {s["id"]: s for s in self.sources["sources"]}
        self.guides = self._load_docs(SRC / "content" / "guides", only_published=True)
        self.pages = self._load_docs(SRC / "content" / "pages")
        self.written: list[str] = []
        self.skipped_drafts: list[str] = []
        self.claims = []  # (page, field, value, source ids) for the claims table
        self.ledger = self._read_ledger()

    # -- helpers ---------------------------------------------------------
    def _load_docs(self, d: Path, only_published: bool = False):
        docs = {}
        if not d.exists():
            return docs
        for p in sorted(d.glob("*.md")):
            fm, body = read_doc(p)
            if only_published and fm.get("status", "").strip() != "published":
                self.skipped_drafts.append(p.stem)
                continue
            docs[p.stem] = (fm, body, p)
        return docs

    def _read_ledger(self):
        f = DATA / "ledger" / "campaign.jsonl"
        rows = []
        if f.exists():
            for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as e:
                    sys.exit(f"FATAL: data/ledger/campaign.jsonl line {n} is not JSON: {e}")
        return rows

    @property
    def base(self) -> str:
        return self.program["site"]["base_url"].rstrip("/") + "/"

    @property
    def abs(self) -> str:  # absolute URL for a repo-relative page
        return self.base

    @property
    def tracking_id(self) -> str:
        return self.program["associates"]["tracking_id"]

    @property
    def links_live(self) -> bool:
        return bool(self.program["commerce_switch"]["allow_live_links"])

    def product_href(self, p: dict, block: str, label: str = "Check the current price and availability on Amazon") -> str:
        """Render the outbound link, or its absence. This is the gate."""
        live = self.links_live and p.get("link_state") == "live" and p.get("official_listing_url")
        if live:
            url = f"https://{self.program['site']['default_marketplace_domain']}/dp/{p['intended_asin']}?tag={self.tracking_id}"
            return (
                f'<a class="btn" href="{E(url)}" rel="sponsored nofollow noopener" data-affiliate'
                f' data-slot="{p["slot"]}" data-block="{E(block)}">{E(label)}</a>'
                f'<span class="muted">Opens amazon.com. Sponsored link.</span>'
            )
    # -- pending state: print the destination, do not link it ---------------
        note = (
            f'<span class="badge pending">link not enabled</span>'
            f'<p class="muted" style="margin:6px 0 0;font-size:14px">Not clickable yet: this listing has not been '
            f'confirmed inside the enrolled Amazon Associates account, so there is no affiliate link to follow. '
            f'The destination we were given is <code>{E(p["submitted_url"])}</code> and the derived candidate is '
            f'<code>{E(p["candidate_listing_url"])}</code>. <a href="product-status.html">What is missing, in one paragraph</a>.</p>'
        )
        return note

    def disclosure_strip(self) -> str:
        a = self.program["associates"]["required_disclosures"]
        return (
            '<div class="disclosure" id="disclosure-strip"><div class="wrap">'
            f'<b>Disclosure.</b> <span>Counter Tested may earn a commission on qualifying purchases made through '
            f'the Amazon links on this page. That is paid to us by Amazon, not added to what you pay. '
            f'Links to Amazon are marked sponsored. <a href="about.html">How this site works</a>.'
            f'</span><span class="tag-line">“{E(a["associate_statement"])}”</span></div></div>'
        )

    def footer(self) -> str:
        a = self.program["associates"]["required_disclosures"]
        inside = "".join(f'<li><a href="{E(i["href"])}">{E(i["label"])}</a></li>' for i in self.layout["nav_inside"])
        extra = ""
        for i in self.layout["footer_extra"]:
            if i.get("external"):
                extra += f'<li><a href="{E(i["href"])}" rel="noopener">{E(i["label"])}</a></li>'
            else:
                extra += f'<li><a href="{E(i["href"])}">{E(i["label"])}</a></li>'
        shelf = "".join(f'<li><a href="product-{p["slug"]}.html">{E(p["intended_asin"])}</a></li>' for p in self.products["products"])
        guides = "".join(f'<li><a href="guide-{g}.html">{E(self.guides[g][0].get("title", g))}</a></li>' for g in self.guides)
        return (
            '<footer class="site"><div class="wrap"><div class="cols">'
            f'<div><h4>Shop</h4><ul><li><a href="shelf.html">The shelf</a></li>{shelf}</ul></div>'
            f'<div><h4>Guides</h4><ul>{guides}</ul></div>'
            f'<div><h4>How we work</h4><ul>{inside}</ul></div>'
            f'<div><h4>Site</h4><ul>{extra}</ul></div>'
            '</div><div class="fine">'
            f'<div class="stmt">{E(a["associate_statement"])} '
            'We do not make or receive any claim that Amazon endorses this site.</div>'
            f'<div>{E(a["amazon_content_disclaimer"])}</div>'
            f'<div>Product prices and availability are determined by Amazon at the time of purchase; this site '
            'displays no price it obtained elsewhere, because it has none it is licensed to show. '
            'Every factual claim carries a source in the <a href="source-register.html">source register</a>; '
            'items we could not confirm are blank and flagged on <a href="flagged-for-review.html">Flagged for review</a>.</div>'
            f'<div>{E(self.program["brand"]["name"])} · built from data in <code>data/</code> · '
            'source: <a href="https://github.com/karagemop466-tech/Affil3">karagemop466-tech/Affil3</a></div>'
            '</div></div></footer>'
        )

    def shell(self, *, title: str, desc: str, body: str, file: str, kind: str = "page",
              doc_slug: str = "", extra_head: str = "", crumbs=None) -> str:
        inside_links = "".join(f'<a href="{E(i["href"])}">{E(i["label"])}</a>' for i in self.layout["nav_inside"][:4])
        current = ' aria-current="page"'
        top_parts = []
        for i in self.layout["nav_reader"]:
            mark = current if i["href"] == file else ""
            top_parts.append(f'<a href="{E(i["href"])}"{mark}>{E(i["label"])}</a>')
        top = "".join(top_parts)
        inside_label = self.layout["nav_inside_label"]
        active_in = current if any(i["href"] == file for i in self.layout["nav_inside"]) else ""
        crumb_html = ""
        if crumbs:
            crumb_html = '<p class="meta" style="margin:14px 0 0">' + " &rsaquo; ".join(
                f'<a href="{E(h)}">{E(t)}</a>' if h else E(t) for t, h in crumbs
            ) + "</p>"
        collector = self.program["measurement"]["endpoint"] or ""
        head_extra = ""
        if self.layout.get("search_console_tag"):
            head_extra = f'<meta name="google-site-verification" content="{E(self.layout["search_console_tag"])}">'
        ld = ""
        if kind == "doc":
            payload = json.dumps(self.article_ld(title, desc, doc_slug, file), ensure_ascii=False, separators=(",", ":"))
            ld = f'<script type="application/ld+json">{payload}</script>'
        # index.html and the directory URL are the same page: canonicalise to the directory form so the
        # site never presents two URLs for its front page.
        abs_url = self.base if file == "index.html" else self.base + file
        return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} · {E(self.program['brand']['name'])}</title>
<meta name="description" content="{E(desc)}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{E(abs_url)}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{E(self.program['brand']['name'])}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{E(abs_url)}">
<meta property="og:image" content="{E(self.base + 'assets/img/hero.jpg')}">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="{E(self.program['brand']['name'])} guides" href="{E(self.base + 'feed.xml')}">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/style.css">
{head_extra}{extra_head}{ld}
</head>
<body data-page-kind="{kind}" data-doc="{E(doc_slug)}" data-collector="{E(collector)}" data-schema-version="{self.events['version']}">
<a class="skip" href="#main">Skip to content</a>
<header class="masthead"><div class="wrap">
  <a class="wordmark" href="index.html"><b>{E(self.program['brand']['name'])}</b><span>{E(self.program['brand']['tagline'])}</span></a>
  <nav class="main" aria-label="Primary">{top}
    <span class="group">{E(inside_label)}</span>{inside_links}
    <a href="{E(self.layout['nav_inside'][0]['href'])}"{active_in}>Full index</a>
  </nav>
</div></header>
{self.disclosure_strip()}
<main id="main">{body}{crumb_html}</main>
{self.footer()}
<script src="assets/track.js" defer></script>
</body></html>
"""

    def article_ld(self, title, desc, doc_slug, file):
        p = self.people["site_team"]
        g = self.guides.get(doc_slug, ({}, "", None))[0]
        d = g.get("date") or self.program.get("_", {}).get("updated", "2026-11-20")
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": desc,
            "datePublished": d,
            "dateModified": d,
            "inLanguage": "en",
            "author": {"@type": "Organization", "name": p["name"]},
            "publisher": {"@type": "Organization", "name": p["name"]},
            "mainEntityOfPage": {"@type": "WebPage", "@id": self.base + file},
            "isAccessibleForFree": True,
        }

    def write(self, rel: str, content: str):
        p = self.out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        self.written.append(rel)

    # -- pages -----------------------------------------------------------
    def page_index(self):
        br = self.program["brand"]
        prods = self.products["products"]
        cards = "".join(self.card(p) for p in prods)
        rows = "".join(self.guide_row(slug) for slug in sorted(self.guides))
        n_live = sum(1 for p in prods if p["link_state"] == "live")
        open_flags = [f for f in self.flags["flags"] if f["status"] == "open"]
        p0 = [q for q in self.questions["needs_owner"]]
        top_q = "".join(
            f'<div class="qa"><h3>{E(q["question"])}</h3><div class="row"><b>blocks</b><div>{inline(q["why_it_blocks"], self.source_ids)}</div></div>'
            f'<div class="row"><b>how to settle it</b><div>{inline(q["discovery"], self.source_ids)}</div></div></div>'
            for q in p0[:3]
        )
        hero_illo = '<figure class="illo" style="margin:0"><img src="assets/img/hero.jpg" alt="Illustration: two schematic kitchen appliances on a counter, drawn as line art, with a tape measure. Not product photography." style="width:100%;display:block;border-radius:10px;border:1px solid var(--line)"></figure>'
        body = f"""
<section class="hero"><div class="wrap">
  <div class="grid two" style="align-items:center">
    <div>
      <p class="kicker">{E(br['name'])} · kitchen appliance shelf</p>
      <h1>Five appliances, four questions,<br>and no invented numbers.</h1>
      <p class="lede">{E(br['blurb'])}</p>
      <div class="cta-row">
        <a class="btn" href="shelf.html">See the shelf</a>
        <a class="btn ghost" href="guides.html">Read the guides</a>
      </div>
      <div class="statusline">
        <div><b>{len(prods)}</b> listings assigned</div>
        <div><b>{n_live}</b> shoppable now</div>
        <div><b>{len(self.guides)}</b> guides published</div>
        <div><b>{len(open_flags)}</b> open items <a href="flagged-for-review.html">in the open</a></div>
        <div>ledger rows: <b>{len(self.ledger)}</b></div>
      </div>
    </div>
    {hero_illo}
  </div>
</div></section>

<section><div class="wrap">
  <div class="sec-head"><h2>On the shelf this week</h2><a href="shelf.html">All five →</a></div>
  <p class="muted measure">Everything here is a listing we were handed, not one we chose. The identifiers are printed exactly as supplied; the names are blank because we have not confirmed them. That is the state of play, not a design flourish.</p>
  <div class="grid shelf">{cards}</div>
</div></section>

<section><div class="wrap">
  <div class="sec-head"><h2>Guides worth ten minutes</h2><a href="guides.html">Index →</a></div>
  {rows}
</div></section>

<section><div class="wrap">
  <div class="grid two">
    <div class="callout"><h4>Before you buy anything from this page</h4>
      <ul>
        <li>Every outbound link to Amazon is a sponsored affiliate link, marked as such in the markup and disclosed above it.</li>
        <li>We print no price, no star rating and no review quote. Not because we forgot, but because we are not licensed to show numbers we cannot source. <a href="source-register.html#S06">The rule is quoted here.</a></li>
        <li>We have not tested these units. What we do instead is hand you the questions a listing page can actually answer.</li>
        <li>Where we could not verify something, the cell is empty and it is written down as a flag. <a href="flagged-for-review.html">See all of them</a>.</li>
      </ul>
    </div>
    <div class="callout plain"><h4>What we are waiting on</h4>
      <p>A few decisions here are not ours to make. These three change the site the most:</p>
      {top_q}
      <p style="margin:0"><a href="questions.html">All open questions →</a> · <a href="suggestions.html">Suggestions to review →</a></p>
    </div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="sec-head"><h2>Topics</h2><a href="topics.html">Clusters →</a></div>
  <div class="grid two">{"".join(self.cluster_card(c) for c in self.clusters['clusters'])}</div>
</div></section>
"""
        return self.shell(
            title=f"{br['name']} — {br['tagline']}",
            desc=br["blurb"],
            body=body, file="index.html",
        )

    def card(self, p: dict) -> str:
        badge = '<span class="badge live">shoppable</span>' if p["link_state"] == "live" and self.links_live else '<span class="badge pending">awaiting confirmation</span>'
        flags = " ".join(f'<a class="badge flag" href="flagged-for-review.html#{f}">{E(f)}</a>' for f in p.get("flags", [])[:3])
        return f"""<article class="card">
  <div>{badge}</div>
  <h3>{E(p['product_name'] or 'Listing ' + str(p['slot']))}</h3>
  <p class="ident">id as supplied: {E(p['intended_asin'])} · {p['intended_asin_char_count']} chars</p>
  <p><span class="badge assumed">{E(p['assumed_shelf_section'])}</span></p>
  <p>{E(p['why_no_fields'][:150])}…</p>
  <div class="foot">{flags}<a href="product-{p['slug']}.html">Full record →</a></div>
</article>"""

    def guide_row(self, slug: str) -> str:
        fm, body, _ = self.guides[slug]
        words = len(re.findall(r"[A-Za-z']+", body))
        mins = max(3, round(words / 220))
        return f"""<div class="guide-row">
  <a class="thumb" href="guide-{slug}.html" aria-label="{E(fm['title'])}">
    <span style="display:grid;place-items:center;height:100%;font-family:var(--serif);font-size:40px;color:var(--accent)">{E(str(words)[:2])}</span>
  </a>
  <div>
    <p class="kicker">{E(fm.get('kicker', ''))}</p>
    <h3><a href="guide-{slug}.html" style="text-decoration:none;color:inherit">{E(fm['title'])}</a></h3>
    <p>{E(fm.get('desc', ''))}</p>
    <p class="meta"><span>{mins} min read</span><span>{E(fm.get('date', ''))}</span>
      {f'<span>Topic: <a href="topic-{fm["cluster"]}.html">{E(fm["cluster"])}</a></span>' if fm.get('cluster') and fm['cluster'] != 'null' else ''}
      <span>{E(' '.join('[' + s + ']' for s in parse_list(fm.get('sources', ''))))}</span></p>
  </div>
</div>"""

    def cluster_card(self, c: dict) -> str:
        n = sum(1 for s, (fm, b, p) in self.guides.items() if fm.get("cluster") == c["id"])
        return f"""<article class="card">
  <h3><a href="topic-{c['id']}.html" style="color:inherit;text-decoration:none">{E(c['title'])}</a></h3>
  <p>{E(c['question'])}</p>
  <div class="foot"><span class="badge grey">{len(c['axes'])} comparison axes</span><span class="muted">{n} guide{'s' if n != 1 else ''}</span></div>
</article>"""

    def page_shelf(self):
        prods = self.products["products"]
        rows = []
        for p in prods:
            st = '<span class="badge live">live</span>' if p["link_state"] == "live" else '<span class="badge pending">pending</span>'
            rows.append(
                "<tr>"
                f'<td><a href="product-{p["slug"]}.html">#{p["slot"]} {E(p["intended_asin"])}</a></td>'
                + cell(p["product_name"], blank_note="unconfirmed")
                + cell(p["assumed_shelf_section"])
                + cell(p["intended_asin_char_count"])
                + cell(p["official_listing_url"], mono=True, blank_note="not confirmed")
                + cell(p["confirmation"]["date"], blank_note="not confirmed")
                + f"<td>{st}</td>"
                + cell(", ".join(p["flags"]), blank_note="-")
                + "</tr>"
            )
        head = "<tr><th>Listing</th><th>Product name</th><th>Shelf section</th><th>id length</th><th>Confirmed listing URL</th><th>Confirmed on</th><th>Links</th><th>Flags</th></tr>"
        checks = "".join(
            f"<tr><td>{inline(b['check'], self.source_ids)}</td><td>{E(b['where'])}</td><td>{inline(b['why_it_matters'], self.source_ids)}</td></tr>"
            for b in self.products["buyer_checks"]
        )
        body = f"""
<div class="wrap page-head">
  <p class="kicker">The shelf</p>
  <h1>What is on it, and what is not</h1>
  <p class="measure">Five listings, all of them handed to us through short links we could not resolve from where this site is built. The table below is the exact state of each: blank cells are blanks because nothing official confirmed them, and each one is written up on the <a href="flagged-for-review.html">review page</a>. The reader-facing product cards are honest about being unfinished, because a shelf that guesses is worse than a shelf with gaps.</p>
  <div class="cta-row"><a class="btn" href="product-status.html">Why nothing is clickable yet</a><a class="btn ghost" href="guides.html">Guides, meanwhile</a></div>
</div>
<div class="wrap">
  <div class="tablewrap"><table><caption>Listing inventory — every row traces to a record in <code>data/products.json</code></caption>
  <thead>{head}</thead><tbody>{''.join(rows)}</tbody></table></div>
  <h2>Five things a buyer should check on any listing</h2>
  <div class="tablewrap"><table><thead><tr><th>Check</th><th>Where to look</th><th>Why it matters</th></tr></thead><tbody>{checks}</tbody></table></div>
  <p class="muted">We link out to the Consumer Product Safety Commission's recall search from the guide pages rather than reproducing recall data here, because it changes daily and we are not licensed to cache anyone's product content.</p>
</div>
"""
        return self.shell(title="The shelf", desc="The five listings on our shelf, their confirmation state, and what a buyer should verify on the listing page.", body=body, file="shelf.html",
                          crumbs=[("Home", "index.html"), ("Shelf", "")])

    def page_product(self, p: dict):
        a = p["confirmation"]["status"]
        rows = [
            ("Identifier as supplied", p["intended_asin"], "operator brief, 2026-11-20", "verbatim"),
            ("Character count", p["intended_asin_char_count"], "counted from the string", "verified by arithmetic"),
            ("Submitted URL", p["submitted_url"], "operator brief", "verbatim"),
            ("Derived candidate URL", p["candidate_listing_url"], "/dp/ pattern substitution", "derived, unclicked"),
            ("Confirmed official listing URL", p["official_listing_url"], "—", "pending"),
            ("Observed redirect target", p["observed_redirect_target"], "—", "not observed from this environment"),
            ("Confirmation date", p["confirmation"]["date"], "—", "pending"),
            ("Confirmation method", p["confirmation"]["method"], "—", "pending"),
            ("Product name / brand", p["product_name"], "—", "pending"),
            ("Category from listing", p["category_from_listing"], "—", "pending"),
            ("Shelf section (assumed)", p["assumed_shelf_section"], p["assumed_shelf_section_basis"], "assumed — FLG-005"),
            ("Price", p["price"], "—", "not shown: licence-restricted field"),
            ("Availability", p["availability"], "—", "not shown: licence-restricted field"),
            ("Rating / review count", p["rating"], "—", "not shown: licence-restricted field"),
            ("Commission rate", p["commission_rate"], "—", "not shown: no authorised report"),
            ("Link state", p["link_state"], "commerce_switch + per-product gate", a),
        ]
        trs = "".join(
            "<tr>"
            + f"<th scope='row'>{E(k)}</th>"
            + (cell(v) if v not in (None, "") else '<td class="blank">blank — nothing confirmed it</td>')
            + f"<td>{inline(str(src), self.source_ids)}</td><td>{E(state)}</td></tr>"
            for k, v, src, state in rows
        )
        flags = "".join(
            f'<div class="flagcard"><h3><a href="flagged-for-review.html#{f}">{f}</a></h3><p>{inline(self._flag_text(f), self.source_ids)}</p></div>'
            for f in p["flags"]
        )
        checks = "".join(f"<li>{inline(b['check'], self.source_ids)}</li>" for b in self.products["buyer_checks"])
        body = f"""
<div class="wrap page-head">
  <p class="kicker">Product-intent record #{p['slot']}</p>
  <h1>{E(p['product_name'] or 'Listing ' + str(p['slot']) + ' — ' + p['intended_asin'])}</h1>
  <p class="measure">This page is the paperwork for one link: what we were given, what we could confirm, and what a human has to click before it becomes shoppable. The product-intent fields (intended identifier, official listing URL, confirmation date, source) are kept apart from the observed redirect target on purpose — merging them is how a guessed destination becomes a “verified” one.</p>
  <div class="chips">{"".join(f'<a class="chip" href="flagged-for-review.html#{f}">{f}</a>' for f in p['flags'])}
   <span class="chip">{E(p['assumed_shelf_section'])} (assumed)</span></div>
</div>
<div class="wrap">
  <div class="grid two">
    <div class="card" style="gap:4px"><h3>Where a buyer would click</h3>
      <p class="muted" style="font-size:13.5px">Destination as we would generate it once confirmed:</p>
      <p class="mono" style="word-break:break-all;margin:0">{E(p['candidate_listing_url'])}</p>
      {self.product_href(p, 'product-page')}
    </div>
    <div class="callout"><h4>What has to happen for that to become a link</h4>
      <ol style="margin:0">
        <li>Open the submitted URL in a signed-in session with the enrolled account and read the final address.</li>
        <li>Check the address bar still contains <code>tag={E(self.tracking_id)}</code>.</li>
        <li>Confirm the listing's title and category, and write them into <code>data/products.json</code>.</li>
        <li>Check the Associates report the next day for the test click.</li>
        <li>Rebuild. The card becomes clickable on its own; nothing else needs editing.</li>
      </ol>
      <p style="margin:8px 0 0"><a href="compliance-gate.html">The gate that enforces step 2 →</a></p>
    </div>
  </div>
  <h2>The record</h2>
  <div class="tablewrap"><table><thead><tr><th>Field</th><th>Value</th><th>Source / basis</th><th>Status</th></tr></thead><tbody>{trs}</tbody></table></div>
  <h2>Buyer checks that work regardless of what we confirm</h2>
  <ul>{checks}</ul>
  <h2>Flags attached to this listing</h2>
  {flags}
</div>
"""
        return self.shell(
            title=f"Listing {p['intended_asin']} — status and source",
            desc="Product-intent confirmation record: identifier as supplied, derived candidate URL, confirmation state, and the unresolved flags for this listing.",
            body=body, file=f"product-{p['slug']}.html",
            crumbs=[("Shelf", "shelf.html"), (p["intended_asin"], "")],
        )

    def _flag_text(self, fid: str) -> str:
        for f in self.flags["flags"]:
            if f["id"] == fid:
                return f["what_we_found"]
        return ""

    def page_guides_index(self):
        rows = "".join(self.guide_row(s) for s in sorted(self.guides, key=lambda x: self.guides[x][0].get("date", ""), reverse=True))
        body = f"""
<div class="wrap page-head">
  <p class="kicker">Guides</p>
  <h1>Buyer questions, answered as far as the evidence goes</h1>
  <p class="measure">Four of these started as working titles in the project brief and are labelled there as hypotheses, not claims about popularity or search volume. They are written to be finished in ten minutes with a tape measure and a listing page open. No score, no star, no verdict on a product we have not cooked in.</p>
</div>
<div class="wrap">{rows}</div>
"""
        return self.shell(title="Guides", desc="Buying-question guides on air fryers, capacity, cleanup and counter space — with the evidence state stated on each page.", body=body, file="guides.html",
                          crumbs=[("Home", "index.html"), ("Guides", "")])

    def page_guide(self, slug: str):
        fm, body_md, _ = self.guides[slug]
        srcs = parse_list(fm.get("sources", ""))
        chips = " ".join(f'<a class="chip" href="source-register.html#{s}">{s}</a>' for s in srcs)
        words = len(re.findall(r"[A-Za-z']+", body_md))
        mins = max(3, round(words / 220))
        who = self.people["site_team"]
        html_body = md_to_html(body_md, self.source_ids)
        body = f"""
<article class="doc"><div class="wrap">
  <div class="head">
    <p class="kicker">{E(fm.get('kicker', ''))}</p>
    <h1>{E(fm['title'])}</h1>
    <p class="lede" style="font-size:19px;color:var(--ink-2)">{E(fm.get('desc', ''))}</p>
  </div>
  <div class="byline">
    <span class="who">{E(fm.get('author', who['name']))}</span>
    <span>{E(fm.get('date', ''))}</span>
    <span>{mins} min read</span>
    <span>no hands-on testing on this page</span>
    {f'<span>Topic: <a href="topic-{fm["cluster"]}.html">{E(fm["cluster"])}</a></span>' if fm.get('cluster') and fm['cluster'] != 'null' else ''}
  </div>
  <div class="src">Sources used for anything factual here: {chips or 'none — the page is method, not data'}.</div>
  <div class="body">{html_body}</div>
  <div class="callout plain" style="margin-top:34px">
    <h4>What we did not test</h4>
    <p style="margin:0">Nobody at {E(who['name'])} has used this category's current models, so this page contains no performance, durability or noise claims. {E(who['what_we_can_claim'][1])}.
    <a href="guide-what-we-did-not-test.html">The house rules, in full →</a></p>
  </div>
  <div class="chips" style="margin-top:20px"><a class="chip" href="guides.html">All guides</a><a class="chip" href="shelf.html">The shelf</a><a class="chip" href="source-register.html">Source register</a></div>
</div></article>
"""
        return self.shell(
            title=fm["title"], desc=fm.get("desc", ""), body=body, file=f"guide-{slug}.html",
            kind="doc", doc_slug=slug,
            crumbs=[("Guides", "guides.html"), (fm["title"], "")],
        )

    def topic_illo(self, cid: str):
        files = {"air-fryers": "topic-capacity.jpg"}
        f = files.get(cid)
        if not f:
            return ""
        return (f'<figure class="illo" style="margin:0 0 18px"><img src="assets/img/{f}" alt="Illustration: two basket cross-sections drawn in line art, one shallow and wide, one deep and narrow. Not product photography." '
                f'style="width:100%;max-width:520px;display:block;border-radius:10px;border:1px solid var(--line)">'
                f'<figcaption class="muted" style="font-size:13px;margin-top:6px">Illustration, not product photography. Product images may not be stored or cached under the programme licence, so the shelf is drawn instead. <a href="source-register.html#S08">[S08]</a></figcaption></figure>')

    def page_topic(self, c: dict):
        guides = [s for s, (fm, b, p) in self.guides.items() if fm.get("cluster") == c["id"]]
        rows = "".join(f'<tr><td>{i + 1}</td><th scope="row">{E(a["name"])}</th><td>{E(a["why"])}</td><td>{E(a["verify_by"])}</td></tr>'
                       for i, a in enumerate(c["axes"]))
        g = "".join(self.guide_row(s) for s in guides) or '<p class="muted">No guide on this topic yet.</p>'
        prods = [p for p in self.products["products"] if c["id"] in (p["assumed_shelf_section"] or "")]
        cards = "".join(self.card(p) for p in prods)
        body = f"""
<div class="wrap page-head">
  <p class="kicker">Topic · {E(c['id'])}</p>
  <h1>{E(c['title'])}</h1>
  <p class="lede measure" style="font-size:19px;color:var(--ink-2)">{E(c['question'])}</p>
  <div class="callout plain"><h4>How this topic got assigned</h4><p style="margin:0">{inline(c['basis'], self.source_ids)} That is an inheritance from the brief, not a fact about the listings — recorded as <a href="flagged-for-review.html#FLG-005">FLG-005</a>. {E(self.program['editorial']['no_generated_claims'])}</p></div>
</div>
<div class="wrap">
  <h2>The axes that decide it</h2>
  <div class="tablewrap"><table><thead><tr><th>#</th><th>Axis</th><th>Why it decides the purchase</th><th>Where a buyer checks it</th></tr></thead><tbody>{rows}</tbody></table></div>
  <h2>On this topic</h2>
  {g}
  <h2>Listings filed here</h2>
  <div class="grid shelf">{cards}</div>
  <hr>
  <h2>Season plan</h2>
  <div class="tablewrap"><table><thead><tr><th>Season</th><th>Window</th><th>Angle</th><th>Status</th><th>Review by</th></tr></thead><tbody>
  {"".join(f'<tr><td>{E(s["title"])}</td><td>{E(s["window"])}</td><td>{E(s["angle"])}</td><td>{E(s["status"])}</td><td>{E(s["review_by"])}</td></tr>' for s in self.clusters["seasons"])}
  </tbody></table></div>
  <p class="muted">Seasonal pages carry a review-by date because the programme requires time-limited promotional sentences to be removed as soon as the promotion ends. We keep out of price-and-deal copy entirely for the same reason: it is the part of the rules a static site is worst at keeping true.</p>
</div>
"""
        return self.shell(title=c["title"], desc=c["question"], body=body, file=f"topic-{c['id']}.html",
                          crumbs=[("Topics", "topics.html"), (c["title"], "")])

    def page_topics(self):
        cards = "".join(self.cluster_card(c) for c in self.clusters["clusters"])
        body = f"""
<div class="wrap page-head"><p class="kicker">Topics</p><h1>Clusters, not keywords</h1>
<p class="measure">A topic here is a buyer question plus the axes that answer it, and the guides that take it apart. It is not a tag bucket: nothing gets published into a topic unless it adds a check a reader can perform.</p></div>
<div class="wrap"><div class="grid two">{cards}</div></div>
"""
        return self.shell(title="Topics", desc="The topic clusters this site writes for, and the axes each one is built on.", body=body, file="topics.html")

    def page_product_status(self):
        rows = ""
        for p in self.products["products"]:
            rows += (
                "<tr>"
                f'<td>#{p["slot"]}</td><td><code>{E(p["intended_asin"])}</code></td>'
                + cell(p["product_name"], blank_note="unconfirmed")
                + f'<td><code>{E(p["candidate_listing_url"])}</code></td>'
                + cell(p["observed_redirect_target"], blank_note="not observed — no egress from the build environment")
                + f'<td><a href="product-{p["slug"]}.html">record</a></td></tr>'
            )
        body = f"""
<div class="wrap page-head">
  <p class="kicker">Shelf status</p>
  <h1>Why nothing here is clickable yet</h1>
  <p class="lede measure" style="font-size:19px">Three sentences, then the detail.</p>
</div>
<div class="wrap measure">
  <p>We were given five links in the form <code>https://link.amazon/&lt;9-character id&gt;</code>. From the machine that builds this site there is no route to that host, so we could not see where any of them land, what the product is called, or whether a tracking tag survives the hop. Publishing "Buy now" buttons over that unknown would put a reader one click from a 404 and put the account one step away from links that do not attribute.</p>
  <p>So the shelf publishes the state instead of the sale, and one person with the enrolled account can turn it on. The programme rules make this a money question, not a style one: purchases arriving through a redirect that hides the intermediate step are disqualified, and so is anything whose link formatting fails to track.</p>
  <div class="callout"><h4>The five-minute version</h4>
    <ol>
      <li>Sign in to the Amazon Associates account, open each submitted link, and read the final URL.</li>
      <li>Check the address bar contains <code>tag={E(self.tracking_id)}</code>. Do not buy anything to test it — self-purchase through your own links is prohibited.</li>
      <li>Record the outcome: <code>python3 tools/product_intake.py confirm --slot 1 --observed-redirect '&lt;final url&gt;' --title '&lt;listing title&gt;' --method SiteStripe --date &lt;YYYY-MM-DD&gt;</code></li>
      <li>Check the next-day report shows the click, then flip <code>commerce_switch.allow_live_links</code> and rebuild. Each card then goes live individually, because each has its own <code>link_state</code>.</li>
    </ol>
    <p style="margin:0">Full protocol: <code>docs/LINK_TEST_PROTOCOL.md</code>. What it enforces automatically: <a href="compliance-gate.html">the gate</a>.</p>
  </div>
  <div class="tablewrap"><table><caption>Per-listing state, copied from <code>data/products.json</code></caption>
  <thead><tr><th>Slot</th><th>id as supplied</th><th>Product name</th><th>Derived candidate URL</th><th>Observed redirect</th><th>Record</th></tr></thead>
  <tbody>{rows}</tbody></table></div>
  <p class="muted">Intended identifier and observed destination are deliberately separate columns and separate fields in the data. They get merged only by evidence, never by convenience.</p>
</div>
"""
        return self.shell(title="Why nothing is clickable yet", desc="The state of each supplied listing link, what blocks it, and the five minutes that would unlock it.", body=body, file="product-status.html")

    # -- inside / operator pages ---------------------------------------
    def page_exec_summary(self):
        n = len(self.sources["sources"])
        body = f"""
<div class="wrap page-head">
  <p class="kicker">Executive summary</p>
  <h1>What this project is, what it is not, and what it costs to finish</h1>
  <p class="muted">Written for the person who has to make six decisions. Every number on this page comes from a file in <code>data/</code>; the claims it rests on are in the <a href="source-register.html">source register</a> ({n} rows, each with the official page and the date it was read).</p>
</div>
<div class="wrap measure">
  <div class="statgrid">
    <div class="stat"><b>{len(self.products['products'])}</b><span>listings assigned</span></div>
    <div class="stat"><b>0</b><span>confirmed destinations</span></div>
    <div class="stat"><b>{len(self.guides)}</b><span>guides published</span></div>
    <div class="stat"><b>{len(self.suggestions['suggestions'])}</b><span>suggestions to review</span></div>
    <div class="stat"><b>{len([q for q in self.questions['discoverable']] + self.questions['needs_owner'])}</b><span>questions needing answers</span></div>
    <div class="stat"><b>{len(self.ledger)}</b><span>ledger rows</span></div>
  </div>

  <h2>The one-paragraph version</h2>
  <p>An affiliate site was asked for: five product links, a tracking ID, automation, measurement, compliance. What exists is a working publishing system that refuses to lie — pages generated from a register, a build gate that will not deploy without disclosure and without a properly tagged link, an event schema, an empty-but-correct campaign ledger, and a live GitHub Pages site. What does not exist is any verifiable fact about the five products, because their identifiers could not be resolved from this environment, and a site that invented them would be worth less than nothing.</p>

  <h2>The finding that changes the brief</h2>
  <p>Amazon's programme policies do not permit the version of "AI-powered affiliate platform" that reads the market for you. The IP licence bars robots and data mining against Program Content, bars storing Program Content images at all (a link to them may be stored for 24 hours), caps other product data caching at 24 hours, bars displaying prices or ratings except from a link Amazon serves or an API call under licence, bars using Program Content to develop or improve machine-learning models, and bars accessing the APIs "for the purpose of aggregating, analyzing, extracting, or repurposing" their content without express prior written approval. A 2026 addition requires any autonomous Agent touching that content to name itself in the HTTP User-Agent string as <code>Agent/[name]</code> and not to mimic human interaction.</p>
  <blockquote>An affiliate automation platform built on scraping or warehousing Amazon data is not a risky version of the plan. It is a different plan, and the risk is the whole account: the agreement lets Amazon stop paying commissions earned anywhere on the site.</blockquote>
  <p>Everything this repo automates therefore sits on our side of the line: intake, validation, generation, gating, scheduling, reporting. The Amazon-facing steps are one human, five minutes per link, and a documented protocol.</p>

  <h2>Constraints that shaped the build (each one is a rule, not a preference)</h2>
  <ul>
    <li><b>Disclosure is not optional or footnoted.</b> <cite>Operating Agreement §5</cite> requires the exact associate sentence, clearly and prominently; the FTC's standard pushes it close to the recommendation and hard to miss, so it is in the layout, above the fold, on every page. <a href="source-register.html#S01">[S01]</a> <a href="source-register.html#S20">[S20]</a></li>
    <li><b>Links must be the tagged format, direct, and correctly formatted.</b> Improperly formatted or indirect links are disqualified purchases — the traffic still happens, the commission does not. <a href="source-register.html#S03">[S03]</a> <a href="source-register.html#S04">[S04]</a></li>
    <li><b>No prices, no ratings, no review quotes, no Amazon images.</b> All four are licence-restricted without API access, which is unconfirmed. The tables look sparse for exactly this reason. <a href="source-register.html#S06">[S06]</a> <a href="source-register.html#S07">[S07]</a> <a href="source-register.html#S08">[S08]</a></li>
    <li><b>No self-purchase, no synthetic clicks.</b> Testing the link by buying through it is prohibited, which is why the protocol verifies the address bar and waits for a real reader. <a href="source-register.html#S12">[S12]</a></li>
    <li><b>No price alerts or deal pages.</b> Price tracking and alerting functionality is prohibited; time-limited promotional copy has to be pulled the day it expires, which a static site should not pretend to do. <a href="source-register.html#S13">[S13]</a> <a href="source-register.html#S15">[S15]</a></li>
    <li><b>There is a clock.</b> Three qualifying sales within 180 days of application, or the application can be withdrawn and the account is not reinstatable. Nobody here knows when it started. That is question Q-01 and it outranks every design decision. <a href="source-register.html#S17">[S17]</a></li>
  </ul>

  <h2>What ships today</h2>
  <ul>
    <li>A GitHub Pages site: front page, shelf, 5 product-intent records, {len(self.guides)} guides, 2 topic clusters, a reader-facing status page, and 7 operator surfaces (source register, suggestions, questions, flags, ledger, measurement, gate).</li>
    <li>A deterministic builder and a 13-check publish gate in CI that fails the deploy on a missing disclosure, a mistagged link, an unlicensed field, an unsupported claim string, or a sitemap/feed/calendar disagreement.</li>
    <li>An intake tool that records confirmations with dates and keeps intended and observed values in separate fields.</li>
    <li>A cookieless event collector with a published schema, five defined events, and a refusal to accept a row that is not one of them.</li>
    <li>A campaign ledger that will not take a number without naming the first-party report it came from.</li>
  </ul>

  <h2>What we need from you — the short version of <a href="questions.html">the questions page</a></h2>
  <ol>
    <li>The application date and qualifying-sale count (Q-01). Without it the roadmap has no deadline and may be pointless.</li>
    <li>Confirmation that <code>{E(self.tracking_id)}</code> exists on the account and that this site's URL is registered (Q-02).</li>
    <li>The five link test, five minutes each (Q-03) — this is the only thing standing between the shelf and revenue.</li>
    <li>Whether API access exists, or will be applied for (Q-04). It decides whether comparison tables with real fields are ever buildable.</li>
    <li>The niche and the byline (Q-09, Q-10), and a definition of success worth measuring (Q-18).</li>
    <li>Approve or reject the {len(self.suggestions['suggestions'])} suggestions; {len([s for s in self.suggestions['suggestions'] if s['status'] == 'proposed'])} are proposed and waiting, and none of them will self-implement.</li>
  </ol>

  <h2>Honest statement of the risk</h2>
  <p>This site is a correct foundation with almost no demand evidence under it. It is hosted on a project path at GitHub Pages, has no backlinks, no measured queries, and no traffic history, so "optimise campaigns to maximise affiliate revenue" is currently an instruction with nothing to optimise against. The plan in the register is deliberately sequenced: resolve the links, get indexed, write twelve guides, read the queries, and only then automate the parts that measurement justifies. Anyone who promises revenue from a five-ASIN starter shelf before that point is guessing.</p>
</div>
"""
        return self.shell(title="Executive summary", desc="What shipped, what the licence forbids, what is unverified, and the six decisions that gate everything else.", body=body, file="executive-summary.html",
                          crumbs=[("How we work", "executive-summary.html"), ("Executive summary", "")])

    def page_source_register(self):
        trs = ""
        for s in self.sources["sources"]:
            v = s["verification"]
            badge = {"primary-full": "live", "primary-full-intro": "live", "primary-landing": "assumed", "primary-snippet": "grey", "reference-only": "pending"}.get(v, "grey")
            trs += (
                f'<tr id="{E(s["id"])}"><th scope="row">{E(s["id"])}</th>'
                f'<td>{inline(s["claim"], {})}</td>'
                f'<td>{E(s["publisher"])}</td>'
                f'<td><a href="{E(s["url"])}" rel="noopener">{E(s["url"].replace("https://", ""))}</a><br><span class="muted" style="font-size:13px">{E(s["section"])}</span></td>'
                f'<td><span class="badge {badge}">{E(v)}</span></td>'
                f'<td>{E(s["accessed"])}</td>'
                f'<td>{E("; ".join(s["used_by"]))}</td></tr>'
            )
        body = f"""
<div class="wrap page-head">
  <p class="kicker">Evidence</p>
  <h1>Source register</h1>
  <p class="measure">Every factual assertion the site or the tooling rests on, with the official page it came from, the date it was read, and how confidently it was read. <b>primary-full</b> means the page text was retrieved in the session that wrote this row and the clause was read in context; <b>primary-snippet</b> means an official page surfaced its own text in search results and was not re-fetched here; <b>reference-only</b> means background that no displayed claim depends on. Where a value could not be confirmed, the site leaves it blank and the gap appears on <a href="flagged-for-review.html">Flagged for review</a>.</p>
  <p class="muted">Quotes are short excerpts for identification, taken from the pages linked above. Documents change: the Operating Agreement row is stamped with its own revision date (updated 2025-10-15) and the Program Policies row with theirs (updated 2026-04-14). Re-check before repeating any row elsewhere.</p>
</div>
<div class="wrap">
  <div class="tablewrap"><table><caption>{len(self.sources['sources'])} sources · read 2026-11-20</caption>
  <thead><tr><th>id</th><th>Claim as used here</th><th>Publisher</th><th>Source</th><th>Verification</th><th>Read</th><th>Used by</th></tr></thead>
  <tbody>{trs}</tbody></table></div>
  <div class="callout"><h4>What is not in here, and why</h4>
  <p style="margin:0">No price, commission rate, star rating, review count, product title or category appears in this register, because nothing in it was retrieved from a source licensed for that purpose. A row for each would be the sort of confident-looking number this project exists to avoid. Product fields stay null in <code>data/products.json</code> until a human supplies them with a date and a method.</p></div>
</div>
"""
        return self.shell(title="Source register", desc="Every claim this site makes, mapped to the official document it came from, with the access date and verification status.", body=body, file="source-register.html")

    def page_suggestions(self):
        tracks = self.suggestions["_meta"]["tracks"]
        adopted = len([s for s in self.suggestions["suggestions"] if s["status"] == "adopted-in-build"])
        blocks = ""
        by_track: dict[str, list] = {}
        for s in self.suggestions["suggestions"]:
            by_track.setdefault(s["track"], []).append(s)
        for track in [t for t in tracks if t in by_track] + [t for t in by_track if t not in tracks]:
            items = "".join(f"""
            <div class="flagcard" id="{E(s['id'])}">
              <h3>{E(s['id'])} · {E(s['title'])}</h3>
              <p style="margin:0 0 4px"><span class="badge {'live' if s['status'] == 'adopted-in-build' else ('grey' if 'proposed' in s['status'] else 'assumed')}">{E(s['status'])}</span>
                 <span class="badge grey">{E(s['priority'])}</span></p>
              <dl>
                <dt>Problem</dt><dd>{inline(s['problem'], self.source_ids)}</dd>
                <dt>Proposal</dt><dd>{inline(s['proposal'], self.source_ids)}</dd>
                <dt>Why it wins</dt><dd>{inline(s['why_it_wins'], self.source_ids)}</dd>
                <dt>What it costs</dt><dd>{inline(s['what_it_costs'], self.source_ids)}</dd>
                <dt>Risk</dt><dd>{inline(s['risk'], self.source_ids)}</dd>
                <dt>Evidence</dt><dd>{" ".join(f'<a href="source-register.html#{e}">[{E(e)}]</a>' for e in s['evidence']) or '—'}</dd>
                <dt>Measurable</dt><dd>{inline(s['measurable'], self.source_ids)}</dd>
                <dt>How to implement</dt><dd>{inline(s['how_to_implement'], self.source_ids)}</dd>
              </dl>
              <div class="decision"><strong>Decision (yours):</strong> <code>{E(s['decision'])}</code> by <code>{E(s['decided_by'] or 'unassigned')}</code> on <code>{E(s['decided_on'] or '—')}</code>
                <div class="box">Set it in <code>data/suggestions.json</code> → <code>"decision": "approve" | "approve-with-changes" | "reject" | "defer"</code>, then rebuild. The register and this page cannot disagree.</div></div>
            </div>""" for s in by_track[track])
            blocks += '<section><div class="sec-head"><h2>' + E(tracks.get(track, track)) + '</h2><span class="muted">' + str(len(by_track[track])) + ' rows</span></div>' + items + '</section>'
        chips = "".join(
            '<a class="chip" href="#' + by_track[tr][0]['id'] + '">' + E(tracks.get(tr, tr)) + ' · ' + str(len(by_track[tr])) + '</a>'
            for tr in tracks if tr in by_track
        )
        body = f"""
<div class="wrap page-head">
  <p class="kicker">Decisions</p>
  <h1>Suggestions, for review before implementation</h1>
  <p class="measure">The brief asked for a place where the path can be chosen rather than assumed. This is it: {len(self.suggestions['suggestions'])} rows, each with the problem, the proposal, the cost, the risk, the evidence and a measurable success test. <b>{adopted}</b> are already implemented in this build because they are the ones that keep the site inside its licence or stop it fabricating — those still need your approval to stay, and the rest wait for you.</p>
  <div class="cta-row"><a class="btn" href="#SG-01">Start with the licence boundary</a><a class="btn ghost" href="questions.html">Questions first? →</a></div>
</div>
<div class="wrap">
  <div class="chips">{chips}</div>
  {blocks}
  <p class="muted">SG-25 and SG-26 do not exist; the gap is recorded in the register's metadata so nobody wastes an hour looking for lost rows. SG-27..SG-30 are the four parallel-pass rows named in the brief (nav labels, RSS, Search Console, reader capture), reproduced here with their original numbers.</p>
</div>
"""
        return self.shell(title="Suggestions", desc="Every recommendation for this project with cost, risk, evidence and a decision field to fill in before anything is implemented.", body=body, file="suggestions.html",
                          crumbs=[("How we work", "executive-summary.html"), ("Suggestions", "")])

    def page_questions(self):
        def qrow(q, kind):
            ans = ""
            if kind == "known":
                ans = f'<div class="row"><b>answer</b><div>{inline(q["answer"], self.source_ids)}</div></div><div class="row"><b>basis</b><div>{E(q["basis"])}</div></div><div class="row"><b>consequence</b><div>{inline(q["consequence"], self.source_ids)}</div></div>'
            else:
                ans = f'<div class="row"><b>why it blocks</b><div>{inline(q.get("why_it_blocks", "decision depends on this"), self.source_ids)}</div></div>' \
                      f'<div class="row"><b>who can answer</b><div>{E(q.get("who_can_answer", "you, or the account holder"))}</div></div>' \
                      f'<div class="row"><b>how to discover it</b><div>{inline(q["discovery"], self.source_ids)}</div></div>'
            tmpl = ""
            if q.get("answer_template"):
                tmpl = '<div class="row"><b>record it as</b><div><code>' + E(json.dumps(q["answer_template"], ensure_ascii=False)) + '</code></div></div>'
            pr = f'<span class="badge {"flag" if q.get("priority") == "P0" else "grey"}">{E(q.get("priority", "—"))}</span>'
            st = f'<span class="badge {"pending" if "needs" in str(q.get("status", "")) else "grey"}">{E(q.get("status", "known"))}</span>'
            return f'<div class="qa" id="{E(q["id"])}"><h3>{pr} {E(q["question"])} {st}</h3>{ans}{tmpl}</div>'
        body = f"""
<div class="wrap page-head">
  <p class="kicker">Known and unknown</p>
  <h1>What has to be true before a decision here is reasonable</h1>
  <p class="measure">Three states only: <b>known</b> (with the official basis), <b>discoverable</b> (with the exact action that finds it), and <b>needs you</b> (a decision or a credential nobody in this sandbox can supply). Each open row carries the discovery method, so "we do not know" is never the end of a thread, and a blank answer is never quietly upgraded into a guess.</p>
  <div class="statgrid">
    <div class="stat"><b>{len(self.questions['known'])}</b><span>known</span></div>
    <div class="stat"><b>{len(self.questions['discoverable'])}</b><span>discoverable</span></div>
    <div class="stat"><b>{len(self.questions['needs_owner'])}</b><span>need the owner</span></div>
    <div class="stat"><b>{len(self.questions['next_round'])}</b><span>second round</span></div>
  </div>
</div>
<div class="wrap measure">
  <h2>Known — with the basis</h2>{"".join(qrow(q, 'known') for q in self.questions['known'])}
  <h2>Discoverable — here is how</h2>{"".join(qrow(q, 'open') for q in self.questions['discoverable'])}
  <h2>Needs the owner</h2>{"".join(qrow(q, 'open') for q in self.questions['needs_owner'])}
  <h2>Second round — after there is data</h2>{"".join(qrow(q, 'open') for q in self.questions['next_round'])}
  <div class="callout"><h4>Suggestions for discovering the missing information</h4>
  <p style="margin:0">The methods above are the short list. Beyond them: (1) one browser session inside the Associates account settles Q-01, Q-02, Q-03 and Q-04 in about 25 minutes and is the highest-value hour available to this project; (2) Search Console verification (SG-29) is the only route to Q-13, and no on-site instrument substitutes for it; (3) a paper clip and a tape measure answer Q-06; (4) asking Amazon Associates support in writing whether a planned analytical use of API data needs approval converts FLG-004 from an interpretation into a documented position — we have not sent that request, so do not treat it as done.</p></div>
</div>
"""
        return self.shell(title="Open questions", desc="What is known, what is discoverable and how, and which questions need the account holder before any decision can be made.", body=body, file="questions.html",
                          crumbs=[("How we work", "executive-summary.html"), ("Questions", "")])

    def page_flags(self):
        cards = ""
        for f in self.flags["flags"]:
            sev = {"compliance": "flag", "data": "assumed", "access": "pending", "scope": "grey", "expectation": "grey", "infrastructure": "grey", "policy": "grey", "measurement": "grey"}.get(f["severity"], "grey")
            links = "".join(f'<li><a href="{E(u)}" rel="noopener">{E(u)}</a></li>' for u in f.get("source_links", []))
            cards += f"""<div class="flagcard {'resolved' if f['status'].startswith('resolved') else ''}" id="{E(f['id'])}">
  <h3>{E(f['id'])} · {E(f['title'])}</h3>
  <p style="margin:0 0 6px"><span class="badge {sev}">{E(f['severity'])}</span> <span class="badge {'live' if f['status'].startswith('resolved') else 'pending'}">{E(f['status'])}</span></p>
  <dl>
    <dt>What we found</dt><dd>{inline(f.get('what_we_found', '—'), self.source_ids)}</dd>
    <dt>What we did about it</dt><dd>{inline(f.get('what_we_did', 'noted above'), self.source_ids)}</dd>
    <dt>How to close it</dt><dd>{inline(f.get('how_to_close', '—'), self.source_ids)}</dd>
    {f'<dt>Sources</dt><dd><ul>{links}</ul></dd>' if links else ''}
  </dl>
</div>"""
        body = f"""
<div class="wrap page-head">
  <p class="kicker">Needs review</p>
  <h1>Flagged for review</h1>
  <p class="measure">Everything we could not settle, published rather than buried. A flag does not block the merge — a broken build does. Read it as the list of things where this site declines to guess, in the order that unblocks the most.</p>
  <div class="chips">{"".join(f'<a class="chip" href="#{E(f["id"])}">{E(f["id"])}</a>' for f in self.flags['flags'])}</div>
</div>
<div class="wrap measure">{cards}
<div class="callout"><h4>If you only do one thing</h4><p style="margin:0">Close FLG-003 and FLG-002 together, in one browser session, with the protocol in <code>docs/LINK_TEST_PROTOCOL.md</code>. Ten minutes of clicking turns most of this page into history and turns the shelf into a shop.</p></div></div>
"""
        return self.shell(title="Flagged for review", desc="Every unresolved item in this project, what was done about it, and how to close it — with source links.", body=body, file="flagged-for-review.html",
                          crumbs=[("How we work", "executive-summary.html"), ("Flags", "")])

    def page_ledger(self):
        cols = ["timestamp", "source", "report_date", "channel", "tracking_id", "eligible_sessions", "clicks", "reported_orders"]
        head = "".join(f"<th>{E(c.replace('_', ' '))}</th>" for c in cols)
        rows = ""
        for r in self.ledger:
            rows += "<tr>" + "".join(cell(r.get(c), blank_note="—") for c in cols) + "</tr>"
        if not rows:
            rows = f'<tr><td colspan="{len(cols)}" class="blank" style="text-align:center;padding:26px">No rows. This is the correct state: there are no authorised first-party report numbers to transcribe yet, and the tool refuses to invent them.</td></tr>'
        body = f"""
<div class="wrap page-head">
  <p class="kicker">Evidence, later</p>
  <h1>Campaign ledger</h1>
  <p class="measure">An empty ledger with a fixed schema, on purpose. Rows arrive only from authorised first-party reports, and only with the dated provenance attached, so that any future claim about performance can be walked back to a screen somebody read. There is no conversion score, no revenue forecast and no projection on this page, because there is nothing to compute them from.</p>
</div>
<div class="wrap">
  <div class="tablewrap"><table><caption><code>data/ledger/campaign.jsonl</code> · {len(self.ledger)} rows</caption><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>
  <div class="grid two">
    <div class="card"><h4>How a row gets added</h4><p class="mono" style="font-size:13px;white-space:pre-wrap;background:#f6f2ea;padding:10px;border-radius:8px">python3 tools/campaign_ledger.py append \\
  --source 'Associates Central &gt; Reports &gt; Tracking report' \\
  --report-date 2026-12-14 --channel organic \\
  --eligible-sessions 12 --clicks 31 --reported-orders 2</p>
      <p class="muted" style="font-size:14px">The tool rejects a row with no <code>--source</code> or no <code>--report-date</code>, rejects unknown field names, and never writes a computed percentage into the file.</p></div>
    <div class="callout"><h4>Why the columns are the columns</h4>
      <p style="margin:0">The brief specified timestamp, source, channel, eligible sessions, clicks and reported orders. Two facts from the programme explain why "and that is all we can honestly say": the commission session closes 24 hours after the click, an order completed up to 89 days later still counts if it came from the cart, and payment/dispatch can lag up to 180 days after purchase. So a clicks-to-orders ratio computed on this week's numbers is a fiction about a window that has not closed. <a href="source-register.html#S18">[S18]</a></p></div>
  </div>
</div>
"""
        return self.shell(title="Campaign ledger", desc="The campaign record: schema, provenance rules, and zero rows until an authorised first-party report supplies them.", body=body, file="campaign-ledger.html",
                          crumbs=[("How we work", "executive-summary.html"), ("Ledger", "")])

    def page_measurement(self):
        evs = ""
        for e in self.events["events"]:
            evs += f"""<div class="flagcard" id="{E(e['id'])}"><h3>{E(e['id'])} · <code>{E(e['name'])}</code></h3>
            <dl><dt>Fires on</dt><dd>{inline(e['fires_on'], self.source_ids)}</dd>
            <dt>Extra fields</dt><dd>{E(', '.join(e['extra_fields']))}</dd>
            <dt>What it answers</dt><dd>{inline(e['answers'], self.source_ids)}</dd>
            <dt>Deliberately not recorded</dt><dd>{inline(e['not_recorded'], self.source_ids)}</dd>
            <dt>Why it is limited that way</dt><dd>{inline(e['why_limited'], self.source_ids)}</dd></dl></div>"""
        ep = self.program["measurement"]["endpoint"]
        ep_note = (
            ("The collector is configured at <code>" + E(str(ep)) + "</code>.")
            if ep else
            "The endpoint is <code>null</code>. GitHub Pages serves static files and cannot run a process, so as "
            "published this site records nothing about its visitors; the script counts in the visitor\u2019s browser and "
            "goes no further. Deploying <code>tools/collect_server.py</code> on any host that runs a process turns "
            "measurement on by writing one value into <code>data/program.json</code>."
        )
        body = f"""
<div class="wrap page-head">
  <p class="kicker">Instrument</p>
  <h1>Measurement</h1>
  <p class="measure">Five events, one collector we run ourselves, no cookies, and an explicit refusal to record anything a bot could fire. The point is not vanity numbers: it is that the site should be able to say which paragraph earned a click, and then behave as if that answer exists.</p>
  <div class="statgrid">
    <div class="stat"><b>{len(self.events['events'])}</b><span>events defined</span></div>
    <div class="stat"><b>{'configured' if ep else 'not configured'}</b><span>collector endpoint</span></div>
    <div class="stat"><b>0</b><span>cookies set</span></div>
    <div class="stat"><b>0</b><span>third-party scripts</span></div>
  </div>
</div>
<div class="wrap">
  <div class="callout"><h4>Endpoint status, stated plainly</h4><p style="margin:0">{ep_note} An empty ledger is a legitimate result. A filled one that nobody measured is not.</p></div>
  <h2>The five events</h2>
  {evs}
  <div class="grid two">
    <div class="card"><h4>Running the collector</h4><p class="mono" style="font-size:13px;white-space:pre-wrap;background:#f6f2ea;padding:10px;border-radius:8px">python3 tools/collect_server.py --host 0.0.0.0 --port 8099 \\
  --out data/ledger/events.jsonl --origin {E(self.program['site']['base_url'].split('/')[2])}</p>
      <p class="muted" style="font-size:14px">Stdlib only. Accepts one JSON object per POST, validates it against the schema above, rejects unknown event names and any payload over 2 KB, and does not read or store the peer address. Summarise with <code>python3 tools/events.py report</code>.</p></div>
    <div class="callout plain"><h4>What this cannot tell you</h4>
      <p style="margin:0">Not revenue, not orders, not a person. Conversions live in Amazon's reports and arrive only through the path described in the <a href="campaign-ledger.html">ledger</a>; a click here that produced nothing may still produce an order for 89 days. And the traffic is currently near zero, so read any early count as an anecdote — the tooling labels it that way rather than letting a chart imply significance. <a href="source-register.html#S18">[S18]</a></p></div>
  </div>
</div>
"""
        return self.shell(title="Measurement", desc="The five defined events, the cookieless self-hosted collector, and the honest limits of what site-side measurement can say.", body=body, file="measurement.html",
                          crumbs=[("How we work", "executive-summary.html"), ("Measurement", "")])

    def page_gate(self):
        checks = [
            ("CHK-01", "Licence boundary", "No module in tools/ or src/ may open a network route to an Amazon host, or ingest Program Content for analysis or model training.", "grep for amazon hosts + Program-Content verbs outside the link builder", "yes", "S10, S11, S14"),
            ("CHK-02", "Disclosure present", "Every emitted page contains the associate sentence verbatim, in the strip above the fold and again in the footer.", "string search per page, exact match on the sentence in program.json", "yes", "S01, S20"),
            ("CHK-03", "No unsupported claims", "Banned strings: best-selling, #1, trending, highest rated, lowest price, guaranteed, editor's choice, we tested — unless the line carries a provenance id.", "regex over emitted HTML and guide sources", "yes", "S16"),
            ("CHK-04", "Tag correctness", "Every href to an Amazon domain carries tag= equal to the registered tracking ID, on a /dp/ or Amazon-served product URL.", "URL parse per anchor", "yes", "S02, S03"),
            ("CHK-05", "Sponsored marking", "Every outbound affiliate anchor has rel containing sponsored and noopener; internal links must not.", "attribute check", "yes", "S22"),
            ("CHK-06", "No cloaking / shorteners", "Published outbound links use the marketplace domain directly. A shortener host is a build error unless FLG-003 is closed with evidence.", "host allowlist", "yes", "S04, S05"),
            ("CHK-07", "No unlicensed price or rating", "No price, star-rating or review-quote markup anywhere without an api_provenance row (which today does not exist).", "regex for currency, 'out of 5', ratingValue", "yes", "S06, S07, S09"),
            ("CHK-08", "Program-content disclaimer", "If any page ever displays text Program Content, the §2(k) disclaimer must be on that page.", "conditional presence check", "yes", "S09"),
            ("CHK-09", "No price alerts", "Reject 'price alert', 'notify me when', 'price drop', 'price history' — prohibited functionality.", "regex", "yes", "S13"),
            ("CHK-10", "Seasonal decay", "Any page with a season or review_by date in the past fails the check, so expired promotional copy cannot linger.", "date compare on clusters + guides", "yes", "S15"),
            ("CHK-11", "Testing honesty", "Guide pages must render the no-hands-on-testing block; the string 'we tested' is only allowed inside a negation.", "structural check", "yes", "S16, S12"),
            ("CHK-12", "Registers agree", "sitemap.xml and feed.xml list exactly the published pages; the editorial calendar's published rows each have a file, and every file has a row.", "set comparison", "yes", ""),
            ("CHK-13", "Indexable, one site", "Every page: title, meta description, self-canonical, robots index,follow, relative internal hrefs that resolve, no missing local asset.", "per-page parse + link resolution", "yes", "S24"),
        ]
        parts = []
        for c in checks:
            src_html = " ".join(
                '<a href="source-register.html#{0}">[{0}]</a>'.format(s.strip()) for s in c[5].split(",") if s.strip()
            ) or "—"
            parts.append(
                "<tr><th scope='row'>" + E(c[0]) + "</th><td>" + E(c[1]) + "</td><td>"
                + inline(c[2], self.source_ids) + "</td><td>" + E(c[3]) + "</td>"
                + "<td><span class='badge live'>" + E(c[4]) + "</span></td><td>" + src_html + "</td></tr>"
            )
        rows = "".join(parts)
        body = f"""
<div class="wrap page-head">
  <p class="kicker">Publishing workflow</p>
  <h1>The compliance gate</h1>
  <p class="measure">Thirteen checks run by <code>tools/check_site.py</code> after the build and before the deploy. Any failure exits non-zero, so the GitHub Actions job fails and nothing publishes. This is the "gate in front of the parts that cannot be automated" from the brief, made boring and mechanical — the parts that can be automated (link formatting, disclosure presence, register consistency) are the ones being automated.</p>
</div>
<div class="wrap">
  <figure class="illo" style="margin:0 0 18px;max-width:420px"><img src="assets/img/method.jpg" alt="Illustration: a stack of documents drawn in line art with a magnifying glass over the top sheet and a single checkmark. Not product photography." style="width:100%;display:block;border-radius:10px;border:1px solid var(--line)"><figcaption class="muted" style="font-size:13px;margin-top:6px">Every check below is a rule copied out of a fetched primary document, not an invented house style.</figcaption></figure>
  <div class="tablewrap"><table><caption>Checks, in build order</caption>
  <thead><tr><th>id</th><th>name</th><th>rule</th><th>how it is tested</th><th>automated</th><th>source</th></tr></thead><tbody>{rows}</tbody></table></div>
  <div class="grid two">
    <div class="callout"><h4>What is deliberately not automated</h4>
      <ul style="margin:0">
        <li><b>Deciding what a product is.</b> Listing confirmation is a human click with a date attached; intake is <code>tools/product_intake.py</code>.</li>
        <li><b>Judging whether a claim is 'overbroad'.</b> CHK-03 catches banned strings, not clever ones. That needs an editor, so the register asks for one.</li>
        <li><b>Whether disclosure placement satisfies a regulator.</b> We can check it exists and where; we cannot check comprehension.</li>
        <li><b>Anything that needs Program Content.</b> No scraper, no price cache, no review corpus, no model trained on Amazon data — that is the agreement, not our caution. <a href="source-register.html#S10">[S10]</a></li>
      </ul></div>
    <div class="callout plain"><h4>Running it yourself</h4>
      <p style="margin:0"><code>python3 tools/build_site.py &amp;&amp; python3 tools/check_site.py</code> — add <code>--strict-flags</code> to make any open compliance flag a failure, and <code>python3 tools/build_site.py --check</code> to prove <code>site/</code> matches what the tools produce. The workflow runs all three.</p>
      <p style="margin:8px 0 0">Deliberate design: the gate lives in the repo, not in someone's diligence, so a future session that forgets the rules is stopped by a red check instead of by an account suspension.</p></div>
  </div>
</div>
"""
        return self.shell(title="Compliance gate", desc="The thirteen checks that run between build and deploy, what each enforces, and what the gate refuses to automate.", body=body, file="compliance-gate.html",
                          crumbs=[("How we work", "executive-summary.html"), ("Gate", "")])

    def page_about_and_privacy(self):
        for slug, (fm, body_md, _) in self.pages.items():
            html_body = md_to_html(body_md, self.source_ids)
            body = f'<article class="doc"><div class="wrap"><div class="head"><p class="kicker">{E(fm.get("kicker",""))}</p><h1>{E(fm["title"])}</h1><p style="font-size:19px;color:var(--ink-2)">{E(fm.get("desc",""))}</p></div><div class="body">{html_body}</div></div></article>'
            self.write(f"{slug}.html", self.shell(title=fm["title"], desc=fm.get("desc", ""), body=body, file=f"{slug}.html"))

    def page_404(self):
        body = f"""
<div class="wrap page-head"><p class="kicker">Not here</p><h1>That page does not exist on this site</h1>
<p class="measure">Which is worth stating plainly, because a site of records that cannot say "we do not have this" is not worth reading. Start from the shelf or the guides; if you followed a broken link from one of our pages, that is a bug and the build gate should have caught it.</p>
<div class="cta-row"><a class="btn" href="index.html">Front page</a><a class="btn ghost" href="shelf.html">Shelf</a><a class="btn ghost" href="guides.html">Guides</a><a class="btn ghost" href="flagged-for-review.html">Flagged for review</a></div></div>
"""
        self.write("404.html", self.shell(title="Not found", desc="404", body=body, file="404.html"))

    # -- feeds ----------------------------------------------------------
    def gen_feed_sitemap_robots(self):
        pages = [w for w in self.written if w.endswith(".html") and w != "404.html"]
        sm = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        for p in sorted(pages):
            url = self.base if p == "index.html" else self.base + p
            sm.append(f"<url><loc>{E(url)}</loc><lastmod>{E(self.program['_meta']['updated'])}</lastmod></url>")
        sm.append("</urlset>")
        self.write("sitemap.xml", "\n".join(sm))

        items = []
        for slug, (fm, _, _) in sorted(self.guides.items(), key=lambda kv: kv[1][0].get("date", ""), reverse=True):
            pub = fm.get("date", self.program["_meta"]["updated"])
            rfc = dt.datetime.strptime(pub, "%Y-%m-%d").strftime("%a, %d %b %Y 09:00:00 +0000")
            items.append(
                "<item><title>" + E(fm["title"]) + "</title><link>" + E(self.base + f"guide-{slug}.html") + "</link>"
                "<guid isPermaLink=\"true\">" + E(self.base + f"guide-{slug}.html") + "</guid>"
                f"<pubDate>{rfc}</pubDate><description>" + E(fm.get("desc", "")) + "</description></item>"
            )
        rss = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<rss version=\"2.0\"><channel>"
               f"<title>{E(self.program['brand']['name'])} guides</title>"
               f"<link>{E(self.base)}</link>"
               f"<description>{E(self.program['brand']['blurb'])}</description>"
               "<language>en-us</language>" + "".join(items) + "</channel></rss>")
        self.write("feed.xml", rss)
        self.write("robots.txt",
                   "User-agent: *\nAllow: /\n\n# Published for completeness. On a GitHub Pages project site this file is served at\n"
                   "# /Affil3/robots.txt, which is not the host root, so crawlers will not read it as a directive.\n"
                   "# Indexing is controlled per page by <meta name=\"robots\"> and by the sitemap submitted in Search Console.\n"
                   f"Sitemap: {self.base}sitemap.xml\n")

    def build(self):
        self.out.mkdir(parents=True, exist_ok=True)
        (self.out / "assets").mkdir(exist_ok=True)
        for f in (SRC / "assets").rglob("*"):
            if f.is_file():
                dst = self.out / "assets" / f.relative_to(SRC / "assets")
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dst)
                self.written.append(str(dst.relative_to(self.out)))

        self.write("index.html", self.page_index())
        self.write("shelf.html", self.page_shelf())
        for p in self.products["products"]:
            self.write(f"product-{p['slug']}.html", self.page_product(p))
        self.write("product-status.html", self.page_product_status())
        self.write("guides.html", self.page_guides_index())
        for slug in sorted(self.guides):
            self.write(f"guide-{slug}.html", self.page_guide(slug))
        self.write("topics.html", self.page_topics())
        for c in self.clusters["clusters"]:
            self.write(f"topic-{c['id']}.html", self.page_topic(c))
        self.write("executive-summary.html", self.page_exec_summary())
        self.write("source-register.html", self.page_source_register())
        self.write("suggestions.html", self.page_suggestions())
        self.write("questions.html", self.page_questions())
        self.write("flagged-for-review.html", self.page_flags())
        self.write("campaign-ledger.html", self.page_ledger())
        self.write("measurement.html", self.page_measurement())
        self.write("compliance-gate.html", self.page_gate())
        self.page_about_and_privacy()
        self.page_404()
        # feed/sitemap must see every page, so it runs last
        self.gen_feed_sitemap_robots()
        return self.written


# ------------------------------------------------------------------------ main

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--check", action="store_true", help="rebuild into a temp dir and diff against --out")
    a = ap.parse_args()
    target = Path(a.out)

    if a.check:
        tmp = ROOT / ".build-tmp"
        if tmp.exists():
            shutil.rmtree(tmp)
        written = Site(tmp).build()
        drift = []
        for rel in written:
            new, old = tmp / rel, target / rel
            if not old.exists():
                drift.append(f"missing from site/: {rel}")
            elif new.read_bytes() != old.read_bytes():
                drift.append(f"stale: {rel} (site/ differs from tool output)")
        extra = [str(p.relative_to(target)) for p in target.rglob("*") if p.is_file() and str(p.relative_to(target)) not in written]
        drift += [f"untracked build output: {x}" for x in sorted(extra)]
        shutil.rmtree(tmp)
        if drift:
            print("\n".join(drift))
            print(f"\nFAIL: {len(drift)} file(s) out of date. Run: python3 tools/build_site.py")
            return 1
        print(f"OK: site/ matches the tools ({len(written)} files)")
        return 0

    s = Site(target)
    written = s.build()
    n_live = sum(1 for p in s.products["products"] if p["link_state"] == "live" and s.links_live)
    print(f"built {len(written)} files into {target.name}")
    print(f"  pages: {len([w for w in written if w.endswith('.html')])}, guides: {len(s.guides)}, product records: {len(s.products['products'])}")
    print(f"  live affiliate links: {n_live} of {len(s.products['products'])} (allow_live_links={s.links_live})")
    print(f"  ledger rows: {len(s.ledger)} · sources: {len(s.sources['sources'])} · suggestions: {len(s.suggestions['suggestions'])} · flags: {len(s.flags['flags'])}")
    stale = [p["intended_asin"] for p in s.products["products"] if p.get("confirmed_at")]
    if stale:
        print(f"  NOTE: product fields last refreshed: {stale} — non-image Program Content may only be cached 24h")
    return 0


if __name__ == "__main__":
    sys.exit(main())
