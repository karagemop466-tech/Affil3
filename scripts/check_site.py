#!/usr/bin/env python3
"""Dependency-free structural checks for this static publication."""
from pathlib import Path
from html.parser import HTMLParser
import csv
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.targets = []; self.has_disclosure = False; self.disclosure_footer = False; self.active_shortlink = False; self.outbound_rels = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('a', 'link'):
            target = attrs.get('href')
            if target: self.targets.append(target)
        if tag == 'a' and attrs.get('href', '').lower().startswith('https://link.amazon/'):
            self.active_shortlink = True
        if tag == 'a' and attrs.get('data-outbound') == 'true':
            self.outbound_rels.append(attrs.get('rel', ''))
        if attrs.get('class') == 'disclosure': self.has_disclosure = True
        if attrs.get('class') == 'footer-disclosure': self.disclosure_footer = True

def fail(message):
    print(f'FAIL: {message}', file=sys.stderr); sys.exit(1)

pages = sorted(ROOT.rglob('*.html'))
if not pages: fail('no HTML pages found')
for page in pages:
    parser = Links(); parser.feed(page.read_text(encoding='utf-8'))
    rel = page.relative_to(ROOT).as_posix()
    if not parser.has_disclosure: fail(f'{rel}: missing above-fold disclosure strip')
    if not parser.disclosure_footer: fail(f'{rel}: missing footer disclosure')
    if parser.active_shortlink: fail(f'{rel}: unverified submitted product link must not be active')
    if any('sponsored' not in rel_value.lower().split() for rel_value in parser.outbound_rels):
        fail(f'{rel}: data-outbound link is missing rel sponsored')
    for target in parser.targets:
        if target.startswith(('https://', 'http://', 'mailto:', 'tel:', 'data:')) or target.startswith('#'):
            continue
        path_part = target.split('#', 1)[0].split('?', 1)[0]
        if not path_part: continue
        candidate = (page.parent / path_part).resolve()
        if not candidate.is_file(): fail(f'{rel}: broken local link {target}')

sitemap_path = ROOT / 'sitemap.xml'
feed_path = ROOT / 'feed.xml'
try:
    sitemap = ET.parse(sitemap_path).getroot()
    feed = ET.parse(feed_path).getroot()
except (ET.ParseError, OSError) as exc:
    fail(f'XML parse failed: {exc}')
ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
locs = {node.text for node in sitemap.findall('sm:url/sm:loc', ns)}
base = 'https://karagemop466-tech.github.io/Affil3/'
expected = {base + ('' if page.name == 'index.html' and page.parent == ROOT else page.relative_to(ROOT).as_posix()) for page in pages}
if locs != expected:
    fail(f'sitemap mismatch; missing={sorted(expected-locs)}, extra={sorted(locs-expected)}')
feed_links = {item.findtext('link') for item in feed.findall('./channel/item')}
expected_guides = {base + p.relative_to(ROOT).as_posix() for p in (ROOT / 'guides').glob('*.html')}
if feed_links != expected_guides:
    fail(f'feed mismatch; missing={sorted(expected_guides-feed_links)}, extra={sorted(feed_links-expected_guides)}')

with (ROOT / 'data/product-intent.csv').open(encoding='utf-8', newline='') as stream:
    product_rows = list(csv.DictReader(stream))
if len(product_rows) != 5: fail(f'expected 5 product-intent rows, found {len(product_rows)}')
for row in product_rows:
    for field in ('intended_asin', 'official_listing_url', 'confirmation_date', 'confirmation_source', 'observed_redirect_target'):
        if row.get(field): fail(f"product {row['record_id']}: unverified field {field} must remain blank")
    if not row.get('official_source_reference', '').startswith('https://sell.amazon.com/'):
        fail(f"product {row['record_id']}: missing official Amazon source reference")

with (ROOT / 'data/campaign-ledger.csv').open(encoding='utf-8', newline='') as stream:
    campaign_rows = list(csv.DictReader(stream))
if campaign_rows: fail('campaign ledger must stay empty until first-party reports provide facts')

print(f'OK: {len(pages)} HTML pages, local links, disclosures, sitemap/feed, five blank-safe product records, empty ledger, and sponsored-link guard.')
