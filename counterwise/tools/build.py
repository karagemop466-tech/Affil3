"""The Counterwise static site builder.

One command:  python3 tools/build.py

Reads data/ and content/, writes docs/. Every page is composed from the register, so a fact
appears on the site only if it appears in the register with a source and a date. The build runs
the gate (tools/gate.py) when it finishes and exits non-zero if the site would mislead anyone.

Standard library only. No template files: the page furniture is short enough to keep in one
place, and a template engine would be a dependency that buys nothing here.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate  # noqa: E402
from site_common import (  # noqa: E402
    CONTENT,
    DATA,
    OUT,
    ROOT,
    data_hash,
    esc,
    fmt_date,
    load,
    md_to_html,
    reading_minutes,
    word_count,
)

CFG = load("config.json")
PRODUCTS = {p["id"]: p for p in load("products.json")["products"]}
LINKS = {l["id"]: l for l in load("links.json")["links"]}
SOURCES = {s["id"]: s for s in load("sources.json")["sources"]}
GUIDES = {g["id"]: g for g in load("guides.json")["guides"]}
CLUSTERS = {c["id"]: c for c in load("clusters.json")["clusters"]}
FLAGS = {f["id"]: f for f in load("flags.json")["flags"]}
BOARD = load("suggestions.json")["board"]
QUESTIONS = load("questions.json")["questions"]
EVENTS = load("events.json")
TODAY = dt.date.today().isoformat()

BASE = CFG["identity"]["base_url"].rstrip("/")
PREFIX = re.sub(r"^https?://[^/]+", "", BASE)
TRACKING = CFG["amazon"]["tracking_id"]
STATEMENT = CFG["disclosure"]["statement"]
FETCH_EXAMPLE = CFG["disclosure"]["ftc_example_sentence"]
ASSET = f"{PREFIX}/assets"
ENDPOINT = CFG["measurement"]["endpoint"]

PUBLISHED_PRODUCT_IDS = [pid for pid, p in PRODUCTS.items() if p["observation"].get("listing_asin_observed_in_path")]
ALL_PAGES: dict[str, dict] = {}
REPORT: dict = {"rules": [], "failures": [], "stats": {}}
REPORT_RULE_ROWS: list = []


# ---------------------------------------------------------------------------- small parts


def url(path: str) -> str:
    """Site-absolute source path -> deployed URL."""
    if path.endswith("/index.html"):
        path = path[: -len("index.html")]
    return (PREFIX + path) if path.startswith("/") else path


def plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def GAP(text: str) -> str:
    return '<span class="gap">' + esc(text) + "</span>"


def SUB(text: str) -> str:
    return '<span class="sub">' + esc(text) + "</span>"


def chip(kind: str, text: str, title: str = "") -> str:
    t = f' title="{esc(title)}"' if title else ""
    return f'<span class="chip chip--{kind}"{t}>{esc(text)}</span>'


def product_state(pid: str) -> tuple[str, str, str]:
    """(chip kind, chip text, plain-language state) for one product row."""
    p = PRODUCTS[pid]
    obs = p["observation"]
    if obs.get("verification") == "unresolved":
        return "gap", "identity not confirmed", "The link we were given never reached a product page."
    if p["intent"].get("status") == "confirmed":
        return "ok", "intent confirmed in-account", "Listing identity confirmed by someone inside the Associates account."
    return "warn", "destination verified, intent unconfirmed", (
        f"We loaded {obs.get('listing_url_observed','the listing')} on {fmt_date(obs.get('observed_on',''))} "
        "and it showed this product. Nobody has confirmed inside the account that this is the listing "
        "the program owner meant to promote."
    )


def link_proof_count() -> str:
    proven = sum(
        1
        for pid in PUBLISHED_PRODUCT_IDS
        if PRODUCTS[pid]["observation"].get("link_state") == "in-account-confirmed"
    )
    total = len(PUBLISHED_PRODUCT_IDS)
    if not proven:
        return "no link proven in the reports yet"
    return f"{proven} of {total} links proven in the reports"


def link_proof_note() -> str:
    states = [
        PRODUCTS[pid]["observation"].get("link_state", "pending-test") for pid in PUBLISHED_PRODUCT_IDS
    ]
    proven = sum(1 for st in states if st == "in-account-confirmed")
    if not proven:
        return "None of them has yet been proven in the reporting interface, which is the one test to run before scaling."
    if proven == len(states):
        return f"All {proven} have been confirmed as credited in the reporting interface."
    return f"{proven} of {len(states)} have been confirmed as credited in the reporting interface; the rest are labelled pending-test on the page."


def obs_date(pid: str) -> str:
    return PRODUCTS[pid]["observation"].get("observed_on", "")


def outbound_link(pid: str, label: str, placement: str, cls: str = "btn") -> str:
    p = PRODUCTS[pid]
    asin = p["observation"].get("listing_asin_observed_in_path", "")
    if not asin:
        return (
            f'<span class="btn btn--ghost" aria-disabled="true" style="opacity:.65">'
            f"Listing not confirmed</span>"
            f'<p class="paid-note">We could not reach a product page for this row, so we publish no link for it. '
            f'See <a href="{url("/review/")}#FLG-004">FLG-004</a>.</p>'
        )
    href = f"https://{CFG['amazon']['marketplace_host']}/dp/{asin}?tag={TRACKING}"
    state = p["observation"].get("link_state", "pending-test")
    proven = state == "in-account-confirmed"
    return (
        f'<a class="{cls}" href="{href}" target="_blank" rel="sponsored nofollow noopener" '
        f'data-outbound="1" data-product="{pid}" data-link-state="{esc(state)}" data-placement="{esc(placement)}">'
        f"{esc(label)} <span class='arrow' aria-hidden='true'>↗</span></a>"
        f'<p class="paid-note"><b>(paid link)</b> Opens {esc(CFG["amazon"]["marketplace_host"])} in a new tab. '
        f"Tagged <code>{esc(TRACKING)}</code>. "
        + ("Click attribution confirmed in the reports. " if proven else "Click attribution is not yet confirmed in the reports. ")
        + "Price and stock are shown by Amazon at click time — we do not store them.</p>"
    )


def pid_or_citation(pid: str) -> str:
    return pid if pid in PRODUCTS else "citation"


def ext(href: str, label: str, product: str = "citation") -> str:
    """An external citation. Links whose host is the marketplace are treated as placements and
    carry the tag, the sponsored marker and the counting attributes, because a reader who clicks a
    product URL from a citation can buy from it and that click should credit the account that
    earned it. Everything else gets nofollow + noopener only."""
    host = re.sub(r"^https?://", "", href).split("/")[0].lower()
    if host == CFG["amazon"]["marketplace_host"]:
        if "tag=" not in href:
            href = href + (("&" if "?" in href else "?") + f"tag={TRACKING}")
        return (
            f'<a href="{esc(href)}" target="_blank" rel="sponsored nofollow noopener" '
            f'data-outbound="1" data-product="{esc(product)}" data-link-state="citation">{label}</a>'
        )
    return f'<a href="{esc(href)}" target="_blank" rel="nofollow noopener">{label}</a>'


def source_link(sid: str) -> str:
    s = SOURCES.get(sid)
    if not s:
        return ""
    badge = {
        "read": chip("ok", "read in full"),
        "snippet": chip("warn", "official domain, snippet"),
        "link-verified": chip("warn", "link verified"),
        "not-read": chip("gap", "not read"),
        "queued": chip("gap", "queued"),
    }.get(s["verification"], "")
    return (
        ext(s["url"], esc(s["title"]))
        + f' <span class="meta">· {esc(s["org"])} · retrieved {fmt_date(s["accessed"])}</span> {badge}'
    )


def source_ref(*ids: str) -> str:
    items = "".join(f"<li>{source_link(i)}</li>" for i in ids if i in SOURCES)
    return f'<aside class="prov"><h4>Sources for this page</h4><ul>{items}</ul></aside>'


def titled_pills(values: list[str]) -> str:
    if not values:
        return '<p class="paid-note">Nothing titled in the listing was usable.</p>'
    lis = "".join(
        f'<li title="verbatim from the listing title captured {esc(PRODUCTS and TODAY)}">{esc(v)}</li>'
        for v in values[:8]
    )
    return f'<ul class="titled">{lis}</ul>'


def checklist(guide: dict) -> str:
    cl = guide.get("checklist") or {}
    items = cl.get("items", [])
    if not items:
        return ""
    rows = "".join(
        f'<li><label><input type="checkbox" data-checklist="{esc(cl["id"])}" data-item="{esc(it["id"])}">'
        f"<span>{esc(it['text'])}</span></label></li>"
        for it in items
    )
    return (
        f'<section class="checklist" id="check-{esc(cl["id"])}">'
        f"<h4>{esc(cl.get('label','Checklist'))}</h4>"
        '<p class="hint">Ticking boxes saves nothing on our side — it is stored in your own browser, '
        "and the only number we record is which line people use. <a href=\"" + url("/privacy/") + '">What is measured</a>.</p>'
        f"<ul>{rows}</ul>"
        '<p class="progress">0 of '
        f"{len(items)} done</p></section>"
    )


def signup_block(where: str) -> str:
    enabled = CFG["reader_capture"]["enabled"]
    return (
        '<section class="nextstep" style="margin-top:22px">'
        f"<h4>Reader capture — {esc('enabled' if enabled else 'not enabled')}</h4>"
        f'<form data-signup data-capture-enabled="{1 if enabled else 0}" novalidate>'
        '<p style="margin:0 0 8px"><label class="meta" for="e-' + esc(where) + '">One email when a new guide ships.</label><br>'
        '<input id="e-' + esc(where) + '" type="email" name="email" required placeholder="you@example.org" '
        'style="font:15px var(--sans);padding:8px 10px;border:1px solid var(--rule);border-radius:6px;background:var(--card);color:var(--ink)">'
        ' <button class="btn btn--ghost" type="submit" style="align-self:auto">Send</button></p>'
        "</form>"
        '<p data-signup-outcome hidden></p>'
        "<p class=\"paid-note\">Nothing is stored on this deployment: there is no endpoint configured. "
        "That is deliberate, and it is decision "
        '<a href="' + url("/suggestions/") + '#S-10">S-10</a>.</p></section>'
    )


def nav(active: str) -> str:
    items = [
        ("guides", "Guides", url("/guides/")),
        ("gear", "Gear we track", url("/gear/")),
        ("compare", "Compare", url("/compare/")),
        ("summary", "Summary", url("/summary/")),
        ("board", "Suggestions", url("/suggestions/")),
    ]
    out = []
    for key, label, href in items:
        cur = ' aria-current="page"' if key == active else ""
        out.append(f'<a href="{href}"{cur}>{label}</a>')
    return '<nav class="nav" aria-label="Main">' + "".join(out) + "</nav>"


def footer() -> str:
    counts = {
        "pages": len(page_plan()),
        "sources": len(SOURCES),
        "flags": len(FLAGS),
    }
    return f"""<footer class="foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="brand" href="{url('/')}" style="color:#fff">
          {LOGOMARK}<span>Counterwise</span>
        </a>
        <p class="foot-lead" style="margin-top:10px">{esc(CFG['identity']['kicker'])}. Independent buyer research for
        countertop cooking gear, assembled from listings we loaded and policies we read.</p>
      </div>
      <div>
        <h4>Read</h4>
        <ul>
          <li><a href="{url('/guides/')}">All guides</a></li>
          <li><a href="{url('/gear/')}">Gear we track</a></li>
          <li><a href="{url('/compare/')}">Compare two machines</a></li>
          <li><a href="{url('/clusters/doneness/')}">Knowing when it's done</a></li>
          <li><a href="{url('/summary/')}">Executive summary</a></li>
        </ul>
      </div>
      <div>
        <h4>Verification</h4>
        <ul>
          <li><a href="{url('/transparency/')}">Transparency hub</a></li>
          <li><a href="{url('/transparency/sources/')}">Source register ({counts['sources']})</a></li>
          <li><a href="{url('/transparency/verification/')}">Link &amp; product evidence</a></li>
          <li><a href="{url('/transparency/method/')}">How this is built</a></li>
          <li><a href="{url('/transparency/gate-report/')}">Gate report</a></li>
          <li><a href="{url('/metrics/')}">Measurement &amp; events</a></li>
        </ul>
      </div>
      <div>
        <h4>Decisions</h4>
        <ul>
          <li><a href="{url('/suggestions/')}">Suggestions board</a></li>
          <li><a href="{url('/questions/')}">Open questions</a></li>
          <li><a href="{url('/review/')}" >Flagged for review ({counts['flags']})</a></li>
          <li><a href="{url('/about/')}">Editorial policy</a></li>
          <li><a href="{url('/disclosure/')}">Disclosure statement</a></li>
          <li><a href="{url('/privacy/')}">Privacy</a></li>
          <li><a href="{url('/feed.xml')}">Atom feed</a></li>
        </ul>
      </div>
    </div>
    <p class="foot-disclosure" data-disclosure="footer"><strong>{esc(STATEMENT)}</strong>
      It applies to every product link on this site, on this page, including this footer.
      <a href="{url('/disclosure/')}">What that means, in full</a>.</p>
    <p class="colophon">Built by <code>tools/build.py</code> from <code>data/</code> + <code>content/</code> ·
      inputs <code>{data_hash()}</code> · {counts['pages']} pages ·
      no cookies, no webfonts, no third-party requests ·
      repository: <a href="{esc(CFG['repository']['clone'])}">{esc(CFG['repository']['clone'].replace('https://',''))}</a></p>
  </div>
