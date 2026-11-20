#!/usr/bin/env python3
"""Render the four register-driven pages of the Affil3 site from data/*.json.

Why this exists: the brief asks to automate what can be automated and to put a gate in front of
what cannot. Registers are the source of truth; the HTML is a build artefact. Hand-editing a
generated page is a mistake the validator will catch (its --check mode fails when committed HTML
differs from the build), so data and prose cannot drift apart.

Usage:
    python3 scripts/build_registers.py          # write pages
    python3 scripts/build_registers.py --check  # exit non-zero if pages are stale
"""
from __future__ import annotations

import html
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# --- navigation: one group, reachable from the footer on every page ---------------------------
NAV = [
    ("index.html", "Home"),
    ("shop.html", "Shop"),
    ("products.html", "Products"),
    ("guides/index.html", "Guides"),
    ("verification.html", "Link evidence"),
    ("suggestions.html", "Decision room"),
    ("questions.html", "Open questions"),
    ("flagged.html", "Flagged"),
    ("disclosure.html", "Disclosure"),
    ("privacy.html", "Privacy"),
    ("about.html", "About"),
]

DISCLOSURE = (
    "<strong>Disclosure:</strong> As an Amazon Associate, we earn from qualifying purchases. "
    "If you buy through our links we may earn a commission at no extra cost to you. Every "
    "outbound product link is marked <code>rel=\"sponsored\"</code>. "
    '<a href="disclosure.html">Why we word it this way &rarr;</a>'
)


def e(value) -> str:
    """Escape for HTML, rendering empty values as the site's blank marker."""
    if value is None or value == "":
        return '<span class="blank">&mdash; not confirmed</span>'
    return html.escape(str(value))


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def page(fname: str, title: str, description: str, current: str, body: str) -> str:
    nav_lines = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == current else ""
        nav_lines.append(f'    <a href="{href}"{cur}>{label}</a>')
    nav = "\n".join(nav_lines)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} &mdash; Affil3</title>
<meta name="description" content="{html.escape(description)}">
<link rel="stylesheet" href="assets/css/main.css">
<link rel="canonical" href="https://karagemop466-tech.github.io/Affil3/{fname}">
<link rel="sitemap" type="application/xml" href="sitemap.xml">
<link rel="alternate" type="application/rss+xml" title="Affil3 &mdash; Recent guides" href="feed.xml">
</head>
<body>
<header class="masthead">
  <div class="wrapper">
    <div class="brand"><a href="index.html">Affil3</a></div>
    <p class="dek">Buyer questions first. Verified links second. Nothing invented.</p>
  </div>
  <div class="disclosure-strip" role="region" aria-label="Affiliate disclosure">
    {DISCLOSURE}
  </div>
  <nav class="navgroup" aria-label="Main navigation">
  <div class="wrapper">
{nav}
  </div>
  </nav>
</header>
<main>
<div class="wrapper">
{body}
</div>
</main>
<footer>
  <div class="wrapper">
    <div class="disclosure-strip footer-strip" role="region" aria-label="Affiliate disclosure">
      {DISCLOSURE}
    </div>
    <nav class="navgroup" aria-label="Site navigation (footer)">
{nav}
    </nav>
    <p class="small">Associates tracking ID <code>shopnow047c-20</code>, unconfirmed against the
    Associates account (see <a href="questions.html#Q-02">Q-02</a>) &bull;
    <a href="sitemap.xml">Sitemap</a> &bull; <a href="feed.xml">RSS</a> &bull;
    <a href="verification.html">Link evidence register</a> &bull;
    <a href="flagged.html">Flagged for review</a></p>
  </div>
