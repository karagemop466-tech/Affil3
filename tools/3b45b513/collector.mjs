#!/usr/bin/env node
/**
 * Counter Desk — self-hosted, privacy-preserving event collector.
 *
 * Deliberately boring. It accepts exactly the five events the site defines, rejects
 * anything else, keeps aggregate counts only, and writes one append-only JSONL file per
 * day. It never stores an IP address, a user agent, a referrer or a cookie.
 *
 * Run:  node tools/3b45b513/collector.mjs            (PORT=8787 by default)
 *       PORT=9000 DATA_DIR=/var/lib/counter-desk node tools/3b45b513/collector.mjs
 *
 * Then set analyticsEndpoint in data/3b45b513/config.json to
 *   https://your-host.example/collect
 * and rebuild. Until that is set, the site sends nothing at all.
 *
 * Deployment note: GitHub Pages cannot run this. It needs a host that runs Node — a
 * small server, a container, or a serverless function wrapping handle().
 */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const DATA_DIR = process.env.DATA_DIR || path.join(ROOT, 'analytics-data');
const PORT = Number(process.env.PORT || 8787);
const ALLOWED_ORIGIN = process.env.ALLOWED_ORIGIN || 'https://karagemop466-tech.github.io';
const MAX_BODY = 2048;

/** The allowlist. A property not listed here is dropped, and an unknown event is refused. */
const EVENTS = {
  page_view: ['page_path', 'page_type'],
  category_view: ['category'],
  product_view: ['product_id', 'category'],
  outbound_click: ['product_id', 'placement'],
  guide_read_75: ['guide_slug'],
};

const isString = (v) => typeof v === 'string' && v.length > 0 && v.length <= 120;

/** Validates a payload and returns { event, properties } or a reason string. */
export function validate(payload) {
  if (!payload || typeof payload !== 'object') return { error: 'body must be an object' };
  const { event, properties } = payload;
  if (typeof event !== 'string' || !Object.prototype.hasOwnProperty.call(EVENTS, event)) {
    return { error: 'unknown event' };
  }
  if (properties !== undefined && (typeof properties !== 'object' || properties === null)) {
    return { error: 'properties must be an object' };
  }
  const clean = {};
  for (const key of EVENTS[event]) {
    const value = properties && properties[key];
    if (value === undefined) continue;
    if (!isString(value)) return { error: `property ${key} must be a string of 1-120 characters` };
    clean[key] = value;
  }
  return { event, properties: clean };
}

function append(record) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  const day = new Date().toISOString().slice(0, 10);
  fs.appendFileSync(path.join(DATA_DIR, `events-${day}.jsonl`), JSON.stringify(record) + '\n');
}

function cors(res) {
  res.setHeader('Access-Control-Allow-Origin', ALLOWED_ORIGIN);
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Vary', 'Origin');
}

/** The whole request handling, exported so a serverless wrapper can reuse it. */
export function handle(req, res, bodyText) {
  cors(res);
  if (req.method === 'OPTIONS') { res.writeHead(204).end(); return; }
  if (req.method !== 'POST') { res.writeHead(405, { Allow: 'POST, OPTIONS' }).end(); return; }
  if ((req.headers['content-type'] || '').split(';')[0].trim() !== 'application/json') {
    res.writeHead(415).end(); return;
  }
  let payload;
  try { payload = JSON.parse(bodyText); } catch { res.writeHead(400).end(); return; }
  const result = validate(payload);
  if (result.error) { res.writeHead(400).end(); return; }
  // Only the four fields below are persisted. No IP, no UA, no referrer, no cookie.
  append({ received_at: new Date().toISOString(), event: result.event, properties: result.properties });
  res.writeHead(204).end();
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const server = http.createServer((req, res) => {
    if (req.url !== '/collect') { res.writeHead(404).end(); return; }
    let body = '';
    let tooBig = false;
    req.on('data', (chunk) => {
      body += chunk;
      if (body.length > MAX_BODY) { tooBig = true; req.destroy(); }
    });
    req.on('end', () => {
      if (tooBig) { res.writeHead(413).end(); return; }
      handle(req, res, body);
    });
  });
  server.listen(PORT, '0.0.0.0', () => {
    console.log(`counter-desk collector on http://0.0.0.0:${PORT}/collect`);
    console.log(`  accepting 5 events, allowing origin ${ALLOWED_ORIGIN}`);
    console.log(`  writing aggregate JSONL to ${DATA_DIR}`);
  });
}
