#!/usr/bin/env node
// Self-hosted analytics collector for Affil3. Node.js built-ins only.
// Stores DAILY AGGREGATE COUNTS per event, property and page path. It does not store
// IP addresses, user agents, cookies, or raw referrer URLs.
// Run:  PORT=8787 SITE_ORIGIN=https://karagemop466-tech.github.io DATA_DIR=./analytics-data node tools/collector.mjs
// Endpoint for the site: https://<your-host>/collect  (set as analyticsEndpoint in data/config.json)
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PORT = Number(process.env.PORT || 8787);
const HOST = process.env.HOST || '0.0.0.0';
const SITE_ORIGIN = process.env.SITE_ORIGIN || 'https://karagemop466-tech.github.io';
const DATA_DIR = path.resolve(process.env.DATA_DIR || path.join(ROOT, 'analytics-data'));
const MAX_BODY = 2048;

const EVENTS = {
  page_view: ['referrer_host'],
  category_view: ['category'],
  product_view: ['product_id'],
  outbound_click: ['product_id', 'destination_host', 'placement'],
  guide_read_75: ['guide'],
};
const SAFE = /^[a-z0-9._\/-]{0,100}$/i;

export function validate(body) {
  if (!body || typeof body !== 'object') return { error: 'bad body' };
  const name = body.event;
  if (!Object.prototype.hasOwnProperty.call(EVENTS, name)) return { error: 'unknown event' };
  const allowedProps = EVENTS[name];
  const props = {};
  const raw = body.props && typeof body.props === 'object' ? body.props : {};
  for (const k of allowedProps) {
    const v = raw[k] == null ? '' : String(raw[k]);
    if (!SAFE.test(v)) return { error: `bad value for ${k}` };
    props[k] = v;
  }
  const p = typeof body.path === 'string' && body.path.length <= 200 ? body.path.split('?')[0] : '';
  if (p && !/^\/[a-z0-9._\/-]*$/i.test(p)) return { error: 'bad path' };
  return { name, props, path: p };
}

function day() { return new Date().toISOString().slice(0, 10); }

function increment(rec) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  const file = path.join(DATA_DIR, `counts-${day()}.json`);
  let data = {};
  try { data = JSON.parse(fs.readFileSync(file, 'utf8')); } catch { data = {}; }
  const key = [rec.name, rec.path, ...Object.entries(rec.props).map(([k, v]) => `${k}=${v}`)].join('|');
  data[key] = (data[key] || 0) + 1;
  const tmp = file + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(data, null, 2));
  fs.renameSync(tmp, file);
}

function cors(res) {
  res.setHeader('Access-Control-Allow-Origin', SITE_ORIGIN);
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'content-type');
  res.setHeader('Vary', 'Origin');
}

export const server = http.createServer((req, res) => {
  cors(res);
  if (req.method === 'OPTIONS') { res.writeHead(204); return res.end(); }
  if (req.url === '/healthz') { res.writeHead(200, { 'content-type': 'text/plain' }); return res.end('ok'); }
  if (req.method !== 'POST' || !(req.url === '/collect' || req.url.startsWith('/collect?'))) {
    res.writeHead(404); return res.end();
  }
  let size = 0; const chunks = [];
  req.on('data', (c) => { size += c.length; if (size > MAX_BODY) { req.destroy(); } else chunks.push(c); });
  req.on('end', () => {
    if (size > MAX_BODY) { res.writeHead(413); return res.end(); }
    let body;
    try { body = JSON.parse(Buffer.concat(chunks).toString('utf8')); } catch { res.writeHead(400); return res.end(); }
    const v = validate(body);
    if (v.error) { res.writeHead(400); return res.end(); }
    try { increment(v); } catch { res.writeHead(500); return res.end(); }
    res.writeHead(204); res.end();
  });
  req.on('error', () => { try { res.writeHead(400); res.end(); } catch {} });
});

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  server.listen(PORT, HOST, () => console.log(`Affil3 collector listening on ${HOST}:${PORT}; origin ${SITE_ORIGIN}; data ${DATA_DIR}`));
}
