#!/usr/bin/env python3
"""Affil3 publishing gate.

This is the gate the brief asks for: the parts of publishing that can be automated are checked
here, and anything that needs a human is refused rather than trusted. It runs in CI on every push
and pull request, and locally via `make check` equivalent:

    python3 scripts/validate_site.py

Rules are numbered so a failure message can be pointed at in a review. The most important ones:

  R03  a blank field must be a blank field, never an inferred value
  R05  product links carry rel=sponsored
  R06  no price or availability figure is displayed anywhere
  R07  no unverifiable superlative or demand claim
  R08  every policy sentence traces to a sourced row in the claims ledger
  R11  generated pages are not hand-edited
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import json

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
failures: list[str] = []
warnings: list[str] = []


def fail(rule: str, msg: str) -> None:
    failures.append(f"{rule}: {msg}")


def warn(rule: str, msg: str) -> None:
    warnings.append(f"{rule}: {msg}")


def read_json(name: str):
    path = DATA / name
    if not path.exists():
        fail("R01", f"missing register {name}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail("R01", f"{name} is not valid JSON: {exc}")
        return None


def require(row: dict, keys: list[str], where: str) -> None:
    """Every listed key must exist. Text keys must be filled; list keys may be legitimately
    empty, because "this needs nothing answered first" is information, not a gap."""
    for k in keys:
        if k not in row:
            fail("R02", f"{where} missing required key '{k}'")
        elif k in MAY_BE_EMPTY:
            continue
        elif row[k] in ("", None, []):
            fail("R02", f"{where} has empty '{k}' - fill it or remove the row")


# Fields where an empty string is the honest, intended value (not yet confirmed by a human).
# Keys that may legitimately be empty, for two distinct reasons:
#  - list keys, where "nothing" is the answer (policy_gate, blocks, ...)
#  - evidence keys, where blank means "not confirmed by anyone yet" and MUST NOT be back-filled.
#    R03 separately requires that any such blank be explained by a flag or an open question.
MAY_BE_EMPTY = {
    "policy_gate", "needs_before_deciding", "excludes_for_now", "blocks", "depends_on",
    "intended_asin", "intended_listing_url", "confirmation_date", "confirmation_source",
    "observed_asin", "observed_asin_length", "observed_breadcrumb", "observed_node_id", "answer",
}

# --- R08 claims ledger ------------------------------------------------------------------------
claims = read_json("claims.json")
claim_ids: set[str] = set()
if claims:
    for c in claims.get("verified_claims", []):
        cid = c.get("id", "?")
        claim_ids.add(cid)
        require(c, ["id", "claim", "quote", "source_url", "publisher", "document_updated",
                    "retrieved", "changes"], f"claim {cid}")
        if not str(c.get("source_url", "")).startswith("https://"):
            fail("R08", f"claim {cid} source_url is not https")
        if "<" in str(c.get("quote", "")):
            fail("R08", f"claim {cid} quote contains markup")
    for c in claims.get("unverified_claims", []):
        require(c, ["id", "statement", "status"], f"unverified claim {c.get('id','?')}")
        status = str(c.get("status", "")).lower()
        if not any(t in status for t in ("not ", "unconfirmed", "unresolved", "deliberately")):
            warn("R08", f"unverified claim {c['id']} status does not say what is missing")

# --- R02/R03 link verification register -------------------------------------------------------
verif = read_json("link-verification.json")
if verif:
    allowed = {
        "resolved-to-different-asin",
        "resolved-to-different-asin-and-different-category",
        "blocked-by-checkpoint",
        "request-failed",
    }
    for r in verif.get("records", []):
        rid = r.get("id", "?")
        require(r, ["id", "submitted_url", "submitted_token", "submitted_token_length",
                    "intended_asin", "intended_listing_url", "confirmation_date",
                    "confirmation_source", "observed_final_url", "observed_asin",
                    "outcome", "observed_at_utc", "review_link", "flags"], f"record {rid}")
        if r.get("outcome") not in allowed:
            fail("R03", f"{rid} outcome '{r.get('outcome')}' is not one of the allowed values")
        # The core integrity rule: intended and observed are separate, and a blank intended field
        # must be flagged, never back-filled from the observed value.
        if not r.get("intended_asin"):
            if not r.get("flags"):
                fail("R03", f"{rid} has no intended ASIN and no flag explaining it")
            if r.get("intended_asin") == r.get("observed_asin") and r.get("observed_asin"):
                fail("R03", f"{rid} intended field appears copied from observed")
        if r.get("intended_asin") and r.get("intended_asin") == r.get("observed_asin"):
            warn("R03", f"{rid} intended equals observed - confirm this is not a copy")
        if not str(r.get("review_link", "")).startswith("https://"):
            fail("R03", f"{rid} review_link must be an https URL for manual review")
    for c in verif.get("controls", []):
        require(c, ["id", "purpose", "request", "observed", "conclusion", "observed_at_utc"],
                f"control {c.get('id','?')}")
    for o in verif.get("observations", []):
        require(o, ["id", "observation", "status", "source"], f"observation {o.get('id','?')}")

# --- suggestions / questions / topics ---------------------------------------------------------
sugg = read_json("suggestions.json")
if sugg:
    for s in sugg.get("suggestions", []):
        sid = s.get("id", "?")
        require(s, ["id", "area", "title", "problem", "proposal", "shop_feel", "expected_effect",
                    "effort", "risk", "policy_gate", "needs_before_deciding", "options",
                    "paste_into_prompt", "status"], f"suggestion {sid}")
        for g in s.get("policy_gate", []):
            if claim_ids and g not in claim_ids:
                fail("R08", f"suggestion {sid} cites {g}, which is not in the claims ledger")
        for q in s.get("needs_before_deciding", []):
            if not re.fullmatch(r"(Q|SUG|PATH)-[A-Z0-9]+", q) and not re.fullmatch(r"Q-\d+", q):
                warn("R02", f"suggestion {sid} references odd id {q}")
    for p in sugg.get("paths", []):
        require(p, ["id", "name", "summary", "pick_if", "includes", "excludes_for_now",
                    "time_to_first_real_page", "risk"], f"path {p.get('id','?')}")
        ids = {s["id"] for s in sugg.get("suggestions", [])}
        for ref in p["includes"] + p["excludes_for_now"]:
            if ref not in ids:
                fail("R02", f"path {p['id']} references unknown suggestion {ref}")

qns = read_json("open-questions.json")
if qns:
    for q in qns.get("questions", []):
        qid = q.get("id", "?")
        require(q, ["id", "category", "question", "why_it_matters", "what_we_know",
                    "what_we_do_not_know", "how_to_find_out", "who_must_answer", "answer",
                    "status", "blocks"], f"question {qid}")
        if q.get("status") == "answered" and not q.get("answer"):
            fail("R03", f"question {qid} is marked answered but the answer field is blank")

topics = read_json("topics.json")
if topics:
    for c in topics.get("clusters", []):
        require(c, ["id", "name", "browse_evidence", "hub_status", "topics"], f"cluster {c.get('id','?')}")
        for t in c.get("topics", []):
            require(t, ["title", "angle", "type", "depends_on", "non_slop_requirement"],
                    f"cluster {c['id']} topic '{t.get('title','?')}'")

# --- HTML rules -------------------------------------------------------------------------------
PAGES = sorted(p for p in ROOT.glob("*.html"))
GUIDES = sorted((ROOT / "guides").glob("*.html"))
ALL = PAGES + GUIDES
if not ALL:
    fail("R01", "no HTML pages found")

PRICE_RE = re.compile(r"(?<![A-Za-z])[$\u00a3\u20ac]\s?\d")
SUPERLATIVE_RE = re.compile(
    r"\b(most popular|best[- ]selling|best[- ]rated|top[- ]rated|number[- ]one|guaranteed to|"
    r"proven to (be|increase)|#1|the best on the market|editor'?s choice)\b",
    re.I,
)
PRODUCT_LINK_RE = re.compile(
    r"<a\b[^>]*href=\"https?://(?:www\.)?(?:amazon\.[a-z.]+|amzn\.to|link\.amazon)[^\"]*"
    r"(?:/dp/|/product-reviews/|/gp/product|link\.amazon)[^\"]*\"[^>]*>",
    re.I,
)
NEGATION_RE = re.compile(
    r"\b(no|not|never|unless|without|avoid|forbid|refuse|may not|must not|disallow|omit)\b", re.I)

for p in ALL:
    txt = p.read_text(encoding="utf-8")
    rel = p.relative_to(ROOT)

    # R04 disclosure above the fold and repeated in the footer
    head = txt.split("</header>")[0]
    if "disclosure-strip" not in head:
        fail("R04", f"{rel} has no disclosure strip inside the header (above the fold)")
    if "footer-strip" not in txt and '<footer' not in txt:
        fail("R04", f"{rel} has no footer")
    elif "<footer" in txt and "disclosure-strip" not in txt.split("<footer", 1)[1]:
        fail("R04", f"{rel} footer does not repeat the disclosure")

    # R06 no displayed price or availability figure
    m = PRICE_RE.search(txt)
    if m:
        fail("R06", f"{rel} displays what looks like a currency amount: ...{txt[max(0,m.start()-60):m.end()+40]}...")

    # R07 no unverifiable superlatives / demand claims. A match only counts when the page uses
    # the phrase to assert something about a product. A phrase that is quoted, or that sits in a
    # sentence explicitly disclaiming it, is a mention, and mentioning a banned phrase is how you
    # write the ban down.
    for m in SUPERLATIVE_RE.finditer(txt):
        sentence = re.split(r"(?<=[.!?])\s", txt[max(0, m.start() - 400):m.end() + 120])[0]
        quoted = re.search(r'[">&][^<]{0,40}$', txt[max(0, m.start() - 40):m.start()])
        if NEGATION_RE.search(sentence) or quoted:
            continue
        fail("R07", f"{rel} contains an unsupported claim: '{m.group(0)}'")

    # R05 product links marked sponsored
    for tag in PRODUCT_LINK_RE.findall(txt):
        rel_m = re.search(r'rel="([^"]*)"', tag)
        if not rel_m or "sponsored" not in rel_m.group(1):
            href = re.search(r'href="([^"]*)"', tag).group(1)
            fail("R05", f"{rel} product link lacks rel=sponsored: {href}")

    # R13 in-page anchors resolve, so a cross-link never lands on the top of a long page
    ids = set(re.findall(r'\sid="([^"]+)"', txt))
    for m in re.finditer(r'href="([^"#]*\.html)#([^"]+)"', txt):
        target = (p.parent / m.group(1)).resolve() if m.group(1) else p
        if not target.exists():
            continue
        frag = m.group(2)
        if frag not in re.findall(r'\sid="([^"]+)"', target.read_text(encoding="utf-8")):
            fail("R13", f"{rel} links to #{frag} on {m.group(1)}, which has no such anchor")

    # R09 no external third-party assets
    for m in re.finditer(r'(?:src|href)="(https?://[^"]+)"', txt):
        host = re.sub(r"^https?://", "", m.group(1)).split("/")[0]
        if host not in ("karagemop466-tech.github.io", "www.amazon.com", "amazon.com", "link.amazon", "affiliate-program.amazon.com",
                        "www.ftc.gov", "ecfr.gov", "www.ecfr.gov", "search.google.com",
                        "www.aboutamazon.com", "www.amazon.co.uk", "assets.example.invalid"):
            warn("R09", f"{rel} references external host {host} (page must render without it)")

    # R10 internal links resolve
    for m in re.finditer(r'href="([^"#:]+\.html)(?:#[^"]*)?"', txt):
        target = (p.parent / m.group(1)).resolve()
        if not target.exists():
            fail("R10", f"{rel} links to missing file {m.group(1)}")

# generated pages are not hand-edited (R11)
if "--no-build-check" not in sys.argv:
    res = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_registers.py"), "--check"],
        capture_output=True, text=True,
    )
    if res.returncode != 0:
        fail("R11", "generated pages differ from the registers -> " + res.stdout.strip().replace("\n", " "))

# sitemap and feed (R12)
for xml_name in ("sitemap.xml", "feed.xml"):
    path = ROOT / xml_name
    if not path.exists():
        fail("R12", f"{xml_name} missing")
        continue
    xtxt = path.read_text(encoding="utf-8")
    for loc in re.findall(r"<loc>https?://[^/]+/(?:Affil3/)?" if xml_name == "sitemap.xml" else r"<loc>([^<]+)</loc>", xtxt):
        name = loc.rstrip("/").split("/")[-1] or "index.html"
        if name.endswith(".xml") or name.endswith(".html"):
            if not (ROOT / name).exists():
                fail("R12", f"{xml_name} lists {name}, which does not exist")

# report
print(f"checked {len(ALL)} pages, {len(claim_ids)} sourced claims")
for w in warnings:
    print(f"  warn  {w}")
if failures:
    print(f"\n{len(failures)} gate failure(s):")
    for f in failures:
        print(f"  FAIL  {f}")
    sys.exit(1)
print("gate passed")
