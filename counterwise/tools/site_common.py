"""Shared helpers for the Counterwise build: data loading, a small markdown renderer, and
path handling that keeps every internal link correct whether the site is served from a domain
root or from a GitHub Pages project path.

Standard library only, on purpose: the gate has to run in CI, in a sandbox and on a laptop with
nothing installed. See data/README.md for the rules this code enforces.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

# Everything is derived from one root so the tests can point the whole toolchain at a copy of the
# surface without monkey-patching five module globals.
SITE_ROOT = Path(__file__).resolve().parent.parent
ROOT = SITE_ROOT
DATA = SITE_ROOT / "data"
CONTENT = SITE_ROOT / "content"
ASSETS_SRC = SITE_ROOT / "assets-src"
OUT = SITE_ROOT  # generated pages are written beside data/ and tools/, published at /Affil3/counterwise/


def set_root(root: str | Path) -> None:
    """Repoint DATA / CONTENT / ASSETS_SRC / OUT. Used by the tests to audit a throwaway copy."""
    global SITE_ROOT, ROOT, DATA, CONTENT, ASSETS_SRC, OUT
    SITE_ROOT = Path(root).resolve()
    ROOT = SITE_ROOT
    DATA = SITE_ROOT / "data"
    CONTENT = SITE_ROOT / "content"
    ASSETS_SRC = SITE_ROOT / "assets-src"
    OUT = SITE_ROOT


# --------------------------------------------------------------------------- data


def load(name: str) -> dict:
    """Read a JSON file from data/, with the `$comment`/`$schema` keys kept for humans."""
    path = DATA / name
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def config() -> dict:
    return load("config.json")


def base_prefix(cfg: dict) -> str:
    """/Affil3 for a project page, "" for a domain root. Derived, never hardcoded."""
    url = cfg["identity"]["base_url"].rstrip("/")
    rest = re.sub(r"^https?://[^/]+", "", url)
    return rest.rstrip("/")


def data_hash() -> str:
    """Hash of everything the site is generated from, so the gate can prove docs/ is current."""
    h = hashlib.sha256()
    # assets-src is hashed as well: the stylesheet and the beacon change what a page claims, so a
    # change there must mark the output stale exactly like a data edit does.
    for folder in (DATA, CONTENT, ASSETS_SRC):
        folder = Path(folder)
        if not folder.exists():
            continue
        for p in sorted(folder.rglob("*")):
            if not p.is_file():
                continue
            # keyed relative to the surface root, so a copied tree hashes identically to the real one
            h.update(p.relative_to(SITE_ROOT).as_posix().encode())
            h.update(b"\0")
            h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()[:16]


# --------------------------------------------------------------------- identifiers


ASIN_RE = re.compile(r"^[A-Z0-9]{10}$")
TRACKING_RE = re.compile(r"^[A-Za-z0-9]{5,}-(20|021|022|023|024|025|026|027|028|029)$")


def is_asin(value: str) -> bool:
    return bool(value) and bool(ASIN_RE.match(value))


def tracking_id_shape_ok(value: str) -> bool:
    return bool(value) and bool(TRACKING_RE.match(value))


def dp_id_from_url(url: str) -> str:
    m = re.search(r"/(?:dp|gp/product)/([A-Za-z0-9]{6,13})", url or "")
    return m.group(1) if m else ""


# ----------------------------------------------------------------- placeholders


PLACEHOLDERS = (
    "tbd",
    "todo",
    "fixme",
    "n/a",
    "lorem ipsum",
    "[insert",
    "[placeholder",
    "coming soon",
    "<insert",
    "asdf",
    "foobar",
    "example.com",
)


def has_placeholder(text) -> str:
    """Return the offending placeholder token, or "" if the text is clean."""
    if not isinstance(text, str):
        return ""
    low = text.lower()
    for token in PLACEHOLDERS:
        if token in low:
            return token
    return ""


# ------------------------------------------------------------- link normalisation


def norm_internal_href(href: str, prefix: str) -> str:
    """Rewrite a site-absolute path from source content into a deploy-correct URL.

    `/gear/index.html`   -> `/Affil3/gear/`
    `/guides/x.html`     -> `/Affil3/guides/x.html`
    `/`                  -> `/Affil3/`
    """
    if not href.startswith("/"):
        return href
    path = href
    if path.endswith("/index.html"):
        path = path[: -len("index.html")]
    if path == "/":
        return prefix + "/"
    return prefix + path


def resolve_to_file(href: str, prefix: str) -> Path | None:
    """Map an internal href to the file that must exist in docs/ for the link to be valid."""
    if href.startswith("#") or href.startswith("mailto:"):
        return None
    path = re.sub(r"^https?://[^/]+", "", href)
    if prefix and path.startswith(prefix):
        path = path[len(prefix) :]
    path = path.split("#")[0].split("?")[0]
    if path == "":
        path = "/"
    if path.startswith("/"):
        rel = path.lstrip("/")
    else:
        rel = path
    rel = rel.lstrip("/")
    if rel == "" or rel.endswith("/"):
        rel += "index.html"
    elif not Path(rel).suffix:
        rel += "/index.html"
    return (OUT / rel).resolve()


# --------------------------------------------------------------- html escaping


def esc(text) -> str:
    return html.escape(str(text), quote=True)


# ------------------------------------------------------------- markdown subset
#
# Supported: ##/###/#### headings, paragraphs, - lists, 1. lists, > quotes, --- rules,
# | tables |, **bold**, *em*, `code`, [text](url), and lines that are already HTML.
# Deliberately small: five files of prose do not need a parser, and a subset this size can be
# tested line by line (see tests/test_markdown.py).

_INLINE_CODE = re.compile(r"`([^`]+)`")
_INLINE_BOLD = re.compile(r"\*\*(.+?)\*\*")
_INLINE_EM = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def inline(text: str, prefix: str) -> str:
    """Escaped inline markdown -> HTML. External links open safely; internal links get the
    deploy prefix; nothing here decides `rel` for product links (build.py owns that, and the
    gate re-checks it in the finished HTML)."""
    out = esc(text)
    out = _INLINE_CODE.sub(r"<code>\1</code>", out)

    def link_sub(m: re.Match) -> str:
        label, href = m.group(1), m.group(2)
        if href.startswith("/"):
            return f'<a href="{norm_internal_href(href, prefix)}">{label}</a>'
        if re.match(r"^https?://", href):
            return f'<a href="{href}" target="_blank" rel="nofollow noopener">{label}</a>'
        return m.group(0)

    out = _LINK.sub(link_sub, out)
    out = _INLINE_BOLD.sub(r"<strong>\1</strong>", out)
    out = _INLINE_EM.sub(r"<em>\1</em>", out)
    return out


def _is_table_sep(line: str) -> bool:
    return bool(re.match(r"^\s*\|?[\s:|-]{3,}\|[\s:|-]*$", line or "")) and "-" in line


def md_to_html(src: str, prefix: str = "") -> str:
    lines = src.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    para: list[str] = []
    list_mode = None  # "ul" | "ol"
    quote: list[str] = []

    def flush_para():
        if para:
            out.append("<p>" + inline(" ".join(para).strip(), prefix) + "</p>")
            para.clear()

    def flush_list():
        nonlocal list_mode
        if list_mode:
            out.append(f"</{list_mode}>")
            list_mode = None

    def flush_quote():
        if quote:
            out.append(
                "<blockquote><p>" + inline(" ".join(quote).strip(), prefix) + "</p></blockquote>"
            )
            quote.clear()

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            flush_para()
            flush_list()
            flush_quote()
            i += 1
            continue

        # table block
        if stripped.startswith("|") and i + 1 < len(lines) and _is_table_sep(lines[i + 1]):
            flush_para()
            flush_list()
            flush_quote()
            header = [c.strip() for c in stripped.strip("|").split("|")]
            rows: list[list[str]] = []
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            thead = "".join(f"<th>{inline(c, prefix)}</th>" for c in header)
            body = []
            for r in rows:
                r = (r + [""] * len(header))[: len(header)]
                body.append("<tr>" + "".join(f"<td>{inline(c, prefix)}</td>" for c in r) + "</tr>")
            out.append(
                '<div class="table-wrap"><table><thead><tr>'
                + thead
                + "</tr></thead><tbody>"
                + "".join(body)
                + "</tbody></table></div>"
            )
            continue

        m = re.match(r"^(#{2,4})\s+(.*)$", stripped)
        if m:
            flush_para()
            flush_list()
            flush_quote()
            level = len(m.group(1))
            text = m.group(2).strip()
            anchor = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
            out.append(
                f'<h{level} id="{anchor}">{inline(text, prefix)}</h{level}>'
            )
            i += 1
            continue

        if re.match(r"^-{3,}$", stripped):
            flush_para()
            flush_list()
            flush_quote()
            out.append("<hr>")
            i += 1
            continue

        if stripped.startswith("> "):
            flush_para()
            flush_list()
            quote.append(stripped[2:])
            i += 1
            continue

        m = re.match(r"^[-*]\s+(.*)$", stripped)
        if m:
            flush_para()
            flush_quote()
            if list_mode != "ul":
                flush_list()
                out.append("<ul>")
                list_mode = "ul"
            out.append("<li>" + inline(m.group(1), prefix) + "</li>")
            i += 1
            continue

        m = re.match(r"^\d+[.)]\s+(.*)$", stripped)
        if m:
            flush_para()
            flush_quote()
            if list_mode != "ol":
                flush_list()
                out.append("<ol>")
                list_mode = "ol"
            out.append("<li>" + inline(m.group(1), prefix) + "</li>")
            i += 1
            continue

        flush_para()
        para.append(stripped)
        i += 1

    flush_para()
    flush_list()
    flush_quote()
    return "\n".join(out)


def word_count(md: str) -> int:
    return len(re.findall(r"[A-Za-z0-9'’°\-]+", md))


def reading_minutes(md: str) -> int:
    return max(2, round(word_count(md) / 220))


def fmt_date(iso: str) -> str:
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    try:
        y, m, d = iso.split("-")
        return f"{int(d)} {months[int(m) - 1]} {y}"
    except Exception:
        return iso
