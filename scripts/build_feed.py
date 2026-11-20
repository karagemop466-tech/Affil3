#!/usr/bin/env python3
"""Build docs/rss.xml from the guide pages under docs/guides/.

Extracts each guide's title and date from its <title> tag and a
<meta name="guide-date"> tag. Running this after publishing a new guide keeps
the feed in sync with the sitemap (part of the publishing cadence).
Standard library only.
"""
import glob
import os
import re
import sys
from html import escape

DOCS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
SITE = "https://karagemop466-tech.github.io/Affil3"
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
DATE_RE = re.compile(r'<meta name="guide-date" content="([^"]+)"', re.IGNORECASE)


def main():
    guides = sorted(glob.glob(os.path.join(DOCS, "guides", "*.html")))
    items = []
    for path in guides:
        rel = os.path.relpath(path, DOCS).replace(os.sep, "/")
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        t = TITLE_RE.search(content)
        d = DATE_RE.search(content)
        title = escape(t.group(1).replace(" — The Countertop Edit", "").strip()) if t else "Untitled guide"
        date = d.group(1) if d else ""
        url = SITE.rstrip("/") + "/" + rel
        items.append(
            "    <item>\n"
            f"      <title>{title}</title>\n"
            f"      <link>{url}</link>\n"
            f"      <guid isPermaLink=\"true\">{url}</guid>\n"
            f"      <pubDate>{date}</pubDate>\n"
            "    </item>"
        )

    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        "  <channel>\n"
        "    <title>The Countertop Edit</title>\n"
        "    <link>" + SITE + "/</link>\n"
        "    <description>Question-shaped buying guides for air fryers and meat thermometers. Source-first, disclosed, no hype.</description>\n"
        "    <language>en-us</language>\n"
        + "\n".join(items) + "\n"
        "  </channel>\n"
        "</rss>\n"
    )
    out = os.path.join(DOCS, "rss.xml")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(feed)
    print(f"Wrote {out} with {len(items)} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