</footer>"""


LOGOMARK = (
    '<svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true" focusable="false">'
    '<rect x="1" y="3" width="18" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="1.6"/>'
    '<path d="M1 8h18" stroke="currentColor" stroke-width="1.6"/>'
    '<circle cx="15.4" cy="5.5" r="1.1" fill="currentColor"/></svg>'
)


def verification_meta() -> str:
    """Search Console ownership proof, emitted only when a token exists (RUNBOOK R6). An empty
    config must stay visible as unverified rather than render as configured-but-silent."""
    tok = (CFG.get("search_console", {}).get("verification_token") or "").strip()
    return f'<meta name="google-site-verification" content="{esc(tok)}">' if tok else ""


def seo_title(text: str) -> str:
    """Keep <title> inside the length a search result will actually show (60-70 chars)."""
    t = text.strip()
    if len(t) <= 70:
        return t
    cut = t[:66]
    cut = cut[: cut.rfind(" ")].rstrip(" ,:;·—-")
    return cut + "…"


def seo_desc(text: str) -> str:
    t = " ".join(text.split())
    if len(t) <= 160:
        return t
    cut = t[:157]
    cut = cut[: cut.rfind(" ")].rstrip(" ,:;·—-.")
    return cut + "…."


def head(title: str, description: str, path: str, extra: str = "") -> str:
    canonical = BASE + (path[: -len("index.html")] if path.endswith("/index.html") else path)
    icon = LOGOMARK.replace("#", "%23").replace("<", "%3C").replace(">", "%3E").replace('"', "%22")
    return f"""<!doctype html>
<html lang="{CFG['identity']['language']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(seo_title(title))}</title>
<meta name="description" content="{esc(seo_desc(description))}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{esc(CFG['identity']['name'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:image" content="{BASE}/assets/img/og-cover.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f6f3ec">
<link rel="alternate" type="application/atom+xml" title="{esc(CFG['identity']['name'])} — new guides" href="{url('/feed.xml')}">
<link rel="icon" href="data:image/svg+xml,{esc(icon)}">
{verification_meta()}
<link rel="stylesheet" href="{ASSET}/site.css">
{extra}
</head>"""


def page(
    key: str,
    path: str,
    title: str,
    description: str,
    main: str,
    kind: str,
    active: str = "",
    jsonld: list | None = None,
    index: bool = True,
) -> str:
    nodes = (jsonld or []) + [
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": breadcrumbs(path),
        }
    ]
    ld = f'<script type="application/ld+json">{json.dumps(nodes[0] if len(nodes) == 1 else nodes, ensure_ascii=False)}</script>'
    robots = "" if index else chr(10) + '<meta name="robots" content="noindex">'
    allowed = ",".join(e["name"] for e in EVENTS["events"])
    body_attrs = (
        f'data-page="{esc(path)}" data-page-kind="{kind}" data-allowed-events="{allowed}" '
        f'data-analytics-endpoint="{esc(ENDPOINT)}"'
    )
    ALL_PAGES[key] = {"path": path, "title": title, "description": description, "kind": kind, "index": index}
    return (
        head(title, description, path, ld + robots)
        + f"""
<body {body_attrs}>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
  <div class="wrap">
    <a class="brand" href="{url('/')}">{LOGOMARK}<span>Counterwise<small>{esc(CFG['identity']['kicker'])}</small></span></a>
    {nav(active)}
    <span class="issue-tag">{esc(CFG['identity']['issue_label'])}</span>
  </div>
</header>
<div class="disclosure">
  <div class="wrap">
    <span class="tag">Disclosure</span>
    <span><strong>{esc(STATEMENT)}</strong> And in the plain words the FTC uses as its example:
    <strong>“{esc(FETCH_EXAMPLE)}”</strong> We are not paid to call anything better; we are paid if you buy
    through a link. <a href="{url('/disclosure/')}">How this works</a>.</span>
  </div>
</div>
<main id="main">
{main}
</main>
{footer()}
<script src="{ASSET}/track.js" defer></script>
</body>
</html>
"""
    )


def breadcrumbs(path: str) -> list[dict]:
    parts = [p for p in path.strip("/").split("/") if p not in ("", "index.html")]
    items = [{"@type": "ListItem", "position": 1, "name": "Counterwise", "item": BASE + "/"}]
    for i, part in enumerate(parts):
        items.append(
            {
                "@type": "ListItem",
                "position": i + 2,
                "name": part.replace("-", " ").replace(".html", "").capitalize(),
                "item": BASE + "/" + "/".join(parts[: i + 1]),
            }
        )
    return items


def crumb_trail(path: str, here: str) -> str:
    """Visible trail. Home is 'Counterwise' rather than the word 'home' because the site has a
    distinct front page that a reader should be able to get back to."""
    steps = [f'<a href="{url("/")}">Counterwise</a>']
    parts = [p for p in path.strip("/").split("/") if p not in ("", "index.html")]
    accum: list[str] = []
    for part in parts[:-1]:
        accum.append(part)
        steps.append(f'<a href="{url("/" + "/".join(accum) + "/")}">{esc(part.replace("-", " "))}</a>')
    steps.append(esc(here))
    return '<p class="breadcrumbs">' + " › ".join(steps) + "</p>"


def titled_pills(values: list[str], captured: str = "") -> str:
    if not values:
        return '<p class="paid-note">No usable attribute text was captured for this row.</p>'
    note = f" as titled on {esc(fmt_date(captured))}" if captured else ""
    lis = "".join(f'<li title="verbatim from the seller&apos;s listing title{note}">{esc(v)}</li>' for v in values[:6])
    return f'<ul class="titled">{lis}</ul>'


# ------------------------------------------------------------------------------- front page


def front() -> str:
    rail = "".join(product_card(pid, "rail") for pid in PUBLISHED_PRODUCT_IDS)
    unresolved = [pid for pid in PRODUCTS if pid not in PUBLISHED_PRODUCT_IDS]
    qlist = "".join(
        f'<li><a href="{url("/guides/" + g["slug"] + ".html")}"><span class="qnum">0{i+1}</span>'
        f'<span class="qtext">{esc(g["title"])}</span><span class="qmeta">{reading_minutes(body_of(g))} min</span></a></li>'
        for i, g in enumerate(GUIDES.values())
    )
    clusters = "".join(
        f'<a class="card card--link" href="{url("/clusters/" + c["id"] + "/")}">'
        f'<span class="kicker">{esc("seasonal · " + c["seasonal"] if c["seasonal"] != "evergreen" else "evergreen")}</span>'
        f"<h3>{esc(c['name'])}</h3><p>{esc(c['question'])}</p>"
        f'<p class="meta">{plural(len(c["guides"]), "guide")} · {plural(len([x for x in c["products"] if x in PUBLISHED_PRODUCT_IDS]), "listing")}</p></a>'
        for c in CLUSTERS.values()
        if c["id"] != "unresolved"
    )
    open_decisions = sum(1 for s in BOARD if not s.get("review_decision"))
    main = f"""
<section class="sec">
  <div class="wrap hero">
    <div>
      <span class="kicker">{esc(CFG['identity']['issue_label'])} · countertop cooking</span>
      <h1>Four machines on the counter, and the questions that decide which one is yours.</h1>
      <p class="deck">We track air fryers, one countertop oven and the probe that settles whether
      anything is cooked. No prices, no star ratings, no invented specs — just the comparisons worth
      making, and a link to the listing so you can see the live number.</p>
      <div class="meta-row">
        <span>Updated {fmt_date(TODAY)}</span><span>·</span>
        <span>{len(PUBLISHED_PRODUCT_IDS)} listings with verified destinations</span><span>·</span>
        <span>·</span><span>{link_proof_count()}</span>
        <span>{len(unresolved)} supplied link still unresolved</span>
      </div>
      <div class="hero-actions">
        <a class="btn" href="{url('/guides/basket-or-oven.html')}">Start with the four measurements <span class="arrow" aria-hidden="true">→</span></a>
        <a class="btn btn--ghost" href="{url('/gear/')}">See what we track</a>
      </div>
    </div>
    <figure class="art">
      <img src="{ASSET}/img/hero-front.png" width="1264" height="848" alt="Line illustration of three countertop cooking machines side by side: a tall single basket, a twin-basket unit, and an oven with French doors.">
      <figcaption>Illustration, drawn for this site — not a product photograph. Why there are no Amazon photos
      here: <a href="{url('/transparency/method/')}">how this is built</a>.</figcaption>
    </figure>
  </div>
</section>

<section class="sec sec--tight">
  <div class="wrap">
    <div class="sec-head"><h2>On the bench</h2><a href="{url('/gear/')}">The full register →</a></div>
    <p class="sec-note">Each card states what the seller's listing title said on the day we loaded it, and what we
    could not confirm. Prices are Amazon's to show, not ours.</p>
    <div class="rail">{rail}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap grid-2" style="align-items:start">
    <div>
      <div class="sec-head"><h2>Start here</h2><a href="{url('/guides/')}">All guides →</a></div>
      <p class="sec-note">Five guides, each built around one question a buyer actually asks. They are ordered by the
      decision they serve, not by search volume — we have none yet.</p>
      <ol class="qlist">{qlist}</ol>
    </div>
    <div>
      <div class="sec-head"><h2>Clusters</h2></div>
      <div class="grid-2" style="gap:14px">{clusters}</div>
      <div class="notice notice--info" style="margin-top:18px">
        <p><strong>November, and it matters.</strong> Whole birds, thick cuts and a small hot cavity are a
        doneness problem before they are an appliance problem. <a href="{url('/guides/is-a-probe-thermometer-worth-it.html')}">The case for a probe →</a></p>
      </div>
      <div class="notice" style="margin-top:14px">
        <p><strong>{open_decisions} suggestions are waiting on a decision</strong> — including whether to attach a
        click counter and whether to buy a domain. <a href="{url('/suggestions/')}">Review the board →</a></p>
      </div>
    </div>
  </div>
</section>

<section class="sec sec--tight">
  <div class="wrap">
    <div class="sec-head"><h2>What we can and cannot stand behind</h2><a href="{url('/transparency/')}">Transparency hub →</a></div>
    <div class="stat-strip">
      <div><span class="n">{len(PUBLISHED_PRODUCT_IDS)}/{len(PRODUCTS)}</span><span class="l">links that resolved to a listing</span></div>
      <div><span class="n">{len(SOURCES)}</span><span class="l">registered sources</span></div>
      <div><span class="n">{sum(1 for s in SOURCES.values() if s['verification']=='read')}</span><span class="l">read in full this session</span></div>
      <div><span class="n">{len(FLAGS)}</span><span class="l">open items, published not buried</span></div>
      <div><span class="n">0</span><span class="l">prices, ratings or forecasts published</span></div>
    </div>
  </div>