</footer>
</body>
</html>
"""


# --- verification.html --------------------------------------------------------------------------
def build_verification() -> str:
    reg = load("link-verification.json")
    rows = []
    for r in reg["records"]:
        flags = ", ".join(
            f'<a href="flagged.html">{f}</a>' for f in r["flags"]
        ) or '<span class="blank">&mdash;</span>'
        out = r["outcome"].replace("-", " ")
        cls = "unverified" if r["outcome"] != "resolved-to-different-asin" else "unverified"
        rows.append(f"""      <tr>
        <td><b>{e(r['id'])}</b></td>
        <td class="url-wrap">{e(r['submitted_url'])}</td>
        <td><code>{e(r['submitted_token'])}</code><br><span class="small">{r['submitted_token_length']} chars</span></td>
        <td>{e(r['intended_asin'])}</td>
        <td>{e(r['intended_listing_url'])}</td>
        <td>{e(r['confirmation_date'])}</td>
        <td class="url-wrap">{e(r['observed_asin'])}</td>
        <td>{e(r['observed_page_title'])}</td>
        <td>{e(" &gt; ".join(r['observed_breadcrumb']))}</td>
        <td><span class="{cls}">{e(out)}</span></td>
        <td>{e(r['observed_at_utc'])}</td>
        <td><a href="{e(r['review_link'])}" rel="sponsored nofollow noopener noreferrer" target="_blank">open</a></td>
        <td class="small">{flags}</td>
      </tr>""")

    observed = []
    for o in reg["observations"]:
        observed.append(
            f'      <li><b>{e(o["id"])}</b> &mdash; {e(o["observation"])}<br>'
            f'      <span class="small">Status: {e(o["status"])} &bull; Source: '
            f'<a href="{e(o["source"])}" rel="noopener noreferrer" target="_blank">{e(o["source"])}</a></span></li>'
        )

    controls = "\n".join(
        f'      <tr><td><b>{e(c["id"])}</b></td><td>{e(c["purpose"])}</td>'
        f'<td class="url-wrap">{e(c["request"])}</td><td>{e(c["observed"])}</td>'
        f'<td>{e(c["conclusion"])}</td></tr>'
        for c in reg["controls"]
    )

    limits = "\n".join(f"      <li>{e(x)}</li>" for x in reg["known_limits"])

    body = f"""  <section>
    <h1>Link evidence register</h1>
    <p class="lead">This is the part of a shop nobody sees but everything depends on: the record of
    what each submitted link actually does. Registered {e(reg['retrieved_at_utc'])} by session
    <code>{e(reg['session'])}</code>. Read it as evidence, not as a verdict on compliance &mdash;
    that determination belongs to Amazon.</p>
    <div class="notebox"><b>Field policy.</b> {e(reg['field_policy'])}</div>
    <div class="notebox"><b>Method.</b> {e(reg['method'])}</div>
  </section>

  <section>
    <h2>The five submitted links</h2>
    <p class="small">Intended columns are what the owner supplied and are blank until the owner
    confirms them. Observed columns are what the retrieval client received. They are never merged.</p>
    <div class="table-scroll">
    <table>
      <caption>Product-intent confirmation record &mdash; intended vs observed, kept in separate columns</caption>
      <thead><tr>
        <th>ID</th><th>Submitted URL</th><th>Submitted token</th><th>Intended ASIN</th>
        <th>Intended listing URL</th><th>Confirmed on</th><th>Observed ASIN</th>
        <th>Observed page title</th><th>Observed category</th><th>Outcome</th>
        <th>Observed on</th><th>Source</th><th>Flags</th>
      </tr></thead>
      <tbody>
{chr(10).join(rows)}
      </tbody>
    </table>
    </div>
    <div class="flagbox"><b>What the table shows.</b> In every case where a product page was
    reached, the ASIN of that page is not the token in the submitted link, and the destination URL
    carries <code>plpRedirect=mhFallback</code>. One link reached an Amazon checkpoint page instead
    of a product. No destination carried an Associates tag parameter.</div>
  </section>

  <section>
    <h2>Observations recorded, with sources</h2>
    <ul>
{chr(10).join(observed)}
    </ul>
  </section>

  <section>
    <h2>Control tests</h2>
    <p class="small">Run to keep the main table honest. An inconclusive control is reported as
    inconclusive rather than dropped.</p>
    <div class="table-scroll">
    <table>
      <caption>Controls run on {e(reg['retrieved_at_utc'])}</caption>
      <thead><tr><th>ID</th><th>Purpose</th><th>Request</th><th>Observed</th><th>Conclusion</th></tr></thead>
      <tbody>
{controls}
      </tbody>
    </table>
    </div>
  </section>

  <section>
    <h2>Limits of this register</h2>
    <ul>
{limits}
    </ul>
    <p><a href="suggestions.html">What to do about it, ranked &rarr; suggestions</a> &bull;
    <a href="questions.html#Q-03">The question that unblocks it &rarr; Q-03</a></p>
  </section>"""
    return page(
        "verification.html",
        "Link evidence register",
        "Dated record of the five submitted Amazon links: token as submitted, destination observed, "
        "intended and observed fields kept separate.",
        "verification.html",
        body,
    )


# --- suggestions.html -------------------------------------------------------------------------
def build_suggestions() -> str:
    reg = load("suggestions.json")
    claims = {c["id"]: c for c in load("claims.json")["verified_claims"]}

    paths = []
    for p in reg["paths"]:
        inc = ", ".join(f'<a href="#{s}">{s}</a>' for s in p["includes"])
        exc = ", ".join(f'<a href="#{s}">{s}</a>' for s in p["excludes_for_now"]) or "none"
        paths.append(f"""      <article class="card path-card" id="{e(p['id'])}">
        <h3>{e(p['name'])}</h3>
        <p class="small">{e(p['id'])}</p>
        <p>{e(p['summary'])}</p>
        <p class="field"><b>Pick it if</b> {e(p['pick_if'])}</p>
        <p class="field"><b>Includes</b> {inc}</p>
        <p class="field"><b>Held back</b> {exc}</p>
        <p class="field"><b>Time to first real page</b> {e(p['time_to_first_real_page'])}</p>
        <p class="note">Risk: {e(p['risk'])}</p>
      </article>""")

    cards = []
    for s in reg["suggestions"]:
        gates = []
        for gid in s["policy_gate"]:
            c = claims.get(gid)
            if c:
                gates.append(
                    f'<li><a href="#{gid}"><b>{gid}</b></a> &mdash; &ldquo;{html.escape(c["quote"])}'
                    f'&hellip;&rdquo; <span class="small">({html.escape(c["publisher"])}, '
                    f'updated {html.escape(c["document_updated"])})</span></li>'
                )
            else:
                gates.append(f'<li><b>{gid}</b></li>')
        gate_html = (
            '<div class="gate"><h4>Policy this rests on</h4><ul>'
            + "".join(gates)
            + "</ul></div>"
            if gates
            else '<div class="gate"><h4>Policy this rests on</h4><p class="small">None asserted. '
                 'This is a craft choice, not a compliance requirement.</p></div>'
        )

        opts = "".join(
            f'<li><b>{e(o["label"])}</b> &mdash; {e(o["tradeoff"])}</li>' for o in s["options"]
        )
        needs = ", ".join(
            f'<a href="questions.html#{q}">{q}</a>' for q in s["needs_before_deciding"]
        ) or "nothing &mdash; you can decide on the evidence already on this page"
        status = s["status"]
        status_cls = {"safe to build now": "ok", "blocked": "unverified"}.get(status, "tag")
        cards.append(f"""      <article class="card sug" id="{e(s['id'])}">
        <p class="tagline">{e(s['area'])} &bull; {e(s['id'])}</p>
        <h3>{e(s['title'])}</h3>
        <p class="statusline"><span class="{status_cls}">{e(status)}</span></p>
        <p class="field"><b>The problem</b> {e(s['problem'])}</p>
        <p class="field"><b>What to do</b> {e(s['proposal'])}</p>
        <p class="field"><b>What the reader notices</b> {e(s['shop_feel'])}</p>
        <p class="field"><b>Expected effect</b> {e(s['expected_effect'])}</p>
        <p class="field"><b>Effort</b> {e(s['effort'])} &nbsp;&nbsp; <b>Risk</b> {e(s['risk'])}</p>
        {gate_html}
        <p class="field"><b>Needs answered first</b> {needs}</p>
        <h4>Paths</h4><ul class="opts">{opts}</ul>
        <h4>If approved, paste this into the build prompt</h4>
        <pre class="prompt">{e(s['paste_into_prompt'])}</pre>
      </article>""")

    legend = "".join(
        f"<li><b>{e(k)}</b> &mdash; {e(v)}</li>" for k, v in reg["status_legend"].items()
    )
    body = f"""  <section>
    <h1>Decision room</h1>
    <p class="lead">{e(reg['how_to_use'])}</p>
    <div class="notebox"><b>Reading the legend.</b><ul>{legend}</ul></div>
  </section>

  <section>
    <h2>Three paths, so you can pick one move rather than sixteen</h2>
    <div class="card-grid path-grid">
{chr(10).join(paths)}
    </div>
  </section>

  <section>
    <h2>All suggestions</h2>
    <div class="sug-grid">
{chr(10).join(cards)}
    </div>
  </section>

  <section>
    <h2>Every rule quoted above, in full</h2>
    <p class="small">Anchors below are what the policy boxes link to. Quotations are verbatim from
    the source named, retrieved {e(load('claims.json')['retrieved_at_utc'])}.</p>
{chr(10).join(
'    <h3 id="' + c["id"] + '">' + c["id"] + " &mdash; " + html.escape(c["claim"]) + "</h3>"
"<p>&ldquo;" + html.escape(c["quote"]) + "&rdquo;</p>"
'<p class="small">' + html.escape(c["publisher"]) + " &bull; document updated "
+ html.escape(c["document_updated"]) + " &bull; retrieved " + html.escape(c["retrieved"])
+ ' &bull; <a href="' + html.escape(c["source_url"])
+ '" rel="noopener noreferrer" target="_blank">source</a></p>'
"<p class='field'><b>What it changes here</b> " + html.escape(c["changes"]) + "</p>"
for c in load("claims.json")["verified_claims"])}
  </section>"""
    return page(
        "suggestions.html",
        "Decision room",
        "Ranked, sourced suggestions for the Affil3 affiliate site, with the policy rule each one "
        "rests on and the paths to choose between.",
        "suggestions.html",
        body,
    )


# --- questions.html ---------------------------------------------------------------------------
def build_questions() -> str:
    reg = load("open-questions.json")
    cards = []
    for q in reg["questions"]:
        blocks = ", ".join(
            f'<a href="suggestions.html#{b}">{b}</a>' if b.startswith("SUG")
            else f'<a href="suggestions.html#{b}">{b}</a>'
            for b in q["blocks"]
        ) or '<span class="blank">nothing is blocked on this; it is context</span>'
        cards.append(f"""      <article class="card q" id="{e(q['id'])}">
        <p class="tagline">{e(q['category'])} &bull; {e(q['id'])} &bull;
        <span class="unverified">{e(q['status'])}</span></p>
        <h3>{e(q['question'])}</h3>
        <p class="field"><b>Why it matters before deciding</b> {e(q['why_it_matters'])}</p>
        <p class="field"><b>What we already know</b> {e(q['what_we_know'])}</p>
        <p class="field"><b>What we do not know</b> {e(q['what_we_do_not_know'])}</p>
        <p class="field"><b>How to find out, including how to go looking</b> {e(q['how_to_find_out'])}</p>
        <p class="field"><b>Who must answer</b> {e(q['who_must_answer'])}</p>
        <p class="field"><b>Blocks</b> {blocks}</p>
        <div class="answer"><b>Your answer</b><p class="blank">{e(q['answer'])}</p></div>
      </article>""")

    by_cat = {}
    for q in reg["questions"]:
        by_cat.setdefault(q["category"], []).append(q["id"])
    index = "\n".join(
        "      <li>"
        + html.escape(cat)
        + " &mdash; "
        + ", ".join(f'<a href="#{i}">{i}</a>' for i in ids)
        + "</li>"
        for cat, ids in by_cat.items()
    )
    key = "".join(f"<li><b>{e(k)}</b> &mdash; {e(v)}</li>" for k, v in reg["answer_key"].items()) if isinstance(reg["answer_key"], dict) else ""
    body = f"""  <section>
    <h1>Open questions</h1>
    <p class="lead">{e(reg['structure'])}</p>
    <div class="notebox"><b>How to answer</b> {e(reg['answer_key'])}</div>
    <h2>Index</h2>
    <ul>
{index}
    </ul>
  </section>

  <section>
    <h2>The register</h2>
    <div class="sug-grid">
{chr(10).join(cards)}
    </div>
  </section>"""
    return page(
        "questions.html",
        "Open questions",
        "Every question that must be answered before a decision on the Affil3 site is reasonable, "
        "with what is known, what is missing, and how to go find the missing part.",
        "questions.html",
        body,
    )


# --- shop.html --------------------------------------------------------------------------------
def build_shop() -> str:
    topics = load("topics.json")
    links = {r["id"]: r for r in load("link-verification.json")["records"]}
    order = {"LINK-01": 1, "LINK-02": 3, "LINK-03": 2, "LINK-05": 4}
    cards = []
    for lid, n in sorted(order.items(), key=lambda kv: kv[1]):
        r = links[lid]
        name = r["observed_page_title"].replace("Amazon.com: ", "").split(" | ")[0].split(" - ")[0]
        cards.append(f"""      <article class="card prod">
        <h3>{e(name)}</h3>
        <p class="small">Destination reached by {e(r['submitted_url'])} on {e(r['observed_at_utc'])}</p>
        <p class="field"><b>What it is</b> {e(r['observed_page_title'])}</p>
        <p class="field"><b>Where it sits</b> {e(" &gt; ".join(r['observed_breadcrumb']))}</p>
        <p class="field"><b>Listing reference</b> <code>{e(r['observed_asin'])}</code></p>
        <p class="field"><b>What we did not check</b> price, availability, ratings and every spec not
        written on the listing. Nothing here was tested by hand.</p>
        <p class="warnline">The intended product for this link is not yet confirmed &mdash; see
        <a href="questions.html#Q-03">Q-03</a>. Do not buy from this card on our say-so.</p>
        <a class="outbound" href="{e(r['review_link'])}" rel="sponsored noopener" target="_blank">Check current price on Amazon &rarr;</a>
      </article>""")

    clusters = []
    for c in topics["clusters"]:
        trows = "".join(
            "<tr><td>" + html.escape(t["title"]) + '</td><td class="small">' + html.escape(t["type"])
            + "</td><td>" + html.escape(t["angle"]) + "</td><td>"
            + (('<a href="questions.html#' + t["depends_on"] + '">' + t["depends_on"] + "</a>") if t["depends_on"] else "not blocked")
            + "</td></tr>"
            for t in c["topics"]
        )
        clusters.append(f"""    <h3>{e(c['name'])} <span class="small">&mdash; {e(c['hub_status'])}</span></h3>
    <p class="small">Evidence for this cluster: {e(c['browse_evidence'])}</p>
    <div class="table-scroll"><table>
      <thead><tr><th>Working title</th><th>Format</th><th>Angle that makes it worth reading</th><th>Gated on</th></tr></thead>
      <tbody>{trows}</tbody>
    </table></div>""")

    cad = "\n".join(f"      <li><b>{e(k)}</b> {e(v)}</li>" for k, v in topics["cadence_proposal"].items())
    body = f"""  <section>
    <h1>What we are actually pointing at</h1>
    <p class="lead">{e(topics['title'])} &mdash; the shelf, the plan, and the honest note about what
    is not settled yet. No prices on this page on purpose: Amazon's program policies let a site show
    price and availability only when Amazon serves it or when it comes from a licensed API feed, and we
    have neither. So the button goes to the listing, where the number is current.</p>
    <div class="flagbox"><b>Read this before trusting the shelf.</b> The five links supplied for this
    project do not currently resolve to products we can confirm. Four land on live listings whose ASIN
    differs from the token in the link, one lands on an Amazon checkpoint page. The cards below show
    the destination each submitted link reached, dated, with the mismatch stated instead of papered
    over. <a href="verification.html">Full evidence register &rarr;</a></div>
  </section>

  <section>
    <h2>On the shelf</h2>
    <div class="product-grid">
{chr(10).join(cards)}
    </div>
    <p class="small">One submitted link (<code>B0c8moW59</code>) is omitted from the shelf because no
    product page was reached. It is recorded in the register, not quietly dropped.</p>
  </section>

  <section>
    <h2 id="clusters">What we are going to write, and why you would read it</h2>
    <p class="small">{e(topics['framing_rule'])}</p>
{chr(10).join(clusters)}
    <div class="notebox"><b>Cadence proposal, not a promise.</b><ul>
{cad}
    </ul></div>
  </section>

  <section>
    <h2>The existing guides</h2>
    <p class="lead">Four question-shaped pieces are already published. They are working titles, and
    they stay live because the questions are the ones a buyer asks regardless of which machine you end
    up pointing at.</p>
    <ul>
      <li><a href="guides/air-fryer-basket-oven.html">Basket or oven-style air fryer: what should you compare?</a></li>
      <li><a href="guides/air-fryer-capacity-checklist.html">A no-hype checklist for comparing air fryer capacity</a></li>
      <li><a href="guides/air-fryer-cleanup-counter-space.html">How to assess cleanup and counter-space trade-offs</a></li>
      <li><a href="guides/multi-function-appliance-questions.html">Questions to ask before buying a multi-function kitchen appliance</a></li>
    </ul>
    <p><a href="suggestions.html">Then tell us which path to take &rarr; the decision room</a></p>
  </section>"""
    return page(
        "shop.html",
        "Shop",
        "The Affil3 shelf: what each submitted link resolves to, dated, plus the editorial clusters "
        "planned around countertop cooking.",
        "shop.html",
        body,
    )


PAGES = {
    "verification.html": build_verification,
    "suggestions.html": build_suggestions,
    "questions.html": build_questions,
    "shop.html": build_shop,
}


def main() -> int:
    check = "--check" in sys.argv
    stale = []
    for fname, builder in PAGES.items():
        out = builder()
        target = ROOT / fname
        if check:
            if not target.exists() or target.read_text(encoding="utf-8") != out:
                stale.append(fname)
            continue
        target.write_text(out, encoding="utf-8")
        print(f"wrote {fname} ({len(out):,} bytes)")
    if check and stale:
        print("stale (re-run scripts/build_registers.py): " + ", ".join(stale))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
