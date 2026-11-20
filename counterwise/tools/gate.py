"""The gate: what must be true before this site is allowed to exist.

Automation handles the parts that can be checked mechanically. This module is the mechanical
part, and it is the reason `python3 tools/build.py` is the only publishing command: a rule that
lives in a style guide decays, a rule that fails a build does not.

    python3 tools/gate.py            # exit 0 = ship, exit 1 = do not
    python3 tools/gate.py --explain  # every rule with the reason it exists
    python3 tools/gate.py --json     # machine-readable report

`verification` on a data row is a promise to the reader. The rules below exist so that promise
cannot be filled in by accident, by optimism, or by a language model filling a blank.
"""

from __future__ import annotations

import argparse
import json
import html as _html
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

from site_common import (
    CONTENT,
    DATA,
    OUT,
    ROOT,
    data_hash,
    dp_id_from_url,
    has_placeholder,
    is_asin,
    load,
    resolve_to_file,
)

LEDGER_COLUMNS = [
    "date",
    "source",
    "channel",
    "eligible_sessions",
    "clicks",
    "reported_orders",
    "reported_commission",
    "product_category_as_reported",
    "retrieved_by",
    "provenance_note",
]

# Each entry: pattern, human reason, and the pages it applies to.
# `scope: product` means reader-facing pages that talk about products (front page, guides, gear,
# clusters). `scope: all` means every page on the site, including this project's own paperwork.
BANNED_PATTERNS = [
    (r"we (?:have )?(?:tested|tried|used|evaluated|hands-on|cooked in)", "all",
     "nobody at this project has cooked in these machines; the day someone does, the claim becomes true and this rule gets a waiver"),
    (r"our (?:top )?pick|editor'?s choice|best overall|best value|best budget|best air fryer", "product",
     "a ranking is a claim about superiority; the brief forbids presenting popularity or superiority as fact"),
    (r"\b(?:4|5)\.\d stars?|\d{1,2},\d{3} (?:ratings?|reviews?)|aggregate rating", "all",
     "ratings drift and were not captured verifiably; see FLG-007"),
    (r"\$\s?\d[\d,]*(?:\.\d\d)?", "product",
     "no prices on product-facing pages (S-04); hosting costs on the board are a different thing and are allowed"),
    (r"\bguarantee[ds]?\b|risk-?free|no-?risk", "all",
     "a promise we cannot underwrite"),
    (r"FDA[- ]approved|cures|prevents (?:cancer|disease)|kills \d+% of", "all",
     "health claims are out of scope for cookware and are the fastest route to a takedown"),
    (r"\bseamless(?:ly)?\b|\bcurate[d]?d?\b|\bcurat\b|\bdelve\b|\bunwind\b|\bunlock\b|\belevate\b|game-?changer|revolutioni[sz]e|top-?notch|look no further|in today['’]s fast[- ]paced|whether you(?:'re| are)|it(?:'s| is) important to note", "all",
     "the vocabulary that makes a page read as generated filler (S-19)"),
    (r"in conclusion|final thought[s]?|at the end of the day|dive in", "all",
     "throat-clearing: the sentence after it usually says nothing"),
    (r"as an amazon associate, i earn", "all",
     "the required statement has exact wording (SG-01); a comma is a paraphrase"),
    (r"verified by (?:our|a panel of) experts|our experts (?:at|recommend)", "all",
     "no expert relationship exists to invoke (FLG-014)"),
]

PRODUCT_SCOPED_KINDS = {"front", "guide", "gear", "cluster", "compare"}

# Tasks live in COORDINATION.md, which is not data; questions may block them by name.
TASK_LABELS = [f"any {w}" for w in ("scaling", "revenue")]


REQUIRED_HEAD_KEYS = ("charset", "viewport", "title", "description", "canonical")