</section>
"""
    return page(
        "front",
        "/index.html",
        "Counterwise — air fryer and countertop oven buying guides",
        "Question-shaped buying guides for air fryers, countertop ovens and probe thermometers. Every product "
        "attribute links to the listing it came from, prices and ratings are deliberately not published, and open "
        "questions are listed on the site.",
        main,
        "front",
        active="",
        jsonld=[
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": CFG["identity"]["name"],
                "url": BASE + "/",
                "description": CFG["identity"]["description"],
                "inLanguage": CFG["identity"]["language"],
                "publisher": {
                    "@type": "Organization",
                    "name": CFG["identity"]["author_entity"],
                    "url": BASE + "/about/",
                },
            }
        ],
    )


def product_card(pid: str, placement: str) -> str:
    p = PRODUCTS[pid]
    kind, label, _state = product_state(pid)
    cluster = CLUSTERS.get(p["cluster"], {})
    return f"""<article class="gcard" id="{esc(pid)}">
  <div class="row"><span class="brandline">{esc(p.get('titled_brand') or 'identity not confirmed')}</span>{chip(kind, label)}</div>
  <h3><a class="title-link" href="{url('/gear/' + p['slug'] + '/')}">{esc(p['display_name'])}</a></h3>
  <p class="why">{esc(cluster.get('short_name', ''))} · {esc(p.get('titled_capacity') or 'capacity not stated in the captured title')}</p>
  {titled_pills(p.get('titled_features', []), obs_date(pid))}
  {outbound_link(pid, 'Check this listing on Amazon', placement)}
</article>"""


def body_of(guide: dict) -> str:
    path = CONTENT / "guides" / f"{guide['slug']}.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""


# ------------------------------------------------------------------------------ gear


def gear_index() -> str:
    rows = []
    for pid in PRODUCTS:
        p = PRODUCTS[pid]
        kind, label, _ = product_state(pid)
        obs = p["observation"]
        cat = obs.get("breadcrumb_observed") or ""
        cap = p.get("titled_capacity") or GAP("not stated in the title we captured")
        href = url("/gear/" + p["slug"] + "/") if pid in PUBLISHED_PRODUCT_IDS else url("/review/#FLG-004")
        seen = "listing page" if obs.get("listing_url_observed") else GAP("no destination reached")
        if obs.get("observed_on"):
            seen += SUB("captured " + fmt_date(obs["observed_on"]))
        link_cell = outbound_link(pid, "Open listing", "table", cls="btn btn--ghost")
        rows.append(
            "<tr data-compare-row data-products=\"" + pid + "\">"
            + "<td>"
            + (
                f'<a href="{href}" class="title-link">{esc(p["display_name"])}</a>'
                if pid in PUBLISHED_PRODUCT_IDS
                else esc(p["display_name"]) + '<span class="sub">no page: identity unconfirmed</span>'
            )
            + SUB(pid + " · link " + str(obs.get("source_link", "")))
            + "</td>"
            + "<td>" + esc(CLUSTERS.get(p["cluster"], {}).get("short_name", "—")) + "</td>"
            + "<td>" + cap + "</td>"
            + "<td>" + (esc(cat) if cat else GAP("not captured")) + "</td>"
            + "<td>" + chip(kind, label) + "</td>"
            + "<td>" + seen + "</td>"
            + "<td>" + link_cell + "</td></tr>"
        )
    main = f"""
<section class="sec">
  <div class="wrap">
    <div class="page-head">
      <span class="kicker">The register</span>
      <h1>Gear we track</h1>
      <p class="deck">Five links were given to this project. Four of them opened a product page we could read;
      one landed on an access check and never reached a listing. That is the whole state of the catalogue,
      shown rather than smoothed over.</p>
    </div>
    <div class="notice notice--info">
      <p><strong>Read the columns this way:</strong> <em>as titled</em> means the seller's own listing title, captured
      {fmt_date(TODAY)} — a marketing string, not a specification. <em>Destination verified</em> means we loaded the page.
      <em>Intent unconfirmed</em> means nobody inside the Associates account has said "yes, that is the product I meant",
      which is a sentence only they can say. Details: <a href="{url('/review/')}#FLG-001">FLG-001</a>.</p>
    </div>
    <div class="table-wrap">
      <table>
        <caption>Four listings with captured evidence, one unresolved row. No prices or ratings appear here by design
        (see <a href="{url('/suggestions/')}#S-04">S-04</a>).</caption>
        <thead><tr><th>Product</th><th>Shape</th><th>Titled capacity</th><th>Category, as observed</th><th>Evidence state</th><th>What we saw</th><th>Link</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>
    <p class="paid-note" style="margin-top:12px">Every published link carries the tracking ID
    <code>{esc(TRACKING)}</code> as a URL parameter and is marked <code>rel="sponsored nofollow"</code>.
    {link_proof_note()} <a href="{url('/questions/')}#Q-03">Q-03</a> · <a href="{url('/review/')}#FLG-002">FLG-002</a>.</p>
    <div class="grid-2" style="margin-top:26px">
      <div class="card"><h3>How to read a capacity claim</h3>
        <p>Quarts describe volume; a single cooking layer describes your dinner.</p>
        <p><a href="{url('/guides/capacity-checklist.html')}">The four checks →</a></p></div>
      <div class="card"><h3>The four measurements</h3>
        <p>Strip, ceiling, swing, sink. Three minutes with a tape measure beats any spec sheet.</p>
        <p><a href="{url('/guides/basket-or-oven.html')}">Start here →</a></p></div>
    </div>
    {source_ref('SG-15','SG-02','SG-01')}
  </div>
</section>
"""
    return page(
        "gear",
        "/gear/index.html",
        "Gear we track — four listings, with evidence states",
        "Every listing this site links to, with what we captured, when we captured it, and exactly which "
        "attributes are the seller's words rather than verified specifications.",
        main,
        "gear",
        active="gear",
    )


def gear_page(pid: str) -> str:
    p = PRODUCTS[pid]
    obs = p["observation"]
    kind, label, state = product_state(pid)
    guides_here = [g for g in GUIDES.values() if pid in g.get("products", [])]
    art = {
        "dual-basket": ("art-basket.png", "Twin baskets drawn to scale against a single deep basket."),
        "single-basket": ("art-basket.png", "A single deep basket, drawn with the clearance a tall unit needs."),
        "oven-style": ("art-oven.png", "Oven-style cavity with rack positions and a door swing arc."),
        "doneness": ("art-probe.png", "A probe entering the thickest part of a bird, away from bone."),
        "unresolved": ("art-basket.png", "Illustration standing in for a product page we could not reach."),
    }[p["cluster"]]
    nots = "".join(f"<li>{esc(n)}</li>" for n in p.get("not_verified", []))
    compares = "".join(f"<li>{esc(c)}</li>" for c in p.get("compare_points", []))
    feats = "".join(f"<li>{esc(f)}</li>" for f in p.get("titled_features", []))
    main = f"""
<section class="sec">
  <div class="wrap">
    <div class="page-head">
      {crumb_trail('/gear/' + p['slug'] + '/', p['display_name'])}
      <span class="kicker">{esc(CLUSTERS.get(p['cluster'],{}).get('name',''))}</span>
      <h1>{esc(p['display_name'])}</h1>
      <div class="byline"><b>{esc(CFG['identity']['author_entity'])}</b>
        <span>Listing captured {fmt_date(obs.get('observed_on') or TODAY)}</span>
        <span>·</span><span>{esc(state)}</span></div>
      <p class="deck">{esc(p.get('titled_capacity') or 'No capacity figure appears in the text we captured.')}
      {chip(kind, label)}</p>
    </div>
    <div class="grid-2" style="align-items:start">
      <div>
        <h2>What the listing says, in the listing's words</h2>
        <ul>{feats or '<li>Nothing usable.</li>'}</ul>
        <p class="paid-note">These are strings lifted from the seller's own listing title. They are the seller's
        claims, formatted for a search engine, and they change without notice. We add nothing to them.</p>
        <h2>What to look at before you decide</h2>
        <ul>{compares}</ul>
        <h2>Where this row goes in the site</h2>
        <ul>{''.join(f'<li><a href="{url("/guides/"+g["slug"]+".html")}">{esc(g["title"])}</a> — {esc(g["question_answered"])}</li>' for g in guides_here) or '<li>No guide references this row yet.</li>'}</ul>
        {outbound_link(pid, 'Check the live price and stock on Amazon', 'gear-page')}
      </div>
      <div>
        <figure class="art"><img src="{ASSET}/img/{art[0]}" width="1200" height="896" alt="{esc(art[1])}">
          <figcaption>Illustration drawn for this site; it is not a photograph of this product.</figcaption></figure>
        <details class="gapbox" open>
          <summary>What we could not verify about this machine</summary>
          <ul>{nots}</ul>
          <p class="paid-note">Those cells are blank on our tables rather than estimated. The reason is in
          <a href="{url('/review/')}#FLG-007">FLG-007</a>: without an authorized data feed, a price we print is a
          screenshot of yesterday.</p>
        </details>
        <div class="notice"><p><strong>Why we do not say whether this one is good.</strong> Nobody here has cooked in it.
        A guide that has not tested a machine can still make a buyer's questions sharper, so that is what this page does.</p></div>
      </div>
    </div>
    {prov_block(obs)}
  </div>
</section>
"""
    return page(
        f"gear:{pid}",
        f"/gear/{p['slug']}/",
        f"{p['display_name']} | Counterwise",
        f"Listing evidence captured {fmt_date(obs.get('observed_on') or TODAY)} for the {p['display_name']}: "
        "what the seller's title says, what we could not confirm, and where the link went.",
        main,
        "gear",
        active="gear",
    )


def prov_block(obs: dict) -> str:
    src = LINKS.get(obs.get("source_link", ""))
    link_bits = ""
    if src:
        link_bits = (
            f"<li>Supplied link: <code>{esc(src['supplied_url'])}</code> — token is "
            f"{src['supplied_token_length']} characters, recorded as given.</li>"
            "<li>Where it led: "
            + ext(
                src["observed_final_url"],
                "<code>" + esc(re.sub("https?://", "", src["observed_final_url"])[:70]) + "…</code>",
                pid_or_citation(src.get("product_id", "")),
            )
            + "</li>"
            f"<li>Tracking tag in the destination we observed: "
            f"{'present' if src['observed_tag_param_present'] else 'absent — see FLG-002'}.</li>"
        )
    return (
        '<aside class="prov"><h4>Provenance of this row</h4><ul>'
        f"<li>Verification state: <strong>{esc(obs.get('verification',''))}</strong>, captured {fmt_date(obs.get('observed_on',''))}.</li>"
        + link_bits
        + "<li>Listing titles are seller-authored marketing copy: <a href=\"" + url("/review/") + "#FLG-008\">FLG-008</a>.</li>"
        + "</ul></aside>"
    )


def compare_page() -> str:
    opts = "".join(
        f'<option value="{pid}">{esc(PRODUCTS[pid]["display_name"])}</option>' for pid in PUBLISHED_PRODUCT_IDS
    )
    rows = f"""
      <tr data-compare-row data-products="P-01 P-03"><td>One layer vs two</td><td>two 3Qt halves: two components at once</td><td>one 8 Qt basket: one bigger batch</td><td>26QT cavity: racks, height, a window</td></tr>
      <tr data-compare-row data-products="P-01"><td>What the title leads with</td><td>twin baskets, view windows, a shared finish mode</td><td class="gap">—</td><td class="gap">—</td></tr>
      <tr data-compare-row data-products="P-03"><td>Named functions</td><td class="gap">—</td><td>air fry, bake, dehydrate, frozen</td><td class="gap">—</td></tr>
      <tr data-compare-row data-products="P-02"><td>Preset count</td><td class="gap">—</td><td class="gap">—</td><td>24 one-touch presets, six accessories</td></tr>
      <tr data-compare-row data-products="P-01 P-02 P-03"><td>Cleaning burden</td><td>two baskets, two trays</td><td>one basket</td><td>door glass, racks, trays, interior walls</td></tr>
      <tr data-compare-row data-products="P-01 P-02 P-03"><td>Price, rating, warranty</td><td class="gap">not published by us</td><td class="gap">not published by us</td><td class="gap">not published by us</td></tr>
    """
    main = f"""