def walk_strings(obj, path="$"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


def _pages() -> dict[str, Path]:
    return {str(p.relative_to(OUT)).replace("\\", "/"): p for p in OUT.rglob("*.html")}


class AnchorScan(HTMLParser):
    """Collect anchors and their attributes from finished HTML, plus img alt coverage."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.anchors: list[dict] = []
        self.images: list[dict] = []
        self.head_scripts: list[str] = []
        self._in_script = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a":
            a["_text"] = ""
            self.anchors.append(a)
        elif tag == "img":
            self.images.append(a)
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._in_script = ""

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, dict(attrs))

    def handle_data(self, data):
        if self.anchors and self.anchors[-1].get("_text") is not None:
            self.anchors[-1]["_text"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.anchors:
            self.anchors[-1]["_text"] = self.anchors[-1]["_text"].strip()[:90]


# --------------------------------------------------------------------- rules
# A rule returns a list of finding strings. Empty list = the rule passed.


def rule_sources_register() -> list[str]:
    out = []
    reg = load("sources.json")
    seen = set()
    allowed = {"read", "snippet", "link-verified", "not-read", "queued"}
    for s in reg["sources"]:
        if not s.get("id") or not s["id"].startswith("SG-"):
            out.append(f"source row without an SG- id: {s.get('title','?')}")
        if s["id"] in seen:
            out.append(f"duplicate source id {s['id']}")
        seen.add(s["id"])
        url = s.get("url", "")
        if not url.startswith("https://"):
            out.append(f"{s['id']}: url is not https ({url!r})")
        if s.get("verification") not in allowed:
            out.append(f"{s['id']}: verification {s.get('verification')!r} is not one of {sorted(allowed)}")
        if s.get("verification") in ("read", "snippet") and not s.get("method"):
            out.append(f"{s['id']}: claims to have been {s['verification']} but records no method")
        if not s.get("accessed"):
            out.append(f"{s['id']}: no retrieval date")
        if not s.get("what_it_supports"):
            out.append(f"{s['id']}: registered but supporting nothing")
    return out


def rule_products() -> list[str]:
    out = []
    for p in load("products.json")["products"]:
        pid = p.get("id", "?")
        intent, obs = p["intent"], p["observation"]
        # 1. An intent record is only valid with the provenance that makes it a confirmation.
        if intent.get("intended_asin") and not (
            intent.get("confirmation_date") and intent.get("confirmed_via") and intent.get("confirmed_by")
        ):
            out.append(f"{pid}: intended_asin filled without confirmation_date/confirmed_via/confirmed_by")
        if intent.get("intended_asin") and not is_asin(intent["intended_asin"]):
            out.append(f"{pid}: intended_asin {intent['intended_asin']!r} is not a 10-character identifier")
        # 2. Blanks must be blank, not "unknown", and never invented.
        for k in ("official_listing_url", "confirmation_date", "confirmed_via", "confirmed_by"):
            v = intent.get(k, "")
            if v and intent.get("status") != "confirmed":
                out.append(f"{pid}: intent.{k} is filled while status is {intent['status']!r}")
        # 3. "as titled" claims must literally be in the captured title.
        title = (obs.get("page_title_observed") or "").lower()
        for feat in p.get("titled_features", []) + [p.get("titled_brand", ""), p.get("titled_capacity", "")]:
            if not feat:
                continue
            probe = feat.split(";")[0].split(" · ")[0].strip().lower()
            probe = re.sub(r"[^a-z0-9 ]", "", probe)[:22].strip()
            if probe and probe not in re.sub(r"[^a-z0-9 ]", "", title):
                out.append(f"{pid}: {feat!r} is not text from the captured listing title")
        # 4. An observation without a date is an anecdote.
        if obs.get("verification") in ("observed", "confirmed") and not obs.get("observed_on"):
            out.append(f"{pid}: observed data with no capture date")
        if obs.get("verification") == "observed" and not obs.get("listing_asin_observed_in_path"):
            out.append(f"{pid}: marked observed but has no listing identifier")
        allowed_states = {"pending-test", "in-account-confirmed", "no-link-published", "citation"}
        state = obs.get("link_state", "pending-test")
        if state not in allowed_states:
            out.append(f"{pid}: link_state {state!r} is not one of {sorted(allowed_states)}")
        if state == "in-account-confirmed" and not obs.get("link_state_verified_on"):
            out.append(
                f"{pid}: link_state claims a confirmed click but records no verification date — "
                "write link_state_verified_on when the report is read (RUNBOOK R2)"
            )
        if obs.get("verification") == "unresolved" and (obs.get("listing_asin_observed_in_path") or obs.get("listing_url_observed")):
            out.append(f"{pid}: unresolved observation carries a product identifier — that is an inference")
        for k, v in walk_strings(p):
            bad = has_placeholder(v)
            if bad:
                out.append(f"{pid}{k}: placeholder text {bad!r} — leave the field blank and flag it instead")
    return out


def rule_links() -> list[str]:
    out = []
    links = load("links.json")["links"]
    for l in links:
        lid = l.get("id", "?")
        if l["supplied_token_length"] != len(l["supplied_token"]):
            out.append(f"{lid}: recorded token length does not match the token itself")
        if l["supplied_url"] != f"https://{l['supplied_host']}/{l['supplied_token']}":
            out.append(f"{lid}: supplied_url does not match host+token as given")
        resolved = l["resolution_status"].startswith("resolved")
        if resolved:
            path_id = dp_id_from_url(l["observed_final_url"])
            if not path_id:
                out.append(f"{lid}: marked resolved but the final URL has no /dp/ identifier")
            elif path_id != l["observed_path_id"]:
                out.append(f"{lid}: observed_path_id {l['observed_path_id']!r} != identifier in the observed URL {path_id!r}")
            if len(path_id) != l["observed_path_id_length"]:
                out.append(f"{lid}: observed_path_id_length is wrong")
            if not l.get("observed_page_title") or not l.get("observed_breadcrumb"):
                out.append(f"{lid}: resolved without a title or breadcrumb to prove it")
            if not l.get("observed_on"):
                out.append(f"{lid}: no capture date")
            tag_present = bool(re.search(r"[?&]tag=", l["observed_final_url"]))
            if tag_present != bool(l["observed_tag_param_present"]):
                out.append(f"{lid}: observed_tag_param_present contradicts the recorded URL")
        else:
            if l.get("observed_path_id") or l.get("observed_page_title", "").startswith("Amazon.com: "):
                out.append(f"{lid}: unresolved row contains product data")
        if not l.get("flags"):
            out.append(f"{lid}: no flag references, so nothing tells a reviewer what is open")
    ids = [l["id"] for l in links]
    if len(ids) != len(set(ids)):
        out.append("duplicate link ids")
    return out


def rule_register_crossrefs() -> list[str]:
    out = []
    sg = {s["id"] for s in load("sources.json")["sources"]}
    fg = {f["id"] for f in load("flags.json")["flags"]}
    pr = {p["id"] for p in load("products.json")["products"]}
    ln = {l["id"] for l in load("links.json")["links"]}
    gd = {g["id"] for g in load("guides.json")["guides"]}
    cl = {c["id"] for c in load("clusters.json")["clusters"]}
    ev = {e["id"] for e in load("events.json")["events"]}

    for p in load("products.json")["products"]:
        for f in p["observation"].get("flags", []):
            if f not in fg:
                out.append(f"{p['id']}: references unknown flag {f}")
        if p["observation"].get("source_link") and p["observation"]["source_link"] not in ln:
            out.append(f"{p['id']}: source_link {p['observation']['source_link']} is not in links.json")
    for l in load("links.json")["links"]:
        for f in l.get("flags", []):
            if f not in fg:
                out.append(f"{l['id']}: references unknown flag {f}")
        if l.get("product_id") and l["product_id"] not in pr:
            out.append(f"{l['id']}: product_id {l['product_id']} does not exist")
    for g in load("guides.json")["guides"]:
        for s in g.get("sources", []):
            if s not in sg:
                out.append(f"{g['id']}: cites unknown source {s}")
        for p in g.get("products", []):
            if p not in pr:
                out.append(f"{g['id']}: references unknown product {p}")
        for c in g.get("clusters", []):
            if c not in cl:
                out.append(f"{g['id']}: references unknown cluster {c}")
        if not g.get("checklist"):
            out.append(f"{g['id']}: guide has no checklist, so it asks the reader for nothing")
        if len(g.get("sources", [])) < 1:
            out.append(f"{g['id']}: guide cites no source at all")
    for c in load("clusters.json")["clusters"]:
        for p in c.get("products", []):
            if p not in pr:
                out.append(f"cluster {c['id']}: unknown product {p}")
        for g in c.get("guides", []):
            if g not in gd:
                out.append(f"cluster {c['id']}: unknown guide {g}")
    for q in load("questions.json")["questions"]:
        for b in q.get("blocks", []):
            known = fg | {x["id"] for x in load("suggestions.json")["board"]} | set(TASK_LABELS)
            if re.match(r"^(S-\d+a?|FLG-\d+)$", b) and b not in known:
                out.append(f"{q['id']}: blocks {b}, which is not a row in the register")
            if b.startswith(("S-", "FLG-", "Q-")) and b not in known and not b.startswith("Q-"):
                out.append(f"{q['id']}: unresolvable reference {b}")
    names = {e["name"] for e in load("events.json")["events"]}
    for e in load("events.json")["events"]:
        if not e.get("decision_it_serves"):
            out.append(f"{e['id']}: an event with no decision it serves is a vanity metric")
        if not e.get("properties"):
            out.append(f"{e['id']}: no payload schema")
    if len(ev) != 5:
        out.append(f"events.json defines {len(ev)} events; the brief asks for exactly five")
    if len(names) != len(ev):
        out.append("event names are not unique")
    for t, v in walk_strings({"questions": load("questions.json"), "suggestions": load("suggestions.json")}):
        bad = has_placeholder(v)
        if bad and "XXXXX" not in v:
            out.append(f"placeholder {bad!r} in {t}{v[:40]!r}")
    return out


def rule_counts_consistent() -> list[str]:
    """Hardcoded tallies in the data files must match what the data actually says."""
    out = []
    sg = load("suggestions.json")
    board = sg["board"]
    want = {"shipped": 0, "needs-pick": 0, "proposed": 0, "open_review_decisions": 0}
    for s in board:
        st = s["status"]
        key = "shipped" if st.startswith("shipped") else ("needs-pick" if st == "needs-pick" else "proposed")
        want[key] += 1
        if not s.get("review_decision"):
            want["open_review_decisions"] += 1
    if sg.get("summary_counts") != want:
        out.append(f"suggestions.json summary_counts {sg.get('summary_counts')} != computed {want}")
    qs = load("questions.json")
    qq = qs["questions"]
    if qs.get("counts", {}).get("total") != len(qq):
        out.append(f"questions.json counts.total {qs.get('counts',{}).get('total')} != {len(qq)} rows")
    # Attribution of each question to a person is an editorial judgement; the total is
    # arithmetic, and arithmetic is what a gate can police.
    return out


def rule_no_hand_edited_output() -> list[str]:
    m = OUT / "manifest.json"
    if not m.exists():
        return ["docs/manifest.json is missing: docs/ was not produced by tools/build.py"]
    man = json.loads(m.read_text(encoding="utf-8"))
    if man.get("inputs_hash") != data_hash():
        return [
            "docs/ is stale: it was built from a different data/ + content/ state "
            f"(manifest {man.get('inputs_hash')}, current {data_hash()}). Run python3 tools/build.py."
        ]
    return []


def rule_pages() -> list[str]:
    out = []
    cfg = load("config.json")
    prefix = re.sub(r"^https?://[^/]+", "", cfg["identity"]["base_url"].rstrip("/"))
    market_host = cfg["amazon"]["marketplace_host"]
    global PREFIX
    PREFIX = prefix
    statement = cfg["disclosure"]["statement"]
    tracking = cfg["amazon"]["tracking_id"]
    pages = _pages()
    if not pages:
        return ["docs/ contains no HTML at all"]

    for rel, path in sorted(pages.items()):
        src = path.read_text(encoding="utf-8")
        kind = next((k for k, v in {
            "front": rel == "index.html",
            "guide": rel.startswith("guides/") and rel != "guides/index.html",
            "gear": rel.startswith("gear/"),
            "cluster": rel.startswith("clusters/"),
            "compare": rel.startswith("compare/"),
        }.items() if v), "paperwork")
        low = src.lower()

        # head furniture
        for key in REQUIRED_HEAD_KEYS:
            if key in ("charset",) and 'charset="utf-8"' not in low:
                out.append(f"{rel}: no charset")
            if key == "viewport" and "name=\"viewport\"" not in low:
                out.append(f"{rel}: no viewport meta")
            if key == "title":
                tm = re.search(r"<title>(.*?)</title>", src, re.S)
                n = len(tm.group(1).strip()) if tm else 0
                if not tm or not 15 <= n <= 70:
                    out.append(
                        f"{rel}: <title> must be 15-70 characters (found {n}: "
                        f"{tm.group(1).strip()[:70] if tm else 'none'!r})"
                    )
            if key == "description":
                dm = re.search(r'<meta name="description" content="([^"]*)"', src)
                if not dm:
                    out.append(f"{rel}: no meta description")
                elif not 60 <= len(dm.group(1)) <= 168:
                    out.append(f"{rel}: meta description is {len(dm.group(1))} chars; keep 60-168 so it is not truncated in a SERP")
            if key == "canonical":
                m = re.search(r'<link rel="canonical" href="([^"]+)"', src)
                if not m:
                    out.append(f"{rel}: no canonical URL")
                elif not m.group(1).startswith(cfg["identity"]["base_url"]):
                    out.append(f"{rel}: canonical {m.group(1)} is not under the configured base URL")
        if 'lang="' not in low:
            out.append(f"{rel}: <html> has no lang attribute")
        if low.count("<h1") == 0:
            out.append(f"{rel}: no <h1>")
        if low.count("<h1") > 1:
            out.append(f"{rel}: {low.count('<h1')} <h1> elements; one page, one headline")
        if "skip" not in low:
            out.append(f"{rel}: no skip link")

        # disclosure: the statement must be inside the above-the-fold strip and inside the footer,
        # not merely present somewhere twice. Placement is the requirement, so placement is checked.
        strip_m = re.search(r'<div class="disclosure">.*?</div>\s*</div>', src, re.S)
        foot_m = re.search(r'<footer class="foot".*?</footer>', src, re.S)
        if not strip_m or statement.lower() not in strip_m.group(0).lower():
            out.append(f"{rel}: the required statement is not inside the above-the-fold disclosure strip")
        if not foot_m or statement.lower() not in foot_m.group(0).lower():
            out.append(f"{rel}: the required statement is not repeated inside the footer")
        if low.count(statement.lower()) < 2:
            out.append(f"{rel}: the required statement appears {low.count(statement.lower())} time(s); it must be above the fold and repeated in the footer")
        if 'class="disclosure"' not in low:
            out.append(f"{rel}: no disclosure strip under the masthead")
        if 'data-disclosure="footer"' not in low:
            out.append(f"{rel}: no footer disclosure block")

        # links
        scan = AnchorScan()
        scan.feed(src)
        def host_of(h: str) -> str:
            m = re.match(r"^https?://([^/]+)", h)
            return m.group(1).lower() if m else ""

        for a in scan.anchors:
            href = a.get("href", "")
            host = host_of(href)
            if re.search(r"amzn\.to|link\.amazon", href):
                out.append(
                    f"{rel}: publishes a short-link form as a link ({href[:60]}). While FLG-003 is open "
                    "the supplied codes are cited as text in the evidence tables, not used as links."
                )
            if host == market_host:
                if f"tag={tracking}" not in href:
                    out.append(f"{rel}: link to the marketplace host without the tracking tag: {href[:78]}")
                rel_attr = (a.get("rel") or "").lower()
                for want in ("sponsored", "nofollow", "noopener"):
                    if want not in rel_attr:
                        out.append(f"{rel}: marketplace link lacks rel={want} ({href[:56]})")
                if not a.get("data-outbound"):
                    out.append(f"{rel}: marketplace link is not marked data-outbound, so a click on it cannot be counted")
                if not a.get("data-product"):
                    out.append(f"{rel}: marketplace link has no data-product value, so a click cannot be attributed")
                if a.get("target") != "_blank":
                    out.append(f"{rel}: marketplace link should open in a new tab and say so to the reader")
            elif host.startswith("http") or ("." in host if host else False):
                if a.get("target") == "_blank" and "noopener" not in (a.get("rel") or ""):
                    out.append(f"{rel}: external link opens a new tab without noopener")
            if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
                continue
            if href.startswith("/") or (href and not re.match(r"^(https?|data):", href)):
                f = resolve_to_file(href, prefix)
                if f is None:
                    continue
                if not f.exists():
                    out.append(f"{rel}: broken internal link {href}")
                    continue
                frag = href.split("#")[1] if "#" in href else ""
                if frag and f.suffix == ".html" and f'id="{frag}"' not in f.read_text(encoding="utf-8"):
                    out.append(f"{rel}: anchor #{frag} does not exist in {href}")

        # every external citation must be registered
        registered = set()
        for s in load("sources.json")["sources"]:
            registered.add(s["url"])
        for l in load("links.json")["links"]:
            registered.add(l["observed_final_url"])
            registered.add(re.sub(r"\?.*$", "", l["observed_final_url"]))
        for p in load("products.json")["products"]:
            u = p["observation"].get("listing_url_observed")
            if u:
                registered.add(u)
        registered.add(cfg["repository"]["clone"])
        registered.add(cfg["repository"]["pages_url"])
        registered.add(cfg["identity"]["base_url"])
        # URLs the register itself cites as evidence are allowed to appear as citations
        for f in load("flags.json")["flags"]:
            for e in f.get("evidence", []):
                if isinstance(e, str) and e.startswith("http"):
                    registered.add(re.sub(r"[#?].*$", "", e))
        for m in load("flags.json").get("brief_id_mapping", []):
            pass
        for a in scan.anchors:
            href = a.get("href", "")
            if host_of(href) == market_host:
                continue  # listing links are checked above: tagged, marked, sponsored
            if not re.match(r"^https?://", href):
                continue
            base = re.sub(r"[#?].*$", "", href)
            if not any(base == r or base.startswith(r) or r.startswith(base) for r in registered):
                out.append(f"{rel}: citation to an unregistered URL: {base}")

        # images carry alt text, exist on disk, and are captioned as what they are
        base_path = cfg["identity"]["base_url"].rstrip("/")
        for img in scan.images:
            if img.get("alt") in (None, ""):
                out.append(f"{rel}: <img> without alt text")
            src_attr = img.get("src", "")
            if src_attr.startswith(("//", "data:")):
                continue
            asset = src_attr
            if asset.startswith(base_path):
                asset = asset[len(base_path) :]
            if asset.startswith(PREFIX):
                asset = asset[len(PREFIX) :]
            target = (OUT / asset.lstrip("/")).resolve()
            if not target.exists():
                out.append(f"{rel}: <img src={src_attr}> has no file behind it")
        for m in re.finditer(r'(?:href|src)="(/[^"]+\.(?:css|js|png|jpg|jpeg|svg|xml))"', src):
            ref = m.group(1)
            if ref.startswith(PREFIX):
                ref = ref[len(PREFIX) :]
            if not (OUT / ref.lstrip("/")).exists():
                out.append(f"{rel}: referenced asset {m.group(1)} is missing from docs/")
        if "<img" in low and "illustration" not in low and rel.startswith(("guides/", "gear/", "clusters/", "index")):
            out.append(f"{rel}: uses artwork without stating that it is illustration, not a product photo (S-05)")

        # voice: a phrase cited inside quotes or <code> in order to ban it is not the site
        # using it. Marked so a reviewer can see the rule and the exception in one file.
        stripped = re.sub(r"<code>.*?</code>", " ", src, flags=re.S)
        stripped = re.sub(r"<[^>]+>", " ", stripped)
        text_only = _html.unescape(stripped)
        for pat, scope, _why in BANNED_PATTERNS:
            if scope == "product" and kind not in PRODUCT_SCOPED_KINDS:
                continue
            for m in re.finditer(pat, text_only, re.I):
                before = text_only[: m.start()].rstrip()
                quoted = before.endswith(('"', "'", "“", "‘", "(", "["))
                if quoted:
                    continue
                out.append(
                    f"{rel}: uses the banned phrase {m.group(0)!r} outside a quotation "
                    "(cite it in quotes if you mean to discuss the rule; see tools/gate.py for the why)"
                )
                break

        # capture freshness on anything that quotes a listing
        if kind in ("gear", "guide", "compare", "cluster") and "captured" not in low:
            out.append(f"{rel}: quotes listings but never says when they were captured (S-18)")
        if kind == "guide" and "what this page does not tell you" not in low:
            out.append(f"{rel}: guide lacks the 'what this page does not tell you' section")
    return out


def rule_jsonld() -> list[str]:
    out = []
    cfg = load("config.json")
    allow = cfg["amazon"].get("pa_api_access") == "confirmed"
    for rel, path in sorted(_pages().items()):
        if rel == "404.html":
            continue
        src = path.read_text(encoding="utf-8")
        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', src, re.S
        )
        if not blocks and rel == "index.html":
            out.append("index.html: no structured data of any kind")
        for raw in blocks:
            try:
                doc = json.loads(raw)
            except json.JSONDecodeError as e:
                out.append(f"{rel}: JSON-LD does not parse ({e})")
                continue
            for node in doc if isinstance(doc, list) else [doc]:
                t = node.get("@type", "")
                if t in ("Product", "Review", "AggregateRating") and not allow:
                    out.append(
                        f"{rel}: {t} markup without a confirmed authorized data feed — see S-07/FLG-011"
                    )
                if t == "Article":
                    for k in ("headline", "datePublished", "dateModified", "author"):
                        if k not in node:
                            out.append(f"{rel}: Article markup missing {k}")
                    if "Person" == str(node.get("author", {}).get("@type")):
                        out.append(f"{rel}: Person author without a named human (FLG-014)")
    return out


def rule_sitemap_feed() -> list[str]:
    out = []
    cfg = load("config.json")
    base = cfg["identity"]["base_url"].rstrip("/")
    sm = OUT / "sitemap.xml"
    fd = OUT / "feed.xml"
    rb = OUT / "robots.txt"
    if not sm.exists():
        return ["docs/sitemap.xml missing"]
    root = ET.fromstring(sm.read_text(encoding="utf-8"))
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    locs = [c.findtext(ns + "loc") for c in root.findall(ns + "url")]
    if not locs:
        out.append("sitemap.xml lists nothing")
    for loc in locs:
        if not loc or not loc.startswith(base):
            out.append(f"sitemap: {loc} is not under {base}")
            continue
        rel = loc[len(base) :].lstrip("/") or "index.html"
        f = resolve_to_file(loc, base.split(".github.io")[-1])
        if f is None or not f.exists():
            out.append(f"sitemap: {loc} has no file behind it")
    indexable = {r for r in _pages() if r != "404.html"}
    mapped = {re.sub(r"^https?://[^/]+", "", l).lstrip("/") or "index.html" for l in locs if l}
    prefix = re.sub(r"^https?://[^/]+", "", base)
    norm = set()
    for m in mapped:
        if prefix and m.startswith(prefix.lstrip("/")):
            m = m[len(prefix.lstrip("/")) :].lstrip("/")
        m = m.strip("/")
        norm.add(m + "/index.html" if m and not m.endswith(".html") else ("index.html" if not m else m))
    missing = indexable - norm
    extra = norm - indexable
    if missing:
        out.append(f"sitemap: pages not listed: {sorted(missing)[:5]}")
    if extra:
        out.append(f"sitemap: entries with no page: {sorted(extra)[:5]}")

    if not fd.exists():
        out.append("docs/feed.xml missing (the brief's reader pass expects a working feed)")
    else:
        froot = ET.fromstring(fd.read_text(encoding="utf-8"))
        fns = "{http://www.w3.org/2005/Atom}"
        entries = froot.findall(fns + "entry")
        if not entries:
            out.append("feed.xml has no entries")
        for e in entries:
            link = e.find(fns + "link")
            href = link.get("href") if link is not None else None
            if not href or not href.startswith(base):
                out.append(f"feed: entry link {href!r} is not absolute under the base URL")
            if not e.findtext(fns + "updated"):
                out.append("feed: entry without <updated>, which the format requires")
            if not e.findtext(fns + "id"):
                out.append("feed: entry without <id>")
        title = froot.findtext(fns + "title") or ""
        if title != cfg["identity"]["name"]:
            out.append(f"feed: title {title!r} does not match the site identity")

    if not rb.exists():
        out.append("robots.txt missing")
    else:
        txt = rb.read_text(encoding="utf-8")
        if "Sitemap:" not in txt:
            out.append("robots.txt does not advertise the sitemap")
        if "noindex" in txt.lower() or "Disallow: /" in txt:
            out.append("robots.txt blocks the site from indexing")
    return out


def rule_measurement() -> list[str]:
    out = []
    cfg = load("config.json")
    events = [e["name"] for e in load("events.json")["events"]]
    track = OUT / "assets" / "track.js"
    if not track.exists():
        return ["docs/assets/track.js missing: clicks cannot be counted"]
    js = track.read_text(encoding="utf-8")
    for name in events:
        if name not in js and name not in json.dumps(load("events.json")):
            out.append(f"event {name} is defined but not emitted")
    if "doNotTrack" not in js or "globalPrivacyControl" not in js:
        out.append("track.js ignores do-not-track or Global Privacy Control while privacy promises opt-out")
    ep = cfg["measurement"]["endpoint"]
    for rel, path in sorted(_pages().items()):
        src = path.read_text(encoding="utf-8")
        m = re.search(r'data-analytics-endpoint="([^"]*)"', src)
        got = m.group(1) if m else None
        if got is None:
            out.append(f"{rel}: no data-analytics-endpoint attribute, so the collector state is invisible in the markup")
        elif got != ep:
            out.append(f"{rel}: endpoint attribute ({got!r}) disagrees with config ({ep!r})")
    if ep and cfg["measurement"]["status"] not in ("deployed", "self-hosted"):
        out.append("an endpoint is configured but measurement.status does not say it is live")
    if not ep and cfg["measurement"]["status"] == "deployed":
        out.append("measurement.status claims deployment with no endpoint — the site would be lying")
    return out


def rule_ledger() -> list[str]:
    out = []
    path = DATA / "ledger" / "campaign_ledger.csv"
    if not path.exists():
        return ["data/ledger/campaign_ledger.csv missing: the campaign ledger is a deliverable"]
    rows = [r for r in path.read_text(encoding="utf-8").strip().split("\n") if r.strip()]
    header = rows[0].split(",")
    if header != LEDGER_COLUMNS:
        out.append(f"ledger header {header} != agreed schema {LEDGER_COLUMNS}")
    for i, line in enumerate(rows[1:], start=2):
        cells = line.split(",")
        rec = dict(zip(header, cells))
        if not rec.get("source"):
            out.append(f"ledger row {i}: numbers without a report they came from")
        if rec.get("reported_orders") and not rec.get("provenance_note"):
            out.append(f"ledger row {i}: orders reported with no provenance note")
        if rec.get("retrieved_by") == "agent-unattended" and (rec.get("reported_orders") or rec.get("reported_commission")):
            out.append(f"ledger row {i}: an unattended agent wrote Amazon-side numbers; that is the part with the gate on it")
    return out


def rule_forecast_absent() -> list[str]:
    out = []
    for rel, path in sorted(_pages().items()):
        low = path.read_text(encoding="utf-8").lower()
        for pat in (
            r"expected (?:to )?(?:earn|revenue|conversion)",
            r"conversion rate of \d",
            r"projected (?:income|revenue)",
            r"\b roi of\b",
            r"\d+(?:\.\d+)?% conversion",
            r"estimated (?:monthly )?(?:earnings|income)",
        ):
            m = re.search(pat, low)
            if m:
                out.append(f"{rel}: publishes a conversion or revenue figure ({m.group(0)!r}); the brief rules it out")
    return out


RULES = [
    ("R01", "source register is complete and honest about how much was read", rule_sources_register),
    ("R02", "product-intent records keep confirmation and observation apart, and never fill a blank with an inference", rule_products),
    ("R03", "link register states exactly what was followed, including the absence of a tag", rule_links),
    ("R04", "every cross-reference resolves: flags, sources, products, clusters, events", rule_register_crossrefs),
    ("R05", "recorded tallies match the data they describe", rule_counts_consistent),
    ("R06", "docs/ was generated from the current data/ and content/", rule_no_hand_edited_output),
    ("R07", "every page: head furniture, disclosure above the fold and in the footer, tagged and marked outbound links, registered citations, no banned voice, no broken links", rule_pages),
    ("R08", "structured data parses and never claims more than the site can support", rule_jsonld),
    ("R09", "sitemap, feed and robots are consistent with the files on disk", rule_sitemap_feed),
    ("R10", "measurement state in the markup agrees with config; opt-out is honoured", rule_measurement),
    ("R11", "the campaign ledger has its schema and no unprovenanced numbers", rule_ledger),
    ("R12", "no conversion score or revenue forecast appears anywhere", rule_forecast_absent),
]


def audit() -> dict:
    report = {"rules": [], "failures": [], "generated_from": data_hash()}
    for rid, why, fn in RULES:
        try:
            findings = fn()
        except Exception as exc:  # a crashing rule is a failed rule, never a passed one
            findings = [f"rule raised {type(exc).__name__}: {exc}"]
        report["rules"].append({"id": rid, "claim": why, "findings": len(findings), "ok": not findings})
        report["failures"].extend(f"[{rid}] {f}" for f in findings)
    pages = _pages()
    report["stats"] = {
        "pages": len(pages),
        "html_bytes": sum(p.stat().st_size for p in pages.values()),
        "data_files": len([p for p in DATA.rglob("*") if p.is_file()]),
        "guides": len(load("guides.json")["guides"]),
        "products": len(load("products.json")["products"]),
        "sources": len(load("sources.json")["sources"]),
        "flags": len(load("flags.json")["flags"]),
        "suggestions": len(load("suggestions.json")["board"]),
        "questions": len(load("questions.json")["questions"]),
    }
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--explain", action="store_true", help="print the rules and why they exist")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    args = ap.parse_args(argv)

    if args.explain:
        for rid, why, _ in RULES:
            print(f"{rid}  {why}")
        print("\nBanned voice patterns, and why:")
        for pat, scope, why in BANNED_PATTERNS:
            print(f"  [{scope}] /{pat}/ — {why}")
        return 0

    rep = audit()
    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        for r in rep["rules"]:
            print(f"{'ok  ' if r['ok'] else 'FAIL'} {r['id']} {r['claim']}" + (f" — {r['findings']} finding(s)" if r["findings"] else ""))
        print()
        for f in rep["failures"][:60]:
            print("  ·", f)
        if len(rep["failures"]) > 60:
            print(f"  … and {len(rep['failures']) - 60} more")
        s = rep["stats"]
        print(
            f"\n{s['pages']} pages · {s['guides']} guides · {s['products']} product rows · "
            f"{s['sources']} sources · {s['flags']} flags · {s['suggestions']} suggestions · {s['questions']} questions"
        )
        print("PASS — the site may ship" if not rep["failures"] else f"FAIL — {len(rep['failures'])} problem(s); docs/ is not publishable")
    return 1 if rep["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