<section class="sec">
  <div class="wrap">
    <div class="page-head">
      <span class="kicker">Side by side</span>
      <h1>Compare two machines on the questions that decide it</h1>
      <p class="deck">A real table in the HTML, not a widget that builds the comparison in memory.
      The filters below only hide rows; the page says everything with JavaScript switched off.</p>
    </div>
    <form class="filters" data-compare-form data-cluster="air-fryers">
      <label for="c1">Show rows for</label>
      <select id="c1" name="a">{opts}</select>
      <label for="c2">and</label>
      <select id="c2" name="b"><option value="">—</option>{opts}</select>
      <span class="paid-note" data-compare-count></span>
    </form>
    <div class="table-wrap">
      <table>
        <caption>Titled claims, side by side, from listing titles captured {fmt_date(TODAY)}. "not published by us" is a
        policy, not a gap in research: see <a href="{url('/suggestions/')}#S-04">S-04</a>.</caption>
        <thead><tr><th>Question</th><th>Twin basket (P-01)</th><th>Single basket (P-03)</th><th>Oven-style (P-02)</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    <div class="grid-2" style="margin-top:24px">
      <div class="card"><h3>Then measure, don't guess</h3><p>Strip, ceiling, swing, sink.</p>
        <p><a href="{url('/guides/basket-or-oven.html')}#check-fit">The four-line sheet →</a></p></div>
      <div class="card"><h3>Then check the layer, not the volume</h3><p>Crisp food needs air reaching it in one layer.</p>
        <p><a href="{url('/guides/capacity-checklist.html')}#why-the-headline-number-is-the-least-useful-one-on-the-page">Capacity checks →</a></p></div>
    </div>
    {source_ref('SG-15')}
  </div>
</section>
"""
    return page(
        "compare",
        "/compare/index.html",
        "Compare air fryer shapes: basket, twin basket, oven-style",
        "A side-by-side table of what three tracked listings claim about themselves, organised by the questions "
        "that decide the purchase, with nothing invented where the evidence stops.",
        main,
        "compare",
        active="compare",
    )


# ---------------------------------------------------------------------------- guides


def guide_page(guide: dict) -> str:
    raw = body_of(guide)
    html_body = md_to_html(raw, PREFIX)
    mins = reading_minutes(raw)
    cluster_names = " · ".join(CLUSTERS[c]["name"] for c in guide["clusters"] if c in CLUSTERS)
    prods = "".join(
        f'<a class="btn btn--ghost" href="{url("/gear/" + PRODUCTS[pid]["slug"] + "/")}">{esc(PRODUCTS[pid]["display_name"])}</a>'
        for pid in guide["products"]
    )
    main = f"""
<section class="sec">
  <div class="wrap">
    <div class="article">
    <div class="page-head" style="padding-top:6px">
      <span class="kicker">{esc(cluster_names)}</span>
      <h1>{esc(guide['title'])}</h1>
      <p class="deck">{esc(guide['deck'])}</p>
      <div class="byline">
        <b>{esc(CFG['identity']['author_entity'])}</b>
        <span>Published {fmt_date(guide['published'])} · updated {fmt_date(guide['updated'])}</span>
        <span>·</span><span>{mins} min read · {word_count(raw)} words</span>
        <span>·</span><span>No product tested by us</span>
      </div>
    </div>
    {html_body}
    {checklist(guide)}
    <div class="nextstep"><h4>Next step</h4><p>{esc(guide['next_step'])}</p>
      <div class="hero-actions" style="margin-top:12px">{prods}</div>
    </div>
    {source_ref(*guide['sources'])}
    {signup_block(guide['slug'])}
    </div>
  </div>
</section>
"""
    ld = [
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": guide["title"],
            "description": guide["deck"],
            "datePublished": guide["published"],
            "dateModified": guide["updated"],
            "inLanguage": CFG["identity"]["language"],
            "author": {"@type": "Organization", "name": CFG["identity"]["author_entity"], "url": BASE + "/about/"},
            "publisher": {"@type": "Organization", "name": CFG["identity"]["author_entity"], "url": BASE + "/"},
            "mainEntityOfPage": BASE + url("/guides/" + guide["slug"] + ".html"),
            "isAccessibleForFree": True,
        }
    ]
    return page(
        f"guide:{guide['id']}",
        f"/guides/{guide['slug']}.html",
        f"{guide.get('seo_title') or guide['title']} | Counterwise",
        guide.get("seo_description") or guide["deck"],
        main,
        "guide",
        active="guides",
        jsonld=ld,
    )


def guides_hub() -> str:
    cards = "".join(
        f"""<a class="card card--link" href="{url('/guides/' + g['slug'] + '.html')}">
      <span class="kicker">{esc(g['question_answered'])}</span>
      <h3>{esc(g['title'])}</h3>
      <p>{esc(g['deck'])}</p>
      <p class="meta">{reading_minutes(body_of(g))} min · published {fmt_date(g['published'])} · {esc(' · '.join(CLUSTERS[c]['short_name'] for c in g['clusters']))}</p>
    </a>"""
        for g in GUIDES.values()
    )
    main = f"""
<section class="sec">
  <div class="wrap">
    <div class="page-head">
      <span class="kicker">The set</span>
      <h1>Five guides, one question each</h1>
      <p class="deck">This is the whole editorial output so far, and that number is a decision rather than a limit
      on ambition: pages get added when they answer a question a real buyer asked, not to occupy a keyword.
      The reasoning is <a href="{url('/suggestions/')}#S-17">S-17</a>.</p>
    </div>
    <div class="grid-2">{cards}</div>
    <h2 style="margin-top:34px">What is deliberately missing</h2>
    <div class="grid-3">
      <div class="card"><h3>No "best of" list</h3><p>Nothing here ranks the four machines, because nothing here has cooked in them.</p></div>
      <div class="card"><h3>No prices</h3><p>Amazon shows a live number the moment you click; ours would be a photograph of yesterday.</p></div>
      <div class="card"><h3>No review markup</h3><p>We publish no <code>Review</code> or <code>AggregateRating</code> structured data while that is true.</p></div>
    </div>
    {source_ref('SG-06','SG-07')}
  </div>
</section>
"""
    return page(
        "guides",
        "/guides/index.html",
        "Buying guides for air fryers, countertop ovens and probe thermometers",
        "Five question-shaped guides covering basket versus oven-style air fryers, capacity claims, cleanup and "
        "counter space, multi-function appliances and doneness — with sources named on every page.",
        main,
        "guide",
        active="guides",
    )


# --------------------------------------------------------------------------- clusters


def cluster_page(cid: str) -> str:
    c = CLUSTERS[cid]
    prods = "".join(
        product_card(pid, "cluster") for pid in c["products"] if pid in PUBLISHED_PRODUCT_IDS
    ) or '<p class="paid-note">No listing in this cluster has a verified destination yet.</p>'
    guides = "".join(
        f'<li><a href="{url("/guides/" + GUIDES[gid]["slug"] + ".html")}">{esc(GUIDES[gid]["title"])}</a> — '
        f'{esc(GUIDES[gid]["deck"])}</li>'
        for gid in c["guides"]
        if gid in GUIDES
    )
    main = f"""
<section class="sec">
  <div class="wrap">
    <div class="page-head">
      <span class="kicker">Cluster · {esc(c['seasonal'])}</span>
      <h1>{esc(c['name'])}</h1>
      <p class="deck">{esc(c['question'])}</p>
    </div>
    <p class="lead-para">{esc(c['description'])}</p>
    <div class="rail" style="margin:22px 0 8px">{prods}</div>
    <h2 style="margin-top:28px">Guides in this cluster</h2>
    <ul>{guides or '<li>None yet.</li>'}</ul>
    <div class="notice notice--info" style="margin-top:18px"><p>A cluster is one buying decision, not one keyword.
    A cluster with no listing and no guide is refused by the build, which is how thin category pages get prevented
    instead of apologised for.</p></div>
    {source_ref('SG-15','SG-06')}
  </div>
</section>
"""
    return page(
        f"cluster:{cid}",
        f"/clusters/{cid}/",
        f"{c['name']} — {c['question']} | Counterwise",
        c["description"][:158],
        main,
        "cluster",
        active="",
    )


# ---------------------------------------------------------------------- decision pages


def suggestions_page() -> str:
    cards = []
    for s in BOARD:
        opts = ""
        if s.get("options"):
            lis = "".join(
                f"<li><strong>{esc(o['label'])}</strong> — {esc(o['tradeoff'])}</li>" for o in s["options"]
            )
            opts = f'<div class="srow"><span>Options</span><ol class="opts">{lis}</ol></div>'
        status = s["status"]
        kind = "ok" if status.startswith("shipped") else ("warn" if status == "needs-pick" else "gap")
        snippet = (
            f'<div class="srow"><span>For the design brief</span><p>{esc(s["prompt_snippet"])}</p></div>'
            if s.get("prompt_snippet")
            else ""
        )
        review = s.get("review_decision") or ""
        cards.append(
            f"""<article class="sug" id="{esc(s['id'])}">
      <div class="row" style="display:flex;gap:6px;flex-wrap:wrap"><span class="flagid">{esc(s['id'])}</span>
        {chip(kind, status)}{chip('plain', s.get('priority',''), 'from the program brief')}
        {chip('plain', s.get('category',''))}</div>
      <h3>{esc(s['title'])}</h3>
      <div class="srow"><span>Proposal</span><p>{esc(s['proposal'])}</p></div>
      <div class="srow"><span>Why</span><p>{esc(s['why'])}</p></div>
      <div class="srow"><span>Effect on readers</span><p>{esc(s['effect_on_readers'])}</p></div>
      <div class="srow"><span>Cost · effort</span><p>{esc(s.get('cost',''))} · {esc(s.get('effort',''))} · risk {esc(s.get('risk',''))} · reversible {esc(s.get('reversible',''))}</p></div>
      {f'<div class="srow"><span>Depends on</span><p>{esc(", ".join(s["depends_on"]) if s.get("depends_on") else "nothing")}</p></div>'}
      {opts}
      {f'<div class="srow"><span>Recommended</span><p>{esc(s["recommended"])}</p></div>' if s.get('recommended') else ''}
      {snippet}
      <p class="decide">Review decision: {esc(review) if review else "— blank, nothing chosen yet. Fill `review_decision` on row " + s['id'] + " in data/suggestions.json and rebuild."}</p>
    </article>"""
        )
    counts = {"shipped": 0, "needs-pick": 0, "proposed": 0}
    for s in BOARD:
        st = s["status"]
        counts["shipped" if st.startswith("shipped") else ("needs-pick" if st == "needs-pick" else "proposed")] += 1
    main = f"""
<section class="sec">
  <div class="wrap">
    <div class="page-head">
      <span class="kicker">Review before you rebuild</span>
      <h1>Suggestions board</h1>
      <p class="deck">Every proposal for this site in one place, with its cost, its risk, whether it can be undone,
      and what it depends on. {counts['shipped']} are already in the build. {counts['needs-pick']} need a choice that
      only the account holder can make. Nothing here has been done on your behalf beyond what is marked shipped, and
      the empty decision lines are the point: this page is a board, not a report.</p>
    </div>
    <div class="stat-strip" style="margin-bottom:24px">
      <div><span class="n">{len(BOARD)}</span><span class="l">suggestions on the board</span></div>
      <div><span class="n">{counts['shipped']}</span><span class="l">shipped in this build</span></div>
      <div><span class="n">{counts['needs-pick']}</span><span class="l">awaiting your pick</span></div>
      <div><span class="n">{counts['proposed']}</span><span class="l">queued, untouched</span></div>
    </div>
    <ul class="anchor-list" style="margin-bottom:22px">
      {''.join(f'<li><a href="#{esc(s["id"])}">{esc(s["id"])} · {esc(s["title"][:38])}</a></li>' for s in BOARD)}
    </ul>
    <div class="board">{"".join(cards)}</div>
  </div>
</section>
"""
    return page(
        "suggestions",
        "/suggestions/index.html",
        "Suggestions board — every proposal, with costs and options",
        "Twenty-three decisions laid out with proposal, rationale, effort, risk and reversibility, so the cheapest "
        "useful change can be picked before anything is rebuilt.",
        main,
        "paperwork",
        active="board",
    )


def questions_page() -> str:
    cards = []
    for q in QUESTIONS:
        cards.append(
            f"""<article class="qcard" id="{esc(q['id'])}">
      <h3><span class="flagid">{esc(q['id'])}</span><br>{esc(q['question'])}</h3>
      <div class="srow">
        <span>Why it matters</span><p>{esc(q['why_it_matters'])}</p>
        <span>We already have</span><p>{esc(q['we_have'])}</p>
        <span>Missing</span><p>{esc(q['we_lack'])}</p>
        <span>How to find out</span><p>{esc(q['how_to_find_out'])}</p>
        <span>Who can answer</span><p>{esc(q['who_can_answer'])}</p>
        <span>Blocks</span><p>{esc(' · '.join(q.get('blocks', [])))}</p>
        <span>Meanwhile</span><p>{esc(q['default_applied'])}</p>
      </div>
    </article>"""
        )
    c = load("questions.json")["counts"]
    main = f"""
<section class="sec">
  <div class="wrap">
    <div class="page-head">
      <span class="kicker">Before a decision is reasonable</span>
      <h1>Open questions, what we have, and how to get the rest</h1>
      <p class="deck">{c['total']} questions. For each one: the information already in hand, the exact gap, the way
      to close it, who can close it, and what this build does while waiting. {c['answerable_only_inside_the_account']}
      of them can only be answered inside the Associates account — no crawler, model or scrape substitutes for that,
      which is why the site says so instead of guessing.</p>
    </div>
    <ul class="anchor-list" style="margin:6px 0 22px">
      {''.join(f'<li><a href="#{esc(q["id"])}">{esc(q["id"])}</a></li>' for q in QUESTIONS)}
    </ul>
    {"".join(cards)}
    <div class="notice notice--ok" style="margin-top:22px"><p><strong>Nothing here blocks the site going live.</strong>
    The gaps change what the site is allowed to claim, not whether it can exist — that separation is the reason the
    pages read like a shop instead of an apology.</p></div>
  </div>
</section>
"""
    return page(
        "questions",
        "/questions/index.html",
        "Open questions to settle before deciding anything",
        "Fourteen decision-blocking questions with what is known, what is missing, how to find out, who can answer, "
        "and the fallback the site applies while each stays open.",
        main,
        "paperwork",
        active="",
    )


def review_page() -> str:
    order = {"blocker": 0, "open": 1, "info": 2, "low": 3}
    rows = []
    for f in sorted(FLAGS.values(), key=lambda x: (order.get(x["severity"], 9), x["id"])):
        ev = "".join(
            ext(
                e,
                f"<code>{esc(re.sub('https?://', '', e)[:44])}</code>",
                pid_or_citation(next((pid for pid, pp in PRODUCTS.items() if e == pp["observation"].get("listing_url_observed")), "")),
            )
            if e.startswith("http")
            else f"<code>{esc(e)}</code>"
            for e in f.get("evidence", [])
        )
        kind = {"blocker": "warn", "open": "warn", "low": "gap", "info": "plain"}.get(f["severity"], "gap")
        rows.append(
            f"""<li id="{esc(f['id'])}">
      <div class="row" style="display:flex;gap:6px;flex-wrap:wrap;align-items:center">
        <span class="flagid">{esc(f['id'])}</span>{chip(kind, f['severity'])}{chip('plain', f['kind'])}
        <span class="meta">raised {fmt_date(f['raised'])} · {esc(f['status'])}</span>
      </div>
      <h3>{esc(f['title'])}</h3>
      <p>{esc(f['detail'])}</p>
      <p><strong>For a reader:</strong> {esc(f['buyer_impact'])}</p>
      <p class="action"><strong>Action to close it:</strong> {esc(f['action'])}</p>
      <div class="evid"><span class="meta">Evidence</span>{ev}</div>
    </li>"""
        )
    mapping = "".join(
        f"<tr><td><code>{esc(m['brief_id'])}</code></td><td>{esc(m['brief_said'])}</td><td>{esc(m['found_here'])}</td></tr>"
        for m in load("flags.json")["brief_id_mapping"]
    )
    blockers = sum(1 for f in FLAGS.values() if f["severity"] == "blocker")
    main = f"""
<section class="sec">
  <div class="wrap">
    <div class="page-head">
      <span class="kicker">Published, not buried</span>
      <h1>Flagged for review</h1>
      <p class="deck">{len(FLAGS)} items this project could not settle: {blockers} of them block a claim, none of them
      block the site. Every row says what was checked, what the reader should make of it, and the action that would
      close it. Nothing here is quietly inferred to fill a gap.</p>
    </div>
    <ul class="anchor-list" style="margin-bottom:22px">
      {''.join(f'<li><a href="#{esc(f["id"])}">{esc(f["id"])}</a></li>' for f in FLAGS.values())}
    </ul>
    <ul class="flags">{"".join(rows)}</ul>
    <h2 style="margin-top:30px">The brief's own row IDs, and what happened to them</h2>
    <p class="sec-note">The program brief cites source and flag IDs as though a register already existed. It did not:
    the repository held one README. This is what was found for each referenced ID, and where it now lives.</p>
    <div class="table-wrap"><table><thead><tr><th>ID in the brief</th><th>What the brief said</th><th>What this project found</th></tr></thead>
    <tbody>{mapping}</tbody></table></div>
    <p class="paid-note" style="margin-top:14px">Corrections are welcome and change the register, not the HTML:
    edit <code>data/*.json</code>, run <code>python3 tools/build.py</code>, and the gate decides whether the claim is
    allowed on a page.</p>
  </div>
</section>
"""
    return page(
        "review",
        "/review/index.html",
        "Flagged for review — the open items, with sources",
        "Every item this affiliate project could not verify from an official source: what was checked, what is "
        "missing, the impact on a reader, and the action that closes it.",
        main,
        "paperwork",
        active="",
    )


def summary_page() -> str:
    acct = [q for q in QUESTIONS if "owner" in q["who_can_answer"].lower() or "account" in q["who_can_answer"].lower()]
    shipped = sum(1 for s in BOARD if s["status"].startswith("shipped"))
    main = f"""
<section class="sec">
  <div class="wrap narrow" style="max-width:47rem">
    <div class="page-head">
      <span class="kicker">Executive summary</span>
      <h1>What exists, what is proven, what is waiting on one person</h1>
    </div>
    <p class="lead-para">This repository is now a working affiliate publication with a verification gate in front of
    it. The site builds itself from a register of sources and evidence; a build fails when a page would claim more
    than the register supports. That inversion — automation for plumbing, a gate for claims — is the single design
    decision everything else follows from.</p>

    <h2>The catalogue</h2>
    <p>Five links were supplied. Four resolved to a readable product page on 2026-11-20: a twin-basket air fryer, a
    26-quart French-door countertop oven, an 8-quart single basket, and a three-probe wireless meat thermometer.
    Together they describe one coherent shelf — countertop cooking, plus the instrument that makes it reliable — so
    the niche was adopted rather than invented. The fifth link never reached a listing from this environment and is
    published as an empty row with a reason. Every token in the five supplied links is nine characters, while the
    listings they opened carry ten-character identifiers; that arithmetic is why no ASIN is recorded as
    <em>intended</em> for any row.</p>

    <h2>What was verified against primary sources</h2>
    <p>Amazon's help text for the disclosure statement, the fixed commission table, Google's documentation of
    <code>rel="sponsored"</code> and of product structured data, the March 2024 spam policy on scaled content, the
    FTC Endorsement Guides as codified, and the USDA temperature chart. The full register — with what was read in
    full, what was captured as a snippet, and what was never read at all — is on the
    <a href="{url('/transparency/sources/')}">source page</a>. A register that graded nothing would be decoration.</p>

    <h2>Two findings that change the plan</h2>
    <p><strong>First, the tracking.</strong> None of the four resolved destinations carried a <code>tag=</code>
    parameter. As supplied, those links would have earned nothing, however much traffic arrived. The site therefore
    publishes rebuilt links with <code>tag={esc(TRACKING)}</code>, and the build refuses any Amazon link without it.
    The remaining step is small and human: prove one click per product in the reporting interface.</p>
    <p><strong>Second, the money is ambiguous and stays that way.</strong> The published fixed rates include
    Furniture, Home, Home Improvement, Lawn &amp; Garden, Pets Products at 3.00%, and a row containing Kitchen at
    1.25%. Air fryers sit under a Home &amp; Kitchen breadcrumb, which decides nothing. A forecast built on either
    number would be fiction, so none is published anywhere on this site; the category is recorded from the first
    real report instead.</p>

    <h2>Reader-facing polish</h2>
    <p>Five question-shaped guides, three clusters, a comparison table in real HTML, disclosure above the fold on
    every page and repeated in the footer, artwork drawn for the site rather than lifted from a listing, an Atom
    feed, a sitemap, a written privacy page that matches the code, and an editorial voice enforced by the build
    instead of requested in a prompt. {shipped} of the {len(BOARD)} suggestions on the board are already shipped.</p>

    <h2>Measurement</h2>
    <p>The five-event schema exists, the click beacon is wired to it, and a stdlib collector is in the repository,
    deliberately unarmed: static hosting cannot run it, and an empty ledger is more useful than a plausible one.
    Nothing is labelled a conversion rate. The moment an endpoint is configured the ledger begins to fill from
    measured clicks, and only Amazon's own reports may add orders.</p>

    <h2>What is waiting on you</h2>
    <p>{len(acct)} questions can only be answered by whoever holds the account — the intended listing per link, the
    existence and live test of the tracking ID, PA-API access, the Search Console property, and the marketplace
    boundary. Each carries the default this site applies while it stays open, so the project moves without waiting
    and no one has to invent an answer.</p>

    <div class="notice notice--ok"><p><strong>Where it stands:</strong> a published site with four listings, five
    guides, {len(SOURCES)} registered sources, {len(FLAGS)} open items shown on the review page, zero published
    prices or ratings, and one test in the Associates interface between this and scaling.</p></div>
    {source_ref('SG-01','SG-02','SG-04','SG-05','SG-06','SG-08','SG-11')}
  </div>
</section>
"""
    return page(
        "summary",
        "/summary/index.html",
        "Executive summary — what was proved, what was refused",
        "One page on the state of the programme: five supplied links, four verified listings, two findings that change "
        "the plan, what was verified against primary sources, and the short list of things only the account holder can "
        "answer.",
        main,
        "paperwork",
        active="summary",
    )


# --------------------------------------------------------------------- transparency


def transparency_hub() -> str:
    items = [
        ("sources", "Source register", f"{len(SOURCES)} rows: what each official page supports, how it was read, and when."),
        ("verification", "Link and product evidence", "The supplied links, where they led, the tag that was missing, and the intent records kept deliberately blank."),
        ("method", "How this is built", "Data → gate → HTML, the rules the gate enforces, the image policy, the cadence, and how to add a row."),
        ("gate-report", "Gate report", "The output of the last verification run: every rule, its finding count, and what was built from which inputs."),
    ]
    cards = "".join(
        f'<a class="card card--link" href="{url("/transparency/" + slug + "/")}"><h3>{esc(t)}</h3><p>{esc(d)}</p></a>'
        for slug, t, d in items
    )
    main = f"""
<section class="sec">
  <div class="wrap">
    <div class="page-head">
      <span class="kicker">The audit surface, kept one click away</span>
      <h1>Transparency</h1>
      <p class="deck">A buyer should read the guides, not the evidence chain. But the chain has to exist and be
      checkable, so it lives here: sources, observations, the build rules that refuse unsupported claims, and the
      output of the last time they ran.</p>
    </div>
    <div class="grid-2">{cards}</div>
    <div class="stat-strip" style="margin-top:26px">
      <div><span class="n">{len(SOURCES)}</span><span class="l">registered sources</span></div>
      <div><span class="n">{sum(1 for s in SOURCES.values() if s['verification']=='read')}</span><span class="l">read in full</span></div>
      <div><span class="n">{sum(1 for s in SOURCES.values() if s['verification']=='snippet')}</span><span class="l">snippet-level from official domains</span></div>
      <div><span class="n">{sum(1 for s in SOURCES.values() if s['verification'] in ('not-read','queued'))}</span><span class="l">declared unread</span></div>
      <div><span class="n">{len(FLAGS)}</span><span class="l">flagged items</span></div>
    </div>
  </div>
</section>
"""
    return page(
        "transparency",
        "/transparency/index.html",
        "Transparency — sources, evidence and the rules this site builds under",
        "Where every claim on Counterwise comes from, how it was verified, and the mechanical rules that stop a page "
        "saying more than the register supports.",
        main,
        "paperwork",
    )


def sources_page() -> str:
    vchip = {"read": "ok", "snippet": "warn", "link-verified": "warn", "not-read": "gap", "queued": "gap"}
    rows = []
    for srow in SOURCES.values():
        supports = " · ".join(srow.get("what_it_supports", []))
        rows.append(
            "<tr><td><code>" + srow["id"] + "</code></td>"
            + "<td>" + esc(srow["org"]) + SUB(srow["kind"]) + "</td>"
            + "<td>" + ext(srow["url"], esc(srow["title"])) + "</td>"
            + "<td>" + esc(supports) + "</td>"
            + "<td>" + chip(vchip[srow["verification"]], srow["verification"])
            + SUB(srow["accessed"]) + "</td></tr>"
        )
    details = "".join(
        f"<tr><td><code>{esc(s['id'])}</code></td><td>{esc(s['method'])}"
        + (f"<br><br><em>What it says that we rely on:</em> {esc(s['notes'])}" if s.get("notes") else "")
        + "</td></tr>"
        for s in SOURCES.values()
    )
    main = f"""
<section class="sec">
  <div class="wrap">
    <div class="page-head">
      <span class="kicker">Register</span>
      <h1>Sources, and how much of each one was actually read</h1>
      <p class="deck">A source list that does not say how the source was read is a costume. Every row here carries a
      retrieval method, a date, and a verification grade: <em>read in full</em>, <em>snippet from the official
      domain</em>, <em>link verified</em>, or <em>not read</em>. The last two are failures to be fixed, listed
      rather than hidden.</p>
    </div>
    <div class="table-wrap"><table>
      <thead><tr><th>ID</th><th>Organisation</th><th>Document</th><th>What it supports here</th><th>Verification</th></tr></thead>
      <tbody>{''.join(rows)}</tbody></table></div>
    <h2 style="margin-top:30px">Retrieval notes</h2>
    <div class="table-wrap"><table><thead><tr><th>ID</th><th>Method and the wording relied on</th></tr></thead><tbody>{details}</tbody></table></div>
    <p class="paid-note" style="margin-top:14px">Amazon's own help pages render policy text inside a signed-in
    session, so at least one clause here was taken from a copy of the same policy on another official marketplace and
    cross-checked against an archive: <a href="{url('/review/')}#FLG-006">FLG-006</a>.</p>
  </div>
</section>
"""
    return page(
        "sources",
        "/transparency/sources/index.html",
        "Source register — what was read, how, and when",
        "Amazon Associates policy text, FTC endorsement rules, Google Search Central documentation, USDA food safety "
        "figures and Amazon listing pages, graded by how completely each was read.",
        main,
        "paperwork",
    )


def verification_page() -> str:
    lrows = []
    for lid, l in LINKS.items():
        ok = l["resolution_status"].startswith("resolved")
        landed = l["observed_final_url"]
        shown = re.sub("https?://(www\.)?", "", landed)
        if ok:
            cell = ext(landed, "<code>" + esc(shown[:54]) + "…</code>", pid_or_citation(l.get("product_id", "")))
        else:
            cell = GAP(landed)
        tagcell = chip("warn", "absent") if not l["observed_tag_param_present"] else chip("ok", "present")
        lrows.append(
            "<tr><td><code>" + lid + "</code></td>"
            + "<td><code>" + esc(l["supplied_url"]) + "</code>"
            + SUB("token is " + str(l["supplied_token_length"]) + " characters, as supplied")
            + "</td>"
            + "<td>" + chip("ok" if ok else "gap", "resolved to a listing" if ok else "never reached a listing") + "</td>"
            + "<td>" + cell + "</td>"
            + "<td>" + (esc(l.get("observed_page_title", "")[:80]) if ok else GAP("no title captured")) + "</td>"
            + "<td>" + tagcell + SUB("in the destination URL") + "</td>"
            + "<td>" + esc(l["observed_on"]) + "</td></tr>"
        )
    prows = []
    blank = GAP("blank — not confirmable from outside the account")
    for pid, p in PRODUCTS.items():
        it, ob = p["intent"], p["observation"]
        prows.append(
            "<tr><td><code>" + pid + "</code></td><td>" + esc(p["display_name"]) + "</td>"
            + "<td>" + (esc(it["intended_asin"]) if it["intended_asin"] else blank) + "</td>"
            + "<td>" + (esc(it["official_listing_url"]) if it["official_listing_url"] else blank) + "</td>"
            + "<td>" + (esc(it["confirmation_date"]) if it["confirmation_date"] else blank) + "</td>"
            + "<td><code>" + esc(ob.get("listing_asin_observed_in_path", "")) + "</code>"
            + SUB("from the URL we loaded, " + str(ob.get("observed_on", ""))) + "</td>"
            + "<td>" + esc(it["status"]) + "</td></tr>"
        )
    main = f"""
<section class="sec">
  <div class="wrap">
    <div class="page-head">
      <span class="kicker">Evidence</span>
      <h1>What each link did, and what nobody has confirmed yet</h1>
      <p class="deck">Two tables that are usually merged in affiliate tooling and are kept apart here on purpose.
      <em>Observed</em> is what this project saw when it followed a link. <em>Intended</em> is a confirmation record
      only the account holder can write. Filling the second from the first is how a register starts lying.</p>
    </div>
    <h2>Supplied links</h2>
    <div class="table-wrap"><table>
      <thead><tr><th>ID</th><th>As supplied</th><th>Resolution</th><th>Where it landed</th><th>Page title, as captured</th><th>Tag in destination</th><th>Date</th></tr></thead>
      <tbody>{''.join(lrows)}</tbody></table></div>
    <p class="paid-note">Method: {esc(load('links.json')['resolution_method'])}</p>
    <h2 style="margin-top:30px">Product-intent confirmation records</h2>
    <div class="table-wrap"><table>
      <thead><tr><th>ID</th><th>Row</th><th>Intended ASIN</th><th>Official listing URL</th><th>Confirmed on</th><th>Observed identifier</th><th>Intent state</th></tr></thead>
      <tbody>{''.join(prows)}</tbody></table></div>
    <ul class="titled" style="margin-top:16px">
      {''.join(f'<li>{esc(r)}</li>' for r in load('products.json')['rules'])}
    </ul>
    <p class="paid-note" style="margin-top:16px">The five rules above are not style advice; three of them are
    enforced by <a href="{url('/transparency/gate-report/')}">the gate</a>.</p>
  </div>
</section>
"""
    return page(
        "verification",
        "/transparency/verification/index.html",
        "Link resolution and product-intent records",
        "The five supplied links with the destination each produced, the absent tracking tag, and the confirmation "
        "fields left blank because only the account holder can fill them.",
        main,
        "paperwork",
    )


def method_page() -> str:
    rules = "".join(
        f"<tr><td><code>{esc(rid)}</code></td><td>{esc(claim)}</td>"
        f"<td class=\"num\">{esc(findings)}</td></tr>"
        for rid, claim, findings in REPORT_RULE_ROWS
    )
    banned = "".join(
        f"<tr><td><code>{esc(pat)}</code></td><td>{esc(scope)}</td><td>{esc(why)}</td></tr>"
        for pat, scope, why in gate.BANNED_PATTERNS
    )
    cad = CFG["cadence"]
    main = f"""
<section class="sec">
  <div class="wrap">
    <div class="page-head">
      <span class="kicker">The machinery</span>
      <h1>How this site is built, and what refuses to build</h1>
      <p class="deck">Three commands stand between a data edit and a published page:
      <code>python3 tools/build.py</code>, then <code>python3 tools/gate.py</code>, then a commit. The generator has
      no opinions; the gate has seventeen of them.</p>
    </div>
    <div class="grid-2" style="align-items:start">
      <div>
        <h2>The pipeline</h2>
        <ol>
          <li><code>data/*.json</code> and <code>content/guides/*.md</code> are the only place facts are written.</li>
          <li><code>tools/build.py</code> renders every page, the sitemap, the feed and this report from those files.
              Nothing is hand-written in <code>docs/</code>.</li>
          <li><code>tools/gate.py</code> checks the finished HTML against the register: sources, disclosure
              placement, tagged and marked outbound links, resolvable internal links, banned voice, structured data
              that never overclaims, and output freshness by content hash.</li>
          <li>A failed gate exits non-zero, so the CI workflow on every push fails and the site cannot be published
              broken or unsourced.</li>
        </ol>
        <h2>Where images come from</h2>
        <p>Drawn for this site and captioned as illustration. No Amazon product imagery appears anywhere, because
        program imagery is licensed through program tooling rather than scraped from a page, and because a
        manufacturer's render is the visual signature of a template site. That reverses when an authorized feed
        exists: <a href="{url('/questions/')}#Q-05">Q-05</a>.</p>
        <h2>Editorial cadence</h2>
        <dl class="kv">
          <dt>Status</dt><dd>{esc(cad['status'])}</dd>
          <dt>Rule</dt><dd>{esc(cad['rule'])}</dd>
          <dt>Window</dt><dd>{esc(cad['first_publication_window'])}</dd>
          <dt>Review</dt><dd>{esc(cad['review_point'])}</dd>
        </dl>
        <h2>How to add or correct a row</h2>
        <pre><code>edit data/products.json (or sources, guides, flags…)
python3 tools/build.py      # regenerate docs/
python3 tools/gate.py        # exit 0 or it does not ship
python3 -m unittest discover -s tests</code></pre>
      </div>
      <div>
        <h2>Gate rules and last finding counts</h2>
        <div class="table-wrap"><table><thead><tr><th>Rule</th><th>What it enforces</th><th class="num">Findings</th></tr></thead>
          <tbody>{rules}</tbody></table></div>
        <h2 style="margin-top:26px">Banned phrasing, and why</h2>
        <div class="table-wrap"><table><thead><tr><th>Pattern</th><th>Applies to</th><th>Reason</th></tr></thead>
          <tbody>{banned}</tbody></table></div>
        <p class="paid-note">A pattern list is a blunderbuss, so every entry carries its reason and can be waived per
        page in <code>tools/gate.py</code>. "not published by us" is allowed on this site; "we tested" is not, until
        somebody does.</p>
      </div>
    </div>
  </div>
</section>
"""
    return page(
        "method",
        "/transparency/method/index.html",
        "How this site is generated, and what its gate refuses",
        "The register-to-HTML pipeline, the seventeen rules the gate enforces, the banned-voice list with reasons, "
        "the image policy and the publishing cadence.",
        main,
        "paperwork",
    )


def gate_report_page() -> str:
    rows = "".join(
        f"<tr><td><code>{esc(r['id'])}</code></td>"
        f"<td>{chip('ok' if r['ok'] else 'warn', 'pass' if r['ok'] else 'fail')}</td>"
        f"<td>{esc(r['claim'])}</td><td class=\"num\">{r['findings']}</td></tr>"
        for r in REPORT["rules"]
    )
    fails = "".join(f"<li><code>{esc(f)}</code></li>" for f in REPORT["failures"][:40]) or (
        "<li>None. Every rule passed on this build.</li>"
    )
    st = REPORT["stats"]
    main = f"""
<section class="sec">
  <div class="wrap">
    <div class="page-head">
      <span class="kicker">Machine output</span>
      <h1>Gate report</h1>
      <p class="deck">Produced by <code>tools/gate.py</code> during this build, over {st['pages']} pages and
      {st['data_files']} register files. A site that claims to be careful should show the check, not the claim.</p>
    </div>
    <div class="stat-strip" style="margin-bottom:20px">
      <div><span class="n">{sum(1 for r in REPORT['rules'] if r['ok'])}/{len(REPORT['rules'])}</span><span class="l">rules passing</span></div>
      <div><span class="n">{len(REPORT['failures'])}</span><span class="l">findings on this run</span></div>
      <div><span class="n">{st['guides']}</span><span class="l">guides</span></div>
      <div><span class="n">{st['sources']}</span><span class="l">sources</span></div>
      <div><span class="n">{round(st['html_bytes']/1024)} KB</span><span class="l">total HTML, all pages</span></div>
    </div>
    <div class="table-wrap"><table><thead><tr><th>Rule</th><th>State</th><th>What it checks</th><th class="num">Findings</th></tr></thead>
      <tbody>{rows}</tbody></table></div>
    <h2 style="margin-top:26px">Findings on the content audit</h2>
    <ul>{fails}</ul>
    <h2 style="margin-top:22px">Build provenance</h2>
    <dl class="kv">
      <dt>Inputs hash</dt><dd><code>{esc(REPORT['generated_from'])}</code> — SHA-256 over every file in <code>data/</code> and <code>content/</code>; the gate fails if the committed HTML was built from anything else.</dd>
      <dt>Sources of truth</dt><dd><code>data/</code> · <code>content/guides/</code> — <code>docs/</code> is output and is never hand-edited</dd>
      <dt>Runtime</dt><dd>Python standard library only; no template engine, no CSS framework, no build dependencies to drift</dd>
      <dt>Second pass</dt><dd>the audit is re-run after this page is written; if the numbers changed, the build rewrites this page and re-audits until it agrees with itself</dd>
    </dl>
  </div>
</section>
"""
    return page(
        "gate-report",
        "/transparency/gate-report/index.html",
        "Gate report — which verification rules passed",
        "The output of the site's own verification run: rule by rule, with finding counts and the input hash the "
        "pages were generated from.",
        main,
        "paperwork",
        index=True,
    )


def metrics_page() -> str:
    rows = "".join(
        f"<tr><td><code>{esc(e['id'])}</code></td><td><code>{esc(e['name'])}</code></td>"
        f"<td>{esc(e['fires_on'])}</td><td>{esc(e['decision_it_serves'])}</td></tr>"
        for e in EVENTS["events"]
    )
    props = "".join(
        "<tr><td><code>%s</code></td><td>%s</td></tr>"
        % (esc(e["name"]), esc(" · ".join(f"{k}: {v}" for k, v in e["properties"].items())))
        for e in EVENTS["events"]
    )
    led = DATA / "ledger" / "campaign_ledger.csv"
    data_rows = max(0, len([l for l in led.read_text(encoding="utf-8").splitlines() if l.strip()]) - 1) if led.exists() else 0
    main = f"""
<section class="sec">
  <div class="wrap">
    <div class="page-head">
      <span class="kicker">Measurement</span>
      <h1>Click and conversion measurement, built and deliberately unarmed</h1>
      <p class="deck">Five events, one collector, one ledger and no numbers — because a static host is not running
      the collector yet and inventing a dashboard would be the worst possible first act. This page is the honest
      version of "analytics is set up".</p>
    </div>
    <div class="notice notice--info"><p><strong>State:</strong> endpoint
    <code>{esc(CFG['measurement']['endpoint'] or '(unset)')}</code> · status <code>{esc(CFG['measurement']['status'])}</code>
    · ledger rows <strong>{data_rows}</strong>. While the endpoint is empty the page queues events in this browser's
    <code>localStorage</code> and sends nothing anywhere. Setting one value in
    <code>data/config.json</code> and rebuilding turns collection on; the queue then flushes once.</p></div>
    <h2>The five events</h2>
    <div class="table-wrap"><table><thead><tr><th>ID</th><th>Event</th><th>Fires on</th><th>Decision it serves</th></tr></thead>
      <tbody>{rows}</tbody></table></div>
    <h2 style="margin-top:26px">Payloads</h2>
    <div class="table-wrap"><table><thead><tr><th>Event</th><th>Properties</th></tr></thead><tbody>{props}</tbody></table></div>
    <h2 style="margin-top:26px">Privacy posture</h2>
    <ul>{''.join(f'<li>{esc(r)}</li>' for r in EVENTS['privacy_rules'])}</ul>
    <h2 style="margin-top:26px">Turning it on</h2>
    <pre><code>python3 tools/collector.py serve --port 8099      # or any host that can run one process
# data/config.json → measurement.endpoint = "https://metrics.example.org"
python3 tools/build.py && python3 tools/gate.py</code></pre>
    <p class="paid-note">The Amazon side of the ledger — orders, commission, product category — may only be written
    from an authorized first-party report, with the report named on the row. That part has a human gate on purpose:
    <code>python3 tools/ledger.py append --help</code>.</p>
    <h2 style="margin-top:26px">What will not appear here</h2>
    <p>No conversion score, no revenue forecast, no modelled earnings, and no percentage attributed to a page that
    has been visited by nobody but a build script.</p>
  </div>
</section>
"""
    return page(
        "metrics",
        "/metrics/index.html",
        "Measurement — five events, a collector, no invented rows",
        "The click and conversion measurement schema this affiliate site ships with, its privacy rules, its current "
        "unarmed state, and the one-line change that enables it.",
        main,
        "paperwork",
    )


def about_page() -> str:
    main = f"""
<section class="sec">
  <div class="wrap narrow" style="max-width:44rem">
    <div class="page-head"><span class="kicker">Who is speaking</span><h1>About, and what a byline means here</h1></div>
    <p class="lead-para">Counterwise is an editorial system with a verification gate. Pages are signed
    <strong>{esc(CFG['identity']['author_entity'])}</strong> because that is what they are: assembled from listings
    that were loaded and from policy documents that were read, then refused or allowed by a build script. There is no
    test kitchen, and the site says so in place of a stock photo of someone holding a spatula.</p>
    <h2>The rules we hold ourselves to</h2>
    <ul>
      <li><strong>No claim of use.</strong> Nothing is "tested", "tried" or "hands-on" unless someone here has done it,
      and no one has.</li>
      <li><strong>No invented attributes.</strong> A product string is either lifted from the listing with its capture
      date, or the field is blank and flagged.</li>
      <li><strong>No prices, no ratings.</strong> Amazon shows the live price at the click.</li>
      <li><strong>Commission is disclosed above the fold, on every page.</strong>
      {esc(STATEMENT)}</li>
      <li><strong>Mistakes get published, not deleted.</strong> The review page lists what is unsettled, with the source
      that would settle it.</li>
    </ul>
    <h2>Corrections</h2>
    <p>If a row here is wrong, the fix is a change to <code>data/</code> in the
    <a href="{esc(CFG['repository']['clone'])}">repository</a>, followed by a rebuild; the site's HTML is generated, so
    an edit that is not in the register does not survive. That is a deliberate inconvenience: it makes an unsourced
    change impossible.</p>
    <h2>Why this niche</h2>
    <p>Because four of five supplied links resolved to countertop cooking appliances and the fifth to a probe
    thermometer, which is a coherent shelf rather than a random set of products. Adopting what the evidence said,
    instead of inventing a market that sounded better, is the entire method in miniature.</p>
    {source_ref('SG-01','SG-06','SG-08')}
  </div>
</section>
"""
    return page(
        "about",
        "/about/index.html",
        "About Counterwise — who signs these pages, and what a byline means here",
        "Who signs the pages here, what a byline means when the work is automated, and the five rules the build "
        "enforces on every claim.",
        main,
        "paperwork",
        active="",
    )


def disclosure_page() -> str:
    main = f"""
<section class="sec">
  <div class="wrap narrow" style="max-width:44rem">
    <div class="page-head"><span class="kicker">The money, plainly</span><h1>Disclosure</h1></div>
    <p class="lead-para"><strong>{esc(STATEMENT)}</strong> That sentence appears under the masthead of every page on
    this site and again in the footer of every page, because Amazon requires that exact statement to appear clearly
    and conspicuously on the site, and because a reader should not have to hunt for the answer to "who pays you".</p>
    <p>The Federal Trade Commission's example of wording a reader understands is a second, separate
    obligation: <strong>“{esc(FETCH_EXAMPLE)}”</strong> It appears in the strip at the top of every page here,
    because a disclosure a reader has to go looking for is a disclosure that does not work.</p>
    <h2>What that means in practice</h2>
    <ul>
      <li>Links to Amazon carry our Associates tag. If you click one and buy, Amazon pays this site a share of the
      sale from the seller. The price you pay does not change.</li>
      <li>Every product link on the page carries a <b>(paid link)</b> label next to it, not a footnote pointing at
      one. Amazon's guidance is that a link-level disclosure should be clear — "(paid link)", "#ad" or
      "#CommissionsEarned" are its own examples — and conspicuous enough that readers notice it near the link.</li>
      <li>Those links are marked <code>rel="sponsored nofollow"</code> so search engines read them as paid
      placements, which is what they are.</li>
      <li>Nothing here is paid for by a brand. No sample has been received from any manufacturer on the register
      (<a href="{url('/questions/')}#Q-13">Q-13</a>), which is what makes the last point true.</li>
    </ul>
    <h2>What this site is not</h2>
    <p>It is not Amazon, it is not affiliated with the brands named in any listing, and it is not a review outlet: no
    product on these pages has been used by anyone here. Where the law and the program overlap — material connections
    under the FTC's Endorsement Guides at 16 CFR Part 255, the disclosure statement in Amazon's agreement — placement
    is the whole practical question, and placement is on every page rather than on an easy-to-miss page.</p>
    <h2>Reading the fine print yourself</h2>
    <p>Two pages we did not read in full this session and do not paraphrase: the
    <a href="{esc(SOURCES['SG-03']['url'])}" target="_blank" rel="nofollow noopener">Associates Operating Agreement</a>,
    which renders inside a signed-in account, and the two FTC guidance pages Amazon's own help article points to.
    The gap is recorded as <a href="{url('/review/')}#FLG-006">FLG-006</a> rather than papered over.</p>
    {source_ref('SG-01','SG-02','SG-05','SG-08')}
  </div>
</section>
"""
    return page(
        "disclosure",
        "/disclosure/index.html",
        "Disclosure — how Counterwise earns from links",
        "The required Amazon Associates statement, what a paid link means for the reader, how links are marked, and "
        "which policy texts this site has not read in full.",
        main,
        "paperwork",
    )


def privacy_page() -> str:
    main = f"""
<section class="sec">
  <div class="wrap narrow" style="max-width:44rem">
    <div class="page-head"><span class="kicker">Short, because it is true</span><h1>Privacy</h1></div>
    <p class="lead-para">This site sets no cookies, loads no webfont, makes no request to any third party, and — as of
    this build — stores nothing at all about you. The measured state and the code are described on the
    <a href="{url('/metrics/')}">metrics page</a>.</p>
    <h2>If collection is ever switched on</h2>
    <ul>
      <li>Only the five events named in <a href="{url('/metrics/')}">the schema</a> may be recorded.</li>
      <li>No IP address is stored. No cookie or fingerprint identifies a reader. Page paths are stored; query strings
      are dropped, so a tagged link cannot leak a session value into a log.</li>
      <li><code>Do Not Track</code> and Global Privacy Control signals stop collection before the first event, in
      code rather than in prose.</li>
      <li>Checklist ticks live in your own browser's storage and never reach us.</li>
    </ul>
    <h2>Reader details</h2>
    <p>The email field on guide pages does not send anything, because no capture endpoint is configured. It says so
    on the page rather than quietly swallowing what you typed. If that changes, this page changes in the same commit —
    and the build fails if collection is enabled while the privacy text still promises nothing.</p>
    <h2>Amazon</h2>
    <p>Following a link here takes you to Amazon, where their own cookie and privacy terms apply, including the
    attribution window that lets a purchase you make later still credit the link you clicked. We keep no record of
    that and cannot see its contents.</p>
    {source_ref('SG-01')}
  </div>
</section>
"""
    return page(
        "privacy",
        "/privacy/index.html",
        "Privacy — no cookies, no third parties, nothing stored",
        "What this site collects (nothing), what it will collect if measurement is enabled (five events, no IP, no "
        "identifiers), and how opt-out is honoured in code.",
        main,
        "paperwork",
    )


def notfound_page() -> str:
    main = f"""
<section class="sec">
  <div class="wrap narrow">
    <div class="page-head"><span class="kicker">404</span><h1>That page is not here</h1>
    <p class="deck">Either it moved or it never existed. Both are our fault rather than yours, and this build
    refuses broken internal links, so the likelier answer is a stale bookmark from a draft.</p></div>
    <div class="grid-3">
      <a class="card card--link" href="{url('/guides/')}"><h3>Guides</h3><p>Five of them, one question each.</p></a>
      <a class="card card--link" href="{url('/gear/')}"><h3>Gear we track</h3><p>The four listings with captured evidence.</p></a>
      <a class="card card--link" href="{url('/review/')}"><h3>Flagged for review</h3><p>Everything this site could not settle.</p></a>
    </div>
  </div>
</section>
"""
    return page("404", "/404.html", "Not found — Counterwise", "The page you asked for is not on this site: it either moved or it never existed. Guides, the gear register and the review page are one click away.", main, "paperwork", index=False)


# ----------------------------------------------------------------------------- feed etc


def atom_feed() -> str:
    def item(g):
        link = BASE + url("/guides/" + g["slug"] + ".html")
        cats = "".join(f'<category term="{esc(CLUSTERS[c]["short_name"])}"/>' for c in g["clusters"])
        return f"""  <entry>
    <title>{esc(g['title'])}</title>
    <link href="{link}"/>
    <id>{link}</id>
    <updated>{g['updated']}T09:00:00Z</updated>
    <published>{g['published']}T09:00:00Z</published>{cats}
    <author><name>{esc(CFG['identity']['author_entity'])}</name><uri>{BASE}/about/</uri></author>
    <summary>{esc(g['deck'])}</summary>
    <content type="html">{esc(md_to_html(body_of(g), PREFIX))}</content>
    <rights>{esc(STATEMENT)}</rights>
  </entry>"""

    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{esc(CFG['identity']['name'])}</title>
  <subtitle>{esc(CFG['identity']['tagline'])}</subtitle>
  <link href="{BASE}{url('/')}"/>
  <link rel="self" href="{BASE}{url('/feed.xml')}"/>
  <id>{BASE}/</id>
  <updated>{TODAY}T09:00:00Z</updated>
  <author><name>{esc(CFG['identity']['author_entity'])}</name><uri>{BASE}/about/</uri></author>
  <rights>{esc(STATEMENT)}</rights>
  <generator>tools/build.py</generator>
{chr(10).join(item(g) for g in GUIDES.values())}
</feed>
"""


def sitemap() -> str:
    entries = []
    for meta in ALL_PAGES.values():
        if not meta["index"]:
            continue
        loc = BASE + meta["path"]
        if loc.endswith("/index.html"):
            loc = loc[: -len("index.html")]
        entries.append(
            f"  <url><loc>{esc(loc)}</loc><lastmod>{TODAY}</lastmod></url>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )


# ------------------------------------------------------------------------------- main


def page_plan() -> list[tuple[str, bool]]:
    """(relative output path, indexable?) for every page this build emits. Used to keep the
    footer and the sitemap counts identical across pages rendered at different moments."""
    items: list[tuple[str, bool]] = [("index.html", True), ("gear/index.html", True)]
    for pid in PUBLISHED_PRODUCT_IDS:
        items.append((f"gear/{PRODUCTS[pid]['slug']}/index.html", True))
    items += [("compare/index.html", True), ("guides/index.html", True)]
    items += [(f"guides/{g['slug']}.html", True) for g in GUIDES.values()]
    items += [(f"clusters/{c['id']}/index.html", True) for c in CLUSTERS.values() if c["id"] != "unresolved"]
    items += [
        ("suggestions/index.html", True),
        ("questions/index.html", True),
        ("review/index.html", True),
        ("summary/index.html", True),
        ("transparency/index.html", True),
        ("transparency/sources/index.html", True),
        ("transparency/verification/index.html", True),
        ("metrics/index.html", True),
        ("about/index.html", True),
        ("disclosure/index.html", True),
        ("privacy/index.html", True),
    ]
    items += [
        ("transparency/method/index.html", True),
        ("transparency/gate-report/index.html", True),
        ("404.html", False),
    ]
    return items


def write(rel: str, content: str) -> None:
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_content_pages() -> None:
    write("index.html", front())
    write("gear/index.html", gear_index())
    for pid in PUBLISHED_PRODUCT_IDS:
        write(f"gear/{PRODUCTS[pid]['slug']}/index.html", gear_page(pid))
    write("compare/index.html", compare_page())
    write("guides/index.html", guides_hub())
    for g in GUIDES.values():
        write(f"guides/{g['slug']}.html", guide_page(g))
    for cid in CLUSTERS:
        if cid != "unresolved":
            write(f"clusters/{cid}/index.html", cluster_page(cid))
    write("suggestions/index.html", suggestions_page())
    write("questions/index.html", questions_page())
    write("review/index.html", review_page())
    write("summary/index.html", summary_page())
    write("transparency/index.html", transparency_hub())
    write("transparency/sources/index.html", sources_page())
    write("transparency/verification/index.html", verification_page())
    write("metrics/index.html", metrics_page())
    write("about/index.html", about_page())
    write("disclosure/index.html", disclosure_page())
    write("privacy/index.html", privacy_page())
    write("404.html", notfound_page())


def render_audit_pages(rep: dict) -> None:
    """The two pages whose numbers come from the gate. They are written last and rewritten until
    the audit they describe stops moving, so the report can never show a state the site is not in."""
    global REPORT, REPORT_RULE_ROWS
    REPORT = rep
    REPORT_RULE_ROWS = [(r["id"], r["claim"], r["findings"]) for r in rep["rules"]]
    write("transparency/method/index.html", method_page())
    write("transparency/gate-report/index.html", gate_report_page())


def render_aux_files(rep: dict) -> None:
    (OUT / "assets").mkdir(parents=True, exist_ok=True)
    src = ROOT / "assets-src"
    shutil.copy(src / "site.css", OUT / "assets" / "site.css")
    shutil.copy(src / "track.js", OUT / "assets" / "track.js")
    if (src / "img").exists():
        (OUT / "assets" / "img").mkdir(exist_ok=True)
        for img in sorted((src / "img").iterdir()):
            if img.suffix.lower() in (".png", ".jpg", ".jpeg", ".svg"):
                shutil.copy(img, OUT / "assets" / "img" / img.name)

    write("feed.xml", atom_feed())
    write("sitemap.xml", sitemap())
    write(
        "robots.txt",
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {BASE}/sitemap.xml\n"
        f"Feed: {BASE}/feed.xml\n"
        "# Static publication. No cookies, no webfonts, no third-party requests, and no analytics\n"
        "# endpoint configured in this build. See /privacy/ and /metrics/.\n",
    )
    write(
        "manifest.json",
        json.dumps(
            {
                "inputs_hash": data_hash(),
                "builder": "tools/build.py",
                "reproducible": "no wall-clock stamp in the manifest, so two builds of the same register produce byte-identical output and CI can require the committed site to match it",
                "pages": sorted(ALL_PAGES.keys()),
                "counts": {
                    "pages": len(page_plan()),
                    "guides": len(GUIDES),
                    "products": len(PRODUCTS),
                    "published_product_links": len(PUBLISHED_PRODUCT_IDS),
                    "sources": len(SOURCES),
                    "flags": len(FLAGS),
                    "suggestions": len(BOARD),
                    "questions": len(QUESTIONS),
                },
                "measurement": {"endpoint": ENDPOINT, "status": CFG["measurement"]["status"]},
                "tracking_id": TRACKING,
                "disclosure_statement": STATEMENT,
                "gate": {"rules": len(rep["rules"]), "findings": len(rep["failures"])},
            },
            indent=2,
        ),
    )
    write(
        "register/data.json",
        json.dumps(
            {
                "generated_from": data_hash(),
                "note": "Machine-readable copy of the register. The site is generated from this data; editing this copy changes nothing, and the gate fails because docs/ no longer matches data/.",
                "sources": load("sources.json")["sources"],
                "links": load("links.json")["links"],
                "products": load("products.json")["products"],
                "events": EVENTS["events"],
            },
            indent=2,
        ),
    )
    write("register/gate-report.json", json.dumps(rep, indent=2))
    (OUT / ".nojekyll").write_text("", encoding="utf-8")


GENERATED_DIRS = [
    "gear", "guides", "clusters", "compare", "questions", "suggestions", "review",
    "summary", "metrics", "about", "disclosure", "privacy", "transparency", "assets", "register",
]
GENERATED_FILES = [
    "index.html", "404.html", "feed.xml", "sitemap.xml", "robots.txt", "manifest.json", ".nojekyll",
]


def clean_generated() -> None:
    """Remove only what this builder writes. counterwise/ also holds data/, content/, tools/ and
    tests/, so a whole-directory wipe would eat the source of truth it is meant to read."""
    for name in GENERATED_DIRS:
        target = OUT / name
        if target.is_dir():
            shutil.rmtree(target)
    for name in GENERATED_FILES:
        target = OUT / name
        if target.exists():
            target.unlink()
    # A generated file left inside data/ would change the input hash after the manifest was
    # written, so the gate would report the build as stale forever. Remove any that appear there.
    reg = OUT / "data"
    for stray in ("register.json", "gate-report.json", "data.json"):
        f = reg / stray
        if f.exists():
            f.unlink()


def build() -> None:
    clean_generated()

    global REPORT, REPORT_RULE_ROWS
    REPORT = {"rules": [{"id": r[0], "claim": r[1], "findings": "not yet run", "ok": False} for r in gate.RULES], "failures": [], "stats": {}}
    REPORT_RULE_ROWS = [(rid, claim, "—") for rid, claim, _ in gate.RULES]

    render_content_pages()

    previous: list[str] | None = None
    rep: dict = REPORT  # type: ignore[assignment]
    for _ in range(4):
        rep = gate.audit()
        render_audit_pages(rep)
        render_aux_files(rep)
        if previous == rep["failures"]:
            break
        previous = rep["failures"]

    final = gate.audit()
    print(f"built {len(page_plan())} pages · inputs {data_hash()}")
    print(f"gate: {len(final['rules'])} rules · {len(final['failures'])} finding(s)")
    if final["failures"]:
        print("\nGATE FAILURES — docs/ is not publishable")
        for f in final["failures"][:60]:
            print("  ·", f)
        if len(final["failures"]) > 60:
            print(f"  … and {len(final['failures']) - 60} more")
        raise SystemExit(1)
    print("gate clean — the site is publishable")


if __name__ == "__main__":
    REPORT: dict = {}
    REPORT_RULE_ROWS: list = []
    build()
